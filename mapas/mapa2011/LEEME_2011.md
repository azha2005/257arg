# Diputados nacionales 2011

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `datos_oficiales/2011/agregado.pkl` (DINE, escrutinio provisorio por mesa).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2011); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 20.158.660 positivos y la tabla nacional 20.574.048. No se ajustan los votos locales para forzar igualdad. `control_bloques_2011.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria (FPV) y aliados | 10.530.147 | 10.793.689 | -263,542 | 495 |
| Frente Amplio Progresista (FAP) y aliados | 2.733.265 | 2.780.984 | -47,719 | 4 |
| Unión para el Desarrollo Social (UDESO) | 2.714.570 | 2.774.548 | -59,978 | 2 |
| Frente Popular-Propuesta Republicana (alianza informal) | 1.424.043 | 1.424.685 | -642 | 6 |
| Compromiso Federal (CF) | 1.196.971 | 1.218.949 | -21,978 | 9 |
| Movimiento Popular Neuquino (MPN) | 86.662 | 88.197 | -1,535 | 10 |

Faltantes (beige, sin imputar): Jujuy: Valle Grande.

Color final de Frente para la Victoria (FPV) y aliados: #50ade6; tabla de Wikipedia: #75AADB. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Unión para el Desarrollo Social (UDESO): #d31515; tabla de Wikipedia: #E10019. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente Popular-Propuesta Republicana (alianza informal): #b73c96; tabla de Wikipedia: #c71585. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Compromiso Federal (CF): #1aff98; tabla de Wikipedia: #66FFCC. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento Popular Neuquino (MPN): #00708b; tabla de Wikipedia: #005C9E. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Tabla nacional de la Wikipedia con votantes (28.509.343) y electores (22.651.068) intercambiados; se usan al revés.

Logos: ver `logos_usados.json` y `logos/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
