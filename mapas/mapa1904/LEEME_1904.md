# Diputados nacionales 1904 · circunscripciones uninominales

`python mapas/mapa1904/build_1904.py` genera el HTML autocontenido y el dataset.
Dependencias: pandas, lxml, svgelements, shapely, numpy y scipy. La geometría
adaptada se guarda en una caché descartable cuyo hash incluye SVG, código y
geometría histórica de referencia.

## Resultados y afiliación

Fuente: [tabla por circunscripción de Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1904),
revisión 175926717, con referencias a expedientes del HCDN y diarios de sesiones.
Se guardan el wikitext, la tabla HTML y `candidatos_1904.csv` con las 199 filas.
No se mezclan las elecciones parciales de julio de 1904, 1905 y siguientes.

- 120 circunscripciones; 60 renovadas y 60 sin elección.
- Votos publicados en 59 de las 60 renovadas: 129.796 votos a candidatos.
- Catamarca 2: Guillermo Correa, PAN, figura electo pero sin cifra de votos.
  Queda beige; su elección conocida cuenta al comprobar las 60 bancas.
- Ganador: el candidato individual más votado. Los competidores del mismo
  partido no se suman para cambiar al ganador de una circunscripción.
- La torta y las barras suman los votos publicados por afiliación partidaria
  más cercana, pedido del usuario. Son un agregado parcial de 59/60, no un
  escrutinio nacional completo. Sin padrón ni participación inventados.
- PAN incluye sus aliados de Partidos Unidos, Asociación Popular de BA,
  Partido Provincial de Salta y Tucumán y los partidos Democrático y
  Constitucional de San Juan, siguiendo las afiliaciones y enlaces del artículo.
  PAN disidente conserva el Partido Provincial bonaerense y Unión Popular
  tucumana. PA, PL, PR, UCN, PS, UCR e independientes quedan separados.
  Los siete votos rotulados «Otros» sin partido identificado quedan en Otros.
- Las fichas individuales y el CSV conservan nombres, partido original y votos
  de cada candidatura. Las fichas provinciales agregan por afiliación.
- La leyenda del artículo suma 53 bancas y difiere de su tabla de 60:
  `CONTROL_1904.json` conserva ambos datos. Se usa la tabla, sin corregir el artículo.

## Cartografía

El SVG aportado por el usuario contiene las 120 circunscripciones y copias
ampliadas de varias unidades. Se quitan las copias ampliadas y se conservan
los trazos geográficos de cada circunscripción; los recuadros se generan desde
esos mismos trazos.

Por pedido del usuario, se adapta el marco cartográfico a `Departamentos_1914`,
la misma referencia del atlas 1912, y a su proyección equirectangular con
coseno de 38° y 44 píxeles por grado. **Las unidades siguen siendo las
circunscripciones del SVG, no municipios ni departamentos.** El SHP se usa
solo como contorno y referencia de proyección. No se asigna ningún voto a
un municipio ni se reparte o recalcula un resultado.

`geometria_1904.py` ajusta el marco provincial y sus controles de perímetro,
deforma los trazos internos y los recorta al contorno de referencia. Las
rendijas geométricas se cierran con la circunscripción contigua. Es una
adaptación aproximada de la cartografía de Commons, no una certificación de
límites legales de 1904. `CONTROL_GEOMETRIA.json` registra los controles y la
cobertura del marco SHP. Los Andes se mantiene como territorio nacional;
sin recuadro antártico. Malvinas en gris.

Malvinas: el mapa grande y el pequeño de provincias reutilizan exactamente
el trazo del atlas 1912, en la misma proyección y con la misma simplificación
del SHP. Contorno negro en el grande y gris de 5 px antes de la escala en el
pequeño, como los demás atlas. No se colorean con resultados electorales.

Capital Federal conserva las veinte circunscripciones históricas numeradas
de Vélez Sarsfield (1) a Socorro (20), las mismas identificadas en el SVG y en
el atlas 1912. Se usan directamente los veinte trazos nativos del SHP, sin
deformación, con simplificación de 0,001 píxeles de póster y cuatro decimales
en el SVG. Así se conserva detalle en la costa y las divisiones del recuadro,
sin cambiar números, nombres, candidatos ni votos.

Ganó lleva la escala de siete tonos habitual del proyecto según el porcentaje
del candidato vencedor. PAN, PR y PS tienen coropletas por deciles, sumando
los votos de todos sus candidatos. Las fichas siguen mostrando el ganador
individual. Se conservan gris de «sin elección», gris claro de territorio y
beige de votos pendientes.

## Atribución y licencias

- [SVG de circunscripciones](https://commons.wikimedia.org/wiki/File:Mapa_de_las_elecciones_legislativas_de_Argentina_de_1904_por_circunscripci%C3%B3n.svg):
  Faustino Sojo, 19 de junio de 2022, CC BY-SA 4.0. Archivo original preservado
  en `circunscripciones_1904.svg`; metadatos en `commons_fuente.json`.
- Shapefile histórico: base de departamentos de Rodríguez/CONICET usada por
  el proyecto, CC BY 2.5 Argentina. La adaptación de la cartografía SVG
  conserva CC BY-SA 4.0 y estas atribuciones.
- Datos transcritos del artículo: Wikipedia, CC BY-SA 4.0; fuentes primarias
  enumeradas en el artículo. No se presenta esta transcripción como una nueva
  verificación independiente de cada acta del HCDN.
- Pedido del usuario: mismos logos de `1916alt`: escarapela PAN, bandera
  circular UCR y emblema PS. Se conservan centrados con zoom; sin línea blanca
  bajo los logos. PAN/UCR son recreaciones del cartel aportado para ese atlas,
  sin diseño exacto de 1904 verificado. No se usa el logo del PDP (fundado después).
  Otros partidos con sigla. Malvinas importadas del SHP histórico, en gris.

## Comprobación

`python mapas/mapa1904/verificar_1904.py`: sumas locales y por afiliación,
conteos de cobertura, cuatro modos sin errores JavaScript, leyenda dentro
del póster, fichas y descargas SVG/CSV. Se revisan visualmente los cuatro
modos, recuadros y posición de los logos. `VALIDACION.json` guarda el control.
