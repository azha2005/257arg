# PASO 2015: diputados nacionales

Elecciones primarias del 9 de agosto de 2015. Generado con `python comun/atlas_leg2003_2025.py 2015pasodip` (29-oct-2026).

- Datos: `datos_oficiales/2015_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado.
- Resultado nacional (torta, barras, métricas): suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO).
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2015 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2015.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria | 7.854.171 | 7.854.171 | +0 | 358 |
| Cambiemos | 6.318.865 | 6.318.865 | +0 | 123 |
| Unidos por una Nueva Alternativa | 3.506.432 | 3.506.432 | +0 | 25 |
| Compromiso Federal | 269.847 | 269.847 | +0 | 9 |
| Chubut Somos Todos | 65.775 | 65.775 | +0 | 3 |
| Movimiento Popular Neuquino | 63.270 | 63.270 | +0 | 7 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): Catamarca: Antofagasta de la Sierra; Chubut: Gastre.

- Emparejamiento con la general (votos): nombre 81.6 %; bloque 12.2 %; sin bloque 2.8 %; nombre contenido 2.0 %; a mano 1.4 %.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
