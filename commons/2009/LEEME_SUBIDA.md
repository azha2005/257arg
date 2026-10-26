# Paquete 2009 para Commons — Elecciones legislativas de Argentina de 2009

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
| Voto a Acuerdo Civico y Social y aliados por departamento | solo mapa | Para subir |
| Voto a Acuerdo Civico y Social y aliados por departamento | con leyenda | Para subir |
| Voto a Acuerdo Civico y Social y aliados por departamento | png | Para subir |
| Voto a Peronismo Federal y aliados por departamento | solo mapa | Para subir |
| Voto a Peronismo Federal y aliados por departamento | con leyenda | Para subir |
| Voto a Peronismo Federal y aliados por departamento | png | Para subir |
| Voto a Union PRO y aliados por departamento | solo mapa | Para subir |
| Voto a Union PRO y aliados por departamento | con leyenda | Para subir |
| Voto a Union PRO y aliados por departamento | png | Para subir |
| Participacion por departamento | solo mapa | Para subir |
| Participacion por departamento | con leyenda | Para subir |
| Participacion por departamento | png | Para subir |

## Antes de subir
- Sin impedimentos conocidos más allá de los avisos de abajo.

## Avisos de este atlas
- El resultado nacional sale de la tabla de Wikipedia; el mapa combina las fuentes indicadas. No se ajustaron los votos locales para forzar igualdad con Wikipedia.
- Buenos Aires: 134 municipios y todas las listas, incluido Nuevo Encuentro (415.856 votos territoriales frente a 415.961 en el total del distrito). General Alvarado estaba codificado 40, duplicando General Alvear; se restituyó 39 por nombre y contraste con PolAr. San Isidro estaba rotulado S. NICOLAS, pero con su código correcto 106. Siete cifras con separadores de miles mal leídos en General Rodríguez se normalizaron; cada municipio cierra al voto.
- La tabla nacional de Wikipedia tiene subtotales que no suman sus componentes: ACyS 5.705.105 frente a 5.875.774; FPV 5.544.069 frente a 5.698.942. Se conservan los subtotales impresos para el cartel y la agrupación de las filas para el mapa. Véase el control por bloque en mapa2009/.
- Tierra del Fuego: Ushuaia, Río Grande y Antártida conservan su resultado departamental. Ocho votos impugnados de Orcadas quedaron sin escrutar según el PDF. Los totales territoriales no incluyen exterior ni privados de libertad.
- La participación utiliza los electores de PolAr, excepto Tierra del Fuego (DINE definitivo); en Buenos Aires y Valle Grande los votos provienen de la planilla recuperada y el padrón de PolAr.
- Logos del artículo de 2009; para FRC, MPN y UdN-FG se usan los emblemas del partido más cercanos disponibles, con diseño de época no verificado, según el criterio del proyecto. Metadatos y licencias registrados en logos_wikipedia/LICENCIAS.md y mapa2009/logos_metadata.json. Peronismo Federal usa violeta en lugar del gris de Wikipedia para distinguirlo de territorios sin voto; UdN-FG ámbar para distinguirlo de FRC.

## Fuentes y licencia
- **Votos:** PolAr_Data (electorArg), datos provisorios por mesa de INDRA / Atlas Electoral de Andy Tow, agregados por departamento y comuna. Buenos Aires y Valle Grande (Jujuy): planilla del usuario Merged file (15).xls, hoja Sheet1, DN 2009; cifras compatibles con el definitivo, sin votos auxiliares. Se conservó la copia original y los controles. Tierra del Fuego: Dirección Nacional Electoral, tierra_del_fuego_28_de_junio_de_2009.pdf, escrutinio definitivo, páginas 6 a 8.
- **Geometría:** Departamentos de 2010 y las 15 comunas de Capital Federal; Chascomús incluye Lezama, que aún no existía en junio de 2009. Antártida con resultado departamental propio.. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}`. Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): Acuerdo Cívico y Socia.png, Logo Frente para la Victoria.svg, Union Pro.png, Flag of the Justicialist Party (square version).svg, Proyectosur logo.png, Nuevo Encuentro (small).png, Frente Renovador de la Concordia Social.png, Logo MPN.png, Logo Frente Grande.png. El detalle de cada licencia está en `logos_wikipedia/LICENCIAS.md`.
- **Fecha de la elección:** 28 de junio de 2009 (confirmar con el artículo).


## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones legislativas de Argentina de 2009» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos vigentes en junio de 2009 y 15 comunas de Capital): [[:commons:File:Elecciones legislativas de Argentina de 2009 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
