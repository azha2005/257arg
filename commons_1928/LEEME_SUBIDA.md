# Paquete 1928 para Commons

## Actualización publicada — 16-oct-2026

Los ocho SVG fueron actualizados como nuevas versiones y los cuatro PNG fueron publicados. Verificación final contra la API de Commons sin caché: **12 IGUAL, 0 DISTINTO, 0 NO SUBIDO** (SHA1). Se conservaron los nombres y las descripciones de los SVG. Los PNG llevan el wikitext preparado y las licencias CC BY 4.0 + CC BY 2.5 AR.

Se revisaron los cuatro modos con leyenda en Commons. En el render grande de resultados se confirmó que las Malvinas aparecen en gris en el mini mapa izquierdo «Provincias» y que el título queda completo. Esta actualización reemplaza los estados pendientes históricos de las secciones siguientes. No se editaron artículos ni páginas de discusión.

Estado al 14-oct-2026. Usuario de Commons: `ItsAHardLife`.

## Estado de la subida
| Archivo | Estado |
|---|---|
| Los 8 SVG (4 «solo mapa» y 4 «con leyenda») | **Tienen una versión local nueva, regenerada el 16-oct-2026** para incorporar el ajuste reciente de Malvinas en el mini «Provincias». Subir como nueva versión conservando los nombres. El contenido de Commons todavía no se actualizó. |
| Los 4 `.png` | **Regenerados el 16-oct-2026** y listos para subir como archivos nuevos. |

El paquete completo se regeneró desde el atlas el 16-oct-2026. El control local con resvg terminó sin errores; falta subir y comprobar en Commons las 12 versiones actuales. El historial de cargas anteriores se conserva en `ESTADO_SUBIDA_SVG.md`.

Después de subir todos, los enlaces de «otras versiones» que hoy están en rojo pasan a azul.

## Qué hay en `subir/`
Cada archivo con su wikitext (`<archivo>.txt`). Por cada modo (`gan`, `ucr`, `opo`, `par`) hay tres versiones:

| Versión | Qué es | Tipografía |
|---|---|---|
| `.png` | el cartel tal cual lo renderiza el atlas (transparente), el mismo estilo que los PNG vigentes de es.wikipedia (p. ej. 2019) | Bahnschrift (parecida a la DIN de Wikipedia), ya rasterizada |
| `(con leyenda).svg` | el mismo cartel en SVG; **texto a trazados** (DejaVu Sans Bold, licencia libre, estirada al ancho de la tipografía del atlas). Se probó con texto vivo (`font-family: 'DIN Next W1G'`, como los SVG de 2023) y en Commons el título se corría sobre el recuadro del año, porque librsvg ignora `textLength` | trazados; cada texto lleva su `<title>` |
| `(solo mapa).svg` | sin ningún texto ni leyenda, como el mapa por departamento de 2019 de Faustino Sojo; cada unidad lleva `<title>` con nombre y resultado | ninguna |

Contenido de los mapas: sin recuadro de la Antártida (en 1928 no había sector reclamado ni voto allí); el rótulo «Sin dato o cifras subsumidas» sale solo en participación, que es el único modo donde alguna unidad lo usa.

Regenerar todo: `python commons_1928/export_svg.py && python commons_1928/build_commons_svg.py && cd commons_1928 && python make_descripciones.py`.
Revisión visual con otro renderizador (resvg): `python commons_1928/chequeo/render_check.py`.

## Cómo subir (paso a paso)
1. Entrar en commons.wikimedia.org con `ItsAHardLife`.
2. Abrir `https://commons.wikimedia.org/wiki/Special:Upload` (formulario clásico; el asistente `Special:UploadWizard` no deja pegar el wikitext completo).
3. «Select file» y elegir el archivo de `commons_1928/subir/`. El nombre de destino debe quedar igual al del archivo.
4. En el cuadro de descripción pegar todo el `.txt` del mismo nombre (`....svg.txt` o `....png.txt`).
5. **Licencia del desplegable: «Ninguna seleccionada»** (la primera). El wikitext ya trae `{{self|cc-by-4.0}}` y `{{Cc-by-2.5-ar}}`; las opciones de «Trabajo propio» agregan GFDL, que no es compatible con CC BY 2.5 AR, y las de «Licencias libres» son para obras ajenas.
6. «Upload file» y esperar unos segundos.
7. Abrir la página del archivo y mirar: la miniatura se dibuja completa (recuadros, mapa; en «con leyenda» también bandera y textos); la sección «Licencia» dice solo CC BY 4.0 y CC BY 2.5 AR; las categorías aparecen abajo. Si hay GFDL o la licencia está duplicada, «Editar» y dejar solo:
```
{{self|cc-by-4.0}}
{{Cc-by-2.5-ar}}
```
8. Si la miniatura sale rota, mandar una captura.

## Subir una nueva versión (para los 8 SVG actuales)
1. Abrir la página del archivo en Commons (p. ej. `File:Elecciones presidenciales de Argentina de 1928 - Resultados por departamento (con leyenda).svg`).
2. Sección «Historial del archivo» → «Subir una nueva versión de este archivo» (o «Upload a new version of this file»).
3. Elegir el archivo del mismo nombre de `commons_1928/subir/`. El nombre no se toca. En el comentario: «Texto a trazados: el título se cortaba en el renderizador de Commons».
4. No hay que pegar el wikitext otra vez: la descripción y la licencia quedan como están.
5. Mirar la miniatura: el título «Elecciones presidenciales de Argentina de» debe terminar antes del recuadro «1928».
6. Repetir con los otros 3. Comprobación posterior: `python` con la API (`prop=imageinfo&iiprop=sha1`) debe dar el mismo SHA1 que `subir/`.

## Anunciar en la discusión del artículo
Hacerlo **antes** de poner el mapa en el artículo (es.wikipedia, `Elecciones presidenciales de Argentina de 1928`, página de discusión).
- No se trata de reemplazar: el mapa del infobox, de Eluan SA (2025), es por provincia; el nuestro es por departamento. Proponer **agregarlo en la sección de resultados** y dejar el del infobox, salvo que haya acuerdo.
- Avisar a Eluan SA en su página de discusión (cortesía; sigue activo).
- Esperar unos días por si alguien objeta antes de editar el artículo.

Texto sugerido (editarlo a gusto):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de las elecciones de 1928 por departamento (división de 1914): [[:commons:File:Elecciones presidenciales de Argentina de 1928 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más versiones con el voto a Yrigoyen, a la oposición y la participación.

Las cifras salen de Cantón (1968), tomo II, y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR). Fuentes y método están en la descripción de cada archivo.

Propongo sumarlo en la sección de resultados, sin reemplazar el mapa por provincia del infobox. ¿Les parece bien? ~~~~
```
Ya existen en Commons dos mapas de 1928 por provincia: `1928 Argentine presidential election.png` (Eluan SA, 2025; el del artículo) y `Elecciones presidenciales de Argentina de 1928.png` (2019).

## Fuentes y licencias
- **Geometría**: Rodríguez, Gonzalo Martín (2022). *Base cartográfica de departamentos para los censos nacionales de la República Argentina desde 1869 a 2010*. CONICET. Dataset, hdl:11336/149867 (`datosdeinvestigacion.conicet.gov.ar/handle/11336/149867`). Contribuidor: Pablo Ernesto De Grande. Licencia **CC BY 2.5 Argentina**, acceso abierto, sin restricción NC. El título de la página dice «1869 a 2022» y la cita «1869 a 2010»: usamos la cita. «2026 v2» figura en `dc.datacite.version` (vista `?show=full`).
- **Por qué CC BY 4.0 y no BY-SA**: CC BY 2.5 permite derivados solo bajo la misma licencia o una posterior, así que BY 4.0 es lo más seguro. Si se prefiere BY-SA, es un cambio de una línea en `make_descripciones.py`. No soy abogado: ante duda, preguntar en el Café de Commons.
- **Votos**: Cantón (1968), tomo II, transcritos a mano desde las imágenes; 11 celdas borrosas resueltas con Lupu y Stokes (`mapa1928/canton/dudosas.txt`). Son hechos; igual conviene citar la página del libro.
- **Logos** (solo en `(con leyenda)` y `.png` del modo ganador), todos «Public domain» según la API de Commons: `Escudo del PDP.svg`, `Monograma utilizado por la UCR Antipersonalista.svg`, `Emblema del Partido Socialista Argentino.svg` y `Flag of Radical Civic Union.svg` (la bandera bicolor sale de este, sin el escudo, que es de 1931).
- **Antártida**: no se dibuja en 1928.

## Verificado
- Categorías: existen en Commons las cinco del wikitext y `SVG maps of Argentina`; también las plantillas `Cc-by-4.0` y `Cc-by-2.5-ar`.
- El «solo mapa» de ganador, ya subido, se ve bien en el renderizador real de Commons.
- Los SVG no tienen CSS, `var()`/`calc()`, `<use>` entre unidades, `<image>` con SVG en data-URI, scripts ni enlaces externos. Los logos están inline. Pesan 2,1 MB.
- Render con resvg igual al del atlas (`chequeo/`), sin errores.

## No verificado
- Los cuatro PNG siguen pendientes de subida. Los ocho SVG están publicados, incluidos los siete subidos en esta tanda.
- Los PNG usan Bahnschrift (fuente de Windows); es salida rasterizada, pero si Commons objetara, la alternativa son los SVG.
- No se consultó a Rodríguez; la licencia de la página alcanza para Commons, pero un aviso al autor sería cortesía.
- Las fechas del reclamo antártico argentino (años 40) están dichas de memoria; confirmarlas antes de citarlas.

## Cambios posteriores
- 14-oct-2026: se quitó el recuadro de la Antártida de los atlas anteriores a 1946 (1916, 1916 ficticio, 1922, 1928, 1930) y el rótulo «Sin dato o cifras subsumidas» sale solo en los modos que lo usan. Los PNG, SVG y wikitext de `subir/` están regenerados.
