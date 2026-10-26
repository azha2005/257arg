# Cantón, 1954, tomo II

Transcripción de las páginas PDF **171–248**, contadas desde 1, del archivo local `raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf`. La página 171 es una portadilla; las **77 páginas de tablas**, 172–248, corresponden a las páginas impresas 177–253.

## Archivos de entrega

- `TRANSCRIPCION_1954.md`: tablas legibles, separadas por página, con las claves de las columnas.
- `canton_1954.csv`: formato largo, UTF-8 con BOM; una celda por registro, con distrito, elección, categoría, unidad, concepto y página de procedencia. Los valores numéricos no llevan separadores de miles. `valor` queda vacío solamente cuando existe una marca explícita en `marca`.
- `canton_1954.json`: las mismas tablas agrupadas por página, con marcas y método de revisión.
- `DIFERENCIAS_ORIGINAL_1954.md`: diferencias entre la suma de votos y votantes, entre varones más mujeres y el total impreso, y casos con más votantes que inscriptos.
- `CONTROL_1954.json`: recuentos y controles reproducibles, incluido el SHA-256 del PDF fuente.

La entrega contiene **1.460 filas**, **9.764 celdas**, **9.138 valores numéricos** y **626 marcas** (`*`: 55; `**`: 571). No quedan celdas vacías sin marca.

## Criterio de transcripción

Se corrigieron las lecturas ilógicas del OCR mediante el escaneo, incluyendo dígitos confundidos, cifras cortadas y asociaciones de cifras con la fila equivocada. Se transcribieron visualmente las tablas de totales, las tres de Capital Federal, las de Catamarca y las tablas únicas de San Luis y Tucumán; para las restantes se combinaron lecturas OCR independientes, controles entre categorías y revisión visual de las discrepancias y de las sumas de fila. El JSON distingue las filas transcritas visualmente del resto. Los controles aritméticos son controles de coherencia, no una garantía de que cada celda haya sido leída manualmente.

Se conservan las cifras impresas aunque no sumen. No se completaron valores por residuo ni se reemplazaron los totales del libro por los calculados. El informe registra **38 diferencias de suma de fila**, **45 diferencias entre categorías** y **9 filas con más votantes que inscriptos**; las categorías de anomalías pueden superponerse.

`*` indica ausencia de dato. `**` identifica unidades incluidas en otra unidad o no consideradas, de acuerdo con las notas del original. Ninguna de estas marcas equivale a cero. Las notas particulares deben consultarse en el escaneo: esta entrega transcribe las tablas y sus claves, no reproduce íntegramente el texto marginal ni todas las notas al pie.

Se regularizó la escritura de los nombres de unidades y partidos para evitar basura del OCR. La columna `pagina_pdf` conserva la procedencia física de cada dato, incluso en Buenos Aires, donde los cortes de las continuaciones cambian entre varones, mujeres y total.

## Alcance electoral y casos del original

Se preserva la elección indicada en cada tabla: diputados, vicepresidente o delegados. Chubut, Formosa, Misiones, Neuquén, Río Negro y Comodoro Rivadavia contienen resultados de vicepresidente; Santa Cruz, de delegados. No deben mezclarse automáticamente con los resultados de diputados.

San Luis (PDF 235) y Tucumán (PDF 245) contienen solamente varones en este bloque. No se construyeron tablas de mujeres ni totales para esos distritos.

Entre las inconsistencias conservadas están las advertencias del original sobre inscriptos y votantes en Chaco y Cura-Có (La Pampa), y la repetición de cifras de Concepción y San Ignacio en el total de Misiones. Las cifras de las categorías separadas siguen siendo las publicadas, aunque discrepen del total.

## Reproducción y trazabilidad

`manual.txt`, `revision_pares.txt` y `correcciones_filas.txt` conservan las lecturas y correcciones visuales. `revision/` contiene imágenes de página, lecturas OCR y hojas de cotejo. Los JSON de `transcripcion/` son registros de trabajo; algunas páginas lógicas agrupan unidades para compararlas entre categorías y no deben usarse como referencia física sin el campo `pagina_fuente`. Para trabajar con datos finales, usar los archivos agregados de entrega.

Desde la raíz del proyecto:

```powershell
python canton1954/controlar.py
python canton1954/exportar.py
```

Estos comandos reconstruyen los datos corregidos y las entregas sin volver a ejecutar el OCR. No se modificaron atlas ni otras bases del proyecto.
