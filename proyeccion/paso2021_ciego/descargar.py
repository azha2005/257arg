from pathlib import Path
import requests,re,json,hashlib,datetime,zipfile

ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'datos_oficiales/2021_paso'
folder.mkdir(exist_ok=True)
u='https://www.argentina.gob.ar/dine/resultados-electorales/elecciones-2021'
s=requests.Session()
s.headers['User-Agent']='Dataelecc electoral historical research'
r=s.get(u,timeout=60);r.raise_for_status()
(folder/'pagina_fuente.html').write_text(r.text,encoding='utf8')
links=re.findall(r'href=["\']([^"\']+)["\']',r.text)
links=[x for x in links if '.zip' in x.lower() and 'paso' in x.lower()]
if not links:raise RuntimeError('No se encontró ZIP PASO: revisar enlaces de la página oficial')
from urllib.parse import urljoin
url=urljoin(u,links[0]);p=folder/'2021-provisorios_paso.zip'
if not p.exists():
 with s.get(url,stream=True,timeout=120) as res:
  res.raise_for_status()
  with p.open('wb') as f:
   for block in res.iter_content(1024*1024):f.write(block)
if not zipfile.is_zipfile(p):raise RuntimeError('La descarga no es ZIP')
with zipfile.ZipFile(p) as z:
 for info in z.infolist():
  target=(folder/'x'/info.filename).resolve()
  if not target.is_relative_to((folder/'x').resolve()):raise RuntimeError('Ruta insegura')
 z.extractall(folder/'x')
meta={'fuente':u,'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'descargado_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(folder/'FUENTE.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
print(json.dumps(meta,indent=2))
