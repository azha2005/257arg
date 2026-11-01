# PASO 2019: diputados nacionales

Elecciones primarias del 11 de agosto de 2019. Generado con `python comun/atlas_leg2003_2025.py 2019pasodip` (29-oct-2026).

- Datos: `datos_oficiales/2019_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico.
- Resultado nacional (torta, barras, métricas): suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO).
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2019 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2019.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente de Todos | 10.812.939 | 10.812.939 | +0 | 406 |
| Juntos por el Cambio | 7.699.089 | 7.699.089 | +0 | 112 |
| Consenso Federal | 2.014.134 | 2.014.134 | +0 | 5 |
| Alianza Frente Renovador de la Concordia | 149.062 | 149.062 | +0 | 3 |
| Movimiento Popular Neuquino | 73.088 | 73.088 | +0 | 2 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

- Emparejamiento con la general (votos): nombre 97.7 %; sin bloque 2.0 %; nombre contenido 0.4 %.
- Catamarca: Antofagasta de la Sierra: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 5 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.
- Chaco: Pcia. de la Plaza: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 32 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.
- Catamarca: Santa Maria: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 65 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.
- Chaco: General Belgrano: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 31 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
