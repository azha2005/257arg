# AMBA por radio censal, elecciones nacionales 2005–2023

Serie solicitada el 1 de noviembre de 2026: diputados nacionales de 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021 y 2023; presidenciales de 2007, 2011, 2015, 2019 y 2023; balotajes de 2015 y 2023. Se agrega la PASO presidencial 2023 por candidato y por fuerza. No incluye senadores ni elecciones provinciales.

Abrir `INDICE.html`. Los atlas son HTML autocontenidos, con búsqueda, zoom, fichas, ganador y hasta cuatro porcentajes. PNG en `png_blanco/serieAMBA2005_2023radios/` y `png_transparentes/serieAMBA2005_2023radios/`; las copias blancas también están en `png_transparentes/all elections white bg/`.

## Cobertura

| Elección | Censo | Cobertura electoral | Método |
|---|---|---|---|
| [2005 · Diputados](atlas_2005dip.html) | 2001 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2007 · Diputados](atlas_2007dip.html) | 2001 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2007 · Presidenciales](atlas_2007pres.html) | 2001 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2009 · Diputados](atlas_2009dip.html) | 2001 | Capital + 40 partidos; 321 radios NE excluidos | Totales municipales completos; perfiles por circuito; NE con proporción municipal uniforme |
| [2011 · Diputados](atlas_2011dip.html) | 2010 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2011 · Presidenciales](atlas_2011pres.html) | 2010 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2013 · Diputados](atlas_2013dip.html) | 2010 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2015 · Diputados](atlas_2015dip.html) | 2010 | Capital + 40 partidos | Escuelas 2015 verificadas: 77.4% de votos; resto, referencia 2025 |
| [2015 · Presidenciales](atlas_2015pres.html) | 2010 | Capital + 40 partidos | Escuelas 2015 verificadas: 77.4% de votos; resto, referencia 2025 |
| [2015 · Balotaje](atlas_2015bal.html) | 2010 | Capital + 40 partidos | Escuelas 2015 verificadas: 75.3% de votos; resto, referencia 2025 |
| [2017 · Diputados](atlas_2017dip.html) | 2010 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2019 · Diputados](atlas_2019dip.html) | 2010 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2019 · Presidenciales](atlas_2019pres.html) | 2010 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2021 · Diputados](atlas_2021dip.html) | 2010 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2023 · Diputados](atlas_2023dip.html) | 2022 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2023 · Presidenciales](atlas_2023pres.html) | 2022 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2023 · Balotaje](atlas_2023bal.html) | 2022 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2023 · PASO por fuerza](atlas_2023pasofuerza.html) | 2022 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |
| [2023 · PASO por candidato](atlas_2023pasocand.html) | 2022 | Capital + 40 partidos | Circuitos → escuelas de referencia 2025 → radios |

AMBA conserva Capital y los mismos 40 partidos de los atlas 2003/2025. Los radios cambian entre censos: 13.392 en 2001, 15.122 en 2010 y 18.101 en 2022. **Los códigos de radio no son una serie territorial armonizada**: comparar un radio de 2001 con otro de 2022 exige una tabla de correspondencia. Para estudiar cambio temporal sobre unidades idénticas conviene generar una segunda serie con una geometría común y documentar esa retroproyección; estos atlas respetan los tres censos indicados.

## Fuentes electorales y agrupaciones

### PASO presidencial 2023: por candidato y por fuerza

El visor adicional `atlas_2023pasointernas.html` permite elegir entre las seis agrupaciones con más de un precandidato registrado en el AMBA: Juntos por el Cambio, Unión por la Patria, FIT-U, MIJD, Proyecto Joven y Frente Liber.AR. Muestra exclusivamente los competidores de la interna seleccionada en el mapa, la torta, las fichas y el CSV. Los porcentajes se normalizan por radio a la suma de votos estimados de esos competidores, no al total de positivos de todas las fuerzas. No se muestran votos absolutos, participación ni categorías ajenas a la interna. Incluye ganador y porcentaje de cada competidor. Un lugar sin votos asignados a esa interna queda beige. A diferencia de la leyenda de la elección completa, aquí se conservan todos los competidores de la interna para mostrar su reparto completo.

Por pedido del usuario, Larreta usa rojo `#e10019` tanto en el mapa completo por candidato como en las internas. Se regeneran las imágenes afectadas. El visor se construye con `internas2023.py` desde el mismo reparto y geometría, sin una nueva interpolación; `CONTROL_INTERNAS2023.json` y `VALIDACION_INTERNAS2023.json` verifican sumas del 100 %, aislamiento de candidatos, fichas y CSV. La renormalización no convierte el reparto original en resultados observados por radio.

Juntos por el Cambio conserva la franja multicolor de Wikipedia por preferencia del usuario. Se usa `logos/bloques_presidenciales/jxc23_franja_completa.png`, extraída nuevamente del original sin eliminar los amarillos que coincidían con el fondo de la leyenda. El recorte es totalmente opaco, continuo y ajustado al marco; su extracción se reproduce con `logos/bloques_presidenciales/extraer_franja_jxc2023.py`.

### Revisión de logos de toda la serie

Los veinte visores ajustan cada imagen al ancho y alto disponibles, centrada y con margen, en lugar de recortarla con escalas heredadas. Se corrigen también los recursos de origen: Cambiemos 2015 y JxC 2019/2023 recuperan los colores que el antiguo borrado de fondo volvía transparentes. Las nuevas extracciones opacas están en `logos/bloques_presidenciales/extraer_bloques_amba.py`. FAP 2011 usa completo `Frente_Amplio_Progresista.gif` de Cronopio Alegre, CC BY-SA 3.0, fechado 2011-07-20, para conservar tanto el color como las puntas de su estrella. CC y UNA 2007 usan el símbolo completo de los archivos de Commons ya conservados, del mismo diseño que las leyendas originales; sus fechas de archivo son posteriores a la elección (2021/2019), con esta reserva, y licencia de dominio público según los metadatos locales. No se sustituyen por diseños nuevos.

`logos_serie.py` aplica los reemplazos por contenido, tanto en diputados como en presidenciales y PASO, sin alterar los recursos de otros atlas. `logos_ajustados_<elección>.json` registra los reemplazos finales sobre los manifiestos originales. `auditar_logos.py` inventaría todos los emblemas visibles, incluidas las seis internas, y produce `AUDITORIA_LOGOS.json` y un contacto visual. `verificar_logos.py` comprueba los marcos reales del navegador en todos los modos y regenera las imágenes de ganador; `verificar_internas2023.py` comprueba además el aislamiento de cada interna y sus CSV. Las coropletas sin leyenda de candidaturas no dibujan estos logos.

En 2023 se evita también el recorte original de LLA y UP: LLA lleva el logotipo tipográfico completo de Commons en la versión blanca ya conservada por el proyecto; UP lleva su símbolo completo extraído del SVG original, separado del nombre por su espacio transparente. Ambos son dominio público según los metadatos locales. El archivo de LLA es del 2023-09-26, posterior a la PASO: se usa como referencia del mismo año con esa reserva, sin atribuirle una verificación de agosto. Se conservan las franjas multicolor de JxC.

`atlas_2023pasocand.html` conserva separadas las 23 listas presidenciales presentes en el AMBA. La fuente nacional registra 27: las otras cuatro son listas de Principios y Valores sin registro electoral en este recorte; no se les inventan resultados locales. El selector «Vista» ofrece Ganador y el porcentaje de cada uno de los 23 precandidatos sobre todos los positivos. Massa/Grabois, Bullrich/Larreta y Bregman/Solano no se suman. Los colores diferentes dentro de cada interna son una decisión de contraste; los emblemas de las alianzas son los ya documentados de Wikipedia. `atlas_2023pasofuerza.html` suma las listas de cada alianza, con enlace directo entre ambas versiones.

La identidad de cada fórmula se cruza por número de agrupación y letra de lista entre la tabla de Wikipedia (`datos/wikipaso/wpaso2023.txt`) y el nomenclador DINE, conservada en `mapeo_paso2023_candidatos.json`. Votos por circuito y lista de `transferencias/circ_2023pp.pkl`, derivados del ZIP oficial de la PASO en `datos_oficiales/2023_paso/`; se cotejan también con su agregado por sección. Método: circuitos → locales y pesos de electores de 2025 → radios 2022 por IDW 1/d², restringido al partido/comuna. No se presenta como una relación mesa–local observada en 2023. Los controles verifican la conservación de cada precandidatura y que la suma de candidatos reproduzca el atlas por fuerza, radio por radio. Las fichas incluyen también las candidaturas menores; valores inferiores a un voto se muestran con decimales porque son estimaciones.

- 2005–2009: PolAr_Data (electorArg / Atlas Electoral de Andy Tow), resultados por mesa conservados en `datos_oficiales/polar/`. Se usan los agregados por circuito de `transferencias/circ_*.pkl`, preparados por `agregar_polar_circuitos.py`.
- 2011–2023: provisorios de la DINE descargados en `datos_oficiales/<año>/`, incluidas las dos segundas vueltas. Agregados por circuito mediante `transferencias/agregar_circuitos.py`. La DINE documenta la cobertura desde 2011 hasta el balotaje 2023 en https://www.argentina.gob.ar/node/437382.
- Agrupación de diputados: los cruces, colores y emblemas de los atlas departamentales ya auditados de cada año. Las listas sin agrupación conservan denominación y votos propios. En 2009 y 2013 se reutilizan sus equivalencias particulares. La columna repetida `0146` de Capital 2009 se suma bajo la misma lista, como en el atlas departamental; no se trata como una fuerza nueva.
- Presidenciales: candidaturas y alianzas correspondientes a cada elección, con los bloques de logos de los mapas presidenciales de Wikipedia/Commons de N2051 (CC0), como en el atlas 2003. Se reutilizan `logos/bloques_presidenciales/` y quedan registrados en `logos_presidenciales_<elección>.json`. Todas las fuerzas ganadoras de los siete mapas presidenciales/balotajes tienen emblema; las menores sin bloque utilizable conservan la sigla. Paletas de los atlas del proyecto y de sus fuentes presidenciales. Las atribuciones están en `logos/LICENCIAS.md`.
- **Torta, barras y métricas son regionales**, calculadas con la fuente electoral del AMBA; no representan el resultado nacional de Wikipedia. Solo las fuerzas que ganan al menos un radio aparecen en la leyenda y las demás se agrupan en Otros, conservando el detalle en las fichas.
- En 2007 presidencial, los 6.933.581 positivos del AMBA coinciden con el atlas por circuito preparado desde la planilla del usuario. No se mezclan blancos/padrón de esa planilla, que no los contiene: salen de PolAr.

## Método principal

Es la adaptación del atlas `mapaAMBA2003radios`, derivado de Poblaciones/LN Data. Un circuito reparte sus votos entre los locales de referencia 2025 que contienen sus polígonos, según los electores de esos locales en 2025. Cada local reparte entre los radios de su partido, circunscripción de Capital hasta 2007 o comuna desde 2009, con peso `1/distancia²` al centroide del radio y piso de distancia de 25 m. No cruza esas unidades. Un radio que recibe menos de un voto pierde su aporte, que se renormaliza entre los restantes. Todas las candidaturas y categorías reciben el mismo peso.

**La presencia de cada escuela en un año anterior y sus pesos relativos son supuestos**, no observaciones de ese año. Barrios y establecimientos posteriores pueden recibir votos anteriores. La población censal no entra en el peso IDW principal. La participación de una ficha es también estimada; no se confunde población censal con padrón electoral.

Los circuitos sin escuela usan su punto interior y se cuentan en cada control. Algunos circuitos sin polígono se ubican con escuelas de 2025 que declaran el mismo circuito y partido: son referencias aproximadas explícitas, nunca polígonos inventados. Se conserva cada caso en `circuitos_sin_poligono_con_escuela2025`. Un circuito de Exaltación de la Cruz en PolAr 2007, `02_037_282`, no empalma con cartografía ni locales; tiene cero votos y queda registrado sin aportar nada. Si faltaran votos positivos de un circuito no ubicable, el partido completo quedaría pendiente en el mapa y sus votos se conservarían en el total regional.

## Mejora de 2015: mesas y locales del mismo año

El archivo `geometria/circuitos_busqueda/galeano_snapshot_2021/establecimientos-ln.geojson` está dentro de una carpeta «2021», pero sus cifras de positivos, blancos, nulos y electores se cotejaron contra la **general presidencial 2015**, mesa por mesa. No se dedujo su año a partir de la carpeta.

Se verificaron 4.830 locales de Capital y la provincia de Buenos Aires; el recorte AMBA y la comprobación de distancia al circuito dejan 3.041 locales usados en la general y 3.039 en el balotaje. Cubren aproximadamente el 77,4 % de los votos en las generales de diputados/presidente y el 75,3 % del balotaje. Cada voto con local verificado parte de ese local real de 2015; el resto mantiene el respaldo aproximado de escuelas 2025. En el balotaje se exige además que el circuito de sus mesas coincida con el declarado por el local. El detalle y las discrepancias están en `cache/control_locales2015.json` y los controles de esas tres elecciones.

La columna auxiliar «votantes» de La Nación es inconsistente con sus propias categorías en numerosos locales; **no se utiliza para votos ni participación**. Las cuatro cifras cotejadas se comparan con la DINE y todos los resultados salen de esta última. Los puntos con distancia superior a 300 m al circuito se rechazan y vuelven al método de respaldo. La aproximación espacial a los hogares sigue existiendo aunque la escuela sea correcta.

## Cartografía

Radios CONICET/Rodríguez: `geometria/cartografia_argentina/conicet/radios/RADIOS_{2001,2010,2022}_V2025-1.zip`. 2001/2022 reutilizan la extracción de los atlas de 2003/2025; 2010 se extrae directamente del SHP con su PRJ y se transforma a WGS84. Se conserva población básica `B_POB_TOT` de 2010.

Circuitos de `geometria/circuitos_serie/por_anio/<año>/aproximada/`, con las reservas propias de cada fuente. Para 2005/2007 se usa el aporte 2003 que conserva códigos INDRA y las 28 circunscripciones. Para Capital 2009 se usa la capa posterior de comunas de 2011 (fuente catalogada 2015), porque la capa histórica de circunscripciones no corresponde a sus nuevos códigos. En Buenos Aires se exige concordancia de nombres o códigos INDRA explícitos; no se igualan códigos INDRA e INDEC por su número. Subcircuitos con letras pueden usar el polígono padre como en el atlas 2025. Ninguna de estas decisiones certifica una geometría histórica legal.

## 2009: NE estimado y sus radios ganadores excluidos

`data__pba_dip_gral2009.csv` tiene vacía la columna `0148` (Nuevo Encuentro) en las 30.792 mesas. La fuente municipal recuperada para el atlas departamental sí tiene Nuevo Encuentro, pero carece del detalle por circuito/mesa. No permite completar un atlas fino sin introducir un reparto adicional de esa fuerza.

El usuario autorizó expresamente estimar NE desde los totales municipales y excluir los radios donde resulte ganador. Por eso esta versión **ya incluye los 40 partidos bonaerenses**, con este modelo condicional:

1. Capital conserva sus votos PolAr. Para Buenos Aires se usan los totales municipales completos del atlas departamental 2009 (`mapas/mapa2009/datos_2009.py`), que contienen NE. Las fuerzas con detalle por circuito conservan su patrón relativo, normalizado por fuerza/bloque al total municipal de esa fuente. No se suman directamente votos de escrutinios diferentes para obtener los nuevos márgenes. Los factores y diferencias están en `ajustes_2009_municipales.json`.
2. NE se distribuye entre radios en proporción a los positivos estimados de las otras fuerzas del mismo municipio. Esto equivale a una **proporción de NE sobre positivos constante en cada municipio**. Es un prior neutral; no aporta una variación intramunicipal de NE que la fuente no tiene. El hecho de que un radio quede excluido depende también de ese supuesto.
3. El modelo da a NE como primero en **321 radios, todos de Morón** (309.380 habitantes del censo 2001). Esos radios quedan beige, sin ganador de reemplazo, en los cinco modos. Se conservan la nota de exclusión y los valores estimados en la ficha. No se descuenta NE para hacer ganar a la segunda fuerza.
4. La torta y las barras son del AMBA completo e incluyen los votos estimados de los radios excluidos; NE va en Otros porque no se dibujan sus radios ganadores. No deben leerse como el resultado del subconjunto de radios coloreados.

También hay dos celdas menores sin perfil en PolAr (un voto de la lista 0188 en el municipio 071 y un voto de 0189 en el 017); se distribuyen según el perfil de positivos del municipio y se registran explícitamente. Blancos y nulos se ajustan a la misma fuente municipal. Los electores siguen siendo PolAr, como en el atlas departamental; no se presentan como padrón definitivo certificado. Las sumas municipales de cada categoría, incluido NE, se cotejan antes del redondeo.

La autorización permite este modelo, pero **no recupera los resultados observados de NE por circuito ni demuestra que esos 321 radios hayan votado de ese modo**. La reserva anterior queda sustituida por la máscara de exclusión solicitada, no por datos recuperados.

## Controles y lectura

**Escala del Frente Renovador en 2013:** se amplía el contraste en «Ganó» y «% FR», de gris claro al gris oscuro de la fuerza, porque la rampa anterior concentraba casi todos los tonos en oscuros similares. Se mantiene el color base del partido y los cortes porcentuales efectivos; en la coropleta se elimina el límite de 0 % duplicado, que producía un intervalo vacío. Votos, porcentajes y ganadores no cambian. Los otros partidos y años conservan sus escalas.

`control_<elección>.json` registra fuentes, censo, circuitos sin geometría/escuela, cobertura, población sin votos, ganadores y error máximo de conservación. `VALIDACION.json` registra la verificación de cada modo en Chrome y el clic de ficha. `CONTACTO.png` reúne los modos Ganó para inspección visual.

Se comprueba la conservación de cada categoría por partido/comuna/circunscripción antes del redondeo, con tolerancia inferior a 0,000001 voto. **La suma espacial de radios contenidos en un circuito no reproduce necesariamente su total**, porque la IDW cruza circuitos dentro del partido. El aporte original de cada circuito se conserva al repartirlo.

Cada preparación genera además un control por población censal dentro de cada circuito (sin escuelas), como en 2003. La coincidencia entre ganadores de ambas variantes es una medida de sensibilidad al reparto; **no es una validación contra votos observados por radio**. Los cortes de colores se ajustan a los percentiles de cada elección; colores más oscuros de dos años no significan necesariamente el mismo porcentaje: consultar sus leyendas.

En las fichas se redondean votos estimados a enteros para lectura; las cifras subyacentes permanecen decimales. Los enteros visibles pueden diferir al sumar. Las mesas no escrutadas o sin votos no permiten inferir el voto faltante.

En 2013, diez radios reciben más votos que electores estimados debido a faltantes/inconsistencias de electores en la fuente por mesa. Conservan sus votos y la reserva; su participación se omite en vez de mostrar más de 100 %. No se inventa un padrón para corregirla.

## Regenerar desde la raíz

Flujo completo con un comando: `python mapas/serieAMBA2005_2023radios/construir.py`. Admite una lista de elecciones, `--sin-preparar` para conservar las asignaciones y `--sin-png` para omitir capturas. También se pueden ejecutar los pasos por separado:

```powershell
python mapas/serieAMBA2005_2023radios/serie.py
python mapas/serieAMBA2005_2023radios/render.py 2023pres
python mapas/serieAMBA2005_2023radios/indice.py
python mapas/serieAMBA2005_2023radios/verificar.py
```

`serie.py` y `verificar.py` admiten una lista de elecciones. Ejecutar `render.py` para cada clave de `KEYS` en `serie.py`. El registro del renderizador común también incluye la serie: `python comun/render_transparentes.py serieAMBA2005_2023radios`.

Dependencias: numpy, pandas, shapely, pyshp, pyproj, Pillow, resvg_py y Playwright/Chrome. No se requiere geopandas. Para abrir en el navegador integrado, servir la raíz por HTTP; el navegador integrado no abre `file://`.

Entrega local, sin Commons ni publicación externa. Fuentes originales y atlas anteriores conservados.
