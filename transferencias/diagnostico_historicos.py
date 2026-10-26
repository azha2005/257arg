"""Diagnóstico interno: predicción de proporciones territoriales y sensibilidad."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import estimar as e
from auditar import auditar
HERE = Path(__file__).resolve().parent
PAIRS = [('1989p','1995p'),('1989d','1994c'),('1985d','1987d')]
PAIRS += [('1983p','1989p'),('1987d','1989p'),('1985d','1989p')]
PAIRS += [('1989p','1997d')]
PAIRS += [('1995p','1997d'),('1995p','1999p'),('1983p','1985d')]

def fullfit(X,Y,w,lam):
    center = e.fit(X.values,Y.values,const=.001,w=w.values)
    g0 = np.log(center[:,:-1]/center[:,-1:]).ravel()
    M = np.zeros((X.shape[1],Y.shape[1]))
    for d in X.index.get_level_values(0).unique():
        B = e.fit_prov(X.loc[d].values,Y.loc[d].values,lam*len(X.loc[d]),w.loc[d].values,g0)
        M += B * X.loc[d].mul(w.loc[d],axis=0).sum().values[:,None]
    return M / M.sum(1,keepdims=True)*100

def main():
    result = []
    for a,b in ([('1914d','1916d')] if '--1914' in sys.argv else PAIRS[-3:] if '--tanda95' in sys.argv else PAIRS):
        A,B,X,Y,w,rows,cols,ctl = e.prepare(a,b)
        saved = json.loads((HERE/f'{a}_{b}/control.json').read_text(encoding='utf8'))
        lam = saved['lambda']
        rng = np.random.default_rng(1989)
        fold = np.zeros(len(X),int)
        districts = X.index.get_level_values(0)
        for d in districts.unique():
            idx = np.flatnonzero(districts==d)
            fold[idx] = rng.permutation(len(idx))%5
        errors = {'modelo':0.,'promedio_provincial':0.}
        provincial_errors = {d:dict(modelo=0.,promedio_provincial=0.,denom=0.) for d in districts.unique()}
        denom = 0.
        for k in range(5):
            tr,te = fold!=k,fold==k
            center = e.fit(X.values[tr],Y.values[tr],const=.001,w=w.values[tr])
            g0 = np.log(center[:,:-1]/center[:,-1:]).ravel()
            for d in districts.unique():
                t = tr & (districts==d); v = te & (districts==d)
                if not v.any(): continue
                if t.sum() >= 5:
                    matrix = e.fit_prov(X.values[t],Y.values[t],lam*t.sum(),w.values[t],g0)
                else: matrix = center
                baseline = np.average(Y.values[t] if t.any() else Y.values[tr],axis=0,weights=w.values[t] if t.any() else w.values[tr])
                for label,pred in [('modelo',X.values[v]@matrix),('promedio_provincial',baseline)]:
                    error = float((w.values[v,None]*(pred-Y.values[v])**2).sum())
                    errors[label] += error
                    provincial_errors[d][label] += error
                denom += w.values[v].sum()*Y.shape[1]
                provincial_errors[d]['denom'] += w.values[v].sum()*Y.shape[1]
        rmse = {key:float(np.sqrt(value/denom)*100) for key,value in errors.items()}
        audit = auditar(f'{a}_{b}')
        item = dict(par=f'{a}_{b}',rmse_validacion_pp=rmse,
                    mejora_modelo_pct=100*(1-rmse['modelo']/rmse['promedio_provincial']),
                    separacion=audit['separacion'],poco_informativa=audit['poco_informativa'],
                    filas=audit['filas'],sensibilidad_calvo_pct=100*saved['votos_distintos_vs_calvo']/saved['votos_total'])
        item['rmse_validacion_por_provincia_pp'] = {
            d:{label:float(np.sqrt(err[label]/err['denom'])*100) for label in errors}
            for d,err in provincial_errors.items()}
        if (a,b) == ('1989p','1995p'):
            keep = np.array([not (d=='20' and c=='S:DESEADO') for d,s,c in X.index])
            ref = fullfit(X,Y,w,lam)
            alt = fullfit(X[keep],Y[keep],w[keep],lam)
            item['sin_deseado_max_cambio_pp_por_fila'] = dict(zip(rows,np.abs(ref-alt).max(1).round(3).tolist()))
            item['deseado_incluido'] = bool((~keep).any())
        (HERE/f'{a}_{b}/diagnostico.json').write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf8')
        result.append(item)
        print(item['par'],rmse,'mejora',item['mejora_modelo_pct'],'separacion',item['separacion'],flush=True)
    path = HERE/('fuentes_1914_1916/diagnostico.json' if '--1914' in sys.argv else 'historicos_1989/diagnostico.json')
    if '--tanda95' in sys.argv:
        previous=json.loads(path.read_text(encoding='utf8'))
        fresh={item['par'] for item in result}
        result=[item for item in previous if item['par'] not in fresh]+result
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')

if __name__ == '__main__': main()
