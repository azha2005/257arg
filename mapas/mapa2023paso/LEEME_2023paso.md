# PASO 2023: presidente

Elecciones primarias del 13 de agosto de 2023. Generado con `python comun/atlas_leg2003_2025.py 2023paso` (29-oct-2026).

- Datos: `datos_oficiales/2023_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico.
- Resultado nacional (torta, barras, métricas): tabla presidencial de «Elecciones primarias de Argentina de 2023» en la Wikipedia en español.
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Agrupaciones y precandidatos: tabla de la Wikipedia (`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.
- Modos de interna: Juntos por el Cambio, Unión por la Patria (color del precandidato más votado dentro de la agrupación).

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| La Libertad Avanza | 7.116.352 | 7.352.244 | -235.892 | 200 |
| Juntos por el Cambio | 6.698.029 | 6.895.941 | -197.912 | 135 |
| Unión por la Patria | 6.460.689 | 6.719.042 | -258.353 | 187 |
| Hacemos por Nuestro País | 907.437 | 914.812 | -7.375 | 6 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
