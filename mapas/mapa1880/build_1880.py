"""Build the 1880 atlas with the verified 1874 viewer and historical geometry."""
import csv
import json
import re
import unicodedata
from pathlib import Path

import xlrd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = HERE.parent / 'mapa1874'
data = json.loads((BASE / 'dataset_1874.json').read_text(encoding='utf-8'))
data.update(slug='elecciones_1880', year='1880')
data['sets']['1'].update(label='1880', subtitle='11 de abril · Voto popular')
data['labels']['pie1'] = 'Voto popular conocido: Bs. As. y Tucumán'
# Keep the viewer's internal identifiers and the palette of the 1874 atlas.
data['candidates']['PAN'].update(n='Julio A. Roca', sub='PAN · irigoyenistas en Bs. As.', logo='PAN')
data['candidates']['MIT'].update(n='Carlos Tejedor', sub='Liberales conciliados', logo='TEJ')
data['solid'] = ['Catamarca', 'Córdoba', 'Corrientes', 'Entre Ríos', 'La Rioja', 'San Juan', 'Salta', 'Jujuy',
                 'San Luis', 'Santa Fe', 'Santiago del Estero', 'Tucumán']
# Electores por provincia: tabla «Resultados por Provincia» de la Wikipedia (Roca, Tejedor, no votaron).
ELECTORES = {'Buenos Aires': (0, 53, 1), 'Catamarca': (12, 0, 0), 'Córdoba': (26, 0, 0), 'Corrientes': (0, 16, 0),
             'Entre Ríos': (18, 0, 0), 'Jujuy': (7, 1, 0), 'La Rioja': (7, 0, 1), 'Mendoza': (10, 0, 0),
             'Salta': (12, 0, 0), 'San Juan': (10, 0, 0), 'San Luis': (9, 0, 1), 'Santa Fe': (12, 0, 0),
             'Santiago del Estero': (18, 0, 0), 'Tucumán': (14, 0, 0)}
assert sum(v[0] for v in ELECTORES.values()) == 155 and sum(v[1] for v in ELECTORES.values()) == 70

def key(name):
    return ''.join(c for c in unicodedata.normalize('NFD', name.lower())
                   if not unicodedata.combining(c)).removesuffix(' (parroquia)')

aliases = {'flores': 'san jose de flores', 'matanzas': 'la matanza',
           'giles': 'san andres de giles', '9 de julio': 'nueve de julio',
           'brandzen': 'brandsen',
           'alvear': 'general alvear', 'ajo': 'general lavalle'}
with (HERE / 'campana_13abril1880.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = {aliases.get(key(r['unidad']), key(r['unidad'])): r for r in csv.DictReader(f)}
book = ROOT / 'datos/canton_ciudad/cd/(9) CF1880PRV.xls'
sheet = xlrd.open_workbook(book).sheet_by_index(0)
city = {key(name).replace('al sud', 'al sur'): (int(m), int(a))
        for _, name, _, m, a in (sheet.row_values(i) for i in range(sheet.nrows))
        if isinstance(m, float) and name.strip() != 'TOTAL'}

unknown, land, light, dark = '#e6dcc3', '#cfcfcf', '#91bdd1', '#687bb5'
ROCA_ELEC, TEJ_ELEC = '#d3e6f4', '#a9b4dc'
def elec(p, note=''):
    roca, tej, nv = ELECTORES[p]
    txt = (f'Color según los electores (Wikipedia): {roca} para Roca, {tej} para Tejedor' + (f', {nv} no votó' if nv else '') + '.')
    return dict(fill=TEJ_ELEC if tej > roca else ROCA_ELEC, lines=[], note=(note + ' ' + txt).strip(),
                metrics=[['Electores Roca', str(roca)], ['Electores Tejedor', str(tej)]])
def numbers(m, a, note):
    total = m + a
    return dict(w='MIT' if m > a else 'PAN', q=round(max(m, a)*100/total, 2),
                lines=[[c,v,round(v*100/total,2)] for c,v in [('MIT',m),('PAN',a)]], note=note)

def provisional(fill, note):
    return dict(fill=fill, lines=[], note=note)

source = 'La Prensa, 13 de abril de 1880, p. 1.'
empty = provisional(unknown, 'Sin dato de voto popular.')
provinces = {}
for p in data['modes'][0]['prov']:
    if p in data['solid']:
        winner = 'Tejedor' if p == 'Corrientes' else 'Roca'
        provinces[p] = provisional(dark if winner == 'Tejedor' else light,
                                   f'Triunfo provincial provisorio de {winner}, sin cifras. {source}')
    else:
        provinces[p] = empty
for province in ('Salta', 'Jujuy'):
    provinces[province] = provisional(light, 'Triunfo provisorio de Roca sin oposición presentada, según La Prensa, 14 de abril de 1880, p. 1. Sin cifras.')
provinces['La Rioja'] = provisional(
    dark, 'Triunfo provisorio de la lista tejedorista según el despacho del escrutinio del 12 de mayo '
    '(El Bien Público, 15 de mayo de 1880). Sin cifras. El posterior voto del Colegio Electoral se registra por separado.')
provinces['Salta']['note'] += (' La Reforma (Salta), 22 de mayo de 1880, p. 3, publica el acta de la Junta Escrutadora '
    'del 12 de mayo: proclama a los 12 electores roquistas por mayoría y menciona votos dispersos a otros 12 ciudadanos, sin cifras '
    '(lectura aportada; el escaneo no está en el repositorio).')
provinces['Tucumán'] = dict(fill=light, lines=[], metrics=[['Votos roquistas', '2.184']],
    note='Triunfo de los electores roquistas con 2.184 votos en toda la provincia, sin lista opositora. '
         'Navajas, tesis doctoral, p. 178, nota 385, que cita AHT, Archivo de la Legislatura, caja 33, legajo 2242. Sin desglose por departamento.')
provinces['Santiago del Estero']['note'] += (' Telegrama del 13 de abril a El Combate (El Porteño, 14 de abril): la lista oficial '
    '«no tuvo 50 votantes» y aparece en la prensa con más de 700 en el departamento Capital.')
provinces['Córdoba']['note'] += (' Telegrama del 13 de abril a La Libertad (El Porteño, 14 de abril): 200 votantes en la ciudad, '
    'con soldados, según el escrutinio.')
provinces['Corrientes']['note'] += (' Telegrama de M. G. Morel del 12 de abril: «ni un voto en contra en toda la provincia»; '
    'El Porteño del 14 de abril atribuye 110 votantes al parte telegráfico. Los dos partes contradicen el color tejedorista, que se conserva.')
provinces['Mendoza'] = provisional(unknown, 'La prensa da a Tejedor ganador en la ciudad y derrotado en la campaña, sin desglose por departamento.')
provinces['Buenos Aires'] = provisional(unknown, 'Hay resultados por parroquia y partido. El cuadro de campaña tiene cobertura parcial y discrepancias aritméticas. Almirante Brown, sin polígono en la base de 1869: 41 votantes según un escrutador (La Prensa, 14 de abril, p. 1), sin indicar la lista.')
for p in list(provinces):
    if p in ELECTORES:
        old = provinces[p]['note']
        provinces[p] = elec(p, '' if old == 'Sin dato de voto popular.' else 'Prensa: ' + old)
provinces['Tucumán']['metrics'].insert(0, ['Votos roquistas', '2.184'])
data['solid'] = [p for p in ELECTORES if p not in ('Buenos Aires', 'Mendoza')]
units = []
matched = set()
for t, previous in zip(data['territories'], data['modes'][0]['units']):
    name, p = key(t['n']), t['p']
    rec = empty
    if t['k'] == 'malvinas' or previous.get('fill') == land:
        rec = provisional(previous.get('fill', land), previous['note'].replace('1874','1880'))
        provinces[p] = rec
    elif p == 'Mendoza' and name in ('capital', 'la capital', 'ciudad'):
        rec = provisional(dark, f'Triunfo provisorio de Tejedor en la ciudad, representada por su departamento. {source}')
    elif p == 'Buenos Aires' and t['k'] == 'parroquia':
        rec = numbers(*city[name], f'Planilla 9 de Canton y Jorrat, basada en {source}')
    elif p == 'Buenos Aires' and name in rows:
        matched.add(name)
        r = rows[name]
        m = int(r['liberal'])
        raw = r['irigoyenista']
        total = r['total_impreso']
        note = f'{source} Total impreso de la fila: {total}.'
        if raw == '-':
            rec = dict(fill=dark, lines=[['MIT', m, None]],
                       note=note + ' Guion en la columna irigoyenista. Triunfo tejedorista informado por el diario, sin porcentaje.')
        else:
            a = int(raw)
            rec = numbers(m, a, note)
            if str(m+a) != total:
                rec['note'] += f' La suma de las dos columnas es {m+a}.'
    if p == 'Buenos Aires' and name == 'las heras' and rec.get('lines'):
        rec['note'] += ' El Porteño del 12 de abril, p. 2, imprime 00 y 00 en su primer cuadro telegráfico.'
    if p == 'Buenos Aires' and name == 'quilmes' and rec.get('lines'):
        rec['note'] += ' Coincide con El Quilmero del 15 de abril de 1880, p. 2 (59 conciliados, 4 irigoyenistas).'
    if rec is empty and p in ELECTORES and p != 'Buenos Aires':
        rec = elec(p)
    units.append(rec)

if set(rows) - matched != {'brandsen'}:
    raise ValueError(f'Cruces rurales pendientes: {set(rows)-matched}')
assert sum(v[0] for v in city.values()) == 5907
assert sum(v[1] for v in city.values()) == 603
pop = {'MIT': sum(v[0] for v in city.values()) + 0, 'PAN': sum(v[1] for v in city.values())}
for r in rows.values():
    pop['MIT'] += int(r['liberal'])
    if r['irigoyenista'] != '-':
        pop['PAN'] += int(r['irigoyenista'])
pop['PAN'] += 2184   # Tucumán
note = ('Fuente: La Prensa del 13 de abril de 1880, portada. Ciudad: planilla 9 del CD de Canton y Jorrat. '
        f'La torta y las barras suman el voto popular conocido: ciudad (CD), las filas de campaña de La Prensa y Tucumán (2.184 roquistas): Tejedor {pop["MIT"]:,}, Roca e irigoyenistas {pop["PAN"]:,}. '.replace(',', '.') +
        'Las provincias sin voto popular completo llevan el color de quien ganó sus electores según la Wikipedia (155 Roca, 70 Tejedor). '
        'El diario imprime 598 para los irigoyenistas de la ciudad. Campaña: 53 filas, 52 con polígono. '
        'Brandsen figura en el diario y queda en el CSV; falta un polígono en la base reutilizada de 1869. '
        'Los guiones del impreso se conservan y no generan porcentajes. Los partes provinciales sin cifras se muestran como provisorios. '
        'Los irigoyenistas bonaerenses apoyaban a Bernardo de Irigoyen. Los partes del interior distinguen a Roca. ' + 
        'Tucumán: 2.184 votos roquistas (Navajas, citando el acta de la Legislatura). '
        'El Porteño atribuye 900 votantes irigoyenistas a la ciudad, contra 598 de La Prensa y 603 del CD. '
        'La Asamblea del 9 de octubre no trató la elección primaria y escrutó solo los colegios: 155 Roca y 70 Tejedor. '
        'La geometría y los recuadros se reutilizan del atlas de 1874.')
keys = [[TEJ_ELEC, 'Electores de Tejedor (Wikipedia)'], [ROCA_ELEC, 'Electores de Roca (Wikipedia)'],
        [dark, 'Triunfo tejedorista provisorio'], [light, 'Triunfo roquista provisorio'],
        [unknown, 'Sin datos de voto popular'], [land, 'Territorio sin elección']]
T = pop['MIT'] + pop['PAN']
national = dict(cands=[dict(code=c,votes=pop[c],pct=round(100*pop[c]/T,2)) for c in ('MIT','PAN')],
                slices=[dict(code=c,v=pop[c]) for c in ('MIT','PAN')],
                metrics=[['Votos conocidos', f'{T:,}'.replace(',', '.')], ['Electores Roca', '155'], ['Electores Tejedor', '70']],partp=None)
data['modes'] = [dict(id='gan', tile='GANÓ', note=note, units=units, prov=provinces,
                      national=national, legend=dict(keys=keys))]
for code, tile in [('MIT','TEJ'),('PAN','ROCA')]:
    ramp = data['candidates'][code]['ramp']
    def pct_rec(r):
        rec = {k:v for k,v in r.items() if k not in ('w','q')}
        pct = next((v[2] for v in rec['lines'] if v[0]==code),None)
        rec['fill'] = (ramp[min(6,max(0,int(pct//10)-2))] if pct is not None else
                       r.get('fill') if r.get('fill') in (land,'#a9a9a9',ROCA_ELEC,TEJ_ELEC) else unknown)
        return rec
    data['modes'].append(dict(id=code.lower(), tile=tile, note=note,
        units=[pct_rec(r) for r in units], prov={p:pct_rec(r) for p,r in provinces.items()},
        national=national, legend=dict(title='% de votos publicados', bars=False,
        stops=list(zip(ramp,['<30%','30%','40%','50%','60%','70%','80%+'])),
        keys=keys[:2]+keys[4:])))
html = (BASE / 'atlas_1874.html').read_text(encoding='utf-8')
html = html.replace('<title>Atlas electoral 1874</title>', '<title>Atlas electoral 1880</title>')
payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
html, changes = re.subn(r'^const DATA=.*;$', lambda _: f'const DATA={payload};', html, flags=re.M)
assert changes == 1
(HERE / 'dataset_1880.json').write_text(payload, encoding='utf-8')
(HERE / 'atlas_1880.html').write_text(html, encoding='utf-8')
print(f'{len(city)} parroquias, {len(matched)}/{len(rows)} filas rurales, {len(data["solid"])} provincias provisorias.')
