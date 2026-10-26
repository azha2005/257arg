
# ---------------------------------------------------------------- candidaturas, logos
CAND = {
    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], logo="FP"),
    "LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a2f85", txt="#5a2f85", logo="LLA"),
    "FIT": dict(n="Frente de Izquierda", sub="y de Trabajadores - Unidad", base=COLOR["FIT"], logo="FIT"),
    "PU": dict(n="Provincias Unidas", sub="Ciudadanos Unidos en Capital", base=COLOR["PU"], bar="#f06a0b", txt="#d9560a", logo="PU"),
    "OTR": dict(n="Otros", sub="Resto de las listas", base="#b3b3b3", bar="#a6a6a6", txt="#8f8f8f", logo="···"),
}
for c in LAB:
    CAND["P_" + c] = dict(n=LAB[c], base=COLOR.get(c, DEFAULT_COL), minor=True)
CAND["P_BLA"] = dict(n="En blanco", base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Nulos e impugnados", base="#b0b0b0", minor=True)


def _ar_svg(t):
    m = re.search(r'viewBox="([\d.\s-]+)"', t)
    if m:
        v = [float(x) for x in m.group(1).split()]
        return v[2] / v[3]
    w = re.search(r'\bwidth="([\d.]+)', t); h = re.search(r'\bheight="([\d.]+)', t)
    return float(w.group(1)) / float(h.group(1)) if w and h else 1.0


def _logo(fn, h=50):
    t = open(os.path.join(LOGOS, fn), encoding="utf8").read()
    t = re.sub(r"<metadata.*?</metadata>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    ar = _ar_svg(t)
    return dict(img="data:image/svg+xml;base64," + base64.b64encode(t.encode("utf8")).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


def _logo_raster(fn, px=360, h=50):
    from PIL import Image
    im = Image.open(os.path.join(LOGOS, fn)).convert("RGBA")
    ar = im.width / im.height
    k = px / max(im.size); im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


_lg = os.path.join(HERE, "logos_amba2025.py")
if os.path.exists(_lg): exec(open(_lg, encoding="utf8").read())

# ---------------------------------------------------------------- resultado de la region (suma de los circuitos de la base)
pos = TOT["pos"]
cands = sorted([{"code": b, "votes": int(TOT["bloc"][b]), "pct": round(100 * TOT["bloc"][b] / pos, 2)} for b in BLOCS], key=lambda c: -c["votes"])
otros = pos - sum(c["votes"] for c in cands)
cands.append({"code": "OTR", "votes": int(otros), "pct": round(100 * otros / pos, 2)})
slices = [{"code": c["code"], "v": c["votes"]} for c in cands[:-1]] + [{"fill": "#717274", "v": int(otros)}]
partp = round(100 * TOT["E"] / TOT["elok"], 2)
NAT_MET = [["Electores (mesas escrutadas)", fmt_n(TOT["elok"])], ["Votantes", fmt_n(TOT["E"])], ["Participación", fmt_p(partp) + " %"],
           ["Votos positivos", fmt_n(pos)], ["Votos en blanco", fmt_n(TOT["bla"])], ["Nulos e impugnados", fmt_n(TOT["nul"] + TOT["imp"])],
           ["Mesas escrutadas", "%s de %s" % (fmt_n(TOT["ok"]), fmt_n(TOT["mesas"]))]]

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


NOTE = ("Fuente: escrutinio provisorio por mesa de diputados nacionales (26 oct. 2025), Dirección Nacional Electoral, datos.mininterior.gob.ar; "
        "porcentajes sobre votos positivos, agregados por circuito electoral. El resultado de la torta y las barras es la suma del AMBA (Capital + 40 partidos). "
        "No es el escrutinio definitivo: %d de %s mesas figuran sin escrutar. Geometría: circuitos CNE/INDEC de 2021; los circuitos que la base subdivide con letras "
        "se muestran con el polígono del circuito de origen (el circuito 548 de Gral. Las Heras no figura en la capa de polígonos: se dibuja el hueco que dejan sus vecinos, inferido). "
        "Provincias Unidas = «Alianza Provincias Unidas» en Buenos Aires y «Ciudadanos Unidos» en Capital." % (TOT["mesas"] - TOT["ok"], fmt_n(TOT["mesas"])))


def mode_choropleth(fn, base, edges, title):
    cols, labels = stops_for(base, edges)
    units = []
    for i in range(len(UKEYS)):
        r = unit_rec[i]; a = unit_an[i]
        nr = {k: v for k, v in r.items() if k not in ("w", "q", "fill")}
        if not a["ok"] or not a["pos"]: nr["fill"] = BEIGE
        else: nr["fill"] = cols[bin_of(fn(a), edges)]
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = cols[bin_of(fn(part_an[p]), edges)]
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False)


pct = lambda b: (lambda a: 100 * a["bloc"][b] / a["pos"])
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(len(UKEYS))], prov=prov_rec,
              national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET),
              legend=dict(keys=[[BEIGE, "Circuito sin mesas en la base provisoria"]]))]
for mid, tile, fn, base, edges, title in (
    ("fp", "FP", pct("FP"), COLOR["FP"], [0, 20, 30, 40, 50, 60, 70], "% Fuerza Patria"),
    ("lla", "LLA", pct("LLA"), COLOR["LLA"], [0, 20, 30, 40, 50, 60, 70], "% La Libertad Avanza"),
    ("fit", "FIT", pct("FIT"), COLOR["FIT"], [0, 3, 5, 8, 12, 18, 25], "% Frente de Izquierda - Unidad"),
    ("par", "PART.", lambda a: 100 * a["E"] / a["elok"], "#4a4a4a", [40, 55, 62, 66, 70, 74, 78], "Participación (mesas escrutadas)")):
    un, pv, lg = mode_choropleth(fn, base, edges, title)
    MODES.append(dict(id=mid, tile=tile, note=NOTE, units=un, prov=pv, national=dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET), legend=lg))

# ---------------------------------------------------------------- SVG
body = []
for i, g in enumerate(G):
    body.append('<path class="d" data-i="%d" d="%s"/>' % (i, geom_d(g)))
caba_idx = [i for i, k in enumerate(UKEYS) if k[0] == "01"]
for i in caba_idx:
    body.append('<path class="dc" data-i="%d" d="%s"/>' % (i, geom_d(shapely.simplify(G_raw[i], 0.01))))
PGEOM = {}
for p in PARTIDOS:
    u = unary_union([G_raw[i] for i in range(len(UKEYS)) if PART[i] == p])
    u = fill_slivers(u.buffer(0.7, join_style=2).buffer(-0.7, join_style=2))
    PGEOM[p] = u
    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(u.boundary)))


def bbox_of(idx):
    return shapely.total_bounds([G_raw[i] for i in idx])


def window(b, aspect, pad=0.07):
    x0, y0, x1, y1 = b
    ww, hh = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    if ww / hh < aspect: ww = hh * aspect
    else: hh = ww / aspect
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(mx - ww / 2, 2), round(my - hh / 2, 2), round(ww, 2), round(hh, 2)]


def idx_of(partidos):
    return [i for i in range(len(UKEYS)) if PART[i] in partidos]


CORE = ["Ciudad de Buenos Aires", "Vicente Lopez", "San Isidro", "San Fernando", "Tigre", "General San Martin", "Tres De Febrero", "Hurlingham", "Moron", "Ituzaingo",
        "San Miguel", "Jose C. Paz", "Malvinas Argentinas", "Lanus", "Avellaneda", "Lomas De Zamora", "Quilmes", "Almirante Brown", "Esteban Echeverria",
        "La Matanza", "Berazategui", "Florencio Varela", "Merlo", "Moreno", "Ezeiza"]
PARTIDOS_NORM = {re.sub(r"[^a-z]", "", p.lower()): p for p in PARTIDOS}
core_idx = [i for i in range(len(UKEYS)) if re.sub(r"[^a-z]", "", PART[i].lower()) in {re.sub(r"[^a-z]", "", c.lower()) for c in CORE}]
lp_idx = [i for i in range(len(UKEYS)) if re.sub(r"[^a-z]", "", PART[i].lower()) in ("laplata", "berisso", "ensenada")]
def win_ll(lon, lat, wlon, aspect):
    x, y = ll(lon, lat); w = wlon * KX * S; hh = w / aspect
    return [round(x - w / 2, 2), round(y - hh / 2, 2), round(w, 2), round(hh, 2)]


INSETS = [
    dict(id="caba", label="Ciudad de Buenos Aires", f=[70, 610, 440, 470], win=window(bbox_of(caba_idx), 440 / 470, 0.04), show=["dc"], sd=2.2, fit="meet"),
    dict(id="core", label="Conurbano y Capital", f=[1450, 140, 430, 420], win=win_ll(-58.50, -34.64, 0.36, 430 / 420), show=["d", "pb"], sd=1.5, sp=2.4),
    dict(id="lp", label="Gran La Plata", f=[1495, 640, 385, 300], win=win_ll(-57.955, -34.905, 0.13, 385 / 300), show=["d", "pb"], sd=1.8, sp=2.6),
]
# sin marcos de los recuadros sobre el mapa principal (distraen)
pv = []

# ---------------------------------------------------------------- dataset
ds = dict(
    slug="diputados_amba_2025", locale="es-AR", country="Argentina",
    title="Elecciones legislativas en el AMBA de", year="2025",
    labels=dict(pie1="Proporción sobre votos positivos", provinces=""),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="2025", subtitle="Por circuito · provisorio")},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp[i], p=PART[i], k="circuito") for i in range(len(UKEYS))],
)
json.dump(ds, open(os.path.join(HERE, "dataset_amba2025.json"), "w", encoding="utf8"), ensure_ascii=False)
