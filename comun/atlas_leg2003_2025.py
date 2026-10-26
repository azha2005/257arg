"""Genera mapa2009/atlas_2009.html y mapa2009/dataset_2009.json (Diputados Nacionales 2009)."""
import os, sys, json, pickle, math, base64, io
import shapely
from shapely import affinity
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.abspath(__file__))
YEAR = int(sys.argv[1])
HERE = os.path.join(ROOT, f"../mapas/mapa{YEAR}")
os.makedirs(HERE, exist_ok=True)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import leg2003_2025_geom as geom
import wikitop
from names import norm

TPL = os.path.join(ROOT, "..", ".claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")
CSS_VARS = ("--v-d:inline;--v-dc:inline;--v-rcb:inline;--v-cabab:inline;--v-rcc:inline;"
            "--v-pb:inline;--v-out:inline;--v-ant:inline;--v-mal:inline")
S, X0, Y0 = 44.0, 643.0, 150.0
LON0, LAT1 = -73.5708041, -21.7807776

import numpy as np


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


def fill_slivers(g, amax=0.15):
    from shapely.geometry import Polygon, MultiPolygon
    gs = g.geoms if hasattr(g, "geoms") else [g]
    out = [Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area >= amax]) for q in gs]
    return out[0] if len(out) == 1 else MultiPolygon(out)


# ---------------------------------------------------------------- geometria (Departamentos_2010 + Lezama)
RAW_CACHE = os.path.join(HERE, "units_leg2003_2025.pkl")
if os.path.exists(RAW_CACHE):
    raw = pickle.load(open(RAW_CACHE, "rb"))
else:
    raw = geom.load(YEAR)
    pickle.dump(raw, open(RAW_CACHE, "wb"))

U = sorted(raw, key=lambda u: (u["prov"], int(u["name"].split()[1]) if u["prov"] == "Capital Federal" else u["name"]))
G_raw = [shapely.transform(u["geom"], proj) for u in U]
G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.3))

PROVS = sorted({u["prov"] for u in U})
prov_geom = {}
for p in PROVS:
    gs = [G[i] for i, u in enumerate(U) if u["prov"] == p]
    prov_geom[p] = unary_union([g.buffer(0.12) for g in gs]).buffer(-0.12)
    if p != "Tierra del Fuego":
        prov_geom[p] = fill_slivers(prov_geom[p], 5.0 if p == "Capital Federal" else 0.15)
country = unary_union(list(prov_geom.values())).buffer(0.1).buffer(-0.1)
_cf, _ba = prov_geom["Capital Federal"], prov_geom["Buenos Aires"]
_win = shapely.box(_cf.bounds[0] - 3, _cf.bounds[1] - 3, _cf.bounds[2] + 3, _cf.bounds[3] + 3)
_n = unary_union([_ba, _cf]).buffer(0.5).buffer(-0.5).intersection(_win).difference(unary_union([_ba, _cf]))
_n = unary_union([q for q in (_n.geoms if hasattr(_n, "geoms") else [_n]) if q.area >= 0.1])
prov_geom["Capital Federal"] = unary_union([_cf, _n])
country = unary_union([country, _n])
prov_geom = {p: g.simplify(0.12) for p, g in prov_geom.items()}
country = country.simplify(0.12)
from outline_clean import clean_outline, clean_holes
country = clean_outline(country)
for _p in PROVS: prov_geom[_p] = clean_holes(prov_geom[_p])
prov_mini = {p: g.simplify(1.2) for p, g in prov_geom.items()}


# Datos y controles compartidos: el cartel nacional se conserva separado del mapa.
from leg2003_2025_data import prepare
D = prepare(YEAR, U)
CAND, MODES, disp, ANT_I = D.CAND, D.MODES, D.disp, D.ANT_I
MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}

# ---------------------------------------------------------------- SVG
body = []
for i, u in enumerate(U):
    body.append('<path class="d" data-i="%d" d="%s"%s/>' % (i, geom_d(G[i]), ' style="stroke:#1b1b1b;stroke-width:1px"' if i in MALV else ""))
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
    body.append('<text class="cn" x="%s" y="%s" text-anchor="middle"%s>%s</text>' % (f2(x) if "f2" in globals() else "%.1f" % x, "%.1f" % y, (' transform="rotate(%d %.1f %.1f)"' % (rot, x, y)) if rot else "", txt))


def bbox_of(idx):
    return shapely.total_bounds([G_raw[i] for i in idx])


def window(b, aspect, pad=0.07):
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
import insets99
insets99.SHP = os.path.join(ROOT, "..", "geometria", "Base deptos 1869-2022", "Departamentos_2001" if YEAR <= 2007 else "Departamentos_2010")
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True)
body.append(X99["ant_body"].replace('class="ant"', 'class="ant" data-i="%d"' % ANT_I))
INSETS = [
    dict(id="tuc", label="Tucumán", f=[450, 300, 200, 185], win=window(bbox_of(tuc), 200 / 185), show=["d", "pb"], sd=2.6, sp=3.4),
    X99["sj"], X99["mza"], X99["res"],
    dict(id="gba", label="Área Metropolitana de Buenos Aires", f=[1247, 785, 647, 320], win=[round(cx - gba_w * 0.42, 2), round(cy - gba_w / (647 / 320) * 0.5, 2), gba_w, round(gba_w / (647 / 320), 2)], show=["d", "pb", "out"], sd=1.9, sp=3.0, so=2.6),
    X99["ant"],
    dict(id="caba", label="Capital Federal", f=[1632, 1187, 191, 232], win=window(caba_b, 191 / 232, 0.05), show=["dc"], sd=3, fit="meet", noframe=True, lx=1728, noclip=True, so=2.6),
]
marks = [("tuc", INSETS[0]["win"]), ("gba", INSETS[4]["win"])] + X99["marks"]
for _, w in marks:
    body.append('<rect class="mk" x="%s" y="%s" width="%s" height="%s"/>' % tuple("%.2f" % v for v in w))

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
pv.append('</g>')

ds = dict(
    year=YEAR, slug=f"diputados_{YEAR}", locale="es-AR", country="Argentina",
    title="Elecciones legislativas de Argentina de",
    exterior=False,
    sets={"1": dict(label="Resultados", subtitle="Diputados nacionales")},
    labels=dict(results="Resultados", won="GANÓ", pie1="Proporción sobre votos positivos",
                pie2="Anillo exterior: Participación", provinces="Provincias"),
    candidates=CAND, insets=INSETS, solid=D.report.get("solid", []),
    territories=[dict(p=u["prov"], n=disp[i], k=u["kind"]) for i, u in enumerate(U)]+[dict(p="Tierra del Fuego",n="Antártida Argentina",k="departamento")],
    modes=MODES,
)
open(os.path.join(HERE, f"dataset_{YEAR}.json"), "w", encoding="utf8").write(json.dumps(ds, ensure_ascii=False))

# ---------------------------------------------------------------- HTML
tpl = open(TPL, encoding="utf8").read()


def sub(old, new):
    global tpl
    assert old in tpl, "no encontrado: " + old[:60]
    tpl = tpl.replace(old, new, 1)


sub("<title>Atlas electoral</title>", f"<title>Elecciones legislativas {YEAR}</title>")
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub('<g id="pv" transform="matrix(0.1448 0 0 0.1448 55.7 599.8)" style="--spf:9.7px">',
    '<g id="pv" transform="matrix(%s 0 0 %s %.2f %.2f)" style="--spf:9.7px">' % (KPV, KPV, pv_tx, pv_ty))
sub('#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}',
    '#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}')
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"',
    'style="--v-d:inline;--v-dc:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<clipPath id="mapclip"><path clip-rule="evenodd" d="M570 100h840v1540h-840z M570 300h80v185h-80z M570 545h79v159h-79z M1247 785h163v320h-163z M1247 1166h163v452h-163z M985 1200h200v320h-200z"/></clipPath>',
    '<clipPath id="mapclip"><path id="clippath" clip-rule="evenodd" d="M570 100h840v1540h-840z"/></clipPath>')

s = tpl.index("const INSETS=["); e = tpl.index("];", s) + 2
tpl = tpl[:s] + "const INSETS=DATA.insets||[];" + tpl[e:]
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

sub('const shade=(code,i)=>{const b=CAND[code].base;return i===0?mixw(b,.15):mulc(b,SHADE_K[i])};',
    open(os.path.join(ROOT, "leyenda_clara.js"), encoding="utf8").read())

# Leyenda compacta para 15 bloques + clave de gris/beige
sub("""    const h=50,win=idx===0&&!LG,bar=C.bar||C.base;
    el("rect",{x:80,y,width:5,height:h-1,fill:mixw(bar,.42)},g);
    el("rect",{x:93,y,width:win?431:337,height:h,fill:bar},g);
    if(win)el("rect",{x:429,y,width:95,height:h,fill:mulc(bar,.85)},g);
    const lg=C.logo||c.code;                                    // sigla grande a la izquierda (en 1999: logo del frente)
    el("text",{x:104,y:y+36,"font-size":lg.length>2?34:40,fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41,width:lg.length>2?(lg.length*20):(lg.length*23),height:3,fill:"#fff",opacity:.8},g);
    el("text",{x:424,y:y+21,"font-size":21,fill:"#fff","text-anchor":"end"},g,C.n);
    if(C.sub)el("text",{x:424,y:y+39,"font-size":15,fill:"#fff","text-anchor":"end",opacity:.95},g,C.sub);
    if(win){
      el("text",{x:477,y:y+29,"font-size":26,fill:"#fff","text-anchor":"middle"},g,f2(c.pct)+"%");
      el("text",{x:497,y:y+44,"font-size":10,fill:"#fff","font-style":"italic","text-anchor":"middle",opacity:.85},g,LAB.won);
    }else{
      el("text",{x:476,y:y+33,"font-size":23,fill:C.txt||bar,"text-anchor":"middle"},g,f2(c.pct)+"%");
    }
    y+=h+(idx+1<rows.length&&!LG&&wins[rows[idx+1].code]?5:7);
  });""",
    """    LEGEND_ROW(g,C,c,y,rows,idx===0&&!LG);
    y+=(rows.length>12?23:27)+2.5;
  });
  if(KEYS){
    y+=(rows.length?14:12);
    KEYS.keys.filter(([k])=>USED(k)).forEach(([col,lab])=>{el("rect",{x:93,y:y-11,width:15,height:13,fill:col,stroke:"#616161","stroke-width":.8},g);el("text",{x:115,y:y,"font-size":13.5,fill:"#616161"},g,lab);y+=19;});
  }
  ANCHOR_LEGEND(g);""")

sub("""      for(let i=0;i<7;i++){
        const x=93+i*46.2,w=43.5;
        el("rect",{x,y,width:w,height:9,fill:shade(c.code,i),opacity:(used[c.code]&&used[c.code][i])?1:.38},g);
        if(idx===0)el("text",{x:x+w/2,y:y-6,"font-size":14,"font-style":"italic",fill:"#616161","text-anchor":"middle"},g,BIN_LABEL[i]);
      }
      y+=15;""",
    """      for(let i=0;i<7;i++){
        const x=93+i*46.2,w=43.5;
        el("rect",{x,y,width:w,height:5.5,fill:shade(c.code,i),opacity:(used[c.code]&&used[c.code][i])?1:.38},g);
        if(idx===0)el("text",{x:x+w/2,y:y-4,"font-size":13,"font-style":"italic",fill:"#616161","text-anchor":"middle"},g,BIN_LABEL[i]);
      }
      y+=(N.cands.length>12?7:8.5);""")

sub("""  const LG=MODES[MODE].legend;                                   // leyenda propia para mapas de color explícito (coropletas)""",
    """  const LG0=MODES[MODE].legend;const LG=(LG0&&LG0.stops)?LG0:null;
  const KEYS=LG0&&LG0.keys?LG0:null;
  const USED=c=>[...document.querySelectorAll('#B .d,#B .dc')].some(e=>(e.getAttribute("fill")||"").toLowerCase()===c.toLowerCase());""")
sub("const rows=(LG&&LG.bars===false)?[]:N.cands;", "const rows=(LG0&&LG0.bars===false)?[]:N.cands;")
sub("""  el("text",{x:93,y:1266,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=1292;""",
    """  const Y0=(!(LG0&&LG0.bars===false)&&N.cands.length>12)?1008:N.cands.length>=8?1160:1266;
  el("text",{x:93,y:Y0,"font-size":19,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=Y0+22;""")

sub("""$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;""", """$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;$("#pie1").setAttribute("x",184);""")
sub("return out.slice(0,4);", "return out.slice(0,6);")
sub("const list=tilesNow(),xs=[1262,1316,1370,1424];",
    "const list=tilesNow(),xs=list.length>5?[1196,1248,1300,1352,1404,1456]:list.length>4?[1208,1262,1316,1370,1424]:[1262,1316,1370,1424];")
sub("    const sw=(t.length>6)?68:48,xx=xs[i];",
    "    const sw=(t.length>6)?68:48,xx=xs[i];")
sub("    if(t.length>5)tt.setAttribute(\"font-size\",15);",
    "    if(t.length>=5)tt.setAttribute(\"font-size\",12.5);")

tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(HERE, f"atlas_{YEAR}.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
