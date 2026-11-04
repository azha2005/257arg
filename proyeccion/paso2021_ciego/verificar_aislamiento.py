"""Controles de separación y de diseño, antes de observar métricas del destino."""
import pandas as pd,numpy as np,json,hashlib
from config import SCHEMES,REPS,KEY
from comun_experimento import HERE,select
from aislar import guard

def main():
 log=guard('pruebas')
 blocked=[]
 for p in [HERE/'sellado/mesas_2021paso.pkl',HERE.parent/'mesas_2021.pkl',HERE.parent/'mesas_2025bl.pkl']:
  try:p.open('rb')
  except PermissionError:blocked.append(str(p))
  else:raise AssertionError('El aislamiento permitió un resultado reservado o posterior')
 frame=pd.read_pickle(HERE/'permitidos/marco_2021_paso.pkl')
 assert set(frame.columns)==set(KEY+['e'])
 for scheme in SCHEMES:
  for rep in range(REPS):
   idx=select('2021_paso',scheme,rep)
   assert len(idx)==len(set(idx))==30
   if scheme=='twitter_parcial':np.testing.assert_array_equal(idx,select('2021_paso','twitter',rep))
 assert frame[KEY].duplicated().sum()==0
 (HERE/'CONTROLES.json').write_text(json.dumps({'accesos_prohibidos_bloqueados':blocked,'muestras_30_unicas':REPS*len(SCHEMES),'marco_sin_votos':True,'twitter_parcial_mismas_mesas':True},indent=2),encoding='utf8')
 print('Aislamiento comprobado, marco sin votos, 700 selecciones de 30 mesas únicas')

if __name__=='__main__':main()
