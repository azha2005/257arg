# Transferencias 1983p → 1989p

Estimaciones ecológicas, no observaciones de cambios individuales de voto.

[Abrir gráfico con selector provincial](sankey_1983p_1989p.html) | [PNG](sankey_1983p_1989p.png)

Base usada: 0 circuitos, 0 grupos y 501 departamentos.
Cobertura de los votos desglosados de origen: **98,73 %** (15,155,100 de 15,350,187).
Penalización elegida por validación cruzada: 2e-06; separación: 37.7 puntos.

Filas no identificadas: PI, MID, MOFEPA, Otros.
Filas cerca del promedio: ninguna.
Sensibilidad principal / Calvo: cambian 1,418,428 votos (8,45 % del total modelado).
El bootstrap no mide toda esta sensibilidad a la especificación.

[Correspondencias y fuentes documentales](../historicos_1989/LEEME.md). Departamentos y circunscripciones de Capital; votos desglosados, sin abstención. Sin imputaciones de votos. Uniones completas para cambios territoriales. Ver historicos_1989/LEEME.md.

[Matriz porcentual](matriz_pct.csv), [votos estimados](matriz_votos.csv), [intervalos](intervalos.csv), [variante Calvo](calvo_nacional.csv), [matriz provincial](por_provincia.csv), [unidades usadas](unidades_utilizadas.csv), [transformaciones](correspondencias.csv), [control completo](control.json).

Alertas provinciales de la auditoría: ninguna.

No incluye abstención. Las unidades incluyen circunscripciones de Capital y uniones territoriales completas. Las exclusiones por calidad están en control.json.

Tierra del Fuego queda fuera por superar el filtro común de crecimiento del volumen de votos; no se estima una matriz provincial con esas unidades descartadas. Hay 23 distritos.

Diagnóstico interno: mejora del error frente al promedio provincial 50.5 %. [Detalles y utilidad](../historicos_1989/LEEME.md), [diagnóstico](diagnostico.json).
