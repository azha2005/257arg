"""Atlas presidencial de 1874 (Avellaneda contra Mitre).

Buenos Aires por partido y parroquia con el cuadro de prensa del 17 de mayo de 1874;
las otras trece provincias quedan en beige por falta de votos populares. La torta y las
barras son un total provisorio: el total impreso del cuadro bonaerense, la única cifra
de votos disponible. Dibujo y plantilla de la familia de entreguerras
(transcripciones/entreguerras/construir.py), con la geometría de 1869 de Rodríguez y De Grande.

Correr con el Python del venv de Mosaic (geopandas):
  "C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/mapa1874/build_1874.py
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
        '94': 'Tierra del Fuego', '99': 'Patagonia'}
TERR = {'Chaco', 'Chubut', 'Formosa', 'La Pampa', 'Misiones', 'Tierra del Fuego', 'Patagonia'}

# Colegio electoral por provincia: tabla «Resultados por Provincia» del artículo
# «Elecciones presidenciales de Argentina de 1874» (es.wikipedia), [PAN, Mitre, no votaron].
ELECTORES = {'Buenos Aires': (0, 53, 1), 'Catamarca': (12, 0, 0), 'Córdoba': (25, 0, 1), 'Corrientes': (16, 0, 0),
             'Entre Ríos': (17, 0, 1), 'Jujuy': (8, 0, 0), 'La Rioja': (8, 0, 0), 'Mendoza': (10, 0, 0),
             'Salta': (12, 0, 0), 'San Juan': (0, 10, 0), 'San Luis': (10, 0, 0), 'Santa Fe': (12, 0, 0),
             'Santiago del Estero': (1, 16, 1), 'Tucumán': (14, 0, 0)}
assert sum(v[0] for v in ELECTORES.values()) == 145 and sum(v[1] for v in ELECTORES.values()) == 79
TOTAL_IMPRESO = {'PAN': 12103, 'MIT': 14971}   # cuadro del 17 de mayo, fila de totales
MENDOZA_PROVISORIO = {'Guaymallen', 'La Paz', 'Junin', 'Rosario', 'San Carlos'}
CORRIENTES_PROVISORIO = {'Capital', 'Empedrado', 'San Cosme'}
SOLID = sorted(set(ELECTORES) - {'Buenos Aires', 'Corrientes', 'Mendoza', 'San Luis', 'La Rioja'})
# San Juan: acta de la Junta Escrutadora del 12 de mayo (La Nación, 2 de junio de 1874, p. 1, col. 3).
SAN_JUAN = {'MIT': 1365, 'PAN': 916}
# La Rioja: cuadro «Cópia del escrutinio practicado el día 12 de Abril» (La Nación, 29 de mayo de 1874,
# p. 1, cols. 6-7, corresponsal mitrista). [Mitre, Avellaneda en mesas legales, Avellaneda en mesas
# impugnadas por los mitristas ("mansillanas"), rótulo del original]. Columnas: 1265, 1224, 1054.
RIOJA = {'Capital': (255, 259, 0, 'Mesa legal'), 'Independencia (Chamical)': (109, 13, 0, 'Independencia, mesa legal'),
         'Arauco': (0, 0, 322, 'Apócrifa'), 'San Blas de los Sauces': (0, 229, 0, 'Sauces, mesa legal'),
         'Villa Argentina (Chilecito)': (409, 0, 231, 'Chilecito'), 'Famatina': (123, 178, 0, 'Mesa legal'),
         'Guandacol': (0, 0, 147, 'Mesa Mansilla'), 'Vinchina': (79, 148, 0, 'Mesa legal'),
         'Gnral. Belgrano': (0, 0, 324, 'Mesa a lo Mansilla'), 'Costa Alta': (220, 201, 0, 'Mesa legal'),
         'Gnral.San Martín': (70, 0, 30, 'San Martín')}
RIOJA_SIN_POLIGONO = ('Costa del Medio (Tama)', 0, 196)
RIOJA_JUNTA = {'PAN': 2278, 'MIT': 1265}
assert sum(v[0] for v in RIOJA.values()) == 1265
assert sum(v[1] for v in RIOJA.values()) + RIOJA_SIN_POLIGONO[2] == 1224
assert sum(v[2] for v in RIOJA.values()) == 1054

# Filas del cuadro que no llevan el nombre del SHP de 1869.
ALIAS = {'general lavalle': ('Ajo', 'Ajó en el censo de 1869; el SHP de 1895 ya lo llama General Lavalle.'),
         'lomas de zamora': ('La Paz', 'La Paz en el censo de 1869 (el pueblo de Lomas se fundó como Pueblo de la Paz).')}
# Partidos con datos y sin polígono en 1869: se toma el de 1895 y se descuenta de sus vecinos.
ROBAR = {'Gnral. Alvear': 'General Alvear'}


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if not unicodedata.combining(c)))


# ---------------------------------------------------------------- geometría 1869
g69 = gpd.read_file(BASE / 'Departamentos_1869.shp', encoding='utf-8')
g95 = gpd.read_file(BASE / 'Departamentos_1895.shp', encoding='utf-8')
U = []
for r in g69.itertuples():
    if r.PROV_COD == '02':
        continue   # la ciudad va con las parroquias de 1872
    prov = PROV[r.PROV_COD]
    nm = r.DEPTO.strip()
    kind = 'partido' if prov == 'Buenos Aires' else ('territorio' if prov in TERR else 'departamento')
    if nm == 'Islas Malvinas':
        kind = 'malvinas'
    U.append(dict(prov=prov, name=nm, kind=kind, geom=shapely.make_valid(r.geometry).buffer(0)))
robados = []
for nm95, nm in ROBAR.items():
    poly = shapely.make_valid(g95[(g95.PROV_COD == '06') & (g95.DEPTO == nm95)].geometry.iloc[0]).buffer(0)
    pba = unary_union([u['geom'] for u in U if u['prov'] == 'Buenos Aires'])
    poly = poly.intersection(pba)
    for u in U:
        if u['prov'] == 'Buenos Aires' and u['geom'].intersects(poly):
            antes = u['geom'].area
            u['geom'] = u['geom'].difference(poly).buffer(0)
            if antes - u['geom'].area > 1e-6:
                robados.append((nm, u['name'], round(100 * (antes - u['geom'].area) / antes, 1)))
    U.append(dict(prov='Buenos Aires', name=nm, kind='partido', geom=poly, robado=True))
parr = gpd.read_file(PARR)
for r in parr.itertuples():
    U.append(dict(prov='Buenos Aires', name=r.parroquia, kind='parroquia', geom=shapely.make_valid(r.geometry).buffer(0)))
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
filas = list(csv.DictReader(open(HERE / 'cuadro_17mayo1874.csv', encoding='utf-8')))
KEY = {}
for i, u in enumerate(U):
    if u['prov'] == 'Buenos Aires':
        KEY[(u['kind'] == 'parroquia', norm(u['name']))] = i
fila_de = {}
sin_poligono = []
for f in filas:
    ciudad = f['zona'] == 'ciudad'
    nm, why = ALIAS.get(f['unidad'].lower(), (f['unidad'], None)) if not ciudad else (f['unidad'], None)
    i = KEY.get((ciudad, norm(nm)))
    if i is None:
        sin_poligono.append(f['unidad'])
        continue
    fila_de[i] = (f, why)

PAN, MIT = 'PAN', 'MIT'
CAND = {
    # Pedido del usuario: celeste claro para el PAN (el #74acdf de los atlas de 1904) y azul
    # oscuro para los mitristas, en la línea de los dos azules de la Wikipedia (#85C1E9, #2874A6).
    PAN: dict(n='Nicolás Avellaneda', sub='Alsina–Avellaneda · PAN', base='#74acdf', logo='PAN',
              ramp=['#eef6fc', '#e0eff9', '#cfe6f6', '#bcdcf2', '#a8d1ee', '#93c6ea', '#7dbbe6']),
    MIT: dict(n='Bartolomé Mitre', sub='Partido Nacionalista', base='#1c3f94', logo='PN',
              ramp=['#5a6fb5', '#3f55a3', '#2b4196', '#1f3585', '#162a72', '#0f205e', '#09174a']),
}
GREY_T, GREY_N, GREY_O = '#cfcfcf', '#e6dcc3', '#9a9a9a'
UNA_CIFRA = ('url(#h_pan)', 'url(#h_mit)')   # rayado: solo cifra PAN, solo cifra Mitre
SIN_PCT = '#d6d0c2'   # modos de porcentaje: una sola cifra, sin porcentaje
MIT_PROVISORIO = '#687bb5'
PAN_PROVISORIO = '#91bdd1'
PROVISORIOS = (MIT_PROVISORIO, PAN_PROVISORIO)
# Provincias sin voto popular completo: color de quien ganó sus electores (Wikipedia).
PAN_ELEC, MIT_ELEC = '#d3e6f4', '#a9b4dc'
VARIANTES = {   # cifras primarias de prensa anteriores al cuadro; no reemplazan la fila
    'San Antonio de Areco': 'Variante: 77 Mitre y 59 Alsina según La Nación del 23 de abril de 1874, p. 2 (informe externo, sin cotejar con el escaneo).',
    'San Miguel': 'Variante: 281 Mitre y 172 Alsina según La Nación del 15 de abril de 1874, p. 1 (informe externo, sin cotejar con el escaneo).',
}


def elec_fill(p):
    pan, mit, _ = ELECTORES[p]
    return PAN_ELEC if pan > mit else MIT_ELEC
def elec_note(p):
    pan, mit, nv = ELECTORES[p]
    return (f'Sin voto popular completo. Color según los electores (Wikipedia): {pan} para Avellaneda, {mit} para Mitre'
            + (f', {nv} no votó' if nv else '') + '.')
KEYS = [[PAN_ELEC, 'Electores de Avellaneda (Wikipedia), sin voto popular'], [MIT_ELEC, 'Electores de Mitre (Wikipedia), sin voto popular'], [PAN_PROVISORIO, 'Triunfo avellanedista provisorio según la prensa'], [MIT_PROVISORIO, 'Triunfo mitrista provisorio según la prensa'], [UNA_CIFRA[0], 'Solo cifra de Alsina–Avellaneda'], [UNA_CIFRA[1], 'Solo cifra de Mitre'], [GREY_O, 'Resultado objetado, nulo o sin elección'], [GREY_N, 'Sin datos de voto popular'],
        [GREY_T, 'Territorio sin elección']]


def fmt(v):
    return f'{int(v):,}'.replace(',', '.')


def mix(hexc, t):
    c = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(255 + (c[k] - 255) * t) for k in range(3))


unit_rec, unit_an = {}, {}
for i, u in enumerate(U):
    p = u['prov']
    if u['kind'] == 'malvinas':
        unit_rec[i] = dict(fill='#a9a9a9', lines=[], note='Islas Malvinas.')
        continue
    if p in TERR:
        txt = 'Territorio sin elección presidencial en 1874.'
        if p == 'Misiones':
            txt = 'Misiones estaba bajo jurisdicción de Corrientes hasta su federalización en 1881; sin dato propio.'
        unit_rec[i] = dict(fill=GREY_T, lines=[], note=txt)
        continue
    if p == 'Mendoza' and u['name'] in MENDOZA_PROVISORIO:
        unit_rec[i] = dict(fill=MIT_PROVISORIO, lines=[],
                           note='Provisorio. Telegrama de Nicanor Larrain del 14 de abril, publicado en La Nación del 17, p. 1. Declara un triunfo mitrista sin cifras.')
        continue
    if p == 'Corrientes' and u['name'] in CORRIENTES_PROVISORIO:
        alcance = (' El despacho se refiere a la ciudad, representada con el polígono departamental.'
                   if u['name'] == 'Capital' else '')
        unit_rec[i] = dict(fill=PAN_PROVISORIO, lines=[],
                           note='Provisorio. La Prensa del 14 de abril, p. 1, informa un triunfo de Avellaneda sin cifras.' + alcance)
        continue
    if p == 'San Luis' and u['name'] == 'La Capital':
        a, m = 92, 382
        d = a + m
        unit_rec[i] = dict(fill=MIT_PROVISORIO, lines=[[MIT, m, 100*m/d], [PAN, a, 100*a/d]],
                           note='Provisorio. Votos publicados para la ciudad de San Luis (La Prensa, 14 de abril, p. 1), ubicados en el departamento La Capital. El resto del departamento no está verificado.')
        unit_an[i] = dict(MIT=m, PAN=a, D=d)
        continue
    if p == 'La Rioja':
        key = next((k for k in RIOJA if norm(k) == norm(u['name'])), None)
        if key:
            m, a, imp, rot = RIOJA[key]
            nota = (f'Cuadro de un corresponsal mitrista, La Nación, 29 de mayo de 1874, p. 1 (rótulo del original: «{rot}»). '
                    'La Junta Escrutadora computó también las mesas impugnadas y dio la provincia a Avellaneda.')
            if imp:
                nota += f' Votos de Avellaneda en mesas impugnadas («mansillanas»): {fmt(imp)}, no incluidos en el porcentaje.'
            if m + a == 0:
                unit_rec[i] = dict(fill=GREY_O, lines=[[PAN, imp, 0]], note=nota + ' Sin votos en mesa legal según el cuadro.')
                continue
            d = m + a
            lines = sorted([[MIT, m, round(100 * m / d, 2)], [PAN, a, round(100 * a / d, 2)]], key=lambda x: -x[1])
            w = MIT if m > a else PAN
            unit_rec[i] = dict(lines=lines, w=w, q=round(100 * max(m, a) / d, 2), note=nota,
                               metrics=[['Votos en mesa legal', fmt(d)]] + ([['Impugnados', fmt(imp)]] if imp else []))
            unit_an[i] = dict(MIT=m, PAN=a, D=d)
            continue
    if p != 'Buenos Aires':
        unit_rec[i] = dict(fill=elec_fill(p), lines=[], note=elec_note(p))
        continue
    fw = fila_de.get(i)
    if not fw:
        unit_rec[i] = dict(fill=GREY_N, lines=[], note='Pendiente: esta unidad no figura en el recorte del cuadro del 17 de mayo.')
        continue
    f, why = fw
    a = int(f['alsina_avellaneda']) if f['alsina_avellaneda'] else None
    m = int(f['mitre']) if f['mitre'] else None
    lines = [[c, v, None] for c, v in ((MIT, m), (PAN, a)) if v is not None]
    nota = 'Cuadro del 17 de mayo de 1874 (prensa). Un guion en el original se conserva como cifra ausente, no como cero.'
    if f['nota']:
        nota += ' Marca del original: ' + f['nota'] + '.'
    if f['unidad'] in VARIANTES:
        nota += ' ' + VARIANTES[f['unidad']]
    if why:
        nota += ' ' + why
    if u.get('robado'):
        nota += ' Sin polígono en el censo de 1869: se usa el del censo de 1895, descontado de los partidos vecinos.'
    if f['nota'] in ('Nula', 'Falsificada', 'No hubo elección'):
        for l in lines:
            l[2] = None
        unit_rec[i] = dict(fill=GREY_O, lines=[[c, v, 0] for c, v, _ in lines], note=nota)
        continue
    if a is not None and m is not None and a + m > 0:
        d = a + m
        lines = [[c, v, round(100 * v / d, 2)] for c, v, _ in sorted(lines, key=lambda x: -x[1])]
        w = MIT if m > a else PAN if a > m else None
        rec = dict(lines=lines, metrics=[['Votos de ambos bandos', fmt(d)]], note=nota)
        if w:
            rec.update(w=w, q=round(100 * max(a, m) / d, 2))
        else:
            rec['fill'] = GREY_O
        unit_rec[i] = rec
        unit_an[i] = dict(MIT=m, PAN=a, D=d)
    else:
        c = MIT if m is not None else PAN
        unit_rec[i] = dict(fill=UNA_CIFRA[1] if c == MIT else UNA_CIFRA[0], lines=[[c, m if c == MIT else a, 0]],
                           note=nota + ' Solo hay cifra para un bando: no se calcula porcentaje ni ganador.')

prov_rec, prov_an = {}, {}
for p in PROVS:
    if p in TERR:
        prov_rec[p] = dict(fill=GREY_T, lines=[], note='Territorio sin elección presidencial.')
        continue
    pan, mit, nv = ELECTORES[p]
    if p == 'Buenos Aires':
        d = TOTAL_IMPRESO[PAN] + TOTAL_IMPRESO[MIT]
        prov_rec[p] = dict(lines=[[MIT, TOTAL_IMPRESO[MIT], round(100 * TOTAL_IMPRESO[MIT] / d, 2)],
                                  [PAN, TOTAL_IMPRESO[PAN], round(100 * TOTAL_IMPRESO[PAN] / d, 2)]],
                           metrics=[['Electores Mitre', str(mit)], ['Electores Avellaneda', str(pan)], ['No votaron', str(nv)]],
                           w=MIT, q=round(100 * TOTAL_IMPRESO[MIT] / d, 2),
                           note='Total impreso del cuadro del 17 de mayo de 1874 (ciudad y campaña), que coincide con el acta de la Junta Escrutadora '
                                'del 16 de mayo publicada en La Nación del 29 de mayo, p. 1 (14.971 contra 12.103, diferencia de 2.868). '
                                'Las filas del recorte suman menos: ver Fuentes y notas.')
        prov_an[p] = dict(MIT=TOTAL_IMPRESO[MIT], PAN=TOTAL_IMPRESO[PAN], D=d)
        continue
    if p == 'San Juan':
        d = SAN_JUAN['MIT'] + SAN_JUAN['PAN']
        prov_rec[p] = dict(lines=[[MIT, 1365, round(100 * 1365 / d, 2)], [PAN, 916, round(100 * 916 / d, 2)]],
                           w=MIT, q=round(100 * 1365 / d, 2), metrics=[['Votos', fmt(d)], ['Electores Mitre', '10']],
                           note='Acta de la Junta Escrutadora del 12 de mayo de 1874, publicada en La Nación del 2 de junio, p. 1. '
                                'Incluye 88 votos expresados del comicio de Albardón, cuyo registro anota 166 sufragantes; '
                                'la Junta dejó al Congreso los 78 restantes. Sin desglose por departamento.')
        prov_an[p] = dict(MIT=1365, PAN=916, D=d)
        continue
    if p == 'La Rioja':
        d = RIOJA_JUNTA['PAN'] + RIOJA_JUNTA['MIT']
        prov_rec[p] = dict(lines=[[PAN, 2278, round(100 * 2278 / d, 2)], [MIT, 1265, round(100 * 1265 / d, 2)]],
                           w=PAN, q=round(100 * 2278 / d, 2),
                           metrics=[['Avellaneda en mesas legales', '1.224'], ['Avellaneda impugnados', '1.054'], ['Electores Avellaneda', '8']],
                           note='Total de la Junta Escrutadora del 12 de mayo según el cuadro de La Nación del 29 de mayo de 1874: '
                                'Avellaneda 2.278 (1.224 en mesas legales y 1.054 en cinco mesas que los mitristas llaman apócrifas) y Mitre 1.265. '
                                'Sin las impugnadas, Mitre gana por 41. Costa del Medio (Tama), 196 para Avellaneda, no tiene polígono en 1869.')
        prov_an[p] = dict(MIT=1265, PAN=2278, D=d)
        continue
    pan, mit, nv = ELECTORES[p]
    prov_rec[p] = dict(lines=[], fill=elec_fill(p), note=elec_note(p),
                       metrics=[['Electores Avellaneda', str(pan)], ['Electores Mitre', str(mit)]] + ([['No votaron', str(nv)]] if nv else []))

# ---------------------------------------------------------------- resultado provisorio
POPULAR = {MIT: TOTAL_IMPRESO[MIT] + SAN_JUAN['MIT'] + RIOJA_JUNTA['MIT'],
           PAN: TOTAL_IMPRESO[PAN] + SAN_JUAN['PAN'] + RIOJA_JUNTA['PAN']}
d = POPULAR[PAN] + POPULAR[MIT]
cands = sorted([dict(code=c, votes=v, pct=round(100 * v / d, 2)) for c, v in POPULAR.items()], key=lambda c: -c['votes'])
slices = [dict(code=c['code'], v=c['votes']) for c in cands]
NAT_MET = [['Votos (Bs. As., San Juan y La Rioja)', fmt(d)], ['Electores Avellaneda', '145'], ['Electores Mitre', '79'], ['No votaron', '4']]
suma_a = sum(int(f['alsina_avellaneda'] or 0) for f in filas)
suma_m = sum(int(f['mitre'] or 0) for f in filas)
NOTE = ('Total provisorio (torta y barras): voto popular conocido, suma de los totales provinciales de Buenos Aires '
        f'(acta de la Junta: Mitre {fmt(TOTAL_IMPRESO[MIT])}, Alsina–Avellaneda {fmt(TOTAL_IMPRESO[PAN])}), San Juan (1.365 y 916) '
        f'y La Rioja (Junta: 1.265 y 2.278): Mitre {fmt(POPULAR[MIT])}, Avellaneda {fmt(POPULAR[PAN])}. '
        'Las provincias sin voto popular completo llevan el color de quien ganó sus electores según la Wikipedia. '
        'Avellaneda ganó el colegio electoral con 145 electores contra 79. '
        f'Las filas del recorte suman {fmt(suma_m)} para Mitre y {fmt(suma_a)} para Alsina–Avellaneda; la diferencia con el total impreso '
        'incluye filas alsinistas que el diario marca como falsificadas y partidos que el recorte no trae. Se conservan ambas cifras, sin ajustar. '
        'Buenos Aires por partido y parroquia: cuadro de prensa, con las marcas del original (falsificada, nula, sin elección). '
        'San Juan: acta de la Junta Escrutadora (Mitre 1.365, Avellaneda 916). La Rioja por departamento con el cuadro mitrista de La Nación del 29 de mayo; '
        'la provincia lleva el total de la Junta (Avellaneda 2.278, incluidos 1.054 votos impugnados, Mitre 1.265). '
        'El acta bonaerense del 16 de mayo confirma el total impreso. Patagones (55 para Mitre) sale del mismo cuadro del 17 de mayo. '
        'San Luis ciudad, cinco departamentos de Mendoza y tres unidades de Corrientes tienen datos provisorios de prensa. Las fichas indican la fuente y el alcance. '
        'Geometría: departamentos del censo de 1869 (Rodríguez y De Grande, CONICET); ciudad con las 14 parroquias de 1872-1886 ajustadas a esa base. '
        'General Alvear toma el polígono de 1895, descontado de Saladillo; Lomas de Zamora es La Paz y General Lavalle es Ajó en el censo de 1869.')


def stops_for(base, edges):
    ts = [0.12 + 0.88 * i / (len(edges) - 1) for i in range(len(edges))]
    return [mix(base, t) for t in ts], ["%d%%" % e for e in edges[:-1]] + ["+%d%%" % edges[-1]]


def bin_of(p, edges):
    i = 0
    while i + 1 < len(edges) and p >= edges[i + 1]:
        i += 1
    return i


def coropleta(code, edges):
    cols, labels = stops_for(CAND[code]['base'], edges)
    cols = CAND[code]['ramp']
    units = []
    for i in range(len(U)):
        r = unit_rec[i]
        a = unit_an.get(i)
        nr = {k: v for k, v in r.items() if k not in ('w', 'q', 'fill')}
        nr['fill'] = cols[bin_of(100 * a[code] / a['D'], edges)] if a else r.get('fill', GREY_N)
        if r.get('fill') in UNA_CIFRA or (r.get('fill') in PROVISORIOS and not a):
            nr['fill'] = SIN_PCT
        units.append(nr)
    prov = {}
    for p, r in prov_rec.items():
        nr = {k: v for k, v in r.items() if k not in ('w', 'q', 'fill')}
        nr['fill'] = cols[bin_of(100 * prov_an[p][code] / prov_an[p]['D'], edges)] if p in prov_an else r.get('fill', GREY_N)
        prov[p] = nr
    keys = [k for k in KEYS if k[0] not in (*UNA_CIFRA, *PROVISORIOS)] + [[SIN_PCT, 'Sin dos cifras publicadas']]
    return units, prov, dict(title='% ' + CAND[code]['n'] + ' (dos bandos)', stops=[[c, l] for c, l in zip(cols, labels)], bars=False, keys=keys)


national = dict(cands=cands, slices=slices, partp=None, metrics=NAT_MET)
MODES = [dict(id='gan', tile='GANÓ', note=NOTE, units=[unit_rec[i] for i in range(len(U))], prov=prov_rec,
              national=national, legend=dict(keys=KEYS))]
for code, tile in ((MIT, 'MITRE'), (PAN, 'PAN')):
    un, pv, lg = coropleta(code, list(range(20, 90, 10)))
    MODES.append(dict(id=code.lower(), tile=tile, note=NOTE, units=un, prov=pv, national=national, legend=lg))

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

disp = {i: (u['name'].title() if u['kind'] == 'partido' and u['name'].islower() else u['name']) for i, u in enumerate(U)}
for i, (f, why) in fila_de.items():
    disp[i] = f['unidad'] + (' (parroquia)' if U[i]['kind'] == 'parroquia' else '')
ds = dict(
    slug="elecciones_1874", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de Argentina de", year="1874",
    labels=dict(pie1="Voto conocido: Bs. As., S. Juan, La Rioja", pie2=""),
    exterior=False, candidates=CAND,
    sets={"1": dict(label="1874", subtitle="Voto popular publicado · deptos. 1869")},
    modes=MODES, insets=INSETS,
    territories=[dict(n=disp[i], p=u['prov'], k=u['kind']) for i, u in enumerate(U)],
    solid=SOLID,
    shade_k=[None, 1, .92, .84, .76, .68, .60],   # como 1928: muchos partidos pasan del 80 % y quedaban casi negros
)
json.dump(ds, open(HERE / "dataset_1874.json", "w", encoding="utf8"), ensure_ascii=False)

# ---------------------------------------------------------------- plantilla (parches de la familia 1912-1940)
tpl = TEMPLATE_SRC.read_text(encoding="utf8")


def sub(old, new, count=1):
    global tpl
    assert tpl.count(old) == count, (old, tpl.count(old))
    tpl = tpl.replace(old, new)


sub("<title>Atlas electoral</title>", "<title>Atlas electoral 1874</title>")
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
        .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":"))).replace("{{MODE}}", "gan"))
(HERE / "atlas_1874.html").write_text(html, encoding="utf8", newline="\n")

control = dict(
    unidades=len(U), filas_cuadro=len(filas), filas_con_poligono=len(fila_de), filas_sin_poligono=sin_poligono,
    partidos_robados_1895=robados,
    ganadores_por_unidad=dict(Counter(r.get('w') for r in unit_rec.values() if r.get('w'))),
    una_sola_cifra=sum(1 for r in unit_rec.values() if r.get('fill', '').startswith('#') and r.get('lines') and len(r['lines']) == 1 and 'w' not in r and r['fill'] != GREY_O),
    objetadas=sum(1 for r in unit_rec.values() if r.get('fill') == GREY_O),
    bonaerenses_sin_fila=[u['name'] for i, u in enumerate(U) if u['prov'] == 'Buenos Aires' and i not in fila_de],
    suma_filas=dict(MIT=suma_m, PAN=suma_a), total_impreso=TOTAL_IMPRESO,
    electores=dict(PAN=145, MIT=79, no_votaron=4),
)
(HERE / "CONTROL_1874.json").write_text(json.dumps(control, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(control, ensure_ascii=False))
