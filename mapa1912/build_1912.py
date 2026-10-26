#!/usr/bin/env python3
"""Atlas electoral de diputados nacionales 1912 (estilo Wikipedia 1999) sobre los departamentos del censo de 1914 (el mas cercano a 1912).

    python build_1912.py            -> mapa1912/atlas_1912_diputados.html (+ dataset_1912.json)

Datos     : ../busqueda1912 (Canton, expedientes del HCDN, diario Santa Fe) y totales provinciales de la Wikipedia.
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

# ---------------------------------------------------------------- datos: busqueda1912 + totales provinciales de la Wikipedia
import pandas as pd
import csv
SRC = os.path.join(HERE, "..", "busqueda1912")

KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
# nombre de la fuente -> poligono(s) de 1914
ALIAS = {
    ("Mendoza", "Ciudad de Mendoza"): (["Capital"], None),
    ("Mendoza", "Luján"): (["Lujan de Cuyo"], None),
}
CAP_CIRC = {"Velez Sarsfield": 1, "San Cristóbal Sud": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sud": 6,
            "San Carlos Norte": 7, "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sud": 10, "Balvanera Norte": 11,
            "Concepción": 12, "Monserrat": 13, "San Nicolás": 14, "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18,
            "Pilar": 19, "Socorro": 20}
CAP_CIRC = {norm(k): v for k, v in CAP_CIRC.items()}

# columna/candidato de la fuente -> codigo de fuerza. Cada partido usa los votos de su primer candidato (como la Wikipedia: «votos al partido»).
LAB = {
    "Capital Federal": {"Unión Cívica Radical": "UCR", "Socialista [columna 4]": "SOC", "Unión Cívica": "UC", "Unión Nacional": "UN", "Unión Comunal": "COM"},
    "Córdoba": {"Unión Cívica Radical": "UCR", "Unión Nacional": "UN", "Constitucional": "CNT", "Autonomista Nacional": "AUT"},
    "Mendoza": {"Candidato: Pedro Benegas": "PPO", "Candidato: Estanislao D. Gaviola": "OFI"},
    "Santa Fe": {"Candidato: Rogelio Araya": "UCR", "Candidato: Lisandro de la Torre": "LDS", "Candidato: Víctor P. Pesenti": "COA"},
}
# candidatos que acompanan al primero de la lista de un partido (no suman: la Wikipedia da los votos del partido = los del primer candidato)
ACOMP = {"Santa Fe": {"Candidato: Benjamín Ávalos", "Candidato: Miguel Coronado", "Candidato: Francisco G. Valdez",      # lista radical
                      "Candidato: Cornelio Casablanca", "Candidato: Ovidio A. Lagos", "Candidato: Fermín Lejarza",      # Liga del Sur
                      "Candidato: Domingo Regules", "Candidato: Hernán Saavedra Lamas", "Candidato: Gregorio García Vieyra"}}   # Coalicion
PARTY = {"UCR": "Unión Cívica Radical", "CNS": "Partido Conservador", "CNT": "Partido Constitucional", "AUT": "Autonomista Nacional",
         "OFI": "Partido Oficial", "PPO": "Partido Popular", "COA": "Partido de la Coalición", "LCO": "Partido Liberal de Corrientes",
         "ACO": "Partido Autonomista de Corrientes", "CCV": "Concentración Cívica", "PLT": "Partido Liberal de Tucumán",
         "UN": "Unión Nacional", "UC": "Unión Cívica", "SOC": "Partido Socialista", "LDS": "Liga del Sur",
         "COM": "Unión Comunal", "DRU": "Defensa Rural", "OTR": "Otros"}
PCOL = {"UCR": "#e10019", "CNS": "#22b5aa", "CNT": "#5cc9c0", "AUT": "#1a9a91", "OFI": "#30d5c8", "PPO": "#3fc2b8", "COA": "#6fe3da",
        "LCO": "#35aae0", "ACO": "#7fc8ec", "CCV": "#a3eee8", "PLT": "#2fb8ad", "UN": "#4169e1", "UC": "#000000", "SOC": "#ff9900",
        "LDS": "#005c9e", "COM": "#bdbdbd", "DRU": "#cfcfcf", "OTR": "#9a9a9a"}
# bloques como la Wikipedia: «Partidos Conservadores» suma las diez filas conservadoras de la tabla nacional (incluye las coaliciones provinciales)
BLOC = {c: "CON" for c in ("CNS", "CNT", "AUT", "OFI", "PPO", "COA", "LCO", "ACO", "CCV", "PLT")}
BLOC.update({"UCR": "UCR", "UN": "UN", "SOC": "SOC", "UC": "UC", "LDS": "LDS", "COM": "OTR", "DRU": "OTR", "OTR": "OTR"})
BLOCS = ["UCR", "CON", "UN", "SOC", "UC", "LDS"]


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --- cifras departamentales: Capital, Cordoba, Mendoza y 5 departamentos de Santa Fe (carpeta busqueda1912)
canton = {}      # (prov, nombre) -> dict(P, vacios, src)
for r in read(os.path.join(SRC, "datos_1912_depto.csv")):
    prov, dep = r["provincia"], r["departamento"]
    if prov not in LAB: continue          # San Juan: 32 colegios sin asignar a departamento; se pinta la provincia entera
    row = canton.setdefault((prov, dep), dict(prov=prov, name=dep, P={}, vacios=0, src=r["fuente_id"]))
    lab = r["partido_o_lista"]
    code = LAB[prov].get(lab)
    if code is None:
        if lab in ACOMP.get(prov, ()): continue
        if prov == "Capital Federal" or prov == "Córdoba": raise SystemExit("columna sin codigo: %s %s" % (prov, lab))
        if r["votos"] != "":
            row["P"]["OTR"] = row["P"].get("OTR", 0) + float(r["votos"])     # el resto de las candidaturas va a «otros»
        continue
    if r["votos"] == "":
        row["vacios"] += 1
    else:
        row["P"][code] = row["P"].get(code, 0) + float(r["votos"])

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
NOELIGE = set()      # en 1912 votaron las 13 provincias y la Capital

# --- totales provinciales: tablas de la Wikipedia («Elecciones legislativas de Argentina de 1912», Resultados por provincia)
# votos de cada partido = votos de su primer candidato; ins = electores registrados; tot = «total de votos»; base de %: suma de los votos a candidatos
PROV = {
    "Buenos Aires": dict(P={"CNS": 75010, "UC": 27818, "UN": 21042, "SOC": 4354}, tot=153602, ins=232000),
    "Capital Federal": dict(P={"UCR": 35721, "UC": 32749, "SOC": 32512, "UN": 29825, "COM": 17102, "DRU": 1643, "OTR": 36453}, tot=106157, ins=126303),
    "Catamarca": dict(P={"OFI": 12017, "OTR": 247}, tot=12434, ins=18332, bla=170),
    "Córdoba": dict(P={"CNT": 23582, "UCR": 15690, "UN": 14850}, tot=57148, ins=99929),
    "Corrientes": dict(P={"LCO": 14515, "ACO": 14367, "OTR": 8773, "UCR": 2702}, tot=40357, ins=53485),
    "Entre Ríos": dict(P={"CNS": 24058, "UCR": 21326}, tot=45384, ins=63184),
    "Jujuy": dict(P={"OFI": 4841, "UCR": 2657}, tot=8460, ins=12380),
    "La Rioja": dict(P={"UN": 4120, "UCR": 3724}, tot=11596, ins=15916),
    "Mendoza": dict(P={"PPO": 15833, "OFI": 8247, "OTR": 74}, tot=24467, ins=38500, bla=313),
    "Salta": dict(P={"CNS": 12404, "UCR": 2695, "OTR": 4367}, tot=19466, ins=26627),
    "San Juan": dict(P={"OFI": 8853, "CCV": 8593, "OTR": 88}, tot=17746, ins=21111, bla=194),
    "San Luis": dict(P={"CNS": 7867, "UN": 3432, "OTR": 4754}, tot=16442, ins=22787),
    "Santa Fe": dict(P={"UCR": 36747, "COA": 17856, "LDS": 17630, "SOC": 154, "OTR": 5958}, tot=78345, ins=98371),
    "Santiago del Estero": dict(P={"UN": 9509, "CNS": 6547}, tot=23136, ins=35261),
    "Tucumán": dict(P={"PLT": 29155}, tot=39891, ins=70815),
}
PROV["Santiago del Estero"]["P"] = {"UN": 9509, "AUT": 6547}      # el «Partido Autonomista Nacional» de la Wikipedia
assert sum(v["tot"] for v in PROV.values()) == 654631 and sum(v["ins"] for v in PROV.values()) == 935001       # cierran con la tabla nacional
SOLID = {"Buenos Aires", "Catamarca", "Corrientes", "Entre Ríos", "Jujuy", "La Rioja", "Salta", "San Juan", "San Luis", "Santiago del Estero", "Tucumán"}   # sin cuadro departamental: se pinta toda la provincia con su resultado
PROV_NOTE = {
    "Buenos Aires": "Expediente 19-D-1912: solo trae el cómputo provincial por candidato, no un cuadro por partido ni por distrito. Partido Conservador (Atencio) 75.010; Unión Cívica (Carballido) 27.818; Unión Nacional (Moreno) 21.042; Partido Socialista (Justo) 4.354.",
    "Capital Federal": "Expediente 12-D-1912 (cómputo distrital por candidato) y Cantón (1968).",
    "Catamarca": "Expediente 28-P-1912 (incluye la repetición del 28 de abril de once mesas anuladas). Partido Oficial (Castillo) 12.017 votos; el resto son 250 votos dispersos.",
    "Córdoba": "Expediente 3-D-1912. Partido Constitucional (Del Barco) 23.582; UCR (Molina) 15.690; Unión Nacional (Mateo Bas) 14.850.",
    "Corrientes": "Expediente 51-D-1912. Partido Liberal (Mora y Araujo) 14.515; Partido Autonomista (Breard) 14.367; Ezquer (Otros en la Wikipedia) 8.773; UCR (Blanco) 2.702.",
    "Entre Ríos": "Expediente 46-D-1912: sin matriz departamental. Partido Conservador (Carbó) 24.058; UCR (Laurencena) 21.326.",
    "Jujuy": "Partido Oficial (González Pérez) 4.841; UCR (Sánchez de Bustamante) 2.657 (la Wikipedia).",
    "La Rioja": "La Junta no completó el escrutinio y lo hizo la Cámara. Unión Nacional (Jaramillo) 4.120; UCR (Luna) 3.724.",
    "Mendoza": "Expediente 42-D-1912: Partido Popular (Benegas) 15.833; Partido Oficial (Gaviola) 8.247; 27 candidatos con 74 votos.",
    "Salta": "Expediente 49-D-1912: sin transcripción completa por mesa. Partido Conservador (Leguizamón) 12.404; UCR (Castellanos) 2.695; el resto, dispersos.",
    "San Juan": "Expediente 27-D-1912. Partido Oficial (Etchegaray) 8.853 y Concentración Cívica (Garro) 8.593: los dos van en Partidos Conservadores, así que el mapa por bloques no distingue entre ellos. La carpeta busqueda1912 trae 107 mesas en 32 colegios (cuatro candidatos), pero no están asignados a departamentos y sus sumas difieren algo del resumen provincial.",
    "San Luis": "Expediente 44-D-1912. Partido Conservador (Arancibia Rodríguez) 7.867; Unión Nacional (Origone) 3.432; Jofré, Rodríguez Jurado y Lucero (Otros en la Wikipedia) 4.417.",
    "Santa Fe": "Expediente 17-D-1912. Los totales de la Wikipedia (78.345) cuentan votos a candidatos; el diario Santa Fe del 16/4 da 74.878 sufragantes.",
    "Santiago del Estero": "Unión Nacional (Arias) 9.509; Partido Autonomista Nacional (Santillán) 6.547. Diferencia de actas 7.080.",
    "Tucumán": "Solo figura el Partido Liberal (Mariño) con 29.155 votos positivos, 73,1 % del total; la diferencia de actas es 10.736. El expediente 26-P-1912 (117 páginas, con 82 mesas anuladas y complementarias) está inventariado en busqueda1912 sin transcribir.",
}
GREY_T, GREY_N, GREY_P = "#cfcfcf", "#8c8c8c", "#e6dcc3"
KEYS = [[GREY_T, "Sin elección: territorio nacional"], [GREY_N, "Cifras subsumidas en otra unidad"],
        [GREY_P, "Sin cifras departamentales"]]


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
    if a["bloc"][w] > 0:
        rec.update(w=w, q=round(100 * a["bloc"][w] / D, 2))
    else:
        rec["fill"] = GREY_N
    if extra_note: rec["note"] = extra_note
    return rec


GEN = "Lista incompleta: cada elector votaba por hasta dos tercios de los cargos y podía tachar y agregar nombres; las cifras son los votos del primer candidato de cada partido."
unit_rec, unit_an = {}, {}
for i, u in enumerate(U):
    p = u["prov"]
    if p in geom.TERR:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1912: sus habitantes no votaban."}
    elif (p, u["name"]) in LOS_ANDES:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio Nacional de Los Andes (1900-1943): sus habitantes no votaban (Cacopardo 1967)."}
    elif p in SOLID:
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin cuadro departamental. " + PROV_NOTE[p] + " El mapa pinta toda la provincia con este resultado."}
    elif i in unit_src:
        r, why, n = unit_src[i]
        if not r["P"]:
            unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón marca las cifras de «%s» como subsumidas en una unidad mayor o no tomadas en cuenta (**, tomo I, Apéndice C): no hay cifra impresa y no es cero." % r["name"]}
            continue
        extras = []
        if norm(r["name"]) != norm(u["name"]) and p != "Capital Federal": extras.append("Nombre en la fuente: «%s»." % r["name"])
        if why: extras.append(why)
        if p == "Capital Federal":
            extras.append("Cantón (1968, t. II), una columna por partido. El título de la tabla dice 1912 pero el pie cita La Nación del 7 y 14/4/1916; los totales de las veinte circunscripciones coinciden con los de la Wikipedia 1912 (p. ej. Unión Cívica 32.739 contra 32.749), así que se tratan como de 1912. La columna 4 no lleva clave impresa y se rotula Socialista por una anotación manuscrita.")
        if p == "Córdoba":
            extras.append("Cantón (1968, t. II): cada columna es una lista y las cuatro suman los votantes del departamento. Constitucional y Autonomista Nacional se cuentan en Partidos Conservadores. La Wikipedia usa otras cifras provinciales (el máximo por candidato).")
        if p == "Mendoza":
            extras.append("Expediente 42-D-1912: suma de las cifras expresas de cada mesa (con las repeticiones del 28/4 en lugar de las mesas anuladas). Benegas es el Partido Popular y Gaviola el Oficial; ambos van en Partidos Conservadores, así que el departamento sale de un solo color. Los 188 votos de las mesas coinciden con el total del acta.")
            if r["name"] == "San Martín": extras.append("La mesa 7 no tiene cómputo en el expediente.")
        if p == "Santa Fe":
            extras.append("Diario Santa Fe (18, 20 y 23/4/1912), escrutinio de la Junta anterior al diploma del 29/4: votos del primer candidato de cada lista (Araya UCR, de la Torre Liga del Sur, Pesenti Coalición). Quedaban mesas complementarias pendientes.")
            if r["name"] == "Belgrano": extras.append("La fuente repite a Valdez con dos cifras (183 y 933); se usa Araya, 183.")
            if r["name"] == "Rosario": extras.append("Una cifra (Coronado) ilegible: no se usa, es acompañante de lista.")
        if p == "Santa Fe" or p == "Mendoza": extras.append(GEN)
        if r["vacios"] and p != "Mendoza": extras.append("%d celda(s) sin cifra en la fuente." % r["vacios"])
        a = analyse(r["P"]); unit_an[i] = a
        unit_rec[i] = rec_from(a, " ".join(extras) or None, [])
    elif p == "Santa Fe":
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin cifras: de los 19 departamentos solo 5 (Rosario, Las Colonias, San Lorenzo, Vera y Belgrano) tienen votos por candidato en el diario Santa Fe del 16 al 25/4/1912."}
    else:
        unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Sin fila para esta unidad en la base de 1912."}

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
        prov_rec[p] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1912: sin voto."}
    else:
        t = prov_an[p]
        met = [["Inscriptos", fmt_n(t["ins"])], ["Votantes", fmt_n(t["vot"])], ["Participación", fmt_p(t["par"]) + " %"]]
        if t["bla"]: met.append(["En blanco", fmt_n(t["bla"])])
        prov_rec[p] = rec_from(t["a"], PROV_NOTE.get(p, "Total provincial según la Wikipedia (Elecciones legislativas de Argentina de 1912).") + " " + GEN, met)

# resultado nacional: tabla del articulo de Wikipedia (ver ../wikitop.py)
sys.path.insert(0, os.path.join(HERE, ".."))
import wikitop
cands, slices, partp, NAT_MET = wikitop.national(1912)
print("sin poligono:", [(r["prov"], r["name"]) for r in unmapped], file=sys.stderr)
_wins = {}
for i, rec in unit_rec.items():
    if rec.get("w"): _wins[rec["w"]] = _wins.get(rec["w"], 0) + 1
for p_ in SOLID:
    w_ = prov_rec[p_].get("w")
    print("  solida", p_, w_, prov_rec[p_].get("q"), file=sys.stderr)
print("unidades ganadas por bloque (sin contar las provincias solidas):", _wins, file=sys.stderr)

CAND = {
    "UCR": dict(n="Unión Cívica Radical", sub="UCR", logo="UCR", base="#e10019"),
    "CON": dict(n="Partidos Conservadores", sub="Conservadores y afines", logo="PC", base="#30d5c8", bar="#1fa89d", txt="#1a8f86"),
    "UN": dict(n="Unión Nacional", sub="UN", logo="UN", base="#4169e1"),
    "SOC": dict(n="Partido Socialista", sub="Socialistas", logo="PS", base="#ff9900", bar="#e08700", txt="#b87500"),
    "UC": dict(n="Unión Cívica", sub="Capital Federal", logo="UC", base="#000000", bar="#000000", txt="#333333"),
    "LDS": dict(n="Liga del Sur", sub="Santa Fe", logo="LDS", base="#005c9e"),
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


NOTE = ("Fuente de los departamentos: carpeta busqueda1912. Capital (20 circunscripciones) y Córdoba (21 de 26 departamentos): Cantón (1968, t. II); Mendoza (16 unidades): suma de las 188 mesas del expediente 42-D-1912; "
        "Santa Fe: 5 de 19 departamentos (Rosario, Las Colonias, San Lorenzo, Vera y Belgrano) del diario Santa Fe, escrutinio de abril de 1912 anterior al diploma. "
        "Las demás provincias (Buenos Aires, Catamarca, Corrientes, Entre Ríos, Jujuy, La Rioja, Salta, San Juan, San Luis, Santiago del Estero y Tucumán) no tienen cuadro departamental en la fuente: "
        "se pinta toda la provincia con el total de la Wikipedia. Cada partido cuenta los votos de su primer candidato (lista incompleta). "
        "Geometría: departamentos del censo de 1914 (los territorios nacionales no votaban). "
        "La Wikipedia imprime 73,20 % de participación nacional, pero 654.631 votantes sobre 935.001 inscriptos da 70,0 %: el mapa usa los números.")
NOTE = wikitop.note(1912) + " " + NOTE


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
        v = fn(prov_an[p]["a"])
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


def mode_par():
    """Participacion: solo hay dato provincial (Wikipedia: votos / electores registrados); cada departamento lleva el color de su provincia."""
    edges = [0, 55, 60, 65, 70, 75, 80]
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
     "Partidos Conservadores (como en la Wikipedia) = Partido Conservador, Constitucional, Autonomista Nacional, Partido Oficial, Partido Popular, Partido de la Coalición, Partido Liberal y Autonomista de Corrientes, Concentración Cívica y Partido Liberal de Tucumán. "),):
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
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True, antarctic=False, omit=("sj", "res"), sj_names={"Capital", "Santa Lucia", "Chimbas", "Rivadavia", "Pocito", "Albardon", "Trinidad", "Concepcion", "Desamparados", "Zonda", "Rawson"}, chaco_names={"Resistencia"})
body.append(X99["ant_body"])
INSETS = [
    dict(id="tuc", label="Tucumán", f=[450, 300, 200, 185], win=window(bbox_of(tuc), 200 / 185), show=["d", "pb"], sd=2.6, sp=3.4),
    dict(id="gba", label="Área Metropolitana de Buenos Aires", f=[1247, 785, 647, 320], win=[round(cx - gba_w * 0.42, 2), round(cy - gba_w / (647 / 320) * 0.5, 2), gba_w, round(gba_w / (647 / 320), 2)], show=["d", "pb", "out"], sd=1.9, sp=3.0, so=2.6),
    dict(id="caba", label="Capital Federal", f=[1632, 1187, 191, 232], win=window(caba_b, 191 / 232, 0.05), show=["dc"], sd=3, fit="meet", noframe=True, lx=1728, noclip=True, so=2.6),
]
GBA = INSETS[1]
INSETS = [X99["mza"], GBA] + ([X99["ant"]] if X99["ant"] else []) + INSETS[2:]   # sin Tucumán, Gran San Juan ni Resistencia: esas provincias van en un solo color
marks = [("gba", GBA["win"])] + X99["marks"]
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
    slug="diputados_1912", locale="es-AR", country="Argentina",
    title="Elecciones legislativas de Argentina de", year="1912",
    labels=dict(pie1="Proporción sobre votos positivos"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1912", subtitle="Deptos. de 1914")},
    modes=MODES, insets=INSETS, solid=sorted(SOLID),
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(HERE, "dataset_1912.json"), "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 1912</title>")
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
out = os.path.join(HERE, "atlas_1912_diputados.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)

