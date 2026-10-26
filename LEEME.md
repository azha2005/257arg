# Resultados electorales argentinos por departamento/partido, 1912–2003

Búsqueda y descarga: 8 de octubre de 2026. Categorías buscadas: presidente y diputados nacionales; todas las fuerzas por separado. Este paquete reúne los datos recuperados y las fuentes documentales localizadas. No constituye una serie nacional completa de todas las fuerzas.

**Atlas legislativos 2003–2025 (20-oct-2026):** los doce atlas y sus paquetes locales de Commons están reunidos en [el índice de legislativas 2003–2025](commons/INDICE_LEGISLATIVAS_2003_2025.md). Incluye fuentes, cobertura, logos, colores y reservas de publicación. La Pampa 2003 se representa con su total provincial definitivo; no se inventan resultados por departamento.

## Qué se consiguió

| Fuente | Cobertura | Desglose | Estado |
|---|---|---|---|
| Lupu–Stokes, Argentina Ecological Dataset | 1912–2003; 16.683 registros | Departamento; votos agrupados en familias radical, peronista, socialista y conservadora | Descargado en DTA y exportado a CSV. Hay elecciones, provincias y categorías faltantes. No permite separar todas las fuerzas. |
| dat.ar, elecciones 2003 | Presidente: 24 distritos/539 unidades; diputados: 23 distritos/517 unidades | Agrupaciones separadas, blancos, nulos y totales | Descargado. Falta La Pampa en diputados. Hay errores de formato e inconsistencias; conservar como fuente para cotejar. |
| polAr, presidenciales 2003 | 62.323 registros de mesa; 24 distritos/539 unidades departamentales o circunscripciones | 18 columnas de listas tras recodificaciones, blancos y nulos | Descargado y agregado por departamento. No validado contra el definitivo. |
| Entre Ríos, diputados 2001 | 17 departamentos, 170 filas de fuerza | Diez fuerzas separadas por departamento, ambos sexos | Descargadas las 17 tablas oficiales y consolidadas. |
| Canton, Materiales para el estudio de la sociología política en la Argentina, 1968 | Selección de elecciones 1912–1965 | Tomo II: resultados nacionales por departamento con partidos separados; tomo I: introducción y cuadros provinciales | **RECUPERADOS ambos tomos en Internet Archive: PDF y OCR.** El tomo II tiene 457 páginas digitales. No es una base completa de todas las fuerzas: el autor advierte omisiones y agrupaciones de minoritarios. |
| Entre Ríos, diputados 1991 | 15 departamentos recuperados, 90 filas | Fuerzas originales; conservar vacíos | CSV parcial. Falta Feliciano; dos recursos del catálogo apuntan a archivos llamados Federal. |
| Entre Ríos, diputados 1997 | 16 unidades departamentales en fuente y grupo separado «custodias», 51 filas | Tres fuerzas, originales oficiales | Descargado y consolidado. Cotejado contra total provincial: ver nota de comprobación. |
| AGN, fondo DNE01 | 1946–1975 | Según el inventario, planillas con cada partido y niveles desde país hasta mesa | Existencia documental confirmada; no se recuperaron las imágenes del fondo. |
| Escolar/PEEL, Bases Departamentales de la Argentina, 1983–1999 | 1983–1999 | Base departamental utilizada como fuente académica | Referencia bibliográfica confirmada; no se encontró una descarga pública. |
| CD de El federalismo electoral argentino, 2001 | Planillas originales departamentales 1983–1999; bases departamentales 1995–1997 y 1999 | El catálogo describe originales del Ministerio del Interior y datos INAP/INDRA | Existencia del CD documentada. No se recuperó. Verificar categorías y cobertura al obtenerlo. |

Los números de unidades territoriales incluyen circunscripciones de Capital Federal y las unidades presentes en cada archivo. No deben interpretarse como un número fijo de departamentos a lo largo del siglo.

## Archivos y uso

`raw/` conserva los originales descargados, sin correcciones. `preparados/` contiene exportaciones, cobertura y consolidaciones, sin imputar ausencias.

- `lupu_stokes_1912_2003_exportacion.csv`: exportación íntegra del DTA. `ucr`, `pj`, `soc` y `con` son familias políticas según la codificación de los autores; no nombres de listas originales. Los datos ausentes quedan vacíos, no se convierten en cero.
- `cobertura_lupu_stokes.csv`: año, mes, categoría, registros territoriales y disponibilidad de las cuatro familias. La cobertura es del archivo observado, no de todas las elecciones celebradas.
- `entre_rios_diputados_2001_por_departamento.csv`: unión de las 17 tablas de ambos sexos. Mantiene votos, porcentaje y nombre de fuerza de la fuente. Se unificaron solamente los separadores de los encabezados (`-` / `_`) y se añadió el departamento tomado del nombre del archivo. No se duplicaron tablas masculinas, femeninas ni el total provincial.
- `polar_presidente_2003_agregado_depto_SIN_VALIDAR.csv`: suma mecánica de mesas por `codprov`, `coddepto`, `depto`, manteniendo las columnas de lista. Es una preparación reproducible, NO un nuevo escrutinio definitivo. Las denominaciones se encuentran en `raw/polar_listas_presidente_2003.csv`.
- `datar_2003_valores_para_revisar.csv`: valores ausentes o con puntuación que requieren revisión. El original contiene mezclas de separadores de miles y otras anomalías.
- `polar_2003_mesas_para_revisar.csv`: 606 filas cuya suma de votos supera el número de electores consignado. No se descartaron ni corrigieron automáticamente.
- `diagnostico.json`: recuentos de cobertura y comprobaciones básicas.
- `preparar.py`: reproduce las exportaciones Lupu–Stokes, Entre Ríos 2001 y diagnósticos de 2003 a partir de los archivos originales del paquete; requiere pandas. Las nuevas consolidaciones 1991/1997 se incluyen junto con sus originales y procedencia.

## Limitaciones importantes

1. La base de Lupu–Stokes no es una base de listas originales. Por ejemplo, las divisiones radicales y los frentes peronistas pueden estar agrupados. No es posible reconstruir los votos de cada lista a partir de cuatro totales de familias. Tampoco corresponde obtener una fuerza menor restando PJ y UCR del total, porque ese resto mezcla otras fuerzas, blancos y nulos.
2. La base no contiene datos para 1924, 1931, 1934, 1936, 1938, 1942 ni 1951. No contiene presidente en 1916 ni diputados en 1922, 1928, 1946 y 1958. Hay coberturas territoriales parciales en otras elecciones; ver el CSV. Esta lista describe faltantes de la base, no inexistencia de documentación histórica.
3. El archivo codifica las constituyentes de diciembre de 1948 y 1957 con `dip=1`; y la elección de vicepresidente de 1954 con `pres=1`. El cuadro de cobertura las identifica expresamente para que se puedan excluir del objetivo presidente/diputados.
4. Para Canton, la introducción original (tomo I, p. XVII) indica expresamente que no incluye el desglose departamental de 1960 y 1963, ni las constituyentes de 1957, y selecciona solo parte de los datos de 1931–1942. Además, en pp. XXVI–XXVII advierte omisiones de partidos menores y agrupaciones como «Varios». Los primeros años tienen cobertura provincial parcial. La base posterior de Lupu–Stokes tiene registros para esos años procedentes de la combinación de fuentes. No debe confundirse el alcance de una obra con el de la base conjunta.
5. El CSV de dat.ar se anuncia como definitivo, pero sus cifras requieren cotejo: La Pampa falta en diputados; valores como `81.160` aparecen en votos; Neuquén presidencial muestra totales internos incompatibles. No se corrigió la puntuación automáticamente ni se utilizó esta fuente para dar por válida una tabla nacional.
6. El repositorio polAr conserva una base presidencial de 2003 y un script que reúne etiquetas de listas con la misma candidatura. Su agregado suma 20.175.874 votos entre listas, blancos y nulos, y contiene las 606 anomalías mencionadas. Por ello no se certifica como definitivo ni se usa para sustituir cifras oficiales.
7. Los límites territoriales y nombres cambian. Para mapas de todo el período se necesitan geometrías históricas o una correspondencia documentada; los territorios sin derecho de participación nacional en una fecha no son ceros electorales.
8. Los mapas originales de Commons no prueban la existencia de una tabla de base: su procedencia fue cuestionada por otros editores en la discusión del autor. Esta advertencia no implica que se haya verificado la acusación, y no afecta al comparativo anterior hecho con Lupu–Stokes.

## Fuentes y vías de recuperación

### Base académica disponible
- [Página de datos de Noam Lupu](https://www.noamlupu.com/data).
- [DTA original](https://noamlupu.com/argentina_ecological_data.dta).
- [Artículo: The Social Bases of Political Parties in Argentina, 1912–2003](https://www.noamlupu.com/social_bases.pdf), apéndices A y B.
- [Apéndice con cobertura por elección y categorías](https://www.noamlupu.com/democracy_interrupted_append.pdf), pp. 5–9. Escolar, Marcelo (2003), *Bases Departamentales de la Argentina, 1983–1999*, PEEL, Universidad Torcuato Di Tella, figura en sus referencias.

### 1912–1965
- Canton, Darío (1968), *Materiales para el estudio de la sociología política en la Argentina*, dos tomos, Instituto Torcuato Di Tella.
- [Reseña que describe sus niveles de desagregación y faltantes](https://introduccionalahistoriajvg.wordpress.com/2014/11/28/%E2%9C%8D-materiales-para-el-estudio-de-la-sociologia-politica-en-la-argentina-1968/).
- [Enlace PDF del tomo I localizado en referencias](http://www.dariocanton.com/publicaciones/sociologia/1968_materiales-para-el-estudio-de-la-sociologia/1968_materiales-para-el-estudio-de-la-sociologia_1.pdf): el sitio del autor devuelve 403, pero se recuperó una copia pública en Internet Archive.
- [Tomo I recuperado](https://archive.org/details/1968-materiales-para-el-estudio-de-la-sociologia-1).
- [Tomo II recuperado](https://archive.org/details/1968-materiales-para-el-estudio-de-la-sociologia-2).
- PDFs y OCR en `raw/canton_1968/`; índice auxiliar de encabezados OCR en `preparados/canton_tomo_II_indice_paginas_OCR.csv`. El OCR contiene errores, incluso en años y cifras; no se debe convertir automáticamente en votos sin cotejar las imágenes. En la página digital 18 del tomo II se verificó visualmente la tabla Córdoba, diputados 1912: UCR, Unión Nacional, Constitucional y Autonomista Nacional, junto con inscriptos y votantes. Varias unidades están marcadas como subsumidas o no consideradas; no equivalen a cero.

### 1946–1975 y 1973
- [AGN: descripción del fondo AR-AGN-DNE01](https://www.argentina.gob.ar/sites/default/files/dai_-_0004_-_2022.pdf). El documento confirma planillas por departamento, sección y mesa, con votos y porcentajes de cada partido; la disponibilidad varía según unidad documental.
- [Serie Resultados electorales](https://atom.mininterior.gob.ar/index.php/resultados-electorales).
- [Buenos Aires: presidenciales 1973](https://atom.mininterior.gob.ar/index.php/buenos-aires-elecciones-nacionales-presidenciales-1973?sf_culture=es). Referencia catalogada: **AR AGN DNE01-De-re-40_077_367a412**. El título de la unidad no basta para afirmar cobertura completa de marzo y septiembre; revisar los folios.

### 1983–1999
- [El federalismo electoral argentino, PDF](https://fhu.unse.edu.ar/carreras/soc/socpolitica/federalismo_electoral_argentino.pdf), Anexo A, pp. 109–110: distingue base provincial de todas las fuerzas y base departamental 1995–1997.
- [Catálogo que detalla el CD complementario](https://books.google.com/books/about/El_federalismo_electoral_argentino.html?hl=en&id=fFQVAQAAIAAJ&output=html_text): incluye planillas originales departamentales del Ministerio del Interior 1983–1999. El PDF del libro NO contiene por sí mismo el CD ni todas esas tablas.
- [DINE: históricos 1983](https://www.argentina.gob.ar/dine/resultados-electorales/elecciones-1983), y páginas de cada elección hasta 2003. Los cuadros visibles por provincia no satisfacen el pedido por departamento; sirven para cotejar agregados.

### Fuentes descargadas 2001 y 2003
- [Entre Ríos, diputados nacionales 2001](https://datos.entrerios.gov.ar/dataset/elecciones-2001); procedencia individual de cada CSV en `raw/entre_rios_2001/procedencia.json`.
- [dat.ar, resultados 2003 por departamento](https://datar.info/dataset/elecciones-nacionales-2003-resultados-definitivos).
- [Recurso CSV dat.ar](https://datar.info/dataset/elecciones-nacionales-2003-resultados-definitivos/resource/335f6414-b977-466d-acae-e1b3071585c8).
- [polAr: repositorio](https://github.com/electorArg/PolAr_Data). Su README está parcialmente desactualizado respecto a la presencia del archivo de 2003; se inspeccionó el árbol actual y se descargó `data/arg_presi_gral2003.csv`.
- [Archivo presidencial polAr](https://github.com/electorArg/PolAr_Data/blob/master/data/arg_presi_gral2003.csv).
- [Script de recodificación polAr](https://github.com/electorArg/PolAr_Data/blob/master/scripts/data_processing/rmd_resultados/fix_2003_presidential_election_data.R).
- [DINE, resultados 2003](https://www.argentina.gob.ar/dine/resultados-electorales/elecciones-2003).

## Orden recomendado para completar la serie de todas las fuerzas

Transcribir y cotejar las tablas departamentales de Canton ya recuperadas para 1912–1965; el fondo AGN para cubrir vacíos de 1946–1973; y el CD/planillas de INAP–Ministerio y base Escolar para 1983–1999. Después, incorporar fuentes provinciales como Entre Ríos 2001 y cotejar los CSV de 2003 con el escrutinio definitivo. Registrar explícitamente cada hueco por elección, categoría y provincia; no afirmar completitud por tener un mapa coloreado o una tabla nacional agregada.

## Nuevos archivos recuperados en esta iteración

- `raw/canton_1968/`: tomo I original (29.677.707 bytes), tomo II PDF con OCR (7.298.229 bytes), texto OCR de ambos y metadatos de procedencia. El PDF OCR del tomo I falló con error 500, por eso se conserva el PDF original y el OCR separado.
- `entre_rios_diputados_1991_parcial.csv`: 15 unidades, 90 filas; valores vacíos permanecen vacíos. Capital se extrajo del RAR con libarchive. Feliciano no se recuperó. No está completo ni cotejado con actas.
- `entre_rios_diputados_1997_por_departamento.csv`: 16 unidades departamentales tal como aparecen en la fuente y «custodias» separado. Las sumas departamentales difieren del total provincial en 168, 129 y 5 votos respectivamente: esas diferencias coinciden exactamente con el grupo «custodias» (ver original). No asignar ese grupo a un departamento. Capital en los archivos refiere a Paraná. No se impone una correspondencia a límites actuales.
- [Entre Ríos 1991](https://datos.entrerios.gov.ar/dataset/elecciones-1991) y [Entre Ríos 1997](https://datos.entrerios.gov.ar/dataset/eleccion-entre-rios-1997).

Anna’s Archive: se buscó la obra y se intentó consultar el buscador público, que devolvió 403. Eso no permite afirmar que la obra esté ausente. Internet Archive sí proporcionó los dos tomos mediante su catálogo y descargas públicas. También se confirmó la tesis de Andrés Martignano (2023), *Mass Migrations in Argentina*, en Nottingham; su antiguo enlace PDF devuelve 404 y no se obtuvo una base de datos adjunta.

Para armar o corregir los atlas (flujo, reglas del usuario, trampas conocidas): `AGENTS.md`.
