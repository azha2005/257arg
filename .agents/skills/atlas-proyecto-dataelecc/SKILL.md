---
name: atlas-proyecto-dataelecc
description: Flujo de este proyecto (dataeleccproyecto) para armar, corregir o regenerar cualquier atlas electoral argentino: por departamento (1912-2025, diputados, presidente, balotaje, PASO, constituyentes), por circunscripción (1904, 1951), por circuito o radio censal (AMBA, PBA), o escenarios hipotéticos y ucronías. Usalo cuando el usuario pida un mapa o atlas nuevo, un año que falta, cambiar un color, un logo, una escala o la geometría de uno hecho, propagar un cambio a todos, publicarlo en el sitio (GitHub Pages) o empaquetarlo para Commons. Dice qué constructor copiar según la época y el tipo, y las reglas de estilo que el usuario ya fijó. Manda sobre mapa-electoral-wikipedia-1999, que es solo la plantilla genérica.
---

# Atlas del proyecto dataeleccproyecto

Hay dos copias idénticas: `.claude/skills/atlas-proyecto-dataelecc/` (Claude Code) y `.agents/skills/atlas-proyecto-dataelecc/` (Codex). Si se edita una, copiar la carpeta a la otra.

Este skill es el resumen operativo. Las reglas completas, con fecha y motivo, están en `AGENTS.md` (raíz). Si algo no coincide, manda `AGENTS.md`, y la nota más nueva manda sobre la más vieja.

## 0. Antes de tocar nada

1. Leer en `AGENTS.md` las notas del año o la familia (buscar el año y la carpeta) y la sección «Reglas que el usuario fijó».
2. Leer el `LEEME` del atlas más parecido ya hecho. **No partir de la plantilla del skill genérico ni de un build viejo**: partir del constructor vigente de esa familia (tabla de abajo). El usuario lo dijo así para 1926: «basate en los mapas ya subidos de esa época».
3. Si el atlas comparte época con uno **ya subido a Commons** (1922, 1928, 1983, 1989, 1994, legislativas 1983-2001, 2003-2025 y PASO), ese es el modelo visual y **no se regenera** salvo pedido.

## 1. Elegir la familia

| Qué | Constructor vigente | Modelo a mirar |
|---|---|---|
| 1912-1940 por departamento (entreguerras) | `transcripciones/entreguerras/construir.py <año>`; cada `mapas/mapa<año>/build_<año>.py` es un envoltorio de 5 líneas | 1922/1928 subidos, 1930, 1926 |
| 1946-1954, 1973 | `python transcripciones/peronismo/atlas4673.py <clave>` | 1946, 1954 |
| 1958-1965 (Cantón) | `python transcripciones/canton5865/atlas5865.py <año>` | 1962 |
| 1983-1999 presidente | `mapas/mapa<año>/build_<año>.py` | 1989, 1999 |
| 1983-2001 diputados | `python comun/atlas_leg8399.py 1983` (también 1989, 1995, 1999; salen en `mapa<año>dip/`) o build propio (1985-1993, 1997, 2001) | 1997, 2001 |
| 2003-2025 diputados, PASO, presidente y balotaje | `python comun/atlas_leg2003_2025.py <clave>` (`2015`, `2015paso`, `2015pasodip`, `2015pres`, `2015bal`) | 2015pres, 2023 |
| Por circunscripción desde un SVG de Commons | `mapas/mapa1904/geometria_1904.py` + `build_1904.py` | 1904, 1951 |
| AMBA o PBA por circuito o radio censal | `mapas/serieAMBA2005_2023radios/construir.py`, `mapas/mapaAMBA2025radios/`, `mapas/mapaPBA2025sep/` | AMBA 2025 por radio |
| Escenario hipotético o ucronía | copia del build real del año + IPF | `mapa1983hipotetico`, `mapa1989convergencia`, `mapa2003alt` |

Detalle de cada familia (datos, geometría, logos, validador): [references/familias.md](references/familias.md).

## 2. Reglas que no se discuten

Datos:
- **Mapa desde las bases locales; torta, barras y métricas desde la tabla de la Wikipedia** (`comun/wikitop.py` o `wiki_nacional_<año>.json`). Nunca la suma de una cobertura parcial como total nacional. Imprimir «bloques según la base» contra «según Wikipedia» y explicar toda diferencia en el LEEME.
- **Agrupaciones como la Wikipedia en español**: chequear el artículo antes de agrupar (el usuario lo recuerda seguido). Sin etiquetas personalistas en legislativas. No juntar partidos menores para fabricar un ganador «Otros».
- **Lo que falta queda beige y rotulado.** No imputar, no repartir votos entre polígonos, no deducir padrón de un porcentaje. Solo se extrapola o imputa con pedido explícito del usuario, y se documenta con la cuenta (Deseado 1995, Trancas 1936, NE 2009).
- Provincia sin detalle: `DATA.solid` con el total provincial; `DATA.solidExcept` para las unidades que sí tienen dato. Distrito que no votó: gris con clave.
- **Unidad con datos sin polígono: robar el polígono de otro shp, nunca fusionar** (partidos nuevos del GBA con `comun/newpartidos.py`, Berazategui 1962, Tolhuin desde 2019).
- Faltantes de 2013 en adelante: la CNE (padron.gob.ar/publica) tiene captcha; **la consulta la hace el usuario** salvo que dé permiso explícito. Antes probar Wayback (definitivos DINE hasta 2011).

Estilo (detalle en [references/estetica.md](references/estetica.md)):
- Leyenda solo con quien gana alguna unidad (excepción pedida: Cavallo 1999).
- **Un partido, el mismo color en todos los atlas**: grepear los builds antes de elegir. Colores de la Wikipedia; si chocan, el fijo del proyecto. Siete tonos bien separados, ni pastel ni casi negro.
- **Logos de época y reusados**: primero el que ya usa otro atlas del mismo año o partido (el de radios, el publicado); si no, el más cercano anotado en `logos/LICENCIAS.md`; si no hay, sigla. **Nunca generar ni retocar logos con IA de imágenes: solo código.**
- Posición del logo según época: 1904-1983 centrado con zoom; el resto al ras de la barra (`comun/logos_al_ras.py`) salvo las excepciones de `comun/logos_ras_excepciones.json`; lo subido a Commons conserva su posición.
- Encabezado con el molde de los subidos; subtítulo de 34 caracteres como máximo.
- En textos para publicar (LEEME del sitio, tuits, descripciones) **sin rayas largas** (—): guion o coma.

Trabajo:
- **No publicar, subir ni commitear sin pedido.** «Dame el HTML local» quiere decir la copia con la capa del sitio (`python sitio/armar.py copiar <dir>`), no el HTML crudo.
- Commons: **no regenerar paquetes hasta que el usuario lo pida**, y avisar cuáles quedaron desactualizados.
- Máximo 4 procesos y prioridad baja (la CPU del usuario se recalienta).
- Decir con claridad qué se miró en captura y qué no; qué es observado, qué es estimado.

## 3. Pasos

1. **Wikitext** del artículo (`action=parse&prop=wikitext`, User-Agent propio, reintento ante 429), guardado en la carpeta (`w<año>.txt` + fuente JSON con revisión). De ahí: tabla nacional, provincial, colores, infobox.
2. **Datos** de la fuente de la familia (Cantón transcripto, expedientes HCDN, Ernesto, Lupu-Stokes, PolAr, DINE, CNE, AGN). Si hay que transcribir, eso es otro skill: `.agents/skills/transcribir-elecciones/SKILL.md`. La autorización para transcribir no autoriza a mapear.
3. **Mapeo** de listas o columnas a bloques de la Wikipedia, con tabla en el LEEME; controles de cierre por provincia.
4. **Geometría** de la época (1914, 1947/1955, 1960, 1980, 1991, 2001, 2010 + Lezama, radios 2001/2010/2022); emparejar por nombre normalizado con alias explícitos. Malvinas gris del SHP; Antártida con recuadro solo desde 1946.
5. **Build** con el constructor de la familia. Controles impresos: base contra Wikipedia, ganadores por bloque, unidades sin polígono, polígonos sin dato.
6. **Mirar**: captura de cada modo (Edge sin cabeza, `#bare-white-m-<id>`) y revisar leyenda (logos cortados, solapes, subtítulos), pestañas (con más de 4, comprimir el título), recuadros (Tucumán, GBA, Capital), escalas legibles y la ficha al hacer clic. Correr el validador de la familia.
7. **Render**: registrar en `comun/render_transparentes.py` y correrlo con la carpeta; fondo blanco con `comun/render_blanco.py`.
8. **Sitio** (solo si se pide): entrada en `sitio/catalogo.py`, `python sitio/armar.py miniaturas <filtro>`, `python sitio/armar.py indice`, revisar la copia local en escritorio y celular.
9. **Cerrar**: `LEEME_<año>.md` (fuentes, mapeo, decisiones, pendientes, qué no se verificó), nota con fecha en `AGENTS.md` y memoria si cambió una regla.

## 4. Cambios que tocan a varios atlas

Un color, logo, geometría o la plantilla (`.claude/skills/mapa-electoral-wikipedia-1999/assets/template.html`, que usan casi todos) se propaga a **todos** los afectados: rebuild, PNG, miniaturas. Listar al usuario cuáles quedaron con paquete de Commons viejo. Antes de cambiar la plantilla, mirar que no rompa los subidos (sus excepciones).

## Comandos frecuentes

```
python mapas/mapa<año>/build_<año>.py
python comun/atlas_leg2003_2025.py <clave>
python comun/render_transparentes.py mapa<año>
python comun/render_blanco.py mapa<año> atlas_<año>.html
python sitio/armar.py miniaturas <filtro> && python sitio/armar.py indice
python sitio/armar.py copiar <dir>
python commons/paquete.py <año> && python commons/chequeo.py   # solo si el usuario lo pide
```
