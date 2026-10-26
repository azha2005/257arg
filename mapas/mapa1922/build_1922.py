#!/usr/bin/env python3
"""Atlas electoral 1922 (estilo Wikipedia 1999) sobre la division departamental del censo de 1914.

    python build_1922.py            -> mapa1922/atlas_1922.html (+ dataset_1922.json)

Geometria : Base deptos 1869-2022/Departamentos_1914.shp.
Departamentos: Canton (1968), t. II, pp. PDF 70-85 (transcripcion manual de las imagenes, canton/p_*.txt).
Provincias y pais: cuadro oficial de la Memoria del Interior 1921-22 segun la Wikipedia (incluye Mendoza y Santiago del Estero, que Canton no trae).
Nombres   : equivalencias documentadas en Cacopardo (1967), Documento de Trabajo n. 47, Cuadro 1.
"""
import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
import sys, os, re, json, math, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, shapely
from shapely.ops import unary_union
import geom
from names import norm
from match import load_data

HERE = os.path.dirname(os.path.abspath(__file__))
LOGOS = os.path.join(HERE, "..", "../logos")   # emblemas de Wikipedia, ver LICENCIAS.md alli
TEMPLATE_SRC = os.path.join(HERE, "..", "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

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
PKL = os.path.join(HERE, "units_raw.pkl")
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

# ---------------------------------------------------------------- datos: Canton (1968), tomo II, elecciones de 1922
sys.path.insert(0, os.path.join(HERE, "canton"))
from spec import SPEC, PARTY, BLOC

KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
# equivalencias nombre de Cantón (1922) -> poligono(s) 1914. Motivo documentado en Cacopardo (1967), Cuadro 1, cuando existe.
ALIAS = {
    ("Buenos Aires", "9 de Julio"): (["Nueve de julio"], None),
    ("Buenos Aires", "Matanza"): (["La Matanza"], None),
    ("Buenos Aires", "Mar Chiquita"): (["Coronel Vidal"], "El partido Coronel Vidal (1914) es el actual Mar Chiquita (Cacopardo 1967)."),
    ("Buenos Aires", "Tordillo"): (["General Conesa"], "El partido General Conesa (1914) volvió a llamarse Tordillo (Cacopardo 1967)."),
    ("Buenos Aires", "General Madariaga"): (["Gnral.Juan Madariaga"], None),
    ("Buenos Aires", "Tigre"): (["Las Conchas (Tigre)"], None),
    ("Salta", "Caldera"): (["La Caldera"], None), ("Salta", "Candelaria"): (["La Candelaria"], None),
    ("San Juan", "Ullún"): (["Ullum"], None),
    ("Buenos Aires", "Trenque Lauquen"): (["Trenquelauquen"], None),
    # unidades sin datos propios: Canton, t. I, Apendice C, dice en que unidad mayor quedaron sus votos
    ("Buenos Aires", "Juárez"): ([], None), ("Buenos Aires", "Tres Arroyos"): ([], None), ("Buenos Aires", "Gonzáles Chaves"): ([], None), ("Buenos Aires", "González Chaves"): ([], None),
    ("Buenos Aires", "Necochea"): (["Necochea", "Tres Arroyos", "Benito Juarez"], "Cantón (t. I, Apéndice C) incluye en Necochea los datos de Juárez, Tres Arroyos y Gonzáles Chaves; el dato se reparte en los tres polígonos de 1914 (Gonzáles Chaves, creado en 1916, no existe en esa base)."),
    ("Córdoba", "General Roca"): ([], None), ("Córdoba", "Pte. Roque Sáenz Peña"): ([], None),
    ("Córdoba", "Juárez Celman"): (["Juárez Célman", "General Roca"], "Cantón (t. I, Apéndice C) incluye en Juárez Celman los datos de General Roca y de Pte. Roque Sáenz Peña; el dato se reparte en los dos polígonos de 1914."),
    ("San Juan", "Chimbas"): ([], None),
    ("Catamarca", "Fray Mamerto Esquiú"): (["Piedra Blanca"], "El departamento Piedra Blanca (1914) es el actual Fray Mamerto Esquiú (Cacopardo 1967)."),
    ("Entre Ríos", "Concepción del Uruguay"): (["Uruguay"], None), ("Entre Ríos", "Rosario Tala"): (["Tala"], None),
    ("La Rioja", "Gobernador Gordillo"): (["Juarez Celman"], "El departamento Juárez Celman (1914) pasó a ser Gobernador Gordillo (Cacopardo 1967)."),
    ("Mendoza", "Luján"): (["Lujan de Cuyo"], None),
    ("Salta", "General Martín Miguel de Güemes"): (["Campo Santo"], "Campo Santo (1914) corresponde al actual General Güemes; asignación por continuidad territorial, no verificada voto a voto."),
    ("San Juan", "Angaco"): (["Angaco Norte"], "Angaco Norte (1914) es el actual Angaco (Cacopardo 1967)."),
    ("San Juan", "San Martín"): (["Angaco Sud"], "Angaco Sud (1914) pasó a ser San Martín (Cacopardo 1967)."),
    ("San Juan", "Rawson"): (["Trinidad"], "Rawson se formó con los distritos 2 y 3 del extinguido Trinidad; el distrito 1 pasó a Capital (Cacopardo 1967). Asignación aproximada."),
    ("San Juan", "Capital"): (["Capital", "Concepción", "Desamparados", "Chimbas"], "Chimbas: Cantón (t. I, Apéndice C) incluye sus datos en Concepción, que en esta base recibe el dato de la Capital. En 1947 Capital incluye los distritos Concepción y Desamparados, que la base de 1914 dibuja aparte (Cacopardo 1967); reciben el mismo dato."),
    ("San Luis", "Pringles"): (["Coronel pringles"], None),
    ("San Luis", "San Martín"): (["Libertador Gral.Sn Martín"], None),
    ("Santa Fe", "Nueve de Julio"): (["9 de Julio"], None),
    ("Santiago del Estero", "General Taboada"): (["28 de Marzo"], "28 de Marzo (1914) es el actual General Taboada (Cacopardo 1967)."),
}
CAP_CIRC = {"Vélez Sarsfield": 1, "San Cristóbal Sud": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sud": 6,
            "San Carlos Norte": 7, "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sud": 10, "Balvanera Norte": 11,
            "Concepción": 12, "Montserrat": 13, "San Nicolás": 14, "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18,
            "Pilar": 19, "Socorro": 20}


def read_rows(path):
    rows = []
    for ln in open(os.path.join(HERE, "canton", path), encoding="utf8"):
        if ln.startswith("#") or "|" not in ln:
            continue
        n, v = ln.rstrip("\n").split("|")
        rows.append((n, None if v.strip() == "-" else [None if x == "?" else int(x) for x in v.split()]))
    return rows


def party_votes(prov, vals):
    """-> dict codigo de partido -> votos (suma de columnas con el mismo codigo), inscriptos, votantes"""
    cols = SPEC[prov]["cols"]
    P, ins, vot = {}, None, None
    for c, x in zip(cols, vals):
        if c == "INS": ins = x
        elif c == "VOT": vot = x
        elif x is not None: P[c] = P.get(c, 0) + x
    return P, ins, vot


canton = {}      # (prov, nombre Canton) -> dict
for prov in SPEC:
    for n, v in read_rows(SPEC[prov]["file"]):
        canton[(prov, n)] = dict(prov=prov, name=n, vals=v)

unit_src, unmapped = {}, []
for (prov, n), r in canton.items():
    if prov == "Capital Federal":
        k = CAP_CIRC.get(n)
        idx = [KEY[("Capital Federal", norm("Circ. %02d" % k))]] if k else []
        why = None
    elif (prov, n) in ALIAS:
        names, why = ALIAS[(prov, n)]
        idx = [KEY[(prov, norm(x))] for x in names]
    else:
        k = (prov, norm(n))
        idx, why = ([KEY[k]] if k in KEY else []), None
    if not idx:
        if r["vals"] is not None: unmapped.append(r)
        continue
    for i in idx:
        assert i not in unit_src, (prov, n, U[i]["name"])
        unit_src[i] = (r, why, len(idx))

# comprobacion: Lupu-Stokes aporta algo donde Canton no tiene dato? (para rellenar huecos)
import pandas as pd
_L = pd.read_csv(os.path.join(HERE, "..", "../datos/preparados", "lupu_stokes_1912_2003_exportacion.csv"))
_L = _L[(_L.year == 1922) & (_L.pres == 1) & (_L.total > 0)]
_PN = {"Cordoba": "Córdoba", "Entre Rios": "Entre Ríos", "Tucuman": "Tucumán"}
_LAL = {"camapana": "campana", "chascomis": "chascomus", "clavarria": "olavarria", "trenquelanguen": "trenquelauquen", "nuevedejulio": "nuevedejulio",
        "valleviego": "valleviejo", "eumahuaca": "humahuaca", "mburcuya": "mburucuya", "3defebrero": "caseros", "juarez": "juarez"}
_cn = {(p, norm(n)) for (p, n), r in canton.items() if r["vals"] is not None}
lupu_extra = []
for _, r in _L.iterrows():
    pv = _PN.get(r.province, r.province); k = norm(r.department); k = _LAL.get(k, k)
    if (pv, k) not in _cn and not (pv == "San Juan" and k in ("capital", "ullun", "rawson", "angaco")):
        lupu_extra.append((pv, r.department, int(r.total)))
print("Lupu con votos y sin fila en Canton (candidatas a rellenar huecos):", lupu_extra, file=sys.stderr)

LOS_ANDES = {("Catamarca", "Antofagasta de la Sierra"), ("Jujuy", "Susques"), ("Salta", "Pastos Grandes"), ("Salta", "San Antonio de los Cobres")}
PENDIENTES = {"Mendoza", "Santiago del Estero"}   # Canton no trae su cuadro de 1922 (Mendoza: el 6-abr-1922 la junta escrutadora nacional anulo la eleccion; ver LEEME)
BLOCS = ["UCR", "CON", "SOC", "DIS", "PDP"]
# formulas y colores de la Wikipedia («Elecciones presidenciales de Argentina de 1922»)
CAND = {
    "UCR": dict(n="Marcelo T. de Alvear", sub="Unión Cívica Radical", logo="UCR", base="#e10019"),
    "CON": dict(n="Norberto Piñero", sub="Concentración Nacional", logo="CN", base="#30d5c8", bar="#1fa89d", txt="#1a8f86"),
    "SOC": dict(n="Nicolás Repetto", sub="Partido Socialista", logo="PS", base="#ff9900", bar="#e08700", txt="#b87500"),
    "DIS": dict(n="Miguel Laurencena", sub="Radicales disidentes", logo="UCRD", base="#ff5500", bar="#e04a00", txt="#c24000"),
    "PDP": dict(n="Carlos Ibarguren", sub="Partido Demócrata Progresista", logo="PDP", base="#005c9e"),
}
PCOL = {"UCR": "#e10019", "OPO": "#f0566a", "CNC": "#35aae0", "CON": "#30d5c8", "UPV": "#6fe3da", "UPO": "#22b5aa", "DEM": "#1f2f6b", "LIB": "#a3eee8",
        "SOC": "#ff9900", "PRI": "#4169e1", "BLO": "#44944a", "ROJ": "#a52a2a", "INT": "#c0504d", "UTU": "#ff9999", "LAU": "#ff5500",
        "DP": "#005c9e", "COM": "#e22928", "BLA": "#c9c9c9"}
for c, col in PCOL.items():
    CAND["P_" + c] = dict(n=PARTY[c], base=col, minor=True)
CAND["P_OTR"] = dict(n="Otros, en blanco o no atribuido", base="#9a9a9a", minor=True)


def _logo(fn, ar):
    import base64
    t = open(os.path.join(LOGOS, fn), encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar)


CAND["UCR"].update(_logo("Bandera_UCR_bicolor.svg", 850 / 510))   # bandera radical antigua (blanca y roja); el escudo es de 1931
CAND["PDP"].update(_logo("Escudo_del_PDP.svg", 1.0))
CAND["SOC"].update(_logo("Emblema_del_Partido_Socialista_Argentino.svg", 1.0))
GREY_T, GREY_N, GREY_P = "#cfcfcf", "#8c8c8c", "#e6dcc3"
KEYS = [[GREY_T, "Territorio nacional: no votaba"], [GREY_N, "Sin dato o cifras subsumidas"],
        [GREY_P, "Mendoza y Santiago del Estero: sin cuadro departamental"]]

# Canton declara «reconstruidos» los inscriptos de estas provincias
INS_RECON = {"Corrientes", "Entre Ríos", "Jujuy", "La Rioja", "Salta", "San Juan", "San Luis", "Tucumán"}
VOT_FUENTE = {"Buenos Aires": "La Prensa del 3 de abril de 1922 (cifras preliminares: en muchos partidos son menores que la suma de los partidos)"}
DUDAS = {
    ("Catamarca", "Valle Viejo"): "La Concentración figura con 322 en la página impresa; Lupu–Stokes trae 622. Se conserva la cifra impresa.",
    ("Buenos Aires", "General Pinto"): "Concentración: 435 impreso; Lupu–Stokes trae 425. Se conserva la cifra impresa.",
    ("Entre Ríos", "Paraná"): "Concentración: 5.516 impreso; Lupu–Stokes trae 5.517. Se conserva la cifra impresa.",
    ("Jujuy", "Yavi"): "La cifra de la Concentración es ilegible en la página (¿9 o 2?) y no se computa.",
    ("Jujuy", "Humahuaca"): "La cifra de la Concentración tiene una mancha de tinta; se lee 0.",
}
TUC_NOTE = ("Cantón rotula «Unión Cívica Radical» a la lista de los radicales disidentes y «Radicales opositores» a la de Alvear; "
            "la asignación se infiere por comparación con el cuadro oficial (ver LEEME).")


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def analyse(prov, vals):
    P, ins, vot = party_votes(prov, vals)
    tabulated = sum(P.values())
    E = max(vot or 0, tabulated) or None                        # votos emitidos
    D = (tabulated - P.get("BLA", 0) - P.get("OTR", 0)) or None   # votos positivos: base de los porcentajes, como en Wikipedia
    bloc = {b: 0 for b in BLOCS}
    for c, x in P.items():
        b = BLOC.get(c)
        if b in bloc: bloc[b] += x
    return dict(P=P, ins=ins, vot=vot, D=D, E=E, tab=tabulated, bloc=bloc)


def rec_from(a, extra_note=None, hole=False):
    D = a["D"]
    if not D: return None
    E = a.get("E") or D   # emitidos: base de blancos y no atribuidos
    P = a["P"]
    lines = [["P_" + c, int(round(x)), round(100 * x / D, 2)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if c not in ("BLA", "OTR") and (x > 0 or c == "UCR")]
    blank = P.get("BLA", 0) + P.get("OTR", 0)
    if blank: lines.append(["P_BLA" if P.get("BLA") and not P.get("OTR") else "P_OTR", int(blank), round(100 * blank / E, 2)])
    rest = E - a["tab"]
    if rest > 0.5: lines.append(["P_OTR", int(round(rest)), round(100 * rest / E, 2)])
    w = max(a["bloc"], key=lambda b: a["bloc"][b])
    met = []
    if a["ins"] is not None: met.append(["Inscriptos", fmt_n(a["ins"])])
    if a["vot"] is not None: met.append(["Votantes", fmt_n(a["vot"])])
    if a["ins"] and a["vot"]: met.append(["Participación", fmt_p(100 * E / a["ins"]) + " %"])
    rec = {"lines": lines, "metrics": met}
    if a["bloc"][w] > 0:
        rec.update(w=w, q=round(100 * a["bloc"][w] / D, 2))
    else:
        rec["fill"] = GREY_N
    notes = []
    if a["vot"] is not None and a["tab"] > 1.03 * a["vot"]:
        notes.append("En la fuente impresa la suma de los partidos (%s) excede a los votantes (%s); la participación se calcula sobre la suma." % (fmt_n(a["tab"]), fmt_n(a["vot"])))
    if hole: notes.append("Hay cifras sin datos o ilegibles en la fila: los porcentajes pueden estar subestimados.")
    if a["vot"] is None: notes.append("Cantón no trae votantes para esta provincia: los porcentajes son sobre la suma de los votos por partido.")
    if extra_note: notes.append(extra_note)
    if notes: rec["note"] = " ".join(notes)
    return rec


# Memoria del Interior 1921-22 (segun la Wikipedia, "Resultados por distrito"): votos Alvear, Pinero, Repetto, Laurencena, otros (PDP en Capital y Santa Fe),
# blancos y diferencia de actas, votantes, registrados. Cada fila cierra: suma de partidos + blancos/diferencia = votantes.
OFICIAL = {
    "Buenos Aires":        (114639, 62029, 12379, 0, 0, 8873, 197920, 406848),
    "Capital Federal":     (68192, 25415, 54813, 9393, 9772, 13783, 181368, 246567),
    "Catamarca":           (10291, 5750, 105, 0, 67, 278, 16491, 26896),
    "Córdoba":             (47838, 31078, 577, 261, 0, 3458, 83212, 177908),
    "Corrientes":          (19944, 27239, 0, 0, 0, 619, 47802, 90896),
    "Entre Ríos":          (33652, 31485, 412, 2377, 97, 2221, 70244, 103199),
    "Jujuy":               (7678, 468, 0, 0, 94, 1396, 9636, 16918),
    "La Rioja":            (6775, 2140, 0, 2016, 0, 282, 11213, 20986),
    "Mendoza":             (2175, 3348, 2590, 14150, 37, 2072, 24372, 57250),
    "Salta":               (2869, 8740, 0, 6707, 5, 920, 19241, 35877),
    "San Juan":            (5639, 5504, 414, 7048, 270, 647, 19522, 28253),
    "San Luis":            (7569, 6709, 0, 126, 240, 0, 14644, 31852),
    "Santa Fe":            (57851, 0, 3004, 0, 32069, 10842, 103766, 174430),
    "Santiago del Estero": (27237, 8380, 962, 0, 0, 0, 36579, 73334),
    "Tucumán":             (6821, 12817, 3216, 16671, 0, 2117, 41642, 95152),
}
for _p, _v in OFICIAL.items():
    assert sum(_v[:6]) == _v[6], (_p, sum(_v[:6]), _v[6])
PDP_OTROS = {"Capital Federal", "Santa Fe"}     # en la columna «otros partidos» de esa tabla, el PDP (nota de la Wikipedia)

unit_rec, unit_an = {}, {}
for i, u in enumerate(U):
    p = u["prov"]
    if p in geom.TERR:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1922: sus habitantes no votaban para presidente."}
    elif (p, u["name"]) in LOS_ANDES:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio Nacional de Los Andes (1900-1943): sus habitantes no votaban para presidente (Cacopardo 1967)."}
    elif p in PENDIENTES:
        o = OFICIAL[p]
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Cantón no trae el cuadro departamental de %s para 1922; tampoco lo publicó La Prensa del 2 al 8 de abril. Total provincial (Memoria del Interior 1921-22, vía Wikipedia): Alvear %s, Piñero %s%s%s." % (
            p, fmt_n(o[0]), fmt_n(o[1]), (", Repetto %s" % fmt_n(o[2])) if o[2] else "", (", Laurencena (lencinistas) %s" % fmt_n(o[3])) if o[3] else "")}
    elif i in unit_src:
        r, why, n = unit_src[i]
        if r["vals"] is None:
            unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón marca las cifras de «%s» como subsumidas bajo una unidad mayor o no tomadas en cuenta." % r["name"]}
            continue
        cols = SPEC[p]["cols"]
        pv = [x for c, x in zip(cols, r["vals"]) if c not in ("INS", "VOT")]
        if all(x is None for x in pv):
            ins = r["vals"][cols.index("INS")]; vot = r["vals"][cols.index("VOT")]
            unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón no trae votos por partido para «%s» (sin datos)%s." % (
                r["name"], (": inscriptos %s" % fmt_n(ins) if ins else "") + (", votantes %s" % fmt_n(vot) if vot else ""))}
            continue
        hole = any(x is None for x in pv)
        extras = []
        if norm(r["name"]) != norm(u["name"]) and p != "Capital Federal": extras.append("Nombre en Cantón: «%s»." % r["name"])
        if why: extras.append(why)
        if n > 1: extras.append("Dato único compartido por %d polígonos." % n)
        if (p, r["name"]) in DUDAS: extras.append(DUDAS[(p, r["name"])])
        if p == "Tucumán": extras.append(TUC_NOTE)
        if p in INS_RECON: extras.append("Inscriptos reconstruidos por Cantón (no son los del padrón).")
        if p in VOT_FUENTE: extras.append("Inscriptos y votantes: " + VOT_FUENTE[p] + ".")
        a = analyse(p, r["vals"]); unit_an[i] = a
        unit_rec[i] = rec_from(a, " ".join(extras) or None, hole)
    else:
        unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Sin fila para esta unidad en Cantón (1922)."}

# nombres de las unidades para el titulo de las tarjetas
disp = {}
for i, (r, why, n) in unit_src.items():
    p = U[i]["prov"]
    disp[i] = ("Circunscripción %d · %s" % (CAP_CIRC[r["name"]], r["name"])) if p == "Capital Federal" else (r["name"] if n == 1 else U[i]["name"])

# provincias y pais: cuadro oficial de la Memoria del Interior (todas las jurisdicciones)
OCODE = ("UCR", "CNC", "SOC", "LAU")
prov_an, nat = {}, dict(ins=0, vot=0, bloc={b: 0 for b in BLOCS}, other=0)
for prov, v in OFICIAL.items():
    P = {c: float(x) for c, x in zip(OCODE, v[:4]) if x}
    if prov in PDP_OTROS: P["DP"] = float(v[4])
    elif v[4]: P["OTR"] = float(v[4])
    prov_an[prov] = dict(P=P, ins=v[7], vot=v[6])
    for c, x in P.items():
        b = BLOC.get(c)
        if b: nat["bloc"][b] += x
        else: nat["other"] += x
    nat["ins"] += v[7]; nat["vot"] += v[6]


def an_of(t):
    tab = sum(t["P"].values()); bloc = {b: 0 for b in BLOCS}
    for c, x in t["P"].items():
        b = BLOC.get(c)
        if b in bloc: bloc[b] += x
    return dict(P=t["P"], ins=t["ins"] or None, vot=t["vot"], D=(tab - t["P"].get("BLA", 0) - t["P"].get("OTR", 0)) or None, E=max(t["vot"] or 0, tab), tab=tab, bloc=bloc)


OF_NOTE = ("Cuadro por distrito de la Memoria del Interior 1921-22 (p. 239-310), tal como lo reproduce la Wikipedia; no se verificó en la Memoria. "
           "Los departamentos salen de Cantón (prensa de la época) y no suman exactamente este total.")
prov_rec = {}
for p in PROVS:
    if p in geom.TERR:
        prov_rec[p] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1922: sin voto presidencial."}
    else:
        extra = OF_NOTE
        if p in PENDIENTES: extra = "Cantón no trae el cuadro departamental. " + OF_NOTE
        if p == "Mendoza": extra += " Mendoza votó el 2 de abril; la junta escrutadora nacional anuló la elección en 189 mesas (6-7 abr.) y el Poder Ejecutivo provincial declaró la nulidad total (La Prensa, 8 y 14 abr. 1922). La fecha del 14 de mayo que da la Wikipedia no se confirma."
        prov_rec[p] = rec_from(an_of(prov_an[p]), extra)
NA = dict(bloc=nat["bloc"], D=nat["vot"], tab=sum(sum(t["P"].values()) for t in prov_an.values()))
cands = sorted([{"code": b, "votes": int(NA["bloc"][b]), "pct": round(100 * NA["bloc"][b] / NA["D"], 2)} for b in BLOCS if NA["bloc"][b] > 0], key=lambda x: -x["votes"])
other = int(nat["other"]); nat_blank = int(NA["D"] - NA["tab"])
slices = [{"code": c["code"], "v": c["votes"]} for c in cands] + [{"fill": "#717274", "v": other}, {"fill": "#dfe0e5", "v": nat_blank}]
partp = round(100 * nat["vot"] / nat["ins"], 2)
NAT_MET = [["Inscriptos", fmt_n(nat["ins"])], ["Votantes", fmt_n(nat["vot"])], ["Participación", fmt_p(partp) + " %"]]
# resultado nacional: tabla del articulo de Wikipedia (ver ../wikitop.py)
sys.path.insert(0, os.path.join(HERE, ".."))
import wikitop
cands, slices, partp, NAT_MET = wikitop.national(1922)
print("pais: inscriptos", nat["ins"], "votantes", nat["vot"], "bloques", {b: int(v) for b, v in NA["bloc"].items()}, "otros", other, "blanco/dif", nat_blank,
      "| sin poligono:", [(r["prov"], r["name"]) for r in unmapped], file=sys.stderr)

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


NOTE = ("Fuente: departamentos, D. Cantón, «Materiales para el estudio de la sociología política en la Argentina» (1968), t. II, elecciones de electores de presidente, 2 abr. 1922 (solo varones); "
        "provincias y país, Memoria del Interior 1921-22 (vía Wikipedia). Geometría: departamentos del censo de 1914.. "
        "Bloques: Alvear (UCR), Piñero (Concentración Nacional y partidos afines), Repetto (Socialista), Laurencena (radicales disidentes), Ibarguren (PDP).")
NOTE = wikitop.note(1922) + " " + NOTE



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
        if p in geom.TERR: prov[p] = r; continue
        v = fn(an_of(prov_an[p]))
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec,
              national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=dict(keys=KEYS))]
for mid, tile, fn, base, edges, title, extra in (
    ("ucr", "UCR", lambda a: 100 * a["bloc"]["UCR"] / a["D"], "#e10019", [0, 10, 25, 40, 50, 60, 70], "% Alvear (UCR)", ""),
    ("con", "CON", lambda a: 100 * a["bloc"]["CON"] / a["D"], "#1fa89d", [0, 10, 20, 30, 40, 50, 60], "% Piñero y afines", "Piñero = Concentración Nacional y partidos conservadores, demócratas, liberales y provinciales afines. "),
    ("par", "PART", lambda a: (100 * a["E"] / a["ins"]) if (a["ins"] and a["vot"]) else None, "#2a6f97", [0, 20, 30, 40, 50, 60, 70], "Participación (votantes / inscriptos)", "")):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, note=extra + NOTE, units=un, prov=pv,
                      national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=lg))

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
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True, antarctic=False, omit=("mza",), sj_names={"Capital", "Santa Lucia", "Chimbas", "Rivadavia", "Pocito", "Albardon", "Trinidad", "Concepcion", "Desamparados", "Zonda", "Rawson"}, chaco_names={"Resistencia"})
body.append(X99["ant_body"])
INSETS = [
    dict(id="tuc", label="Tucumán", f=[450, 300, 200, 185], win=window(bbox_of(tuc), 200 / 185), show=["d", "pb"], sd=2.6, sp=3.4),
    dict(id="gba", label="Área Metropolitana de Buenos Aires", f=[1247, 785, 647, 320], win=[round(cx - gba_w * 0.42, 2), round(cy - gba_w / (647 / 320) * 0.5, 2), gba_w, round(gba_w / (647 / 320), 2)], show=["d", "pb", "out"], sd=1.9, sp=3.0, so=2.6),
    dict(id="caba", label="Capital Federal", f=[1632, 1187, 191, 232], win=window(caba_b, 191 / 232, 0.05), show=["dc"], sd=3, fit="meet", noframe=True, lx=1728, noclip=True, so=2.6),
]
GBA = INSETS[1]
INSETS = [INSETS[0]] + [X99[k] for k in ("sj", "mza", "res") if X99[k]] + [GBA] + ([X99["ant"]] if X99["ant"] else []) + INSETS[2:]   # sin recuadro de la Antártida (anterior a 1946)
marks = [("tuc", INSETS[0]["win"]), ("gba", GBA["win"])] + X99["marks"]
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
    slug="elecciones_1922", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de Argentina de", year="1922",
    labels=dict(pie1="Proporción sobre votos positivos"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1922", subtitle="Cantón (1968) · deptos. de 1914")},
    modes=MODES, insets=INSETS, solid=sorted(PENDIENTES),
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(HERE, "dataset_1922.json"), "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Elecciones presidenciales 1922</title>")
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
# cinco candidaturas + tres claves de gris: la leyenda arranca mas arriba para no salirse del lienzo
sub("  let y=1292;", "  let y=1190;")
sub('el("text",{x:93,y:1266,', 'el("text",{x:93,y:1164,')
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(HERE, "atlas_1922.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
