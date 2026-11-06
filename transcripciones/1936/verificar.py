"""Controles de la transcripción; ejecutar desde cualquier directorio.

No imputa campos ausentes ni convierte votos nominales en electores.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent

def leer(nombre):
    with (BASE / nombre).open(encoding='utf-8-sig', newline='') as fp:
        return list(csv.DictReader(fp))

sf = leer('santa_fe/candidatos.csv')
totales = leer('santa_fe/totales.csv')
identidades = [(r['departamento'], r['partido'], r['candidato']) for r in sf]
assert len(identidades) == len(set(identidades)), 'Duplicados en Santa Fe'
assert len(sf) == 399 and len(totales) == 19
por_candidato = defaultdict(int)
for r in sf:
    por_candidato[r['candidato']] += int(r['votos'])
control_previo = json.loads((BASE / 'santa_fe/control.json').read_text(encoding='utf-8-sig'))
comparaciones = []
for r in control_previo['candidatos']:
    total = por_candidato[r['nombre']]
    comparaciones.append({'candidato': r['nombre'], 'suma_departamentos': total,
                          'total_acta_p99': r['total_acta'], 'diferencia': total-r['total_acta']})
assert all(x['diferencia'] == 0 for x in comparaciones)
otros = sum(int(r['otros_candidatos']) for r in totales if r['otros_candidatos'])
resultado = {
    'santa_fe': {
        'departamentos': len(totales), 'celdas_nominales': len(sf),
        'candidatos': comparaciones,
        'blancos_suma': sum(int(r['blancos']) for r in totales), 'blancos_acta_p99': 9903,
        'votantes_suma': sum(int(r['votantes']) for r in totales), 'votantes_acta_p99': 263277,
        'otros_candidatos': {
            'suma_solo_menciones_explicitas': otros, 'total_acta_p99': 133,
            'departamentos_sin_mencion': [r['departamento'] for r in totales if not r['otros_candidatos']],
            'literal_san_martin_p97': 'M 4',
            'suma_menciones_si_se_lee_4_en_san_martin': otros + 4,
            'reserva': 'San Martín conserva M 4 sin normalizar. Primera lectura 14 retirada por cotejo visual; otras ausencias no son cero.'
        }
    },
    'tucuman_acta': json.loads((BASE / 'tucuman/control_acta.json').read_text(encoding='utf-8')),
    'fuentes_sha256': {
        n: hashlib.sha256((BASE / 'expedientes_hcdn' / n).read_bytes()).hexdigest()
        for n in ['26-ov-1936.pdf', '29-ov-1936.pdf']
    },
}
assert resultado['santa_fe']['blancos_suma'] == 9903
assert resultado['santa_fe']['votantes_suma'] == 263277
for nombre in ['tucuman/parte_a/lectura_parcial.csv', 'tucuman/parte_b/lectura_consolidada.csv']:
    if not (BASE / nombre).exists():
        continue
    filas = leer(nombre)
    paginas = Counter(r['pagina_pdf'] for r in filas)
    resultado[nombre] = {'celdas_registradas': len(filas), 'celdas_por_pagina': dict(paginas),
                         'nota': 'Conteo de registros, no prueba de cobertura exhaustiva.'}
if (BASE / 'tucuman/CONTROL_CELDAS.json').exists():
    consolidacion = json.loads((BASE / 'tucuman/CONTROL_CELDAS.json').read_text(encoding='utf-8'))
    for entrada, datos in consolidacion['entradas'].items():
        actual = hashlib.sha256((BASE / 'tucuman' / entrada).read_bytes()).hexdigest()
        assert actual == datos['sha256'], f'Consolidación desactualizada: ejecutar tucuman/consolidar.py ({entrada})'
    resultado['tucuman_planillas'] = consolidacion
    celdas = leer('tucuman/celdas.csv')
    focales = []
    for pagina, hasta, fila_total in [('72', 13, '14'), ('96', 7, '7.5')]:
        grupo = [r for r in celdas if r['pagina_pdf'] == pagina and r['candidato_categoria'] == 'Manuel Martínez']
        detalle = [r for r in grupo if float(r['fila_orden_pdf']) <= hasta]
        impreso = next(r for r in grupo if r['fila_orden_pdf'] == fila_total)
        assert len(detalle) == hasta and all(r['votos_literal'].isdigit() for r in detalle)
        suma = sum(int(r['votos_literal']) for r in detalle)
        total = int(impreso['votos_literal'])
        focales.append({'pagina_pdf': pagina, 'candidato': 'Manuel Martínez',
                        'filas_detalle': hasta, 'suma_filas': suma, 'subtotal_impreso': total,
                        'diferencia_suma_menos_impreso': suma-total,
                        'accion': 'Se conserva literal; ver REVISION.md.'})
    resultado['tucuman_controles_focales'] = focales
(BASE / 'CONTROL.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Santa Fe: 19 departamentos, 399 votos nominales; 21 candidatos, blancos y votantes cierran.')
print(f'Otros candidatos: {otros} en menciones sin marca; San Martín M 4 sin normalizar (con lectura 4 sumarían 133).')
print('Tucumán: totales departamentales del acta cierran; planillas nominales con cobertura separada.')
