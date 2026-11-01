# PASO 2013: diputados nacionales

Elecciones primarias del 11 de agosto de 2013. Generado con `python comun/atlas_leg2003_2025.py 2013paso` (29-oct-2026).

- Datos: `datos_oficiales/2013_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado.
- Resultado nacional (torta, barras, métricas): suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO).
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2013 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2013.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria | 6.472.095 | 6.472.095 | +0 | 223 |
| Frente Progresista Cívico y Social | 5.332.900 | 5.332.900 | +0 | 110 |
| Frente Renovador | 3.227.918 | 3.227.918 | +0 | 74 |
| Propuesta Republicana | 1.802.536 | 1.802.536 | +0 | 5 |
| Unidos por la Libertad y el Trabajo | 927.225 | 927.225 | +0 | 3 |
| Unión por Córdoba | 581.290 | 581.290 | +0 | 20 |
| Compromiso Federal | 325.739 | 325.739 | +0 | 17 |
| Frente Renovador de la Concordia | 207.441 | 207.441 | +0 | 16 |
| Movimiento Popular Neuquino | 185.320 | 185.320 | +0 | 16 |
| Partido Fe | 145.286 | 145.286 | +0 | 1 |
| Partido Justicialista | 137.718 | 137.718 | +0 | 24 |
| Partido Acción Chubutense | 132.423 | 132.423 | +0 | 12 |
| Salta Somos Todos | 99.252 | 99.252 | +0 | 2 |
| Partido Renovador de Salta | 42.976 | 42.976 | +0 | 1 |
| Unión por la República – Frente por la Justicia | 38.936 | 38.936 | +0 | 1 |
| Mov. Indep. de Justicia y Dignidad | 22.384 | 22.384 | +0 | 1 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): Jujuy: Valle Grande.

- Emparejamiento con la general (votos): número 89.3 %; sin bloque 10.6 %; bloque 0.0 %.
- Unidos por la Libertad y el Trabajo (Buenos Aires, agrupación 0507): no tiene bloque en la general de 2013 y gana alguna unidad; lleva bloque propio (#EE2225, color de su fila en la tabla de las legislativas de 2013 de la Wikipedia).
- Unión por la República – Frente por la Justicia (Salta, agrupación 0536): no tiene bloque en la general de 2013 y gana alguna unidad; lleva bloque propio (#4a148c, violeta oscuro: sin color en la Wikipedia ni en la DINE, y el magenta se confundía con el PACh y Salta Somos Todos).

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
