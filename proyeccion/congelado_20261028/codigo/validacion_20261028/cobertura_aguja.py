"""Validacion del nuevo bootstrap completo y piso sistematico en destino 2025.
Piso elegido exclusivamente con errores de 2019->2023 en escrutinio_completo.csv.
Nuevas semillas, 3 trayectorias por orden, 60 remuestras por corte. Diagnostico
retrospectivo; cortes dependientes y pocas trayectorias, no garantia de cobertura.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json,time
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
sys.argv=[sys.argv[0],'2023p','2025bl','--circuito']
import backtest as bt
import aguja as ag

cal=pd.read_csv(HERE/'escrutinio_completo.csv')
cal=cal[(cal.par=='2019p->2023p')&(cal.metodo=='D_sin_ajuste')]
needs=[]
for f,g in cal.groupby('corte'):
    required=np.quantile(np.abs(g.error),.95)/1.96
    old=.603*(1-f)*f**(-.316)
    if required>old:needs.append(required/(1-f))
floor=float(np.ceil(max(needs,default=0)*10)/10)
assert np.isclose(floor,ag.SIS_PISO)
(HERE/'calibracion_aguja.json').write_text(json.dumps(dict(
    entrenamiento='2019p->2023p, 6 semillas, 5 ordenes, sin votos 2025',piso=floor,
    criterio='q95(error absoluto)/1.96/(1-f) en cortes donde el sistematico anterior queda corto; redondeo superior a 0.1',
    evaluacion='2023p->2025bl, semillas nuevas, sin reoptimizar despues'),indent=2),encoding='utf-8')
ag.STEPS=np.array([.01,.05,.25,.5])
st,info,cols=bt.state();rows=[];start=time.time()
for scheme in ['azar','geo','geo_circ','capital','sesgo']:
    for rep in range(3):
        steps,real=ag.run(st,scheme,20261029+rep,nboot=60,path=False)
        for step in steps:
            for j,col in enumerate([cols[p] for p in st['pos']]):
                rows.append(dict(esquema=scheme,rep=rep,corte=step['x'],fuerza=col,
                                 real=float(real[j]),punto=step['proy'][j],lo=step['lo'][j],hi=step['hi'][j],
                                 cubre=step['lo'][j]<=real[j]<=step['hi'][j],
                                 error=step['proy'][j]-real[j]))
        pd.DataFrame(rows).to_csv(HERE/'aguja_cobertura_2025.csv',index=False)
        print(scheme,rep,'%.0fs'%(time.time()-start),flush=True)
print(pd.DataFrame(rows).groupby(['esquema','fuerza']).cubre.mean().round(3).to_string())
