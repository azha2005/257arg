# PASO 2011: presidente

Elecciones primarias del 14 de agosto de 2011. Generado con `python comun/atlas_leg2003_2025.py 2011paso` (29-oct-2026).

- Datos: `datos_oficiales/2011_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado.
- Resultado nacional (torta, barras, métricas): tabla presidencial de «Elecciones primarias de Argentina de 2011» en la Wikipedia en español.
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Agrupaciones y precandidatos: tabla de la Wikipedia (`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria | 10.540.703 | 10.762.217 | -221.514 | 505 |
| Unión para el Desarrollo Social | 2.561.935 | 2.614.211 | -52.276 | 2 |
| Frente Popular | 2.565.297 | 2.595.996 | -30.699 | 8 |
| Frente Amplio Progresista | 2.149.595 | 2.180.110 | -30.515 | 2 |
| Compromiso Federal | 1.721.629 | 1.749.971 | -28.342 | 9 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): Jujuy: Valle Grande.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
