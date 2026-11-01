# PASO 2015: presidente

Elecciones primarias del 9 de agosto de 2015. Generado con `python comun/atlas_leg2003_2025.py 2015paso` (29-oct-2026).

- Datos: `datos_oficiales/2015_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado.
- Resultado nacional (torta, barras, métricas): tabla presidencial de «Elecciones primarias de Argentina de 2015» en la Wikipedia en español.
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Agrupaciones y precandidatos: tabla de la Wikipedia (`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.
- Modos de interna: Cambiemos, Unidos por una Nueva Alternativa (color del precandidato más votado dentro de la agrupación).

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria | 8.424.749 | 8.720.573 | -295.824 | 373 |
| Cambiemos | 6.595.914 | 6.791.278 | -195.364 | 115 |
| Unidos por una Nueva Alternativa | 4.525.497 | 4.639.405 | -113.908 | 28 |
| Compromiso Federal | 462.304 | 472.341 | -10.037 | 9 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): Catamarca: Antofagasta de la Sierra; Chubut: Gastre.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
