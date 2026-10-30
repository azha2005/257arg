# PASO 2011: presidente

Elecciones primarias del 14 de agosto de 2011. Generado con `python comun/atlas_leg2003_2025.py 2011paso` (29-oct-2026).

- Datos: `datos_oficiales/2011_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado.
- Resultado nacional (torta, barras, métricas): tabla presidencial de «Elecciones primarias de Argentina de 2011» en la Wikipedia en español.
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Agrupaciones y precandidatos: tabla de la Wikipedia (`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria | 10.541.987 | 10.762.217 | -220.230 | 506 |
| Unión para el Desarrollo Social | 2.562.174 | 2.614.211 | -52.037 | 2 |
| Frente Popular | 2.565.351 | 2.595.996 | -30.645 | 8 |
| Frente Amplio Progresista | 2.149.616 | 2.180.110 | -30.494 | 2 |
| Compromiso Federal | 1.721.648 | 1.749.971 | -28.323 | 9 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

- Jujuy: Valle Grande: Votos del escrutinio definitivo de la DINE (jujuy_paso2011_archivo.pdf (escrutinio_primarias_jujuy.pdf de elecciones.gob.ar, copia de Wayback), página 9; 11 mesas), porque no hay mesas en el provisorio. Inscriptos: 2.357 según el escrutinio definitivo de la DINE.

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
