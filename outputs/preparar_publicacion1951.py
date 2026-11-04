from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'scratch_publicar_1951'
assert (DEST/'.git').is_file()
files=['comun/wikitop.py','comun/render_transparentes.py','comun/logos_ras_excepciones.json','sitio/catalogo.py',
       'sitio/miniaturas/mapa1951__atlas_1951.webp','sitio/miniaturas/mapa1951__atlas_1951_claro.webp']
files += [str(p.relative_to(ROOT)).replace('\\','/')for p in (ROOT/'mapas/mapa1951').iterdir()if p.is_file()and p.suffix in ('.py','.json','.csv','.md','.html')and not p.name.startswith('revision_')]
files += [str(p.relative_to(ROOT)).replace('\\','/')for p in (ROOT/'mapas/mapa1951/shp').iterdir()if p.is_file()]
files += ['datos/circunscripciones1951_1954/'+name for name in ('FUENTES.json','circunscripciones_1951.svg','commons1951.json','control_tablas1951.json','inspeccionar.py','preparar1951.py','resultados1951.json','wiki1951.html')]
for name in files:
    target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
agents=DEST/'AGENTS.md'
note='- **Atlas 1951 por circunscripción (2-nov-2026)**: `mapas/mapa1951/`, 139 circunscripciones de diputados y 11 de delegados, SVG de Faustino Sojo adaptado a contornos históricos, misma proyección y Malvinas grises. Diez puntos de minoría (8 UCR, 2 PP) sin duplicar votos; tamaño con crecimiento limitado al acercar. Capital visible en el principal. Fichas sin desbordes y nombres completos en varias líneas. Torta nacional de Wikipedia; discrepancias locales conservadas en LEEME. SHP y controles en la carpeta. Catálogo y miniaturas clara/oscura registrados; la copia de Pages agrega Fuentes y notas plegable, recuadros, tema y vistas móviles, como en 1904.\n\n'
text=agents.read_text(encoding='utf8');first=text.index('\n')+1
agents.write_text(text[:first]+'\n'+note+text[first:].lstrip('\n'),encoding='utf8')
print('Copiados',len(files),'archivos del atlas; cambios ajenos excluidos.')
