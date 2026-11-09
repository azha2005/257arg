"""Atlas presidencial de 1868: provincias coloreadas por sus electores (Wikipedia).

Reutiliza el visor, la geometría de 1869 y los recuadros del atlas de 1874.
Correr: python mapas/mapa1868/build_1868.py (después de construir mapa1874).
"""
import csv
import json
import unicodedata
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'mapa1874'
data = json.loads((BASE / 'dataset_1874.json').read_text(encoding='utf-8'))
data.update(slug='elecciones_1868', year='1868')
data['sets']['1'].update(label='1868', subtitle='Electores y voto bonaerense')
data['labels']['pie1'] = 'Voto conocido: solo Buenos Aires'

# Colores de la Wikipedia, con Sarmiento en gris pizarra (el negro del artículo tapa los bordes).
data['candidates'] = {
    'SAR': dict(n='Domingo F. Sarmiento', sub='Independiente · Alsina', base='#3d4652', logo='DFS',
                ramp=['#c9ced5', '#aab2bc', '#8c95a2', '#6f7987', '#56606d', '#3d4652', '#272e37']),
    'URQ': dict(n='Justo José de Urquiza', sub='Partido Federal', base='#b31b1b', logo='PF',
                ramp=['#f2c9c9', '#e6a3a3', '#d97b7b', '#cc5252', '#b31b1b', '#8f1515', '#6b1010']),
    'ELI': dict(n='Rufino de Elizalde', sub='Partido Nacionalista', base='#35aae0', logo='PN',
                ramp=['#d3ecf8', '#b4def3', '#93d0ee', '#6fc0e8', '#35aae0', '#2389b8', '#196a8f']),
}
# Tabla «Resultados por Provincia» del artículo de la Wikipedia: presidente.
# [Sarmiento, Urquiza, Elizalde, Rawson, Vélez Sarsfield], no votaron.
ELECTORES = {'Buenos Aires': ((24, 0, 0, 3, 1), 0), 'Catamarca': ((0, 0, 10, 0, 0), 0),
             'Córdoba': ((16, 0, 0, 0, 0), 0), 'Corrientes': (None, 12), 'Entre Ríos': ((0, 8, 0, 0, 0), 0),
             'Jujuy': ((7, 0, 0, 0, 0), 1), 'La Rioja': ((6, 0, 0, 0, 0), 2), 'Mendoza': ((10, 0, 0, 0, 0), 0),
             'Salta': ((0, 10, 0, 0, 0), 0), 'San Juan': ((8, 0, 0, 0, 0), 0), 'San Luis': ((8, 0, 0, 0, 0), 0),
             'Santa Fe': ((0, 8, 0, 0, 0), 0), 'Santiago del Estero': ((0, 0, 12, 0, 0), 0), 'Tucumán': (None, 10)}
TOT = [sum(v[0][k] for v in ELECTORES.values() if v[0]) for k in range(5)]
assert TOT == [79, 26, 22, 3, 1], TOT
NOMBRES = ['Sarmiento', 'Urquiza', 'Elizalde', 'Rawson', 'Vélez Sarsfield']
CODES = ['SAR', 'URQ', 'ELI']
unknown, land, grey = '#e6dcc3', '#cfcfcf', '#9a9a9a'
SAN_LUIS = (' Voto popular: «La lista de Electores favorable al Dr. Elizalde triunfó en la ciudad y cinco Departamentos [...] '
            'La lista de Elizalde triunfó por 163 votos» (Nación Argentina, 30 de abril de 1868, p. 1), con denuncias de registros falsos '
            'de los sarmientistas. Sin cifras por lista. Los 8 electores votaron después por Sarmiento.')
TUC_E = '#d3ecf8'
CIUDAD = (' Voto popular en la ciudad (Nación Argentina, 17 de abril de 1868, p. 2, «Eleccion de electores»): '
          'la lista ganadora encabeza con 1.186 votos por elector y la otra con 862; algunos candidatos tienen cifras intermedias '
          '(1.034, 977, 789, 720). No se escrutaron Catedral al Norte y Barracas al Norte. No hay cuadro por parroquia ni por partido.')


def prov_rec(p):
    v, nv = ELECTORES[p]
    if v is None:
        if p == 'Tucumán':
            return dict(fill=TUC_E, lines=[], metrics=[['Electores', str(nv)]],
                        note='La Wikipedia no computa sus electores: las actas del colegio del 12 de junio se extraviaron en el correo y llegaron '
                             'al Congreso después del escrutinio. Voto popular: ganó la lista del club El Pueblo (Elizalde-Paunero) contra el Club '
                             'Sarmiento, que protestó; la Legislatura proclamó a sus 10 electores el 14 de mayo (Amenta, sobre El Pueblo de abril y mayo '
                             'de 1868; Nación Argentina, 30 de abril de 1868, p. 1). Tono claro de Elizalde, sin cifras.')
        txt = 'Corrientes no votó (Wikipedia).'
        return dict(fill=grey, lines=[], note=txt,
                    metrics=[['Electores', str(nv)]])
    tot = sum(v)
    lines = [[CODES[k], n, round(100 * n / tot, 2)] for k, n in enumerate(v[:3]) if n]
    w = CODES[max(range(3), key=lambda k: v[k])]
    met = [[f'Electores {NOMBRES[k]}', str(n)] for k, n in enumerate(v) if n] + ([['No votaron', str(nv)]] if nv else [])
    note = 'Color según los electores (Wikipedia). Sin voto popular por departamento.'
    if p == 'Buenos Aires':
        note += CIUDAD
    if p == 'San Luis':
        note += SAN_LUIS
    return dict(lines=sorted(lines, key=lambda x: -x[1]), w=w, q=round(100 * max(v[:3]) / tot, 2), metrics=met, note=note)


provinces = {}
for p, r in data['modes'][0]['prov'].items():
    provinces[p] = prov_rec(p) if p in ELECTORES else dict(fill=land, lines=[], note='Territorio sin elección presidencial en 1868.')
# Buenos Aires: voto popular por lista. Club Popular = autonomistas de Alsina (sus electores votaron
# a Sarmiento); Club Libertad = nacionalistas mitristas (Elizalde).
FUENTE = 'Nación Argentina, 21 de abril de 1868, p. 2, «Elecciones en la Campaña».'
CITY = (1186, 862)      # cabezas de lista, 17 de abril
PRINTED = (4273, 739)   # total impreso del cuadro de campaña
SARL, ELIL, NOV = '#aab2bc', '#93d0ee', '#6f6f6f'


def key(n):
    return ''.join(c for c in unicodedata.normalize('NFD', n.lower()) if not unicodedata.combining(c))


rows = {key(r['unidad']): r for r in csv.DictReader(open(HERE / 'campana_21abril1868.csv', encoding='utf-8'))}
row_sum = [sum(int(r[c]) for r in rows.values() if r[c] not in ('', '-')) for c in ('popular', 'libertad')]
LBL = {'SAR': 'Club Popular', 'ELI': 'Club Libertad'}


def fmt(v):
    return f'{v:,}'.replace(',', '.')


def lista(pop, lib, note):
    d = pop + lib
    lines = sorted([[c, v, round(100 * v / d, 2)] for c, v in (('SAR', pop), ('ELI', lib))], key=lambda x: -x[1])
    return dict(lines=lines, w=lines[0][0], q=lines[0][2], metrics=[['Votos de ambas listas', fmt(d)]], note=note)


city_rec = lista(*CITY, 'Total de toda la ciudad, no por parroquia (Nación Argentina, 17 de abril de 1868, p. 2, «Eleccion de electores»). '
                 'Cabezas de lista: Club Popular 1.186 votos por elector, Club Libertad 862; algunos candidatos tienen cifras intermedias '
                 '(1.034, 977, 789, 720). No se escrutaron Catedral al Norte y Barracas al Norte.')
units, matched = [], set()
for t, prev in zip(data['territories'], data['modes'][0]['units']):
    if t['k'] == 'malvinas' or prev.get('fill') == land:
        units.append(dict(fill=prev.get('fill', land), lines=[], note=prev['note'].replace('1874', '1868')))
    elif t['k'] == 'parroquia':
        units.append(dict(city_rec))
    elif t['p'] == 'Buenos Aires':
        r = rows.get(key(t['n']))
        if not r:
            units.append(dict(fill=unknown, lines=[], note='Sin fila en el cuadro de campaña del 21 de abril.'))
            continue
        matched.add(key(t['n']))
        note = (f'Texto del original: «{r["literal"]}».' if '24 de abril' in r['literal'] else f'{FUENTE} Texto del original: «{r["literal"]}».')
        if r['popular'] == '-':
            units.append(dict(fill=NOV, lines=[], note=note))
        elif r['popular'] and r['libertad']:
            units.append(lista(int(r['popular']), int(r['libertad']), note))
        else:
            c, v = ('SAR', int(r['popular'])) if r['popular'] else ('ELI', int(r['libertad']))
            units.append(dict(fill=SARL if c == 'SAR' else ELIL, lines=[[c, v, None]],
                              note=note + f' Solo se publica la cifra de la lista ganadora ({LBL[c]}).'))
    else:
        units.append(dict(provinces[t['p']]))
assert matched == set(rows), set(rows) - matched
data['solid'] = [p for p in ELECTORES if p != 'Buenos Aires']
provinces['Buenos Aires']['note'] = ('Color según los electores (Wikipedia). Voto popular: ciudad 1.186 Club Popular y 862 Club Libertad '
    f'(cabezas de lista); campaña, {FUENTE} Las filas suman {fmt(row_sum[0])} y {fmt(row_sum[1])}; el diario imprime 4.273 y 739.')

T = sum(TOT)
POP = (CITY[0] + PRINTED[0], CITY[1] + PRINTED[1])
PT = sum(POP)
note = ('Voto popular solo para Buenos Aires. Ciudad como un total (Nación Argentina, 17 de abril: cabezas de lista 1.186 y 862); '
        'campaña por partido (Nación Argentina, 21 de abril). Club Popular (autonomistas de Alsina, cuyos electores votaron a Sarmiento) '
        'en el color de Sarmiento; Club Libertad (mitristas) en el de Elizalde. Donde el diario solo da la cifra de la lista ganadora, tono claro sin porcentaje. '
        f'Torta y barras: ciudad más los totales impresos de campaña (4.273 y 739): {fmt(POP[0])} y {fmt(POP[1])}. '
        f'Las filas de campaña suman {fmt(row_sum[0])} y {fmt(row_sum[1])}; no cierran con lo impreso y se conservan sin ajustar. '
        'Las demás provincias llevan el color del candidato que ganó sus electores según la Wikipedia (Sarmiento 79, Urquiza 26, Elizalde 22, '
        'Rawson 3, Vélez Sarsfield 1). Corrientes no votó (gris). Tucumán, en tono claro de Elizalde: ganó su lista y la Legislatura proclamó a sus electores, pero las actas del colegio llegaron tarde y la Wikipedia no las computa. '
        'Geometría: departamentos del censo de 1869 (Rodríguez y De Grande, CONICET), reutilizada del atlas de 1874.')
national = dict(cands=[dict(code=c, votes=POP[k], pct=round(100 * POP[k] / PT, 2)) for k, c in enumerate(('SAR', 'ELI'))] + [dict(code='URQ', votes=0, pct=0)],
                slices=[dict(code=c, v=POP[k]) for k, c in enumerate(('SAR', 'ELI'))],
                metrics=[['Votos conocidos (Bs. As.)', fmt(PT)], ['Electores Sarmiento', '79'], ['Electores Urquiza', '26'],
                         ['Electores Elizalde', '22'], ['No votaron', '25']], partp=None)
keys = [[SARL, 'Solo cifra del Club Popular'], [ELIL, 'Solo cifra del Club Libertad'], [NOV, 'No hubo elección'], [grey, 'No votó'], [TUC_E, 'Elizalde: lista ganadora sin actas del colegio (Tucumán)'], [unknown, 'Sin datos'], [land, 'Territorio sin elección']]
data['modes'] = [dict(id='gan', tile='GANÓ', note=note, units=units, prov=provinces, national=national, legend=dict(keys=keys))]
html = (BASE / 'atlas_1874.html').read_text(encoding='utf-8')
html = html.replace('<title>Atlas electoral 1874</title>', '<title>Atlas electoral 1868</title>')
payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
html, n = re.subn(r'^const DATA=.*;$', lambda _: f'const DATA={payload};', html, flags=re.M)
assert n == 1
(HERE / 'dataset_1868.json').write_text(payload, encoding='utf-8')
(HERE / 'atlas_1868.html').write_text(html, encoding='utf-8')
print('electores', TOT, 'provincias', len(ELECTORES))
