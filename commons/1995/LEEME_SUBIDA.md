# Paquete 1995 para Commons — Elecciones presidenciales de Argentina de 1995

Estado al 2026-10-20. Todo **sin subir**. Instrucciones del procedimiento: [`../INSTRUCCIONES_GENERICAS.md`](../INSTRUCCIONES_GENERICAS.md). Usuario de Commons: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. 

| Modo | Versión | Estado |
|---|---|---|
| Resultados por departamento | solo mapa | Para subir |
| Resultados por departamento | con leyenda | Para subir |
| Resultados por departamento | png | Para subir |
| Voto a Menem - Ruckauf por departamento | solo mapa | Para subir |
| Voto a Menem - Ruckauf por departamento | con leyenda | Para subir |
| Voto a Menem - Ruckauf por departamento | png | Para subir |
| Voto a Bordon - Alvarez (FREPASO) por departamento | solo mapa | Para subir |
| Voto a Bordon - Alvarez (FREPASO) por departamento | con leyenda | Para subir |
| Voto a Bordon - Alvarez (FREPASO) por departamento | png | Para subir |
| Voto a Massaccesi - Hernandez (UCR) por departamento | solo mapa | Para subir |
| Voto a Massaccesi - Hernandez (UCR) por departamento | con leyenda | Para subir |
| Voto a Massaccesi - Hernandez (UCR) por departamento | png | Para subir |

## Antes de subir
- Sin impedimentos conocidos más allá de los avisos de abajo.

## Avisos de este atlas
- Son votos del escrutinio por departamento de la base de Ernesto Calvo, no del provisorio; incluye la Antártida (sumada a Ushuaia, que el mapa de 1991 no separa).
- Deseado (Santa Cruz): la base trae solo 221 positivos con 34.173 electores. Se imputaron 26.265 votos (PJ 16.790, FREPASO 4.562, UCR 4.913) para que las tres fórmulas de Santa Cruz coincidan con la tabla provincial; las demás fuerzas quedan como en la base. La ficha lo dice.
- En Tucumán la columna «fr» de la base (167.796 votos) coincide exacto con Bordón en la tabla provincial: se cuenta como FREPASO. Chaco: la tabla provincial de la Wikipedia tiene un error (Menem 207.857, Massaccesi 101.763); se mantuvo la base (227.857 y 91.763), que con las demás provincias da el total nacional exacto.
- Cotejo con el mapa por departamento vigente en Commons: el ganador coincide en el 96 % de las unidades; casi todas las diferencias son de agrupación (aquel pinta por lista, este por fórmula, como la tabla del artículo). General Guido y Vicente López no se explican por eso (`analisis/cotejo_wikipedia/LEEME_COTEJO.md`).
- Diamante (Entre Ríos) trae más votantes que inscriptos en la base: su ficha no muestra participación. Los partidos creados después del censo de 1991 tienen polígono propio (shapefile de 2001 recortado al contorno de 1991).
- El emblema del FREPASO es la recreación de Commons de 2025 (CC0) que usa el artículo; el diseño de época no está verificado (la boleta de 1995 muestra otro recuadro).

## Fuentes y licencia
- **Votos:** Base de datos electorales por departamento de Ernesto Calvo (elecciones presidenciales). Referencia bibliográfica: Calvo, Ernesto; Escolar, Marcelo (2005). ''La nueva política de partidos en la Argentina: crisis política, realineamientos partidarios y reforma electoral''. Buenos Aires: Prometeo Libros / PENT. Base no publicada: se contrastó con Lupu y Stokes y, en Mendoza, con la transcripción de la UNCuyo. Totales por fórmula: Menem 8.685.779 (Wikipedia 8.687.511), Bordón 5.095.318 (5.096.104), Massaccesi 2.955.794 (2.956.137); 20 de 24 provincias coinciden exacto o a menos de 700 votos con la tabla por distrito del artículo.
- **Geometría:** Departamentos de 1991 y, para los partidos y departamentos creados después del censo de 1991 (Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas, 2 de Abril y, en 2001, San Salvador), su polígono del shapefile de 2001 recortado al contorno de 1991; para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}`. Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): Flag of the Justicialist Party (square version).svg, Arg FREPASO logo Remake (cropped).png, Escudo de la UCR.svg. El detalle de cada licencia está en `logos/LICENCIAS.md`.
- **Fecha de la elección:** 14 de mayo de 1995 (confirmar con el artículo).


## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones presidenciales de Argentina de 1995» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos de 1991 y 2001): [[:commons:File:Elecciones presidenciales de Argentina de 1995 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
