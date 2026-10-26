# Diputados nacionales 2015

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `datos_oficiales/2015/agregado.pkl` (DINE, escrutinio provisorio por mesa).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2015); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 22.679.308 positivos y la tabla nacional 23.314.026. No se ajustan los votos locales para forzar igualdad. `control_bloques_2015.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria (FpV) | 8.421.454 | 8.765.438 | -343,984 | 320 |
| Cambiemos | 7.988.480 | 8.102.381 | -113,901 | 178 |
| Unidos por una Nueva Alternativa (UNA) | 3.988.312 | 4.115.414 | -127,102 | 10 |
| Compromiso Federal (CF) | 269.901 | 275.047 | -5,146 | 9 |
| Chubut Somos Todos (ChuSoTo) | 79.663 | 85.730 | -6,067 | 6 |
| Movimiento Popular Neuquino (MPN) | 54.633 | 56.315 | -1,682 | 4 |

Faltantes (beige, sin imputar): ninguno en el continente.
Tolhuin todavía no era un departamento en la fecha de esta elección: la ley provincial 1186 se sancionó el 27-oct-2017, después de los comicios del 22-oct-2017. Se conserva la división de Río Grande/Ushuaia del shapefile 2010. Fuente: https://www.legistdf.gob.ar/lp/leyes/Provinciales/LEYP1186.pdf

Color final de Frente para la Victoria (FpV): #50ade6; tabla de Wikipedia: #75AADB. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Cambiemos: #f4ce00; tabla de Wikipedia: #FFD700. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Unidos por una Nueva Alternativa (UNA): #231f20; tabla de Wikipedia: #4C2882. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Compromiso Federal (CF): #1aff98; tabla de Wikipedia: #66FFCC. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Chubut Somos Todos (ChuSoTo): #9ccc65; tabla de Wikipedia: #2ab665. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento Popular Neuquino (MPN): #00708b; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.

Logos: ver `logos_usados.json` y `logos/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
