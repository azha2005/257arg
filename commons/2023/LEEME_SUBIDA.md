# Paquete 2023 para Commons — Elecciones legislativas de Argentina de 2023

Estado al 2026-10-20. Todo **sin subir**. Instrucciones del procedimiento: [`../INSTRUCCIONES_GENERICAS.md`](../INSTRUCCIONES_GENERICAS.md). Usuario de Commons: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. 

| Modo | Versión | Estado |
|---|---|---|
| Resultados por departamento | solo mapa | Para subir |
| Resultados por departamento | con leyenda | Para subir |
| Resultados por departamento | png | Para subir |
| Voto a Union por la Patria por departamento | solo mapa | Para subir |
| Voto a Union por la Patria por departamento | con leyenda | Para subir |
| Voto a Union por la Patria por departamento | png | Para subir |
| Voto a La Libertad Avanza por departamento | solo mapa | Para subir |
| Voto a La Libertad Avanza por departamento | con leyenda | Para subir |
| Voto a La Libertad Avanza por departamento | png | Para subir |
| Voto a Juntos por el Cambio por departamento | solo mapa | Para subir |
| Voto a Juntos por el Cambio por departamento | con leyenda | Para subir |
| Voto a Juntos por el Cambio por departamento | png | Para subir |
| Voto a Hacemos por Nuestro Pais por departamento | solo mapa | Para subir |
| Voto a Hacemos por Nuestro Pais por departamento | con leyenda | Para subir |
| Voto a Hacemos por Nuestro Pais por departamento | png | Para subir |
| Participacion por departamento | solo mapa | Para subir |
| Participacion por departamento | con leyenda | Para subir |
| Participacion por departamento | png | Para subir |

## Antes de subir
- Sin impedimentos conocidos más allá de los avisos de abajo.

## Avisos de este atlas
- El resultado nacional sale de la tabla del artículo de Wikipedia; el mapa utiliza los resultados territoriales de la fuente indicada. Los positivos de la base suman 24,059,851 y Wikipedia 24,546,861. No se ajustaron las cifras para forzar igualdad.
- Alianzas y colores de las tablas de Wikipedia (instantáneas y revisiones en fuentes_leg2003_2025/); mapeo de todas las listas y diferencias por bloque en el LEEME y CSV del atlas.
- Sólo los bloques con alguna unidad ganada aparecen en la leyenda nacional. Las demás listas permanecen en las fichas de cada unidad.
- Geometría histórica: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. El límite La Paz/Choya se conserva como en el shapefile histórico.
- Faltantes sin imputación: ninguno.
- Logos tomados del artículo de la elección o del partido. Las reconstrucciones posteriores se anotan como diseño de época no verificado. Ver logos_usados.json y LICENCIAS.md.
- Color final de Unión por la Patria: #009ce4; tabla de Wikipedia: #009FE3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Libertad Avanza: #6c4c98; tabla de Wikipedia: #6C4C99. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Juntos por el Cambio: #fcbc00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Hacemos por Nuestro País: #283084; tabla de Wikipedia: #0B5397. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Por Santa Cruz: #d81b60; tabla de Wikipedia: #0268B3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Movimiento Popular Neuquino: #00708b; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.

## Fuentes y licencia
- **Votos:** Dirección Nacional Electoral, Resultados Provisionales Elecciones 2023, datos por mesa publicados en datos.gob.ar y agregados por departamento/comuna.
- **Geometría:** Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}`. Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): Juntos-Por-El-Cambio-Logo.svg, Logo Hacemos por nuestro pais.svg, Logo JSRN Argentina.svg, Logo La Libertad Avanza (sin águila).svg, Logo Union por la Patria.svg, SER Santa Cruz logo.png. El detalle de cada licencia está en `logos_wikipedia/LICENCIAS.md`.
- **Fecha de la elección:** 22 de octubre de 2023 (cotejada con el artículo).


## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones legislativas de Argentina de 2023» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos de 2010, 15 comunas, lezama y tolhuin separados con polígonos indec 2022 recortados al contorno histórico): [[:commons:File:Elecciones legislativas de Argentina de 2023 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
