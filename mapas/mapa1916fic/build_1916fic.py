#!/usr/bin/env python3
"""Atlas FICTICIO de las elecciones presidenciales de 1916 (línea alternativa; estilo Wikipedia 1999) sobre los departamentos del censo de 1914.

    python build_1916fic.py            -> mapa1916fic/atlas_1916_alt.html (+ dataset_1916fic.json)

Datos     : ../1916dip (Canton 1968 t. II transcripto + expediente de Salta 58-D-1916); Lupu-Stokes solo para cifras ilegibles.
Geometria : Departamentos_1914 (cache units_raw.pkl).  Nombres: Cacopardo (1967), Cuadro 1.
"""
import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
import sys, os, re, json, math, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, shapely
from shapely.ops import unary_union
import geom
from names import norm

HERE = os.path.dirname(os.path.abspath(__file__))
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

# ---------------------------------------------------------------- datos: Canton (1968) t. II, diputados nacionales 1916 + Salta (exp. 58-D-1916)
import pandas as pd
SRC = os.path.join(HERE, "..", "../transcripciones/1916dip")
CANTON = os.path.join(SRC, "canton_diputados_1916")

KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
# equivalencias nombre de Canton -> poligono(s) 1914 (mismas que el atlas de 1928; motivo documentado en Cacopardo 1967, Cuadro 1)
ALIAS = {
    ("Buenos Aires", "9 de Julio"): (["Nueve de julio"], None),
    ("Buenos Aires", "Matanza"): (["La Matanza"], None),
    ("Buenos Aires", "Mar Chiquita"): (["Coronel Vidal"], "El partido Coronel Vidal (1914) es el actual Mar Chiquita (Cacopardo 1967)."),
    ("Buenos Aires", "Tordillo"): (["General Conesa"], "El partido General Conesa (1914) volvió a llamarse Tordillo (Cacopardo 1967)."),
    ("Buenos Aires", "General Madariaga"): (["Gnral.Juan Madariaga"], None),
    ("Buenos Aires", "Tigre"): (["Las Conchas (Tigre)"], None),
    # unidades sin datos propios: Canton, t. I, Apendice C, dice en que unidad mayor quedaron sus votos
    ("Buenos Aires", "Juárez"): ([], None), ("Buenos Aires", "Tres Arroyos"): ([], None), ("Buenos Aires", "Gonzáles Chaves"): ([], None), ("Buenos Aires", "González Chaves"): ([], None),
    ("Buenos Aires", "Necochea"): (["Necochea", "Tres Arroyos", "Benito Juarez"], "Cantón (t. I, Apéndice C) incluye en Necochea los datos de Juárez, Tres Arroyos y Gonzáles Chaves; el dato se reparte en los tres polígonos de 1914 (Gonzáles Chaves, creado en 1916, no existe en esa base)."),
    ("Córdoba", "General Roca"): ([], None), ("Córdoba", "Pte. Roque Sáenz Peña"): ([], None),
    ("Córdoba", "Juárez Celman"): (["Juárez Célman", "General Roca"], "Cantón (t. I, Apéndice C) incluye en Juárez Celman los datos de General Roca y de Pte. Roque Sáenz Peña; el dato se reparte en los dos polígonos de 1914."),
    ("Catamarca", "Fray Mamerto Esquiú"): (["Piedra Blanca"], "El departamento Piedra Blanca (1914) es el actual Fray Mamerto Esquiú (Cacopardo 1967)."),
    ("Entre Ríos", "Concepción del Uruguay"): (["Uruguay"], None), ("Entre Ríos", "Rosario Tala"): (["Tala"], None),
    ("La Rioja", "Gobernador Gordillo"): (["Juarez Celman"], "El departamento Juárez Celman (1914) pasó a ser Gobernador Gordillo (Cacopardo 1967)."),
    ("Mendoza", "Luján"): (["Lujan de Cuyo"], None),
    ("San Luis", "Pringles"): (["Coronel pringles"], None),
    ("San Luis", "San Martín"): (["Libertador Gral.Sn Martín"], None),
    ("Santa Fe", "Nuevo de Julio"): (["9 de Julio"], None),
}
CAP_CIRC = {"Velez Sarsfield": 1, "San Cristóbal Sud": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sud": 6,
            "San Carlos Norte": 7, "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sud": 10, "Balvanera Norte": 11,
            "Concepción": 12, "Monserrat": 13, "San Nicolás": 14, "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18,
            "Pilar": 19, "Socorro": 20}
CAP_CIRC = {norm(k): v for k, v in CAP_CIRC.items()}

# rotulo de Canton -> codigo de fuerza (el mismo numero de columna no es el mismo partido en todo el pais)
CODE = {"Unión Cívica Radical": "UCR", "Concentración": "CNC", "Conservador": "CNS", "Provincialista": "PRV", "Unión Popular": "UPO",
        "Liberal": "LIB", "Autonomista": "AUT", "Socialista": "SOC", "Socialista Argentino": "SAR", "Demócrata Progresista": "PDP",
        "Radical disidente": "RDI", "Radical situacionista (Comité Nacional)": "RSI", "Unión Provincial": "UPV"}
DEMOCRATA = {"Córdoba": "DEM", "San Luis": "DEM", "Santa Fe": "PDP"}     # «Demócrata»: conservador en Cordoba y San Luis; en Santa Fe se lo trata como Demócrata Progresista (inferencia, ver LEEME)
PARTY = {"UCR": "Unión Cívica Radical", "RSI": "Radical situacionista (Comité Nacional)", "RDI": "Radical disidente",
         "CNC": "Concentración", "CNS": "Conservador", "PRV": "Provincialista", "UPO": "Unión Popular", "DEM": "Demócrata",
         "LIB": "Liberal", "AUT": "Autonomista", "PDP": "Demócrata Progresista", "SOC": "Socialista", "SAR": "Partido Socialista Argentino", "UPV": "Unión Provincial"}
# bloques y colores de la Wikipedia («Elecciones legislativas de Argentina de 1916»): la Concentracion Conservadora agrupa
# conservadores, Concentracion, Partido Popular, Union Democratica, Union Provincial y Autonomista de Corrientes; la Concentracion
# Civica de Corrientes (liberales, Pacto Autonomista-Liberal) va aparte.
BLOC = {"UCR": "UCR", "RSI": "UCR", "RDI": "RAD", "CNC": "CON", "CNS": "CON", "PRV": "CON", "UPO": "CON", "DEM": "CON", "LIB": "CCI",
        "AUT": "CON", "UPV": "CON", "PDP": "PDP", "SOC": "SOC", "SAR": "SAR"}
PCOL = {"UCR": "#e10019", "RSI": "#f0566a", "RDI": "#a52a2a", "CNC": "#30d5c8", "CNS": "#22b5aa", "PRV": "#6fe3da", "UPO": "#1a9a91",
        "DEM": "#1f2f6b", "LIB": "#35aae0", "AUT": "#a3eee8", "UPV": "#5cc9c0", "PDP": "#005c9e", "SOC": "#ff9900", "SAR": "#ff6700"}


def fmt_i(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def code_of(prov, rotulo):
    if rotulo == "Demócrata":
        return DEMOCRATA[prov]
    return CODE[rotulo]


cells = pd.read_csv(os.path.join(CANTON, "celdas_1916.csv"), encoding="utf-8-sig")
cot = pd.read_csv(os.path.join(CANTON, "cotejo_lupu_1916.csv"), encoding="utf-8-sig")
LUPU = {}      # (distrito, unidad, rotulo(s)) -> valor Lupu (familia)
for _, r in cot.iterrows():
    if pd.notna(r.valor_lupu):
        LUPU[(r.distrito, r.unidad, r.columnas_canton)] = int(r.valor_lupu)


import itertools


def cands(pat):
    """valores compatibles con una lectura con '?': cada '?' es un digito ilegible; un '?' final tambien puede ser una marca de duda."""
    out = set()
    qs = [k for k, ch in enumerate(pat) if ch == "?"]
    if 0 < len(qs) <= 3 and all(ch.isdigit() or ch == "?" for ch in pat):
        for combo in itertools.product("0123456789", repeat=len(qs)):
            t = list(pat)
            for k, d in zip(qs, combo): t[k] = d
            if t[0] != "0": out.add(int(("".join(t))))
    if pat.endswith("?") and pat[:-1].isdigit(): out.add(int(pat[:-1]))
    return out


def pick(pat, target):
    cs = sorted(cands(pat))
    if not cs: return None
    if target is None: return float(cs[len(cs) // 2])
    return float(min(cs, key=lambda c: abs(c - target)))


# razones tipicas por provincia (filas totalmente legibles): votos partidarios / votantes y votantes / inscriptos
RV, RP = {}, {}
for prov, g0 in cells.groupby("distrito"):
    ok = g0.groupby("unidad").filter(lambda x: (x.estado == "numero_legible").all())
    v = ok[ok.tipo == "votos"].valor.sum(); vo = ok[ok.variable == "Votantes"].valor.sum(); ins = ok[ok.variable == "Inscriptos"].valor.sum()
    RV[prov] = (v / vo) if vo else None
    RP[prov] = (vo / ins) if ins else None

canton = {}      # (prov, nombre) -> dict
for (prov, name), g in cells.groupby(["distrito", "unidad"], sort=False):
    row = dict(prov=prov, name=name, ins=None, vot=None, P={}, recon=[], flags=set())
    pend_v, pend_p = [], []
    for _, c in g.iterrows():
        e = c.estado
        if c.tipo == "padron":
            if e == "numero_legible":
                row["ins" if c.variable == "Inscriptos" else "vot"] = float(c.valor)
            elif e == "lectura_no_resuelta":
                pend_p.append(c)
            continue
        if e in ("numero_legible", "transcripcion_visual_previa"):
            row["P"][code_of(prov, c.variable)] = [float(c.valor), None]
        elif e == "subsumido_o_no_considerado":
            row["flags"].add("subsumido")
        elif e == "lectura_no_resuelta":
            pend_v.append(c)
        elif e == "sin_datos":
            row["flags"].add("sin_datos")
        elif e == "guion_sin_cifra":
            row["flags"].add("guion")
    rv = RV.get(prov) or 0.96
    # 1) votos partidarios ilegibles: Lupu-Stokes si encaja con la lectura > resto de la fila (Cordoba y San Luis, donde la suma iguala a votantes) > valor mas cercano a lo esperable
    todo = []
    for c in pend_v:
        pat = str(c.lectura).rstrip(); code = code_of(prov, c.variable); val = how = None
        for k, v in LUPU.items():
            if k[0] == prov and k[1] == name and c.variable in k[2].split(" + "):
                others = [x for x in k[2].split(" + ") if x != c.variable]
                if all(code_of(prov, x) in row["P"] for x in others):
                    rest = v - sum(row["P"][code_of(prov, x)][0] for x in others)
                    if rest >= 0 and rest in cands(pat): val, how = float(rest), "Lupu–Stokes"
        if val is None and prov in ("Córdoba", "San Luis") and row["vot"] is not None and len(pend_v) == 1:
            rest = row["vot"] - sum(v[0] for v in row["P"].values())
            if rest in cands(pat): val, how = float(rest), "resto de la fila"
        if val is not None:
            row["P"][code] = [val, how]; row["recon"].append("%s %s (%s)" % (c.variable, fmt_i(val), how))
        else:
            todo.append((c, pat, code))
    for c, pat, code in todo:
        known = sum(v[0] for v in row["P"].values())
        tgt = (rv * row["vot"] - known) / len(todo) if row["vot"] is not None else None
        if tgt is not None and tgt < 0: tgt = 0
        val = pick(pat, tgt)
        if val is not None:
            row["P"][code] = [val, "estimado"]; row["recon"].append("%s ≈ %s (estimado)" % (c.variable, fmt_i(val)))
        else:
            row["flags"].add("celda_perdida")
    # 2) votantes e inscriptos ilegibles
    for c in sorted(pend_p, key=lambda c: c.variable != "Votantes"):
        pat = str(c.lectura).rstrip()
        if c.variable == "Votantes":
            tgt = (sum(v[0] for v in row["P"].values()) / rv) if row["P"] else None
            val = pick(pat, tgt)
            if val is not None: row["vot"] = val
        else:
            rp = RP.get(prov)
            tgt = (row["vot"] / rp) if (row["vot"] is not None and rp) else None
            val = pick(pat, tgt)
            if val is not None: row["ins"] = val
        if val is not None: row["recon"].append("%s ≈ %s (estimado)" % (c.variable, fmt_i(val)))
    canton[(prov, name)] = row

# filas que Canton deja en blanco ("*", sin datos) y que el escrutinio de la junta electoral completa (votos del primer candidato de cada lista)
ACTA_LR = ("Cantón no trae votos para %s; se toman del acta de la Junta Escrutadora Nacional de La Rioja (Cámara de Diputados, expediente 9-D-1916, "
           "pp. PDF %s), mesa por mesa: %s. Votantes = sufragantes del acta.")
PRENSA = {   # (prov, nombre): (votos, votantes, nota)
    ("Jujuy", "Valle Grande"): ({"PRV": 165.0, "UCR": 111.0}, None,
        "Cantón no trae votos para Valle Grande; se toman del escrutinio de la junta electoral publicado en La Prensa del 8 de abril de 1916, p. 6 "
        "(«candidatos a diputados: provincial, 165; radical, 111»). Cierra con el acumulado de Puch y Claros del mismo despacho; inscriptos de Cantón."),
    ("La Rioja", "Independencia"): ({"PRV": 203.0, "UCR": 64.0}, 266.0,
        ACTA_LR % ("Independencia", "65-67", "mesa 1, de la Colina 75 y Baigorri 24; mesa 2, 69 y 15 (1 en blanco); mesa 3, 59 y 25 (2 sobres vacíos)")),
    ("La Rioja", "General Lamadrid"): ({"PRV": 150.0, "UCR": 155.0}, 308.0,
        ACTA_LR % ("General Lamadrid («General La Madrid» en el acta)", "163-165", "mesa 1, Baigorri 112 y de la Colina 90; mesa 2, 43 y 60 (3 sobres vacíos en total)")),
}
SIN_DATOS = {}
for k, (P, vot, why) in PRENSA.items():
    r = canton[k]
    r["P"] = {c: [v, None] for c, v in P.items()}
    r["flags"].discard("sin_datos"); r["prensa"] = why
    if vot is not None:
        r["vot"] = vot
        c = cells[(cells.distrito == k[0]) & (cells.unidad == k[1]) & (cells.variable == "Inscriptos")].iloc[0]
        if c.estado == "lectura_no_resuelta":   # inscriptos ilegibles: re-estimar con los votantes del acta
            rp = RP.get(k[0]); val = pick(str(c.lectura).rstrip(), vot / rp) if rp else None   # sin razon provincial no hay base para estimar
            r["ins"] = val if val is not None and val >= vot else None
            r["recon"] = [x for x in r["recon"] if not x.startswith("Inscriptos")]
            if r["ins"] is not None: r["recon"].append("Inscriptos ≈ %s (estimado)" % fmt_i(r["ins"]))

# ---- San Juan y Santiago del Estero: no hay cuadro de 1916 en las fuentes. Se toma la forma geográfica de la presidencial más cercana de Cantón:
#      San Juan 1922 (mapa1922/canton/p_SJ.txt) y Santiago del Estero 1928 (mapa1928/canton/p_SGO.txt; Cantón no trae 1922 para esa provincia).
PROXY = {"San Juan": (os.path.join(HERE, "..", "mapa1922", "canton", "p_SJ.txt"), ["UCR", "SOC", "BLO", "CNC"], "1922"),
         "Santiago del Estero": (os.path.join(HERE, "..", "mapa1928", "canton", "p_SGO.txt"), ["UCR", "ANT", "SOC", "BLA"], "1928")}
for _prov, (_path, _cols, _yr) in PROXY.items():
    for _ln in open(_path, encoding="utf8"):
        if _ln.startswith("#") or not _ln.strip(): continue
        _name, _vals = _ln.rstrip().split("|", 1)
        if _vals.strip() == "-": continue                      # fila subsumida (Chimbas, Zonda)
        _v = _vals.split()
        _row = dict(prov=_prov, name=_name, ins=float(_v[0]) if _v[0].isdigit() else None, vot=float(_v[1]) if _v[1].isdigit() else None,
                    P={c: [float(x), None] for c, x in zip(_cols, _v[2:]) if x.isdigit() and c != "BLA"}, recon=[], flags=set(), proxy=_yr)
        canton[(_prov, _name)] = _row
ALIAS.update({
    ("San Juan", "Ullún"): (["Ullum"], None),
    ("San Juan", "Angaco"): (["Angaco Norte"], "Angaco Norte (1914) es el actual Angaco (Cacopardo 1967)."),
    ("San Juan", "San Martín"): (["Angaco Sud"], "Angaco Sud (1914) pasó a ser San Martín (Cacopardo 1967)."),
    ("San Juan", "Rawson"): (["Trinidad"], "Rawson se formó con los distritos 2 y 3 del extinguido Trinidad; el distrito 1 pasó a Capital (Cacopardo 1967). Asignación aproximada."),
    ("San Juan", "Capital"): (["Capital", "Concepción", "Desamparados", "Chimbas"], "Chimbas: Cantón (t. I, Apéndice C) incluye sus datos en Concepción, que en esta base recibe el dato de la Capital. Concepción y Desamparados, que la base de 1914 dibuja aparte, reciben el mismo dato (Cacopardo 1967)."),
    ("Santiago del Estero", "General Taboada"): (["28 de Marzo"], "28 de Marzo (1914) es el actual General Taboada (Cacopardo 1967)."),
})
unit_src, unmapped = {}, []
for (prov, n), r in canton.items():
    if prov == "Capital Federal":
        k = CAP_CIRC.get(norm(n))
        idx = [KEY[("Capital Federal", norm("Circ. %02d" % k))]] if k else []
        why = None
    elif (prov, n) in ALIAS:
        names, why = ALIAS[(prov, n)]
        idx = [KEY[(prov, norm(x))] for x in names]
    else:
        k = (prov, norm(n))
        idx, why = ([KEY[k]] if k in KEY else []), None
    if not idx:
        if r["P"]: unmapped.append(r)
        continue
    for i in idx:
        assert i not in unit_src, (prov, n, U[i]["name"])
        unit_src[i] = (r, why, len(idx))

LOS_ANDES = {("Catamarca", "Antofagasta de la Sierra"), ("Jujuy", "Susques"), ("Salta", "Pastos Grandes"), ("Salta", "San Antonio de los Cobres")}
PENDIENTES = {"San Juan", "Santiago del Estero"}

# ---- Salta: planilla del 15 de abril de 1916 (exp. 58-D-1916), 38 colegios -> 21 departamentos de 1914 (agrupacion = hipotesis del paquete 1916dip)
# Partidos (Wikipedia, Elecciones legislativas de 1916): Usandivaras-Cornejo = Union Provincial; Outes-Echazu = UCR; Lesser-Piniella = Socialista.
SA_COL = pd.read_csv(os.path.join(SRC, "colegios_diputados_15abril.csv"), encoding="utf-8-sig")
SA_MAP = pd.read_csv(os.path.join(SRC, "correspondencias_colegios.csv"), encoding="utf-8-sig")
SA_ALL = pd.read_csv(os.path.join(SRC, "diputados_por_colegio_todas_columnas.csv"), encoding="utf-8-sig")
SA_DEP = dict(zip(SA_MAP.colegio_numero, SA_MAP.departamento_candidato))
SA_SOC = SA_ALL[SA_ALL.candidato == "Eliseo M. Lesser"].set_index("colegio_numero").votos.fillna(0).to_dict()
salta = {}
for _, r in SA_COL.iterrows():
    d = SA_DEP[r.colegio_numero]
    s_ = salta.setdefault(d, dict(UPV=0, UCR=0, SOC=0, suf=0, col=[]))
    s_["UPV"] += int(r["Agustín Usandivaras"]); s_["UCR"] += int(r["Carlos Outes"]); s_["SOC"] += int(SA_SOC.get(r.colegio_numero, 0))
    s_["suf"] += int(r.sufragantes); s_["col"].append(r.colegio_nombre)
salta_idx = {KEY[("Salta", norm(d))]: s_ for d, s_ in salta.items()}
assert len(salta_idx) == 21, len(salta_idx)
SALTA_NOTE = ("Colegios electorales: %s. Votos del primer candidato de cada lista (Usandivaras: Unión Provincial; Outes: UCR; Lesser: Socialista), planilla del 15 de abril (exp. 58-D-1916); "
              "los partidos son los de la Wikipedia y la agrupación de colegios en departamentos es una hipótesis.")

# ---------------------------------------------------------------- LÍNEA ALTERNATIVA
# Objetivo: tabla provincial del docx (lore_1916.docx, validada en tabla.py). Forma geográfica: Cantón (1968), diputados nacionales 1916.
# Cada partido de Cantón se reescala, departamento por departamento, hasta que la provincia dé exactamente la cifra de la tabla.
BLOCS = ["UCR", "PDP", "PS", "CC", "RAD"]
TAB = json.load(open(os.path.join(HERE, "tabla_1916fic.json"), encoding="utf8"))
TGT = TAB["prov"]
for _p, _d in TGT.items():   # Jujuy: 3.501 + 3.970 + 1.298 + 227 = 8.996, la tabla imprime 8.993 (se usa la suma)
    _d["VOT"] = _d["UCR"] + _d["PDP"] + _d["PS"] + _d["CC"] + _d["RAD"] + _d["BLA"]

# cómo se lee cada columna de Cantón en la línea alternativa (códigos de Cantón; ver CODE arriba)
#   dlt: pasa a De la Torre | cc: pasa a la Concentración Conservadora | split: lista única que se reparte entre ambos
CFG = {
    "Buenos Aires": dict(split=["CNS"]),
    "Capital Federal": dict(dlt=["PDP"]),
    "Catamarca": dict(dlt=["CNC"]),
    "Córdoba": dict(dlt=["DEM"]),
    "Corrientes": dict(dlt=["LIB"], cc=["AUT"]),         # liberales (Pacto Autonomista-Liberal) con De la Torre; autonomistas con el ex-PAN
    "Entre Ríos": dict(dlt=["CNC"]),
    "Jujuy": dict(split=["PRV"]),
    "La Rioja": dict(dlt=["PRV"]),
    "Mendoza": dict(dlt=["CNS"]),
    "Salta": dict(dlt=["UPV"]),
    "San Luis": dict(dlt=["DEM"], cc=["UPO"]),           # «Demócrata» con De la Torre; Unión Popular con la disidencia
    "Santa Fe": dict(dlt=["PDP"], rad=["RDI"]),
    "Tucumán": dict(split=["CNS"]),
    "San Juan": dict(ucr=["UCR", "BLO"], dlt=["CNC"]),    # forma de 1922: radicales (UCR + bloquistas) con Yrigoyen, Concentración con De la Torre
    "Santiago del Estero": dict(ucr=["UCR"], cc=["ANT"]),  # forma de 1928: UCR con Yrigoyen, antipersonalistas con el ex-PAN (no hay De la Torre en la tabla)
}
PROXY_NOTE = {
    "San Juan": "San Juan no tiene cuadro por departamento de 1916 en las fuentes: la forma geográfica sale de la presidencial de 1922 (Cantón t. II, p. PDF 82). Radicales (UCR + bloquistas) = Yrigoyen; Concentración = De la Torre; socialistas = Justo. El inscripto es el «reconstruido» de Cantón.",
    "Santiago del Estero": "Santiago del Estero no tiene cuadro por departamento de 1916 ni de 1922 (Cantón no lo trae): la forma geográfica sale de la presidencial de 1928 (Cantón t. II, p. PDF 121). UCR = Yrigoyen; antipersonalistas = ex-PAN; socialistas = Justo.",
}
FLAT = set()
UCR_C = ("UCR", "RSI")


def lrm(vals, total):
    """reparte `total` en enteros proporcionalmente a `vals` (restos mayores); suma exacta"""
    total = int(total); s = float(sum(vals))
    if total == 0 or not vals: return [0] * len(vals)
    if s <= 0: vals, s = [1.0] * len(vals), float(len(vals))
    raw = [v * total / s for v in vals]; fl = [int(math.floor(x)) for x in raw]
    for i in sorted(range(len(vals)), key=lambda i: -(raw[i] - fl[i]))[:total - sum(fl)]: fl[i] += 1
    return fl


# filas reales por provincia: clave (prov, nombre de Cantón) o ("Salta", depto)
REAL = {}
for (prov, n), r in canton.items():
    if prov in FLAT or not r["P"]: continue
    REAL.setdefault(prov, {})[(prov, n)] = dict(P={c: x[0] for c, x in r["P"].items()}, ins=r["ins"], vot=r["vot"])
REAL["Salta"] = {("Salta", d): dict(P=dict(UPV=float(s_["UPV"]), UCR=float(s_["UCR"]), SOC=float(s_["SOC"])), ins=None, vot=float(s_["suf"])) for d, s_ in salta.items()}
SPLIT_B = 1.2    # pendiente del reparto De la Torre / ex-PAN según el tamaño del departamento


def split_share(K, tdlt):
    """parte de De la Torre en cada departamento: más alta en los grandes (el PDP se apoya en los centros urbanos, la disidencia en el interior);
    el nivel se calibra para que la provincia dé tdlt"""
    L = [math.log(k + 1.0) for k in K]; m = sum(L) / len(L); sd = (sum((x - m) ** 2 for x in L) / len(L)) ** .5 or 1.0
    z = [(x - m) / sd for x in L]
    lo, hi = -40.0, 40.0
    for _ in range(80):
        a = (lo + hi) / 2
        t = sum(k / (1 + math.exp(-(a + SPLIT_B * zi))) for k, zi in zip(K, z))
        lo, hi = (a, hi) if t < tdlt else (lo, a)
    return [1 / (1 + math.exp(-(a + SPLIT_B * zi))) for zi in z]


def fit_reg(w, v, total, cap=0.92):
    """padrón por departamento ∝ w, con participación máxima `cap`; suma `total`"""
    lock = set()
    while True:
        free = [i for i in range(len(w)) if i not in lock]
        rest = total - sum(v[i] / cap for i in lock); sw = sum(w[i] for i in free)
        assert rest > 0 and sw > 0
        r = [v[i] / cap if i in lock else w[i] * rest / sw for i in range(len(w))]
        new = [i for i in free if v[i] > cap * r[i]]
        if not new: return r
        lock.update(new)


ALT = {}      # (prov, clave) -> dict(P=votos por candidato, BLA, ins, vot)
for prov, rows in REAL.items():
    T = TGT[prov]; cfg = CFG[prov]; keys = list(rows)
    src = {k: dict(UCR=sum(rows[k]["P"].get(c, 0) for c in cfg.get("ucr", UCR_C)), DLT=sum(rows[k]["P"].get(c, 0) for c in cfg.get("dlt", [])),
                   CC=sum(rows[k]["P"].get(c, 0) for c in cfg.get("cc", [])), SPL=sum(rows[k]["P"].get(c, 0) for c in cfg.get("split", [])),
                   RAD=sum(rows[k]["P"].get(c, 0) for c in cfg.get("rad", [])), PS=sum(rows[k]["P"].get(c, 0) for c in cfg.get("ps", ["SOC"]))) for k in keys}
    w_all = [sum(src[k][c] for c in ("UCR", "DLT", "CC", "SPL", "RAD", "PS")) for k in keys]     # peso de reserva: tamaño real del departamento

    def col(code, target):
        w = [src[k][code] for k in keys]
        return lrm(w if sum(w) > 0 else w_all, target)

    ucr = col("UCR", T["UCR"]); ps = col("PS", T["PS"]); rad = col("RAD", T["RAD"])
    if "split" in cfg:
        K = lrm([src[k]["SPL"] for k in keys], T["PDP"] + T["CC"])
        sh = split_share(K, T["PDP"])
        dlt = lrm([k_ * s_ for k_, s_ in zip(K, sh)], T["PDP"])
        cc = [k_ - d_ for k_, d_ in zip(K, dlt)]
    else:
        dlt = col("DLT", T["PDP"]); cc = col("CC", T["CC"])
    pos = [ucr[i] + ps[i] + rad[i] + dlt[i] + cc[i] for i in range(len(keys))]
    bla = lrm(pos, T["BLA"])
    vot = [pos[i] + bla[i] for i in range(len(keys))]
    wins_ = [rows[k]["ins"] if rows[k]["ins"] else None for k in keys]
    # inscriptos: los de Cantón reescalados al total provincial; donde Cantón no los trae se reparten según los votantes
    if all(w is None for w in wins_):
        reg = lrm([rows[k]["vot"] or vot[i] for i, k in enumerate(keys)], T["REG"])
    else:
        mean_p = sum(vot[i] for i, w in enumerate(wins_) if w) / sum(w for w in wins_ if w)
        # donde Cantón trae un padrón ilegible o más chico que los votos reescalados (La Rioja, cuyo cuadro está incompleto; San Juan con el padrón de 1922),
        # el padrón del departamento se fija en el mínimo que permite votar y el resto se reescala para que la provincia dé la tabla
        reg = lrm(fit_reg([w if w else vot[i] / mean_p for i, w in enumerate(wins_)], vot, T["REG"]), T["REG"])
    for i, k in enumerate(keys):
        ALT[k] = dict(P={"UCR": ucr[i], "PDP": dlt[i], "PS": ps[i], "CC": cc[i], "RAD": rad[i]}, BLA=bla[i], vot=vot[i], ins=reg[i])
    for c in ("UCR", "PDP", "PS", "CC", "RAD"):
        assert sum(ALT[k]["P"][c] for k in keys) == T[c], (prov, c)
    assert sum(ALT[k]["BLA"] for k in keys) == T["BLA"] and sum(ALT[k]["vot"] for k in keys) == T["VOT"] and sum(ALT[k]["ins"] for k in keys) == T["REG"], prov
print("provincias reescaladas:", len(REAL), file=sys.stderr)

CAND = {
    "UCR": dict(n="Hipólito Yrigoyen", sub="Unión Cívica Radical", logo="UCR", base="#e10019"),
    "PDP": dict(n="Lisandro de la Torre", sub="Partido Demócrata Progresista", logo="PDP", base="#005c9e"),
    "PS": dict(n="Juan B. Justo", sub="Partido Socialista", logo="PS", base="#ff9900", bar="#e08700", txt="#b87500"),
    "CC": dict(n="Ex-PAN", sub="Concentración Conservadora", logo="PAN", base="#30d5c8", bar="#1fa89d", txt="#1a8f86"),
    "RAD": dict(n="UCR Disidente", sub="Sin candidato · Santa Fe", logo="UCRD", base="#dd8a59", bar="#dd8a59", txt="#c8703a"),   # color del cartel
    "BLA": dict(n="En blanco", base="#9a9a9a", minor=True),
}
LOGOS = os.path.join(HERE, "..", "../logos")
LOGOS_FIC = os.path.join(HERE, "logos")


def _logo(path, ar):
    import base64
    t = open(path, encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar)


CAND["UCR"].update(_logo(os.path.join(LOGOS_FIC, "ucr_bandera_circular.svg"), 1.0))      # los emblemas del cartel: bandera circular de la UCR…
CAND["RAD"].update(_logo(os.path.join(LOGOS_FIC, "ucr_bandera_circular.svg"), 1.0))      # …repetida en la UCR disidente, como en el cartel
CAND["CC"].update(_logo(os.path.join(LOGOS_FIC, "pan_escarapela.svg"), 1.0))             # escarapela «P.A.N.» (redibujada del cartel)
CAND["PDP"].update(_logo(os.path.join(LOGOS, "Escudo_del_PDP.svg"), 1.0))
CAND["PS"].update(_logo(os.path.join(LOGOS, "Emblema_del_Partido_Socialista_Argentino.svg"), 1.0))
GREY_T, GREY_N = "#cfcfcf", "#8c8c8c"
KEYS = [[GREY_T, "Territorio nacional: no votaba"], [GREY_N, "Cifras subsumidas en otra unidad"]]


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def analyse(P, bla, ins, vot):
    D = sum(P.values())
    return dict(P=dict(P), bla=bla, ins=ins, vot=vot, D=D or None, E=D + bla)


def rec_from(a, note=None, extra_metrics=(), sections=None):
    D = a["D"]
    if not D: return None
    P = a["P"]
    lines = [[c, int(x), round(100 * x / D, 2)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x > 0]
    if a["bla"] > 0: lines.append(["BLA", int(a["bla"]), round(100 * a["bla"] / a["E"], 2)])
    met = list(extra_metrics)
    if a["ins"]: met.append(["Inscriptos", fmt_n(a["ins"])])
    met.append(["Votantes", fmt_n(a["vot"])])
    if a["ins"]: met.append(["Participación", fmt_p(100 * a["vot"] / a["ins"]) + " %"])
    w = max(P, key=lambda c: P[c])
    rec = dict(lines=lines, metrics=met, w=w, q=round(100 * P[w] / D, 2))
    if sections: rec["sections"] = sections
    if note: rec["note"] = note
    return rec


METHOD = ("Línea alternativa: los votos de Cantón (diputados 1916) de cada departamento se reescalaron para que la provincia dé la cifra de la tabla de la alt-timeline; "
          "los votos sacados a la UCR quedan en blanco o no votaron, no pasan a otra lista.")
SPLIT_NOTE = ("El reparto de la derecha entre De la Torre y la Concentración Conservadora es una estimación: Cantón trae una sola lista conservadora, y la parte de De la Torre "
              "se hizo más alta en los departamentos grandes.")
DIRECT_NOTE = {"Corrientes": "Liberales (Cantón) = De la Torre; autonomistas = Concentración Conservadora.",
               "San Luis": "«Demócrata» (Cantón) = De la Torre; Unión Popular = Concentración Conservadora."}

prov_an = {}
for prov, T in TGT.items():
    prov_an[prov] = analyse({c: T[c] for c in BLOCS}, T["BLA"], T["REG"], T["VOT"])

ELEC = {"UCR": "ELU", "PDP": "ELP", "PS": "ELS", "CC": "ELC", "RAD": "ELR"}
ELNAME = {"UCR": "Yrigoyen (UCR)", "PDP": "De la Torre (PDP)", "PS": "Justo (PS)", "CC": "Ex-PAN (Concentración Conservadora)", "RAD": "UCR Disidente"}
prov_rec = {}
for p in PROVS:
    if p in geom.TERR:
        prov_rec[p] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1916: sin voto."}
        continue
    T = TGT[p]
    sec = [dict(title="Colegio Electoral (%d electores)" % T["EL"], rows=[[ELNAME[c], "%d" % T[e]] for c, e in ELEC.items() if T[e]]),
           dict(title="Votación final del Colegio Electoral", rows=[[n_, "%d" % v_] for n_, v_ in (("Yrigoyen", T["ELU"]), ("De la Torre (PDP + ex-PAN + UCR Disidente)", T["ELP"] + T["ELC"] + T["ELR"]), ("Justo", T["ELS"])) if v_])]
    note = METHOD + (" " + PROXY_NOTE[p] if p in PROXY_NOTE else "")
    prov_rec[p] = rec_from(prov_an[p], note, [["Electores", str(T["EL"])]], sec)

unit_rec, unit_an = {}, {}
for i, u in enumerate(U):
    p = u["prov"]
    if p in geom.TERR:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1916: sus habitantes no votaban."}
    elif (p, u["name"]) in LOS_ANDES:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio Nacional de Los Andes (1900-1943): sus habitantes no votaban (Cacopardo 1967)."}
    elif i in salta_idx:
        k = [k for k in REAL["Salta"] if norm(k[1]) == norm(U[i]["name"])][0]; al = ALT[k]
        a = analyse(al["P"], al["BLA"], al["ins"], al["vot"]); unit_an[i] = a
        unit_rec[i] = rec_from(a, "Colegios electorales: %s. " % ", ".join(salta_idx[i]["col"]) + METHOD)
    elif i in unit_src:
        r, why, n = unit_src[i]
        k = (p, r["name"])
        if k not in ALT:
            if "sin_datos" in r["flags"]:
                unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón no trae votos para «%s» (celdas «*», sin datos)." % r["name"]}
            else:
                unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón marca las cifras de «%s» como subsumidas bajo una unidad mayor o no tomadas en cuenta." % r["name"]}
            continue
        al = ALT[k]; a = analyse(al["P"], al["BLA"], al["ins"], al["vot"]); unit_an[i] = a
        extras = []
        if r.get("prensa"): extras.append(r["prensa"])
        if norm(r["name"]) != norm(u["name"]) and p != "Capital Federal": extras.append("Nombre en Cantón: «%s»." % r["name"])
        if why: extras.append(why)
        if n > 1: extras.append("Dato único compartido por %d polígonos." % n)
        if r["recon"]: extras.append("Cifra(s) ilegible(s) en la fuente, reconstruida(s): " + "; ".join(r["recon"]) + ".")
        if "split" in CFG[p]: extras.append(SPLIT_NOTE)
        if p in DIRECT_NOTE: extras.append(DIRECT_NOTE[p])
        if p in PROXY_NOTE: extras.append(PROXY_NOTE[p])
        extras.append(METHOD)
        unit_rec[i] = rec_from(a, " ".join(extras))
    else:
        unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Sin fila para esta unidad en Cantón (1916)."}

disp = {}
for i, (r, why, n) in unit_src.items():
    p = U[i]["prov"]
    disp[i] = ("Circunscripción %d · %s" % (CAP_CIRC[norm(r["name"])], r["name"])) if p == "Capital Federal" else (r["name"] if n == 1 else U[i]["name"])

# resultado nacional: suma de la tabla provincial
NV = {c: sum(TGT[p][c] for p in TGT) for c in BLOCS}
NPOS, NBLA = sum(NV.values()), sum(TGT[p]["BLA"] for p in TGT)
NVOT, NREG = sum(TGT[p]["VOT"] for p in TGT), sum(TGT[p]["REG"] for p in TGT)
NEL = {c: sum(TGT[p][e] for p in TGT) for c, e in ELEC.items()}
cands = sorted([{"code": c, "votes": v, "pct": round(100 * v / NPOS, 2)} for c, v in NV.items()], key=lambda x: -x["votes"])
slices = [{"code": c["code"], "v": c["votes"]} for c in cands]
partp = round(100 * NVOT / NREG, 2)
NAT_MET = [["Inscriptos", fmt_n(NREG)], ["Votantes", fmt_n(NVOT)], ["Participación", fmt_p(partp) + " %"], ["Votos positivos", fmt_n(NPOS)], ["En blanco", fmt_n(NBLA)],
           ["Voto popular", "Yrigoyen"], ["Presidente electo (C.E.)", "De la Torre"]]
print("pais:", NV, "positivos", NPOS, "votantes", NVOT, "electores", NEL, file=sys.stderr)


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


NOTE = ("LÍNEA ALTERNATIVA (ficticia). Resultados provinciales: tabla de la alt-timeline (lore_1916.docx). Departamentos: votos reales de diputados nacionales 1916 (Cantón 1968, t. II; Salta: exp. 58-D-1916; San Juan: presidencial 1922; Santiago del Estero: presidencial 1928) "
        "reescalados hasta que cada provincia dé la cifra de la tabla; son estimaciones, no resultados observados. " + METHOD + " Geometría: departamentos del censo de 1914.")


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(U)):
        r = unit_rec[i]; a = unit_an.get(i)
        p = fn(a) if (a and a["D"]) else None
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(p, edges)] if p is not None else r.get("fill", GREY_N)
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        if p in geom.TERR: prov[p] = r; continue
        v = fn(prov_an[p])
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


NAT = dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET)
MODES = [dict(id="gan", tile="GANÓ", set="1", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec, national=NAT, legend=dict(keys=KEYS))]
for mid, tile, st, fn, base, edges, title in (
    ("ucr", "UCR", "1", lambda a: 100 * a["P"]["UCR"] / a["D"], "#e10019", [0, 15, 30, 40, 50, 60, 70], "% Yrigoyen (UCR)"),
    ("pdp", "PDP", "1", lambda a: 100 * a["P"]["PDP"] / a["D"], "#005c9e", [0, 15, 30, 40, 50, 60, 70], "% De la Torre (PDP)"),
    ("ps", "PS", "2", lambda a: 100 * a["P"]["PS"] / a["D"], "#e08700", [0, 2, 5, 10, 20, 30, 40], "% Justo (PS)"),
    ("cc", "CC", "2", lambda a: 100 * a["P"]["CC"] / a["D"], "#1fa89d", [0, 5, 15, 30, 40, 50, 60], "% Ex-PAN (Concentración Conservadora)"),
    ("par", "PART", "2", lambda a: (100 * a["vot"] / a["ins"]) if a["ins"] else None, "#2a6f97", [0, 30, 40, 50, 60, 70, 80], "Participación (votantes / inscriptos)")):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, set=st, note=NOTE, units=un, prov=pv, national=NAT, legend=lg))



# ---------------------------------------------------------------- ADDENDUM: Colegio Electoral
CE_COL = {"UCR": "#e10019", "PDP": "#005c9e", "PS": "#ff9900", "CC": "#30d5c8", "RAD": "#dd8a59"}
CE_TXT = "#616262"


def hemicycle(cx, cy, R, r0, rows, parts, dot):
    """parlamento de 300 puntos: filas con puntos proporcionales al radio, ordenados por ángulo de izquierda a derecha; `parts` = [(color, escaños)] en ese orden"""
    N = sum(n for _, n in parts)
    rr = [r0 + (R - r0) * i / (rows - 1) for i in range(rows)]
    cnt = lrm(rr, N)
    seats = []
    for r, n in zip(rr, cnt):
        for k in range(n):
            th = math.pi * (1 - (k + 0.5) / n)
            seats.append((-th, r, cx + r * math.cos(th), cy - r * math.sin(th)))
    seats.sort(key=lambda t: (t[0], t[1]))
    out, i = [], 0
    for col, n in parts:
        out.append('<g fill="%s">' % col + "".join('<circle cx="%.1f" cy="%.1f" r="%s"/>' % (x, y, dot) for _, _, x, y in seats[i:i + n]) + "</g>")
        i += n
    return "".join(out)


def _t(x, y, txt, size=16, anchor="start", bold=False, fill=CE_TXT, italic=False):
    return '<text x="%s" y="%s" font-size="%s" text-anchor="%s" fill="%s"%s%s>%s</text>' % (
        x, y, size, anchor, fill, ' font-weight="700"' if bold else "", ' font-style="italic"' if italic else "", txt)


NEL_ = {c: NEL[c] for c in BLOCS}
DLT_E = NEL_["PDP"] + NEL_["CC"] + NEL_["RAD"]
assert DLT_E == 159 and NEL_["UCR"] == 127 and NEL_["PS"] == 14 and DLT_E + NEL_["UCR"] + NEL_["PS"] == 300
XA, XB, CY = 1465, 1700, 305
ce = ['<g id="ce">']
ce.append(_t(XA, 168, "Colegio Electoral", 22, "middle", True))
ce.append(hemicycle(XA, CY, 108, 44, 9, [(CE_COL["PS"], NEL_["PS"]), (CE_COL["UCR"], NEL_["UCR"]), (CE_COL["RAD"], NEL_["RAD"]), (CE_COL["PDP"], NEL_["PDP"]), (CE_COL["CC"], NEL_["CC"])], 3.1))
ce.append(_t(XA, CY - 6, "300", 36, "middle", True))
ce.append(_t(XB, 168, "Votación final del C.E.", 22, "middle", True))
ce.append(hemicycle(XB, CY, 108, 44, 9, [(CE_COL["PS"], NEL_["PS"]), (CE_COL["UCR"], NEL_["UCR"]), (CE_COL["PDP"], DLT_E)], 3.1))
ce.append(_t(XB, CY - 6, "300", 36, "middle", True))
# convenciones bajo el primer hemiciclo
y = 346
for c, lab in (("UCR", "Yrigoyen · UCR"), ("PDP", "De la Torre · PDP"), ("PS", "Justo · PS"), ("CC", "Ex-PAN"), ("RAD", "UCR Disidente")):
    ce.append('<rect x="1357" y="%d" width="12" height="12" fill="%s"/>' % (y - 11, CE_COL[c]))
    ce.append(_t(1377, y, lab, 15))
    ce.append(_t(1573, y, NEL_[c], 15, "end", True))
    y += 22
# resultado de la votación final
y = 352
for lab, v in (("De la Torre", DLT_E), ("Yrigoyen", NEL_["UCR"]), ("Justo", NEL_["PS"])):
    ce.append(_t(1612, y, lab, 20, "start", True)); ce.append(_t(1812, y, v, 20, "end", True)); y += 30
ce.append(_t(1712, 462, "151 votos para la", 17, "middle", True)); ce.append(_t(1712, 482, "presidencia", 17, "middle", True))
# cómo se armó el voto de De la Torre
W, X0, Yb = 520, 1357, 528
ce.append(_t(X0, Yb - 10, "Los 159 votos de De la Torre en el Colegio Electoral", 16, "start", True))
x = X0
for c, n, lab in (("PDP", NEL_["PDP"], "PDP 121"), ("CC", NEL_["CC"], "CC 19"), ("RAD", NEL_["RAD"], "UCRD 19")):
    w = W * n / DLT_E
    ce.append('<rect x="%.1f" y="%d" width="%.1f" height="26" fill="%s"/>' % (x, Yb, w, CE_COL[c]))
    ce.append(_t("%.1f" % (x + w / 2), Yb + 18, lab, 13, "middle", True, "#fff" if c != "CC" else "#0b4f4a"))
    x += w
for i_, txt in enumerate(("Yrigoyen ganó el voto popular (%s %%) pero quedó con %d electores," % (("%.2f" % (100 * NV["UCR"] / NPOS)).replace(".", ","), NEL_["UCR"]),
                          "lejos de los 151 necesarios. De la Torre (%s %%) fue electo" % ("%.2f" % (100 * NV["PDP"] / NPOS)).replace(".", ","),
                          "presidente por coalición: a sus 121 electores del PDP se",
                          "sumaron los 19 del ex-PAN y los 19 de la UCR Disidente.")):
    ce.append(_t(X0, 590 + 23 * i_, txt, 16, "start", i_ == 0))
ce.append("</g>")
CE_SVG = "".join(ce)

ORD = ["Buenos Aires", "Capital Federal", "Catamarca", "Córdoba", "Corrientes", "Entre Ríos", "Jujuy", "La Rioja", "Mendoza", "Salta", "San Juan", "San Luis", "Santa Fe", "Santiago del Estero", "Tucumán"]
rows_ = []
for pv in ORD:
    T = TGT[pv]
    rows_.append("<tr><th>%s</th><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=f>%s</td><td class=f>%s</td><td class=f>%s</td></tr>" % (
        pv, T["EL"], T["ELU"] or "·", T["ELP"] or "·", T["ELS"] or "·", T["ELC"] or "·", T["ELR"] or "·",
        T["ELU"] or "·", (T["ELP"] + T["ELC"] + T["ELR"]) or "·", T["ELS"] or "·"))
rows_.append("<tr class=t><th>Total</th><td>300</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td class=f>%d</td><td class=f>%d</td><td class=f>%d</td></tr>" % (
    NEL_["UCR"], NEL_["PDP"], NEL_["PS"], NEL_["CC"], NEL_["RAD"], NEL_["UCR"], DLT_E, NEL_["PS"]))
CE_HTML = ('<section id="addendum"><h2>Addendum · el Colegio Electoral</h2>'
           '<p><b>Yrigoyen ganó el voto popular</b> (%s %% de los votos positivos, contra %s %% de De la Torre), pero ninguna lista alcanzó los 151 electores. '
           '<b>De la Torre fue electo presidente por coalición</b>: sus 121 electores del PDP, más los 19 del ex-PAN (Concentración Conservadora, que decidió apoyar al binomio demoprogresista) '
           'y los 19 de la UCR Disidente de Santa Fe (que devolvió el favor del PDP en la elección a gobernador) dieron 159 votos. Yrigoyen se quedó con sus 127 electores y Justo con los 14 de la Capital.</p>'
           '<table><thead><tr><th rowspan=2>Provincia</th><th rowspan=2>Electores</th><th colspan=5>Electores elegidos por lista</th><th colspan=3>Votación final</th></tr>'
           '<tr><th>UCR</th><th>PDP</th><th>PS</th><th>Ex-PAN</th><th>UCRD</th><th class=f>Yrigoyen</th><th class=f>De la Torre</th><th class=f>Justo</th></tr></thead><tbody>%s</tbody></table>'
           '<p class=n>Mayoría necesaria: 151 de 300. Línea alternativa (ficticia): el Colegio Electoral y su votación son los del documento de la alt-timeline (lore_1916.docx).</p></section>') % (
    ("%.2f" % (100 * NV["UCR"] / NPOS)).replace(".", ","), ("%.2f" % (100 * NV["PDP"] / NPOS)).replace(".", ","), "".join(rows_))
CE_CSS = """#addendum{max-width:1100px;margin:34px auto 10px;padding:0 6px;color:var(--fg);font-size:15px;line-height:1.5}
#addendum h2{font-size:24px;margin:0 0 8px}
#addendum table{border-collapse:collapse;margin:14px 0 6px;width:100%;font-size:14px}
#addendum th,#addendum td{padding:4px 9px;border-bottom:1px solid var(--line);text-align:right}
#addendum th:first-child{text-align:left}
#addendum thead th{text-align:center;color:var(--mut);font-weight:600}
#addendum .f{background:rgba(112,166,215,.12)}
#addendum tr.t th,#addendum tr.t td{font-weight:700;border-top:2px solid var(--line)}
#addendum .n{color:var(--mut);font-size:13px}
body.bare #addendum{display:none}
"""


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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
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
    slug="presidenciales_1916_alt", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de Argentina de", year="1916",
    labels=dict(pie1="Proporción sobre votos positivos", won="MÁS VOTADO"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="Result.", subtitle="Alt-timeline · estimado"), "2": dict(label="Otros", subtitle="Alt-timeline · estimado")},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(HERE, "dataset_1916fic.json"), "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Presidenciales 1916 (alt)</title>")
sub("<!-- Exterior -->", CE_SVG + "\n<!-- Exterior -->")
sub("</svg>\n</div>\n<div id=\"card\"", "</svg>\n" + CE_HTML + "\n</div>\n<div id=\"card\"")
sub("body.bare #bar{display:none}body.bare #wrap{padding:0;max-width:none}\n</style>", "body.bare #bar{display:none}body.bare #wrap{padding:0;max-width:none}\n" + CE_CSS + "</style>")
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
# leyenda mas alta: caben 6 bloques + 5 claves de color
sub('el("text",{x:93,y:1266,"font-size":20,fill:"#616161"}', 'el("text",{x:93,y:1056,"font-size":20,fill:"#616161"}')
sub("  let y=1292;", "  let y=1082;")
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(HERE, "atlas_1916_alt.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)

