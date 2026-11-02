# Paquete 2001 para Commons — Elecciones legislativas de Argentina de 2001

Estado al 2026-10-20. Todo **sin subir**. Instrucciones del procedimiento: [`../INSTRUCCIONES_GENERICAS.md`](../INSTRUCCIONES_GENERICAS.md). Usuario de Commons: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. 

| Modo | Versión | Estado |
|---|---|---|
| Resultados por departamento | solo mapa | Para subir |
| Resultados por departamento | con leyenda | Para subir |
| Resultados por departamento | png | Para subir |
| Voto a Concertacion Justicialista por departamento | solo mapa | Para subir |
| Voto a Concertacion Justicialista por departamento | con leyenda | Para subir |
| Voto a Concertacion Justicialista por departamento | png | Para subir |
| Voto a Alianza (UCR, FREPASO y aliados) por departamento | solo mapa | Para subir |
| Voto a Alianza (UCR, FREPASO y aliados) por departamento | con leyenda | Para subir |
| Voto a Alianza (UCR, FREPASO y aliados) por departamento | png | Para subir |
| Voto a ARI y socios por departamento | solo mapa | Para subir |
| Voto a ARI y socios por departamento | con leyenda | Para subir |
| Voto a ARI y socios por departamento | png | Para subir |

## Antes de subir
- Sin impedimentos conocidos más allá de los avisos de abajo.

## Avisos de este atlas
- La base de Ernesto trae menos votos que la tabla del artículo: 13,97 millones de positivos contra 14,29 (−2,3 %). El resultado nacional del cartel sale de la tabla; los departamentos, de la base.
- Bloques como la tabla del artículo: «Concertación Justicialista» suma el PJ, el Partido Nuevo de Corrientes, Unión por Córdoba (con el UCeDé cordobés), el Frente por un Nuevo País, la Alianza de Centro y demás frentes que la tabla agrega; el Frente Unión por Buenos Aires (Capital) es fila aparte. «Alianza» y «ARI» siguen sus totales. Los grupos de Ernesto que la tabla separa o junta distinto se corrigieron columna por columna (`mapa2001/LEEME_2001.md`).
- Colores de la Wikipedia (PJ #318CE7, Alianza #DC0143, ARI #6FB53E, AR #3E5298, PD #1F2F6B, MPN #0070B8). PAUFE lleva el ámbar del proyecto (#F59E0B) en lugar del gris de la Wikipedia, que se confundía con «otros». Excepción: el Frente Unión por Buenos Aires lleva en la tabla el azul del PJ y se le dio uno más claro para distinguirlo. El logo del ARI de Commons figura de 2002 (diseño de época no verificado); el de la Concertación es de 2019 y se usó la bandera del PJ.
- En 2001 hubo muchos votos en blanco y nulos (24 %): los porcentajes del mapa son sobre votos positivos, como el resto de los atlas.
- Los partidos creados después del censo de 1991 y San Salvador (Entre Ríos) tienen su propio polígono, tomado del shapefile de 2001. Los códigos de departamento de las planillas de Santiago del Estero y San Luis siguen la numeración de 1995 y 1993 (se eligió por la correlación de votos; ver `base8399/ernesto/LEEME.md`).
- Dos partidos bonaerenses (Almirante Brown y General San Martín) traen una columna con 1.000 votos de más que no cierra con los positivos: se usó la suma de las listas.

## Fuentes y licencia
- **Votos:** Base de datos electorales por departamento de Ernesto Calvo, planillas por provincia de `2001 x DTO/Diputados Nacionales` (diputados nacionales). Base no publicada: se contrastó con las tablas provinciales del artículo de la Wikipedia (queda 0 a 3 % por debajo en casi todas las provincias, 6 % en Salta).
- **Geometría:** Departamentos de 1991 y, para los partidos y departamentos creados después del censo de 1991 (Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas, 2 de Abril y, en 2001, San Salvador), su polígono del shapefile de 2001 recortado al contorno de 1991; para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{self|cc-by-4.0}}` + `{{Cc-by-2.5-ar}}`. Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): Flag of the Justicialist Party (square version).svg, Alianza.png, Ari Logo.svg, Logo Accion por la Republica.svg, Escudo del Partido Demócrata (Argentina).svg, Logo MPN.png. El detalle de cada licencia está en `logos/LICENCIAS.md`.
- **Fecha de la elección:** 14 de octubre de 2001 (confirmar con el artículo).


## Discusión del artículo
Texto sugerido para la página de discusión de «Elecciones legislativas de Argentina de 2001» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento (departamentos de 1991 y 2001): [[:commons:File:Elecciones legislativas de Argentina de 2001 - Resultados por departamento (solo mapa).svg|ganador por departamento]], más las versiones con el voto de cada bloque y la participación.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
