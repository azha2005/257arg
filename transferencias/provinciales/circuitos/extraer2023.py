"""Nuevas provinciales 2023 por circuito y Santa Fe por distrito."""
import concurrent.futures as cf
import json
from pathlib import Path
import pandas as pd
import requests
from lxml import etree
from zipfile import ZipFile
from extraer_api import get_json,RAW,HERE,TR
ROOT=TR.parent

def chaco():
 units=json.loads((RAW/'chaco2023_circuitos.json').read_text(encoding='utf8'))['results']
 units=[u for u in units if u['circuito_id']]
 total=json.loads((RAW/'chaco2023_total.json').read_text(encoding='utf8'))['gobernador']
 ref=pd.Series({x['name']:int(x['value']) for x in total['totales_por_partido'] if isinstance(x['value'],(int,float))})
 ref['Blanco y nulo']=sum(int(x['value']) for x in total['no_positivos'])
 def task(u):
  j=get_json('chaco2023_circ_'+str(u['circuito_id'])+'.json','https://resultados.electoralchaco.gob.ar/api/v1/resultados/resultados-provinciales/',
   params=dict(eleccion_id=3,tipo_resultado='escrutinio_definitivo',departamento_id='',municipio_id='',circuito_id=u['circuito_id'],mesa_id=''))
  d=j['gobernador'];row={x['name']:int(x['value']) for x in d['totales_por_partido'] if x['name'] in ref.index and isinstance(x['value'],(int,float))}
  row['Blanco y nulo']=sum(int(x['value']) for x in d['no_positivos'])
  if len(row)==1:
   assert row['Blanco y nulo']==0
   return None
  assert set(row)==set(ref.index),(u,set(row),set(ref.index))
  row.update(circuito=u['circuito_nombre'],departamento=u['departamento_nombre'],municipio=u['municipio_nombre'],id_api=u['circuito_id'])
  return row
 with cf.ThreadPoolExecutor(4) as pool:t=pd.DataFrame([r for r in pool.map(task,units) if r is not None])
 assert not t.isna().any().any()
 print('CHACO2023',len(t),'diferencias vs total',(t[ref.index].sum()-ref).to_dict(),flush=True)
 t.to_pickle(HERE/'chaco2023.pkl');t.to_csv(HERE/'chaco2023.csv',index=False,encoding='utf-8-sig')

def ods(file):
 # Evita dependencia odf; expande celdas repetidas, conservando texto.
 ns={'t':'urn:oasis:names:tc:opendocument:xmlns:table:1.0','x':'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
 root=etree.fromstring(ZipFile(file).read('content.xml'))
 out=[]
 for sheet in root.xpath('//t:table',namespaces=ns):
  rows=[]
  for tr in sheet.xpath('./t:table-row',namespaces=ns):
   row=[]
   for td in tr:
    val=' '.join(td.xpath('.//x:p//text()',namespaces=ns))
    n=int(td.get('{'+ns['t']+'}number-columns-repeated','1'))
    row.extend([val]*min(n,30))
   if any(row):rows.append(row)
  out.append((sheet.get('{'+ns['t']+'}name'),rows))
 return out

def santafe():
 url='https://www.santafe.gov.ar/tribunalelectoral/wp-content/uploads/sites/84/2024/08/resultadosGenerales2023.ods'
 f=RAW/'santafe2023.ods'
 if not f.exists():
  r=requests.get(url,timeout=50);r.raise_for_status();f.write_bytes(r.content)
 for name,rows in ods(f):
  print('SF2023 hoja',name,'filas',len(rows),'muestra',rows[:3],flush=True)
  pd.to_pickle(rows,HERE/('sf2023_'+name.replace('/','_')+'.pkl'))

def dine():
 file=next(x for x in (ROOT/'datos_oficiales/2023/x').rglob('*.csv') if 'resultado' in x.name.lower())
 cols=['distrito_id','seccion_id','seccion_nombre','circuito_id','circuito_nombre','mesa_id','mesa_tipo','cargo_nombre','agrupacion_nombre','votos_tipo','votos_cantidad']
 tables=[]
 for ch in pd.read_csv(file,dtype=str,usecols=cols,chunksize=1500000):
  mask=ch.cargo_nombre.str.contains('GOBERNADOR|JEFE',case=False,na=False)&ch.mesa_tipo.eq('NATIVOS')
  v=ch[mask].copy()
  if v.empty:continue
  v['v']=pd.to_numeric(v.votos_cantidad)
  keys=[c for c in cols if c not in ['mesa_id','votos_cantidad']]
  tables.append(v.groupby(keys,dropna=False).v.sum().reset_index())
 t=pd.concat(tables).groupby(keys,dropna=False).v.sum().reset_index()
 t.to_pickle(HERE/'dine_gob2023.pkl');t.to_csv(HERE/'dine_gob2023.csv',index=False,encoding='utf-8-sig')
 print('DINEGOB',t.groupby('distrito_id').v.sum().to_dict(),flush=True)

if __name__=='__main__':
 import sys
 funcs={'chaco':chaco,'santafe':santafe,'dine':dine}
 with cf.ThreadPoolExecutor(3) as pool:list(pool.map(lambda n:funcs[n](),sys.argv[1:] or funcs))
