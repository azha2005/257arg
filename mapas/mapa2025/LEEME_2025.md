# Diputados nacionales 2025

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `datos_oficiales/2025/agregado.pkl` (DINE, escrutinio provisorio por mesa).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2025); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 22.977.871 positivos y la tabla nacional 23.212.615. No se ajustan los votos locales para forzar igualdad. `control_bloques_2025.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| La Libertad Avanza | 9.341.798 | 9.437.860 | -96,062 | 256 |
| Fuerza Patria | 7.720.973 | 7.824.427 | -103,454 | 199 |
| Provincias Unidas | 1.763.751 | 1.792.675 | -28,924 | 24 |
| Innovación Federal | 488.307 | 497.655 | -9,348 | 29 |
| Por San Juan | 132.286 | 133.432 | -1,146 | 6 |
| La Neuquinidad | 120.772 | 121.504 | -732 | 12 |
| Frente Primero Jujuy Avanza | 61.539 | 61.777 | -238 | 1 |
| Frente Popular Agrario y Social | 50.428 | 50.583 | -155 | 1 |

Faltantes (beige, sin imputar): ninguno en el continente.

Pedido expreso del usuario: Provincias Unidas en naranja #FF682C (ficha de Wikipedia), en lugar del pastel #FFCC99 de la tabla.
Color final de La Libertad Avanza: #6c4c98; tabla de Wikipedia: #6C4C99. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Fuerza Patria: #009ce4; tabla de Wikipedia: #009FE3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Provincias Unidas: #FF682C; tabla de Wikipedia: #FFCC99. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente Primero Jujuy Avanza: #c2185b; tabla de Wikipedia: #283B73. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Partido Fe: #8d5524; tabla de Wikipedia: #0070BA. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente Popular Agrario y Social: #8d5524; tabla de Wikipedia: #129254. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Propuesta Republicana: #f4ce00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Fuerza Republicana: #7b3f00; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Compromiso Federal: #1aff98; tabla de Wikipedia: #66FFCC. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.

Logos: ver `logos_usados.json` y `logos/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
