#!/usr/bin/env python3
"""Atlas de las elecciones peronistas 1946-1973, estilo Wikipedia 1999 (mismo diseño que canton5865/atlas5865.py).

    python transcripciones/peronismo/atlas4673.py 1946    -> mapas/mapa1946/   presidente, 24-feb-1946 (Cantón)
    python transcripciones/peronismo/atlas4673.py 1948    -> mapas/mapa1948/   diputados, 7-mar-1948 (Lupu-Stokes)
    python transcripciones/peronismo/atlas4673.py 1948c   -> mapas/mapa1948c/  convencionales constituyentes, 5-dic-1948 (Lupu-Stokes)
    python transcripciones/peronismo/atlas4673.py 1954    -> mapas/mapa1954/   diputados, 25-abr-1954 (Cantón)
    python transcripciones/peronismo/atlas4673.py 1973    -> mapas/mapa1973/   presidente, 11-mar-1973 (Lupu-Stokes)
    python transcripciones/peronismo/atlas4673.py 1973s   -> mapas/mapa1973s/  presidente, 23-sep-1973 (Lupu-Stokes)

Datos     : fuentes4673.py (Cantón 1968, t. II, o Lupu y Stokes 2009 con el «otros» repartido según la Wikipedia, estimado).
Geometría : geom4673.py (1947 / 1960 / 1970; provincia de Buenos Aires con el shapefile de 1955 del usuario).
Resultado nacional: comun/wikitop.py (tabla del artículo de la Wikipedia).
"""
import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]
import sys, os, re, json, pickle, base64, io
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(H, "..")
sys.path.insert(0, H); sys.path.insert(0, os.path.join(ROOT, "canton5865"))
import numpy as np, shapely
from shapely.ops import unary_union
import geom60, geom4673, fuentes4673, wikiprov4673
from names import norm
import wikitop, insets99
from outline_clean import clean_outline, clean_holes

K = sys.argv[1] if len(sys.argv) > 1 else "1954"
Y = int(K[:4])
OUTDIR = os.path.join(ROOT, "../mapas/mapa%s" % K)
os.makedirs(OUTDIR, exist_ok=True)
LOGOS = os.path.join(ROOT, "../logos")
TEMPLATE_SRC = os.path.join(ROOT, "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

# ---------------------------------------------------------------- configuración por elección
PJ_C, UCR_C, CON_C = "#318ce7", "#e10019", "#1f2f6b"
PJ_IMG, UCR_IMG = ("Flag_PJ_escudo_clasico_cuadrada.svg", None), ("Escudo_de_la_UCR.svg", None)
TERR46 = ("Chaco", "Chubut", "Formosa", "La Pampa", "Misiones", "Neuquén", "Río Negro", "Santa Cruz", "Tierra del Fuego")
TERR54 = ("Chubut", "Formosa", "Misiones", "Neuquén", "Río Negro", "Santa Cruz", "Tierra del Fuego")
NO_TERR = "%s era territorio nacional: sus habitantes no votaban en las elecciones nacionales (derecho reconocido por la reforma de 1949)."
NO_TERR54 = ("%s era territorio nacional: no elegía diputados nacionales. Votó vicepresidente (Santa Cruz, delegados): esas cifras de Cantón "
             "están en la ficha, pero la unidad no se colorea.")
C1948 = dict(PP=dict(n="Partido Peronista", sub="PP", base=PJ_C, logo="PP", img=PJ_IMG),
             UCR=dict(n="Unión Cívica Radical", sub="UCR", base=UCR_C, logo="UCR", img=UCR_IMG),
             PS=dict(n="Partido Socialista", sub="PS", base="#ff9900", logo="PS", img=("Emblema_del_Partido_Socialista_Argentino.svg", None)),
             PD=dict(n="Partido Demócrata", sub="Conservadores", base=CON_C, logo="PD"),
             PDP=dict(n="Demócrata Progresista", sub="PDP", base="#005c9e", logo="PDP", img=("Escudo_del_PDP.svg", None)),
             PC=dict(n="Partido Comunista", sub="PC", base="#8b1a1a", logo="PC"),
             POR=dict(n="Partido Obrero de la Revolución", sub="Santa Fe", base="#6a1b9a", logo="POR"),
             FOR=dict(n="Frente Obrero Revolucionario", sub="Tucumán", base="#4a148c", logo="FOR"),
             CO=dict(n="Concentración Obrera", sub="CO", base="#795548", logo="CO"),
             PSRN=dict(n="Socialista de la Revolución Nacional", sub="PSRN", base="#ff7043", logo="PSRN"))
C1973 = dict(FJL=dict(n="Héctor J. Cámpora", sub="FREJULI", base=PJ_C, logo="FJL", img=PJ_IMG),
             UCR=dict(n="Ricardo Balbín", sub="UCR", base=UCR_C, logo="UCR", img=UCR_IMG),
             APF=dict(n="Francisco Manrique", sub="APF", base="#e6b800", logo="APF"),
             APR=dict(n="Oscar Alende", sub="APR", base="#d10047", logo="APR"),
             ARF=dict(n="Ezequiel Martínez", sub="ARF", base="#2e7d32", logo="ARF"),
             NF=dict(n="Julio Chamizo", sub="Nueva Fuerza", base="#29c0ef", logo="NF"),
             PSD=dict(n="Américo Ghioldi", sub="PSD", base="#ffad00", logo="PSD", img=("Partido_Socialista_Democratico_Argentina.png", None)),
             PST=dict(n="Juan Carlos Coral", sub="PST", base="#8b0000", logo="PST"),
             FIP=dict(n="Jorge Abelardo Ramos", sub="FIP", base="#b22222", logo="FIP"))
CFG = {
    "1946": dict(src="canton", title="Elecciones presidenciales de Argentina de", tab="Elecciones presidenciales 1946", cargo="presidente",
                 fuente="elección de electores de presidente del 24 de febrero de 1946", geo="deptos. de 1947",
                 cand=dict(PER=dict(n="Juan Domingo Perón", sub="Laborismo y UCR-JR", base=PJ_C, logo="PER", img=PJ_IMG),
                           UD=dict(n="José P. Tamborini", sub="Unión Democrática", base=UCR_C, logo="UD"),
                           PDN=dict(n="Partido Demócrata Nacional", sub="Conservadores", base=CON_C, logo="PDN"),
                           UCRB=dict(n="UCR Bloquista", sub="San Juan", base="#44944a", logo="UCRB", img=("Estrella_bloquista.png", None)),
                           UCRSE=dict(n="UCR de Santiago del Estero", sub="Unificada", base="#a52a2a", logo="UCRU"),
                           LEN=dict(n="UCR Lencinista", sub="Mendoza", base="#ff5500", logo="UCRL")),
                 modes=[("per", "PER", "PER", PJ_C, [0, 30, 40, 50, 60, 70, 80], "% Perón"),
                        ("ud", "UD", "UD", UCR_C, [0, 20, 30, 40, 50, 60, 70], "% Tamborini (Unión Democrática)")],
                 noeleccion={p: NO_TERR % p for p in TERR46}, solid={}, par=True),
    "1948": dict(src="ls", title="Elecciones legislativas de Argentina de", tab="Diputados nacionales 1948", cargo="diputados",
                 fuente="diputados nacionales, 7 de marzo de 1948", geo="deptos. de 1947", cand=C1948,
                 modes=[("pp", "PP", "PP", PJ_C, [0, 30, 40, 50, 60, 70, 80], "% Partido Peronista"),
                        ("ucr", "UCR", "UCR", UCR_C, [0, 10, 20, 30, 40, 50, 60], "% Unión Cívica Radical")],
                 noeleccion=dict({p: NO_TERR % p for p in TERR46},
                                 **{p: "%s no renovó diputados nacionales en marzo de 1948 (tabla del artículo de la Wikipedia)." % p
                                    for p in ("Catamarca", "Jujuy", "La Rioja", "Salta")}), solid={}, par=False),
    "1948c": dict(src="ls", title="Elecciones de convencionales constituyentes de Argentina de", tab="Constituyentes 1948", cargo="constituyentes",
                  fuente="convencionales constituyentes, 5 de diciembre de 1948", geo="deptos. de 1947", cand=C1948,
                  modes=[("pp", "PP", "PP", PJ_C, [0, 40, 50, 60, 70, 80, 90], "% Partido Peronista"),
                         ("ucr", "UCR", "UCR", UCR_C, [0, 10, 20, 30, 40, 50, 60], "% Unión Cívica Radical")],
                  noeleccion={p: NO_TERR % p for p in TERR46},
                  solid={p: "Lupu y Stokes no traen %s en diciembre de 1948: se pinta la provincia con el total de la Wikipedia." % p
                         for p in ("Córdoba", "Corrientes", "Mendoza")}, par=False),
    "1954": dict(src="canton", title="Elecciones legislativas de Argentina de", tab="Diputados nacionales 1954", cargo="diputados",
                 fuente="diputados nacionales, 25 de abril de 1954", geo="deptos. de 1960", cand=C1948,
                 modes=[("pp", "PP", "PP", PJ_C, [0, 40, 50, 60, 70, 80, 90], "% Partido Peronista"),
                        ("ucr", "UCR", "UCR", UCR_C, [0, 10, 20, 30, 40, 50, 60], "% Unión Cívica Radical")],
                 noeleccion={p: NO_TERR54 % p for p in TERR54}, solid={}, par=True),
    "1973": dict(src="ls", title="Elecciones presidenciales de Argentina de marzo de", tab="Elecciones presidenciales marzo 1973", cargo="presidente",
                 fuente="elección presidencial del 11 de marzo de 1973", geo="deptos. de 1970", cand=C1973,
                 modes=[("fjl", "FJL", "FJL", PJ_C, [0, 30, 40, 50, 60, 70, 80], "% Cámpora (FREJULI)"),
                        ("ucr", "UCR", "UCR", UCR_C, [0, 10, 20, 30, 40, 50, 60], "% Balbín (UCR)"),
                        ("apf", "APF", "APF", "#e6b800", [0, 10, 20, 30, 40, 50, 60], "% Manrique (APF, estimado)")],
                 noeleccion={}, solid={"Tierra del Fuego": "Lupu y Stokes no traen Tierra del Fuego: se pinta el territorio con el total de la Wikipedia."}, par=False),
    "1973s": dict(src="ls", title="Elecciones presidenciales de Argentina de septiembre de", tab="Elecciones presidenciales septiembre 1973", cargo="presidente",
                  fuente="elección presidencial del 23 de septiembre de 1973", geo="deptos. de 1970",
                  cand=dict(C1973, FJL=dict(n="Juan Domingo Perón", sub="FREJULI y FIP", base=PJ_C, logo="FJL", img=PJ_IMG),
                            APF=dict(C1973["APF"]), PST=dict(C1973["PST"])),
                  modes=[("fjl", "FJL", "FJL", PJ_C, [0, 40, 50, 60, 70, 80, 90], "% Perón (FREJULI y FIP)"),
                         ("ucr", "UCR", "UCR", UCR_C, [0, 10, 20, 30, 40, 50, 60], "% Balbín (UCR)"),
                         ("apf", "APF", "APF", "#e6b800", [0, 5, 10, 15, 20, 25, 30], "% Manrique (APF, estimado)")],
                  noeleccion={}, solid={"Tierra del Fuego": "Lupu y Stokes no traen Tierra del Fuego: se pinta el territorio con el total de la Wikipedia."}, par=False),
}
C = CFG[K]
LS = C["src"] == "ls"
GREY_NE, GREY_SD, GREY_N, GREY_MAL, GREY_OTR = "#cfcfcf", "#e6dcc3", "#8c8c8c", "#a9a9a9", "#9a9a9a"
GREY_PAD = "#dadada"
SRC_NAME = "Lupu y Stokes" if LS else "Cantón"
KEYS = [[GREY_NE, {"presidente": "Sin elección propia (territorio nacional)", "diputados": "Sin elección de diputados nacionales",
                   "constituyentes": "Sin elección (territorio nacional)"}[C["cargo"]]],
        [GREY_SD, "Sin dato propio en %s" % SRC_NAME], [GREY_OTR, "Gana un partido sin bloque en el atlas"]]

# ---------------------------------------------------------------- proyección (la misma de los demás atlas)
S, X0, Y0 = 44.0, 643.0, 150.0
LON0, LAT1 = -73.5708041, -21.7807776


def proj(a):
    a = np.asarray(a, float).copy()
    a[:, 0] = (a[:, 0] - LON0) * geom60.KX * S + X0
    a[:, 1] = (LAT1 - a[:, 1]) * S + Y0
    return a


def ll(lon, lat):
    return ((lon - LON0) * geom60.KX * S + X0, (LAT1 - lat) * S + Y0)


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
        if len(pts) >= 2: out.append("M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts))
    return "".join(out)


def fmt_n(v): return "{:,}".format(int(v)).replace(",", ".")
def fmt_p(v): return ("%.1f" % v).replace(".", ",")


# ---------------------------------------------------------------- geometría
PKL = os.path.join(OUTDIR, "units_raw.pkl")
if not os.path.exists(PKL):
    pickle.dump(geom4673.load(K), open(PKL, "wb"))
U = pickle.load(open(PKL, "rb"))
U.sort(key=lambda u: (u["prov"], u["name"]))
G_raw = [shapely.transform(u["geom"], proj) for u in U]
G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.3))
PROVS = sorted(set(u["prov"] for u in U))
prov_geom = {}
for p in PROVS:
    prov_geom[p] = unary_union([G[i].buffer(0.12) for i, u in enumerate(U) if u["prov"] == p]).buffer(-0.12)
country = unary_union(list(prov_geom.values())).buffer(0.1).buffer(-0.1)
prov_geom = {p: g.simplify(0.12) for p, g in prov_geom.items()}
country = clean_outline(country.simplify(0.12))
prov_geom = {p: clean_holes(g, name=p) for p, g in prov_geom.items()}
prov_mini = {p: g.simplify(0.7) for p, g in prov_geom.items()}

# ---------------------------------------------------------------- datos
if LS:
    COLMAP, REPARTO, NOTAS_LS = fuentes4673.reparto_ls(K)
    D = fuentes4673.lupu_stokes(K, REPARTO, COLMAP)
else:
    D = fuentes4673.canton(K)
WPROV = wikiprov4673.provincial(K) if LS else {}
KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
ALIAS = {   # nombre en la fuente -> polígono (cambios de nombre u ortografía)
    ("Buenos Aires", "General Madariaga"): "General Juan Madariaga", ("Buenos Aires", "Matanza"): "La Matanza",
    ("Buenos Aires", "9 de Julio"): "Nueve de julio", ("Buenos Aires", "Lanús"): "4 de Junio", ("Buenos Aires", "González Chaves"): "Adolfo Gonzáles Chaves",
    ("Buenos Aires", "Gonzales Chaves"): "Adolfo Gonzáles Chaves", ("Buenos Aires", "Juárez"): "Benito Juarez",
    ("Buenos Aires", "C. de M. Leonardo Rosales"): "Coronel de marina Leonardo Rosales", ("Buenos Aires", "Leandro N. Alem"): "Leandro N.Alem",
}
if Y == 1973: ALIAS = {}   # los de arriba son para los partidos bonaerenses de 1955
ALIAS60 = {   # los mismos del atlas de 1958 (polígonos de 1960)
    ("Córdoba", "Ischillín"): "Ischilín", ("Córdoba", "Pte. Roque Saenz Peña"): "Pdte.Roque Saenz Peña",
    ("Chaco", "Cap. General O'Higgins"): "O´Higgins", ("Chaco", "Fray Justo S. María de Oro"): "Fray Justo Sta.Ma. De Oro",
    ("Chaco", "Lib. General San Martín"): "Libertador Gnral Sn Martín", ("Chaco", "9 de Julio"): "Nueve de Julio",
    ("Chaco", "Presidencia de la Plaza"): "Pdte. De la Plaza", ("Chaco", "Sargento Cabral"): "Sgto. Cabral",
    ("Chubut", "Río Senguerr"): "Río Senguer", ("Entre Ríos", "Concepción del Uruguay"): "Uruguay", ("Entre Ríos", "Rosario Tala"): "Tala",
    ("La Pampa", "Conhello"): "Conhelo", ("La Rioja", "Rivadavia"): "Gnral.Juan F.Quiroga", ("La Rioja", "Facundo Quiroga"): "Gnral.Juan F.Quiroga",
    ("Mendoza", "Luján"): "Lujan de Cuyo", ("Misiones", "Candelarias"): "Candelaria", ("Misiones", "Lib. General San Martín"): "Gral.San martín",
    ("Río Negro", "General Conesa"): "Conesa", ("Salta", "Caldera"): "La Caldera", ("Salta", "Candelaria"): "La Candelaria",
    ("Salta", "General José de San Martín"): "Gnral.José San Martín", ("Salta", "General Martín Miguel de Güemes"): "Gnral.Guemes",
    ("Salta", "Gral. Martín Miguel de Güemes"): "Gnral.Guemes", ("San Juan", "Ullún"): "Ullum",
    ("San Luis", "Gobernador Vicente Dupuy"): "Gobernador Dupuy", ("San Luis", "Pringles"): "Coronel pringles",
    ("San Luis", "San Martín"): "Libertador Gral.Sn Martín", ("Santa Fe", "Nueve de Julio"): "9 de Julio",
    ("Santiago del Estero", "Matará"): "Juan F.Ibarra", ("Tucumán", "Tafí"): "Tafi Viejo",
}
ALIAS.update({tuple(k.split("|")): v for k, v in json.load(open(os.path.join(H, "alias_%s.json" % ("1960" if Y == 1954 else "1970" if Y == 1973 else "1947")), encoding="utf8")).items()}
             if os.path.exists(os.path.join(H, "alias_%s.json" % ("1960" if Y == 1954 else "1970" if Y == 1973 else "1947"))) else {})
if Y == 1954:
    for k, v in ALIAS60.items(): ALIAS.setdefault(k, v)
CAP = {norm(k): v for k, v in {"Vélez Sarsfield": 1, "San Cristóbal Sud": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sud": 6,
       "San Carlos Norte": 7, "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sud": 10, "Balvanera Norte": 11, "Concepción": 12,
       "Monserrat": 13, "San Nicolás": 14, "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18, "Pilar": 19, "Socorro": 20}.items()}


def alias_key(p, n):
    return ALIAS.get((p, n)) or n


src, unmapped = {}, []
for (p, n), d in D.items():
    if p == "Capital Federal":
        k = int(n) if n.isdigit() else CAP.get(norm(n))
        i = KEY.get((p, norm("Circ. %02d" % k))) if k else None
    else:
        i = KEY.get((p, norm(alias_key(p, n))))
    if i is None or ALIAS.get((p, n), 1) is None:
        unmapped.append((p, n, d.get("vot") or d.get("tot"))); continue
    assert i not in src, (p, n, U[i]["name"], src[i][0])
    src[i] = (n, d)
print(K, "sin polígono:", unmapped, file=sys.stderr)
json.dump([[p, n] for p, n, v in unmapped if v], open(os.path.join(OUTDIR, "sin_poligono_%s.json" % K), "w", encoding="utf8"), ensure_ascii=False, indent=0)
# filas sin correspondencia segura con un polígono (nombres de 1954 que no siguen en los mapas posteriores): quedan fuera del mapa
SIN_LUGAR = {("Chaco", "Cabo Mayor Farina"), ("Chaco", "12 de Abril")} | {k for k, v in ALIAS.items() if v is None}
assert all(not v or (p, n) in SIN_LUGAR for p, n, v in unmapped), [x for x in unmapped if x[2] and (x[0], x[1]) not in SIN_LUGAR]
NOTE_SIN_LUGAR = {}
PLACE_NOTE = {("San Juan", "Desamparados"): "Capital", ("Salta", "General San Martin"): "Oran"}   # fila sin polígono propio -> polígono que la contiene
for p, n, v in unmapped:
    if (p, n) in PLACE_NOTE and v:
        NOTE_SIN_LUGAR[(p, PLACE_NOTE[(p, n)])] = ("Lupu y Stokes traen además una fila «%s» (%s votos) sin polígono propio en el mapa de 1947; "
                                                   "no se suma a esta unidad." % (n, fmt_n(v)))
if Y == 1954:
    _t = "; ".join("«%s» (%s votantes)" % (n, fmt_n(v)) for p, n, v in unmapped if (p, n) in SIN_LUGAR)
    for n60 in ("12 de Octubre", "Tapenaga"):
        NOTE_SIN_LUGAR[("Chaco", n60)] = ("En 1954 los departamentos del Chaco tenían nombres de la época peronista. Por votantes, «24 de Febrero» se "
            "asignó a Mayor Luis J. Fontana y «Güemes» a General Güemes; no se encontró correspondencia segura para %s, que deberían ser "
            "este departamento y su vecino: se dejan sin pintar." % _t)

# partidos -> código de línea de ficha (P_k), con el color de su bloque
PCODE = {}


def pcode(name, b):
    k = (name, b)
    if k not in PCODE:
        PCODE[k] = "P_%d" % len(PCODE)
    return PCODE[k]


CAND = {b: {k: v for k, v in c.items() if k != "img"} for b, c in C["cand"].items()}
BLOCS = list(C["cand"])


def competidores(parties):
    """bloques sumados; los partidos sin bloque compiten cada uno por su cuenta"""
    c = {}
    for n, v, b in parties:
        k = b or ("~" + n)
        c[k] = c.get(k, 0) + v
    return c


def rec_from(parties, bla, nul, ins, vot, extra=None, color=True, tot=None, est=False):
    """parties: [(nombre, votos, bloque)] -> ficha con líneas, métricas, ganador y % sobre votos positivos."""
    pos = sum(v for _, v, _ in parties)
    if pos <= 0: return None
    lines = [[pcode(n, b), int(v), round(100 * v / pos, 2)] for n, v, b in sorted(parties, key=lambda x: -x[1]) if v > 0]
    E = pos + bla + nul
    if bla: lines.append(["P_BLA", int(bla), round(100 * bla / E, 2)])
    if nul: lines.append(["P_NUL", int(nul), round(100 * nul / E, 2)])
    met = []
    if ins: met.append(["Inscriptos", fmt_n(ins)])
    if vot: met.append(["Votantes", fmt_n(vot)])
    if ins and vot and vot <= ins: met.append(["Participación", fmt_p(100 * vot / ins) + " %"])
    met.append(["Votos positivos" + (" (est.)" if est else ""), fmt_n(pos)])
    if tot: met.append(["Total en Lupu y Stokes", fmt_n(tot)])
    rec = {"lines": lines, "metrics": met}
    cp = competidores(parties)
    w = max(cp, key=cp.get)
    if color:
        if w in BLOCS: rec.update(w=w, q=round(100 * cp[w] / pos, 2))
        else: rec["fill"] = GREY_OTR
    notes = []
    if vot and ins and vot > ins: notes.append("En la fuente los votantes (%s) superan a los inscriptos (%s): no se calcula la participación." % (fmt_n(vot), fmt_n(ins)))
    if vot and abs(pos + bla + nul - vot) > max(30, 0.01 * vot):
        notes.append("En la fuente la suma de partidos, blancos y anulados (%s) no coincide con los votantes (%s)." % (fmt_n(pos + bla + nul), fmt_n(vot)))
    if extra: notes.append(extra)
    if notes: rec["note"] = " ".join(notes)
    return rec


EST_NOTE = ("Lupu y Stokes solo distinguen peronismo, UCR, socialistas y conservadores; las filas «(est.)» son una estimación: el resto de la "
            "unidad (su total menos esas familias) se repartió entre los demás partidos de la tabla provincial de la Wikipedia, en proporción "
            "a sus votos en la provincia.")
SUBS_NOTE = "Cantón (t. I, apéndice C) incluye las cifras de %s dentro de las de %s: se pinta el conjunto con ese resultado."

AN = {}   # unidad -> agregados para las coropletas
unit_rec, disp = {}, {}
MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}
for i, u in enumerate(U):
    p = u["prov"]
    geo_note = u.get("nota_geo")
    if i in MALV:
        unit_rec[i] = dict(lines=[], metrics=[], fill=GREY_MAL, note="Sin dato: islas bajo administración británica (se muestran en gris)."); continue
    if p in C["solid"]: unit_rec[i] = None; continue
    if i not in src:
        unit_rec[i] = dict(lines=[], fill=GREY_NE if p in C["noeleccion"] else GREY_SD,
                           note=(C["noeleccion"].get(p) or NOTE_SIN_LUGAR.get((p, u["name"])) or "%s no trae fila para esta unidad." % SRC_NAME) + (" " + geo_note if geo_note else "")); continue
    n, d = src[i]
    disp[i] = ("Circunscripción %d · %s" % (u["circ"], n)) if (p == "Capital Federal" and not n.isdigit()) else (
        "Circunscripción %d" % u["circ"] if p == "Capital Federal" else n)
    extras = []
    if geo_note: extras.append(geo_note)
    if u.get("cedio"): extras.append("Polígono sin %s, que tiene polígono propio." % " ni ".join(u["cedio"]))
    if d.get("solo_varones"): extras.append("Cantón solo publica los votos de varones de esta provincia en 1954: la ficha y el color son de varones solamente.")
    for x in d.get("zona_cr_extra", []):
        extras.append("La parte de este departamento que pertenecía a la Zona Militar de Comodoro Rivadavia votó aparte: %s." %
                      ", ".join("%s %s" % (pn, fmt_n(v)) for pn, v, _ in x["parties"]))
    if d.get("zona_cr"): extras.append("Cantón lo publica dentro de la Zona Militar de Comodoro Rivadavia (1944-1955).")
    if K == "1946" and p == "San Luis":
        extras.append("Cantón (p. 167) rotula la col. 3 como Unión Democrática y la 4 como Laborista; la Wikipedia da los mismos totales al revés "
                      "(Tamborini 17.784, Perón 15.576) y la UD ganó los 10 electores de San Luis. Se dejan las cifras como las publica Cantón.")
    if NOTE_SIN_LUGAR.get((p, u["name"])): extras.append(NOTE_SIN_LUGAR[(p, u["name"])])
    if d.get("est"): extras.append(EST_NOTE)
    if LS and NOTAS_LS.get(p): extras.append("Provincia: " + "; ".join(NOTAS_LS[p]) + ".")
    if not d["parties"]:
        unit_rec[i] = dict(lines=[], fill=GREY_NE if p in C["noeleccion"] else GREY_SD,
                           note="%s trae la fila «%s» sin cifras." % (SRC_NAME, n) + (" " + " ".join(extras) if extras else "")); continue
    if p in C["noeleccion"]:
        r = rec_from(d["parties"], d["bla"], d["nul"], d["ins"], d["vot"], color=False,
                     extra=" ".join([C["noeleccion"][p]] + extras).strip())
        r["fill"] = GREY_NE
        unit_rec[i] = r; continue
    unit_rec[i] = rec_from(d["parties"], d["bla"], d["nul"], d["ins"], d["vot"], extra=" ".join(extras) or None, tot=d.get("tot"), est=d.get("est"))
    pos = sum(v for _, v, _ in d["parties"])
    bl = {}
    for _, v, b in d["parties"]: bl[b] = bl.get(b, 0) + v
    AN[i] = dict(pos=pos, bloc=bl, ins=d["ins"], vot=d["vot"])

# unidades que Cantón suma dentro de otra (apéndice C): se pintan con el resultado del conjunto
if not LS:
    subs = dict(fuentes4673.SUBSUME)
    for (p, n), (yy, host) in fuentes4673.SUBSUME_YEAR.items():
        if yy == K: subs[(p, n)] = host
    groups = {}
    for (p, n), host in subs.items():
        i = KEY.get((p, norm(alias_key(p, n)))); j = KEY.get((p, norm(alias_key(p, host))))
        if i is None or j is None or j not in AN or i in AN: continue
        groups.setdefault(j, []).append(i)
    for j, mem in groups.items():
        names = [U[i]["name"] if (U[i]["prov"], U[i]["name"]) not in () else "" for i in mem]
        names = [src[i][0] if i in src else U[i]["name"] for i in mem]
        note = SUBS_NOTE % (", ".join(names), src[j][0])
        unit_rec[j] = dict(unit_rec[j]); unit_rec[j]["note"] = (unit_rec[j].get("note", "") + " " + note).strip()
        for i in mem:
            r = dict(unit_rec[j]); r["note"] = note
            unit_rec[i] = r; AN[i] = AN[j]; disp[i] = disp.get(i) or U[i]["name"]

# ---------------------------------------------------------------- provincias
def wiki_parties(p):
    rows = WPROV.get(p) or []
    parties = [(n, v, fuentes4673.bloque_wiki(K, n)) for n, v in rows if not n.startswith("#") and v]
    tot = {n[1:].lower(): v for n, v in rows if n.startswith("#") and v}
    pos = sum(v for _, v, _ in parties)
    vot = tot.get("total de votos") or tot.get("votantes")
    ins = tot.get("votantes registrados/participación")
    bla = (tot.get("blanco", 0) + tot.get("nulo", 0)) if "blanco" in tot else ((vot - pos) if vot else 0)
    return parties, bla, ins, vot


def wiki_solid_1948c():   # las tres provincias que Lupu-Stokes no trae en diciembre de 1948
    return {p: wiki_parties(p) for p in C["solid"]}


prov_rec, prov_an = {}, {}
for p in PROVS:
    if p in C["noeleccion"]:
        prov_rec[p] = dict(lines=[], fill=GREY_NE, note=C["noeleccion"][p]); continue
    if LS and WPROV.get(p):
        parties, bla, ins, vot = wiki_parties(p)
        if K == "1973s":   # «Total Perón»: FREJULI y FIP juntos
            pass
        extra = ("Total provincial de la tabla de la Wikipedia." + (" " + C["solid"][p] if p in C["solid"] else "") +
                 " Los departamentos salen de Lupu y Stokes.")
        r = rec_from(parties, bla, 0, ins, vot, extra=extra)
        prov_rec[p] = r
        bl = {}
        for _, v, b in parties: bl[b] = bl.get(b, 0) + v
        prov_an[p] = dict(pos=sum(v for _, v, _ in parties), bloc=bl, ins=ins, vot=vot)
        continue
    parties, bla, nul, ins, vot, ok = {}, 0, 0, 0, 0, True
    for i, u in enumerate(U):
        if u["prov"] != p or i not in src: continue
        d = src[i][1]
        for n, v, b in d["parties"]: parties[(n, b)] = parties.get((n, b), 0) + v
        bla += d["bla"]; nul += d["nul"]
        if d["parties"]:
            if d["ins"] and d["vot"] and d["vot"] <= d["ins"]: ins += d["ins"]; vot += d["vot"]
            else: ok = False
    pl = [(n, v, b) for (n, b), v in parties.items()]
    if not pl:
        prov_rec[p] = dict(lines=[], fill=GREY_SD, note="Sin datos en %s." % SRC_NAME); continue
    prov_rec[p] = rec_from(pl, bla, nul, ins if ok else None, vot if ok else None,
                           extra="Suma de las unidades de %s." % SRC_NAME + ("" if ok else " La participación provincial no se calcula: alguna unidad no trae padrón o sus votantes superan a los inscriptos."))
    bl = {}
    for n, v, b in pl: bl[b] = bl.get(b, 0) + v
    prov_an[p] = dict(pos=sum(v for _, v, _ in pl), bloc=bl, ins=ins if ok else None, vot=vot if ok else None)
for i in range(len(U)):
    if unit_rec[i] is None:   # provincias en color sólido
        r = dict(prov_rec[U[i]["prov"]]); r["note"] = "Sin detalle departamental. " + C["solid"][U[i]["prov"]]
        unit_rec[i] = r
json.dump([dict(prov=U[i]["prov"], unidad=U[i]["name"], estado="beige" if r.get("fill") == GREY_SD else "sólido", nota=r.get("note"))
           for i, r in unit_rec.items() if r.get("fill") == GREY_SD or U[i]["prov"] in C["solid"]],
          open(os.path.join(OUTDIR, "faltantes_%s.json" % K), "w", encoding="utf8"), ensure_ascii=False, indent=1)

# códigos de las líneas de ficha
for (n, b), code in PCODE.items():
    CAND[code] = dict(n=n, base=C["cand"][b]["base"] if b in C["cand"] else "#9a9a9a", minor=True)
CAND["P_BLA"] = dict(n="En blanco" + ("" if Y == 1946 else " y anulados") + (" (est.)" if LS else ""), base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Anulados", base="#b0b0b0", minor=True)


# ---------------------------------------------------------------- logos
def _logo(fn):
    path = os.path.join(LOGOS, fn)
    if fn.endswith(".svg"):
        t = open(path, encoding="utf8").read()
        t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S); t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
        m = re.search(r'viewBox="\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)', t)
        ar = float(m.group(3)) / float(m.group(4)) if m else 1.0
        return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar)
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    bb = im.getchannel("A").getbbox()
    if bb: im = im.crop(bb)
    s = 320 / max(im.size)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=im.width / im.height)


for b, c in C["cand"].items():
    if c.get("img"):
        CAND[b].update(_logo(c["img"][0]))
        if CAND[b]["ar"] > 1.6: CAND[b]["bl"] = 0.62   # logos anchos (MID): más bajos para que entren en el marco

# ---------------------------------------------------------------- nacional (Wikipedia) y modos
wins = {}
for i, r in unit_rec.items():
    if r.get("w"): wins[r["w"]] = wins.get(r["w"], 0) + 1
print(K, "unidades ganadas:", wins, file=sys.stderr)
cands, slices, partp, NAT_MET = wikitop.national(K)
assert {c["code"] for c in cands} == set(wins), ({c["code"] for c in cands}, wins)

GEO = {"deptos. de 1947": "departamentos de 1947", "deptos. de 1960": "departamentos de 1960", "deptos. de 1970": "departamentos de 1970"}[C["geo"]]
if LS:
    NOTE = (wikitop.note(K).replace("Cantón (1968)", "Lupu y Stokes (2009)") + " Fuente departamental: N. Lupu y S. Stokes, «The Social Bases of Political Parties in "
            "Argentina, 1912-2003» (LARR, 2009), base ecológica, %s. Solo distingue peronismo, UCR, socialistas y conservadores: el resto está "
            "estimado con las tablas provinciales de la Wikipedia (filas «est.»). Geometría: %s%s." % (C["fuente"], GEO,
            "; provincia de Buenos Aires: partidos de 1955" if Y < 1960 else "; Capital: 28 circunscripciones aproximadas"))
else:
    NOTE = (wikitop.note(K) + " Fuente departamental: D. Cantón, «Materiales para el estudio de la sociología política en la Argentina» (1968), "
            "t. II, %s, cifras tal como se publican. Geometría: %s; provincia de Buenos Aires: partidos de 1955." % (C["fuente"], GEO))


def mix(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(255 + (c[k] - 255) * t) for k in range(3))


def stops_for(base, edges):
    ts = [0.12 + 0.88 * i / (len(edges) - 1) for i in range(len(edges))]
    return [mix(base, t) for t in ts], ["%d%%" % e for e in edges[:-1]] + ["+%d%%" % edges[-1]]


def bin_of(p, edges):
    i = 0
    while i + 1 < len(edges) and p >= edges[i + 1]: i += 1
    return i


def mode_choropleth(fn, base, edges, title, keys):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(U)):
        r = unit_rec[i]; a = AN.get(i)
        v = fn(a) if a else None
        nr = {k: x for k, x in r.items() if k not in ("w", "q", "fill")}
        if v is not None: nr["fill"] = cols[bin_of(v, edges)]
        elif a: nr["fill"] = GREY_PAD
        else: nr["fill"] = r.get("fill", GREY_N)
        if U[i]["prov"] in C["solid"]:
            pv = fn(prov_an[U[i]["prov"]]); nr["fill"] = cols[bin_of(pv, edges)] if pv is not None else GREY_PAD
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        nr = {k: x for k, x in r.items() if k not in ("w", "q", "fill")}
        v = fn(prov_an[p]) if p in prov_an else None
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else r.get("fill", GREY_PAD)
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=keys)


NAT = dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET)
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec, national=NAT, legend=dict(keys=KEYS))]
for mid, tile, b, base, edges, title in C["modes"]:
    un, pv, lg = mode_choropleth(lambda a, b=b: 100 * a["bloc"].get(b, 0) / a["pos"] if a["pos"] else None, base, edges, title, KEYS)
    MODES.append(dict(id=mid, tile=tile, note=NOTE, units=un, prov=pv, national=NAT, legend=lg))
_par = lambda a: a.get("part") if a.get("part") else ((100 * a["vot"] / a["ins"]) if (a.get("ins") and a.get("vot") and a["vot"] <= a["ins"]) else None)
if C["par"]:
    un, pv, lg = mode_choropleth(_par, "#2a6f97", [0, 60, 65, 70, 75, 80, 85] if Y == 1946 else [0, 70, 75, 80, 85, 90, 95],
                                 "Participación (votantes / inscriptos)", KEYS + [[GREY_PAD, "Sin padrón o padrón inconsistente en la fuente"]])
    MODES.append(dict(id="par", tile="PART", note=NOTE, units=un, prov=pv, national=NAT, legend=lg))
for _m in MODES:
    for _i in MALV: _m["units"][_i] = dict(unit_rec[_i])

# ---------------------------------------------------------------- SVG
body = []
for i, u in enumerate(U):
    body.append('<path class="d" data-i="%d" d="%s"%s/>' % (i, geom_d(G[i]), ' style="stroke:#1b1b1b;stroke-width:1px"' if i in MALV else ""))
cap_idx = [i for i, u in enumerate(U) if u["prov"] == "Capital Federal"]
for i in cap_idx:
    body.append('<path class="dc" data-i="%d" d="%s"/>' % (i, geom_d(shapely.simplify(G_raw[i], 0.01))))
for p in PROVS:
    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(prov_geom[p].boundary)))
body.append('<path class="out" d="%s"/>' % line_d(country.boundary))
for txt, lon, lat, rot in (("BOLIVIA", -65.2, -21.55, 0), ("PARAGUAY", -59.3, -22.05, 0), ("BRASIL", -53.2, -25.2, 0),
                           ("URUGUAY", -56.0, -32.2, 0), ("CHILE", -73.9, -39.0, -90)):
    x, y = ll(lon, lat)
    body.append('<text class="cn" x="%s" y="%s" text-anchor="middle"%s>%s</text>' % (f2(x), f2(y), (' transform="rotate(%d %s %s)"' % (rot, f2(x), f2(y))) if rot else "", txt))


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
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True, chaco_names={"Resistencia"} if Y < 1954 else {"San Fernando"})
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

KPV = 0.2669
bx0, by0, bx1, by1 = shapely.total_bounds([prov_geom[p] for p in PROVS])
pv_tx, pv_ty = 182 - KPV * (bx0 + bx1) / 2, 600 - KPV * by0
pv = ['<g>']
for p in PROVS:
    pv.append('<path class="pf" data-prov="%s" d="%s"/>' % (p, geom_d(prov_mini[p])))
for _i in MALV:
    pv.append('<path class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round" d="%s"/>' % geom_d(G[_i]))
pv.append("</g>")

# ---------------------------------------------------------------- dataset y plantilla
ds = dict(
    slug="elecciones_%s" % K, locale="es-AR", country="Argentina", title=C["title"], year=str(Y),
    labels=dict(pie1="Proporción sobre votos positivos"), exterior=False, candidates=CAND,
    sets={"1": dict(label=str(Y), subtitle="%s · %s" % ("Lupu y Stokes" if LS else "Cantón (1968)", C["geo"]))},
    modes=MODES, insets=INSETS, solid=sorted(C["solid"]),
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(OUTDIR, "dataset_%s.json" % K), "w", encoding="utf8"), ensure_ascii=False)

tpl = open(TEMPLATE_SRC, encoding="utf8").read()


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>%s</title>" % C["tab"])
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"', 'style="--v-d:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub('<g id="pv" transform="matrix(0.1448 0 0 0.1448 55.7 599.8)" style="--spf:9.7px">', '<g id="pv" transform="matrix(%s 0 0 %s %s %s)" style="--spf:9.7px">' % (KPV, KPV, f2(pv_tx), f2(pv_ty)))
sub("#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}", "#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}")
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
# muchos bloques: la leyenda empieza más arriba y con barras más bajas (más aún con más de 7)
sub('''el("text",{x:93,y:1266,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=1292''',
    '''const MANY=N.cands.length>4,LOTS=N.cands.length>7,HUGE=N.cands.length>9,Y0=LOTS?1000:MANY?1024:1266;
  el("text",{x:93,y:Y0,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=Y0+26;''')
sub("const h=50,win=idx===0&&!LG", "const h=HUGE?31:LOTS?38:MANY?42:50,k=h/50,win=idx===0&&!LG")
sub('''el("text",{x:104,y:y+36,"font-size":lg.length>2?34:40,fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41,''',
    '''el("text",{x:104,y:y+36*k,"font-size":(lg.length>3?26:lg.length>2?30:34)*(MANY?.9:1),fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41*k,''')
sub('width:lg.length>2?(lg.length*20):(lg.length*23),height:3', 'width:(lg.length>3?lg.length*15:lg.length>2?(lg.length*18):(lg.length*20))*(MANY?.9:1),height:3')
sub('el("text",{x:424,y:y+21,"font-size":21,', 'el("text",{x:424,y:y+20*k,"font-size":HUGE?15:MANY?18:21,')
sub('if(C.sub)el("text",{x:424,y:y+39,"font-size":15,', 'if(C.sub)el("text",{x:424,y:y+37*k,"font-size":HUGE?11:MANY?13:15,')
sub('el("text",{x:477,y:y+29,"font-size":26,', 'el("text",{x:477,y:y+29*k,"font-size":MANY?23:26,')
sub('el("text",{x:497,y:y+44,"font-size":10,', 'el("text",{x:497,y:y+44*k,"font-size":10,')
sub('el("text",{x:476,y:y+33,"font-size":23,', 'el("text",{x:476,y:y+33*k,"font-size":MANY?20:23,')
if len(MODES) == 5:
    sub("return out.slice(0,4);", "return out.slice(0,5);")
    sub("xs=[1262,1316,1370,1424]", "xs=[1262,1314,1366,1418,1470]")
    sub('<text id="sub" x="1515"', '<text id="sub" x="1536"')
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(OUTDIR, "atlas_%s.html" % K)
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
