"""Correspondencias y totales leídos visualmente por el agente principal.

Páginas PDF desde 1. No convierte votos nominales en votos de lista.
"""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'tucuman'
OUT.mkdir(exist_ok=True)
DATOS = [
    ('Capital', 1, 19, '9-21', 26516, 26506, 21),
    ('Famaillá', 22, 34, '23-27', 9943, 9937, 27),
    ('Monteros', 35, 54, '29-33', 9110, 9112, 33),
    ('Chicligasta', 55, 68, '35-39', 8300, 8300, 39),
    ('Río Chico', 69, 77, '41-45', 8244, 8240, 45),
    ('Graneros', 78, 82, '45-47', 3591, 3589, 47),
    ('Leales', 83, 91, '47-49', 3888, 3882, 49),
    ('Cruz Alta', 92, 111, '49-56', 12617, 12592, 56),
    ('Burruyacú', 112, 124, '57-59', 4293, 4301, 59),
    ('Trancas', 125, 127, '61', 1731, 1732, 61),
    ('Tafí', 128, 134, '61-67', 5927, 5922, 67),
]

with (OUT / 'acta_departamentos.csv').open('w', encoding='utf-8', newline='') as fp:
    w = csv.writer(fp)
    w.writerow(['departamento', 'circuito_desde', 'circuito_hasta', 'paginas_pdf',
                'sobres_segun_acta', 'sobres_en_urna', 'pagina_total_pdf', 'nota'])
    for depto, primero, ultimo, paginas, acta, urna, pagina in DATOS:
        nota = ('Imagen tenue e invertida verticalmente; lectura del canal rojo con '
                'contraste local. No OCR ni inferencia por diferencia.' if pagina == 56 else '')
        w.writerow([depto, primero, ultimo, paginas, acta, urna, pagina, nota])

with (OUT / 'circuitos_departamentos.csv').open('w', encoding='utf-8', newline='') as fp:
    w = csv.writer(fp)
    w.writerow(['circuito', 'departamento', 'paginas_pdf', 'criterio'])
    for depto, primero, ultimo, paginas, *_ in DATOS:
        for numero in range(primero, ultimo + 1):
            w.writerow([numero, depto, paginas, 'secuencia bajo encabezado del acta'])
    for circuito, depto, paginas in [
        ('1 bis', 'Capital', '11'), ('2 bis', 'Capital', '13'),
        ('3 bis', 'Capital', '15'), ('73 bis', 'Río Chico', '43'),
        ('90 bis', 'Leales', '49'), ('125 bis', 'Trancas', '61'),
    ]:
        w.writerow([circuito, depto, paginas, 'encabezado explícito'])

control = {
    'fuente': '26-ov-1936.pdf',
    'lectura': 'visual por el principal; no segunda lectura de las planillas de candidatos',
    'departamentos': len(DATOS),
    'acta_suma': sum(x[4] for x in DATOS), 'acta_total_p67': 94160,
    'urna_suma': sum(x[5] for x in DATOS), 'urna_total_p67': 94113,
    'advertencias': [
        'Son sobres según acta y hallados en urna, no votos positivos de partido.',
        'Circuitos 20 y 21 no aparecen entre Capital y Famaillá; no se asignaron.',
        'Cruz Alta 109-111 y su total se recuperan de la imagen tenue p56.',
        'P69 admite al escrutinio las mesas observadas de circuitos 13 y 65.',
        'La correspondencia no identifica por sí sola las filas sin rótulo de las planillas.',
    ],
}
assert control['acta_suma'] == control['acta_total_p67']
assert control['urna_suma'] == control['urna_total_p67']
(OUT / 'control_acta.json').write_text(json.dumps(control, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(control, ensure_ascii=False, indent=2))
