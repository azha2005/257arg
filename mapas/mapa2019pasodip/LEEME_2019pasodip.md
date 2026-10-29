# PASO 2019: diputados nacionales

Elecciones primarias del 11 de agosto de 2019. Generado con `python comun/atlas_leg2003_2025.py 2019pasodip` (29-oct-2026).

- Datos: `datos_oficiales/2019_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico.
- Resultado nacional (torta, barras, métricas): suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO).
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2019 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2019.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente de Todos | 10.793.359 | 10.793.359 | +0 | 403 |
| Juntos por el Cambio | 7.693.637 | 7.693.637 | +0 | 111 |
| Consenso Federal | 2.013.210 | 2.013.210 | +0 | 5 |
| Alianza Frente Renovador de la Concordia | 149.062 | 149.062 | +0 | 3 |
| Movimiento Popular Neuquino | 73.088 | 73.088 | +0 | 2 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): Catamarca: Antofagasta de la Sierra; Catamarca: Santa María; Chaco: General Belgrano; Chaco: Presidencia de la Plaza.

- Emparejamiento con la general (votos): nombre 97.7 %; sin bloque 2.0 %; nombre contenido 0.4 %.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
