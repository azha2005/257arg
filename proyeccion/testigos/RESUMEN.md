# Circuitos y mesas testigo

Generado por `python proyeccion/testigos.py`. Cifra: % del peronismo (FPV, FdT, UxP) sobre positivos. 3732 circuitos presentes con 100 votos o mas en las seis elecciones (los circuitos que cambiaron de codigo, como Santa Fe en 2023, quedan afuera).

Nacional: 2011p 53.96 %, 2015p 36.86 %, 2015b 48.60 %, 2019p 48.10 %, 2023p 36.69 %, 2023b 44.31 %

## 1. Testigos elegidos con 2011-2019, probados en 2023

Error absoluto en puntos del % nacional. Para los testigos hay una sola seleccion (err_p90 = err_abs); al azar, 500 sorteos.

### 2023p (real 36.69 %)

| N circuitos | testigos nivel | testigos swing | azar crudo | azar + swing 2019 |
|---|---|---|---|---|
| 5 | 2.09 (p90 2.09) | 3.40 (p90 3.40) | 6.38 (p90 13.27) | 2.06 (p90 4.25) |
| 10 | 0.42 (p90 0.42) | 0.33 (p90 0.33) | 5.57 (p90 10.92) | 1.53 (p90 3.12) |
| 25 | 0.85 (p90 0.85) | 1.94 (p90 1.94) | 4.18 (p90 7.98) | 1.03 (p90 2.11) |
| 50 | 0.05 (p90 0.05) | 0.90 (p90 0.90) | 3.75 (p90 6.57) | 0.76 (p90 1.57) |
| 100 | 0.11 (p90 0.11) | 0.81 (p90 0.81) | 3.46 (p90 5.41) | 0.56 (p90 1.16) |
| 250 | 0.68 (p90 0.68) | 1.14 (p90 1.14) | 3.03 (p90 3.97) | 0.49 (p90 0.85) |

### 2023b (real 44.31 %)

| N circuitos | testigos nivel | testigos swing | azar crudo | azar + swing 2019 |
|---|---|---|---|---|
| 5 | 3.84 (p90 3.84) | 1.89 (p90 1.89) | 6.88 (p90 13.29) | 2.49 (p90 5.10) |
| 10 | 1.54 (p90 1.54) | 0.08 (p90 0.08) | 5.44 (p90 10.63) | 1.82 (p90 3.66) |
| 25 | 0.29 (p90 0.29) | 1.31 (p90 1.31) | 4.19 (p90 7.92) | 1.18 (p90 2.43) |
| 50 | 0.32 (p90 0.32) | 0.23 (p90 0.23) | 3.85 (p90 7.06) | 0.94 (p90 1.89) |
| 100 | 0.15 (p90 0.15) | 0.67 (p90 0.67) | 3.60 (p90 5.51) | 0.75 (p90 1.56) |
| 250 | 0.80 (p90 0.80) | 1.15 (p90 1.15) | 3.18 (p90 4.17) | 0.72 (p90 1.17) |

**¿Persisten?** Correlacion (Spearman) entre el puntaje de 2011-2019 y la distancia al nacional en 2023: 2023p nivel 0.65, swing 0.17, 2023b nivel 0.63, swing 0.10.

## Los 25 circuitos mas parecidos al pais en 2011-2019

`nivel` = desvio cuadratico medio 2011-2019; despues, la diferencia con el nacional en 2023.

| distrito | seccion | circuito | nivel | 2023 general | 2023 balotaje | votos |
|---|---|---|---|---|---|---|
| Buenos Aires | La Plata | 0503A | 0.79 | +2.49 | +3.45 | 6910 |
| La Pampa | Maracó | 00057 | 0.97 | -4.83 | -4.78 | 17939 |
| Buenos Aires | 25 de Mayo | 00991 | 1.02 | -4.55 | -10.08 | 447 |
| Buenos Aires | Lobos | 00575 | 1.04 | -2.46 | -3.93 | 5629 |
| Buenos Aires | Leandro N. Alem | 00549 | 1.18 | -1.09 | -3.88 | 6696 |
| Buenos Aires | Pehuajó | 00734 | 1.19 | -0.15 | -1.84 | 22548 |
| Buenos Aires | Exaltación de la Cruz | 00293 | 1.28 | -2.79 | -4.38 | 8787 |
| Buenos Aires | Cañuelas | 00158 | 1.31 | +0.45 | -0.21 | 2987 |
| Ciudad Autónoma de Buenos Aires | Comuna 04 | 00052 | 1.37 | +4.80 | +7.09 | 8443 |
| Buenos Aires | La Plata | 0508E | 1.38 | +3.92 | +3.22 | 6294 |
| Buenos Aires | Villa Gesell | 00344 | 1.50 | +0.13 | -1.30 | 21740 |
| La Pampa | Chapaleufú | 00022 | 1.52 | -8.12 | -8.79 | 5398 |
| Entre Ríos | Paraná | 00005 | 1.55 | +0.86 | -0.75 | 8417 |
| Buenos Aires | Tres de Febrero | 00395 | 1.68 | +4.17 | +5.13 | 33040 |
| Entre Ríos | Paraná | 00010 | 1.68 | +2.53 | +1.10 | 4964 |
| Buenos Aires | General San Martín | 00378 | 1.69 | +7.45 | +8.50 | 21278 |
| Tucumán | Capital | 0009A | 1.75 | +0.13 | -2.51 | 8067 |
| Buenos Aires | General Las Heras | 00547 | 1.75 | +4.57 | +4.64 | 9742 |
| Buenos Aires | La Matanza | 00632 | 1.78 | +3.11 | +4.79 | 8645 |
| Buenos Aires | Rauch | 00806 | 1.91 | +1.26 | +2.80 | 9926 |
| Buenos Aires | Cañuelas | 00157 | 1.91 | +1.29 | -0.56 | 24163 |
| Buenos Aires | Morón | 00673 | 1.92 | +7.45 | +8.63 | 32413 |
| Buenos Aires | Bragado | 00140 | 1.92 | -1.55 | -2.69 | 447 |
| Buenos Aires | La Plata | 00508 | 1.93 | +5.55 | +7.21 | 8367 |
| Buenos Aires | General Alvarado | 00306 | 1.95 | -3.38 | -3.68 | 4913 |

## 2. Mesas: 1.a vuelta 2023 -> balotaje

101124 mesas con 100 votos positivos o mas; distancia media de todas al nacional del balotaje: 11.14 puntos. Correlacion (Spearman) entre la distancia en una y otra vuelta: 0.87.

| mesas mas cercanas en la 1.a vuelta | distancia en la 1.a | distancia media en el balotaje | % del grupo sumado en el balotaje (real 44.31) |
|---|---|---|---|
| 10 | 0.00 | 2.65 | 45.88 |
| 100 | 0.01 | 3.05 | 44.56 |
| 1000 | 0.09 | 3.08 | 44.58 |
| 5000 | 0.43 | 3.06 | 44.46 |

Una mesa tiene unos 300 votantes: solo por azar su % se mueve unos ±3 puntos, asi que una mesa sola no sirve de testigo; un grupo de mesas elegido con la eleccion anterior si, pero esas mesas no llegan cuando uno quiere. Por eso el modelo de proyeccion tiene que funcionar con las mesas que entren, al azar o no.
