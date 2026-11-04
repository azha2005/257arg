# Revisión de la proyección argentina

Nota posterior: las correcciones autorizadas ya se implementaron y midieron en [validacion_20261028/RESULTADOS.md](../validacion_20261028/RESULTADOS.md). Este documento conserva el diagnóstico previo a esa implementación.

28 de octubre de 2026. Revisión de código, documentación, resultados guardados, sondas reproducibles y bibliografía primaria. Los modelos operativos no se modificaron.

## Dictamen

La base es razonable: proyectar desde el voto anterior, regularizar cuando hay pocas actas, incorporar correcciones locales y conservar lo ya escrutado. No hay evidencia suficiente para reemplazarla por un modelo más complejo en bloque. Las prioridades son corregir el universo de evaluación y el tratamiento de información incompleta, hacer coherentes votos y bancas, y validar la incertidumbre fuera de las elecciones usadas para elegir el método.

Hay dos productos diferentes:

- Escrutinio masivo: `backtest.py` y `aguja.py`, con mesas completas que van llegando.
- Fotos: `fotos_modelo.py`, `proyectar_fotos.py` y `congreso.py`, con muestras pequeñas, voluntarias y a veces incompletas.

Las garantías de uno no se trasladan automáticamente al otro. Una matriz predictiva de Goodman sin restricciones tampoco debe interpretarse como identificación de transferencias individuales de votantes.

## 1. Prioridad alta: evaluar el país completo

`backtest.prepare()` cruza con `how="inner"` y descarta unidades sin votos. Luego `state()` y los simuladores calculan la verdad sobre ese mismo subconjunto. Esto es válido para comparar métodos en el universo emparejado, pero no demuestra precisión nacional.

Sonda con los archivos locales actuales; porcentajes sobre positivos del provisorio local, no del definitivo ni de Wikipedia:

| Par | Cobertura de votos positivos | Distritos enteros ausentes | Ganador en todo el archivo | Ganador en el universo del backtest |
|---|---:|---|---:|---:|
| 2015 general → balotaje | 97,31 % | Ninguno | 51,404 % | 51,582 % |
| 2023 general → balotaje | 98,59 % | Ninguno | 55,695 % | 55,759 % |
| 2019 presidente → 2023 presidente | 89,48 % | Santa Fe y Tierra del Fuego | 36,688 % | 37,199 % |
| 2021 diputados → 2023 presidente | 90,78 % | Santa Fe | 36,688 % | 37,292 % |
| 2023 presidente → 2025 diputados | 97,76 % | Ninguno | 40,656 % | 40,736 % |

En 2019→2023 hay una diferencia de 0,51 puntos en el nivel que se evalúa, antes de discutir el error del pronóstico. No corresponde sumar mecánicamente esos 0,51 puntos a cada error: hay que volver a proyectar el universo faltante y recalcular.

**Cambio recomendado:** usar el padrón/universo de la elección destino como marco; enlace histórico por circuito cuando es válido, luego sección y distrito como respaldo documentado. Conservar las unidades sin enlace y modelar su incertidumbre. Publicar métricas tanto del universo completo como del emparejado y de las unidades con respaldo agregado.

También fijar antes de la noche las fuerzas y el denominador: `load()` elige columnas mirando el total final (umbral nacional de 1 %) y `state()` excluye `OTRAS LISTAS` de `pos`. En los cinco pares de la sonda esto no produjo una diferencia adicional entre los dos denominadores positivos; sí es un riesgo para elecciones con muchas listas pequeñas. La verdad de evaluación debe ser siempre todos los votos positivos correspondientes al objetivo.

## 2. Prioridad alta: cada fuerza necesita sus pesos y su máscara de observación

`proyectar_fotos.proj()` calcula un solo repesado AMBA/resto. Después `fotos_modelo.goodman()` elimina, por columna, las actas donde esa fuerza es desconocida. El repesado deja de corresponder a la muestra efectivamente utilizada.

Con las 27 actas reales y dos orígenes:

| Fuerza | Actas que la informan | Peso efectivo del AMBA |
|---|---:|---:|
| LLA | 27 | 29,29 % |
| FP | 27 | 29,29 % |
| OTRAS | 16 | 15,70 % |
| FIT | 17 | 17,16 % |
| PU | 16 | 15,70 % |

El objetivo del repesado es 29,29 %. No basta con decir que todas las actas están repesadas: para las columnas incompletas el resultado es otro.

**Piloto realizado:** 500 colecciones por par, semilla nueva, patrón `como25`; en hasta diez actas del AMBA se ocultan las columnas que no son los dos primeros. Se compara el mismo Goodman, con los mismos datos, cambiando únicamente el cálculo de pesos por columna. Las muestras son sintéticas y la ocultación se impone por región, no por el resultado oculto.

| Par | Error medio por fuerza, pesos comunes | Pesos por fuerza | Reducción |
|---|---:|---:|---:|
| 2019 → 2023 | 1,370 puntos | 1,272 puntos | 7,18 % |
| 2021 → 2023 | 1,267 puntos | 1,183 puntos | 6,60 % |
| 2023 → 2025 | 1,804 puntos | 1,687 puntos | 6,51 % |

El error del margen entre los principales cambia muy poco: 2,656→2,649; 2,837→2,819; 2,637→2,643. El beneficio aparece en las fuerzas menos informadas y no debe anunciarse como una mejora del margen. El piloto hereda los universos incompletos de la sección 1 y no es una validación independiente del modelo completo.

**Cambio recomendado:** recalcular pesos dentro de cada máscara de observación y dentro de cada remuestra. Registrar por fuerza actas, circuitos, fuentes independientes, regiones cubiertas y tamaño efectivo de muestra. Con un estrato sin observaciones, el repesado no puede recuperar la información: se necesita extrapolación explícita y mayor incertidumbre.

## 3. Prioridad alta: impedir probabilidades falsas por datos ausentes

Tres problemas diferentes:

1. **Contaminación de todo el bootstrap.** Si una fuerza solo se observa en un circuito, algunas remuestras no incluyen ese circuito. Goodman devuelve `NaN`; `pct()` puede propagarlo a todas las fuerzas. Luego `bs.mean(0)` contamina incluso las remuestras originalmente válidas. En una sonda con las actas reales modificadas para que PU solo sea visible en un circuito, el punto fue finito, pero las 400 remuestras finales quedaron inválidas. `(marg > 0).mean()` dio 0 % porque las comparaciones con `NaN` son falsas.
2. **El evento calculado no es ser primero.** `proyectar_fotos.py` compara al primero puntual únicamente contra el segundo puntual. Con tres fuerzas, puede superar al segundo y perder contra el tercero. La probabilidad de liderar debe comparar con todas las fuerzas en cada remuestra. Sonda de tres remuestras: el cálculo pareado da 100 % y la frecuencia de primer puesto es 66,7 %. Es un ejemplo sintético, no el resultado observado de las 27 actas.
3. **Fuerzas totalmente ausentes del CSV.** La lista de fuerzas se arma con `a.bloque.unique()`. Una fuerza que nadie informó puede desaparecer del pronóstico y del denominador. Se necesita un catálogo electoral externo al conjunto de fotos.

**Cambio recomendado:** distinguir cero observado, dato desconocido y lista no presentada. Verificar finitud antes de calcular intervalos/probabilidades y mostrar «no estimable» cuando falta soporte. No resolverlo reemplazando `mean` por `nanmean` y descartando remuestras: eso condicionaría la inferencia a haber observado a la fuerza y podría estrechar las bandas. Hace falta una especificación que mantenga esa incertidumbre, o suspender ese resultado.

## 4. Prioridad alta: un único pronóstico coherente para votos y bancas

`congreso_html()` aplica el prior de gobernadores a los votos distritales, pero la tabla nacional conserva `R['pt']`, anterior a esa corrección. Con las actas reales:

| Fuerza | Nacional mostrado | Nacional implícito en los votos corregidos que alimentan las bancas |
|---|---:|---:|
| LLA | 43,03 % | 41,60 % |
| FP | 35,78 % | 34,07 % |
| PU | 5,28 % | 8,08 % |

Las fuerzas provinciales explícitas deben reagruparse al comparar OTRAS. La pequeña diferencia antes de aplicar gobernadores también existe: se promedian porcentajes en el nacional y votos en el distrital.

**Cambio recomendado:** producir una distribución conjunta de votos por distrito, con no negatividad y restricciones de presencia de listas; sumar cada realización para el nacional y usar esa misma realización para bancas. Si se mantienen dos modelos, presentarlos expresamente como escenarios diferentes.

Problemas adicionales comprobados o identificados en esa capa:

- `provinciales()` usa todos los votos informados del distrito como denominador y trata la ausencia de la fuerza provincial como cero. En una sonda de Córdoba, una foto parcial que informa únicamente LLA y FP baja PU de 23,74 % a 14,25 %, sin informar ningún dato de PU. Para actualizar una proporción se necesitan numerador y denominador compatibles; una foto parcial no es evidencia de cero.
- En las remuestras se vuelven a usar las actas originales completas para actualizar el prior provincial, aunque el ajuste de Goodman sí fue remuestreado. No se está remuestreando todo el estimador y se pierde parte de su covarianza.
- Se asignan votos a fuerzas ausentes de la boleta provincial: con estas actas hay unos 36.083 votos proyectados de PU en cuatro distritos sin su lista y 5.273 de FIT en Corrientes. En esta corrida no generaron bancas inexistentes, pero el cero estructural debería imponerse siempre a partir del catálogo oficial de listas.
- El umbral usa el padrón del primer origen. Para una elección futura hay que usar el padrón de destino, y evaluar los votos sobre ese mismo marco. El promedio de padrones históricos no sustituye al vigente.
- El reparto de OTRAS mediante Zipf es una hipótesis sobre listas desconocidas. Conviene modelar las listas relevantes separadamente y propagar la incertidumbre de las restantes. No confundir un supuesto que reproduce una elección con un resultado identificado por las fotos.

## 5. Prioridad alta: validar bandas y probabilidades fuera del ajuste

El proyecto ya reconoce que la banda de la aguja se ajustó con los mismos órdenes con los que se evaluó. Los archivos guardados muestran que el problema persiste: en 2019→2023 con orden `sesgo`, la cobertura de la banda nominal de 95 % cae a 36,4 % entre 5–25 % contado y a 0 % después de 25 %. Con orden `geo`, después del 25 %, es 84,2 %. Son simulaciones de llegada; no representan frecuencias observadas en noches reales.

Para fotos, multiplicar todo por 1,4 no asegura 95 %. Como diagnóstico sobre `z = |error|/semiancho` guardado, una banda simétrica de factor 1,4 cubre 89,6 % en 2021→2023 tipo Twitter y 92,8 % en 2023→2025. Este cálculo no es la cobertura exacta del pipeline actual: los archivos usan percentiles sin el mismo recentrado, y el pipeline puede promediar dos orígenes. Justamente falta medir el procedimiento completo tal como se publica.

**Diseño recomendado:**

1. Reservar elecciones destino completas para evaluación. Elegir regularización, factor y variables usando únicamente las restantes; además hacer una prueba temporal con solo años anteriores. Dos orígenes hacia 2023 no equivalen a dos elecciones destino independientes.
2. Ejecutar el mismo pipeline que recibe actas en producción: denominadores estimados, respaldo por sección, fotos parciales, duplicados, catálogo de listas y correcciones provinciales. Los simuladores de fotos principales usan padrón real de destino y datos más completos que algunas entradas operativas.
3. Separar error de muestra, error de extrapolación y sensibilidad a selección por cambio. El bootstrap de circuitos vistos no aprende el comportamiento de una región nunca vista ni corrige que se publiquen las mesas donde una fuerza mejoró inesperadamente.
4. Medir cobertura y ancho por fuerza, margen, distrito y tramo del conteo; añadir puntuación de intervalos y Brier/log-score para eventos, con cautela por las pocas elecciones independientes. Medir también falsos llamados a lo largo de toda la trayectoria, no solo cobertura de un corte aislado.
5. Guardar capturas horarias y probar órdenes reales. Retener `sesgo` y agregar sesgo por residuo del modelo, retraso por partido/fuente, provincias enteras tardías, datos que nunca llegan y correcciones del escrutinio.

La documentación del Washington Post muestra por qué la agregación requiere tratar la correlación de errores entre unidades, y separar entrenamiento de calibración. Su propuesta posterior combina bootstrap con modelos de errores para unidades aún no observadas. Son referencias útiles para la arquitectura de incertidumbre, no una demostración de que funcionen sin adaptación en Argentina. [Actualización técnica 2020](https://s3.us-east-1.amazonaws.com/elex-models-prod/elex-models-prod/2020-general/write-up/election_model_writeup_update1.pdf), [Cherian, Bronner y Candès, modelo de 2024](https://jjcherian.github.io/assets/pdf/election_poster.pdf).

La predicción conformal tampoco garantiza cobertura con selección arbitraria: bajo cambio de distribución de covariables se requieren hipótesis sobre la estabilidad condicional y los pesos. No usar la palabra «conformal» como sustituto de probar esas condiciones. [Tibshirani et al., 2019](https://papers.neurips.cc/paper_files/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf).

## 6. Qué probar después de las correcciones

**A. Regularización y calibración con pocas variables conocidas para todo el país.** Mantener Goodman como referencia y ensayar un efecto de distrito parcialmente agrupado, perfil político anterior y tamaño/urbanización. Para fotos, probar balance regularizado de esos perfiles además de AMBA/resto, sin forzar 24 pesos provinciales con 30 actas. Elegirlo en validación geográfica y electoral separada. El estudio de Si destaca que la validez de MRP depende de auxiliares relacionados con el resultado y la selección; no basta con añadir más celdas. [Si, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12140408/).

**B. Soporte y extrapolación como condiciones para informar.** Mostrar número efectivo de circuitos y fuentes por fuerza, dispersión de pesos, fracción del padrón sin perfiles similares y sensibilidad al retirar una fuente/provincia. Un mínimo fijo de 30 actas o 1 % de mesas no basta. No achicar la banda solo porque coinciden los porcentajes históricos agregados: puede quedar selección por cambio dentro de cada perfil.

**C. Revisar el benchmarking del escrutinio masivo.** La aguja sigue usando el nacional de D. Los resultados guardados favorecen quitar el ajuste forzoso antes de añadir complejidad. Recalculando el error absoluto medio con todos los órdenes y cortes 0,2–25 %:

| Par | D | D sin ajuste | E sin ajuste |
|---|---:|---:|---:|
| 2015 general → balotaje | 0,799 | 0,657 | 0,605 |
| 2023 general → balotaje | 0,607 | 0,512 | 0,476 |
| 2019 → 2023 | 1,571 | 1,295 | 1,217 |

Son comparaciones dentro de las elecciones usadas para desarrollar los modelos. Mi siguiente candidato sería D sin ajuste; E se evalúa aparte para saber si las vecinas aportan fuera de muestra. La evidencia israelí no decide por sí sola qué ocurre en Argentina. Recalibrar la banda al cambiar el estimador, sin trasladar el factor de D automáticamente.

**D. Prior del ICG como componente opcional.** `icg_fotos.prior()` elimina la elección objetivo pero incluye años futuros. Para simular 2023 incorpora 2025. En la sonda, el prior 2023 cambia poco al entrenar solo con el pasado (33,628→33,690); en 2021 cambia 31,885→30,030. Por eso no afirmo que la mejora publicada sea causada por la fuga temporal, pero la evaluación no es prospectiva. Para 2025 ya no hay años posteriores y ese problema no aplica.

Usar entrenamiento temporal, excluir decisiones de selección de variables tomadas mirando el año de prueba y estimar la covarianza entre errores del prior y de las actas. La fórmula actual de pesos por varianza es óptima solo bajo condiciones adicionales, entre ellas la ausencia de sesgos y covarianza relevante. El ICG ya empeoró algunas estimaciones de bancas en los resultados locales; no lo activaría por defecto.

**E. Trazabilidad de actas.** El identificador actual contiene el nombre de la foto. La misma mesa con otra imagen se cuenta dos veces: la sonda pasó de 27 a 28 actas y movió FP −0,238 puntos sin información electoral nueva. La clave debe representar elección, cargo, distrito, sección, circuito, mesa y tipo; las imágenes son evidencia/versiones de esa misma observación. Conservar fuente, hora y correcciones permite además identificar dependencia entre fotos de un mismo emisor.

## Orden de implementación propuesto

1. Corregir identidad de mesas, máscaras de datos desconocidos, catálogo de fuerzas y verificaciones numéricas/eventos de probabilidad.
2. Corregir pesos por fuerza y la actualización provincial con fotos parciales; hacer votos nacionales y bancas derivaciones de la misma distribución.
3. Reconstruir backtests con el universo completo y el pipeline operativo; reservar elecciones para evaluación final.
4. Recalibrar bandas y verificar probabilidades; incluir selección por cambio y fuentes agrupadas.
5. Comparar D sin ajuste, variantes jerárquicas y balance de perfiles. Integrar solo mejoras que se sostengan en la evaluación reservada.

No recomiendo reabrir por defecto lealtad fija, ancla proporcional fuerte o prior de encuestas: el proyecto ya tiene resultados desfavorables para sus formulaciones ensayadas. Más remuestras del mismo conjunto de fotos tampoco solucionan cobertura territorial ni selección.

## Evidencia y reproducción

Desde la raíz del proyecto:

```powershell
python -X utf8 proyeccion/revision_astra_20261028/auditar.py
python -X utf8 proyeccion/revision_astra_20261028/experimento_pesos.py
```

- `resultados.json`: universos, pruebas con actas reales, sondas sintéticas claramente identificadas, contraste temporal del ICG, métricas existentes y hashes de archivos revisados.
- `piloto_pesos.csv`: 1.500 colecciones, tres variantes emparejadas por colección.
- `piloto_pesos_resumen.json`: resumen del piloto.

Ubicaciones de código revisadas: `backtest.py:101` y `:390`; `fotos_modelo.py:52` y `:121`; `proyectar_fotos.py:76`, `:86`, `:151`, `:166`, `:186` y `:293`; `congreso.py:126` y `:179`; `fotos_sim.py:121`; `fotos_sim2.py:20`; `icg/icg_fotos.py:23`; `aguja.py:49` y `:97`. Las líneas corresponden a los archivos al momento de esta revisión.

Alcance: se verificaron los mecanismos descritos y se ejecutó un piloto pequeño. No se construyó todavía el nuevo universo completo ni se hizo una validación prospectiva de una metodología sustituta. Los backtests contra el provisorio no demuestran exactitud contra el escrutinio definitivo.
