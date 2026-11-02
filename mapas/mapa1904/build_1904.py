"""1904: circunscripciones uninominales del SVG aportado y tabla de Wikipedia.

python mapas/mapa1904/build_1904.py
Dependencias: pandas, lxml, svgelements. No requiere cartografía moderna.
"""
from pathlib import Path
from collections import Counter, defaultdict
import copy, csv, hashlib, html, io, json, re, sys, xml.etree.ElementTree as ET
import math
import pickle
import pandas as pd
from svgelements import SVG, Path as SVGPath
from geometria_1904 import build as adapt_geometry, d_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'comun'))
L = '{http://www.inkscape.org/namespaces/inkscape}label'
SOURCE = HERE / 'circunscripciones_1904.svg'
if not SOURCE.exists():
    SOURCE.write_bytes((Path.home() / 'Downloads' / 'Mapa_de_las_elecciones_legislativas_de_Argentina_de_1904_por_circunscripción.svg').read_bytes())

def clean(s):
    return re.sub(r'\[[^\]]*\]|\u200b', '', str(s)).strip()

def dump(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2,default=lambda v:v.item()), encoding='utf8')

table = pd.read_html(io.StringIO((HERE / 'wiki1904.html').read_text(encoding='utf8')), keep_default_na=False)[2]
groups = {}
for _, row in table.iterrows():
    province, circ, person, _, party, votes = map(clean, row)
    number = int(circ.split('.')[0])
    key = province, number
    value = None if votes == 'Sin datos' else int(votes.replace('.', ''))
    groups.setdefault(key, {'name': circ, 'rows': []})['rows'].append({'candidate': person, 'party': party, 'votes': value})
assert len(groups) == 60

def party_code(p):
    if not p or p == 'Otros': return 'OTR'
    if p.startswith('Unión Cívica Radical'): return 'UCR'
    if p.startswith('Unión Cívica Nacional'): return 'UCN'
    if p == 'Partido Provincial-Partidos Unidos' or p == 'Unión Popular': return 'DIS'
    if p == 'Partido Autonomista': return 'PA'
    if p == 'Partido Liberal': return 'PL'
    if p == 'Partido Republicano': return 'PR'
    if p == 'Partido Socialista': return 'PS'
    if p in ('Independiente', 'Otros'): return 'IND'
    if p.startswith('PAN') or p in ('Partido Autonomista Nacional', 'Partido Provincial', 'Partido Democrático', 'Partido Constitucional', 'Asociación Popular-Partidos Unidos'): return 'PAN'
    raise ValueError(p)

specs = [
    ('PAN', 'Autonomista Nacional', 'PAN y aliados', '#74acdf'),
    ('DIS', 'PAN disidente', 'Provincial BA · Unión Popular', '#30d5c8'),
    ('PA', 'Partido Autonomista', 'Autonomistas', '#0067a5'),
    ('PL', 'Partido Liberal', 'Corrientes', '#35aae0'),
    ('IND', 'Independientes', 'Candidaturas independientes', '#777777'),
    ('PR', 'Partido Republicano', 'Republicanos', '#4169e1'),
    ('UCN', 'Unión Cívica Nacional', 'UCN · Partidos Unidos', '#22b14c'),
    ('PS', 'Partido Socialista', 'Socialistas', '#ff9900'),
    ('UCR', 'Unión Cívica Radical', 'UCR · Partidos Unidos', '#e10019'),
]
CAND = {c: dict(n=n, sub=s, base=col, logo=c) for c,n,s,col in specs}
CAND['OTR'] = dict(n='Otros sin afiliación identificada',base='#999999')
# Pedido del usuario: mismos recursos de 1916alt; sin introducir el PDP en 1904.
old = json.loads((ROOT / 'mapas/mapa1916fic/dataset_1916fic.json').read_text(encoding='utf8'))['candidates']
for c, source in [('UCR', 'UCR'), ('PS', 'PS'), ('PAN', 'CC')]:
    for field in ('img', 'ar', 'bl'):
        if field in old[source]: CAND[c][field] = old[source][field]
seats = Counter(party_code(g['rows'][0]['party']) for g in groups.values())
assert sum(seats.values()) == 60
totals = Counter()
for g in groups.values():
    for r in g['rows']: totals[party_code(r['party'])] += r['votes'] or 0
positive = sum(totals.values())
national = dict(cands=[dict(code=c, votes=v, pct=100*v/positive) for c,v in totals.most_common() if seats[c]],
                slices=[dict(code=c,v=v) for c,v in totals.items() if v],
                metrics=[['Votos publicados',f'{positive:,}'.replace(',','.')],['Cobertura con votos', '59 de 60 circunscripciones'],['Bancas renovadas', '60 de 120']])
NATIONAL_NOTE = ('La torta y las barras suman los votos publicados por la afiliación partidaria más cercana, a pedido del usuario: cobertura 59 de 60 circunscripciones, sin total nacional completo. '
                 'Se conservan PAN disidente (Partido Provincial bonaerense y Unión Popular tucumana), autonomistas, liberales, republicanos, UCN, PS, UCR e independientes separados. '
                 'Partido Provincial de Salta y Tucumán, Democrático y Constitucional de San Juan y Asociación Popular se agrupan con PAN, siguiendo los enlaces partidarios y la clasificación del artículo. '
                 'La leyenda del artículo suma 53: se conserva esta discrepancia en el control. Ganó identifica al candidato más votado, sin sumar sus competidores del mismo partido. '
                 'Las fichas conservan los candidatos separados. Porcentajes sobre la suma de votos publicados; sin padrón, blancos ni participación inferidos. '
                 'Catamarca 2: diputado electo conocido, votos no publicados, mapa beige. Gris: sin elección; gris claro: territorios sin representación. '
                 'Solo elección general del 13 de marzo; se excluyen elecciones parciales de 1904 y 1905. '
                 'Cartografía: SVG de Commons aportado por el usuario, no límites departamentales modernos. Fuente: https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1904')

tree = ET.parse(SOURCE).getroot()
parsed = SVG.parse(str(SOURCE), parse_display_none=True)
paths = {p.id: p for p in parsed.elements() if isinstance(p, SVGPath)}
layer = next(x for x in tree if x.get('id') == 'layer2')
units = []
def add(element, name, province, kind, key=None, exclude=()):
    ids = [e.get('id') for e in element.iter() if e.get('id') in paths and not any(z in e.get('id','') for z in exclude)]
    # El original trae copias ampliadas de BA y CABA dentro de cada unidad.
    # Se conserva únicamente el trazo geográfico; nuestros recuadros usan ese mismo trazo.
    if province == 'Buenos Aires': ids=[i for i in ids if paths[i].bbox()[1]<2300]
    if province == 'Capital Federal': ids=[i for i in ids if paths[i].bbox()[2]<1650 and 1450<paths[i].bbox()[1]<1650]
    if ids: units.append(dict(n=name, p=province, k=kind, key=key, ids=ids))

for province in list(layer)[1:]:
    p = province.get(L)
    for element in province:
        label = element.get(L, '')
        m = re.match(r'(\d+) - (.+)', label)
        if m:
            add(element, m[2], p, 'circunscripción', (p, int(m[1])))
assert len(units) == 120, len(units)
others = list(layer)[0]
for territory in list(others)[1:]:
    p = territory.get(L)
    add(territory, p, 'Territorios nacionales', 'territorio nacional')
fuego = ET.Element('g')
for e in others.iter():
    if e.get('id') in ('g2051','g2057'): fuego.append(copy.deepcopy(e))
add(fuego, 'Tierra del Fuego', 'Territorios nacionales', 'territorio nacional')
# Los Andes (1900–1943): Susques y el sector rotulado Los Andes en el SVG.
andes = ET.Element('g')
for e in layer.iter():
    if e.get(L) in ('Susques', 'Los Andes'): andes.append(copy.deepcopy(e))
add(andes, 'Los Andes', 'Territorios nacionales', 'territorio nacional')
assert sum(u['k']=='territorio nacional' for u in units) == 10, [(u['n'],len(u['ids'])) for u in units if u['k']=='territorio nacional']
cache=HERE/'geometria_adaptada.pkl'
raw_cache=ROOT/'mapas/mapa1912/units_raw.pkl'
if not raw_cache.exists():
    sys.path.insert(0,str(ROOT/'mapas/mapa1912'))
    import geom
    raw_cache.write_bytes(pickle.dumps(geom.load()))
cache_key=hashlib.sha256(SOURCE.read_bytes()+(HERE/'geometria_1904.py').read_bytes()+(ROOT/'mapas/mapa1912/units_raw.pkl').read_bytes()+repr([u['ids']for u in units]).encode()).hexdigest()
saved=pickle.loads(cache.read_bytes())if cache.exists()else {}
if saved.get('key')==cache_key:
    geometries,geometry_audit,province_shapes=saved['data']
else:
    geometries,geometry_audit,province_shapes=adapt_geometry(units,paths,ROOT)
    cache.write_bytes(pickle.dumps(dict(key=cache_key,data=(geometries,geometry_audit,province_shapes))))
dump('CONTROL_GEOMETRIA.json',geometry_audit)

body, pv = [], []
records, rows_export = [], []
for i,u in enumerate(units):
    d=d_path(geometries[i],4 if u['p']=='Capital Federal'else 2);cls='dc' if u['p']=='Capital Federal' else 'd'
    body.append(f'<path class="{cls}" data-i="{i}" d="{d}"/>')
    if u['key'] not in groups:
        territory = u['k']=='territorio nacional'
        records.append(dict(fill='#c5c5c5' if territory else '#808080', lines=[], note='Territorio nacional sin representación en Diputados.' if territory else 'Esta circunscripción no renovó su banca el 13 de marzo de 1904.'))
        continue
    g = groups[u['key']]; first = g['rows'][0]; c = party_code(first['party'])
    known = all(r['votes'] is not None for r in g['rows'])
    total = sum(r['votes'] or 0 for r in g['rows'])
    lines=[]
    for j,r in enumerate(g['rows']):
        code=f'c{i}_{j}'; pc=party_code(r['party'])
        CAND[code]=dict(n=r['candidate']+(' · '+r['party'] if r['party'] else ''), base=CAND[pc]['base'])
        lines.append([code,r['votes'],100*r['votes']/total if known else None])
        rows_export.append(dict(provincia=u['p'],numero=u['key'][1],circunscripcion=u['n'],**r,bloque=pc))
    assert not known or first['votes'] == max(r['votes'] for r in g['rows'])
    records.append(dict(w=c if known else None, q=100*first['votes']/total if known else None,
                        lines=lines,
                        metrics=[['Votos publicados', f'{total:,}'.replace(',','.')]] if known else [],
                        note=('Electo: '+first['candidate']+' ('+first['party']+'). '+('Votos individuales; no se suman candidatos para decidir el ganador.' if known else 'La fuente no publica votos: sin porcentaje ni imputación.'))))
    if not known:records[-1]['fill']='#e6dcc3'

for p,g in province_shapes.items():
    label='Territorios nacionales'if p in [u['n']for u in units if u['k']=='territorio nacional']else p
    pv.append(f'<path class="pf" data-prov="{html.escape(label)}" d="{d_path(g.simplify(.3))}"/>')
import shapely
import lxml.html
# Mismo trazo SHP, simplificación y proyección del atlas 1912; no una
# segunda versión de las islas con mayor densidad o contorno distinto.
reference=json.loads((ROOT/'mapas/mapa1912/dataset_1912.json').read_text(encoding='utf8'))
mal_index=next(i for i,u in enumerate(reference['territories'])if u['n']=='Islas Malvinas')
reference_svg=lxml.html.parse(str(ROOT/'mapas/mapa1912/atlas_1912_diputados.html')).getroot().get_element_by_id('B')
mal_paths=[p.get('d')for p in reference_svg.iter('path')if p.get('data-i')==str(mal_index)]
assert len(mal_paths)==1
mal_path=mal_paths[0]
body.append('<path class="mal" style="display:inline;fill:#a9a9a9;stroke:#1b1b1b;stroke-width:1" d="'+mal_path+'"/>')
pv.append('<path class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round" d="'+mal_path+'"/>')

def window(prov, nums=None, pad=.07):
    import shapely
    indices=[i for i,u in enumerate(units) if u['p']==prov and (nums is None or u['key'][1] in nums)]
    x,y,X,Y=shapely.total_bounds([geometries[i]for i in indices]);w,h=X-x,Y-y
    return [x-w*pad,y-h*pad,w*(1+2*pad),h*(1+2*pad)]
insets=[
 dict(id='tuc',label='Tucumán',f=[450,300,200,185],win=window('Tucumán'),show=['d'],sd=1.5),
 dict(id='sj',label='Gran San Juan',f=[328,545,321,159],win=window('San Juan',[1,3]),show=['d'],sd=1.5),
 dict(id='mza',label='Gran Mendoza',f=[328,783,224,187],win=window('Mendoza'),show=['d'],sd=1.5),
 dict(id='res',label='Resistencia + Corrientes capital',f=[1413,499,464,209],win=window('Corrientes',[1]),show=['d'],sd=1.5),
 dict(id='amba',label='Área Metropolitana de Buenos Aires',f=[1247,785,647,320],win=window('Buenos Aires',[8,9,10,11,12,13,14]),show=['d','dc'],sd=1.5),
 dict(id='caba',label='Capital Federal',f=[1632,1187,191,232],win=window('Capital Federal',pad=.02),show=['dc'],sd=1.5,fit='meet',noframe=True,lx=1728),
]
def city_window(lon,lat,w,h):
    x=(lon+73.5708041)*math.cos(math.radians(38))*44+643
    y=(-21.7807776-lat)*44+150
    return [x-w/2,y-h/2,w,h]
insets[1]['win']=city_window(-68.52,-31.54,57.3,28.4)
insets[2]['win']=city_window(-68.85,-32.90,90.12,75.24)
insets[3]['win']=city_window(-58.92,-27.46,100,45.04)
# El mismo recorte metropolitano que 1912, en la misma proyección.
insets[4]['win']=copy.deepcopy(next(i['win']for i in json.loads((ROOT/'mapas/mapa1912/dataset_1912.json').read_text(encoding='utf8'))['insets']if i['id']=='gba'))
prov = {p:dict(fill='#c5c5c5',lines=[],note='Seleccione una circunscripción para ver los candidatos. La provincia no fue un distrito único en esta elección.') for p in {u['p']for u in units}}
for p in prov:
    votes=Counter()
    for (province,_),g in groups.items():
        if province==p:
            for r in g['rows']:votes[party_code(r['party'])]+=r['votes']or 0
    s=sum(votes.values())
    if s:
        winner= votes.most_common(1)[0][0]
        prov[p]=dict(w=winner,q=100*votes[winner]/s,lines=[[c,v,100*v/s]for c,v in votes.most_common()],note='Agregado provincial de votos publicados por afiliación; el mapa y las fichas individuales mantienen las circunscripciones uninominales. En Catamarca no hay cifras publicadas.')
NATIONAL_NOTE+=' Las circunscripciones del SVG se adaptan geométricamente a los contornos del SHP 1914 y la proyección habitual del proyecto; los límites internos son una aproximación cartográfica, sin transformar los resultados a municipios ni departamentos.'
NATIONAL_NOTE+=' Agradecemos a Faustino Sojo, usuario de Wikipedia, por la elaboración de los SVG y la recopilación de los datos de esta elección.'
NATIONAL_NOTE+=' SVG original: Faustino Sojo (2022), CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Mapa_de_las_elecciones_legislativas_de_Argentina_de_1904_por_circunscripci%C3%B3n.svg . SHP histórico: Rodríguez/CONICET, CC BY 2.5 Argentina. Cartografía adaptada: CC BY-SA 4.0.'
modes=[dict(id='gan',tile='GANÓ',set='1',units=records,prov=prov,national=national,note=NATIONAL_NOTE)]
for code in ('PAN','PR','PS'):
    rs=copy.deepcopy(records)
    for i,(u,r) in enumerate(zip(units,rs)):
        if u['key'] not in groups or records[i].get('q') is None: continue
        g=groups[u['key']]; total=sum(x['votes']for x in g['rows'])
        pct=100*sum(x['votes']for x in g['rows'] if party_code(x['party'])==code)/total
        # La coropleta suma votos de todos los candidatos del partido; el ganador sigue siendo individual.
        base=CAND[code]['base']; rgb=[int(base[k:k+2],16)for k in (1,3,5)]
        a=.12+.88*min(9,int(pct/10))/9
        r['fill']='#'+''.join(f'{round(255+(x-255)*a):02x}'for x in rgb)
        r['metrics'].append([f'% {code} · todos sus candidatos',f'{pct:.2f} %'])
    rgb=[int(CAND[code]['base'][k:k+2],16)for k in (1,3,5)]
    stops=[['#'+''.join(f'{round(255+(v-255)*(.12+.88*j/9)):02x}'for v in rgb),f'{10*j}'+(' %'if j<9 else '+ %')]for j in range(10)]
    modes.append(dict(id=code.lower(),tile='% '+code,set='1',units=rs,prov=prov,national=national,note=NATIONAL_NOTE,legend=dict(title='% '+code+' · votos publicados',stops=stops)))
ds=dict(slug='diputados_1904',locale='es-AR',country='Argentina',title='Elecciones legislativas de Argentina de',year='1904',exterior=False,
        labels=dict(pie1='Votos por afiliación · cobertura parcial',pie2='',results='Votos publicados',won='VOTOS'),candidates=CAND,
        sets={'1':dict(label='1904',subtitle='Ley 4161 · 13 de marzo')},modes=modes,insets=insets,solid=[],
        territories=[{k:u[k]for k in ('n','p','k')}for u in units])
dump('dataset_1904.json',ds)
dump('CONTROL_1904.json',dict(circunscripciones=120,renovadas=len(groups),sin_eleccion=60,territorios=10,con_votos=59,sin_votos=['Catamarca 2'],bancas_tabla=dict(seats),bancas_leyenda_wikipedia=53,
                             geometria_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),votos_por_afiliacion=dict(totals),positivos_publicados=positive,metodo='Ganador individual; torta de votos publicados por afiliación, 59/60 circunscripciones; sin imputación.'))
with (HERE/'candidatos_1904.csv').open('w',encoding='utf-8-sig',newline='')as f:
    w=csv.DictWriter(f,fieldnames=list(rows_export[0]));w.writeheader();w.writerows(rows_export)

tpl=(ROOT/'.claude/skills/mapa-electoral-wikipedia-1999/assets/template.html').read_text(encoding='utf8')
tpl=tpl.replace('<title>Atlas electoral</title>','<title>Diputados nacionales 1904 · Circunscripciones</title>')
tpl=re.sub(r'(<svg\b[^>]*\bid="atlas"[^>]*>)',lambda m:m[1]+'<desc>'+html.escape(NATIONAL_NOTE)+'</desc>',tpl,count=1)
tpl=tpl.replace('</head>','<style>.nt{stroke:none!important}</style></head>')
tpl=re.sub(r'<image id="frontiers"[^>]+/>','<g id="frontiers"></g>',tpl)
start=tpl.index('const INSETS=[');end=tpl.index('];',start)+2
tpl=tpl[:start]+'const INSETS=DATA.insets||[];'+tpl[end:]
tpl=tpl.replace('function drawExterior(){\n  const g=$("#exterior");g.replaceChildren();','function drawExterior(){\n  const g=$("#exterior");g.replaceChildren();if(DATA.exterior===false){$("#malv").replaceChildren();return;}')
tpl=tpl.replace('const h=50,win=idx===0&&!LG','const h=34,win=idx===0&&!LG').replace('let y=1292;','let y=995;').replace('x:93,y:1266','x:93,y:969')
tpl=tpl.replace('y:y+36,"font-size":lg.length>2?34:40','y:y+28,"font-size":lg.length>2?25:30').replace('y:y+41','y:y+32').replace('y:y+39,"font-size":15','y:y+31,"font-size":12').replace('y:y+21,"font-size":21','y:y+16,"font-size":18').replace('y:y+33,"font-size":23','y:y+27,"font-size":21')
logo_old='el("text",{x:104,y:y+28,"font-size":lg.length>2?25:30,fill:"#fff","letter-spacing":-1},g,lg);'
tpl=tpl.replace(logo_old,'if(C.img){const ih=h*(C.bl||1.2),iw=ih*(C.ar||1),cv=el("svg",{x:93,y,width:100,height:h,overflow:"hidden"},g);el("image",{href:C.img,x:4+(h*1.2-iw)/2,y:-(ih-h)/2,width:iw,height:ih,preserveAspectRatio:"xMidYMid meet"},cv);}else '+logo_old)
tpl=tpl.replace('el("rect",{x:104,y:y+32,width:lg.length>2?', 'if(!C.img)el("rect",{x:104,y:y+32,width:lg.length>2?')
end_legend='    y+=h+(idx+1<rows.length&&!LG&&wins[rows[idx+1].code]?5:7);\n  });'
tpl=tpl.replace(end_legend,end_legend+'''
  y+=14;for(const [col,text]of [["#808080","Sin elección"],["#c5c5c5","Territorio nacional · sin representación"],["#e6dcc3","Catamarca 2 · votos no publicados"]]){
    el("rect",{x:93,y:y-12,width:14,height:14,fill:col},g);el("text",{x:116,y,"font-size":14,fill:"#616161"},g,text);y+=21;}
''')
tpl=tpl.replace('transform="matrix(0.1448 0 0 0.1448 55.7 599.8)"','transform="matrix(0.22 0 0 0.22 -30 565)"')
# Marcas de recuadros antes de 1946: seis, sin Antártida.
tpl=re.sub(r'<path clip-rule="evenodd" d="M570 100h840v1540h-840z [^"]+"/>','<path id="clippath" clip-rule="evenodd" d="M570 100h840v1540h-840z"/>',tpl)
tpl=tpl.replace('function drawInsets(){','function drawInsets(){let cd="M570 100h840v1540h-840z";for(const I of INSETS){const [x,y,w,h]=I.f,x0=Math.max(570,x),y0=Math.max(100,y),x1=Math.min(1410,x+w),y1=Math.min(1640,y+h);if(x1>x0&&y1>y0)cd+=` M${x0} ${y0}h${x1-x0}v${y1-y0}h${x0-x1}z`;}$("#clippath").setAttribute("d",cd);')
for a,b in {'{{MAIN_S}}':'1','{{MAIN_TX}}':'0','{{MAIN_TY}}':'0','{{MAP}}':''.join(body),'{{PV}}':''.join(pv),'{{DATA}}':json.dumps(ds,ensure_ascii=False,separators=(',',':')),'{{MODE}}':'gan'}.items():tpl=tpl.replace(a,b)
assert not re.search(r'\{\{[A-Z_]+\}\}',tpl)
(HERE/'atlas_1904.html').write_text(tpl,encoding='utf8',newline='\n')
print('1904:',len(units),'unidades;',dict(seats),'; 59 circunscripciones con votos, Catamarca pendiente.')
