"""FREJULI + renovadores, con 8,6 puntos nacionales transferidos a UCR."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'mapa1985/build_1985.py'
source = SOURCE.read_text(encoding='utf8')

adjust = '''
# Unión de las ramas justicialista y renovadora de 1985.
entries = list(unit_src.values())
def is_peronist(c, e):
    return CODE2BLOC.get(c) in ('PJ','REN') or (c == 'flib' and e['prov'] == 'Capital Federal')
original_per = np.array([sum(v for c,v in e['P'].items() if is_peronist(c,e)) for e in entries], dtype=int)
positive = sum(e['pos'] if e['pos'] is not None else sum(e['P'].values()) for e in entries)
transfer = round(positive * .086)
raw = original_per * (transfer / original_per.sum())
moved = np.floor(raw).astype(int)
order = np.argsort(-(raw-moved), kind='stable')
moved[order[:transfer-int(moved.sum())]] += 1
assert int(moved.sum()) == transfer
assert np.all(moved <= original_per)
audit_rows = []
for e, before, delta in zip(entries, original_per, moved):
    old_total = sum(e['P'].values())
    p = {c:v for c,v in e['P'].items() if not is_peronist(c,e)}
    p['frejuli'] = int(before-delta)
    p['ucr'] = p.get('ucr',0) + int(delta)
    assert sum(p.values()) == old_total
    e['P'] = p
    audit_rows.append(dict(provincia=e['prov'],unidad=e['name'],peronismo_original=int(before),transferido=int(delta),peronismo_final=int(before-delta)))
CODE2BLOC = {c: ('PJ' if b=='REN' else b) for c,b in CODE2BLOC.items()}
BLOCS.remove('REN')
CAND['PJ'].update(n='FREJULI + Renovadores', sub='Peronismo unido')
CAND['P_frejuli'].update(n='FREJULI + Frente Renovador',base='#318ce7')
json.dump(dict(positive_votes_base=positive,transferred_votes_base=transfer,transfer_points=8.6,
              method='Quita proporcional al voto peronista local, restos mayores al total nacional',
              units=audit_rows),open(SCENARIO_OUT/'control.json','w',encoding='utf8'),ensure_ascii=False,indent=2)
'''
source = source.replace('unit_rec, unit_an = {}, {}', adjust + '\nunit_rec, unit_an = {}, {}')
source = source.replace('cands, slices, partp, NAT_MET = wikitop.national(1985)', '''
cands, slices, partp, NAT_MET = wikitop.national(1985)
wiki = wikitop.WIKI[1985]
delta = round(wiki['positivos'] * .086)
national_votes = {c['code']:c['votes'] for c in cands}
national_votes['UCR'] += delta
national_votes['PJ'] += national_votes.pop('REN') - delta
winners = {r.get('w') for i,r in unit_rec.items() if U[i]['name'] != 'Islas Malvinas'}
cands = [dict(code=c,votes=v,pct=round(100*v/wiki['positivos'],2)) for c,v in national_votes.items() if c in winners]
cands.sort(key=lambda c:-c['votes'])
slices = [dict(code=c['code'],v=c['votes']) for c in cands]
slices.append(dict(fill='#717274',v=wiki['positivos']-sum(c['votes'] for c in cands)))
NAT_MET = [['Escenario','Hipotético'],['Traspaso a UCR','8,6 puntos'], *NAT_MET]
''')
start = source.index('NOTE = (')
end = source.index('\nKEYS = []', start)
source = source[:start] + '''NOTE = ("ESCENARIO HIPOTÉTICO 1985: FREJULI/PJ + Frente Renovador y aliados. "
        "Se transfieren 8,6 puntos nacionales del peronismo unido a la UCR, con quita proporcional a los votos peronistas de cada unidad. "
        "Las demás fuerzas, los positivos locales, los blancos, los nulos y el padrón se conservan. "
        "Base territorial: Ernesto Calvo; nacional: tabla histórica de Wikipedia modificada por el escenario. "
        "Geometría de 1980 y Capital aproximada. Es una simulación, no transferencias individuales observadas.")
''' + source[end:]
source = source.replace('"Suma de los departamentos de la base de Ernesto Calvo."', '"Escenario hipotético: suma de unidades con traspaso proporcional a UCR."')
source = source.replace('unit_rec[i] = rec_from(a, " ".join(extras) or None)', 'unit_rec[i] = rec_from(a, "Escenario hipotético: peronismo unido menos traspaso proporcional a UCR. " + " ".join(extras))')
source = '\n'.join(line for line in source.split('\n') if not line.strip().startswith('("ren", "REN", lambda'))
source = source.replace('"% PJ (FREJULI y afines)"', '"% FREJULI + Frente Renovador"')
source = source.replace('slug="elecciones_1985"', 'slug="escenario_1985_peronismo_menos_86"')
source = source.replace('subtitle="Base de E. Calvo · deptos. de 1980"', 'subtitle="Hipótesis · PJ unido −8,6 pp"')
# Ajustar emblemas al alto máximo real para evitar cortes en leyendas cortas.
source = source.replace('def _logo(fn, h=42):', 'def _logo(fn, h=50):')
source = source.replace('def _logo_raster(fn, px=360, h=42):', 'def _logo_raster(fn, px=360, h=50):')
source = source.replace('os.path.join(HERE, "dataset_1985.json")', 'str(SCENARIO_OUT / "dataset_1985_peronismo.json")')
source = source.replace('os.path.join(HERE, "atlas_1985.html")', 'str(SCENARIO_OUT / "atlas_1985_peronismo.html")')
exec(compile(source, str(SOURCE), 'exec'), {'__file__':str(SOURCE),'__name__':'__main__','SCENARIO_OUT':HERE})
