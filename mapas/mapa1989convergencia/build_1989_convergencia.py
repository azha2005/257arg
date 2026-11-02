"""Escenario 1989: Casella/Convergencia 55,51; Menem/PJ 30,10; Alsogaray 6,17."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent/'mapa1989/build_1989.py'
source = SOURCE.read_text(encoding='utf8')
adjust = '''
# Perfiles históricos por candidatura, renombrados para el escenario.
prior_mapping = dict(CODE2BLOC)
new_codes = {'ANG':'casella','MEN':'menem','ALS':'alsogaray'}
entries = list(unit_src.values())
for e in entries:
    p = collections.Counter()
    for c,v in e['P'].items():
        p[new_codes.get(prior_mapping.get(c),c)] += v
    e['P'] = dict(p)
CODE2BLOC.update(casella='ANG',menem='MEN',alsogaray='ALS')
for c,b in [('casella','ANG'),('menem','MEN'),('alsogaray','ALS')]:
    CAND['P_'+c] = dict(n=CAND[b]['n']+' · '+CAND[b]['sub'],base=CAND[b]['base'],minor=True)
codes = sorted({c for e in entries for c,v in e['P'].items() if v>0})
matrix = np.array([[e['P'].get(c,0) for c in codes] for e in entries],float)
rows = matrix.sum(axis=1)
original = matrix.sum(axis=0)
target = original.copy()
requested = dict(casella=.5551,menem=.3010,alsogaray=.0617)
rest = [j for j,c in enumerate(codes) if c not in requested]
target[rest] *= rows.sum()*.0822/original[rest].sum()
for c,v in requested.items(): target[codes.index(c)] = rows.sum()*v
for iteration in range(10000):
    matrix *= target/matrix.sum(axis=0)
    matrix *= (rows/matrix.sum(axis=1))[:,None]
    if np.max(np.abs(matrix.sum(axis=0)-target)) < 1e-7: break
else: raise RuntimeError('IPF no converge')
rounded = np.floor(matrix).astype(int)
for i in range(len(entries)):
    n = int(rows[i]-rounded[i].sum())
    order = np.argsort(-(matrix[i]-rounded[i]),kind='stable')
    rounded[i,order[:n]] += 1
for i,e in enumerate(entries):
    e['P'] = {c:int(rounded[i,j]) for j,c in enumerate(codes) if rounded[i,j]}
    e['pos'] = int(rows[i])
scenario_totals = dict(zip(codes,rounded.sum(axis=0).tolist()))
# El nuevo reparto puede dar ganadores que no ganaban en el atlas histórico.
extra_winners = set()
for e in entries:
    grouped = collections.Counter()
    for c,v in e['P'].items(): grouped[CODE2BLOC.get(c,'X_'+c)] += v
    winner = max(grouped,key=grouped.get)
    if winner.startswith('X_'): extra_winners.add(winner[2:])
for c in sorted(extra_winners):
    b = 'X_'+c
    CODE2BLOC[c] = b
    BLOCS.append(b)
    CAND[b] = dict(n=LABEL[c],sub='',base=COLOR[c],logo={'fr':'FR','ablo':'BLO'}.get(c,c.upper()))
    # mismo emblema que en los atlas de 1987–1994 (2-nov-2026, pedido del usuario: reusar logos ya usados)
    if c in ('fr','ablo'): CAND[b].update(_logo_raster({'fr':'Logo_Fuerza_Republicana.png','ablo':'Estrella_bloquista.png'}[c]))
for c,v in requested.items(): assert round(100*scenario_totals[c]/rows.sum(),2)==round(v*100,2)
assert np.all(rounded.sum(axis=1)==rows)
audit = dict(method='IPF sobre perfiles presidenciales históricos, con redondeo por mayores restos local',
             requested_percent={c:round(v*100,2) for c,v in requested.items()},
             other_percent=8.22,positive_votes=int(rows.sum()),units=len(entries),iterations=iteration+1,
             simulated_votes=scenario_totals,max_row_error=0,
             max_column_rounding_error=float(np.max(np.abs(rounded.sum(axis=0)-target))),
             prior='Casella: perfil histórico Angeloz/UCR+CFI; Menem: perfil histórico Menem/FREJUPO y aliados; Alsogaray: Alianza de Centro. PJR sin desagregación propia.')
json.dump(audit,open(SCENARIO_OUT/'control.json','w',encoding='utf8'),ensure_ascii=False,indent=2)
'''
source = source.replace('unit_rec, unit_an = {}, {}',adjust+'\nunit_rec, unit_an = {}, {}')
source = source.replace('dict(n="Eduardo Angeloz", sub="UCR + CFI", base="#e10019", logo="UCR")',
                        'dict(n="Juan Manuel Casella", sub="Convergencia · PJR + UCR", base="#e10019", logo="CON")')
source = source.replace('sub="Frejupo y aliados"','sub="Partido Justicialista"')
# Convergencia usa el escudo habitual de la UCR por pedido del usuario.
source = source.replace('CAND["MEN"].update(_logo_raster("Frejupo_logo_1989.png")); CAND["MEN"]["bl"] = 0.6',
                        'CAND["MEN"].update(_logo("Flag_of_the_Justicialist_Party_(square_version).svg"))')
source = source.replace('def _logo(fn, h=42):','def _logo(fn, h=50):')
source = source.replace('def _logo_raster(fn, px=360, h=42):','def _logo_raster(fn, px=360, h=50):')
source = source.replace('cands, slices, partp, NAT_MET = wikitop.national(1989)', '''
_, _, partp, _ = wikitop.national(1989)
win = {r.get('w') for i,r in unit_rec.items() if U[i]['name']!='Islas Malvinas'}
cands = [dict(code=b,votes=sum(v for c,v in scenario_totals.items() if CODE2BLOC.get(c)==b),pct=0) for b in BLOCS if b in win]
cands.sort(key=lambda c:-c['votes'])
for c in cands: c['pct'] = round(100*c['votes']/sum(scenario_totals.values()),2)
slices = [dict(code=c['code'],v=c['votes']) for c in cands]
slices.append(dict(fill='#717274',v=sum(scenario_totals.values())-sum(c['votes'] for c in cands)))
NAT_MET = [['Escenario','Hipotético'],['Casella','55,51 %'],['Menem','30,10 %'],['Alsogaray','6,17 %'],['Otros','8,22 %']]
''')
start = source.index('NOTE = (')
end = source.index('\nKEYS = []',start)
source = source[:start]+'''NOTE = ("ESCENARIO HIPOTÉTICO: Casella / Convergencia (PJR + UCR) 55,51 %; Menem / PJ 30,10 %; Alsogaray 6,17 %; otros 8,22 %. "
        "Distribución estimada mediante IPF sobre los perfiles territoriales de 1989: Casella usa el perfil de Angeloz; PJR no se observa por separado. "
        "Menem usa el perfil del FREJUPO histórico, renombrado PJ por el escenario. Positivos locales conservados; no son resultados históricos. "
        "Base: Ernesto Calvo, con las correcciones y reservas del atlas 1989. Blancos, nulos y padrón históricos; geometría de 1980 y Capital aproximada.")
'''+source[end:]
source = source.replace('"Suma de los departamentos de la base de Ernesto Calvo."','"Escenario hipotético: suma de unidades ajustadas por IPF."')
source = source.replace('unit_rec[i] = rec_from(a, " ".join(extras) or None)','unit_rec[i] = rec_from(a, "Escenario hipotético estimado mediante IPF. " + " ".join(extras))')
source = source.replace('("ang", "ANG", lambda','("ang", "CAS", lambda')
source = source.replace('"% Angeloz (UCR + CFI)"','"% Casella · Convergencia"')
source = source.replace('"% Menem - Duhalde"','"% Menem · PJ"')
source = source.replace('slug="elecciones_1989"','slug="escenario_1989_convergencia"')
source = source.replace('subtitle="Base de E. Calvo · deptos. de 1980"','subtitle="Hipótesis · Convergencia"')
source = source.replace('os.path.join(HERE, "dataset_1989.json")','str(SCENARIO_OUT/"dataset_1989_convergencia.json")')
source = source.replace('os.path.join(HERE, "atlas_1989.html")','str(SCENARIO_OUT/"atlas_1989_convergencia.html")')
exec(compile(source,str(SOURCE),'exec'),{'__file__':str(SOURCE),'__name__':'__main__','SCENARIO_OUT':HERE})
