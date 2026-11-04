"""Cotejo diagnóstico independiente con Lupu–Stokes: no modifica votos ni reconstruye listas."""
from itertools import combinations
from collections import defaultdict
import json
import numpy as np
import pandas as pd
from datos import load, norm, HERE, ROOT

AL={'camapana':'campana','chascomis':'chascomus','valleviego':'valleviejo','eumahuaca':'humahuaca',
    'mburcuya':'mburucuya','nuevedejulio':'9dejulio','nuevedejuli':'9dejulio','trenquelanguen':'trenquelauquen',
    'piedrablanca':'fraymamertoesquiu'}
def nk(s):return AL.get(norm(s),norm(s))
ls=pd.read_csv(ROOT/'datos/preparados/lupu_stokes_1912_2003_exportacion.csv')
ls=ls[ls.year.eq(1926)&ls.dip.eq(1)&ls.total.gt(0)]
lk={(nk(r.province),nk(r.department)):r for r in ls.itertuples()}
out=[];missing=[]
for prov in sorted({r['prov'] for r in load(1926)}):
    pairs=[]
    for r in load(1926):
        if r['prov']!=prov or not r['P']:continue
        s=lk.get((nk(prov),nk(r['name'])))
        if s is None:missing.append([prov,r['name']]);continue
        pairs.append((r,s))
    names=sorted({s for r,_ in pairs for s in r['P']})
    for family in ('ucr','soc','con'):
        valid=[(r,s) for r,s in pairs if pd.notna(getattr(s,family))]
        if not valid or not any(getattr(s,family)>0 for _,s in valid):continue
        target=np.array([getattr(s,family) for _,s in valid]);best=None
        # Busca únicamente qué subconjunto publicado se parece a la familia académica,
        # para detectar digitaciones; nunca convierte esa familia en votos de una lista.
        for k in range(1,len(names)+1):
            for cols in combinations(names,k):
                val=np.array([sum(r['P'].get(c,0) for c in cols) for r,_ in valid])
                score=(int(np.count_nonzero(val-target)),float(np.abs(val-target).sum()),len(cols))
                if best is None or score<best[0]:best=(score,cols,val)
        score,cols,vals=best
        dif=[dict(unidad=r['name'],pagina_pdf=r['page'],canton=int(v),lupu=int(t),diferencia=int(v-t)) for (r,_),v,t in zip(valid,vals,target) if v!=t]
        out.append(dict(provincia=prov,familia=family,columnas_diagnosticas=cols,filas=len(valid),coinciden=len(valid)-len(dif),diferencias=dif))
result=dict(metodo='Emparejamiento nominal; subconjunto de columnas más próximo, solo diagnóstico, no corrección ni identificación partidaria.',
    comparaciones=out,sin_pareja=missing)
(HERE/'COTEJO_LUPU_1926.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('comparaciones',sum(r['filas'] for r in out),'exactas',sum(r['coinciden'] for r in out))
for r in out:
    if r['diferencias']:print(r['provincia'],r['familia'],r['columnas_diagnosticas'],r['diferencias'])
