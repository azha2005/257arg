# PASO 2019: presidente

Elecciones primarias del 11 de agosto de 2019. Generado con `python comun/atlas_leg2003_2025.py 2019paso` (29-oct-2026).

- Datos: `datos_oficiales/2019_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico.
- Resultado nacional (torta, barras, métricas): tabla presidencial de «Elecciones primarias de Argentina de 2019» en la Wikipedia en español.
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Agrupaciones y precandidatos: tabla de la Wikipedia (`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente de Todos | 11.641.608 | 12.205.938 | -564.330 | 434 |
| Juntos por el Cambio | 7.831.430 | 8.121.689 | -290.259 | 93 |
| Consenso Federal | 2.008.456 | 2.081.315 | -72.859 | 1 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

- Catamarca: Antofagasta de la Sierra: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 5 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.
- Chaco: Pcia. de la Plaza: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 32 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.
- Catamarca: Santa Maria: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 65 mesas), porque no hay mesas en el provisorio. La planilla no trae inscriptos: sin participación.
- Chaco: General Belgrano: Votos de la consulta de escrutinio por zona de la CNE (padron.gob.ar/publica, 31 mesas), que reemplaza el único voto del provisorio (una mesa suelta). La planilla no trae inscriptos: sin participación.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
