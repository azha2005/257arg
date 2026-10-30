"""Planillas «Consulta de Escrutinio por Zona» de la CNE (padron.gob.ar/publica, bajadas a mano por el usuario) de las
secciones que no tienen mesas en el escrutinio provisorio de las PASO -> datos/fuentes_leg2003_2025/complementos_paso.json.

Cada entrada guarda las filas tal como las da la CNE (número y nombre de agrupación, nombre de lista, votos);
`comun/paso_data.load()` las empareja con los números de agrupación y de lista de la DINE del mismo distrito."""
from pathlib import Path
import json, re, xlrd

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'complementos_paso.json'
DIST = {'CATAMARCA': '03', 'CHACO': '06', 'CHUBUT': '07'}
CARGO = {'PRESIDENTE': 'presidente', 'DIPUTADO NACIONAL': 'diputados'}
# inscriptos: la planilla no los trae; cuando da el porcentaje de votantes se despeja (único entero que lo redondea)
ELECTORES = {('zona_muni_0032_2.xls'): (1564, '1.057 votantes = 67,58 % de los inscriptos')}


def leer(f):
    sh = xlrd.open_workbook(f, ignore_workbook_corruption=True).sheet_by_index(0)
    rows = [sh.row_values(r) for r in range(sh.nrows)]
    txt = lambda r: ' '.join(str(c) for c in r if c != '')
    year = int(re.search(r'(\d{4})', next(txt(r) for r in rows if 'FECHA ELECCION' in txt(r))).group(1))
    d = DIST[re.search(r'Distrito:\s*(.+)', next(txt(r) for r in rows if 'Distrito:' in txt(r))).group(1).strip()]
    sec = next(r for r in rows if str(r[0]).startswith('Secci') and 'General' not in str(r[0]))
    s, nombre = re.match(r'(\d+)\s*-\s*(.+)', next(c for c in sec[1:] if c)).groups()
    mesas = next(int(r[r.index('Normal (padron Electoral)') + 1]) for r in rows if 'Normal (padron Electoral)' in r)
    hi = next(i for i, r in enumerate(rows) if r[0] == 'NRO')
    cols = {j: CARGO[k] for j, c in enumerate(rows[hi]) for k in CARGO if str(c).strip().startswith(k)}
    out = {c: dict(listas=[], blancos=0, nulos=0, total=0) for c in cols.values()}
    # la planilla cambia de un año a otro: la agrupación va en una fila sin votos con su número en la primera columna
    # («215», «0151», «219/506») y sus listas debajo, con el mismo número, la letra («A») o número y letra («503A»)
    cur = None
    for r in rows[hi + 1:]:
        if r[0] != '' and not any(isinstance(r[j], float) for j in cols):
            cur = (str(int(r[0])) if isinstance(r[0], float) else str(r[0]).strip().lstrip('0'), r[1].strip()); continue
        for j, c in cols.items():
            x = r[j]
            if x == '': continue
            if r[0] != '':
                out[c]['listas'].append([cur[0], cur[1], r[1].strip(), int(x)])
            elif 'BLANCO' in r[1]: out[c]['blancos'] += int(x)
            elif re.search(r'NULOS|RECURRIDOS|IMPUGNADOS', r[1]): out[c]['nulos'] += int(x)
            elif 'TOTALES' in r[1]: out[c]['total'] = int(x)
    for c, x in out.items():
        assert sum(l[3] for l in x['listas']) + x['blancos'] + x['nulos'] == x['total'], (f, c)
    e = ELECTORES.get(Path(f).name)
    return dict(year=year, d=d, s=s[-3:], nombre=nombre.strip(), mesas=mesas, archivo=f'padron_publica/paso/{Path(f).name}',
                electores=e[0] if e else 0, electores_fuente=e[1] if e else 'la planilla no trae inscriptos', cargos=out)


# PASO sin CNE: escrutinio definitivo de la DINE por distrito (elecciones.gob.ar/estadistica/archivos/<año>_primarias/,
# copia de la Wayback Machine), transcripto a mano. Cada lista: [número, agrupación, nombre de lista, votos].
PDF = [dict(year=2011, d='10', s='008', nombre='VALLE GRANDE', mesas=11, electores=2357,
            electores_fuente='2.357 según el escrutinio definitivo de la DINE',
            archivo='jujuy_paso2011_archivo.pdf (escrutinio_primarias_jujuy.pdf de elecciones.gob.ar, copia de Wayback), página 9',
            cargos=dict(
                presidente=dict(listas=[['37', 'PARTIDO DEL CAMPO POPULAR', '', 1], ['47', 'COALICION CIVICA ARI', '', 7],
                                        ['57', 'MOVIMIENTO DE ACCION VECINAL', '', 2], ['131', 'FRENTE PARA LA VICTORIA', '', 1284],
                                        ['132', 'FRENTE POPULAR', '', 54], ['133', 'COMPROMISO FEDERAL', '', 19],
                                        ['134', 'FRENTE AMPLIO PROGRESISTA', '', 21], ['135', 'FRENTE DE IZQ.Y DE LOS TRABAJ.', '', 11],
                                        ['136', 'PROYECTO SUR', '', 2], ['137', 'UNION PARA EL DESAR.SOCIAL', '', 239]],
                                blancos=48, nulos=32, total=1720),
                diputados=dict(listas=[['23', 'UNION POPULAR', '', 30], ['63', 'ES POSIBLE', '', 11], ['68', 'NUEVA IZQUIERDA', '', 2],
                                       ['501', 'FRENTE PARA LA VICTORIA', '', 929], ['502', 'FRENTE PRIMERO JUJUY', '', 221],
                                       ['503', 'FRENTE DE IZQ.Y DE LOS TRABAJ.', '', 9], ['504', 'UNION PARA EL DESAR.SOCIAL', '', 242],
                                       ['505', 'FRENTE AMPLIO PROGRESISTA', '', 14]],
                               blancos=234, nulos=28, total=1720)))]


if __name__ == '__main__':
    for e in PDF:
        for c, x in e['cargos'].items():
            assert sum(l[3] for l in x['listas']) + x['blancos'] + x['nulos'] == x['total'], (e['year'], c)
    ent = [leer(f) for f in sorted(HERE.glob('*.xls'))] + PDF
    OUT.write_text(json.dumps(ent, ensure_ascii=False, indent=1), encoding='utf8')
    for e in ent:
        print(e['year'], e['d'], e['s'], e['nombre'], e['mesas'], {c: x['total'] for c, x in e['cargos'].items()})
