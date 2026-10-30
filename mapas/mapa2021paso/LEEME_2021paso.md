# PASO 2021: diputados nacionales

Elecciones primarias del 12 de septiembre de 2021. Generado con `python comun/atlas_leg2003_2025.py 2021paso` (29-oct-2026).

- Datos: `datos_oficiales/2021_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico.
- Resultado nacional (torta, barras, métricas): suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO).
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2021 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2021.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Juntos por el Cambio | 8.899.255 | 8.899.255 | +0 | 300 |
| Frente de Todos | 6.960.708 | 6.960.708 | +0 | 189 |
| Tercera Vía y Peronismo Federal | 1.125.565 | 1.125.565 | +0 | 3 |
| Frente Renovador de la Concordia | 197.494 | 197.494 | +0 | 9 |
| Movimiento Popular Neuquino | 130.351 | 130.351 | +0 | 14 |
| Juntos Somos Río Negro | 122.612 | 122.612 | +0 | 12 |
| Somos Energía para Renovar Santa Cruz | 35.511 | 35.511 | +0 | 1 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

- Emparejamiento con la general (votos): nombre 94.3 %; sin bloque 4.8 %; bloque 0.8 %; número 0.2 %.
- Catamarca: Antofagasta de la Sierra: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 5 mesas), porque no hay mesas en el provisorio. Inscriptos: 1.057 votantes = 67,58 % de los inscriptos.
- Chubut: Gastre: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 5 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
