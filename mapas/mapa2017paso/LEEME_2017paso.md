# PASO 2017: diputados nacionales

Elecciones primarias del 13 de agosto de 2017. Generado con `python comun/atlas_leg2003_2025.py 2017paso` (29-oct-2026).

- Datos: `datos_oficiales/2017_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado.
- Resultado nacional (torta, barras, métricas): métricas de la tabla nacional de diputados de «Elecciones primarias de Argentina de 2017» en la Wikipedia; votos por bloque, suma del provisorio de la DINE.
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2017 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2017.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Cambiemos | 8.455.114 | 8.455.114 | +0 | 228 |
| Unidad Ciudadana | 4.828.610 | 4.828.610 | +0 | 100 |
| Peronismo no kirchnerista | 4.241.341 | 4.241.341 | +0 | 184 |
| 1País | 1.773.998 | 1.773.998 | +0 | 1 |
| Frente Progresista Cívico y Social | 270.025 | 270.025 | +0 | 1 |
| Movimiento Popular Neuquino | 81.409 | 81.409 | +0 | 6 |
| Chubut para Todos | 78.463 | 78.463 | +0 | 6 |
| Juntos Somos Río Negro | 66.279 | 66.279 | +0 | 1 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

- Emparejamiento con la general (votos): nombre 96.1 %; sin bloque 3.9 %; bloque 0.0 %.
- Juntos Somos Río Negro (Río Negro, agrupación 0569): no tiene bloque en la general de 2017 y gana alguna unidad; lleva bloque propio con el color y el logo del atlas de diputados 2021 (#49A942).

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
