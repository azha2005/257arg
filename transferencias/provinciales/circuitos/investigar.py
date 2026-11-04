"""Inventario público de granularidad y empalmes; no ajusta resultados."""
from pathlib import Path
import concurrent.futures as cf
import json
import requests
import urllib3
urllib3.disable_warnings()
HERE=Path(__file__).resolve().parent
RAW=HERE/'fuentes';RAW.mkdir(parents=True,exist_ok=True)
TASKS={
 'chaco_circuitos':('GET','https://resultados.electoralchaco.gob.ar/api/v1/circuitos/',dict(eleccion_id=15)),
 'chaco_municipios':('GET','https://resultados.electoralchaco.gob.ar/api/v1/municipios/',dict(eleccion_id=15)),
 'corrientes_circuitos':('GET','https://elecciones2025-definitivo-api.corrientes.gob.ar/api/escrutinio/circuitos/listadoconmesa',{}),
 'corrientes_filtro_circuito':('POST','https://elecciones2025-definitivo-api.corrientes.gob.ar/api/comun/filtroTipo',dict(filtroTipoId=4)),
}
def run(kv):
 name,(method,url,body)=kv;file=RAW/(name+'.json')
 try:
  if file.exists():j=json.loads(file.read_text(encoding='utf8'))
  else:
   r=requests.request(method,url,params=body if method=='GET' else None,json=body if method=='POST' else None,timeout=35,verify=False)
   r.raise_for_status();j=r.json();file.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
  print(name,str(j)[:1800],flush=True)
 except requests.RequestException as e:print(name,str(e),flush=True)
if __name__=='__main__':
 with cf.ThreadPoolExecutor(4) as pool:list(pool.map(run,TASKS.items()))
