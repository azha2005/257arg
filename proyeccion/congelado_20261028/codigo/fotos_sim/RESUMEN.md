# Fotos de actas: calibración con elecciones terminadas

Generado por `proyeccion/fotos_sim.py` (ver el encabezado del script). Error del **margen entre los dos primeros** en puntos (sobre votos positivos). `cobertura` = veces que la banda del 95 % por bootstrap de circuitos contiene el margen real; `factor` = por cuánto multiplicar la banda para que cubra el 95 %.

## 2015p → 2015b

Error absoluto medio del margen:

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | 1.60 | 1.13 | 0.75 | 1.22 | 0.87 | 0.59 | 2.22 | 1.53 | 1.06 | 3.24 | 2.79 | 2.63 |
| Goodman lam=0,1 + AMBA/resto | 1.51 | 1.05 | 0.70 | 1.20 | 0.84 | 0.58 | 2.06 | 1.38 | 0.98 | 2.53 | 1.73 | 1.35 |
| Goodman lam=0,1 + regiones | 1.59 | 1.08 | 0.71 | 1.30 | 0.85 | 0.59 | 2.16 | 1.46 | 0.98 | 2.53 | 1.79 | 1.38 |
| Goodman lam=0,3 | 1.61 | 1.13 | 0.75 | 1.24 | 0.88 | 0.60 | 2.21 | 1.52 | 1.07 | 3.19 | 2.77 | 2.64 |
| swing uniforme | 1.68 | 1.15 | 0.77 | 1.31 | 0.92 | 0.62 | 2.30 | 1.53 | 1.09 | 3.14 | 2.72 | 2.56 |
| swing uniforme + regiones | 1.68 | 1.16 | 0.73 | 1.41 | 0.90 | 0.61 | 2.17 | 1.44 | 1.04 | 2.42 | 1.75 | 1.39 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | -0.16 | -0.21 | -0.03 | -0.32 | +0.06 | -0.10 | -0.06 | -0.32 | +0.07 | -3.13 | -2.72 | -2.62 |
| Goodman lam=0,1 + AMBA/resto | -0.18 | -0.15 | -0.04 | -0.30 | +0.03 | -0.09 | +0.08 | -0.24 | +0.04 | -0.92 | -0.37 | -0.25 |
| Goodman lam=0,1 + regiones | -0.20 | -0.13 | +0.02 | -0.68 | +0.11 | -0.18 | -0.37 | -0.45 | +0.03 | -1.87 | -0.90 | -0.51 |
| Goodman lam=0,3 | -0.10 | -0.20 | -0.02 | -0.33 | +0.08 | -0.12 | +0.02 | -0.28 | +0.09 | -3.10 | -2.70 | -2.63 |
| swing uniforme | -0.05 | -0.19 | -0.03 | -0.43 | +0.09 | -0.14 | +0.09 | -0.22 | +0.13 | -3.01 | -2.65 | -2.55 |
| swing uniforme + regiones | -0.12 | -0.13 | +0.01 | -0.83 | +0.10 | -0.20 | -0.30 | -0.40 | +0.05 | -1.21 | -0.47 | -0.20 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 25 | 90 | 3.26 | 1.21 |
| Goodman lam=0,1 | azar | 50 | 91 | 2.46 | 1.15 |
| Goodman lam=0,1 | azar | 100 | 90 | 1.73 | 1.18 |
| Goodman lam=0,1 | estrat | 25 | 98 | 3.04 | 0.89 |
| Goodman lam=0,1 | estrat | 50 | 96 | 2.48 | 0.94 |
| Goodman lam=0,1 | estrat | 100 | 96 | 1.74 | 0.91 |
| Goodman lam=0,1 | racimos | 25 | 83 | 4.49 | 1.58 |
| Goodman lam=0,1 | racimos | 50 | 90 | 3.17 | 1.15 |
| Goodman lam=0,1 | racimos | 100 | 92 | 2.43 | 1.10 |
| Goodman lam=0,1 | twitter | 25 | 52 | 3.43 | 2.25 |
| Goodman lam=0,1 | twitter | 50 | 52 | 2.77 | 2.32 |
| Goodman lam=0,1 | twitter | 100 | 34 | 2.09 | 2.78 |
| Goodman lam=0,1 + AMBA/resto | azar | 25 | 88 | 3.16 | 1.21 |
| Goodman lam=0,1 + AMBA/resto | azar | 50 | 90 | 2.32 | 1.17 |
| Goodman lam=0,1 + AMBA/resto | azar | 100 | 90 | 1.62 | 1.15 |
| Goodman lam=0,1 + AMBA/resto | estrat | 25 | 92 | 2.85 | 1.03 |
| Goodman lam=0,1 + AMBA/resto | estrat | 50 | 96 | 2.30 | 1.03 |
| Goodman lam=0,1 + AMBA/resto | estrat | 100 | 98 | 1.63 | 0.82 |
| Goodman lam=0,1 + AMBA/resto | racimos | 25 | 85 | 4.38 | 1.59 |
| Goodman lam=0,1 + AMBA/resto | racimos | 50 | 90 | 2.95 | 1.11 |
| Goodman lam=0,1 + AMBA/resto | racimos | 100 | 92 | 2.24 | 1.06 |
| Goodman lam=0,1 + AMBA/resto | twitter | 25 | 72 | 4.10 | 1.94 |
| Goodman lam=0,1 + AMBA/resto | twitter | 50 | 80 | 3.25 | 1.46 |
| Goodman lam=0,1 + AMBA/resto | twitter | 100 | 82 | 2.63 | 1.42 |
| swing uniforme + regiones | azar | 25 | 88 | 3.09 | 1.25 |
| swing uniforme + regiones | azar | 50 | 90 | 2.45 | 1.28 |
| swing uniforme + regiones | azar | 100 | 88 | 1.70 | 1.28 |
| swing uniforme + regiones | estrat | 25 | 89 | 2.93 | 1.25 |
| swing uniforme + regiones | estrat | 50 | 94 | 2.40 | 1.02 |
| swing uniforme + regiones | estrat | 100 | 96 | 1.64 | 0.93 |
| swing uniforme + regiones | racimos | 25 | 78 | 4.20 | 1.45 |
| swing uniforme + regiones | racimos | 50 | 91 | 2.87 | 1.18 |
| swing uniforme + regiones | racimos | 100 | 94 | 2.28 | 1.06 |
| swing uniforme + regiones | twitter | 25 | 65 | 3.68 | 2.01 |
| swing uniforme + regiones | twitter | 50 | 78 | 2.98 | 1.81 |
| swing uniforme + regiones | twitter | 100 | 83 | 2.45 | 1.43 |

## 2015p → 2015b → n28 → ancla

Error absoluto medio del margen:

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | 1.24 | 1.76 |
| Prop. lam=0,1 + AMBA/resto | 1.26 | 1.77 |
| Prop. lam=300/n + AMBA/resto | 2.00 | 2.14 |
| Prop. puro + AMBA/resto | 3.29 | 3.16 |
| swing uniforme | 1.31 | 2.84 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | -0.18 | -0.15 |
| Prop. lam=0,1 + AMBA/resto | -0.24 | -0.22 |
| Prop. lam=300/n + AMBA/resto | -1.91 | -1.73 |
| Prop. puro + AMBA/resto | -3.28 | -3.12 |
| swing uniforme | -0.05 | -2.69 |

## 2019p → 2023p

Error absoluto medio del margen:

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | 2.08 | 1.64 | 1.14 | 1.73 | 1.27 | 0.89 | 3.51 | 2.57 | 1.71 | 5.82 | 4.86 | 4.92 |
| Goodman lam=0,1 + AMBA/resto | 1.94 | 1.45 | 1.01 | 1.72 | 1.29 | 0.89 | 3.23 | 2.24 | 1.47 | 3.84 | 2.54 | 1.90 |
| Goodman lam=0,1 + regiones | 1.88 | 1.43 | 0.98 | 1.72 | 1.27 | 0.87 | 3.29 | 2.43 | 1.46 | 4.36 | 2.82 | 2.05 |
| Goodman lam=0,3 | 2.08 | 1.65 | 1.14 | 1.73 | 1.27 | 0.90 | 3.46 | 2.55 | 1.71 | 5.69 | 4.78 | 4.85 |
| swing uniforme | 2.08 | 1.66 | 1.15 | 1.75 | 1.27 | 0.92 | 3.50 | 2.57 | 1.71 | 5.57 | 4.65 | 4.70 |
| swing uniforme + regiones | 1.97 | 1.46 | 1.00 | 1.78 | 1.29 | 0.90 | 3.35 | 2.51 | 1.50 | 4.09 | 2.71 | 2.05 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | -0.07 | +0.08 | -0.13 | +0.07 | -0.34 | +0.24 | -0.18 | +0.17 | -0.08 | +5.67 | +4.83 | +4.92 |
| Goodman lam=0,1 + AMBA/resto | -0.11 | +0.01 | -0.10 | +0.01 | -0.34 | +0.20 | -0.38 | +0.06 | -0.02 | +0.95 | +0.15 | -0.03 |
| Goodman lam=0,1 + regiones | +0.22 | +0.05 | -0.09 | +0.35 | -0.32 | +0.19 | +1.14 | +0.76 | +0.15 | +3.56 | +1.82 | +0.69 |
| Goodman lam=0,3 | -0.06 | +0.08 | -0.13 | +0.08 | -0.34 | +0.24 | -0.16 | +0.18 | -0.08 | +5.58 | +4.76 | +4.85 |
| swing uniforme | +0.00 | +0.10 | -0.12 | +0.17 | -0.33 | +0.26 | -0.05 | +0.25 | -0.04 | +5.46 | +4.64 | +4.70 |
| swing uniforme + regiones | +0.38 | +0.09 | -0.08 | +0.46 | -0.32 | +0.20 | +1.42 | +0.95 | +0.22 | +3.21 | +1.58 | +0.57 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 25 | 94 | 5.10 | 1.00 |
| Goodman lam=0,1 | azar | 50 | 91 | 3.69 | 1.07 |
| Goodman lam=0,1 | azar | 100 | 94 | 2.63 | 1.04 |
| Goodman lam=0,1 | estrat | 25 | 98 | 5.23 | 0.77 |
| Goodman lam=0,1 | estrat | 50 | 96 | 3.79 | 0.94 |
| Goodman lam=0,1 | estrat | 100 | 97 | 2.62 | 0.87 |
| Goodman lam=0,1 | racimos | 25 | 85 | 7.26 | 1.47 |
| Goodman lam=0,1 | racimos | 50 | 88 | 5.54 | 1.40 |
| Goodman lam=0,1 | racimos | 100 | 94 | 4.04 | 1.04 |
| Goodman lam=0,1 | twitter | 25 | 56 | 6.15 | 2.51 |
| Goodman lam=0,1 | twitter | 50 | 58 | 5.13 | 1.97 |
| Goodman lam=0,1 | twitter | 100 | 27 | 3.61 | 2.31 |
| Goodman lam=0,1 + AMBA/resto | azar | 25 | 92 | 4.64 | 1.08 |
| Goodman lam=0,1 + AMBA/resto | azar | 50 | 91 | 3.28 | 1.11 |
| Goodman lam=0,1 + AMBA/resto | azar | 100 | 94 | 2.32 | 1.01 |
| Goodman lam=0,1 + AMBA/resto | estrat | 25 | 95 | 4.70 | 0.89 |
| Goodman lam=0,1 + AMBA/resto | estrat | 50 | 94 | 3.31 | 1.08 |
| Goodman lam=0,1 + AMBA/resto | estrat | 100 | 94 | 2.32 | 1.10 |
| Goodman lam=0,1 + AMBA/resto | racimos | 25 | 86 | 7.07 | 1.33 |
| Goodman lam=0,1 + AMBA/resto | racimos | 50 | 90 | 5.01 | 1.20 |
| Goodman lam=0,1 + AMBA/resto | racimos | 100 | 94 | 3.47 | 1.00 |
| Goodman lam=0,1 + AMBA/resto | twitter | 25 | 76 | 6.94 | 1.90 |
| Goodman lam=0,1 + AMBA/resto | twitter | 50 | 88 | 5.47 | 1.28 |
| Goodman lam=0,1 + AMBA/resto | twitter | 100 | 92 | 4.09 | 1.21 |
| swing uniforme + regiones | azar | 25 | 90 | 4.53 | 1.21 |
| swing uniforme + regiones | azar | 50 | 90 | 3.31 | 1.21 |
| swing uniforme + regiones | azar | 100 | 94 | 2.33 | 1.06 |
| swing uniforme + regiones | estrat | 25 | 94 | 4.57 | 0.94 |
| swing uniforme + regiones | estrat | 50 | 93 | 3.28 | 1.07 |
| swing uniforme + regiones | estrat | 100 | 94 | 2.26 | 1.09 |
| swing uniforme + regiones | racimos | 25 | 81 | 6.10 | 1.55 |
| swing uniforme + regiones | racimos | 50 | 82 | 4.68 | 1.42 |
| swing uniforme + regiones | racimos | 100 | 91 | 3.47 | 1.12 |
| swing uniforme + regiones | twitter | 25 | 55 | 5.44 | 1.87 |
| swing uniforme + regiones | twitter | 50 | 68 | 4.52 | 1.53 |
| swing uniforme + regiones | twitter | 100 | 82 | 3.67 | 1.34 |

## 2019p → 2023p → n28 → ancla

Error absoluto medio del margen:

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | 1.97 | 2.69 |
| Prop. lam=0,1 + AMBA/resto | 1.93 | 2.65 |
| Prop. lam=300/n + AMBA/resto | 21.86 | 21.34 |
| Prop. puro + AMBA/resto | 38.65 | 38.49 |
| swing uniforme | 2.17 | 5.03 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | -0.30 | -0.19 |
| Prop. lam=0,1 + AMBA/resto | +0.26 | +0.39 |
| Prop. lam=300/n + AMBA/resto | +21.86 | +21.34 |
| Prop. puro + AMBA/resto | +38.65 | +38.49 |
| swing uniforme | -0.16 | +4.81 |

## 2019p → 2023p → n30

Error absoluto medio del margen:

| Método | azar 30 | como25 30 | twitter 30 |
|---|---:|---:|---:|
| Goodman lam=0,1 | 2.05 | 4.63 | 4.27 |
| Goodman lam=0,1 + AMBA/resto | 1.85 | 2.71 | 3.29 |
| Goodman lam=0,1 + regiones | 1.86 | 2.67 | 3.59 |
| Goodman lam=0,3 | 2.05 | 4.72 | 4.21 |
| swing uniforme | 2.06 | 5.04 | 4.26 |
| swing uniforme + regiones | 1.90 | 2.71 | 3.57 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 30 | como25 30 | twitter 30 |
|---|---:|---:|---:|
| Goodman lam=0,1 | -0.07 | +4.30 | +3.92 |
| Goodman lam=0,1 + AMBA/resto | -0.14 | -0.26 | +0.26 |
| Goodman lam=0,1 + regiones | +0.10 | +0.56 | +2.60 |
| Goodman lam=0,3 | -0.07 | +4.46 | +3.90 |
| swing uniforme | -0.04 | +4.86 | +3.95 |
| swing uniforme + regiones | +0.17 | +0.87 | +2.59 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 30 | 92 | 4.71 | 1.06 |
| Goodman lam=0,1 | como25 | 30 | 85 | 6.22 | 1.59 |
| Goodman lam=0,1 | twitter | 30 | 75 | 6.59 | 1.79 |
| Goodman lam=0,1 + AMBA/resto | azar | 30 | 92 | 4.24 | 1.07 |
| Goodman lam=0,1 + AMBA/resto | como25 | 30 | 88 | 5.67 | 1.31 |
| Goodman lam=0,1 + AMBA/resto | twitter | 30 | 85 | 6.81 | 1.42 |
| swing uniforme + regiones | azar | 30 | 88 | 4.14 | 1.22 |
| swing uniforme + regiones | como25 | 30 | 83 | 4.97 | 1.51 |
| swing uniforme + regiones | twitter | 30 | 60 | 5.24 | 1.88 |

## 2021bl → 2023p

Error absoluto medio del margen:

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | 2.44 | 1.67 | 1.09 | 1.83 | 1.25 | 0.84 | 3.91 | 2.74 | 1.79 | 7.14 | 5.74 | 5.60 |
| Goodman lam=0,1 + AMBA/resto | 2.14 | 1.52 | 0.99 | 1.87 | 1.24 | 0.85 | 3.46 | 2.27 | 1.48 | 4.59 | 3.05 | 2.21 |
| Goodman lam=0,1 + regiones | 2.03 | 1.38 | 0.93 | 1.87 | 1.22 | 0.82 | 3.81 | 2.33 | 1.52 | 5.35 | 3.48 | 2.31 |
| Goodman lam=0,3 | 2.56 | 1.76 | 1.16 | 1.86 | 1.27 | 0.85 | 4.01 | 2.91 | 1.90 | 7.74 | 6.49 | 6.51 |
| swing uniforme | 2.66 | 1.83 | 1.20 | 1.88 | 1.25 | 0.86 | 4.07 | 3.02 | 1.97 | 8.16 | 7.08 | 7.22 |
| swing uniforme + regiones | 2.13 | 1.46 | 0.96 | 1.89 | 1.23 | 0.84 | 3.95 | 2.44 | 1.59 | 5.06 | 3.44 | 2.35 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | -0.28 | +0.08 | +0.01 | +0.69 | -0.04 | +0.10 | +0.69 | +0.19 | -0.07 | +7.09 | +5.73 | +5.60 |
| Goodman lam=0,1 + AMBA/resto | -0.20 | +0.13 | -0.00 | +0.66 | -0.08 | +0.02 | +0.56 | +0.17 | -0.01 | +2.15 | +1.13 | +0.62 |
| Goodman lam=0,1 + regiones | +0.11 | +0.19 | -0.03 | +0.81 | -0.02 | +0.05 | +2.16 | +0.95 | +0.13 | +4.94 | +2.83 | +1.40 |
| Goodman lam=0,3 | -0.34 | +0.05 | -0.00 | +0.75 | -0.05 | +0.12 | +0.54 | +0.11 | -0.11 | +7.70 | +6.48 | +6.51 |
| swing uniforme | -0.39 | +0.05 | +0.04 | +0.82 | +0.02 | +0.22 | +0.32 | +0.05 | -0.12 | +8.13 | +7.07 | +7.22 |
| swing uniforme + regiones | +0.15 | +0.20 | +0.01 | +0.88 | +0.03 | +0.13 | +2.48 | +1.11 | +0.15 | +4.41 | +2.44 | +1.22 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 25 | 90 | 5.41 | 1.29 |
| Goodman lam=0,1 | azar | 50 | 94 | 3.89 | 1.02 |
| Goodman lam=0,1 | azar | 100 | 94 | 2.78 | 0.89 |
| Goodman lam=0,1 | estrat | 25 | 98 | 5.48 | 0.86 |
| Goodman lam=0,1 | estrat | 50 | 99 | 3.83 | 0.81 |
| Goodman lam=0,1 | estrat | 100 | 98 | 2.76 | 0.72 |
| Goodman lam=0,1 | racimos | 25 | 83 | 8.15 | 1.61 |
| Goodman lam=0,1 | racimos | 50 | 90 | 6.03 | 1.23 |
| Goodman lam=0,1 | racimos | 100 | 96 | 4.30 | 0.98 |
| Goodman lam=0,1 | twitter | 25 | 46 | 7.46 | 2.86 |
| Goodman lam=0,1 | twitter | 50 | 40 | 5.57 | 2.30 |
| Goodman lam=0,1 | twitter | 100 | 18 | 4.06 | 2.76 |
| Goodman lam=0,1 + AMBA/resto | azar | 25 | 90 | 4.75 | 1.13 |
| Goodman lam=0,1 + AMBA/resto | azar | 50 | 93 | 3.44 | 1.17 |
| Goodman lam=0,1 + AMBA/resto | azar | 100 | 95 | 2.37 | 0.95 |
| Goodman lam=0,1 + AMBA/resto | estrat | 25 | 95 | 4.80 | 0.96 |
| Goodman lam=0,1 + AMBA/resto | estrat | 50 | 96 | 3.28 | 0.95 |
| Goodman lam=0,1 + AMBA/resto | estrat | 100 | 97 | 2.42 | 0.85 |
| Goodman lam=0,1 + AMBA/resto | racimos | 25 | 84 | 7.80 | 1.55 |
| Goodman lam=0,1 + AMBA/resto | racimos | 50 | 90 | 5.19 | 1.10 |
| Goodman lam=0,1 + AMBA/resto | racimos | 100 | 91 | 3.61 | 1.10 |
| Goodman lam=0,1 + AMBA/resto | twitter | 25 | 67 | 8.39 | 2.28 |
| Goodman lam=0,1 + AMBA/resto | twitter | 50 | 82 | 5.90 | 1.48 |
| Goodman lam=0,1 + AMBA/resto | twitter | 100 | 82 | 4.46 | 1.49 |
| swing uniforme + regiones | azar | 25 | 86 | 4.83 | 1.21 |
| swing uniforme + regiones | azar | 50 | 94 | 3.37 | 0.96 |
| swing uniforme + regiones | azar | 100 | 94 | 2.29 | 1.01 |
| swing uniforme + regiones | estrat | 25 | 92 | 4.61 | 1.02 |
| swing uniforme + regiones | estrat | 50 | 95 | 3.18 | 0.97 |
| swing uniforme + regiones | estrat | 100 | 96 | 2.26 | 0.93 |
| swing uniforme + regiones | racimos | 25 | 76 | 7.31 | 1.85 |
| swing uniforme + regiones | racimos | 50 | 78 | 5.00 | 1.31 |
| swing uniforme + regiones | racimos | 100 | 91 | 3.57 | 1.22 |
| swing uniforme + regiones | twitter | 25 | 40 | 6.53 | 2.49 |
| swing uniforme + regiones | twitter | 50 | 57 | 5.11 | 2.02 |
| swing uniforme + regiones | twitter | 100 | 74 | 4.15 | 1.54 |

## 2021bl → 2023p → n28 → ancla

Error absoluto medio del margen:

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | 2.17 | 3.02 |
| Prop. lam=0,1 + AMBA/resto | 2.23 | 3.14 |
| Prop. lam=300/n + AMBA/resto | 13.23 | 13.03 |
| Prop. puro + AMBA/resto | 23.58 | 23.56 |
| swing uniforme | 2.59 | 7.41 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | -0.09 | +0.27 |
| Prop. lam=0,1 + AMBA/resto | +0.31 | +0.70 |
| Prop. lam=300/n + AMBA/resto | +13.23 | +13.03 |
| Prop. puro + AMBA/resto | +23.58 | +23.56 |
| swing uniforme | -0.13 | +7.38 |

## 2021bl → 2023p → n30

Error absoluto medio del margen:

| Método | azar 30 | como25 30 | twitter 30 |
|---|---:|---:|---:|
| Goodman lam=0,1 | 2.15 | 4.97 | 5.50 |
| Goodman lam=0,1 + AMBA/resto | 1.89 | 2.74 | 4.00 |
| Goodman lam=0,1 + regiones | 1.91 | 2.79 | 4.64 |
| Goodman lam=0,3 | 2.27 | 5.97 | 5.80 |
| swing uniforme | 2.34 | 7.22 | 6.03 |
| swing uniforme + regiones | 1.99 | 2.94 | 4.49 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 30 | como25 30 | twitter 30 |
|---|---:|---:|---:|
| Goodman lam=0,1 | +0.07 | +4.80 | +5.16 |
| Goodman lam=0,1 + AMBA/resto | +0.03 | -0.04 | +1.54 |
| Goodman lam=0,1 + regiones | +0.30 | +0.93 | +3.96 |
| Goodman lam=0,3 | +0.05 | +5.89 | +5.54 |
| swing uniforme | +0.05 | +7.21 | +5.83 |
| swing uniforme + regiones | +0.35 | +1.20 | +3.66 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 30 | 90 | 4.97 | 1.14 |
| Goodman lam=0,1 | como25 | 30 | 74 | 6.66 | 1.67 |
| Goodman lam=0,1 | twitter | 30 | 61 | 7.44 | 2.17 |
| Goodman lam=0,1 + AMBA/resto | azar | 30 | 90 | 4.36 | 1.23 |
| Goodman lam=0,1 + AMBA/resto | como25 | 30 | 88 | 5.91 | 1.29 |
| Goodman lam=0,1 + AMBA/resto | twitter | 30 | 73 | 7.40 | 1.83 |
| swing uniforme + regiones | azar | 30 | 90 | 4.33 | 1.27 |
| swing uniforme + regiones | como25 | 30 | 78 | 5.31 | 1.46 |
| swing uniforme + regiones | twitter | 30 | 46 | 6.11 | 2.13 |

## 2023p → 2023b

Error absoluto medio del margen:

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | 1.21 | 0.82 | 0.55 | 1.15 | 0.80 | 0.56 | 1.57 | 1.10 | 0.74 | 1.63 | 1.12 | 0.77 |
| Goodman lam=0,1 + AMBA/resto | 1.23 | 0.83 | 0.55 | 1.17 | 0.80 | 0.57 | 1.61 | 1.10 | 0.75 | 1.90 | 1.30 | 0.91 |
| Goodman lam=0,1 + regiones | 1.29 | 0.84 | 0.56 | 1.17 | 0.80 | 0.56 | 1.65 | 1.09 | 0.77 | 1.74 | 1.32 | 0.93 |
| Goodman lam=0,3 | 1.34 | 0.91 | 0.60 | 1.25 | 0.88 | 0.61 | 1.74 | 1.25 | 0.87 | 1.89 | 1.25 | 0.86 |
| swing uniforme | 1.74 | 1.17 | 0.73 | 1.60 | 1.09 | 0.77 | 2.28 | 1.73 | 1.23 | 2.70 | 1.82 | 1.32 |
| swing uniforme + regiones | 1.82 | 1.18 | 0.77 | 1.61 | 1.07 | 0.76 | 2.63 | 1.80 | 1.22 | 2.81 | 1.92 | 1.40 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | -0.07 | -0.04 | -0.11 | -0.02 | -0.05 | -0.05 | -0.28 | -0.12 | -0.04 | -0.79 | -0.59 | -0.34 |
| Goodman lam=0,1 + AMBA/resto | -0.07 | -0.04 | -0.12 | -0.00 | -0.03 | -0.04 | -0.27 | -0.12 | -0.04 | -0.34 | -0.18 | +0.02 |
| Goodman lam=0,1 + regiones | -0.05 | -0.04 | -0.11 | -0.03 | -0.11 | -0.04 | -0.22 | -0.05 | -0.03 | -0.40 | -0.20 | +0.02 |
| Goodman lam=0,3 | -0.11 | -0.11 | -0.17 | -0.12 | -0.09 | -0.10 | -0.35 | -0.18 | -0.09 | -0.85 | -0.66 | -0.32 |
| swing uniforme | +0.07 | -0.00 | -0.03 | -0.08 | +0.05 | +0.06 | -0.20 | -0.02 | +0.06 | -0.91 | -0.77 | -0.27 |
| swing uniforme + regiones | +0.12 | -0.02 | -0.03 | -0.17 | -0.08 | +0.09 | -0.07 | +0.13 | +0.01 | -0.31 | -0.00 | +0.24 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 25 | 91 | 2.65 | 1.17 |
| Goodman lam=0,1 | azar | 50 | 92 | 1.82 | 1.18 |
| Goodman lam=0,1 | azar | 100 | 94 | 1.31 | 0.97 |
| Goodman lam=0,1 | estrat | 25 | 91 | 2.54 | 1.12 |
| Goodman lam=0,1 | estrat | 50 | 94 | 1.86 | 0.98 |
| Goodman lam=0,1 | estrat | 100 | 94 | 1.33 | 1.00 |
| Goodman lam=0,1 | racimos | 25 | 88 | 3.54 | 1.14 |
| Goodman lam=0,1 | racimos | 50 | 86 | 2.33 | 1.28 |
| Goodman lam=0,1 | racimos | 100 | 92 | 1.63 | 1.16 |
| Goodman lam=0,1 | twitter | 25 | 80 | 3.23 | 1.24 |
| Goodman lam=0,1 | twitter | 50 | 87 | 2.28 | 1.22 |
| Goodman lam=0,1 | twitter | 100 | 87 | 1.62 | 1.20 |
| Goodman lam=0,1 + AMBA/resto | azar | 25 | 88 | 2.64 | 1.21 |
| Goodman lam=0,1 + AMBA/resto | azar | 50 | 92 | 1.82 | 1.13 |
| Goodman lam=0,1 + AMBA/resto | azar | 100 | 94 | 1.32 | 1.06 |
| Goodman lam=0,1 + AMBA/resto | estrat | 25 | 89 | 2.52 | 1.23 |
| Goodman lam=0,1 + AMBA/resto | estrat | 50 | 96 | 1.90 | 0.97 |
| Goodman lam=0,1 + AMBA/resto | estrat | 100 | 92 | 1.32 | 0.96 |
| Goodman lam=0,1 + AMBA/resto | racimos | 25 | 84 | 3.42 | 1.38 |
| Goodman lam=0,1 + AMBA/resto | racimos | 50 | 86 | 2.38 | 1.20 |
| Goodman lam=0,1 + AMBA/resto | racimos | 100 | 90 | 1.63 | 1.22 |
| Goodman lam=0,1 + AMBA/resto | twitter | 25 | 82 | 3.76 | 1.42 |
| Goodman lam=0,1 + AMBA/resto | twitter | 50 | 89 | 2.81 | 1.20 |
| Goodman lam=0,1 + AMBA/resto | twitter | 100 | 91 | 1.95 | 1.15 |
| swing uniforme + regiones | azar | 25 | 87 | 3.71 | 1.29 |
| swing uniforme + regiones | azar | 50 | 90 | 2.57 | 1.26 |
| swing uniforme + regiones | azar | 100 | 96 | 1.86 | 0.96 |
| swing uniforme + regiones | estrat | 25 | 92 | 3.73 | 1.10 |
| swing uniforme + regiones | estrat | 50 | 94 | 2.59 | 1.07 |
| swing uniforme + regiones | estrat | 100 | 94 | 1.81 | 1.04 |
| swing uniforme + regiones | racimos | 25 | 84 | 4.98 | 1.39 |
| swing uniforme + regiones | racimos | 50 | 86 | 3.86 | 1.26 |
| swing uniforme + regiones | racimos | 100 | 93 | 2.68 | 1.06 |
| swing uniforme + regiones | twitter | 25 | 82 | 4.99 | 1.46 |
| swing uniforme + regiones | twitter | 50 | 88 | 3.74 | 1.36 |
| swing uniforme + regiones | twitter | 100 | 93 | 2.91 | 1.14 |

## 2023p → 2023b → n28 → ancla

Error absoluto medio del margen:

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | 1.08 | 1.42 |
| Prop. lam=0,1 + AMBA/resto | 1.10 | 1.46 |
| Prop. lam=300/n + AMBA/resto | 6.52 | 6.28 |
| Prop. puro + AMBA/resto | 10.87 | 10.59 |
| swing uniforme | 1.57 | 2.93 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | -0.08 | -0.08 |
| Prop. lam=0,1 + AMBA/resto | -0.24 | -0.27 |
| Prop. lam=300/n + AMBA/resto | -6.52 | -6.28 |
| Prop. puro + AMBA/resto | -10.87 | -10.59 |
| swing uniforme | -0.02 | -0.75 |

## 2023p → 2025bl

Error absoluto medio del margen:

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | 2.24 | 1.46 | 1.01 | 1.83 | 1.18 | 0.88 | 3.37 | 2.35 | 1.51 | 3.79 | 2.62 | 2.26 |
| Goodman lam=0,1 + AMBA/resto | 2.21 | 1.46 | 0.98 | 1.82 | 1.21 | 0.87 | 3.40 | 2.32 | 1.51 | 4.28 | 2.74 | 2.04 |
| Goodman lam=0,1 + regiones | 2.21 | 1.46 | 0.97 | 1.85 | 1.22 | 0.85 | 3.34 | 2.40 | 1.61 | 3.70 | 2.62 | 2.04 |
| Goodman lam=0,3 | 2.23 | 1.48 | 1.04 | 1.91 | 1.22 | 0.91 | 3.40 | 2.39 | 1.55 | 3.91 | 2.90 | 2.69 |
| swing uniforme | 2.26 | 1.57 | 1.13 | 2.06 | 1.34 | 0.95 | 3.46 | 2.56 | 1.65 | 4.27 | 3.36 | 3.33 |
| swing uniforme + regiones | 2.30 | 1.48 | 1.04 | 2.04 | 1.36 | 0.92 | 3.54 | 2.56 | 1.79 | 3.81 | 2.64 | 2.16 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 25 | azar 50 | azar 100 | estrat 25 | estrat 50 | estrat 100 | racimos 25 | racimos 50 | racimos 100 | twitter 25 | twitter 50 | twitter 100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Goodman lam=0,1 | -0.02 | -0.13 | -0.08 | +0.50 | -0.00 | +0.39 | +0.39 | +0.45 | +0.22 | +2.54 | +1.91 | +2.02 |
| Goodman lam=0,1 + AMBA/resto | -0.01 | -0.15 | -0.05 | +0.41 | -0.10 | +0.34 | +0.26 | +0.37 | +0.17 | +0.74 | +0.04 | +0.11 |
| Goodman lam=0,1 + regiones | +0.17 | -0.17 | -0.04 | +0.48 | +0.01 | +0.26 | +0.77 | +0.54 | +0.14 | +1.65 | +0.52 | +0.41 |
| Goodman lam=0,3 | +0.07 | -0.07 | -0.02 | +0.53 | +0.01 | +0.40 | +0.46 | +0.46 | +0.22 | +3.14 | +2.49 | +2.59 |
| swing uniforme | +0.07 | -0.11 | -0.06 | +0.42 | -0.11 | +0.26 | +0.43 | +0.30 | +0.05 | +3.78 | +3.11 | +3.28 |
| swing uniforme + regiones | +0.36 | -0.17 | +0.02 | +0.40 | -0.10 | +0.10 | +1.02 | +0.53 | +0.07 | +1.97 | +0.63 | +0.43 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 25 | 90 | 4.90 | 1.24 |
| Goodman lam=0,1 | azar | 50 | 90 | 3.37 | 1.09 |
| Goodman lam=0,1 | azar | 100 | 92 | 2.54 | 1.15 |
| Goodman lam=0,1 | estrat | 25 | 96 | 5.16 | 0.93 |
| Goodman lam=0,1 | estrat | 50 | 95 | 3.40 | 1.00 |
| Goodman lam=0,1 | estrat | 100 | 96 | 2.44 | 0.87 |
| Goodman lam=0,1 | racimos | 25 | 84 | 6.18 | 1.43 |
| Goodman lam=0,1 | racimos | 50 | 90 | 4.74 | 1.33 |
| Goodman lam=0,1 | racimos | 100 | 93 | 3.38 | 1.04 |
| Goodman lam=0,1 | twitter | 25 | 71 | 5.34 | 1.88 |
| Goodman lam=0,1 | twitter | 50 | 78 | 4.45 | 1.57 |
| Goodman lam=0,1 | twitter | 100 | 70 | 3.21 | 1.80 |
| Goodman lam=0,1 + AMBA/resto | azar | 25 | 88 | 4.87 | 1.28 |
| Goodman lam=0,1 + AMBA/resto | azar | 50 | 92 | 3.36 | 1.04 |
| Goodman lam=0,1 + AMBA/resto | azar | 100 | 90 | 2.48 | 1.11 |
| Goodman lam=0,1 + AMBA/resto | estrat | 25 | 96 | 5.16 | 0.95 |
| Goodman lam=0,1 + AMBA/resto | estrat | 50 | 95 | 3.33 | 0.89 |
| Goodman lam=0,1 + AMBA/resto | estrat | 100 | 96 | 2.44 | 0.94 |
| Goodman lam=0,1 + AMBA/resto | racimos | 25 | 86 | 6.31 | 1.39 |
| Goodman lam=0,1 + AMBA/resto | racimos | 50 | 86 | 4.71 | 1.29 |
| Goodman lam=0,1 + AMBA/resto | racimos | 100 | 92 | 3.35 | 1.00 |
| Goodman lam=0,1 + AMBA/resto | twitter | 25 | 76 | 6.77 | 1.84 |
| Goodman lam=0,1 + AMBA/resto | twitter | 50 | 88 | 5.56 | 1.43 |
| Goodman lam=0,1 + AMBA/resto | twitter | 100 | 88 | 4.21 | 1.34 |
| swing uniforme + regiones | azar | 25 | 87 | 4.94 | 1.32 |
| swing uniforme + regiones | azar | 50 | 90 | 3.53 | 1.08 |
| swing uniforme + regiones | azar | 100 | 92 | 2.60 | 1.06 |
| swing uniforme + regiones | estrat | 25 | 94 | 5.17 | 1.02 |
| swing uniforme + regiones | estrat | 50 | 96 | 3.62 | 0.91 |
| swing uniforme + regiones | estrat | 100 | 94 | 2.56 | 0.97 |
| swing uniforme + regiones | racimos | 25 | 84 | 6.13 | 1.42 |
| swing uniforme + regiones | racimos | 50 | 87 | 4.93 | 1.35 |
| swing uniforme + regiones | racimos | 100 | 92 | 3.53 | 1.20 |
| swing uniforme + regiones | twitter | 25 | 74 | 5.83 | 1.76 |
| swing uniforme + regiones | twitter | 50 | 80 | 4.75 | 1.43 |
| swing uniforme + regiones | twitter | 100 | 84 | 3.94 | 1.39 |

## 2023p → 2025bl → n28 → ancla

Error absoluto medio del margen:

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | 1.91 | 2.87 |
| Prop. lam=0,1 + AMBA/resto | 1.88 | 2.79 |
| Prop. lam=300/n + AMBA/resto | 2.28 | 2.45 |
| Prop. puro + AMBA/resto | 3.31 | 3.17 |
| swing uniforme | 2.09 | 4.12 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 28 | como25 28 |
|---|---:|---:|
| Goodman lam=0,1 + AMBA/resto | +0.04 | -0.11 |
| Prop. lam=0,1 + AMBA/resto | +0.09 | -0.05 |
| Prop. lam=300/n + AMBA/resto | +2.21 | +2.08 |
| Prop. puro + AMBA/resto | +3.31 | +3.14 |
| swing uniforme | +0.04 | +3.63 |

## 2023p → 2025bl → n30

Error absoluto medio del margen:

| Método | azar 30 | como25 30 | twitter 30 |
|---|---:|---:|---:|
| Goodman lam=0,1 | 1.93 | 2.77 | 3.08 |
| Goodman lam=0,1 + AMBA/resto | 1.93 | 2.77 | 3.39 |
| Goodman lam=0,1 + regiones | 2.02 | 2.80 | 3.18 |
| Goodman lam=0,3 | 1.94 | 3.13 | 3.20 |
| swing uniforme | 2.01 | 3.93 | 3.56 |
| swing uniforme + regiones | 2.08 | 2.92 | 3.33 |

Sesgo medio del margen (signo +: sobrestima al primero):

| Método | azar 30 | como25 30 | twitter 30 |
|---|---:|---:|---:|
| Goodman lam=0,1 | -0.01 | +1.99 | +1.98 |
| Goodman lam=0,1 + AMBA/resto | +0.03 | +0.04 | +0.51 |
| Goodman lam=0,1 + regiones | +0.09 | +0.37 | +1.31 |
| Goodman lam=0,3 | +0.07 | +2.67 | +2.46 |
| swing uniforme | +0.07 | +3.55 | +2.95 |
| swing uniforme + regiones | +0.26 | +0.64 | +1.59 |

Banda del 95 % (bootstrap de circuitos):

| Método | esquema | n | cobertura % | semiancho medio | factor |
|---|---|---:|---:|---:|---:|
| Goodman lam=0,1 | azar | 30 | 91 | 4.41 | 1.10 |
| Goodman lam=0,1 | como25 | 30 | 81 | 4.97 | 1.61 |
| Goodman lam=0,1 | twitter | 30 | 75 | 5.46 | 1.71 |
| Goodman lam=0,1 + AMBA/resto | azar | 30 | 92 | 4.39 | 1.11 |
| Goodman lam=0,1 + AMBA/resto | como25 | 30 | 84 | 5.61 | 1.38 |
| Goodman lam=0,1 + AMBA/resto | twitter | 30 | 83 | 6.52 | 1.61 |
| swing uniforme + regiones | azar | 30 | 90 | 4.48 | 1.21 |
| swing uniforme + regiones | como25 | 30 | 84 | 5.29 | 1.52 |
| swing uniforme + regiones | twitter | 30 | 75 | 5.53 | 1.62 |
