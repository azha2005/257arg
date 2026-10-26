# Buenos Aires: presidente 1983 → diputados 1985

[Abrir el gráfico provincial](sankey_1983p_1985d.html#02) | [PNG](PBA_1983p_1985d.png)

Se conservaron **125 partidos** y el **100.00 % del voto desglosado de origen**. No incluye abstención.

Se distingue PJ de peronismo renovador en 1985. La tabla compara el modelo principal provincial ponderado y penalizado hacia el nacional con una matriz ajustada solo en PBA, sin ponderación y con penalización 0,001, siguiendo la especificación de Calvo. Esta segunda matriz es provincial; no es la variante nacional de `calvo_nacional.csv`.

| Origen 1983 | Destino 1985 | Principal % | Calvo provincial % | Bootstrap principal 5–95 % |
|---|---|---:|---:|---:|
| UCR (Alfonsín) | UCR | 72.6 | 75.8 | 68.4–76.4 |
| UCR (Alfonsín) | PJ | 0.2 | 0.6 | 0.1–0.5 |
| UCR (Alfonsín) | Peronismo renovador | 9.7 | 11.6 | 5.7–13.5 |
| UCR (Alfonsín) | PI | 5.4 | 1.7 | 2.4–8.2 |
| PJ (Luder) | UCR | 7.3 | 7.9 | 2.4–11.0 |
| PJ (Luder) | PJ | 23.1 | 20.8 | 20.7–24.9 |
| PJ (Luder) | Peronismo renovador | 47.4 | 50.2 | 42.8–54.8 |
| PJ (Luder) | PI | 9.8 | 9.0 | 6.3–13.3 |

Diagnóstico interno en PBA: RMSE 2.23 puntos frente a 3.05 del promedio provincial de entrenamiento; mejora del 27.0 %.

El bootstrap provincial remuestrea 200 veces los partidos y mantiene fijo el centro nacional. No incluye la incertidumbre del centro, de las fuentes o de las correspondencias. Las diferencias entre variantes pueden ser mayores que sus intervalos. Los porcentajes describen una inferencia territorial y no identifican cambios individuales de voto.

[Comparación completa e intervalos](PBA_comparacion_modelos.csv), [control](PBA_control.json), [reservas del cruce nacional](RESUMEN.md).
