from pathlib import Path
import csv,json
from exportar import ROOT,PROJECT

files=[ROOT/'1937/canton_1937.csv',ROOT/'1940/canton_1940.csv',PROJECT/'canton1946/canton_1946.csv']
rows=[]
for f in files:
    with f.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream);fields=reader.fieldnames;rows+=list(reader)
assert len(rows)==2963
assert all(r['valor'] or r['marca'] in ('*','**') for r in rows)
assert len({(r['anio'],r['provincia'],r['unidad'],r['columna']) for r in rows})==len(rows)
with (ROOT/'canton_1937_1940_1946.csv').open('w',encoding='utf-8-sig',newline='') as stream:
    w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(rows)
notes=['# Notas de transcripción', '', 'Se conservan las lecturas del escaneo. Una alerta aritmética no equivale a un error del original ni a evidencia de fraude; las tablas pueden omitir categorías o presentar votos por partido con el tratamiento descrito en la introducción de Cantón. No se aplicó ningún ajuste por residuo.', '', '## Lecturas particulares', '', '- 1937, La Rioja, San Blas de los Sauces, columna Concordancia: `*` (sin dato). No se calculó a partir de votantes y las demás columnas.', '- 1940, Capital Federal, Concepción, Concentración Obrera: el impreso dice **6.081**. Se conserva aun cuando la suma de las fuerzas supera a votantes.', '- 1940, Capital Federal, Socorro, Unión Cívica Radical Capital: **5.218**; el último dígito está intervenido a mano en el ejemplar. La imagen ampliada está en `revision/socorro147.png`.', '- 1940, Capital Federal, Santa Lucía: votantes **18.556**, con cifras intervenidas en el ejemplar; Agrupación Defensiva **141**.', '- 1946, Santiago del Estero, Salavina: votantes **1.612**, aunque las tres fuerzas suman 2.530. Se conserva el dato publicado.', '', '## Alertas de las sumas', '', 'En 1937 se comparan las columnas que incluyen blancos y observados/anulados. En 1940 y 1946 se muestran las sumas mayores que votantes, además de las diferencias de Tucumán 1940, cuya clave incluye blancos y anulados. Las sumas menores en tablas que omiten categorías no se convierten en votos de una fuerza ni en blancos/nulos.', '', '| Año | PDF | Unidad | Votantes | Suma de columnas publicadas | Diferencia |', '|---:|---:|---|---:|---:|---:|']
for year,folder in [(1937,ROOT/'1937'),(1940,ROOT/'1940'),(1946,PROJECT/'canton1946')]:
    control=json.loads((folder/f'CONTROL_{year}.json').read_text(encoding='utf-8'))
    for r in control['alertas_aritmeticas']:
        notes.append(f"| {year} | {r['pagina_pdf']} | {r['unidad']} | {r['votantes']} | {r['suma_columnas']} | {r['diferencia']} |")
(ROOT/'NOTAS_DE_TRANSCRIPCION.md').write_text('\n'.join(notes)+'\n',encoding='utf-8')
print('CSV conjunto verificado:',len(rows),'celdas; sin duplicados ni vacíos sin marca.')
