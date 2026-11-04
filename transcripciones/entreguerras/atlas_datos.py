"""Adaptación de datos al contrato de los atlas históricos ya publicados."""
from pathlib import Path
from collections import Counter, defaultdict
import base64, copy, json
from datos import load, export, NATIONAL, ROOT

HERE=Path(__file__).resolve().parent
NO_ELECCION={1918:{'San Luis'},1920:{'Catamarca'},1926:{'San Luis'},1937:set(),1940:{'Catamarca','Jujuy','La Rioja','Salta','San Juan'}}
TERR={'Chaco','Chubut','Formosa','La Pampa','Misiones','Neuquén','Río Negro','Santa Cruz','Tierra del Fuego'}

def prepare(y,U,norm):
    rows=load(y);export(y)
    ref=json.loads((ROOT/'mapas/mapa1930/dataset_1930.json').read_text(encoding='utf-8'))['candidates']
    CAND={}
    for code,old in [('UCR','UCR'),('CON','CD'),('PS','PS'),('ANT','RAN'),('LEN','LEN'),('BLO','BLO')]:
        CAND[code]=copy.deepcopy(ref[old])
    CAND['CON'].update(n='Partidos Conservadores',sub='Demócratas, liberales y aliados',logo='CON')
    CAND['UCR']['sub']='Unión Cívica Radical'
    CAND['ANT'].update(n='UCR Antipersonalista',sub='Radicalismo antipersonalista',logo='UCRA')
    CAND['UNIF']=dict(n='UCR Unificada',sub='Santa Fe, Santiago y San Juan',base='#a52a2a',logo='UCRU')
    CAND['DIS']=dict(n='Radicalismo disidente',sub='Principistas, rojos y otras listas',base='#b350a1',logo='DIS')
    CAND['IND']=dict(n='Independientes',sub='Comité Independiente y otras listas',base='#687582',logo='IND')
    if y in (1918,1920):
        CAND['PDP']=copy.deepcopy(ref['PDP'])
        CAND['DIS']=dict(n='Radicalismo disidente',sub='Rojos, disidentes y afines',base='#a52a2a',logo='UCRD')
        CAND['PSA']=dict(n='Socialista Argentino',sub='Partido Socialista Argentino',base='#b350a1',logo='PSA')
    if y>=1931:
        img=base64.b64encode((ROOT/'logos/Escudo_de_la_UCR.svg').read_bytes()).decode()
        CAND['UCR'].update(img='data:image/svg+xml;base64,'+img,ar=1.0)
        CAND['CON']=dict(n='Concordancia',sub='PDN, antipersonalistas y aliados',base='#76acdc',logo='CON')
        # Azul del antipersonalismo en los mapas históricos: distingue la coalición del rojo radical.
        if y==1937:
            CAND['CON'].update(n='Roberto M. Ortiz',sub='Concordancia')
            CAND['UCR'].update(n='Marcelo T. de Alvear',sub='Unión Cívica Radical')
            CAND['PS'].update(n='Nicolás Repetto',sub='Partido Socialista')
        else:
            CAND['UCR']['sub']='Unión Cívica Radical'
            CAND['FP']=dict(n='UCR – Frente Popular',sub='Tucumán',base='#b350a1',logo='UCRFP')
    raw_wins=Counter(max(r['bloc'],key=r['bloc'].get) for r in rows if r['P'])
    BLOCS=[b for b in NATIONAL[y]['blocs'] if raw_wins[b]]
    KEY={(u['prov'],norm(u['name'])):i for i,u in enumerate(U)}
    aliases=json.loads((HERE/'alias_1914.json').read_text(encoding='utf-8'))
    alias={(p,n):(nn,why) for p,n,nn,why in aliases}
    unit_src={};unmapped=[];disp={}
    for r in rows:
        p,n=r['prov'],r['name'];why=None
        if p=='Capital Federal':names=[f'Circ. {r["circ"]:02d}'] if r['circ'] else []
        elif (p,n) in alias:names,why=alias[(p,n)]
        else:names=[n]
        idx=[KEY[(p,norm(s))] for s in names if (p,norm(s)) in KEY]
        if r['P'] and not idx:unmapped.append(r)
        for i in idx:
            # Filas con ** no sustituyen una fila agregada compartida ya asignada.
            if i in unit_src:
                if not r['P']:continue
                if not unit_src[i][0]['P']:pass
                else:raise AssertionError((y,p,n,U[i]['name']))
            unit_src[i]=(r,why,len(idx))
            disp[i]=f'Circunscripción {r["circ"]} · {n}' if p=='Capital Federal' else (n if len(idx)==1 else U[i]['name'])
    GREY_T,GREY_N='#cfcfcf','#e6dcc3'
    KEYS=[[GREY_T,'Sin elección nacional propia'],[GREY_N,'Pendiente: sin dato propio publicado']]
    if y in (1918,1920):KEYS[1][1]='Sin dato propio o identidad pendiente'
    def analysis(rr):
        p={};bloc=defaultdict(int);ins=vot=0;bla=nul=0
        for r in rr:
            for c,v in r['P'].items():p[c]=p.get(c,0)+v
            for b,v in r['bloc'].items():bloc[b]+=v
            ins+=r['ins'] or 0;vot+=r['vot'] or 0;bla+=r['blancos'] or 0;nul+=r['nulos'] or 0
        if y in (1918,1920):
            if any(r['ins'] is None for r in rr):ins=None
            if any(r['vot'] is None for r in rr):vot=None
        return dict(P=p,bloc=dict(bloc),ins=ins or None,vot=vot or None,D=sum(p.values()),blancos=bla,nulos=nul)
    party_code={s:'P_'+str(i) for i,s in enumerate(sorted({s for r in rows for s in r['P']}))}
    for s,c in party_code.items():
        n=norm(s)
        if 'socialista' in n and 'independiente' not in n:b='PS'
        elif 'lencinista' in n:b='LEN'
        elif 'bloquista' in n:b='BLO'
        elif 'frentepopular' in n:b='FP'
        elif 'antipersonalista' in n:b='ANT' if y==1926 else 'CON'
        elif 'concordancia' in n or 'democrata' in n or 'conservador' in n or 'liberal' in n or 'concentracion' in n or 'unionprovincial' in n:b='CON'
        elif 'unificada' in n or 'santafe' in n or 'unificado' in n:b='UNIF' if y==1926 else 'CON'
        elif 'radical' in n:b='UCR'
        else:b='IND'
        CAND[c]=dict(n=s,base=CAND.get(b,{}).get('base','#808080'),logo='')
    if y in (1918,1920):
        # La misma palabra puede significar fuerzas distintas en provincias distintas:
        # el color del rótulo original es solo auxiliar, sin determinar agrupaciones.
        for s,c in party_code.items():
            bs={r.get('party_bloc',{}).get(s) for r in rows if s in r['P']}
            if len(bs)==1:
                b=next(iter(bs));CAND[c]['base']=CAND.get(b,{}).get('base','#808080')
    CAND['P_BLA']=dict(n='En blanco (o blancos y anulados, según tabla)',base='#dadada')
    CAND['P_NUL']=dict(n='Observados y/o anulados',base='#999999')
    def rec(a,note):
        d=a['D'];lines=[[party_code[c],v,round(100*v/d,2)] for c,v in sorted(a['P'].items(),key=lambda kv:-kv[1])]
        for c,k in [('P_BLA','blancos'),('P_NUL','nulos')]:
            if a[k]:
                den=a['vot'] or (d+a['blancos']+a['nulos'])
                lines.append([c,a[k],round(100*a[k]/den,2)])
        metrics=[]
        for label,k in [('Inscriptos','ins'),('Votantes','vot')]:
            if a[k] is not None:metrics.append([label,f'{a[k]:,}'.replace(',','.')])
        if a['ins'] and a['vot']:metrics.append(['Participación',('%.1f %%'%(100*a['vot']/a['ins'])).replace('.',',')])
        w=max(a['bloc'],key=a['bloc'].get);out=dict(lines=lines,metrics=metrics,note=note)
        if w in BLOCS:out.update(w=w,q=round(100*a['bloc'][w]/d,2))
        else:out.update(fill='#9a9a9a')
        return out
    unit_rec={};unit_an={};usedrows=set()
    losandes={('Catamarca','Antofagasta de la Sierra'),('Jujuy','Susques'),('Salta','Pastos Grandes'),('Salta','San Antonio de los Cobres')}
    for i,u in enumerate(U):
        p=u['prov'];r,why,n=unit_src.get(i,(None,None,0))
        if p in TERR or (p,u['name']) in losandes or p in NO_ELECCION[y]:
            text=(f'{p} no renovó diputados nacionales en {y} (tabla de bancas de Wikipedia).' if p in NO_ELECCION[y] else
                  'Territorio nacional: sin elección nacional propia en esta fecha.')
            unit_rec[i]=dict(fill=GREY_T,lines=[],note=text);continue
        if not r or not r['P']:
            text=('La fuente marca esta unidad con '+', '.join(sorted(set(r['marks'].values())))+'. No equivale a cero.' if r else
                  f'Pendiente: Cantón no publica un resultado propio de esta unidad para {y}.')
            unit_rec[i]=dict(fill=GREY_N,lines=[],note=text);continue
        a=analysis([r]);note=f'Cantón (1968), t. II, página PDF {r["page"]}, impresa {r["book"]}; varones solamente.'
        if r.get('source_note'):note+=' '+r['source_note']
        if r.get('reserva'):note+=' Reserva de fuente: '+r['reserva']
        if y in (1918,1920) and r['blancos'] and r['vot'] is None:
            note+=' El porcentaje de blancos se calcula sobre las columnas publicadas (positivos + blancos), porque la tabla no publica votantes.'
        if why:note+=' '+why.replace('se reparte','se representa')
        if n>1:note+=f' Una única fila de datos, representada en {n} polígonos; no son votos independientes.'
        if r['marks']:note+=' Hay categorías sin cifra: '+str(r['marks'])+'.'
        tab=a['D']+a['blancos']+a['nulos']
        if a['vot'] is not None and tab!=a['vot']:
            note+=f' Suma de columnas publicadas: {tab:,}; votantes impresos: {a["vot"]:,}. Se conserva la diferencia; no se atribuye a otra fuerza ni a blancos.'
        unit_rec[i]=rec(a,note)
        if r.get('unresolved'):
            unit_rec[i].pop('w',None);unit_rec[i].pop('q',None);unit_rec[i]['fill']=GREY_N
        else:unit_an[i]=a
        usedrows.add((r['prov'],r['name']))
    prov_an={};prov_rec={}
    for p in sorted({u['prov'] for u in U}):
        rr=[r for r in rows if r['prov']==p and r['P']]
        if p in TERR or p in NO_ELECCION[y]:prov_rec[p]=dict(fill=GREY_T,lines=[],note='Sin elección nacional propia o sin renovación de diputados.');continue
        if not rr:prov_rec[p]=dict(fill=GREY_N,lines=[],note='Pendiente: sin tabla departamental publicada por Cantón.');continue
        a=analysis(rr);prov_an[p]=a
        prov_rec[p]=rec(a,'Suma de las filas publicadas por Cantón, sin duplicar los datos compartidos entre polígonos. No se garantiza cobertura provincial completa.')
        if any(r.get('reserva') for r in rr):prov_rec[p]['note']+=' Reserva cronológica de la fuente impresa: ver fichas locales y Fuentes y notas.'
        if any(r.get('unresolved') for r in rr):
            prov_an.pop(p,None);prov_rec[p].pop('w',None);prov_rec[p].pop('q',None);prov_rec[p]['fill']=GREY_N
            prov_rec[p]['note']+=' Identidad partidaria de las columnas pendiente: no se asigna ganador a los rótulos contradictorios del impreso.'
    return locals()
