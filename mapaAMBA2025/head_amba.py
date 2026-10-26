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
LOGOS = os.path.join(ROOT, "logos_wikipedia")
TEMPLATE_SRC = os.path.join(ROOT, ".claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

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
