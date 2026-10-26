"""Prepare reviewable Wikipedia edits; publication happens through the browser."""
import difflib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEYS = ['1983dip', '1985', '1987', '1989dip', '1991', '1993', '1994', '1995dip', '1997', '1999dip', '2001']
OUT = ROOT / 'articulos_20261020'
rows = []
for key in KEYS:
    year = key[:4]
    original = (OUT / f'{year}.wiki').read_text(encoding='utf-8')
    text = original
    files = sorted(p.name for p in (ROOT / key / 'subir').glob('*.svg'))
    main = next(f for f in files if ' - Resultados por departamento (con leyenda).svg' in f)
    plain = next(f for f in files if ' - Resultados por departamento (solo mapa).svg' in f)
    old = re.search(r'^\|\s*mapa\s*=([^\n]*)', text, re.M)
    oldname = old.group(1).strip() if old else ''
    office = 'convencionales constituyentes' if year == '1994' else 'diputados nacionales'
    block = f'| mapa_título = Resultados de {office}\n'
    block += '| leyenda_mapa1 = <center>{{Switcher\n'
    block += f'| [[Archivo:{main}|300px]]\n| Mostrar resultados por departamento\n'
    if oldname:
        seats = 'convencionales' if year == '1994' else 'diputados'
        block += f'| [[{oldname}|300px]]\n| Mostrar resultados y {seats} por distrito\n'
    # A selector with one option is pointless when no previous map exists.
    block += '}}</center>\n'
    if not oldname:
        block = f'| mapa_título = Resultados por departamento\n| mapa = Archivo:{main}\n| mapa_tamaño = 300px\n'
    for field in ['mapa_título', 'mapa', 'mapa_tamaño', 'leyenda_mapa1']:
        text = re.sub(r'^\|\s*' + field + r'\s*=[^\n]*\n', '', text, count=1, flags=re.M)
    anchor = re.search(r'^\|\s*(?:cargo|diagrama_título)\s*=', text, re.M)
    assert anchor
    text = text[:anchor.start()] + block + '\n' + text[anchor.start():]
    boundary = 'departamentos de 1980' if int(year) <= 1989 else 'departamentos de 1991, con las divisiones posteriores indicadas en la descripción del archivo'
    note = ''
    if year == '1995':
        note = ' El dato de Deseado se calculó a partir del total provincial menos los otros seis departamentos, como se detalla en Commons.'
    if year == '1997':
        note = ' San Luis se representa con su resultado provincial por falta de detalle departamental.'
    if year == '1999':
        note = ' San Luis y Santa Cruz se representan con sus resultados provinciales por falta de detalle departamental.'
    section = '\n== Resultados por departamento ==\n'
    section += f'[[Archivo:{plain}|miniaturadeimagen|centro|550px|Resultados de {office} por departamento ({boundary}). Fuente: base electoral de Ernesto Calvo; véanse las fuentes y salvedades en la descripción del archivo.{note}]]\n\n'
    section += '<gallery mode="packed" heights="200px">\n'
    for f in files:
        if '(solo mapa)' not in f or f == plain:
            continue
        label = f.split(' - ', 1)[1].removesuffix(' por departamento (solo mapa).svg')
        label = label.replace('Participacion', 'Participación')
        section += f'Archivo:{f}|{label}\n'
    if year == '2001':
        bronca = sorted(p.name for p in (ROOT / '2001bronca' / 'subir').glob('*solo mapa*.svg'))
        for f in bronca:
            if 'Resultados por departamento' in f:
                label = 'Comparación de las fuerzas con los votos en blanco y nulos agrupados («voto bronca»). Variante analítica; no fue una candidatura.'
            elif 'Voto a Voto bronca' in f:
                label = 'Votos en blanco y nulos («voto bronca») sobre positivos, blancos y nulos.'
            else:
                continue
            section += f'Archivo:{f}|{label}\n'
    section += '</gallery>\n\n'
    target = re.search(r'^== Resultados por (?:provincia|distrito) ==', text, re.M)
    assert target
    text = text[:target.start()] + section + text[target.start():]
    assert not oldname or f'[[{oldname}|300px]]' in text
    (OUT / f'{year}_propuesto.wiki').write_text(text, encoding='utf-8')
    (OUT / f'{year}.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile=f'{year}_actual', tofile=f'{year}_propuesto')), encoding='utf-8')
    rows.append(dict(year=year, original=original, proposed=text, oldmap=oldname))
(ROOT / 'article_manifest_20261020.html').write_text('<!doctype html><meta charset=utf-8><pre>' + html.escape(json.dumps(rows, ensure_ascii=False)) + '</pre>', encoding='utf-8')
print('Prepared', len(rows), 'article edits and diffs.')
