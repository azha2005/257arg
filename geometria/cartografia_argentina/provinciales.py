from pathlib import Path
import requests,concurrent.futures as cf,re
from urllib.parse import urljoin
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
jobs=[('ipec_plantas2010','https://www.santafe.gov.ar/ipecinformes/plantasurbanas2010/'),('ipec_plantas2022','https://www.santafe.gov.ar/ipecinformes/plantasurbanas/'),('idesf_portal','https://www.santafe.gov.ar/idesf/geoportal/'),('georef_catalogo','https://www.datos.gob.ar/es/dataset/jgm-servicio-normalizacion-datos-geograficos/archivo/jgm_8.28')]
def get(job):
    name,url=job
    try:
        r=requests.get(url,timeout=(12,45));(META/(name+'.txt')).write_text(r.text,encoding='utf-8')
        print(name,r.status_code,len(r.content),flush=True)
        print('\n'.join(urljoin(r.url,x) for x in re.findall(r'(?:src|href)=[\"\x27]([^\"\x27]+)',r.text) if any(t in x.lower() for t in ['.js','.zip','geojson','download','descarga','xlsx','servicio','wfs'])),flush=True)
    except Exception as e:print(name,str(e),flush=True)
with cf.ThreadPoolExecutor(5) as ex:list(ex.map(get,jobs))
