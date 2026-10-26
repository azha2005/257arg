# Diputados nacionales 2017

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `datos_oficiales/2017/agregado.pkl` (DINE, escrutinio provisorio por mesa).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2017); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 24.329.184 positivos y la tabla nacional 24.580.114. No se ajustan los votos locales para forzar igualdad. `control_bloques_2017.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Cambiemos | 10.161.053 | 10.263.329 | -102,276 | 267 |
| Unidad Ciudadana y el kirchnerismo | 5.504.474 | 5.577.812 | -73,338 | 97 |
| peronismo no kirchnerista | 4.066.934 | 3.935.362 | +131,572 | 148 |
| Frente Progresista Cívico y Social | 345.918 | 347.853 | -1,935 | 1 |
| Chubut para Todos (CpT) | 100.326 | 101.613 | -1,287 | 9 |
| Movimiento Popular Neuquino (MPN) | 80.732 | 81.077 | -345 | 4 |

Faltantes (beige, sin imputar): Jujuy: Valle Grande.
Tolhuin todavía no era un departamento en la fecha de esta elección: la ley provincial 1186 se sancionó el 27-oct-2017, después de los comicios del 22-oct-2017. Se conserva la división de Río Grande/Ushuaia del shapefile 2010. Fuente: https://www.legistdf.gob.ar/lp/leyes/Provinciales/LEYP1186.pdf

Color final de Cambiemos: #f4ce00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Unidad Ciudadana y el kirchnerismo: #2ea3ff; tabla de Wikipedia: #75AADB. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de peronismo no kirchnerista: #1aff98; tabla de Wikipedia: #318CE7. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente Progresista Cívico y Social: #ff6600; tabla de Wikipedia: #FF8C00. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Fuerza Republicana (FR): #7b3f00; tabla de Wikipedia: #00708B. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Chubut para Todos (CpT): #9ccc65; tabla de Wikipedia: #2ab665. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento Popular Neuquino (MPN): #00708b; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.

Logos: ver `logos_usados.json` y `logos_wikipedia/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
