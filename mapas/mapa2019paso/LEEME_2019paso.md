# PASO 2019: presidente

Elecciones primarias del 11 de agosto de 2019. Generado con `python comun/atlas_leg2003_2025.py 2019paso` (29-oct-2026).

- Datos: `datos_oficiales/2019_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico.
- Resultado nacional (torta, barras, métricas): tabla presidencial de «Elecciones primarias de Argentina de 2019» en la Wikipedia en español.
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Agrupaciones y precandidatos: tabla de la Wikipedia (`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente de Todos | 11.622.428 | 12.205.938 | -583.510 | 431 |
| Juntos por el Cambio | 7.825.208 | 8.121.689 | -296.481 | 93 |
| Consenso Federal | 2.007.035 | 2.081.315 | -74.280 | 1 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): Catamarca: Antofagasta de la Sierra; Catamarca: Santa María; Chaco: Presidencia de la Plaza.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
