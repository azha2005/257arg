"""Cámara de Diputados para la proyección de la noche (28-oct-2026): reparto D'Hondt por distrito de las bancas que se
renuevan, las que no se renuevan (las ganadas en la elección anterior, por fuerza), el hemiciclo al estilo del
generador de diagramas de la Wikipedia (Parliament diagram tool, disposición en arco) y un mapa por provincia.
Lo usa proyectar_fotos.py --congreso <año>.

- Bancas por distrito: tabla «Bancas por distrito» de datos/wikileg/wleg2025.txt (257; 127 se renuevan en 2025, 2021,
  2017...; las otras 130 en 2023, 2027...).
- Umbral: 3 % del padrón electoral del distrito (ley 22.838). Padrón: electores por circuito de la elección.
- Bancas que no se renuevan: D'Hondt sobre las listas de mapas/mapa<año-2>/mapeo_listas_<año-2>.csv, con el padrón
  de esa elección. Los bloques de menos del 3 % del país quedan con su nombre y se dibujan como «Provinciales y otras».
  En 2025 (y años con revisión guardada) salen en cambio de la tabla «Bancas por bloque» de la Wikipedia: ver REVISION.
- La columna OTRAS de la proyección se parte entre las listas menores oficializadas del distrito con un perfil de Zipf
  (ZIPF), para que una lista provincial pueda ganar una banca sin inflar su peso: ver repartir()."""
import os, json, re, math
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DIST = {"01": "Capital Federal", "02": "Buenos Aires", "03": "Catamarca", "04": "Córdoba", "05": "Corrientes",
        "06": "Chaco", "07": "Chubut", "08": "Entre Ríos", "09": "Formosa", "10": "Jujuy", "11": "La Pampa",
        "12": "La Rioja", "13": "Mendoza", "14": "Misiones", "15": "Neuquén", "16": "Río Negro", "17": "Salta",
        "18": "San Juan", "19": "San Luis", "20": "Santa Cruz", "21": "Santa Fe", "22": "Santiago del Estero",
        "23": "Tucumán", "24": "Tierra del Fuego"}
WIKI_NOMBRE = {"Provincia de Buenos Aires": "Buenos Aires", "Ciudad de Buenos Aires": "Capital Federal"}
UMBRAL = 0.03
# fuerzas: nombre largo, color (paleta de los atlas legislativos 2023/2025) y orden de izquierda a derecha
FUERZAS = {"FIT": ("FIT-Unidad", "#ed4d57"), "FP": ("Fuerza Patria", "#009ce4"),
           "UxP": ("Unión por la Patria", "#009ce4"), "PROV": ("Provinciales y otras", "#9e9e9e"),
           "HxNP": ("Hacemos por Nuestro País", "#283084"), "PU": ("Provincias Unidas", "#FF682C"),
           "JxC": ("Juntos por el Cambio", "#fcbc00"), "LLA": ("La Libertad Avanza", "#6c4c98")}
ORDEN = ["FIT", "FP", "UxP", "PROV", "HxNP", "PU", "JxC", "LLA"]
CORTO = {"La Libertad Avanza": "LLA", "Libertad Avanza": "LLA", "Avanza Libertad y La Libertad Avanza": "LLA",
         "Fuerza Patria": "FP", "Unión por la Patria": "UxP", "Provincias Unidas": "PU",
         "Frente de Izquierda y de Trabajadores - Unidad": "FIT", "Juntos por el Cambio": "JxC",
         "Hacemos por Nuestro País": "HxNP"}


def bancas():
    """{distrito: (total, se renuevan en 2025)}."""
    t = open(os.path.join(ROOT, "datos", "wikileg", "wleg2025.txt"), encoding="utf8").read()
    i = t.index("=== Bancas por distrito ===")
    j = t.index("{|", i)
    tb = t[j:t.index("\n|}", j)]
    inv = {v: k for k, v in DIST.items()}
    out = {}
    for blk in tb.split("\n|-")[1:]:
        m = re.search(r"\{\{(?:bandera2|ARG)\|([^}]*)\}\}\s*\n\|\s*(\d+)\s*\n\|\s*(\d+)", blk)
        if m:
            out[inv[WIKI_NOMBRE.get(m.group(1), m.group(1))]] = (int(m.group(2)), int(m.group(3)))
    assert sum(v[0] for v in out.values()) == 257 and sum(v[1] for v in out.values()) == 127
    return out


def renuevan(anio):
    """{distrito: bancas que se eligen en anio}."""
    b = bancas()
    return {d: (r if (anio - 2025) % 4 == 0 else t - r) for d, (t, r) in b.items()}


def dhondt(votos, n, umbral=0.0):
    """votos = {lista: votos}; las listas por debajo del umbral (en votos) no entran."""
    ok = {k: v for k, v in votos.items() if v >= umbral and v > 0}
    seats = {k: 0 for k in votos}
    for _ in range(n):
        if not ok:
            break
        k = max(ok, key=lambda x: (ok[x] / (seats[x] + 1), ok[x]))
        seats[k] += 1
    return seats


def padron(anio):
    """Electores por distrito en la elección legislativa anio (o presidencial si no hay)."""
    for f in (os.path.join(HERE, "circ_%sbl.pkl" % anio), os.path.join(ROOT, "transferencias", "circ_%s.pkl" % anio)):
        if os.path.exists(f):
            _, e = pd.read_pickle(f)
            return e.groupby(level=0).sum().to_dict()
    raise FileNotFoundError("sin padrón de %s" % anio)


def listas(anio):
    m = pd.read_csv(os.path.join(ROOT, "mapas", "mapa%s" % anio, "mapeo_listas_%s.csv" % anio), dtype=str,
                    encoding="utf-8-sig")
    m["votos"] = m.votos.astype(int)
    m["distrito"] = m.distrito.str.zfill(2)
    tot = m.groupby("bloque").votos.sum()
    big = set(tot[tot >= .03 * tot.sum()].index)
    m["fuerza"] = [CORTO.get(b, b) if b in big else "PROV" for b in m.bloque]
    return m


def electos(anio):
    """Bancas ganadas en anio por fuerza: ({distrito: {fuerza: bancas}}, {fuerza: bancas})."""
    m, pad, ren = listas(anio), padron(anio), renuevan(anio)
    por, tot = {}, {}
    for d, g in m.groupby("distrito"):
        s = dhondt(dict(zip(g.lista + "|" + g.bloque, g.votos)), ren[d], UMBRAL * pad[d])
        fz = dict(zip(g.lista + "|" + g.bloque, g.fuerza))
        por[d] = {}
        for k, v in s.items():
            if v:
                por[d][fz[k]] = por[d].get(fz[k], 0) + v
                tot[fz[k]] = tot.get(fz[k], 0) + v
    return por, tot


ZIPF = 1.6        # perfil de las listas menores de un distrito: la k-esima saca ~ k^-ZIPF (ajuste de 2021; 2019 1,05)


def n_menores(anio, fuerzas):
    """{distrito: listas oficializadas fuera de las fuerzas proyectadas}. Solo se cuentan listas (se conocen antes de
    la eleccion), no se miran sus votos. Sin mapeo del año (2027 antes de oficializar), las de anio - 4."""
    for a in (anio, anio - 4):
        f = os.path.join(ROOT, "mapas", "mapa%s" % a, "mapeo_listas_%s.csv" % a)
        if os.path.exists(f):
            m = pd.read_csv(f, dtype=str, encoding="utf-8-sig")
            m["distrito"] = m.distrito.str.zfill(2)
            m["bloque"] = m.bloque.fillna(m.nombre)
            m = m[~m.bloque.map(lambda b: CORTO.get(b, b)).isin(fuerzas)]
            return m.groupby("distrito").bloque.nunique().to_dict()
    return {}


def repartir(votos_d, anio, pad):
    """votos_d = DataFrame distrito x fuerza (votos proyectados, con OTRAS). Devuelve ({distrito: {fuerza: bancas}},
    {fuerza: bancas}). OTRAS se parte entre las listas menores oficializadas del distrito con un perfil de Zipf: con
    las listas menores de la eleccion anterior (la regla de antes) OTRAS quedaba casi entera en una lista, porque en
    2023 casi no las hubo, y con los votos reales de 2025 daba 16 bancas provinciales en vez de 5."""
    ren = renuevan(anio)
    nm = n_menores(anio, {c for c in votos_d.columns if not c.startswith("PROV:")})
    por, tot = {}, {}
    for d in votos_d.index:
        v = {k: float(x) for k, x in votos_d.loc[d].items() if k != "OTRAS" and np.isfinite(x)}
        ot = float(votos_d.loc[d].get("OTRAS", 0) or 0)
        if ot > 0:
            n = nm.get(d, 4) - sum(1 for k, x in v.items() if k.startswith("PROV:") and x > 0)   # las de la tabla ya estan
            w = np.arange(1, max(n, 1) + 1, dtype=float) ** -ZIPF
            for i, s in enumerate(w / w.sum()):
                v["PROV|%d" % (i + 1)] = ot * s
        s = dhondt(v, ren[d], UMBRAL * pad[d])
        por[d] = {}
        for k, n in s.items():
            if n:
                f = "PROV" if k.startswith("PROV") else k
                por[d][f] = por[d].get(f, 0) + n
                tot[f] = tot.get(f, 0) + n
    return por, tot


# ---------------------------------------------------------------- partidos de los gobernadores (solo legislativas)
K_FOTOS = 3000.0     # votos de actas del distrito que pesan lo mismo que el prior
_RET = {}
TOMA_MAX = 0.5    # parte de la fuerza aliada que puede pasar al gobernador antes del reparto proporcional


def _tabla_prov():
    t = pd.read_csv(os.path.join(HERE, "provinciales.csv"), dtype={"distrito": str})
    t["distrito"] = t.distrito.str.zfill(2)
    return t


def retencion(anio):
    """Cuánto del voto a gobernador retiene su fuerza en la legislativa siguiente: promedio de (% legislativo / %
    gobernador) en las filas de provinciales.csv de años anteriores (calibración ex ante)."""
    t = _tabla_prov()
    r = []
    for _, x in t[t.anio < anio].iterrows():
        L = listas(int(x.anio))
        L = L[L.distrito == x.distrito]
        v = L[L.nombre.str.upper().str.contains(x.lista.upper(), regex=False, na=False)].votos.sum()
        r.append(100 * v / L.votos.sum() / x.pct_gob)
    return float(np.mean(r)), r


def provinciales(votos_d, anio, actas=None, rng=None):
    """Pone la fuerza del gobernador de cada distrito de provinciales.csv en su nivel esperado: retención × % que sacó
    el gobernador, mezclado con lo que muestran las actas de ese distrito (K_FOTOS votos de pseudoconteo). Una fuerza
    «PROV:<nombre>» sale de OTRAS como lista propia; si es una columna proyectada (PU), se corrige su nivel. El resto
    de las columnas se escala en proporción. La proyección presidencial no lo usa: con la boleta de presidente esos
    partidos casi no compiten. Con rng (remuestras del bootstrap) la retención de cada distrito se sortea con la
    dispersión relativa de la calibración, para que la banda cuente el error del prior. Devuelve (votos, notas)."""
    t = _tabla_prov()
    t = t[t.anio == anio]
    if not len(t):
        return votos_d, []
    if anio not in _RET:
        _RET[anio] = retencion(anio)
    k, r = _RET[anio]
    cv = np.std(r, ddof=1) / np.mean(r)
    V = votos_d.copy()
    notas = []
    for _, x in t.iterrows():
        d = x.distrito
        if d not in V.index:
            continue
        cols = [c for c in V.columns if c != "BN" and c != "ABSTENCION"]
        tot = V.loc[d, cols].sum()
        s = k * x.pct_gob / 100 * (np.exp(rng.normal(0, cv) - cv ** 2 / 2) if rng is not None else 1)
        fv = ft = 0.0
        if actas is not None:
            a = actas[(actas.distrito_id == d) & (actas.bloque != "BN")]
            ft = a.votos.sum()
            fv = (a[a.bloque == x.fuerza] if not x.fuerza.startswith("PROV:") else
                  a[a.lista.str.upper().str.contains(x.lista.upper(), regex=False, na=False)]).votos.sum()
        s = (s * K_FOTOS + fv) / (K_FOTOS + ft)
        if x.fuerza not in V.columns:
            V[x.fuerza] = 0.0
        c = V.loc[d, x.fuerza] / tot
        otras = [col for col in cols + ([x.fuerza] if x.fuerza not in cols else []) if col != x.fuerza]
        if x.fuerza.startswith("PROV:") and "OTRAS" in otras:   # la lista sale de OTRAS hasta donde alcance
            saca = min(V.loc[d, "OTRAS"], max(s - c, 0) * tot)
            V.loc[d, "OTRAS"] -= saca
            V.loc[d, x.fuerza] += saca
            c = V.loc[d, x.fuerza] / tot
        tom = x.get("toma_de")
        if isinstance(tom, str) and tom in V.columns and s * tot > V.loc[d, x.fuerza]:
            # gobernador aliado de esa fuerza en la eleccion anterior: hasta la mitad de lo que le falta sale de ella
            saca = min(V.loc[d, tom] * TOMA_MAX, s * tot - V.loc[d, x.fuerza])
            V.loc[d, tom] -= saca
            V.loc[d, x.fuerza] += saca
        resto = V.loc[d, otras].sum()
        if resto > 0:
            V.loc[d, otras] *= (1 - s) * tot / resto
        V.loc[d, x.fuerza] = s * tot
        notas.append("%s: %s %.0f %% (%s sacó %.1f %% en %d × retención %.2f%s)" % (
            DIST[d], x.fuerza.replace("PROV:", ""), 100 * s, x.gobernador, x.pct_gob, x.eleccion_gob, k,
            "; %d votos en actas" % ft if ft else ""))
    return V.fillna(0), notas


# ---------------------------------------------------------------- hemiciclo (disposición del generador de la Wikipedia)
_TOTALS = [3, 15, 33, 61, 95, 138, 189, 247, 313, 388, 469, 559, 657, 762, 876, 997, 1126, 1263, 1408, 1560]


def arco(n):
    """Centros (x, y) y radio de n bancas, como ArchDiagram del Parliament diagram tool (David Richfield):
    filas en arcos concéntricos, ordenadas por ángulo de izquierda a derecha. Coordenadas del SVG de la Wikipedia
    (360 x 185)."""
    rows = next(i + 1 for i, t in enumerate(_TOTALS) if t >= n)
    radius = 0.4 / rows
    pos = []
    for i in range(1, rows):
        J = int(float(n) / _TOTALS[rows - 1] * math.pi / (2 * math.asin(2.0 / (3.0 * rows + 4.0 * i - 2.0))))
        R = (3.0 * rows + 4.0 * i - 2.0) / (4.0 * rows)
        if J == 1:
            pos.append((math.pi / 2, 1.75, R))
        else:
            for j in range(J):
                a = j * (math.pi - 2 * math.sin(radius / R)) / (J - 1) + math.sin(radius / R)
                pos.append((a, R * math.cos(a) + 1.75, R * math.sin(a)))
    J = n - len(pos)
    R = (7.0 * rows - 2.0) / (4.0 * rows)
    if J == 1:
        pos.append((math.pi / 2, 1.75, R))
    else:
        for j in range(J):
            a = j * (math.pi - 2 * math.sin(radius / R)) / (J - 1) + math.sin(radius / R)
            pos.append((a, R * math.cos(a) + 1.75, R * math.sin(a)))
    pos.sort(reverse=True)
    return [(x * 100 + 5, 100 * (1.75 - y) + 5) for _, x, y in pos], radius * 100


def hemiciclo_svg(grupos, titulo="", mayoria=None):
    """grupos = [(código, bancas)] de izquierda a derecha. SVG con la leyenda debajo."""
    n = sum(b for _, b in grupos)
    pts, r = arco(n)
    cols = sum([[FUERZAS.get(g, (g, "#9e9e9e"))[1]] * b for g, b in grupos], [])
    L = []
    for (x, y), c in zip(pts, cols):
        L.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="#fff" stroke-width="%.2f"/>' % (
            x, y, r * 0.93, c, r * 0.12))
    L.append('<text x="180" y="175" font-size="34" font-weight="bold" text-anchor="middle" '
             'font-family="sans-serif">%d</text>' % n)
    if mayoria:
        L.append('<text x="180" y="186" font-size="8" text-anchor="middle" fill="#555" font-family="sans-serif">'
                 'mayoría: %d</text>' % mayoria)
    vis = [(g, b) for g, b in grupos if b > 0]
    fs, dy = (10.5, 16) if len(vis) <= 8 else (8.2, 12.5)        # muchos bloques: leyenda mas chica
    for i, (g, b) in enumerate(vis):
        fila, col = divmod(i, 2)
        x0, y0 = 8 + col * 178, 205 + fila * dy
        L.append('<rect x="%d" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (
            x0, y0 - fs * 0.85, fs, fs, FUERZAS.get(g, (g, "#9e9e9e"))[1]))
        L.append('<text x="%.1f" y="%.1f" font-size="%.1f" font-family="sans-serif">%s <tspan font-weight="bold">%d'
                 '</tspan></text>' % (x0 + fs * 1.5, y0, fs, FUERZAS.get(g, (g,))[0], b))
    h = 215 + dy * ((len(vis) + 1) // 2)
    t = ('<text x="180" y="-6" font-size="12" font-weight="bold" text-anchor="middle" font-family="sans-serif">%s'
         '</text>' % titulo) if titulo else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 %d 360 %.0f" width="540">%s%s</svg>'
            % (-20 if titulo else 0, h + (20 if titulo else 0), t, "".join(L)))


def ordenar(tot):
    """{fuerza: bancas} -> [(fuerza, bancas)] en ORDEN; lo que no esta en FUERZAS va a PROV."""
    agg = {}
    for f, b in tot.items():
        k = f if f in FUERZAS else "PROV"
        agg[k] = agg.get(k, 0) + b
    return [(f, agg[f]) for f in ORDEN if agg.get(f)]


# ---------------------------------------------------------------- mapa por provincia
def _provincias():
    """Contornos de provincia (los del mini «Provincias» del atlas de 2025), en caché en provincias_svg.json."""
    f = os.path.join(HERE, "provincias_svg.json")
    if not os.path.exists(f):
        h = open(os.path.join(ROOT, "mapas", "mapa2025", "atlas_2025.html"), encoding="utf8").read()
        p = dict(re.findall(r'<path class="pf" data-prov="([^"]+)" d="([^"]+)"', h))
        json.dump(p, open(f, "w", encoding="utf8"), ensure_ascii=False)
    return json.load(open(f, encoding="utf8"))


def _bbox(d):
    v = np.array(re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", d), float)
    return v[:, 0].min(), v[:, 1].min(), v[:, 0].max(), v[:, 1].max()


def mapa_svg(ganador, detalle):
    """ganador = {distrito: fuerza}; detalle = {distrito: texto del tooltip}. Capital Federal ampliada en un recuadro."""
    P = _provincias()
    inv = {v: k for k, v in DIST.items()}
    bb = np.array([_bbox(d) for p, d in P.items() if p in inv])
    x0, y0, x1, y1 = bb[:, 0].min(), bb[:, 1].min(), bb[:, 2].max(), bb[:, 3].max()
    L = []
    for p, d in P.items():
        if p not in inv:
            continue
        c = FUERZAS.get(ganador.get(inv[p]), ("", "#e8e0c8"))[1]
        L.append('<path d="%s" fill="%s" stroke="#fff" stroke-width="1.6"><title>%s</title></path>' % (
            d, c, detalle.get(inv[p], p)))
    cb = _bbox(P["Capital Federal"])
    s, cx, cy = 9.0, (cb[0] + cb[2]) / 2, (cb[1] + cb[3]) / 2
    ix, iy = x1 - 40, y0 + 690                                 # recuadro de Capital, frente a la costa
    c = FUERZAS.get(ganador.get("01"), ("", "#e8e0c8"))[1]
    L.append('<rect x="%.1f" y="%.1f" width="120" height="120" fill="#fff" stroke="#888"/>' % (ix - 60, iy - 60))
    L.append('<path d="%s" fill="%s" stroke="#fff" transform="translate(%.1f %.1f) scale(%.1f) translate(%.1f %.1f)">'
             '<title>%s</title></path>' % (P["Capital Federal"], c, ix, iy, s, -cx, -cy, detalle.get("01", "")))
    L.append('<text x="%.1f" y="%.1f" font-size="15" text-anchor="middle" font-family="sans-serif">Capital Federal</text>'
             % (ix, iy + 78))
    L.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#888"/>' % (cx, cy, ix - 60, iy))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.0f %.0f %.0f %.0f" width="380">%s</svg>'
            % (x0 - 10, y0 - 10, x1 - x0 + 90, y1 - y0 + 20, "".join(L)))


# ---------------------------------------------------------------- bancas que no se renuevan, por bloque de la cámara
# Composición por bloque legislativo antes de la asunción (10 de diciembre): tabla «Bancas por bloque» del artículo de
# la elección (columnas Totales y A renovar). 2025: revisión 170886514 del 9-dic-2025 (la última antes del 10-dic),
# guardada en datos/wikileg/revisiones/. Las que no se renuevan = Totales - A renovar.
REVISION = {2025: os.path.join(ROOT, "datos", "wikileg", "revisiones", "wleg2025_rev170886514.txt")}
_COLOR_WIKI = {"Unión por la Patria": "#009ce4", "La Libertad Avanza": "#6c4c98", "Propuesta Republicana": "#f4ce00",
               "Unión Cívica Radical": "#e10019", "red": "#b71c1c"}
_CODIGO = {"Fuerza Patria": "FP", "La Libertad Avanza": "LLA", "FIT-Unidad": "FIT", "Provincias Unidas": "PU"}
# de izquierda a derecha en el hemiciclo (los bloques que no estan aca van antes de Provincias Unidas)
ORDEN_CAMARA = ["FIT", "FP", "UxP", "Por Santa Cruz", "Independencia", "Producción y Trabajo", "Somos Fueguinos",
                "Unidos", "Defendamos Santa Fe", "PROV", "Innovación Federal", "Movimiento Popular Neuquino",
                "CREO", "Liga del Interior - ELI", "Encuentro Federal", "HxNP", "Defendamos Córdoba",
                "Democracia Para Siempre", "Unión Cívica Radical", "Coalición Cívica", "PU", "JxC",
                "Republicanos Unidos", "PRO", "Movimiento de Integración y Desarrollo", "Futuro y Libertad",
                "Coherencia", "LLA"]


def bloques_camara(anio):
    """{bloque: (bancas totales, a renovar, color)} de la tabla «Bancas por bloque» de la revision guardada."""
    t = open(REVISION[anio], encoding="utf8").read()
    i = t.index("=== Bancas por bloque")
    tb = t[i:t.index("\n|}", i)]
    out = {}
    for b in tb.split("\n|-"):
        n = re.search(r'align="left"\s*\|\s*(.+)', b)
        s = re.findall(r"escaños\|hex=(?:\{\{Color político\|[^}]*\}\}|[^|]*)\|(\d+)\|(\d+)", b.replace("\n", ""))
        c = re.search(r'(?:bgcolor=|background-color:)"?(?:\{\{Color político\|([^}]*)\}\}|(#?\w+))', b)
        if n and len(s) >= 2:
            nm = re.sub(r"<ref.*", "", n.group(1))
            nm = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", nm).strip()
            col = c.group(1) or c.group(2) if c else "#9e9e9e"
            out[nm] = (int(s[0][0]), int(s[1][0]), _COLOR_WIKI.get(col, col))
    assert sum(v[0] for v in out.values()) == 257
    return out


def no_renuevan(anio):
    """{clave: bancas} de las que siguen en la camara despues de la eleccion de anio. Con la revision de la Wikipedia
    del año (bloques de la camara antes de la asuncion) usa Totales - A renovar; sin ella, las ganadas en anio - 2.
    Registra en FUERZAS el nombre y el color de cada bloque nuevo."""
    if anio in REVISION:
        out = {}
        for nm, (t, r, col) in bloques_camara(anio).items():
            k = _CODIGO.get(nm, nm)
            if k not in FUERZAS:
                FUERZAS[k] = (nm, col)
            if t - r:
                out[k] = t - r
        assert sum(out.values()) == 257 - sum(renuevan(anio).values())
        return out
    return electos(anio - 2)[1]


def ordenar_camara(tot):
    """{clave: bancas} -> [(clave, bancas)] de izquierda a derecha."""
    pos = {k: i for i, k in enumerate(ORDEN_CAMARA)}
    return sorted([(k, b) for k, b in tot.items() if b], key=lambda kb: pos.get(kb[0], pos["PU"] - 0.5))
