# Transferencias 1995p → 1997d

Estimaciones ecológicas, no observaciones de cambios individuales de voto.

[Abrir gráfico con selector provincial](sankey_1995p_1997d.html) | [PNG](sankey_1995p_1997d.png)

Base usada: 0 circuitos, 0 grupos y 517 departamentos.
Cobertura de los votos desglosados de origen: **97,07 %** (17,637,440 de 18,169,065).
Penalización elegida por validación cruzada: 2e-05; separación: 33.5 puntos.

Filas no identificadas: Otros, Blanco y nulo.
Filas cerca del promedio: ninguna.
Sensibilidad principal / Calvo: cambian 4,277,878 votos (23,86 % del total modelado).
El bootstrap no mide toda esta sensibilidad a la especificación.

[Correspondencias y fuentes documentales](../historicos_1989/LEEME.md). Departamentos sin fusiones ajenas al par; votos desglosados, sin abstención. Deseado 1995 extrapolado por autorización previa; sin otras imputaciones. Ver historicos_1989/LEEME.md.

[Matriz porcentual](matriz_pct.csv), [votos estimados](matriz_votos.csv), [intervalos](intervalos.csv), [variante Calvo](calvo_nacional.csv), [matriz provincial](por_provincia.csv), [unidades usadas](unidades_utilizadas.csv), [transformaciones](correspondencias.csv), [control completo](control.json).

Alertas provinciales de la auditoría: [{"distrito": "22", "destino": "Otros", "estimado": 5496, "real": 2490}].

No incluye abstención. Las unidades incluyen circunscripciones de Capital y uniones territoriales completas. Las exclusiones por calidad están en control.json.

San Luis no tiene datos departamentales de diputados 1997 en la base: queda fuera del ajuste y del selector; no se distribuye el total provincial. Hay 23 distritos.

Diagnóstico interno: mejora del error frente al promedio provincial 31.5 %. [Detalles y utilidad](../historicos_1989/LEEME.md), [diagnóstico](diagnostico.json).
