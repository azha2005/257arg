# PASO 2023: diputados nacionales

Elecciones primarias del 13 de agosto de 2023. Generado con `python comun/atlas_leg2003_2025.py 2023pasodip` (29-oct-2026).

- Datos: `datos_oficiales/2023_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico.
- Resultado nacional (torta, barras, métricas): suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO).
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2023 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2023.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Juntos por el Cambio | 6.440.111 | 6.440.111 | +0 | 143 |
| Unión por la Patria | 6.147.395 | 6.147.395 | +0 | 222 |
| La Libertad Avanza | 5.883.911 | 5.883.911 | +0 | 155 |
| Hacemos por Nuestro País | 640.389 | 640.389 | +0 | 6 |
| Juntos Somos Río Negro | 35.662 | 35.662 | +0 | 1 |
| Movimiento Popular Neuquino | 34.993 | 34.993 | +0 | 1 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

- Emparejamiento con la general (votos): nombre 94.7 %; sin bloque 4.0 %; nombre contenido 1.0 %; bloque 0.3 %.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
