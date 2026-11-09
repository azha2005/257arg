"""Atlas presidencial de 1886 (Juárez Celman contra los Partidos Unidos).

Ver LEEME_1886.md. Geometría del censo de 1895 con la Capital anterior a 1887.
Provincia de Buenos Aires por partido (recorte de prensa con datos del comité rochista), Capital por
parroquia con las dos versiones del CD de Cantón y Jorrat y el resto por electores (Wikipedia).
Visor, proyección y plantilla del atlas de 1874.

Correr con el Python del venv de Mosaic (geopandas):
  "C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/mapa1886/build_1886.py
"""
from pathlib import Path
import csv, json, math, os, re, sys, unicodedata
from collections import Counter
import numpy as np
import geopandas as gpd
import shapely
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "comun"))
from outline_clean import clean_outline, clean_holes

TEMPLATE_SRC = ROOT / ".claude/skills/mapa-electoral-wikipedia-1999/assets/template.html"
BASE = ROOT / "geometria/Base deptos 1869-2022"
PARR = ROOT / "geometria/parroquias_capital_1864_1898/parroquias_1872_base.shp"

PROV = {'06': 'Buenos Aires', '10': 'Catamarca', '14': 'Córdoba', '18': 'Corrientes', '22': 'Chaco',
        '26': 'Chubut', '30': 'Entre Ríos', '34': 'Formosa', '38': 'Jujuy', '42': 'La Pampa',
        '46': 'La Rioja', '50': 'Mendoza', '54': 'Misiones', '66': 'Salta', '70': 'San Juan',
        '74': 'San Luis', '82': 'Santa Fe', '86': 'Santiago del Estero', '90': 'Tucumán',
        '94': 'Tierra del Fuego', '99': 'Patagonia', '58': 'Neuquén', '62': 'Río Negro', '78': 'Santa Cruz'}
TERR = {'Chaco', 'Chubut', 'Formosa', 'La Pampa', 'Misiones', 'Tierra del Fuego', 'Patagonia', 'Neuquén', 'Río Negro', 'Santa Cruz'}

ALIAS = {'Ajó': 'Gnral. Lavalle', 'Alvear': 'Gnral. Alvear', 'Barracas': 'Barracas al Sud', 'Brandzen': 'Brandsen',
         'Juárez': 'Benito Juárez', 'Las Heras': 'Gnral. Las Heras', 'Matanzas': 'La Matanza', '9 de Julio': 'Nueve de Julio',
         'Ranchos': 'Gnral. Paz (Ranchos)', 'Rodríguez': 'Gnral. Rodríguez', 'Giles': 'San Andrés de Giles',
         'San Antonio': 'San Antonio de Areco', 'San Martín': 'Gnral. San Martín', 'Suárez': 'Crnel. Suárez'}
ROBAR69 = ('Belgrano', 'San Jose de Flores')   # anexados a la Capital en 1887


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if not unicodedata.combining(c)))


# ---------------------------------------------------------------- geometría 1895 (+ Capital anterior a 1887)
g95 = gpd.read_file(BASE / 'Departamentos_1895.shp', encoding='utf-8')
g69 = gpd.read_file(BASE / 'Departamentos_1869.shp', encoding='utf-8')
U = []
for r in g95.itertuples():
    if r.PROV_COD == '02':
        continue
    prov = PROV[r.PROV_COD]
    nm = r.DEPTO.strip()
    kind = 'partido' if prov == 'Buenos Aires' else ('territorio' if prov in TERR else 'departamento')
    if nm == 'Islas Malvinas':
        kind = 'malvinas'
    U.append(dict(prov=prov, name=nm, kind=kind, geom=shapely.make_valid(r.geometry).buffer(0)))
parr = gpd.read_file(PARR)
cap_old = unary_union([shapely.make_valid(g).buffer(0) for g in parr.geometry])
pba = unary_union([u['geom'] for u in U if u['prov'] == 'Buenos Aires'])
for nm in ROBAR69:
    poly = shapely.make_valid(g69[(g69.PROV_COD == '06') & (g69.DEPTO.apply(norm) == norm(nm))].geometry.iloc[0]).buffer(0)
    U.append(dict(prov='Buenos Aires', name=nm.replace('Jose', 'José'), kind='partido', robado=True,
                  geom=poly.difference(pba).difference(cap_old).buffer(0)))
for r in parr.itertuples():
    U.append(dict(prov='Capital', name=r.parroquia, kind='parroquia', geom=shapely.make_valid(r.geometry).buffer(0)))
U.sort(key=lambda u: (u['prov'], u['kind'] != 'parroquia', u['name']))


# Misma proyección que los atlas 1912-1940.
LAT0 = -38.0
KX = math.cos(math.radians(LAT0))
S, X0, Y0 = 44.0, 643.0, 150.0
LON0, LAT1 = -73.5708041, -21.7807776


def proj(a):
    a = np.asarray(a, float).copy()
    a[:, 0] = (a[:, 0] - LON0) * KX * S + X0
    a[:, 1] = (LAT1 - a[:, 1]) * S + Y0
    return a


def ll(lon, lat):
    return ((lon - LON0) * KX * S + X0, (LAT1 - lat) * S + Y0)


def f2(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


def ring_d(c):
    pts = list(c.coords)
    return "M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts[:-1]) + "Z"


def geom_d(g):
    if g.is_empty:
        return ""
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type != "Polygon":
            continue
        out.append(ring_d(p.exterior))
        out += [ring_d(h) for h in p.interiors]
    return "".join(out)


def line_d(g):
    out = []
    for l in (g.geoms if hasattr(g, "geoms") else [g]):
        pts = list(l.coords)
        if len(pts) >= 2:
            out.append("M" + "L".join("%s %s" % (f2(x), f2(y)) for x, y in pts))
    return "".join(out)


G_raw = [shapely.transform(u['geom'], proj) for u in U]
G = list(shapely.coverage_simplify(np.array(G_raw, dtype=object), 0.3))
PROVS = sorted(set(u['prov'] for u in U))
prov_geom = {p: unary_union([G[i].buffer(0.12) for i, u in enumerate(U) if u['prov'] == p and u['kind'] != 'malvinas']).buffer(-0.12)
             for p in PROVS}
prov_geom = {p: g for p, g in prov_geom.items() if not g.is_empty}
PROVS = sorted(prov_geom)
country = unary_union(list(prov_geom.values())).buffer(0.1).buffer(-0.1).simplify(0.12)
country = clean_outline(country)
prov_geom = {p: clean_holes(g.simplify(0.12), name=p) for p, g in prov_geom.items()}
prov_mini = {p: g.simplify(0.7) for p, g in prov_geom.items()}

# ---------------------------------------------------------------- datos
def nk(s):
    return norm(s)


filas = list(csv.DictReader(open(HERE / 'provincia_1886.csv', encoding='utf-8')))
KEY = {(u['kind'] == 'parroquia', norm(u['name'])): i for i, u in enumerate(U) if u['prov'] == 'Buenos Aires'}
fila_de, sin_poligono = {}, []
for f in filas:
    nm = ALIAS.get(f['unidad'], f['unidad'])
    i = KEY.get((False, norm(nm)))
    if i is None:
        sin_poligono.append(f['unidad'])
        continue
    fila_de[i] = f

# Capital: CD de Cantón y Jorrat, planilla 11 (El Diario, 12 de abril de 1886), dos versiones.
CAP = {}
for r in csv.DictReader(open(HERE / 'capital_1886.csv', encoding='utf-8')):
    if r['parroquia'] == 'Total':
        continue
    v = [int(r[c]) if r[c] else None for c in ('pu_segun_pu', 'juar_segun_pu', 'pu_segun_policia', 'juar_segun_policia')]
    CAP[norm(r['parroquia'].replace('Catedral', 'Catedral al'))] = dict(PU=(v[0], v[1]), POL=(v[2], v[3]))
CAPTOT = dict(PU=(7004, 3960), POL=(5306, 8605))   # fila Total de la planilla

JUA, PU = 'JUA', 'PU'
CAND = {
    JUA: dict(n='Miguel Juárez Celman', sub='Partido Autonomista Nacional', base='#74acdf', logo='PAN',
              ramp=['#eef6fc', '#e0eff9', '#cfe6f6', '#bcdcf2', '#a8d1ee', '#93c6ea', '#7dbbe6']),
    PU: dict(n='Partidos Unidos', sub='Coaligados · Ocampo e Irigoyen', base='#c90016', logo='PU',
             ramp=['#f7c6cc', '#ef9fa9', '#e57785', '#da4f62', '#c90016', '#a10012', '#79000d']),
}
GREY_T, GREY_N, NOV = '#cfcfcf', '#e6dcc3', '#6f6f6f'
JUA_L, PU_L = '#cfe6f6', '#f2b8c0'          # una sola cifra publicada
JUA_E, PU_E, NOVOTO = '#e3eef7', '#f6dfe2', '#9a9a9a'   # electores (Wikipedia), sin voto popular
# Tabla «Resultados por provincia» de la Wikipedia: [Juárez Celman, Partidos Unidos (Ocampo + Irigoyen)], no votaron.
ELECTORES = {'Buenos Aires': (0, 31, 5), 'Capital': (22, 0, 0), 'Catamarca': (12, 0, 0), 'Córdoba': (26, 0, 0),
             'Corrientes': (15, 0, 1), 'Entre Ríos': (18, 0, 0), 'Jujuy': (8, 0, 0), 'La Rioja': (8, 0, 0),
             'Mendoza': (10, 0, 0), 'Salta': None, 'San Juan': (10, 0, 0), 'San Luis': (10, 0, 0),
             'Santa Fe': (11, 0, 1), 'Santiago del Estero': (18, 0, 0), 'Tucumán': (0, 14, 0)}
assert sum(v[0] for v in ELECTORES.values() if v) == 168 and sum(v[1] for v in ELECTORES.values() if v) == 45
FUENTE_P = ('Recorte de prensa aportado por el usuario, abril de 1886: «El resultado de las elecciones del Domingo en la Provincia», '
            'datos del comité rochista (c = coaligados, j = juaristas).')
PRINTED = (21070, 3028)
KEYS = [[JUA_E, 'Electores de Juárez Celman (Wikipedia), sin voto popular'], [PU_E, 'Electores de los Partidos Unidos (Wikipedia), sin voto popular'],
        [PU_L, 'Solo cifra de los coaligados'], [JUA_L, 'Solo cifra de los juaristas'], [NOV, 'No hubo elección'],
        [NOVOTO, 'No votó'], [GREY_N, 'Sin datos'], [GREY_T, 'Territorio sin elección']]


def fmt(v):
    return f'{int(v):,}'.replace(',', '.')


def two(pu, ju, note):
    d = pu + ju
    lines = sorted([[PU, pu, round(100 * pu / d, 2)], [JUA, ju, round(100 * ju / d, 2)]], key=lambda x: -x[1])
    rec = dict(lines=lines, metrics=[['Votos de ambos bandos', fmt(d)]], note=note)
    if pu != ju:
        rec.update(w=lines[0][0], q=lines[0][2])
    else:
        rec['fill'] = GREY_N
    return rec


def elec(p):
    v = ELECTORES.get(p)
    if v is None:
        return dict(fill=NOVOTO, lines=[], note='Salta no votó (Wikipedia).')
    ju, pu, nv = v
    return dict(fill=PU_E if pu > ju else JUA_E, lines=[],
                note=f'Sin voto popular. Color según los electores (Wikipedia): {ju} para Juárez Celman, {pu} para los Partidos Unidos'
                     + (f', {nv} no votaron' if nv else '') + '.',
                metrics=[['Electores Juárez Celman', str(ju)], ['Electores Partidos Unidos', str(pu)]])


def unit_for(i, u, version):
    p = u['prov']
    if u['kind'] == 'malvinas':
        return dict(fill='#a9a9a9', lines=[], note='Islas Malvinas.')
    if p in TERR:
        return dict(fill=GREY_T, lines=[], note='Territorio nacional: sin elección presidencial en 1886.')
    if u['kind'] == 'parroquia':
        c = CAP.get(norm(u['name']))
        lab = 'según los Partidos Unidos' if version == 'PU' else 'según la policía'
        base = (f'Versión {lab}. CD de Cantón y Jorrat, planilla 11, tomada de El Diario del 12 de abril de 1886; '
                'los autores la reproducen «a pesar de sus inconsistencias».')
        if c is None:
            return dict(fill=GREY_N, lines=[], note='Sin fila en la planilla.')
        pu, ju = c[version]
        otra = c['POL' if version == 'PU' else 'PU']
        base += f' La otra versión da {fmt(otra[0]) if otra[0] is not None else "—"} P.U. y {fmt(otra[1]) if otra[1] is not None else "—"} juaristas.'
        if pu is None and ju is None:
            return dict(fill=GREY_N, lines=[], note=base + ' Esta versión no trae cifras.')
        if pu is None or ju is None:
            cc, vv = (PU, pu) if ju is None else (JUA, ju)
            return dict(fill=PU_L if cc == PU else JUA_L, lines=[[cc, vv, None]],
                        note=base + ' Mesa doble: esta versión solo computa la mesa de un bando.')
        return two(pu, ju, base)
    if p == 'Buenos Aires':
        f = fila_de.get(i)
        if not f:
            return dict(fill=GREY_N, lines=[], note='Pendiente: el partido no figura en el recorte.')
        note = FUENTE_P + (f' {f["nota"].capitalize()}.' if f['nota'] else '')
        if u.get('robado'):
            note += ' Partido anexado a la Capital en 1887: polígono del censo de 1869.'
        if f['coaligados'] == '-':
            return dict(fill=NOV, lines=[], note=note)
        if f['coaligados'] == '':
            return dict(fill=GREY_N, lines=[], note=note)
        pu = int(f['coaligados'])
        if f['juaristas']:
            return two(pu, int(f['juaristas']), note)
        return dict(fill=PU_L, lines=[[PU, pu, None]], note=note + ' Solo figura la cifra de los coaligados.')
    if p == 'San Luis' and u['name'] == 'La Capital':
        r = elec(p)
        r.update(fill=PU_L, lines=[[PU, 800, None], [JUA, 500, None]],
                 note='Ciudad de San Luis, estimación del corresponsal (diario porteño, telegrama del 13 de abril de 1886, aportado por el usuario): '
                      'todas las mesas eran juaristas; «se calcula en más de ochocientos» los votantes de los Partidos Unidos y «en quinientos» '
                      'los de los juaristas, pero el resultado fue favorable a Juárez Celman. La elección fue protestada. Cálculo, no escrutinio: '
                      'sin porcentaje y fuera de la torta. ' + r['note'])
        return r
    return elec(p)


def prov_for(p, version):
    if p in TERR:
        return dict(fill=GREY_T, lines=[], note='Territorio nacional.')
    if p == 'Buenos Aires':
        r = two(PRINTED[0], PRINTED[1], f'Total impreso del recorte: 21.070 coaligados y 3.028 juaristas. {FUENTE_P} '
                f'Las filas suman {fmt(SUMA[0])} y {fmt(SUMA[1])}; no se ajustan. Electores: 31 Partidos Unidos (Ocampo), 5 no votaron. '
                'Incluye Belgrano y San José de Flores, anexados a la Capital en 1887.')
        r['metrics'] += [['Electores Partidos Unidos', '31']]
        return r
    if p == 'Capital':
        pu, ju = CAPTOT[version]
        r = two(pu, ju, f'Fila Total de la planilla 11 del CD ({"según los Partidos Unidos" if version == "PU" else "según la policía"}). Electores: 22 para Juárez Celman.')
        r['metrics'] += [['Electores Juárez Celman', '22']]
        return r
    return elec(p)


SUMA = [sum(int(f[c]) for f in filas if f[c] not in ('', '-')) for c in ('coaligados', 'juaristas')]
MODES = []
for version, tile, lab in (('PU', 'P.U.', 'según los Partidos Unidos'), ('POL', 'POLICÍA', 'según la policía')):
    cpu, cju = CAPTOT[version]
    tot = {PU: PRINTED[0] + cpu, JUA: PRINTED[1] + cju}
    d = sum(tot.values())
    cands = sorted([dict(code=c, votes=v, pct=round(100 * v / d, 2)) for c, v in tot.items()], key=lambda c: -c['votes'])
    note = (f'Voto popular conocido: provincia de Buenos Aires por partido y Capital por parroquia ({lab}). '
            f'Provincia: {FUENTE_P} Total impreso 21.070 coaligados y 3.028 juaristas; las filas suman {fmt(SUMA[0])} y {fmt(SUMA[1])}, sin ajustar. '
            'Capital: CD de Cantón y Jorrat, planilla 11, con las dos versiones de El Diario del 12 de abril (Partidos Unidos y policía); '
            'en las parroquias de mesas dobles cada versión computa solo la mesa de su bando. '
            f'Torta y barras: total impreso de la provincia más la Capital {lab}. '
            'Las demás provincias llevan, en tono claro, el color de quien ganó sus electores según la Wikipedia (Juárez Celman 168; '
            'Partidos Unidos 45, en Buenos Aires y Tucumán). Salta no votó. '
            'Geometría: departamentos del censo de 1895 (Rodríguez y De Grande, CONICET); Capital con las 14 parroquias de 1872-1886; '
            'Belgrano y San José de Flores con el polígono de 1869. Ensenada (530 c, 6 j) no tiene polígono propio en 1895: va en esta nota.')
    MODES.append(dict(id=version.lower(), tile=tile, note=note,
                      units=[unit_for(i, u, version) for i, u in enumerate(U)],
                      prov={p: prov_for(p, version) for p in PROVS},
                      national=dict(cands=cands, slices=[dict(code=c['code'], v=c['votes']) for c in cands], partp=None,
                                    metrics=[['Votos conocidos', fmt(d)], ['Electores Juárez Celman', '168'],
                                             ['Electores Partidos Unidos', '45'], ['No votaron', '19']]),
                      legend=dict(keys=KEYS)))
SOLID = sorted(p for p in ELECTORES if p not in ('Buenos Aires', 'Capital'))

# ---------------------------------------------------------------- SVG
body = [('<defs>'
         '<pattern id="h_pan" patternUnits="userSpaceOnUse" width="1.6" height="1.6" patternTransform="rotate(45)">'
         '<rect width="1.6" height="1.6" fill="#ffffff"/><rect width="0.8" height="1.6" fill="#7dbbe6"/></pattern>'
         '<pattern id="h_mit" patternUnits="userSpaceOnUse" width="1.6" height="1.6" patternTransform="rotate(45)">'
         '<rect width="1.6" height="1.6" fill="#ffffff"/><rect width="0.8" height="1.6" fill="#162a72"/></pattern>'
         '</defs>')]
for i, u in enumerate(U):
    if u['kind'] == 'malvinas':
        body.append('<path class="mal" style="display:inline;fill:#a9a9a9;stroke:#1b1b1b;stroke-width:1" d="%s"/>' % geom_d(G[i]))
    body.append('<path class="d" data-i="%d" d="%s"/>' % (i, geom_d(G[i])))
cap_idx = [i for i, u in enumerate(U) if u['kind'] == 'parroquia']
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
    if ww / hh < aspect:
        ww = hh * aspect
    else:
        hh = ww / aspect
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [round(mx - ww / 2, 2), round(my - hh / 2, 2), round(ww, 2), round(hh, 2)]


tuc = [i for i, u in enumerate(U) if u['prov'] == 'Tucumán']
caba_b = bbox_of(cap_idx)
cx, cy = (caba_b[0] + caba_b[2]) / 2, (caba_b[1] + caba_b[3]) / 2
gba_w = 62.0
INSETS = [
    None and dict(id="tuc", label="Tucumán", f=[450, 300, 200, 185], win=window(bbox_of(tuc), 200 / 185), show=["d", "pb"], sd=2.6, sp=3.4),
    dict(id="gba", label="Alrededores de la ciudad de Buenos Aires", f=[1247, 785, 647, 320],
         win=[round(cx - gba_w * 0.42, 2), round(cy - gba_w / (647 / 320) * 0.5, 2), gba_w, round(gba_w / (647 / 320), 2)],
         show=["d", "pb", "out"], sd=1.9, sp=3.0, so=2.6),
    dict(id="caba", label="Ciudad de Buenos Aires", f=[1632, 1187, 191, 232], win=window(caba_b, 191 / 232, 0.05), show=["dc"], sd=3,
         fit="meet", noframe=True, lx=1728, noclip=True, so=2.6),
]
INSETS = [I for I in INSETS if I]   # sin Tucumán: la provincia va en color sólido
for w in (INSETS[0]["win"],):
    body.append('<rect class="mk" x="%s" y="%s" width="%s" height="%s"/>' % tuple(f2(v) for v in w))

KPV = 0.2669
bx0, by0, bx1, by1 = shapely.total_bounds([prov_geom[p] for p in PROVS])
pv_tx = 182 - KPV * (bx0 + bx1) / 2
pv_ty = 600 - KPV * by0
pv = ['<g>'] + ['<path class="pf" data-prov="%s" d="%s"/>' % (p, geom_d(prov_mini[p])) for p in PROVS]
pv += ['<path class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round" d="%s"/>' % geom_d(G[i])
       for i, u in enumerate(U) if u['kind'] == 'malvinas']
pv.append('</g>')

disp = {i: u['name'] for i, u in enumerate(U)}
for i, f in fila_de.items():
    disp[i] = f['unidad']
for i, u in enumerate(U):
    if u['kind'] == 'parroquia':
        disp[i] = u['name'] + ' (parroquia)'
ds = dict(
    slug="elecciones_1886", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de Argentina de", year="1886",
    labels=dict(pie1="Voto conocido: Bs. As. y Capital", pie2=""),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1886", subtitle="Voto popular · deptos. 1895")},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp[i], p=u['prov'], k=u['kind']) for i, u in enumerate(U)],
    solid=SOLID,
    shade_k=[None, 1, .92, .84, .76, .68, .60],
)
json.dump(ds, open(HERE / "dataset_1886.json", "w", encoding="utf8"), ensure_ascii=False)

# ---------------------------------------------------------------- plantilla (parches de la familia 1912-1940)
tpl = TEMPLATE_SRC.read_text(encoding="utf8")


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Atlas electoral 1886</title>")
# Rampas propias (pedido del usuario: que se distingan): el PAN no se oscurece, Mitre no se aclara.
sub("const shade=(code,i)=>{const b=CAND[code].base;", "const shade=(code,i)=>{if(CAND[code].ramp)return CAND[code].ramp[i];const b=CAND[code].base;")
sub('style="--v-d:inline;--v-dc:inline;--v-pb:inline;--sd:1.5px;--sp:3px;--so:3.2px"', 'style="--v-d:inline;--v-pb:inline;--v-out:inline;--v-cn:inline;--sd:1.5px;--sp:3px;--so:3.2px"')
sub('<image id="frontiers" href="{{FRONTIERS}}" x="570" y="100" width="840" height="1540"/>', '<g id="frontiers"></g>')
sub('<g id="pv" transform="matrix(0.1448 0 0 0.1448 55.7 599.8)" style="--spf:9.7px">', '<g id="pv" transform="matrix(%s 0 0 %s %s %s)" style="--spf:9.7px">' % (KPV, KPV, f2(pv_tx), f2(pv_ty)))
sub("#frontiers,.pb,.out,.out2,.antf,.antg,.mal{pointer-events:none}", "#frontiers,.pb,.out,.out2,.antf,.antg,.mal,.cn,.mk{pointer-events:none}\n.cn{display:var(--v-cn,none);fill:#616261;font-size:24px;font-weight:700}\n.mk{display:var(--v-mk,none);fill:none;stroke:#616261;stroke-width:1.4}")
i0 = tpl.index("const INSETS=[")
i1 = tpl.index("];", i0) + 2
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
sub("""    y+=h+(idx+1<rows.length&&!LG&&wins[rows[idx+1].code]?5:7);
  });""", """    y+=h+(idx+1<rows.length&&!LG&&wins[rows[idx+1].code]?5:7);
  });
  if(KEYS){
    y+=(rows.length?22:14);
    KEYS.keys.filter(([k])=>USED(k)).forEach(([col,lab])=>{el("rect",{x:93,y:y-12,width:16,height:14,fill:col,stroke:"#616161","stroke-width":.8},g);el("text",{x:118,y:y,"font-size":15,fill:"#616161"},g,lab);y+=22;});
  }""")
sub("""  const LG=MODES[MODE].legend;                                   // leyenda propia para mapas de color explícito (coropletas)""",
    """  const LG0=MODES[MODE].legend;const LG=(LG0&&LG0.stops)?LG0:null;   // leyenda propia para mapas de color explícito (coropletas)
  const KEYS=LG0&&LG0.keys?LG0:null;
  const USED=c=>[...document.querySelectorAll('#B .d,#B .dc')].some(e=>(e.getAttribute("fill")||"").toLowerCase()===c.toLowerCase());
  """)
sub("const rows=(LG&&LG.bars===false)?[]:N.cands;", "const rows=(LG0&&LG0.bars===false)?[]:N.cands;")
sub("""$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;""", """$("#pie1").textContent=LAB.pie1;$("#pie2").textContent=LAB.pie2;$("#pie1").setAttribute("x",184);""")
tpl = tpl.replace("{{MAIN_S}}", "1").replace("{{MAIN_TX}}", "0").replace("{{MAIN_TY}}", "0")
html = (tpl.replace("{{MAP}}", "".join(body)).replace("{{PV}}", "".join(pv))
        .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "pu"))
(HERE / "atlas_1886.html").write_text(html, encoding="utf8", newline="\n")


control = dict(unidades=len(U), filas=len(filas), filas_con_poligono=len(fila_de), filas_sin_poligono=sin_poligono,
               suma_filas=SUMA, total_impreso=PRINTED, parroquias=len(CAP))
(HERE / "CONTROL_1886.json").write_text(json.dumps(control, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(control, ensure_ascii=False))
