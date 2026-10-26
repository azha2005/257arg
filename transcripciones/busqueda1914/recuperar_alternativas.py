from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,csv
root=Path(__file__).resolve().parent
targets=[('Corrientes','https://web.archive.org/web/20220509003432id_/https://apym.hcdn.gob.ar/uploads/expedientes/pdf/21-d-1914.pdf'),('Mendoza','https://web.archive.org/web/20220509003441id_/https://apym.hcdn.gob.ar/uploads/expedientes/pdf/29-p-1914.pdf'),('Corrientes','https://apym.hcdn.gob.ar/uploads/expedientes/pdf/21-p-1914.pdf'),('Mendoza','https://apym.hcdn.gob.ar/uploads/expedientes/pdf/29-d-1914.pdf')]
def run(pair):
    province,url=pair;s=requests.Session();s.trust_env=False
    row=dict(provincia=province,url=url,fecha_consulta='2026-10-15',tamano_bytes=0,estado='',archivo='')
    try:
        r=s.get(url,timeout=30,headers={'User-Agent':'AtlasElectoralResearch/1.0 (https://commons.wikimedia.org/wiki/User:ItsAHardLife)'})
        row['estado']=str(r.status_code)
        if r.ok and r.content.startswith(b'%PDF'):
            name=province.lower()+'_'+('wayback_' if 'archive.org' in url else 'alternativa_')+url.split('/')[-1]
            p=root/'fuentes'/name;p.write_bytes(r.content)
            row.update(tamano_bytes=len(r.content),archivo=str(p.relative_to(root)),estado='descargado; verificar distrito y año')
    except Exception as e: row['estado']=str(e)
    print(province,row['estado'],flush=True);return row
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(run,targets))
    with (root/'fuentes_alternativas.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
