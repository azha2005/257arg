# Cartografía argentina: circuitos, radios, departamentos y municipios

Recolección del 31 de octubre de 2026. Prioridad desde 2003, conservando también los históricos anteriores. Las descargas originales están separadas por fuente y sus coordenadas y atributos se conservaron. No se reemplazó la geometría de ningún atlas.

**Para usar los SHP, abrir el [catálogo por año y capa](../catalogo_shp/LEEME.md).** Cada carpeta contiene un único shapefile con sus componentes, procedencia, criterio del año y hashes. Incluye las dos recolecciones y las capas históricas preexistentes de `geometria/`. Las repeticiones de fuentes se conservan y están identificadas; no representan delimitaciones distintas.

También hay un [índice HTML filtrable](../catalogo_shp/CATALOGO.html) por año, tipo y nombre de archivo/localidad. Resultado final: **2.621 carpetas de SHP**, con **9.664 componentes** (2,20 GB) y **2.567 conjuntos de componentes distintos**. Se verificó identidad SHA-256 de cada copia. 61 carpetas quedaron sin año comprobado; 1.239 carecen de PRJ en su fuente, principalmente plantas urbanas IPEC 2010. Se señala cada ausencia sin inventar un CRS. El total incluye manzanas y ejes auxiliares: no son 2.621 colecciones de circuitos.

Los GeoJSON, KML, GPKG y demás originales siguen disponibles en esta carpeta y en [circuitos_busqueda](../circuitos_busqueda/LEEME.md). No se convirtieron a SHP para hacerlos pasar por originales. [INVENTARIO.md](INVENTARIO.md) lista las capas nuevas; [metadatos/descargas.json](metadatos/descargas.json) registra URLs, tamaños, licencias declaradas, hashes y errores. [plan_descargas.json](plan_descargas.json) contiene las notas de selección. Los conteos describen registros, no garantizan cobertura territorial ni exactitud topológica.

## Cobertura recuperada

| Familia | Cortes recuperados | Archivos / fuente | Precisiones |
|---|---|---|---|
| Circuitos electorales | Entre Ríos 1995/1999; CABA 1999/2015 y capa histórica rotulada 2006; Buenos Aires 2001/2003; Córdoba capital 2011/2013–2017/2019; copias 2019/2021; conjuntos nacionales declarados 2021/2025; actuales sin vigencia comprobada | [Colección e informe de circuitos](../circuitos_busqueda/LEEME.md) | Las series nacionales 2021/2025 incluyen reconstrucciones. No se consiguió cartografía nacional independiente para cada elección desde 2003. |
| Radios censales nacionales corregidos | 1991, 2001, 2010, 2022 | `conicet/radios/`, [CEUR-CONICET](https://ri.conicet.gov.ar/handle/11336/149711) | Edición V2025-1. Son reconstrucciones corregidas y estandarizadas sobre fuentes INDEC, no originales sin modificar. |
| Radios censales nacionales, edición anterior | 1991, 2001, 2010 | `ceur_legacy/`, copia fijada al commit de enero de 2021 de [argentina-geography](https://github.com/matuteiglesias/argentina-geography) | Otra edición de los mismos censos, no tres censos adicionales. Origen CEUR. Fechas y commit completos en el manifiesto. |
| Radios censales oficiales | 2010: las 24 jurisdicciones; 2022: nacional | `indec/2010/`, `indec/2022/`; [INDEC Codgeo](https://www.indec.gob.ar/indec/web/Institucional-Indec-Codgeo), [GeoNode INDEC](https://geonode.indec.gob.ar/layers/geonode_data:geonode:radios_censales2) | 2010 suma 52.408 registros en las 24 descargas; 2022 tiene 66.515. No coinciden exactamente con CEUR. |
| Fracciones censales oficiales | 2022 | `indec/2022/fracciones_censales.zip` | 6.571 registros. Complemento útil para agregación; no circuito electoral. |
| Precenso de viviendas | Operativo 2019–2020 | `indec/precenso_2019_2020/`; [descargas INDEC](https://precensodeviviendas.indec.gob.ar/descargas) | 39.612 radios, 529 departamentos y 1.093 localidades. Cobertura del operativo centrada en localidades de 2.000 habitantes o más; los polígonos departamentales no prueban datos completos. No se afirma que sus límites sean nuevos de 2020. |
| Radios provinciales y CABA | PBA 2010/2022, CABA 2001/2010, Neuquén 2022 | `pba/radios/`, `caba/`, `neuquen/` | Originales oficiales alternativos, SHP y formatos adicionales. CABA: 3.409 y 3.554 radios. Neuquén: 1.075. |
| Plantas urbanas de Santa Fe | Portales IPEC 2010 y 2022 | `santafe/ipec/`, [IPEC](https://www.estadisticasantafe.gob.ar/contenido/cartografia-censal/) | Se recuperaron los 816 ZIP enlazados: 406 bajo 2010 y 410 bajo 2022. Incluyen radios, manzanas y ejes de calles. No son ejidos municipales. Las notas internas de la muestra 2022 aún mencionan 2010 y campos 2020: se conserva esa discrepancia sin inventar vigencia. |
| Radios 2001, subconjunto con datos | 2001 | `boccolini_2001/`; [CONICET, Boccolini](https://ri.conicet.gov.ar/handle/11336/284090) | GeoPackage de 34.182 radios con densidad superior a 1 hab/ha. No es una capa nacional íntegra. Geometría INDEC declarada sin modificar; atributos derivados. |
| Radios GeoParquet | 1991, 2001, 2010, 2022 | `source_cooperative/`; [Nissim Lebovits / Source Cooperative](https://source.coop/nlebovits/censo-argentino) | Derivados de la geometría CEUR-CONICET reproyectados a EPSG:4326, no una fuente independiente de límites. Se conservaron README y metadatos STAC de cada corte. |
| Departamentos históricos | 1869, 1895, 1914, 1947, 1960, 1970, 1980, 1991, 2001, 2010, 2022 | `conicet/deptos/Base_deptos_1869-2022.zip`; [Rodríguez / CONICET](https://ri.conicet.gov.ar/handle/11336/149867) | Incluye variantes IPUMS 1970/1980 y secciones de Capital Federal 1960. Se conservó también el ZIP 1947 anidado. La edición actual no reemplazó los archivos preexistentes. |
| Departamentos actuales y oficiales 2022 | Nacional; Neuquén | `indec/2022/departamentos.zip`, `georef_actual/departamentos.geojson`, `neuquen/departamentos_202610.zip` | Nacional: 529 registros. Neuquén: 16, etiquetados 2022 en el visor aunque el nombre técnico termina en 202610. |
| Municipios | 2017 y 2022 | `poblaciones/Municipios_2017.zip` y `Municipios_2022.zip`; [Poblaciones, b2](https://n2t.net/ark:/26680/b2) | 1.135 y 1.205 registros. No incluyen necesariamente todas las otras categorías de gobierno local. |
| Otras formas de gobierno local | 2022 | `poblaciones/Gobiernos_locales_2022.zip`; [Poblaciones, b19](https://n2t.net/ark:/26680/b19) | 2.078 registros. No sumar mecánicamente a municipios: pueden existir relaciones espaciales y definiciones diferentes entre capas. |
| Gobiernos locales oficiales | 2022 | `indec/2022/gobiernos_locales4.zip`; [GeoNode INDEC](https://geonode.indec.gob.ar/layers/geonode_data:geonode:gobiernos_locales4) | 2.282 registros; la ficha informa 49 entidades sin representación espacial en Entre Ríos, Formosa y Río Negro. Coincidir con WFS hits no elimina esa limitación. |
| Municipios y gobiernos locales, sin corte comprobado | Snapshot descargado en 2026 | `georef_actual/`; [Georef](https://www.argentina.gob.ar/georef/descarga-de-la-base-completa) | GeoJSON de municipios legacy: 2.082 polígonos; gobiernos locales v2: 2.280. Son polígonos comprobados. Las consultas con centroides no se cuentan como límites. |
| Radios municipales/comunales | Snapshot actual, servicio documentado desde 2019 | `cordoba/radios_municipales_comunales_actual.zip`; [IDECOR](https://www.idecor.gob.ar/usa-y-descarga-los-limites-oficiales-de-las-localidades-de-cordoba/) | 427 registros jurídicos municipales/comunales; no son radios censales ni circuitos. No asignar 2019 a la descarga actual solo por la fecha del artículo. |
| Gobiernos locales provinciales | Neuquén 2022 | `neuquen/gob_locales_2022.zip`; [visor DPEyC](https://www.estadisticaneuquen.gob.ar/apps/visor/) | 57 registros. Se preserva la fuente provincial además de las colecciones nacionales. |

## Diferencias comprobadas entre ediciones de radios

| Censo | CEUR copia existente en 2021 | CEUR V2025-1 | INDEC descargado ahora |
|---|---:|---:|---:|
| 1991 | 40.160 | 40.099 | — |
| 2001 | 46.591 | 46.582 | Solo CABA y subconjunto de Boccolini; no nacional original completo independiente |
| 2010 | 52.401 | 52.406 | 52.408 (24 ZIP provinciales) |
| 2022 | — | 66.502 | 66.515 |

No se determinó que estas diferencias sean errores: hay correcciones, cambios de edición y criterios distintos. Las notas de CEUR están descargadas en `conicet/radios/NOTAS_VERSION_2025-1.docx`. La tabla de esa nota y el ZIP actual de 2010 difieren en cuatro registros: aquí se informa el conteo efectivo del SHP (52.406), sin alterar el archivo.

## Fechas, calidad y licencias

El año censal, el año de publicación y la vigencia de una delimitación son datos distintos. La organización por año indica su criterio en cada `FUENTE.json`. Los snapshots de repositorio solo prueban que esa copia existía entonces. Los archivos sin evidencia de año van a `sin_fecha_verificada`. No se multiplicaron capas actuales para llenar años faltantes.

Se verificaron CRC de ZIP, hashes SHA-256, lectura SHP/SHX/DBF y cantidades de registros; el GeoPackage pasó `PRAGMA quick_check` y se leyeron las cabeceras y metadatos GeoParquet. Cuatro capas nacionales INDEC 2022 coinciden con el conteo WFS hits. Los RAR se leyeron sin modificar sus componentes. No se comprobó la topología completa ni la concordancia legal de todos los límites, y no se repararon geometrías. Las capas del ZIP original del usuario carecen de PRJ: se conservan sin asignar una proyección supuesta.

CEUR-CONICET y Boccolini: CC BY 2.5 Unported según registros; Poblaciones: CC BY 4.0 según metadatos; PBA: CC BY 4.0; Buenos Aires Data: CC BY 2.5 Argentina. IDECOR declara CC BY-SA en sus metadatos, con versión a cotejar antes de publicación. Para INDEC, IGN y otros servicios revisar la ficha correspondiente: esta recolección no impone una licencia única a materiales de distinta procedencia.

## Búsquedas sin recuperación y límites de exhaustividad

- No se recuperó una serie municipal nacional anual desde 2003 ni un corte nacional explícito 2003/2018. Un catálogo publicado en 2018 con actualización semanal no demuestra que su descarga actual conserve esa geometría histórica.
- Las descargas directas IGN `municipio.zip` y `departamento.zip` fallaron por resolución DNS en esta sesión. Georef y Poblaciones son alternativas, pero no se presentan como copias idénticas de esos archivos.
- Georef v2 `municipios.geojson` devolvió 404; la descarga legacy sí funcionó. Las consultas que devuelven puntos no reemplazan los polígonos.
- El artículo de Rodríguez sobre comparabilidad retrospectiva describe fracciones reconstruidas de CABA 1970/1980. El antiguo Drive enlazado no se pudo recuperar mediante el conector: no se cuentan esos archivos como descargados. El registro CONICET de frecuencias 1980 contiene tablas; no prueba una cartografía nacional de radios 1980 disponible.
- Los 816 paquetes urbanos enlazados por IPEC se descargaron. IDESF también posee distritos municipales/comunales: las fichas de identificadores CSV encontradas no se contaron como polígonos; el portal de descargas redirigió al inicio de sesión provincial. No se atribuye cobertura de ejidos a los radios urbanos de IPEC.
- East View comercializa GIS censales; se identificó como alternativa sin recuperación de archivos. No se convirtieron sus etiquetas comerciales ADM en municipios legales. Source Cooperative sí se incorporó como GeoParquet derivado, con procedencia declarada.
- Los históricos de circuitos no recuperados, fuentes con HTTP 401, errores, WFS deshabilitado y propuestas sin aprobar están detallados en el [informe específico](../circuitos_busqueda/LEEME.md).

Esta es una recolección amplia de fuentes recuperables, no una prueba de que no existan más archivos en archivos provinciales, repositorios privados o publicaciones no indexadas.

## Reproducción

`descargar.py --new-only` incorpora recursos nuevos del plan sin repetir los errores antiguos. `inventariar.py` relee los originales y genera conteos. `organizar_shp.py` copia los componentes al catálogo y verifica identidad de bytes, sin cambiar los originales. `indice_catalogo.py` genera el índice HTML filtrable y los inventarios anuales. Los scripts de descubrimiento y los JSON de `metadatos/` conservan las rutas y respuestas utilizadas. Reejecutarlos puede descargar una versión posterior de servicios vivos; no debe confundirse con el snapshot de esta sesión. La dependencia NumPy necesaria para leer GeoParquet está aislada en `_deps/`; no se sustituyó la instalación global del proyecto.
