# Proyección con 29 actas (27 circuitos) — origen 2023p,2021bl

Modelo: Goodman encogido al swing (λ = 0.1) con repesado AMBA / resto por fuerza observada; banda nominal del 95 % por bootstrap de circuitos × 1.4; promedio de los orígenes 2023p y 2021bl.

| Fuerza | Proyección | Banda 95 % | Suma cruda de las actas | Swing uniforme | Solo 2023p | Solo 2021bl |
|---|---:|---:|---:|---:|---:|---:|
| LLA | **41.7** | 37.6–45.8 | 45.7 | 40.9 | 42.4 | 41.9 |
| FP | **32.4** | 27.4–36.4 | 31.8 | 34.3 | 34.8 | 31.6 |
| PU | **9.5** | 6.6–12.8 | 9.6 | 9.5 | 8.3 | 9.0 |
| FIT | **4.0** | 3.2–4.8 | 3.0 | 3.8 | 3.9 | 4.3 |
| OTRAS | **12.4** | 9.0–16.8 | 9.9 | 11.5 | 10.5 | 13.2 |

Margen LLA − FP: **+9.3** puntos (banda +1.5 a +17.1). Frecuencia de primer puesto en las remuestras para LLA: 99.7 %.

El nacional proyectado y las bancas salen de las mismas realizaciones por distrito, con corrección provincial. Las columnas de swing y de cada origen son referencias sin esa corrección.


## Soporte por fuerza

| Fuerza | Actas | Circuitos | Actas efectivas por pesos | Peso AMBA |
|---|---:|---:|---:|---:|
| LLA | 29 | 27 | 26.3 | 29.2 % |
| FP | 29 | 27 | 26.3 | 29.2 % |
| PU | 29 | 27 | 26.3 | 29.2 % |
| FIT | 29 | 27 | 26.3 | 29.2 % |
| OTRAS | 28 | 26 | 25.6 | 29.2 % |

El tamaño efectivo mostrado mide la desigualdad de pesos, no la independencia entre fotos. Los circuitos se remuestrean juntos.
## De dónde vienen las actas

| Región | % del padrón | actas |
|---|---:|---:|
| AMBA | 29 | 5 |
| Centro | 20 | 7 |
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
| FP | 33.6 | 32.4 | -1.2 |
| PU | 7.7 | 9.5 | +1.8 |
| FIT | 3.9 | 4.0 | +0.1 |
| OTRAS | 14.2 | 12.4 | -1.8 |
| Margen LLA − FP | +7.1 | +9.3 | +2.2 |

## Diputados 2025 (127 bancas)

| Fuerza | Bancas | Banda 90 % | Real | Cámara |
|---|---:|---:|---:|---:|
| FIT-Unidad | 2 | 1–3 | 3 | 3 |
| Fuerza Patria | 46 | 40–51 | 47 | 98 |
| Provinciales y otras | 5 | 3–10 | 5 | 5 |
| Provincias Unidas | 11 | 6–14 | 8 | 11 |
| La Libertad Avanza | 63 | 57–69 | 64 | 96 |

HTML con los hemiciclos, el mapa y las tablas: `actas_sin_cordoba_5023_congreso.html`
