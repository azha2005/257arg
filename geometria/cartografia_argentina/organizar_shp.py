"""Copias por año y capa. Preserva bytes y procedencia; no altera originales."""
from pathlib import Path, PurePosixPath
from urllib.parse import quote
import sys,json,re,zipfile,io,hashlib,subprocess,collections,unicodedata
ROOT=Path(__file__).resolve().parent;GEO=ROOT.parent;OUT=GEO/'catalogo_shp'
sys.path.insert(0,str(GEO/'circuitos_busqueda/_deps'))
import shapefile
OUT.mkdir(exist_ok=True)
entries=[];seen=set();errors=[];archive_handles=[]
EXTS={'.shp','.shx','.dbf','.prj','.qpj','.cpg','.sbn','.sbx','.shp.xml','.xml','.qix','.fix','.qmd','.sld','.lyr','.avl','.ain','.aih','.atx','.fbn','.fbx','.idm','.ind'}
def slug(s,n=40):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
    return re.sub('[^A-Za-z0-9_-]+','_',s).strip('_')[:n] or 'capa'
def add(base,info):
    key=str(base.resolve())+'!'+info['archivo']
    if key in seen:return
    seen.add(key);entries.append((base,dict(info)))
for base in [ROOT,GEO/'circuitos_busqueda']:
    for r in json.loads((base/'metadatos/inventario_capas.json').read_text(encoding='utf-8')):
        if r.get('formato')=='SHP':add(base,r)
for p in GEO.rglob('*.shp'):
    rel=p.relative_to(GEO)
    if rel.parts[0] in ('catalogo_shp','cartografia_argentina','circuitos_busqueda'):continue
    add(GEO,dict(archivo=rel.as_posix(),formato='SHP',tipo='departamento' if rel.parts[0].startswith('Base deptos') else 'cartografía preexistente',fuente='Archivo preexistente del proyecto; consultar README de su carpeta',nota='Original local conservado; no se presume identidad con la descarga nueva.'))
class Rar:
    def __init__(self,p):self.p=p;self.names=subprocess.check_output(['tar','-tf',str(p)],text=True,encoding='utf-8').splitlines()
    def namelist(self):return self.names
    def read(self,n):return subprocess.check_output(['tar','-xOf',str(self.p),n])
def archive(p):
    return Rar(p) if p.suffix.lower()=='.rar' else zipfile.ZipFile(p)
def access(base,locator):
    parts=locator.split('!');p=base/parts[0]
    if len(parts)==1:
        return [x.name for x in p.parent.iterdir() if x.is_file()],lambda n:(p.parent/n).read_bytes(),p.name
    z=archive(p);archive_handles.append(z)
    for part in parts[1:-1]:
        z=zipfile.ZipFile(io.BytesIO(z.read(part)));archive_handles.append(z)
    return z.namelist(),z.read,parts[-1]
# Incluye el archivo ZIP anidado del paquete departamental.
for row in json.loads((ROOT/'metadatos/descargas.json').read_text(encoding='utf-8')):
    p=ROOT/row['archivo']
    if row['estado']!='verificado' or p.suffix.lower()!='.zip':continue
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if n.lower().endswith('.zip'):
                with zipfile.ZipFile(io.BytesIO(z.read(n))) as sub:
                    for member in sub.namelist():
                        if member.lower().endswith('.shp'):
                            info=dict(row,archivo=row['archivo']+'!'+n+'!'+member,formato='SHP')
                            if row['id'].startswith('ipec_'):
                                info['tipo']={'r':'radio censal (planta urbana)','m':'manzana censal (auxiliar)','e':'eje de calle (auxiliar)'}.get(PurePosixPath(member).name[:1].lower(),'cartografía urbana IPEC')
                                info['nota']=row.get('nota','')+' Capa hallada en ZIP anidado: conservar el nombre del archivo interno al identificar la localidad.'
                            add(ROOT,info)
def year_of(r):
    loc=r['archivo'];name=loc.split('!')[-1].split('/')[-1]
    evidence=r.get('corte') or r.get('corte_declarado') or ''
    # Los departamentos contienen el año censal en el nombre, además del año de edición.
    m=re.search(r'Departamentos[_ ]+(18\d\d|19\d\d|20\d\d)(?!\d)',name,re.I)
    if m:return m[1],'Año censal identificado en nombre de capa y colección departamental'
    if re.fullmatch(r'(18|19|20)\d\d',evidence):return evidence,'Corte declarado en inventario de la fuente'
    if 'precenso_' in r.get('id_fuente',r.get('id','')):return '2019-2020','Período del Precenso; no demuestra límites nuevos de esos años'
    if 'snapshot_20190308/' in loc:return '2019','Copia existente en marzo de 2019; vigencia electoral no verificada'
    if loc.startswith('caba_2015/') or loc.startswith('nyu_caba_2015/'):return '2015','Dataset de la elección 2015'
    if '/extraido_2011/' in loc:return '2011','Corte expresamente identificado por catálogo Córdoba'
    if loc.startswith('aporte_usuario/'):
        for token,yr in [('bsas_circuitos01','2001'),('bsas_circuitos03','2003'),('er_circuitos95','1995'),('er_circuitos99','1999')]:
            if token.lower() in name.lower():return yr,'README interno del ZIP aportado'
    if loc.startswith('shapefile1955/') and name.lower()=='1955pba.shp':return '1955','Año declarado por carpeta y nombre preexistentes; procedencia externa pendiente'
    if evidence.startswith('2022 según visor'):return '2022','Año indicado en visor oficial; descarga actual'
    return 'sin_fecha_verificada',evidence or 'No se encontró evidencia suficiente para asignar año'
def family(r):
    t=r.get('tipo','').lower()
    if 'radio censal' in t:return 'radios_censales'
    if 'fracci' in t:return 'fracciones_censales'
    if 'depart' in t:return 'departamentos'
    if 'manzana' in t:return 'manzanas_auxiliares'
    if 'eje de calle' in t:return 'ejes_calles_auxiliares'
    if any(x in t for x in ['municip','gobierno','comuna']):return 'municipios_gobiernos_locales'
    if 'circuitos_busqueda' in r['_base']:return 'circuitos_y_auxiliares'
    return 'otros'
rows=[];signatures=collections.defaultdict(list)
for base,r in entries:
    try:
        r['_base']=str(base);year,why=year_of(r);kind=family(r)
        names,read,member=access(base,r['archivo']);stem=member[:-4]
        files=[]
        for n in names:
            if not n.lower().startswith(stem.lower()):continue
            tail=n[len(stem):].lower()
            if tail not in EXTS:continue
            data=read(n);files.append((PurePosixPath(n).name,data,hashlib.sha256(data).hexdigest()))
        for handle in archive_handles:
            if hasattr(handle,'close'):handle.close()
        archive_handles.clear()
        if not any(n.lower().endswith('.shp') for n,_,_ in files):raise ValueError('No se encontró componente SHP')
        ident=hashlib.sha256((str(base.resolve())+'!'+r['archivo']).encode()).hexdigest()[:10]
        folder=OUT/year/kind/(slug(PurePosixPath(member).stem,32)+'_'+ident)
        folder.mkdir(parents=True,exist_ok=True)
        components=[]
        for name,data,h in files:
            dest=folder/name
            if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest()!=h:dest.write_bytes(data)
            if hashlib.sha256(dest.read_bytes()).hexdigest()!=h:raise ValueError('Copia no coincide: '+name)
            components.append(dict(archivo=name,bytes=len(data),sha256=h))
        shp=next(folder/n for n,_,_ in files if n.lower().endswith('.shp'))
        reader=shapefile.Reader(str(shp),encoding='latin1')
        signature=hashlib.sha256(json.dumps(sorted((n[len(PurePosixPath(member).stem):].lower(),h) for n,_,h in files),ensure_ascii=False).encode()).hexdigest()
        missing=[ext for ext in ['.shx','.dbf','.prj'] if not any(n.lower().endswith(ext) for n,_,_ in files)]
        out=dict(anio_carpeta=year,criterio_anio=why,tipo=kind,carpeta=folder.relative_to(OUT).as_posix(),shp=shp.name,entidades=len(reader),shape_type=reader.shapeType,componentes=components,faltan_componentes=missing,origen_absoluto=str(base.resolve())+'/'+r['archivo'],metadata_original={k:v for k,v in r.items() if k!='_base'},firma_componentes=signature)
        reader.close()
        (folder/'FUENTE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
        text=['# '+shp.stem,'',f'Año de clasificación: **{year}**. {why}.','',f'Entidades: {out["entidades"]}. Tipo SHP: {out["shape_type"]}.','',f'Original: `{out["origen_absoluto"]}`.','',f'Fuente: {r.get("fuente","")}',f'Notas originales: {r.get("nota","")}',f'Componentes ausentes: {", ".join(missing) or "ninguno de SHX/DBF/PRJ"}.','', 'Los archivos son copias de bytes de la fuente. No se asignó un CRS faltante, no se repararon geometrías ni se alteraron atributos. Ver FUENTE.json para hashes y metadatos completos.']
        (folder/'LEEME.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
        rows.append(out);signatures[signature].append(out['carpeta'])
    except Exception as e:errors.append(dict(origen=str(base)+'/'+r['archivo'],error=str(e)))
for z in archive_handles:
    if hasattr(z,'close'):z.close()
(OUT/'catalogo.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'errores.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'duplicados_exactos.json').write_text(json.dumps([v for v in signatures.values() if len(v)>1],ensure_ascii=False,indent=2),encoding='utf-8')
counts=collections.Counter(r['anio_carpeta'] for r in rows)
lines=['# Shapefiles por año y capa','','Cada carpeta de capa contiene **un solo SHP** con sus componentes originales, `LEEME.md` y `FUENTE.json`. Se incluyeron las dos recolecciones y los SHP preexistentes de `geometria/`; no se alteraron las fuentes. Los otros formatos siguen en las carpetas originales.','',f'{len(rows)} carpetas de capa; {len(signatures)} conjuntos de componentes distintos. Se conservan copias de fuentes distintas para no borrar su procedencia. No equivalen a {len(rows)} límites o años independientes.','', 'Los años de snapshot se señalan como copias de época, sin afirmar vigencia. `sin_fecha_verificada` reúne los archivos que no permiten asignar año. El año 1955 se infiere solo del nombre local y se señala esa limitación.','',f'Incidencias de extracción/lectura: {len(errors)}. Ver `errores.json`. La lectura estructural y los hashes no validan la exactitud geográfica o topológica.','','| Año o período | Carpetas |','|---|---:|']
for year,count in sorted(counts.items()):lines.append(f'| [{year}]({quote(year)}/) | {count} |')
lines+=['','| Año | Tipo | Capa | Entidades | Faltantes |','|---|---|---|---:|---|']
for r in sorted(rows,key=lambda x:(x['anio_carpeta'],x['tipo'],x['carpeta'])):lines.append(f'| {r["anio_carpeta"]} | {r["tipo"]} | [{r["shp"]}]({quote(r["carpeta"]+"/LEEME.md")}) | {r["entidades"]} | {", ".join(r["faltan_componentes"])} |')
(OUT/'LEEME.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('CARPETAS',len(rows),'DISTINTOS',len(signatures),'ERRORES',errors,'ANIOS',dict(sorted(counts.items())),flush=True)
