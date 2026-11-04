from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import json,re,requests,concurrent.futures as cf
ROOT=Path(__file__).resolve().parent
META=ROOT/'metadatos';META.mkdir(exist_ok=True)
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        for key in ('href','src'):
            if key in d:self.links.append(d[key])
for name,base in [('conicet_radios','https://ri.conicet.gov.ar/'),('indec_radios','https://geonode.indec.gob.ar/'),('poblaciones','https://poblaciones.org/')]:
    txt=(META/(name+'.html')).read_text(encoding='utf-8')
    parser=Links();parser.feed(txt)
    print(name,flush=True)
    if name.startswith('conicet'):print(txt[:1500],flush=True)
    print('\n'.join(urljoin(base,u) for u in parser.links if any(s in u.lower() for s in ['download','zip','geojson','municipio','gobierno','radios','wfs','wp-content/uploads'])),flush=True)

jobs=[('conicet_radios_alt','https://datosdeinvestigacion.conicet.gov.ar/handle/11336/149711'),('conicet_deptos_alt','https://datosdeinvestigacion.conicet.gov.ar/handle/11336/149867?show=full'),('argentina_geography_tree','https://api.github.com/repos/matuteiglesias/argentina-geography/git/trees/main?recursive=1'),('pba_radios','https://catalogo.datos.gba.gob.ar/api/3/action/package_show?id=radios-censales'),('caba_radios','https://data.buenosaires.gob.ar/api/3/action/package_show?id=informacion-censal-por-radio')]
def fetch(job):
    name,u=job
    try:
        r=requests.get(u,timeout=(10,35));(META/(name+'.txt')).write_text(r.text,encoding='utf-8');print(name,r.status_code,len(r.content),flush=True)
        if 'tree' in name:
            print([x['path'] for x in r.json().get('tree',[]) if any(s in x['path'].lower() for s in ['source','municip','radios','manifest','download'])][:90],flush=True)
    except Exception as e:print(name,str(e),flush=True)
with cf.ThreadPoolExecutor(5) as ex:list(ex.map(fetch,jobs))
