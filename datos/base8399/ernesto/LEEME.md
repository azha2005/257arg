# Capa 3: bases de Ernesto Calvo, país por departamento 1983–1999

Origen: `Bases Ernesto/País x Departamento/TPDENP19xxT.xls` (nueve archivos, 1983 a 1999; una hoja por provincia). Se regenera con `python ../construir_ernesto.py "<carpeta Bases Ernesto>"` y `python ../control_ernesto.py` (requieren `xlrd`).

## Qué hay
- `AAAA_<cargo>/dpto_partidos.csv`: votos por departamento y columna de partido, formato largo, sin corregir ni imputar. Cargos: `presidente`, `diputados` (nacionales), `senadores_nac`, `gobernador`, `diputados_prov`, `senadores_prov`, y `otras_<sufijo>` para categorías que el sufijo del archivo no permite interpretar (convencionales, concejales, etc.). 64 combinaciones año–cargo, resumidas en `resumen.csv`.
- `tipo_fila`: `agrupacion` (columna de partido o lista), `positivos` (`pos`, la suma de las agrupaciones), `blancos`, `nulos`, `impugnados_recurridos`, `total`, `electores`. **No sumar `positivos`, `total` ni `electores` con las agrupaciones.** `electores` (padrón) se asignó al cargo del bloque de columnas anterior; es una inferencia de posición.
- `codigo_partido` es la sigla de la columna (por ejemplo `pj`, `ucr`, `ads`); su significado está en `codigos_AAAA.csv`, que copia las hojas de leyendas sin interpretar. El mismo código puede significar cosas distintas en provincias distintas.
- `anomalias.csv` (97 filas): columnas con sufijo de año distinto del archivo (por ejemplo `89dn` en el archivo de 1985), nombres sin sufijo, y celdas con texto en lugar de número (`f/d`, `?`, `,`). Se excluyen del CSV de datos y quedan acá.
- `control_interno.csv` y `control_vs_lupu.csv`.

## Cobertura
- **Presidente**: 1983, 1989, 1995, 1999. En 1999 faltan San Luis y Santa Cruz (sus hojas no traen columnas de presidente). El archivo de 1991 trae solo 15 filas de presidente.
- **Diputados nacionales**: 1983, 1985, 1987 (falta Tierra del Fuego), 1989, 1991, 1993, 1995, 1997 (falta San Luis) y 1999 (faltan San Luis y Santa Cruz).
- Unidades: 523 a 537 por elección (departamentos; Capital Federal viene por sección electoral).
- Quedan sin procesar los demás archivos de la carpeta: circuitos de Buenos Aires, Capital, Córdoba, Entre Ríos y Santa Fe; las tablas de 2001 por departamento; los de «agrupaciones»; y las bases Access/SPSS.

## Contraste con Lupu–Stokes (`control_vs_lupu.csv`)
- **El `total` de Lupu se reconstruye con esta base**: presidente = agrupaciones + blancos + nulos (la columna `tot`), diputados = agrupaciones + blancos (sin nulos). Con esa definición coinciden 472 de 497 unidades en presidente 1983 (el resto: 21 sin fila en Lupu, 4 que difieren), 457 de 500 en 1989, 452 de 509 en 1995, 413 de 495 en 1999; en diputados, entre 376 y 455 por año (sin contar 1997). Es consistente con lo que dijo Lupu: salen de la base de Escolar.
- **1997 diputados**: coinciden solo 69 de 500 unidades (Corrientes, La Pampa y Santiago del Estero enteras); la definición del total no encaja y no se investigó.
- **Unidades que Ernesto trae y Lupu no** (`sin_fila_lupu`): presidente 1983, 21; 1989, 34; 1995, 44; 1999, 82 (entre ellas 30 de Buenos Aires, 17 de Misiones y 13 de Río Negro). Puede ser ausencia real o diferencia de nombre; no se distinguió.
- En Capital Federal Lupu trae circuitos y Ernesto secciones: solo se compara por provincia.
- **Consistencia interna** (`control_interno.csv`): en muchas unidades la suma de agrupaciones no cierra con `pos` o con `tot` (más en categorías provinciales). No se investigaron una por una.

## Pendiente
- Partido por partido: falta una tabla de equivalencias código → familia/alianza (los criterios están en `Bases Ernesto/Criterios para elaboración de listados de alianzas.doc`, sin leer) para integrar con la capa `detalle_partidos.csv`.
- Contrastar Mendoza 1983–1999 con la transcripción de UNCuyo (capa 2), y las 1997 con los otros archivos.

- **Convencionales constituyentes 1994**: `1994_constituyentes/` (de `1994-const.xls`, script `construir_const94.py`; anomalías en `anomalias.csv`).

- **Diputados nacionales 2001**: `2001_diputados/` (de `2001 x DTO/Diputados Nacionales`, script `../construir_dn2001.py`; `mapeo_columnas.csv` = hoja `dn2001` de `agrupaciones/DN01.xls`). Las planillas traen solo el código de departamento (`DTO`): los nombres se tomaron de las otras elecciones por código INDRA (San Luis: 1993; Santiago del Estero: 1995; resto: 1997). 24 provincias, 538 unidades, 13.968.343 positivos (la tabla de Wikipedia da 14.290.108).
