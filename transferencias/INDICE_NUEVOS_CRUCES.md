# Cruces solicitados: índice y verificación

Cada HTML incluye una vista conjunta y selector provincial. 1914d→1916d tiene cobertura parcial de siete jurisdicciones. Los cruces con 1987d tienen 23 distritos porque Tierra del Fuego no votó; 1983p/1985d→1989p excluyen ese distrito por el filtro de crecimiento; 1997d tiene 23 porque falta San Luis; 1999p tiene 22 porque faltan San Luis y Santa Cruz. Los demás tienen 24. Las cintas muestran votos y porcentajes al pasar el cursor.

| Par | Gráfico | Resumen y reservas | Unidades | Cobertura origen |
|---|---|---|---:|---:|
| 2013_2017 | [HTML](2013_2017/sankey_2013_2017.html) | [Resumen](2013_2017/RESUMEN.md) | 4593 | 96.41 % |
| 2015p_2023p | [HTML](2015p_2023p/sankey_2015p_2023p.html) | [Resumen](2015p_2023p/RESUMEN.md) | 4306 | 91.24 % |
| 2015p_2023b | [HTML](2015p_2023b/sankey_2015p_2023b.html) | [Resumen](2015p_2023b/RESUMEN.md) | 4314 | 91.18 % |
| 2015b_2023p | [HTML](2015b_2023p/sankey_2015b_2023p.html) | [Resumen](2015b_2023p/RESUMEN.md) | 4428 | 91.95 % |
| 2015b_2023b | [HTML](2015b_2023b/sankey_2015b_2023b.html) | [Resumen](2015b_2023b/RESUMEN.md) | 4446 | 92.11 % |
| 2013_2015p | [HTML](2013_2015p/sankey_2013_2015p.html) | [Resumen](2013_2015p/RESUMEN.md) | 4878 | 97.64 % |
| 2013_2015b | [HTML](2013_2015b/sankey_2013_2015b.html) | [Resumen](2013_2015b/RESUMEN.md) | 4963 | 98.05 % |
| 2009_2015p | [HTML](2009_2015p/sankey_2009_2015p.html) | [Resumen](2009_2015p/RESUMEN.md) | 4208 | 92.53 % |
| 2009_2015b | [HTML](2009_2015b/sankey_2009_2015b.html) | [Resumen](2009_2015b/RESUMEN.md) | 4294 | 93.17 % |
| 2017_2019p | [HTML](2017_2019p/sankey_2017_2019p.html) | [Resumen](2017_2019p/RESUMEN.md) | 5242 | 97.95 % |
| 2017_2019 | [HTML](2017_2019/sankey_2017_2019.html) | [Resumen](2017_2019/RESUMEN.md) | 5233 | 97.95 % |
| 2015p_2019p | [HTML](2015p_2019p/sankey_2015p_2019p.html) | [Resumen](2015p_2019p/RESUMEN.md) | 4829 | 96.40 % |
| 2015b_2019p | [HTML](2015b_2019p/sankey_2015b_2019p.html) | [Resumen](2015b_2019p/RESUMEN.md) | 4968 | 96.94 % |
| 1989p_1995p | [HTML](1989p_1995p/sankey_1989p_1995p.html) | [Resumen](1989p_1995p/RESUMEN.md) | 503 | 97.13 % |
| 1989d_1994c | [HTML](1989d_1994c/sankey_1989d_1994c.html) | [Resumen](1989d_1994c/RESUMEN.md) | 514 | 99.53 % |
| 1985d_1987d | [HTML](1985d_1987d/sankey_1985d_1987d.html) | [Resumen](1985d_1987d/RESUMEN.md) | 507 | 96.44 % |
| 1983p_1989p | [HTML](1983p_1989p/sankey_1983p_1989p.html) | [Resumen](1983p_1989p/RESUMEN.md) | 501 | 98.73 % |
| 1987d_1989p | [HTML](1987d_1989p/sankey_1987d_1989p.html) | [Resumen](1987d_1989p/RESUMEN.md) | 508 | 97.75 % |
| 1985d_1989p | [HTML](1985d_1989p/sankey_1985d_1989p.html) | [Resumen](1985d_1989p/RESUMEN.md) | 506 | 98.86 % |
| 1989p_1997d | [HTML](1989p_1997d/sankey_1989p_1997d.html) | [Resumen](1989p_1997d/RESUMEN.md) | 497 | 98.02 % |
| 1995p_1997d | [HTML](1995p_1997d/sankey_1995p_1997d.html) | [Resumen](1995p_1997d/RESUMEN.md) | 517 | 97.07 % |
| 1995p_1999p | [HTML](1995p_1999p/sankey_1995p_1999p.html) | [Resumen](1995p_1999p/RESUMEN.md) | 506 | 96.59 % |
| 1983p_1985d | [HTML](1983p_1985d/sankey_1983p_1985d.html) | [Resumen](1983p_1985d/RESUMEN.md) | 519 | 99.33 % |
| 1914d_1916d | [HTML](1914d_1916d/sankey_1914d_1916d.html) | [Resumen](1914d_1916d/RESUMEN.md) | 130 | 70.40 % |

Verificación: matrices no negativas, conservación de totales al redondeo, intervalos ordenados, destinos ausentes en cero, correspondencias conservando categorías, 575 vistas con porcentajes cotejados contra CSV, enlaces directos por provincia y ausencia de errores JavaScript.

[Fuentes y pendientes de correspondencias](correspondencias_2013_2017/LEEME.md). `p`: general presidencial; `b`: balotaje; `d`: diputados; `1994c`: constituyentes. 2009, 2013 y 2017 sin sufijo: diputados nacionales.

Los cruces históricos usan votos desglosados y no incluyen abstención: [fuentes, extrapolación y utilidad](historicos_1989/LEEME.md). Su cobertura no es cobertura del padrón.

[PBA 1983p→1985d: comparación provincial de modelos](1983p_1985d/PBA.md).

[1914–1916: fuentes y cobertura](fuentes_1914_1916/LEEME.md) | [Cacopardo: revisión de los cruces existentes](revision_cacopardo_1967/LEEME.md).

**Brasil 2026, 1.ª vuelta → balotaje**: [HTML](brasil_2026p_2026b/sankey_brasil_2026p_2026b.html) / [sin No votó](brasil_2026p_2026b/sankey_brasil_2026p_2026b_votantes.html) | [Resumen](brasil_2026p_2026b/RESUMEN.md) | 497.147 secciones | 99.62 % del padrón del balotaje. Verificado con `brasil2026_verificar.py` y `brasil2026_revisar_html.py` (29 vistas por gráfico).
