# Proyección con 30 actas (28 circuitos) — origen 2023p,2021bl

Modelo: Goodman encogido al swing (λ = 0.1) con repesado AMBA / resto por fuerza observada; banda nominal del 95 % por bootstrap de circuitos × 1.4; promedio de los orígenes 2023p y 2021bl.

| Fuerza | Proyección | Banda 95 % | Suma cruda de las actas | Swing uniforme | Solo 2023p | Solo 2021bl |
|---|---:|---:|---:|---:|---:|---:|
| LLA | **41.7** | 37.1–45.5 | 45.8 | 40.7 | 42.5 | 41.8 |
| FP | **32.2** | 27.8–36.5 | 30.8 | 34.1 | 34.5 | 31.5 |
| PU | **9.6** | 7.1–12.7 | 10.3 | 9.5 | 8.3 | 8.9 |
| FIT | **4.0** | 3.2–4.8 | 2.9 | 3.8 | 3.9 | 4.3 |
| OTRAS | **12.6** | 9.3–17.5 | 10.2 | 11.8 | 10.7 | 13.5 |

Margen LLA − FP: **+9.5** puntos (banda +2.1 a +17.2). Frecuencia de primer puesto en las remuestras para LLA: 98.7 %.

El nacional proyectado y las bancas salen de las mismas realizaciones por distrito, con corrección provincial. Las columnas de swing y de cada origen son referencias sin esa corrección.


## Soporte por fuerza

| Fuerza | Actas | Circuitos | Actas efectivas por pesos | Peso AMBA |
|---|---:|---:|---:|---:|
| LLA | 30 | 28 | 26.9 | 29.2 % |
| FP | 30 | 28 | 26.9 | 29.2 % |
| PU | 30 | 28 | 26.9 | 29.2 % |
| FIT | 30 | 28 | 26.9 | 29.2 % |
| OTRAS | 29 | 27 | 26.3 | 29.2 % |

El tamaño efectivo mostrado mide la desigualdad de pesos, no la independencia entre fotos. Los circuitos se remuestrean juntos.
## De dónde vienen las actas

| Región | % del padrón | actas |
|---|---:|---:|
| AMBA | 29 | 5 |
| Centro | 20 | 8 |
| Buenos Aires interior | 15 | 5 |
| NOA | 13 | 4 |
| NEA | 10 | 4 |
| Cuyo | 7 | 1 |
| Patagonia | 7 | 3 |

- 17 % de las actas son del AMBA (el AMBA es el 29 % del padrón); están repesadas.
- 1 actas incompletas (solo algunas fuerzas): cuentan para esas fuerzas.
- 1 actas sin circuito reconocido: se comparan con su sección.
- Respaldo del universo en 2023p: {'circuito': 5633, 'seccion': 171}
- Respaldo del universo en 2021bl: {'circuito': 5082, 'seccion': 658, 'distrito': 64}

Validación del procedimiento corregido: `validacion_20261028/RESULTADOS.md`. Las bandas son condicionales al modelo y al esquema de muestreo; el bootstrap no identifica selección por cambio no observado.

## Contra el resultado real (2025bl)

| Fuerza | Real | Proyección | Error |
|---|---:|---:|---:|
| LLA | 40.7 | 41.7 | +1.0 |
| FP | 33.6 | 32.2 | -1.4 |
| PU | 7.7 | 9.6 | +1.9 |
| FIT | 3.9 | 4.0 | +0.1 |
| OTRAS | 14.2 | 12.6 | -1.5 |
| Margen LLA − FP | +7.1 | +9.5 | +2.4 |

## Diputados 2025 (127 bancas)

| Fuerza | Bancas | Banda 90 % | Real | Cámara |
|---|---:|---:|---:|---:|
| FIT-Unidad | 3 | 1–3 | 3 | 4 |
| Fuerza Patria | 46 | 40–51 | 47 | 98 |
| Provinciales y otras | 5 | 3–11 | 5 | 5 |
| Provincias Unidas | 10 | 6–14 | 8 | 10 |
| La Libertad Avanza | 63 | 57–69 | 64 | 96 |

HTML con los hemiciclos, el mapa y las tablas: `actas_congreso.html`
