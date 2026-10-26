"""Índice, registro de logos y manifiesto de entregables legislativos."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parent
YEARS=list(range(2003,2026,2))
NEW=(2003,2005,2007,2011,2015,2017,2019,2021,2023,2025)
reports={y:json.loads((ROOT/f'mapa{y}/control_cobertura.json').read_text(encoding='utf8')) for y in NEW}
lines=['# Legislativas 2003–2025: atlas y paquetes para Commons','',
       'Diputados nacionales, compilación 20-oct-2026. Diez atlas nuevos y las referencias 2009/2013. Todos los mapas conservan el estilo del proyecto. No se subieron archivos a Commons.','',
       'Colores de las barras/partidos de Wikipedia (no los fondos pastel de los subtotales) y colores ya verificados en los atlas de 2009 y 2013 para las mismas fuerzas. Provincias Unidas 2025 usa naranja **#FF682C**, por pedido del usuario. Los cambios de contraste están en cada LEEME.','',
       '| Año | Atlas | Paquete | Cobertura / reservas de datos |','|---|---|---|---|']
for y in YEARS:
    r=reports.get(y)
    if r:
        missing=r['missing'];status=('Pendiente: '+', '.join(missing)) if missing else 'Sin departamentos pendientes'
        if r.get('solid'):status+='; '+', '.join(r['solid'])+' en color provincial sólido'
        if r['antartida_sin_dato']:status+='; Antártida sin dato propio'
    else:
        status='Referencia existente, cobertura completa' if y==2009 else 'Referencia existente: Ramón Lista y Valle Grande sin mesas escrutadas'
    lines.append(f'| {y} | [Abrir](../mapa{y}/atlas_{y}.html) · [LEEME](../mapa{y}/LEEME_{y}.md) | [Carpeta {y}]({y}/subir/) · [Instrucciones]({y}/LEEME_SUBIDA.md) | {status} |')
lines+=['','## Geometría y fuentes','',
        '- 2003, 2005 y 2007: shapefile censal de 2001 + 28 circunscripciones de Capital; las circunscripciones son aproximadas y se ajustan al contorno, como en el proyecto.',
        '- 2009: referencia con 15 comunas y Chascomús sin Lezama (elección anterior a su creación).',
        '- 2011 en adelante: departamentos de 2010 + Lezama separado; Tolhuin aparece desde 2019. La ley provincial 1186 que crea el departamento se sancionó el 27-oct-2017, después de la elección legislativa del 22-oct-2017. La ley 892 de 2012 transformaba el municipio, no creaba el departamento. Fuente: https://www.legistdf.gob.ar/lp/leyes/Provinciales/LEYP1186.pdf',
        '- La Paz/Choya conserva el límite histórico de hecho, según la decisión anterior del usuario. Los polígonos modernos de Lezama/Tolhuin se recortan al contorno histórico, sin trasladar ese límite disputado.',
        '- 2003: dat.ar, contrastado por unidad. La Plata: corrección de 21 separadores de miles, original intacto. La Pampa: total provincial definitivo de la DINE; el PDF declara que no se recibieron resultados por departamento. Magdalena y Punta Indio tienen una cifra de lista ausente y quedan pendientes.',
        '- 2005–2007: PolAr/INDRA/Andy Tow. Se completaron los seis departamentos ausentes de La Pampa 2005 y Valle Grande 2005 con las tablas oficiales de la DINE, verificadas visualmente y cerradas al voto.',
        '- 2011–2025: DINE, provisorios por mesa. Santa Fe cambia la numeración de secciones en 2023: se empareja por nombre y no se confunden sus departamentos con antiguas subsecciones de Rosario/La Capital.',
        '- 2009 y 2013 conservan sus fuentes, logos y decisiones ya verificadas. Se regeneran sus PNG y paquetes, sin sustituir sus builds/datasets.',
        '- Las tablas nacionales salen de Wikipedia, nunca de la suma de la base. Los CSV `mapeo_listas` y `control_bloques` conservan el cruce de alianzas y las diferencias. No se imputan votos para forzar igualdad.','',
        '## Logos, licencias y publicación','',
        'Los emblemas y sus metadatos están en `fuentes_leg2003_2025/`, `mapa<año>/logos_usados.json` y `logos_wikipedia/LICENCIAS.md`. Las variantes con siglas omiten los emblemas con reservas de época, reutilizaciones sin metadatos completos o licencias ShareAlike. Los archivos con logos ShareAlike llevan CC BY-SA 4.0; los demás CC BY 4.0, más CC BY 2.5 Argentina por la geometría de Rodríguez/CONICET.',
        '',
        '**Los atlas con faltantes no deben publicarse como completos.** Cada `LEEME_SUBIDA.md` identifica qué versiones están en espera. No se disfrazan votos provinciales de resultados departamentales.','',
        '## Verificación','',
        'Se verifican los 71 modos de los doce atlas: hash/pestaña activa, ausencia de errores JavaScript y consistencia entre territorios y registros. Se revisaron las capturas de todos los modos. Las hojas de revisión están en `revision_leg2003_2025/`. `commons/chequeo.py` comprueba los SVG exportados y genera renders independientes con resvg.','',
        '## Reproducir','',
        '```powershell',
        'python atlas_leg2003_2025.py 2025',
        'python validar_render_leg2003_2025.py 2025',
        'python commons/paquete.py 2025',
        'python commons/chequeo.py 2025',
        'python cerrar_leg2003_2025.py',
        '```','']
(ROOT/'commons/INDICE_LEGISLATIVAS_2003_2025.md').write_text('\n'.join(lines),encoding='utf8')
license_lines=['## Legislativas 2003–2025 — revisión 20-oct-2026','',
 'Emblemas añadidos/reutilizados para los diez atlas nuevos. Fecha original de extmetadata.DateTimeOriginal; una fecha posterior no certifica el diseño de época. Las reconstrucciones se marcan como reserva y tienen variante con siglas. El detalle completo de autor/licencia se conserva en fuentes_leg2003_2025/logos_metadata.json.','',
 '| Logo / fuente | Usado en | Licencia registrada | Fecha original | Reserva de época |','|---|---|---|---|---|']
logos={}
for y,r in reports.items():
    for l in r['logos']:
        if not l['archivo']:continue
        k=l['commons_title'];q=logos.setdefault(k,dict(l,years=[]));q['years'].append(str(y));q['reserva_epoca']=q['reserva_epoca'] or l['reserva_epoca']
for k,l in sorted(logos.items()):
    label=f'[{k}]({l["fuente"]})' if l['fuente'].startswith('https:') else f'{k} (registro previo del proyecto)'
    license_lines.append(f'| {label} | {", ".join(l["years"])} | {l["licencia"] or "Ver metadatos de Commons"} | {l["fecha_original"] or "Sin fecha verificada"} | {"Sí; diseño de época no verificado" if l["reserva_epoca"] else "Sin reserva detectada en los metadatos"} |')
license_lines+=['','Las fuerzas sin logo disponible conservan la sigla; no se generaron emblemas inventados.','']
p=ROOT/'logos_wikipedia/LICENCIAS.md';txt=p.read_text(encoding='utf8');marker='## Legislativas 2003–2025 — revisión 20-oct-2026'
if marker in txt:txt=txt[:txt.index(marker)].rstrip()+'\n\n'
p.write_text(txt.rstrip()+'\n\n'+'\n'.join(license_lines),encoding='utf8')
manifest=[]
for y in YEARS:
    folder=ROOT/f'commons/{y}/subir'
    for p in sorted(folder.glob('*')):
        if p.is_file():manifest.append(dict(year=y,path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(ROOT/'commons/MANIFIESTO_LEGISLATIVAS_2003_2025.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Índice y licencias actualizados. Archivos empaquetados:',len(manifest))
