"""Serie nacional anual: cortes documentados y composiciones aproximadas separadas.
No deduce vigencia legal de un commit ni repara/disuelve los originales.
"""
from pathlib import Path
import sys,json,csv,io,zipfile,re,hashlib,collections,unicodedata,warnings
ROOT=Path(__file__).resolve().parent;SRC=ROOT.parent/'circuitos_busqueda'
sys.path.insert(0,str(SRC/'_deps'))
import shapefile
from pyproj import CRS,Transformer
from shapely.geometry import shape,mapping,Polygon,MultiPolygon,GeometryCollection
from shapely.ops import transform
from shapely import wkt,normalize,to_wkb
from shapely.geometry.polygon import orient
warnings.filterwarnings('ignore',category=DeprecationWarning)
NAMES=['CABA','Buenos Aires','Catamarca','Córdoba','Corrientes','Chaco','Chubut','Entre Ríos','Formosa','Jujuy','La Pampa','La Rioja','Mendoza','Misiones','Neuquén','Río Negro','Salta','San Juan','San Luis','Santa Cruz','Santa Fe','Santiago del Estero','Tucumán','Tierra del Fuego']
FILES=['CABA','PBA','Catamarca','Cordoba','Corrientes','Chaco','Chubut','EntreRios','Formosa','Jujuy','LaPampa','LaRioja','Mendoza','Misiones','Neuquen','RioNegro','Salta','SanJuan','SanLuis','SantaCruz','SantaFe','Santiago','Tucuman','TdF']
MANIFEST={r['archivo']:r for r in json.loads((SRC/'metadatos/descargas.json').read_text(encoding='utf-8'))}
sources=[];cache={};issues=[];UPDATES=[];SHP_CACHE={};JSON_GEOMETRY_CACHE={}
def register(ident,file,district,year,end=None,documented=False,scope='distrito',schema='galeano',crs=None,quality='',temporal='',note='',member=None):
    entry=dict(id=ident,archivo=file,distrito=f'{district:02}',desde=year,hasta=end or year,documentada=documented,alcance=scope,esquema=schema,crs=crs,calidad=quality,temporalidad=temporal,nota=note)
    if member:entry['miembro']=member
    entry['fuente_original']=MANIFEST.get(file,{})
    sources.append(entry);return entry
for year in [2021,2025]:
    for code,file in enumerate(FILES,1):
        register(f'galeano_{year}_{code:02}',f'galeano/{year}/{file}.geojson',code,year,documented=True,quality='oficial_y_reconstruida_segun_autor',temporal='corte_declarado_por_autor',note='Año atribuido por Galeano; no certificación legal independiente. Incluye reconstrucciones y marcadores sin circuito. Códigos de departamento conservados en el sistema de la fuente.')
for code in range(1,25):
    register(f'cne_consulta2026_{code:02}',f'cne_sin_fecha/circuito_{code:02}.geojson',code,2026,schema='cne',quality='descarga_organismo_cobertura_no_certificada',temporal='consulta_2026_no_vigencia',note='Descargada en octubre de 2026. No se conoce fecha general de vigencia. Salta tiene cobertura diferente e inferior en cantidad a la reconstrucción de Galeano; no se presume completitud.')
    sources[-1]['prioridad']=5
    alternatives=sorted((SRC/'sige').glob(f'distrito_{code:02}.circuitos_electorales*.geojson'))
    if alternatives:
        s=register(f'sige_consulta2026_{code:02}',alternatives[0].relative_to(SRC).as_posix(),code,2026,schema='sige',quality='organismo_cobertura_no_certificada',temporal='consulta_2026_no_vigencia',note='Descarga pública del sigE CNE de octubre de 2026. Conserva códigos INDRA e INDEC por separado. El nombre de capa o fecha de consulta no certifican vigencia electoral. Tiene prioridad frente a la descarga del portal anterior cuando ambas comparten fecha de consulta.')
        s['prioridad']=0
for code in range(1,25):
    p=f'snapshot_20190308/data/circuitos/circuito_{code:02}/circuito_{code:02}.shp'
    if not (SRC/p).exists():continue
    register(f'copia2019_{code:02}',p,code,2019,scope='capital_cordoba' if code==4 else ('parcial_no_integrable' if code in [10,16,17,24] else 'distrito'),schema='cne_shp',quality='copia_historica_cobertura_no_certificada',temporal='copia_existente_2019_no_vigencia',crs='EPSG:4326',note='El commit acredita existencia en marzo de 2019, no vigencia. Las capas parciales de Jujuy, Río Negro, Salta y Tierra del Fuego se conservan como alternativas y no reemplazan distritos completos.')
for name,district,year,date_known in [('bsas_circuitos01',2,2001,True),('bsas_circuitos03',2,2003,True),('caba_circuitos',1,2003,False),('cba_circuitos',4,2003,False),('Ctes_Circuitos_region',5,2003,False),('er_circuitos95',8,1995,True),('er_circuitos99',8,1999,True),('santafe_circuitos',21,2003,False)]:
    register('usuario_'+name,f'aporte_usuario/circuitos/{name}.shp',district,year,schema='usuario',crs='EPSG:22193',quality='crs_inferido_sin_prj',temporal='corte_historico_readme' if date_known else 'confeccion_2003_no_vigencia',note='Original sin PRJ. Se asume Campo Inchauspe / Argentina 3 (EPSG:22193) por coincidencia de coordenadas con CABA GeoDa y la descripción de aquella fuente. Suposición no confirmada para cada provincia; únicamente aproximada. No se modifica el original.')
register('geoda_caba1999','geoda_caba_1999/buenosaires.zip',1,1999,documented=True,schema='geoda',crs='EPSG:22193',member='buenosaires/buenosaires.shp',quality='catalogo_historico',temporal='eleccion_1999_declarada',note='GeoDa declara Gauss Kruger Zone 3 (Inchauspe). Se usa el CRS Campo Inchauspe / Argentina 3 del registro PROJ. https://geodacenter.github.io/data-and-lab/buenos-aires_old/')
register('caba2015_nyu','nyu_caba_2015/nyu_2451_34197.zip',1,2015,documented=True,schema='caba2015',crs='EPSG:4326',member='ba_circuitos_electorales/ba_circuitos_electorales.shp',quality='catalogo_historico',temporal='corte_2015_catalogado',note='SHP WGS84 de NYU/UTexas; evita volver a reproyectar la copia oficial local.')
register('caba_historico_rotulo2006','sige/custom_distrito_01_4.geojson',1,2006,schema='caba_historico',quality='fecha_ambigua',temporal='rotulo_2006_no_vigencia',note='Capa denominada Circuitos 2006, descrita como anterior a reorganización de 2006. El año sirve solo como referencia aproximada; no prueba vigencia en 2006.')
register('cordoba_capital2011','cordoba/extraido_2011/Seccionales y circuitos electorales 2011/Seccionales_2011.shp',4,2011,documented=True,scope='capital_cordoba',schema='cordoba2011',crs='PRJ',quality='catalogo_local_historico',temporal='corte_2011_catalogado',note='Solo Capital. Código compuesto Seccional + Subsección; conservar campos originales.')
register('cordoba_capital2013_2017','cordoba/circuitos-electorales-de-la-ciudad-de-cordoba/03.csv',4,2013,end=2017,documented=True,scope='capital_cordoba',schema='cordoba_csv2013',quality='catalogo_local_historico',temporal='periodo_2013_2017_declarado',note='Periodo expresamente declarado por catálogo; el campo Name se conserva como código de origen. No es provincia completa.')
register('cordoba_capital2019','cordoba/circuitos-electorales-de-la-ciudad-de-cordoba/00.csv',4,2019,documented=True,scope='capital_cordoba',schema='cordoba_csv2019',quality='catalogo_local_historico',temporal='corte_2019_catalogado',note='Solo Capital. El código INDEC del departamento no se iguala automáticamente al código electoral; unidad Capital identificada por nombre y alcance del catálogo.')
BLOCKED={
    'galeano_2025_01':'CABA 2025: desplazamiento mediano de centroides de 497,84 m respecto de CNE actual; 2021 difiere 1,43 m. Se aísla como variante con posible problema de georreferenciación, sin corregir el original.',
    'galeano_2021_15':'Neuquén 2021: desplazamiento mediano de 232,98 m respecto de CNE actual; 2025 coincide (mediana 0 m). No interpretar ese desplazamiento como reforma de todos los circuitos.',
    'copia2019_15':'Neuquén copia 2019: desplazamiento mediano de 232,99 m respecto de CNE actual, en 155 códigos comunes. Variante aislada.',
    'cne_consulta2026_04':'CNE Córdoba actual: campo circuito nulo en los 640 registros. Se conserva como fuente geométrica alternativa, pero no reemplaza automáticamente la capa que sí tiene identificadores.'}
for s in sources:
    if s['id'] in BLOCKED:s.update(excluir_seleccion_automatica=True,alerta=BLOCKED[s['id']])
def simple(v,width=0):
    if v is None:return None
    if isinstance(v,float) and v.is_integer():v=int(v)
    s=str(v).strip().upper()
    return s.zfill(width) if s and re.fullmatch(r'\d+[A-Z]*',s) else (s or None)
def circuit_code(v):
    raw=str(v).strip().upper() if v is not None else ''
    # El propio campo declara código actual y anterior: 3396( ex3390).
    match=re.fullmatch(r'(\d+[A-Z]*)\s*\(\s*EX\s*([0-9A-Z]+)\s*\)',raw)
    if match:return simple(match[1],5),simple(match[2],5)
    return simple(v,5),None
def normal_text(v):return ''.join(c for c in unicodedata.normalize('NFKD',str(v or '')).upper() if not unicodedata.combining(c)).strip()
def coordinates(geom):
    if geom['type']=='GeometryCollection':
        for child in geom.get('geometries',[]):yield from coordinates(child)
        return
    def walk(value):
        if value and isinstance(value[0],(int,float)):yield value
        else:
            for child in value:yield from walk(child)
    yield from walk(geom.get('coordinates',[]))
def drop_degenerate(geom,removed):
    # GEOS y GDAL rechazan líneas de un punto y anillos de menos de cuatro: se retiran y se cuentan.
    t=geom['type'];c=geom.get('coordinates')
    if t=='GeometryCollection':
        kids=[k for k in (drop_degenerate(child,removed) for child in geom.get('geometries',[])) if k]
        return None if not kids else kids[0] if len(kids)==1 else dict(type=t,geometries=kids)
    if t=='LineString':
        if len(c)>=2:return geom
        removed.append('LineString de un punto');return None
    if t=='MultiLineString':
        lines=[l for l in c if len(l)>=2];removed.extend(['LineString de un punto']*(len(c)-len(lines)))
        return dict(type=t,coordinates=lines) if lines else None
    if t=='Polygon':
        if not c or len(c[0])<4:removed.append('Polígono con anillo exterior degenerado');return None
        rings=[c[0]]+[r for r in c[1:] if len(r)>=4];removed.extend(['Anillo interior degenerado']*(len(c)-len(rings)))
        return dict(type=t,coordinates=rings)
    if t=='MultiPolygon':
        polys=[drop_degenerate(dict(type='Polygon',coordinates=p),removed) for p in c];polys=[p['coordinates'] for p in polys if p]
        return dict(type=t,coordinates=polys) if polys else None
    return geom
def polygon_parts(geom):
    if geom['type']=='GeometryCollection':return [p for child in geom.get('geometries',[]) for p in polygon_parts(child)]
    if geom['type'] not in ('Polygon','MultiPolygon'):return []
    return polygons(shape(geom))
def features_for(s):
    if s['id'] in cache:return cache[s['id']]
    p=SRC/s['archivo'];schema=s['esquema'];pairs=[]
    if p.suffix=='.geojson':
        j=json.loads(p.read_text(encoding='utf-8'));pairs=[(f.get('properties') or {},f.get('geometry')) for f in j['features']]
    elif p.suffix=='.csv':
        with p.open(encoding='utf-8-sig',newline='') as stream:
            for r in csv.DictReader(stream):pairs.append(({k:v for k,v in r.items() if k!='WKT'},mapping(wkt.loads(r['WKT']))))
    else:
        if p.suffix=='.zip':
            with zipfile.ZipFile(p) as z:
                stem=s['miembro'][:-4];lookup={n.lower():n for n in z.namelist()}
                r=shapefile.Reader(shp=io.BytesIO(z.read(lookup[(stem+'.shp').lower()])),shx=io.BytesIO(z.read(lookup[(stem+'.shx').lower()])),dbf=io.BytesIO(z.read(lookup[(stem+'.dbf').lower()])),encoding='latin1')
        else:r=shapefile.Reader(str(p),encoding='latin1')
        pairs=[(rec.record.as_dict(),rec.shape.__geo_interface__) for rec in r.iterShapeRecords()];r.close()
    transformer=None
    if s['crs'] and s['crs']!='EPSG:4326':
        crs=p.with_suffix('.prj').read_text() if s['crs']=='PRJ' else s['crs']
        transformer=Transformer.from_crs(crs,'EPSG:4326',always_xy=True)
    out=[]
    for index,(props,geom) in enumerate(pairs):
        if not geom:issues.append(dict(fuente=s['id'],fila=index,error='Geometría nula; no integrada'));continue
        parse_error=None;cleaning=None
        try:g=shape(geom)
        except Exception as exc:
            g=None;parse_error=str(exc);removed=[];clean=drop_degenerate(geom,removed)
            try:g=shape(clean) if clean else None
            except Exception:g=None
            if g is not None:
                geom=clean;cleaning='Retirados de la fuente: '+'; '.join(f'{n} {k}' for k,n in collections.Counter(removed).items())+'. El original está en circuitos_busqueda.'
                issues.append(dict(fuente=s['id'],fila=index,error=parse_error,accion=cleaning))
            else:issues.append(dict(fuente=s['id'],fila=index,error=parse_error,accion='Se conserva geometría original en GeoJSON; SHP extrae solo componentes poligonales legibles'))
        if transformer:
            if g is None:raise ValueError('No puede reproyectarse geometría ilegible '+s['id'])
            g=transform(transformer.transform,g);geom=mapping(g)
        if g is not None and g.is_empty:issues.append(dict(fuente=s['id'],fila=index,error='Geometría vacía; no integrada'));continue
        xy=list(coordinates(geom))
        if not xy:issues.append(dict(fuente=s['id'],fila=index,error='Sin coordenadas; no integrada'));continue
        if any(not (-180<=v[0]<=180 and -90<=v[1]<=90) for v in xy):raise ValueError('Coordenadas fuera de CRS84 '+s['id'])
        if schema=='galeano':code=props.get('circuito');section=props.get('coddepto');section_name='Capital' if s['distrito']=='04' and simple(section,3)=='001' else None
        elif schema in ['cne','cne_shp','cordoba_csv2019','sige']:code=props.get('circuito');section=props.get('indra_d') if schema=='sige' else props.get('indec_d');section_name=props.get('departamen')
        elif schema=='usuario':code=props.get('CIRC');section=props.get('DEPTO');section_name=props.get('DEPARTAMEN')
        elif schema=='geoda':code=props.get('CIRC');section=props.get('CIRCUNS');section_name=props.get('CIRCUNSCRI')
        elif schema=='caba2015':code=props.get('circuito_n');section=props.get('comuna');section_name=None
        elif schema=='caba_historico':code=props.get('circuito');section=props.get('circuns');section_name=props.get('circuns0')
        elif schema=='cordoba2011':code=str(props.get('Seccionale','')).strip()+str(props.get('Subsecc','')).strip();section='001';section_name='Capital'
        elif schema=='normalizado':code=props.get('codigo_circuito');section=props.get('codigo_seccion');section_name=props.get('nombre_seccion')
        else:code=props.get('Name');section='001';section_name='Capital'
        capital=s['distrito']=='04' and (s['alcance']=='capital_cordoba' or normal_text(section_name)=='CAPITAL')
        code,former_code=circuit_code(code);section=simple(section,3)
        has_code=bool(code and re.fullmatch(r'\d+[A-Z]*',code) and code.strip('0'))
        data=dict(codigo_distrito=s['distrito'],distrito=NAMES[int(s['distrito'])-1],codigo_seccion_fuente=section,nombre_seccion=section_name,codigo_circuito=code,codigo_circuito_original=None if code is None else str(props.get('circuito',props.get('CIRC',props.get('Name',code)))),identificador_utilizable=has_code,unidad_parche='04-CAPITAL' if capital else None,id_fuente=s['id'],archivo_fuente=s['archivo'],indice_fuente=index,anio_fuente_desde=s['desde'],anio_fuente_hasta=s['hasta'],temporalidad_fuente=s['temporalidad'],calidad_geometria=s['calidad'],geometria_valida=g.is_valid if g is not None else False,error_lectura_geometria=parse_error,depuracion_geometria=cleaning,sistema_codigos=schema,nota_fuente=s['nota'],atributos_originales=props)
        data['codigo_anterior_declarado_en_fuente']=former_code
        out.append(dict(type='Feature',geometry=geom,properties=data))
    cache[s['id']]=out;return out
def distance(s,y):return max(s['desde']-y,0,y-s['hasta'])
def choose(candidates,y):
    return min(candidates,key=lambda s:(distance(s,y),s['desde']>y,not s['documentada'],s['calidad']=='crs_inferido_sin_prj',s.get('prioridad',10),s['id'])) if candidates else None
def augment(f,s,y,mode):
    p=dict(f['properties']);d=distance(s,y)
    use=('corte_o_periodo_declarado' if s['documentada'] else 'fecha_de_referencia_no_vigencia') if not d else ('retroproyeccion_desde_fuente_posterior' if s['desde']>y else 'arrastre_desde_fuente_anterior')
    p.update(anio_objetivo=y,version=mode,uso_temporal=use,distancia_anios=d,extrapolacion_temporal=bool(d),nota_version='Composición aproximada autorizada: no cartografía certificada del año.' if mode=='aproximada' else 'Corte temporal atribuido por fuente; revisar calidad geométrica y reconstrucciones del autor.')
    return dict(type='Feature',geometry=f['geometry'],properties=p)
def polygons(g):
    if g.geom_type=='Polygon':return [g]
    if g.geom_type in ('MultiPolygon','GeometryCollection'):return [p for sub in g.geoms for p in polygons(sub)]
    return []
def export(folder,features,y,mode,coverage):
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/'circuitos_argentina.geojson'
    with path.open('w',encoding='utf-8') as stream:
        stream.write('{"type":"FeatureCollection","name":'+json.dumps(f'Argentina {y} - {mode}')+',"features":[')
        for index,f in enumerate(features):
            if index:stream.write(',')
            key=(f['properties']['id_fuente'],f['properties']['indice_fuente'])
            if key not in JSON_GEOMETRY_CACHE:JSON_GEOMETRY_CACHE[key]=json.dumps(f['geometry'],ensure_ascii=False,separators=(',',':'),allow_nan=False)
            stream.write('{"type":"Feature","geometry":'+JSON_GEOMETRY_CACHE[key]+',"properties":')
            json.dump(f['properties'],stream,ensure_ascii=False,separators=(',',':'),default=str,allow_nan=False);stream.write('}')
        stream.write(']}')
    sp=folder/'shp';sp.mkdir(exist_ok=True)
    w=shapefile.Writer(str(sp/'circuitos_argentina'),shapeType=shapefile.POLYGON,encoding='utf-8')
    for name,kind,size in [('dist','C',2),('seccion','C',12),('circuito','C',30),('anio_obj','N',4),('src_desde','N',4),('src_hasta','N',4),('fuente_id','C',70),('uso_temp','C',65),('calidad','C',65),('valid_geom','L',1),('src_fila','N',8)]:w.field(name,kind,size)
    omitted=[];reduced=[]
    for f in features:
        p=f['properties'];key=(p['id_fuente'],p['indice_fuente'])
        if key not in SHP_CACHE:
            parts=polygon_parts(f['geometry'])
            if parts:
                oriented=[orient(polygon,sign=-1.0) for polygon in parts]
                g=oriented[0] if len(oriented)==1 else MultiPolygon(oriented)
                SHP_CACHE[key]=shapefile.Shape._from_geojson(mapping(g))
            else:SHP_CACHE[key]=None
        if SHP_CACHE[key] is None:omitted.append(dict(fuente=p['id_fuente'],fila=p['indice_fuente'],motivo='Sin componente poligonal'));continue
        if f['geometry']['type']=='GeometryCollection':reduced.append(dict(fuente=p['id_fuente'],fila=p['indice_fuente'],accion='SHP contiene solo componentes poligonales; GeoJSON conserva colección original'))
        w.shape(SHP_CACHE[key]);w.record(p['codigo_distrito'],p['codigo_seccion_fuente'],p['codigo_circuito'],y,p['anio_fuente_desde'],p['anio_fuente_hasta'],p['id_fuente'],p['uso_temporal'],p['calidad_geometria'],p['geometria_valida'],p['indice_fuente'])
    w.close();(sp/'circuitos_argentina.prj').write_text(CRS(4326).to_wkt(version='WKT1_ESRI'),encoding='utf-8');(sp/'circuitos_argentina.cpg').write_text('UTF-8')
    info=dict(anio=y,version=mode,entidades_geojson=len(features),registros_shp=len(features)-len(omitted),omitidos_shp=omitted,colecciones_solo_poligonos_en_shp=reduced,distritos_con_alguna_geometria=len(set(f['properties']['codigo_distrito'] for f in features)),circuitos_con_codigo_distintos=len(set((f['properties']['id_fuente'],f['properties']['codigo_seccion_fuente'],f['properties']['codigo_circuito']) for f in features if f['properties']['identificador_utilizable'])),sin_codigo_utilizable=sum(not f['properties']['identificador_utilizable'] for f in features),geometrias_invalidas_sin_reparar=sum(not f['properties']['geometria_valida'] for f in features),usos_temporales=dict(collections.Counter(f['properties']['uso_temporal'] for f in features)),calidades=dict(collections.Counter(f['properties']['calidad_geometria'] for f in features)),cobertura_por_distrito=coverage,sha256_geojson=hashlib.sha256(path.read_bytes()).hexdigest())
    (folder/'NOTAS.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    text=f'# Argentina {y}: {mode}\n\n'+('Composición aproximada: incluye fuentes de otros años y supuestos de CRS señalados por registro. No atribuir vigencia legal al conjunto.\n' if mode=='aproximada' else 'Solo cortes o períodos atribuidos explícitamente por las fuentes, sin arrastre temporal. «Documentada» no equivale a oficial ni a validada geométricamente.\n')
    text+=f'\n{len(features)} entidades GeoJSON; {info["registros_shp"]} registros poligonales SHP. {info["distritos_con_alguna_geometria"]} distritos con alguna geometría; no implica cobertura total. Ver NOTAS.json para cobertura y limitaciones.\n\nCRS84/EPSG:4326. El GeoJSON conserva los atributos originales y notas completas. El SHP tiene campos breves y un subconjunto de columnas; FUENTE/NOTAS del directorio son parte del conjunto. No se repararon ni disolvieron geometrías; solo se retiraron componentes degenerados (líneas de un punto) que GDAL no puede leer, anotados en depuracion_geometria. Los marcadores sin código se conservan y se identifican.\n\nCampos clave: id_fuente, codigo_distrito, codigo_seccion_fuente, codigo_circuito, anio_fuente_desde/hasta, uso_temporal, calidad_geometria, sistema_codigos. Códigos de sección de fuentes distintas no son intercambiables sin tabla de equivalencias. «Mismo código» no garantiza misma geografía entre años.\n'
    (folder/'LEEME.md').write_text(text,encoding='utf-8')
    return info
def annual(y,mode):
    fs=[];coverage=[]
    for code in range(1,25):
        d=f'{code:02}';candidates=[s for s in sources if s['distrito']==d and s['alcance']=='distrito' and not s.get('excluir_seleccion_automatica')]
        if mode=='documentada':candidates=[s for s in candidates if s['documentada'] and not distance(s,y)]
        selected=choose(candidates,y);local=[];featurelist=features_for(selected) if selected else []
        if code==4:
            patches=[s for s in sources if s['alcance']=='capital_cordoba']
            if mode=='documentada':patches=[s for s in patches if s['documentada'] and not distance(s,y)]
            patch=choose(patches,y)
            if patch and (selected is None or distance(patch,y)<distance(selected,y) or (distance(patch,y)==0 and (patch['documentada'] and not selected['documentada']))):
                kept=[f for f in featurelist if f['properties']['unidad_parche']!='04-CAPITAL'];removed=len(featurelist)-len(kept)
                if not featurelist or removed:
                    featurelist=kept;local=[augment(f,patch,y,mode) for f in features_for(patch)]
                    local_note=dict(id_fuente=patch['id'],sustituidos_capital=removed,agregados=len(local))
                else:local_note=dict(id_fuente=patch['id'],no_aplicado='No se pudo identificar Capital en la base; no superponer silenciosamente')
            else:local_note=None
        else:local_note=None
        data=[augment(f,selected,y,mode) for f in featurelist] if selected else []
        data.extend(local)
        data,update_log=apply_updates(data,d,y,mode)
        fs.extend(data)
        coverage.append(dict(distrito=d,nombre=NAMES[code-1],fuente_distrital=selected['id'] if selected else None,fuentes_aisladas=[dict(id=s['id'],alerta=s['alerta']) for s in sources if s['distrito']==d and s.get('excluir_seleccion_automatica')],parche_capital=local_note,actualizaciones=update_log,entidades=len(data),estado='fuente_distrital_no_completitud_certificada' if selected else ('solo_cobertura_local' if data else 'pendiente')))
    return export(ROOT/'por_anio'/str(y)/mode,fs,y,mode,coverage)
def apply_updates(data,d,y,mode):
    log=[]
    for u in UPDATES:
        if str(u['distrito']).zfill(2)!=d or not u['desde']<=y<=u['hasta'] or mode not in u['versiones']:continue
        s=next(s for s in sources if s['id']==u['id_fuente'])
        if mode=='documentada' and (not s['documentada'] or distance(s,y)):
            raise ValueError('La actualización documentada requiere corte/período explícito: '+u['id'])
        selector=u['selector']
        def selected_feature(f):
            p=f['properties']
            return p['sistema_codigos'] in selector['sistemas_codigos'] and p['codigo_seccion_fuente'] in selector['secciones'] and (not selector.get('circuitos') or p['codigo_circuito'] in selector['circuitos'])
        removed=[f for f in data if selected_feature(f)]
        if len(removed)!=u['esperados_retirados'][mode]:
            raise ValueError(f"{u['id']}: retiro esperado {u['esperados_retirados'][mode]}, observado {len(removed)}; revisar esquema/cobertura")
        new=[augment(f,s,y,mode) for f in features_for(s)]
        if any(f['properties']['codigo_distrito']!=d for f in new):raise ValueError('Fuente de otro distrito en actualización '+u['id'])
        for f in new:f['properties'].update(actualizacion_id=u['id'],evidencia_actualizacion=u['evidencia_url'],nota_actualizacion=u['nota'])
        data=[f for f in data if not selected_feature(f)]+new
        log.append(dict(id=u['id'],retirados=len(removed),agregados=len(new),fuente=s['id'],evidencia_url=u['evidencia_url'],nota=u['nota']))
    return data,log
def load_config():
    global UPDATES
    extra=ROOT/'fuentes_adicionales.json';config=ROOT/'actualizaciones.json'
    if not extra.exists():extra.write_text('[]\n',encoding='utf-8')
    if not config.exists():config.write_text('[]\n',encoding='utf-8')
    for s in json.loads(extra.read_text(encoding='utf-8')):
        if s['esquema']!='normalizado':raise ValueError('Las fuentes adicionales deben usar esquema normalizado')
        if any(x['id']==s['id'] for x in sources):raise ValueError('ID de fuente repetido '+s['id'])
        for field in ['archivo','distrito','desde','hasta','documentada','alcance','crs','calidad','temporalidad','nota']:
            if field not in s:raise ValueError('Falta campo '+field)
        if not (SRC/s['archivo']).exists():raise ValueError('No existe fuente '+s['archivo'])
        sources.append(s)
    UPDATES=json.loads(config.read_text(encoding='utf-8'))
    for u in UPDATES:
        for field in ['id','distrito','desde','hasta','versiones','id_fuente','selector','esperados_retirados','evidencia_url','nota']:
            if field not in u:raise ValueError('Falta campo en actualización: '+field)
        if not u['evidencia_url'] or not u['nota']:raise ValueError('Actualización sin evidencia/nota')
        if not any(s['id']==u['id_fuente'] for s in sources):raise ValueError('Fuente de actualización desconocida')
        if not u['selector']['sistemas_codigos'] or not u['selector']['secciones']:raise ValueError('Selector de reemplazo vacío')
def comparison():
    groups={}
    for year in [2021,2025]:
        groups[year]=collections.defaultdict(list)
        for s in sources:
            if not s['id'].startswith(f'galeano_{year}_'):continue
            for f in features_for(s):
                p=f['properties']
                if not p['identificador_utilizable']:continue
                groups[year][(p['codigo_distrito'],p['codigo_seccion_fuente'],p['codigo_circuito'])].append(f['geometry'])
    def digest(geometries):
        def data(g):
            try:return b'GEOS:'+to_wkb(normalize(shape(g)))
            except Exception:return b'JSON:'+json.dumps(g,sort_keys=True,separators=(',',':')).encode()
        return hashlib.sha256(b''.join(sorted(data(g) for g in geometries))).hexdigest()
    hashes={y:{k:digest(g) for k,g in groups[y].items()} for y in groups}
    rows=[]
    for key in sorted(set(hashes[2021])|set(hashes[2025]),key=str):
        a=hashes[2021].get(key);b=hashes[2025].get(key)
        rows.append(dict(distrito=key[0],seccion_fuente=key[1],circuito=key[2],estado='igual_geometria_codificada' if a==b else ('diferencia_geometrica_en_misma_clave' if a and b else ('solo_2021' if a else 'solo_2025')),hash_2021=a,hash_2025=b))
    # Un vínculo geométrico exacto es candidato de renumeración, no equivalencia electoral certificada.
    old=collections.defaultdict(list);new=collections.defaultdict(list)
    for key,h in hashes[2021].items():old[(key[0],h)].append(key)
    for key,h in hashes[2025].items():new[(key[0],h)].append(key)
    matches=[dict(distrito=k[0],claves_2021=a,claves_2025=new[k],tipo='coincidencia_geometrica_exacta_sin_certificar_equivalencia') for k,a in old.items() if k in new and a!=new[k]]
    dest=ROOT/'cambios';dest.mkdir(exist_ok=True)
    (dest/'comparacion_2021_2025.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'candidatos_renumeracion.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2),encoding='utf-8')
    summary=[dict(distrito=f'{d:02}',nombre=NAMES[d-1],estados=dict(collections.Counter(r['estado'] for r in rows if r['distrito']==f'{d:02}'))) for d in range(1,25)]
    (dest/'resumen_distrital.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary
def main():
    ROOT.mkdir(exist_ok=True)
    load_config()
    summaries=[]
    requested=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--solo-anios=')),None)
    selected_years=set(map(int,requested.split(','))) if requested else None
    for year in range(2003,2027):
        for mode in ['documentada','aproximada']:
            note=ROOT/'por_anio'/str(year)/mode/'NOTAS.json'
            if (('--reanudar' in sys.argv) or (selected_years is not None and year not in selected_years)) and note.exists():
                result=json.loads(note.read_text(encoding='utf-8'));p=note.parent/'circuitos_argentina.geojson'
                if hashlib.sha256(p.read_bytes()).hexdigest()!=result['sha256_geojson']:raise ValueError('Salida previa incompleta '+str(p))
            else:result=annual(year,mode)
            summaries.append(result)
            print(year,mode,result['entidades_geojson'],result['distritos_con_alguna_geometria'],flush=True)
    changes=comparison()
    (ROOT/'fuentes_integrables.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'resumen_anual.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'incidencias_ingesta.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
    chosen_files=set(s['archivo'] for s in sources)
    inventory=json.loads((SRC/'metadatos/inventario_capas.json').read_text(encoding='utf-8'))
    review=[dict(archivo=r['archivo'],formato=r['formato'],decision='registrado_para_serie' if r['archivo'].split('!')[0] in chosen_files else 'alternativa_no_seleccionada',nota='No se mezclan variantes de fuente sin alcance y fecha controlados. Propuestas, puntos y capas auxiliares no reemplazan circuitos aprobados.') for r in inventory]
    (ROOT/'revision_inventario.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
    print('FUENTES',len(sources),'INCIDENCIAS',len(issues),'VERSIONES',len(summaries),flush=True)
if __name__=='__main__':main()
