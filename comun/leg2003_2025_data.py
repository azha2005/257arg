"""Datos, alianzas Wikipedia y controles de los atlas legislativos 2003–2025."""
from pathlib import Path
from collections import Counter, defaultdict
from types import SimpleNamespace
import sys, re, json, pickle, difflib, base64, io, html
import pandas as pd
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'../datos/wikileg'))
sys.path.insert(0,str(ROOT/'../mapas/mapa2013'))
from names import norm
from bloques_leg import wiki_groups, match
from bloques_prov import match_prov, prov_tables
from parse_wleg import rows, clean
from leg2003_2025_geom import description

D2P=dict(zip((str(n).zfill(2) for n in range(1,25)),['Capital Federal','Buenos Aires','Catamarca','Córdoba','Corrientes','Chaco','Chubut','Entre Ríos','Formosa','Jujuy','La Pampa','La Rioja','Mendoza','Misiones','Neuquén','Río Negro','Salta','San Juan','San Luis','Santa Cruz','Santa Fe','Santiago del Estero','Tucumán','Tierra del Fuego']))
BEIGE='#e6dcc3';GREY='#a9a9a9'
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def num(x):return f'{int(x):,}'.replace(',','.')
def table(year):
    t=(ROOT/'../datos/fuentes_leg2003_2025'/f'wleg{year}.txt').read_text(encoding='utf8')
    i=re.search(r'\n== Resultados(?: generales)? ==',t).start();i=t.index('{|',i);j=t.index('\n|}',i)
    return t,t[i:j]

def groups_for(year):
    g=wiki_groups(year,'DIPUTADOS')
    # El subtotal de FPCyS de 2017 no dice «Total» y el parser histórico lo duplicaba.
    if year==2017:
        parts=[x for x in g if x['total'] in (287613,42248,10763,7229)]
        total=next(x for x in g if x['total']==347853)
        total['filas']=[r for x in parts for r in x['filas']]
        g=[x for x in g if x not in parts]
    if year==2021:
        for x in g:
            if x['total']==28796:x['grupo']='Partido Felicidad'
    return g

def short(n):
    pairs=[('libertad avanza','LLA'),('avanza libertad','LLA'),('fuerza patria','FP'),('unión por la patria','UP'),('frente de todos','FdT'),('juntos por el cambio','JxC'),('cambiemos','CAM'),('provincias unidas','PU'),('frente para la victoria','FPV'),('unidad ciudadana','UC'),('peronismo no kirchnerista','PJ'),('peronismo federal','PF'),('justicia, unión','PF'),('unión cívica radical','UCR'),('concertación para una','UNA'),('desarrollo social','UDESO'),('república igualitaria','ARI'),('coalición cívica','CC'),('frente amplio progresista','FAP'),('progresista cívico','FPCyS'),('propuesta republicana','PRO'),('frente popular-propuesta','FP-PRO'),('frente de izquierda','FIT'),('recrear','RECR'),('compromiso para el cambio','FCPC'),('partido justicialista','PJ'),('dignidad y la independencia','MODIN'),('partido socialista','PS'),('acción federalista','PAUFE'),('unidad federalista','PAUFE'),('frente nuevo','FN'),('frente renovador de la concordia','FRC'),('popular neuquino','MPN'),('renovador de salta','PRS'),('compromiso federal','CF'),('unidos por una nueva','UNA'),('1país','1País'),('consenso federal','CF'),('hacemos por nuestro','HxNP'),('tercera vía','PF'),('juntos somos río','JSRN'),('por santa cruz','PSC'),('chubut somos','ChuSoTo'),('chubut para todos','CpT'),('unión por córdoba','UxC'),('frente cívico y social de catamarca','FCyS'),('fuerza republicana','FR'),('innovación federal','IF'),('la neuquinidad','LN')]
    low=n.lower()
    for s,c in pairs:
        if s in low:return c
    m=re.search(r'\(([^()]+)\)',n)
    if m and len(m.group(1))<=8:return m.group(1)
    words=re.findall(r'\w+',n)
    return ''.join(w[0].upper() for w in words if w.lower() not in ('de','del','la','las','los','y','por','para','el'))[:6]

def load_votes(year,folder):
    invalid={};changes=[]
    if year!=2003:
        v,m=pd.read_pickle(ROOT/'../datos_oficiales'/str(year)/('agregado_polar.pkl' if year<2011 else 'agregado.pkl'))
        v=v[v.cargo_nombre.str.contains('DIPUTAD')].copy();m=m[m.cargo_nombre.str.contains('DIPUTAD')].copy()
    else:
        d=pd.read_csv(ROOT/'../raw/datar_2003_departamento_SIN_VALIDAR.csv');d=d[d.eleccion=='DN'].copy()
        dec=d.votos.notna()&(d.votos%1!=0)
        assert set(d.loc[dec,'departamento'])=={'LA PLATA'}
        d.loc[dec,'votos']=(d.loc[dec,'votos']*1000).round()
        changes.append('La Plata: 21 valores con separador de miles leído como decimal se multiplican por 1000; no se altera el CSV original.')
        for (di,si),sub in d.groupby(['provinciaId','departamentoId']):
            key=(str(di).zfill(2),str(si).zfill(3))
            if sub.votos.isna().any():invalid[key]='La fuente deja al menos una lista sin cifra. Se conserva la unidad pendiente, sin sustituir la celda por cero.'
            pos=sub[sub.partidoId=='990'].votos.sum();s=sub[~sub.partidoId.isin(['990','991','992','994'])].votos.sum()
            if int(s)!=int(pos):invalid[key]=f'La suma de listas ({num(s)}) no coincide con los positivos declarados ({num(pos)}). Dato pendiente de cotejo.'
        v=pd.DataFrame(dict(distrito_id=d.provinciaId.astype(int).astype(str).str.zfill(2),seccion_id=d.departamentoId.astype(int).astype(str).str.zfill(3),seccion_nombre=d.departamento,
                            agrupacion_id=d.partidoId,agrupacion_nombre=d.partido,cargo_nombre='DIPUTADOS NACIONALES',v=d.votos))
        v['distrito_nombre']=v.distrito_id.map(D2P).replace({'Capital Federal':'Ciudad de Buenos Aires'})
        v['votos_tipo']=v.agrupacion_id.map({'990':'TOTAL_POS','991':'BLANCO','992':'NULO','994':'TOTAL'}).fillna('POSITIVO')
        v=v[~v.votos_tipo.isin(['TOTAL_POS','TOTAL']) & v.v.notna()].copy()
        v['v']=v.v.astype(int)
        m=pd.DataFrame(columns=['distrito_id','seccion_id','cargo_nombre','mesa_electores','mesa_id'])
        pd.to_pickle((v,m),folder/'agregado_preparado.pkl')
    for df in (v,m):
        df['distrito_id']=df.distrito_id.astype(int).astype(str).str.zfill(2)
        df['seccion_id']=df.seccion_id.astype(int).astype(str).str.zfill(3)
    v['agrupacion_id']=v.agrupacion_id.fillna('').astype(str).str.zfill(4)
    v['v']=pd.to_numeric(v.v).astype(int)
    compath=ROOT/'../datos/fuentes_leg2003_2025/complementos_departamentales.json'
    if compath.exists():
        for c in json.loads(compath.read_text(encoding='utf8')):
            if c['year']!=year:continue
            d,s=c['d'],c['s']
            names=dict(zip(v[v.distrito_id==d].agrupacion_id,v[v.distrito_id==d].agrupacion_nombre))
            v=v[~((v.distrito_id==d)&(v.seccion_id==s))].copy()
            added=[]
            for a,n in c['votes'].items():
                assert a in names,(year,d,a)
                added.append(dict(distrito_id=d,distrito_nombre='Ciudad de Buenos Aires' if d=='01' else D2P[d],seccion_id=s,seccion_nombre=c['name'],agrupacion_id=a,agrupacion_nombre=names[a],votos_tipo='POSITIVO',v=n,cargo_nombre='DIPUTADOS NACIONALES'))
            for typ,key in [('BLANCO','bla'),('NULO','nul')]:
                added.append(dict(distrito_id=d,distrito_nombre=D2P[d],seccion_id=s,seccion_nombre=c['name'],agrupacion_id='0000',agrupacion_nombre='',votos_tipo=typ,v=c[key],cargo_nombre='DIPUTADOS NACIONALES'))
            v=pd.concat([v,pd.DataFrame(added)],ignore_index=True)
            changes.append(c['name']+': '+c['source'])
    return v,m,invalid,changes

ALIASES={
 'coronelrosales':'coroneldemarinaleonardorosales','coroneldemarinalrosales':'coroneldemarinaleonardorosales','generalmadariaga':'generaljuanmadariaga',
 'arrecifes':'bartolomemitre','1odemayo':'1demayo','pasodeindios':'pasodelosindios','generalangelvicentepenaloza':'generalangelvpenaloza',
 'generaljuanfacundoquiroga':'generaljuanfquiroga','generalortizdeocampo':'generalocampo','pilcaniyeu':'pilnaniyeu','sanantoniooeste':'sanantonio',
 'generaljosesanmartin':'generaljosedesanmartin','pueyrredon':'lacapital','juanmartindepueyrredon':'lacapital','pellegrini':'pelegrini','famailla':'famalla',
 'sanfernandodelvalledecatamarca':'capital','doctorroquefaenzpena':'presidenteroquesaenzpena','doctormanuelbelgrano':'drmanuelbelgrano',
}
PROV_ALIASES={}
# Equivalencias comprobadas por los atlas de referencia (sin ejecutar sus datos).
import ast
ns={'norm':norm}
src=ast.parse((ROOT/'../mapas/mapa2013/build_2013.py').read_text(encoding='utf8'))
for node in src.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EALIAS' for t in node.targets):
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases2013>','exec'),ns)
PROV_ALIASES.update(ns['EALIAS'])
src=ast.parse((ROOT/'../mapas/mapa2009/datos_2009.py').read_text(encoding='utf8'))
for node in src.body:
    if isinstance(node,ast.For) and isinstance(node.iter,ast.Call) and isinstance(node.iter.func,ast.Attribute) and isinstance(node.iter.func.value,ast.Dict):
        pairs=ast.literal_eval(node.iter.func.value)
        if 'Buenos Aires' in pairs:
            for p,pp in pairs.items():
                for a,b in pp:PROV_ALIASES[(p,norm(a))]=norm(b)
for p,pp in {
 'Buenos Aires':[('CAP. SARMIENTO','Capitán Sarmiento'),('EXALTAC. DE LA CRUZ','Exaltación de la Cruz'),('G. RODRIGUEZ','General Rodríguez'),('G. SAN MARTIN','General San Martín'),('S. MIGUEL','San Miguel'),('S. ANDRÉS DE GILES','San Andrés de Giles'),('S. ANTONIO DE ARECO','San Antonio de Areco'),('S. FERNANDO','San Fernando'),('S. ISIDRO','San Isidro'),('3 DE FEBRERO','Tres de Febrero'),('V. LOPEZ','Vicente López'),('F. AMEGUINO','Florentino Ameghino'),('MALVINAS ARG.','Malvinas Argentinas')],
 'Catamarca':[('F. MAMERTO ESQUIÚ','Fray Mamerto Esquiú')],
 'Córdoba':[('R. SÁENZ PEÑA','Presidente Roque Sáenz Peña')],
 'Corrientes':[('P. DE LOS LIBRES','Paso de los Libres'),('S. L. DEL PALMAR','San Luis del Palmar')],
 'Chaco':[('CDTE. FERNÁNDEZ','Comandante Fernández'),('F. J. STA. MARÍA DE ORO','Fray Justo Santa María de Oro')],
 'Formosa':[('Capital','Formosa')],
 'La Rioja':[('S B DE LOS SAUCES','San Blas de los Sauces'),('A. V. PEÑALOZA','General Angel V. Peñaloza'),('J. F. QUIROGA','General Juan F. Quiroga'),('G.O. DE OCAMPO','General Ocampo'),('R V PEÑALOZA','Rosario Vera Peñaloza')],
 'Misiones':[('CECP. DE LA SIERRA','Concepción'),('GRAL. SAN MARTÍN','Libertador General San Martín')],
 'Jujuy':[('GRAL. BELGRANO','Dr. Manuel Belgrano')],
 'Chubut':[('F. Ameghino','Florentino Ameghino')],
}.items():
    for a,b in pp:PROV_ALIASES[(p,norm(a))]=norm(b)
for p,pp in {
 'Chaco':[('CMDTE. FERNÁNDEZ','Comandante Fernández'),('FRAY J.S.M.DE ORO','Fray Justo Santa María de Oro')],
 'La Rioja':[('JUAN F. QUIROGA','General Juan F. Quiroga')],
 'Misiones':[('L.N.ALEM','Leandro N. Alem'),('LIB. GRAL. SAN MARTÍN','Libertador General San Martín'),('GRAL. M BELGRANO','General Manuel Belgrano')],
 'Río Negro':[('GENERAL CONESA','Conesa')],
 'Salta':[('GRAL SAN MARTÍN','General José de San Martín')],
 'San Luis':[('DUPUY','Gobernador Dupuy')],
 'Santiago del Estero':[('JUAN FELIPE IBARRA','Juan F. Ibarra')],
 'Chubut':[('Río Senger','Río Senguer')],
 'Tucumán':[('Juan Bautista Alberdi','Juan B. Alberdi')],
 'Santa Fe':[('Villa Constitución','Constitución')],
}.items():
    for a,b in pp:PROV_ALIASES[(p,norm(a))]=norm(b)
PROV_ALIASES[('Chaco',norm('Fray Justo Sta. María de Oro'))]=norm('Fray Justo Santa María de Oro')

def prepare(year,U):
    folder=ROOT/f'../mapas/mapa{year}';folder.mkdir(exist_ok=True)
    v,m,invalid,changes=load_votes(year,folder)
    groups=groups_for(year)
    # Los snapshots originales quedan intactos. El matcher histórico usa wikileg;
    # la descarga en vivo se contrasta y registra por revisión, sin pisar referencias.
    if year<=2007:
        _,mapping,matchlog,_=match_prov(year,'DIPUTADOS',str(folder/'agregado_preparado.pkl') if year==2003 else None)
        def mapped(r):return mapping.get((r.distrito_nombre,r.agrupacion_nombre))
    else:
        _,_,mapping,_=match(year,'DIPUTADOS')
        def mapped(r):return mapping.get(r.agrupacion_nombre)
    # Normaliza rótulos corregidos en el parser sin cambiar la afiliación.
    def fixgroup(n):
        if year==2017 and n and (n.startswith('Frente Progresista') or n=='Partido Socialista (PS)'):return next(x['grupo'] for x in groups if x['total']==347853)
        if year==2021 and n=='Partido':return 'Partido Felicidad'
        return n
    ids={g['grupo']:f'B{i:02d}' for i,g in enumerate(groups,1)}
    bycode={ids[g['grupo']]:g for g in groups}
    positive=v[v.votos_tipo=='POSITIVO']
    listmap={};maprows=[];unmatched=[]
    for (d,a),sub in positive.groupby(['distrito_id','agrupacion_id']):
        r=next(sub.itertuples());label=fixgroup(mapped(r))
        if year==2003:
            correction={('05','0165'):'Partido Nuevo de Corrientes',('13','0501'):'Partido Justicialista'}
            fragment=correction.get((d,a))
            if fragment:label=next(g['grupo'] for g in groups if fragment in g['grupo'])
            if d in ('06','18') and r.agrupacion_nombre=='FRENTE GRANDE':label=next(g['grupo'] for g in groups if g['grupo']=='Frente Grande (FG)')
        # Correcciones contra las filas provinciales: listas omitidas por el cruce de nombres.
        if year==2015 and r.agrupacion_nombre in ('UNION PARA VIVIR MEJOR','UNION CIVICA RADICAL'):
            label=next(g['grupo'] for g in groups if g['grupo']=='Cambiemos')
        if year in (2005,2007) and d=='13':
            # PolAr Mendoza usa nombres de partido diferentes a los de INDRA.
            aliases={2005:{'Partido Demócrata':'Alianza Propuesta Republicana','Partido Federal':'Frente para la Victoria','Polo Social':'Frente para la Victoria','Partido Todos':'Todos - Movimiento','Intransigente':'Unión Cívica Radical','F.I.S.C.A.L.':'Unión Cívica Radical'},
                     2007:{'Intransigente':'Frente para la Victoria','Polo Social':'Frente para la Victoria','Partido Federal':'Frente para la Victoria','Movimiento Libres del Sur':'Frente para la Victoria','Compromiso por Mendoza':'Frente para la Victoria','P. de Todos por los Derechos Sociales':'Frente para la Victoria','P. Propuestas p/el Cambio de MZA':'Frente para la Victoria','Convergencia del Sur':'Frente para la Victoria','Unidad para el Cambio':'Frente para la Victoria'}}
            fragment=aliases[year].get(r.agrupacion_nombre)
            if fragment:
                hits=[g['grupo'] for g in groups if fragment in g['grupo']]
                if hits:label=hits[0]
            if year==2007 and r.agrupacion_nombre=='El Movimiento de las Provincias Unidas':
                label=next(g['grupo'] for g in groups if g['grupo']=='Concertación para Una Nación Avanzada')
        code=ids.get(label)
        listmap[(d,a)]=code
        maprows.append(dict(distrito=d,provincia=D2P[d],lista=a,nombre=r.agrupacion_nombre,bloque=label or '',codigo=code or '',votos=int(sub.v.sum())))
        if not code:unmatched.append(maprows[-1])
    pd.DataFrame(maprows).to_csv(folder/f'mapeo_listas_{year}.csv',index=False,encoding='utf-8-sig')
    colors=json.loads((ROOT/'../datos/fuentes_leg2003_2025/colores.json').read_text(encoding='utf8'))
    text,tbl=table(year);tr=rows(tbl)
    CAND={}
    for code,g in bycode.items():
        color=g['filas'][0].get('color') if g['filas'] else None
        totals=[r for r in tr if r['votos']==g['total']]
        if totals and totals[-1].get('color'):color=totals[-1]['color']
        # Los subtotales suelen tener fondo pastel de tabla. El color partidario
        # está en la barra {{porcentaje|c=...}} / hex=..., no en ese fondo.
        vote_label=f"{g['total']:,}".replace(',','.')
        blocks=[block for block in tbl.split('\n|-') if re.search(r'(?<![\d.])'+re.escape(vote_label)+r'(?![\d.])',block)]
        if blocks:
            cm=re.search(r'\{\{porcentaje\|(?:c|hex)=\s*(?:\{\{[Cc]olor político\|([^}|]+)\}\}|#?([0-9A-Fa-f]{6}))\s*\|',blocks[-1])
            if cm:
                proposed=cm.group(1) or '#'+cm.group(2)
                # Algunas barras usan gris genérico, aunque la fila identifica
                # al partido con su color (p. ej. ChuSoTo 2015).
                if proposed.lower() not in ('#808080','#000000','#ffffff'):color=proposed
        color=clean(colors.get(color,color) or '')
        if not color or not re.fullmatch('#[a-fA-F0-9]{6}',color):color='#717274'
        name=re.sub(r'\s*\([^)]*\)','',g['grupo'])
        name=re.sub(r' y aliados$','',name)
        CAND[code]=dict(n=name,base=color,logo=short(g['grupo']))
    original_colors={c:x['base'] for c,x in CAND.items()}
    # Excepciones de contraste, como en los atlas 2009/2013: quedan documentadas.
    contrast={
      2003:{'Movimiento Federal para Recrear el Crecimiento':'#8e6bd8','Fuerza Republicana (FR)':'#7b3f00','Partido Renovador de Salta (PRS)':'#cddc39','Unidos por Salta':'#ff69b4','Frente Cívico y Social de Catamarca':'#0097a7','Acción Federalista por Buenos Aires':'#f59e0b','Partido Nuevo de Corrientes - Partido Federal':'#40e0d0'},
      2005:{'Peronismo Federal':'#8e6bd8','Partido Unidad Federalista (PAUFE)':'#f59e0b','Partido Renovador de Salta (PRS)':'#cddc39'},
      2025:{'Frente Primero Jujuy Avanza':'#c2185b','Frente Popular Agrario y Social':'#8d5524'},
    }
    for label,color in contrast.get(year,{}).items():
        if label in ids:
            code=ids[label];old=CAND[code]['base'];CAND[code]['base']=color
    # Pedido 20-oct: colores de Wikipedia o los de los atlas 2009/2013 verificados.
    # Se cargan los valores del dataset de referencia, evitando otra paleta paralela.
    ref09=json.loads((ROOT/'../mapas/mapa2009/dataset_2009.json').read_text(encoding='utf8'))['candidates']
    ref13=json.loads((ROOT/'../mapas/mapa2013/dataset_2013.json').read_text(encoding='utf8'))['candidates']
    for code,g in bycode.items():
        label=g['grupo'];low=label.lower();source=None;ref=None
        if 'frente para la victoria' in low:ref=ref13['FPV'];source='FPV 2013'
        elif 'propuesta republicana' in low or 'unión pro' in low:ref=ref13['PRO'];source='PRO 2013'
        elif 'frente renovador de la concordia' in low:ref=ref13['FRC'];source='FRC 2013'
        elif 'popular neuquino' in low:ref=ref13['MPN'];source='MPN 2013'
        elif 'progresista cívico y social' in low:ref=ref13['FPCyS'];source='FPCyS 2013'
        elif 'partido renovador de salta' in low:ref=ref13['PARES'];source='PRS 2013'
        elif 'compromiso federal' in low:ref=ref13['CF'];source='CF 2013'
        elif 'frente de izquierda' in low:ref=ref13['FIT'];source='FIT 2013'
        elif 'unión por córdoba' in low:ref=ref13['UxC'];source='UxC 2013'
        elif 'partido acción chubutense' in low:ref=ref13['PACh'];source='PACh 2013'
        elif 'partido fe'==low:ref=ref13['FE'];source='Fe 2013'
        elif 'partido justicialista' in low:ref=ref13['PJ'];source='PJ 2013'
        elif 'peronismo federal' in low or 'peronismo no kirchnerista' in low:ref=ref09['PF'];source='Peronismo Federal 2009'
        elif 'proyecto sur'==low:ref=ref09['SUR'];source='Proyecto Sur 2009'
        if ref:
            old=CAND[code]['base']
            for k in ('base','bar','txt'):
                if k in ref:CAND[code][k]=ref[k]
    if year==2025:
        code=ids['Provincias Unidas'];old=CAND[code]['base'];CAND[code]['base']='#FF682C'
        changes.append(f'Pedido expreso del usuario: Provincias Unidas en naranja #FF682C (ficha de Wikipedia), en lugar del pastel {old} de la tabla.')
    # Revisión del 20-oct-2026 (pedido del usuario): colores de los mapas presidenciales de la Wikipedia más cercanos a cada
    # elección, leídos de sus leyendas (fuentes_leg2003_2025/presidenciales/). Los partidos provinciales conservan el suyo;
    # donde dos colores se confundían dentro del mismo mapa se cambió el del partido menor.
    P=dict(PJ03='#1c5ece',FPV='#50ade6',PRO='#f4ce00',RSA='#1aff98',ARI='#74b744',UNA07='#d31515',FAP='#ff6600',
           UDESO='#d31515',FP11='#b73c96',UNA15='#231f20',FDT='#2ea3ff',CF19='#2f3b81',UP='#009ce4',LLA='#6c4c98',JXC23='#fcbc00',HXNP='#283084')
    D=lambda c:dict(base=c)
    review={
      2003:{'Partido Justicialista':D(P['PJ03']),'Afirmación para una República':D(P['ARI']),'Recrear':D(P['PRO']),
            'Frente Compromiso para el Cambio':D('#3e5298'),         # pedido del usuario: azul de Acción por la República (Cavallo, 1999)
            'Movimiento por la Dignidad':D('#e67e22')},              # MODIN: naranja del proyecto (1993-1995)
      2005:{'Frente para la Victoria':D(P['FPV']),'Propuesta Republicana':D(P['PRO']),'Afirmación para una República':D(P['ARI']),
            'Peronismo Federal':D(P['RSA']),'Progresista Cívico':D(P['FAP']),
            'Frente Nuevo':D('#ff69b4')},                            # pedido del usuario: el rojo anaranjado de la tabla no se distinguía del FPCyS
      2007:{'Frente para la Victoria':D(P['FPV']),'Coalición Cívica':D(P['ARI']),'Nación Avanzada':D(P['UNA07']),
            'Propuesta Republicana':D(P['PRO']),'Peronismo Federal':D(P['RSA'])},
      2011:{'Frente para la Victoria':D(P['FPV']),'Frente Amplio Progresista':D(P['FAP']),'Desarrollo Social':D(P['UDESO']),
            'Frente Popular':D(P['FP11']),'Compromiso Federal':D(P['RSA'])},
      2015:{'Frente para la Victoria':D(P['FPV']),'Cambiemos':D(P['PRO']),'Nueva Alternativa':D(P['UNA15']),'Compromiso Federal':D(P['RSA'])},
      2017:{'Cambiemos':D(P['PRO']),'Unidad Ciudadana':D(P['FDT']),'peronismo no kirchnerista':D(P['RSA']),'Progresista Cívico':D(P['FAP'])},
      2019:{'Frente de Todos':D(P['FDT']),'Juntos por el Cambio':D(P['PRO']),'Consenso Federal':D(P['CF19'])},
      2021:{'Juntos por el Cambio':D(P['PRO']),'Frente de Todos':D(P['FDT']),'Tercera vía':D(P['CF19']),
            'Somos Energía para Renovar Santa Cruz':D('#d81b60')},   # el azul de la tabla se confundía con el FdT
      2023:{'Unión por la Patria':D(P['UP']),'Libertad Avanza':D(P['LLA']),'Juntos por el Cambio':D(P['JXC23']),
            'Hacemos por Nuestro País':D(P['HXNP']),
            'Por Santa Cruz':D('#ea5530')},   # pedido del usuario: su azul oscuro se confunde con Hacemos y los tonos oscuros de UP, así que va la mezcla rojo/naranja de los puntos del logo
      2025:{'La Libertad Avanza':D(P['LLA']),'Fuerza Patria':D(P['UP'])},
    }
    for code,g in bycode.items():
        low=g['grupo'].lower()
        # FRC y su alianza de 2025: índigo, para no confundirse con el azul marino de Consenso Federal / Tercera Vía / Hacemos
        if 'concordia' in low:review.setdefault(year,{})[g['grupo']]=D('#5c6bc0')
        # Innovación Federal 2025 conserva el azul marino: el índigo se confundía con el violeta de LLA
    for code,g in bycode.items():
        if 'fuerza republicana' in g['grupo'].lower():review.setdefault(year,{})[g['grupo']]=dict(base='#7b3f00')   # color fijo del proyecto
        # Chubut Somos Todos / para Todos: verde lima, distinto del menta del peronismo federal/CF y del verde de JSRN
        if re.search(r'chubut (somos|para) todos',g['grupo'].lower()):review.setdefault(year,{})[g['grupo']]=dict(base='#9ccc65')
    for frag,ref in review.get(year,{}).items():
        for code,g in bycode.items():
            if frag.lower() in g['grupo'].lower():
                for k in ('bar','txt'):CAND[code].pop(k,None)
                CAND[code].update({k:ref[k] for k in ('base','bar','txt') if k in ref})
    rename={2017:{'peronismo no kirchnerista':'Peronismo no kirchnerista','Unidad Ciudadana y el kirchnerismo':'Unidad Ciudadana'},
            2021:{'Tercera vía y el Peronismo Federal':'Tercera Vía y Peronismo Federal'},
            2023:{'Libertad Avanza':'La Libertad Avanza'}}
    for c in bycode:
        CAND[c]['n']=rename.get(year,{}).get(CAND[c]['n'],CAND[c]['n'])
    for c,g in bycode.items():
        if original_colors[c].lower()!=CAND[c]['base'].lower():
            changes.append(f'Color final de {g["grupo"]}: {CAND[c]["base"]}; tabla de Wikipedia: {original_colors[c]}. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.')
    for candidate in CAND.values():
        rgb=[int(candidate['base'][i:i+2],16) for i in (1,3,5)]
        if 'bar' not in candidate and sum(a*b for a,b in zip(rgb,(.2126,.7152,.0722)))>165:
            candidate['bar']='#'+''.join(f'{round(c*.66):02x}' for c in rgb)
            candidate['txt']=candidate['bar']
    CAND['P_BLA']=dict(n='Votos en blanco',base='#b5b5b5');CAND['P_NUL']=dict(n='Nulos, recurridos e impugnados',base='#8a8a8a')
    for r in maprows:
        CAND[f"P_{r['distrito']}_{r['lista']}"]=dict(n=r['nombre'],base=CAND[r['codigo']]['base'] if r['codigo'] else '#8c8c8c')

    # Padrón: sólo el publicado; no se infieren mesas escrutadas a partir de votos.
    if len(m):
        m['e']=pd.to_numeric(m.mesa_electores,errors='coerce').fillna(0).astype(int)
        elect=m.groupby(['distrito_id','seccion_id']).e.sum().to_dict()
    else:elect={}
    compath=ROOT/'../datos/fuentes_leg2003_2025/complementos_departamentales.json'
    complements=json.loads(compath.read_text(encoding='utf8')) if compath.exists() else []
    for c in complements:
        if c['year']==year:elect[(c['d'],c['s'])]=c['el']
    sections={}
    for (d,s),sub in v.groupby(['distrito_id','seccion_id']):
        names=sub.seccion_nombre.dropna().astype(str);name=next((n for n in names if n and n.lower()!='nan'),'')
        votes=sub[sub.votos_tipo=='POSITIVO'].groupby('agrupacion_id').v.sum().to_dict()
        b=defaultdict(int)
        for a,n in votes.items():b[listmap.get((d,a)) or f'L_{d}_{a}']+=int(n)
        sections[(d,s)]=dict(d=d,s=s,name=name,v={f'P_{d}_{a}':int(n) for a,n in votes.items()},b=dict(b),pos=int(sum(votes.values())),
                             bla=int(sub[sub.votos_tipo.isin(['BLANCO','EN BLANCO'])].v.sum()),nul=int(sub[sub.votos_tipo.isin(['NULO','RECURRIDO','IMPUGNADO'])].v.sum()),
                             el=int(elect.get((d,s),0)),note=invalid.get((d,s),''),invalid=(d,s) in invalid)
        for c in complements:
            if c['year']==year and (c['d'],c['s'])==(d,s):sections[(d,s)]['note']=c['source']
    merges={('08','002'):'001',('21','010'):'009',('21','014'):'013',('21','015'):'013'}
    # Sólo fusionar las secciones auxiliares identificadas, nunca departamentos nuevos.
    for key,target in merges.items():
        if key not in sections:continue
        src=sections[key]
        if src['name'] and norm(src['name']) not in ('','suburbios','paranacampana','rosariosecciones','rosariosuburbios','lacapitalsuburbios'):
            # INDRA conserva códigos de subsección pero puede darles el nombre de cabecera.
            continue
        dst=sections.setdefault((key[0],target),dict(src,s=target,v={},b={},pos=0,bla=0,nul=0,el=0,note='',invalid=False))
        for k in ('pos','bla','nul','el'):dst[k]+=src[k]
        for k in ('v','b'):
            for a,n in src[k].items():dst[k][a]=dst[k].get(a,0)+n
        dst['note']+=' Incluye la subsección electoral '+key[1]+'.'
        del sections[key]
    ant=sections.pop(('24','003'),None)
    idx={(u['prov'],norm(u['name'])):i for i,u in enumerate(U) if u['name']!='Islas Malvinas'}
    linked={};unmapped_units=[]
    for (d,s),rec in sections.items():
        p=D2P[d]
        if p=='Capital Federal':key=(p,norm(('Circ. %02d' if year<=2007 else 'Comuna %d')%int(s)))
        else:
            nn=norm(rec['name']); key=(p,nn)
            if key not in idx:key=(p,PROV_ALIASES.get((p,nn),ALIASES.get(nn,nn)))
        i=idx.get(key)
        if i is None:
            candidates=[k for k in idx if k[0]==p]
            exact=[k for k in candidates if norm(k[1])==norm(rec['name'])]
            if len(exact)==1:i=idx[exact[0]]
        if i is None:unmapped_units.append((p,s,rec['name']))
        else:
            assert i not in linked,('Secciones duplicadas',p,s)
            linked[i]=rec
    dump(folder/'sin_poligono.json',unmapped_units)
    if unmapped_units:raise ValueError(('Sin polígono',year,unmapped_units))
    return finish(year,U,folder,groups,bycode,CAND,linked,ant,maprows,unmatched,changes,text,tbl)

def finish(year,U,folder,groups,bycode,CAND,linked,ant,maprows,unmatched,changes,text,tbl):
    # Nacional: métricas de la tabla, sin sumar las bases territoriales.
    rs=rows(tbl)
    def metric(fragment,default=None):
        for r in rs:
            if fragment in r['nombre'].lower():return r['votos']
        if default is not None:return default
        raise ValueError(('Métrica nacional ausente',year,fragment))
    pos=metric('votos positivos',metric('votos afirmativos',metric('votos válidos',0)))
    if not pos:raise ValueError(('Sin positivos nacionales',year))
    bla=metric('votos en blanco',0);nul=metric('votos anulados',metric('votos nulos',0));ins=metric('electores registrados')
    # «Participación» es la fila de métricas (colspan=3), no un partido con esa palabra en el nombre (Partido de Participación, 2003-2007; 2025)
    tot=[r['votos'] for r in rs if 'colspan=3' in r['nombre'].replace(' ','') and 'particip' in r['nombre'].lower()]
    total=tot[0] if tot else pos+bla+nul
    if total>ins:   # 2011 y 2021: la tabla de la Wikipedia trae votantes y electores intercambiados
        changes.append(f'Tabla nacional de la Wikipedia con votantes ({total:,}) y electores ({ins:,}) intercambiados; se usan al revés.'.replace(',','.'))
        total,ins=ins,total
    solid=['La Pampa'] if year==2003 else []
    if solid:changes.append('La Pampa 2003: color provincial sólido con el definitivo DINE, página 2. La propia fuente declara que no recibió resultados por departamento; no se atribuye un resultado a cada departamento.')
    missing=[];unknown_winners=[];wins=Counter()
    for i,u in enumerate(U):
        if u['name']=='Islas Malvinas':continue
        if u['prov'] in solid:continue
        r=linked.get(i)
        if not r or r['invalid'] or not r['pos']:missing.append(f"{u['prov']}: {u['name']}");continue
        w=max(r['b'],key=r['b'].get)
        if w not in bycode:unknown_winners.append((u['prov'],u['name'],w))
        else:wins[w]+=1
    if ant and ant['pos']:wins[max(ant['b'],key=ant['b'].get)]+=1
    dump(folder/'ganadores_sin_agrupar.json',unknown_winners)
    if unknown_winners:raise ValueError(('Ganadores sin bloque Wikipedia',year,unknown_winners))
    win_codes=[c for c in bycode if wins[c]]
    national_votes={c:bycode[c]['total'] for c in win_codes}
    others=pos-sum(national_votes.values());assert others>=0,(year,others)
    W=dict(art=f'Elecciones legislativas de Argentina de {year}',blocs=national_votes,otros=others,positivos=pos,blancos=bla,dif=nul,total=total,inscriptos=ins,lab_pos='Votos positivos',lab_bla='Votos en blanco',lab_nul='Votos nulos / anulados')
    dump(folder/f'wiki_nacional_{year}.json',W)
    import wikitop
    wikitop.WIKI[year]=W
    cands,slices,partp,metrics=wikitop.national(year)
    # Los logos se incrustan sólo después de determinar los ganadores de unidades.
    logo_info=logos(year,win_codes,bycode,CAND,text,folder)
    control=[]
    for c,g in bycode.items():
        b=sum(r['votos'] for r in maprows if r['codigo']==c)
        control.append(dict(bloque=g['grupo'],codigo=c,base=b,wikipedia=g['total'],diferencia=b-g['total'],ganadas=wins[c]))
    pd.DataFrame(control).to_csv(folder/f'control_bloques_{year}.csv',index=False,encoding='utf-8-sig')
    note=f'Nacional: tabla de Wikipedia. Mapa: {"dat.ar (cotejado por unidad)" if year==2003 else "PolAr / Andy Tow (provisorio)" if year<2011 else "DINE, escrutinio provisorio"}. {description(year)}. No se imputan votos. Diferencias y faltantes en LEEME.'
    prov={}
    def add(r):
        p=D2P[r['d']];q=prov.setdefault(p,dict(d=r['d'],s='',name=p,v={},b={},pos=0,bla=0,nul=0,el=0,note='',invalid=False))
        for k in ('pos','bla','nul','el'):q[k]+=r[k]
        for k in ('v','b'):
            for a,n in r[k].items():q[k][a]=q[k].get(a,0)+n
    for r in linked.values():add(r)
    if ant:add(ant)
    if year==2003:
        vals=[('Frente para la Victoria - ARI - MID - Acción Desarrollista',28115,'Partido Justicialista y aliados'),('Movimiento de Unidad Popular',1913,'Partido Socialista Auténtico'),('Frente Alternativa Pampeana',40180,'Unión Cívica Radical y aliados'),('Partido Justicialista',76344,'Partido Justicialista y aliados'),('Partido Popular de la Reconstrucción',1397,'Partido Popular de la Reconstrucción (PPR)'),('Partido Humanista',2798,'Partido Humanista'),('Pueblo Nuevo',2783,'Pueblo Nuevo')]
        pv={};bb=defaultdict(int)
        for n,(lab,vv,block) in enumerate(vals):
            key=f'P_SOLID11_{n}';code=next((c for c,g in bycode.items() if g['grupo']==block),None)
            assert code,(lab,block)
            CAND[key]=dict(n=lab,base=CAND[code]['base']);pv[key]=vv;bb[code]+=vv
            maprows.append(dict(distrito='11',provincia='La Pampa',lista=f'PROV{n}',nombre=lab,bloque=block,codigo=code,votos=vv,nivel='provincia (color sólido)',fuente='DINE definitivo, la_pampa_2003_archivo.pdf, página 2'))
        assert sum(pv.values())==153530
        prov['La Pampa']=dict(d='11',s='',name='La Pampa',v=pv,b=dict(bb),pos=153530,bla=26627,nul=1353,el=223802,note='Resultado provincial definitivo DINE, página 2. Sin resultados por departamento informados según la nota del PDF; se pinta la provincia entera, sin dividir votos.',invalid=False)
        # El control incluye el total provincial sólido una sola vez.
        for row in control:
            vv=bb.get(row['codigo'],0);row['base']+=vv;row['diferencia']+=vv
        pd.DataFrame(control).to_csv(folder/f'control_bloques_{year}.csv',index=False,encoding='utf-8-sig')
        pd.DataFrame(maprows).to_csv(folder/f'mapeo_listas_{year}.csv',index=False,encoding='utf-8-sig')
    def record(r):
        if not r or not r['pos'] or r['invalid']:
            return dict(lines=[],metrics=[],fill=BEIGE,note=(r['note'] if r and r['note'] else 'Pendiente: sin resultado desagregado en la fuente. No se imputan votos.'))
        lines=[[c,n,round(100*n/r['pos'],2)] for c,n in sorted(r['v'].items(),key=lambda x:-x[1]) if n]
        emit=r['pos']+r['bla']+r['nul']
        for c,k in [('P_BLA','bla'),('P_NUL','nul')]:
            if r[k]:lines.append([c,r[k],round(100*r[k]/emit,2)])
        met=[['Votos positivos',num(r['pos'])],['Votantes',num(emit)]]
        msg=r['note']
        if r['el']:
            met.insert(0,['Inscriptos',num(r['el'])])
            if emit<=r['el']:met.append(['Participación',f"{100*emit/r['el']:.2f}".replace('.',',')+' %'])
            else:msg+=' Padrón inconsistente: votantes mayores que inscriptos; no se calcula participación.'
        w=max(r['b'],key=r['b'].get)
        out=dict(lines=lines,metrics=met,note=msg,w=w,q=round(100*r['b'][w]/r['pos'],2))
        return out
    # No copiar un total provincial a departamentos sin datos.
    unit_records=[record(linked.get(i)) for i in range(len(U))]
    for i,u in enumerate(U):
        if u['prov'] in solid:unit_records[i]=record(prov[u['prov']])
    for i,u in enumerate(U):
        if u['name']=='Islas Malvinas':unit_records[i]=dict(lines=[],metrics=[],fill=GREY,note='Sin voto argentino: islas bajo administración británica.')
    ant_record=record(ant)
    nat=dict(cands=cands,slices=slices,partp=partp,metrics=metrics)
    keys=[[BEIGE,'Sin resultado desagregado / pendiente']]
    modes=[dict(id='gan',tile='GANÓ',note=note,units=unit_records+[ant_record],prov={p:record(r) for p,r in prov.items()},national=nat,legend=dict(keys=keys))]
    specs=[]
    for c in sorted(bycode,key=lambda c:-bycode[c]['total'])[:4]:
        specs.append((c.lower(),short(bycode[c]['grupo']),lambda r,c=c:100*r['b'].get(c,0)/r['pos'],CAND[c]['base'],'% '+CAND[c]['n']))
    if year!=2003:specs.append(('par','PART',lambda r:100*(r['pos']+r['bla']+r['nul'])/r['el'] if r['el'] and r['pos']+r['bla']+r['nul']<=r['el'] else None,'#2a6f97','Participación sobre el padrón publicado (%)'))
    def tone(base,k):
        rgb=[int(base[j:j+2],16) for j in (1,3,5)];return '#'+''.join(f'{round(x*k):02x}' for x in rgb)
    for mid,tile,fn,color,title in specs:
        edges=[0,70,75,80,85,90,95] if mid=='par' else [0,10,20,30,40,50,60]
        cols=[tone(color,k) for k in (1,.85,.7,.55,.4,.3,.2)]
        def chor(rec,r):
            out={k:v for k,v in rec.items() if k not in ('w','q','fill')}
            q=fn(r) if r and r['pos'] and not r['invalid'] else None
            ix=max([i for i,e in enumerate(edges) if q>=e] or [0]) if q is not None else 0
            out['fill']=cols[ix] if q is not None else BEIGE
            return out
        un=[chor(unit_records[i],prov.get(u['prov']) if u['prov'] in solid else linked.get(i)) if u['name']!='Islas Malvinas' else unit_records[i] for i,u in enumerate(U)]
        un.append(chor(ant_record,ant))
        modes.append(dict(id=mid,tile=tile,note=note,units=un,prov={p:chor(record(r),r) for p,r in prov.items()},national=nat,
                          legend=dict(title=title,stops=[[c,('+' if i==6 else '')+str(e)+'%'] for i,(c,e) in enumerate(zip(cols,edges))],bars=False,keys=keys)))
    disp={i:(f"{u['name']} · {u['parroquia']}" if 'parroquia' in u else u['name']) for i,u in enumerate(U)}
    report=dict(year=year,geometry=description(year),solid=solid,units=len(U)+1,with_data=sum(bool(r and r['pos'] and not r['invalid']) for r in linked.values())+bool(ant and ant['pos']),missing=missing,
                antartida_sin_dato=not bool(ant and ant['pos']),winners={bycode[c]['grupo']:n for c,n in wins.items() if c in bycode},logos=logo_info,corrections=changes,unmatched_lists=unmatched,
                base_positivos=int(sum(r['votos'] for r in maprows)),wikipedia_positivos=pos,national=W)
    dump(folder/'control_cobertura.json',report)
    readme(year,folder,report,control)
    print(year,'unidades',report['units'],'con datos',report['with_data'],'pendientes',missing,'ganadores',report['winners'],flush=True)
    return SimpleNamespace(CAND=CAND,MODES=modes,disp=disp,ANT_I=len(U),report=report)

def logos(year,codes,bycode,CAND,text,folder):
    from PIL import Image
    meta=json.loads((ROOT/'../datos/fuentes_leg2003_2025/logos_metadata.json').read_text(encoding='utf8'))
    pages={norm(p['title'][5:]):p for p in meta.values() if p.get('imageinfo')}
    info=[]
    imfields=dict(re.findall(r'^[ \t]*\|[ \t]*imagen(\d+)[ \t]*=[ \t]*(.*?)[ \t]*$',text,re.M))
    votfields=dict(re.findall(r'^[ \t]*\|[ \t]*votos(\d+)[ \t]*=[ \t]*(.*?)[ \t]*$',text,re.M))
    imfields={k:re.sub(r'^(?:Archivo|File|Imagen):\s*','',v).strip() for k,v in imfields.items()}
    byvote={int(re.sub(r'\D','',v)):imfields[k] for k,v in votfields.items() if k in imfields and re.sub(r'\D','',v)}
    partyfields=dict(re.findall(r'^[ \t]*\|[ \t]*partido(\d+)[ \t]*=[ \t]*(.*?)[ \t]*$',text,re.M))
    byshort={short(clean(party)):imfields[k] for k,party in partyfields.items() if k in imfields and 'HSSamarbete' not in imfields[k]}
    fallback={'MPN':'Logo_MPN.png','PRS':'PRS_logo.png','FRC':'Frente_Renovador_de_la_Concordia_Social.png','PJ':'Flag_of_the_Justicialist_Party_(square_version).svg','UCR':'Escudo_de_la_UCR.svg','PRO':'Propuesta_Republicana.png','FPV':'Logo_Frente_para_la_Victoria.svg','FIT':'Frente_de_Izquierda_y_de_los_Trabajadores_Logo.svg','CF':'ACFederal.png','ARI':'Ari_Logo.svg','FPCyS':'Logo_FPCyS.png','FR':'Logo_Fuerza_Republicana.png','CC':'Coalición_Cívica.png'}
    for code in codes:
        g=bycode[code];title=byvote.get(g['total']) or byshort.get(short(g['grupo']))
        regional={'Juntos Somos Río Negro':'Logo JSRN Argentina.svg'}
        artpath=ROOT/'../datos/fuentes_leg2003_2025/logos_regionales_articulos.json'
        if artpath.exists():
            art=json.loads(artpath.read_text(encoding='utf8'))
            regional.update({p['title']:p['pageimage'] for p in art.get('query',{}).get('pages',{}).values() if p.get('pageimage')})
        for label,fn0 in regional.items():
            if label in g['grupo'] and not title:title=fn0
        if 'Frente Nuevo' in g['grupo'] and not title:title=regional.get('Frente Cívico de Córdoba')
        if 'Chubut para Todos' in g['grupo'] and not title:title=regional.get('Chubut Somos Todos')
        if 'Por Santa Cruz' in g['grupo'] and not title:title=regional.get('Somos Energía para Renovar Santa Cruz')
        if 'Por San Juan' in g['grupo'] and not title:title=regional.get('Producción y Trabajo')
        if 'Frente Popular Agrario' in g['grupo'] and not title:title=regional.get('Partido Agrario y Social')
        if 'Frente Primero Jujuy' in g['grupo'] and not title:title=regional.get('Primero Jujuy')
        p=pages.get(norm(title or ''))
        fn=None;reserve=False;license='';date='';source=''
        if p:
            safe=re.sub(r'[<>:"/\\|?*]','',p['title'][5:].replace(' ','_'))
            fn=ROOT/'../datos/fuentes_leg2003_2025/logos'/safe
            if not fn.exists():
                same=ROOT/'../logos'/p['title'][5:].replace(' ','_')
                if same.exists():fn=same
                exact_alias={'Logo La Libertad Avanza (sin águila).svg':'Logo_La_Libertad_Avanza_sin_aguila.svg','Logo Frente de Izquierda y de Trabajadores-Unidad.svg':'Logo_FIT_Unidad.svg','Logo de "Provincias Unidas".svg':'Logo_Provincias_Unidas.svg','Logo Union por la Patria.svg':'Logo_Union_por_la_Patria.svg'}
                if p['title'][5:] in exact_alias and (ROOT/'../logos'/exact_alias[p['title'][5:]]).exists():fn=ROOT/'../logos'/exact_alias[p['title'][5:]]
            ext=p['imageinfo'][0].get('extmetadata',{})
            date=clean(ext.get('DateTimeOriginal',{}).get('value',''))
            license=clean(ext.get('LicenseShortName',{}).get('value',''))
            source=p['imageinfo'][0].get('descriptionurl','')
            # Fecha del dibujo: no confundir con fecha de subida a Commons.
            yrs=[int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',date)]
            reserve=bool(yrs and max(yrs)>year)
            election_dates={2003:'2003-11-23',2005:'2005-10-23',2007:'2007-10-28',2011:'2011-10-23',2015:'2015-10-25',2017:'2017-10-22',2019:'2019-10-27',2021:'2021-11-14',2023:'2023-10-22',2025:'2025-10-26'}
            exact_date=re.search(r'\b(?:19|20)\d{2}-\d{2}-\d{2}\b',date)
            if exact_date and exact_date.group()>election_dates[year]:reserve=True
        if not fn or not fn.exists():
            local=fallback.get(short(g['grupo']))
            if short(g['grupo'])=='CF' and 'Compromiso Federal' not in g['grupo']:local=None
            fn=ROOT/'../logos'/local if local else None
            if fn and fn.exists():
                reserve=True;title=local;license='Ver LICENCIAS.md del proyecto';source='logos/LICENCIAS.md'
            else:fn=None
        # Nunca usar MODIN para PAUFE: son organizaciones diferentes.
        if short(g['grupo'])=='PAUFE' and fn and 'MODIN' in fn.name:fn=None
        # Por Santa Cruz 2023: emblema aportado por el usuario (21-oct-2026); el de SER es de otra alianza.
        if year==2023 and 'Por Santa Cruz' in g['grupo']:
            fn=ROOT/'../logos/Logo_Por_Santa_Cruz.png';title='Logo_Por_Santa_Cruz.png';reserve=False
            license='Aportado por el usuario; sin licencia libre verificada';source='logos/LICENCIAS.md';date='2023'
        if fn:
            if fn.suffix.lower()=='.svg':
                import resvg_py
                raw=bytes(resvg_py.svg_to_bytes(svg_path=str(fn),height=140))
                image=Image.open(io.BytesIO(raw)).convert('RGBA')
            else:image=Image.open(fn).convert('RGBA')
            bb=image.getbbox()
            if bb:image=image.crop(bb)
            if image.height>140:image.thumbnail((600,140),Image.Resampling.LANCZOS)
            b=io.BytesIO();image.save(b,'PNG')
            CAND[code].update(img='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode(),ar=round(image.width/image.height,4),bl=min(1.05,82/max(1,image.width/image.height)/27))
            from logo_paleta import paleta,cobertura
            CAND[code]['logpal']=paleta(image);CAND[code]['logcov']=cobertura(image)   # la leyenda usa la versión monocroma si el logo se confunde con la barra
        info.append(dict(code=code,grupo=g['grupo'],archivo=Path(fn).resolve().relative_to(ROOT.parent).as_posix() if fn else None,commons_title=title if fn else None,fecha_original=date,licencia=license,reserva_epoca=reserve,fuente=source))
    from bloques_wiki import aplicar
    for code,blk in aplicar(CAND,year):   # bloques de los mapas presidenciales de la Wikipedia (CC0)
        for x in info:
            if x['code']==code:x.update(bloque_wikipedia=f'logos/bloques_presidenciales/{blk}.png')
    dump(folder/'logos_usados.json',info)
    return info

def readme(year,folder,report,control):
    s=f'# Diputados nacionales {year}\n\nAtlas según el estilo del proyecto; compilación 20-oct-2026.\n\n'
    s+=f"Geometría: {report['geometry']}. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.\n\n"
    s+='Fuentes: '+('`raw/datar_2003_departamento_SIN_VALIDAR.csv` (dat.ar, resultados llamados definitivos por la fuente; cotejo de sumas por unidad)' if year==2003 else f'`datos_oficiales/{year}/agregado_polar.pkl` (PolAr/INDRA/Andy Tow, provisorio)' if year<2011 else f'`datos_oficiales/{year}/agregado.pkl` (DINE, escrutinio provisorio por mesa)')+'.\n\n'
    s+=f"El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_{year}); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman {num(report['base_positivos'])} positivos y la tabla nacional {num(report['wikipedia_positivos'])}. No se ajustan los votos locales para forzar igualdad. `control_bloques_{year}.csv` conserva todas las diferencias.\n\n"
    s+='Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.\n\n'
    if report.get('solid'):s+='Provincias en color sólido: '+', '.join(report['solid'])+'. Total provincial, sin inventar resultados departamentales.\n\n'
    s+='| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |\n|---|---:|---:|---:|---:|\n'
    for r in control:
        if r['ganadas']:s+=f"| {r['bloque']} | {num(r['base'])} | {num(r['wikipedia'])} | {r['diferencia']:+,} | {r['ganadas']} |\n"
    s+='\nFaltantes (beige, sin imputar): '+('; '.join(report['missing']) or 'ninguno en el continente')+'.\n'
    if report['antartida_sin_dato']:s+='Antártida sin resultado separado: beige.\n'
    if year in (2015,2017):s+='Tolhuin todavía no era un departamento en la fecha de esta elección: la ley provincial 1186 se sancionó el 27-oct-2017, después de los comicios del 22-oct-2017. Se conserva la división de Río Grande/Ushuaia del shapefile 2010. Fuente: https://www.legistdf.gob.ar/lp/leyes/Provinciales/LEYP1186.pdf\n'
    s+='\n'+'\n'.join(report['corrections'])+'\n\nLogos: ver `logos_usados.json` y `logos/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.\n\nEstado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.\n'
    (folder/f'LEEME_{year}.md').write_text(s,encoding='utf8')
