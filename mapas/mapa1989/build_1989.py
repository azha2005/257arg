#!/usr/bin/env python3
"""Atlas electoral 1989, presidente (estilo Wikipedia 1999), sobre los departamentos del censo de 1980.

    python build_1989.py            -> mapa1989/atlas_1989.html (+ dataset_1989.json)

Geometria : Base deptos 1869-2022/Departamentos_1980.shp (departamentos y partidos) + 28 circunscripciones de Capital Federal
            extraidas del SVG de Wikipedia 1999 (caba28.py; la numeracion oficial esta en CIRCUNSCRIPCIONES_CABA_28.md).
Datos     : base de Ernesto Calvo (TPDENP1989T.xls, hojas por provincia; ../base8399/ernesto/1989_presidente/dpto_partidos.csv).
Nacional  : tabla de «Elecciones presidenciales de Argentina de 1989» de la Wikipedia en espanol (../wikitop.py).
"""
import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
import sys, os, re, json, math, csv, pickle, collections, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np, shapely
from shapely.ops import unary_union
import geom
from names import norm

HERE = os.path.dirname(os.path.abspath(__file__))
LOGOS = os.path.join(HERE, "..", "../logos")   # emblemas de Wikipedia, ver LICENCIAS.md alli
TEMPLATE_SRC = os.path.join(HERE, "..", "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")
ERNESTO = os.path.join(HERE, "..", "../datos/base8399", "ernesto", "1989_presidente", "dpto_partidos.csv")

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


def fill_slivers(g, amax=0.15):
    """quita los huecos interiores de menos de amax (unidades de mapa^2): rendijas entre poligonos, no lagos ni islas"""
    from shapely.geometry import Polygon, MultiPolygon
    gs = g.geoms if hasattr(g, "geoms") else [g]
    out = [Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area >= amax]) for q in gs]
    return out[0] if len(out) == 1 else MultiPolygon(out)


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
    if p != 'Tierra del Fuego': prov_geom[p] = fill_slivers(prov_geom[p], 5.0 if p == 'Capital Federal' else 0.15)   # los huecos entre unidades dibujadas a mano (Capital) no son agua
country = unary_union(list(prov_geom.values())).buffer(0.1).buffer(-0.1)
# la boca del Riachuelo es un entrante de la costa entre Capital y Avellaneda que el contorno dibuja como un gancho: se cierra solo ese entrante
_cf, _ba = prov_geom["Capital Federal"], prov_geom["Buenos Aires"]
_win = shapely.box(_cf.bounds[0] - 3, _cf.bounds[1] - 3, _cf.bounds[2] + 3, _cf.bounds[3] + 3)
_n = unary_union([_ba, _cf]).buffer(0.5).buffer(-0.5).intersection(_win).difference(unary_union([_ba, _cf]))
_n = unary_union([q for q in (_n.geoms if hasattr(_n, "geoms") else [_n]) if q.area >= 0.1])
prov_geom["Capital Federal"] = unary_union([_cf, _n])
country = unary_union([country, _n])
prov_geom = {p: g.simplify(0.12) for p, g in prov_geom.items()}
country = country.simplify(0.12)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from outline_clean import clean_outline, clean_holes
country = clean_outline(country)    # quita huecos e islotes diminutos del contorno (puntos grises en San Luis y la costa de Buenos Aires)
prov_geom = {p: clean_holes(g, name=p) for p, g in prov_geom.items()}    # rellena rendijas diminutas dentro de cada provincia (puntos blancos en San Luis y Buenos Aires)
prov_mini = {p: g.simplify(0.7) for p, g in prov_geom.items()}

# nombres con tildes: los de territories.json (base de Wikipedia 1999), cuando coinciden
_T = json.load(open(os.path.join(HERE, "..", "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "territories.json"), encoding="utf8"))["units"]
NICE = {(t["prov"], norm(t["name"])): t["name"] for t in _T}

# ---------------------------------------------------------------- datos: base de Ernesto Calvo, presidente 1989
ENT = {}   # (provincia, nombre de la fuente) -> dict
for r in csv.DictReader(open(ERNESTO, encoding="utf-8-sig")):
    e = ENT.setdefault((r["provincia"], r["departamento"]), dict(prov=r["provincia"], name=r["departamento"], P={}, pos=None, bla=None, nul=None, tot=None, el=None))
    v = float(r["votos"]); v = int(v) if v == int(v) else v
    t = r["tipo_fila"]
    if t == "agrupacion": e["P"][r["codigo_partido"]] = e["P"].get(r["codigo_partido"], 0) + v
    elif t == "positivos": e["pos"] = v
    elif t == "blancos": e["bla"] = v
    elif t == "nulos": e["nul"] = v
    elif t == "total": e["tot"] = v
    elif t == "electores": e["el"] = v
# Errores de la base de Ernesto en 1989 (comparada con la tabla por distrito de Wikipedia, ver LEEME_1989.md):
# en 3 unidades falta la columna de la UCR y el total de positivos de la unidad si es correcto: se imputa el residuo (positivos - resto de fuerzas)
IMPUTAR = {("Salta", "r de la frontera"): "ucr", ("Corrientes", "saladas"): "ucr", ("San Juan", "25 de mayo"): "ucr"}
for k, c in IMPUTAR.items():
    e = ENT[k]; gap = e["pos"] - sum(e["P"].values())
    assert gap > 0 and c not in e["P"], (k, gap)
    e["P"][c] = gap
    e["imput"] = "Corregido: la base no trae la columna de la UCR en esta unidad; se imputó el residuo de los positivos (%s votos)." % ("{:,}".format(int(gap)).replace(",", "."))


# Unidades que la base trae como departamento aparte y el mapa de 1980 incluye en otra: se suman
def fusionar(nuevo, base, texto):
    n, b = ENT.pop(nuevo), ENT[base]
    for c, x in n["P"].items(): b["P"][c] = b["P"].get(c, 0) + x
    for k in ("pos", "bla", "nul", "tot", "el"):
        b[k] = (b[k] or 0) + (n[k] or 0)
    b["merged"] = texto
fusionar(("Entre Ríos", "islas de ibicuy"), ("Entre Ríos", "gualeguaychu"), "Incluye Islas del Ibicuy, que la base trae como departamento aparte y el mapa de 1980 incluye en Gualeguaychú.")
fusionar(("Jujuy", "palpala"), ("Jujuy", "capital"), "Incluye Palpalá, que la base trae como departamento aparte y el mapa de 1980 incluye en Capital.")
fusionar(("Buenos Aires", "Tres Lomas"), ("Buenos Aires", "Pellegrini"), "Incluye Tres Lomas, que la base trae como partido aparte y el mapa de 1980 incluye en Pellegrini.")
KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}

# nombre de la fuente -> poligono, cuando la comparacion de nombres no alcanza (los nombres de Ernesto son los de la base original)
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
    ("Chaco", "capital"): "San Fernando", ("La Rioja", "chamical"): "Gobernador Gordillo", ("La Rioja", "coronel felipe varela"): "General Lavalle",
    ("La Rioja", "penaloza"): "General Angel V. Peñaloza", ("La Rioja", "vera penaloza"): "Rosario Vera Peñaloza", ("La Rioja", "quiroga"): "General Juan F. Quiroga",
    ("Río Negro", "veinticinco de mayo"): "25 de Mayo", ("Santiago del Estero", "brig.j.f.ibarra"): "Brigadier J. Felipe Ibarra",
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
        unmatched.append((prov, n)); continue
    assert idx not in unit_src, (prov, n, U[idx]["name"])
    unit_src[idx] = e
print("Ernesto sin poligono:", unmatched, "| poligonos sin Ernesto:", [(U[i]["prov"], U[i]["name"]) for i in range(len(U)) if i not in unit_src], file=sys.stderr)
assert not unmatched

# ---------------------------------------------------------------- bloques (formulas de la tabla de Wikipedia) y partidos
BLOCS = ["MEN", "ANG", "ALS", "EBO", "MPN"]   # solo las fuerzas que ganan alguna unidad; el resto va en «otros»
# codigo de columna de la base -> formula, segun la tabla de Wikipedia (las sumas coinciden con ella salvo unos cientos de votos, ver LEEME_1989.md):
#   MEN (Menem-Duhalde, 7.957.518) = FREJUPO + Corriente Renovadora (Santiago del Estero) + PTP (Mendoza) + MID (La Rioja)
#   ANG (Angeloz, 6.213.217) = UCR + UCR-CFI + UCR-Movilizacion-MPC + CFI + CFI-Partido Federal + Partido Federal (la alianza UCR + CFI)
#   ALS (Alsogaray-Natale, 1.200.172) = Alianza de Centro + PAL-PDP-MLP (Corrientes) + UCD + PDP + Alianza de Centro-UCD
#   EBO (Estevez Boero-Bravo, 240.132) = Unidad Socialista + PSP + PS del Chaco y de Formosa + PSD
CODE2BLOC = {"frejupo": "MEN", "fcr": "MEN", "ptp": "MEN", "mid": "MEN",
             "ucr": "ANG", "ucrfi": "ANG", "ucrmc": "ANG", "cfi": "ANG", "cfifed": "ANG", "fed": "ANG",
             "adc": "ALS", "paldpml": "ALS", "ucd": "ALS", "pdp": "ALS", "adcucd": "ALS",
             "aus": "EBO", "us": "EBO", "psp": "EBO", "ps": "EBO", "psd": "EBO", "mpn": "MPN"}
LABEL = {"frejupo": "Frente Justicialista de Unidad Popular", "fcr": "Corriente Renovadora", "ptp": "Partido del Trabajo y del Pueblo", "mid": "Movimiento de Integración y Desarrollo",
         "ucr": "Unión Cívica Radical", "ucrfi": "UCR - Confederación Federalista Independiente", "ucrmc": "UCR - Movilización - Movimiento Popular Catamarqueño",
         "cfi": "Confederación Federalista Independiente", "cfifed": "CFI - Partido Federal", "fed": "Partido Federal", "adc": "Alianza de Centro",
         "paldpml": "Pacto Autonomista Liberal - PDP - Movimiento Liberación Popular", "ucd": "Unión del Centro Democrático", "pdp": "Partido Demócrata Progresista",
         "adcucd": "Alianza de Centro - UCD", "aiu": "Izquierda Unida", "bju": "Partido Blanco de los Jubilados", "aus": "Unidad Socialista", "us": "Unidad Socialista",
         "psp": "Partido Socialista Popular", "ps": "Partido Socialista del Chaco y de Formosa", "psd": "Partido Socialista Democrático", "fr": "Fuerza Republicana",
         "po": "Partido Obrero", "fhv": "Frente Humanista - Verde", "mpn": "Movimiento Popular Neuquino", "ablo": "Alianza Bloquista", "acha": "Acción Chaqueña",
         "cr": "Cruzada Renovadora", "ind": "Partido de la Independencia", "accp": "Acción Popular", "sol": "Partido Socialista Obrero para la Liberación", "mdpa": "Movimiento Democrático Popular Antiimperialista",
         "acpo": "Acuerdo Popular", "mur": "Movimiento Unidad Renovadora", "alr": "Azul, Lealtad, Restauración", "pd": "Partido Demócrata de Jujuy", "dlpp": "Partido Demócrata Liberal - Movimiento Popular Provincial",
         "jub": "Partido de los Jubilados", "lib": "Partido de la Liberación", "fren": "Frente Renovador", "tyc": "Tradición y Coherencia", "js": "Justicia Social",
         "ua": "Frente Unión Autonomista", "upro": "Unión Provincial", "apro": "Acción Provinciana", "dpbb": "Defensa Provincial - Bandera Blanca", "mpf": "Movimiento Popular Fueguino",
         "mn": "Movimiento Nacionalista", "upop": "Unificación Populista", "psa": "Partido Socialista Auténtico", "auf": "Partido Auténtico Formoseño", "pc": "Partido Comunista",
         "muc": "Movimiento de Unidad Chaqueña", "mpli": "Movimiento Patriótico de Liberación"}
# colores distintos entre si para las fuerzas de la leyenda; los demas, gris o un tono de su familia
COLOR = {"frejupo": "#318ce7", "fcr": "#318ce7", "ptp": "#318ce7", "mid": "#318ce7",
         "ucr": "#e10019", "ucrfi": "#e10019", "ucrmc": "#e10019", "cfi": "#e10019", "cfifed": "#e10019", "fed": "#e10019",
         "adc": "#8e6bd8", "paldpml": "#8e6bd8", "ucd": "#8e6bd8", "pdp": "#8e6bd8", "adcucd": "#8e6bd8",
         "aus": "#f59e0b", "us": "#f59e0b", "psp": "#f59e0b", "ps": "#f59e0b", "psd": "#f59e0b", "mpn": "#14306e",
         "aiu": "#c2399b", "bju": "#9a9a9a", "fr": "#8b5a2b", "po": "#a31515", "fhv": "#2e8b57", "ablo": "#44944a", "acha": "#2e8b57"}
DEFAULT_COL = "#9a9a9a"
for c in LABEL:
    COLOR.setdefault(c, DEFAULT_COL)
CAND = {
    "MEN": dict(n="Carlos Menem", sub="Frejupo y aliados", base="#318ce7", logo="PJ"),
    "ANG": dict(n="Eduardo Angeloz", sub="UCR + CFI", base="#e10019", logo="UCR"),
    "ALS": dict(n="Álvaro Alsogaray", sub="Alianza de Centro", base="#8e6bd8", logo="UCD"),
    "EBO": dict(n="Guillermo Estévez Boero", sub="Unidad Socialista", base="#f59e0b", bar="#d98a00", txt="#b86f00", logo="EBO"),
    "MPN": dict(n="Mov. Popular Neuquino", sub="Neuquén", base="#14306e", logo="MPN"),
}
for c, col in COLOR.items():
    CAND["P_" + c] = dict(n=LABEL[c], base=col, minor=True)
CAND["P_BLA"] = dict(n="En blanco", base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Anulados", base="#b0b0b0", minor=True)
CAND["P_OTR"] = dict(n="Otros", base="#9a9a9a", minor=True)


def _ar_svg(t):
    m = re.search(r'viewBox="([\d.\s-]+)"', t)
    if m:
        v = [float(x) for x in m.group(1).split()]
        return v[2] / v[3]
    w = re.search(r'\bwidth="([\d.]+)', t); h = re.search(r'\bheight="([\d.]+)', t)
    return float(w.group(1)) / float(h.group(1)) if w and h else 1.0


def _logo(fn, h=42):
    import base64
    t = open(os.path.join(LOGOS, fn), encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    ar = _ar_svg(t)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


def _logo_raster(fn, px=360, h=42):
    import base64, io
    from PIL import Image
    im = Image.open(os.path.join(LOGOS, fn)).convert("RGBA")
    ar = im.width / im.height
    k = px / max(im.size); im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


# logos: solo los de epoca (UCR: escudo de 1931; PJ: bandera cuadrada, diseno de 1946). PAL, Bloquista, MPN y MOFEPA llevan sigla: sus archivos de Commons son de 2018 a 2025.
# logos: solo los de epoca. UCR (escudo de 1931), PJ (bandera cuadrada, diseno de 1946) y UCeDe (infobox del articulo de 1985 y 1987); el resto lleva sigla
CAND["ANG"].update(_logo("Escudo_de_la_UCR.svg"))
CAND["MEN"].update(_logo_raster("Frejupo_logo_1989.png")); CAND["MEN"]["bl"] = 0.6   # el logo es muy ancho: con bl 0,69 se recortaba la O en el marco de 110 px
CAND["EBO"].update(_logo("Emblema_del_Partido_Socialista_Argentino.svg"))
CAND["MPN"].update(_logo_raster("Logo_MPN.png"))
CAND["ALS"].update(_logo_raster("UCEDE_logo_chico.png"))
GREY_N = "#8c8c8c"


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def analyse(e):
    P = dict(e["P"])
    pos = e["pos"] if e["pos"] is not None else sum(P.values())
    emit = e["tot"] if e["tot"] else pos + (e["bla"] or 0) + (e["nul"] or 0)
    bloc = {b: 0 for b in BLOCS}
    for c, x in P.items():
        b = CODE2BLOC.get(c)
        if b in bloc: bloc[b] += x
    return dict(P=P, pos=pos, E=emit, bla=e["bla"] or 0, nul=e["nul"] or 0, ins=e["el"], bloc=bloc, tab=sum(P.values()))


def rec_from(a, note=None):
    D = a["pos"]
    if not D: return None
    P = a["P"]
    lines = [["P_" + c, int(x), round(100 * x / D, 2)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x > 0]
    E = a["E"]
    if a["bla"]: lines.append(["P_BLA", int(a["bla"]), round(100 * a["bla"] / E, 2)])
    if a["nul"]: lines.append(["P_NUL", int(a["nul"]), round(100 * a["nul"] / E, 2)])
    met = []
    if a["ins"]: met.append(["Inscriptos", fmt_n(a["ins"])])
    met.append(["Votantes", fmt_n(E)])
    if a["ins"]: met.append(["Participación", fmt_p(100 * E / a["ins"]) + " %"])
    met.append(["Votos positivos", fmt_n(D)])
    w = max(a["bloc"], key=lambda b: a["bloc"][b])
    rec = {"lines": lines, "metrics": met}
    if a["bloc"][w] > 0 and a["bloc"][w] >= max(P.values() or [0]):
        rec.update(w=w, q=round(100 * a["bloc"][w] / D, 2))
    else:
        # gana un partido que no es uno de los bloques de la leyenda
        top = max(P, key=lambda c: P[c]) if P else None
        rec.update(fill=COLOR.get(top, GREY_N) if top else GREY_N)
    if note: rec["note"] = note
    return rec


unit_rec, unit_an = {}, {}
disp = {}
for i, u in enumerate(U):
    p = u["prov"]
    e = unit_src.get(i)
    nice = NICE.get((p, norm(u["name"])), u["name"])
    if p == "Capital Federal":
        num = int(u["name"].split()[1])
        disp[i] = "Circunscripción %d · %s" % (num, u.get("parroquia") or nice)
    else:
        disp[i] = nice
    if e is None:
        unit_rec[i] = None      # se completa con el dato provincial (Islas Malvinas)
        continue
    a = analyse(e); unit_an[i] = a
    extras = []
    if norm(e["name"]) != norm(u["name"]) and p != "Capital Federal": extras.append("Nombre en la base: «%s»." % e["name"])
    if e.get("merged"): extras.append(e["merged"])
    if e.get("imput"): extras.append(e["imput"])
    if e["tot"] is None: extras.append("La base no trae el total de votantes de esta unidad: se calculó como positivos + blancos + nulos.")
    unit_rec[i] = rec_from(a, " ".join(extras) or None)

# provincias y pais (suma de unidades de la base)
prov_an = {}
for i, a in unit_an.items():
    p = U[i]["prov"]
    t = prov_an.setdefault(p, dict(P={}, pos=0, E=0, bla=0, nul=0, ins=0, ins_ok=True, bloc={b: 0 for b in BLOCS}, tab=0))
    for c, x in a["P"].items(): t["P"][c] = t["P"].get(c, 0) + x
    t["pos"] += a["pos"]; t["E"] += a["E"]; t["bla"] += a["bla"]; t["nul"] += a["nul"]; t["tab"] += a["tab"]
    if a["ins"]: t["ins"] += a["ins"]
    else: t["ins_ok"] = False
    for b, x in a["bloc"].items(): t["bloc"][b] += x
for p, t in prov_an.items():
    if not t["ins_ok"]: t["ins"] = None
prov_rec = {p: rec_from(t, "Suma de los departamentos de la base de Ernesto Calvo.") for p, t in prov_an.items()}
# unidades sin dato propio (Islas Malvinas): heredan la provincia
for i in range(len(U)):
    if unit_rec[i] is None:
        r = dict(prov_rec[U[i]["prov"]]); r["note"] = "Sin dato propio: se muestra el resultado de la provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur."
        unit_rec[i] = r

# resultado nacional: tabla del articulo de Wikipedia (ver ../wikitop.py)
sys.path.insert(0, os.path.join(HERE, ".."))
import wikitop
cands, slices, partp, NAT_MET = wikitop.national(1989)
tot_ernesto = collections.Counter()
for t in prov_an.values():
    for b, x in t["bloc"].items(): tot_ernesto[b] += x
print("bloques segun la base:", dict(tot_ernesto), "| segun Wikipedia:", {c["code"]: c["votes"] for c in cands}, file=sys.stderr)

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


NOTE = ("Fuente: departamentos y provincias, base de Ernesto Calvo (datos del Ministerio del Interior, 14 may. 1989), porcentajes sobre votos positivos; "
        "resultado nacional (torta y barras): tabla de «Elecciones presidenciales de Argentina de 1989» de la Wikipedia en español. "
        "Geometría: departamentos del censo de 1980 y circunscripciones de Capital Federal del mapa de Wikipedia. Las fórmulas siguen los totales de la tabla de Wikipedia: "
        "Angeloz = UCR y CFI; Alsogaray = Alianza de Centro y aliados; Menem incluye a la Corriente Renovadora de Santiago del Estero. "
        "Se corrigieron 3 cifras de la base de Ernesto que no cierran con el total de la unidad (ver cada unidad y LEEME_1989.md).")
KEYS = []


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(U)):
        r = unit_rec[i]; a = unit_an.get(i)
        p = fn(a) if (a and a["pos"]) else None
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        if p is None:   # Islas Malvinas: dato de la provincia
            p = fn(prov_an[U[i]["prov"]])
        nr["fill"] = cols[bin_of(p, edges)] if p is not None else GREY_N
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        v = fn(prov_an[p])
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False)


# estilo del mapa de 1995: Malvinas en gris con contorno negro (no se pintan con el color de Tierra del Fuego)
MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}
_MAL_REC = dict(lines=[], metrics=[], fill="#a9a9a9", note="Sin dato: islas bajo administración británica (se muestran en gris).")
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec,
              national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend={})]
for mid, tile, fn, base, edges, title, extra in (
    ("men", "MEN", lambda a: 100 * a["bloc"]["MEN"] / a["pos"], "#318ce7", [0, 30, 40, 50, 60, 70, 80], "% Menem - Duhalde", ""),
    ("ang", "ANG", lambda a: 100 * a["bloc"]["ANG"] / a["pos"], "#e10019", [0, 20, 30, 40, 50, 60, 70], "% Angeloz (UCR + CFI)", ""),
    ("als", "ALS", lambda a: 100 * a["bloc"]["ALS"] / a["pos"], "#8e6bd8", [0, 2, 5, 10, 15, 20, 30], "% Alsogaray (Alianza de Centro)", "")):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, note=extra + NOTE, units=un, prov=pv,
                      national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=lg))

for _m in MODES:
    for _i in MALV: _m["units"][_i] = dict(_MAL_REC)

# ---------------------------------------------------------------- SVG
body = []
for i, u in enumerate(U):
    body.append('<path class="d" data-i="%d" d="%s"%s/>' % (i, geom_d(G[i]), ' style="stroke:#1b1b1b;stroke-width:1px"' if i in MALV else ""))
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
    return shapely.total_bounds([G_raw[i] for i in idx])


def window(b, aspect, pad=0.07):
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
import insets99
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True)    # los siete recuadros de Wikipedia 1999: tuc, sj, mza, res, gba, ant, caba
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
for _i, _u in enumerate(U):   # Malvinas en gris tambien en el mini de provincias (la simplificacion de provincias las borra)
    if _u["name"] == "Islas Malvinas":
        pv.append('<path class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round" d="%s"/>' % geom_d(G[_i]))
pv.append("</g>")

# dataset ----------------------------------------------------------------
ds = dict(
    slug="elecciones_1989", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de Argentina de", year="1989",
    labels=dict(pie1="Proporción sobre votos positivos"),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1989", subtitle="Base de E. Calvo · deptos. de 1980")},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(HERE, "dataset_1989.json"), "w", encoding="utf8"), ensure_ascii=False)

# template ---------------------------------------------------------------
tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Elecciones presidenciales 1989</title>")
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"', 'style="--v-d:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub('<g id="pv" transform="matrix(0.1448 0 0 0.1448 55.7 599.8)" style="--spf:9.7px">', '<g id="pv" transform="matrix(%s 0 0 %s %s %s)" style="--spf:9.7px">' % (KPV, KPV, f2(pv_tx), f2(pv_ty)))
sub("#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}", "#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}")
# recuadros dirigidos por el dataset
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
  const KEYS=LG0&&LG0.keys?LG0:null;
  const USED=c=>[...document.querySelectorAll('#B .d,#B .dc')].some(e=>(e.getAttribute("fill")||"").toLowerCase()===c.toLowerCase());   // solo se rotula el gris que alguna unidad usa en este modo
  """)
sub("if(LG&&LG.keys){", "if(KEYS){")
sub("LG.keys.forEach(", "KEYS.keys.filter(([k])=>USED(k)).forEach(")
sub("const rows=(LG&&LG.bars===false)?[]:N.cands;", "const rows=(LG0&&LG0.bars===false)?[]:N.cands;")
# pie sin segundo texto cuando no hay participacion
sub("""$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;""", """$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;$("#pie1").setAttribute("x",184);""")
# leyenda de 9 bloques: empieza mas arriba (bajo el mini de provincias) y con barras mas bajas
sub('''el("text",{x:93,y:1266,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=1292''',
    '''const MANY=N.cands.length>5,Y0=MANY?1024:1266;
  el("text",{x:93,y:Y0,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=Y0+26;''')
sub("const h=50,win=idx===0&&!LG", "const h=MANY?42:50,k=h/50,win=idx===0&&!LG")
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
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(HERE, "atlas_1989.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
