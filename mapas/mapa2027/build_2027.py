"""Genera mapa2027/atlas_2027.html y mapa2027/dataset_2027.json (escenario hipotetico: presidenciales 2027, 1.a vuelta y balotaje)."""
import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
import os, sys, json, pickle, math, base64, io
import shapely
from shapely import affinity
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import geom
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




# ---------------------------------------------------------------- escenario 2027 (simulacion; ver escenario27.py)
import escenario27 as E
BASE = pickle.load(open(os.path.join(HERE, "base27.pkl"), "rb"))
assert [(p, n) for p, n, _ in BASE["U"]] == [(u["prov"], u["name"]) for u in U], "orden de unidades distinto de prep27"
O = E.run(verbose=False)
OK = O["ok"]
ROW = {i: r for r, i in enumerate(OK)}
V1, R2, POS23 = O["v1"], O["r2"], O["V"].sum(1)
D23 = O["d"]
CODES = E.CANDS                      # MIL BRE KIC VIL SCI MAN SCH
MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}
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


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


GREY_N = "#8c8c8c"

# Candidaturas del escenario (colores: LLA, FIT y Provincias Unidas como en AMBA 2025; PJ azul del proyecto)
CAND = {
    "MIL": dict(n="Javier Milei", sub="La Libertad Avanza · Santilli", base="#6f3fa0", bar="#5a2f85", txt="#5a2f85", logo="LLA"),
    "BRE": dict(n="Myriam Bregman", sub="Frente Popular · Siley", base="#a31515", logo="FIT"),
    "KIC": dict(n="Axel Kicillof", sub="Derecho al Futuro · Lousteau", base="#318ce7", logo="MDF"),
    "VIL": dict(n="Victoria Villarruel", sub="Todo por Argentina · Centurión", base="#c2185b", bar="#6d0f45", txt="#a3134f", logo="TxA"),
    "SCI": dict(n="Daniel Scioli", sub="Una Argentina Renovada · Jalil", base="#14b8a6", bar="#10a091", txt="#0c7d70", logo="UAR"),
    "MAN": dict(n="Facundo Manes", sub="Consenso Federal · Oliveto", base="#43a047", bar="#388e3c", txt="#2e7d32", logo="CF"),
    "SCH": dict(n="Juan Schiaretti", sub="Provincias Unidas · García", base="#ff7f20", bar="#f06a0b", txt="#d9560a", logo="PU"),
    "OTR": dict(n="Otros", sub="Scioli y Manes (sin unidad ganada)", base="#9a9a9a", bar="#8c8c8c", txt="#6f6f6f", logo="S+M"),
}


def _logo_raster(fn, px=360):
    from PIL import Image
    im = Image.open(os.path.join(HERE, "..", "../logos", fn)).convert("RGBA")
    ar = im.width / im.height
    k = px / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=round(ar, 3), bl=round(min(1.1, 98 / (ar * 50)), 3))


# Emblemas de las fuerzas de 2025 (recortes del PNG del usuario usados en AMBA 2025); el resto lleva sigla
CAND["MIL"].update(_logo_raster("AMBA2025_lla_del_png_original.png"))
CAND["BRE"].update(_logo_raster("AMBA2025_fit_del_png_original.png"))
CAND["SCH"].update(_logo_raster("AMBA2025_pu_del_png_original.png"))
CAND["KIC"].update(_logo_raster("Logo_MDF_Kicillof.png"))          # recorte de la imagen del usuario (16-oct-2026)
CAND["VIL"].update(_logo_raster("Logo_Villarruel_V.png"))
CAND["VIL"]["bl"] = 0.82     # logo alto: que entre entero en la barra

NOTE1 = ("ESCENARIO HIPOTÉTICO, no es un resultado: primera vuelta del 24-oct-2027 inferida por departamento a partir de las generales y la PASO 2023 "
         "(DINE, escrutinio provisorio) con una matriz de traspasos de voto ajustada para que el total nacional coincida con el escenario. "
         "Se supone el mismo electorado de 2023, escalado al total del escenario.")
NOTE2 = ("ESCENARIO HIPOTÉTICO, no es un resultado: balotaje Milei - Bregman del 21-nov-2027 inferido desde la primera vuelta simulada con traspasos "
         "de cada candidatura (y abstención), ajustado al total nacional del escenario.")


def unit_sections(i):
    x = D23[i]; p = x["lla"] + x["uxp"] + x["jxc"] + x["hxnp"] + x["fit"]
    pc = lambda v: fmt_p(100 * v / p) + " %"
    return [dict(title="Punto de partida: generales 2023", rows=[
        ["Milei (La Libertad Avanza)", pc(x["lla"])], ["Massa + Grabois (Unión por la Patria)", pc(x["uxp"])],
        ["Bullrich + Larreta (Juntos por el Cambio)", pc(x["jxc"])], ["Schiaretti (Hacemos)", pc(x["hxnp"])], ["Bregman (FIT-U)", pc(x["fit"])],
        ["Grabois dentro de UxP (PASO 2023)", fmt_p(100 * x["g"]) + " %"], ["Larreta dentro de JxC (PASO 2023)", fmt_p(100 * x["l"]) + " %"],
        ["Gómez Centurión 2019, relativo al país", "×%.2f" % x["c"]]])]


def rec_from_votes(votes, codes, note=None, sections=None):
    D = float(sum(votes))
    order = sorted(range(len(codes)), key=lambda k: -votes[k])
    lines = [[codes[k], int(round(votes[k])), round(100 * votes[k] / D, 2)] for k in order if votes[k] > 0]
    rec = {"lines": lines, "metrics": [["Votos positivos (escenario)", fmt_n(D)]],
           "w": codes[order[0]], "q": round(100 * votes[order[0]] / D, 2)}
    if note: rec["note"] = note
    if sections: rec["sections"] = sections
    return rec


R1_UNIT, R2_UNIT, DISP = {}, {}, {}
for i, u in enumerate(U):
    p = u["prov"]
    if i in MALV:
        continue
    r = ROW[i]
    if p == "Capital Federal":
        num = int(u["name"].split()[1]); DISP[i] = "Comuna %d · %s" % (num, BARRIOS_COMUNA[num])
    else:
        DISP[i] = NICE.get((p, norm(u["name"])), u["name"])
    secs = unit_sections(i)
    R1_UNIT[i] = rec_from_votes(V1[r], CODES, sections=secs)
    R2_UNIT[i] = rec_from_votes(R2[r], ["MIL", "BRE"], sections=secs)
for i in MALV:
    DISP[i] = U[i]["name"]


def prov_votes(p, M):
    ix = [ROW[i] for i in ROW if U[i]["prov"] == p]
    return M[ix].sum(0)


PROVS_ALL = sorted({u["prov"] for u in U})
R1_PROV = {p: rec_from_votes(prov_votes(p, V1), CODES) for p in PROVS_ALL}
R2_PROV = {p: rec_from_votes(prov_votes(p, R2), ["MIL", "BRE"]) for p in PROVS_ALL}
_MAL_REC = dict(lines=[], metrics=[], fill="#a9a9a9", note="Sin dato: islas bajo administración británica (se muestran en gris).")
R1_UNITS = [R1_UNIT.get(i, dict(_MAL_REC)) for i in range(len(U))]
R2_UNITS = [R2_UNIT.get(i, dict(_MAL_REC)) for i in range(len(U))]

# ---------------------------------------------------------------- resultado nacional del escenario (la imagen del usuario)
S1 = sum(E.T1.values()); S2 = sum(E.T2.values())
WINS1 = {c: sum(1 for i in R1_UNIT if R1_UNIT[i]["w"] == c) for c in CODES}
WINS1.update({c + "_p": sum(1 for p in R1_PROV if R1_PROV[p]["w"] == c) for c in CODES})
LEG1 = [c for c in sorted(CODES, key=lambda c: -E.T1[c]) if WINS1[c] > 0 or WINS1[c + "_p"] > 0]     # leyenda: solo quienes ganan alguna unidad
OTR1 = S1 - sum(E.T1[c] for c in LEG1)
cands1 = [{"code": c, "votes": E.T1[c], "pct": round(100 * E.T1[c] / S1, 2)} for c in LEG1]
if OTR1: cands1.append({"code": "OTR", "votes": OTR1, "pct": round(100 * OTR1 / S1, 2)})
slices1 = [{"code": c["code"], "v": c["votes"]} if c["code"] != "OTR" else {"fill": CAND["OTR"]["base"], "v": c["votes"]} for c in cands1]
cands2 = [{"code": c, "votes": E.T2[c], "pct": round(100 * E.T2[c] / S2, 2)} for c in ("MIL", "BRE")]
NAT1 = dict(cands=cands1, slices=slices1, partp=79.18,
            metrics=[["Inscriptos", "35.112.844"], ["Votantes", fmt_n(S1)], ["Participación", "79,18 %"], ["Votos positivos", fmt_n(S1)]])
NAT2 = dict(cands=cands2, slices=[{"code": c["code"], "v": c["votes"]} for c in cands2], partp=68.32,
            metrics=[["Inscriptos", "34.763.082"], ["Votantes", fmt_n(S2)], ["Participación", "68,32 %"], ["Votos positivos", fmt_n(S2)]])
print("Leyenda 1.a vuelta:", LEG1, "| otros:", OTR1, file=sys.stderr)
print("Unidades ganadas 1.a vuelta:", {c: WINS1[c] for c in CODES}, "provincias:", {c: WINS1[c + "_p"] for c in CODES}, file=sys.stderr)
W2 = {c: sum(1 for i in R2_UNIT if R2_UNIT[i]["w"] == c) for c in ("MIL", "BRE")}
W2p = {c: sum(1 for p in R2_PROV if R2_PROV[p]["w"] == c) for c in ("MIL", "BRE")}
print("Balotaje: departamentos", W2, "provincias", W2p, file=sys.stderr)


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


def mode_choropleth(units_rec, prov_rec, M, k, base, edges, title):
    cols, labels = stops_for(base, edges)
    pct = lambda row: 100 * row[k] / row.sum()
    units = []
    for i in range(len(U)):
        r = units_rec[i]
        nr = {kk: v for kk, v in r.items() if kk not in ("w", "q", "fill")}
        if i in MALV:
            units.append(dict(_MAL_REC)); continue
        nr["fill"] = cols[bin_of(pct(M[ROW[i]]), edges)]
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        nr = {kk: v for kk, v in r.items() if kk not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(pct(prov_votes(p, M)), edges)]
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False)


MODES = [dict(id="gan", tile="GANÓ", set="1", note=NOTE1, units=R1_UNITS, prov=R1_PROV, national=NAT1, legend={})]
for mid, tile, k, base, edges, title in (
    ("mil", "MILEI", 0, "#6f3fa0", [20, 25, 30, 35, 40, 45, 50], "% Javier Milei (La Libertad Avanza)"),
    ("bre", "BREG.", 1, "#a31515", [6, 9, 12, 15, 18, 22, 26], "% Myriam Bregman (Frente Popular)"),
    ("kic", "KICI.", 2, "#318ce7", [8, 11, 14, 17, 20, 25, 30], "% Axel Kicillof (Derecho al Futuro)"),
    ("vil", "VILL.", 3, "#c2185b", [6, 8, 10, 12, 14, 16, 18], "% Victoria Villarruel (Todo por Argentina)")):
    un, pv_, lg = mode_choropleth(R1_UNITS, R1_PROV, V1, k, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, set="1", note=NOTE1, units=un, prov=pv_, national=NAT1, legend=lg))
MODES.append(dict(id="gan2", tile="GANÓ", set="2", note=NOTE2, units=R2_UNITS, prov=R2_PROV, national=NAT2, legend={}))
for mid, tile, k, base, edges, title in (
    ("bre2", "BREG.", 1, "#a31515", [20, 25, 30, 35, 40, 45, 50], "% Myriam Bregman en el balotaje"),
    ("mil2", "MILEI", 0, "#6f3fa0", [50, 55, 60, 65, 70, 75, 80], "% Javier Milei en el balotaje")):
    un, pv_, lg = mode_choropleth(R2_UNITS, R2_PROV, R2, k, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, set="2", note=NOTE2, units=un, prov=pv_, national=NAT2, legend=lg))
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
for _i in MALV:   # Malvinas en gris tambien en el mini de provincias (la simplificacion de provincias las borra)
    pv.append('<path class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round" d="%s"/>' % geom_d(G[_i]))
pv.append('</g>')


ds = dict(
    year="2027", slug="presidente_2027_escenario", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de", exterior=False,
    sets={"1": dict(label="1ª V.", subtitle="Hipotético · 1ª vuelta"), "2": dict(label="2ª V.", subtitle="Hipotético · balotaje")},
    bins=[30, 40, 50, 60, 70, 80], bin_labels=["20%", "30%", "40%", "50%", "60%", "70%", "+80%"],
    labels=dict(results="Resultados", won="GANÓ", pie1="Proporción sobre votos positivos",
                pie2="Anillo exterior: Participación", provinces="Provincias"),
    candidates=CAND, insets=INSETS,
    territories=[dict(p=u["prov"], n=DISP[i], k=u["kind"]) for i, u in enumerate(U)],
    modes=MODES,
)
open(os.path.join(HERE, "dataset_2027.json"), "w", encoding="utf8").write(json.dumps(ds, ensure_ascii=False))

# ---------------------------------------------------------------- HTML
tpl = open(TPL, encoding="utf8").read()


def sub(old, new):
    global tpl
    assert old in tpl, "no encontrado: " + old[:60]
    tpl = tpl.replace(old, new, 1)



sub("<title>Atlas electoral</title>", "<title>Presidenciales 2027 (escenario)</title>")
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
sub('if(C.sub)el("text",{x:424,y:y+39,"font-size":15,', 'if(C.sub)el("text",{x:424,y:y+37*k,"font-size":MANY?13:15,')
sub('el("text",{x:477,y:y+29,"font-size":26,', 'el("text",{x:477,y:y+29*k,"font-size":MANY?23:26,')
sub('el("text",{x:497,y:y+44,"font-size":10,', 'el("text",{x:497,y:y+44*k,"font-size":10,')
sub('el("text",{x:476,y:y+33,"font-size":23,', 'el("text",{x:476,y:y+33*k,"font-size":MANY?20:23,')

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
out = os.path.join(HERE, "atlas_2027.html")
open(out, "w", encoding="utf8", newline="\n").write(html)
print("escrito", out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)
