# Diputados nacionales 2003

Atlas según el estilo del proyecto; compilación 20-oct-2026.

Geometría: Departamentos de 2001 y 28 circunscripciones de Capital Federal (ajustadas al contorno). Se conserva el límite de hecho La Paz/Choya del shapefile histórico, según decisión del usuario. Antártida tiene resultado propio cuando la fuente lo desagrega.

Fuentes: `raw/datar_2003_departamento_SIN_VALIDAR.csv` (dat.ar, resultados llamados definitivos por la fuente; cotejo de sumas por unidad).

El cartel nacional usa la tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2003); snapshots y revisión de origen en `fuentes_leg2003_2025/`. Los votos de la base suman 15.728.197 positivos y la tabla nacional 15.729.072. No se ajustan los votos locales para forzar igualdad. `control_bloques_2003.csv` conserva todas las diferencias.

Sólo las fuerzas que ganan alguna unidad aparecen en la leyenda y en las barras nacionales; el resto integra otros en la torta y permanece en el detalle. `mapeo_listas` conserva cada lista y bloque. Colores de las filas de Wikipedia resueltos mediante expandtemplates; las excepciones por contraste se detallan abajo.

Provincias en color sólido: La Pampa. Total provincial, sin inventar resultados departamentales.

| Bloque | Base | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Partido Justicialista y aliados | 6.216.929 | 6.250.817 | -33,888 | 365 |
| Unión Cívica Radical y aliados | 2.008.283 | 2.117.075 | -108,792 | 48 |
| Afirmación para una República Igualitaria y aliados | 1.498.810 | 1.536.838 | -38,028 | 13 |
| Movimiento Federal para Recrear el Crecimiento | 609.752 | 632.303 | -22,551 | 1 |
| Frente Compromiso para el Cambio | 610.961 | 611.013 | -52 | 17 |
| Movimiento por la Dignidad y la Independencia y aliados | 608.021 | 606.886 | +1,135 | 1 |
| Acción Federalista por Buenos Aires | 433.362 | 433.369 | -7 | 1 |
| Frente Nuevo - Frente Grande | 410.338 | 410.340 | -2 | 1 |
| Fuerza Republicana (FR) | 125.954 | 125.954 | +0 | 8 |
| Frente de Todos (Corrientes) | 121.992 | 121.992 | +0 | 16 |
| Partido Nuevo de Corrientes - Partido Federal | 99.868 | 102.764 | -2,896 | 8 |
| Partido Renovador de Salta (PRS) | 95.855 | 95.845 | +10 | 1 |
| Movimiento Popular Neuquino (MPN) | 90.738 | 90.740 | -2 | 16 |
| Unidos por Salta | 68.229 | 68.216 | +13 | 2 |
| Frente Cívico y Social de Catamarca | 63.415 | 63.415 | +0 | 16 |
| Partido Demócrata Cristiano (PDC) | 70.908 | 51.449 | +19,459 | 1 |

Faltantes (beige, sin imputar): Buenos Aires: Magdalena; Buenos Aires: Punta Indio.

La Plata: 21 valores con separador de miles leído como decimal se multiplican por 1000; no se altera el CSV original.
Color final de Partido Justicialista y aliados: #1c5ece; tabla de Wikipedia: #318CE7. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Afirmación para una República Igualitaria y aliados: #74b744; tabla de Wikipedia: #6fb53e. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento Federal para Recrear el Crecimiento: #f4ce00; tabla de Wikipedia: #35649C. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente Compromiso para el Cambio: #3e5298; tabla de Wikipedia: #176BAB. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento por la Dignidad y la Independencia y aliados: #e67e22; tabla de Wikipedia: #FFEF00. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Acción Federalista por Buenos Aires: #f59e0b; tabla de Wikipedia: #808080. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Fuerza Republicana (FR): #7b3f00; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Partido Nuevo de Corrientes - Partido Federal: #40e0d0; tabla de Wikipedia: #FF8800. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Partido Renovador de Salta (PRS): #8e44ad; tabla de Wikipedia: #1E90FF. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Movimiento Popular Neuquino (MPN): #00708b; tabla de Wikipedia: #0070B8. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Unidos por Salta: #ff69b4; tabla de Wikipedia: #E10019. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Frente Cívico y Social de Catamarca: #0097a7; tabla de Wikipedia: #FF0000. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
Color final de Partido Acción Chubutense (PACH): #c2185b; tabla de Wikipedia: #0A1172. Ajuste por contraste o continuidad con los atlas verificados de 2009/2013.
La Pampa 2003: color provincial sólido con el definitivo DINE, página 2. La propia fuente declara que no recibió resultados por departamento; no se atribuye un resultado a cada departamento.

Logos: ver `logos_usados.json` y `logos_wikipedia/LICENCIAS.md`. Las reservas de fecha o licencia se señalan expresamente; la versión con siglas permite prescindir de emblemas dudosos.

Estado: generado localmente, sin subir a Commons. Las carencias de datos deben resolverse antes de publicar el atlas completo.
