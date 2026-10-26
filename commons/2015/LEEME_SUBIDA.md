# Paquete 2015 para Commons — Elecciones legislativas de Argentina de 2015

Estado al 2026-10-20. Todo **sin subir**. Instrucciones del procedimiento: [`../INSTRUCCIONES_GENERICAS.md`](../INSTRUCCIONES_GENERICAS.md). Usuario de Commons: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. 

| Modo | Versión | Estado |
|---|---|---|
| Resultados por departamento | solo mapa | Para subir |
| Resultados por departamento | con leyenda | **NO subir todavía** |
| Resultados por departamento | png | **NO subir todavía** |
| Resultados por departamento | con leyenda y siglas (sin emblemas dudosos) | Para subir |
| Resultados por departamento | png con siglas (sin emblemas dudosos) | Para subir |
| Voto a Frente para la Victoria por departamento | solo mapa | Para subir |
| Voto a Frente para la Victoria por departamento | con leyenda | **NO subir todavía** |
| Voto a Frente para la Victoria por departamento | png | **NO subir todavía** |
| Voto a Frente para la Victoria por departamento | con leyenda y siglas (sin emblemas dudosos) | Para subir |
| Voto a Frente para la Victoria por departamento | png con siglas (sin emblemas dudosos) | Para subir |
| Voto a Cambiemos por departamento | solo mapa | Para subir |
| Voto a Cambiemos por departamento | con leyenda | **NO subir todavía** |
| Voto a Cambiemos por departamento | png | **NO subir todavía** |
| Voto a Cambiemos por departamento | con leyenda y siglas (sin emblemas dudosos) | Para subir |
| Voto a Cambiemos por departamento | png con siglas (sin emblemas dudosos) | Para subir |
| Voto a Unidos por una Nueva Alternativa por departamento | solo mapa | Para subir |
| Voto a Unidos por una Nueva Alternativa por departamento | con leyenda | **NO subir todavía** |
| Voto a Unidos por una Nueva Alternativa por departamento | png | **NO subir todavía** |
| Voto a Unidos por una Nueva Alternativa por departamento | con leyenda y siglas (sin emblemas dudosos) | Para subir |
| Voto a Unidos por una Nueva Alternativa por departamento | png con siglas (sin emblemas dudosos) | Para subir |
| Voto a Frente de Izquierda y de los Trabajadores por departamento | solo mapa | Para subir |
| Voto a Frente de Izquierda y de los Trabajadores por departamento | con leyenda | **NO subir todavía** |
| Voto a Frente de Izquierda y de los Trabajadores por departamento | png | **NO subir todavía** |
| Voto a Frente de Izquierda y de los Trabajadores por departamento | con leyenda y siglas (sin emblemas dudosos) | Para subir |
| Voto a Frente de Izquierda y de los Trabajadores por departamento | png con siglas (sin emblemas dudosos) | Para subir |
| Participacion por departamento | solo mapa | Para subir |
| Participacion por departamento | con leyenda | **NO subir todavía** |
| Participacion por departamento | png | **NO subir todavía** |
| Participacion por departamento | con leyenda y siglas (sin emblemas dudosos) | Para subir |
| Participacion por departamento | png con siglas (sin emblemas dudosos) | Para subir |

## Antes de subir
- **Versiones con logos en espera («con leyenda» y PNG):** Revisar licencias/fechas de los logos reutilizados antes de subir las versiones con emblemas. La variante con siglas omite estos emblemas.

## Avisos de este atlas
- El resultado nacional sale de la tabla del artículo de Wikipedia; el mapa utiliza los resultados territoriales de la fuente indicada. Los positivos de la base suman 22,679,308 y Wikipedia 23,314,026. No se ajustaron las cifras para forzar igualdad.
- Alianzas y colores de las tablas de Wikipedia (instantáneas y revisiones en fuentes_leg2003_2025/); mapeo de todas las listas y diferencias por bloque en el LEEME y CSV del atlas.
- Sólo los bloques con alguna unidad ganada aparecen en la leyenda nacional. Las demás listas permanecen en las fichas de cada unidad.
- Geometría histórica: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. El límite La Paz/Choya se conserva como en el shapefile histórico.
- Faltantes sin imputación: ninguno.
- Logos tomados del artículo de la elección o del partido. Las reconstrucciones posteriores se anotan como diseño de época no verificado. Ver logos_usados.json y LICENCIAS.md.
- Color final de Frente para la Victoria (FpV): #50ade6; tabla de Wikipedia: #75AADB. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Cambiemos: #f4ce00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Unidos por una Nueva Alternativa (UNA): #231f20; tabla de Wikipedia: #4C2882. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Compromiso Federal (CF): #1aff98; tabla de Wikipedia: #66FFCC. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Chubut Somos Todos (ChuSoTo): #c62828; tabla de Wikipedia: #2ab665. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
- Color final de Movimiento Popular Neuquino (MPN): #00708b; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.

## Fuentes y licencia
- **Votos:** Dirección Nacional Electoral, Resultados Provisionales Elecciones 2015, datos por mesa publicados en datos.gob.ar y agregados por departamento/comuna.
- **Geometría:** Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}`. Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): ACFederal.png, Cambiemos logofinal.png, Chubut Somos Todos logo.png, Logo Frente para la Victoria.svg, Logo MPN.png, Una logo.png. El detalle de cada licencia está en `logos_wikipedia/LICENCIAS.md`.
- **Fecha de la elección:** 25 de octubre de 2015 (cotejada con el artículo).


## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones legislativas de Argentina de 2015» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos de 2010, 15 comunas de capital federal y lezama separado): [[:commons:File:Elecciones legislativas de Argentina de 2015 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
