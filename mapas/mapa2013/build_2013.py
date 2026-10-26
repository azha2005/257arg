"""Genera mapa2013/atlas_2013.html y mapa2013/dataset_2013.json (Diputados Nacionales 2013)."""
import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
import os, sys, json, pickle, math, base64, io
import shapely
from shapely import affinity
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import geom, wikitop
from names import norm

TPL = os.path.join(HERE, "..", "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")
CSS_VARS = ("--v-d:inline;--v-dc:inline;--v-rcb:inline;--v-cabab:inline;--v-rcc:inline;"
            "--v-pb:inline;--v-out:inline;--v-ant:inline;--v-mal:inline")
S, X0, Y0 = 44.0, 643.0, 150.0
LON0, LAT1 = -73.5708041, -21.7807776

import numpy as np


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
    from shapely.geometry import Polygon, MultiPolygon
    gs = g.geoms if hasattr(g, "geoms") else [g]
    out = [Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area >= amax]) for q in gs]
    return out[0] if len(out) == 1 else MultiPolygon(out)


# ---------------------------------------------------------------- geometria (Departamentos_2010 + Lezama)
RAW_CACHE = os.path.join(HERE, "units_raw.pkl")
if os.path.exists(RAW_CACHE):
    raw = pickle.load(open(RAW_CACHE, "rb"))
else:
    raw = geom.load()
    pickle.dump(raw, open(RAW_CACHE, "wb"))

U = sorted(raw, key=lambda u: (u["prov"], int(u["name"].split()[1]) if u["prov"] == "Capital Federal" else u["name"]))
G_raw = [shapely.transform(u["geom"], proj) for u in U]
G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.3))

PROVS = sorted({u["prov"] for u in U})
prov_geom = {}
for p in PROVS:
    gs = [G[i] for i, u in enumerate(U) if u["prov"] == p]
    prov_geom[p] = unary_union([g.buffer(0.12) for g in gs]).buffer(-0.12)
    if p != "Tierra del Fuego":
        prov_geom[p] = fill_slivers(prov_geom[p], 5.0 if p == "Capital Federal" else 0.15)
country = unary_union(list(prov_geom.values())).buffer(0.1).buffer(-0.1)
_cf, _ba = prov_geom["Capital Federal"], prov_geom["Buenos Aires"]
_win = shapely.box(_cf.bounds[0] - 3, _cf.bounds[1] - 3, _cf.bounds[2] + 3, _cf.bounds[3] + 3)
_n = unary_union([_ba, _cf]).buffer(0.5).buffer(-0.5).intersection(_win).difference(unary_union([_ba, _cf]))
_n = unary_union([q for q in (_n.geoms if hasattr(_n, "geoms") else [_n]) if q.area >= 0.1])
prov_geom["Capital Federal"] = unary_union([_cf, _n])
country = unary_union([country, _n])
prov_geom = {p: g.simplify(0.12) for p, g in prov_geom.items()}
country = country.simplify(0.12)
from outline_clean import clean_outline, clean_holes
country = clean_outline(country)
for _p in PROVS: prov_geom[_p] = clean_holes(prov_geom[_p])
prov_mini = {p: g.simplify(1.2) for p, g in prov_geom.items()}


# ---------------------------------------------------------------- datos DINE 2013
AG = pickle.load(open(os.path.join(HERE, "..", "../datos_oficiales", "2013", "agregado.pkl"), "rb"))
MESAS = pickle.load(open(os.path.join(HERE, "..", "../datos_oficiales", "2013", "mesas_depto.pkl"), "rb"))
D2P = {
    "01": "Capital Federal", "02": "Buenos Aires", "03": "Catamarca", "04": "Córdoba",
    "05": "Corrientes", "06": "Chaco", "07": "Chubut", "08": "Entre Ríos",
    "09": "Formosa", "10": "Jujuy", "11": "La Pampa", "12": "La Rioja",
    "13": "Mendoza", "14": "Misiones", "15": "Neuquén", "16": "Río Negro",
    "17": "Salta", "18": "San Juan", "19": "San Luis", "20": "Santa Cruz",
    "21": "Santa Fe", "22": "Santiago del Estero", "23": "Tucumán", "24": "Tierra del Fuego",
}

# Sub-secciones de la DINE que integran un departamento del mapa:
# - Entre Ríos 002 (circuitos de Paraná Campaña, sin nombre en la tabla de ámbitos) -> 001 Paraná
# - Santa Fe 010 (Suburbios de La Capital) -> 009 La Capital; 014 y 015 (Rosario Secciones y Suburbios) -> 013 Rosario
# - Tierra del Fuego 003 (Antártida Argentina) -> 001 Ushuaia
SUBSEC_MERGE = {
    ("08", "002"): ("001", "Incluye la sección 002 (Paraná Campaña: %s votos positivos)."),
    ("21", "010"): ("009", "Incluye la sección 010 (Suburbios de La Capital: %s votos positivos)."),
    ("21", "014"): ("013", "Incluye las secciones 014 y 015 (Rosario Secciones y Suburbios)."),
    ("21", "015"): ("013", None),
    ("24", "003"): ("001", "Incluye el departamento Antártida Argentina (%s votos positivos en 6 de 9 mesas)."),
}

EALIAS = {
    ("Buenos Aires", "arrecifes"): norm("Bartolome Mitre"),
    ("Buenos Aires", "coronelrosales"): norm("Coronel de Marina L. Rosales"),
    ("Buenos Aires", "generalmadariaga"): norm("General Juan Madariaga"),
    ("Chaco", "1odemayo"): norm("1 de Mayo"),
    ("Chubut", "pasodeindios"): norm("Paso de los Indios"),
    ("La Rioja", "generalangelvicentepenaloza"): norm("General Angel V. Peñaloza"),
    ("La Rioja", "generaljuanfacundoquiroga"): norm("General Juan F. Quiroga"),
    ("La Rioja", "generalortizdeocampo"): norm("General Ocampo"),
    ("Río Negro", "pilcaniyeu"): norm("Pilnaniyeu"),
    ("Río Negro", "sanantoniooeste"): norm("San Antonio"),
    ("Salta", "generaljosesanmartin"): norm("General Jose de San Martin"),
    ("San Luis", "pueyrredon"): norm("La Capital"),
    ("Santiago del Estero", "pellegrini"): norm("Pelegrini"),
    ("Tucumán", "famailla"): norm("Famalla"),
}

NICE = {
    ("Buenos Aires", norm("Bartolome Mitre")): "Arrecifes (Bartolomé Mitre)",
    ("Buenos Aires", norm("Coronel de Marina L. Rosales")): "Coronel Rosales",
    ("Buenos Aires", norm("General Juan Madariaga")): "General Juan Madariaga",
    ("Chaco", norm("1 de Mayo")): "1.º de Mayo",
    ("Chubut", norm("Paso de los Indios")): "Paso de Indios",
    ("La Rioja", norm("General Angel V. Peñaloza")): "General Ángel V. Peñaloza",
    ("La Rioja", norm("General Juan F. Quiroga")): "General Juan Facundo Quiroga",
    ("La Rioja", norm("General Ocampo")): "General Ortiz de Ocampo",
    ("Río Negro", norm("Pilnaniyeu")): "Pilcaniyeu",
    ("Río Negro", norm("San Antonio")): "San Antonio",
    ("Salta", norm("General Jose de San Martin")): "General José de San Martín",
    ("San Luis", norm("La Capital")): "Juan Martín de Pueyrredón (La Capital)",
    ("Santiago del Estero", norm("Pelegrini")): "Pellegrini",
    ("Tucumán", norm("Famalla")): "Famaillá",
}

BARRIOS_COMUNA = {
    1: "Retiro, San Nicolás, Puerto Madero, San Telmo, Montserrat y Constitución",
    2: "Recoleta",
    3: "Balvanera y San Cristóbal",
    4: "La Boca, Barracas, Parque Patricios y Nueva Pompeya",
    5: "Almagro y Boedo",
    6: "Caballito",
    7: "Flores y Parque Chacabuco",
    8: "Villa Soldati, Villa Riachuelo y Villa Lugano",
    9: "Liniers, Mataderos y Parque Avellaneda",
    10: "Villa Real, Monte Castro, Versalles, Floresta, Vélez Sársfield y Villa Luro",
    11: "Villa General Mitre, Villa Devoto, Villa del Parque y Villa Santa Rita",
    12: "Coghlan, Saavedra, Villa Urquiza y Villa Pueyrredón",
    13: "Núñez, Belgrano y Colegiales",
    14: "Palermo",
    15: "Chacarita, Villa Crespo, La Paternal, Villa Ortúzar, Agronomía y Parque Chas",
}

# ---------------------------------------------------------------- bloques de Wikipedia (tabla nacional)
BLOCS = ("FPV", "FPCyS", "FR", "PRO", "FIT", "UxC", "FRC", "CF", "PACh", "FE", "MPN", "SST", "PJ", "PARES", "MIJD")

# Asignacion exacta de cada (distrito_id, agrupacion_id) a las filas de la tabla nacional de Wikipedia
LIST2BLOC = {}
for _d in D2P:
    LIST2BLOC[(_d, "0501")] = "FPV"
LIST2BLOC.update({
    ("22", "0541"): "FPV",   # Frente Civico por Santiago
    ("17", "0002"): "FPV",   # PJ Salta (incluido dentro de FPV en la tabla nacional de Wikipedia)
    ("17", "0054"): "FPV",   # Partido de la Victoria Salta
    ("24", "0201"): "FPV",   # Movimiento Solidario Popular TDF
    ("24", "0199"): "FPV",   # Espacio Democratico para la Victoria TDF
    # FPCyS (Frente Progresista Civico y Social, UCR, UNEN, PS, CC-ARI y aliados)
    ("02", "0514"): "FPCyS", ("04", "0514"): "FPCyS", ("10", "0514"): "FPCyS", ("19", "0514"): "FPCyS", ("21", "0514"): "FPCyS", ("22", "0514"): "FPCyS",
    ("04", "0003"): "FPCyS", ("07", "0003"): "FPCyS", ("08", "0003"): "FPCyS", ("13", "0003"): "FPCyS", ("14", "0003"): "FPCyS", ("16", "0003"): "FPCyS", ("17", "0003"): "FPCyS", ("18", "0003"): "FPCyS", ("24", "0003"): "FPCyS",
    ("01", "0502"): "FPCyS", # Alianza UNEN (CABA)
    ("23", "0543"): "FPCyS", # Acuerdo Civico y Social (Tucuman)
    ("05", "0517"): "FPCyS", # Encuentro por Corrientes (ECO)
    ("06", "0519"): "FPCyS", # Union por Chaco
    ("10", "0522"): "FPCyS", # Frente Jujeno
    ("09", "0521"): "FPCyS", # Frente Amplio Formoseno
    ("12", "0548"): "FPCyS", # Fuerza Civica Riojana
    ("16", "0534"): "FPCyS", # Alianza Frente Progresista (Rio Negro)
    ("03", "0508"): "FPCyS", # Frente Civico y Social (Catamarca)
    ("11", "0525"): "FPCyS", # FrePam (La Pampa)
    ("04", "0047"): "FPCyS", ("07", "0047"): "FPCyS", # CC-ARI
    ("20", "0538"): "FPCyS", # Union Para Vivir Mejor (Santa Cruz)
    ("15", "0532"): "FPCyS", # Compromiso Civico Neuquino
    ("14", "0050"): "FPCyS", # Partido Socialista (Misiones)
    ("13", "0528"): "FPCyS", # FAP - CC-ARI (Mendoza)
    ("15", "0533"): "FPCyS", # Frente Progresista Sur (Neuquen)
    ("24", "0069"): "FPCyS", # GEN (TDF)
    ("08", "0546"): "FPCyS", # Frente Amplio Progresista (Entre Rios)
    # FR (Frente Renovador y aliados)
    ("02", "0510"): "FR",    # Frente Renovador (Buenos Aires)
    ("05", "0516"): "FR",    # Cambio Popular (Corrientes)
    ("03", "0509"): "FR",    # Frente Tercera Posicion (Catamarca)
    ("21", "0180"): "FR",    # Santafesino Cien por Ciento
    ("23", "0186"): "FR",    # Partido Laborista de la Independencia (Tucuman)
    # PRO (Propuesta Republicana y aliados)
    ("01", "0503"): "PRO", ("04", "0503"): "PRO", ("10", "0523"): "PRO", # Union PRO (CABA, Cordoba y Jujuy)
    ("21", "0547"): "PRO",   # Union PRO Santa Fe Federal
    ("08", "0545"): "PRO",   # Union por Entre Rios
    ("17", "0535"): "PRO",   # Frente Popular Salteno
    ("14", "0531"): "PRO",   # Frente Unidos (Misiones)
    ("13", "0527"): "PRO",   # Union PD-PRO (Mendoza)
    ("11", "0526"): "PRO",   # Frente Propuesta Federal (La Pampa)
    ("23", "0064"): "PRO",   # PRO (Tucuman)
    ("12", "0549"): "PRO",   # Frente Nuevo Pacto Federal (La Rioja)
    ("24", "0544"): "PRO",   # Union Federal (TDF)
    # FIT (Frente de Izquierda y de los Trabajadores)
    ("01", "0505"): "FIT", ("02", "0505"): "FIT", ("04", "0505"): "FIT", ("10", "0505"): "FIT",
    ("13", "0505"): "FIT", ("15", "0505"): "FIT", ("21", "0505"): "FIT", ("23", "0505"): "FIT",
    ("03", "0014"): "FIT", ("06", "0014"): "FIT", ("09", "0014"): "FIT", ("16", "0014"): "FIT", ("17", "0014"): "FIT", ("20", "0014"): "FIT", # Partido Obrero
    ("12", "0061"): "FIT", ("18", "0061"): "FIT", ("22", "0061"): "FIT", # Izquierda por una Opcion Socialista
    ("11", "0190"): "FIT",   # PTS (La Pampa)
    # Bloques provinciales y fuerzas con al menos un departamento ganado
    ("04", "0512"): "UxC",   # Union por Cordoba
    ("14", "0529"): "FRC",   # Frente Renovador de la Concordia (Misiones)
    ("12", "0504"): "CF", ("13", "0504"): "CF", ("18", "0504"): "CF", ("19", "0504"): "CF", # Compromiso Federal
    ("07", "0157"): "PACh",  # Partido Accion Chubutense
    ("02", "0513"): "FE", ("22", "0324"): "FE", # Union con Fe / Partido Fe
    ("15", "0153"): "MPN",   # Movimiento Popular Neuquino
    ("17", "0203"): "SST",   # Salta Somos Todos
    ("11", "0002"): "PJ", ("20", "0002"): "PJ", ("24", "0002"): "PJ", # Partido Justicialista (La Pampa, Santa Cruz, TDF)
    ("17", "0155"): "PARES", # Partido Renovador de Salta
    ("17", "0060"): "MIJD",  # Movimiento Independiente de Justicia y Dignidad (Salta)
})


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


# Colores de la tabla de Wikipedia (con ajustes de contraste de barra/texto para amarillos/celestes/menta)
CAND = {
    "FPV":   dict(n="Frente para la Victoria", sub="PJ, F. Cívico por Santiago y aliados", base="#50ade6", logo="FPV"),
    "FPCyS": dict(n="Frente Progresista Cívico y Social", sub="UCR, PS, CC-ARI, UNEN y aliados", base="#ff6600", logo="FPCyS"),
    "FR":    dict(n="Frente Renovador", sub="Frente Renovador y aliados", base="#3d454d", bar="#333333", txt="#333333", logo="FR"),
    "PRO":   dict(n="Propuesta Republicana", sub="Unión PRO y aliados", base="#f4ce00", logo="PRO"),
    "FIT":   dict(n="Frente de Izquierda", sub="PO, PTS e Izquierda Socialista", base="#f65058", bar="#d93840", txt="#d93840", logo="FIT"),
    "UxC":   dict(n="Unión por Córdoba", sub="Córdoba", base="#19bc9d", bar="#149e84", txt="#149e84", logo="UxC"),
    "FRC":   dict(n="Frente Renovador de la Concordia", sub="Misiones", base="#294593", logo="FRC"),
    "CF":    dict(n="Compromiso Federal", sub="San Luis y aliados", base="#1aff98", logo="CF"),
    "PACh":  dict(n="Partido Acción Chubutense", sub="Chubut", base="#c2185b", logo="PACh"),
    "FE":    dict(n="Partido Fe", sub="Unión con Fe · Buenos Aires", base="#8d5524", logo="FE"),
    "MPN":   dict(n="Movimiento Popular Neuquino", sub="Neuquén", base="#00708b", logo="MPN"),
    "SST":   dict(n="Salta Somos Todos", sub="Salta", base="#ff69b4", bar="#e0509c", txt="#c43a85", logo="SST"),
    "PJ":    dict(n="Partido Justicialista", sub="La Pampa, Santa Cruz y T. del Fuego", base="#318ce7", logo="PJ"),
    "PARES": dict(n="Partido Renovador de Salta", sub="Salta", base="#8e44ad", logo="PRS"),
    "MIJD":  dict(n="Mov. Indep. de Justicia y Dignidad", sub="Salta", base="#b0c236", bar="#8fa020", txt="#7a8a18", logo="MIJD"),
    "P_BLA": dict(n="Votos en blanco", base="#b5b5b5"),
    "P_NUL": dict(n="Votos nulos, recurridos e impugnados", base="#8a8a8a"),
}

# Nombres legibles para todas las listas provinciales de la DINE
votes_df, _ = AG
votes_dn = votes_df[votes_df["cargo_nombre"] == "DIPUTADO NACIONAL"].copy()
votes_dn["v"] = votes_dn["v"].astype(int)

LIST_NAMES = {}
for (_d, _aid), _grp in votes_dn[votes_dn["votos_tipo"] == "POSITIVO"].groupby(["distrito_id", "agrupacion_id"]):
    _aname = str(_grp["agrupacion_nombre"].iloc[0])
    _k = "P_%s_%s" % (_d, _aid)
    _b = LIST2BLOC.get((_d, _aid))
    _nm = _aname.strip().title()
    for _w, _r in (("De ", "de "), ("Del ", "del "), ("La ", "la "), ("Las ", "las "), ("Los ", "los "), ("Y ", "y "),
                   ("Por ", "por "), ("Para ", "para "), ("En ", "en "), ("El ", "el "), ("Al ", "al "), ("Con ", "con "),
                   ("Ucr", "UCR"), ("Pro", "PRO"), ("Fp", "FP"), ("Fpv", "FPV"), ("Gen", "GEN"), ("Ari", "ARI"),
                   ("Fit", "FIT"), ("Mst", "MST"), ("Pts", "PTS"), ("Pach", "PACh"), ("Mpn", "MPN"), ("Mijd", "MIJD"),
                   ("Unen", "UNEN"), ("Frepam", "FrePam"), ("Eco", "ECO"), ("Pd", "PD")):
        _nm = _nm.replace(_w, _r)
    if _nm[:1].islower(): _nm = _nm[:1].upper() + _nm[1:]
    if _b:
        _nm = "%s (%s)" % (_nm, _b)
    LIST_NAMES[(_d, _aid)] = _nm
    CAND[_k] = dict(n=_nm, base=CAND[_b]["base"] if _b else "#8c8c8c")


# Logos de Wikipedia (embebidos en data URI; si es SVG se rasteriza a PNG con Edge)
def _logo(fn, h=80):
    p = os.path.join(HERE, "..", "../logos", fn)
    from PIL import Image
    if fn.endswith(".svg"):
        png_cache = os.path.join(HERE, "_logo_" + os.path.splitext(fn)[0] + ".png")
        if not os.path.exists(png_cache):
            import subprocess, tempfile
            raw_svg = open(p, "rb").read()
            b64 = base64.b64encode(raw_svg).decode()
            tmp = os.path.join(tempfile.gettempdir(), "l2013.html")
            open(tmp, "w", encoding="utf8").write(
                f'<!doctype html><body style="margin:0;background:transparent">'
                f'<img id=i src="data:image/svg+xml;base64,{b64}" style="height:{h*3}px;display:block"></body>')
            edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            if not os.path.exists(edge): edge = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            subprocess.check_call([edge, "--headless=new", "--hide-scrollbars", "--default-background-color=00000000",
                                   "--window-size=900,400", f"--screenshot={png_cache}",
                                   "file:///" + tmp.replace("\\", "/")])
        im = Image.open(png_cache).convert("RGBA")
        bb = im.getbbox()
        if bb: im = im.crop(bb)
    else:
        im = Image.open(p).convert("RGBA")
    ar = round(im.width / im.height, 3)
    if im.height > h * 2:
        im = im.resize((int(round(h * 2 * ar)), h * 2), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    from logo_paleta import paleta, cobertura   # la leyenda usa la versión monocroma si el logo se confunde con la barra
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.08, 86 / (ar * 28)), 3), logpal=paleta(im), logcov=cobertura(im))


exec(open(os.path.join(HERE, "logos_2013.py"), encoding="utf8").read())
from bloques_wiki import aplicar as _bloques   # bloques de los mapas presidenciales de la Wikipedia (CC0)
_bloques(CAND, 2013)

# Agrupar las secciones DINE fusionando sub-secciones
sec_raw = {}
for (d, s), grp in votes_dn.groupby(["distrito_id", "seccion_id"]):
    s_names = [str(x).strip() for x in grp["seccion_nombre"].dropna().unique() if str(x).strip() and str(x).strip().lower() != "nan"]
    sname = s_names[0] if s_names else ""
    pos = int(grp[grp["votos_tipo"] == "POSITIVO"]["v"].sum())
    bla = int(grp[grp["votos_tipo"] == "EN BLANCO"]["v"].sum())
    nul = int(grp[grp["votos_tipo"].isin(["NULO", "RECURRIDO", "IMPUGNADO"])]["v"].sum())
    vdict = {}
    for _, row in grp[grp["votos_tipo"] == "POSITIVO"].iterrows():
        aid = str(row["agrupacion_id"])
        vdict[aid] = vdict.get(aid, 0) + int(row["v"])
    ms = MESAS.get((d, s), dict(n=0, ok=0, e_tot=0, e_ok=0))
    if (d, s) in SUBSEC_MERGE:
        target_s, note_tpl = SUBSEC_MERGE[(d, s)]
        t = sec_raw.setdefault((d, target_s), dict(d=d, s=target_s, name="", el=0, el_ok=0, m_tot=0, m_ok=0,
                                                   pos=0, bla=0, nul=0, v={}, notes=[]))
        t["el"] += ms["e_tot"]; t["el_ok"] += ms["e_ok"]
        t["m_tot"] += ms["n"]; t["m_ok"] += ms["ok"]
        t["pos"] += pos; t["bla"] += bla; t["nul"] += nul
        for aid, vv in vdict.items():
            t["v"][aid] = t["v"].get(aid, 0) + vv
        if note_tpl:
            t["notes"].append((note_tpl % fmt_n(pos)) if "%s" in note_tpl else note_tpl)
    else:
        t = sec_raw.setdefault((d, s), dict(d=d, s=s, name=sname, el=0, el_ok=0, m_tot=0, m_ok=0,
                                            pos=0, bla=0, nul=0, v={}, notes=[]))
        if sname: t["name"] = sname
        t["el"] += ms["e_tot"]; t["el_ok"] += ms["e_ok"]
        t["m_tot"] += ms["n"]; t["m_ok"] += ms["ok"]
        t["pos"] += pos; t["bla"] += bla; t["nul"] += nul
        for aid, vv in vdict.items():
            t["v"][aid] = t["v"].get(aid, 0) + vv

# Emparejar cada unidad del mapa con su seccion DINE
idx_by_key = {}
for i, u in enumerate(U):
    if u["name"] == "Islas Malvinas": continue
    idx_by_key[(u["prov"], norm(u["name"]))] = i

unit_src = {}
unmatched = []
for (d, s), rec in sorted(sec_raw.items()):
    p = D2P[d]
    if p == "Capital Federal":
        k = (p, norm("Comuna %d" % int(s)))
    else:
        nm = norm(rec["name"])
        k = (p, EALIAS.get((p, nm), nm))
    i = idx_by_key.get(k)
    if i is None:
        unmatched.append((p, s, rec["name"]))
    else:
        unit_src[i] = rec

assert not unmatched, ("Sin poligono:", unmatched)
missing_geom = [u["prov"] + ":" + u["name"] for i, u in enumerate(U) if i not in unit_src and u["name"] != "Islas Malvinas"]
assert not missing_geom, ("Poligonos sin dato:", missing_geom)

GREY_N = "#8c8c8c"
GREY_P = "#e6dcc3"   # beige para unidades con 0 mesas escrutadas en el provisorio (Regla 8)


def analyse(e):
    d = e["d"]
    P = {"%s_%s" % (d, aid): v for aid, v in e["v"].items() if v > 0}
    pos = e["pos"]
    emit = pos + e["bla"] + e["nul"]
    bloc = {b: 0 for b in BLOCS}
    for aid, v in e["v"].items():
        b = LIST2BLOC.get((d, aid))
        if b in bloc: bloc[b] += v
    # Para participacion departamental se usa el padron de las mesas escrutadas (el_ok)
    ins = e["el_ok"] if e["el_ok"] > 0 else e["el"]
    return dict(d=d, P=P, pos=pos, E=emit, bla=e["bla"], nul=e["nul"], ins=ins,
                el_tot=e["el"], el_ok=e["el_ok"], m_tot=e["m_tot"], m_ok=e["m_ok"], bloc=bloc)


def rec_from(a, note=None):
    D = a["pos"]
    if not D:
        met = [["Inscriptos (padrón)", fmt_n(a["el_tot"])], ["Mesas escrutadas", "0 de %d" % a["m_tot"]]]
        msg = "Sin datos en el escrutinio provisorio de la DINE (0 de %d mesas escrutadas; %s electores habilitados)." % (a["m_tot"], fmt_n(a["el_tot"]))
        if note: msg = msg + " " + note
        return dict(lines=[], metrics=met, fill=GREY_P, note=msg)
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
        top = max(P, key=lambda c: P[c]) if P else None
        rec.update(fill=CAND.get("P_" + top, {}).get("base", GREY_N) if top else GREY_N)
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
        disp[i] = "Comuna %d · %s" % (num, BARRIOS_COMUNA[num])
    else:
        disp[i] = nice
    if e is None:
        unit_rec[i] = None
        continue
    a = analyse(e); unit_an[i] = a
    extras = []
    if p != "Capital Federal" and norm(e["name"]) != norm(u["name"]) and (p, norm(u["name"])) not in NICE:
        extras.append("Nombre en la base DINE: «%s»." % e["name"])
    extras.extend(e["notes"])
    if 0 < a["m_ok"] < a["m_tot"]:
        extras.append("Escrutinio provisorio: %d de %d mesas computadas (%s de %s electores)." % (
            a["m_ok"], a["m_tot"], fmt_n(a["el_ok"]), fmt_n(a["el_tot"])))
    unit_rec[i] = rec_from(a, " ".join(extras) or None)

# Totales provinciales y nacionales (suma de la base provisoria)
prov_an = {}
for i, a in unit_an.items():
    p = U[i]["prov"]
    pa = prov_an.setdefault(p, dict(P={}, pos=0, E=0, bla=0, nul=0, ins=0, el_tot=0, el_ok=0, m_tot=0, m_ok=0, bloc={b: 0 for b in BLOCS}))
    for k in ("pos", "E", "bla", "nul", "ins", "el_tot", "el_ok", "m_tot", "m_ok"): pa[k] += a[k]
    for c, x in a["P"].items(): pa["P"][c] = pa["P"].get(c, 0) + x
    for b in BLOCS: pa["bloc"][b] += a["bloc"][b]

prov_rec = {}
for p, pa in prov_an.items():
    pnote = None
    if pa["m_ok"] < pa["m_tot"]:
        pnote = "Escrutinio provisorio en la provincia: %d de %d mesas computadas (%.2f %%)." % (
            pa["m_ok"], pa["m_tot"], 100 * pa["m_ok"] / pa["m_tot"])
    prov_rec[p] = rec_from(pa, pnote)
for i, r in list(unit_rec.items()):
    if r is None: unit_rec[i] = prov_rec[U[i]["prov"]]

# ---------------------------------------------------------------- control contra Wikipedia
tot_bloc = {b: sum(pa["bloc"][b] for pa in prov_an.values()) for b in BLOCS}
tot_pos = sum(pa["pos"] for pa in prov_an.values())
W = wikitop.WIKI[2013]
print("=== Bloques segun la base provisoria DINE vs. Wikipedia (definitivo) ===", file=sys.stderr)
for b in BLOCS:
    vb, vw = tot_bloc[b], W["blocs"][b]
    print("  %-6s  DINE=%10s  Wiki=%10s  dif=%+d (%.2f%%)" % (b, fmt_n(vb), fmt_n(vw), vb - vw, 100 * (vb - vw) / vw), file=sys.stderr)
from collections import Counter
print("Ganadores por unidad:", Counter(r.get("w") or r.get("fill") for i, r in unit_rec.items() if U[i]["name"] != "Islas Malvinas"), file=sys.stderr)

cands, slices, partp, NAT_MET = wikitop.national(2013)
NOTE = ("Resultado nacional (torta y barras): escrutinio definitivo de «%s» en la Wikipedia en español "
        "(porcentajes sobre votos positivos). Mapa departamental y comunal: escrutinio provisorio por mesa de la DINE "
        "(89.980 de 91.582 mesas computadas, 98,25 %%); Ramón Lista (Formosa) y Valle Grande (Jujuy) figuran con 0 mesas escrutadas." % W["art"])

KEYS = [[GREY_P, "Sin dato en el escrutinio provisorio (0 mesas)"]]


def stops_for(base_hex, edges):
    r0, g0, b0 = (int(base_hex[j:j + 2], 16) for j in (1, 3, 5))
    ks = [1.15, 1.0, 0.85, 0.70, 0.55, 0.40, 0.25][:len(edges)]
    cols = []
    for k in ks:
        if k > 1:
            t = k - 1
            c = (r0 + (255 - r0) * t, g0 + (255 - g0) * t, b0 + (255 - b0) * t)
        else:
            c = (r0 * k, g0 * k, b0 * k)
        cols.append("#" + "".join("%02x" % max(0, min(255, int(round(v)))) for v in c))
    labels = ["%d%%" % e for e in edges[:-1]] + ["+%d%%" % edges[-1]]
    return cols, labels


def bin_of(p, edges):
    i = 0
    while i < len(edges) - 1 and p >= edges[i + 1]: i += 1
    return i


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(U)):
        r = unit_rec[i]; a = unit_an.get(i)
        p = fn(a) if (a and a["pos"]) else None
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        if i not in unit_an:   # Islas Malvinas
            p = fn(prov_an[U[i]["prov"]])
        nr["fill"] = cols[bin_of(p, edges)] if p is not None else GREY_P
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        v = fn(prov_an[p])
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(v, edges)] if v is not None else GREY_N
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=KEYS)


MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}
_MAL_REC = dict(lines=[], metrics=[], fill="#a9a9a9", note="Sin dato: islas bajo administración británica (se muestran en gris).")
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec,
              national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=dict(keys=KEYS))]
for mid, tile, fn, base, edges, title, extra in (
    ("fpv", "FPV", lambda a: 100 * a["bloc"]["FPV"] / a["pos"], "#4a8bc2", [0, 20, 30, 40, 50, 60, 70], "% Frente para la Victoria y aliados", ""),
    ("fpcys", "FPCyS", lambda a: 100 * a["bloc"]["FPCyS"] / a["pos"], "#ff8c00", [0, 15, 25, 35, 45, 55, 65], "% Frente Progresista Cívico y Social y aliados", ""),
    ("fr", "FR", lambda a: 100 * a["bloc"]["FR"] / a["pos"], "#4a5568", [0, 10, 20, 30, 40, 50, 60], "% Frente Renovador y aliados", ""),
    ("pro", "PRO", lambda a: 100 * a["bloc"]["PRO"] / a["pos"], "#eab308", [0, 5, 10, 20, 30, 40, 50], "% Unión PRO y aliados", ""),
    ("par", "PART", lambda a: (100 * a["E"] / a["ins"]) if a["ins"] else None, "#2a6f97", [0, 70, 75, 80, 85, 90, 95], "Participación sobre mesas escrutadas (%)", "")):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, note=extra + NOTE, units=un, prov=pv,
                      national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=lg))

for _m in MODES:
    for _i in MALV: _m["units"][_i] = dict(_MAL_REC)

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
    body.append('<text class="cn" x="%s" y="%s" text-anchor="middle"%s>%s</text>' % (f2(x) if "f2" in globals() else "%.1f" % x, "%.1f" % y, (' transform="rotate(%d %.1f %.1f)"' % (rot, x, y)) if rot else "", txt))


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
insets99.SHP = os.path.join(HERE, "..", "../geometria/Base deptos 1869-2022", "Departamentos_2010")
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
    body.append('<rect class="mk" x="%s" y="%s" width="%s" height="%s"/>' % tuple("%.2f" % v for v in w))

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
pv.append('</g>')

ds = dict(
    year=2013, slug="diputados_2013", locale="es-AR", country="Argentina",
    title="Elecciones legislativas de Argentina de",
    exterior=False,
    sets={"1": dict(label="Resultados", subtitle="Diputados nacionales")},
    labels=dict(results="Resultados", won="GANÓ", pie1="Proporción sobre votos positivos",
                pie2="Anillo exterior: Participación", provinces="Provincias"),
    candidates=CAND, insets=INSETS,
    territories=[dict(p=u["prov"], n=disp[i], k=u["kind"]) for i, u in enumerate(U)],
    modes=MODES,
)
open(os.path.join(HERE, "dataset_2013.json"), "w", encoding="utf8").write(json.dumps(ds, ensure_ascii=False))

# ---------------------------------------------------------------- HTML
tpl = open(TPL, encoding="utf8").read()


def sub(old, new):
    global tpl
    assert old in tpl, "no encontrado: " + old[:60]
    tpl = tpl.replace(old, new, 1)


sub("<title>Atlas electoral</title>", "<title>Elecciones legislativas 2013</title>")
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub('<g id="pv" transform="matrix(0.1448 0 0 0.1448 55.7 599.8)" style="--spf:9.7px">',
    '<g id="pv" transform="matrix(%s 0 0 %s %.2f %.2f)" style="--spf:9.7px">' % (KPV, KPV, pv_tx, pv_ty))
sub('#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}',
    '#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}')
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"',
    'style="--v-d:inline;--v-dc:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<clipPath id="mapclip"><path clip-rule="evenodd" d="M570 100h840v1540h-840z M570 300h80v185h-80z M570 545h79v159h-79z M1247 785h163v320h-163z M1247 1166h163v452h-163z M985 1200h200v320h-200z"/></clipPath>',
    '<clipPath id="mapclip"><path id="clippath" clip-rule="evenodd" d="M570 100h840v1540h-840z"/></clipPath>')

s = tpl.index("const INSETS=["); e = tpl.index("];", s) + 2
tpl = tpl[:s] + "const INSETS=DATA.insets||[];" + tpl[e:]
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

sub('const shade=(code,i)=>{const b=CAND[code].base;return i===0?mixw(b,.15):mulc(b,SHADE_K[i])};',
    open(os.path.join(HERE, "..", "../comun/leyenda_clara.js"), encoding="utf8").read())
# Leyenda compacta para 15 bloques + clave de gris/beige
sub("""    const h=50,win=idx===0&&!LG,bar=C.bar||C.base;
    el("rect",{x:80,y,width:5,height:h-1,fill:mixw(bar,.42)},g);
    el("rect",{x:93,y,width:win?431:337,height:h,fill:bar},g);
    if(win)el("rect",{x:429,y,width:95,height:h,fill:mulc(bar,.85)},g);
    const lg=C.logo||c.code;                                    // sigla grande a la izquierda (en 1999: logo del frente)
    el("text",{x:104,y:y+36,"font-size":lg.length>2?34:40,fill:"#fff","letter-spacing":-1},g,lg);
    el("rect",{x:104,y:y+41,width:lg.length>2?(lg.length*20):(lg.length*23),height:3,fill:"#fff",opacity:.8},g);
    el("text",{x:424,y:y+21,"font-size":21,fill:"#fff","text-anchor":"end"},g,C.n);
    if(C.sub)el("text",{x:424,y:y+39,"font-size":15,fill:"#fff","text-anchor":"end",opacity:.95},g,C.sub);
    if(win){
      el("text",{x:477,y:y+29,"font-size":26,fill:"#fff","text-anchor":"middle"},g,f2(c.pct)+"%");
      el("text",{x:497,y:y+44,"font-size":10,fill:"#fff","font-style":"italic","text-anchor":"middle",opacity:.85},g,LAB.won);
    }else{
      el("text",{x:476,y:y+33,"font-size":23,fill:C.txt||bar,"text-anchor":"middle"},g,f2(c.pct)+"%");
    }
    y+=h+(idx+1<rows.length&&!LG&&wins[rows[idx+1].code]?5:7);
  });""",
    """    LEGEND_ROW(g,C,c,y,rows,idx===0&&!LG,27);
    y+=27+2.5;
  });
  if(KEYS){
    y+=(rows.length?14:12);
    KEYS.keys.filter(([k])=>USED(k)).forEach(([col,lab])=>{el("rect",{x:93,y:y-11,width:15,height:13,fill:col,stroke:"#616161","stroke-width":.8},g);el("text",{x:115,y:y,"font-size":13.5,fill:"#616161"},g,lab);y+=19;});
  }
  ANCHOR_LEGEND(g);""")

sub("""      for(let i=0;i<7;i++){
        const x=93+i*46.2,w=43.5;
        el("rect",{x,y,width:w,height:9,fill:shade(c.code,i),opacity:(used[c.code]&&used[c.code][i])?1:.38},g);
        if(idx===0)el("text",{x:x+w/2,y:y-6,"font-size":14,"font-style":"italic",fill:"#616161","text-anchor":"middle"},g,BIN_LABEL[i]);
      }
      y+=15;""",
    """      for(let i=0;i<7;i++){
        const x=93+i*46.2,w=43.5;
        el("rect",{x,y,width:w,height:5.5,fill:shade(c.code,i),opacity:(used[c.code]&&used[c.code][i])?1:.38},g);
        if(idx===0)el("text",{x:x+w/2,y:y-4,"font-size":13,"font-style":"italic",fill:"#616161","text-anchor":"middle"},g,BIN_LABEL[i]);
      }
      y+=8.5;""")

sub("""  const LG=MODES[MODE].legend;                                   // leyenda propia para mapas de color explícito (coropletas)""",
    """  const LG0=MODES[MODE].legend;const LG=(LG0&&LG0.stops)?LG0:null;
  const KEYS=LG0&&LG0.keys?LG0:null;
  const USED=c=>[...document.querySelectorAll('#B .d,#B .dc')].some(e=>(e.getAttribute("fill")||"").toLowerCase()===c.toLowerCase());""")
sub("const rows=(LG&&LG.bars===false)?[]:N.cands;", "const rows=(LG0&&LG0.bars===false)?[]:N.cands;")
sub("""  el("text",{x:93,y:1266,"font-size":20,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=1292;""",
    """  const Y0=(!(LG0&&LG0.bars===false)&&N.cands.length>10)?1022:1266;
  el("text",{x:93,y:Y0,"font-size":19,fill:"#616161"},g,(LG&&LG.title)||LAB.results);
  let y=Y0+22;""")

sub("""$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;""", """$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;$("#pie1").setAttribute("x",184);""")
sub("return out.slice(0,4);", "return out.slice(0,6);")
sub("const list=tilesNow(),xs=[1262,1316,1370,1424];",
    "const list=tilesNow(),xs=list.length>5?[1196,1248,1300,1352,1404,1456]:list.length>4?[1208,1262,1316,1370,1424]:[1262,1316,1370,1424];")
sub("    const sw=(t.length>6)?68:48,xx=xs[i];",
    "    const sw=(t.length>6)?68:48,xx=xs[i];")
sub("    if(t.length>5)tt.setAttribute(\"font-size\",15);",
    "    if(t.length>=5)tt.setAttribute(\"font-size\",12.5);")

tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
           .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
out = os.path.join(HERE, "atlas_2013.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
