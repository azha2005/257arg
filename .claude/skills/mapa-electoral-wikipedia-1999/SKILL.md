---
name: mapa-electoral-wikipedia-1999
description: Genera mapas electorales de Argentina por departamento en el estilo exacto del mapa de Wikipedia "Elecciones presidenciales de Argentina de 1999" (título con caja de bandera, pie con anillo de participación, leyenda de 7 tonos por candidato, insets de Tucumán, Gran San Juan, Gran Mendoza, Resistencia, AMBA, CABA y Antártida), como HTML autónomo con pestañas, tooltip y descarga SVG/PNG. Usalo siempre que el usuario pida un mapa, atlas o poster electoral argentino "estilo Wikipedia", "estilo 1999", "como el de Wikipedia", resultados por departamento o por provincia de cualquier elección (real, histórica, hipotética o simulada), una segunda vuelta o ballotage simulado, una coropleta (participación, margen, % de un candidato) con ese diseño, o cuando adjunte un PNG/SVG de ese estilo y quiera reproducirlo con otros datos, aunque no diga "skill" ni nombre el formato.
---

# Mapa electoral argentino en estilo Wikipedia 1999

Produce un HTML autónomo (≈9 MB, sin recursos externos) con la misma composición que `1999.png`: mismos colores, líneas, marcos, tipografía y disposición. Es interactivo sin perder esa estética: zoom y arrastre del mapa, pasar el mouse muestra una mini ventana y hacer clic fija una tarjeta con el **porcentaje y los votos de cada candidatura** del departamento, filtro por provincia, buscador, pestañas por modo y descargas SVG/PNG/CSV. Todo lo que cambia entre elecciones vive en un `dataset.json`; el generador y la plantilla no se tocan para cambiar de datos.

## Flujo

1. **Reunir lo necesario.** Datos (CSV/tabla/docx) con provincia + departamento + votos o % por candidato. Si el usuario tiene el PNG de referencia, pedirlo: sirve para verificar y para recalibrar. Si no hay datos por departamento, preguntar si alcanza con el nivel provincial (se pinta cada departamento con el color de su provincia).
2. **Emparejar territorios.** `python3 scripts/match_territories.py datos.csv --prov-col … --name-col …` contra los 538 territorios del mapa base (510 departamentos/partidos + 28 circunscripciones de CABA). Resolver lo que quede sin pareja antes de seguir; no rellenar a ciegas.
3. **Armar `dataset.json`** según `references/dataset-schema.md`. Empezar de `scripts/example_prepare_1976.py` (preparación completa de un caso real) y de `references/data-recipes.md`, que dice qué armar para cada tipo de dato: ganador con % por tramos, solo provincias, varias variantes, dos vueltas, segunda vuelta simulada con traspasos (`assets/segunda_vuelta.py`), métricas con color explícito + leyenda propia.
4. **Generar** (una página con todos los modos; `--start-mode` elige con cuál abre): `python3 assets/build_atlas.py --dataset dataset.json --out atlas.html [--start-mode id]`.
5. **Verificar mirando, no suponiendo.** `scripts/shot.sh atlas.html captura.png bare-white` (Edge headless, 1920×1649) y mirar la captura; si hay referencia, `scripts/cmp.ps1 -Ref 1999.png -Cmd pair …` para cotejar regiones lado a lado. Revisar todos los modos con `#bare-white-m-<id>` y que la leyenda, el pie y los totales coincidan con los números de entrada.
6. **Entregar** el HTML y decir con claridad qué es fiel al original y qué es aproximado (abajo).

## Qué es fiel y qué es aproximado (decirlo siempre)
- Fiel: mapa principal (alineado a ~1 px), colores/paleta de tonos, grosores de línea, pie, anillo, leyenda, título, marcos, AMBA, San Juan, CABA, Antártida, fronteras y nombres de países vecinos.
- Aproximado: **Tucumán, Gran Mendoza y Resistencia + Corrientes**: el original usa otra geometría que no está en el mapa base, así que el zoom es parecido, no idéntico. Los tres recuadros de la derecha del título (retratos en 1999) son pestañas de modo. El globo "Exterior" es genérico (gris si no hubo voto exterior). Las fronteras vienen de un recorte del propio PNG de 1999 (arte fijo).
- Los departamentos casi nunca son resultados observados: si son estimaciones o simulaciones, rotularlo en `note`, `subtitle` y al entregar.

## Archivos del skill
- `assets/` → `build_atlas.py` (generador), `template.html` (maqueta + JS, todo dirigido por el dataset), `base_1999_departamentos.svg` (geometría de Wikipedia, CC), `territories.json` (índice de territorios), `geom_rows.json`, `frontiers.png`, `segunda_vuelta.py` (traspaso de votos).
- `scripts/` → `match_territories.py`, `example_prepare_1976.py`, `shot.sh`, `cmp.ps1`, `measure_png.ps1`, `make_frontiers.ps1`, `regsearch.js` + `runreg1.sh` (registro automático de zooms).
- `references/` → `dataset-schema.md` (formato), `data-recipes.md` (qué armar según el dato), `style-spec.md` (medidas del estilo), `insets.md` (cómo se ubican los zooms y sus límites), `gotchas.md` (errores ya cometidos: leerlo antes de tocar el CSS o los scripts).

## Cuándo tocar la plantilla o el generador
Solo si el usuario pide un cambio de diseño o hay otra referencia visual: medir con `scripts/measure_png.ps1`, cambiar `template.html`, regenerar y comparar con `cmp.ps1`. Antes de editar CSS leer `references/gotchas.md` (los selectores con ancestro rompen los `<use>`; el grosor de línea se divide por la escala acumulada).

## Entorno
Las herramientas de verificación asumen Windows con Edge, Git Bash y PowerShell (como en la sesión donde se construyó). En otro sistema, cambiar la ruta de Edge en `shot.sh`/`runreg1.sh` y reemplazar `cmp.ps1` por cualquier comparación de imágenes. La tipografía es Bahnschrift (viene con Windows 10+); en otro sistema cae a una sans condensada.
