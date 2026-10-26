# Diputados 1914 → diputados 1916: fuentes y comparabilidad

[Abrir resultado de cobertura parcial](../1914d_1916d/sankey_1914d_1916d.html) | [Buenos Aires](../1914d_1916d/PBA.md) | [Capital Federal](../1914d_1916d/Capital.md).

Es un análisis ecológico de **votos atribuidos a fuerzas o al primer candidato publicado**, no de sufragantes únicos. Con lista incompleta y panachage, sumar primeros candidatos no equivale necesariamente a contar personas. No se incluyen blancos, nulos ni abstención. Tampoco se usan los resultados provinciales sólidos del atlas como observaciones departamentales.

## Qué entra al principal

Se usan las transcripciones originales y las columnas completas. Se excluye cualquier unidad con una cifra partidaria requerida ilegible, vacía o con cómputo explícitamente parcial. Un cero entra únicamente si está transcripto como cero. Se descartan las estimaciones numéricas realizadas para el atlas de 1916 y la inferencia por residuo de Concepción del Uruguay 1914. Santa Fe, cuyos datos 1914 son prensa provisoria/parcial, queda fuera de este principal. No se alteraron las fuentes originales ni los atlas.

La preparación deja 191 unidades completas en origen y 178 en destino dentro de las siete jurisdicciones investigadas. Hay 157 unidades territoriales comunes; el filtro habitual de crecimiento relativo 0,75–1,33 deja **130 unidades**, con **261.739 votos partidarios de origen** y **337.261 de destino**. La cobertura del 70,40 % se refiere a los 371.799 votos de la selección completa y legible de 1914, **no al total nacional ni al total de cada provincia**.

| Jurisdicción | Unidades utilizadas | Cobertura del voto de su selección legible de 1914 |
|---|---:|---:|
| Capital Federal | 20 circunscripciones | 100,0 % |
| Buenos Aires | 71 unidades | 72,5 % |
| Córdoba | 2 departamentos | 26,7 % |
| Corrientes | 14 unidades | 54,1 % |
| Entre Ríos | 5 departamentos | 30,3 % |
| La Rioja | 5 departamentos | 63,0 % |
| Mendoza | 13 unidades | 57,9 % |

Las coberturas provinciales exactas están en el control del par. Córdoba tiene menos de cinco unidades y su vista advierte que no permite identificar una matriz provincial suficiente. Las otras provincias también tienen distintos niveles de selección y no deben leerse como una muestra representativa del país.

## Correspondencias revisadas con Cacopardo

Se leyó `DTS 47_Cacopardo_1967.pdf`, incluyendo las páginas pertinentes completas y el Anexo del Cuadro 1. Las capturas de evidencia están en `cacopardo_paginas/`; la extracción textual sirve para localizar, no para decidir por sí sola las llaves y líneas del cuadro. [Manifiesto con SHA-256 del PDF y de las transcripciones](control_preparacion.json).

El documento describe cambios entre los censos de 1869, 1895, 1914, 1947 y 1960. Su introducción (PDF6, impresa1) dice que no incluye todos los cambios intermedios que no quedaron reflejados entre censos. Por eso no se toma la igualdad de nombre como una certificación absoluta de límites electorales. Para la agregación de votos compartidos se combina Cacopardo con las notas de Cantón, Apéndice C, y con las observaciones de las transcripciones.

- **Necochea, Juárez, Tres Arroyos y González Chaves:** una sola unidad de comparación. El Cuadro 1 (PDF30, impresa25) fecha González Chaves en 1916 y el Anexo (PDF67, impresa64) muestra sus tres partidos de origen. Cantón publica los votos subsumidos en Necochea. Se usa ese dato una vez; no las tres copias de polígonos del mapa.
- **Juárez Celman, General Roca y Presidente Roque Sáenz Peña:** territorio agregado cuando el dato de Cantón lo requiere. Cacopardo (PDF32, impresa27) muestra que Juárez Celman y General Roca ya eran distintos en 1914 y que Roque Sáenz Peña aparece después como subdivisión de Juárez Celman. La agregación electoral se debe a la subsunción de Cantón, no a que fueran un mismo departamento administrativo en 1914.
- **Córdoba, Tercero Abajo / General San Martín:** equivalencia de nombre del Cuadro 1 (PDF33, impresa28). Se conserva una clave común.
- **Corrientes, San Martín / General Alvear:** una unidad cuando Cantón subsume el segundo; la evolución territorial está en PDF34, impresa29. Libres/Paso de los Libres y San Luis/San Luis del Palmar se normalizan explícitamente.
- **Mendoza, San Rafael / General Alvear / Malargüe:** una unidad común para el dato subsumido, con la genealogía del Cuadro 1 (PDF40, impresa35). Ciudad/Capital y Luján/Luján de Cuyo son alias.
- **La Rioja, Juárez Celman / Gobernador Gordillo:** cambio de nombre del Cuadro 1 (PDF39, impresa34), sin inventar un departamento adicional.
- **Entre Ríos, Uruguay / Concepción del Uruguay y Tala / Rosario Tala:** nombres cotejados en PDF35–36. Concepción no se incluye porque el valor 1914 disponible es una inferencia.
- **Esteban Echeverría y Roque Pérez:** Cacopardo los fecha en 1913 (PDF29–30). Ya existían a ambos lados de 1914–1916; la falta de votos en 1914 no se soluciona sumándolos a un vecino. Cantón los marca con `*` sin datos, distinto de `**` subsumido. Se excluyen, sin imputar.
- **Capital:** se conservan las mismas veinte denominaciones electorales de las tablas de Cantón. Cacopardo PDF19 se refiere a secciones policiales/censales, y advierte que una redistribución anterior no era comparable; no se usa esa descripción como si fuera una equivalencia automática entre circunscripciones electorales.

[Correspondencias completas con página fuente](correspondencias.csv), [cifras, estados y localizadores](cifras_y_fuentes.csv), [exclusiones por fuente](exclusiones_fuente.csv) y [lecturas dudosas no usadas en el principal](lecturas_no_usadas_en_principal.csv).

## Robustez y utilidad

El modelo mantiene la especificación del proyecto: centro nacional ponderado, matrices provinciales penalizadas, cinco penalizaciones evaluadas, validación cruzada y 200 remuestreos. Su separación es 42,2 puntos; en validación interna el error territorial baja de 5,40 a 4,76 puntos, una mejora del 11,8 %. El «centro nacional» es aquí el centro de la cobertura parcial, no una estimación de todos los distritos argentinos. El bootstrap no incorpora toda la incertidumbre de selección, fuentes y especificación.

Además del principal se recalculan tres variantes con la misma penalización:

| Variante | Unidades | Cobertura de la selección legible de origen |
|---|---:|---:|
| Principal, lecturas directas y filtro habitual | 130 | 70,40 % |
| Lecturas recuperadas directamente en Lupu–Stokes, con filtro | 149 | 81,71 % |
| Lecturas directas, sin filtro de crecimiento | 157 | 82,42 % |
| Lecturas recuperadas en Lupu–Stokes, sin filtro | 181 | 96,20 % |

La variante Lupu solo acepta una cifra de una fuerza individual, expresamente publicada en el cotejo, compatible con los dígitos legibles. No reparte una familia partidaria ni calcula residuos ni elige el número más cercano a una media. Sigue siendo una variante de fuente y no se mezcla con el principal.

En la suma parcial, las filas grandes cambian hasta 3,9 puntos al combinar ambas sensibilidades. Independientes y Otros cambian mucho más. En PBA las filas radical y conservadora son las más estables frente a la variante provincial de Calvo; la fila socialista cambia hasta 24,3 puntos entre especificaciones. En Capital, Conservadores y Unión Cívica no quedan identificados: en alguna celda cambian 48,8 y 34,4 puntos, respectivamente; la fila UCR también cambia 25,5 puntos. **Capital requiere reservas fuertes aunque tenga sus veinte unidades.** Los intervalos del principal no sustituyen esta comprobación.

[Diagnóstico](../1914d_1916d/diagnostico.json), [sensibilidad por fuente/filtro](../1914d_1916d/sensibilidad.json), [comparación provincial completa](../1914d_1916d/sensibilidad_provincial.csv). Cada informe de PBA y Capital incluye 200 remuestreos provinciales y comparación con el ajuste Calvo solo en esa jurisdicción.

## Reproducir

1. `python transferencias/preparar_1914_1916.py`
2. `python transferencias/estimar.py 1914d 1916d`
3. `python transferencias/diagnostico_historicos.py --1914`
4. `python transferencias/revisar_1914_1916.py`
5. `python transferencias/verificar_nuevos_cruces.py --1914`

[Revisión territorial de los demás cruces y mapas 1912/1914/1916](../revision_cacopardo_1967/LEEME.md).
