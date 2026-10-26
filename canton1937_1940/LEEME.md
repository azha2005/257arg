# Cantón: 1937, 1940 y 1946

Transcripción de las tablas departamentales del tomo II de **Darío Cantón, Materiales para el estudio de la sociología política en la Argentina (1968)**.

| Año | Elección | Distritos publicados | PDF, desde 1 | Páginas impresas | Filas |
|---|---|---|---|---|---:|
| 1937 | Electores de Presidente y Vice | Capital Federal, Córdoba, La Rioja, Tucumán | 142–145 | 143–146 | 76 |
| 1940 | Diputados nacionales | Capital Federal, Córdoba, Entre Ríos, Santa Fe, Tucumán | 147–151 | 149–153 | 91 |
| 1946 | Electores de Presidente y Vice | Capital Federal y las 14 provincias de entonces | 153–170 | 157–174 | 381 |

Son **27 páginas de tablas, 548 filas y 2.963 celdas**: 2.790 números, 172 marcas `**` y una marca `*`. Todas las tablas corresponden a varones solamente. Se preservan los números de circunscripción de Capital Federal en un campo separado.

## Archivos

- [CSV conjunto de los tres años](canton_1937_1940_1946.csv).
- 1937: [tablas](1937/TRANSCRIPCION_1937.md), [CSV](1937/canton_1937.csv), [JSON](1937/canton_1937.json), [control](1937/CONTROL_1937.json).
- 1940: [tablas](1940/TRANSCRIPCION_1940.md), [CSV](1940/canton_1940.csv), [JSON](1940/canton_1940.json), [control](1940/CONTROL_1940.json).
- 1946: [tablas](../canton1946/TRANSCRIPCION_1946.md), [CSV](../canton1946/canton_1946.csv), [JSON](../canton1946/canton_1946.json), [control](../canton1946/CONTROL_1946.json).
- [Alertas aritméticas y lecturas particulares](NOTAS_DE_TRANSCRIPCION.md).

Los CSV usan formato largo y UTF-8 con BOM: cada celda conserva año, elección, distrito, unidad, concepto y las páginas PDF e impresa. Los valores no llevan separadores de miles. Un valor vacío tiene siempre una marca explícita en la columna `marca`.

## Qué significa la selección de 1937 y 1940

La introducción del tomo I, **página XVI, PDF 20**, explica que para 1931–1942 Cantón prescindió de los datos departamentales de los distritos donde no ganó la oposición, por presunción de fraude mientras estudios históricos más detallados no demostraran lo contrario. Se conserva una [imagen del pasaje](revision/criterio_canton_tomoI_pdf20.png).

Por eso esta entrega identifica los distritos como **selección publicada por Cantón**, sin certificar ausencia de toda irregularidad. La disponibilidad de una tabla no constituye por sí sola una prueba de comicios completamente limpios. No se clasificaron distritos adicionales a partir de sus porcentajes electorales.

El índice del tomo II no incluye tablas departamentales de **1936 ni de 1938**. Entre 1930 y 1946 publica los bloques de 1937 y 1940. Esto describe la cobertura departamental del tomo II; no significa que esos años carezcan de resultados provinciales en el tomo I ni que no puedan recuperarse datos en otras fuentes.

## Lectura y controles

Todas las filas se transcribieron visualmente desde el escaneo. Después se hizo una lectura OCR local independiente para detectar posibles errores de digitación. Se revisaron visualmente las diferencias útiles del cotejo y se corrigieron los dígitos mal leídos. `manual.txt` y `../canton1946/manual.txt` son las entradas de reconstrucción. `revision/`, `../canton1946/revision/` y `cotejo/` guardan las imágenes y la asistencia de revisión; los archivos OCR son auxiliares, no la autoridad numérica.

No se imputó ninguna cifra por residuo. Se conserva `*` para ausencia de dato y `**` para cifras subsumidas en otra unidad o no consideradas, conforme a la nota del original. Ninguna marca equivale a cero.

Se mantienen las agrupaciones y claves de cada página. En 1946, por ejemplo, San Luis presenta Unión Democrática y Laborista; Santiago del Estero agrega una agrupación radical local, y Tucumán distingue dos partidos laboristas. No se transformaron esas columnas en un peronismo agregado ni se incorporaron partidos que Cantón no desglosa. Tampoco se generaron blancos o anulados donde la tabla los omite.

Las sumas diferentes de `Votantes` son alertas de coherencia, no ajustes automáticos ni evidencia de fraude. En particular, muchas tablas no publican todas las categorías necesarias para que la suma cierre. Se conservaron los valores impresos incluso en las filas con sumas mayores que votantes.

## Reproducir

Desde la raíz del proyecto:

```powershell
python canton1937_1940/exportar.py
python canton1937_1940/cerrar.py
```

La fuente es `raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf`; su SHA-256 está en los JSON. No se modificaron atlas, geometrías ni otras bases electorales.
