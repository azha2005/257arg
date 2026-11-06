"""Une lecturas del frente sin inferir votos, circuitos ni ceros.

Las pistas de cara incierta y el resumen p102 no entran en celdas.csv.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENTRADAS = ['parte_a/lectura_parcial.csv', 'parte_b/lectura_consolidada.csv']
campos = ['archivo_fuente', 'pagina_pdf', 'bloque_lectura', 'fila_orden_pdf',
          'mesa_literal', 'circuito', 'lista', 'candidato_categoria',
          'votos_literal', 'valor_numerico', 'estado_celda', 'observacion',
          'archivo_transcripcion']
salida = []
metadatos = {'archivo_fuente': '26-ov-1936.pdf', 'entradas': {},
             'reserva': 'Primera lectura parcial, sin suma territorial. Guiones no convertidos en cero. '
                        'Pistas de cara incierta y resumen p102 separados. Los identificadores '
                        'de fila son de lectura, no números de mesa o circuito.'}
for nombre in ENTRADAS:
    ruta = BASE / nombre
    with ruta.open(encoding='utf-8-sig', newline='') as fp:
        filas = list(csv.DictReader(fp))
    claves = set()
    cantidades_renglon = Counter()
    for r in filas:
        literal = r['votos_literal'].strip()
        ordinal = r['fila_orden_pdf']
        clave = (r['pagina_pdf'], ordinal, r['candidato'])
        if clave in claves:
            raise ValueError(f'Celda duplicada en {nombre}: {clave}')
        claves.add(clave)
        cantidades_renglon[(r['pagina_pdf'], ordinal)] += 1
        if re.fullmatch(r'\d+', literal):
            valor, estado = int(literal), 'numero_leido'
        elif literal == '-':
            valor, estado = '', 'guion_literal'
        elif literal in ('', '?'):
            valor, estado = '', 'no_resuelto'
        else:
            valor, estado = '', 'lectura_con_reserva'
        salida.append(dict(zip(campos, [
            '26-ov-1936.pdf', r['pagina_pdf'], nombre.split('/')[0], ordinal,
            r['mesa'], r.get('circuito', ''), r['lista'], r['candidato'],
            literal, valor, estado, r.get('observacion', ''), nombre,
        ])))
    assert all(n == 14 for n in cantidades_renglon.values()), f'Renglón sin las 14 columnas nominales/categorías en {nombre}'
    metadatos['entradas'][nombre] = {
        'sha256': hashlib.sha256(ruta.read_bytes()).hexdigest(),
        'celdas': len(filas), 'renglones': len({(r['pagina_pdf'], r['fila_orden_pdf']) for r in filas}),
    }
with (BASE / 'celdas.csv').open('w', encoding='utf-8-sig', newline='') as fp:
    w = csv.DictWriter(fp, fieldnames=campos)
    w.writeheader()
    w.writerows(salida)
metadatos['celdas_por_estado'] = dict(Counter(r['estado_celda'] for r in salida))
metadatos['celdas_por_pagina'] = dict(Counter(r['pagina_pdf'] for r in salida))
metadatos['celdas_total'] = len(salida)
(BASE / 'CONTROL_CELDAS.json').write_text(json.dumps(metadatos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(metadatos, ensure_ascii=False, indent=2))
