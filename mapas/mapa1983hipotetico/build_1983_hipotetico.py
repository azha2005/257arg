"""Escenario solicitado: Alfonsín 41,58 %, Luder 50,33 % (positivos).

Reutiliza el constructor histórico, sin modificar sus archivos ni resultados.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'mapa1983' / 'build_1983.py'
source = SOURCE.read_text(encoding='utf8')

adjust = '''
# Ajuste biproporcional: conserva ceros y totales positivos por unidad.
codes = sorted({c for e in unit_src.values() for c in e['P']})
entries = list(unit_src.values())
matrix = np.array([[e['P'].get(c, 0) for c in codes] for e in entries], float)
rows = matrix.sum(axis=1)
original = matrix.sum(axis=0)
target = original.copy()
rest = [j for j, c in enumerate(codes) if c not in ('ucr', 'pj')]
target[rest] *= rows.sum() * .0809 / original[rest].sum()
target[codes.index('ucr')] = rows.sum() * .4158
target[codes.index('pj')] = rows.sum() * .5033
for iteration in range(10000):
    matrix *= target / matrix.sum(axis=0)
    matrix *= (rows / matrix.sum(axis=1))[:, None]
    if np.max(np.abs(matrix.sum(axis=0) - target)) < 1e-7:
        break
else:
    raise RuntimeError('IPF no converge')
# Redondeo por unidad: conserva exactamente sus positivos.
rounded = np.floor(matrix).astype(int)
for i in range(len(entries)):
    n = int(rows[i] - rounded[i].sum())
    order = np.argsort(-(matrix[i] - rounded[i]), kind='stable')
    rounded[i, order[:n]] += 1
for i, e in enumerate(entries):
    e['P'] = {c: int(rounded[i,j]) for j,c in enumerate(codes) if rounded[i,j]}
    e['pos'] = int(rows[i])
scenario_totals = dict(zip(codes, rounded.sum(axis=0).tolist()))
for c, p in [('ucr', 41.58), ('pj', 50.33)]:
    assert round(100 * scenario_totals[c] / rows.sum(), 2) == p
audit = dict(method='IPF con ceros estructurales y redondeo por unidad',
             iterations=iteration+1, units=len(entries), positive_votes=int(rows.sum()),
             requested_percent=dict(ucr=41.58,pj=50.33,others=8.09),
             simulated_votes=scenario_totals,
             max_column_rounding_error=float(np.max(np.abs(rounded.sum(axis=0)-target))),
             max_row_error=int(np.max(np.abs(rounded.sum(axis=1)-rows))))
json.dump(audit, open(SCENARIO_OUT / 'control.json', 'w', encoding='utf8'), ensure_ascii=False, indent=2)
'''
source = source.replace('unit_rec, unit_an = {}, {}', adjust + '\nunit_rec, unit_an = {}, {}')
source = source.replace('cands, slices, partp, NAT_MET = wikitop.national(1983)', '''
_, _, partp, NAT_MET = wikitop.national(1983)
win = {r.get('w') for i,r in unit_rec.items() if U[i]['name'] != 'Islas Malvinas'}
cands = [dict(code=b, votes=sum(v for c,v in scenario_totals.items() if CODE2BLOC.get(c)==b), pct=0) for b in BLOCS if b in win]
cands.sort(key=lambda c: -c['votes'])
for c in cands: c['pct'] = round(100*c['votes']/sum(scenario_totals.values()),2)
slices = [dict(code=c['code'],v=c['votes']) for c in cands]
slices.append(dict(fill='#717274',v=sum(scenario_totals.values())-sum(c['votes'] for c in cands)))
NAT_MET = [['Escenario', 'Hipotético'], ['Alfonsín', '41,58 %'], ['Luder', '50,33 %'], ['Otras fuerzas', '8,09 %']]
''')
start = source.index('NOTE = (')
end = source.index('\nKEYS = []', start)
source = source[:start] + '''NOTE = ("ESCENARIO HIPOTÉTICO: Alfonsín 41,58 %, Luder 50,33 %, otras fuerzas 8,09 %. "
        "Distribución territorial estimada mediante ajuste biproporcional (IPF) de la base de Ernesto Calvo de 1983; "
        "conserva los positivos de cada departamento y circunscripción. No son resultados históricos ni transferencias observadas. "
        "Blancos, nulos, padrón y participación se conservan de la base histórica. Geometría de 1980 y Capital aproximada.")
''' + source[end:]
source = source.replace('"Suma de los departamentos de la base de Ernesto Calvo."', '"Escenario hipotético: suma de departamentos ajustados por IPF."')
source = source.replace('unit_rec[i] = rec_from(a, " ".join(extras) or None)', 'unit_rec[i] = rec_from(a, "Escenario hipotético estimado por IPF. " + " ".join(extras))')
source = source.replace('slug="elecciones_1983"', 'slug="escenario_1983_4158_5033"')
# Título habitual; la aclaración hipotética sigue en subtítulo y fuentes.
source = source.replace('CAND["PJ"].update(_logo("Flag_of_the_Justicialist_Party_(square_version).svg"))', '''CAND["PJ"].update(_logo_raster("Luder_Presidente_transparente.png", px=1280, h=50))
CAND["PJ"].update(bl=170 / (50 * CAND["PJ"]["ar"]), logoWidth=180)''')
source = source.replace('_logo_raster("Pacto_Autonomista_Liberal_PL_PA.png")', '_logo_raster("Pacto_Autonomista_Liberal_PL_PA.png", h=50)')
source = source.replace('subtitle="Base de E. Calvo · deptos. de 1980"', 'subtitle="Hipótesis · ajuste IPF"')
source = source.replace('n="Pacto Autonomista - Liberal"', 'n="Autonomista–Liberal"')
source = source.replace('os.path.join(HERE, "dataset_1983.json")', 'str(SCENARIO_OUT / "dataset_1983_hipotetico.json")')
source = source.replace('os.path.join(HERE, "atlas_1983.html")', 'str(SCENARIO_OUT / "atlas_1983_hipotetico.html")')
source = source.replace('<title>Elecciones presidenciales 1983</title>', '<title>Escenario hipotético 1983 · Alfonsín 41,58 / Luder 50,33</title>')
# Dar al rótulo ancho espacio propio, sin tocar colores ni los otros emblemas.
source = source.replace('html = (tpl.replace', '''tpl = tpl.replace('x:93,y,width:110,height:h,overflow:', 'x:93,y,width:C.logoWidth||110,height:h,overflow:')
html = (tpl.replace''')
exec(compile(source, str(SOURCE), 'exec'), {'__file__': str(SOURCE), '__name__': '__main__', 'SCENARIO_OUT': HERE})
