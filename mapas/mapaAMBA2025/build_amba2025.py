"""Atlas de diputados nacionales 2025 en el AMBA por circuito electoral (estilo Wikipedia 1999).
Votos: escrutinio provisorio por mesa de la DINE (datos.mininterior.gob.ar, elecciones_legislativas_2025.zip), agregados por circuito en agregar.py.
Geometria: circuitos CNE/INDEC (circuitos_electorales_AR, 2021). Los circuitos que la base subdivide con letras (0364A...) se juntan en el poligono del circuito de origen.
AMBA = Capital + 24 partidos del GBA + 16 partidos de la region metropolitana (Berisso, Brandsen, Campana, Canuelas, Ensenada, Escobar, Exaltacion de la Cruz,
General Las Heras, General Rodriguez, La Plata, Lujan, Marcos Paz, Pilar, Presidente Peron, San Vicente, Zarate)."""
import sys, os, re, json, math, collections, base64, io
import numpy as np, shapely
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
import pandas as pd
import geomamba

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
LOGOS = os.path.join(ROOT, "../logos")
TEMPLATE_SRC = os.path.join(ROOT, "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

# ---------------------------------------------------------------- proyeccion (equirrectangular con cos(lat) a 34,7 S)
KX = math.cos(math.radians(34.7))
LON0, LAT1 = -59.3775, -33.9233
S, X0, Y0 = 975.0, 548.0, 140.0


def proj(a):
    a = np.asarray(a, float).copy()
    a[:, 0] = (a[:, 0] - LON0) * KX * S + X0
    a[:, 1] = (LAT1 - a[:, 1]) * S + Y0
    return a


def ll(lon, lat):
    return ((lon - LON0) * KX * S + X0, (LAT1 - lat) * S + Y0)


def f2(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


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


# ---------------------------------------------------------------- datos
d, feats, target = geomamba.load()
POS = d[d.votos_tipo == "POSITIVO"].copy()

# circuito de la base sin poligono en la capa de la CNE: se usa el hueco que dejan sus vecinos de la misma seccion (inferido, con nota)
INFERRED = set()
_amba_secs0 = {("02", k[1]) for k in target if k[0] == "02"}
for _k3 in [k for k, t in target.items() if t is None]:
    _all = [proj_geom(g) for kk, g in feats.items() if kk[0] == "01" or (kk[0] == "02" and ("02", kk[1]) in _amba_secs0)]
    _U = unary_union([g.buffer(0.3) for g in _all])
    _holes = [Polygon(hh) for p in (_U.geoms if hasattr(_U, "geoms") else [_U]) for hh in p.interiors]
    _same = unary_union([proj_geom(g) for kk, g in feats.items() if kk[0] == "02" and kk[1] == _k3[1]])
    _c = [hh for hh in _holes if hh.buffer(1.5).intersects(_same)]
    if _c:
        _h = max(_c, key=lambda q: q.area); _p = np.array(_h.exterior.coords)
        _kk = ("02", _k3[1], _k3[2])
        feats[_kk] = Polygon(np.column_stack([LON0 + (_p[:, 0] - X0) / (KX * S), LAT1 - (_p[:, 1] - Y0) / S]))
        target[_k3] = _kk; INFERRED.add(_kk)


def bloc_of(n):
    n = n.replace("�", "O")
    if "FUERZA PATRIA" in n: return "FP"
    if "LA LIBERTAD AVANZA" in n: return "LLA"
    if "IZQUIERDA Y DE TRABAJADORES" in n: return "FIT"
    if n in ("CIUDADANOS UNIDOS", "ALIANZA PROVINCIAS UNIDAS"): return "PU"
    return None


def slug(n):
    n = n.replace("�", "o")
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")[:40]


POS["bloc"] = POS.agrupacion_nombre.map(bloc_of)
POS["code"] = [b if b else slug(n) for b, n in zip(POS.bloc, POS.agrupacion_nombre)]
LAB = {}
for c, n in zip(POS.code, POS.agrupacion_nombre):
    LAB.setdefault(c, n.replace("�", "Ó").title().replace("Alianza ", "").replace("Frente De", "Frente de"))
LAB.update(FP="Fuerza Patria", LLA="La Libertad Avanza", FIT="Frente de Izquierda y de Trabajadores - Unidad", PU="Provincias Unidas (Ciudadanos Unidos en Capital)")
BLOCS = ["FP", "LLA", "FIT", "PU"]
COLOR = dict(FP="#318ce7", LLA="#6f3fa0", FIT="#a31515", PU="#ff7f20")
DEFAULT_COL = "#9a9a9a"

# mesas: electores y escrutadas
M = d.drop_duplicates("mesa")[["mesa", "dist", "sec", "cir", "elec", "estado_final"]].copy()
M["ok"] = M.estado_final == "ESCRUTADO"
M["elok"] = np.where(M.ok, M.elec, 0)
KEY3 = ["dist", "sec", "cir"]
PDICT = collections.defaultdict(collections.Counter)
for (a, b, c, code), v in POS.groupby(KEY3 + ["code"]).v.sum().items():
    PDICT[(a, b, c)][code] += v
ODICT = {}
for (a, b, c, t), v in d[d.votos_tipo != "POSITIVO"].groupby(KEY3 + ["votos_tipo"]).v.sum().items():
    ODICT.setdefault((a, b, c), {})[t] = v
MG = M.groupby(KEY3).agg(mesas=("mesa", "size"), ok=("ok", "sum"), el=("elec", "sum"), elok=("elok", "sum")).to_dict("index")

# unidades = poligonos con los circuitos de la base que caen en cada uno
members = collections.defaultdict(list)
nopoly = []
for key3, t in target.items():
    (members[t] if t else nopoly).append(key3)
# poligonos del AMBA que la base provisoria no trae (circuitos sin mesas): se dibujan en beige
_amba_secs = {(k[0], k[1]) for k in target if k[0] == "02"}
for k in feats:
    if k[0] == "02" and ("02", k[1]) in _amba_secs and k not in members: members[k] = []
UKEYS = sorted(members)
part_of = d.drop_duplicates(["dist", "sec"]).set_index(["dist", "sec"]).part.to_dict()
sec_name = d.drop_duplicates(["dist", "sec"]).set_index(["dist", "sec"]).seccion_nombre.to_dict()


def feats_sec(k):
    return next(m[1] for m in members[k]) if members[k] else "001"


def agg_for(keys):
    P = collections.Counter(); bla = nul = imp = mesas = ok = 0; el = elok = 0
    for k in keys:
        P.update(PDICT.get(k, {}))
        o = ODICT.get(k, {})
        bla += o.get("EN BLANCO", 0); nul += o.get("NULO", 0); imp += o.get("IMPUGNADO", 0) + o.get("RECURRIDO", 0)
        g = MG.get(k)
        if g: mesas += g["mesas"]; ok += g["ok"]; el += g["el"]; elok += g["elok"]
    pos = sum(P.values())
    a = dict(P=dict(P), pos=pos, bla=bla, nul=nul, imp=imp, mesas=int(mesas), ok=int(ok), el=el, elok=elok)
    a["bloc"] = {b: P.get(b, 0) for b in BLOCS}
    a["E"] = pos + bla + nul + imp   # votantes de las mesas escrutadas
    return a


def fmt_n(v): return "{:,}".format(int(round(v))).replace(",", ".")
def fmt_p(v): return ("%.1f" % v).replace(".", ",")
GREY_N = "#8c8c8c"; BEIGE = "#e6dcc3"


def rec_from(a, note=None):
    D = a["pos"]
    if not a["ok"] or not D:
        return dict(lines=[], metrics=[["Mesas escrutadas", "%d de %d" % (a["ok"], a["mesas"])]], fill=BEIGE,
                    note=(note + " " if note else "") + "Sin mesas escrutadas en el recuento provisorio: queda sin dato.")
    P = a["P"]
    lines = [["P_" + c, int(x), round(100 * x / D, 2)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x > 0][:14]
    E = a["E"]
    if a["bla"]: lines.append(["P_BLA", int(a["bla"]), round(100 * a["bla"] / E, 2)])
    if a["nul"]: lines.append(["P_NUL", int(a["nul"]), round(100 * a["nul"] / E, 2)])
    met = []
    if a["elok"]: met.append(["Electores (mesas escrutadas)", fmt_n(a["elok"])])
    met.append(["Votantes", fmt_n(E)])
    if a["elok"]: met.append(["Participación", fmt_p(100 * E / a["elok"]) + " %"])
    met.append(["Votos positivos", fmt_n(D)])
    met.append(["Mesas escrutadas", "%d de %d" % (a["ok"], a["mesas"])])
    rec = {"lines": lines, "metrics": met}
    top = max(P, key=lambda c: P[c])
    if top in BLOCS: rec.update(w=top, q=round(100 * P[top] / D, 2))
    else: rec.update(fill=COLOR.get(top, GREY_N))
    if a["ok"] < a["mesas"]:
        note = ((note + " ") if note else "") + "%d mesas sin escrutar en el recuento provisorio." % (a["mesas"] - a["ok"])
    if note: rec["note"] = note
    return rec


# ---------------------------------------------------------------- geometria
G_raw = [proj_geom(feats[k]) for k in UKEYS]
try:
    G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.04))
except Exception as e:
    print("coverage_simplify fallo (%s): simplify por poligono" % e, file=sys.stderr)
    G = [g.simplify(0.04, preserve_topology=True) for g in G_raw]
PART = [part_of[("01", feats_sec(k))] if k[0] == "01" else part_of[(k[0], k[1])] for k in UKEYS]
PART = ["Ciudad de Buenos Aires" if p == "CABA" else p for p in PART]
disp, unit_an, unit_rec = {}, {}, {}
for i, k in enumerate(UKEYS):
    mem = members[k]
    a = agg_for(mem); unit_an[i] = a
    dist = k[0]
    if dist == "01":
        disp[i] = "Circuito %d · %s" % (int(k[2]), sec_name[(dist, mem[0][1])].title())
    else:
        disp[i] = "Circuito %s" % k[2].lstrip("0") + (" y subdivisiones" if len(mem) > 1 else "")
    note = None
    if not mem: note = "Circuito del mapa sin mesas en la base provisoria."
    if k in INFERRED: note = "Polígono inferido: el circuito no figura en la capa de polígonos de la CNE y se dibuja el hueco que dejan sus vecinos de la misma sección."
    if len(mem) > 1:
        note = "Suma %d circuitos de la base (%s): la base los subdivide con letras y el mapa solo tiene el polígono del circuito de origen." % (len(mem), ", ".join(sorted(m[2] for m in mem)))
    unit_rec[i] = rec_from(a, note)

# totales del AMBA: todos los circuitos de la base, tambien el que no tiene poligono
TOT = agg_for(list(target))
print("AMBA: positivos", TOT["pos"], "bloques", TOT["bloc"], "mesas", TOT["ok"], "/", TOT["mesas"], "sin poligono:", nopoly, file=sys.stderr)
PARTIDOS = sorted(set(PART))
part_an = {}
for p in PARTIDOS:
    keys = [m for i, k in enumerate(UKEYS) if PART[i] == p for m in members[k]]
    part_an[p] = agg_for(keys)
prov_rec = {p: rec_from(a, "Suma de los circuitos del partido.") for p, a in part_an.items()}


# ---------------------------------------------------------------- candidaturas, logos
CAND = {
    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], logo="FP"),
    "LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a2f85", txt="#5a2f85", logo="LLA"),
    "FIT": dict(n="Frente de Izquierda", sub="y de Trabajadores - Unidad", base=COLOR["FIT"], logo="FIT"),
    "PU": dict(n="Provincias Unidas", sub="Ciudadanos Unidos en Capital", base=COLOR["PU"], bar="#f06a0b", txt="#d9560a", logo="PU"),
    "OTR": dict(n="Otros", sub="Resto de las listas", base="#b3b3b3", bar="#a6a6a6", txt="#8f8f8f", logo="···"),
}
for c in LAB:
    CAND["P_" + c] = dict(n=LAB[c], base=COLOR.get(c, DEFAULT_COL), minor=True)
CAND["P_BLA"] = dict(n="En blanco", base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Nulos e impugnados", base="#b0b0b0", minor=True)


def _ar_svg(t):
    m = re.search(r'viewBox="([\d.\s-]+)"', t)
    if m:
        v = [float(x) for x in m.group(1).split()]
        return v[2] / v[3]
    w = re.search(r'\bwidth="([\d.]+)', t); h = re.search(r'\bheight="([\d.]+)', t)
    return float(w.group(1)) / float(h.group(1)) if w and h else 1.0


def _logo(fn, h=50):
    t = open(os.path.join(LOGOS, fn), encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    ar = _ar_svg(t)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


def _logo_raster(fn, px=360, h=50):
    from PIL import Image
    im = Image.open(os.path.join(LOGOS, fn)).convert("RGBA")
    ar = im.width / im.height
    k = px / max(im.size); im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


_lg = os.path.join(HERE, "logos_amba2025.py")
if os.path.exists(_lg): exec(open(_lg, encoding="utf8").read())

# ---------------------------------------------------------------- resultado de la region (suma de los circuitos de la base)
pos = TOT["pos"]
cands = sorted([{"code": b, "votes": int(TOT["bloc"][b]), "pct": round(100 * TOT["bloc"][b] / pos, 2)} for b in BLOCS], key=lambda c: -c["votes"])
otros = pos - sum(c["votes"] for c in cands)
cands.append({"code": "OTR", "votes": int(otros), "pct": round(100 * otros / pos, 2)})
slices = [{"code": c["code"], "v": c["votes"]} for c in cands[:-1]] + [{"fill": "#717274", "v": int(otros)}]
partp = round(100 * TOT["E"] / TOT["elok"], 2)
NAT_MET = [["Electores (mesas escrutadas)", fmt_n(TOT["elok"])], ["Votantes", fmt_n(TOT["E"])], ["Participación", fmt_p(partp) + " %"],
           ["Votos positivos", fmt_n(pos)], ["Votos en blanco", fmt_n(TOT["bla"])], ["Nulos e impugnados", fmt_n(TOT["nul"] + TOT["imp"])],
           ["Mesas escrutadas", "%s de %s" % (fmt_n(TOT["ok"]), fmt_n(TOT["mesas"]))]]

# ---------------------------------------------------------------- modos
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


NOTE = ("Fuente: escrutinio provisorio por mesa de diputados nacionales (26 oct. 2025), Dirección Nacional Electoral, datos.mininterior.gob.ar; "
        "porcentajes sobre votos positivos, agregados por circuito electoral. El resultado de la torta y las barras es la suma del AMBA (Capital + 40 partidos). "
        "No es el escrutinio definitivo: %d de %s mesas figuran sin escrutar. Geometría: circuitos CNE/INDEC de 2021; los circuitos que la base subdivide con letras "
        "se muestran con el polígono del circuito de origen (el circuito 548 de Gral. Las Heras no figura en la capa de polígonos: se dibuja el hueco que dejan sus vecinos, inferido). "
        "Provincias Unidas = «Alianza Provincias Unidas» en Buenos Aires y «Ciudadanos Unidos» en Capital." % (TOT["mesas"] - TOT["ok"], fmt_n(TOT["mesas"])))


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(UKEYS)):
        r = unit_rec[i]; a = unit_an[i]
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        if not a["ok"] or not a["pos"]: nr["fill"] = BEIGE
        else: nr["fill"] = cols[bin_of(fn(a), edges)]
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(fn(part_an[p]), edges)]
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False)


pct = lambda b: (lambda a: 100 * a["bloc"][b] / a["pos"])
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(UKEYS))], prov=prov_rec,
              national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET),
              legend=dict(keys=[[BEIGE, "Circuito sin mesas en la base provisoria"]]))]
for mid, tile, fn, base, edges, title in (
    ("fp", "FP", pct("FP"), COLOR["FP"], [0, 20, 30, 40, 50, 60, 70], "% Fuerza Patria"),
    ("lla", "LLA", pct("LLA"), COLOR["LLA"], [0, 20, 30, 40, 50, 60, 70], "% La Libertad Avanza"),
    ("fit", "FIT", pct("FIT"), COLOR["FIT"], [0, 3, 5, 8, 12, 18, 25], "% Frente de Izquierda - Unidad"),
    ("par", "PART.", lambda a: 100 * a["E"] / a["elok"], "#4a4a4a", [40, 55, 62, 66, 70, 74, 78], "Participación (mesas escrutadas)")):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, note=NOTE, units=un, prov=pv, national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=lg))

# ---------------------------------------------------------------- SVG
body = []
for i, g in enumerate(G):
    body.append('<path class="d" data-i="%d" d="%s"/>' % (i, geom_d(g)))
caba_idx = [i for i, k in enumerate(UKEYS) if k[0] == "01"]
for i in caba_idx:
    body.append('<path class="dc" data-i="%d" d="%s"/>' % (i, geom_d(shapely.simplify(G_raw[i], 0.01))))
PGEOM = {}
for p in PARTIDOS:
    u = unary_union([G_raw[i] for i in range(len(UKEYS)) if PART[i] == p])
    u = fill_slivers(u.buffer(0.7, join_style=2).buffer(-0.7, join_style=2))
    PGEOM[p] = u
    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(u.boundary)))


def bbox_of(idx):
    return shapely.total_bounds([G_raw[i] for i in idx])


def window(b, aspect, pad=0.07):
    x0, y0, x1, y1 = b
    ww, hh = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    if ww / hh < aspect: ww = hh * aspect
    else: hh = ww / aspect
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(mx - ww / 2, 2), round(my - hh / 2, 2), round(ww, 2), round(hh, 2)]


def idx_of(partidos):
    return [i for i in range(len(UKEYS)) if PART[i] in partidos]


CORE = ["Ciudad de Buenos Aires", "Vicente Lopez", "San Isidro", "San Fernando", "Tigre", "General San Martin", "Tres De Febrero", "Hurlingham", "Moron", "Ituzaingo",
        "San Miguel", "Jose C. Paz", "Malvinas Argentinas", "Lanus", "Avellaneda", "Lomas De Zamora", "Quilmes", "Almirante Brown", "Esteban Echeverria",
        "La Matanza", "Berazategui", "Florencio Varela", "Merlo", "Moreno", "Ezeiza"]
PARTIDOS_NORM = {re.sub(r"[^a-z]", "", p.lower()): p for p in PARTIDOS}
core_idx = [i for i in range(len(UKEYS)) if re.sub(r"[^a-z]", "", PART[i].lower()) in {re.sub(r"[^a-z]", "", c.lower()) for c in CORE}]
lp_idx = [i for i in range(len(UKEYS)) if re.sub(r"[^a-z]", "", PART[i].lower()) in ("laplata", "berisso", "ensenada")]
def win_ll(lon, lat, wlon, aspect):
    x, y = ll(lon, lat); w = wlon * KX * S; hh = w / aspect
    return [round(x - w / 2, 2), round(y - hh / 2, 2), round(w, 2), round(hh, 2)]


INSETS = [
    dict(id="caba", label="Ciudad de Buenos Aires", f=[70, 610, 440, 470], win=window(bbox_of(caba_idx), 440 / 470, 0.04), show=["dc"], sd=2.2, fit="meet"),
    dict(id="core", label="Conurbano y Capital", f=[1450, 140, 430, 420], win=win_ll(-58.50, -34.64, 0.36, 430 / 420), show=["d", "pb"], sd=1.5, sp=2.4),
    dict(id="lp", label="Gran La Plata", f=[1495, 640, 385, 300], win=win_ll(-57.955, -34.905, 0.13, 385 / 300), show=["d", "pb"], sd=1.8, sp=2.6),
]
# sin marcos de los recuadros sobre el mapa principal (distraen)
pv = []

# ---------------------------------------------------------------- dataset
ds = dict(
    slug="diputados_amba_2025", locale="es-AR", country="Argentina",
    title="Elecciones legislativas en el AMBA de", year="2025",
    labels=dict(pie1="Proporción sobre votos positivos", provinces=""),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="2025", subtitle="Por circuito · provisorio")},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp[i], p=PART[i], k="circuito") for i in range(len(UKEYS))],
)
json.dump(ds, open(os.path.join(HERE, "dataset_amba2025.json"), "w", encoding="utf8"), ensure_ascii=False)

tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 2025 · AMBA por circuito</title>")
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"', 'style="--v-d:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--v-mk:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub("#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}", "#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}")
# recuadros dirigidos por el dataset
i0 = tpl.index("const INSETS=["); i1 = tpl.index("];", i0) + 2
tpl = tpl[:i0] + "const INSETS=DATA.insets||[];" + tpl[i1:]
sub('<defs><clipPath id="mapclip"><path clip-rule="evenodd" d="M570 100h840v1540h-840z M570 300h80v185h-80z M570 545h79v159h-79z M1247 785h163v320h-163z M1247 1166h163v452h-163z M985 1200h200v320-200z"/></clipPath></defs>'.replace("v320-200z", "v320h-200z"),
    '<defs><clipPath id="mapclip"><path id="clippath" clip-rule="evenodd" d="M540 100h1380v1540h-1380z"/></clipPath></defs>')
sub("function drawInsets(){", """function clipHoles(){
  const R=[540,100,1920,1640];let d="M540 100h1380v1540h-1380z";
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
      el("image",{href:C.img,x:Math.max(3,4+(h*1.2-iw)/2),y:-(ih-h)/2,width:iw,height:ih,preserveAspectRatio:"xMidYMid meet"},cv);}
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
  const KEYS=LG0&&LG0.keys?LG0:null;""")
sub("if(LG&&LG.keys){", "if(KEYS){")
sub("LG.keys.forEach(", "KEYS.keys.forEach(")
sub("const rows=(LG&&LG.bars===false)?[]:N.cands;", "const rows=(LG0&&LG0.bars===false)?[]:N.cands;")
# pie sin segundo texto cuando no hay participacion
sub("""$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;""", """$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;$("#pie1").setAttribute("x",184);""")
# leyenda de 9 bloques: empieza mas arriba (bajo el mini de provincias) y con barras mas bajas
sub('''el("text",{x:93,y:1266,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=1292''',
    '''const MANY=N.cands.length>5,Y0=MANY?(N.cands.length>9?1008:1024):1266;
  el("text",{x:93,y:Y0,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=Y0+26;''')
sub("const h=50,win=idx===0&&!LG", "const h=MANY?(N.cands.length>10?35:42):50,k=h/50,win=idx===0&&!LG")
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
sub("return out.slice(0,4);", "return out.slice(0,5);")
sub("const list=tilesNow(),xs=[1262,1316,1370,1424];", "const list=tilesNow(),xs=tilesNow().length>4?[1208,1262,1316,1370,1424]:[1262,1316,1370,1424];")
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(HERE, "atlas_amba2025.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
