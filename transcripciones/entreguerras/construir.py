"""Atlas 1926/1937/1940, derivado del dibujo de 1930 y de los atlas publicados 1922/1928.
Uso desde la raíz: python transcripciones/entreguerras/construir.py 1926
"""
from pathlib import Path
import sys, os, json, pickle, copy, re
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'comun'),str(ROOT/'mapas/mapa1930')]
import numpy as np, shapely
from shapely.ops import unary_union
import geom
from names import norm
from atlas_datos import prepare
from datos import NATIONAL
Y=int(sys.argv[1]);assert Y in (1918,1920,1926,1936,1937,1940)
HERE=str(ROOT/'mapas'/f'mapa{Y}');Path(HERE).mkdir(exist_ok=True)
TEMPLATE_SRC=str(ROOT/'.claude/skills/mapa-electoral-wikipedia-1999/assets/template.html')
# ---------------------------------------------------------------- proyeccion
S, X0, Y0 = 44.0, 643.0, 150.0
LON0, LAT1 = -73.5708041, -21.7807776


def proj(a):
    a = np.asarray(a, float).copy()
    a[:, 0] = (a[:, 0] - LON0) * geom.KX * S + X0
    a[:, 1] = (LAT1 - a[:, 1]) * S + Y0
    return a


def ll(lon, lat):
    return ((lon - LON0) * geom.KX * S + X0, (LAT1 - lat) * S + Y0)


def f2(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


def ring_d(c):
    pts = list(c.coords)
    return "M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts[:-1]) + "Z"


def geom_d(g):
    if g.is_empty:
        return ""
    gs = g.geoms if hasattr(g, "geoms") else [g]
    out = []
    for p in gs:
        if p.geom_type != "Polygon":
            continue
        out.append(ring_d(p.exterior))
        for h in p.interiors:
            out.append(ring_d(h))
    return "".join(out)


def line_d(g):
    gs = g.geoms if hasattr(g, "geoms") else [g]
    out = []
    for l in gs:
        pts = list(l.coords)
        if len(pts) < 2:
            continue
        out.append("M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts))
    return "".join(out)


# ---------------------------------------------------------------- geometria
PKL = str(ROOT / "mapas/mapa1930/units_raw.pkl")
if not os.path.exists(PKL):
    pickle.dump(geom.load(), open(PKL, "wb"))
U = pickle.load(open(PKL, "rb"))
U.sort(key=lambda u: (u["prov"], u["name"]))
G_raw = [shapely.transform(u["geom"], proj) for u in U]
G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.3))
print("unidades", len(U), "coords", sum(shapely.get_num_coordinates(g) for g in G), file=sys.stderr)

PROVS = sorted(set(u["prov"] for u in U))
prov_geom = {}
for p in PROVS:
    gs = [G[i] for i, u in enumerate(U) if u["prov"] == p]
    prov_geom[p] = unary_union([g.buffer(0.12) for g in gs]).buffer(-0.12)
country = unary_union(list(prov_geom.values())).buffer(0.1).buffer(-0.1)
prov_geom = {p: g.simplify(0.12) for p, g in prov_geom.items()}
country = country.simplify(0.12)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from outline_clean import clean_outline, clean_holes
country = clean_outline(country)    # quita huecos e islotes diminutos del contorno (puntos grises en San Luis y la costa de Buenos Aires)
prov_geom = {p: clean_holes(g, name=p) for p, g in prov_geom.items()}    # rellena rendijas diminutas dentro de cada provincia (puntos blancos en San Luis y Buenos Aires)
prov_mini = {p: g.simplify(0.7) for p, g in prov_geom.items()}


ctx=prepare(Y,U,norm)
for k in ('KEY','CAND','BLOCS','GREY_T','GREY_N','KEYS','unit_rec','unit_an','prov_rec','prov_an','disp','unmapped'):
    globals()[k]=ctx[k]
an_of=lambda t:t
import wikitop
cands,slices,partp,NAT_MET=wikitop.national(Y)
NOTE=(wikitop.note(Y)+
      ' Fuente local: Cantón (1968), t. II, varones solamente. Geometría de 1914, como los atlas publicados de 1922/1928; '
      'correspondencias nominales y unidades compartidas documentadas. Sin imputación de votos. ')
if Y==1936:
    NOTE=('Resultado nacional (torta y barras): tabla de «Elecciones legislativas de Argentina de 1936» en la Wikipedia en español, porcentajes sobre votos positivos. '
          'Departamentos: actas de las Juntas Escrutadoras de Tucumán (expediente 26-OV-1936) y Santa Fe (29-OV-1936) de la Cámara de Diputados; '
          'Cantón no publica 1936 por departamento. Cada lista cuenta los votos de su candidato más votado en la provincia, como la Wikipedia. '
          'En Trancas (Tucumán) los nulos y blancos están extrapolados del residuo provincial; las listas son lecturas. '
          'Las otras nueve provincias que votaron, sin cuadro departamental, se pintan enteras con su total provincial de la Wikipedia; '
          'Catamarca, La Rioja, Salta y San Juan no renovaron diputados. Concordancia = PDN, UCR de Santa Fe, UCR Unificada, Partido Liberal de Corrientes, '
          'Partido Socialista Independiente, Partido Popular de Jujuy y aliados, como el «Total Concordancia» del artículo. Geometría de 1914. ')
if Y in (1937,1940):
    NOTE+='Cobertura parcial: selección de distritos publicada por Cantón según su criterio editorial de 1931–1942; no certifica ausencia de irregularidades. '
if Y in (1918,1920):
    NOTE+='Cobertura parcial de las tablas publicadas; sin completar con votos provinciales. '
    NOTE+=('Reserva cronológica: Capital y Santa Fe 1918 citan prensa de 1922 para partidos; se conserva el año del encabezado del libro. ' if Y==1918 else
           'Reserva cronológica: Capital 1920 cita prensa de 1924 para votantes; Jujuy conserva cifras con identidad partidaria pendiente en beige. ')
NOTE+='La suma territorial puede diferir del resultado nacional de Wikipedia; se conservan las discrepancias del original.'
def fmt_n(v):return f'{int(v):,}'.replace(',','.')
def fmt_p(v):return ('%.1f'%v).replace('.',',')
def mix(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(255 + (c[k] - 255) * t) for k in range(3))


def stops_for(base, edges):
    ts = [0.12 + 0.88 * i / (len(edges) - 1) for i in range(len(edges))]
    lab = ["%d%%" % e for e in edges[:-1]] + ["+%d%%" % edges[-1]]
    return [mix(base, t) for t in ts], lab


def bin_of(p, edges):
    i = 0
    while i + 1 < len(edges) and p >= edges[i + 1]: i += 1
    return i


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(U)):
        r = unit_rec[i]; a = unit_an.get(i)
        p = fn(a) if (a and a["D"]) else None
        if p is not None:
            nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
            nr["fill"] = cols[bin_of(p, edges)]
            units.append(nr)
        else:
            nr = {k: v for k, v in r.items() if k not in ("w", "q")}
            nr.setdefault("fill", GREY_N)
            units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        if p in geom.TERR or p not in prov_an: prov[p] = r; continue
        v = fn(an_of(prov_an[p]))
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)



MODES=[dict(id='gan',tile='GANÓ',note=NOTE,units=[unit_rec[i] for i in range(len(U))],prov=prov_rec,
            national=dict(cands=cands,slices=slices,partp=partp,metrics=NAT_MET),legend=dict(keys=KEYS))]
for b in BLOCS:
    un,pv,lg=mode_choropleth(lambda a,b=b:100*a['bloc'].get(b,0)/a['D'],CAND[b]['base'],list(range(0,70,10)),'% '+CAND[b]['n'])
    MODES.append(dict(id=b.lower(),tile=b if b in ('UCR','CON','ANT') else '',note=NOTE,units=un,prov=pv,
                      national=dict(cands=cands,slices=slices,partp=partp,metrics=NAT_MET),legend=lg))
un,pv,lg=mode_choropleth(lambda a:100*a['vot']/a['ins'] if a['vot'] and a['ins'] else None,
                         '#2a6f97',[0,40,50,60,70,80,90],'Participación (votantes / inscriptos)')
MODES.append(dict(id='par',tile='PART',note=NOTE,units=un,prov=pv,
                  national=dict(cands=cands,slices=slices,partp=partp,metrics=NAT_MET),legend=lg))
# ---------------------------------------------------------------- SVG
def idx_of(prov, name):
    return KEY[(prov, norm(name))]


body = []
for i, u in enumerate(U):
    body.append('<path class="d" data-i="%d" d="%s"/>' % (i, geom_d(G[i])))
# circunscripciones de la Capital en alta resolucion para su recuadro
cap_idx = [i for i, u in enumerate(U) if u["prov"] == "Capital Federal"]
for i in cap_idx:
    hi = shapely.simplify(G_raw[i], 0.01)
    body.append('<path class="dc" data-i="%d" d="%s"/>' % (i, geom_d(hi)))
for p in PROVS:
    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(prov_geom[p].boundary)))
body.append('<path class="out" d="%s"/>' % line_d(country.boundary))
for txt, lon, lat, rot in (("BOLIVIA", -65.2, -21.55, 0), ("PARAGUAY", -59.3, -22.05, 0), ("BRASIL", -53.2, -25.2, 0),
                           ("URUGUAY", -56.0, -32.2, 0), ("CHILE", -73.9, -39.0, -90)):
    x, y = ll(lon, lat)
    body.append('<text class="cn" x="%s" y="%s" text-anchor="middle"%s>%s</text>' % (f2(x), f2(y), (' transform="rotate(%d %s %s)"' % (rot, f2(x), f2(y))) if rot else "", txt))

# insets ---------------------------------------------------------------
def bbox_of(idx):
    b = shapely.total_bounds([G_raw[i] for i in idx]); return b


def window(b, aspect, pad=0.07, cx=None, cy=None, w=None):
    x0, y0, x1, y1 = b
    ww, hh = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    if ww / hh < aspect: ww = hh * aspect
    else: hh = ww / aspect
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(mx - ww / 2, 2), round(my - hh / 2, 2), round(ww, 2), round(hh, 2)]


tuc = [i for i, u in enumerate(U) if u["prov"] == "Tucumán"]
caba_b = bbox_of(cap_idx)
cx, cy = (caba_b[0] + caba_b[2]) / 2, (caba_b[1] + caba_b[3]) / 2
gba_w = 62.0
import insets99    # los recuadros que faltaban (Gran San Juan, Gran Mendoza, Resistencia + Corrientes y Antártida), como en Wikipedia 1999
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True, antarctic=False, sj_names={"Capital", "Santa Lucia", "Chimbas", "Rivadavia", "Pocito", "Albardon", "Trinidad", "Concepcion", "Desamparados", "Zonda", "Rawson"}, chaco_names={"Resistencia"})
body.append(X99["ant_body"])
INSETS = [
    dict(id="tuc", label="Tucumán", f=[450, 300, 200, 185], win=window(bbox_of(tuc), 200 / 185), show=["d", "pb"], sd=2.6, sp=3.4),
    dict(id="gba", label="Área Metropolitana de Buenos Aires", f=[1247, 785, 647, 320], win=[round(cx - gba_w * 0.42, 2), round(cy - gba_w / (647 / 320) * 0.5, 2), gba_w, round(gba_w / (647 / 320), 2)], show=["d", "pb", "out"], sd=1.9, sp=3.0, so=2.6),
    dict(id="caba", label="Capital Federal", f=[1632, 1187, 191, 232], win=window(caba_b, 191 / 232, 0.05), show=["dc"], sd=3, fit="meet", noframe=True, lx=1728, noclip=True, so=2.6),
]
INSETS = [INSETS[0], X99["sj"], X99["mza"], X99["res"], INSETS[1]] + ([X99["ant"]] if X99["ant"] else []) + INSETS[2:]   # sin recuadro de la Antártida (anterior a 1946)
marks = [("tuc", INSETS[0]["win"]), ("gba", INSETS[4]["win"])] + X99["marks"]
for _, w in marks:
    body.append('<rect class="mk" x="%s" y="%s" width="%s" height="%s"/>' % tuple(f2(v) for v in w))

# mini de provincias
KPV = 0.2669
bx0, by0, bx1, by1 = shapely.total_bounds([prov_geom[p] for p in PROVS])
pv_tx = 182 - KPV * (bx0 + bx1) / 2
pv_ty = 600 - KPV * by0
pv = ['<g>']
for p in PROVS:
    pv.append('<path class="pf" data-prov="%s" d="%s"/>' % (p, geom_d(prov_mini[p])))
for _i, _u in enumerate(U):   # Malvinas en gris tambien en el mini de provincias (la simplificacion de provincias las borra)
    if _u["name"] == "Islas Malvinas":
        pv.append('<path class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round" d="%s"/>' % geom_d(G[_i]))
pv.append("</g>")

# dataset ----------------------------------------------------------------
ds = dict(
    slug=f"elecciones_{Y}", locale="es-AR", country="Argentina",
    title=("Elecciones presidenciales de Argentina de" if Y==1937 else "Elecciones legislativas de Argentina de"), year=str(Y),
    labels=dict(pie1="Proporción sobre votos positivos"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label=str(Y), subtitle=("Actas HCDN · deptos. de 1914" if Y==1936 else "Cantón · deptos. de 1914"))},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
if ctx['SOLID']: ds['solid']=sorted(ctx['SOLID'])   # 1936: provincias pintadas con su total
json.dump(ds, open(os.path.join(HERE, f"dataset_{Y}.json"), "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", f"<title>Atlas electoral {Y}</title>")
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"', 'style="--v-d:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub('<g id="pv" transform="matrix(0.1448 0 0 0.1448 55.7 599.8)" style="--spf:9.7px">', '<g id="pv" transform="matrix(%s 0 0 %s %s %s)" style="--spf:9.7px">' % (KPV, KPV, f2(pv_tx), f2(pv_ty)))
sub("#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}", "#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}")
# recuadros dirigidos por el dataset
i0 = tpl.index("const INSETS=["); i1 = tpl.index("];", i0) + 2
tpl = tpl[:i0] + "const INSETS=DATA.insets||[];" + tpl[i1:]
sub('<defs><clipPath id="mapclip"><path clip-rule="evenodd" d="M570 100h840v1540h-840z M570 300h80v185h-80z M570 545h79v159h-79z M1247 785h163v320h-163z M1247 1166h163v452h-163z M985 1200h200v320h-200z"/></clipPath></defs>',
    '<defs><clipPath id="mapclip"><path id="clippath" clip-rule="evenodd" d="M570 100h840v1540h-840z"/></clipPath></defs>')
sub("function drawInsets(){", """function clipHoles(){
  const R=[570,100,1410,1640];let d="M570 100h840v1540h-840z";
  for(const I of INSETS){if(I.noclip)continue;const [x,y,w,h]=I.f;const x0=Math.max(x,R[0]),y0=Math.max(y,R[1]),x1=Math.min(x+w,R[2]),y1=Math.min(y+h,R[3]);
    if(x1>x0&&y1>y0)d+=` M${x0} ${y0}h${x1-x0}v${y1-y0}h${x0-x1}z`;}
  $("#clippath").setAttribute("d",d);
}
function drawInsets(){
  clipHoles();""")
sub("    if(I.sf)st+=`;--sf:${(I.sf/sc).toFixed(4)}px`;", "    if(I.sf)st+=`;--sf:${(I.sf/sc).toFixed(4)}px`;\n    if(I.so)st+=`;--so:${(I.so/sc).toFixed(4)}px`;")
sub("function drawExterior(){\n  const g=$(\"#exterior\");g.replaceChildren();", "function drawExterior(){\n  const g=$(\"#exterior\");g.replaceChildren();\n  if(DATA.exterior===false){$(\"#malv\").replaceChildren();return;}")
# leyenda: claves de gris y modo sin rampa
sub("""    el("text",{x:104,y:y+36,"font-size":lg.length>2?34:40,fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41,width:lg.length>2?(lg.length*20):(lg.length*23),height:3,fill:"#fff",opacity:.8},g);""",
    """if(C.img){const ih=h*(C.bl||1.2),iw=ih*(C.ar||1),cv=el("svg",{x:93,y,width:110,height:h,overflow:"hidden"},g);   // el logo desborda la barra y se recorta al marco
      el("image",{href:C.img,x:4+(h*1.2-iw)/2,y:-(ih-h)/2,width:iw,height:ih,preserveAspectRatio:"xMidYMid meet"},cv);}
    else{el("text",{x:104,y:y+36,"font-size":lg.length>2?34:40,fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41,width:lg.length>2?(lg.length*20):(lg.length*23),height:3,fill:"#fff",opacity:.8},g);}""")
sub("""    y+=h+(idx+1<rows.length&&!LG&&wins[rows[idx+1].code]?5:7);
  });""", """    y+=h+(idx+1<rows.length&&!LG&&wins[rows[idx+1].code]?5:7);
  });
  if(LG&&LG.keys){
    y+=(rows.length?22:14);
    LG.keys.forEach(([col,lab])=>{el("rect",{x:93,y:y-12,width:16,height:14,fill:col,stroke:"#616161","stroke-width":.8},g);el("text",{x:118,y:y,"font-size":15,fill:"#616161"},g,lab);y+=22;});
  }""")
sub("""  const LG=MODES[MODE].legend;                                   // leyenda propia para mapas de color explícito (coropletas)""",
    """  const LG0=MODES[MODE].legend;const LG=(LG0&&LG0.stops)?LG0:null;   // leyenda propia para mapas de color explícito (coropletas)
  const KEYS=LG0&&LG0.keys?LG0:null;
  const USED=c=>[...document.querySelectorAll('#B .d,#B .dc')].some(e=>(e.getAttribute("fill")||"").toLowerCase()===c.toLowerCase());   // solo se rotula el gris que alguna unidad usa en este modo
  """)
sub("if(LG&&LG.keys){", "if(KEYS){")
sub("LG.keys.forEach(", "KEYS.keys.filter(([k])=>USED(k)).forEach(")
sub("const rows=(LG&&LG.bars===false)?[]:N.cands;", "const rows=(LG0&&LG0.bars===false)?[]:N.cands;")
# pie sin segundo texto cuando no hay participacion
sub("""$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;""", """$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;$("#pie1").setAttribute("x",184);""")
# leyenda de 8 bloques: empieza mas arriba (bajo el mini de provincias) y con barras mas bajas
sub('''el("text",{x:93,y:1266,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=1292''',
    '''const MANY=N.cands.length>5,Y0=N.cands.length>8?980:MANY?1024:1266;
  el("text",{x:93,y:Y0,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=Y0+26;''')
sub("const h=50,win=idx===0&&!LG", "const h=N.cands.length>8?34:MANY?42:50,k=h/50,win=idx===0&&!LG")
sub('''el("text",{x:104,y:y+36,"font-size":lg.length>2?34:40,fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41,''',
    '''el("text",{x:104,y:y+36*k,"font-size":(lg.length>3?26:lg.length>2?30:34)*(MANY?.9:1),fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41*k,''')
sub('width:lg.length>2?(lg.length*20):(lg.length*23),height:3', 'width:(lg.length>3?lg.length*15:lg.length>2?(lg.length*18):(lg.length*20))*(MANY?.9:1),height:3')
sub('el("text",{x:424,y:y+21,"font-size":21,', 'el("text",{x:424,y:y+20*k,"font-size":MANY?18:21,')
sub('if(C.sub)el("text",{x:424,y:y+39,"font-size":15,', 'if(C.sub)el("text",{x:424,y:y+37*k,"font-size":MANY?13:15,')
sub('el("text",{x:477,y:y+29,"font-size":26,', 'el("text",{x:477,y:y+29*k,"font-size":MANY?23:26,')
sub('el("text",{x:497,y:y+44,"font-size":10,', 'el("text",{x:497,y:y+44*k,"font-size":10,')
sub('el("text",{x:476,y:y+33,"font-size":23,', 'el("text",{x:476,y:y+33*k,"font-size":MANY?20:23,')
# cinco modos: un recuadro mas y el subtitulo corrido a la derecha
sub("return out.slice(0,4);", "return out.slice(0,5);")
sub("xs=[1262,1316,1370,1424]", "xs=[1262,1314,1366,1418,1470]")
sub('<text id="sub" x="1515"', '<text id="sub" x="1536"')
tpl = re.sub(r'function tilesNow\(\)\{.*?\n\}', '''function tilesNow(){
  let list=DATA.modes.filter(m=>m.tile).map(m=>[m.id,m.tile]);
  if(!list.some(([id])=>id===MODE))list.splice(4,0,[MODE,MODES[MODE].tile||MODE.toUpperCase()]);
  return list.slice(0,5);
}''', tpl, count=1, flags=re.S)
if Y in (1918,1920):
    # Cinco ganadores necesitan espacio bajo el mini provincial, sin achicar las barras históricas.
    tpl=tpl.replace('Y0=N.cands.length>8?980:MANY?1024:1266','Y0=N.cands.length>8?980:MANY?1024:1164')
    # La descarga conserva las reservas del registro y avisa cuando una fila se comparte.
    tpl=tpl.replace('"pct_ganador"];codes.forEach', '"pct_ganador","fuente_y_reservas"];codes.forEach')
    tpl=tpl.replace('u.q!=null?u.q:""];', 'u.q!=null?u.q:"",u.note||""];')
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(HERE, f"atlas_{Y}.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print('escrito',out,flush=True)
from collections import Counter
control=dict(anio=Y,unidades_geometricas=len(U),unidades_con_votos=len(unit_an),
    ganadores_por_poligono=dict(Counter(r.get('w') for r in unit_rec.values() if r.get('w'))),
    sin_poligono=[dict(prov=r['prov'],unidad=r['name'],pagina_pdf=r['page'],votos=sum(r['P'].values())) for r in unmapped],
    filas_fuente_usadas_sin_duplicar=len(ctx['usedrows']),
    fuente_geometria='Departamentos_1914; mismo dibujo y proyección que 1922/1928/1930',
    modos=[m['id'] for m in MODES])
if Y in (1918,1920):
    control['poligonos_con_cifras_publicadas']=sum(bool(r.get('lines')) for r in unit_rec.values())
    control['poligonos_con_identidad_pendiente']=[dict(prov=U[i]['prov'],unidad=U[i]['name']) for i,r in unit_rec.items() if r.get('lines') and i not in unit_an]
Path(HERE,'CONTROL_ATLAS.json').write_text(json.dumps(control,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(control,ensure_ascii=False),flush=True)
