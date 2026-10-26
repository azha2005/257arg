# Diputados nacionales 2023

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `datos_oficiales/2023/agregado.pkl` (DINE, escrutinio provisorio por mesa).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2023); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 24.059.851 positivos y la tabla nacional 24.546.861. No se ajustan los votos locales para forzar igualdad. `control_bloques_2023.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Unión por la Patria | 9.094.285 | 9.298.491 | -204,206 | 335 |
| Libertad Avanza | 6.712.560 | 6.843.049 | -130,489 | 104 |
| Juntos por el Cambio | 6.291.879 | 6.412.133 | -120,254 | 75 |
| Hacemos por Nuestro País | 939.918 | 946.840 | -6,922 | 8 |
| Juntos Somos Río Negro | 59.044 | 60.259 | -1,215 | 1 |
| Por Santa Cruz | 53.181 | 55.430 | -2,249 | 5 |

Faltantes (beige, sin imputar): ninguno en el continente.

Color final de Unión por la Patria: #009ce4; tabla de Wikipedia: #009FE3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Libertad Avanza: #6c4c98; tabla de Wikipedia: #6C4C99. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Juntos por el Cambio: #fcbc00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Hacemos por Nuestro País: #283084; tabla de Wikipedia: #0B5397. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Por Santa Cruz: #ea5530; tabla de Wikipedia: #0268B3. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento Popular Neuquino: #00708b; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.

Logos: ver `logos_usados.json` y `logos/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
