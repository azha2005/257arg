"""Empalma rangos de mesas del archivo LN con los resultados de 2015.

La copia está en una carpeta llamada snapshot_2021, pero sus cifras corresponden
a la presidencial GENERAL 2015: se verifica cada local contra el CSV de la DINE.
No se atribuye automáticamente esa fecha a los puntos ni a los rangos sin cotejo.
"""
from pathlib import Path
from collections import defaultdict
import re, json, sys
import pandas as pd
from serie import ROOT, CACHE, norm, cir, dump


def load():
    path=CACHE/'mesas_locales_2015_v2.pkl'
    if path.exists():return pd.read_pickle(path)
    fs=json.loads((ROOT/'geometria/circuitos_busqueda/galeano_snapshot_2021/establecimientos-ln.geojson').read_text(encoding='utf8'))['features']
    fs=[f for f in fs if f['properties']['id_distrito'] in (1,2)]
    candidates=defaultdict(list); points={}; props={}
    for j,ft in enumerate(fs):
        p=ft['properties'];d=f"{int(p['id_distrito']):02d}";s=f"{int(p['id_seccion']):03d}"
        ranges=re.findall(r'(\d+)\s*-\s*(\d+)',str(p['rangos_mesas']))
        if not ranges:continue
        for a,b in ranges:
            for m in range(int(a),int(b)+1):candidates[d,s,m].append(j)
        points[j]=tuple(ft['geometry']['coordinates']);props[j]=p
    m2l={k:vs[0] for k,vs in candidates.items() if len(set(vs))==1}
    votes={};tables={};controls={}
    for kind in ['general','balotaje']:
        source=next((ROOT/f'datos_oficiales/2015{"_balotaje" if kind=="balotaje" else ""}/x').rglob('Resultado*.csv'))
        parts=[]
        use=['distrito_id','seccion_id','circuito_id','mesa_id','mesa_tipo','mesa_electores','cargo_nombre','agrupacion_id','agrupacion_nombre','votos_tipo','votos_cantidad']
        for chunk in pd.read_csv(source,dtype=str,chunksize=600000,usecols=lambda c:c.lower() in use):
            chunk.columns=chunk.columns.str.lower()
            mask=chunk.distrito_id.isin(['1','2']) & chunk.cargo_nombre.str.contains('PRESIDENTE|DIPUTAD.*NACIONAL',na=False)
            sub=chunk[mask].copy()
            if len(sub):parts.append(sub)
        data=pd.concat(parts,ignore_index=True)
        data['dist']=data.distrito_id.map(lambda x:f'{int(x):02d}')
        data['sec']=data.seccion_id.map(lambda x:f'{int(x):03d}')
        data['cir']=data.circuito_id.map(cir)
        data['mid']=data.mesa_id.astype(int)
        data['v']=pd.to_numeric(data.votos_cantidad)
        data['local']=[m2l.get(k,-1) for k in zip(data.dist,data.sec,data.mid)]
        # Ninguna mesa puede recibir una escuela que declara otro circuito.
        for mid,r in data[data.local>=0].drop_duplicates(['dist','sec','cir','mid']).iterrows():
            p=props[r.local]
            allowed={cir(c) for c in re.findall(r'\d+[A-Z]?',str(p['circuitos']))}
            if r.cir not in allowed:data.loc[(data.dist==r.dist)&(data.sec==r.sec)&(data.mid==r.mid),'local']=-1
        tables[kind]=data
        if kind=='general':
            pres=data[data.cargo_nombre.str.contains('PRESIDENTE')]
            records=[];valid=set()
            for local,g in pres[pres.local>=0].groupby('local'):
                p=props[local]
                vals=dict(votantes=int(g.v.sum()),positivos=int(g[g.votos_tipo=='POSITIVO'].v.sum()),
                          blancos=int(g[g.votos_tipo.isin(['EN BLANCO','BLANCO','BLANCOS'])].v.sum()),
                          nulos=int(g[g.votos_tipo=='NULO'].v.sum()),
                          electores=int(pd.to_numeric(g.drop_duplicates(['dist','sec','mid','mesa_tipo']).mesa_electores).sum()))
                # LN tiene «votantes» incompatibles con sus propias categorías en muchos locales.
                # Se cotejan positivos, blancos, nulos y electores; esa columna auxiliar no se usa.
                equal=all(vals[k]==int(p[k]) for k in ('positivos','blancos','nulos','electores'))
                if equal:valid.add(local)
                records.append(dict(local=int(local),**vals,igual=equal,ln={k:p[k] for k in vals}))
            controls['locales_cotejados']=len(records);controls['locales_identicos_2015']=len(valid)
            controls['ejemplos_no_identicos']=[r for r in records if not r['igual']][:15]
            # Solo usar rangos comprobados contra cuatro cifras independientes.
            controls['locales_validos']=sorted(int(x) for x in valid)
    for kind,data in tables.items():
        data.loc[~data.local.isin(valid),'local']=-1
    result=(tables,points,props,controls)
    pd.to_pickle(result,path)
    dump(CACHE/'control_locales2015.json',controls)
    print('LN2015',controls['locales_cotejados'],controls['locales_identicos_2015'],flush=True)
    return result


if __name__=='__main__':load()
