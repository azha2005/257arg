# Diputados nacionales 2019

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `datos_oficiales/2019/agregado.pkl` (DINE, escrutinio provisorio por mesa).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2019); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 24.769.142 positivos y la tabla nacional 25.639.274. No se ajustan los votos locales para forzar igualdad. `control_bloques_2019.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente de Todos y aliados | 11.506.371 | 11.950.926 | -444,555 | 355 |
| Juntos por el Cambio y aliados | 10.015.849 | 10.347.402 | -331,553 | 160 |
| Consenso Federal y aliados | 1.803.526 | 1.878.282 | -74,756 | 1 |
| Alianza Frente Renovador de la Concordia (FRC) | 185.629 | 191.876 | -6,247 | 5 |
| Juntos Somos Río Negro (JSRN) | 116.331 | 121.478 | -5,147 | 1 |
| Movimiento Popular Neuquino (MPN) | 75.795 | 78.310 | -2,515 | 5 |

Faltantes (beige, sin imputar): Catamarca: Antofagasta de la Sierra.

Color final de Frente de Todos y aliados: #2ea3ff; tabla de Wikipedia: #009FE3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Juntos por el Cambio y aliados: #f4ce00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Consenso Federal y aliados: #2f3b81; tabla de Wikipedia: #283084. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Alianza Frente Renovador de la Concordia (FRC): #5c6bc0; tabla de Wikipedia: #294593. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.

Logos: ver `logos_usados.json` y `logos_wikipedia/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
