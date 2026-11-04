"""Cotejo diagnóstico con las familias de Lupu–Stokes. No modifica la transcripción."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
from exportar import ROOT, norm

ALIASES={'camapana':'campana','chascomis':'chascomus','valleviego':'valleviejo','eumahuaca':'humahuaca',
 'mburcuya':'mburucuya','nuevedejulio':'9dejulio','nuevedejuli':'9dejulio','trenquelanguen':'trenquelauquen',
 'clavarria':'olavarria','piedrablanca':'fraymamertoesquiu','concepciondeluruguay':'uruguay',
 'rosariotala':'tala','velezsarfield':'velezsarsfield','nuevejulio':'9dejulio'}
def nk(s):return ALIASES.get(norm(s),norm(s))

def compare(year):
    folder=ROOT/f'transcripciones/canton{year}'
    doc=json.loads((folder/f'canton_{year}.json').read_text(encoding='utf-8'))
    ls=pd.read_csv(ROOT/'datos/preparados/lupu_stokes_1912_2003_exportacion.csv')
    ls=ls[ls.year.eq(year)&ls.dip.eq(1)&ls.total.gt(0)]
    pairs=[];missing=[];unread=[]
    # Lupu llama las circunscripciones de Capital por nombre; solo normalización documentada.
    lk={(nk(s.province),nk(s.department)):s for s in ls.itertuples()}
    for pg in doc['paginas']:
        cols={str(c):v for c,v in pg['columnas'].items() if norm(v) not in ('inscriptos','votantes') and not any(z in norm(v) for z in ('blanco','anulado'))}
        for row in pg['filas']:
            vals={str(c):v for c,v in row['valores'].items()}
            if not any(vals.get(c) is not None for c in cols):continue
            s=lk.get((nk(pg['provincia']),nk(row['unidad'])))
            if s is None:missing.append([pg['provincia'],row['unidad'],pg['pagina_pdf']]);continue
            pairs.append((pg,row,s,cols))
    results=[]
    for prov in sorted({p[0]['provincia'] for p in pairs}):
        p=[x for x in pairs if x[0]['provincia']==prov]
        columns=p[0][3]
        for family in ('ucr','soc','con'):
            valid=[x for x in p if pd.notna(getattr(x[2],family))]
            if not valid or not any(getattr(x[2],family)>0 for x in valid):continue
            target=np.array([getattr(x[2],family) for x in valid]);best=None
            available=[c for c in columns if any(x[1]['valores'].get(c) is not None for x in valid)]
            for k in range(1,len(available)+1):
                for subset in combinations(available,k):
                    val=np.array([sum(x[1]['valores'].get(c) or 0 for c in subset) for x in valid])
                    known=np.array([all(x[1]['valores'].get(c) is not None for c in subset) for x in valid])
                    score=(float(np.abs((val-target)[known]).sum()),int(np.count_nonzero((val-target)[known])),len(subset))
                    if best is None or score<best[0]:best=(score,subset,val,known)
            if best is None:continue
            score,subset,values,known=best;diffs=[]
            for x,v,t,kn in zip(valid,values,target,known):
                if not kn:
                    unread.append(dict(provincia=prov,unidad=x[1]['unidad'],pagina_pdf=x[0]['pagina_pdf'],familia=family,columnas=list(subset),lupu=int(t)))
                elif v!=t:diffs.append(dict(unidad=x[1]['unidad'],pagina_pdf=x[0]['pagina_pdf'],canton=int(v),lupu=int(t),diferencia=int(v-t)))
            results.append(dict(provincia=prov,familia=family,columnas_diagnosticas={c:columns[c] for c in subset},filas_comparables=int(sum(known)),coincidencias=int(sum(known))-len(diffs),diferencias=diffs))
    out=dict(anio=year,metodo='Subconjunto de columnas con mayor proximidad a cada familia académica, por distrito. Solo detecta posibles digitaciones; no prueba identidad política ni se usa para reemplazar la imagen.',comparaciones=results,sin_pareja=missing,ilegibles_no_comparados=unread)
    (folder/f'COTEJO_LUPU_{year}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(year,'comparaciones',sum(r['filas_comparables'] for r in results),'exactas',sum(r['coincidencias'] for r in results),'sin pareja',len(missing))
    for r in results:
        if r['diferencias']:print(r['provincia'],r['familia'],r['columnas_diagnosticas'],r['diferencias'])
    print('ilegibles',unread)
    return out

if __name__=='__main__':
    for y in map(int,sys.argv[1:] or (1918,1920)):compare(y)
