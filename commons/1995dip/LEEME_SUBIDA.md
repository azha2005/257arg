# Paquete 1995dip para Commons — Elecciones legislativas de Argentina de 1995

Estado al 2026-10-20. **Publicado en Commons y verificado por SHA1**. Véase [registro de publicación](../ESTADO_LEGISLATIVAS_2026-10-20.md). Usuario: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. 

| Modo | Versión | Estado |
|---|---|---|
| Resultados por departamento | solo mapa | Subido y verificado |
| Resultados por departamento | con leyenda | Subido y verificado |
| Resultados por departamento | png | Subido y verificado |
| Voto a Partido Justicialista por departamento | solo mapa | Subido y verificado |
| Voto a Partido Justicialista por departamento | con leyenda | Subido y verificado |
| Voto a Partido Justicialista por departamento | png | Subido y verificado |
| Voto a Union Civica Radical por departamento | solo mapa | Subido y verificado |
| Voto a Union Civica Radical por departamento | con leyenda | Subido y verificado |
| Voto a Union Civica Radical por departamento | png | Subido y verificado |
| Voto a Frente Pais Solidario por departamento | solo mapa | Subido y verificado |
| Voto a Frente Pais Solidario por departamento | con leyenda | Subido y verificado |
| Voto a Frente Pais Solidario por departamento | png | Subido y verificado |
| Participacion por departamento | solo mapa | Subido y verificado |
| Participacion por departamento | con leyenda | Subido y verificado |
| Participacion por departamento | png | Subido y verificado |

## Antes de subir
- Sin impedimentos conocidos más allá de los avisos de abajo.

## Avisos de este atlas
- En Tucumán el código fr de la base es el FREPASO y frep es Fuerza Republicana; en Jujuy fr es Fuerza Republicana agrupada con el MODIN. El Partido Federal va con la UCR en Córdoba y con el PJ en los demás distritos, como la tabla nacional.
- Córdoba: la base no trae la columna del Partido Federal; el residuo de cada departamento entre positivos declarados y suma de las fuerzas (14.914 votos en total, la Wikipedia da 14.915) se imputa a la UCR, con nota en la ficha. San Juan trae la fila de positivos repetida: se toma la primera, que coincide con la suma de las fuerzas.
- Deseado (Santa Cruz): la base trae un registro incompleto; por pedido del usuario se calcula como el total provincial de la Wikipedia menos los otros seis departamentos, fuerza por fuerza y para blancos, nulos, votantes e inscriptos (original y cálculo en `mapa1995dip/deseado_extrapolado.json`). No es un resultado departamental observado.
- Los partidos creados después del censo de 1991 tienen su propio polígono, tomado del shapefile de 2001 y recortado al contorno de 1991. El Sector Antártico de la base se suma a Ushuaia.
- Logos reutilizados del proyecto; en varios emblemas provinciales el diseño de época no está verificado (ver `logos_wikipedia/LICENCIAS.md`).

## Fuentes y licencia
- **Votos:** Base de datos electorales por departamento de Ernesto Calvo, hojas por provincia de `TPDENP1995T.xls` (diputados nacionales). Base no publicada: se contrastó con las tablas nacional y provinciales del artículo de la Wikipedia (PJ −0,02 %, UCR −0,003 %, FREPASO −0,03 %).
- **Geometría:** Departamentos de 1991 y, para los partidos y departamentos creados después del censo de 1991 (Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas, 2 de Abril y, en 2001, San Salvador), su polígono del shapefile de 2001 recortado al contorno de 1991; para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**: por eso los archivos llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}` (ver las instrucciones genéricas).
- **Logos** (solo «con leyenda» y PNG): Flag of the Justicialist Party (square version).svg, Escudo de la UCR.svg, Arg FREPASO logo Remake (cropped).png, Pacto Autonomista - Liberal.png, Logo MPN.png. El detalle de cada licencia está en `logos_wikipedia/LICENCIAS.md`.
- **Fecha de la elección:** 14 de mayo de 1995 (puesta de memoria; confirmar con el artículo).
- **Categorías de Commons que no existen y se omitieron:** 1995 Argentine legislative election, 1995 Argentine presidential election.

## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones legislativas de Argentina de 1995» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos de 1991 y 2001): [[:commons:File:Elecciones legislativas de Argentina de 1995 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```

## Publicación del 20-oct-2026

Verificados 15 nombres: 15 imágenes distintas y 0 redirecciones a imágenes idénticas. Todas coinciden con el SHA1 local. Artículo publicado conservando sus mapas previos; ver el registro enlazado arriba.
