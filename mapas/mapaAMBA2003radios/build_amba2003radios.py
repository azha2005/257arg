"""Atlas de las presidenciales 2003 en el AMBA por radio censal 2001 (estilo Wikipedia 1999).
  python build_amba2003radios.py        -> atlas_amba2003radios.html      (variante idw: escuelas 2025 dentro del circuito 2003, 1/d^2)
  python build_amba2003radios.py pob    -> atlas_amba2003radios_pob.html  (control: población 2001 dentro del circuito)
Antes: radios_amba2001.py (radios, con geopandas) y asignar.py (reparto).
Proyección, recuadros y parches a la plantilla: los del atlas AMBA 2025 (cola tomada de ../mapaAMBA2025/tail_amba.py con reemplazos)."""
import sys, os, re, json, math, collections, base64, io, pickle, unicodedata
import numpy as np, shapely
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon, shape

VAR = sys.argv[1] if len(sys.argv) > 1 else "idw"
assert VAR in ("idw", "pob")
SUF = "" if VAR == "idw" else "_pob"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CIRC = os.path.join(ROOT, "mapaAMBA2025")
LOGOS = os.path.join(ROOT, "../logos")
TEMPLATE_SRC = os.path.join(ROOT, "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

# ---------------------------------------------------------------- proyección (la del atlas AMBA 2025)
KX = math.cos(math.radians(34.7))
LON0, LAT1 = -59.3775, -33.9233
S, X0, Y0 = 975.0, 548.0, 140.0


def proj(a):
    a = np.asarray(a, float).copy()
    a[:, 0] = (a[:, 0] - LON0) * KX * S + X0
    a[:, 1] = (LAT1 - a[:, 1]) * S + Y0
    return a


def ll(lon, lat): return ((lon - LON0) * KX * S + X0, (LAT1 - lat) * S + Y0)
def f2(x): return ("%.2f" % x).rstrip("0").rstrip(".")


def ring_d(c):
    pts = list(c.coords)
    return "M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts[:-1]) + "Z"


def geom_d(g):
    if g.is_empty: return ""
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type != "Polygon": continue
        out.append(ring_d(p.exterior))
        for h in p.interiors: out.append(ring_d(h))
    return "".join(out)


def line_d(g):
    out = []
    for l in (g.geoms if hasattr(g, "geoms") else [g]):
        pts = list(l.coords)
        if len(pts) < 2: continue
        out.append("M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts))
    return "".join(out)


def fill_slivers(g, amax=6.0):
    gs = [q for q in (g.geoms if hasattr(g, "geoms") else [g]) if q.geom_type == "Polygon"]
    out = [Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area >= amax]) for q in gs]
    return out[0] if len(out) == 1 else MultiPolygon(out)


def proj_geom(g):
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type != "Polygon": continue
        out.append(Polygon(proj(np.array(p.exterior.coords)), [proj(np.array(i.coords)) for i in p.interiors]))
    g2 = shapely.make_valid(MultiPolygon(out)) if out else Polygon()
    if g2.geom_type == "GeometryCollection":
        ps = [q for q in g2.geoms if q.geom_type in ("Polygon", "MultiPolygon")]
        g2 = unary_union(ps) if ps else Polygon()
    return g2


def ascii_t(s): return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()


# ---------------------------------------------------------------- datos: reparto por radio (asignar.py)
AS = pickle.load(open(os.path.join(HERE, "asignacion_%s.pkl" % VAR), "rb"))
A, CATS, rp = AS["A"], AS["CATS"], AS["radios"]
ci = {c: i for i, c in enumerate(CATS)}
PCATS = [c for c in CATS if not c.startswith("_")]
# tabla nacional de la Wikipedia (fórmula: candidato a presidente y fuerza)
NAMES = dict(M=("Carlos Menem", "Frente por la Lealtad"), K=("Néstor Kirchner", "Frente para la Victoria"),
             L=("Ricardo López Murphy", "Mov. Federal Recrear"), R=("Adolfo Rodríguez Saá", "Frente Movimiento Popular"),
             C=("Elisa Carrió", "Arg. x una Rep. de Iguales"), MOREAU=("Leopoldo Moreau", "Unión Cívica Radical"),
             WALSH=("Patricia Walsh", "Izquierda Unida"), BRAVO=("Alfredo Bravo", "Partido Socialista"), ALTAMIRA=("Jorge Altamira", "Partido Obrero"),
             VENTURINO=("Enrique Venturino", "Confederación Federalista Independiente"), SULLINGS=("Guillermo Sullings", "Partido Humanista"),
             ARCAGNI=("José Carlos Arcagni", "Unión Popular"), MAZZITELLI=("Mario Mazzitelli", "Partido Socialista Auténtico"),
             ZAFFORE=("Carlos Zaffore", "Movimiento de Integración y Desarrollo"), HERRERA=("Manuel Herrera", "Partido Demócrata Cristiano"),
             BREIDE=("Gustavo Breide Obeid", "Partido Popular de la Reconstrucción"), MUSSA=("Juan Ricardo Mussa", "Confederación para el Desarrollo"),
             TERAN=("Ricardo Terán", "Movimiento Socialista de los Trabajadores"))
LAB = {c: "%s (%s)" % NAMES[c] for c in PCATS}
BLOCS = ["M", "K", "L", "R", "C"]
# paleta del mapa presidencial 2003 de la Wikipedia, la misma de las legislativas 2003-2005 del proyecto
COLOR = dict(M="#1c5ece", K="#50ade6", L="#f4ce00", R="#1aff98", C="#74b744")
DEFAULT_COL = "#9a9a9a"
GREY_N = "#8c8c8c"; BEIGE = "#e6dcc3"


def fmt_n(v): return "{:,}".format(int(round(v))).replace(",", ".")
def fmt_p(v): return ("%.1f" % v).replace(".", ",")


def agg_rows(rows):
    v = A[rows].sum(0) if len(np.shape(rows)) else A[rows]
    P = {c: float(v[ci[c]]) for c in PCATS if v[ci[c]] > 0}
    g = lambda c: float(v[ci[c]]) if c in ci else 0.0
    pos = sum(P.values())
    a = dict(P=P, pos=pos, bla=g("_BLA"), nul=g("_NUL"), imp=0.0, mesas=g("_MES"), ok=g("_MOK"), el=g("_ELOK"), elok=g("_ELOK"))
    a["bloc"] = {b: P.get(b, 0) for b in BLOCS}
    a["E"] = pos + a["bla"] + a["nul"]
    return a


def rec_from(a, pob=None, note=None, unit=True):
    D = a["pos"]
    if D < 0.5:
        met = [["Población 2001", fmt_n(pob)]] if pob is not None else []
        return dict(lines=[], metrics=met, fill=BEIGE, note=(note + " " if note else "") + "Sin votos asignados por el método.")
    P = a["P"]
    lines = [["P_" + c, int(round(x)), round(100 * x / D, 1)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x >= 0.5][:8 if unit else 14]
    E = a["E"]
    if a["bla"] >= 0.5: lines.append(["P_BLA", int(round(a["bla"])), round(100 * a["bla"] / E, 2)])
    if a["nul"] >= 0.5: lines.append(["P_NUL", int(round(a["nul"])), round(100 * a["nul"] / E, 2)])
    met = []
    if pob is not None: met.append(["Población 2001", fmt_n(pob)])
    est = " (estimados)" if unit else ""
    if a["elok"]: met.append(["Electores" + est, fmt_n(a["elok"])])
    met.append(["Votantes" + est, fmt_n(E)])
    if a["elok"]: met.append(["Participación", fmt_p(100 * E / a["elok"]) + " %"])
    met.append(["Votos positivos" + est, fmt_n(D)])
    if not unit: met.append(["Mesas con votos", "%s de %s" % (fmt_n(a["ok"]), fmt_n(a["mesas"]))])
    rec = {"lines": lines, "metrics": met}
    top = max(P, key=lambda c: P[c])
    if top in BLOCS: rec.update(w=top, q=round(100 * P[top] / D, 2))
    else: rec.update(fill=COLOR.get(top, GREY_N))
    if note: rec["note"] = note
    return rec


# ---------------------------------------------------------------- unidades = radios 2001
R = json.load(open(os.path.join(HERE, "radios_amba2001.geojson"), encoding="utf8"))["features"]
assert [f["properties"]["COD_2001"] for f in R] == list(rp.COD_2001)
UKEYS = [("01" if f["properties"]["PROV"] == "02" else "02", f["properties"]["COD_2001"]) for f in R]
PART = ["Ciudad de Buenos Aires" if p == "02" else ascii_t(n) for p, n in zip(rp.PROV, rp.partido)]
CIRCUNS = AS["circuns"]
POBR = rp.POB_TOT.fillna(0).to_numpy(float)
G_raw = [proj_geom(shape(f["geometry"])) for f in R]
try:
    G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.04))
except Exception as e:
    print("coverage_simplify falló (%s): simplify por polígono" % e, file=sys.stderr)
    G = [g.simplify(0.04, preserve_topology=True) for g in G_raw]
disp, unit_an, unit_rec = {}, {}, {}
for i, k in enumerate(UKEYS):
    a = agg_rows(i); unit_an[i] = a
    c = k[1]
    disp[i] = "Radio %s-%s-%s" % (c[2:5], c[5:7], c[7:9]) + (" · %s" % CIRCUNS[rp.unit[i][1]] if k[0] == "01" else "")
    unit_rec[i] = rec_from(a, POBR[i])
    a["ok"] = 1 if a["pos"] >= 0.5 else 0
TOT = agg_rows(np.arange(len(UKEYS)))
PARTIDOS = sorted(set(PART))
part_an = {p: agg_rows(np.array([i for i in range(len(UKEYS)) if PART[i] == p])) for p in PARTIDOS}
prov_rec = {p: rec_from(a, None, "Suma de los radios del partido (= votos de PolAr en el partido).", unit=False) for p, a in part_an.items()}
WIN = collections.Counter(r.get("w") for r in unit_rec.values() if r.get("w"))
print(VAR, "radios:", len(UKEYS), "ganadores:", dict(WIN), "beige:", sum(1 for r in unit_rec.values() if r.get("fill") == BEIGE),
      "AMBA positivos", round(TOT["pos"]), {b: round(100 * TOT["bloc"][b] / TOT["pos"], 2) for b in BLOCS}, file=sys.stderr)
LEG = [b for b in BLOCS if WIN.get(b)]   # regla 3: solo los que ganan algún radio

# ---------------------------------------------------------------- candidaturas, logos (bloques del mapa presidencial 2003 de la Wikipedia, CC0)
BLK = dict(M="menem", K="fpv03", L="recrear", R="mnp", C="ari")
CAND = {b: dict(n=NAMES[b][0], sub=NAMES[b][1], base=COLOR[b]) for b in BLOCS}
CAND["L"].update(bar="#e8c000", txt="#a88a00")
CAND["R"].update(bar="#12d985", txt="#0f9e62")
CAND["C"].update(txt="#5a9433")


# rampas propias de los 7 tonos del modo «Ganó» (parche a shade() en la cola): con el .25 de la plantilla los oscuros de Menem y
# Kirchner terminaban en el mismo azul marino. Kirchner se queda en celestes y azul acero; los demás se oscurecen hasta .55.
def _hx(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def _rgb(c): return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)
def _mixw(h, t): return _rgb([c + (255 - c) * t for c in _hx(h)])
def _mulc(h, k): return _rgb([c * k for c in _hx(h)])


for b in BLOCS:
    CAND[b]["ramp"] = [_mixw(COLOR[b], .15), COLOR[b]] + [_mulc(COLOR[b], k) for k in (.9, .8, .7, .62, .55)]
CAND["K"]["ramp"] = [_mixw(COLOR["K"], .45), _mixw(COLOR["K"], .3), _mixw(COLOR["K"], .15), COLOR["K"]] + [_mulc(COLOR["K"], k) for k in (.9, .8, .72)]
CAND["OTR"] = dict(n="Otros", sub="Resto de las candidaturas", base="#b3b3b3", bar="#a6a6a6", txt="#8f8f8f", logo="···")
for c in PCATS:
    CAND["P_" + c] = dict(n=LAB[c], base=COLOR.get(c, DEFAULT_COL), minor=True)
CAND["P_BLA"] = dict(n="En blanco", base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Nulos", base="#b0b0b0", minor=True)


def _logo_raster(fn, h=50):
    from PIL import Image
    im = Image.open(fn).convert("RGBA")
    # el recorte del mapa de la Wikipedia arrastra a veces el comienzo del nombre (MNP: una «A» y una «F» a la derecha):
    # se corta en el primer hueco transparente de 10 columnas o más después del emblema
    col = (np.array(im)[..., 3] > 40).any(0)
    xs = np.flatnonzero(col)
    if len(xs):
        gaps = np.flatnonzero(np.diff(xs) >= 10)
        if len(gaps): im = im.crop((0, 0, int(xs[gaps[0]]) + 3, im.height))
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    ar = im.width / im.height
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


for b, f in BLK.items():
    CAND[b].update(_logo_raster(os.path.join(LOGOS, "bloques_presidenciales", f + ".png")))

# ---------------------------------------------------------------- resultado de la región
pos = TOT["pos"]
cands = sorted([{"code": b, "votes": int(TOT["bloc"][b]), "pct": round(100 * TOT["bloc"][b] / pos, 2)} for b in LEG], key=lambda c: -c["votes"])
otros = pos - sum(c["votes"] for c in cands)
cands.append({"code": "OTR", "votes": int(otros), "pct": round(100 * otros / pos, 2)})
slices = [{"code": c["code"], "v": c["votes"]} for c in cands[:-1]] + [{"fill": "#717274", "v": int(otros)}]
partp = round(100 * TOT["E"] / TOT["elok"], 2)
NAT_MET = [["Electores (mesas con votos)", fmt_n(TOT["elok"])], ["Votantes", fmt_n(TOT["E"])], ["Participación", fmt_p(partp) + " %"],
           ["Votos positivos", fmt_n(pos)], ["Votos en blanco", fmt_n(TOT["bla"])], ["Votos nulos", fmt_n(TOT["nul"])],
           ["Mesas con votos", "%s de %s" % (fmt_n(TOT["ok"]), fmt_n(TOT["mesas"]))], ["Radios censales 2001", fmt_n(len(UKEYS))]]


# ---------------------------------------------------------------- modos
def mix(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(255 + (c[k] - 255) * t) for k in range(3))


def dark(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(c[k] * (1 - t)) for k in range(3))


def stops_for(base, edges):
    # de casi blanco al color del candidato y de ahí más oscuro: los colores de 2003 son claros y la rampa hasta el color quedaba pálida
    n = len(edges); h = n // 2
    cols = [mix(base, 0.12 + 0.88 * i / h) for i in range(h)] + [dark(base, 0.55 * j / (n - 1 - h)) for j in range(n - h)]
    lab = ["%d%%" % e for e in edges[:-1]] + ["+%d%%" % edges[-1]]
    return cols, lab


def bin_of(p, edges):
    i = 0
    while i + 1 < len(edges) and p >= edges[i + 1]: i += 1
    return i


C = AS["ctrl"]
NOTE = ("Fuente: elección presidencial del 27 abr. 2003 por mesa, PolAr (Atlas Electoral de Andy Tow); circuitos de 2003 del aporte del usuario (proyección inferida). "
        + ("No hay registro de en qué escuela votó cada mesa en 2003: cada circuito reparte sus votos entre las escuelas de 2025 que caen dentro de él "
           "(locales de la DINE 2025 ubicados con los padrones de escuelas), según sus electores de 2025, y cada escuela entre los radios censales 2001 "
           "de su partido (circunscripción en Capital) con peso 1/distancia² (método de Poblaciones / LN Data). %d circuitos sin escuela usan su punto interior. "
           % C["circuitos_sin_escuela"] if VAR == "idw" else
           "Control sin locales: cada circuito reparte sus votos entre los radios censales 2001 que caen en él, en proporción a su población. ")
        + "Es una estimación: el voto no se registra por radio y se supone que en 2003 se votaba en las mismas escuelas que en 2025. "
        "Los totales por circuito, partido y circunscripción son exactos. Radios: CONICET (Rodríguez), censo 2001. Porcentajes sobre votos positivos.")


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(UKEYS)):
        r = unit_rec[i]; a = unit_an[i]
        nr = {k: v for k, v in r.items() if k in ("fill",)}
        nr["fill"] = BEIGE if not a["ok"] or not a["pos"] else cols[bin_of(fn(a), edges)]
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(fn(part_an[p]), edges)]
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False)


pct = lambda b: (lambda a: 100 * a["bloc"][b] / a["pos"])
NATL = dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET)
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(UKEYS))], prov=prov_rec, national=NATL,
              legend=dict(keys=[[BEIGE, "Radio sin votos asignados"]] if any(r.get("fill") == BEIGE for r in unit_rec.values()) else []))]
# cortes cerca de los percentiles 10-95 de cada candidato por radio, para que se noten los cambios
for mid, tile, b, edges in (("k", "KIRCH.", "K", [0, 17, 20, 24, 28, 32, 36]), ("m", "MENEM", "M", [0, 14, 16, 19, 22, 25, 28]),
                            ("l", "LÓPEZ", "L", [0, 8, 11, 15, 20, 27, 35]), ("c", "CARRIÓ", "C", [0, 10, 13, 16, 19, 21, 23])):
    un, pv_, lg = mode_choropleth(pct(b), COLOR[b], edges, "%% %s" % NAMES[b][0])
    MODES.append(dict(id=mid, tile=tile, note=NOTE, units=un, prov=pv_, national=NATL, legend=lg))

# ---------------------------------------------------------------- SVG
body = []
for i, g in enumerate(G):
    body.append('<path class="d" data-i="%d" d="%s"/>' % (i, geom_d(g)))
caba_idx = [i for i, k in enumerate(UKEYS) if k[0] == "01"]
for i in caba_idx:
    body.append('<path class="dc" data-i="%d" d="%s"/>' % (i, geom_d(shapely.simplify(G_raw[i], 0.01))))
for p in PARTIDOS:
    u = unary_union([G_raw[i] for i in range(len(UKEYS)) if PART[i] == p])
    u = fill_slivers(u.buffer(0.7, join_style=2).buffer(-0.7, join_style=2))
    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(u.boundary)))
# circunscripciones de Capital como divisores (las secciones electorales de 2003; las comunas son de 2005)
for _c in sorted(CIRCUNS):
    _u = unary_union([G_raw[i] for i in caba_idx if rp.unit[i][1] == _c])
    _u = fill_slivers(_u.buffer(0.3, join_style=2).buffer(-0.3, join_style=2))
    body.append('<path class="pb" data-prov="Ciudad de Buenos Aires" d="%s"/>' % line_d(_u.boundary))


def bbox_of(idx):
    return shapely.total_bounds([G_raw[i] for i in idx])


def window(b, aspect, pad=0.07):
    x0, y0, x1, y1 = b
    ww, hh = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    if ww / hh < aspect: ww = hh * aspect
    else: hh = ww / aspect
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(mx - ww / 2, 2), round(my - hh / 2, 2), round(ww, 2), round(hh, 2)]


def win_ll(lon, lat, wlon, aspect):
    x, y = ll(lon, lat); w = wlon * KX * S; hh = w / aspect
    return [round(x - w / 2, 2), round(y - hh / 2, 2), round(w, 2), round(hh, 2)]


INSETS = [
    # más arriba que en 2025: la leyenda tiene seis filas y arranca en y=1024
    dict(id="caba", label="Ciudad de Buenos Aires", f=[70, 545, 440, 440], win=window(bbox_of(caba_idx), 440 / 440, 0.04), show=["dc", "pb"], sd=0.25, sp=1.8, fit="meet"),
    dict(id="core", label="Conurbano y Capital", f=[1450, 140, 430, 420], win=win_ll(-58.50, -34.64, 0.36, 430 / 420), show=["d", "pb"], sd=0.2, sp=2.4),
    dict(id="lp", label="Gran La Plata", f=[1495, 640, 385, 300], win=win_ll(-57.955, -34.905, 0.13, 385 / 300), show=["d", "pb"], sd=0.25, sp=2.6),
]
pv = []
# los modos de coropleta no repiten las fichas: el navegador las copia del modo «ganó» (parche a la plantilla en la cola)
ds = dict(
    slug="presidenciales_amba_2003_radios" + SUF, locale="es-AR", country="Argentina",
    title="Elecciones presidenciales en el AMBA de", year="2003",
    labels=dict(pie1="Proporción sobre votos positivos", provinces=""),
    # escala fina, como el AMBA 2025 por radio: con cinco fuerzas el ganador saca entre 22 y 37 % en el 90 % de los radios (mediana 27)
    exterior=False, candidates=CAND, bins=[22, 24, 27, 30, 33, 37], bin_labels=["<22%", "22%", "24%", "27%", "30%", "33%", "+37%"],
    sets={"1": dict(label="2003", subtitle=("Por radio censal · estimado" if VAR == "idw" else "Por radio · estimado (población)"))},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp[i], p=PART[i], k="radio") for i in range(len(UKEYS))],
)
json.dump(ds, open(os.path.join(HERE, "dataset_amba2003radios%s.json" % SUF), "w", encoding="utf8"), ensure_ascii=False)


# ---------------------------------------------------------------- cola del atlas AMBA 2025 (plantilla y parches), con reemplazos
def load_part(fn, patches):
    t = open(os.path.join(CIRC, fn), encoding="utf8").read()
    for old, new in patches:
        assert t.count(old) == 1, (fn, old[:60], t.count(old))
        t = t.replace(old, new)
    return t


TAIL = load_part("tail_amba.py", [
    ('sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 2025 · AMBA por circuito</title>")',
     'sub("<title>Atlas electoral</title>", "<title>Presidenciales 2003 · AMBA por radio</title>")\n'
     'sub("const shade=(code,i)=>{const b=CAND[code].base;", "const shade=(code,i)=>{const b=CAND[code].base;if(CAND[code].ramp)return CAND[code].ramp[i];")\n'
     'sub("const MODES={};DATA.modes.forEach(m=>MODES[m.id]=m);", "const MODES={};DATA.modes.forEach(m=>MODES[m.id]=m);'
     'DATA.modes.slice(1).forEach(m=>m.units.forEach((u,i)=>{const g=DATA.modes[0].units[i];if(!u.lines){u.lines=g.lines;u.metrics=g.metrics;if(g.note)u.note=g.note;}}));")\n'
     'sub(\'mw.style.setProperty("--sd",(1.5/Z.k).toFixed(4)+"px");\', \'mw.style.setProperty("--sd",(0.3/Z.k).toFixed(4)+"px");\')'),
    ("--v-mk:inline;--sd:1.5px;", "--v-mk:inline;--sd:0.3px;"),
    ('out = os.path.join(HERE, "atlas_amba2025.html")', 'out = os.path.join(HERE, "atlas_amba2003radios%s.html" % SUF)'),
])
exec(TAIL)
