"""Selecciona en 2017, calibra en 2019; no abre resultados PASO 2021."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np,pandas as pd,json,hashlib,datetime,math,time
from config import FORCES,SCHEMES,LAMBDAS,DEV_REPS,DEV_BOOT
from comun_experimento import HERE,select,reveal,fit
from aislar import guard

def main():
 log=guard('desarrollo');start=time.time();rows=[]
 w=pd.read_pickle(HERE/'permitidos/mesas_2017.pkl')
 real=100*w[FORCES].sum()/w[FORCES].sum().sum()
 for scheme in SCHEMES:
  for rep in range(DEV_REPS):
   a=reveal(w,select('2017',scheme,rep),scheme)
   for lam in LAMBDAS:
    R=fit(a,['2015','2013'],'2017',lam=lam)
    rows.append(dict(esquema=scheme,rep=rep,lambda_='swing' if np.isinf(lam) else str(lam),mae=float(np.abs(R['pt']-real.to_numpy()).mean())))
  print('Seleccion 2017',scheme,'%.0fs'%(time.time()-start),flush=True)
 scores=pd.DataFrame(rows);scores.to_csv(HERE/'seleccion_2017.csv',index=False)
 means=scores.groupby('lambda_').mae.mean()
 # La clave secundaria favorece mayor regularización si hubiese igualdad exacta.
 best=min(LAMBDAS,key=lambda l:(means['swing' if np.isinf(l) else str(l)],-l))
 w=pd.read_pickle(HERE/'permitidos/mesas_2019.pkl')
 t=100*w[FORCES].sum()/w[FORCES].sum().sum();actual=t.JXC-t.FDT
 rows=[];failed=0
 for scheme in SCHEMES:
  for rep in range(DEV_REPS):
   a=reveal(w,select('2019',scheme,rep),scheme)
   R=fit(a,['2017','2015'],'2019',lam=best,factor=1.,boot=DEV_BOOT,seed=9000+rep)
   point=R['pt'][0]-R['pt'][1];b=R['bs'][:,0]-R['bs'][:,1]
   lo,hi=np.percentile(b,[2.5,97.5]);side=hi-point if actual>point else point-lo
   need=abs(point-actual)/side if side>0 and np.isfinite(side) else np.inf
   failed+=int(not np.isfinite(need))
   rows.append(dict(esquema=scheme,rep=rep,margen=point,real=actual,lo=lo,hi=hi,expansion_necesaria=need))
  print('Calibracion 2019',scheme,'%.0fs'%(time.time()-start),flush=True)
 cal=pd.DataFrame(rows);cal.to_csv(HERE/'calibracion_2019.csv',index=False)
 if failed:raise RuntimeError('No existe expansión finita para alguna banda de calibración; revisar sin abrir 2021')
 factor=max(1.,math.ceil(float(np.quantile(cal.expansion_necesaria,.95))*10)/10)
 cfg=dict(creado_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seleccion='2017',calibracion='2019',lambda_temporal='swing' if np.isinf(best) else best,factor_temporal=factor,
  scores_2017=means.to_dict(),lambda_congelado=.1,factor_congelado=1.4,semillas='config.py',destino_no_abierto='PASO 2021')
 (HERE/'PARAMETROS_SELLADOS.json').write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding='utf8')
 print('Parametros sellados',json.dumps(cfg,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
