import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "comun")]  # módulos compartidos (reorganización: ver README)
from pathlib import Path
import json,sys,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from atlas_leg8399 import INFO
sys.path.insert(0,str(ROOT/'commons'))
from config import ATLAS
fmt=lambda v:f'{v:,}'.replace(',','.')
for y in [1983,1989,1995,1999]:
    folder=ROOT/f'mapas/mapa{y}dip';a=json.loads((folder/'auditoria.json').read_text(encoding='utf8'));ds=json.loads((folder/f'dataset_{y}dip.json').read_text(encoding='utf8'))
    cfg=ATLAS[f'{y}dip'];cands=ds['candidates']
    name=lambda c:(cands[c]['n']+(' ('+cands[c]['sub']+')' if cands[c].get('sub') and cands[c]['sub']!='y aliados' else ''))
    solid=a.get('solidas',{})
    L=[f'# Atlas legislativo de {y} (diputados nacionales)','',
       f'Atlas de las elecciones de diputados nacionales del {cfg["fecha"]}, por departamento. Es independiente del atlas presidencial'+(' del mismo año' if y in (1983,1989,1995) else '')+'. '
       f'{a["con_datos"]} de {a["unidades"]} unidades con votos de la base'+(f'; {", ".join(solid)} en color sólido con el total provincial de la Wikipedia' if solid else '')+'; las Islas Malvinas en gris.','',
       '## Reproducir','',f'```',f'python mapa{y}dip/build_{y}dip.py',f'python render_transparentes.py mapa{y}dip',f'python render_blanco.py mapa{y}dip atlas_{y}_diputados.html',f'python commons/paquete.py {y}dip','python tools/documentar_leg8399.py','```','',
       '## Fuentes','',f'- Votos por departamento: base de Ernesto Calvo, `base8399/ernesto/{y}_diputados/dpto_partidos.csv` (hojas de `TPDENP{y}T.xls`).',
       f'- Resultado nacional del cartel (torta, barras, métricas): tabla del artículo [Elecciones legislativas de Argentina de {y}](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_{y}), clave `{y}_diputados` de `wikitop.py`.',
       f'- Copias del artículo en esta carpeta: `w{y}.txt`, `wiki.html`, `wiki_rows.json` (tabla nacional) y `wiki_prov_listas.json` (tablas provinciales).',
       '- Geometría: '+('departamentos del censo de 1980 (`mapa'+str(y)+'/units_raw.pkl`).' if cfg['geom']=='1980' else 'departamentos de 1991 con los partidos nuevos con polígono propio (`mapa'+('2001' if y==1999 else str(y))+'/units_raw.pkl`).'),
       '- Constructor: `atlas_leg8399.py` (compartido con los otros tres años). `FAMS[%d]` asigna cada código de la base a un bloque de la tabla nacional; `bloc()` tiene las excepciones por provincia.'%y,'',
       '## Decisiones','']+['- '+x for x in cfg['avisos']]
    L+=['','## Bloques: base contra Wikipedia','','| Bloque | Base | Wikipedia | Diferencia |','|---|---:|---:|---:|']
    L+=[f'| {r["bloque"]} | {fmt(r["base"])} | {fmt(r["wikipedia"])} | {r["diferencia"]:+,} |'.replace(',','.') for r in a['comparacion']]
    L+=['','La base incluye '+(' y '.join(solid)+' con su total provincial y ' if solid else '')+'las imputaciones de abajo. Las diferencias restantes no se reparten entre departamentos.']
    if a.get('imputados'):
        L+=['','## Imputaciones','','| Provincia | Departamento | Bloque | Votos |','|---|---|---|---:|']+[f'| {x["prov"]} | {x["nombre"]} | {x["bloque"]} | {fmt(x["votos"])} |' for x in a['imputados']]
    pd=[x for x in a.get('positivos_distintos',[])]
    if pd:
        L+=['','## Positivos declarados distintos de la suma de las fuerzas','','Los porcentajes se calculan sobre la suma de las fuerzas; el valor declarado queda en la ficha.','','| Provincia | Departamento | Declarados | Suma |','|---|---|---:|---:|']+[f'| {x["prov"]} | {x["nombre"]} | {fmt(x["declarados"])} | {fmt(x["suma"])} |' for x in pd]
    if a.get('filas_repetidas'):
        L+=['',f'Filas de métricas repetidas en la base (se toma la primera): {len(a["filas_repetidas"])} departamentos de '+', '.join(sorted({x["prov"] for x in a["filas_repetidas"]}))+'.']
    if a.get('padron_inconsistente'):
        L+=['','Padrón inconsistente (más votantes que inscriptos; gris claro en participación y sin ese dato en la ficha): '+', '.join(f'{x["nombre"]} ({x["prov"]}, {fmt(x["votantes"])} votantes / {fmt(x["inscriptos"])} inscriptos)' for x in a['padron_inconsistente'])+'.']
    L+=['','## Modos y leyenda','',f'Pestañas: {", ".join(m["tile"] for m in ds["modes"])}.'+('' if any(m['id']=='par' for m in ds['modes']) else ' Sin participación: la base no trae el padrón en todos los departamentos.'),'',
        'Ganadores (unidades'+(', cada provincia sólida cuenta una' if solid else '')+'): '+'; '.join(f'{name(c)} {n}' for c,n in sorted(a['ganadores'].items(),key=lambda kv:-kv[1]))+'.','',
        'La leyenda lleva solo las fuerzas que ganan alguna unidad; las demás van a «otros» en la torta y siguen en la ficha de cada unidad. Logos y reservas de época en `logos_wikipedia/LICENCIAS.md`.']
    pend=[x for x in a['sin_dato'] if x['nombre']!='Islas Malvinas']
    L+=['','## Pendientes','']+(['- Sin dato: '+', '.join(f'{x["nombre"]} ({x["prov"]})' for x in pend)] if pend else [])
    L+=['- Deseado (Santa Cruz) es un cálculo, no un dato observado: reemplazarlo si aparece el registro departamental.' for x in a.get('registros_extrapolados',[])]
    if solid:L+=['- '+' y '.join(solid)+': buscar los resultados por departamento (escrutinio definitivo o prensa provincial).']
    if not pend and not solid and not a.get('registros_extrapolados'):L+=['- Nada pendiente en la cobertura; las diferencias con la Wikipedia están arriba.']
    L+=['','## Commons','',f'Paquete local en `commons/{y}dip/subir/` (sin subir). Ver `commons/{y}dip/LEEME_SUBIDA.md`.']
    (folder/f'LEEME_{y}dip.md').write_text('\n'.join(L)+'\n',encoding='utf8')
bronca=ROOT/'mapas/mapa2001bronca'
a=json.loads((bronca/'auditoria.json').read_text(encoding='utf8'))
(bronca/'LEEME_2001bronca.md').write_text('''# Legislativas de 2001 con voto bronca

Variante analítica del atlas histórico de 2001, sin modificarlo. Ejecutar `python mapa2001bronca/build_2001bronca.py`.

Voto bronca = blancos + nulos. Se trata como una opción de comparación capaz de ganar unidades, no como una candidatura histórica. Todos los porcentajes de votos de los cinco modos usan positivos + blancos + nulos; la participación conserva su denominador de inscriptos. Los blancos y nulos se agrupan una sola vez en las fichas.

Los datos territoriales y la agrupación provincial de alianzas proceden exactamente del atlas original de 2001 y de sus reglas MAPCOL/GROUP2BLOC/OVERRIDE. El gráfico nacional conserva las cifras de Wikipedia: 2.022.587 blancos + 2.486.296 nulos = 4.508.883 votos bronca; denominador 18.798.991; 23,98 %. El mapa hereda las discrepancias entre los votos territoriales y nacionales documentadas en mapa2001/LEEME_2001.md. No se ajustaron esos votos.

Los bloques que pierden todas sus unidades al introducir el voto bronca pasan a otros en la torta. Se conservan en el detalle local. El símbolo de urna es un gráfico original explicativo, no un emblema histórico; SVG en logos_wikipedia/Voto_bronca_urna.svg. Los demás logos y sus reservas se conservan del atlas de 2001.

PAUFE usa el ámbar #f59e0b, igual que el atlas original de 2001 (unificado el 19-oct-2026 a pedido del usuario; la Wikipedia usa un gris que se confundía con el voto bronca #5b5b5b).

Paquete local: commons/2001bronca/subir/. Los nombres de los archivos incluyen «voto bronca» para distinguirlos de los resultados sobre positivos. Las descripciones en español e inglés explican el denominador y la naturaleza analítica. Todo sin subir.

Auditoría:
'''+json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for name in ['mapa1983dip','mapa1989dip','mapa1995dip','mapa1999dip','mapa2001bronca']:
    for f in (ROOT/'png_blanco'/name).glob('*.png'):shutil.copy2(f,ROOT/'png_transparentes/all elections white bg'/f.name)
