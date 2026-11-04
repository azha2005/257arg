"""D, D sin benchmarking y E sin benchmarking sobre universo completo disponible.
No cambia la aguja ni su calibracion: deja la evidencia de la comparacion.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json,time
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
sys.argv=sys.argv[:1]
import backtest as bt

rows=[];universes=[];start=time.time()
for a,b,circ in [('2015p','2015b',False),('2023p','2023b',False),('2019p','2023p',True)]:
    bt.Y0,bt.Y1,bt.CIRC=a,b,circ
    st,info,cols=bt.state()
    assert np.isclose(info['votos_destino'],info['votos_evaluados'])
    truth=bt.summarize(st['Vd'],st,st['dist'])[0]
    universes.append(dict(par=a+'->'+b,**info,real=truth,distritos=int(st['ndist'])))
    for scheme in ['azar','geo','geo_circ','capital','sesgo']:
        for rep in range(6):
            order=bt.order(st,scheme,np.random.default_rng(19800+rep))
            for cut in [.002,.01,.05,.25,.5]:
                cnt=np.zeros(len(st['e']),bool);cnt[order[:round(cut*len(cnt))]]=True
                for name,bench,near in [('D',True,False),('D_sin_ajuste',False,False),('E_sin_ajuste',False,True)]:
                    V=bt.project_BC(st,cnt,True,'F_tam',bench=bench,vecinas=near)
                    assert np.allclose(V[cnt],st['Vd'][cnt])
                    nat,_,dp,_=bt.summarize(V,st,st['dist'])
                    reald=bt.summarize(st['Vd'],st,st['dist'])[2]
                    rows.append(dict(par=a+'->'+b,esquema=scheme,rep=rep,corte=cut,metodo=name,
                                     error=nat-truth,mae_distritos=np.abs(dp-reald).mean(),
                                     minimo_votos=float(V.min())))
        print(a,b,scheme,'%.0fs'%(time.time()-start),flush=True)
        pd.DataFrame(rows).to_csv(HERE/'escrutinio_completo.csv',index=False)
    (HERE/'universos_completos.json').write_text(json.dumps(universes,indent=2,ensure_ascii=False),encoding='utf-8')
print(pd.DataFrame(rows).assign(abs_error=lambda d:d.error.abs()).groupby(['par','metodo']).abs_error.mean().round(3))
