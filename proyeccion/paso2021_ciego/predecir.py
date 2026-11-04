"""Predicciones sin abrir resultados totales ni archivos de elecciones posteriores."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np,pandas as pd,json,hashlib,time,datetime
from config import FORCES,SCHEMES,REPS,BOOT
from comun_experimento import HERE,fit,raw
from aislar import guard

def metrics_payload(R):
 bs=R['bs'];j,k=0,1;ok=R['inferencia_valida']
 mb=bs[:,j]-bs[:,k]
 interval=np.percentile(mb,[2.5,97.5]).tolist() if ok else [None,None]
 district=R['distrito_pt'];dp=100*district/district.sum(1,keepdims=True)
 return dict(punto=R['pt'].tolist(),lo=R['lo'].tolist(),hi=R['hi'].tolist(),margen=float(R['pt'][j]-R['pt'][k]),
  margen_banda=interval,prob_primero=R['prob_primero'].tolist(),inferencia_valida=ok,
  distritos=R['distritos'],porcentaje_distrito=dp.tolist(),circuitos=len(np.unique(R['clus'])))

def main():
 log=guard('prediccion');start=time.time()
 cfg=json.loads((HERE/'PARAMETROS_SELLADOS.json').read_text(encoding='utf8'))
 lam=np.inf if cfg['lambda_temporal']=='swing' else cfg['lambda_temporal']
 out=HERE/'predicciones';out.mkdir(exist_ok=True)
 records=[]
 for scheme in SCHEMES:
  for rep in range(REPS):
   a=pd.read_json(HERE/'actas_reveladas'/('%s_%03d.json'%(scheme,rep)),orient='records',dtype={'distrito_id':str,'circuito':str,'mesa':str,'mesa_tipo':str})
   if len(a[['distrito_id','seccion_id','circuito','mesa','mesa_tipo']].drop_duplicates())!=30:raise AssertionError('No hay 30 mesas')
   common=dict(esquema=scheme,rep=rep)
   for name,ln,fac in [('congelado',.1,1.4),('temporal',lam,cfg['factor_temporal'])]:
    R=fit(a,['2019','2017'],'2021_paso',lam=ln,factor=fac,boot=BOOT,seed=2021000+rep)
    records.append(dict(**common,modelo=name,**metrics_payload(R)))
   # Comparaciones sin elegir parámetros ni mirar la evaluación.
   for name,orig,ln,weighted in [('swing',['2019','2017'],np.inf,True),('solo_2019',['2019'],.1,True),('sin_repesado',['2019','2017'],.1,False),('sin_regularizar',['2019','2017'],0.,True)]:
    R=fit(a,orig,'2021_paso',lam=ln,weighted=weighted)
    payload=metrics_payload(R)
    records.append(dict(**common,modelo=name,**payload))
   for name,weighted in [('crudo',False),('crudo_ponderado',True)]:
    pt=raw(a,'2021_paso',weighted=weighted)
    records.append(dict(**common,modelo=name,punto=pt.tolist(),margen=float(pt[0]-pt[1])))
   if (rep+1)%20==0:print('Prediccion',scheme,rep+1,'%.0fs'%(time.time()-start),flush=True)
  (out/(scheme+'.json')).write_text(json.dumps([r for r in records if r['esquema']==scheme],ensure_ascii=False,allow_nan=True),encoding='utf8')
 manifest={'creado_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evaluacion_abierta':False,'colecciones':len(records)//8,
  'archivos':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.json')},
  'parametros_sha256':hashlib.sha256((HERE/'PARAMETROS_SELLADOS.json').read_bytes()).hexdigest()}
 (HERE/'PREDICCIONES_SELLADAS.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 print('Predicciones selladas: ya pueden evaluarse sin retocar el modelo',flush=True)

if __name__=='__main__':main()
