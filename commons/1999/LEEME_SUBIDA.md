# Paquete 1999 para Commons — Elecciones presidenciales de Argentina de 1999

Estado al 2026-10-20. Todo **sin subir**. Instrucciones del procedimiento: [`../INSTRUCCIONES_GENERICAS.md`](../INSTRUCCIONES_GENERICAS.md). Usuario de Commons: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. 

| Modo | Versión | Estado |
|---|---|---|
| Resultados por departamento | solo mapa | Para subir |
| Resultados por departamento | con leyenda | Para subir |
| Resultados por departamento | png | Para subir |
| Voto a De la Rua - Alvarez (Alianza) por departamento | solo mapa | Para subir |
| Voto a De la Rua - Alvarez (Alianza) por departamento | con leyenda | Para subir |
| Voto a De la Rua - Alvarez (Alianza) por departamento | png | Para subir |
| Voto a Duhalde - Ortega (Concertacion) por departamento | solo mapa | Para subir |
| Voto a Duhalde - Ortega (Concertacion) por departamento | con leyenda | Para subir |
| Voto a Duhalde - Ortega (Concertacion) por departamento | png | Para subir |
| Voto a Cavallo - Caro Figueroa (AR) por departamento | solo mapa | Para subir |
| Voto a Cavallo - Caro Figueroa (AR) por departamento | con leyenda | Para subir |
| Voto a Cavallo - Caro Figueroa (AR) por departamento | png | Para subir |

## Antes de subir
- Sin impedimentos conocidos más allá de los avisos de abajo.

## Avisos de este atlas
- Son votos del escrutinio por departamento, no porcentajes del provisorio. Las listas se suman por fórmula según la tabla «Acceso a boletas» del artículo (la UCeDé va con Duhalde salvo en Santa Fe, donde llevó a Cavallo; el PDP de Santa Fe y el PAL-PDP de Corrientes con De la Rúa).
- San Luis y Santa Cruz: Cavallo y las demás fórmulas vienen juntos en la fuente y no se reparten. En el mapa de Cavallo esas dos provincias van en beige, con clave en la leyenda; por eso la suma departamental de Cavallo (1.912.819) queda 24.725 votos por debajo de la tabla (1.937.544). Para ellas no hay blancos, nulos ni inscriptos.
- Cavallo (10,22 %) no gana ninguna unidad pero va en la leyenda como tercera fuerza. Sin mapa de participación: la base no trae inscriptos para Buenos Aires, Catamarca, Córdoba ni Tierra del Fuego.
- La Antártida viene aparte en la base (153 votantes; Duhalde 92, De la Rúa 23): se suma a Ushuaia porque el mapa de 1991 no la separa, pero el recuadro de la Antártida se pinta con su propio resultado. La tabla del artículo repite en «otros» de Tierra del Fuego la cifra de Cavallo (8.707); la base da 1.307.
- **Difiere del mapa por departamento vigente** (`Resultados de las Elecciones presidenciales de Argentina de 1999 (por departamento).svg`, De la Rúa 284 y Duhalde 243 unidades; aquí 340 y 198 sobre 538, con las 28 circunscripciones de Capital y los partidos nuevos). Según su autor, aquel se hizo con los porcentajes del provisorio. No se cotejó unidad por unidad: conviene decirlo en la discusión.
- San Salvador (Entre Ríos) y los partidos creados después del censo de 1991 tienen polígono propio (shapefile de 2001 recortado al contorno de 1991).

## Fuentes y licencia
- **Votos:** Base de datos electorales por departamento de Ernesto Calvo (elecciones presidenciales). Referencia bibliográfica: Calvo, Ernesto; Escolar, Marcelo (2005). ''La nueva política de partidos en la Argentina: crisis política, realineamientos partidarios y reforma electoral''. Buenos Aires: Prometeo Libros / PENT. Base no publicada: se contrastó con Lupu y Stokes y, en Mendoza, con la transcripción de la UNCuyo. Coincide con la tabla «Resultados por distrito» del artículo a menos de 0,5 % del total provincial (Formosa, 1 punto en De la Rúa). San Luis y Santa Cruz, que faltan en esa base: Lupu, Noam; Stokes, Susan, ''Argentine Electoral Data, 1912–2003'' (por departamento), que traen solo la Alianza, la Concertación Justicialista y el total de votos positivos.
- **Geometría:** Departamentos de 1991 y, para los partidos y departamentos creados después del censo de 1991 (Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas, 2 de Abril y, en 2001, San Salvador), su polígono del shapefile de 2001 recortado al contorno de 1991; para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}`. Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): Alianza.png, Flag of the Justicialist Party (square version).svg, Logo Accion por la Republica.svg. El detalle de cada licencia está en `logos/LICENCIAS.md`.
- **Fecha de la elección:** 24 de octubre de 1999 (confirmar con el artículo).


## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones presidenciales de Argentina de 1999» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos de 1991 y 2001): [[:commons:File:Elecciones presidenciales de Argentina de 1999 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
