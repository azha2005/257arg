"""Atlas de diputados nacionales 2025 en el AMBA por radio censal 2022 (estilo Wikipedia 1999), con el metodo de Poblaciones / LN Data.
  python build_amba2025radios.py        -> atlas_amba2025radios.html      (variante idw: Poblaciones, 1/d^2 dentro del partido)
  python build_amba2025radios.py pob    -> atlas_amba2025radios_pob.html  (variante pob: poblacion/d^2 dentro del circuito)
Antes: geocodificar.py (puntos de los locales), radios_amba.py (radios, con geopandas) y asignar.py (reparto).
La parte del medio y la cola (candidaturas, modos, SVG, parches a la plantilla) se toman de ../mapaAMBA2025 (mid_amba.py y tail_amba.py)
con los reemplazos de PATCH: el atlas por circuito y este quedan iguales salvo la unidad."""
import sys, os, re, json, math, collections, base64, io, pickle, unicodedata
import numpy as np, shapely
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon, shape
import pandas as pd

VAR = sys.argv[1] if len(sys.argv) > 1 else "idw"
assert VAR in ("idw", "pob")
SUF = "" if VAR == "idw" else "_pob"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CIRC = os.path.join(ROOT, "mapaAMBA2025")
LOGOS = os.path.join(ROOT, "../logos")
TEMPLATE_SRC = os.path.join(ROOT, "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

# ---------------------------------------------------------------- proyeccion (la del atlas por circuito)
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
LAB = {c: AS["LAB"][c].title().replace("Alianza ", "").replace("Frente De", "Frente de") for c in PCATS}
LAB.update(FP="Fuerza Patria", LLA="La Libertad Avanza", FIT="Frente de Izquierda y de Trabajadores - Unidad", PU="Provincias Unidas (Ciudadanos Unidos en Capital)")
BLOCS = ["FP", "LLA", "FIT", "PU"]
# colores del atlas legislativo 2025 (paleta de los mapas presidenciales de la Wikipedia; PU naranja por pedido del usuario)
COLOR = dict(FP="#009ce4", LLA="#6c4c98", FIT="#f65058", PU="#FF682C")
DEFAULT_COL = "#9a9a9a"
GREY_N = "#8c8c8c"; BEIGE = "#e6dcc3"


def fmt_n(v): return "{:,}".format(int(round(v))).replace(",", ".")
def fmt_p(v): return ("%.1f" % v).replace(".", ",")


def agg_rows(rows):
    v = A[rows].sum(0) if len(np.shape(rows)) else A[rows]
    P = {c: float(v[ci[c]]) for c in PCATS if v[ci[c]] > 0}
    g = lambda c: float(v[ci[c]]) if c in ci else 0.0
    pos = sum(P.values())
    a = dict(P=P, pos=pos, bla=g("_BLA"), nul=g("_NUL"), imp=g("_IMP"), mesas=g("_MES"), ok=g("_MOK"), el=g("_ELOK"), elok=g("_ELOK"))
    a["bloc"] = {b: P.get(b, 0) for b in BLOCS}
    a["E"] = pos + a["bla"] + a["nul"] + a["imp"]
    return a


def rec_from(a, pob=None, note=None, unit=True):
    D = a["pos"]
    if D < 0.5:
        met = [["Población 2022", fmt_n(pob)]] if pob is not None else []
        return dict(lines=[], metrics=met, fill=BEIGE, note=(note + " " if note else "") + "Sin votos asignados por el método (ningún local cerca o menos de 1 voto).")
    P = a["P"]
    lines = [["P_" + c, int(round(x)), round(100 * x / D, 1)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x >= 0.5][:8 if unit else 14]
    E = a["E"]
    if a["bla"] >= 0.5: lines.append(["P_BLA", int(round(a["bla"])), round(100 * a["bla"] / E, 2)])
    if a["nul"] >= 0.5: lines.append(["P_NUL", int(round(a["nul"])), round(100 * a["nul"] / E, 2)])
    met = []
    if pob is not None: met.append(["Población 2022", fmt_n(pob)])
    est = " (estimados)" if unit else ""
    if a["elok"]: met.append(["Electores" + est, fmt_n(a["elok"])])
    met.append(["Votantes" + est, fmt_n(E)])
    if a["elok"]: met.append(["Participación", fmt_p(100 * E / a["elok"]) + " %"])
    met.append(["Votos positivos" + est, fmt_n(D)])
    if not unit: met.append(["Mesas escrutadas", "%s de %s" % (fmt_n(a["ok"]), fmt_n(a["mesas"]))])
    rec = {"lines": lines, "metrics": met}
    top = max(P, key=lambda c: P[c])
    if top in BLOCS: rec.update(w=top, q=round(100 * P[top] / D, 2))
    else: rec.update(fill=COLOR.get(top, GREY_N))
    if note: rec["note"] = note
    return rec


# ---------------------------------------------------------------- unidades = radios
R = json.load(open(os.path.join(HERE, "radios_amba2022.geojson"), encoding="utf8"))["features"]
assert [f["properties"]["COD_2022"] for f in R] == list(rp.COD_2022)
UKEYS = [("01" if f["properties"]["PROV"] == "02" else "02", f["properties"]["COD_2022"]) for f in R]
PART = ["Ciudad de Buenos Aires" if p == "02" else ascii_t(n) for p, n in zip(rp.PROV, rp.partido)]
POBR = rp.POB_TOT_P.fillna(0).to_numpy(float)
G_raw = [proj_geom(shape(f["geometry"])) for f in R]
try:
    G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.04))
except Exception as e:
    print("coverage_simplify fallo (%s): simplify por poligono" % e, file=sys.stderr)
    G = [g.simplify(0.04, preserve_topology=True) for g in G_raw]
disp, unit_an, unit_rec = {}, {}, {}
for i, k in enumerate(UKEYS):
    a = agg_rows(i); unit_an[i] = a
    c = k[1]
    disp[i] = "Radio %s-%s-%s" % (c[2:5], c[5:7], c[7:9]) + (" · Comuna %d" % (int(c[2:5]) // 7) if k[0] == "01" else "")
    unit_rec[i] = rec_from(a, POBR[i])
    a["ok"] = 1 if a["pos"] >= 0.5 else 0   # los modos de coropleta piden «ok» y «pos»
TOT = agg_rows(np.arange(len(UKEYS)))
PARTIDOS = sorted(set(PART))
part_an = {p: agg_rows(np.array([i for i in range(len(UKEYS)) if PART[i] == p])) for p in PARTIDOS}
prov_rec = {p: rec_from(a, None, "Suma de los radios del partido (= escrutinio provisorio del partido).", unit=False) for p, a in part_an.items()}
WIN = collections.Counter(r.get("w") for r in unit_rec.values() if r.get("w"))
print(VAR, "radios:", len(UKEYS), "ganadores:", dict(WIN), "beige:", sum(1 for r in unit_rec.values() if r.get("fill") == BEIGE),
      "AMBA positivos", round(TOT["pos"]), file=sys.stderr)
LEG = [b for b in BLOCS if WIN.get(b)]   # regla 3: solo los que ganan algun radio

# ---------------------------------------------------------------- parte del medio y cola del atlas por circuito, con reemplazos
def load_part(fn, patches):
    t = open(os.path.join(CIRC, fn), encoding="utf8").read()
    for old, new in patches:
        assert t.count(old) == 1, (fn, old[:60], t.count(old))
        t = t.replace(old, new)
    return t


NOTE = ("Fuente: escrutinio provisorio por mesa de diputados nacionales (26 oct. 2025), Dirección Nacional Electoral; locales de votación de la misma base, "
        "ubicados con los padrones oficiales de escuelas (DGCyE de la Provincia y Ministerio de Educación de la Ciudad), georef y La Nación 2021. "
        + ("Cada local reparte sus votos entre los radios censales 2022 de su partido (comuna en Capital) con peso 1/distancia² al centroide del radio "
           "(método de Poblaciones / LN Data); los radios con menos de 1 voto quedan en 0. " if VAR == "idw" else
           "Cada local reparte sus votos entre los radios censales 2022 de su circuito con peso población 2022 / distancia² al centroide; los radios con menos de 1 voto quedan en 0. ")
        + "Es una estimación: el voto no se registra por radio. La torta y las barras son la suma del AMBA (Capital + 40 partidos); los totales por partido son exactos. "
        "Radios: CONICET (Rodríguez), censo 2022. Porcentajes sobre votos positivos.")
MID = load_part("mid_amba.py", [
    ('    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], logo="FP"),', '    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], bar="#0089c9", logo="FP"),'),
    ('"LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a2f85", txt="#5a2f85", logo="LLA"),', '"LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a3f80", txt="#5a3f80", logo="LLA"),'),
    ('base=COLOR["FIT"], logo="FIT"),', 'base=COLOR["FIT"], bar="#d93840", txt="#d93840", logo="FIT"),'),
    ('# ---------------------------------------------------------------- resultado de la region (suma de los circuitos de la base)',
     'exec(open(os.path.join(HERE, "logos_radios.py"), encoding="utf8").read())\n# ---------------------------------------------------------------- resultado de la region'),
    ('for b in BLOCS], key=lambda c: -c["votes"])', 'for b in LEG], key=lambda c: -c["votes"])'),
    ('["Mesas escrutadas", "%s de %s" % (fmt_n(TOT["ok"]), fmt_n(TOT["mesas"]))]]', '["Mesas escrutadas", "%s de %s" % (fmt_n(TOT["ok"]), fmt_n(TOT["mesas"]))], ["Radios censales", fmt_n(len(UKEYS))]]'),
    ('legend=dict(keys=[[BEIGE, "Circuito sin mesas en la base provisoria"]]))]', 'legend=dict(keys=[[BEIGE, "Radio sin votos asignados"]]))]'),
    ('    ("par", "PART.", lambda a: 100 * a["E"] / a["elok"], "#4a4a4a", [40, 55, 62, 66, 70, 74, 78], "Participación (mesas escrutadas)")):',
     '    ("par", "PART.", lambda a: 100 * a["E"] / a["elok"], "#4a4a4a", [40, 55, 62, 66, 70, 74, 78], "Participación estimada")):'),
    ('slug="diputados_amba_2025"', 'slug="diputados_amba_2025_radios" + SUF'),
    ('sets={"1": dict(label="2025", subtitle="Por circuito · provisorio")},', 'sets={"1": dict(label="2025", subtitle=("Por radio censal · estimado" if VAR == "idw" else "Por radio · estimado (población)"))},'),
    ('territories=[dict(n=disp[i], p=PART[i], k="circuito") for i in range(len(UKEYS))],', 'territories=[dict(n=disp[i], p=PART[i], k="radio") for i in range(len(UKEYS))],'),
    ('json.dump(ds, open(os.path.join(HERE, "dataset_amba2025.json"), "w", encoding="utf8"), ensure_ascii=False)',
     'json.dump(ds, open(os.path.join(HERE, "dataset_amba2025radios%s.json" % SUF), "w", encoding="utf8"), ensure_ascii=False)'),
    # escala mas fina (pedido del usuario): por radio el ganador saca 41-58 % en el 90 % de los casos y la de 10 puntos dejaba dos tonos
    ('exterior=False, candidates=CAND,', 'exterior=False, candidates=CAND, bins=[42, 45, 47, 50, 55, 60], bin_labels=["<42%", "42%", "45%", "47%", "50%", "55%", "+60%"],'),
    ('("fp", "FP", pct("FP"), COLOR["FP"], [0, 20, 30, 40, 50, 60, 70], "% Fuerza Patria"),', '("fp", "FP", pct("FP"), COLOR["FP"], [0, 25, 32, 38, 44, 50, 56], "% Fuerza Patria"),'),
    ('("lla", "LLA", pct("LLA"), COLOR["LLA"], [0, 20, 30, 40, 50, 60, 70], "% La Libertad Avanza"),', '("lla", "LLA", pct("LLA"), COLOR["LLA"], [0, 25, 32, 38, 44, 50, 56], "% La Libertad Avanza"),'),
    # comunas de Capital como divisores, igual que los partidos (pedido del usuario)
    ("""    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(u.boundary)))""",
     """    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(u.boundary)))\n"""
     """for _c in sorted({int(x) for x in rp.comuna.dropna()}):\n"""
     """    _u = unary_union([G_raw[i] for i in range(len(UKEYS)) if UKEYS[i][0] == "01" and int(UKEYS[i][1][2:5]) // 7 == _c])\n"""
     """    _u = fill_slivers(_u.buffer(0.3, join_style=2).buffer(-0.3, join_style=2))\n"""
     """    body.append('<path class="pb" data-prov="Ciudad de Buenos Aires" d="%s"/>' % line_d(_u.boundary))"""),
    # bordes de radio finos: con 1,5 px los radios chicos del conurbano quedaban blancos
    ('show=["dc"], sd=2.2, fit="meet")', 'show=["dc", "pb"], sd=0.25, sp=1.8, fit="meet")'),
    ('show=["d", "pb"], sd=1.5, sp=2.4)', 'show=["d", "pb"], sd=0.2, sp=2.4)'),
    ('show=["d", "pb"], sd=1.8, sp=2.6)', 'show=["d", "pb"], sd=0.25, sp=2.6)'),
    # los modos de coropleta no repiten las fichas: el navegador las copia del modo «ganó» (parche a la plantilla en TAIL)
    ('# ---------------------------------------------------------------- SVG',
     'for _m in MODES[1:]:\n    _m["units"] = [{k: v for k, v in u.items() if k in ("fill", "w", "q")} for u in _m["units"]]\n# ---------------------------------------------------------------- SVG'),
])
MID = re.sub(r'\nNOTE = \(.*?\n\n', "\n\n", MID, count=1, flags=re.S)
TAIL = load_part("tail_amba.py", [
    ('sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 2025 · AMBA por circuito</title>")',
     'sub("<title>Atlas electoral</title>", "<title>Diputados 2025 · AMBA por radio</title>")\n'
     'sub("const MODES={};DATA.modes.forEach(m=>MODES[m.id]=m);", "const MODES={};DATA.modes.forEach(m=>MODES[m.id]=m);'
     'DATA.modes.slice(1).forEach(m=>m.units.forEach((u,i)=>{const g=DATA.modes[0].units[i];if(!u.lines){u.lines=g.lines;u.metrics=g.metrics;if(g.note)u.note=g.note;}}));")\n'
     'sub(\'mw.style.setProperty("--sd",(1.5/Z.k).toFixed(4)+"px");\', \'mw.style.setProperty("--sd",(0.3/Z.k).toFixed(4)+"px");\')'),
    ("--v-mk:inline;--sd:1.5px;", "--v-mk:inline;--sd:0.3px;"),
    ('out = os.path.join(HERE, "atlas_amba2025.html")', 'out = os.path.join(HERE, "atlas_amba2025radios%s.html" % SUF)'),
])
exec(MID)
exec(TAIL)
