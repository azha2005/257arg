from pathlib import Path
import sys,json,hashlib,zipfile,io,collections,xml.etree.ElementTree as ET,subprocess,sqlite3
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
sys.path.insert(0,str(ROOT/'_deps'))
sys.path.insert(0,str(ROOT.parent/'circuitos_busqueda/_deps'))
import shapefile
downloads=json.loads((META/'descargas.json').read_text(encoding='utf-8'))
layers=[];issues=[]

class RarReader:
    def __init__(self,path):
        self.path=path
        self.names=subprocess.check_output(['tar','-tf',str(path)],text=True,encoding='utf-8').splitlines()
    def namelist(self):return self.names
    def read(self,name):return subprocess.check_output(['tar','-xOf',str(self.path),name])
def shp_info(z,member,source):
    source=dict(source)
    if source['id'].startswith('ipec_'):
        first=member.split('/')[-1][:1].lower()
        source['tipo']={'r':'radio censal (planta urbana)','m':'manzana censal (auxiliar)','e':'eje de calle (auxiliar)'}.get(first,'cartografía urbana IPEC (auxiliar)')
        source['nota']=source.get('nota','')+' Las notas internas de la muestra publicada bajo 2022 conservan referencias a 2010 y campos frac2020/rad2020. El año de carpeta sigue el catálogo, no certifica por sí solo vigencia de cada borde.'
    stem=member[:-4];lookup={n.lower():n for n in z.namelist()}
    get=lambda ext:z.read(lookup[(stem+ext).lower()])
    r=shapefile.Reader(shp=io.BytesIO(get('.shp')),shx=io.BytesIO(get('.shx')),dbf=io.BytesIO(get('.dbf')),encoding='latin1')
    count_shx=(len(get('.shx'))-100)//8
    fields=[f[0] for f in r.fields[1:]]
    row=dict(id_fuente=source['id'],archivo=source['archivo']+'!'+member,tipo=source['tipo'],corte=source['corte'],cobertura=source['cobertura'],features=len(r),registros_shx=count_shx,shape_type=r.shapeType,bbox=list(r.bbox),campos=fields,formato='SHP',fuente=source['fuente'])
    row.update(nota=source.get('nota',''),licencia=source.get('licencia','Consultar fuente'),url_descarga=source.get('url',''))
    try:row['crs_wkt']=get('.prj').decode('utf-8',errors='replace')
    except KeyError:row['crs_wkt']=None
    try:row['encoding_declarado']=get('.cpg').decode('ascii',errors='replace').strip()
    except KeyError:pass
    if count_shx!=len(r):issues.append(dict(archivo=row['archivo'],error='Cantidad de geometrías SHX y registros DBF difiere'))
    pfield=next((f for f in ['PROV','cpr','provincia','PROVINCIA'] if f in fields),None)
    key=next((f for f in fields if f.startswith('COD_') and not f.endswith('_B')),None) or next((f for f in ['cod_indec','link','LINK','CODIGO'] if f in fields),None)
    needed={f for f in [pfield,key] if f};counts=collections.Counter();codes=[]
    if needed:
        for record in r.iterRecords(fields=list(needed)):
            d=record.as_dict()
            if pfield:counts[str(d.get(pfield))]+=1
            if key:codes.append(str(d.get(key)))
    if counts:row['entidades_por_provincia']=dict(counts)
    if key:row.update(campo_codigo=key,codigos_distintos=len(set(codes)),codigos_vacios=sum(not c.strip() or c=='None' for c in codes))
    return row
for row in downloads:
    if row['estado']!='verificado':continue
    p=ROOT/row['archivo']
    try:
        if p.suffix.lower()=='.zip':
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if n.lower().endswith('.shp') and not n.startswith('__MACOSX/'):
                        layers.append(shp_info(z,n,row))
                    elif row['id'].startswith('ipec_') and n.lower().endswith('metadatos.zip'):
                        # Conserva las notas de cada localidad junto al archivo original.
                        dest=p.with_suffix('.metadatos.zip')
                        if not dest.exists():dest.write_bytes(z.read(n))
        elif p.suffix.lower() in ('.json','.geojson'):
            j=json.loads(p.read_text(encoding='utf-8-sig'));fs=j.get('features',[])
            if 'features' not in j:continue
            layers.append(dict(id_fuente=row['id'],archivo=row['archivo'],tipo=row['tipo'],corte=row['corte'],cobertura=row['cobertura'],formato='GeoJSON',features=len(fs),tipos_geometria=dict(collections.Counter((f.get('geometry') or {}).get('type','null') for f in fs)),fuente=row['fuente']))
        elif p.suffix.lower()=='.rar':
            z=RarReader(p)
            for n in z.namelist():
                if n.lower().endswith('.shp'):layers.append(shp_info(z,n,row))
        elif p.suffix.lower()=='.gpkg':
            with sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True) as db:
                for table,geom,kind,srs in db.execute('SELECT table_name,column_name,geometry_type_name,srs_id FROM gpkg_geometry_columns'):
                    safe='"'+table.replace('"','""')+'"'
                    count=db.execute('SELECT count(*) FROM '+safe).fetchone()[0]
                    columns=[x[1] for x in db.execute('PRAGMA table_info('+safe+')')]
                    layers.append(dict(id_fuente=row['id'],archivo=row['archivo']+'!'+table,tipo=row['tipo'],corte=row['corte'],cobertura=row['cobertura'],formato='GPKG',features=count,campos=columns,tipo_geometria=kind,srs_id=srs,fuente=row['fuente'],sqlite_integrity=db.execute('PRAGMA quick_check').fetchone()[0]))
        elif p.suffix.lower()=='.parquet':
            import pyarrow.parquet as pq
            f=pq.ParquetFile(p);meta=f.schema_arrow.metadata or {};geo=json.loads(meta.get(b'geo',b'{}'))
            if not geo:raise ValueError('Parquet sin metadatos GeoParquet: no contar como geometría')
            layers.append(dict(id_fuente=row['id'],archivo=row['archivo'],tipo=row['tipo'],corte=row['corte'],cobertura=row['cobertura'],formato='GeoParquet',features=f.metadata.num_rows,campos=f.schema.names,geo=geo,fuente=row['fuente'],nota=row.get('nota',''),licencia=row.get('licencia','')))
    except Exception as e:issues.append(dict(archivo=row['archivo'],error=str(e)))
for layer in layers:
    ident=layer['id_fuente']
    if ident.startswith('indec2022_'):
        name=ident.removeprefix('indec2022_')
        f=META/('indec_hits_'+name+'.xml') if name!='radios' else META/'indec_hits.txt'
        if f.exists():
            t=ET.fromstring(f.read_text(encoding='utf-8'));num=t.attrib.get('numberOfFeatures') or t.attrib.get('numberMatched')
            if num and num.isdigit():
                layer['features_wfs_hits']=int(num)
                if int(num)!=layer['features']:issues.append(dict(archivo=layer['archivo'],error='Conteo WFS hits y archivo difiere',esperado=int(num),actual=layer['features']))

existing=[]
for p in (ROOT.parent/'Base deptos 1869-2022').glob('*.shp'):
    r=shapefile.Reader(str(p),encoding='latin1');h=hashlib.sha256(p.read_bytes()).hexdigest()
    existing.append(dict(archivo=str(p.resolve()),features=len(r),sha256_shp=h,nota='Preexistente en proyecto. No se reemplazó. Cotejar con ZIP CONICET actual antes de asumir igualdad.'))
(META/'inventario_capas.json').write_text(json.dumps(layers,ensure_ascii=False,indent=2),encoding='utf-8')
(META/'validacion.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
(META/'departamentos_preexistentes.json').write_text(json.dumps(existing,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Inventario de capas descargadas','', 'Entidades = registros geométricos, no necesariamente códigos distintos. Los años se conservan por fuente; las fechas de publicación no sustituyen vigencia. No se disolvieron ni repararon límites.', '', '| Tipo | Corte / evidencia | Cobertura declarada | Archivo | Entidades |','|---|---|---|---|---:|']
from urllib.parse import quote
for r in layers:
    path=r['archivo'].split('!')[0];lines.append(f'| {r["tipo"]} | {r["corte"]} | {r["cobertura"]} | [{r["archivo"]}]({quote(path)}) | {r["features"]} |')
(ROOT/'INVENTARIO.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('CAPAS',len(layers),'INCIDENCIAS',issues,'PREEXISTENTES',len(existing),flush=True)
print('\n'.join(str((r['id_fuente'],r['archivo'].split('!')[-1],r['features'],r.get('codigos_distintos'),r.get('features_wfs_hits'))) for r in layers if r['id_fuente'].startswith(('conicet','indec2022','georef'))),flush=True)
