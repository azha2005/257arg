# Capital Federal: diputados 1914 → diputados 1916

[Abrir gráfico provincial](sankey_1914d_1916d.html#01) | [PNG](Capital_1914_1916.png)

**20 unidades utilizadas**. Cobertura del voto de la selección legible y completa de 1914: **100.0 %**. No es cobertura provincial total ni cobertura del padrón.

Solo cifras observadas. No se añaden ceros para reemplazar lecturas dudosas. La matriz Calvo provincial se ajusta solo con estas unidades, sin pesos y con penalización 0,001; es distinta de la variante nacional de Calvo.

| Origen | Destino | Principal % | Calvo provincial % | Bootstrap principal 5–95 % |
|---|---|---:|---:|---:|
| UCR | Socialistas | 0.8 | 8.5 | 0.6–1.6 |
| UCR | PDP | 1.2 | 7.0 | 1.0–1.8 |
| UCR | Socialista Argentino | 16.3 | 28.2 | 5.1–21.7 |
| UCR | UCR | 81.8 | 56.3 | 76.1–92.4 |
| Conservadores | Socialistas | 1.5 | 11.9 | 1.1–3.3 |
| Conservadores | PDP | 3.9 | 14.8 | 2.3–13.8 |
| Conservadores | Socialista Argentino | 8.3 | 35.8 | 2.0–33.8 |
| Conservadores | UCR | 86.3 | 37.5 | 61.7–92.0 |
| Socialistas | Socialistas | 71.8 | 61.4 | 67.0–74.9 |
| Socialistas | PDP | 3.0 | 3.8 | 1.2–5.0 |
| Socialistas | Socialista Argentino | 23.1 | 12.0 | 20.5–27.8 |
| Socialistas | UCR | 2.0 | 22.9 | 1.2–3.1 |
| Unión Cívica | Socialistas | 7.5 | 8.6 | 1.3–12.8 |
| Unión Cívica | PDP | 40.8 | 23.5 | 34.2–45.9 |
| Unión Cívica | Socialista Argentino | 44.4 | 26.2 | 33.2–58.0 |
| Unión Cívica | UCR | 7.3 | 41.7 | 1.5–22.1 |

RMSE interno: 1.87 puntos, frente a 3.32 del promedio provincial de entrenamiento.

Filas inestables entre las dos especificaciones provinciales: Conservadores, Unión Cívica.

Sensibilidad a fuentes y selección:

| Variante | Unidades | Mayor cambio por celda en filas presentes |
|---|---:|---:|
| lecturas_Lupu | 20 | 2.6 puntos |
| sin_filtro_crecimiento | 20 | 3.7 puntos |
| Lupu_sin_filtro | 20 | 5.8 puntos |

Los intervalos remuestrean 200 veces las unidades y mantienen fijo el centro nacional. No cubren toda la incertidumbre de fuentes, agregación, selección o modelo. Las transferencias son inferencias sobre territorios, no seguimiento individual.

[CSV completo](Capital_comparacion.csv), [sensibilidad por provincia](sensibilidad_provincial.csv), [fuentes y límites](../fuentes_1914_1916/LEEME.md).
