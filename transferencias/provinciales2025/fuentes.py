"""Fuentes públicas de elecciones desdobladas de 2025; conserva originales."""
from pathlib import Path
import concurrent.futures as cf
import hashlib
import json
import lxml.html
import requests
import urllib3

HERE = Path(__file__).resolve().parent
RAW = HERE / 'fuentes'
RAW.mkdir(exist_ok=True)
MANIFEST = RAW / 'manifest.json'
INDEX = {
    'pba':'https://www.juntaelectoral.gba.gov.ar/escrutinio-definitivo-2025/escrutinio-argentinos/index.html',
    'salta':'https://www.electoralsalta.gov.ar/elecciones/generales/escrutinio-definitivo',
    'misiones':'https://www.electoralmisiones.gov.ar/elecciones-legislativas-provinciales-2025-resultados-del-escrutinio-definitivo/',
    'jujuy':'https://www.electoraljujuy.gob.ar/index.php/estadisticas/elecciones-2005-2021/elecc-11-de-mayo-de-2025',
    'chaco':'https://resultados.electoralchaco.gob.ar/historico/',
    'formosa':'https://tep.jusformosa.gob.ar/resultados',
    'corrientes':'https://elecciones2025-definitivo.corrientes.gob.ar/escrutinio',
    'sanluis':'https://escrutinio.sanluis.gov.ar/EPSLAsp/Resultados/Resultado.asp',
    'santafe':'https://www.santafe.gov.ar/elecciones2025/resultadosEscrutinio/',
    'caba':'https://data.buenosaires.gob.ar/api/3/action/package_show?id=elecciones-2025',
}


def descargar(name,url):
    p=RAW/name
    if not p.exists():
        # El certificado intermedio de Chaco no está en el almacén del host;
        # se documenta esa limitación en el catálogo de fuentes.
        verify='electoralchaco.gob.ar' not in url
        with requests.Session() as s:
            for i in range(3):
                try:
                    r=s.get(url,timeout=35,verify=verify)
                    r.raise_for_status()
                    p.write_bytes(r.content)
                    break
                except requests.RequestException:
                    if i==2:raise
    return p


def enlaces(path,base):
    t=lxml.html.fromstring(path.read_bytes())
    t.make_links_absolute(base)
    return [(a.get('href'),a.text_content().strip()) for a in t.xpath('//a[@href]')]


if __name__=='__main__':
    def task(kv):
        k,u=kv
        try:
            p=descargar(k+'_indice.'+('json' if k=='caba' else 'html'),u)
            if k=='caba':
                links=[(x['url'],x['name']) for x in json.loads(p.read_text(encoding='utf8'))['result']['resources']]
            else:links=enlaces(p,u)
            relevant=[(u,n) for u,n in links if any(s in (u+n).lower() for s in ['xlsx','csv','ods','pdf','2025','1229','convencional','escrutinio','resultado'])]
            print(k,relevant[-40:],flush=True)
            return k,dict(url=u,enlaces=links,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        except Exception as e:
            print(k,str(e),flush=True)
            return k,dict(url=u,error=str(e))
    with cf.ThreadPoolExecutor(5) as pool:
        result=dict(pool.map(task,INDEX.items()))
    MANIFEST.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
