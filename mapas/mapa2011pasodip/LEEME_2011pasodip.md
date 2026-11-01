# PASO 2011: diputados nacionales

Elecciones primarias del 14 de agosto de 2011. Generado con `python comun/atlas_leg2003_2025.py 2011pasodip` (29-oct-2026).

- Datos: `datos_oficiales/2011_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado.
- Resultado nacional (torta, barras, métricas): suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO).
- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.
- Bloques: el de la misma agrupación en la general de 2011 (`comun/paso_bloques.py`), con color y logo del atlas de diputados 2011.

| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Frente para la Victoria | 9.702.849 | 9.702.849 | +0 | 489 |
| Unión para el Desarrollo Social | 2.706.411 | 2.706.411 | +0 | 14 |
| Frente Popular-Propuesta Republicana | 2.053.030 | 2.053.030 | +0 | 9 |
| Frente Amplio Progresista | 1.791.438 | 1.791.438 | +0 | 2 |
| Compromiso Federal | 1.256.088 | 1.256.088 | +0 | 9 |
| Alianza Justicialista | 118.251 | 118.251 | +0 | 3 |
| Movimiento Popular Neuquino | 55.167 | 55.167 | +0 | 1 |

Referencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).

Sin mesas (beige, sin imputar): ninguna.

- Emparejamiento con la general (votos): nombre 86.0 %; nombre contenido 6.0 %; sin bloque 3.6 %; bloque 2.7 %; a mano 1.5 %; número 0.2 %.
- Jujuy: Valle Grande: Votos del escrutinio definitivo de la DINE (jujuy_paso2011_archivo.pdf (escrutinio_primarias_jujuy.pdf de elecciones.gob.ar, copia de Wayback), página 9; 11 mesas), porque no hay mesas en el provisorio. Inscriptos: 2.357 según el escrutinio definitivo de la DINE.
- Alianza Justicialista (Córdoba, agrupación 0506): no tiene bloque en la general de 2011 y gana alguna unidad; lleva bloque propio (#1f3a93, azul oscuro: el celeste de la DINE se confundía con el FPV).

Estado: generado localmente, sin PNG transparentes ni paquete de Commons.
