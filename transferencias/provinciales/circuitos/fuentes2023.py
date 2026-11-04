from pathlib import Path
import concurrent.futures as cf
import requests
import lxml.html
from extraer_api import get_json,RAW
URLS={
 'santafe2023':'https://www.santafe.gob.ar/ms/tribunalelectoral/eleccion/elecciones-2023/',
 'santafe2023_nuevo':'https://www.santafe.gov.ar/tribunalelectoral/elecciones/elecciones-2023/',
 'mendoza2023':'https://elecciones.mendoza.gob.ar/resultados-escrutinios/',
 'cordoba2023':'https://elecciones2023.cba.gov.ar/',
 'misiones2023':'https://www.electoralmisiones.gov.ar/elecciones-generales-2023/',
 'sanluis2023':'https://electoral.justiciasanluis.gov.ar/?page_id=3636',
}
def task(kv):
 name,url=kv;f=RAW/(name+'.html')
 try:
  if not f.exists():
   r=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0'});r.raise_for_status();f.write_bytes(r.content)
  doc=lxml.html.fromstring(f.read_bytes());doc.make_links_absolute(url)
  links=[(x.get('href'),x.text_content().strip()[:90]) for x in doc.xpath('//a[@href]') if any(s in ((x.get('href')or'')+x.text_content()).lower() for s in ['ods','csv','xlsx','resultados','escrutinio'])]
  print(name,links[-35:],flush=True)
 except requests.RequestException as e:print(name,type(e).__name__,str(e)[:100],flush=True)
if __name__=='__main__':
 with cf.ThreadPoolExecutor(4) as pool:list(pool.map(task,URLS.items()))
 for name,path in [('circuitos','/api/v1/circuitos/'),('municipios','/api/v1/municipios/'),('total','/api/v1/resultados/resultados-provinciales/')]:
  params=dict(eleccion_id=3)
  if name=='total':params.update(tipo_resultado='escrutinio_definitivo',departamento_id='',municipio_id='',circuito_id='',mesa_id='')
  try:
   j=get_json('chaco2023_'+name+'.json','https://resultados.electoralchaco.gob.ar'+path,params=params)
   print('chaco2023',name,str(j)[:600],flush=True)
  except requests.RequestException as e:print('chaco2023',name,str(e),flush=True)
