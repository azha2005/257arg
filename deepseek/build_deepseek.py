#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atlas ucrónico: elecciones presidenciales de Argentina de 1987.

Escenario de la ucronía «The Shining Austral Pearl» (Argentina gana la guerra de Malvinas).
Los totales provinciales salen del xlsx aportado por el usuario (`Argentina 1987.xlsx`);
el reparto por departamento es una ESTIMACIÓN a partir de la base de diputados de 1987
(y del presidential de 1989 para Tierra del Fuego), con IPF y redondeo controlado.

    python deepseek/build_deepseek.py

Salidas: deepseek/atlas_1987_ucronia.html + deepseek/dataset_1987_ucronia.json
No modifica ningún archivo existente del repositorio.
"""
import os as _os, sys as _sys
HERE = _os.path.dirname(_os.path.abspath(__file__))
ROOT = _os.path.dirname(HERE)
M1987 = _os.path.join(ROOT, "mapas", "mapa1987")
_sys.path[:0] = [_os.path.join(ROOT, "comun"), M1987]

import sys, os, re, json, csv, pickle, collections
import numpy as np
import shapely
from shapely.ops import unary_union
from scipy.optimize import linprog
import geom
from names import norm
import insets99
from outline_clean import clean_outline, clean_holes

LOGOS = os.path.join(ROOT, "logos")
TEMPLATE_SRC = os.path.join(ROOT, ".claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")
ERNESTO = os.path.join(ROOT, "datos/base8399/ernesto/1987_diputados/dpto_partidos.csv")
ERNESTO89 = os.path.join(ROOT, "datos/base8399/ernesto/1989_presidente/dpto_partidos.csv")
XLSX = os.path.join(HERE, "Argentina 1987.xlsx")
OUT = os.path.join(HERE, "atlas_1987_ucronia.html")
DATASET = os.path.join(HERE, "dataset_1987_ucronia.json")

# ---------------------------------------------------------------- proyección
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


def fill_slivers(g, amax=0.15):
    """Quita huecos interiores de menos de amax (rendijas entre polígonos, no lagos ni islas)."""
    from shapely.geometry import Polygon, MultiPolygon
    gs = g.geoms if hasattr(g, "geoms") else [g]
    out = [Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area >= amax]) for q in gs]
    return out[0] if len(out) == 1 else MultiPolygon(out)


# ---------------------------------------------------------------- geometría
PKL = os.path.join(M1987, "units_raw.pkl")
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
    if p != "Tierra del Fuego":
        prov_geom[p] = fill_slivers(prov_geom[p], 5.0 if p == "Capital Federal" else 0.15)
country = unary_union(list(prov_geom.values())).buffer(0.1).buffer(-0.1)
# cierra el entrante de la boca del Riachuelo, como el atlas de 1987
_cf, _ba = prov_geom["Capital Federal"], prov_geom["Buenos Aires"]
_win = shapely.box(_cf.bounds[0] - 3, _cf.bounds[1] - 3, _cf.bounds[2] + 3, _cf.bounds[3] + 3)
_n = unary_union([_ba, _cf]).buffer(0.5).buffer(-0.5).intersection(_win).difference(unary_union([_ba, _cf]))
_n = unary_union([q for q in (_n.geoms if hasattr(_n, "geoms") else [_n]) if q.area >= 0.1])
prov_geom["Capital Federal"] = unary_union([_cf, _n])
country = unary_union([country, _n])
prov_geom = {p: g.simplify(0.12) for p, g in prov_geom.items()}
country = country.simplify(0.12)
country = clean_outline(country)
prov_geom = {p: clean_holes(g, name=p) for p, g in prov_geom.items()}
prov_mini = {p: g.simplify(0.7) for p, g in prov_geom.items()}

_T = json.load(open(os.path.join(ROOT, ".claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "territories.json"), encoding="utf8"))["units"]
NICE = {(t["prov"], norm(t["name"])): t["name"] for t in _T}

# ---------------------------------------------------------------- base 1987 (perfil departamental)
ENT = {}
for r in csv.DictReader(open(ERNESTO, encoding="utf-8-sig")):
    e = ENT.setdefault((r["provincia"], r["departamento"]), dict(prov=r["provincia"], name=r["departamento"], P={}, pos=None, bla=None, nul=None, tot=None, el=None))
    v = float(r["votos"])
    v = int(v) if v == int(v) else v
    t = r["tipo_fila"]
    if t == "agrupacion":
        e["P"][r["codigo_partido"]] = e["P"].get(r["codigo_partido"], 0) + v
    elif t == "positivos":
        e["pos"] = v
    elif t == "blancos":
        e["bla"] = v
    elif t == "nulos":
        e["nul"] = v
    elif t == "total":
        e["tot"] = v
    elif t == "electores":
        e["el"] = v

# Correcciones documentadas en mapas/mapa1987/LEEME_1987.md (se repiten acá para no tocar aquel build):
IMPUTAR = {("Entre Ríos", "federacion"): "fje", ("Mendoza", "junin"): "pj", ("Chaco", "12 de octubre"): "pj", ("Corrientes", "curuzu cuatia"): "pj", ("Neuquén", "capital"): "mid",
           ("Jujuy", "rinconada"): "pj", ("La Pampa", "chalileo"): "pj", ("Chubut", "telsen"): "pj", ("Capital Federal", "5"): "ptp", ("Río Negro", "conesa"): "mid",
           ("Santa Fe", "constitucion"): "fren", ("San Juan", "caucete"): "fal"}
for k, c in IMPUTAR.items():
    e = ENT[k]
    gap = e["pos"] - sum(e["P"].values())
    assert gap > 0 and e["P"][c] <= 9, (k, gap, e["P"][c])
    e["P"][c] += gap
lp = ENT[("Buenos Aires", "La Plata")]
assert lp["P"]["fjren"] == 11919
lp["P"]["fjren"] += 99984
lp["pos"] += 99984
lp["tot"] += 99984


def fusionar(nuevo, base, texto):
    n, b = ENT.pop(nuevo), ENT[base]
    for c, x in n["P"].items():
        b["P"][c] = b["P"].get(c, 0) + x
    for k in ("pos", "bla", "nul", "tot", "el"):
        b[k] = (b[k] or 0) + (n[k] or 0)
    b["merged"] = texto


fusionar(("Entre Ríos", "islas de ibicuy"), ("Entre Ríos", "gualeguaychu"), "Incluye Islas del Ibicuy, que la base trae como departamento aparte y el mapa de 1980 incluye en Gualeguaychú.")
fusionar(("Jujuy", "palpala"), ("Jujuy", "capital"), "Incluye Palpalá, que la base trae como departamento aparte y el mapa de 1980 incluye en Capital.")
fusionar(("Buenos Aires", "Tres Lomas"), ("Buenos Aires", "Pellegrini"), "Incluye Tres Lomas, que la base trae como partido aparte y el mapa de 1980 incluye en Pellegrini.")

KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
EALIAS = {
    ("Chaco", "fray justo santa maria"): "Fray Justo Santa Maria de Oro", ("Chaco", "pte de la plaza"): "Presidente de la Plaza",
    ("Chubut", "f ameghino"): "Florentino Ameghino", ("Chubut", "paso de los indios"): "Paso de Indios",
    ("Corrientes", "beron de estrada"): "Beron de Astrada",
    ("Córdoba", "roque saenz pena"): "Presidente Roque Saenz Peña",
    ("Formosa", "capital"): "Formosa", ("Formosa", "pilaga"): "Pilagas",
    ("La Rioja", "facundo quiroga"): "General Juan F. Quiroga", ("La Rioja", "gral angel penaloza"): "General Angel V. Peñaloza",
    ("Mendoza", "lujan"): "Lujan de Cuyo",
    ("Misiones", "concepcion de la sierra"): "Concepcion", ("Misiones", "gral m belgrano"): "General Manuel Belgrano", ("Misiones", "l gran san martin"): "Libertador General San Martin",
    ("Neuquén", "capital"): "Confluencia", ("Neuquén", "catal lil"): "Catan-Lil",
    ("Salta", "capital"): "La Capital", ("Salta", "guachapas"): "Guachipas", ("Salta", "la candelaria"): "Candelaria", ("Salta", "san martin"): "General Jose de San Martin",
    ("San Juan", "nueve de julio"): "9 de Julio",
    ("San Luis", "capital"): "La Capital", ("San Luis", "pedernera"): "General Pedernera", ("San Luis", "pringles"): "Coronel Pringles", ("San Luis", "san martin"): "Libertador General San Martin",
    ("Santiago del Estero", "atimisqui"): "Atamisqui", ("Santiago del Estero", "gimenez"): "Jimenez", ("Santiago del Estero", "ibarra"): "Brigadier J. Felipe Ibarra",
    ("Santiago del Estero", "mariano moreno"): "Moreno", ("Santiago del Estero", "quebracho"): "Quebrachos", ("Santiago del Estero", "villa salavina"): "Salavina",
    ("Tucumán", "capital"): "San Miguel de Tucuman", ("Tucumán", "alberdi"): "Juan B. Alberdi",
    ("Buenos Aires", "coronel de marina l rosal"): "Coronel de Marina Leonardo Rosales", ("Buenos Aires", "saliquelo"): "Salliqueló",
    ("Chaco", "capital"): "San Fernando",
    ("Santiago del Estero", "capital"): "Capital",
    ("La Rioja", "penaloza"): "General Angel V. Peñaloza", ("La Rioja", "vera penaloza"): "Rosario Vera Peñaloza", ("La Rioja", "quiroga"): "General Juan F. Quiroga",
    ("La Rioja", "felipe varela"): "General Lavalle",
    ("La Pampa", "conhello"): "Conhelo", ("Salta", "r de la frontera"): "Rosario de la Frontera", ("Salta", "r de lerma"): "Rosario de Lerma",
}
EALIAS = {(p, norm(n)): v for (p, n), v in EALIAS.items()}
unit_src, unmatched = {}, []
for (prov, n), e in ENT.items():
    if prov == "Capital Federal":
        idx = KEY.get((prov, norm("Circ. %02d" % int(n))))
    else:
        nm = EALIAS.get((prov, norm(n)))
        idx = KEY.get((prov, norm(nm if nm else n)))
    if idx is None:
        unmatched.append((prov, n))
        continue
    assert idx not in unit_src, (prov, n, U[idx]["name"])
    unit_src[idx] = e
print("Ernesto sin polígono:", unmatched, file=sys.stderr)
assert not unmatched
print("polígonos sin Ernesto:", [(U[i]["prov"], U[i]["name"]) for i in range(len(U)) if i not in unit_src], file=sys.stderr)

# ---------------------------------------------------------------- xlsx del escenario
import openpyxl
wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["1987"]
PARTIES = ["PJ", "UCR", "MON", "PDS", "PI", "MID", "OTROS"]
X = {}
for row in ws.iter_rows(min_row=3, max_row=26, values_only=True):
    if not row[0]:
        continue
    prov = str(row[0]).strip()
    prov = {"Neuquen": "Neuquén", "Rio Negro": "Río Negro"}.get(prov, prov)
    votes = {p: int(row[i]) for p, i in zip(PARTIES, (1, 4, 7, 10, 13, 16, 19))}
    elect = {p: int(row[i]) for p, i in zip(PARTIES, (3, 6, 9, 12, 15, 18, 21))}
    total = int(row[22])
    assert sum(votes.values()) == total, (prov, votes, total)
    assert prov in PROVS, (prov, PROVS)
    X[prov] = dict(votes=votes, elect=elect, total=total)
assert len(X) == 24, len(X)
print("xlsx:", len(X), "provincias,", sum(v["total"] for v in X.values()), "positivos", file=sys.stderr)
print("electores:", {p: sum(v["elect"][p] for v in X.values()) for p in PARTIES}, file=sys.stderr)

# ---------------------------------------------------------------- bloques
PJ = {"pj", "fjren", "fjpart", "fj", "fje", "frejuli", "fpv"}
UCR = {"ucr", "ucrde", "ucrcon", "ucrvp"}
# MON = UCeDé y aliados + los partidos provinciales conservadores / de gobierno que
# la ucronía agrupa en el Movimiento de Opinión Nacional (PDP Mendoza, MPN, Bloquista,
# PRS, PAL de Corrientes, Acción Chubutense, etc.).
MON = {"ucd", "ucddpuc", "ucddem", "ducd", "apce", "ucdmpp", "adc", "ucdsr", "ucddp",
       "mpn", "ablo", "pd", "prs", "pri", "ach", "paldpml", "dpbb", "pca", "cp", "fed", "auton", "tyc", "mrf", "alpa", "ays", "mur"}
PI = {"pi"}
MID = {"mid", "midcr"}
BLOCS = ["MON", "UCR", "PJ", "PDS", "PI", "MID", "OTROS"]


def code2bloc(c):
    if c in PJ: return "PJ"
    if c in UCR: return "UCR"
    if c in MON: return "MON"
    if c in PI: return "PI"
    if c in MID: return "MID"
    return "OTROS"


# ---------------------------------------------------------------- perfil departamental (prior)
rows_by_prov = collections.defaultdict(list)
for i, u in enumerate(U):
    if u["prov"] == "Tierra del Fuego":
        continue
    if i in unit_src:
        rows_by_prov[u["prov"]].append(i)

prior = {}
for p, idxs in rows_by_prov.items():
    n = len(idxs)
    tot = np.array([unit_src[i]["pos"] if unit_src[i]["pos"] is not None else sum(unit_src[i]["P"].values()) for i in idxs], float)
    prof = {b: np.zeros(n) for b in BLOCS}
    for k, i in enumerate(idxs):
        for c, v in unit_src[i]["P"].items():
            prof[code2bloc(c)][k] += v
    M = np.zeros((n, len(BLOCS)))
    for j, b in enumerate(BLOCS):
        own = prof[b]
        share = own.sum() / tot.sum()
        # Las fuerzas chicas se mezclan con un perfil uniforme para que un pico local
        # (p. ej. el MID de Andalgala en 1987) no las haga ganar un departamento que
        # no ganan en el escenario. El PDS no tiene lista propia en la base de 1987:
        # se reparte uniforme dentro de cada provincia (ver LEEME).
        w = 0.85 if share >= 0.03 else 0.30
        if b == "PDS":
            w = 0.0
        if own.sum() > 0 and w > 0:
            M[:, j] = w * own / own.sum() + (1 - w) * tot / tot.sum()
        else:
            M[:, j] = tot / tot.sum()
    prior[p] = M

# Tierra del Fuego: no está en la base de 1987; se usa el presidential de 1989 como perfil
ENT89 = {}
for r in csv.DictReader(open(ERNESTO89, encoding="utf-8-sig")):
    if r["provincia"] != "Tierra del Fuego":
        continue
    e = ENT89.setdefault(r["departamento"], dict(P={}, pos=None))
    v = int(float(r["votos"]))
    if r["tipo_fila"] == "agrupacion":
        e["P"][r["codigo_partido"]] = e["P"].get(r["codigo_partido"], 0) + v
    elif r["tipo_fila"] == "positivos":
        e["pos"] = v
tdf_base_idx = [i for i, u in enumerate(U) if u["prov"] == "Tierra del Fuego" and u["name"] != "Islas Malvinas"]
tdf_base_names = [U[i]["name"] for i in tdf_base_idx]
assert sorted(n.lower() for n in tdf_base_names) == sorted(ENT89), (tdf_base_names, list(ENT89))
malv_idx = [i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"]
assert len(malv_idx) == 1, malv_idx
tdf_idx = tdf_base_idx + malv_idx          # Río Grande, Ushuaia, Islas Malvinas
tdf_names = tdf_base_names + ["Islas Malvinas"]


def ipf(M, r, c, iters=3000, tol=1e-12):
    M = M.copy()
    nz = c > 0
    M[:, ~nz] = 0
    for _ in range(iters):
        rs = M.sum(1)
        M *= (r / np.where(rs == 0, 1, rs))[:, None]
        cs = M.sum(0)
        M[:, nz] *= (c[nz] / cs[nz])[None, :]
        if np.abs(M.sum(1) - r).max() < tol and np.abs(M.sum(0) - c).max() < tol:
            break
    return M


def controlled_round(q, r, c):
    """Redondeo controlado: enteros con totales de fila y columna exactos y cada celda floor/ceil de q."""
    n, m = q.shape
    x = np.floor(q).astype(int)
    nz = c > 0
    x[:, ~nz] = 0
    R = r - x.sum(1)
    C = c - x.sum(0)
    assert (R >= 0).all() and (C >= 0).all(), (R, C)
    cols = [j for j in range(m) if nz[j]]
    k = len(cols)
    A = np.zeros((n + k, n * k))
    for i in range(n):
        A[i, i * k:(i + 1) * k] = 1
    for jj in range(k):
        A[n + jj, jj::k] = 1
    b = np.r_[R, C[cols]]
    frac = q[:, cols] - np.floor(q[:, cols])
    res = linprog((1 - frac).ravel(), A_eq=A, b_eq=b, bounds=(0, 1), method="highs")
    if not res.success:
        raise RuntimeError("redondeo controlado: %s" % res.message)
    y = np.round(res.x).astype(int).reshape(n, k)
    assert (y.sum(1) == R).all() and (y.sum(0) == C[cols]).all()
    for jj, j in enumerate(cols):
        x[:, j] += y[:, jj]
    return x


def largest_remainder(values, total):
    values = np.asarray(values, float)
    base = np.floor(values).astype(int)
    rem = int(total) - int(base.sum())
    order = np.argsort(-(values - base), kind="stable")
    base[order[:rem]] += 1
    return base


def fit_excluding_pds(M, r, c):
    """Ajusta las demás fuerzas y asigna al PDS una proporción uniforme del total de cada unidad.
    Así el PDS no hereda el perfil local de otras fuerzas (no tiene lista propia en 1987) y su
    coropleta queda plana dentro de cada provincia, como se documenta en el LEEME."""
    jp = BLOCS.index("PDS")
    other = [j for j in range(len(BLOCS)) if j != jp]
    pds = largest_remainder(r * (c[jp] / r.sum()), c[jp])
    assert (pds >= 0).all() and (pds <= r).all() and pds.sum() == c[jp]
    ro, co = r - pds, c[other]
    Mo = M[:, other]
    Mo = ipf(Mo, ro, co)
    Mo *= (ro / Mo.sum(1))[:, None]
    nz = co > 0
    Mo[:, nz] *= (co[nz] / Mo[:, nz].sum(0))[None, :]
    return controlled_round(Mo, ro, co), pds, other


EST = {}
for p, idxs in rows_by_prov.items():
    n = len(idxs)
    pos = np.array([unit_src[i]["pos"] if unit_src[i]["pos"] is not None else sum(unit_src[i]["P"].values()) for i in idxs], float)
    r = largest_remainder(pos * (X[p]["total"] / pos.sum()), X[p]["total"])
    c = np.array([X[p]["votes"][b] for b in BLOCS], int)
    x, pds, other = fit_excluding_pds(prior[p], r, c)
    for k, i in enumerate(idxs):
        EST[i] = {BLOCS[j]: int(x[k, jj]) for jj, j in enumerate(other)}
        EST[i]["PDS"] = int(pds[k])

# Tierra del Fuego: el xlsx trae el total provincial, sin las Malvinas. En la ucronía las
# islas votaron: se agregan como tercera unidad con un 5 % estimado del total provincial
# (656 votos), sin sumar votos fuera de ese total. El resto se reparte entre Río Grande y
# Ushuaia con el perfil del presidential de 1989.
base_pos = np.array([ENT89[n.lower()]["pos"] for n in tdf_base_names], float)
malv_votes = int(round(X["Tierra del Fuego"]["total"] * 0.05))
rest_total = X["Tierra del Fuego"]["total"] - malv_votes
r = np.r_[largest_remainder(base_pos * (rest_total / base_pos.sum()), rest_total), malv_votes]
c = np.array([X["Tierra del Fuego"]["votes"][b] for b in BLOCS], int)
M = np.zeros((len(tdf_idx), len(BLOCS)))
prov_own = collections.Counter()
for k, nme in enumerate(tdf_base_names):
    e = ENT89[nme.lower()]
    ownb = collections.Counter()
    for code, v in e["P"].items():
        b = "PJ" if code == "frejupo" else "UCR" if code == "ucr" else "MON" if code == "adc" else "MID" if code == "mid" else "OTROS"
        ownb[b] += v
        prov_own[b] += v
    for j, b in enumerate(BLOCS):
        M[k, j] = 0.85 * ownb[b] / e["pos"] + 0.15 * e["pos"] / base_pos.sum()
# Malvinas: sin perfil propio, se usa el promedio provincial de las otras dos unidades.
avg = np.array([0.85 * prov_own[b] / base_pos.sum() + 0.15 / len(tdf_idx) for b in BLOCS])
M[len(tdf_base_names)] = avg / avg.sum()
x, pds, other = fit_excluding_pds(M, r, c)
for k, i in enumerate(tdf_idx):
    EST[i] = {BLOCS[j]: int(x[k, jj]) for jj, j in enumerate(other)}
    EST[i]["PDS"] = int(pds[k])

# controles
for p, idxs in rows_by_prov.items():
    assert sum(sum(EST[i].values()) for i in idxs) == X[p]["total"]
    for b in BLOCS:
        assert sum(EST[i][b] for i in idxs) == X[p]["votes"][b], (p, b)
assert sum(sum(EST[i].values()) for i in tdf_idx) == X["Tierra del Fuego"]["total"]
for b in BLOCS:
    assert sum(EST[i][b] for i in tdf_idx) == X["Tierra del Fuego"]["votes"][b], b

# ---------------------------------------------------------------- fichas
GREY_N = "#8c8c8c"
GREY_T = "#cfcfcf"
MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def rec_from(e, note=None):
    D = sum(e.values())
    if not D:
        return {"fill": GREY_N, "lines": [], "metrics": [], "note": note}
    lines = [["P_" + b, int(v), round(100 * v / D, 2)] for b, v in sorted(e.items(), key=lambda kv: (-kv[1], BLOCS.index(kv[0]))) if v > 0]
    w = max(BLOCS, key=lambda b: (e[b], -BLOCS.index(b)))
    rec = dict(lines=lines, metrics=[["Votos positivos", fmt_n(D)]], w=w, q=round(100 * e[w] / D, 2))
    if note:
        rec["note"] = note
    return rec


unit_rec = {}
for i, u in enumerate(U):
    if i in EST:
        note = None
        if u["prov"] == "Tierra del Fuego":
            if u["name"] == "Islas Malvinas":
                note = ("Reparto estimado: en la ucronía las Malvinas votaron, pero el xlsx no trae su dato. "
                        "Se les asigna un 5 % del total provincial (656 votos) con el perfil promedio de Tierra del Fuego; "
                        "esos votos están incluidos en el total provincial y no se suman aparte.")
            else:
                note = ("Reparto estimado: la base de 1987 no incluye Tierra del Fuego; se usó el perfil del presidential de 1989, "
                        "escalado al total provincial del xlsx (que incluye las Malvinas).")
        unit_rec[i] = rec_from(EST[i], note)
    else:
        unit_rec[i] = dict(fill=GREY_N, lines=[], metrics=[], note="Sin dato.")

prov_est = {}
for i, e in EST.items():
    p = U[i]["prov"]
    t = prov_est.setdefault(p, {b: 0 for b in BLOCS})
    for b in BLOCS:
        t[b] += e[b]
prov_rec = {}
for p in PROVS:
    if p not in prov_est:
        prov_rec[p] = dict(fill=GREY_N, lines=[], metrics=[], note="Sin dato.")
        continue
    _el = " · ".join("%s %d" % (b, X[p]["elect"][b]) for b in BLOCS if X[p]["elect"][b])
    rec = rec_from(prov_est[p], "Totales provinciales del xlsx del escenario; reparto departamental estimado con la base de diputados de 1987. Electores del colegio: %s." % _el)
    rec["metrics"].append(["Electores", fmt_n(sum(X[p]["elect"].values()))])
    prov_rec[p] = rec

wins = collections.Counter()
for i, r in unit_rec.items():
    if r.get("w"):
        wins[r["w"]] += 1
print("ganadores por unidad:", dict(wins), file=sys.stderr)
print("ganadores por provincia:", dict(collections.Counter(prov_rec[p].get("w") for p in PROVS if prov_rec[p].get("w"))), file=sys.stderr)

# ---------------------------------------------------------------- candidaturas y resultado nacional
NAT_V = {b: sum(X[p]["votes"][b] for p in X) for b in BLOCS}
NAT_E = {b: sum(X[p]["elect"][b] for p in X) for b in BLOCS}
NAT_T = sum(NAT_V.values())


def _ar_svg(t):
    m = re.search(r'viewBox="([\d.\s-]+)"', t)
    if m:
        v = [float(x) for x in m.group(1).split()]
        return v[2] / v[3]
    w = re.search(r'\bwidth="([\d.]+)', t)
    h = re.search(r'\bheight="([\d.]+)', t)
    return float(w.group(1)) / float(h.group(1)) if w and h else 1.0


def _logo(fn, h=42):
    import base64
    t = open(os.path.join(LOGOS, fn), encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    ar = _ar_svg(t)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


def _logo_svg_path(path, px=360, h=42):
    """Logo SVG fuera de logos/: se rasteriza con el mismo motor que usa logos_al_ras
    para recortar el margen, así el navegador y el recorte ven lo mismo."""
    import base64, io
    import resvg_py
    from PIL import Image
    src = open(path, encoding="utf8").read()
    ar = _ar_svg(src)
    raw = bytes(resvg_py.svg_to_bytes(svg_string=src, width=px))
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


def _logo_raster(fn, px=360, h=42):
    import base64, io
    from PIL import Image
    im = Image.open(os.path.join(LOGOS, fn)).convert("RGBA")
    ar = im.width / im.height
    k = px / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


COLOR = {"MON": "#00838f", "UCR": "#e10019", "PJ": "#318ce7", "PDS": "#2e7d32",
         "PI": "#d10047", "MID": "#0f2b3d", "OTROS": "#9a9a9a"}
LABEL = {"MON": "Movimiento de Opinión Nacional", "UCR": "Unión Cívica Radical", "PJ": "Partido Justicialista",
         "PDS": "Partido por la Democracia Social", "PI": "Partido Intransigente",
         "MID": "Mov. de Integración y Desarrollo", "OTROS": "Otros"}
CAND = {
    "MON": dict(n="Movimiento de Opinión Nacional", sub="Frúgoli", base="#00838f", logo="MON"),
    "UCR": dict(n="Unión Cívica Radical", sub="Pugliese", base="#e10019", logo="UCR"),
    "PJ": dict(n="Partido Justicialista", sub="Matera", base="#318ce7", logo="PJ"),
    "PDS": dict(n="Partido por la Democracia Social", sub="Fracassi", base="#2e7d32", logo="PDS"),
    "PI": dict(n="Partido Intransigente", sub="Alende", base="#d10047", logo="PI"),
    "MID": dict(n="Mov. de Integración y Desarrollo", sub="Frigerio", base="#0f2b3d", logo="MID"),
    "OTROS": dict(n="Otros", base="#9a9a9a"),
}
CAND["MON"].update(_logo_svg_path(os.path.join(HERE, "logos", "Logo_Mon.svg")))
CAND["UCR"].update(_logo("Escudo_de_la_UCR.svg"))
CAND["PJ"].update(_logo("Flag_of_the_Justicialist_Party_(square_version).svg"))
CAND["PI"].update(_logo("Emblema_Partido_Intransigente.svg"))
CAND["MID"].update(_logo("Logo_MID.svg"))
for c in BLOCS:
    CAND["P_" + c] = dict(n=LABEL[c], base=COLOR[c], minor=True)
CAND["P_BLA"] = dict(n="En blanco", base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Anulados", base="#b0b0b0", minor=True)
CAND["P_OTR"] = dict(n="Otros", base="#9a9a9a", minor=True)

KEYS = []


def fmt_pct(v):
    return ("%.2f" % v).replace(".", ",")


# Leyenda: solo las fuerzas que ganan al menos una unidad (regla 3 del proyecto).
# Las demás van juntas en la torta como «Otros» y siguen en la ficha de cada unidad.
cands_order = [b for b in sorted(BLOCS, key=lambda b: -NAT_V[b]) if wins.get(b)]
nat_cands = [dict(code=b, votes=NAT_V[b], pct=round(100 * NAT_V[b] / NAT_T, 2)) for b in cands_order]
_rest = [b for b in BLOCS if b not in cands_order and NAT_V[b] > 0]
nat_slices = [dict(code=b, v=NAT_V[b]) for b in cands_order]
if _rest:
    nat_slices.append(dict(fill="#9a9a9a", v=sum(NAT_V[b] for b in _rest)))
nat_metrics = [["Votos positivos", fmt_n(NAT_T)], ["Electores", fmt_n(sum(NAT_E.values()))], ["Mayoría necesaria", "301"],
               ["PDS (Massera)", "%s (%s %%) · %d electores" % (fmt_n(NAT_V["PDS"]), fmt_pct(100 * NAT_V["PDS"] / NAT_T), NAT_E["PDS"])],
               ["PI / MID / otros", "%s / %s / %s" % (fmt_n(NAT_V["PI"]), fmt_n(NAT_V["MID"]), fmt_n(NAT_V["OTROS"]))]]
print("leyenda:", [(c["code"], c["votes"]) for c in nat_cands], file=sys.stderr)
print("torta otros:", [(k, nat_slices[-1]["v"]) for k in ("rest",)], file=sys.stderr)
print("nacional:", NAT_V, "electores:", NAT_E, file=sys.stderr)

NOTE = ("Ucronía: escenario «The Shining Austral Pearl» (Argentina gana la guerra de Malvinas), elección presidencial de 1987. "
        "Los totales provinciales y los electores salen del xlsx aportado por el usuario; el reparto por departamento es una ESTIMACIÓN "
        "a partir de la base de diputados de 1987 (perfil de cada fuerza) y del presidential de 1989 para Tierra del Fuego, ajustada por IPF "
        "a los totales provinciales y redondeada de forma controlada. No son votos observados por departamento. "
        "En la ucronía las Malvinas votaron: se agregan como tercera unidad de Tierra del Fuego con un 5 % estimado del total provincial "
        "(656 votos, perfil promedio provincial), sin sumar votos fuera de ese total. "
        "MON = Movimiento de Opinión Nacional (UCeDé y aliados + partidos provinciales conservadores: PDP de Mendoza, MPN, Bloquista, PRS, PAL de Corrientes, etc.). "
        "PDS = Partido por la Democracia Social, el partido de Massera; lleva a Fracassi. No tiene lista propia en la base de 1987 (la única PDS de la base es Formosa 1983, 257 votos), "
        "así que su voto se reparte uniformemente dentro de cada provincia: no gana departamentos, pero conserva los 20 electores que le asigna el xlsx. "
        "PJ, UCR, PI y MID son las listas de la base de 1987; «Otros» reúne al resto. "
        "El xlsx no trae inscriptos, blancos ni nulos: no se muestra participación. "
        "MON ganó el voto popular (31,59 %) y obtuvo 212 electores; ninguna fuerza alcanzó los 301 necesarios, así que el Colegio no eligió presidente en la primera votación. "
        "La imagen de la ucronía dice 5.291.282 votos para MON; el xlsx dice 5.391.282: se usa el xlsx y la diferencia de 100.000 queda anotada.")


def mix(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(255 + (c[k] - 255) * t) for k in range(3))


def stops_for(base, edges):
    ts = [0.12 + 0.88 * i / (len(edges) - 1) for i in range(len(edges))]
    lab = ["%d%%" % e for e in edges[:-1]] + ["+%d%%" % edges[-1]]
    return [mix(base, t) for t in ts], lab


def bin_of(p, edges):
    i = 0
    while i + 1 < len(edges) and p >= edges[i + 1]:
        i += 1
    return i


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(U)):
        r = unit_rec[i]
        e = EST.get(i)
        p = fn(e) if e else None
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(p, edges)] if p is not None else r.get("fill", GREY_N)
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        if p not in prov_est:
            prov[p] = dict(r)
            continue
        v = fn(prov_est[p])
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec,
              national=dict(cands=nat_cands, slices=nat_slices, partp=None, metrics=nat_metrics), legend=dict(keys=KEYS))]
for mid, tile, fn, base, edges, title in (
    ("mon", "MON", lambda e: 100 * e["MON"] / sum(e.values()), "#00838f", [0, 5, 10, 20, 30, 40, 50], "% MON (Movimiento de Opinión Nacional)"),
    ("ucr", "UCR", lambda e: 100 * e["UCR"] / sum(e.values()), "#e10019", [0, 10, 20, 30, 40, 50, 60], "% UCR"),
    ("pj", "PJ", lambda e: 100 * e["PJ"] / sum(e.values()), "#318ce7", [0, 10, 20, 30, 40, 50, 60], "% PJ"),
    ("pds", "PDS", lambda e: 100 * e["PDS"] / sum(e.values()), "#2e7d32", [0, 2, 4, 6, 8, 10, 12], "% PDS (Massera)")):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, note=NOTE, units=un, prov=pv,
                      national=dict(cands=nat_cands, slices=nat_slices, partp=None, metrics=nat_metrics), legend=lg))

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
    body.append('<text class="cn" x="%s" y="%s" text-anchor="middle"%s>%s</text>' % (f2(x), f2(y), (' transform="rotate(%d %s %s)"' % (rot, f2(x), f2(y))) if rot else "", txt))


# insets ---------------------------------------------------------------
def bbox_of(idx):
    return shapely.total_bounds([G_raw[i] for i in idx])


def window(b, aspect, pad=0.07):
    x0, y0, x1, y1 = b
    ww, hh = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    if ww / hh < aspect:
        ww = hh * aspect
    else:
        hh = ww / aspect
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(mx - ww / 2, 2), round(my - hh / 2, 2), round(ww, 2), round(hh, 2)]


tuc = [i for i, u in enumerate(U) if u["prov"] == "Tucumán"]
caba_b = bbox_of(cap_idx)
cx, cy = (caba_b[0] + caba_b[2]) / 2, (caba_b[1] + caba_b[3]) / 2
gba_w = 62.0
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True)
body.append(X99["ant_body"])
INSETS = [
    dict(id="tuc", label="Tucumán", f=[450, 300, 200, 185], win=window(bbox_of(tuc), 200 / 185), show=["d", "pb"], sd=2.6, sp=3.4),
    X99["sj"], X99["mza"], X99["res"],
    dict(id="gba", label="Área Metropolitana de Buenos Aires", f=[1247, 785, 647, 320], win=[round(cx - gba_w * 0.42, 2), round(cy - gba_w / (647 / 320) * 0.5, 2), gba_w, round(gba_w / (647 / 320), 2)], show=["d", "pb", "out"], sd=1.9, sp=3.0, so=2.6),
    X99["ant"],
    dict(id="caba", label="Capital Federal", f=[1632, 1187, 191, 232], win=window(caba_b, 191 / 232, 0.05), show=["dc"], sd=3, fit="meet", noframe=True, lx=1728, noclip=True, so=2.6),
]
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
for _i, _u in enumerate(U):
    if _u["name"] == "Islas Malvinas":
        pv.append('<path class="pfm" style="fill:#00838f;stroke:#00838f;stroke-width:5px;stroke-linejoin:round" d="%s"/>' % geom_d(G[_i]))
pv.append("</g>")

# dataset ----------------------------------------------------------------
disp = {}
for i, u in enumerate(U):
    p = u["prov"]
    nice = NICE.get((p, norm(u["name"])), u["name"])
    if p == "Capital Federal":
        num = int(u["name"].split()[1])
        disp[i] = "Circunscripción %d · %s" % (num, u.get("parroquia") or nice)
    else:
        disp[i] = nice

ds = dict(
    slug="elecciones_1987_ucronia", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de Argentina de", year="1987",
    labels=dict(pie1="Proporción sobre votos positivos", pie2="", results="Resultados", won="GANÓ", provinces="Provincias"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1987", subtitle="Ucronía · deptos. de 1980")},
    bins=[30, 35, 40, 45, 50, 55],
    bin_labels=["25%", "30%", "35%", "40%", "45%", "50%", "+55%"],
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(DATASET, "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Elecciones presidenciales 1987 (ucronía)</title>")
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"', 'style="--v-d:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub('<g id="pv" transform="matrix(0.1448 0 0 0.1448 55.7 599.8)" style="--spf:9.7px">', '<g id="pv" transform="matrix(%s 0 0 %s %s %s)" style="--spf:9.7px">' % (KPV, KPV, f2(pv_tx), f2(pv_ty)))
sub("#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}", "#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}")
i0 = tpl.index("const INSETS=["); i1 = tpl.index("];", i0) + 2
tpl = tpl[:i0] + "const INSETS=DATA.insets||[];" + tpl[i1:]
sub('<defs><clipPath id="mapclip"><path clip-rule="evenodd" d="M570 100h840v1540h-840z M570 300h80v185h-80z M570 545h79v159h-79z M1247 785h163v320h-163z M1247 1166h163v452h-163z M985 1200h200v320-200z"/></clipPath></defs>'.replace("v320-200z", "v320h-200z"),
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
  const KEYS=LG0&&LG0.keys?LG0:null;
  const USED=c=>[...document.querySelectorAll('#B .d,#B .dc')].some(e=>(e.getAttribute("fill")||"").toLowerCase()===c.toLowerCase());   // solo se rotula el gris que alguna unidad usa en este modo
  """)
sub("if(LG&&LG.keys){", "if(KEYS){")
sub("LG.keys.forEach(", "KEYS.keys.filter(([k])=>USED(k)).forEach(")
sub("const rows=(LG&&LG.bars===false)?[]:N.cands;", "const rows=(LG0&&LG0.bars===false)?[]:N.cands;")
sub("""$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;""", """$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;$("#pie1").setAttribute("x",184);""")
sub('''el("text",{x:93,y:1266,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=1292''',
    '''const MANY=N.cands.length>5,Y0=MANY?(N.cands.length>9?1008:1024):1266;
  el("text",{x:93,y:Y0,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=Y0+26;''')
sub("const h=50,win=idx===0&&!LG", "const h=MANY?42:50,k=h/50,win=idx===0&&!LG")
sub('''el("text",{x:104,y:y+36,"font-size":lg.length>2?34:40,fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41,''',
    '''el("text",{x:104,y:y+36*k,"font-size":(lg.length>3?26:lg.length>2?30:34)*(MANY?.9:1),fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41*k,''')
sub('width:lg.length>2?(lg.length*20):(lg.length*23),height:3', 'width:(lg.length>3?lg.length*15:lg.length>2?(lg.length*18):(lg.length*20))*(MANY?.9:1),height:3')
sub('el("text",{x:424,y:y+21,"font-size":21,', 'el("text",{x:424,y:y+20*k,"font-size":MANY?18:21,')
sub('el("text",{x:424,y:y+20*k,"font-size":MANY?18:21,fill:"#fff","text-anchor":"end"},g,C.n);',
    '''const nm=el("text",{x:424,y:y+20*k,"font-size":MANY?18:21,fill:"#fff","text-anchor":"end"},g,C.n);
    const nmw=424-(93+(C.img?Math.min(h*(C.ar||1),116):11))-8;   // el nombre largo no pisa el logo de la barra
    if(nmw>0&&nm.getComputedTextLength()>nmw){nm.setAttribute("textLength",nmw.toFixed(1));nm.setAttribute("lengthAdjust","spacingAndGlyphs");}''')
sub('if(C.sub)el("text",{x:424,y:y+39,"font-size":15,', 'if(C.sub)el("text",{x:424,y:y+37*k,"font-size":MANY?13:15,')
sub('el("text",{x:477,y:y+29,"font-size":26,', 'el("text",{x:477,y:y+29*k,"font-size":MANY?23:26,')
sub('el("text",{x:497,y:y+44,"font-size":10,', 'el("text",{x:497,y:y+44*k,"font-size":10,')
sub('el("text",{x:476,y:y+33,"font-size":23,', 'el("text",{x:476,y:y+33*k,"font-size":MANY?20:23,')
sub("const tl=Math.min(1088,Math.round(1088*title.length/41));",
    "const r0=document.querySelector(\"#tiles rect\"),x0=r0?+r0.getAttribute(\"x\"):1262;const tl=Math.min(1088,Math.round(1088*title.length/41),x0-22-13-114-14);")
sub("const list=tilesNow(),xs=[1262,1316,1370,1424];", "const list=tilesNow(),xs=list0len()>4?[1208,1262,1316,1370,1424]:[1262,1316,1370,1424];")
sub("return out.slice(0,4);", "return out.slice(0,5);")
sub("function drawTiles(){", "function list0len(){return tilesNow().length}\nfunction drawTiles(){")
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
open(OUT, "w", encoding="utf8", newline="\n").write(html)

# logos de la leyenda al ras de la barra (regla general; este atlas no está en las excepciones)
sys.path.insert(0, os.path.join(ROOT, "comun"))
import logos_al_ras
print("logos:", logos_al_ras.aplicar(OUT), file=sys.stderr)
print("escrito", OUT, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
