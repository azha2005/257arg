"""Abre el destino después de verificar las predicciones y parámetros sellados."""
from pathlib import Path
import json,hashlib,datetime
import numpy as np,pandas as pd
from config import FORCES,SCHEMES
HERE=Path(__file__).resolve().parent

def main():
 seal=json.loads((HERE/'PREDICCIONES_SELLADAS.json').read_text(encoding='utf8'))
 for n,h in seal['archivos'].items():
  assert hashlib.sha256((HERE/'predicciones'/n).read_bytes()).hexdigest()==h,'Predicción modificada'
 assert hashlib.sha256((HERE/'PARAMETROS_SELLADOS.json').read_bytes()).hexdigest()==seal['parametros_sha256']
 # Primera apertura del total reservado por el evaluador.
 w=pd.read_pickle(HERE/'sellado/mesas_2021paso.pkl')
 votes=w[FORCES].sum();truth=100*votes/votes.sum();rm=truth.JXC-truth.FDT
 td=w.groupby('distrito_id')[FORCES].sum();td=100*td.div(td.sum(1),axis=0)
 rows=[];forces=[];districts=[]
 for p in sorted((HERE/'predicciones').glob('*.json')):
  for r in json.loads(p.read_text(encoding='utf8')):
   pt=np.array(r['punto']);err=pt-truth.to_numpy();common={k:r[k] for k in ['esquema','rep','modelo']}
   b=r.get('margen_banda',[np.nan,np.nan]);lo,hi=[np.nan if v is None else v for v in b]
   row=dict(**common,mae_fuerzas=np.abs(err).mean(),margen=r['margen'],real_margen=rm,error_margen=r['margen']-rm,
    abs_error_margen=abs(r['margen']-rm),inferencia_valida=r.get('inferencia_valida',False),lo=lo,hi=hi,
    cubre_margen=bool(lo<=rm<=hi),ancho_margen=hi-lo,ganador_acertado=bool(np.argmax(pt)==np.argmax(truth)),
    brier=np.nan,mae_distrito=np.nan,ganadores_distrito=np.nan)
   if r.get('inferencia_valida',False):
    probs=np.array(r['prob_primero']);actual=np.eye(len(FORCES))[np.argmax(truth)]
    row['brier']=np.square(probs-actual).sum()
   for j,f in enumerate(FORCES):
    low=r.get('lo',[np.nan]*5)[j];high=r.get('hi',[np.nan]*5)[j]
    forces.append(dict(**common,fuerza=f,punto=pt[j],real=truth[f],error=err[j],abs_error=abs(err[j]),lo=low,hi=high,
     cubre=bool(np.isfinite(low) and low<=truth[f]<=high),ancho=high-low))
   if 'porcentaje_distrito' in r:
    dp=pd.DataFrame(r['porcentaje_distrito'],index=r['distritos'],columns=FORCES)
    reald=td.reindex(dp.index);de=(dp-reald).abs()
    row['mae_distrito']=de.to_numpy().mean();row['ganadores_distrito']=(dp.idxmax(1)==reald.idxmax(1)).sum()
    for d in dp.index:
     for f in FORCES:districts.append(dict(**common,distrito=d,fuerza=f,punto=dp.loc[d,f],real=reald.loc[d,f],error=dp.loc[d,f]-reald.loc[d,f]))
   rows.append(row)
 d=pd.DataFrame(rows);d.to_csv(HERE/'evaluacion_muestras.csv',index=False)
 pd.DataFrame(forces).to_csv(HERE/'evaluacion_fuerzas.csv',index=False)
 pd.DataFrame(districts).to_csv(HERE/'evaluacion_distritos.csv',index=False)
 summary=d.groupby(['esquema','modelo'])[['mae_fuerzas','abs_error_margen','error_margen','inferencia_valida','cubre_margen','ancho_margen','mae_distrito','ganadores_distrito','brier']].mean()
 summary.to_csv(HERE/'RESUMEN.csv')
 actual=dict(nacional=truth.to_dict(),margen_JXC_FDT=float(rm),distritos=td.to_dict(orient='index'),mesas=len(w),votos_positivos=int(votes.sum()),evaluado_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 (HERE/'REAL_ABIERTO.json').write_text(json.dumps(actual,indent=2),encoding='utf8')
 print('Resultado reservado abierto para evaluación:',truth.round(3).to_dict(),'margen',round(rm,3))
 print(summary.round(3).to_string())

if __name__=='__main__':main()
