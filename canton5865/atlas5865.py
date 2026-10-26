#!/usr/bin/env python3
"""Atlas 1958 (presidente), 1962 y 1965 (diputados nacionales) con los datos de Cantón (1968), estilo Wikipedia 1999.

    python canton5865/atlas5865.py 1958     -> mapa1958/atlas_1958.html (+ dataset_1958.json)
    python canton5865/atlas5865.py 1962     -> mapa1962/...
    python canton5865/atlas5865.py 1965     -> mapa1965/...

Datos     : Cantón, «Materiales para el estudio de la sociología política en la Argentina» (1968), t. II, transcripto en
            scratch/transcripcion/ y corregido con canton5865/correcciones.py (cada corrección, con la página y el motivo).
Bloques   : filas de las tablas de Wikipedia (canton5865/mapeo.py). Resultado nacional: wikitop.py.
Geometría : Departamentos_1960 + secciones electorales de Capital; polígonos propios de 1970 y 1947 (canton5865/geom60.py).
"""
import sys, os, re, json, pickle, base64, io
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(H, "..")
sys.path.insert(0, H); sys.path.insert(0, ROOT)
import numpy as np, shapely
from shapely.ops import unary_union
import geom60
from names import norm
from datos import cargar_todo, unidades, competidores, ganador
import wikitop, insets99
from outline_clean import clean_outline, clean_holes

Y = int(sys.argv[1]) if len(sys.argv) > 1 else 1958
OUTDIR = os.path.join(ROOT, "mapa%d" % Y)
os.makedirs(OUTDIR, exist_ok=True)
LOGOS = os.path.join(ROOT, "logos_wikipedia")
TEMPLATE_SRC = os.path.join(ROOT, ".claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

# ---------------------------------------------------------------- configuración por año
UCRI_C, UCRP_C, FNPC_C = "#f4845f", "#e10019", "#1f2f6b"
CFG = {
    1958: dict(
        title="Elecciones presidenciales de Argentina de", tab="Elecciones presidenciales 1958", cargo="presidente",
        cand={"UCRI": dict(n="Arturo Frondizi", sub="UCRI", base=UCRI_C, logo="UCRI", img=("Escudo_UCRI_1963_plano.svg", None)),
              "UCRP": dict(n="Ricardo Balbín", sub="UCRP", base=UCRP_C, logo="UCRP", img=("UCRP_escudo.svg", None)),
              "CON": dict(n="Partidos conservadores", sub="PD y afines", base=FNPC_C, logo="PD"),
              "URB": dict(n="UCRI Rojo y Blanco", sub="Santiago del Estero", base="#c2185b", logo="RyB"),
              "NPE": dict(n="Partido Populista", sub="Catamarca", base="#35aae0", logo="PP")},
        modes=[("ucri", "UCRI", "UCRI", "#f4845f", [0, 30, 40, 50, 60, 70, 80], "% Frondizi (UCRI)"),
               ("ucrp", "UCRP", "UCRP", "#e10019", [0, 20, 30, 40, 50, 60, 70], "% Balbín (UCRP)")],
        noeleccion={}, solid={
            "Corrientes": dict(src="Cantón no trae el escrutinio presidencial de Corrientes (solo el de diputados, con muchas filas que no cierran): se pinta la provincia con el total de la Wikipedia.",
                               P=[("Unión Cívica Radical Intransigente", 87836, "UCRI"), ("Unión Cívica Radical del Pueblo", 21421, "UCRP"),
                                  ("Partido Liberal de Corrientes", 51092, None), ("Partido Demócrata Cristiano", 11687, None), ("Partido Socialista", 870, None),
                                  ("Otros partidos", 95987 - 51092, None)], blanul=20213, vot=238014, part=84.83),
            "Río Negro": dict(src="Cantón no trae Río Negro en 1958: se pinta la provincia con el total de la Wikipedia.",
                              P=[("Unión Cívica Radical Intransigente", 20790, "UCRI"), ("Unión Cívica Radical del Pueblo", 13953, "UCRP"),
                                 ("Partido Demócrata Cristiano", 5881, None), ("Partido Socialista", 2735, None), ("Otros partidos", 3161, None)],
                              blanul=14851, vot=61371, part=80.86)},
        tdf="Tierra del Fuego era territorio nacional; Cantón suma sus votos presidenciales a los de Capital Federal («Capital Federal y Tierra del Fuego»), sin detalle propio."),
    1962: dict(
        title="Elecciones de diputados nacionales de Argentina de", tab="Diputados nacionales 1962", cargo="diputados",
        cand={"FJ": dict(n="Frente Justicialista", sub="UP y neoperonistas", base="#318ce7", logo="FJ", img=("Flag_PJ_escudo_clasico_cuadrada.svg", None)),
              "UCRI": dict(n="UCR Intransigente", sub="UCRI", base=UCRI_C, logo="UCRI", img=("Escudo_UCRI_1963_plano.svg", None)),
              "UCRP": dict(n="UCR del Pueblo", sub="UCRP y afines", base=UCRP_C, logo="UCRP", img=("UCRP_escudo.svg", None)),
              "FNPC": dict(n="Fed. de Partidos de Centro", sub="Conservadores", base=FNPC_C, logo="FNPC", img=("Logo_de_la_FdC.png", None)),
              "PSD": dict(n="Socialista Democrático", sub="PSD", base="#ffad00", logo="PSD", img=("Partido_Socialista_Democratico_Argentina.png", None)),
              "PDP": dict(n="Demócrata Progresista", sub="PDP", base="#005c9e", logo="PDP", img=("Escudo_del_PDP.svg", None))},
        modes=[("fj", "FJ", "FJ", "#318ce7", [0, 20, 30, 40, 50, 60, 70], "% Frente Justicialista"),
               ("ucri", "UCRI", "UCRI", "#f4845f", [0, 10, 20, 30, 40, 50, 60], "% UCR Intransigente"),
               ("ucrp", "UCRP", "UCRP", "#e10019", [0, 10, 20, 30, 40, 50, 60], "% UCR del Pueblo")],
        noeleccion={p: "%s no eligió diputados nacionales en marzo de 1962 (tabla de bancas del artículo de la Wikipedia)." % p
                    for p in ("Catamarca", "Formosa", "La Rioja", "Misiones", "San Luis", "Santa Cruz")},
        solid={"Santiago del Estero": dict(src="Cantón no trae los diputados de Santiago del Estero de 1962: se pinta la provincia con el total de la Wikipedia.", wiki=True)},
        tdf="Tierra del Fuego era territorio nacional: no elegía diputados nacionales."),
    1965: dict(
        title="Elecciones de diputados nacionales de Argentina de", tab="Diputados nacionales 1965", cargo="diputados",
        cand={"UP": dict(n="Unión Popular", sub="UP", base="#009999", logo="UP", img=("Union_popular_logo_blanco.png", None)),
              "UCRP": dict(n="UCR del Pueblo", sub="UCRP", base=UCRP_C, logo="UCRP", img=("UCRP_escudo.svg", None)),
              "FNPC": dict(n="Fed. de Partidos de Centro", sub="Conservadores", base=FNPC_C, logo="FNPC", img=("Logo_de_la_FdC.png", None)),
              "MID": dict(n="MID", sub="Integración y Desarrollo", base="#0f2b3d", logo="MID", img=("MID_logo_1963.png", None)),
              "MPP": dict(n="Mov. populares provinciales", sub="Neoperonistas", base="#318ce7", logo="MPP", img=("Flag_PJ_escudo_clasico_cuadrada.svg", None)),
              "UCRI": dict(n="UCR Intransigente", sub="UCRI", base=UCRI_C, logo="UCRI", img=("Escudo_UCRI_1963_plano.svg", None)),
              "PDP": dict(n="Demócrata Progresista", sub="PDP", base="#005c9e", logo="PDP", img=("Escudo_del_PDP.svg", None)),
              "UCRB": dict(n="UCR Bloquista", sub="San Juan", base="#44944a", logo="UCRB", img=("Estrella_bloquista.png", None)),
              "MFL": dict(n="Línea Las Flores-Luján", sub="Buenos Aires", base="#9e9d24", logo="MFL"),
              "PUN": dict(n="Partido Unidad Nacional", sub="Santa Cruz", base="#8d6e63", logo="PUN"),
              "UPM": dict(n="Unión Provincial", sub="Misiones", base="#ffb300", logo="UP Mis")},
        modes=[("up", "UP", "UP", "#009999", [0, 20, 30, 40, 50, 60, 70], "% Unión Popular"),
               ("ucrp", "UCRP", "UCRP", "#e10019", [0, 20, 30, 40, 50, 60, 70], "% UCR del Pueblo"),
               ("mpp", "MPP", "MPP", "#318ce7", [0, 10, 20, 30, 40, 50, 60], "% movimientos populares provinciales")],
        noeleccion={p: "%s no eligió diputados nacionales en marzo de 1965 (Cantón, t. I: «no hubo elecciones»)." % p
                    for p in ("Jujuy", "Salta")},
        solid={}, tdf="Tierra del Fuego era territorio nacional: no elegía diputados nacionales."),
}
C = CFG[Y]
BLOCS = list(C["cand"])
GREY_NE, GREY_SD, GREY_N, GREY_MAL = "#cfcfcf", "#e6dcc3", "#8c8c8c", "#a9a9a9"
GREY_PAD = "#dadada"
KEYS = [[GREY_NE, "Sin elección" + (" de diputados nacionales" if C["cargo"] == "diputados" else " propia (territorio nacional)")],
        [GREY_SD, "Sin dato propio en Cantón"]]
NOTE_CANTON = {
    1965: dict({p: "La Wikipedia no trae esta provincia en 1965; el resumen nacional de diputados del t. I de Cantón (Ministerio del Interior) sí la incluye."
                for p in ("Formosa", "La Rioja", "Misiones")},
               Catamarca="La Wikipedia no trae esta provincia en 1965; el resumen nacional de diputados del t. I de Cantón (Ministerio del Interior) sí la incluye. "
                         "Cantón aclara que «no hubo elecciones en todos los departamentos» de Catamarca."),
}

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
    pickle.dump(geom60.load(Y), open(PKL, "wb"))
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
T, LOG = cargar_todo()
D = unidades(T, Y)
KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
ALIAS = {   # nombre en Cantón -> polígono de 1960 (cambios de nombre u ortografía)
    ("Buenos Aires", "Caseros"): "Daireaux", ("Buenos Aires", "C. de M. Leonardo Rosales"): "Crnel de marina Leonardo Rosales",
    ("Buenos Aires", "General Madariaga"): "Gnral.Juan Madariaga", ("Buenos Aires", "González Chaves"): "Adolfo Gonzáles Chaves",
    ("Buenos Aires", "Hipólito Irigoyen"): "Hipólito Yrigoyen", ("Buenos Aires", "Juárez"): "Benito Juarez", ("Buenos Aires", "Matanza"): "La Matanza",
    ("Buenos Aires", "9 de Julio"): "Nueve de julio", ("Buenos Aires", "Tordillo"): "General Conesa", ("Buenos Aires", "3 de Febrero"): "Tres de Febrero",
    ("Buenos Aires", "Zona Nac. Puerto La Plata"): "Zona Nacional Puerto La Plata",
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
ALIAS_NOTE = {
    ("Buenos Aires", "Caseros"): "El partido de Caseros pasó a llamarse Daireaux en 1970.",
    ("Buenos Aires", "Tordillo"): "En el mapa de 1960 el partido de Tordillo figura como General Conesa.",
    ("La Rioja", "Rivadavia"): "En el mapa de 1960 el departamento figura como General Juan Facundo Quiroga.",
    ("Santiago del Estero", "Matará"): "En el mapa de 1960 el departamento figura como Juan Felipe Ibarra.",
}
CAP = {norm(k): v for k, v in {"Vélez Sarsfield": 1, "San Cristóbal Sud": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sud": 6,
       "San Carlos Norte": 7, "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sud": 10, "Balvanera Norte": 11, "Concepción": 12,
       "Monserrat": 13, "San Nicolás": 14, "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18, "Pilar": 19, "Socorro": 20}.items()}

src, unmapped = {}, []
for (p, n), d in D.items():
    if p == "Capital Federal":
        k = CAP.get(norm(n))
        i = KEY.get((p, norm("Circ. %02d" % k))) if k else None
    else:
        i = KEY.get((p, norm(ALIAS.get((p, n), n))))
    if i is None:
        unmapped.append((p, n, d["vot"])); continue
    assert i not in src, (p, n, U[i]["name"])
    src[i] = (n, d)
print(Y, "sin polígono:", unmapped, file=sys.stderr)
assert all(not v for _, _, v in unmapped), unmapped    # solo pueden quedar afuera filas vacías (Puerto de Capital)

# partidos -> código de línea de ficha (P_k), con el color de su bloque
PCODE = {}


def pcode(name, b):
    k = (name, b)
    if k not in PCODE:
        PCODE[k] = "P_%d" % len(PCODE)
    return PCODE[k]


CAND = {}
for b, c in C["cand"].items():
    CAND[b] = {k: v for k, v in c.items() if k != "img"}


def rec_from(parties, bla, nul, ins, vot, extra=None, color=True):
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
    met.append(["Votos positivos", fmt_n(pos)])
    rec = {"lines": lines, "metrics": met}
    d = dict(parties=parties, bloc={})
    for n, v, b in parties: d["bloc"][b or "OTR"] = d["bloc"].get(b or "OTR", 0) + v
    w = ganador(d)
    if color:
        assert w in BLOCS, (Y, w, parties[:3])
        rec.update(w=w, q=round(100 * competidores(d)[w] / pos, 2))
    notes = []
    if vot and ins and vot > ins: notes.append("En la fuente los votantes (%s) superan a los inscriptos (%s): no se calcula la participación." % (fmt_n(vot), fmt_n(ins)))
    if vot and abs(pos + bla + nul - vot) > max(30, 0.01 * vot):
        notes.append("En la fuente la suma de partidos, blancos y anulados (%s) no coincide con los votantes (%s)." % (fmt_n(pos + bla + nul), fmt_n(vot)))
    if extra: notes.append(extra)
    if notes: rec["note"] = " ".join(notes)
    return rec


AN = {}   # unidad -> agregados para las coropletas
unit_rec, disp = {}, {}
MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}
for i, u in enumerate(U):
    p = u["prov"]
    geo_note = u.get("nota_geo")
    if i in MALV:
        unit_rec[i] = dict(lines=[], metrics=[], fill=GREY_MAL, note="Sin dato: islas bajo administración británica (se muestran en gris)."); continue
    if p == "Tierra del Fuego":
        unit_rec[i] = dict(lines=[], fill=GREY_NE, note=C["tdf"]); continue
    if p in C["solid"]: unit_rec[i] = None; continue
    if i not in src:
        unit_rec[i] = dict(lines=[], fill=GREY_SD if p not in C["noeleccion"] else GREY_NE,
                           note=(C["noeleccion"].get(p) or "Cantón no trae fila para esta unidad.") + (" " + geo_note if geo_note else "")); continue
    n, d = src[i]
    disp[i] = ("Circunscripción %d · %s" % (u["circ"], n)) if p == "Capital Federal" else n
    extras = []
    if p != "Capital Federal" and norm(n) != norm(u["name"]) and (p, n) in ALIAS_NOTE: extras.append(ALIAS_NOTE[(p, n)])
    if geo_note: extras.append(geo_note)
    if u.get("cedio"): extras.append("Polígono de 1960 sin %s, que tiene polígono propio." % " ni ".join(u["cedio"]))
    if d["imput"]: extras.append("La página de Cantón está cortada al pie: los votos de UCRI, UCRP y los demás partidos de la primera mitad de la fila son el residuo del total provincial de la Wikipedia; faltan inscriptos y votantes.")
    if not d["parties"]:
        unit_rec[i] = dict(lines=[], fill=GREY_SD if p not in C["noeleccion"] else GREY_NE,
                           note="Cantón trae la fila «%s» sin cifras: la unidad todavía no existía o votó dentro de otra." % n + (" " + " ".join(extras) if extras else "")); continue
    if p in C["noeleccion"]:
        r = rec_from(d["parties"], d["bla"], d["nul"], d["ins"], d["vot"], color=False,
                     extra=" ".join([C["noeleccion"][p] + " Cantón trae igualmente estas cifras para la misma fecha (probablemente comicios provinciales): se muestran en la ficha, pero la unidad no se colorea.",
                                     ] + extras).strip())
        r["fill"] = GREY_NE
        unit_rec[i] = r; continue
    if NOTE_CANTON.get(Y, {}).get(p): extras.append(NOTE_CANTON[Y][p])
    unit_rec[i] = rec_from(d["parties"], d["bla"], d["nul"], d["ins"], d["vot"], extra=" ".join(extras) or None)
    pos = sum(v for _, v, _ in d["parties"])
    bl = {}
    for _, v, b in d["parties"]: bl[b] = bl.get(b, 0) + v
    AN[i] = dict(pos=pos, bloc=bl, ins=d["ins"], vot=d["vot"])

# ---------------------------------------------------------------- provincias
prov_rec, prov_an = {}, {}
for p in PROVS:
    if p == "Tierra del Fuego":
        prov_rec[p] = dict(lines=[], fill=GREY_NE, note=C["tdf"]); continue
    if p in C["noeleccion"]:
        prov_rec[p] = dict(lines=[], fill=GREY_NE, note=C["noeleccion"][p]); continue
    if p in C["solid"]:
        s = C["solid"][p]
        if s.get("wiki"):
            import wikiprov
            rows = wikiprov.parse("w1962.txt", "== Resultados por provincia")[p]
            import mapeo
            parties = [(f, v, mapeo.bloque(Y, p, f)) for f, v in rows if not f.startswith("#")]
            tot = {f[1:]: v for f, v in rows if f.startswith("#")}
            print(p, "totales Wikipedia:", tot, file=sys.stderr)
            bla = sum(v for f, v in tot.items() if re.search("blanco|nulo", f, re.I)); vot = next((v for f, v in tot.items() if f.lower().startswith("total")), None)
            ins = next((v for f, v in tot.items() if "registrados" in f.lower()), None)
            r = rec_from(parties, bla, 0, ins, vot, extra=s["src"] + " Blancos y nulos juntos, como en la tabla.")
        else:
            r = rec_from(s["P"], s["blanul"], 0, None, s["vot"], extra=s["src"] + " Blancos y anulados juntos, como en la tabla.")
            r["metrics"].insert(1, ["Participación", fmt_p(s["part"]) + " %"])
        prov_rec[p] = r
        parties = s["P"] if not s.get("wiki") else parties
        bl = {}
        for _, v, b in parties: bl[b] = bl.get(b, 0) + v
        prov_an[p] = dict(pos=sum(v for _, v, _ in parties), bloc=bl, ins=None, vot=None, part=s.get("part"))
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
    prov_rec[p] = rec_from(pl, bla, nul, ins if ok else None, vot if ok else None,
                           extra="Suma de las unidades de Cantón." + (" " + NOTE_CANTON[Y][p] if NOTE_CANTON.get(Y, {}).get(p) else "") + ("" if ok else " La participación provincial no se calcula: alguna unidad no trae padrón o sus votantes superan a los inscriptos."))
    bl = {}
    for n, v, b in pl: bl[b] = bl.get(b, 0) + v
    prov_an[p] = dict(pos=sum(v for _, v, _ in pl), bloc=bl, ins=ins if ok else None, vot=vot if ok else None)
for i in range(len(U)):
    if unit_rec[i] is None:   # provincias en color sólido
        r = dict(prov_rec[U[i]["prov"]]); r["note"] = "Sin detalle departamental. " + C["solid"][U[i]["prov"]]["src"]
        unit_rec[i] = r
# unidades sin dato (beige) y en color sólido: lista para buscar lo que falta
json.dump([dict(prov=U[i]["prov"], unidad=U[i]["name"], estado="beige" if r.get("fill") == GREY_SD else "sólido", nota=r.get("note"))
           for i, r in unit_rec.items() if r.get("fill") == GREY_SD or U[i]["prov"] in C["solid"]],
          open(os.path.join(OUTDIR, "faltantes_%d.json" % Y), "w", encoding="utf8"), ensure_ascii=False, indent=1)

# códigos de las líneas de ficha
for (n, b), code in PCODE.items():
    CAND[code] = dict(n=n, base=C["cand"][b]["base"] if b in C["cand"] else "#9a9a9a", minor=True)
CAND["P_BLA"] = dict(n="En blanco" if Y != 1958 or True else "En blanco", base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Anulados", base="#b0b0b0", minor=True)
for k in list(CAND):   # «En blanco y anulados» en las provincias sólidas
    pass


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
cands, slices, partp, NAT_MET = wikitop.national(Y)
assert {c["code"] for c in cands} == set(BLOCS), ({c["code"] for c in cands}, BLOCS)
wins = {}
for i, r in unit_rec.items():
    if r.get("w"): wins[r["w"]] = wins.get(r["w"], 0) + 1
print(Y, "unidades ganadas:", wins, file=sys.stderr)
assert set(wins) == set(BLOCS), (wins, BLOCS)

FUENTE = {1958: "elección presidencial del 23 de febrero de 1958", 1962: "diputados nacionales, 18 de marzo de 1962", 1965: "diputados nacionales, 14 de marzo de 1965"}[Y]
NOTE = (wikitop.note(Y) + " Fuente departamental: D. Cantón, «Materiales para el estudio de la sociología política en la Argentina» (1968), t. II, %s, "
        "con %d correcciones de transcripción documentadas. Geometría: departamentos de 1960." % (FUENTE, sum(1 for e in LOG if e[0] == Y)))


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
un, pv, lg = mode_choropleth(_par, "#2a6f97", [0, 70, 75, 80, 85, 90, 95], "Participación (votantes / inscriptos)", KEYS + [[GREY_PAD, "Sin padrón o padrón inconsistente en la fuente"]])
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
X99 = insets99.build(U, G_raw, window, bbox_of, style95=True, chaco_names={"San Fernando"})
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
    slug="elecciones_%d" % Y, locale="es-AR", country="Argentina", title=C["title"], year=str(Y),
    labels=dict(pie1="Proporción sobre votos positivos"), exterior=False, candidates=CAND,
    sets={"1": dict(label=str(Y), subtitle="Cantón (1968) · deptos. de 1960")},
    modes=MODES, insets=INSETS, solid=sorted(C["solid"]),
    territories=[dict(n=disp.get(i, u["name"]), p=u["prov"], k=u["kind"]) for i, u in enumerate(U)],
)
json.dump(ds, open(os.path.join(OUTDIR, "dataset_%d.json" % Y), "w", encoding="utf8"), ensure_ascii=False)

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
out = os.path.join(OUTDIR, "atlas_%d.html" % Y)
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
