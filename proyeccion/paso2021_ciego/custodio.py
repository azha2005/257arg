"""Revela solo las 30 actas seleccionadas sin mostrar el total reservado."""
from pathlib import Path
import json,hashlib,pandas as pd
from config import SCHEMES,REPS
from comun_experimento import HERE,select,reveal

if __name__=='__main__':
 w=pd.read_pickle(HERE/'sellado/mesas_2021paso.pkl')
 out=HERE/'actas_reveladas';out.mkdir(exist_ok=True)
 selections=[]
 for scheme in SCHEMES:
  for rep in range(REPS):
   idx=select('2021_paso',scheme,rep);a=reveal(w,idx,scheme)
   path=out/('%s_%03d.json'%(scheme,rep))
   path.write_text(a.to_json(orient='records',force_ascii=False),encoding='utf8')
   selections.append(dict(esquema=scheme,rep=rep,filas_origen=idx.tolist(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 print('Reveladas',len(selections),'colecciones de 30 mesas; no se abrió el total al predictor')
 (HERE/'selecciones.json').write_text(json.dumps(selections,indent=2),encoding='utf8')
