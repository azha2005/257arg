#!/usr/bin/env python3
"""Atlas electoral de diputados nacionales 1916 (estilo Wikipedia 1999) sobre los departamentos del censo de 1914.

    python build_1916.py            -> mapa1916dip/atlas_1916_diputados.html (+ dataset_1916.json)

Datos     : ../1916dip (Canton 1968 t. II transcripto + expediente de Salta 58-D-1916); Lupu-Stokes solo para cifras ilegibles.
Geometria : Departamentos_1914 (cache units_raw.pkl).  Nombres: Cacopardo (1967), Cuadro 1.
"""
import sys, os, re, json, math, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, shapely
from shapely.ops import unary_union
import geom
from names import norm

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_SRC = os.path.join(HERE, "..", ".claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

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
SRC = os.path.join(HERE, "..", "1916dip")
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
PENDIENTES = set()
# San Juan y Santiago del Estero: Canton no trae su cuadro departamental, pero la Wikipedia trae el total provincial (expedientes 53-D-1916 y 7-D-1916 de la Camara de Diputados).
# El mapa pinta toda la provincia con ese resultado, sin mostrar los departamentos (DATA.solid). Los "otros" de San Juan (10 votos) quedan en "no atribuido".
PROV_ONLY = {"San Juan": dict(P={"CNS": 9244.0, "UCR": 7742.0, "SOC": 383.0}, ins=23379.0, vot=17750.0, exp="53-D-1916", lab="Partido Conservador 9.244 (53,2 %), UCR 7.742 (44,6 %), Socialista 383 (2,2 %)"),
             "Santiago del Estero": dict(P={"DEM": 15146.0, "UCR": 14721.0, "PDP": 1842.0, "SOC": 303.0}, ins=56599.0, vot=32012.0, exp="7-D-1916", lab="Unión Democrática 15.146 (47,3 %), UCR 14.721 (46,0 %), Demócrata Progresista 1.842 (5,8 %), Socialista 303 (0,9 %)")}
SOLID = set(PROV_ONLY)
PROV_NOTE = {p: "Total provincial según la Wikipedia (expediente %s de la Cámara de Diputados): %s. Cantón no trae el cuadro departamental: el mapa pinta toda la provincia con este resultado." % (v["exp"], v["lab"]) for p, v in PROV_ONLY.items()}

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

BLOCS = ["UCR", "CON", "PDP", "SOC", "SAR", "RAD", "CCI"]
CAND = {
    "UCR": dict(n="Unión Cívica Radical", sub="UCR y radicales situacionistas", logo="UCR", base="#e10019"),
    "CON": dict(n="Concentración Conservadora", sub="Conservadores y partidos provinciales", logo="CC", base="#30d5c8", bar="#1fa89d", txt="#1a8f86"),
    "PDP": dict(n="Demócrata Progresista", sub="Partido Demócrata Progresista", logo="PDP", base="#005c9e"),
    "SOC": dict(n="Partido Socialista", sub="Socialistas", logo="PS", base="#ff9900", bar="#e08700", txt="#b87500"),
    "SAR": dict(n="Socialista Argentino", sub="Capital (distinto del PS)", logo="PSA", base="#ff6700", bar="#e05a00", txt="#c24e00"),
    "RAD": dict(n="UCR Disidente", sub="Santa Fe", logo="UCRD", base="#a52a2a"),
    "CCI": dict(n="Concentración Cívica", sub="Corrientes", logo="CCi", base="#35aae0", bar="#2a93c4", txt="#1f7aa6"),
}
for c, col in PCOL.items():
    CAND["P_" + c] = dict(n=PARTY[c], base=col, minor=True)
CAND["P_OTR"] = dict(n="Otros, en blanco o no atribuido", base="#9a9a9a", minor=True)


LOGOS = os.path.join(HERE, "..", "logos_wikipedia")   # emblemas de Wikipedia, ver LICENCIAS.md alli


def _logo(fn, ar):
    import base64
    t = open(os.path.join(LOGOS, fn), encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar)


CAND["UCR"].update(_logo("Bandera_UCR_bicolor.svg", 850 / 510))   # bandera radical antigua (blanca y roja); el escudo es de 1931
# Concentración Cívica (Corrientes): sin logo de época (el del Pacto Autonomista-Liberal es posterior): lleva sigla
CAND["PDP"].update(_logo("Escudo_del_PDP.svg", 1.0))
CAND["SOC"].update(_logo("Emblema_del_Partido_Socialista_Argentino.svg", 1.0))
GREY_T, GREY_N, GREY_P = "#cfcfcf", "#8c8c8c", "#e6dcc3"
KEYS = [[GREY_T, "Territorio nacional: no votaba"], [GREY_N, "Cifras subsumidas en otra unidad"],
        [GREY_P, "San Juan y Santiago del Estero: sin datos aún"]]


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def analyse(row):
    P = {c: x[0] for c, x in row["P"].items()}
    ins, vot = row["ins"], row["vot"]
    tab = sum(P.values())
    E = max(vot or 0, tab) or None                        # votos emitidos
    D = (tab - P.get("BLA", 0) - P.get("OTR", 0)) or None   # votos positivos: base de los porcentajes, como en Wikipedia
    bloc = {b: 0 for b in BLOCS}
    for c, x in P.items():
        bloc[BLOC[c]] += x
    return dict(P=P, ins=ins, vot=vot, D=D, E=E, tab=tab, bloc=bloc)


def rec_from(a, extra_note=None):
    D = a["D"]
    if not D: return None
    E = a.get("E") or D   # emitidos: base de blancos y no atribuidos
    P = a["P"]
    lines = [["P_" + c, int(round(x)), round(100 * x / D, 2)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x > 0 or c == "UCR"]
    rest = E - a["tab"]
    if rest > 0.5: lines.append(["P_OTR", int(round(rest)), round(100 * rest / E, 2)])
    w = max(a["bloc"], key=lambda b: a["bloc"][b])
    met = []
    if a["ins"] is not None: met.append(["Inscriptos", fmt_n(a["ins"])])
    if a["vot"] is not None: met.append(["Votantes", fmt_n(a["vot"])])
    if a["ins"] and a["vot"]: met.append(["Participación", fmt_p(100 * a["vot"] / a["ins"]) + " %"])
    rec = {"lines": lines, "metrics": met}
    if a["bloc"][w] > 0:
        rec.update(w=w, q=round(100 * a["bloc"][w] / D, 2))
    else:
        rec["fill"] = GREY_N
    notes = []
    if a["vot"] is not None and a["tab"] > 1.03 * a["vot"]:
        notes.append("En la fuente impresa la suma de las columnas partidarias (%s) excede a los votantes (%s)." % (fmt_n(a["tab"]), fmt_n(a["vot"])))
    if extra_note: notes.append(extra_note)
    if notes: rec["note"] = " ".join(notes)
    return rec


unit_rec, unit_an = {}, {}
for i, u in enumerate(U):
    p = u["prov"]
    if p in geom.TERR:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1916: sus habitantes no votaban."}
    elif (p, u["name"]) in LOS_ANDES:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio Nacional de Los Andes (1900-1943): sus habitantes no votaban (Cacopardo 1967)."}
    elif p in PENDIENTES:
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin datos todavía: no hay cuadro de %s para 1916 en las fuentes reunidas." % p}
    elif p in SOLID:
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin cuadro departamental en Cantón. " + PROV_NOTE[p]}
    elif i in salta_idx:
        s_ = salta_idx[i]
        a = analyse(dict(P={c: [float(s_[c]), None] for c in ("UCR", "UPV", "SOC") if s_[c] > 0}, ins=None, vot=float(s_["suf"])))
        unit_an[i] = a
        unit_rec[i] = rec_from(a, SALTA_NOTE % ", ".join(s_["col"]))
    elif i in unit_src:
        r, why, n = unit_src[i]
        if not r["P"] and "sin_datos" in r["flags"]:
            unit_rec[i] = {"fill": GREY_P, "lines": [], "note": SIN_DATOS.get((p, r["name"]), "Cantón no trae votos para «%s» (celdas «*», sin datos)." % r["name"])}
            continue
        if not r["P"]:
            unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón marca las cifras de «%s» como subsumidas bajo una unidad mayor o no tomadas en cuenta." % r["name"]}
            continue
        extras = []
        if r.get("prensa"): extras.append(r["prensa"])
        if norm(r["name"]) != norm(u["name"]) and p != "Capital Federal": extras.append("Nombre en Cantón: «%s»." % r["name"])
        if why: extras.append(why)
        if n > 1: extras.append("Dato único compartido por %d polígonos." % n)
        if r["recon"]: extras.append("Cifra(s) ilegible(s) en la fuente, reconstruida(s): " + "; ".join(r["recon"]) + ".")
        if "celda_perdida" in r["flags"]: extras.append("Hay cifras ilegibles sin reconstruir: los porcentajes pueden estar subestimados.")
        a = analyse(r); unit_an[i] = a
        unit_rec[i] = rec_from(a, " ".join(extras) or None)
    else:
        unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Sin fila para esta unidad en Cantón (1916)."}

disp = {}
for i, (r, why, n) in unit_src.items():
    p = U[i]["prov"]
    disp[i] = ("Circunscripción %d · %s" % (CAP_CIRC[norm(r["name"])], r["name"])) if p == "Capital Federal" else (r["name"] if n == 1 else U[i]["name"])

# provincias y pais (solo lo cargado: faltan San Juan y Santiago del Estero; Salta se excluye por no tener partidos atribuidos)
prov_an, nat = {}, dict(P={}, ins=0, vot=0, bloc={b: 0 for b in BLOCS})
for (prov, n), r in canton.items():
    if not r["P"] and not r["vot"]: continue
    tot = prov_an.setdefault(prov, dict(P={}, ins=0, vot=0))
    for c, x in r["P"].items(): tot["P"][c] = tot["P"].get(c, 0) + x[0]
    if r["ins"] is not None: tot["ins"] += r["ins"]
    tot["vot"] += r["vot"] if r["vot"] is not None else sum(x[0] for x in r["P"].values())
prov_an["Salta"] = dict(P={c: float(sum(s_[c] for s_ in salta.values())) for c in ("UCR", "UPV", "SOC")}, ins=0, vot=float(sum(s_["suf"] for s_ in salta.values())))
for p_, v_ in PROV_ONLY.items():
    prov_an[p_] = dict(P=dict(v_["P"]), ins=v_["ins"], vot=v_["vot"])
for prov, t in prov_an.items():
    for c, x in t["P"].items():
        nat["P"][c] = nat["P"].get(c, 0) + x
        nat["bloc"][BLOC[c]] += x
    nat["ins"] += t["ins"]; nat["vot"] += t["vot"]


def an_of(t):
    tab = sum(t["P"].values()); bloc = {b: 0 for b in BLOCS}
    for c, x in t["P"].items():
        bloc[BLOC[c]] += x
    return dict(P=t["P"], ins=t["ins"] or None, vot=t["vot"], D=(tab - t["P"].get("BLA", 0) - t["P"].get("OTR", 0)) or None, E=max(t["vot"] or 0, tab), tab=tab, bloc=bloc)


prov_rec = {}
for p in PROVS:
    if p in geom.TERR:
        prov_rec[p] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1916: sin voto."}
    elif p in PENDIENTES:
        prov_rec[p] = {"fill": GREY_P, "lines": [], "note": "Sin datos todavía."}
    elif p in SOLID:
        prov_rec[p] = rec_from(an_of(prov_an[p]), PROV_NOTE[p])
    elif p == "Salta":
        prov_rec[p] = rec_from(an_of(prov_an[p]), "Planilla del 15 de abril de 1916 (exp. 58-D-1916). Los totales proclamados el 1 de mayo fueron Usandivaras (Unión Provincial) 11.339, Outes (UCR) 6.723 y Lesser (Socialista) 121.")
    else:
        prov_rec[p] = rec_from(an_of(prov_an[p]))
NA = dict(P=nat["P"], ins=nat["ins"], vot=nat["vot"], D=nat["vot"], tab=sum(nat["P"].values()), bloc=nat["bloc"])
cands = sorted([{"code": b, "votes": int(NA["bloc"][b]), "pct": round(100 * NA["bloc"][b] / NA["D"], 2)} for b in BLOCS if NA["bloc"][b] > 0], key=lambda x: -x["votes"])
other = max(0, NA["D"] - sum(NA["bloc"].values()))
slices = [{"code": c["code"], "v": c["votes"]} for c in cands] + [{"fill": "#dfe0e5", "v": int(other)}]
ins_ok = sum(t["ins"] for t in prov_an.values() if t["ins"])
vot_ok = sum(t["vot"] for t in prov_an.values() if t["ins"])
partp = round(100 * vot_ok / ins_ok, 2)
NAT_MET = [["Votantes (13 de 15 distritos)", fmt_n(nat["vot"])], ["Participación (sin Capital ni Salta)", fmt_p(partp) + " %"]]
# resultado nacional: tabla del articulo de Wikipedia (ver ../wikitop.py)
sys.path.insert(0, os.path.join(HERE, ".."))
import wikitop
cands, slices, partp, NAT_MET = wikitop.national(1916)
print("pais: votantes", nat["vot"], "bloques", {b: int(v) for b, v in NA["bloc"].items()}, "| sin poligono:",
      [(r["prov"], r["name"]) for r in unmapped], file=sys.stderr)

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


NOTE = ("Fuente: D. Cantón, «Materiales para el estudio de la sociología política en la Argentina» (1968), t. II, diputados nacionales, 2 abr. 1916 (transcripción del paquete 1916dip); "
        "Salta: expediente 58-D-1916 (partidos según la Wikipedia). Cada columna partidaria de Cantón puede ser el candidato más votado de la lista y no el total del partido. "
        "Geometría: departamentos del censo de 1914.. San Juan y Santiago del Estero: solo total provincial (Wikipedia), sin datos departamentales.")
NOTE = wikitop.note(1916) + " " + NOTE



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
        if p in geom.TERR or p in PENDIENTES: prov[p] = r; continue
        v = fn(an_of(prov_an[p]))
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec,
              national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=dict(keys=KEYS))]
for mid, tile, fn, base, edges, title, extra in (
    ("ucr", "UCR", lambda a: 100 * a["bloc"]["UCR"] / a["D"], "#e10019", [0, 15, 30, 40, 50, 60, 70], "% UCR (Comité Nacional)", ""),
    ("con", "CON", lambda a: 100 * a["bloc"]["CON"] / a["D"], "#1fa89d", [0, 15, 30, 40, 50, 60, 70], "% Concentración Conservadora", "Concentración Conservadora (como en Wikipedia) = Concentración, conservadores, demócratas (Córdoba, San Luis), autonomistas de Corrientes, provincialistas, Unión Popular y Unión Provincial (Salta). Los liberales de Corrientes (Concentración Cívica) van aparte. "),
    ("par", "PART", lambda a: (100 * a["vot"] / a["ins"]) if (a["ins"] and a["vot"]) else None, "#2a6f97", [0, 30, 40, 50, 60, 70, 80], "Participación (votantes / inscriptos)", "")):
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
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True, antarctic=False, omit=("sj",), sj_names={"Capital", "Santa Lucia", "Chimbas", "Rivadavia", "Pocito", "Albardon", "Trinidad", "Concepcion", "Desamparados", "Zonda", "Rawson"}, chaco_names={"Resistencia"})
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
    slug="diputados_1916", locale="es-AR", country="Argentina",
    title="Elecciones legislativas de Argentina de", year="1916",
    labels=dict(pie1="Proporción sobre votos positivos"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1916", subtitle="Cantón (1968) · deptos. de 1914")},
    modes=MODES, insets=INSETS, solid=sorted(SOLID),
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(HERE, "dataset_1916.json"), "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 1916</title>")
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
out = os.path.join(HERE, "atlas_1916_diputados.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)

