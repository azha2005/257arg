"""1951 por circunscripción. SVG→contorno SHP, como 1904; sin repartir votos."""
from pathlib import Path
from collections import Counter, defaultdict
import copy, csv, hashlib, html, json, math, pickle, re, sys
import xml.etree.ElementTree as ET
import shapely
from shapely.ops import unary_union
from svgelements import SVG, Path as SVGPath
from lxml import html as lh
from geometria_1951 import build, d_path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SRC=ROOT/'datos/circunscripciones1951_1954'
sys.path.insert(0,str(ROOT/'comun'))
import wikitop
def dump(name,value):
    (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,default=lambda v:v.item()),encoding='utf8')
source=SRC/'circunscripciones_1951.svg'
tree=ET.parse(source).getroot()
L='{http://www.inkscape.org/namespaces/inkscape}label'
parsed=SVG.parse(str(source),parse_display_none=True)
paths={p.id:p for p in parsed.elements() if isinstance(p,SVGPath)}
layer=next(e for e in tree if e.get('id')=='layer2')
units=[]
# La caché de departamentos puede regenerarse desde su constructor propietario.
raw_cache=ROOT/'mapas/mapa1948/units_raw.pkl'
if not raw_cache.exists():
    sys.path.insert(0,str(ROOT/'transcripciones/peronismo'))
    import geom4673
    raw_cache.write_bytes(pickle.dumps(geom4673.load('1948')))
def add(element,p,number=1,kind='circunscripción',ids=None):
    if ids is None: ids=[e.get('id') for e in element.iter() if e.get('id') in paths]
    if p=='Buenos Aires':ids=[i for i in ids if paths[i].bbox()[1]<2100]
    if p=='Capital Federal':ids=[i for i in ids if paths[i].bbox()[1]<2000]
    assert ids,(p,number)
    units.append(dict(n=f'Circunscripción {number}.ª' if kind=='circunscripción' else p,p=p,k=kind,key=(p,number),ids=ids))
territories={'Río Negro','Formosa','Misiones'}
single={'Chubut','Santa Cruz','Neuquén'}
for e in layer:
    p=e.get(L)
    p='Buenos Aires' if p=='Provincia de Buenos Aires' else p
    if p in ('La Pampa','Chaco'):
        add(e,p,kind='provincia sin elección nacional');continue
    if p in single:
        # Los tres distritos y la Gobernación Militar son unidades indivisas:
        # su contorno se toma del SHP 1947, que conserva las divisiones de época.
        add(e,p,kind='territorio nacional');continue
    if p.startswith('Tierra del Fuego'):
        add(e,'Tierra del Fuego',kind='territorio nacional',ids=['path4686-2','path4688']);continue
    for c in e:
        label=c.get(L,'')
        m=re.fullmatch(r'Circunscripción (\d+)ª',label)
        if m:add(c,p,int(m[1]))
# Un contorno SHP propio para la Gobernación, no votos de Chubut o Santa Cruz.
add(next(e for e in layer if e.get(L)=='Chubut'),'Comodoro Rivadavia',kind='territorio nacional')
assert len(units)==152,len(units)
cache_key=hashlib.sha256(source.read_bytes()+(HERE/'geometria_1951.py').read_bytes()+(ROOT/'mapas/mapa1948/units_raw.pkl').read_bytes()+repr(units).encode()).hexdigest()
cache=HERE/'geometria_adaptada.pkl'
saved=pickle.loads(cache.read_bytes()) if cache.exists() else {}
if saved.get('key')==cache_key: geometries,audit,provinces=saved['data']
else:
    geometries,audit,provinces=build(units,paths,ROOT)
    cache.write_bytes(pickle.dumps(dict(key=cache_key,data=(geometries,audit,provinces))))
dump('CONTROL_GEOMETRIA.json',audit)
data=json.loads((SRC/'resultados1951.json').read_text(encoding='utf8'))
results={(r['provincia'],r['numero']):r for r in data}
assert len(results)==150
assert set(results)=={u['key']for u in units if u['p'] not in ('Chaco','La Pampa')}
reference=json.loads((ROOT/'mapas/mapa1954/dataset_1954.json').read_text(encoding='utf8'))
candidates={c:copy.deepcopy(reference['candidates'][c]) for c in ('PP','UCR','PS','PD','PDP','PC','CO')}
candidates.update(UCN=dict(n='Unión Cívica Nacionalista',base='#008577'),OTR=dict(n='Partidos varios',base='#777777'))
def n(v):return f'{v:,}'.replace(',','.')
def record(r):
    metrics=r['metricas']; pos=metrics['Votos positivos']; votes=Counter()
    lines=[]
    for j,c in enumerate(r['candidatos']):
        votes[c['codigo']]+=c['votos']
        code=f"{r['provincia']}_{r['numero']}_{j}"
        candidates[code]=dict(n=c['partido']+(' · '+c['nombre'] if c['nombre'] and c['nombre']!='Sin datos' else ''),base=candidates[c['codigo']]['base'],minor=True)
        lines.append([code,c['votos'],100*c['votos']/pos])
    winner=max(r['candidatos'],key=lambda c:c['votos'])
    note=('Diputado nacional' if r['cargo']=='diputado' else 'Delegado territorial')+'. Votos por circunscripción, sin reparto departamental. '
    delta=pos-sum(votes.values())
    if delta:note+=f'La suma de candidaturas difiere de los positivos declarados en {n(delta)} votos; se conservan ambas cifras. '
    if metrics.get('Diferencia de votos'):note+=f"Diferencia de votos declarada por la fuente: {n(metrics['Diferencia de votos'])}. "
    # Candidatos y padrón observados; la diferencia no se atribuye a ningún partido.
    return dict(w=winner['codigo'],q=100*winner['votos']/pos,lines=lines,
                metrics=[[{'Registrados/participación':'Inscriptos'}.get(k,k),n(v)]for k,v in metrics.items()]+[['Participación',f"{100*metrics['Total de votos']/metrics['Registrados/participación']:.2f} %".replace('.',',')]],note=note)
records=[record(results[u['key']]) if u['key'] in results else dict(fill='#cfcfcf',lines=[],note='Sin elección nacional de diputados el 11 de noviembre de 1951. Las elecciones provinciales/constituyentes y las parciales posteriores no se incorporan.') for u in units]
minorities=[]
for province_element in layer:
    p=province_element.get(L)
    if p=='Provincia de Buenos Aires':p='Buenos Aires'
    for element in province_element:
        m=re.fullmatch(r'Circunscripción (\d+)ª \(Minoría\)',element.get(L,''))
        if not m:continue
        number=int(m[1]);r=results[p,number]
        ranked=sorted(r['candidatos'],key=lambda c:c['votos'],reverse=True)
        # El SVG identifica la banca adicional. El candidato no ganador se
        # obtiene de la misma tabla, sin tratar el punto como otra votación.
        c=ranked[1];i=next(i for i,u in enumerate(units)if u['key']==(p,number))
        info=dict(provincia=p,numero=number,indice=i,**c)
        minorities.append(info)
        records[i]['note']+=f" Banca de minoría (punto del SVG): {c['nombre']} ({c['partido']}), {n(c['votos'])} votos. Banca adicional, no una elección separada; estos votos ya están incluidos en la circunscripción."
assert len(minorities)==10 and Counter(c['codigo']for c in minorities)=={'UCR':8,'PP':2}
dump('bancas_minoria_1951.json',minorities)
cands,slices,partp,metrics=wikitop.national('1951')
national=dict(cands=cands,slices=slices,partp=partp,metrics=metrics)
note=('Votos y padrón por circunscripción: tabla de Wikipedia, con fuente en Confirmación electoral de la voluntad justicialista del pueblo argentino, elecciones del 11 de noviembre de 1951. '
      'El PDF aportado corresponde a 1951, no a 1954. Torta y barras nacionales: tabla nacional de Wikipedia, sin ajustarla a las sumas locales. '
      'Incluye 139 circunscripciones de diputados y 11 de delegados territoriales. Los diez puntos del SVG son bancas de minoría (8 UCR y 2 PP), no elecciones separadas: se muestran sin duplicar votos ni circunscripciones. Excluye las elecciones provinciales y las parciales posteriores. '
      'PP incluye Partido Peronista Femenino; UCR incluye Unionistas. Ganó usa la candidatura individual más votada. '
      'Diferencias conservadas: Santa Fe 4.ª suma 79.140 votos a candidatos frente a 79.160 positivos; PS suma 74.370 frente a 73.927 nacionales y PC 70.681 frente a 71.124 nacionales. '
      'SVG de Faustino Sojo (Commons, CC BY-SA 4.0), cotejado con las láminas del PDF. Adaptación aproximada al contorno SHP histórico 1947 y Buenos Aires 1955 de Rodríguez/CONICET (CC BY 2.5 AR), '
      'con el mismo método y proyección del atlas 1904: no es una certificación de límites ni una conversión de votos a departamentos. '
      'Capital conserva las 28 circunscripciones de 1951 del SVG, no las veinte del SHP ni las veintiocho de 1973. '
      'Chaco y La Pampa sin elección nacional en esta fecha, en gris. Malvinas del SHP del proyecto, en gris. '
      'Agradecemos a Faustino Sojo por el SVG y la recopilación de resultados. https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1951')
prov={};prov_stats={}
for p in provinces:
    rows=[r for r in data if r['provincia']==p]
    counts=Counter()
    for r in rows:
        for c in r['candidatos']:counts[c['codigo']]+=c['votos']
    pos=sum(r['metricas']['Votos positivos']for r in rows)
    prov_stats[p]=dict(pos=pos,votantes=sum(r['metricas']['Total de votos']for r in rows),electores=sum(r['metricas']['Registrados/participación']for r in rows),votos=counts)
    if pos:
        win=counts.most_common(1)[0][0]
        prov[p]=dict(w=win,q=100*counts[win]/pos,lines=[[c,v,100*v/pos]for c,v in counts.most_common()],note='Agregado de las circunscripciones publicadas; no incluye otra elección ni votos imputados.')
    else:prov[p]=dict(fill='#cfcfcf',lines=[],note='Sin elección nacional el 11 de noviembre de 1951.')
keys=[['#cfcfcf','Sin elección nacional en esta fecha']]
modes=[dict(id='gan',tile='GANÓ',units=records,prov=prov,national=national,note=note,legend=dict(keys=keys))]
for code in ('PP','UCR'):
    rs=copy.deepcopy(records);rgb=[int(candidates[code]['base'][k:k+2],16)for k in (1,3,5)]
    colors=['#'+''.join(f'{round(255+(v-255)*(.12+.88*j/9)):02x}'for v in rgb)for j in range(10)]
    for i,u in enumerate(units):
        if u['key'] not in results:continue
        r=results[u['key']];pct=100*sum(c['votos']for c in r['candidatos']if c['codigo']==code)/r['metricas']['Votos positivos']
        rs[i]['fill']=colors[min(9,int(pct/10))]
    provincial=copy.deepcopy(prov)
    for p,st in prov_stats.items():
        if st['pos']:
            pct=100*st['votos'][code]/st['pos']
            provincial[p]['fill']=colors[min(9,int(pct/10))]
            provincial[p]['metrics']=[['% '+code,f'{pct:.2f} %'.replace('.',',')]]
    modes.append(dict(id=code.lower(),tile='% '+code,units=rs,prov=provincial,national=national,note=note,legend=dict(title='% '+candidates[code]['n'],stops=[[col,str(j*10)+(' %'if j<9 else '+ %')]for j,col in enumerate(colors)],bars=False,keys=keys)))
rs=copy.deepcopy(records)
colors=['#f2e9f8','#dcc6ec','#c5a3df','#aa7dd0','#8b57bc','#6e359f','#501981']
for i,u in enumerate(units):
    if u['key'] in results:
        r=results[u['key']]['metricas'];pct=100*r['Total de votos']/r['Registrados/participación']
        rs[i]['fill']=colors[max(0,min(6,int((pct-40)/10)))]
provincial=copy.deepcopy(prov)
for p,st in prov_stats.items():
    if st['electores']:
        pct=100*st['votantes']/st['electores']
        provincial[p]['fill']=colors[max(0,min(6,int((pct-40)/10)))]
        provincial[p]['metrics']=[['Votantes',n(st['votantes'])],['Inscriptos',n(st['electores'])],['Participación',f'{pct:.2f} %'.replace('.',',')]]
modes.append(dict(id='par',tile='PART.',units=rs,prov=provincial,national=national,note=note,legend=dict(title='Participación sobre inscriptos',stops=[[c,str(40+j*10)+(' %'if j<6 else '+ %')]for j,c in enumerate(colors)],bars=False,keys=keys)))
insets=copy.deepcopy(reference['insets'])
for i in insets:
    i['win']=copy.deepcopy(next((q['win']for q in json.loads((ROOT/'mapas/mapa1904/dataset_1904.json').read_text(encoding='utf8'))['insets']if q['id']==({'gba':'amba'}.get(i['id'],i['id']))),i['win']))
    if i['id'] in ('gba','tuc','sj','mza','res'):i['show']=['d','dc','pb'];i['sd']=1.5
    if i['id']=='caba':
        g=provinces['Capital Federal'];x,y,X,Y=g.bounds;w,h=X-x,Y-y
        i['win']=[x-.025*w,y-.025*h,w*1.05,h*1.05];i['sd']=1.5
ds=dict(slug='diputados_1951_circunscripciones',locale='es-AR',country='Argentina',title='Elecciones legislativas de Argentina de',year='1951',exterior=False,labels=dict(pie1='Proporción sobre votos positivos'),candidates=candidates,sets={'1':dict(label='1951',subtitle='Circunscripciones')},modes=modes,insets=insets,solid=[],territories=[{k:u[k]for k in ('n','p','k')}for u in units])
dump('dataset_1951.json',ds)
body=[]
for i,(u,g) in enumerate(zip(units,geometries)):
    body.append(f'<path class="{"dc" if u["p"]=="Capital Federal" else "d"}" data-i="{i}" d="{d_path(g,4 if u["p"]=="Capital Federal" else 2)}"/>')
for p,g in provinces.items():body.append(f'<path class="pb" data-p="{html.escape(p)}" d="{d_path(g)}"/>')
for c in minorities:
    point=geometries[c['indice']].representative_point()
    cls='minor-caba'if c['provincia']=='Capital Federal'else 'minor-d'
    if c['provincia'] in ('Capital Federal','Buenos Aires'):cls+=' minor-metro'
    body.append(f'<circle class="minority {cls}" data-i="{c["indice"]}" data-minority="{c["codigo"]}" cx="{point.x:.4f}" cy="{point.y:.4f}" r="1.8" style="fill:{candidates[c["codigo"]]["base"]}"/>')
ref_html=(ROOT/'mapas/mapa1954/atlas_1954.html').read_text(encoding='utf8')
doc=lh.fromstring(ref_html)
# Conserva el recuadro antártico del proyecto, sin añadirle votos.
body.extend(lh.tostring(e,encoding='unicode',method='html')for e in doc.get_element_by_id('B') if e.get('class') in ('ant','antg','antf'))
old=lh.fromstring((ROOT/'mapas/mapa1904/atlas_1904.html').read_text(encoding='utf8'))
mal=next(e for e in old.get_element_by_id('B')if e.get('class')=='mal').get('d')
body.append(f'<path class="mal" style="display:inline;fill:#a9a9a9;stroke:#1b1b1b;stroke-width:1" d="{mal}"/>')
pv=[f'<path class="pf" data-prov="{html.escape(p)}" d="{d_path(g.simplify(.3))}"/>'for p,g in provinces.items()]
pv.append(f'<path class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round" d="{mal}"/>')
def replace_group(s,id,content):
    m=re.search(r'<g\b[^>]*\bid="'+id+r'"[^>]*>',s);assert m,id
    depth=1
    for end in re.finditer(r'<g\b[^>]*>|</g>',s[m.end():]):
        depth+=-1 if end[0]=='</g>' else 1
        if depth==0:return s[:m.end()]+content+s[m.end()+end.start():]
    raise ValueError(id)
out=replace_group(ref_html,'B',''.join(body))
out=replace_group(out,'pv',''.join(pv))
out=re.sub(r'const DATA=.*?;\n',lambda m:'const DATA='+json.dumps(ds,ensure_ascii=False,separators=(',',':'))+';\n',out,count=1)
out=re.sub(r'<title>.*?</title>','<title>Diputados nacionales 1951 · Circunscripciones</title>',out,count=1)
styles='.ant,.antg{fill:#a9a9a9!important}.minority{r:var(--dotr,1.8px);stroke:#111}.minority,.minority.sel{stroke-width:var(--dotstroke,.45px)}.minor-metro{r:var(--dotr-metro,1px)}.minor-d{display:var(--v-mind,none)}.minor-caba{display:var(--v-minc,none)}'
out=re.sub(r'(<svg\b[^>]*\bid="atlas"[^>]*>)',lambda m:m[1]+'<style>'+styles+'</style>',out,count=1)
out=out.replace('--v-d:inline;--v-pb:inline;--v-out:inline;','--v-d:inline;--v-dc:inline;--v-pb:inline;--v-out:inline;--v-mind:inline;--v-minc:inline;')
out=out.replace('function applyZoom(){','function applyZoom(){\n  const dotGrowth=Math.log2(Z.k);mw.style.setProperty("--dotr",(Math.min(3.6,1.8+.5*dotGrowth)/Z.k)+"px");mw.style.setProperty("--dotr-metro",(Math.min(3.2,1+.6*dotGrowth)/Z.k)+"px");mw.style.setProperty("--dotstroke",(.6/Z.k)+"px");',1)
out=out.replace('</head>','<style>.c-met{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 12px}.c-met>div{min-width:0;overflow-wrap:anywhere}.c-met b{overflow-wrap:anywhere}#card .c-row,#tip .c-row{grid-template-columns:minmax(0,1fr) 58px 70px;align-items:start;margin:5px 0;row-gap:3px}#card .c-row .nm,#tip .c-row .nm{display:block;min-width:0;white-space:normal;overflow:visible;text-overflow:clip;overflow-wrap:anywhere;line-height:1.35}#card .c-row .nm i,#tip .c-row .nm i{display:inline-block;margin-right:6px}</style></head>',1)
overlay='''
    for(const dot of document.querySelectorAll('#B circle[data-minority]')){
      if(dot.classList.contains('minor-caba')?!I.show.includes('dc'):!I.show.includes('d'))continue;
      const c=dot.cloneNode(false);c.style.display='inline';c.style.setProperty('--dotr',(2.5/sc)+'px');c.style.setProperty('--dotr-metro',(1.4/sc)+'px');c.style.setProperty('--dotstroke',(.45/sc)+'px');
      c.addEventListener('pointerup',ev=>{ev.stopPropagation();selectUnit(+c.dataset.i,false,{x:ev.clientX,y:ev.clientY});});
      s.appendChild(c);
    }
'''
out=out.replace('el("use",{href:"#B",style:st},s);','el("use",{href:"#B",style:st},s);'+overlay,1)
keyjs='''function drawMinorityKey(){
  const g=$('#legend'),b=g.getBBox(),y=b.y+b.height+22;
  el('circle',{cx:99,cy:y-4,r:3,fill:'#e10019',stroke:'#111','stroke-width':.65},g);
  el('circle',{cx:114,cy:y-4,r:3,fill:'#318ce7',stroke:'#111','stroke-width':.65},g);
  el('text',{x:128,y,'font-size':14,fill:'#616161'},g,'Puntos: bancas adicionales de minoría');
}
'''
out=out.replace('function setMode(m){',keyjs+'function setMode(m){',1).replace('drawLegend(N);drawTiles();','drawLegend(N);drawMinorityKey();drawTiles();',1)
(HERE/'atlas_1951.html').write_text(out,encoding='utf8',newline='\n')
totals=Counter()
for r in data:
    for c in r['candidatos']:totals[c['codigo']]+=c['votos']
seat_counts=Counter(r.get('w')for r in records if r.get('w'))+Counter(c['codigo']for c in minorities)
assert seat_counts=={'PP':146,'UCR':14}
dump('CONTROL_1951.json',dict(unidades=len(units),con_resultados=len(data),diputados=sum(r['cargo']=='diputado'for r in data),delegados=sum(r['cargo']=='delegado'for r in data),ganadores=dict(Counter(r.get('w')for r in records)),bancas_minoria=dict(Counter(c['codigo']for c in minorities)),bancas_y_delegados_totales=dict(seat_counts),votos_locales=dict(totals),positivos_locales=sum(r['metricas']['Votos positivos']for r in data),positivos_nacionales=wikitop.WIKI['1951']['positivos'],fuente_svg_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),metodo='SVG a contornos SHP históricos por método 1904; votos observados por circunscripción, sin reparto.'))
# Entrega GIS: la deformación ocurre en coordenadas de póster. Se invierte
# la proyección para entregar coordenadas geográficas WGS84, no píxeles.
import shapefile
from pyproj import CRS
from shapely.geometry.polygon import orient
gis=HERE/'shp';gis.mkdir(exist_ok=True)
def inverse(a):
    a=a.copy();a[:,0]=(a[:,0]-643)/(math.cos(math.radians(38))*44)-73.5708041
    a[:,1]=-21.7807776-(a[:,1]-150)/44
    return a
features=[]
with shapefile.Writer(str(gis/'circunscripciones_1951'),shapeType=shapefile.POLYGON,encoding='utf8') as writer:
    for name,typ,size in [('provincia','C',80),('circ','N',4),('unidad','C',80),('cargo','C',32),('ganador','C',8),('positivos','N',12),('electores','N',12),('metodo','C',60)]:writer.field(name,typ,size)
    for u,g in zip(units,geometries):
        geographic=shapely.transform(g,inverse)
        polys=[geographic]if geographic.geom_type=='Polygon'else list(geographic.geoms)
        parts=[]
        for polygon in polys:
            polygon=orient(polygon,sign=-1)
            parts.append(list(polygon.exterior.coords));parts.extend(list(r.coords)for r in polygon.interiors)
        writer.poly(parts)
        r=results.get(u['key']);positive=r['metricas']['Votos positivos']if r else None
        winner=max(r['candidatos'],key=lambda c:c['votos'])['codigo']if r else ''
        properties=dict(provincia=u['p'],circ=u['key'][1]if r else 0,unidad=u['n'],cargo=r['cargo']if r else 'sin elección nacional',ganador=winner,positivos=positive,electores=r['metricas']['Registrados/participación']if r else None,metodo='SVG adaptado a contorno SHP; aproximado')
        writer.record(*properties.values())
        features.append(dict(type='Feature',properties=properties,geometry=shapely.geometry.mapping(geographic)))
(gis/'circunscripciones_1951.prj').write_text(CRS.from_epsg(4326).to_wkt(version='WKT1_ESRI'),encoding='ascii')
(gis/'circunscripciones_1951.cpg').write_text('UTF-8',encoding='ascii')
(gis/'circunscripciones_1951.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False,separators=(',',':')),encoding='utf8')
# Referencia insular idéntica al atlas 1904; separada de las unidades con votos.
mal_raw=next(u['geom']for u in pickle.loads((ROOT/'mapas/mapa1912/units_raw.pkl').read_bytes())if u['name']=='Islas Malvinas')
with shapefile.Writer(str(gis/'malvinas_referencia'),shapeType=shapefile.POLYGON,encoding='utf8')as writer:
    writer.field('nombre','C',80)
    polygons=[mal_raw]if mal_raw.geom_type=='Polygon'else list(mal_raw.geoms)
    parts=[]
    for polygon in polygons:
        polygon=orient(polygon,sign=-1)
        parts.append(list(polygon.exterior.coords));parts.extend(list(r.coords)for r in polygon.interiors)
    writer.poly(parts);writer.record('Islas Malvinas · sin resultado electoral')
(gis/'malvinas_referencia.prj').write_text(CRS.from_epsg(4326).to_wkt(version='WKT1_ESRI'),encoding='ascii')
(gis/'malvinas_referencia.cpg').write_text('UTF-8',encoding='ascii')
with shapefile.Writer(str(gis/'bancas_minoria_1951'),shapeType=shapefile.POINT,encoding='utf8')as writer:
    for name,typ,size in [('provincia','C',80),('circ','N',4),('partido','C',8),('candidato','C',120),('votos','N',12),('nota','C',120)]:writer.field(name,typ,size)
    for c in minorities:
        point=shapely.transform(geometries[c['indice']].representative_point(),inverse)
        writer.point(point.x,point.y)
        writer.record(c['provincia'],c['numero'],c['codigo'],c['nombre'],c['votos'],'Banca adicional; votos ya incluidos en la circunscripción')
(gis/'bancas_minoria_1951.prj').write_text(CRS.from_epsg(4326).to_wkt(version='WKT1_ESRI'),encoding='ascii')
(gis/'bancas_minoria_1951.cpg').write_text('UTF-8',encoding='ascii')
with (HERE/'candidatos_1951.csv').open('w',encoding='utf-8-sig',newline='')as f:
    fieldnames=['provincia','numero','cargo','partido','codigo','nombre','votos','literal_votos','porcentaje_fuente']
    writer=csv.DictWriter(f,fieldnames=fieldnames);writer.writeheader()
    for r in data:
        for c in r['candidatos']:writer.writerow(dict(provincia=r['provincia'],numero=r['numero'],cargo=r['cargo'],**c))
print('1951:',len(units),'unidades;',len(data),'con resultados;',Counter(r.get('w')for r in records))
