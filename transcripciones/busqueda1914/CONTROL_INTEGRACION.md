# Control estructural del consolidado integrado

**Actualización de fase3,15/10/2026:** Santa Fe pasó a152 filas territoriales/150 cifras/2 vacíos, distinguiendo siete resúmenes y tres sumas parciales. Los parciales globales son166 filas/164 cifras/2 vacíos, sin cambios en1192 filas/1094 cifras principales. Fuentes de fase3 incluidas en el manifiesto. El corte temporal y los controles anteriores que siguen se conservan como historial.

**Corte medido:** 15 de octubre de 2026, 02:31:57 (-03). El conteo describe los archivos presentes en ese momento; no es un corte permanente ni certifica la transcripción de las fuentes. Se contaron filas, vacíos, claves y referencias sin copiar ni revisar visualmente cifras electorales.

El conteo anterior de **1.043 filas / 945 cifras / 98 ausencias / 6 distritos**, medido a las 02:28, fue un corte intermedio y queda reemplazado por este estado. Se conserva aquí como historial, no como cifra vigente.

## Archivo principal

`datos_1914_depto.csv` tiene las siete columnas esperadas: `provincia`, `departamento`, `partido_o_lista`, `votos`, `fila_fuente`, `fuente_id` y `nota`.

| Distrito | Filas | `votos` presente | `votos` vacío |
|---|---:|---:|---:|
| Buenos Aires | 360 | 304 | 56 |
| Capital Federal | 84 | 80 | 4 |
| Córdoba | 200 | 166 | 34 |
| Corrientes | 288 | 287 | 1 |
| Entre Ríos | 42 | 39 | 3 |
| La Rioja | 69 | 69 | 0 |
| Mendoza | 149 | 149 | 0 |
| **Total** | **1.192** | **1.094** | **98** |

No hay valores `votos` no numéricos ni vacíos en las otras seis columnas. El JSON `control_consolidacion.json` coincide con el CSV en el total y en el desglose por distrito.

## Claves y referencias

- La clave de fila (`provincia`, `departamento`, `partido_o_lista`, `fuente_id`, `fila_fuente`) es única: 1.192 claves para 1.192 filas.
- La clave lógica (`provincia`, `departamento`, `partido_o_lista`) también es única dentro del principal; no hay renglones repetidos entre fuentes alternativas.
- El principal usa siete `fuente_id`; cada uno coincide exactamente con un registro de `fuentes.csv`.
- Los cinco archivos físicos referenciados por el principal existen y cada uno aparece una vez en `inventario_pdfs.csv`. El inventario tiene 41 entradas y todas las rutas listadas existen.
- `fuentes.csv` tiene 92 registros y 91 IDs únicos. `hcdn_26p1914_impugnados` está repetido dos veces con la misma URL y el mismo archivo; ese ID no se usa en el principal, en el archivo parcial ni en la complementaria de Mendoza.
- En la unión de IDs usados por el principal, el archivo parcial y la complementaria de Mendoza hay 15 IDs distintos; los 15 tienen exactamente una coincidencia en el manifiesto. Los 15 registros del manifiesto dejan vacío el campo `provincia`, aunque la provincia sí está consignada en los datos.

## Archivos separados del principal

`datos_1914_parciales.csv` contiene **120 filas: 117 con `votos` y 3 vacías**. El desglose es Santa Fe 106 (103 con valor y 3 vacías), Jujuy 7 y Tucumán 7. Sus claves compuestas y lógicas no se repiten dentro del archivo, y no hay claves lógicas compartidas con el principal. Sus ocho `fuente_id` resuelven exactamente una vez en `fuentes.csv`. Las ocho referencias físicas existen; seis son imágenes JPG fuera del inventario de PDF y dos son PDF, cada uno inventariado una vez. Estas filas parciales siguen separadas: no equivalen a cobertura provincial completa ni deben sumarse automáticamente al principal.

Mendoza aporta **149 filas principales de 16 departamentos**, incorporadas en el corte de 22/3. `fase2/mendoza/datos_complementaria.csv` mantiene aparte otras **46 filas** de fuente complementaria. Esa salida tiene observaciones a nivel de mesa; no se debe anexar como si fueran filas departamentales. Requeriría agregación y conciliación explícitas a una unidad compatible antes de cualquier integración, para evitar doble conteo. El PDF asociado existe y está una vez en el inventario. Los archivos de totales provinciales y de control de Mendoza son controles de comparación, no filas para fusionar con la base departamental.

## Estado de integración reflejado

El `consolidar.py` presente genera el principal con la salida detallada principal más complementarias de Córdoba en reemplazo de la selección cordobesa anterior, agrega el CSV departamental de La Rioja y la salida principal de Mendoza. Produce por separado `datos_1914_parciales.csv` con las filas disponibles de Santa Fe, Jujuy y Tucumán. Recoge manifiestos de la raíz, `partes/` y `fase2/`. No se modificaron scripts ni datos para esta auditoría.

La medición verifica estructura, presencia de archivos, unicidad de claves y resolución de referencias. No verifica si cada cifra coincide con su página fuente, no completa ausencias y no certifica el alcance o validez jurídica de los agregados. Las tres ausencias de Santa Fe y las 98 ausencias del principal siguen siendo vacíos, no ceros.

## Repetición del control

Los conteos pueden repetirse leyendo `datos_1914_depto.csv`, `datos_1914_parciales.csv`, `fase2/mendoza/datos_complementaria.csv`, `fuentes.csv`, `inventario_pdfs.csv` y `control_consolidacion.json`, y agrupando por las claves descritas. Si cambian las transcripciones o la selección de fuentes, registrar un nuevo corte con fecha y hora, y actualizar también el informe general.
