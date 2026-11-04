"""Auditoría y barrera de acceso de datos para el predictor (no una sandbox SO)."""
from pathlib import Path
import sys,json,datetime
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def guard(label):
 log=HERE/('accesos_'+label+'.jsonl')
 stream=log.open('w',encoding='utf8')
 seen=set()
 frozen=HERE.parent/'congelado_20261028/codigo'
 def hook(event,args):
  if event!='open' or not args or isinstance(args[0],int):return
  try:p=Path(args[0]).resolve()
  except (TypeError,ValueError):return
  if not p.is_relative_to(ROOT):return
  allowed=(p.is_relative_to(HERE) and not p.is_relative_to(HERE/'sellado')) or p.is_relative_to(frozen)
  if p==log:return
  if not allowed:
   stream.write(json.dumps({'path':str(p),'permitido':False})+'\n');stream.flush()
   raise PermissionError('Dato fuera del aislamiento: '+str(p))
  key=str(p)
  if key not in seen:
   seen.add(key);stream.write(json.dumps({'path':key,'permitido':True})+'\n');stream.flush()
 sys.addaudithook(hook)
 return stream
