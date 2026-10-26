"""Exporta la transcripción cotejada sin trasladar las erratas del OCR al original."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf'


def main():
    logical = [json.loads((ROOT / f'transcripcion/p_{p}.json').read_text(encoding='utf-8')) for p in range(172, 249)]
    pages = {p['pagina_pdf']: {k: v for k, v in p.items() if k not in ('filas', 'estado')} | {'filas': []} for p in logical}
    keys = set()
    sums, participation = [], []
    for p in logical:
        for row in p['filas']:
            src = row.get('pagina_fuente', p['pagina_pdf'])
            key = (p['provincia'], p['categoria'], row['departamento'])
            assert key not in keys, key
            keys.add(key)
            values = row['valores']
            assert len(values) == len(p['columnas'])
            assert all(v is not None or row['literales'][c] in ('*', '**') for c, v in values.items())
            visual = p['estado'] == 'transcripción visual' or row.get('estado') == 'transcripción visual'
            cleaned = {
                'unidad': row['departamento'],
                'valores': values,
                'marcas': {c: row['literales'][c] for c, v in values.items() if v is None},
                'revision': 'fila transcrita visualmente' if visual else 'OCR cotejado con controles aritméticos y revisión visual de discrepancias',
                'columnas_cotejadas_visualmente': sorted(set(row.get('celdas_revisadas', [])), key=int),
            }
            pages[src]['filas'].append(cleaned)
            ref = {'pagina_pdf': src, 'provincia': p['provincia'], 'categoria': p['categoria'], 'unidad': row['departamento']}
            nums = list(values.values())
            if all(v is not None for v in nums[1:]) and sum(nums[2:]) != nums[1]:
                sums.append(ref | {'votantes': nums[1], 'suma_columnas_votos': sum(nums[2:]), 'diferencia': sum(nums[2:]) - nums[1]})
            if nums[0] is not None and nums[1] is not None and nums[1] > nums[0]:
                participation.append(ref | {'inscriptos': nums[0], 'votantes': nums[1]})
    pages = list(pages.values())
    assert len(pages) == 77 and all(p['filas'] for p in pages)
    # Mantener el orden físico de Buenos Aires: las continuaciones no cortan en la misma unidad.
    for p in pages:
        if p['provincia'] == 'Buenos Aires' and p['categoria'] == 'mujeres solamente':
            p['filas'].sort(key=lambda r: r['unidad'].casefold())
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    metadata = {'titulo': 'Cantón: elecciones de 1954, tomo II', 'archivo_fuente': str(SOURCE.relative_to(ROOT.parent)), 'sha256_fuente': digest, 'paginas_pdf_solicitadas': [171, 248], 'pagina_171': 'Portadilla; no contiene tabla', 'criterio': 'Cifras del impreso. Se corrigen errores del OCR, no se imputan valores ni se corrigen las inconsistencias del libro.', 'marcas': {'*': 'Sin dato; véanse las notas de la página original.', '**': 'Incluido en otra unidad o no considerado, según la nota del original; no equivale a cero.'}}
    (ROOT / 'canton_1954.json').write_text(json.dumps({'metadatos': metadata, 'paginas': pages}, ensure_ascii=False, indent=2), encoding='utf-8')
    count = 0
    with (ROOT / 'canton_1954.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        fields = ['anio', 'tomo', 'pagina_pdf', 'pagina_libro', 'provincia', 'eleccion', 'categoria', 'unidad', 'columna', 'concepto', 'valor', 'marca']
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for p in pages:
            for r in p['filas']:
                for c, label in p['columnas'].items():
                    writer.writerow({'anio': 1954, 'tomo': 'II', **{k: p[k] for k in ['pagina_pdf', 'pagina_libro', 'provincia', 'eleccion', 'categoria']}, 'unidad': r['unidad'], 'columna': c, 'concepto': label, 'valor': r['valores'][c], 'marca': r['marcas'].get(c, '')})
                    count += 1
    md = ['# Cantón, tomo II: elecciones de 1954', '', 'Transcripción de las tablas de las páginas PDF 172–248. La página PDF 171 es una portadilla. Las cifras conservan las inconsistencias del impreso; `*` y `**` no son ceros. Véanse `LEEME.md` y `DIFERENCIAS_ORIGINAL_1954.md`.', '']
    for p in pages:
        md += [f"## PDF {p['pagina_pdf']} · libro {p['pagina_libro']}: {p['provincia']}", '', f"{p['eleccion']}; {p['categoria']}.", '', 'Claves: ' + '; '.join(f'{c}: {label}' for c, label in p['columnas'].items()) + '.', '', '| Unidad | ' + ' | '.join(p['columnas']) + ' |', '|---|' + '---:|' * len(p['columnas'])]
        for r in p['filas']:
            md.append('| ' + r['unidad'] + ' | ' + ' | '.join(str(v) if v is not None else r['marcas'][c] for c, v in r['valores'].items()) + ' |')
        md.append('')
    (ROOT / 'TRANSCRIPCION_1954.md').write_text('\n'.join(md), encoding='utf-8')
    sex = json.loads((ROOT / 'revision/cotejo_sexos.json').read_text(encoding='utf-8'))
    stats = {'paginas_tablas': 77, 'filas': len(keys), 'celdas': count, 'provincias_o_distritos': len({p['provincia'] for p in pages}), 'celdas_numericas': sum(v is not None for p in pages for r in p['filas'] for v in r['valores'].values()), 'marcas': dict(Counter(m for p in pages for r in p['filas'] for m in r['marcas'].values())), 'celdas_vacias_sin_marca': 0, 'sha256_fuente': digest, 'diferencias_suma_fila': sums, 'diferencias_varones_mujeres_total': sex, 'votantes_mayores_que_inscriptos': participation, 'criterio_discrepancias': 'Se conservaron las lecturas del original tras cotejar las discrepancias con las imágenes; no se ajustaron por residuo.'}
    (ROOT / 'CONTROL_1954.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    report = ['# Diferencias aritméticas del original', '', 'Las cifras de estas filas se conservaron tras cotejarlas con el escaneo. La diferencia es un control, no una corrección propuesta.', '', '## Suma de votos frente a votantes', '', '| PDF | Distrito | Categoría | Unidad | Votantes | Suma de votos | Diferencia |', '|---:|---|---|---|---:|---:|---:|']
    for r in sums:
        report.append('| ' + ' | '.join(str(r[k]) for k in ['pagina_pdf', 'provincia', 'categoria', 'unidad', 'votantes', 'suma_columnas_votos', 'diferencia']) + ' |')
    report += ['', '## Varones más mujeres frente al total impreso', '', 'Las páginas indicadas corresponden a varones, mujeres y total. En Buenos Aires la página física de algunas filas de mujeres cambia por los cortes de continuación; la referencia exacta de cada dato está en el CSV/JSON.', '', '| Páginas PDF | Unidad | Columna | Varones | Mujeres | Total impreso | Diferencia |', '|---|---|---:|---:|---:|---:|---:|']
    for r in sex:
        a, b, total = r['lecturas']
        report.append(f"| {', '.join(map(str, r['paginas']))} | {r['unidad']} | {r['columna']} | {a} | {b} | {total} | {a+b-total if None not in (a,b,total) else 'No comparable'} |")
    report += ['', '## Votantes mayores que inscriptos', '', '| PDF | Distrito | Categoría | Unidad | Inscriptos | Votantes |', '|---:|---|---|---|---:|---:|']
    for r in participation:
        report.append('| ' + ' | '.join(str(r[k]) for k in ['pagina_pdf', 'provincia', 'categoria', 'unidad', 'inscriptos', 'votantes']) + ' |')
    (ROOT / 'DIFERENCIAS_ORIGINAL_1954.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in stats.items() if not isinstance(v, list)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
