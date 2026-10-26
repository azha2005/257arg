"""Record the independently audited publication; never writes to Wikimedia."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT/'auditoria_publicacion_20261020.json').read_text(encoding='utf-8'))
assert len(report['files']) == 184 and all(f['same'] for f in report['files'])
assert len(report['articles']) == 11
assert all(a['section'] and a['main'] and a['previous_map_preserved'] and a['bronca_below'] for a in report['articles'])
lines = ['# Publicación de atlas legislativos y constituyentes — 20-oct-2026', '',
         'Publicación solicitada por el usuario: legislativas de 1983 a 2001, variante voto bronca de 2001 y constituyentes de 1994.', '',
         '- Commons: 162 archivos distintos subidos con el TXT correspondiente; 22 nombres adicionales redirigen a una versión idéntica para evitar duplicados.',
         '- Auditoría por API: los 184 nombres resuelven a archivos cuyo SHA1 coincide exactamente con el archivo local. Ningún archivo previo fue reemplazado.',
         '- Wikipedia: 11 artículos publicados. Nuestro mapa con leyenda es el principal. Todos los mapas previos de las fichas se conservan como segunda opción de `Switcher`.',
         '- 1993, 1995 y 2001 no tenían mapa en la ficha: se añadió directamente, sin selector de una sola opción.',
         '- Cada artículo incorpora una sección de resultados por departamento y una galería de coropletas, con participación donde existe.',
         '- Voto bronca: aparece únicamente en la galería inferior de 2001, con aclaración de variante analítica y denominador positivos + blancos + nulos.',
         '- Se conservaron las advertencias de fuentes, datos calculados y licencias de los TXT. No se publicaron mensajes en discusiones.', '',
         '## Revisiones publicadas', '', '| Elección | Revisión | Mapas previos |', '|---|---|---|']
for a in sorted(report['articles'], key=lambda a:a['year']):
    label = f"Constituyentes {a['year']}" if a['year'] == 1994 else f"Diputados {a['year']}"
    lines.append(f"| {label} | [{a['revid']}]({a['url']}) | {'Conservados en selector' if a['switcher'] else 'Sin mapa previo en la ficha'} |")
lines += ['', '## Archivos y redirecciones', '', '| Paquete | Imágenes distintas | Redirecciones | SHA1 correctos |', '|---|---:|---:|---:|']
keys = list(dict.fromkeys(f['key'] for f in report['files']))
for key in keys:
    fs = [f for f in report['files'] if f['key'] == key]
    aliases = [f for f in fs if f['redirect']]
    lines.append(f"| {key} | {len(fs)-len(aliases)} | {len(aliases)} | {len(fs)}/{len(fs)} |")
    readme = ROOT/key/'LEEME_SUBIDA.md'
    text = readme.read_text(encoding='utf-8')
    text = re.sub(r'Estado al [^\n]+', 'Estado al 2026-10-20. **Publicado en Commons y verificado por SHA1**. Véase [registro de publicación](../ESTADO_LEGISLATIVAS_2026-10-20.md). Usuario: `ItsAHardLife`.', text, count=1)
    text = text.replace('| Para subir |', '| Subido y verificado |')
    text += '\n## Publicación del 20-oct-2026\n\n'
    text += f"Verificados {len(fs)} nombres: {len(fs)-len(aliases)} imágenes distintas y {len(aliases)} redirecciones a imágenes idénticas. Todas coinciden con el SHA1 local. Artículo publicado conservando sus mapas previos; ver el registro enlazado arriba.\n"
    if aliases:
        text += '\nRedirecciones creadas (los archivos locales se conservan):\n\n'
        text += '\n'.join(f"- `{f['name']}` → `{f['target'][5:]}`" for f in aliases) + '\n'
    readme.write_text(text, encoding='utf-8')
lines += ['', '## Evidencia', '',
          '- `auditoria_publicacion_20261020.json`: archivos, SHA1, redirecciones, miniaturas y revisiones.',
          '- `auditoria_publicacion_20261020.log`: salida de la comprobación independiente.',
          '- `articulos_20261020/`: texto anterior, texto propuesto, diff y texto publicado por artículo.',
          '- Previsualizaciones inspeccionadas visualmente: fichas y selectores de 1983, 1985, 1987, 1989, 1991, 1994, 1997 y 1999; secciones y galerías de 1993, 1995 y 2001. Confirmación posterior de las 11 publicaciones por API.', '']
(ROOT/'ESTADO_LEGISLATIVAS_2026-10-20.md').write_text('\n'.join(lines), encoding='utf-8')
index = ROOT/'INDICE_LEGISLATIVAS_1983_2001.md'
text = index.read_text(encoding='utf-8')
text = text.replace('Preparados localmente el 19 de octubre de 2026. No se subió ningún archivo.', 'Publicados en Commons y en sus artículos el 20 de octubre de 2026. Incluye las diez legislativas de 1983 a 2001, voto bronca y constituyentes de 1994. [Registro y revisiones](ESTADO_LEGISLATIVAS_2026-10-20.md).')
index.write_text(text, encoding='utf-8')
print('Publication recorded:', len(report['files']), 'file names;', len(report['articles']), 'articles.')
