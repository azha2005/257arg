# Transferencias 1995p → 1999p

Estimaciones ecológicas, no observaciones de cambios individuales de voto.

[Abrir gráfico con selector provincial](sankey_1995p_1999p.html) | [PNG](sankey_1995p_1999p.png)

Base usada: 0 circuitos, 0 grupos y 506 departamentos.
Cobertura de los votos desglosados de origen: **96,59 %** (17,550,247 de 18,169,065).
Penalización elegida por validación cruzada: 2e-05; separación: 35.8 puntos.

Filas no identificadas: Otros, Blanco y nulo.
Filas cerca del promedio: ninguna.
Sensibilidad principal / Calvo: cambian 2,308,143 votos (12,05 % del total modelado).
El bootstrap no mide toda esta sensibilidad a la especificación.

[Correspondencias y fuentes documentales](../historicos_1989/LEEME.md). Departamentos sin fusiones ajenas al par; votos desglosados, sin abstención. Deseado 1995 extrapolado por autorización previa; sin otras imputaciones. Ver historicos_1989/LEEME.md.

[Matriz porcentual](matriz_pct.csv), [votos estimados](matriz_votos.csv), [intervalos](intervalos.csv), [variante Calvo](calvo_nacional.csv), [matriz provincial](por_provincia.csv), [unidades usadas](unidades_utilizadas.csv), [transformaciones](correspondencias.csv), [control completo](control.json).

Alertas provinciales de la auditoría: [{"distrito": "06", "destino": "Blanco y nulo", "estimado": 12716, "real": 7808}, {"distrito": "14", "destino": "Blanco y nulo", "estimado": 11316, "real": 6103}].

No incluye abstención. Las unidades incluyen circunscripciones de Capital y uniones territoriales completas. Las exclusiones por calidad están en control.json.

La base presidencial 1999 no incluye San Luis ni Santa Cruz. Quedan fuera del ajuste y del selector: 22 distritos. La extrapolación de Deseado 1995 se conserva en la fuente de origen pero esa unidad no interviene en este cruce. No se usó la imputación de fuerzas menores de otras bases del proyecto.

Diagnóstico interno: mejora del error frente al promedio provincial 34.5 %. [Detalles y utilidad](../historicos_1989/LEEME.md), [diagnóstico](diagnostico.json).
