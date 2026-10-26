# Paquete 2013 para Commons — Elecciones legislativas de Argentina de 2013

Estado al 2026-10-20. Todo **sin subir**. Instrucciones del procedimiento: [`../INSTRUCCIONES_GENERICAS.md`](../INSTRUCCIONES_GENERICAS.md). Usuario de Commons: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. 

| Modo | Versión | Estado |
|---|---|---|
| Resultados por departamento | solo mapa | Para subir |
| Resultados por departamento | con leyenda | Para subir |
| Resultados por departamento | png | Para subir |
| Voto a Frente para la Victoria y aliados por departamento | solo mapa | Para subir |
| Voto a Frente para la Victoria y aliados por departamento | con leyenda | Para subir |
| Voto a Frente para la Victoria y aliados por departamento | png | Para subir |
| Voto a Frente Progresista Civico y Social y aliados por departamento | solo mapa | Para subir |
| Voto a Frente Progresista Civico y Social y aliados por departamento | con leyenda | Para subir |
| Voto a Frente Progresista Civico y Social y aliados por departamento | png | Para subir |
| Voto a Frente Renovador y aliados por departamento | solo mapa | Para subir |
| Voto a Frente Renovador y aliados por departamento | con leyenda | Para subir |
| Voto a Frente Renovador y aliados por departamento | png | Para subir |
| Voto a Union PRO y aliados por departamento | solo mapa | Para subir |
| Voto a Union PRO y aliados por departamento | con leyenda | Para subir |
| Voto a Union PRO y aliados por departamento | png | Para subir |
| Participacion por departamento | solo mapa | Para subir |
| Participacion por departamento | con leyenda | Para subir |
| Participacion por departamento | png | Para subir |

## Antes de subir
- Sin impedimentos conocidos más allá de los avisos de abajo.

## Avisos de este atlas
- Los votos por departamento salen del escrutinio provisorio por mesa de la DINE (22.369.514 votos positivos sobre 22.612.238 del definitivo, 98,9 %); el resultado nacional del cartel sale de la tabla definitiva del artículo de la Wikipedia.
- Dos departamentos (Ramón Lista en Formosa, 26 mesas; Valle Grande en Jujuy, 11 mesas) tienen 0 mesas escrutadas en el provisorio de la DINE y quedan en beige con clave en la leyenda. En las unidades con escrutinio parcial, la participación se calcula sobre los electores de las mesas computadas y la tarjeta aclara cuántas mesas entraron.
- El partido de Lezama (creado en diciembre de 2009) se escindió del polígono de Chascomús del shapefile de 2010 usando el contorno del INDEC de 2022 (`Departamentos_2022_INDEC.shp`, dominio público / datos abiertos INDEC).
- En la tabla nacional del artículo de la Wikipedia, el subtotal del Frente Progresista Cívico y Social (5.510.949) no incluye el FAP de Entre Ríos (45.026 votos en el definitivo; 128.431 en el provisorio) y suma en Capital Federal los votos de UNEN a senadores (509.446) en vez de diputados (589.545); por eso la suma provisoria del bloque (5.582.090) supera en 1,29 % al subtotal impreso en la tabla.
- El Frente Renovador (color #1B2936 de la tabla de Wikipedia), el Partido Acción Chubutense (#00598C, cambiado de #0087D1 para separarlo del PJ y el Partido Fe), el MPN (#00708B) y el Partido Fe (#1268B3) respetan los colores del artículo o tonos diferenciados dentro de la leyenda.

## Fuentes y licencia
- **Votos:** Dirección Nacional Electoral (DINE), ''Resultados Provisionales Elecciones 2013'' (por mesa, publicados en datos.gob.ar: `mesas_2013.csv`, `votos_partidos_2013.csv` y `votos_no_positivos_2013.csv`), agregados por departamento y comuna.
- **Geometría:** Departamentos de 2010 (con las 15 comunas de Capital Federal) y el partido de Lezama (creado en diciembre de 2009, escindido de Chascomús con el polígono del INDEC 2022 recortado al contorno de Chascomús de 2010). Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}`. Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): Logo Frente para la Victoria.svg, Logo FPCyS.png, Logo del Frente Renovador.png, Propuesta Republicana.png, Frente de Izquierda y de los Trabajadores Logo.svg, Logo Union por Cordoba.png, Frente Renovador de la Concordia Social.png, ACFederal.png, Partido Acción Chubutense.png, Logo de Partido Fe.svg, Logo MPN.png, Flag of the Justicialist Party (square version).svg, PRS logo.png, Logo MIJD.png. Sin página en Commons con ese nombre (se dejaron sin enlace): Logo Union por Cordoba.png. El detalle de cada licencia está en `logos_wikipedia/LICENCIAS.md`.
- **Fecha de la elección:** 27 de octubre de 2013 (confirmar con el artículo).


## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones legislativas de Argentina de 2013» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos de 2010 (con comunas de CABA y Lezama)): [[:commons:File:Elecciones legislativas de Argentina de 2013 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
