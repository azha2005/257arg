"""Propuestas de correspondencia monotónica: NO certifica asignaciones.

Compara etiquetas de mesas y una huella numérica auxiliar. Suma nominal/3
con blancos/nulos es solo un indicador aproximado, nunca votos observados
de partido ni un cálculo definitivo de votantes. Los guiones se prueban
como cero únicamente en esa huella, sin cambiar ninguna transcripción.
"""
import csv
import json
import math
import re
import statistics
from collections import OrderedDict
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent

def leer(p):
    with (BASE / p).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

esperadas = leer('acta_mesas_a.csv') + leer('acta_mesas_b.csv')
esperadas = [r for r in esperadas if 'TOTAL' not in r['mesa_literal'].upper()]
grupos = OrderedDict()
for r in leer('celdas.csv'):
    grupos.setdefault((r['pagina_pdf'], r['fila_orden_pdf']), []).append(r)
observadas = []
for (p, f), celdas in grupos.items():
    if 'TOTAL' in celdas[0]['mesa_literal'].upper():
        continue
    vals = {r['candidato_categoria']: r['votos_literal'] for r in celdas}
    nums = [v for k, v in vals.items() if k not in ('Blancos', 'Nulos')]
    proxy = None
    # Medianas intralista SOLO para la búsqueda de correspondencias: no
    # salen como votos ni reemplazan '?' en ningún archivo de transcripción.
    partes = []
    for k in range(0,12,3):
        grupo = [int(v) if v.isdigit() else 0 for v in nums[k:k+3] if v.isdigit() or v == '-']
        partes.append(statistics.mean(grupo) if len(grupo) == 3 else (statistics.median(grupo) if grupo else None))
    if all(v is not None for v in partes):
        proxy = sum(partes)
        for k in ('Blancos', 'Nulos'):
            if vals[k].isdigit():
                proxy += int(vals[k])
    observadas.append({'pagina_pdf': p, 'fila_orden_pdf': f,
                       'mesa_literal': celdas[0]['mesa_literal'], 'proxy': proxy})

def firma(etiqueta):
    s = etiqueta.lower()
    n = tuple(int(x) for x in re.findall(r'\d+', s))
    sup = 'sup' in s or s.strip() == '-s.'
    return n, sup

def etiqueta_costo(o, e):
    on, os = firma(o)
    en, es = firma(e)
    if on == en and os == es:
        return 0
    if not on and os:
        return 0.2 if es else (0.7 if en and en[0] == 1 else 4)
    if on == en:
        return 0.3
    if len(on) == 1 and on[0] in en:
        return 0.6
    return 6

# Anclajes por texto y secuencias particularmente singulares. Las demás
# asignaciones son propuestas pendientes de cotejo visual del principal.
anclas = {}
for r in observadas:
    p, f = int(r['pagina_pdf']), float(r['fila_orden_pdf'])
    circuito = None
    if p == 72:
        circuito = '1'
    elif p == 73 and f <= 11:
        circuito = '1 bis'
    elif p == 90:
        circuito = '78'
    elif p == 91:
        circuito = '82'
    elif p == 93:
        circuito = '90 bis' if f == 1 else '91'
    elif p == 99:
        circuito = '125' if f <= 2 else ('125 bis' if f <= 4 else ('126' if f <= 7 else '127'))
    elif p == 100:
        circuito = '128'
    elif p == 101:
        circuito = '130' if f <= 7 else ('131' if f <= 9 else ('132' if f <= 13 else ('133' if f <= 15 else '134')))
    if circuito:
        anclas[(p, r['fila_orden_pdf'])] = circuito

def circ(s):
    return s.lower().replace(' ', '').replace('.', '')

n, m = len(observadas), len(esperadas)
costos = np.empty((n, m))
for i, o in enumerate(observadas):
    ancla = anclas.get((int(o['pagina_pdf']), o['fila_orden_pdf']))
    for j, e in enumerate(esperadas):
        if ancla and circ(e['circuito']) != circ(ancla):
            costos[i, j] = 1e6
            continue
        costo = etiqueta_costo(o['mesa_literal'], e['mesa_literal'])
        if o['proxy'] is not None and e['sobres_urna'].isdigit():
            urna = int(e['sobres_urna'])
            costo += min(12, abs(o['proxy']-urna) / max(5, urna*.035)) * .5
        costos[i, j] = costo

# Se permiten huecos: una fila ausente en el registro de lectura no se
# inventa, y una fila observada imposible de alinear puede quedar fuera.
salto_acta, salto_planilla = 0.8, 8.0
dp = np.full((n+1, m+1), np.inf)
paso = np.zeros((n+1, m+1), dtype=np.uint8)
dp[0, :] = np.arange(m+1)*salto_acta
dp[:, 0] = np.arange(n+1)*salto_planilla
for i in range(1, n+1):
    for j in range(1, m+1):
        o = observadas[i-1]
        penalizacion_salto = 1000 if (int(o['pagina_pdf']),o['fila_orden_pdf']) in anclas else salto_planilla
        opts = [dp[i-1,j-1]+costos[i-1,j-1], dp[i,j-1]+salto_acta, dp[i-1,j]+penalizacion_salto]
        k = int(np.argmin(opts))
        dp[i,j], paso[i,j] = opts[k], k
asignadas = {}
i, j = n, m
while i and j:
    k = paso[i,j]
    if k == 0:
        asignadas[i-1] = j-1
        i, j = i-1, j-1
    elif k == 1:
        j -= 1
    else:
        i -= 1

campos = ['pagina_planilla','fila_orden_pdf','mesa_planilla','circuito_propuesto',
          'departamento_propuesto','mesa_acta','pagina_acta','sobres_acta','sobres_urna',
          'huella_aproximada','costo_local','anclaje','estado']
with (BASE/'propuestas_alineamiento.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w=csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    for i,o in enumerate(observadas):
        j=asignadas.get(i)
        e=esperadas[j] if j is not None else {}
        w.writerow(dict(zip(campos,[o['pagina_pdf'],o['fila_orden_pdf'],o['mesa_literal'],
                    e.get('circuito',''),e.get('departamento',''),e.get('mesa_literal',''),
                    e.get('pagina_pdf',''),e.get('sobres_acta',''),e.get('sobres_urna',''),
                    round(o['proxy'],3) if o['proxy'] is not None else '',
                    round(costos[i,j],3) if j is not None else '',
                    anclas.get((int(o['pagina_pdf']),o['fila_orden_pdf']),''),
                    'propuesta automática, requiere cotejo'])))
print(json.dumps({'filas_planilla':n,'filas_acta':m,'filas_alineadas':len(asignadas),
                  'costo_global':float(dp[n,m])},ensure_ascii=False))
