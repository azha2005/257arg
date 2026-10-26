"""Constructor compartido de diputados 1983/1989/1995/1999; reutiliza atlas históricos."""
from pathlib import Path
import sys, json, csv, collections, pickle, re, ast, unicodedata, base64, io
from PIL import Image
ROOT=Path(__file__).resolve().parent
def norm(s):
    s=re.sub(r'\s*-\s*\d+\s*$','',str(s))
    s=unicodedata.normalize('NFKD',str(s).lower())
    s=''.join(c for c in s if not unicodedata.combining(c))
    for a,b in [('gnral','general'),('gral','general'),('crnel','coronel'),('cnel','coronel'),('gdor','gobernador'),('pdte','presidente'),('sn','san')]:
        s=re.sub(r'\b'+a+r'\b',b,s)
    return re.sub(r'[^a-z0-9]','',s)
FAMS={
1983:dict(UCR='ucr',PJ='pj',PAL='aut liber',BLO='blo',MPN='mpn',MPJ='mpj',MFP='mfp',AF='af pd mlp lp demer fed',UCD='ucd cnc c',PI='pi',MID='mid',PC='pc',PDC='dc',ADS='ads pdp adp psd'),
1989:dict(PJ='frejupo fcr mpli ptp mid apro',UCR='ucr ucrfi ucrmc cfifed mov mpc',ADC='adc paldpml ucd adcucd pdp',CFI='cfi fed',IU='aiu',US='aus us psp ps psd',FR='fr',CR='cr',MPN='mpn',BLO='ablo',ACHA='acha',MPF='mpf',PPR='pri js'),
1995:dict(PJ='afjufe pj ucd afju frejupo afjen afjupo fjuvi afreet afcbio fjub fpv prs blo acha fed mpj mapjuj mpchu afjuso fj',UCR='ucr aucrpu aucrmid ucrp ucrfci afcs mid ucrfsol',FREP='afpaso fpaso acfg afgen fg afpais afg us',MOD='mod deli',PDP='pdp',PAL='palpdp',FR='frep',PD='pd',MPN='mpn',SUR='asur alsur ptp surptp pc',MPF='mpf'),
1999:dict(ALI='ali adp aftod alisal ali00 alisj palpdp alifcso frepaso fcystf fg dc',PJ='acjc cjc pj cjcer apj cjccha acjcfj afjes acjcmpu acjcfe acjc00 acjc01 acjc02 acjc03 pais nc mregp aciu jubacc cp ach mod fed fiydscz',AR='apr aapr aaprf aaprmpatp',UBO='ubo',PD='pd',FR='fr',MPN='mpn',IU='aiumst aiu aiupc iu pc mst msoct',MPF='mpf',PH='ph pheco'),
}
INFO={
'UCR':('Unión Cívica Radical','#e10019','Escudo_de_la_UCR.svg'),
'PJ':('Partido Justicialista','#318ce7','Flag_of_the_Justicialist_Party_(square_version).svg'),
'PAL':('Pacto Autonomista Liberal','#40e0d0','Pacto_Autonomista_Liberal_PL_PA.png'),
'BLO':('Partido Bloquista','#44944a','Estrella_bloquista.png'),
'MPN':('Movimiento Popular Neuquino','#14306e','Logo_MPN.png'),
'MPJ':('Movimiento Popular Jujeño','#17117d','Logo_Movimiento_Popular_Jujeno.png'),
'MFP':('Movimiento Federalista Pampeano','#f59e0b','Logo_Mofepa_limpio.png'),
'AF':('Alianza Federal','#f59e0b','ALIANZA_FEDERAL1983_2.png'),
'UCD':('Unión del Centro Democrático','#8e6bd8','UCEDE_logo_chico.png'),
'ADC':('Alianza de Centro','#8e6bd8','UCEDE_logo_chico.png'),
'PI':('Partido Intransigente','#d10047','Emblema_Partido_Intransigente.svg'),
'MID':('Integración y Desarrollo','#238443','Logo_MID.svg'),
'PC':('Partido Comunista','#b51d27',None),
'PDC':('Demócrata Cristiano','#2b3094',None),
'ADS':('Alianza Demócrata Socialista','#ff7f50','Escudo_del_PDP.svg'),
'CFI':('Confederación Federalista','#f59e0b','CFI_Confederacion_Federalista_Independiente.png'),
'IU':('Izquierda Unida','#a31515',None),
'US':('Unidad Socialista','#ff7f50','Emblema_del_Partido_Socialista_Argentino.svg'),
'FR':('Fuerza Republicana','#7b3f00','Logo_Fuerza_Republicana.png'),
'CR':('Cruzada Renovadora','#004d40','Cruzada_Renovadora_San_Juan.png'),
'ACHA':('Acción Chaqueña','#9a6b32',None),
'MPF':('Movimiento Popular Fueguino','#0097a7','Logo_MOPOF_Fueguino.png'),
'PPR':('Provincial Rionegrino','#467847','Partido_Provincial_Rionegrino.png'),
'FREP':('Frente País Solidario','#a349a4','Logo_FREPASO_remake.png'),
'MOD':('MODIN','#e67e22','Logo_MODIN.png'),
'PDP':('Demócrata Progresista','#005c9e','Escudo_del_PDP.svg'),
'PD':('Partido Demócrata','#1f4096','Escudo_del_Partido_Democrata.svg'),
'SUR':('Alianza Sur','#a31515',None),
'ALI':('Alianza','#dc0143','Alianza.png'),
'AR':('Acción por la República','#3e5298','Logo_Accion_por_la_Republica.svg'),
'UBO':('Unidad Bonaerense','#e6aa24',None),
'PH':('Partido Humanista','#ff8800',None),
}
NATIONAL={
1983:dict(UCR=7104748,PJ=5697610,PAL=113482,BLO=61737,MPN=36168,MPJ=26535,MFP=16490,AF=169585,UCD=251541,PI=411883,MID=223763,PC=182296,PDC=139881,ADS=125085),
1989:dict(PJ=7460488,UCR=4865835,ADC=1796271,CFI=565080,IU=580943,US=451177,FR=213957,CR=87273,MPN=49070,BLO=39171,ACHA=45298,MPF=2309,PPR=22331),
1995:dict(PJ=8371132,UCR=3718920,FREP=3599764,MOD=311987,PDP=158857,PAL=158269,FR=119546,PD=114581,MPN=60781,SUR=83434,MPF=7683),
1999:dict(ALI=8497076,PJ=7153786,AR=1502732,UBO=289860,PD=235357,FR=99572,MPN=89798,IU=150493,MPF=4562,PH=144712),
}
MET={1983:(14811231,451756,87199,15350186,17929951,0),1989:(16645516,307578,99482,17092120,20034252,39544),1995:(16953823,1087334,122995,18202652,22177954,38500),1999:(18516870,1122980,192862,19832712,24107414,0)}
def logo(fn):
    p=ROOT/'logos_wikipedia'/fn
    if p.suffix=='.svg':
        data=p.read_bytes(); mime='image/svg+xml'
        m=re.search(r'viewBox="([\d.\s-]+)"',data.decode()); vals=list(map(float,m[1].split())) if m else [0,0,1,1]; ar=vals[2]/vals[3]
    else:
        im=Image.open(p).convert('RGBA');ar=im.width/im.height;im.thumbnail((400,300)); b=io.BytesIO();im.save(b,format='PNG');data=b.getvalue();mime='image/png'
    return dict(img='data:'+mime+';base64,'+base64.b64encode(data).decode(),ar=ar,bl=min(1.1,98/(ar*42)))
def build(year):
    folder=ROOT/f'mapa{year}dip';folder.mkdir(exist_ok=True)
    srcyear=2001 if year==1999 else year
    src=ROOT/f'mapa{srcyear}'
    original=json.loads((src/f'dataset_{srcyear}.json').read_text(encoding='utf8'))
    units=sorted(pickle.load(open(src/'units_raw.pkl','rb')),key=lambda u:(u['prov'],u['name']))
    assert len(units)==len(original['territories'])
    aliases={}
    for sy in [1983,1985,1987,1989,1991,1993,1995,1997,2001]:
        tree=ast.parse((ROOT/f'mapa{sy}/build_{sy}.py').read_text(encoding='utf-8-sig'))
        for node in tree.body:
            val=None
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EALIAS' for t in node.targets) and isinstance(node.value,ast.Dict): val=node.value
            if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='EALIAS' and node.value.func.attr=='update': val=node.value.args[0]
            if val:
                for (p,n),target in ast.literal_eval(val).items(): aliases.setdefault((p,norm(n)),set()).add(norm(target))
    index={(u['prov'],norm(u['name'])):i for i,u in enumerate(units)}
    extra={('Buenos Aires','General Lamadrid'):'Gnral.La Madrid',('Buenos Aires','AMEGHINO'):'Florentino Ameghino',('Buenos Aires','CNEL. ROSALES'):'Coronel de Marina Leonardo Rosales',('Buenos Aires','GONZALES CHAVEZ'):'Adolfo Gonzales Chaves',('Buenos Aires','GRAL. MADARIAGA'):'Gnral.Juan Madariaga',('Buenos Aires','JUAREZ'):'Benito Juarez',('Buenos Aires','MALVINAS ARGENTINA'):'Malvinas Argentinas',('Buenos Aires','PERON'):'Presidente Perón',('Buenos Aires','TORDILLIO'):'Tordillo',('Buenos Aires','TRENQUE LAUNQUEN'):'Trenque Lauquen',('Buenos Aires','VEINTICINCO DE MAYO'):'25 de Mayo',('Córdoba','r. saenz peña'):'Pdte.Roque Saenz Peña',('Corrientes','sl del palmar'):'San Luis del Palmar',('La Pampa','quemu'):'Quemú Quemú',('La Rioja','f. varela'):'Crnel.Felipe Varela',('La Rioja','gral ortiz de ocampo'):'General Ocampo',('San Luis','Pedernera'):'Gnral.Pedernera',('San Luis','San Martin'):'Libertador Gral.Sn Martín',('Tierra del Fuego','Ushuia'):'Ushuaia'}
    for (p,n),v in extra.items():aliases.setdefault((p,norm(n)),set()).add(norm(v))
    def find(p,n):
        if p=='Capital Federal' and n.isdigit(): return index.get((p,norm('Circ. %02d'%int(n))))
        candidates={norm(n)}|aliases.get((p,norm(n)),set())
        hits={index[(p,v)] for v in candidates if (p,v) in index}
        return next(iter(hits)) if len(hits)==1 else None
    names_by_code={}
    for y in [1983,1985,1987,1989,1991,1993,1995,1997]:
        for r in csv.DictReader(open(ROOT/f'base8399/ernesto/{y}_diputados/dpto_partidos.csv',encoding='utf-8-sig')):
            if not r['departamento'].isdigit(): names_by_code.setdefault(r['codigo_indra'],r['departamento'])
    labels={}
    for sy in [1983,1985,1987,1989,1991,1993,1995,1997,2001]:
        tree=ast.parse((ROOT/f'mapa{sy}/build_{sy}.py').read_text(encoding='utf-8-sig'))
        for node in tree.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LABEL' for t in node.targets) and isinstance(node.value,ast.Dict):
                try: labels.update(ast.literal_eval(node.value))
                except (ValueError,TypeError): pass
    fam={c:b for b,cs in FAMS[year].items() for c in cs.split()}
    def bloc(c,p):
        if year==1995:
            if c=='fr': return 'FREP' if p=='Tucumán' else 'MOD'
            if c=='fed' and p=='Córdoba': return 'UCR'
        if year==1999 and c=='ucd': return 'AR' if p=='Santa Fe' else 'PJ'
        if year==1999 and c=='cjccat': return 'PJ'
        if year==1999 and c in ('nmov','fifnc'): return 'PJ'
        if year==1999 and c=='pais' and p=='Salta':return 'ALI'
        return fam.get(c,'P_'+c)
    ent={}
    for r in csv.DictReader(open(ROOT/f'base8399/ernesto/{year}_diputados/dpto_partidos.csv',encoding='utf-8-sig')):
        p,n=r['provincia'],r['departamento'];n=names_by_code.get(r['codigo_indra'],n) if n.isdigit() and p!='Capital Federal' else n
        e=ent.setdefault((p,n),dict(p=p,n=n,P=collections.Counter(),m=collections.Counter()))
        c=r['codigo_partido'];v=float(r['votos']);assert v==int(v),(r,v);v=int(v)
        if r['tipo_fila']=='agrupacion' and not re.fullmatch(r'pos\d*',c): e['P'][bloc(c,p)]+=v
        elif r['tipo_fila'] in e['m']:
            # Fila de métrica repetida en la base (positivos en San Juan 1995, total en Río Negro 1983, electores en Córdoba 1999): vale la primera.
            e.setdefault('dups',[]).append(f"{r['tipo_fila']} {v:,}".replace(',','.'))
        else: e['m'][r['tipo_fila']]=v
    # Ibicuy es parte de Gualeguaychú en 1980; no se fusionan divisiones posteriores en 1995/99.
    if year in (1983,1989):
        keys={ (p,norm(n)):(p,n) for p,n in ent}
        ik=keys.get(('Entre Ríos',norm('islas de ibicuy')));gk=keys.get(('Entre Ríos',norm('gualeguaychu')))
        if ik and gk:
            e=ent.pop(ik);ent[gk]['P'].update(e['P']);ent[gk]['m'].update(e['m']);ent[gk]['note']='Incluye Islas del Ibicuy, contenido en Gualeguaychú en la geometría de 1980.'
        if year==1989:
            for p,n,old in [('Buenos Aires','Tres Lomas','Pellegrini'),('Jujuy','palpala','capital')]:
                ik=keys.get((p,norm(n)));gk=keys.get((p,norm(old)))
                if ik and gk:
                    e=ent.pop(ik);ent[gk]['P'].update(e['P']);ent[gk]['m'].update(e['m']);ent[gk]['note']=f'Incluye {n}, contenido en {old} en la geometría de 1980.'
    if year in (1995,1999):
        for p,n in list(ent):
            if p=='Tierra del Fuego' and norm(n) in ('sectorantarticoargentino','antartida'):
                e=ent.pop((p,n)); target=next(k for k in ent if k[0]==p and norm(k[1]) in ('ushuaia','ushuia'))
                ent[target]['P'].update(e['P']);ent[target]['m'].update(e['m']);ent[target]['note']='Incluye la fila del Sector Antártico Argentino de la base.'
    if year==1999:
        # Corrientes trae el lema ACJC00 y sus tres sublemas: contar una sola vez.
        for e in ent.values():
            if e['p']=='Corrientes':
                raw=[r for r in csv.DictReader(open(ROOT/'base8399/ernesto/1999_diputados/dpto_partidos.csv',encoding='utf-8-sig')) if r['provincia']==e['p'] and r['departamento']==e['n'] and r['tipo_fila']=='agrupacion']
                vv={r['codigo_partido']:int(float(r['votos'])) for r in raw}
                if 'acjc00' in vv:
                    children=sum(vv.get(c,0) for c in ('acjc01','acjc02','acjc03'))
                    e['P']['PJ']-=children;e['note']=f'Corrientes: se usa el lema ACJC00 ({vv["acjc00"]} votos), sin sumar de nuevo los sublemas ACJC01/02/03 ({children}); las diferencias entre ambos niveles se conservan.'
    # Celdas en 0 de una fuerza mayor cuyo residuo (positivos declarados menos suma partidaria) es exactamente
    # lo que falta frente a la tabla provincial de Wikipedia: se imputa el residuo, con nota (regla del proyecto).
    IMPUTE={1983:[('Misiones','capital','UCR','Unión Cívica Radical'),('Salta','capital','PJ','Partido Justicialista'),('Catamarca','andalgala','PJ','Partido Justicialista'),('San Luis','chacabuco','UCR','Unión Cívica Radical')]}
    if IMPUTE.get(year):
        wikirows=json.loads((folder/'wiki_prov_listas.json').read_text(encoding='utf8'))
        for p,n,b,wname in IMPUTE[year]:
            e=ent[(p,n)];gap=e['m']['positivos']-sum(e['P'].values())
            prov_base=sum(x['P'][b] for x in ent.values() if x['p']==p)
            wv=next(r['votos'] for r in wikirows if r['provincia']==p and r['nombre']==wname)
            assert e['P'][b]==0 and gap>0 and wv-prov_base==gap,(p,n,b,gap,wv-prov_base)
            e['P'][b]=gap
            e['note']=f'La base trae 0 votos para {wname} en este departamento; la diferencia entre los positivos declarados y la suma de las demás fuerzas ({gap:,} votos) coincide exactamente con lo que falta frente al total provincial de Wikipedia, así que se imputa ese residuo.'.replace(',','.')
            e['imputado']=dict(bloque=b,votos=gap)
    if year==1995:
        # Córdoba: la base no trae la columna del Partido Federal (Wikipedia: 14.915 votos, sumados a la UCR como en la tabla nacional).
        # El residuo de cada departamento entre positivos declarados y suma partidaria suma lo mismo: se imputa a UCR con nota.
        cba=[e for e in ent.values() if e['p']=='Córdoba']
        gaps={id(e):e['m']['positivos']-sum(e['P'].values()) for e in cba}
        assert abs(sum(gaps.values())-14915)<=1 and min(gaps.values())>=0,sum(gaps.values())
        for e in cba:
            g=gaps[id(e)]
            if g:
                e['P']['UCR']+=g;e['imputado']=dict(bloque='UCR',votos=g)
                e['note']=f'La base no trae la columna del Partido Federal en Córdoba; se imputa a la UCR (con la que suma la tabla nacional de Wikipedia) el residuo entre positivos declarados y suma de las fuerzas: {g:,} votos.'.replace(',','.')
    matched={};unmatched=[]
    for (p,n),e in ent.items():
        i=find(p,n)
        if i is None: unmatched.append((p,n));continue
        assert i not in matched,(p,n,units[i]['name'])
        matched[i]=e
    if year==1995:
        for e in matched.values():
            if e['p']=='Santa Cruz' and norm(e['n'])=='deseado':
                assert e['m']['total']==232 and e['m']['electores']==34173
                wikirows=json.loads((folder/'wiki_prov_listas.json').read_text(encoding='utf8'))
                wikiv={r['nombre']:r['votos'] for r in wikirows if r['provincia']=='Santa Cruz'}
                partyrows={'pj':'Partido Justicialista','ucr':'Encuentro Santacruceño','fpaso':'Frente País Solidario','fut':'Frente Unidad de los Trabajadores','mod':'Movimiento por la Dignidad y la Independencia','muscz':'Movimiento Unidad Santacruceña'}
                others=[r for r in matched.values() if r['p']=='Santa Cruz' and r is not e]
                original_record=dict(P=dict(e['P']),m=dict(e['m']))
                residuals={bloc(c,'Santa Cruz'):wikiv[name]-sum(o['P'][bloc(c,'Santa Cruz')] for o in others) for c,name in partyrows.items()}
                assert all(v>=0 for v in residuals.values()),residuals
                e['P']=collections.Counter(residuals)
                for code,name in [('positivos','Votos positivos'),('blancos','Votos en blanco'),('nulos','Votos nulos'),('total','Participación'),('electores','Electores registrados')]:
                    e['m'][code]=wikiv[name]-sum(o['m'][code] for o in others)
                assert sum(e['P'].values())==e['m']['positivos']
                assert e['m']['positivos']+e['m']['blancos']+e['m']['nulos']==e['m']['total']
                e['note']='Extrapolado por pedido del usuario (19-oct-2026): total provincial de Wikipedia menos los otros seis departamentos de Santa Cruz, fuerza por fuerza y para positivos, blancos, nulos, votantes e inscriptos. No es un resultado departamental observado.'
                e['extrapolado']=dict(original=original_record,resultado=dict(P=dict(e['P']),m=dict(e['m'])),metodo=e['note'])
                (folder/'deseado_extrapolado.json').write_text(json.dumps(e['extrapolado'],ensure_ascii=False,indent=2),encoding='utf8')
    (folder/'sin_emparejar.json').write_text(json.dumps(unmatched,ensure_ascii=False,indent=2),encoding='utf8')
    if unmatched: print(year,'SIN EMPAREJAR',unmatched);return
    def aggregate(entries):
        out=dict(P=collections.Counter(),m=collections.Counter())
        for e in entries: out['P'].update(e['P']);out['m'].update(e['m'])
        return out
    provinces={p:aggregate(e for e in matched.values() if e['p']==p) for p in sorted({e['p'] for e in matched.values()})}
    # Provincias sin datos departamentales en la base: color sólido con el total provincial de Wikipedia (DATA.solid), como San Luis en 1997.
    solid={}
    SOLIDMAP={1999:{'San Luis':{'Alianza para el Trabajo, la Justicia y la Educación':'ALI','Frente Justicialista Unión por San Luis':'PJ'},'Santa Cruz':{'Alianza para el Trabajo, la Justicia y la Educación':'ALI','Partido Justicialista':'PJ','Partido Humanista':'PH'}}}
    extra_names={}
    for p,mp in SOLIDMAP.get(year,{}).items():
        assert p not in provinces,p
        meta={'Votos positivos':'positivos','Votos en blanco':'blancos','Votos nulos':'nulos','Participación':'total','Electores registrados':'electores'}
        e=dict(p=p,n=p,P=collections.Counter(),m=collections.Counter())
        for r in json.loads((folder/'wiki_prov_listas.json').read_text(encoding='utf8')):
            if r['provincia']!=p:continue
            if r['nombre'] in meta:e['m'][meta[r['nombre']]]=r['votos'];continue
            code=mp.get(r['nombre']) or 'P_w'+norm(r['nombre'])[:12]
            extra_names[code]=r['nombre'];e['P'][code]+=r['votos']
        assert sum(e['P'].values())==e['m']['positivos'] and e['m']['positivos']+e['m']['blancos']+e['m']['nulos']==e['m']['total'],(p,e)
        e['note']=f'Total provincial según Wikipedia (Elecciones legislativas de Argentina de {year}): la base de Ernesto no trae los departamentos de {p}, así que el mapa pinta toda la provincia con este resultado, sin detalle departamental.'
        provinces[p]=solid[p]=e
    allcodes=set().union(*(set(e['P']) for e in list(matched.values())+list(solid.values())))
    candidates={}
    for c in allcodes:
        name,col,fn=INFO.get(c,(extra_names.get(c) or labels.get(c[2:],c[2:].upper()),'#9a9a9a',None))
        display={'UCR':('Unión Cívica Radical','y aliados'),'PJ':('Partido Justicialista','y aliados'),'MPN':('Movimiento Popular Neuquino','Neuquén'),'MFP':('Federalista Pampeano','MOFEPA'),'PAL':('Pacto Autonomista Liberal','Corrientes'),'CFI':('Confederación Federalista','Independiente'),'ADC':('Alianza de Centro','UCeDé y aliados'),'FREP':('Frente País Solidario','FREPASO'),'AR':('Acción por la República','y aliados')}
        dn,sub=display.get(c,(name,''))
        if c=='PAL':dn,sub='Pacto Autonomista','Liberal · Corrientes'
        if c=='PJ' and year==1989:dn,sub,fn='FREJUPO','Frentes justicialistas','Frejupo_logo_1989.png'
        if c=='PJ' and year==1999:dn,sub='Concertación Justicialista','y aliados';fn='Concertacion_Justicialista_1999.png'
        if c=='ALI':sub='UCR, FREPASO y aliados'
        candidates[c]=dict(n=dn,sub=sub,base=col,logo=c,minor=c.startswith('P_'))
        if fn:candidates[c].update(logo(fn))
        if c=='PJ' and year==1989:candidates[c]['bl']=0.6
    for c,n,col in [('P_BLA','En blanco','#cccccc'),('P_NUL','Anulados','#aaaaaa')]:candidates[c]=dict(n=n,base=col,minor=True)
    fmt=lambda v:f'{v:,}'.replace(',','.')
    def rec(e):
        if e.get('pending'):return dict(lines=[],metrics=[],fill='#e8ddc7',note=e['pending'])
        P=e['P'];m=e['m'];pos=sum(P.values()) or m.get('positivos',0);tot=m.get('total') or pos+m.get('blancos',0)+m.get('nulos',0)
        if not sum(P.values()):return dict(lines=[],metrics=[],fill='#e8ddc7',note='Pendiente: sin votos departamentales en la base.')
        w=max(P,key=P.get)
        met=[['Votos positivos',fmt(pos)],['Votantes',fmt(tot)]]
        badpad=bool(m.get('electores')) and tot>m['electores']
        if m.get('electores'):met += [['Inscriptos',fmt(m['electores'])]]+([] if badpad else [['Participación',f'{100*tot/m["electores"]:.2f} %'.replace('.',',')]])
        lines=[[c,v,round(100*v/pos,2)] for c,v in P.most_common() if v>0]
        lines += [[c,m.get(k,0),round(100*m.get(k,0)/tot,2)] for c,k in [('P_BLA','blancos'),('P_NUL','nulos')] if m.get(k)]
        notes=[e.get('note','')]
        gap=m.get('positivos',pos)-pos
        if gap:notes.append('La base declara '+fmt(m['positivos'])+' votos positivos y la suma de las fuerzas da '+fmt(pos)+' (diferencia: '+fmt(gap)+'); los porcentajes se calculan sobre la suma. No se imputa.')
        if badpad:notes.append('La base trae menos inscriptos ('+fmt(m['electores'])+') que votantes ('+fmt(tot)+'): padrón inconsistente, sin dato de participación.')
        if e.get('dups'):notes.append('Filas repetidas en la base, descartadas: '+', '.join(e['dups'])+'.')
        return dict(w=w,q=round(100*P[w]/pos,2),lines=lines,metrics=met,note=' '.join(x for x in notes if x))
    pending=dict(lines=[],metrics=[],fill='#e8ddc7',note='Pendiente: sin datos departamentales en la base de Ernesto. No se imputan votos.')
    mal=dict(lines=[],metrics=[],fill='#a9a9a9',note='Sin votación: Islas Malvinas.')
    def unitrec(i,u):
        if i in matched:return rec(matched[i])
        if u['prov'] in solid:return rec(solid[u['prov']])
        return dict(mal if u['name']=='Islas Malvinas' else pending)
    records=[unitrec(i,u) for i,u in enumerate(units)]
    srcent=lambda i:matched.get(i) or solid.get(units[i]['prov'])
    provrecords={p:rec(e) for p,e in provinces.items()}
    for p in {u['prov'] for u in units}:provrecords.setdefault(p,dict(pending))
    wins=collections.Counter(r.get('w') for i,r in enumerate(records) if r.get('w') and i in matched)
    wins.update(rec(e)['w'] for e in solid.values())
    assert not [c for c in wins if c not in NATIONAL[year]],('Ganador sin topline',wins)
    pos,bla,nul,total,ins,dif=MET[year]
    import wikitop
    key=f'{year}_diputados'
    assert set(wikitop.WIKI[key]['blocs'])==set(wins),(year,wins)
    national=dict(zip(('cands','slices','partp','metrics'),wikitop.national(key)))
    note=f'Fuente departamental: base de Ernesto Calvo, diputados nacionales {year}. Resultado nacional: tabla del artículo de Wikipedia. Geometría y recuadros: atlas del proyecto. Sin imputar diferencias; ver LEEME_{year}dip.md.'
    modes=[dict(id='gan',tile='GANÓ',note=note,units=records,prov=provrecords,national=national,legend=dict(keys=[['#e8ddc7','Pendiente de datos departamentales']]))]
    leaders=sorted(NATIONAL[year],key=lambda c:-NATIONAL[year][c])[:3]
    for c in leaders:
        edges=[0,10,20,30,40,50,60]; col=INFO[c][1];rgb=[int(col[i:i+2],16) for i in (1,3,5)]
        shades=['#'+''.join(f'{round(255+(v-255)*(0.12+0.88*j/6)):02x}' for v in rgb) for j in range(7)]
        def color(e):
            if e.get('pending'):return '#e8ddc7'
            den=sum(e['P'].values());p=100*e['P'][c]/den if den else 0
            return shades[max(j for j,x in enumerate(edges) if p>=x)]
        rr=[dict(records[i],fill=color(srcent(i))) if srcent(i) else dict(records[i]) for i in range(len(units))]
        pv={p:dict(provrecords[p],fill=color(e)) for p,e in provinces.items()}
        for p,r in provrecords.items():pv.setdefault(p,dict(r))
        modes.append(dict(id=c.lower(),tile=c,note=note,units=rr,prov=pv,national=national,legend=dict(title='% '+INFO[c][0],stops=list(zip(shades,[f'{x} %' for x in edges])),bars=False,keys=[['#e8ddc7','Pendiente de datos departamentales']])))
    electorate_missing=[i for i,e in matched.items() if not e['m'].get('electores')]
    if not electorate_missing:
        edges=[0,70,75,80,85,90,95];shades=['#e5eff5','#c1d9e8','#96bfd6','#6a9fbd','#447e9e','#245d7c','#0b3b57']
        def turnout(e):
            if e.get('pending'):return '#e8ddc7'
            m=e['m'];v=100*(m.get('total') or sum(e['P'].values())+m.get('blancos',0)+m.get('nulos',0))/m['electores']
            if v>100:return '#cfcfcf'
            return shades[max(j for j,x in enumerate(edges) if v>=x)]
        rr=[dict(records[i],fill=turnout(srcent(i))) if srcent(i) else dict(records[i]) for i in range(len(units))]
        okpad=lambda x:x['m'].get('electores') and x['m'].get('total',0)<=x['m']['electores']
        pv={p:dict(provrecords[p],fill=turnout(aggregate(x for x in matched.values() if x['p']==p and okpad(x)))) for p,e in provinces.items()}
        for p,r in provrecords.items():pv.setdefault(p,dict(r))
        modes.append(dict(id='par',tile='PART',note=note,units=rr,prov=pv,national=national,legend=dict(title='Participación',stops=list(zip(shades,[f'{x} %' for x in edges])),bars=False,keys=[['#e8ddc7','Pendiente de datos departamentales'],['#cfcfcf','Padrón inconsistente en la base']])))
    original.update(slug=f'legislativas_{year}',title='Elecciones legislativas de Argentina de',year=str(year),candidates=candidates,modes=modes,sets={'1':dict(label=str(year),subtitle='Diputados nacionales')})
    original.pop('solid',None)
    if solid:original['solid']=sorted(solid)
    payload=json.dumps(original,ensure_ascii=False,separators=(',',':'))
    (folder/f'dataset_{year}dip.json').write_text(payload,encoding='utf8')
    html=(src/f'atlas_{srcyear}.html').read_text(encoding='utf8')
    html,n=re.subn(r'const DATA=.*?;\n',lambda m:'const DATA='+payload+';\n',html,count=1);assert n==1
    html=re.sub(r'<title>.*?</title>',f'<title>Legislativas {year} · Diputados nacionales</title>',html,count=1)
    html=html.replace('return out.slice(0,4);','return out.slice(0,5);')
    html=html.replace('const MANY=N.cands.length>5','const MANY=N.cands.length>4')
    html=html.replace('const list=tilesNow(),xs=[1262,1316,1370,1424];','const list=tilesNow(),xs=tilesNow().length>4?[1208,1262,1316,1370,1424]:[1262,1316,1370,1424];')
    (folder/f'atlas_{year}_diputados.html').write_text(html,encoding='utf8')
    sums=aggregate(list(matched.values())+list(solid.values()))['P']
    audit=dict(year=year,ganadores=dict(wins),unidades=len(units),con_datos=len(matched),sin_dato=[dict(prov=u['prov'],nombre=u['name']) for i,u in enumerate(units) if i not in matched and u['prov'] not in solid],solidas={p:dict(P=dict(e['P']),m=dict(e['m'])) for p,e in solid.items()},comparacion=[dict(bloque=c,base=sums[c],wikipedia=v,diferencia=sums[c]-v) for c,v in NATIONAL[year].items()],mapeo=FAMS[year],wiki_entry=wikitop.WIKI[key],provincias={p:dict(e['P']) for p,e in provinces.items()})
    audit['imputados']=[dict(prov=e['p'],nombre=e['n'],**e['imputado']) for e in matched.values() if e.get('imputado')]
    audit['filas_repetidas']=[dict(prov=e['p'],nombre=e['n'],descartadas=e['dups']) for e in matched.values() if e.get('dups')]
    audit['positivos_distintos']=[dict(prov=e['p'],nombre=e['n'],declarados=e['m']['positivos'],suma=sum(e['P'].values())) for e in matched.values() if e['m'].get('positivos') and e['m']['positivos']!=sum(e['P'].values())]
    audit['padron_inconsistente']=[dict(prov=e['p'],nombre=e['n'],inscriptos=e['m']['electores'],votantes=e['m'].get('total')) for e in matched.values() if e['m'].get('electores') and e['m'].get('total',0)>e['m']['electores']]
    audit['registros_incompletos']=[dict(prov=e['p'],nombre=e['n'],nota=e['pending']) for e in matched.values() if e.get('pending')]
    audit['registros_extrapolados']=[dict(prov=e['p'],nombre=e['n'],**e['extrapolado']) for e in matched.values() if e.get('extrapolado')]
    (folder/'auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
    print(year,'ganadores',dict(wins),'unidades',len(units),'datos',len(matched),'faltantes',audit['sin_dato'])
    print('COMPARACION',audit['comparacion'])
if __name__=='__main__':
    for y in map(int,sys.argv[1:] or [1983,1989,1995,1999]):build(y)

