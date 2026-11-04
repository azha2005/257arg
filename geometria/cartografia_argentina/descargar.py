"""Descarga a temporales, verifica formato e integridad y registra procedencia."""
from pathlib import Path
import concurrent.futures as cf
import hashlib,json,time,zipfile,requests,sys
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
sys.path.insert(0,str(ROOT/'_deps'))
MANIFEST=META/'descargas.json'
def check(path):
    if not path.stat().st_size:raise ValueError('Respuesta vacía')
    with path.open('rb') as f:head=f.read(512).lstrip()
    if head.lower().startswith((b'<html',b'<!doctype')):raise ValueError('HTML en lugar de datos')
    suffix=path.name.removesuffix('.part').split('.')[-1].lower()
    info={}
    if suffix in ('zip','docx'):
        with zipfile.ZipFile(path) as z:
            bad=z.testzip()
            if bad:raise ValueError('CRC inválido '+bad)
            info['miembros']=z.namelist()
    elif suffix in ('json','geojson'):
        with path.open(encoding='utf-8-sig') as f:j=json.load(f)
        if j.get('error') or j.get('errors'):raise ValueError(str(j)[:300])
        if 'features' in j:
            info['features']=len(j['features']);info['tipos_geometria']=sorted({(x.get('geometry') or {}).get('type','null') for x in j['features']})
    elif suffix=='pdf' and not head.startswith(b'%PDF'):raise ValueError('Cabecera PDF inválida')
    elif suffix=='rar' and not head.startswith(b'Rar!\x1a\x07'):raise ValueError('Cabecera RAR inválida')
    elif suffix=='gpkg' and not head.startswith(b'SQLite format 3\x00'):raise ValueError('Cabecera GeoPackage inválida')
    elif suffix=='parquet':
        import pyarrow.parquet as pq
        f=pq.ParquetFile(path)
        info.update(features=f.metadata.num_rows,campos=f.schema.names)
    return info
def fetch(job):
    row=dict(job);p=ROOT/job['archivo'];p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.part');t0=time.monotonic()
    try:
        if p.exists():row.update(check(p))
        else:
            with requests.get(job['url'],stream=True,timeout=(15,70),headers={'User-Agent':'ArgentinaCartographyResearch/1.0'}) as r:
                r.raise_for_status(); row['url_resuelta']=r.url;row['content_type']=r.headers.get('Content-Type');row['last_modified_servidor']=r.headers.get('Last-Modified')
                count=0
                with temp.open('wb') as out:
                    for block in r.iter_content(1024*1024):
                        out.write(block);count+=len(block)
                        if count>1500*1024*1024:raise ValueError('Supera 1,5 GB: revisar recurso antes de continuar')
                        if time.monotonic()-t0>900:raise TimeoutError('Descarga excede 15 minutos')
            row.update(check(temp));temp.replace(p)
        h=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
        row.update(estado='verificado',bytes=p.stat().st_size,sha256=h.hexdigest(),fecha_consulta='2026-10-31')
    except Exception as e:row.update(estado='error',error=str(e),fecha_consulta='2026-10-31')
    row['segundos']=round(time.monotonic()-t0,1)
    print(row['estado'],job['id'],row.get('bytes',''),row.get('error',''),flush=True)
    return row
def main():
    jobs=json.loads((ROOT/'plan_descargas.json').read_text(encoding='utf-8'))
    rows={r['id']:r for r in json.loads(MANIFEST.read_text(encoding='utf-8'))} if MANIFEST.exists() else {}
    jobs=[j for j in jobs if not (rows.get(j['id'],{}).get('estado')=='verificado' and (ROOT/j['archivo']).exists()) and not ('--new-only' in sys.argv and j['id'] in rows)]
    print('Pendientes',len(jobs),flush=True)
    with cf.ThreadPoolExecutor(5) as ex:
        for result in ex.map(fetch,jobs):
            rows[result['id']]=result
            MANIFEST.write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
