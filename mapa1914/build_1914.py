#!/usr/bin/env python3
"""Atlas electoral de diputados nacionales 1914 (estilo Wikipedia 1999) sobre los departamentos del censo de 1914.

    python build_1914.py            -> mapa1914/atlas_1914_diputados.html (+ dataset_1914.json)

Datos     : ../busqueda1914 (consolidado 1914) y totales provinciales de la Wikipedia.
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

# ---------------------------------------------------------------- datos: busqueda1914 (consolidado) + totales provinciales de la Wikipedia
import pandas as pd
import csv
SRC = os.path.join(HERE, "..", "busqueda1914")

KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
# nombre del consolidado -> poligono(s) de 1914. Mismas equivalencias que el atlas de 1916 (Cacopardo 1967, Cuadro 1; Canton t. I, Apendice C)
ALIAS = {
    ("Buenos Aires", "9 de Julio"): (["Nueve de julio"], None),
    ("Buenos Aires", "Matanza"): (["La Matanza"], None),
    ("Buenos Aires", "Mar Chiquita"): (["Coronel Vidal"], "El partido Coronel Vidal (1914) es el actual Mar Chiquita (Cacopardo 1967)."),
    ("Buenos Aires", "Tordillo"): (["General Conesa"], "El partido General Conesa (1914) volvió a llamarse Tordillo (Cacopardo 1967)."),
    ("Buenos Aires", "General Madariaga"): (["Gnral.Juan Madariaga"], None),
    ("Buenos Aires", "Tigre"): (["Las Conchas (Tigre)"], None),
    ("Buenos Aires", "Juárez"): ([], None), ("Buenos Aires", "Tres Arroyos"): ([], None), ("Buenos Aires", "González Chaves"): ([], None),
    ("Buenos Aires", "Necochea"): (["Necochea", "Tres Arroyos", "Benito Juarez"], "Cantón (t. I, Apéndice C) incluye en Necochea los datos de Juárez, Tres Arroyos y Gonzáles Chaves; el dato se reparte en los tres polígonos de 1914 (Gonzáles Chaves, creado en 1916, no existe en esa base)."),
    ("Córdoba", "Tercero Abajo"): (["General San Martín"], "El departamento Tercero Abajo (1914) es el actual General San Martín (Cacopardo 1967)."),
    ("Córdoba", "General Roca"): (["General Roca"], None),
    ("Corrientes", "Libres"): (["Paso de los Libres"], None),
    ("Corrientes", "San Luis"): (["San Luís del Palmar"], None),
    ("Entre Ríos", "Concepción del Uruguay"): (["Uruguay"], None), ("Entre Ríos", "Rosario Tala"): (["Tala"], None),
    ("Mendoza", "Ciudad"): (["Capital"], None), ("Mendoza", "Luján"): (["Lujan de Cuyo"], None),
    ("Santa Fe", "Capital"): (["La Capital"], None),
}
CAP_CIRC = {"Velez Sarsfield": 1, "San Cristóbal Sud": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sud": 6,
            "San Carlos Norte": 7, "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sud": 10, "Balvanera Norte": 11,
            "Concepción": 12, "Monserrat": 13, "San Nicolás": 14, "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18,
            "Pilar": 19, "Socorro": 20}
CAP_CIRC = {norm(k): v for k, v in CAP_CIRC.items()}

# columna/candidato del consolidado -> codigo de fuerza. Cada partido usa los votos de su primer candidato (como la Wikipedia: «votos al partido»).
LAB = {
    "Buenos Aires": {"Conservador": "CNS", "Unión Cívica Radical": "UCR", "Socialista": "SOC"},
    "Capital Federal": {"Unión Cívica Radical": "UCR", "Socialista": "SOC", "Unión Cívica": "UC", "Constitucional": "CNT"},
    "Entre Ríos": {"Unión Cívica Radical": "UCR", "Provinciales": "PRV", "Carbosistas": "CRB"},
    "Córdoba": {"Garzón": "DEM", "Salas Oroño": "UCR", "Peña": "IND", "Parpal": "SOC"},
    "Corrientes": {"Álvaro I. Márquez": "CLA", "Manuel Bejarano": "LDI", "Pedro Numa Soto": "UCR"},
    "La Rioja": {"Antonio P. García": "CNS", "Pelagio B. Luna": "UCR"},
    "Mendoza": {"Luis F. Silveti": "PPO", "Diógenes Aguirre": "UCR"},
    "Santa Fe": {"Araya": "UCR", "Correa": "LDS", "Reynés": "SOC", "Adolfo Benavídez": "OTR"},
}
BLANCOS = {"En blanco", "Votos en blanco"}
# candidatos que acompañan al primero de la lista de un partido (no suman: la Wikipedia da los votos del partido = los del primer candidato)
ACOMP = {"Córdoba": {"Del Viso", "Vaca Narvaja", "Fernández", "Paolucci"},
         "Corrientes": {"Guillermo Rojas", "Evaristo Pérez Virasoro", "Manuel Bonastre", "Pedro Sánchez", "Ernesto E. Ezquer", "Ramón Díaz de Vivar",
                        "Ángel Blanco", "Juan P. Acosta", "Eudoro Vargas Gómez"},
         "Mendoza": {"Rafael M. Aguirre", "Pedro N. Ortiz"}}
PARTY = {"UCR": "Unión Cívica Radical", "CNS": "Partido Conservador", "CNT": "Partido Constitucional", "PRV": "Partido Provincial", "CRB": "Carbosistas",
         "DEM": "Partido Demócrata", "PPO": "Partido Popular", "CLA": "Coalición Liberal y Autonomista", "LDI": "Partido Liberal Disidente",
         "UDE": "Unión Democrática", "OFI": "Partido Oficialista", "UPV": "Unión Provincial", "CCV": "Concentración Cívica",
         "SOC": "Partido Socialista", "UC": "Unión Cívica", "LDS": "Liga del Sur", "IND": "Independientes (Peña)", "OTR": "Otros",
         "UPO": "Unión Popular", "LIB": "Partido Liberal", "NAC": "Partido Nacionalista", "CCN": "Concentración Conservadora"}
PCOL = {"UCR": "#e10019", "CNS": "#22b5aa", "CNT": "#5cc9c0", "PRV": "#1a9a91", "CRB": "#a3eee8", "DEM": "#1f2f6b", "PPO": "#3fc2b8", "CLA": "#35aae0",
        "LDI": "#7fc8ec", "UDE": "#2fb8ad", "OFI": "#30d5c8", "UPV": "#6fe3da", "CCV": "#30d5c8", "SOC": "#ff9900", "UC": "#000000", "LDS": "#005c9e",
        "IND": "#a0a0a0", "OTR": "#9a9a9a", "UPO": "#bdbdbd", "LIB": "#9ad3ee", "NAC": "#cfcfcf", "CCN": "#30d5c8"}
# bloques como la Wikipedia: «Partidos Conservadores» suma todas las filas conservadoras, demócrata, provinciales y la coalición liberal-autonomista de Corrientes
BLOC = {c: "CON" for c in ("CNS", "CNT", "PRV", "CRB", "DEM", "PPO", "CLA", "LDI", "UDE", "OFI", "UPV", "CCV", "CCN")}
BLOC.update({"UCR": "UCR", "SOC": "SOC", "UC": "UC", "LDS": "LDS", "IND": "IND", "OTR": "OTR", "UPO": "OTR", "LIB": "OTR", "NAC": "OTR"})
BLOCS = ["UCR", "CON", "SOC", "LDS", "UC", "IND"]


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --- cifras departamentales: consolidado principal (7 provincias) + Santa Fe (prensa, parciales)
canton = {}      # (prov, nombre) -> dict(P, blank, note, parcial)
for r in read(os.path.join(SRC, "datos_1914_depto.csv")):
    prov, dep = r["provincia"], r["departamento"]
    row = canton.setdefault((prov, dep), dict(prov=prov, name=dep, P={}, blank=None, vacios=0, src=r["fuente_id"], parcial=False))
    lab = r["partido_o_lista"]
    if lab in BLANCOS:
        if r["votos"] != "": row["blank"] = float(r["votos"])
        continue
    code = LAB[prov].get(lab)
    if code is None:
        if lab in ACOMP.get(prov, ()): continue
        if r["votos"] != "":
            row["P"]["OTR"] = row["P"].get("OTR", 0) + float(r["votos"])     # el resto de las candidaturas va a «otros»
        continue
    if r["votos"] == "":
        row["vacios"] += 1
    else:
        row["P"][code] = row["P"].get(code, 0) + float(r["votos"])
SF_PARCIAL = {"Capital", "General López"}
for r in read(os.path.join(SRC, "datos_1914_parciales.csv")):
    if r["provincia"] != "Santa Fe": continue
    dep, lab = r["departamento"], r["partido_o_lista"]
    code = LAB["Santa Fe"].get(lab)
    if code is None or r["votos"] == "": continue
    # la sigla de cada partido sale de su primer candidato (Araya, Correa, Reynés); Correa y Reynés se ubican con su grupo impreso
    g = r.get("grupo_fuente", "")
    if code == "UCR" and g not in ("", "Radicales"): continue
    if code == "LDS" and g not in ("", "Liguistas"): continue
    if code == "SOC" and g not in ("", "Socialistas"): continue
    row = canton.setdefault(("Santa Fe", dep), dict(prov="Santa Fe", name=dep, P={}, blank=None, vacios=0, src=r["fuente_id"], parcial=dep in SF_PARCIAL))
    assert code not in row["P"], (dep, lab)
    row["P"][code] = float(r["votos"])

# Concepción del Uruguay (Entre Ríos): Cantón no trae cifras. Inferencia por residuo pedida por el usuario (15-oct-2026), guardada aparte en la carpeta de investigación
ER_INF = {"Unión Cívica Radical": "UCR", "Provinciales": "PRV", "Carbosistas": "CRB"}
_row = canton[("Entre Ríos", "Concepción del Uruguay")]
for r in read(os.path.join(SRC, "fase2", "entre_rios", "inferencia_concepcion.csv")):
    _row["P"][ER_INF[r["partido_o_lista"]]] = float(r["votos"])
_row["inferido"] = True; _row["vacios"] = 0

# La Prensa (31/3 a 2/4/1914): cifras provisorias que llenan huecos (ver busqueda1914/fase3/pba_laprensa/LEEME.md).
#   Buenos Aires: General San Martín, San Antonio de Areco y San Isidro (UCR y PS); Santa Fe: Caseros, Constitución y el total de General López.
LP_CODE = {"Conservador": "CNS", "Unión Cívica Radical": "UCR", "Socialista": "SOC", "Perfecto Araya": "UCR", "Francisco Correa": "LDS", "Agustín Reynés": "SOC"}
for r in read(os.path.join(SRC, "fase3", "pba_laprensa", "datos_laprensa.csv")):
    key = (r["provincia"], r["departamento"])
    row = canton.setdefault(key, dict(prov=r["provincia"], name=r["departamento"], P={}, blank=None, vacios=0, src=r["fuente_id"], parcial=False))
    if r["provincia"] == "Santa Fe" and row.get("lp") is None:
        row["P"] = {}; row["parcial"] = False          # el total de La Prensa reemplaza la suma parcial de localidades (General López)
    row["P"][LP_CODE[r["partido_o_lista"]]] = float(r["votos"])
    row["vacios"] = 0; row["lp"] = True
    row["prensa"] = ("Completado con La Prensa (Buenos Aires, " + r["fila_fuente"].split(",")[1].strip() + " p. " + r["fila_fuente"].split("p. ")[1].split(" ")[0] + "): " if r["provincia"] == "Buenos Aires" else "") + r["nota"].replace("Solo se transcriben los primeros candidatos de cada partido (Araya, Correa, Reynés). ", "")

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
NOELIGE = {"San Luis"}      # San Luis no renovó diputados en 1914

# --- totales provinciales: tablas de la Wikipedia («Elecciones legislativas de Argentina de 1914», Resultados por provincia)
# votos de cada partido = votos de su primer candidato; ins = electores registrados; tot = total de votos; base de %: votos positivos (o el total si no se publican)
PROV = {
    "Buenos Aires": dict(P={"CNS": 63062, "UCR": 55705, "SOC": 6719}, tot=132964, ins=254194),
    "Capital Federal": dict(P={"SOC": 44335, "UCR": 38722, "UC": 20222, "CNT": 15193, "UPO": 2863, "LIB": 815, "NAC": 588, "OTR": 1154}, tot=124532, ins=147689, bla=640),
    "Catamarca": dict(P={"OFI": 7703, "OTR": 5735}, tot=13528, ins=19690, bla=85),
    "Córdoba": dict(P={"DEM": 18875, "UCR": 16862, "IND": 9823, "SOC": 262}, tot=53198, ins=122433),
    "Corrientes": dict(P={"CLA": 19783, "LDI": 8937, "UCR": 8776}, tot=37496, ins=61684),
    "Entre Ríos": dict(P={"UCR": 25947, "PRV": 21339, "CRB": 6615, "OTR": 816}, tot=54717, ins=71445),
    "Jujuy": dict(P={"OFI": 3806, "UCR": 3606}, tot=8097, ins=14000),
    "La Rioja": dict(P={"CNS": 6599, "UCR": 500, "OTR": 235}, tot=7980, ins=16400, bla=646),
    "Mendoza": dict(P={"PPO": 15453, "UCR": 6871, "OTR": 801}, tot=23720, ins=40987, bla=595),
    "Salta": dict(P={"UPV": 10389, "UCR": 242, "SOC": 193, "OTR": 231}, tot=14114, ins=28303, bla=3059),
    "San Juan": dict(P={"CCV": 10194, "UCR": 3187, "SOC": 202, "OTR": 17}, tot=13755, ins=22016, bla=155),
    "Santa Fe": dict(P={"UCR": 38969, "LDS": 16601, "SOC": 2228, "OTR": 4932}, tot=62730, ins=108163),
    "Santiago del Estero": dict(P={"UDE": 22258, "SOC": 544}, tot=23331, ins=48876),
    "Tucumán": dict(P={"CCN": 19139, "IND": 11563, "UCR": 11456, "SOC": 531}, tot=42689, ins=71662),
}
for p_, v_ in PROV.items():
    pos = sum(v_["P"].values())
    assert pos + v_.get("bla", 0) <= v_["tot"] + 1, (p_, pos, v_)
SOLID = {"Catamarca", "Jujuy", "Salta", "San Juan", "Santiago del Estero", "Tucumán"}      # sin cuadro departamental: se pinta toda la provincia con su resultado
PROV_NOTE = {
    "Catamarca": "Expediente 42-D-1914. Partido Oficialista (Mercado) 57,3 %; Guillermo Correa (Otros) 29,3 %.",
    "Jujuy": "La Cámara rechazó los despachos de mayoría y minoría en la sesión del 24 de julio de 1914 y la elección quedó anulada (la Wikipedia da 3.806 al Partido Oficialista y 3.606 a la UCR sobre votos positivos 7.412).",
    "Salta": "Expediente 27-P-1914. Unión Provincial (Saravia Castro) 94,0 %.",
    "San Juan": "Expediente 19-P-1914. Concentración Cívica (Barrera) 75,0 % contra la UCR 23,4 %.",
    "Santiago del Estero": "Expediente 18-P-1914. Unión Democrática (Salvatierra) 97,6 %.",
    "Tucumán": "Concentración Conservadora (Padilla) 44,8 %; Eduardo Paz (Otros en la Wikipedia) 27,1 %; UCR (Uttinger) 26,8 %. Cifras de los comicios impugnados aparte en busqueda1914.",
}
GREY_T, GREY_N, GREY_P, GREY_I = "#cfcfcf", "#8c8c8c", "#e6dcc3", "#a8a8b0"
KEYS = [[GREY_T, "Sin elección: territorio nacional o San Luis"], [GREY_N, "Cifras subsumidas en otra unidad"],
        [GREY_P, "Sin cifras departamentales"], [GREY_I, "Ganó un independiente (Córdoba)"]]


def analyse(P):
    P = {c: x for c, x in P.items() if x > 0}
    D = sum(P.values()) or None
    bloc = {b: 0 for b in BLOCS}
    for c, x in P.items():
        b = BLOC[c]
        if b in bloc: bloc[b] += x
    return dict(P=P, D=D, bloc=bloc)


def lines_of(P, D):
    out = [["P_" + c, int(round(x)), round(100 * x / D, 2)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x > 0]
    return out


def rec_from(a, extra_note=None, met=None, fill=None):
    D = a["D"]
    if not D: return None
    rec = {"lines": lines_of(a["P"], D), "metrics": met or []}
    w = max(a["bloc"], key=lambda b: a["bloc"][b])
    if w == "IND" and a["bloc"][w] > 0:
        rec["fill"] = GREY_I      # independientes (Peña, Córdoba): no forman bloque en la Wikipedia, van en «otros»
    elif a["bloc"][w] > 0:
        rec.update(w=w, q=round(100 * a["bloc"][w] / D, 2))
    else:
        rec["fill"] = GREY_N
    if extra_note: rec["note"] = extra_note
    return rec


unit_rec, unit_an = {}, {}
for i, u in enumerate(U):
    p = u["prov"]
    if p in geom.TERR:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1914: sus habitantes no votaban."}
    elif (p, u["name"]) in LOS_ANDES:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio Nacional de Los Andes (1900-1943): sus habitantes no votaban (Cacopardo 1967)."}
    elif p in NOELIGE:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "San Luis no renovó diputados en 1914."}
    elif p in SOLID:
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin cuadro departamental. " + PROV_NOTE[p] + " El mapa pinta toda la provincia con este resultado."}
    elif i in unit_src:
        r, why, n = unit_src[i]
        if not r["P"]:
            if p == "Entre Ríos":
                unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Concepción del Uruguay: Cantón no trae cifras. Queda sin pintar; el residuo provincial (inferencia condicional, no transcripción) está en busqueda1914/fase2/entre_rios/INFERENCIA_CONCEPCION.md."}
            else:
                unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón marca las cifras de «%s» como subsumidas bajo una unidad mayor o no tomadas en cuenta." % r["name"]}
            continue
        extras = []
        if r.get("lp"): extras.append(r["prensa"])
        if r.get("inferido"): extras.append("INFERIDO, no transcrito: residuo entre el total provincial de la Wikipedia y la suma de los otros 13 departamentos de Cantón (UCR 2.900, Provinciales 3.859, Carbosistas 687). Supone que toda la diferencia pertenece a este único departamento sin cifras; no incluye «otros» ni blancos.")
        if norm(r["name"]) != norm(u["name"]) and p != "Capital Federal": extras.append("Nombre en el consolidado: «%s»." % r["name"])
        if why: extras.append(why)
        if n > 1: extras.append("Dato único compartido por %d polígonos." % n)
        if r["vacios"]: extras.append("%d celda(s) sin cifra en la fuente: los porcentajes pueden estar subestimados." % r["vacios"])
        if p == "Santa Fe":
            extras.append(("La Prensa" if r.get("lp") else "Prensa del diario Santa Fe") + " durante el escrutinio (31/3 a 2/4/1914), anterior al definitivo del 8/4: votos del primer candidato de cada lista (Araya, Correa, Reynés).")
            if r["parcial"]: extras.append("SUMA PARCIAL de las localidades publicadas, no el total del departamento: faltan localidades.")
        if p == "La Rioja": extras.append("Según las mesas que la Comisión declaró válidas (expediente 13-P-1914); no es la resolución final de la Cámara.")
        if p == "Córdoba": extras.append("Principal del 22/3 más complementaria del 5/4; no incluye las adiciones del 23/4 sin departamento.")
        if p == "Mendoza": extras.append("Solo la elección principal del 22/3; la complementaria del 5/4 queda aparte.")
        if p == "Buenos Aires" or p == "Capital Federal" or p == "Entre Ríos": extras.append("Cada columna es un partido según Cantón (1968, t. II).")
        met = [["En blanco", fmt_n(r["blank"])]] if r["blank"] is not None else []
        a = analyse(r["P"]); unit_an[i] = a
        unit_rec[i] = rec_from(a, " ".join(extras) or None, met)
    elif p == "Santa Fe":
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin tabla departamental: el diario Santa Fe no publicó este departamento entre el 24/3 y el 8/4/1914."}
    else:
        unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Sin fila para esta unidad en el consolidado de 1914."}

disp = {}
for i, (r, why, n) in unit_src.items():
    p = U[i]["prov"]
    disp[i] = ("Circunscripción %d · %s" % (CAP_CIRC[norm(r["name"])], r["name"])) if p == "Capital Federal" else (r["name"] if n == 1 else U[i]["name"])

# provincias: totales de la Wikipedia
prov_an = {}
for p_, v_ in PROV.items():
    prov_an[p_] = dict(a=analyse(v_["P"]), ins=v_["ins"], vot=v_["tot"], bla=v_.get("bla"), par=100 * v_["tot"] / v_["ins"])
prov_rec = {}
for p in PROVS:
    if p in geom.TERR:
        prov_rec[p] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1914: sin voto."}
    elif p in NOELIGE:
        prov_rec[p] = {"fill": GREY_T, "lines": [], "note": "San Luis no renovó diputados en 1914."}
    else:
        t = prov_an[p]
        met = [["Inscriptos", fmt_n(t["ins"])], ["Votantes", fmt_n(t["vot"])], ["Participación", fmt_p(t["par"]) + " %"]]
        if t["bla"]: met.append(["En blanco", fmt_n(t["bla"])])
        prov_rec[p] = rec_from(t["a"], PROV_NOTE.get(p, "Total provincial según la Wikipedia (Elecciones legislativas de Argentina de 1914)."), met)

# resultado nacional: tabla del articulo de Wikipedia (ver ../wikitop.py)
sys.path.insert(0, os.path.join(HERE, ".."))
import wikitop
cands, slices, partp, NAT_MET = wikitop.national(1914)
print("sin poligono:", [(r["prov"], r["name"]) for r in unmapped], file=sys.stderr)
_wins = {}
for i, rec in unit_rec.items():
    if rec.get("w"): _wins[rec["w"]] = _wins.get(rec["w"], 0) + 1
for p_, rec in prov_rec.items():
    pass
print("unidades ganadas por bloque:", _wins, file=sys.stderr)

CAND = {
    "UCR": dict(n="Unión Cívica Radical", sub="UCR", logo="UCR", base="#e10019"),
    "CON": dict(n="Partidos Conservadores", sub="Conservadores y afines", logo="PC", base="#30d5c8", bar="#1fa89d", txt="#1a8f86"),
    "SOC": dict(n="Partido Socialista", sub="Socialistas", logo="PS", base="#ff9900", bar="#e08700", txt="#b87500"),
    "LDS": dict(n="Liga del Sur", sub="Santa Fe", logo="LDS", base="#005c9e"),
    "UC": dict(n="Unión Cívica", sub="Capital Federal", logo="UC", base="#000000", bar="#000000", txt="#333333"),
    }
for c, col in PCOL.items():
    CAND["P_" + c] = dict(n=PARTY[c], base=col, minor=True)

LOGOS = os.path.join(HERE, "..", "logos_wikipedia")   # emblemas de Wikipedia, ver LICENCIAS.md alli


def _logo(fn, ar):
    import base64
    t = open(os.path.join(LOGOS, fn), encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar)


CAND["UCR"].update(_logo("Bandera_UCR_bicolor.svg", 850 / 510))   # bandera radical antigua (blanca y roja); el escudo es de 1931
CAND["SOC"].update(_logo("Emblema_del_Partido_Socialista_Argentino.svg", 1.0))

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


NOTE = ("Fuente de los departamentos: consolidado de la investigación de 1914 (carpeta busqueda1914): Cantón (1968, t. II) para Buenos Aires, Capital y Entre Ríos; "
        "expedientes de la Cámara de Diputados para Córdoba, Corrientes, La Rioja y Mendoza; prensa del diario Santa Fe para 10 departamentos de Santa Fe (sin los 7 restantes), "
        "y totales provinciales de la Wikipedia donde no hay cuadro departamental (Catamarca, Jujuy, Salta, San Juan, Santiago del Estero y Tucumán: se pinta toda la provincia). "
        "Cada partido cuenta los votos de su primer candidato. Geometría: departamentos del censo de 1914. San Luis no renovó diputados.")
NOTE = wikitop.note(1914) + " " + NOTE


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
        if p in geom.TERR or p in NOELIGE: prov[p] = r; continue
        v = fn(prov_an[p]["a"])
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


def mode_par():
    """Participacion: solo hay dato provincial (Wikipedia: votos / electores registrados); cada departamento lleva el color de su provincia."""
    edges = [0, 45, 50, 55, 60, 70, 80]
    cols, labels = stops_for("#2a6f97", edges)
    units, prov = [], {}
    for i, u in enumerate(U):
        r = unit_rec[i]; p = u["prov"]
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        if p in prov_an:
            nr["fill"] = cols[bin_of(prov_an[p]["par"], edges)]
            nr["note"] = ((nr.get("note", "") + " ") if nr.get("note") else "") + "Participación de la provincia (no hay cifras de electores por departamento): %s %%." % fmt_p(prov_an[p]["par"])
        else:
            nr["fill"] = r.get("fill", GREY_N)
        units.append(nr)
    for p, r in prov_rec.items():
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(prov_an[p]["par"], edges)] if p in prov_an else r.get("fill", GREY_N)
        prov[p] = nr
    return units, prov, dict(title="Participación provincial (votos / electores registrados)", stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec,
              national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=dict(keys=KEYS))]
for mid, tile, fn, base, edges, title, extra in (
    ("ucr", "UCR", lambda a: 100 * a["bloc"]["UCR"] / a["D"], "#e10019", [0, 15, 30, 40, 50, 60, 70], "% UCR", ""),
    ("con", "CON", lambda a: 100 * a["bloc"]["CON"] / a["D"], "#1fa89d", [0, 15, 30, 40, 50, 60, 70], "% Partidos Conservadores",
     "Partidos Conservadores (como en la Wikipedia) = conservadores, Partido Demócrata de Córdoba, Unión Democrática, Partido Provincial, Partido Popular, Partido Oficialista, Unión Provincial, Concentración Cívica, Carbosistas, Constitucional y la coalición liberal-autonomista de Corrientes. "),):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, note=extra + NOTE, units=un, prov=pv,
                      national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=lg))
un, pv, lg = mode_par()
MODES.append(dict(id="par", tile="PART", note="La participación solo existe por provincia. " + NOTE, units=un, prov=pv,
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
    slug="diputados_1914", locale="es-AR", country="Argentina",
    title="Elecciones legislativas de Argentina de", year="1914",
    labels=dict(pie1="Proporción sobre votos positivos"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1914", subtitle="Consolidado 1914 · deptos. de 1914")},
    modes=MODES, insets=INSETS, solid=sorted(SOLID),
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(HERE, "dataset_1914.json"), "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 1914</title>")
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
out = os.path.join(HERE, "atlas_1914_diputados.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)

