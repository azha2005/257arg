"""API pública que utiliza el visor oficial del escrutinio definitivo."""
import json
import requests
import pandas as pd
import urllib3
from fuentes import HERE,RAW
urllib3.disable_warnings()
BASE='https://resultados.electoralchaco.gob.ar'
S=requests.Session()
S.verify=False

def get(name,path,params):
 f=RAW/('chaco_'+name+'.json')
 if not f.exists():
  r=S.get(BASE+path,params=params,timeout=35);r.raise_for_status()
  f.write_text(json.dumps(r.json(),ensure_ascii=False,indent=2),encoding='utf8')
 return json.loads(f.read_text(encoding='utf8'))

if __name__=='__main__':
 S.get(BASE+'/historico/',timeout=25)
 dep=get('departamentos','/api/v1/departamentos/',{'eleccion_id':15})
 params=dict(eleccion_id=15,tipo_resultado='escrutinio_definitivo',departamento_id='',municipio_id='',circuito_id='',mesa_id='')
 total=get('general','/api/v1/resultados/resultados-provinciales/',params)
 rows=[]
 for unit in dep['results']:
  if str(unit['id']).isdigit() and unit['id']!=0:
   p=dict(params,departamento_id=unit['id'])
   data=get('dep_'+str(unit['id']),'/api/v1/resultados/resultados-provinciales/',p)
   row={x['name']:x['value'] for x in data['diputados']['totales_por_partido']}
   row['Blanco y nulo']=sum(x['value'] for x in data['diputados']['no_positivos'])
   row['unidad']=unit['text']
   rows.append(row)
 t=pd.DataFrame(rows).set_index('unidad')
 assert not t.isna().any().any()
 reference={x['name']:x['value'] for x in total['diputados']['totales_por_partido']}
 reference['Blanco y nulo']=sum(x['value'] for x in total['diputados']['no_positivos'])
 assert t.sum().to_dict()==reference,(t.sum()-pd.Series(reference)).to_dict()
 t.to_pickle(HERE/'prov_chaco.pkl')
 t.to_csv(HERE/'prov_chaco.csv',encoding='utf-8-sig')
 print('CHACO',t.shape,t.sum().to_dict(),flush=True)
