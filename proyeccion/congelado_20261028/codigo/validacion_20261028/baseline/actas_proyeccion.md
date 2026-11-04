# Proyección con 27 actas (16 circuitos) — origen 2023p,2021bl

Modelo: Goodman encogido al swing (λ = 0.1) con las actas repesadas AMBA / resto; banda del 95 % por bootstrap de circuitos × 1.4; promedio de los orígenes 2023p y 2021bl.

| Fuerza | Proyección | Banda 95 % | Suma cruda de las actas | Swing uniforme | Solo 2023p | Solo 2021bl |
|---|---:|---:|---:|---:|---:|---:|
| LLA | **43.0** | 39.1–47.6 | 49.1 | 43.6 | 44.9 | 41.1 |
| FP | **35.8** | 32.5–39.0 | 37.7 | 32.9 | 35.9 | 35.7 |
| OTRAS | **11.0** | 7.5–14.7 | 6.8 | 12.1 | 10.1 | 12.0 |
| FIT | **4.9** | 3.8–6.0 | 4.2 | 5.2 | 4.5 | 5.2 |
| PU | **5.3** | 3.0–8.6 | 2.2 | 6.2 | 4.6 | 6.0 |

Margen LLA − FP: **+7.3** puntos (banda +0.7 a +14.5). Probabilidad de que LLA quede primero: 98 %.

## De dónde vienen las actas

| Región | % del padrón | actas |
|---|---:|---:|
| AMBA | 30 | 20 |
| Centro | 20 | 0 |
| Buenos Aires interior | 15 | 2 |
| NOA | 13 | 1 |
| NEA | 9 | 1 |
| Cuyo | 7 | 1 |
| Patagonia | 6 | 2 |

- **Regiones sin actas**: Centro. El modelo les aplica el cambio del resto; las fuerzas fuertes ahí (listas provinciales, PU en Córdoba y Santa Fe) pueden quedar bajas.
- 74 % de las actas son del AMBA (el AMBA es el 29 % del padrón); están repesadas.
- 11 actas incompletas (solo algunas fuerzas): cuentan para esas fuerzas.
- 12 actas sin circuito reconocido: se comparan con su sección.

Error típico del margen con este método (`fotos_sim.py` y `fotos_sim2.py`, 2019/2021 → 2023 y 2021/2023 → 2025), con ~30 actas: 1,9 puntos si son al azar y 2,7–3,1 si están armadas como las de Twitter (2/3 del AMBA y racimos), promediando dos orígenes; con uno solo, 10–20 % más.

## Contra el resultado real (2025bl)

| Fuerza | Real | Proyección | Error |
|---|---:|---:|---:|
| LLA | 40.7 | 43.0 | +2.4 |
| FP | 33.6 | 35.8 | +2.2 |
| OTRAS | 14.2 | 11.0 | -3.1 |
| FIT | 3.9 | 4.9 | +1.0 |
| PU | 7.7 | 5.3 | -2.4 |
| Margen LLA − FP | +7.1 | +7.3 | +0.2 |

## Diputados 2025 (127 bancas)

| Fuerza | Bancas | Banda 90 % | Real | Cámara |
|---|---:|---:|---:|---:|
| FIT-Unidad | 3 | 2–3 | 3 | 4 |
| Fuerza Patria | 49 | 44–53 | 47 | 101 |
| Provinciales y otras | 5 | 3–9 | 5 | 5 |
| Provincias Unidas | 8 | 5–12 | 8 | 8 |
| La Libertad Avanza | 62 | 56–67 | 64 | 95 |

HTML con los hemiciclos, el mapa y las tablas: `actas_congreso.html`
