# Buenos Aires: diputados 1914 → diputados 1916

[Abrir gráfico provincial](sankey_1914d_1916d.html#02) | [PNG](PBA_1914_1916.png)

**71 unidades utilizadas**. Cobertura del voto de la selección legible y completa de 1914: **72.5 %**. No es cobertura provincial total ni cobertura del padrón.

Solo cifras observadas. No se añaden ceros para reemplazar lecturas dudosas. La matriz Calvo provincial se ajusta solo con estas unidades, sin pesos y con penalización 0,001; es distinta de la variante nacional de Calvo.

| Origen | Destino | Principal % | Calvo provincial % | Bootstrap principal 5–95 % |
|---|---|---:|---:|---:|
| UCR | Conservadores | 29.5 | 28.1 | 21.2–37.5 |
| UCR | Socialistas | 1.0 | 1.8 | 0.8–1.4 |
| UCR | UCR | 69.6 | 70.2 | 61.6–77.8 |
| Conservadores | Conservadores | 73.3 | 76.9 | 66.2–81.2 |
| Conservadores | Socialistas | 0.8 | 1.2 | 0.6–1.2 |
| Conservadores | UCR | 25.9 | 21.8 | 18.2–32.7 |
| Socialistas | Conservadores | 24.0 | 14.5 | 4.0–42.7 |
| Socialistas | Socialistas | 49.0 | 34.2 | 36.8–58.0 |
| Socialistas | UCR | 27.0 | 51.3 | 12.3–51.6 |

RMSE interno: 5.44 puntos, frente a 6.50 del promedio provincial de entrenamiento.

Filas inestables entre las dos especificaciones provinciales: ninguna con el umbral de la auditoría.

Sensibilidad a fuentes y selección:

| Variante | Unidades | Mayor cambio por celda en filas presentes |
|---|---:|---:|
| lecturas_Lupu | 81 | 1.4 puntos |
| sin_filtro_crecimiento | 86 | 2.5 puntos |
| Lupu_sin_filtro | 98 | 3.2 puntos |

Los intervalos remuestrean 200 veces las unidades y mantienen fijo el centro nacional. No cubren toda la incertidumbre de fuentes, agregación, selección o modelo. Las transferencias son inferencias sobre territorios, no seguimiento individual.

[CSV completo](PBA_comparacion.csv), [sensibilidad por provincia](sensibilidad_provincial.csv), [fuentes y límites](../fuentes_1914_1916/LEEME.md).
