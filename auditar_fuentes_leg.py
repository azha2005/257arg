from pathlib import Path
import pandas as pd, json,sys
ROOT=Path(__file__).resolve().parent
out={}
for y in range(2003,2026,2):
    if y==2003:continue
    v,m=pd.read_pickle(ROOT/'datos_oficiales'/str(y)/('agregado_polar.pkl' if y<2011 else 'agregado.pkl'))
    v=v[v.cargo_nombre.str.contains('DIPUTAD')].copy()
    m=m[m.cargo_nombre.str.contains('DIPUTAD')].copy()
    for c in ('distrito_id','seccion_id'):
        v[c]=v[c].astype(int).astype(str);m[c]=m[c].astype(int).astype(str)
    m['e']=pd.to_numeric(m.mesa_electores,errors='coerce').fillna(0)
    e=m.groupby(['distrito_id','seccion_id']).e.sum()
    a=v.groupby(['distrito_id','seccion_id']).v.sum()
    bad=[(k,int(n),int(e.get(k,0))) for k,n in a.items() if n>e.get(k,0) and e.get(k,0)>0]
    out[y]={'votos_tipo':v.groupby('votos_tipo').v.sum().to_dict(),'padron_inconsistente':bad,'sin_votos':[(k,int(n)) for k,n in a.items() if n==0]}
out['2003_LaPlata']=pd.read_csv(ROOT/'raw/datar_2003_departamento_SIN_VALIDAR.csv').query("eleccion=='DN' and departamento=='LA PLATA'")[['partido','votos']].to_dict('records')
(ROOT/'auditoria_fuentes_leg.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False)[:1200])
