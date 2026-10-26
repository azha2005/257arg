# Diputados nacionales 2009

Elección del 28 de junio de 2009. Atlas autocontenido en `atlas_2009.html`, datos en `dataset_2009.json`. Seis vistas: ganador, FPV, ACyS, Peronismo Federal, Unión PRO y participación. Nueve fuerzas en la leyenda, todas con al menos una unidad ganada y con logo.

## Cobertura y fuentes

**526 unidades electorales con votos**, más Malvinas en gris: 15 comunas de Capital, partidos y departamentos de las 23 provincias y Antártida Argentina con ficha y resultado propios. Sin provincias en color sólido ni departamentos beige. No se imputaron votos.

- Fuente principal: `datos_oficiales/2009/agregado_polar.pkl`, preparado por `agregar_polar.py` a partir de PolAr_Data (electorArg, INDRA / Atlas Electoral de Andy Tow), escrutinio provisorio por mesa.
- Buenos Aires: todas las listas de los 134 municipios, recuperadas de **`<disco externo>/Merged file (15).xls`, hoja `Sheet1`, año 2009, elección DN**. Copia íntegra y sin modificar en `datos_oficiales/2009/complementos/merged_file_15_original.xls`. La procedencia anterior de esta planilla no está documentada; sus cifras son compatibles con el definitivo territorial. No se certifica su origen oficial. Se reemplazó la provincia completa, evitando mezclar listas provisorias y definitivas en el mismo municipio.
- Valle Grande (Jujuy): todas las listas de la misma planilla, 1.734 positivos, 49 blancos, 12 nulos y 1.795 votantes. En PolAr estaban todas en cero.
- Tierra del Fuego: reemplazo completo con el [PDF definitivo de la DINE](https://www.argentina.gob.ar/sites/default/files/tierra_del_fuego_28_de_junio_de_2009.pdf), páginas 6 (Río Grande), 7 (Antártida) y 8 (Ushuaia), transcritas y verificadas visualmente. Positivos: 32.667, 142 y 28.073, respectivamente. Cada tabla cierra al voto. La Antártida tiene ocho votos impugnados de Orcadas informados aparte y sin escrutar; no se transforman en votos a partidos. Exterior y privados de libertad están separados en el PDF y no se asignan a departamentos.
- El cartel nacional conserva los subtotales de la [tabla de Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2009), mediante `wikitop.WIKI[2009]`. La instantánea de wikitext es `wikileg/wleg2009.txt`, copiada como `w2009.txt`. También se conserva el XLSX nacional y provincial de la DINE en `complementos/`, utilizado para cotejar Buenos Aires y Tierra del Fuego.

La búsqueda local examinó 211 libros de carpetas locales y de un disco externo, además de copias y archivos comprimidos pertinentes. Las planillas `<disco externo>/REGIONES/2009DIPUTADOS\2009PBA.xls` y `.xlsx` omitían Nuevo Encuentro; no se usaron para completar ese partido. La copia antigua de PolAr conserva los mismos NA que la descargada para el proyecto. El inventario y los resultados de la búsqueda quedan en `busqueda_fuentes/`.

## Correcciones de la planilla recuperada

No se alteró el XLS original. La preparación reproducible está en `datos_2009.py`.

1. General Rodríguez: siete números estaban almacenados como decimales con separador de miles mal interpretado. Se normalizaron **15.665 → 15.665 votos, 9.983 → 9.983, 1.030 → 1.030, 5.446 → 5.446, 34.446 → 34.446, 2.256 → 2.256 y 37.262 → 37.262**: en almacenamiento, por ejemplo, 1.030 era el número decimal 1,03. Después de multiplicar esos siete valores por mil, todas las listas suman exactamente los positivos y positivos + blancos + nulos suman los votantes. No es una imputación de partido por residuo.
2. General Alvarado tenía código 40, duplicado con General Alvear. Se restituyó 39 por nombre y contraste con PolAr; no se fusionaron ambos municipios.
3. San Isidro aparece como «S. NICOLAS» con código 106; San Nicolás aparece por separado con código 107. Se conservan los códigos y se usa el nombre validado contra PolAr. «MOROM» se identifica como Morón por su código.
4. Las 134 tablas bonaerenses cierran individualmente: listas = positivos y positivos + blancos + nulos = votantes. El total territorial es 7.512.153 positivos frente a 7.515.293 en la tabla provincial completa de la DINE. Nuevo Encuentro suma 415.856 territoriales frente a 415.961 del total provincial; no se asignan esos 105 votos restantes a ningún municipio.

## Agrupaciones y diferencias nacionales

`mapeo_listas_2009.csv` conserva cada lista, código, provincia, grupo y votos; `control_bloques_2009.csv` compara todas las agrupaciones de la base con Wikipedia. Se parte del cruce existente de `wikileg/bloques_prov.py` y se corrigen explícitamente Misiones (Frente Justicialista de la Dignidad y el Progreso → FPV; Frente de la Esperanza → MID), Santiago del Estero (Acuerdo Cívico–Unidad Popular → ACyS) y Corrientes (Encuentro por Corrientes y PDP → ACyS). Los bloques suman las listas aliadas aunque se presentaran separadas, como la tabla nacional.

| Bloque ganador | Base del mapa | Wikipedia | Diferencia |
|---|---:|---:|---:|
| ACyS | 5.902.965 | 5.705.105 | +197.860 |
| FPV | 5.615.923 | 5.544.069 | +71.854 |
| Unión PRO | 3.675.854 | 3.675.747 | +107 |
| Peronismo Federal | 1.587.503 | 1.560.298 | +27.205 |
| Proyecto Sur | 439.020 | 448.711 | −9.691 |
| Nuevo Encuentro | 415.856 | 415.961 | −105 |
| FRC | 209.703 | 212.621 | −2.918 |
| MPN | 77.058 | 78.703 | −1.645 |
| UdN–FG | 24.033 | 24.496 | −463 |

La tabla de Wikipedia presenta discrepancias internas: las filas componentes de ACyS suman **5.875.774**, pero su subtotal impreso es **5.705.105**; las de FPV suman **5.698.942**, frente al subtotal **5.544.069**. Esto explica parte de las diferencias con el mapa; el resto combina diferencias de escrutinio, cobertura de votos auxiliares y las asignaciones documentadas. No se afirma igualdad exacta ni se modificaron cifras para forzarla. Los positivos de las fuentes territoriales suman 19.637.305, frente a 19.326.863 impresos en Wikipedia. Además, positivos + blancos + anulados + ocho impugnados de Wikipedia no suman sus 20.477.584 votantes; se conservan sus cifras originales y su participación calculada sobre 27.942.194 inscriptos.

Ganadores: FPV 217; ACyS 146 (incluye Antártida); PRO 104; Peronismo Federal 28; FRC 16; MPN 11; Proyecto Sur 2; Nuevo Encuentro 1 (Morón, 39,23 %); UdN–FG 1. Las demás fuerzas permanecen en la ficha de cada unidad y se agrupan como «otros» en el cartel nacional.

## Geometría, estilo y logos

Build derivado de 2013. Shapefile `Departamentos_2010`, con 15 comunas de Capital, sin dividir Lezama (creado después de la elección). Los partidos nuevos del GBA y San Salvador tienen polígono propio. Los siete recuadros del proyecto, Malvinas en gris y la Antártida polar siguen el estilo 1995/1999. Los zooms usan esa geometría y no son una reproducción exacta del dibujo original de Wikipedia.

Colores de Wikipedia: ACyS rojo, FPV celeste, PRO amarillo, Proyecto Sur verde, Nuevo Encuentro cian y FRC azul. Excepciones para contraste: Peronismo Federal violeta en lugar de gris; UdN–FG ámbar; MPN turquesa oscuro, como el atlas 2013. Leyenda compacta de nueve filas, adelantada para evitar recortes. Los seis primeros logos son los de la infobox de 2009; para FRC, MPN y UdN–FG se usan los del partido, con la reserva de época del proyecto. Se consultó `DateTimeOriginal` antes de usarlos. Licencias, fechas posteriores y diseños no verificados se documentan en `logos_wikipedia/LICENCIAS.md`; respuesta original de Commons en `logos_metadata.json`. El logo de UdN–FG representa al Frente Grande, no es un emblema específico de la alianza.

La participación departamental usa electores de PolAr, excepto Tierra del Fuego, que usa DINE. Para Buenos Aires y Valle Grande combina los votos recuperados con los electores de PolAr; no se presenta como padrón definitivo certificado.

## Salidas y validación

- HTML y JSON: `python mapa2009/build_2009.py`. `preparar_atlas2009.py` permite volver a derivar el build desde el de 2013; no altera la plantilla común.
- PNG transparentes: `png_transparentes/mapa2009/`; blancos: `png_blanco/mapa2009/` y copias en `png_transparentes/all elections white bg/`.
- Commons: `commons/2009/subir/`, seis modos en SVG con y sin leyenda, PNG y descripciones. Licencias CC BY 4.0 + CC BY 2.5 Argentina para la geometría, y las licencias propias de cada emblema. Preparado localmente, **sin subir**.
- Verificado: ninguna unidad sin geometría, ningún polígono electoral sin datos, 526 unidades con votos, nueve logos embebidos, los seis modos activos y sin errores JavaScript. Revisión visual de las seis vistas, la leyenda, las pestañas, Capital, AMBA y los recuadros. `commons/chequeo.py 2009` comprueba SVG compatibles y genera muestras con otro renderizador.
