"""Atlas de la serie AMBA 2005–2023. Derivado del constructor por radio de 2003.
Uso: python mapas/serieAMBA2005_2023radios/render.py 2023pres
"""
import sys, os, re, json, math, collections, base64, io, pickle, unicodedata
import numpy as np, shapely
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon, shape

from serie import KEYS, radios, norm
KEY = sys.argv[1]
assert KEY in KEYS
VAR = 'idw'
SUF = ''
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CIRC = os.path.join(ROOT, "mapaAMBA2025")
LOGOS = os.path.join(ROOT, "../logos")
TEMPLATE_SRC = os.path.join(ROOT, "../.claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "template.html")

# ---------------------------------------------------------------- proyección (la del atlas AMBA 2025)
KX = math.cos(math.radians(34.7))
LON0, LAT1 = -59.3775, -33.9233
S, X0, Y0 = 975.0, 548.0, 140.0


def proj(a):
    a = np.asarray(a, float).copy()
    a[:, 0] = (a[:, 0] - LON0) * KX * S + X0
    a[:, 1] = (LAT1 - a[:, 1]) * S + Y0
    return a


def ll(lon, lat): return ((lon - LON0) * KX * S + X0, (LAT1 - lat) * S + Y0)
def f2(x): return ("%.2f" % x).rstrip("0").rstrip(".")


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
        if len(pts) < 2: continue
        out.append("M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts))
    return "".join(out)


def fill_slivers(g, amax=6.0):
    gs = [q for q in (g.geoms if hasattr(g, "geoms") else [g]) if q.geom_type == "Polygon"]
    out = [Polygon(q.exterior, [i for i in q.interiors if Polygon(i).area >= amax]) for q in gs]
    return out[0] if len(out) == 1 else MultiPolygon(out)


def proj_geom(g):
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type != "Polygon": continue
        out.append(Polygon(proj(np.array(p.exterior.coords)), [proj(np.array(i.coords)) for i in p.interiors]))
    g2 = shapely.make_valid(MultiPolygon(out)) if out else Polygon()
    if g2.geom_type == "GeometryCollection":
        ps = [q for q in g2.geoms if q.geom_type in ("Polygon", "MultiPolygon")]
        g2 = unary_union(ps) if ps else Polygon()
    return g2


def ascii_t(s): return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()


# ---------------------------------------------------------------- datos: reparto por radio (asignar.py)
AS = pickle.load(open(os.path.join(HERE, "asignacion_%s.pkl" % KEY), "rb"))
YEAR, CENSO = AS['year'], AS['censo']
ISDIP = KEY.endswith('dip')
ISBAL = KEY.endswith('bal')
ISPASO = 'paso' in KEY
PASCAND = KEY.endswith('pasocand')
TITLE = 'Diputados nacionales' if ISDIP else 'Balotaje presidencial' if ISBAL else 'Elecciones presidenciales'
if ISPASO:TITLE='PASO presidenciales'
A, CATS, rp = AS["A"], AS["CATS"], AS["radios"]
ci = {c: i for i, c in enumerate(CATS)}
PCATS = [c for c in CATS if not c.startswith("_")]
CAND_SOURCE = AS['candidates']
NAMES = {c:(CAND_SOURCE[c]['n'],CAND_SOURCE[c].get('sub','')) for c in PCATS}
LAB = {c: ' · '.join(x for x in NAMES[c] if x) for c in PCATS}
BLOCS = PCATS
COLOR = {c:CAND_SOURCE[c]['base'] for c in BLOCS}
DEFAULT_COL = "#9a9a9a"
GREY_N = "#8c8c8c"; BEIGE = "#e6dcc3"


def fmt_n(v): return "{:,}".format(int(round(v))).replace(",", ".")
def fmt_p(v): return ("%.1f" % v).replace(".", ",")


def agg_rows(rows):
    v = A[rows].sum(0) if len(np.shape(rows)) else A[rows]
    return agg_vector(v)


def agg_vector(v):
    P = {c: float(v[ci[c]]) for c in PCATS if v[ci[c]] > 0}
    g = lambda c: float(v[ci[c]]) if c in ci else 0.0
    pos = sum(P.values())
    a = dict(P=P, pos=pos, bla=g("_BLA"), nul=g("_NUL"), imp=g('_IMP'), mesas=g("_MES"), ok=g("_MOK"), el=g("_ELOK"), elok=g("_ELOK"))
    a["bloc"] = {b: P.get(b, 0) for b in BLOCS}
    a["E"] = pos + a["bla"] + a["nul"] + a['imp']
    return a


def rec_from(a, pob=None, note=None, unit=True):
    D = a["pos"]
    if D < 0.5:
        met = [["Población %s" % CENSO, fmt_n(pob)]] if pob is not None else []
        return dict(lines=[], metrics=met, fill=BEIGE, note=(note + " " if note else "") + "Sin votos asignados por el método.")
    P = a["P"]
    limit=len(PCATS) if ISPASO else 8 if unit else 14
    lines = [["P_" + c, round(x,2) if ISPASO and x<1 else int(round(x)), round(100 * x / D, 2 if ISPASO else 1)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x > 0 and (ISPASO or x>=.5)][:limit]
    E = a["E"]
    if a["bla"] >= 0.5: lines.append(["P_BLA", int(round(a["bla"])), round(100 * a["bla"] / E, 2)])
    if a["nul"] >= 0.5: lines.append(["P_NUL", int(round(a["nul"])), round(100 * a["nul"] / E, 2)])
    met = []
    if a['imp'] >= .5: lines.append(['P_IMP', int(round(a['imp'])), round(100*a['imp']/E,2)])
    if pob is not None: met.append(["Población %s" % CENSO, fmt_n(pob)])
    est = " (estimados)" if unit else ""
    if a["elok"]: met.append(["Electores" + est, fmt_n(a["elok"])])
    met.append(["Votantes" + est, fmt_n(E)])
    if a["elok"] and E <= a['elok'] + 1e-6:
        met.append(["Participación estimada" if unit and YEAR==2013 else "Participación", fmt_p(100 * E / a["elok"]) + " %"])
    elif a['elok'] and E > a['elok'] + 1e-6:
        note=(note+' ' if note else '')+'Participación no calculable: los electores de la fuente son inferiores a los votos asignados.'
    met.append(["Votos positivos" + est, fmt_n(D)])
    if not unit and a['mesas']: met.append(["Mesas con votos", "%s de %s" % (fmt_n(a["ok"]), fmt_n(a["mesas"]))])
    rec = {"lines": lines, "metrics": met}
    top = max(P, key=lambda c: P[c])
    tied = sum(abs(v-P[top])<1e-8 for v in P.values())>1
    if tied: rec.update(fill=GREY_N)
    elif top in BLOCS: rec.update(w=top, q=round(100 * P[top] / D, 2))
    else: rec.update(fill=COLOR.get(top, GREY_N))
    if note: rec["note"] = note
    return rec


# ---------------------------------------------------------------- unidades = radios 2001
R, _, _ = radios(CENSO)
assert [f["properties"]["COD"] for f in R] == list(rp.COD)
UKEYS = [("01" if f["properties"]["PROV"] == "02" else "02", f["properties"]["COD"]) for f in R]
PART = ["Ciudad de Buenos Aires" if p == "02" else ascii_t(n) for p, n in zip(rp.PROV, rp.partido)]
CIRCUNS = AS["circuns"]
POBR = rp.POB.fillna(0).to_numpy(float)
G_raw = [proj_geom(shape(f["geometry"])) for f in R]
try:
    G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.04))
except Exception as e:
    print("coverage_simplify falló (%s): simplify por polígono" % e, file=sys.stderr)
    G = [g.simplify(0.04, preserve_topology=True) for g in G_raw]
disp, unit_an, unit_rec = {}, {}, {}
for i, k in enumerate(UKEYS):
    a = agg_rows(i); unit_an[i] = a
    c = k[1]
    disp[i] = "Radio %s-%s-%s" % (c[2:5], c[5:7], c[7:9]) + (" · %s" % CIRCUNS[rp.unit[i][1]] if k[0] == "01" else "")
    pending = AS['ctrl']['missing_list_pba'] and k[0]=='02'
    note = 'Pendiente: falta Nuevo Encuentro por mesa/circuito en PolAr 2009. No se reparten los totales municipales.' if pending else 'Estimación por radio censal; no es un resultado observado.'
    if list(rp.unit[i]) in AS['ctrl'].get('unidades_pendientes',[]):
        note='Pendiente: al menos un circuito del partido no tiene correspondencia geográfica verificable. Se conserva el resultado en el total regional.'
    unit_rec[i] = rec_from(a, POBR[i], note)
    excluded_NE = AS['ctrl'].get('NE_estimado_municipal',False) and a['P'] and max(a['P'],key=a['P'].get)=='NE'
    if excluded_NE:
        unit_rec[i].pop('w',None);unit_rec[i].pop('q',None)
        unit_rec[i].update(fill=BEIGE,note='Excluido por pedido del usuario: NE resulta primero en esta estimación. NE se distribuye con la misma proporción municipal de positivos; no se conocen sus votos por circuito o radio.')
    a["ok"] = 1 if a["pos"] >= 0.5 and not excluded_NE else 0
# ---------------------------------------------------------------- niveles «Partido» y «Circuito» (selector de nivel)
# Las unidades extra van después de los radios (mismo índice data-i en el SVG y en los modos): partidos y comunas
# o circunscripciones de Capital como suma exacta de sus radios; circuitos con los votos observados de la fuente.
NR = len(UKEYS)
EXTRA_V = []   # votos (columnas de A) de cada unidad extra: los usa internas2023.py
EXTRA = []   # (kind, nombre, geometría proyectada, es_capital)
_units = list(rp.unit)
UNIT_IDX = collections.defaultdict(list)
for i, u in enumerate(_units): UNIT_IDX[tuple(u)].append(i)
UNIT_GEOM = {u: unary_union([G_raw[i] for i in ix]) for u, ix in UNIT_IDX.items()}
for u in sorted(UNIT_IDX, key=lambda u: (u[0], PART[UNIT_IDX[u][0]] if u[0] == '02' else CIRCUNS.get(u[1], u[1]))):
    ix = np.array(UNIT_IDX[u])
    capital = u[0] == '01'
    name = ('Comuna %d' % int(u[1]) if YEAR >= 2009 else CIRCUNS.get(u[1], u[1])) if capital else rp.partido[ix[0]]
    a = agg_rows(ix)
    rec = rec_from(a, float(POBR[ix].sum()), 'Suma de las estimaciones por radio: coincide con el total de la fuente.')
    if AS['ctrl'].get('NE_estimado_municipal') and a['P'] and max(a['P'], key=a['P'].get) == 'NE':
        rec.pop('w', None); rec.pop('q', None)
        rec.update(fill=BEIGE, note='Excluido por pedido del usuario: NE resulta primero; NE solo tiene total municipal.')
        a['ok'] = 0
    else: a['ok'] = 1 if a['pos'] >= 0.5 else 0
    j = NR + len(EXTRA)
    unit_an[j] = a; unit_rec[j] = rec; disp[j] = name
    g = fill_slivers(UNIT_GEOM[u].buffer(0.7, join_style=2).buffer(-0.7, join_style=2))
    EXTRA.append(('partido', name, g, capital, PART[ix[0]])); EXTRA_V.append(A[ix].sum(0))
_cf = os.path.join(HERE, 'circuitos_%s.pkl' % KEY)
CAPA_CIRC = pickle.load(open(_cf, 'rb')) if os.path.exists(_cf) else None
if CAPA_CIRC is not None:
    _cats = list(AS['CATS']); CIRC_PEND = []
    for k, wkb in sorted(CAPA_CIRC['geom'].items()):
        u = tuple(CAPA_CIRC['unit'][k])
        if u not in UNIT_GEOM: continue
        v = CAPA_CIRC['V'].loc[k].reindex(_cats, fill_value=0).to_numpy(float)
        a = agg_vector(v)
        capital = k[0] == '01'
        sec = CAPA_CIRC['seccion'].get(k, k[1])
        name = 'Circuito %s · %s' % (k[2], ('Comuna %d' % int(u[1]) if YEAR >= 2009 else CIRCUNS.get(u[1], sec)) if capital else sec)
        if YEAR == 2009 and AS['ctrl'].get('NE_estimado_municipal') and not capital:
            rec = dict(lines=[], metrics=[], fill=BEIGE, note='NE no tiene votos por circuito en 2009 (solo totales municipales): '
                       'sin el resultado completo, el circuito no se colorea. Ver el nivel Partido.')
            a['ok'] = 0
        else:
            rec = rec_from(a, None, 'Resultado observado del circuito (%s); no es una estimación.' % AS['ctrl'].get('source_kind', 'fuente'))
            a['ok'] = 1 if a['pos'] >= 0.5 else 0
        g = proj_geom(shapely.from_wkb(wkb))
        try: g = g.intersection(UNIT_GEOM[u])
        except Exception: g = shapely.make_valid(g).intersection(UNIT_GEOM[u])
        if g.is_empty: continue
        CIRC_PEND.append((u, a, rec, name, g, capital, v))
    # La cartografía de circuitos no cubre todo el recorte (islas del Delta, rurales). Las rendijas chicas
    # (<1 % del partido) se suman al circuito vecino más cercano; el resto queda beige y rotulado: no se
    # adjudica territorio a un circuito sin saber a cuál pertenece.
    _sin_pol = collections.Counter(('01', k[1]) if k[0] == '01' else ('02', norm(CAPA_CIRC['seccion'].get(tuple(k), ''))) for k in CAPA_CIRC['missing'])
    for u in sorted({c[0] for c in CIRC_PEND}):
        mine = [c for c in CIRC_PEND if c[0] == u]
        gap = UNIT_GEOM[u].difference(unary_union([c[4] for c in mine]))
        resto = []
        for piece in getattr(gap, 'geoms', [gap]):
            if piece.is_empty or piece.area <= 0: continue
            if piece.area < 0.01 * UNIT_GEOM[u].area:
                n = min(range(len(mine)), key=lambda t: mine[t][4].distance(piece))
                mine[n] = mine[n][:4] + (mine[n][4].union(piece),) + mine[n][5:]
            else: resto.append(piece)
        for (u_, a, rec, name, g, capital, v) in mine:
            j = NR + len(EXTRA)
            unit_an[j] = a; unit_rec[j] = rec; disp[j] = name
            EXTRA.append(('circuito', name, g, capital, PART[UNIT_IDX[u][0]])); EXTRA_V.append(v)
        if resto:
            j = NR + len(EXTRA)
            sec = ('Comuna %d' % int(u[1]) if YEAR >= 2009 else CIRCUNS.get(u[1], u[1])) if u[0] == '01' else rp.partido[UNIT_IDX[u][0]]
            unit_an[j] = dict(agg_vector(np.zeros(len(AS['CATS']))), ok=0)
            unit_rec[j] = dict(lines=[], metrics=[], fill=BEIGE, note=(
                'Sin polígono de circuito en la cartografía' + (' (la fuente trae %d circuito(s) de este partido sin polígono)' % _sin_pol[u] if _sin_pol[u] else '') +
                ': el área no se adjudica a ningún circuito. Ver el nivel Radio.'))
            disp[j] = 'Área sin circuito · ' + sec
            EXTRA.append(('circuito', disp[j], unary_union(resto), u[0] == '01', PART[UNIT_IDX[u][0]])); EXTRA_V.append(np.zeros(A.shape[1]))
NU = NR + len(EXTRA)
pickle.dump(dict(V=np.array(EXTRA_V, float).reshape(len(EXTRA_V), A.shape[1]), kind=[e[0] for e in EXTRA]),
            open(os.path.join(HERE, 'niveles_%s.pkl' % KEY), 'wb'))

# circuitos del recorte que la fuente trae en cero (p. ej. el Delta de San Fernando y dos rurales de Cañuelas en el
# provisorio del balotaje 2023): sus radios quedan beige y la ficha y la clave dicen por qué, sin imputar votos.
# Solo cuentan los circuitos con votos en otra elección del mismo año: los que no votan nunca (La Plata 493) no
# explican nada y sus radios conservan la nota genérica.
SIN_MESAS = collections.defaultdict(list); NOMBRE_SEC = {}
def _circ_votos(rel):
    f = os.path.join(HERE, "..", "..", rel)
    if not (rel.endswith('.pkl') and os.path.exists(f)): return None
    d = pickle.load(open(f, 'rb'))[0]
    d = d.assign(sk=d.distrito_id + '_' + d.seccion_id.astype(str).str.zfill(3))
    return d.groupby(['sk', 'circuito']).v.sum()
_aqui = _circ_votos(AS['ctrl'].get('source', ''))
if _aqui is not None:
    _otras = set()
    for _k in KEYS:
        _cf = os.path.join(HERE, 'control_%s.json' % _k)
        if _k != KEY and _k[:4] == KEY[:4] and os.path.exists(_cf):
            _s = json.load(open(_cf, encoding='utf-8')).get('source', '')
            if _s and _s != AS['ctrl'].get('source'):
                _v = _circ_votos(_s)
                if _v is not None: _otras |= set(_v[_v > 0].index)
    _sec = AS['ctrl'].get('sections', {})
    for (sk, circ), v in _aqui.items():
        if v == 0 and sk.startswith('02') and sk in _sec and (sk, circ) in _otras: SIN_MESAS[norm(_sec[sk])].append(circ); NOMBRE_SEC[norm(_sec[sk])] = _sec[sk]
for i, r in unit_rec.items():
    if i >= NR: continue
    p = rp.unit[i][1]
    if r.get('fill') == BEIGE and not r.get('w') and SIN_MESAS.get(p):
        r['note'] = ('Sin votos asignados: la fuente (%s) no trae votos %s %s de %s; no se imputan.'
                     % (AS['ctrl'].get('source_kind', 'fuente'), 'de los circuitos' if len(SIN_MESAS[p]) > 1 else 'del circuito',
                        ', '.join(sorted(SIN_MESAS[p])), NOMBRE_SEC[p]))
TOT = agg_vector(AS['total_vector']) if 'total_vector' in AS else agg_rows(np.arange(len(UKEYS)))
PARTIDOS = sorted(set(PART))
part_an = {p: agg_rows(np.array([i for i in range(len(UKEYS)) if PART[i] == p])) for p in PARTIDOS}
from serie import norm
for p in PARTIDOS:
    pk='Ciudad de Buenos Aires' if p=='Ciudad de Buenos Aires' else norm(p)
    if pk in AS.get('part_totals',{}):part_an[p]=agg_vector(AS['part_totals'][pk])
prov_rec = {p: rec_from(a, None, "Suma de estimaciones; totales conservados de la fuente en las unidades cubiertas.", unit=False) for p, a in part_an.items()}
WIN = collections.Counter(unit_rec[i].get("w") for i in range(NR) if unit_rec[i].get("w"))
print(VAR, "radios:", len(UKEYS), "ganadores:", dict(WIN), "beige:", sum(1 for i in range(NR) if unit_rec[i].get("fill") == BEIGE), "partidos y circuitos:", collections.Counter(e[0] for e in EXTRA),
      "AMBA positivos", round(TOT["pos"]), {b: round(100 * TOT["bloc"][b] / TOT["pos"], 2) for b in sorted(BLOCS,key=lambda b:-TOT['bloc'][b])[:6]}, file=sys.stderr)
LEG = [b for b in BLOCS if WIN.get(b)]   # regla 3: solo los que ganan algún radio

# ---------------------------------------------------------------- candidaturas del atlas de cada año; emblemas ya documentados
CAND = {b:dict(CAND_SOURCE[b]) for b in BLOCS}


# rampas propias de los 7 tonos del modo «Ganó» (parche a shade() en la cola): con el .25 de la plantilla los oscuros de Menem y
# Kirchner terminaban en el mismo azul marino. Kirchner se queda en celestes y azul acero; los demás se oscurecen hasta .55.
def _hx(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def _rgb(c): return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)
def _mixw(h, t): return _rgb([c + (255 - c) * t for c in _hx(h)])
def _mulc(h, k): return _rgb([c * k for c in _hx(h)])


def fr2013_ramp(n):
    # Gris acero a casi negro: separar tonos sin volver pastel el mapa del FR.
    light, dark = np.array([139, 147, 155]), np.array([7, 15, 23])
    return [_rgb(light + (dark - light) * t) for t in np.linspace(0, 1, n)]


import colorsys
def _warm(h):
    H, L, S = colorsys.rgb_to_hls(*[c / 255 for c in _hx(h)]); return 38 < H * 360 < 68 and S > .5
def _amber(h, k):
    # Como leyenda_clara.js de los atlas legislativos: los amarillos se oscurecen hacia el ámbar, no hacia el oliva.
    H, L, S = colorsys.rgb_to_hls(*[c / 255 for c in _hx(h)])
    return _rgb([v * 255 for v in colorsys.hls_to_rgb(((H * 360 - (1 - k) * 24) % 360) / 360, L * (.3 + .7 * k), S)])
for b in BLOCS:
    dark = _amber if _warm(COLOR[b]) else _mulc
    CAND[b]["ramp"] = [_mixw(COLOR[b], .15), COLOR[b]] + [dark(COLOR[b], k) for k in (.9, .8, .7, .62, .55)]
    # Barra con el color del partido, como las legislativas 2003-2025 (pedido del usuario: Cambiemos amarillo, no oliva).
    CAND[b].pop("bar", None)
    if _warm(COLOR[b]): CAND[b]["txt"] = _amber(COLOR[b], .55)
    if CAND[b].get("n") == "Unidos por una Nueva Alternativa": CAND[b]["n"] = "UNA"   # pedido del usuario
if KEY == '2013dip':
    CAND['FR']['ramp'] = fr2013_ramp(7)
CAND["OTR"] = dict(n="Otros", sub="Resto de las candidaturas", base="#b3b3b3", bar="#a6a6a6", txt="#8f8f8f", logo="···")
for c in PCATS:
    CAND["P_" + c] = dict(n=LAB[c], base=COLOR.get(c, DEFAULT_COL), minor=True)
CAND["P_BLA"] = dict(n="En blanco", base="#c9c9c9", minor=True)
CAND["P_NUL"] = dict(n="Nulos", base="#b0b0b0", minor=True)
CAND['P_IMP'] = dict(n='Recurridos, impugnados y comando',base='#aaa',minor=True)


def _logo_raster(fn, h=50):
    from PIL import Image
    im = Image.open(fn).convert("RGBA")
    # el recorte del mapa de la Wikipedia arrastra a veces el comienzo del nombre (MNP: una «A» y una «F» a la derecha):
    # se corta en el primer hueco transparente de 10 columnas o más después del emblema
    col = (np.array(im)[..., 3] > 40).any(0)
    xs = np.flatnonzero(col)
    if len(xs):
        gaps = np.flatnonzero(np.diff(xs) >= 10)
        if len(gaps): im = im.crop((0, 0, int(xs[gaps[0]]) + 3, im.height))
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    ar = im.width / im.height
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))



PRES_LOGOS = {
    2007: dict(FPV='fpv07',CC='cc',UNA='una07',RECR='recrear'),
    2011: dict(FPV='fpv11',FAP='fap',UDESO='udeso',CF='cf11',FP='fp11',CC='cc'),
    2015: dict(FPV='fpv15',CAM='cambiemos',UNA='una15',CF='cf15'),
    2019: dict(FDT='fdt',JXC='sisepuede',CF='consenso'),
    2023: dict(UP='up',LLA='lla',JXC='jxc23',HXNP='hacemos'),
}
LOGO_INFO=[]
if not ISDIP and not ISPASO:
    from PIL import Image
    for code,block in PRES_LOGOS[YEAR].items():
        if code not in CAND:continue
        fn=os.path.join(LOGOS,'bloques_presidenciales',block+'.png')
        im=Image.open(fn).convert('RGBA')
        # Mantener el bloque tal como fue extraído del mapa de Wikipedia.
        b=io.BytesIO();im.save(b,'PNG',optimize=True)
        ar=im.width/im.height
        CAND[code].update(img='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode(),
                          ar=ar,bl=round(min(1.1,98/(ar*50)),3),blk=block)
        LOGO_INFO.append(dict(codigo=code,archivo='logos/bloques_presidenciales/'+block+'.png',
                              fuente='Mapa presidencial de Wikipedia / Commons, N2051, CC0; registro previo del proyecto'))
    json.dump(LOGO_INFO,open(os.path.join(HERE,'logos_presidenciales_'+KEY+'.json'),'w',encoding='utf8'),ensure_ascii=False,indent=2)


from logos_serie import corregir
LOGOS_CORREGIDOS = corregir(CAND)
json.dump(LOGOS_CORREGIDOS, open(os.path.join(HERE, 'logos_ajustados_'+KEY+'.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- resultado de la región
pos = round(TOT["pos"])
cands = sorted([{"code": b, "votes": int(round(TOT["bloc"][b])), "pct": round(100 * TOT["bloc"][b] / pos, 2)} for b in LEG], key=lambda c: -c["votes"])
otros = pos - sum(c["votes"] for c in cands)
slices = [{"code": c["code"], "v": c["votes"]} for c in cands]
if 100 * otros / pos >= 0.005:   # en los balotajes no queda resto (a lo sumo el redondeo): sin fila «Otros 0,00 %»
    cands.append({"code": "OTR", "votes": int(otros), "pct": round(100 * otros / pos, 2)})
    slices.append({"fill": "#717274", "v": int(otros)})
partp = round(100 * TOT["E"] / TOT["elok"], 2)
NAT_MET = [["Electores (mesas con votos)", fmt_n(TOT["elok"])], ["Votantes", fmt_n(TOT["E"])], ["Participación", fmt_p(partp) + " %"],
           ["Votos positivos", fmt_n(pos)], ["Votos en blanco", fmt_n(TOT["bla"])], ["Votos nulos", fmt_n(TOT["nul"])],
           ["Radios censales %s" % CENSO, fmt_n(len(UKEYS))]]
if AS['ctrl']['missing_list_pba']:
    NAT_MET.append(['Cobertura electoral','Solo Capital; 40 partidos pendientes'])
if AS['ctrl'].get('NE_estimado_municipal'):
    NAT_MET.append(['Radios excluidos: NE estimado',fmt_n(AS['ctrl']['radios_excluidos_NE'])])


# ---------------------------------------------------------------- modos
def mix(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(255 + (c[k] - 255) * t) for k in range(3))


def dark(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(c[k] * (1 - t)) for k in range(3))


def stops_for(base, edges):
    # de casi blanco al color del candidato y de ahí más oscuro: los colores de 2003 son claros y la rampa hasta el color quedaba pálida
    n = len(edges); h = n // 2
    cols = [mix(base, 0.12 + 0.88 * i / h) for i in range(h)] + [dark(base, 0.55 * j / (n - 1 - h)) for j in range(n - h)]
    lab = ["%g%%" % e for e in edges[:-1]] + ["+%g%%" % edges[-1]]
    return cols, lab


def bin_of(p, edges):
    i = 0
    while i + 1 < len(edges) and p >= edges[i + 1]: i += 1
    return i


C = AS["ctrl"]
NOTE = (f"Fuente: {C['source_kind']}, {YEAR}. Estimación por radio: resultados por circuito repartidos entre escuelas de 2025 "
        f"según sus electores de 2025, y desde cada escuela por 1/distancia² dentro del partido o "
        f"{'circunscripción' if YEAR<2009 else 'comuna'} en Capital. {C['circuitos_sin_escuela']} circuitos sin escuela usan su punto interior. "
        f"Radios CONICET, censo {CENSO}. Cartografía de circuitos aproximada, sin certificación de vigencia histórica. "
        "El voto no se registra por radio. Los totales cubiertos se conservan antes del redondeo; los porcentajes son sobre positivos. "
        + ('Buenos Aires pendiente: falta Nuevo Encuentro por circuito; torta y barras corresponden solo a Capital. ' if C['missing_list_pba'] else '')
        + (f"{len(C['unidades_pendientes'])} partidos pendientes en el mapa por circuitos sin correspondencia; sus votos integran el total regional. " if C.get('unidades_pendientes') else '')
        + (f"{len(C.get('circuitos_sin_poligono_con_escuela2025',[]))} circuitos sin polígono usan escuelas de 2025 con el mismo código y partido. " if C.get('circuitos_sin_poligono_con_escuela2025') else ''))
if YEAR==2015:
    NOTE=(f"Fuente: DINE, escrutinio provisorio {YEAR}. Estimación por radio con peso 1/distancia², restringida al partido o comuna. "
          f"{C['locales_2015_usados']} locales del archivo de La Nación cotejados con los rangos de mesas, positivos, blancos, nulos y electores de la general 2015 "
          f"cubren el {100*C['proporcion_votos_con_local_2015']:.1f}% de los votos de esta elección. El resto usa escuelas y pesos de electores de 2025 dentro de cada circuito. "
          + ('Para el balotaje se verificó también que los rangos empalmen con sus circuitos. ' if ISBAL else '')
          + f"Radios CONICET, censo {CENSO}. Cartografía de circuitos aproximada. El voto no se registra por radio. "
          "Totales por partido y comuna conservados antes del redondeo. Porcentajes sobre votos positivos.")
if YEAR==2009 and C.get('NE_estimado_municipal'):
    NOTE=("Estimación 2009: Capital conserva PolAr. En Buenos Aires, las listas con detalle mantienen su perfil por circuito, "
          "ajustado a los totales municipales completos del atlas 2009. NE no tiene detalle por circuito: se le asigna la misma proporción "
          "sobre positivos a todos los radios de cada municipio. No se infiere una variación interna de NE que la fuente no informa. "
          f"{C['radios_excluidos_NE']} radios donde NE resulta primero quedan beige y excluidos en todos los modos, por pedido del usuario. "
          "El resto usa escuelas y pesos de 2025 e IDW, radios 2001. La torta conserva el AMBA completo, incluidos los votos de los radios excluidos; "
          "NE integra Otros. Totales municipales completos conservados, salvo electores que siguen siendo de PolAr. No son ganadores observados por radio.")
if ISPASO:
    NOTE += (" PASO del 13 de agosto de 2023. "
             + ("Cada precandidatura compite por separado; Massa/Grabois, Bullrich/Larreta y Bregman/Solano no se suman. " if PASCAND else "En esta vista se suman las listas de cada agrupación. ")
             + f"La fuente tiene {C['listas_presentes_amba']} listas presidenciales presentes en el AMBA de las 27 nacionales. "
             "Torta regional sobre positivos, no resultado nacional. La proporción entre métodos no mide acierto observado por radio.")


def mode_choropleth(fn, base, edges, title, palette=None):
    cols, labels = stops_for(base, edges)
    if palette is not None:
        assert len(palette) == len(edges)
        cols = palette
    units = []
    for i in range(NU):
        r = unit_rec[i]; a = unit_an[i]
        nr = {k: v for k, v in r.items() if k in ("fill",)}
        nr["fill"] = BEIGE if not a["ok"] or not a["pos"] else cols[bin_of(fn(a), edges)]
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        nr = {k: val for k, val in r.items() if k not in ("w", "q", "fill")}
        nr["fill"] = BEIGE if part_an[p]['pos']<.5 else cols[bin_of(fn(part_an[p]), edges)]
        prov[p] = nr
    return units, prov, dict(title=title, stops=[[c, l] for c, l in zip(cols, labels)], bars=False,
                            keys=[[BEIGE,'Sin asignación / pendiente']] if any(r.get('fill')==BEIGE for r in units) else [])


pct = lambda b: (lambda a: 100 * a["bloc"][b] / a["pos"])
NATL = dict(cands=cands, slices=slices, partp=partp, metrics=NAT_MET)
MODES = [dict(id="gan", tile="GANÓ", note=NOTE, units=[unit_rec[i] for i in range(NU)], prov=prov_rec, national=NATL,
              legend=dict(keys=[[BEIGE, "NE estimado excluido / sin asignación" if C.get('NE_estimado_municipal') else ("Sin votos: circuito en cero en la fuente" if any(r.get("fill") == BEIGE and 'no se imputan' in r.get('note', '') for r in unit_rec.values()) else "Radio sin votos asignados") + (" o área sin circuito" if any(str(d).startswith('Área sin circuito') for d in disp.values()) else "")]] if any(r.get("fill") == BEIGE for r in unit_rec.values()) else []))]
# Cortes adaptados a los percentiles por radio, como en 2003 y 2025.
RANKED = sorted(BLOCS,key=lambda b:-TOT['bloc'][b])
if C.get('NE_estimado_municipal'):RANKED=[b for b in RANKED if b!='NE']
for b in (RANKED if PASCAND else RANKED[:4]):
    mid=b.lower(); tile=CAND[b].get('logo',b)[:6]
    values=np.array([100*unit_an[i]['bloc'][b]/unit_an[i]['pos'] for i in range(NR) if unit_an[i]['pos']>=.5])
    cuts=np.percentile(values,[10,25,40,60,80,95])
    if PASCAND:
        digits=1 if cuts[-1]>=5 else 2 if cuts[-1]>=.5 else 3
        edges=[0]+sorted({round(float(v),digits) for v in cuts if round(float(v),digits)>0})
        if len(edges)<3:
            hi=max(float(values.max()),1e-6)
            edges=[0,hi/3,hi*2/3,hi]
    else:edges=[0]+sorted(set(round(float(v),1) for v in cuts))
    palette = None
    if KEY == '2013dip' and b == 'FR':
        edges = sorted(set(edges))  # Los radios sin FR generaban dos límites de 0 %.
        palette = fr2013_ramp(len(edges))
    un, pv_, lg = mode_choropleth(pct(b), COLOR[b], edges, "%% %s" % NAMES[b][0], palette=palette)
    MODES.append(dict(id=mid, tile=tile, label='% '+NAMES[b][0], note=NOTE, units=un, prov=pv_, national=NATL, legend=lg))

# ---------------------------------------------------------------- SVG
body = []
for i, g in enumerate(G):
    body.append('<path class="d" data-i="%d" d="%s"/>' % (i, geom_d(g)))
caba_idx = [i for i, k in enumerate(UKEYS) if k[0] == "01"]
for i in caba_idx:
    body.append('<path class="dc" data-i="%d" d="%s"/>' % (i, geom_d(shapely.simplify(G_raw[i], 0.01))))
# niveles: partido (pp, y ppc para el recuadro de Capital) y circuito (ck, ckc); el selector cambia qué clase muestran
for j, (kind, _n, g, capital, _p) in enumerate(EXTRA, NR):
    cl = 'pp' if kind == 'partido' else 'ck'
    body.append('<path class="%s" data-i="%d" d="%s"/>' % (cl, j, geom_d(g.simplify(0.04, preserve_topology=True))))
    if capital: body.append('<path class="%sc" data-i="%d" d="%s"/>' % (cl, j, geom_d(g.simplify(0.01, preserve_topology=True))))
for p in PARTIDOS:
    u = unary_union([G_raw[i] for i in range(len(UKEYS)) if PART[i] == p])
    u = fill_slivers(u.buffer(0.7, join_style=2).buffer(-0.7, join_style=2))
    body.append('<path class="pb" data-prov="%s" d="%s"/>' % (p, line_d(u.boundary)))
# circunscripciones de Capital como divisores (las secciones electorales de 2003; las comunas son de 2005)
for _c in sorted(CIRCUNS):
    _u = unary_union([G_raw[i] for i in caba_idx if rp.unit[i][1] == _c])
    _u = fill_slivers(_u.buffer(0.3, join_style=2).buffer(-0.3, join_style=2))
    body.append('<path class="pb" data-prov="Ciudad de Buenos Aires" d="%s"/>' % line_d(_u.boundary))


def bbox_of(idx):
    return shapely.total_bounds([G_raw[i] for i in idx])


def window(b, aspect, pad=0.07):
    x0, y0, x1, y1 = b
    ww, hh = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    if ww / hh < aspect: ww = hh * aspect
    else: hh = ww / aspect
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(mx - ww / 2, 2), round(my - hh / 2, 2), round(ww, 2), round(hh, 2)]


def win_ll(lon, lat, wlon, aspect):
    x, y = ll(lon, lat); w = wlon * KX * S; hh = w / aspect
    return [round(x - w / 2, 2), round(y - hh / 2, 2), round(w, 2), round(hh, 2)]


INSETS = [
    # más arriba que en 2025: la leyenda tiene seis filas y arranca en y=1024
    dict(id="caba", label="Ciudad de Buenos Aires", f=[70, 545, 440, 440], win=window(bbox_of(caba_idx), 440 / 440, 0.04), show=["dc", "pb"], sd=0.25, sp=1.8, fit="meet"),
    dict(id="core", label="Conurbano y Capital", f=[1450, 140, 430, 420], win=win_ll(-58.50, -34.64, 0.36, 430 / 420), show=["d", "pb"], sd=0.2, sp=2.4),
    dict(id="lp", label="Gran La Plata", f=[1495, 640, 385, 300], win=win_ll(-57.955, -34.905, 0.13, 385 / 300), show=["d", "pb"], sd=0.25, sp=2.6),
]
pv = []
# los modos de coropleta no repiten las fichas: el navegador las copia del modo «ganó» (parche a la plantilla en la cola)
ds = dict(
    slug="amba_" + KEY + "_radios", locale="es-AR", country="Argentina",
    title=TITLE+" en el AMBA de", year=str(YEAR),
    labels=dict(pie1="Proporción sobre votos positivos", provinces=""),
    # escala fina, como el AMBA 2025 por radio: con cinco fuerzas el ganador saca entre 22 y 37 % en el 90 % de los radios (mediana 27)
    exterior=False, candidates=CAND, bins=(WIN_BINS:=sorted(set(int(round(v)) for v in np.percentile([unit_rec[i]['q'] for i in range(NR) if 'q' in unit_rec[i]],[10,25,40,60,80,95])))),
    bin_labels=[('<' if i==0 else '+' if i==len(WIN_BINS) else '')+str(v)+'%' for i,v in enumerate([WIN_BINS[0]]+WIN_BINS)],
    sets={"1": dict(label=str(YEAR), subtitle=("Por candidato · estimado" if PASCAND else "Por fuerza · estimado" if ISPASO else "Por radio censal · estimado"))},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp[i], p=PART[i], k="radio") for i in range(NR)] + [dict(n=e[1], p=e[4], k=e[0]) for e in EXTRA],
)
json.dump(ds, open(os.path.join(HERE, "dataset_%s.json" % KEY), "w", encoding="utf8"), ensure_ascii=False)


# ---------------------------------------------------------------- cola del atlas AMBA 2025 (plantilla y parches), con reemplazos
def load_part(fn, patches):
    t = open(os.path.join(CIRC, fn), encoding="utf8").read()
    for old, new in patches:
        assert t.count(old) == 1, (fn, old[:60], t.count(old))
        t = t.replace(old, new)
    return t


TAIL = load_part("tail_amba.py", [
    ('sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 2025 · AMBA por circuito</title>")',
     ('sub("<title>Atlas electoral</title>", "<title>%s %s · AMBA por radio</title>")\n' % (TITLE,YEAR)) +
     'sub("const shade=(code,i)=>{const b=CAND[code].base;", "const shade=(code,i)=>{const b=CAND[code].base;if(CAND[code].ramp)return CAND[code].ramp[i];")\n'
     'sub("const MODES={};DATA.modes.forEach(m=>MODES[m.id]=m);", "const MODES={};DATA.modes.forEach(m=>MODES[m.id]=m);'
     'DATA.modes.slice(1).forEach(m=>m.units.forEach((u,i)=>{const g=DATA.modes[0].units[i];if(!u.lines){u.lines=g.lines;u.metrics=g.metrics;if(g.note)u.note=g.note;}}));")\n'
     'sub(\'mw.style.setProperty("--sd",(1.5/Z.k).toFixed(4)+"px");\', \'mw.style.setProperty("--sd",(0.3/Z.k).toFixed(4)+"px");\')'),
    ("--v-mk:inline;--sd:1.5px;", "--v-mk:inline;--sd:0.3px;"),
    ('out = os.path.join(HERE, "atlas_amba2025.html")', 'out = os.path.join(HERE, "atlas_%s.html" % KEY)'),
])
old_name='el("text",{x:424,y:y+20*k,"font-size":MANY?18:21,fill:"#fff","text-anchor":"end"},g,C.n);'
# con un bloque de la Wikipedia a toda la altura, el nombre y el subtítulo se comprimen al espacio que queda a su derecha
new_name=('const nlim=C.img&&C.blk?Math.min(215,424-93-h*1.05*(C.ar||1)-10):215,cname='+old_name[:-1]+';'
          'if(cname.getComputedTextLength()>nlim){cname.setAttribute("textLength",nlim);cname.setAttribute("lengthAdjust","spacingAndGlyphs");}')
old_subt='el("text",{x:424,y:y+37*k,"font-size":MANY?13:15,fill:"#fff","text-anchor":"end",opacity:.95},g,C.sub);'
new_subt=('{const csub='+old_subt[:-1]+';'   # va detrás de un if(C.sub): entre llaves
          'if(csub.getComputedTextLength()>nlim){csub.setAttribute("textLength",nlim);csub.setAttribute("lengthAdjust","spacingAndGlyphs");}}')
marker='html = (tpl.replace('
assert TAIL.count(marker)==1
TAIL=TAIL.replace(marker,'sub('+repr(old_name)+','+repr(new_name)+')\n'+marker)
TAIL=TAIL.replace(marker,'sub('+repr(old_subt)+','+repr(new_subt)+')\n'+marker)
# Ajustar al marco completo, sin depender del bl heredado de otra altura de fila.
old_logo = '''if(C.img){const ih=h*(C.bl||1.2),iw=ih*(C.ar||1),cv=el("svg",{x:93,y,width:110,height:h,overflow:"hidden"},g);   // el logo desborda la barra y se recorta al marco
      el("image",{href:C.img,x:Math.max(3,4+(h*1.2-iw)/2),y:-(ih-h)/2,width:iw,height:ih,preserveAspectRatio:"xMidYMid meet"},cv);}'''
# Los bloques de los mapas presidenciales de la Wikipedia van pegados al borde izquierdo de la barra y a toda su
# altura (leve zoom que recorta apenas arriba y abajo), como en los mapas ya subidos: sin franjas entre el bloque y
# la barra, así que el ancho es el que dé la proporción (no se limita al marco de 110 px). Los demás logos, centrados.
new_logo = '''if(C.img&&C.blk){const ar=C.ar||1,bh=h*1.05,bw=bh*ar,cv=el("svg",{x:93,y,width:bw,height:h,overflow:"hidden"},g);
      el("image",{href:C.img,x:0,y:(h-bh)/2,width:bw,height:bh,preserveAspectRatio:"xMinYMid meet"},cv);}
    else if(C.img){const ar=C.ar||1,ih=Math.min(h-6,102/ar),iw=ih*ar,cv=el("svg",{x:93,y,width:110,height:h,overflow:"hidden"},g);
      el("image",{href:C.img,x:(110-iw)/2,y:(h-ih)/2,width:iw,height:ih,preserveAspectRatio:"xMidYMid meet"},cv);}'''
TAIL=TAIL.replace(marker,'sub('+repr(old_logo)+','+repr(new_logo)+')\n'+marker)
# Selector de nivel (2-nov-2026, pedido del usuario): Partido / Circuito / Radio. Cada nivel es una clase de trazos
# (d/dc, ck/ckc, pp/ppc); el nivel elegido renombra las variables --v-d y --v-dc del mapa y de los recuadros.
# La búsqueda salta al nivel de la unidad elegida y el CSV baja solo el nivel visible. #nv-c o #nv-p en la URL.
NIVEL_PATCHES = [
    ('.d{display:var(--v-d,none);stroke-width:calc(var(--sd,2px) / var(--k,1))}',
     '.d{display:var(--v-d,none);stroke-width:calc(var(--sd,2px) / var(--k,1))}\n'
     '.ck,.ckc,.pp,.ppc{stroke:#fff;stroke-linejoin:round;stroke-linecap:round;stroke-width:calc(var(--sd,2px) / var(--k,1))}\n'
     '.ck{display:var(--v-ck,none)}.ckc{display:var(--v-ckc,none)}.pp{display:var(--v-pp,none)}.ppc{display:var(--v-ppc,none)}\n'
     '#niv button.on{background:#70a6d7;color:#111;border-color:#70a6d7}'),
    ('<span class="sp"></span>',
     '<div class="grp" id="niv" role="group" aria-label="Nivel del mapa"><span>Nivel:</span>'
     '<button data-n="p" title="Partidos y, en Capital, %s: suma de los radios">Partido</button>'
     '<button data-n="c" title="Circuitos electorales: votos observados de la fuente">Circuito</button>'
     '<button data-n="r" class="on" title="Radios censales: estimación">Radio</button></div><span class="sp"></span>'
     % ('comunas' if YEAR >= 2009 else 'circunscripciones')),
    ('let st=I.show.map(c=>`--v-${c}:inline`).join(";");',
     'let st=I.show.map(c=>`--v-${nivCls(c)}:inline`).join(";");'),
    ('function selectUnit(i,zoom,pos){',
     'function selectUnit(i,zoom,pos){if(T[i].k!==NIVK[NIVEL])setNivel(NIVOF[T[i].k]);'),
    ('M.units.forEach((u,i)=>{const row=',
     'M.units.forEach((u,i)=>{if(T[i].k!==NIVK[NIVEL])return;const row='),
    ('drawTiles();drawTitle();renderCard();highlight();}',
     'drawTiles();drawTitle();renderCard();highlight();}\n'
     'const NIV={r:["d","dc"],c:["ck","ckc"],p:["pp","ppc"]},NIVK={r:"radio",c:"circuito",p:"partido"},NIVOF={radio:"r",circuito:"c",partido:"p"};\n'
     'let NIVEL=((location.hash.match(/nv-([rcp])/)||[])[1])||"r";\n'
     'function nivCls(c){return c==="d"?NIV[NIVEL][0]:c==="dc"?NIV[NIVEL][1]:c;}\n'
     'function setNivel(n){NIVEL=n;const mw=$("#mainwrap");if(mw.dataset.o==null)mw.dataset.o=mw.getAttribute("style");\n'
     '  mw.setAttribute("style",mw.dataset.o.replace(/--v-(dc|d):/g,(m,c)=>"--v-"+nivCls(c)+":"));drawInsets();\n'
     '  document.querySelectorAll("#niv button").forEach(b=>b.classList.toggle("on",b.dataset.n===n));\n'
     '  if(SEL&&SEL.type==="unit"&&T[SEL.i].k!==NIVK[n])clearSel();}'),
    ('const tip=$("#tip");',
     'document.querySelectorAll("#niv button").forEach(b=>b.addEventListener("click",()=>setNivel(b.dataset.n)));\n'
     'const tip=$("#tip");'),
    ('let DRAG=null,SEL=null;', 'let DRAG=null,SEL=null;\nsetNivel(NIVEL);'),
]
for old, new in NIVEL_PATCHES:
    TAIL = TAIL.replace(marker, 'sub(' + repr(old) + ',' + repr(new) + ')\n' + marker)
if (YEAR==2009 and C.get('NE_estimado_municipal')) or PASCAND:
    old_y='const MANY=N.cands.length>5,Y0=MANY?(N.cands.length>9?1008:1024):1266;'
    new_y='const MANY=N.cands.length>5,Y0=MODE==="gan"?1200:1266;'
    TAIL=TAIL.replace(marker,'sub('+repr(old_y)+','+repr(new_y)+')\n'+marker)
if PASCAND:
    # Todas las precandidaturas quedan accesibles sin apilar decenas de pestañas.
    import html as htmlmod
    options='<option value="gan">Ganador por candidato</option>'+''.join(
        '<option value="'+m['id']+'">'+htmlmod.escape(m['label'])+'</option>' for m in MODES[1:])
    select='<div class="grp"><label for="paso-mode">Vista:</label><select id="paso-mode" aria-label="Candidato o mapa" style="max-width:350px">'+options+'</select></div>'
    base_template=open(TEMPLATE_SRC,encoding='utf8').read()
    begin=base_template.index('function tilesNow(){');end=base_template.index('function drawTiles(){',begin)
    old_tiles=base_template[begin:end].replace('out.slice(0,4)','out.slice(0,5)')
    new_tiles=('function tilesNow(){const out=DATA.modes.slice(0,4).map(m=>[m.id,m.tile||m.id]);'
               'if(!out.some(x=>x[0]===MODE))out.push([MODE,MODES[MODE].tile||MODE]);return out;}\n')
    patches=[('<span class="sp"></span>',select+'<span class="sp"></span>'),
             (old_tiles,new_tiles),
             ('function setMode(m){MODE=m;','function setMode(m){MODE=m;const sm=$("#paso-mode");if(sm)sm.value=m;'),
             ('const tip=$("#tip");','const psel=$("#paso-mode");psel.addEventListener("change",()=>setMode(psel.value));\nconst tip=$("#tip");')]
    for old,new in patches:TAIL=TAIL.replace(marker,'sub('+repr(old)+','+repr(new)+')\n'+marker)
if ISPASO:
    other='2023pasofuerza' if PASCAND else '2023pasocand'
    link='<div class="grp"><a style="color:#70a6d7" href="atlas_'+other+'.html">Ver por '+('fuerza' if PASCAND else 'candidato')+'</a></div><span class="sp"></span>'
    TAIL=TAIL.replace(marker,'sub('+repr('<span class="sp"></span>')+','+repr(link)+')\n'+marker)
exec(TAIL)
