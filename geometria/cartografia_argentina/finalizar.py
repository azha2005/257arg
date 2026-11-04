from pathlib import Path
import json,sys,hashlib,collections
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos';OUT=ROOT.parent/'catalogo_shp'
sys.path.insert(0,str(ROOT/'_deps'))
from descargar import check,fetch
manifest=META/'descargas.json'
rows=json.loads(manifest.read_text(encoding='utf-8'));byid={r['id']:r for r in rows}
for job in json.loads((ROOT/'plan_descargas.json').read_text(encoding='utf-8')):
    if not job['id'].startswith('sourcecoop_') or byid.get(job['id'],{}).get('estado')=='verificado':continue
    path=ROOT/job['archivo'];temp=path.with_name(path.name+'.part')
    if temp.exists():
        check(temp);temp.replace(path)
    byid[job['id']]=fetch(job)
manifest.write_text(json.dumps(list(byid.values()),ensure_ascii=False,indent=2),encoding='utf-8')
catalog=json.loads((OUT/'catalogo.json').read_text(encoding='utf-8'));errors=[];count=0;total=0
for row in catalog:
    folder=OUT/row['carpeta']
    if len(list(folder.glob('*.shp')))!=1:errors.append(dict(carpeta=row['carpeta'],error='No contiene exactamente un SHP'))
    for c in row['componentes']:
        p=folder/c['archivo'];data=p.read_bytes();count+=1;total+=len(data)
        if hashlib.sha256(data).hexdigest()!=c['sha256']:errors.append(dict(archivo=str(p),error='Hash diferente'))
all_shp=list(OUT.rglob('*.shp'))
if len(all_shp)!=len(catalog):errors.append(dict(error='Número físico de SHP diferente al catálogo',fisicos=len(all_shp),catalogo=len(catalog)))
result=dict(carpetas_shp=len(catalog),shp_fisicos=len(all_shp),componentes=count,bytes_componentes=total,conjuntos_componentes_distintos=len(set(r['firma_componentes'] for r in catalog)),por_anio=dict(sorted(collections.Counter(r['anio_carpeta'] for r in catalog).items())),faltantes_prj=sum('.prj' in r['faltan_componentes'] for r in catalog),errores=errors,descargas=collections.Counter(r['estado'] for r in byid.values()),bytes_descargados=sum(r.get('bytes',0) for r in byid.values()),geoParquet=[dict(archivo=r['archivo'],estado=r['estado'],features=r.get('features')) for r in byid.values() if r['id'].startswith('sourcecoop_') and r['archivo'].endswith('.parquet')])
(OUT/'validacion_final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if errors:raise SystemExit(1)
