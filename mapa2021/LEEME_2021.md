# Diputados nacionales 2021

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `datos_oficiales/2021/agregado.pkl` (DINE, escrutinio provisorio por mesa).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2021); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 23.238.621 positivos y la tabla nacional 23.265.427. No se ajustan los votos locales para forzar igualdad. `control_bloques_2021.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Juntos por el Cambio | 9.806.007 | 9.945.804 | -139,797 | 293 |
| Frente de Todos | 7.879.511 | 8.041.290 | -161,779 | 196 |
| Tercera vía y el Peronismo Federal | 1.300.092 | 1.325.494 | -25,402 | 5 |
| Frente Renovador de la Concordia | 229.225 | 230.817 | -1,592 | 7 |
| Juntos Somos Río Negro | 138.545 | 140.634 | -2,089 | 12 |
| Movimiento Popular Neuquino | 111.177 | 112.027 | -850 | 12 |
| Somos Energía para Renovar Santa Cruz | 46.500 | 46.633 | -133 | 1 |
| Chubut Somos Todos | 28.793 | 29.622 | -829 | 1 |

Faltantes (beige, sin imputar): Chaco: Tapenagá.

Color final de Juntos por el Cambio: #f4ce00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente de Todos: #2ea3ff; tabla de Wikipedia: #009FE3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Tercera vía y el Peronismo Federal: #2f3b81; tabla de Wikipedia: #15b587. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente Renovador de la Concordia: #5c6bc0; tabla de Wikipedia: #294593. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento Popular Neuquino: #00708b; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Somos Energía para Renovar Santa Cruz: #d81b60; tabla de Wikipedia: #0268B3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Chubut Somos Todos: #9ccc65; tabla de Wikipedia: #2AB665. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Tabla nacional de la Wikipedia con votantes (34.413.824) y electores (24.433.604) intercambiados; se usan al revés.

Logos: ver `logos_usados.json` y `logos_wikipedia/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
