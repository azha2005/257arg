# Cantón: diputados nacionales de 1916

Transcripción de las 15 páginas del extracto de Darío Cantón (1968), Materiales para el estudio de la sociología política en la Argentina, tomo II. Extracto: páginas 1–15; PDF original: 28–42; páginas impresas: 17–31.

## Alcance

Se recorrieron los doce cuadros distritales y se registraron todas sus filas territoriales y columnas partidarias. Capital Federal reutiliza los 80 valores visualmente transcritos en el paquete anterior; las once provincias se transcribieron en este trabajo. Se incluyeron también las columnas de inscriptos y votantes de las provincias. Capital no presenta esas cifras en el cuadro y no se inventaron.

El registro contiene 312 filas territoriales y 868 celdas partidarias. No equivale a 312 departamentos históricos con resultados completos: incluye Puerto, unidades con cifras subsumidas y nombres territoriales posteriores utilizados por Cantón. No se asignaron geometrías ni códigos modernos. Se regularizaron tildes y nombres reconocibles; los rótulos deteriorados se identificaron con el orden del cuadro y, cuando estaba disponible, con la exportación Lupu–Stokes. No usar los nombres como prueba de equivalencia territorial histórica.

No hay cuadros de Salta, San Juan ni Santiago del Estero en este extracto. Tampoco es una transcripción presidencial. Transcribir todas las columnas que Cantón publicó no garantiza recuperar todas las agrupaciones o candidatos que participaron.

## Valores y estados

- `valor`: entero cuando la cifra pudo leerse; null/CSV vacío cuando no se resolvió.
- `lectura`: registro de trabajo del contenido de la celda, sin puntos de miles. Los signos `?` indican dígitos pendientes o una propuesta de lectura que NO se usa como número.
- `numero_legible`: lectura visual de este trabajo.
- `transcripcion_visual_previa`: Capital, recuperada del paquete anterior.
- `lectura_no_resuelta`: celda deteriorada; no fue rellenada con Lupu ni con una resta.
- `sin_datos`: asterisco simple; en La Rioja afecta a toda la columna de votantes según el encabezado.
- `subsumido_o_no_considerado`: doble asterisco. Cantón indica cifras subsumidas en una unidad mayor o no consideradas; no se resolvió cada relación territorial en esta entrega.
- `guion_sin_cifra`: Puerto, Capital Federal.

Los signos de ausencia nunca se convirtieron en cero. Los ceros numéricos se conservaron cuando estaban publicados. Las filas legibles no fueron corregidas para hacer coincidir sus sumas con votantes.

Esta es una transcripción con pendientes explícitos, no una edición definitiva: consultar `lecturas_pendientes` para las celdas deterioradas, especialmente Buenos Aires, Córdoba y La Rioja. `diagnostico.json` y `cobertura_1916` contienen los recuentos actuales. Un cotejo coincidente no certifica exactitud histórica ni resuelve por sí solo una celda ilegible.

## Archivos

- `votos_1916.csv` / `.json`: una fila por unidad y columna partidaria, con página y estado.
- `padron_1916.csv` / `.json`: inscriptos y votantes, separados de los votos partidarios.
- `celdas_1916.csv` / `.json`: ambas categorías juntas para auditar.
- `claves_1916.csv` / `.json`: rótulos propios de cada distrito; el mismo número de columna no representa el mismo partido en todo el país.
- `cobertura_1916.csv` / `.json`: filas territoriales, números recuperados y pendientes por distrito.
- `cotejo_lupu_1916.csv` / `.json`: comparación de familias recodificadas. No constituye una segunda fuente histórica independiente.
- `unidades_sin_equivalencia_lupu`: filas sin equivalente identificado en la exportación previa; no prueba de ausencia en la base completa.
- `lecturas_pendientes`: celdas con problemas de lectura, incluidos padrón y votos.
- `transcripcion.txt` y `construir.py`: registro de trabajo y generador reproducible. Ejecutar el script desde esta carpeta para regenerar los datos en `resultado/`.
- PDF fuente y JSON originales de Capital y Lupu–Stokes, sin modificación.

## Cotejo

Para comparar se normalizaron acentos y se documentaron alias de errores de nombres en el script. No se asignaron códigos territoriales.

En Corrientes, `con` se compara con Liberal + Autonomista. En Santa Fe, `ucr` se compara con Radical disidente + Radical situacionista, y `con` con Demócrata. En Capital, `con` se compara con Socialista Argentino + Demócrata Progresista: eso NO convierte ambas fuerzas en conservadoras. En San Luis, la exportación recuperada coincide con la columna Demócrata para `con` y NO conserva Unión Popular; esta última se mantiene como fuerza separada en la transcripción. Son reglas auxiliares para cotejar la recodificación, no reclasificaciones de los datos originales.

Las diferencias numéricas legibles conservadas son Paclín (Concentración: 294 frente a 284 en Lupu), Tunuyán (Conservador: 381 frente a 361) y Paraná (UCR: 6205 frente a 6206). Requieren otra fuente o mejor reproducción; no se decidió cuál es históricamente correcta. Las demás diferencias potenciales que dependen de celdas deterioradas quedan sin comparación numérica.

Las columnas de Cantón y los totales de Lupu no son automáticamente votos mutuamente excluyentes o votantes. En las primeras elecciones Cantón puede usar el candidato más votado de una lista; no calcular porcentajes o participación con sumas partidarias sin revisar el método de la obra y la elección.

## Procedencia

- Cantón, tomo II: https://archive.org/details/1968-materiales-para-el-estudio-de-la-sociologia-2
- Cantón, tomo I y notas metodológicas: https://archive.org/details/1968-materiales-para-el-estudio-de-la-sociologia-1
- Exportación auxiliar: https://noamlupu.com/argentina_ecological_data.dta

Las fuentes originales citadas por Cantón se encuentran al pie de cada cuadro del PDF adjunto. Varias son retrospectivas periodísticas de 1922: el año de publicación de la fuente no cambia el año 1916 rotulado en la tabla. No se consultaron nuevamente esos diarios para esta entrega.
