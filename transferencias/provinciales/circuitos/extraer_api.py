"""Descarga territorial del mismo API público que emplean los visores."""
from pathlib import Path
import concurrent.futures as cf
import json
import re
import sys
import requests
import urllib3
import pandas as pd
urllib3.disable_warnings()
HERE=Path(__file__).resolve().parent;RAW=HERE/'fuentes'
TR=HERE.parents[1]

def get_json(name,url,params=None,body=None):
 f=RAW/name
 if not f.exists():
  for retry in range(3):
   try:
    r=requests.request('POST' if body is not None else 'GET',url,params=params,json=body,timeout=40,verify=False)
    r.raise_for_status();j=r.json()
    f.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8');break
   except requests.RequestException:
    if retry==2:raise
 return json.loads(f.read_text(encoding='utf8'))

def chaco():
 units=json.loads((RAW/'chaco_circuitos.json').read_text(encoding='utf8'))['results']
 units=[x for x in units if x['circuito_id']]
 def task(u):
  j=get_json('chaco_circ_'+str(u['circuito_id'])+'.json','https://resultados.electoralchaco.gob.ar/api/v1/resultados/resultados-provinciales/',
   params=dict(eleccion_id=15,tipo_resultado='escrutinio_definitivo',departamento_id='',municipio_id='',circuito_id=u['circuito_id'],mesa_id=''))
  d=j['diputados'];row={x['name']:int(x['value']) for x in d['totales_por_partido']}
  row['Blanco y nulo']=sum(int(x['value']) for x in d['no_positivos'])
  if not d['totales_por_partido']:
   assert row['Blanco y nulo']==0
   return None # circuitos reflejados en otros, según aviso oficial
  row.update(circuito=u['circuito_nombre'],departamento=u['departamento_nombre'],municipio=u['municipio_nombre'],id_api=u['circuito_id'])
  return row
 with cf.ThreadPoolExecutor(4) as pool:rows=[r for r in pool.map(task,units) if r is not None]
 t=pd.DataFrame(rows)
 assert not t.isna().any().any(),t.loc[:,t.isna().any()].to_dict()
 t.to_pickle(HERE/'chaco2025.pkl');t.to_csv(HERE/'chaco2025.csv',index=False,encoding='utf-8-sig')
 ref=pd.read_pickle(TR/'provinciales2025/prov_chaco.pkl').sum()
 diff=t[ref.index].sum()-ref
 print('CHACO',len(t),'diferencias contra total',diff.to_dict(),flush=True)
 return t

def corrientes():
 units=next(x['datos'] for x in json.loads((RAW/'corrientes_filtro_circuito.json').read_text(encoding='utf8')) if x['filtroTipoId']==4)
 def task(u):
  j=get_json('corrientes_circ_'+str(u['valor'])+'.json','https://elecciones2025-definitivo-api.corrientes.gob.ar/api/escrutinio/resultados/buscar',
   body=dict(filtroTipoId=4,valor=u['valor'],descripcion='Circuito',seleccionUnica=True,valorDescripcion=u['descripcion']))['data']
  rows=[]
  for cargo in ['Gobernador','Diputados','Senadores']:
   row={}
   for a in j['alianzas']:
    value=next((v['votos'] for v in a['alianzaData'] if v['titulo']==cargo),None)
    if value is not None:row[a['alianza']]=value
   row['Blanco y nulo']=sum(v['votos'] for p in j['partidos'] if p['partido'].upper().startswith('VOTOS ') for v in p['partidoData'] if v['titulo']==cargo)
   total=next(x['totalGeneral'] for x in j['totalVotos'] if x['cargoDescripcion']==cargo)
   assert sum(row.values())==total,(u,cargo,row,total)
   row.update(cargo=cargo,circuito=u['descripcion'].split(' - ')[0].strip(),nombre=u['descripcion'],id_api=u['valor'])
   rows.append(row)
  return rows
 with cf.ThreadPoolExecutor(4) as pool:result=list(pool.map(task,units))
 t=pd.DataFrame([r for batch in result for r in batch]).fillna(0)
 t.to_pickle(HERE/'corrientes2025.pkl');t.to_csv(HERE/'corrientes2025.csv',index=False,encoding='utf-8-sig')
 for cargo,g in t.groupby('cargo'):
  ref=pd.read_pickle(TR/('provinciales2025/prov_corrientes_'+cargo.lower()+'.pkl')).drop(columns='control_total').sum()
  print('CORRIENTES',cargo,len(g),'diferencias vs departamentos',(g[ref.index].sum()-ref).to_dict(),flush=True)
 return t

if __name__=='__main__':
 funcs={'chaco':chaco,'corrientes':corrientes}
 for name in sys.argv[1:] or list(funcs):funcs[name]()
