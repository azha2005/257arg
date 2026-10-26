# Auditoría de las transferencias

Generado por `auditar.py`. «Peso»: % del padrón de la categoría de origen. «Dif. Calvo»: máxima diferencia, en puntos, entre la variante principal y la de Calvo (una sola matriz nacional), con la celda donde ocurre. «IC»: máximo ancho del intervalo bootstrap 5–95. Una fila **no identificada** (más de 30 puntos de diferencia entre variantes en alguna celda, o más de 20 si pesa menos de 5 % del padrón) no se puede leer: los datos no alcanzan para saber adónde fueron esos votantes.

«Separación»: cuánto se aparta en promedio cada fila grande (partidos con 5 % o más del padrón) del resultado total del destino, en puntos (media ponderada de ½·Σ|fila − promedio|). Si es menor a 25, la matriz es **poco informativa**: el voto de origen casi no predice el de destino y todas las filas se parecen al promedio por falta de señal, no porque los votantes se hayan repartido igual. Las dos variantes coinciden en ese caso, así que el criterio de Calvo no lo detecta. «Sep.» por fila es la misma medida para esa fila (principal / Calvo); una fila de 5 % o más del padrón con separación menor a 25 se marca **cerca del promedio** (en el sankey, †): puede ser un electorado que de verdad se repartió como el total, o falta de señal para esa fila; si la variante de Calvo también queda cerca, lo segundo es más probable.

## 2009 → 2011

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.7597, '2e-05': 2.5571, '2e-06': 2.4776, '2e-07': 2.4542, '0': 2.4648}

Separación de las filas: 42.9 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 20.3 | 8.3 | Frente para la Victoria | 94.1 | 85.8 | 2.6 | 56.9 / 48.6 |  |
| Acuerdo Cívico y Social | 21.1 | 7.7 | UDESO (UCR) | 31.4 | 39.1 | 6.4 | 36.5 / 35.9 |  |
| PRO / Unión-PRO | 13.2 | 13.4 | FAP | 3.4 | 16.9 | 8.2 | 39.8 / 29.6 |  |
| Peronismo Federal | 5.7 | 30.0 | Compromiso Federal | 14.0 | 44.0 | 20.9 | 23.6 / 42.1 | **cerca del promedio** |
| Proyecto Sur | 1.5 | 66.4 | Frente Popular / PRO | 0.6 | 67.0 | 5.2 | 69.9 / 79.2 | **no identificada** |
| Otros | 7.3 | 24.3 | Otros | 8.6 | 33.0 | 9.3 | 28.4 / 35.2 |  |
| Blanco y nulo | 3.6 | 27.3 | Frente para la Victoria | 42.3 | 15.0 | 16.2 | 45.7 / 72.0 | **no identificada** |
| No votó | 27.3 | 7.6 | No votó | 60.1 | 67.7 | 5.5 | 38.8 / 46.3 |  |

## 2011 → 2023

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.7513, '2e-05': 2.4507, '2e-06': 2.3009, '2e-07': 2.2747, '0': 2.3129}

Separación de las filas: 34.1 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 37.0 | 9.4 | Unión por la Patria | 53.7 | 63.1 | 4.8 | 28.5 / 39.0 |  |
| UDESO (UCR) | 9.5 | 6.4 | La Libertad Avanza | 22.5 | 28.9 | 6.1 | 40.4 / 47.7 |  |
| FAP | 9.9 | 16.9 | Hacemos | 4.2 | 21.1 | 13.9 | 48.9 / 55.7 |  |
| Frente Popular / PRO | 4.9 | 12.8 | Juntos por el Cambio | 60.7 | 47.9 | 10.6 | 46.5 / 45.3 |  |
| Compromiso Federal | 4.4 | 21.3 | Hacemos | 5.4 | 26.7 | 16.4 | 45.6 / 70.5 | **no identificada** |
| CC-ARI | 2.2 | 25.3 | Juntos por el Cambio | 73.7 | 99.0 | 21.8 | 56.3 / 80.2 | **no identificada** |
| FIT | 2.0 | 78.9 | La Libertad Avanza | 7.6 | 86.5 | 5.4 | 59.7 / 76.2 | **no identificada** |
| Otros | 1.4 | 10.6 | Juntos por el Cambio | 5.6 | 16.1 | 15.0 | 41.6 / 39.3 |  |
| Blanco y nulo | 7.0 | 35.7 | Juntos por el Cambio | 6.0 | 41.7 | 9.4 | 53.8 / 58.3 | **no identificada** |
| No votó | 21.8 | 4.2 | La Libertad Avanza | 9.2 | 4.9 | 6.1 | 47.1 / 47.9 |  |

## 2013 → 2025

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.6329, '2e-05': 2.4164, '2e-06': 2.3134, '2e-07': 2.3039, '0': 2.3073}

Separación de las filas: 29.6 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 24.0 | 15.3 | Fuerza Patria | 55.9 | 71.2 | 4.4 | 36.2 / 51.2 |  |
| FPCyS / UNEN | 18.7 | 8.7 | Otros | 8.9 | 0.2 | 6.1 | 25.9 / 33.8 |  |
| Frente Renovador | 12.9 | 18.0 | La Libertad Avanza | 34.7 | 52.7 | 6.7 | 12.3 / 28.2 | **cerca del promedio** |
| PRO | 6.7 | 12.0 | La Libertad Avanza | 74.9 | 62.9 | 12.7 | 49.5 / 52.6 |  |
| FIT | 4.0 | 22.9 | Otros | 22.4 | 45.2 | 11.6 | 38.7 / 62.4 | **no identificada** |
| Unión por Córdoba | 1.8 | 11.7 | Provincias Unidas | 47.2 | 58.9 | 6.4 | 52.1 / 68.8 |  |
| Otros | 7.9 | 14.6 | Otros | 22.4 | 37.0 | 8.3 | 17.4 / 28.3 |  |
| Blanco y nulo | 4.5 | 10.6 | Otros | 9.1 | 19.7 | 12.7 | 21.2 / 34.6 |  |
| No votó | 19.6 | 16.1 | No votó | 70.2 | 86.3 | 8.1 | 38.5 / 54.6 |  |

## 2019 → 2023

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.4278, '2e-05': 2.1746, '2e-06': 2.0955, '2e-07': 2.0827, '0': 2.0791}

Separación de las filas: 43.0 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente de Todos | 35.2 | 7.1 | La Libertad Avanza | 14.8 | 7.8 | 2.7 | 40.6 / 48.6 |  |
| Juntos por el Cambio | 30.4 | 8.5 | La Libertad Avanza | 24.7 | 33.2 | 2.5 | 42.7 / 52.2 |  |
| Consenso Federal | 5.5 | 55.0 | Hacemos | 21.4 | 76.4 | 16.7 | 60.1 / 77.7 | **no identificada** |
| FIT-U | 2.2 | 53.7 | Unión por la Patria | 53.9 | 0.2 | 12.6 | 57.7 / 76.9 | **no identificada** |
| Otros | 2.1 | 19.7 | Unión por la Patria | 34.1 | 14.4 | 11.7 | 44.5 / 62.1 |  |
| Blanco y nulo | 5.1 | 17.8 | Blanco y nulo | 43.0 | 25.3 | 11.4 | 65.3 / 43.6 |  |
| No votó | 19.4 | 3.8 | No votó | 89.1 | 92.9 | 4.0 | 66.2 / 70.1 |  |

## 2019 → 2025

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.4489, '2e-05': 2.2245, '2e-06': 2.0895, '2e-07': 2.0324, '0': 2.0297}

Separación de las filas: 34.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente de Todos | 35.2 | 13.0 | Fuerza Patria | 51.4 | 64.4 | 2.1 | 30.2 / 42.9 |  |
| Juntos por el Cambio | 30.4 | 5.8 | No votó | 15.9 | 21.7 | 3.0 | 38.5 / 41.1 |  |
| Consenso Federal | 5.5 | 51.5 | Provincias Unidas | 23.5 | 75.0 | 11.3 | 42.6 / 85.7 | **no identificada** |
| FIT-U | 2.2 | 66.1 | Fuerza Patria | 66.3 | 0.2 | 13.5 | 60.4 / 60.1 | **no identificada** |
| Otros | 2.1 | 55.2 | Otros | 36.8 | 92.1 | 15.8 | 42.8 / 86.9 | **no identificada** |
| Blanco y nulo | 5.1 | 23.7 | No votó | 19.1 | 42.7 | 12.6 | 27.5 / 20.2 |  |
| No votó | 19.5 | 9.4 | No votó | 86.7 | 77.4 | 5.3 | 54.8 / 49.6 |  |

## 2021 → 2025

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.4835, '2e-05': 2.2621, '2e-06': 2.0394, '2e-07': 1.9977, '0': 1.9952}

Separación de las filas: 42.9 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente de Todos | 23.3 | 14.8 | Fuerza Patria | 68.7 | 83.5 | 3.9 | 47.4 / 62.0 |  |
| Juntos por el Cambio | 28.8 | 7.3 | No votó | 12.9 | 20.2 | 2.6 | 39.2 / 39.6 |  |
| Libertarios (AL + LLA) | 3.7 | 27.9 | Fuerza Patria | 8.7 | 36.6 | 5.4 | 50.5 / 51.3 | **no identificada** |
| FIT-U | 3.7 | 39.1 | Otros | 12.5 | 51.6 | 10.6 | 48.3 / 75.7 | **no identificada** |
| Tercera Vía / PF | 3.8 | 33.8 | Provincias Unidas | 37.2 | 71.0 | 17.4 | 36.3 / 85.4 | **no identificada** |
| Otros | 5.0 | 36.2 | Otros | 42.9 | 79.0 | 11.0 | 43.6 / 79.6 | **no identificada** |
| Blanco y nulo | 3.5 | 22.4 | La Libertad Avanza | 36.1 | 58.5 | 11.3 | 35.9 / 42.4 | **no identificada** |
| No votó | 28.2 | 5.6 | Fuerza Patria | 5.8 | 0.1 | 4.3 | 52.1 / 54.1 |  |

## 2023 → 2025

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.3267, '2e-05': 2.0443, '2e-06': 1.93, '2e-07': 1.898, '0': 1.8951}

Separación de las filas: 45.6 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Unión por la Patria | 26.0 | 10.6 | Fuerza Patria | 73.2 | 83.8 | 2.3 | 51.7 / 62.3 |  |
| La Libertad Avanza | 19.3 | 6.7 | Otros | 13.2 | 19.9 | 6.1 | 36.2 / 40.0 |  |
| Juntos por el Cambio | 18.0 | 10.4 | No votó | 8.3 | 18.8 | 8.5 | 47.0 / 46.5 |  |
| Hacemos | 2.7 | 26.1 | Provincias Unidas | 52.3 | 78.4 | 20.8 | 53.7 / 85.1 | **no identificada** |
| FIT-U | 2.2 | 17.0 | Otros | 25.1 | 42.1 | 9.5 | 70.1 / 81.4 |  |
| Otros | 0.7 | 41.8 | Otros | 57.9 | 99.7 | 13.3 | 49.9 / 90.5 | **no identificada** |
| Blanco y nulo | 7.9 | 17.1 | La Libertad Avanza | 19.1 | 36.2 | 5.9 | 25.9 / 32.6 |  |
| No votó | 23.1 | 3.6 | Otros | 1.6 | 5.2 | 3.6 | 58.7 / 56.1 |  |

## 2019p → 2023p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.3745, '2e-05': 2.2183, '2e-06': 2.1103, '2e-07': 2.0902, '0': 2.092}

Separación de las filas: 42.5 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente de Todos | 38.1 | 5.0 | Unión por la Patria | 66.9 | 71.9 | 1.6 | 40.5 / 44.6 |  |
| Juntos por el Cambio | 31.8 | 7.7 | Hacemos | 8.3 | 16.1 | 2.4 | 45.0 / 50.6 |  |
| Consenso Federal | 4.9 | 54.2 | La Libertad Avanza | 41.4 | 95.6 | 10.3 | 40.6 / 73.4 | **no identificada** |
| FIT-U | 1.7 | 58.9 | Unión por la Patria | 59.4 | 0.4 | 9.0 | 48.6 / 74.6 | **no identificada** |
| NOS + Unite | 2.5 | 8.2 | La Libertad Avanza | 90.4 | 98.6 | 12.8 | 68.4 / 76.1 |  |
| Blanco y nulo | 2.0 | 35.5 | La Libertad Avanza | 70.8 | 35.3 | 9.0 | 65.6 / 46.4 | **no identificada** |
| No votó | 19.0 | 4.7 | No votó | 89.0 | 93.8 | 4.0 | 66.9 / 71.6 |  |

## 2011p → 2023p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.71, '2e-05': 2.5518, '2e-06': 2.4022, '2e-07': 2.3863, '0': 2.3999}

Separación de las filas: 36.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 40.8 | 5.0 | Unión por la Patria | 55.7 | 60.7 | 4.3 | 29.4 / 33.8 |  |
| FAP | 13.0 | 7.8 | No votó | 11.0 | 3.2 | 11.4 | 43.2 / 54.7 |  |
| UDESO (UCR) | 8.4 | 9.5 | La Libertad Avanza | 46.1 | 36.6 | 7.6 | 52.2 / 51.4 |  |
| Compromiso Federal | 6.2 | 16.1 | Hacemos | 8.4 | 24.5 | 10.3 | 43.8 / 62.3 |  |
| Frente Popular | 4.4 | 26.0 | Juntos por el Cambio | 66.6 | 40.7 | 14.7 | 48.8 / 41.6 | **no identificada** |
| FIT | 1.8 | 68.4 | Unión por la Patria | 68.9 | 0.5 | 8.7 | 56.6 / 62.2 | **no identificada** |
| CC-ARI | 1.4 | 0.6 | Hacemos | 0.7 | 0.1 | 0.7 | 79.9 / 80.0 |  |
| Blanco y nulo | 3.2 | 27.8 | Juntos por el Cambio | 7.7 | 35.5 | 13.3 | 53.9 / 49.1 | **no identificada** |
| No votó | 20.9 | 8.3 | La Libertad Avanza | 10.4 | 2.1 | 5.7 | 46.6 / 49.1 |  |

## 2023p → 2023b

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 1.2904, '2e-05': 1.2233, '2e-06': 1.1801, '2e-07': 1.1666, '0': 1.1644}

Separación de las filas: 55.1 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Unión por la Patria | 27.7 | 0.2 | No votó | 1.2 | 1.0 | 0.7 | 65.7 / 65.9 |  |
| La Libertad Avanza | 22.6 | 0.4 | La Libertad Avanza | 99.4 | 99.8 | 0.4 | 58.2 / 58.6 |  |
| Juntos por el Cambio | 18.0 | 4.0 | No votó | 4.7 | 8.7 | 1.3 | 44.6 / 41.5 |  |
| Hacemos | 5.1 | 3.8 | Unión por la Patria | 28.2 | 32.0 | 5.2 | 20.8 / 16.9 | **cerca del promedio** |
| FIT-U | 2.0 | 25.3 | Unión por la Patria | 61.9 | 36.6 | 6.2 | 47.0 / 35.8 | **no identificada** |
| Blanco y nulo | 2.3 | 5.9 | La Libertad Avanza | 14.9 | 20.8 | 4.9 | 48.5 / 46.1 |  |
| No votó | 22.3 | 1.8 | No votó | 91.4 | 89.5 | 1.2 | 67.8 / 65.9 |  |

## 2019p → 2023b

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.2897, '2e-05': 2.2286, '2e-06': 2.1688, '2e-07': 2.1507, '0': 2.1465}

Separación de las filas: 40.9 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente de Todos | 38.1 | 8.0 | Unión por la Patria | 68.9 | 77.0 | 2.0 | 36.3 / 44.3 |  |
| Juntos por el Cambio | 31.8 | 2.9 | Unión por la Patria | 3.1 | 0.1 | 1.7 | 46.5 / 48.7 |  |
| Consenso Federal | 4.9 | 49.0 | La Libertad Avanza | 49.4 | 98.3 | 13.7 | 21.0 / 57.1 | **no identificada** |
| FIT-U | 1.7 | 39.7 | Unión por la Patria | 80.1 | 40.4 | 8.2 | 47.5 / 39.1 | **no identificada** |
| NOS + Unite | 2.5 | 8.4 | La Libertad Avanza | 90.7 | 99.1 | 13.6 | 49.4 / 57.8 |  |
| Blanco y nulo | 2.0 | 56.5 | La Libertad Avanza | 85.7 | 29.1 | 13.2 | 46.9 / 21.3 | **no identificada** |
| No votó | 18.9 | 5.1 | No votó | 86.2 | 91.4 | 4.9 | 62.6 / 67.7 |  |

## 2011p → 2023b

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 3.6275, '2e-05': 3.3969, '2e-06': 3.2742, '2e-07': 3.2492, '0': 3.2761}

Separación de las filas: 33.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 40.7 | 2.0 | No votó | 18.0 | 16.0 | 4.4 | 28.4 / 29.9 |  |
| FAP | 13.0 | 21.1 | La Libertad Avanza | 68.0 | 89.1 | 15.7 | 31.5 / 50.6 |  |
| UDESO (UCR) | 8.4 | 4.0 | Unión por la Patria | 4.1 | 0.1 | 7.3 | 50.3 / 52.6 |  |
| Compromiso Federal | 6.2 | 12.8 | La Libertad Avanza | 86.5 | 99.3 | 11.9 | 45.1 / 58.0 |  |
| Frente Popular | 4.4 | 17.3 | No votó | 16.1 | 33.4 | 15.8 | 28.6 / 32.0 |  |
| FIT | 1.8 | 61.1 | Unión por la Patria | 75.7 | 14.6 | 8.4 | 43.2 / 46.1 | **no identificada** |
| CC-ARI | 1.4 | 35.8 | No votó | 4.5 | 40.3 | 11.1 | 42.8 / 31.1 | **no identificada** |
| Blanco y nulo | 3.2 | 27.9 | No votó | 7.9 | 35.8 | 11.0 | 36.2 / 31.3 | **no identificada** |
| No votó | 20.9 | 15.2 | Unión por la Patria | 14.4 | 29.6 | 8.3 | 38.8 / 34.8 |  |

## 1954p → 1958p

Penalización elegida: 0.0002; error de validación cruzada (pp): {'0.0002': 4.2852, '2e-05': 4.3362, '2e-06': 4.3534, '2e-07': 4.3633, '0': 4.3931}

Separación de las filas: 36.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Partido Peronista | 54.3 | 15.1 | UCRI (Frondizi) | 65.5 | 50.5 | 3.1 | 28.4 / 20.6 |  |
| UCR | 27.8 | 10.9 | UCRI (Frondizi) | 18.2 | 29.0 | 4.5 | 51.6 / 41.4 |  |
| Otros | 2.8 | 8.7 | Otros | 76.1 | 84.9 | 6.3 | 63.9 / 70.9 |  |
| Blanco y nulo | 1.8 | 73.5 | UCRI (Frondizi) | 20.6 | 94.1 | 3.1 | 52.4 / 52.3 | **no identificada** |
| No votó | 13.4 | 26.0 | Otros | 33.6 | 7.6 | 5.6 | 38.9 / 31.6 |  |

## 1954d → 1965d

Penalización elegida: 2e-05; error de validación cruzada (pp): {'0.0002': 3.4174, '2e-05': 3.3012, '2e-06': 3.2889, '2e-07': 3.3017, '0': 3.3181}

Separación de las filas: 29.5 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Partido Peronista | 54.0 | 7.2 | UP y neoperonistas | 50.0 | 42.8 | 3.9 | 23.6 / 16.0 | **cerca del promedio** |
| UCR | 27.5 | 5.1 | UCRI | 2.0 | 7.1 | 10.2 | 41.2 / 37.0 |  |
| Otros | 2.9 | 63.6 | FNPC (centro) | 34.9 | 98.5 | 23.9 | 74.4 / 93.1 | **no identificada** |
| Blanco y nulo | 1.7 | 79.8 | MID | 16.0 | 95.9 | 10.4 | 65.3 / 90.8 | **no identificada** |
| No votó | 13.8 | 20.0 | No votó | 39.2 | 59.3 | 9.7 | 49.7 / 55.2 |  |

## 2003p → 2005

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 4.0929, '2e-05': 3.6944, '2e-06': 3.4769, '2e-07': 3.4562, '0': 3.4855}

Separación de las filas: 38.9 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Kirchner (FPV) | 17.0 | 15.7 | Peronismo Federal | 15.8 | 0.2 | 6.1 | 44.2 / 46.0 |  |
| Menem (Lealtad) | 18.9 | 8.2 | Frente para la Victoria | 43.8 | 52.0 | 5.4 | 22.5 / 32.2 | **cerca del promedio** |
| López Murphy (Recrear) | 12.5 | 16.6 | UCR y aliados | 17.7 | 1.1 | 5.3 | 52.0 / 55.6 |  |
| Rodríguez Saá (MNP) | 11.1 | 35.7 | Peronismo Federal | 6.4 | 42.1 | 8.1 | 29.6 / 36.9 | **no identificada** |
| Carrió (ARI) | 11.0 | 21.6 | FPCyS (Santa Fe) | 7.8 | 29.4 | 7.3 | 53.5 / 64.8 |  |
| Otros | 7.2 | 58.5 | UCR y aliados | 25.9 | 84.4 | 16.9 | 64.1 / 77.0 | **no identificada** |
| Blanco y nulo | 2.0 | 26.6 | Frente para la Victoria | 5.9 | 32.4 | 23.2 | 71.6 / 60.9 | **no identificada** |
| No votó | 20.4 | 9.0 | Frente para la Victoria | 3.1 | 12.1 | 3.2 | 62.5 / 57.0 |  |

## 2003p → 2007p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 3.1999, '2e-05': 2.9641, '2e-06': 2.8663, '2e-07': 2.8461, '0': 2.851}

Separación de las filas: 46.8 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Kirchner (FPV) | 17.0 | 8.6 | Cristina Kirchner (FPV) | 70.3 | 78.9 | 5.9 | 41.3 / 47.4 |  |
| Menem (Lealtad) | 19.0 | 4.7 | Rodríguez Saá (FREJULI) | 6.4 | 1.8 | 5.1 | 36.5 / 38.1 |  |
| López Murphy (Recrear) | 12.5 | 11.1 | Lavagna (UNA) | 42.1 | 53.2 | 3.3 | 63.1 / 65.9 |  |
| Rodríguez Saá (MNP) | 11.1 | 34.8 | Cristina Kirchner (FPV) | 50.5 | 15.7 | 6.2 | 34.7 / 50.0 | **no identificada** |
| Carrió (ARI) | 10.9 | 12.9 | Carrió (CC) | 73.3 | 86.1 | 5.2 | 67.0 / 77.7 |  |
| Otros | 7.2 | 6.9 | No votó | 32.5 | 25.6 | 9.3 | 40.6 / 38.0 |  |
| Blanco y nulo | 2.0 | 24.6 | Lavagna (UNA) | 20.7 | 45.3 | 6.6 | 69.6 / 75.3 | **no identificada** |
| No votó | 20.4 | 7.8 | Cristina Kirchner (FPV) | 2.9 | 10.7 | 3.3 | 53.9 / 52.6 |  |

## 2003p → 2009

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 3.7964, '2e-05': 3.4586, '2e-06': 3.2776, '2e-07': 3.2499, '0': 3.2654}

Separación de las filas: 36.6 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Kirchner (FPV) | 17.0 | 9.6 | PRO / Unión-PRO | 8.3 | 17.9 | 6.8 | 44.9 / 50.8 |  |
| Menem (Lealtad) | 19.0 | 23.4 | PRO / Unión-PRO | 23.6 | 0.2 | 7.4 | 27.2 / 35.2 |  |
| López Murphy (Recrear) | 12.5 | 6.9 | PRO / Unión-PRO | 23.9 | 30.8 | 5.4 | 57.3 / 62.9 |  |
| Rodríguez Saá (MNP) | 11.2 | 25.3 | Peronismo Federal | 10.6 | 35.9 | 8.7 | 12.7 / 32.1 | **cerca del promedio** |
| Carrió (ARI) | 10.9 | 19.2 | Peronismo Federal | 2.5 | 21.6 | 7.8 | 40.7 / 47.6 |  |
| Otros | 7.2 | 55.8 | Acuerdo Cívico y Social | 33.3 | 89.1 | 10.1 | 30.7 / 70.4 | **no identificada** |
| Blanco y nulo | 2.0 | 53.7 | Acuerdo Cívico y Social | 44.7 | 98.4 | 31.7 | 53.4 / 76.9 | **no identificada** |
| No votó | 20.3 | 11.7 | Peronismo Federal | 0.7 | 12.3 | 6.5 | 55.6 / 56.9 |  |

## 2009 → 2013

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 3.5622, '2e-05': 3.34, '2e-06': 3.0636, '2e-07': 3.034, '0': 3.1399}

Separación de las filas: 51.0 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 20.5 | 6.2 | Frente Renovador | 6.2 | 0.0 | 6.3 | 55.7 / 56.6 |  |
| Acuerdo Cívico y Social | 21.2 | 6.2 | Unión por Córdoba | 0.1 | 6.3 | 3.8 | 49.3 / 57.9 |  |
| PRO / Unión-PRO | 13.2 | 31.9 | Frente Renovador | 49.3 | 81.3 | 18.2 | 51.0 / 70.4 | **no identificada** |
| Peronismo Federal | 5.6 | 27.1 | Otros | 5.0 | 32.1 | 11.1 | 40.2 / 74.0 |  |
| Proyecto Sur | 1.5 | 66.8 | PRO | 12.3 | 79.1 | 4.6 | 55.5 / 74.4 | **no identificada** |
| Otros | 7.3 | 53.9 | Otros | 28.7 | 82.6 | 22.2 | 35.6 / 81.0 | **no identificada** |
| Blanco y nulo | 3.6 | 10.6 | PRO | 10.9 | 0.3 | 28.7 | 53.8 / 69.6 |  |
| No votó | 27.2 | 12.6 | Frente para la Victoria | 15.7 | 28.3 | 4.3 | 38.8 / 45.2 |  |

## 2011p → 2015p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.5842, '2e-05': 2.4483, '2e-06': 2.3611, '2e-07': 2.3392, '0': 2.3515}

Separación de las filas: 46.3 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 41.1 | 2.4 | UNA (Massa) | 19.0 | 16.6 | 2.8 | 40.2 / 40.7 |  |
| FAP | 12.8 | 23.0 | Cambiemos | 76.8 | 99.8 | 7.7 | 55.0 / 72.8 |  |
| UDESO (UCR) | 8.4 | 5.0 | UNA (Massa) | 9.4 | 14.4 | 7.4 | 61.0 / 58.3 |  |
| Compromiso Federal | 6.0 | 40.9 | Compromiso Federal | 11.9 | 52.8 | 12.4 | 49.4 / 54.8 | **no identificada** |
| Frente Popular | 4.5 | 17.3 | Cambiemos | 58.1 | 40.8 | 11.6 | 47.3 / 50.3 |  |
| FIT | 1.8 | 38.1 | UNA (Massa) | 61.0 | 99.1 | 33.1 | 67.8 / 82.3 | **no identificada** |
| CC-ARI | 1.4 | 19.1 | Cambiemos | 91.9 | 72.7 | 8.1 | 70.2 / 65.3 |  |
| Blanco y nulo | 3.2 | 16.1 | Cambiemos | 8.7 | 24.8 | 14.2 | 63.4 / 47.0 |  |
| No votó | 21.0 | 9.5 | No votó | 73.9 | 64.3 | 3.9 | 54.9 / 45.4 |  |

## 2015p → 2015b

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 1.9129, '2e-05': 1.8231, '2e-06': 1.7539, '2e-07': 1.7367, '0': 1.7398}

Separación de las filas: 49.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 28.8 | 2.7 | No votó | 0.8 | 3.5 | 0.5 | 59.9 / 57.6 |  |
| Cambiemos | 26.8 | 0.2 | Cambiemos | 99.7 | 99.9 | 0.3 | 59.0 / 59.2 |  |
| UNA (Massa) | 16.7 | 7.0 | Cambiemos | 54.3 | 61.3 | 2.8 | 15.0 / 21.1 | **cerca del promedio** |
| FIT | 2.6 | 11.2 | Frente para la Victoria | 80.9 | 69.6 | 4.6 | 51.8 / 44.2 |  |
| Progresistas | 2.0 | 19.3 | Cambiemos | 63.0 | 43.7 | 8.5 | 43.5 / 26.4 |  |
| Compromiso Federal | 1.3 | 3.0 | Frente para la Victoria | 34.9 | 37.9 | 6.4 | 12.9 / 9.1 |  |
| Blanco y nulo | 2.6 | 20.2 | Frente para la Victoria | 63.6 | 43.4 | 11.7 | 30.7 / 25.8 | **no identificada** |
| No votó | 19.3 | 5.3 | Frente para la Victoria | 1.6 | 6.9 | 2.6 | 65.2 / 64.4 |  |

## 2011p → 2015b

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 3.0391, '2e-05': 2.8723, '2e-06': 2.8637, '2e-07': 2.8447, '0': 2.8299}

Separación de las filas: 49.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 41.2 | 5.1 | Frente para la Victoria | 84.7 | 79.6 | 2.2 | 46.4 / 41.3 |  |
| FAP | 12.7 | 9.2 | Cambiemos | 90.6 | 99.9 | 8.9 | 51.7 / 59.3 |  |
| UDESO (UCR) | 8.4 | 2.9 | Cambiemos | 96.9 | 99.8 | 2.7 | 56.3 / 59.2 |  |
| Compromiso Federal | 6.0 | 18.7 | Cambiemos | 93.8 | 75.2 | 3.3 | 53.2 / 36.4 |  |
| Frente Popular | 4.4 | 5.5 | Blanco y nulo | 1.9 | 7.4 | 9.2 | 47.1 / 51.9 |  |
| FIT | 1.8 | 66.2 | Cambiemos | 31.8 | 98.0 | 22.0 | 24.5 / 57.4 | **no identificada** |
| CC-ARI | 1.4 | 2.4 | Blanco y nulo | 8.0 | 10.4 | 13.2 | 50.4 / 51.7 |  |
| Blanco y nulo | 3.2 | 19.4 | No votó | 11.6 | 31.0 | 12.6 | 30.9 / 33.7 |  |
| No votó | 21.0 | 15.4 | Frente para la Victoria | 8.3 | 23.7 | 4.1 | 46.2 / 40.4 |  |

## 1958d → 1962d

Penalización elegida: 2e-05; error de validación cruzada (pp): {'0.0002': 3.8697, '2e-05': 3.814, '2e-06': 3.8166, '2e-07': 3.8293, '0': 3.84}

Separación de las filas: 37.1 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCRI (Frondizi) | 41.6 | 15.9 | UCRI | 13.3 | 29.1 | 5.5 | 25.6 / 22.7 |  |
| UCRP (Balbín) | 27.2 | 20.7 | UCRI | 39.2 | 18.4 | 7.2 | 54.7 / 51.2 |  |
| Otros | 14.4 | 16.2 | UP y neoperonistas | 9.8 | 26.0 | 21.0 | 40.8 / 25.5 |  |
| Blanco y nulo | 8.3 | 1.9 | UP y neoperonistas | 76.2 | 74.2 | 14.7 | 46.3 / 44.3 |  |
| No votó | 8.6 | 25.2 | No votó | 45.0 | 70.2 | 15.9 | 46.6 / 60.8 |  |

Provincias donde un destino recibe más del 125 % de sus votos reales:

- 10, Otros: 2334 estimados contra 15 reales

## 1930d → 1946d

Penalización elegida: 0.0002; error de validación cruzada (pp): {'0.0002': 5.3247, '2e-05': 5.304, '2e-06': 5.3089, '2e-07': 5.324, '0': 5.3297}

Separación de las filas: 9.5 puntos — **matriz poco informativa**: las filas repiten el promedio

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR (yrigoyenismo) | 31.4 | 3.6 | Otros | 1.9 | 5.5 | 10.8 | 5.0 / 5.2 | **cerca del promedio** |
| Conservadores | 14.3 | 13.3 | Perón | 46.4 | 33.1 | 14.5 | 13.9 / 23.8 | **cerca del promedio** |
| Antipersonalistas | 8.0 | 2.8 | Unión Democrática | 33.0 | 30.1 | 23.1 | 6.5 / 6.5 | **cerca del promedio** |
| Socialistas | 13.4 | 4.1 | Unión Democrática | 49.8 | 45.7 | 12.1 | 17.3 / 15.5 | **cerca del promedio** |
| Otros | 6.4 | 11.0 | Perón | 71.2 | 60.2 | 28.8 | 27.6 / 16.7 |  |
| Blanco y nulo | 2.1 | 13.0 | Perón | 89.9 | 76.9 | 11.8 | 46.3 / 35.4 |  |
| No votó | 24.4 | 5.4 | Unión Democrática | 33.8 | 28.4 | 11.3 | 18.0 / 22.9 |  |

## 1937d → 1946d

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 4.1448, '2e-05': 3.9021, '2e-06': 3.855, '2e-07': 3.8882, '0': 3.873}

Separación de las filas: 30.5 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR (Alvear) | 49.1 | 15.2 | Unión Democrática | 24.9 | 40.1 | 16.5 | 23.3 / 13.5 | **cerca del promedio** |
| Concordancia (Ortiz) | 26.0 | 43.1 | Unión Democrática | 83.2 | 40.1 | 10.8 | 44.1 / 21.6 | **no identificada** |
| Socialista | 3.9 | 9.7 | Perón | 98.5 | 88.8 | 71.0 | 54.0 / 47.8 |  |
| Otros | 1.6 | 94.5 | Perón | 95.7 | 1.2 | 9.9 | 51.3 / 55.7 | **no identificada** |
| Blanco y nulo | 3.0 | 51.3 | Perón | 39.6 | 91.0 | 62.3 | 9.9 / 49.5 | **no identificada** |
| No votó | 16.5 | 35.0 | No votó | 63.2 | 28.2 | 34.7 | 55.7 / 24.3 | **no identificada** |

## 1940d → 1946d

Penalización elegida: 0.0002; error de validación cruzada (pp): {'0.0002': 4.772, '2e-05': 4.8384, '2e-06': 4.9345, '2e-07': 4.953, '0': 4.9455}

Separación de las filas: 19.9 puntos — **matriz poco informativa**: las filas repiten el promedio

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR | 35.5 | 14.5 | Perón | 66.0 | 51.4 | 24.1 | 20.9 / 8.7 | **cerca del promedio** |
| Concordancia | 23.5 | 18.1 | Perón | 23.8 | 42.0 | 22.4 | 21.3 / 5.6 | **cerca del promedio** |
| Socialista | 9.6 | 8.2 | Perón | 48.6 | 40.4 | 50.2 | 12.6 / 17.1 | **cerca del promedio** |
| Otros | 5.4 | 4.8 | Perón | 91.0 | 95.8 | 14.2 | 47.0 / 51.4 |  |
| Blanco y nulo | 3.6 | 1.1 | Demócrata Nacional | 0.4 | 1.5 | 2.0 | 47.9 / 49.5 |  |
| No votó | 22.5 | 9.7 | Unión Democrática | 48.8 | 58.5 | 9.8 | 31.8 / 40.8 |  |

Provincias donde un destino recibe más del 125 % de sus votos reales:

- 01, Blanco y nulo: 12385 estimados contra 8196 reales

## 1999pc → 2003pc

Penalización elegida: 0.0002; error de validación cruzada (pp): {'0.0002': 6.8729, '2e-05': 6.8889, '2e-06': 6.8985, '2e-07': 6.9041, '0': 6.9053}

Separación de las filas: 38.6 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Alianza (De la Rúa) | 45.1 | 8.8 | Otros | 11.6 | 20.4 | 7.6 | 27.5 / 30.2 |  |
| PJ (Duhalde) | 30.3 | 8.3 | Rodríguez Saá (MNP) | 25.9 | 17.6 | 7.4 | 44.1 / 44.2 |  |
| AR (Cavallo) | 9.7 | 18.2 | López Murphy (Recrear) | 43.8 | 25.6 | 11.1 | 53.2 / 41.9 |  |
| UCeDé | 8.3 | 20.8 | Menem (Lealtad) | 89.7 | 68.9 | 2.6 | 62.3 / 42.1 |  |
| Otros | 2.4 | 63.4 | Carrió (ARI) | 86.5 | 23.1 | 1.1 | 75.5 / 31.5 | **no identificada** |
| Blanco y nulo | 4.2 | 23.9 | Carrió (ARI) | 5.8 | 29.7 | 15.7 | 52.4 / 49.4 | **no identificada** |

## 1991c → 1995c

Penalización elegida: 0.0002; error de validación cruzada (pp): {'0.0002': 2.9601, '2e-05': 2.9708, '2e-06': 2.9799, '2e-07': 2.9815, '0': 2.9847}

Separación de las filas: 46.5 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR | 44.2 | 8.2 | UCR | 73.8 | 82.0 | 1.8 | 41.9 / 49.5 |  |
| PJ | 32.9 | 6.1 | PJ | 88.1 | 94.1 | 1.7 | 50.2 / 56.2 |  |
| UCeDé | 7.8 | 14.9 | UCeDé | 34.1 | 49.0 | 6.7 | 56.2 / 61.9 |  |
| CFI | 5.1 | 10.5 | PJ | 74.7 | 85.3 | 5.0 | 47.2 / 49.3 |  |
| Otros | 4.6 | 37.2 | FREPASO | 95.0 | 57.9 | 0.3 | 83.7 / 65.5 | **no identificada** |
| Blanco y nulo | 5.4 | 10.4 | FREPASO | 65.0 | 75.4 | 6.8 | 66.0 / 73.3 |  |

## 1999pe → 2003pe

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 4.1638, '2e-05': 4.1201, '2e-06': 4.0722, '2e-07': 4.0698, '0': 4.0985}

Separación de las filas: 27.4 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Alianza (De la Rúa) | 46.2 | 12.3 | Carrió (ARI) | 22.5 | 10.2 | 5.6 | 18.5 / 33.1 | **cerca del promedio** |
| PJ (Duhalde) | 36.5 | 26.9 | Menem (Lealtad) | 46.3 | 73.1 | 6.7 | 33.1 / 49.5 |  |
| AR (Cavallo) | 9.8 | 18.3 | López Murphy (Recrear) | 63.7 | 45.4 | 19.4 | 47.8 / 53.9 |  |
| Otros | 3.0 | 22.6 | Kirchner (FPV) | 37.1 | 14.4 | 51.4 | 57.3 / 48.0 | **no identificada** |
| Blanco y nulo | 4.5 | 39.3 | Menem (Lealtad) | 39.6 | 0.3 | 47.3 | 48.1 / 70.9 | **no identificada** |

## 2013 → 2017

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 3.2698, '2e-05': 3.0277, '2e-06': 2.902, '2e-07': 2.8707, '0': 2.9041}

Separación de las filas: 43.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 24.1 | 24.0 | Unidad Ciudadana | 51.7 | 27.7 | 4.9 | 54.5 / 39.9 |  |
| FPCyS / UNEN | 18.2 | 16.1 | Peronismo no kirchnerista | 1.0 | 17.1 | 3.9 | 49.5 / 46.8 |  |
| Frente Renovador | 13.6 | 27.8 | Cambiemos | 29.7 | 57.6 | 8.1 | 17.6 / 47.2 | **cerca del promedio** |
| PRO | 6.4 | 33.3 | Cambiemos | 72.1 | 38.8 | 8.3 | 42.4 / 50.2 | **no identificada** |
| FIT | 4.0 | 28.6 | Otros | 28.8 | 0.3 | 9.8 | 54.4 / 63.4 | **no identificada** |
| Unión por Córdoba | 1.8 | 12.0 | Cambiemos | 16.1 | 28.1 | 6.1 | 62.1 / 50.8 |  |
| Otros | 7.9 | 16.5 | Unidad Ciudadana | 7.5 | 24.0 | 6.6 | 27.2 / 28.3 |  |
| Blanco y nulo | 4.6 | 28.8 | No votó | 30.3 | 1.5 | 7.7 | 42.0 / 43.2 | **no identificada** |
| No votó | 19.5 | 6.9 | Unidad Ciudadana | 4.4 | 11.3 | 5.3 | 46.0 / 45.2 |  |

## 2015p → 2023p

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.3447, '2e-05': 2.2285, '2e-06': 2.1532, '2e-07': 2.124, '0': 2.1234}

Separación de las filas: 42.8 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 29.0 | 6.6 | Unión por la Patria | 71.5 | 78.0 | 2.6 | 45.1 / 50.5 |  |
| Cambiemos | 26.6 | 10.3 | Juntos por el Cambio | 59.6 | 49.3 | 2.0 | 45.9 / 46.5 |  |
| UNA (Massa) | 16.8 | 10.4 | Unión por la Patria | 14.1 | 3.7 | 4.7 | 34.1 / 40.1 |  |
| FIT | 2.6 | 27.0 | Unión por la Patria | 64.8 | 37.8 | 5.6 | 48.5 / 43.2 | **no identificada** |
| Progresistas | 2.0 | 27.8 | Juntos por el Cambio | 49.6 | 77.4 | 11.8 | 50.6 / 59.1 | **no identificada** |
| Compromiso Federal | 1.3 | 22.0 | La Libertad Avanza | 66.3 | 44.3 | 9.3 | 44.2 / 26.6 | **no identificada** |
| Blanco y nulo | 2.6 | 28.3 | La Libertad Avanza | 67.2 | 38.8 | 9.5 | 59.2 / 37.5 | **no identificada** |
| No votó | 19.2 | 9.1 | No votó | 80.5 | 89.7 | 4.5 | 58.9 / 67.6 |  |

## 2015p → 2023b

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.6248, '2e-05': 2.4849, '2e-06': 2.4312, '2e-07': 2.4124, '0': 2.4187}

Separación de las filas: 39.6 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 29.0 | 5.8 | No votó | 16.2 | 10.3 | 2.5 | 41.7 / 45.8 |  |
| Cambiemos | 26.6 | 2.8 | No votó | 7.8 | 10.6 | 1.8 | 47.3 / 45.5 |  |
| UNA (Massa) | 16.8 | 6.5 | La Libertad Avanza | 64.7 | 71.2 | 3.9 | 23.7 / 30.5 | **cerca del promedio** |
| FIT | 2.6 | 43.5 | Unión por la Patria | 78.5 | 35.0 | 5.2 | 49.6 / 17.5 | **no identificada** |
| Progresistas | 2.0 | 1.3 | Unión por la Patria | 99.5 | 98.2 | 1.7 | 66.8 / 65.5 |  |
| Compromiso Federal | 1.3 | 18.0 | La Libertad Avanza | 68.2 | 50.2 | 6.4 | 27.0 / 9.9 |  |
| Blanco y nulo | 2.6 | 25.1 | No votó | 5.1 | 30.1 | 9.1 | 44.5 / 32.1 | **no identificada** |
| No votó | 19.2 | 7.5 | No votó | 74.9 | 82.4 | 3.9 | 51.3 / 58.8 |  |

## 2015b → 2023p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.6463, '2e-05': 2.5378, '2e-06': 2.4442, '2e-07': 2.4251, '0': 2.4323}

Separación de las filas: 39.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 38.6 | 5.6 | Unión por la Patria | 65.7 | 71.2 | 1.6 | 40.0 / 43.9 |  |
| Cambiemos | 40.4 | 7.5 | No votó | 11.2 | 3.7 | 2.2 | 38.4 / 47.4 |  |
| Blanco y nulo | 2.0 | 51.4 | Unión por la Patria | 51.7 | 0.4 | 11.9 | 50.0 / 67.9 | **no identificada** |
| No votó | 19.0 | 9.0 | No votó | 85.4 | 94.4 | 5.8 | 63.6 / 72.6 |  |

## 2015b → 2023b

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.5552, '2e-05': 2.4982, '2e-06': 2.4637, '2e-07': 2.4412, '0': 2.4556}

Separación de las filas: 40.0 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 38.7 | 5.9 | Unión por la Patria | 69.0 | 74.9 | 1.4 | 36.2 / 42.1 |  |
| Cambiemos | 40.4 | 5.7 | Unión por la Patria | 6.1 | 0.4 | 1.6 | 43.6 / 45.9 |  |
| Blanco y nulo | 2.0 | 58.9 | Unión por la Patria | 74.1 | 15.2 | 6.3 | 62.4 / 43.6 | **no identificada** |
| No votó | 19.0 | 6.4 | La Libertad Avanza | 6.7 | 0.3 | 4.6 | 57.0 / 62.8 |  |

## 2013 → 2015p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.9205, '2e-05': 2.7416, '2e-06': 2.6864, '2e-07': 2.6766, '0': 2.6737}

Separación de las filas: 45.8 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 24.0 | 5.4 | Frente para la Victoria | 86.5 | 81.1 | 2.7 | 57.8 / 52.3 |  |
| FPCyS / UNEN | 18.3 | 13.1 | Cambiemos | 75.9 | 62.9 | 3.7 | 49.8 / 36.4 |  |
| Frente Renovador | 13.4 | 41.3 | Cambiemos | 18.6 | 59.9 | 6.8 | 22.6 / 43.6 | **no identificada**, **cerca del promedio** |
| PRO | 6.5 | 7.0 | UNA (Massa) | 21.1 | 28.1 | 10.3 | 38.0 / 47.9 |  |
| FIT | 4.0 | 13.5 | UNA (Massa) | 28.1 | 41.6 | 9.2 | 52.5 / 52.3 |  |
| Unión por Córdoba | 1.8 | 31.3 | Cambiemos | 14.1 | 45.4 | 6.7 | 38.9 / 38.7 | **no identificada** |
| Otros | 7.9 | 10.3 | Compromiso Federal | 6.4 | 16.7 | 5.5 | 19.2 / 27.7 |  |
| Blanco y nulo | 4.5 | 14.0 | UNA (Massa) | 42.5 | 28.6 | 7.8 | 40.0 / 48.5 |  |
| No votó | 19.6 | 12.9 | Cambiemos | 14.3 | 1.4 | 5.2 | 49.7 / 56.8 |  |

## 2013 → 2015b

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 4.0508, '2e-05': 3.8017, '2e-06': 3.7445, '2e-07': 3.7352, '0': 3.7353}

Separación de las filas: 41.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 24.1 | 6.6 | Frente para la Victoria | 94.0 | 87.4 | 1.5 | 55.7 / 49.1 |  |
| FPCyS / UNEN | 18.3 | 13.7 | Cambiemos | 90.1 | 76.4 | 3.1 | 49.4 / 35.7 |  |
| Frente Renovador | 13.4 | 34.6 | Cambiemos | 43.2 | 77.8 | 7.1 | 2.6 / 37.2 | **no identificada**, **cerca del promedio** |
| PRO | 6.5 | 2.3 | No votó | 5.5 | 3.2 | 4.6 | 43.6 / 44.3 |  |
| FIT | 4.0 | 7.9 | Blanco y nulo | 11.2 | 3.3 | 12.0 | 33.1 / 32.3 |  |
| Unión por Córdoba | 1.8 | 15.3 | Cambiemos | 50.4 | 65.8 | 8.4 | 10.9 / 25.1 |  |
| Otros | 7.9 | 12.2 | Frente para la Victoria | 37.1 | 49.2 | 6.2 | 10.0 / 12.2 |  |
| Blanco y nulo | 4.6 | 26.6 | Cambiemos | 15.1 | 41.8 | 11.1 | 25.6 / 9.0 | **no identificada** |
| No votó | 19.6 | 15.8 | Cambiemos | 22.9 | 7.1 | 5.3 | 45.2 / 53.5 |  |

## 2009 → 2015p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 3.1847, '2e-05': 2.9933, '2e-06': 2.9512, '2e-07': 2.9398, '0': 2.9398}

Separación de las filas: 42.4 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 20.3 | 11.2 | Frente para la Victoria | 83.2 | 72.0 | 3.3 | 54.7 / 47.5 |  |
| Acuerdo Cívico y Social | 21.4 | 9.3 | Cambiemos | 78.0 | 68.7 | 2.5 | 50.7 / 41.5 |  |
| PRO / Unión-PRO | 13.3 | 19.5 | Cambiemos | 39.0 | 58.5 | 10.8 | 19.0 / 46.8 | **cerca del promedio** |
| Peronismo Federal | 5.7 | 15.0 | Frente para la Victoria | 24.2 | 9.1 | 6.1 | 22.5 / 30.1 | **cerca del promedio** |
| Proyecto Sur | 1.6 | 64.5 | Cambiemos | 7.6 | 72.0 | 12.0 | 50.1 / 62.3 | **no identificada** |
| Otros | 7.2 | 23.9 | UNA (Massa) | 41.5 | 17.6 | 9.8 | 30.2 / 26.7 |  |
| Blanco y nulo | 3.6 | 33.4 | UNA (Massa) | 72.1 | 38.7 | 22.4 | 64.6 / 66.3 | **no identificada** |
| No votó | 27.1 | 19.9 | Frente para la Victoria | 20.3 | 40.2 | 6.5 | 32.7 / 45.5 |  |

## 2009 → 2015b

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 4.3459, '2e-05': 4.0512, '2e-06': 3.9633, '2e-07': 3.9559, '0': 3.9616}

Separación de las filas: 40.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 20.4 | 12.2 | Frente para la Victoria | 92.3 | 80.1 | 1.9 | 54.3 / 42.1 |  |
| Acuerdo Cívico y Social | 21.3 | 7.6 | Cambiemos | 87.0 | 79.4 | 2.3 | 46.1 / 38.5 |  |
| PRO / Unión-PRO | 13.3 | 16.6 | Cambiemos | 64.5 | 81.1 | 8.6 | 25.6 / 40.2 |  |
| Peronismo Federal | 5.6 | 10.3 | Cambiemos | 47.2 | 57.5 | 6.6 | 6.3 / 16.6 | **cerca del promedio** |
| Proyecto Sur | 1.5 | 24.9 | Frente para la Victoria | 30.2 | 5.3 | 15.1 | 22.8 / 36.6 | **no identificada** |
| Otros | 7.1 | 4.3 | Frente para la Victoria | 54.9 | 59.2 | 5.9 | 17.1 / 21.7 |  |
| Blanco y nulo | 3.6 | 20.3 | Cambiemos | 32.1 | 52.4 | 18.2 | 8.8 / 16.5 | **no identificada** |
| No votó | 27.1 | 14.0 | Cambiemos | 21.3 | 7.4 | 5.2 | 26.7 / 34.8 |  |

## 2017 → 2019p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.2998, '2e-05': 2.1341, '2e-06': 2.0542, '2e-07': 2.0472, '0': 2.0486}

Separación de las filas: 57.1 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Cambiemos | 30.7 | 1.1 | Consenso Federal | 3.7 | 4.8 | 1.3 | 60.5 / 60.3 |  |
| Unidad Ciudadana | 16.5 | 8.2 | Frente de Todos | 95.7 | 87.6 | 2.1 | 57.8 / 49.6 |  |
| Peronismo no kirchnerista | 12.6 | 4.3 | Juntos por el Cambio | 4.9 | 0.7 | 3.2 | 47.7 / 50.4 |  |
| 1País | 4.3 | 21.4 | Frente de Todos | 64.8 | 86.2 | 8.1 | 43.2 / 50.8 | **no identificada** |
| FIT | 3.5 | 12.2 | Frente de Todos | 38.2 | 50.4 | 7.8 | 34.0 / 43.2 |  |
| Otros | 6.2 | 10.1 | Frente de Todos | 24.4 | 34.5 | 4.7 | 18.6 / 13.2 |  |
| Blanco y nulo | 3.3 | 7.8 | Frente de Todos | 60.6 | 52.8 | 8.4 | 47.6 / 41.7 |  |
| No votó | 22.9 | 7.0 | No votó | 71.8 | 78.8 | 3.0 | 55.7 / 62.2 |  |

## 2017 → 2019

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.4243, '2e-05': 2.2189, '2e-06': 2.1111, '2e-07': 2.0952, '0': 2.099}

Separación de las filas: 57.9 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Cambiemos | 30.7 | 3.7 | Consenso Federal | 3.4 | 7.1 | 1.3 | 61.0 / 60.0 |  |
| Unidad Ciudadana | 16.5 | 10.6 | Frente de Todos | 95.0 | 84.3 | 1.4 | 59.9 / 52.0 |  |
| Peronismo no kirchnerista | 12.6 | 3.6 | Frente de Todos | 75.6 | 79.2 | 2.8 | 47.7 / 48.2 |  |
| 1País | 4.3 | 19.1 | Frente de Todos | 67.8 | 86.9 | 8.5 | 42.9 / 51.9 |  |
| FIT | 3.5 | 15.6 | Frente de Todos | 28.1 | 43.7 | 5.8 | 48.6 / 43.6 |  |
| Otros | 6.2 | 18.5 | Frente de Todos | 15.7 | 34.2 | 4.2 | 28.6 / 12.0 |  |
| Blanco y nulo | 3.3 | 9.6 | Frente de Todos | 52.0 | 42.4 | 7.7 | 54.3 / 46.3 |  |
| No votó | 22.9 | 8.7 | No votó | 74.1 | 82.8 | 2.7 | 56.7 / 63.6 |  |

## 2015p → 2019p

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 1.787, '2e-05': 1.6975, '2e-06': 1.6311, '2e-07': 1.605, '0': 1.6077}

Separación de las filas: 52.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 28.9 | 1.5 | Frente de Todos | 96.9 | 95.3 | 1.0 | 59.0 / 57.4 |  |
| Cambiemos | 26.7 | 3.6 | Juntos por el Cambio | 98.0 | 94.5 | 0.7 | 65.9 / 62.4 |  |
| UNA (Massa) | 16.7 | 13.2 | Juntos por el Cambio | 23.7 | 36.9 | 3.5 | 20.8 / 18.7 | **cerca del promedio** |
| FIT | 2.6 | 20.6 | Frente de Todos | 62.5 | 42.0 | 6.1 | 39.2 / 47.3 | **no identificada** |
| Progresistas | 2.0 | 32.8 | Frente de Todos | 6.4 | 39.2 | 7.5 | 59.9 / 41.2 | **no identificada** |
| Compromiso Federal | 1.3 | 13.5 | Juntos por el Cambio | 11.7 | 25.2 | 12.6 | 32.0 / 21.2 |  |
| Blanco y nulo | 2.6 | 26.7 | Frente de Todos | 48.8 | 22.1 | 11.9 | 36.3 / 46.5 | **no identificada** |
| No votó | 19.3 | 3.3 | Frente de Todos | 4.2 | 7.5 | 2.7 | 64.3 / 64.8 |  |

## 2015b → 2019p

Penalización elegida: 2e-05; error de validación cruzada (pp): {'0.0002': 1.7568, '2e-05': 1.7253, '2e-06': 1.7174, '2e-07': 1.713, '0': 1.7131}

Separación de las filas: 51.1 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Frente para la Victoria | 38.4 | 1.0 | Frente de Todos | 92.8 | 93.9 | 0.6 | 55.0 / 55.9 |  |
| Cambiemos | 40.5 | 2.8 | No votó | 9.9 | 7.1 | 0.7 | 47.5 / 49.7 |  |
| Blanco y nulo | 2.0 | 24.1 | Consenso Federal | 78.0 | 53.9 | 1.2 | 88.8 / 83.7 | **no identificada** |
| No votó | 19.1 | 8.9 | No votó | 74.5 | 83.4 | 1.4 | 62.4 / 68.1 |  |

## 1989p → 1995p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 4.2548, '2e-05': 4.1987, '2e-06': 4.143, '2e-07': 4.1204, '0': 4.1227}

Separación de las filas: 27.4 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| PJ (Menem) | 46.9 | 15.5 | PJ (Menem) | 72.6 | 88.1 | 6.7 | 26.7 / 40.3 |  |
| UCR (Angeloz) | 36.4 | 12.1 | UCR (Massaccesi) | 38.1 | 50.1 | 7.5 | 30.2 / 37.3 |  |
| Alianza de Centro | 7.0 | 55.1 | FREPASO (Bordón) | 27.5 | 82.6 | 15.5 | 17.7 / 54.4 | **no identificada**, **cerca del promedio** |
| Unidad Socialista | 1.4 | 3.7 | FREPASO (Bordón) | 99.0 | 95.3 | 2.9 | 70.9 / 67.2 |  |
| MPN | 0.2 | 16.6 | PJ (Menem) | 67.4 | 50.7 | 37.7 | 42.6 / 30.6 |  |
| Otros | 6.0 | 13.9 | Otros | 4.1 | 18.0 | 27.7 | 53.9 / 54.8 |  |
| Blanco y nulo | 2.0 | 34.1 | FREPASO (Bordón) | 36.8 | 2.7 | 20.4 | 18.7 / 41.4 | **no identificada** |

## 1989d → 1994c

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.6237, '2e-05': 2.4007, '2e-06': 2.377, '2e-07': 2.3547, '0': 2.3699}

Separación de las filas: 32.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| PJ | 43.9 | 21.8 | PJ | 56.7 | 78.5 | 7.8 | 28.0 / 42.9 |  |
| UCR | 28.4 | 12.8 | PJ | 20.3 | 7.6 | 7.9 | 36.3 / 47.5 |  |
| Alianza de Centro | 10.5 | 53.5 | PAL | 7.1 | 60.6 | 13.9 | 38.3 / 65.6 | **no identificada** |
| CFI | 3.3 | 46.5 | PRS | 8.1 | 54.7 | 26.5 | 44.5 / 77.2 | **no identificada** |
| Izquierda Unida | 3.4 | 9.7 | Frente Grande | 88.9 | 98.5 | 2.5 | 79.0 / 86.2 |  |
| Unidad Socialista | 2.6 | 46.3 | Frente Grande | 16.5 | 62.8 | 43.4 | 67.4 / 71.8 | **no identificada** |
| Fuerza Republicana | 1.3 | 37.6 | Fuerza Republicana | 61.4 | 99.0 | 35.9 | 62.3 / 97.3 | **no identificada** |
| MPN | 0.4 | 22.2 | Frente Grande | 3.8 | 26.0 | 29.2 | 64.5 / 84.2 | **no identificada** |
| Otros | 3.9 | 16.3 | Otros | 36.6 | 53.0 | 39.3 | 43.8 / 49.0 |  |
| Blanco y nulo | 2.4 | 27.5 | Otros | 66.3 | 93.7 | 42.3 | 57.4 / 81.3 | **no identificada** |

## 1985d → 1987d

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.0416, '2e-05': 1.7909, '2e-06': 1.7031, '2e-07': 1.7026, '0': 1.7105}

Separación de las filas: 46.8 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR | 42.6 | 9.9 | PJ | 11.9 | 21.8 | 3.6 | 43.5 / 40.7 |  |
| PJ | 24.3 | 3.3 | PJ | 86.7 | 83.4 | 5.0 | 47.6 / 44.6 |  |
| Peronismo renovador | 10.3 | 14.5 | PJ | 95.7 | 81.2 | 8.2 | 55.2 / 40.8 |  |
| PI | 5.9 | 17.0 | UCeDé | 8.7 | 25.7 | 19.2 | 52.9 / 66.7 |  |
| UCeDé | 3.6 | 9.4 | UCeDé | 86.6 | 77.2 | 21.7 | 80.8 / 72.5 |  |
| Frente del Pueblo | 2.3 | 41.7 | PJ | 43.4 | 1.7 | 28.5 | 43.2 / 73.6 | **no identificada** |
| PAL | 1.1 | 8.4 | Otros | 1.6 | 10.0 | 20.3 | 84.4 / 86.7 |  |
| PRS | 0.5 | 20.6 | Otros | 72.8 | 52.2 | 18.3 | 60.0 / 42.4 | **no identificada** |
| Bloquista | 0.3 | 5.2 | Bloquista | 98.5 | 93.3 | 37.6 | 98.1 / 93.2 |  |
| MPN | 0.1 | 16.9 | MPN | 81.8 | 98.7 | 28.1 | 81.6 / 98.5 |  |
| Otros | 7.1 | 18.6 | UCeDé | 21.1 | 2.5 | 11.1 | 61.7 / 58.2 |  |
| Blanco y nulo | 1.9 | 52.1 | PPR | 4.3 | 56.4 | 22.5 | 39.1 / 68.9 | **no identificada** |

## 1983p → 1989p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.5332, '2e-05': 2.256, '2e-06': 2.2066, '2e-07': 2.2027, '0': 2.2167}

Separación de las filas: 37.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR (Alfonsín) | 50.2 | 5.4 | PJ (Menem) | 15.3 | 20.7 | 4.1 | 33.8 / 30.6 |  |
| PJ (Luder) | 39.2 | 5.4 | PJ (Menem) | 89.0 | 83.5 | 5.2 | 42.6 / 38.0 |  |
| PI | 2.2 | 56.5 | Alianza de Centro | 4.6 | 61.1 | 25.7 | 39.4 / 73.4 | **no identificada** |
| MID | 1.1 | 21.3 | PJ (Menem) | 17.1 | 38.4 | 16.1 | 35.9 / 20.4 | **no identificada** |
| Alianza Federal | 0.7 | 12.4 | Alianza de Centro | 74.0 | 61.6 | 21.2 | 69.9 / 63.8 |  |
| PAL | 0.7 | 14.5 | Alianza de Centro | 76.8 | 91.3 | 17.8 | 70.2 / 84.6 |  |
| Bloquista | 0.4 | 11.5 | PJ (Menem) | 44.0 | 32.4 | 52.5 | 45.7 / 54.8 |  |
| MPN | 0.2 | 5.7 | PJ (Menem) | 11.4 | 17.2 | 18.3 | 78.8 / 77.3 |  |
| MOFEPA | 0.1 | 23.3 | PJ (Menem) | 24.5 | 47.8 | 27.0 | 26.6 / 7.7 | **no identificada** |
| Otros | 2.4 | 25.4 | Otros | 38.0 | 12.6 | 15.0 | 43.9 / 22.1 | **no identificada** |
| Blanco y nulo | 2.8 | 11.4 | UCR (Angeloz) | 23.2 | 34.6 | 11.9 | 23.4 / 14.8 |  |

## 1987d → 1989p

Penalización elegida: 2e-05; error de validación cruzada (pp): {'0.0002': 2.4538, '2e-05': 2.3266, '2e-06': 2.387, '2e-07': 2.4055, '0': 2.4281}

Separación de las filas: 47.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| PJ | 40.6 | 4.5 | UCR (Angeloz) | 0.5 | 5.0 | 2.4 | 46.7 / 45.1 |  |
| UCR | 36.2 | 8.4 | PJ (Menem) | 6.5 | 15.0 | 2.1 | 48.6 / 41.1 |  |
| UCeDé | 5.7 | 16.3 | UCR (Angeloz) | 38.1 | 21.8 | 10.2 | 49.2 / 49.9 |  |
| FAP (Catamarca) | 0.6 | 56.8 | PJ (Menem) | 91.2 | 34.4 | 14.0 | 45.8 / 56.9 | **no identificada** |
| PAL | 1.0 | 15.9 | UCR (Angeloz) | 16.4 | 0.5 | 34.0 | 56.5 / 65.1 |  |
| MPN | 0.1 | 5.5 | PJ (Menem) | 26.8 | 32.2 | 19.0 | 67.2 / 65.2 |  |
| Bloquista | 0.4 | 20.9 | PJ (Menem) | 40.9 | 20.0 | 48.5 | 37.5 / 57.6 | **no identificada** |
| PPR | 0.2 | 18.3 | UCR (Angeloz) | 42.0 | 23.7 | 33.6 | 11.7 / 20.1 |  |
| Otros | 12.7 | 19.0 | PJ (Menem) | 34.2 | 15.2 | 7.7 | 26.7 / 31.5 |  |
| Blanco y nulo | 2.5 | 16.5 | UCR (Angeloz) | 4.3 | 20.8 | 23.1 | 43.9 / 42.4 |  |

## 1985d → 1989p

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.3441, '2e-05': 2.3188, '2e-06': 2.2935, '2e-07': 2.2984, '0': 2.2984}

Separación de las filas: 41.0 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR | 42.7 | 9.2 | PJ (Menem) | 13.1 | 22.3 | 3.5 | 37.3 / 36.5 |  |
| PJ | 23.9 | 3.4 | Otros | 1.7 | 5.2 | 3.8 | 48.0 / 46.7 |  |
| Peronismo renovador | 10.5 | 10.3 | PJ (Menem) | 94.0 | 83.7 | 7.1 | 47.5 / 43.0 |  |
| PI | 6.0 | 17.5 | PJ (Menem) | 53.1 | 35.6 | 15.7 | 27.3 / 27.6 |  |
| UCeDé | 3.6 | 4.9 | Alianza de Centro | 63.9 | 59.0 | 13.6 | 56.8 / 53.0 |  |
| Frente del Pueblo | 2.3 | 6.9 | Otros | 29.1 | 22.1 | 22.6 | 45.3 / 40.4 |  |
| PAL | 1.1 | 35.4 | Alianza de Centro | 37.4 | 72.8 | 60.3 | 31.9 / 66.8 | **no identificada** |
| PRS | 0.5 | 12.0 | Otros | 13.7 | 1.8 | 50.6 | 46.2 / 44.3 |  |
| Bloquista | 0.3 | 18.2 | Otros | 43.5 | 61.8 | 47.1 | 39.7 / 57.0 |  |
| MPN | 0.2 | 2.1 | PJ (Menem) | 16.8 | 14.7 | 28.3 | 81.0 / 81.2 |  |
| Otros | 7.0 | 14.9 | PJ (Menem) | 21.4 | 6.4 | 11.3 | 28.8 / 43.9 |  |
| Blanco y nulo | 1.9 | 3.0 | Blanco y nulo | 1.6 | 4.7 | 14.1 | 36.6 / 37.5 |  |

## 1989p → 1997d

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 3.3389, '2e-05': 3.0834, '2e-06': 2.9747, '2e-07': 2.9286, '0': 2.9782}

Separación de las filas: 30.0 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| PJ (Menem) | 46.8 | 23.9 | PJ | 59.5 | 83.3 | 7.6 | 26.8 / 49.6 |  |
| UCR (Angeloz) | 36.0 | 16.4 | Alianza | 74.8 | 91.3 | 9.5 | 30.8 / 48.0 |  |
| Alianza de Centro | 6.9 | 62.1 | Partido Nuevo | 2.2 | 64.3 | 28.2 | 47.2 / 89.5 | **no identificada** |
| Unidad Socialista | 1.4 | 24.8 | Otros | 27.4 | 2.6 | 20.7 | 46.7 / 45.7 | **no identificada** |
| MPN | 0.2 | 36.2 | PJ | 41.7 | 5.5 | 40.9 | 65.6 / 81.8 | **no identificada** |
| Otros | 6.6 | 49.3 | Alianza | 58.6 | 9.3 | 20.0 | 42.2 / 76.4 | **no identificada** |
| Blanco y nulo | 2.0 | 42.1 | Otros | 43.5 | 1.4 | 42.1 | 51.9 / 48.1 | **no identificada** |

## 1995p → 1997d

Penalización elegida: 2e-05; error de validación cruzada (pp): {'0.0002': 2.7722, '2e-05': 2.6555, '2e-06': 2.8583, '2e-07': 2.8846, '0': 2.9358}

Separación de las filas: 33.5 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| PJ (Menem) | 47.9 | 18.7 | PJ | 58.1 | 76.9 | 6.1 | 29.9 / 43.7 |  |
| FREPASO (Bordón) | 28.0 | 23.5 | Alianza | 84.4 | 60.9 | 4.9 | 41.1 / 40.7 |  |
| UCR (Massaccesi) | 16.3 | 13.8 | PJ | 24.1 | 10.3 | 7.7 | 30.9 / 44.4 |  |
| Otros | 3.5 | 79.5 | Fuerza Republicana | 2.8 | 82.3 | 37.5 | 52.2 / 86.6 | **no identificada** |
| Blanco y nulo | 4.3 | 31.4 | MPN | 1.6 | 33.0 | 19.7 | 65.5 / 66.9 | **no identificada** |

Provincias donde un destino recibe más del 125 % de sus votos reales:

- 22, Otros: 5496 estimados contra 2490 reales

## 1995p → 1999p

Penalización elegida: 2e-05; error de validación cruzada (pp): {'0.0002': 3.4998, '2e-05': 3.4347, '2e-06': 3.5293, '2e-07': 3.5255, '0': 3.5323}

Separación de las filas: 35.8 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| PJ (Menem) | 48.0 | 9.7 | PJ (Duhalde) | 63.4 | 73.2 | 4.6 | 31.8 / 36.5 |  |
| FREPASO (Bordón) | 27.8 | 9.3 | AR (Cavallo) | 13.0 | 22.3 | 3.8 | 42.3 / 42.8 |  |
| UCR (Massaccesi) | 16.4 | 1.6 | Alianza (De la Rúa) | 82.7 | 81.1 | 9.6 | 36.7 / 35.1 |  |
| Otros | 3.5 | 43.6 | PJ (Duhalde) | 93.4 | 49.8 | 5.2 | 56.7 / 37.7 | **no identificada** |
| Blanco y nulo | 4.3 | 25.0 | AR (Cavallo) | 41.9 | 16.9 | 15.3 | 41.3 / 34.3 | **no identificada** |

Provincias donde un destino recibe más del 125 % de sus votos reales:

- 06, Blanco y nulo: 12716 estimados contra 7808 reales
- 14, Blanco y nulo: 11316 estimados contra 6103 reales

## 1983p → 1985d

Penalización elegida: 2e-06; error de validación cruzada (pp): {'0.0002': 2.572, '2e-05': 2.4049, '2e-06': 2.2606, '2e-07': 2.2564, '0': 2.2917}

Separación de las filas: 33.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR (Alfonsín) | 50.2 | 9.4 | Peronismo renovador | 3.9 | 13.3 | 6.7 | 29.2 / 26.4 |  |
| PJ (Luder) | 39.1 | 19.2 | Peronismo renovador | 19.4 | 0.1 | 6.9 | 39.4 / 40.1 |  |
| PI | 2.3 | 94.2 | Peronismo renovador | 2.6 | 96.8 | 24.5 | 54.3 / 86.5 | **no identificada** |
| MID | 1.2 | 34.4 | UCR | 53.7 | 19.3 | 27.5 | 18.8 / 47.2 | **no identificada** |
| Alianza Federal | 0.7 | 30.3 | UCeDé | 47.1 | 16.8 | 37.9 | 54.7 / 49.5 | **no identificada** |
| PAL | 0.7 | 10.9 | PAL | 88.5 | 99.4 | 18.5 | 87.4 / 98.3 |  |
| Bloquista | 0.4 | 20.5 | Bloquista | 60.8 | 81.3 | 39.8 | 60.5 / 81.1 | **no identificada** |
| MPN | 0.2 | 9.5 | UCR | 15.1 | 5.6 | 18.0 | 79.3 / 87.7 |  |
| MOFEPA | 0.1 | 30.5 | PJ | 14.6 | 45.1 | 23.6 | 63.3 / 62.0 | **no identificada** |
| Otros | 2.4 | 33.2 | PJ | 25.1 | 58.3 | 17.2 | 51.5 / 63.5 | **no identificada** |
| Blanco y nulo | 2.7 | 32.2 | PJ | 3.8 | 36.0 | 40.7 | 29.9 / 22.7 | **no identificada** |

## 1914d → 1916d

Penalización elegida: 2e-05; error de validación cruzada (pp): {'0.0002': 3.7074, '2e-05': 3.4702, '2e-06': 3.4665, '2e-07': 3.4814, '0': 3.5002}

Separación de las filas: 42.2 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| UCR | 36.6 | 17.2 | Conservadores | 14.2 | 31.5 | 9.0 | 33.8 / 26.9 |  |
| Conservadores | 36.2 | 7.7 | UCR | 36.4 | 28.8 | 10.3 | 32.4 / 40.9 |  |
| Socialistas | 18.4 | 5.3 | Socialista Argentino | 20.4 | 25.7 | 6.9 | 65.6 / 68.4 |  |
| Unión Cívica | 7.9 | 14.0 | Socialista Argentino | 44.4 | 58.4 | 22.3 | 71.1 / 73.4 |  |
| Independientes (Peña) | 0.8 | 38.0 | UCR | 71.5 | 33.4 | 15.6 | 30.9 / 16.8 | **no identificada** |
| Otros | 0.2 | 12.4 | UCR | 20.7 | 8.3 | 66.4 | 43.7 / 47.2 |  |

## 2023pp → 2025

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.7458, '2e-05': 2.2163, '2e-06': 1.9674, '2e-07': 1.9093, '0': 1.9223}

Separación de las filas: 50.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Massa (UxP) | 14.7 | 12.7 | Fuerza Patria | 87.2 | 99.9 | 2.3 | 65.7 / 78.4 |  |
| Grabois (UxP) | 4.0 | 13.5 | Fuerza Patria | 80.9 | 67.4 | 9.3 | 63.1 / 58.5 |  |
| Milei (LLA) | 20.7 | 9.4 | Otros | 15.8 | 25.2 | 4.6 | 36.4 / 41.5 |  |
| Bullrich (JxC) | 11.6 | 5.2 | No votó | 2.2 | 7.4 | 4.4 | 63.5 / 60.8 |  |
| Larreta (JxC) | 7.8 | 17.0 | Fuerza Patria | 4.6 | 21.7 | 9.2 | 41.1 / 41.2 |  |
| Schiaretti (Hacemos) | 2.6 | 35.2 | Provincias Unidas | 53.2 | 88.4 | 15.0 | 51.2 / 85.3 | **no identificada** |
| FIT-U | 1.8 | 17.2 | Fuerza Patria | 17.8 | 0.6 | 10.2 | 59.6 / 74.6 |  |
| Otros | 2.1 | 60.7 | Otros | 38.2 | 98.9 | 23.3 | 61.4 / 89.8 | **no identificada** |
| Blanco y nulo | 4.3 | 20.1 | Fuerza Patria | 20.8 | 0.7 | 13.3 | 27.6 / 38.0 | **no identificada** |
| No votó | 30.3 | 4.6 | Fuerza Patria | 5.9 | 1.4 | 2.7 | 52.1 / 54.2 |  |

## 2023p → 2025

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.3416, '2e-05': 2.1213, '2e-06': 1.9872, '2e-07': 1.9544, '0': 1.9649}

Separación de las filas: 42.7 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Unión por la Patria | 27.6 | 8.9 | Fuerza Patria | 70.1 | 79.0 | 2.2 | 49.0 / 57.4 |  |
| La Libertad Avanza | 22.7 | 9.7 | Otros | 12.1 | 21.9 | 4.9 | 31.2 / 43.2 |  |
| Juntos por el Cambio | 17.9 | 11.6 | No votó | 7.6 | 19.3 | 7.9 | 47.3 / 45.9 |  |
| Hacemos | 5.1 | 42.7 | Provincias Unidas | 37.3 | 80.0 | 12.8 | 43.6 / 85.2 | **no identificada** |
| FIT-U | 2.0 | 44.8 | Otros | 26.4 | 71.2 | 15.6 | 69.2 / 86.7 | **no identificada** |
| Blanco y nulo | 2.3 | 15.4 | Otros | 38.9 | 54.3 | 14.8 | 61.9 / 78.9 |  |
| No votó | 22.3 | 1.5 | Otros | 1.0 | 2.5 | 3.7 | 61.5 / 61.2 |  |

## 2023b → 2025

Penalización elegida: 2e-07; error de validación cruzada (pp): {'0.0002': 2.4028, '2e-05': 2.2414, '2e-06': 2.1095, '2e-07': 2.0883, '0': 2.0928}

Separación de las filas: 41.4 puntos

| Origen | Peso | Dif. Calvo | Celda | Principal | Calvo | IC | Sep. | |
|---|---|---|---|---|---|---|---|---|
| Unión por la Patria | 32.6 | 5.4 | Fuerza Patria | 64.0 | 69.4 | 2.2 | 47.5 / 49.1 |  |
| La Libertad Avanza | 41.2 | 4.3 | Provincias Unidas | 6.2 | 10.4 | 2.2 | 36.6 / 40.7 |  |
| Blanco y nulo | 2.5 | 52.8 | La Libertad Avanza | 53.5 | 0.7 | 8.9 | 45.7 / 80.3 | **no identificada** |
| No votó | 23.7 | 4.3 | No votó | 91.0 | 86.7 | 4.6 | 59.3 / 56.0 |  |
