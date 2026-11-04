# Circuitos electorales argentinos: serie nacional 2003–2026

Se generaron dos versiones para cada año, en **GeoJSON y SHP**, a pedido del usuario. Los originales se conservan en `../circuitos_busqueda/`. Abrir [INDICE.html](INDICE.html) para elegir año y versión y descargar el ZIP con todos los componentes del SHP.

**Son composiciones reproducibles de fuentes disponibles, no una serie histórica nacional certificada.** La versión aproximada cubre los 24 distritos con alguna geometría; esa presencia no prueba cobertura territorial completa. La documentada puede ser parcial o estar vacía. No se inventaron geometrías para llenar la documentada.

## Las dos versiones

- **Documentada:** incorpora únicamente capas cuyo autor o catálogo atribuye expresamente el año o período solicitado. «Documentada» acredita esa atribución temporal, no que la cartografía sea oficial, exacta o jurídicamente vigente. Galeano incluye reconstrucciones. Por ejemplo, Córdoba capital aporta 2011, 2013–2017 y 2019; no toda Córdoba. Los originales de 2003 sin PRJ no entran en esta versión mediante una proyección supuesta.
- **Aproximada:** elige para cada distrito una fuente temporalmente cercana y completa los faltantes, incluso con geometría posterior. En empate prefiere la anterior; entre fuentes de una misma fecha de referencia prioriza el corte declarado y, para las consultas actuales, sigE sobre el portal anterior. Cada entidad indica el año de origen, la distancia temporal y si hubo arrastre o retroproyección. Se aplican además las capas locales de Córdoba capital cuando tienen mejor evidencia temporal que la base provincial.

**Un cambio entre dos aproximaciones anuales no demuestra que ese año se haya aprobado una modificación electoral.** Puede responder al criterio de cercanía entre fuentes disponibles. En particular, los años tempranos contienen numerosas retroproyecciones. Las fechas de confección de 2003, las copias de repositorio de 2019 y la consulta de 2026 no se presentan como vigencia electoral.

## Archivos por año

```
por_anio/2003/documentada/
por_anio/2003/aproximada/
...
por_anio/2026/documentada/
por_anio/2026/aproximada/
```

Cada directorio contiene `circuitos_argentina.geojson`, `shp/circuitos_argentina.*`, `LEEME.md`, `NOTAS.json` y un ZIP con los componentes disponibles del SHP y sus notas. Cada SHP tiene su propia carpeta. El GeoJSON lleva las notas y atributos completos; el DBF usa nombres cortos y un subconjunto de columnas.

Campos para consultar antes de usar una entidad: `anio_objetivo`, `anio_fuente_desde`, `anio_fuente_hasta`, `uso_temporal`, `distancia_anios`, `id_fuente`, `calidad_geometria`, `sistema_codigos`, `codigo_seccion_fuente`, `codigo_circuito`, `codigo_circuito_original`, `geometria_valida` y `nota_fuente`. Las propiedades originales se conservan en `atributos_originales`.

Los códigos son texto: se conservan letras y ceros. En expresiones como `3396( ex3390)` se separa el código actual del anterior que la propia fuente declara. **INDRA, INDEC y los sistemas de las distintas épocas no se igualan por rellenar ceros.** Tampoco se supone que un código idéntico mantenga los mismos límites. Cada fuente conserva su espacio de códigos.

## Alertas que cambiaron la selección

La comparación detectó diferencias de georreferenciación, además de diferencias de límites o nombres. No se reinterpretaron todos esos movimientos como reformas electorales:

| Variante aislada | Evidencia observada | Decisión |
|---|---|---|
| Galeano CABA 2025 | Los centroides de 167 códigos comunes están a una mediana de 497,84 m de la descarga CNE actual; la versión 2021 difiere una mediana de 1,43 m. | No se selecciona automáticamente 2025. La documentada 2025 deja CABA pendiente. La aproximada recurre a otra fuente, indicando su fecha. |
| Galeano Neuquén 2021 | Mediana de 232,98 m respecto de CNE actual en 155 códigos comunes; la versión 2025 coincide con mediana 0 m en 171. | La documentada 2021 deja Neuquén pendiente; la aproximada usa una alternativa. |
| Copia Neuquén de marzo de 2019 | Mediana de 232,99 m respecto de CNE actual, en 155 códigos comunes. | También se aísla de la selección automática. |
| Portal CNE anterior, Córdoba, consulta 2026 | Los 640 registros tienen el campo circuito nulo. | Se conserva como alternativa, pero se prefiere el sigE, que sí proporciona códigos. |

Estas mediciones son alertas comparativas, **no identifican por sí solas la causa ni prueban la exactitud absoluta de la referencia actual**. No se trasladaron los polígonos para hacerlos coincidir. Los originales y variantes aisladas siguen disponibles. [cambios/auditoria_desplazamientos.json](cambios/auditoria_desplazamientos.json) detalla el contraste entre ediciones; las decisiones se registran también por fuente y año.

Hay geometrías vacías, inválidas y colecciones con líneas ilegibles en las fuentes. Las vacías quedan registradas en `incidencias_ingesta.json` y no aportan geometría al nacional. Cuando GEOS no puede leer una geometría porque trae componentes degenerados (en Galeano 2021, tres circuitos de San Juan con líneas de un solo punto dentro de una colección), se retiran solo esos componentes y queda el detalle en `depuracion_geometria` y en `incidencias_ingesta.json`; el original sigue en `../circuitos_busqueda/`. Hasta el 1-nov-2026 el GeoJSON los conservaba tal cual, y GDAL, QGIS y geopandas no podían abrir los archivos de 2021 a 2023. Las demás colecciones se conservan como vienen y se marca la invalidez. El SHP, por ser poligonal, extrae solo sus componentes poligonales legibles. `NOTAS.json` identifica las colecciones reducidas y omisiones. No se repararon topológicamente los polígonos ni se disolvieron territorios.

## Cobertura territorial

Que estén los 24 distritos no quiere decir que esté toda la provincia. [COBERTURA.md](COBERTURA.md) (generado con `cobertura.py`, que necesita geopandas) da el porcentaje de superficie con algún circuito para cada año y versión. En la aproximada, cinco distritos quedan por debajo del 90 % porque sus fuentes solo traen los circuitos de las localidades, o una parte de la provincia:

- **Río Negro** (~15 % hasta 2025) y **San Luis** (14–22 % hasta 2025).
- **Tierra del Fuego**: 3,4 % de la Isla Grande hasta 2023 (solo Ushuaia y Río Grande).
- **Mendoza**: 69,6 % de 2021 a 2025 (Galeano 2021/2025), contra 99,6 % en los años anteriores.
- **Catamarca**: 84,9 % hasta 2025.

En 2026 (consulta sigE) todos superan el 98 %. Es superficie, no padrón: el área sin circuito es sobre todo rural y despoblada, pero un mapa la muestra vacía.

## Archivos antiguos sin proyección

GeoDa describe su CABA 1999 como Gauss Kruger zona 3, datum Inchauspe: [catálogo original](https://geodacenter.github.io/data-and-lab/buenos-aires_old/). Se utilizó Campo Inchauspe / Argentina 3, EPSG:22193, para esa fuente.

Los SHP aportados por el usuario comparten coordenadas de referencia con aquella CABA, pero carecen de PRJ. La transformación EPSG:22193 → EPSG:4326 se usa **como supuesto explícito solamente en la aproximada**, no como identificación confirmada para cada provincia. No se añadieron PRJ a los originales. Córdoba capital 2011 sí se transforma desde su PRJ propio. Los GeoJSON nacionales y SHP de salida usan CRS84/EPSG:4326.

## Cómo incorporar cambios municipales o de circuitos

La infraestructura permite reemplazar solo la sección o los circuitos afectados. No es necesario sustituir todo el país ni toda una provincia. Se requiere:

1. Un archivo con los polígonos nuevos y los códigos de la fuente, con CRS conocido o una incertidumbre expresamente declarada.
2. El alcance territorial y el período que la evidencia permite atribuirle. Fecha de proyecto, aprobación, publicación y aplicación electoral son datos diferentes.
3. Una regla en `actualizaciones.json`, con fuente, selector, años, nota y enlace de evidencia. El selector identifica el sistema de códigos y las secciones, y opcionalmente los circuitos que se retiran.
4. El número esperado de entidades retiradas en cada versión. Si el resultado no coincide, el constructor se detiene: no superpone ni elimina silenciosamente otra unidad.

`fuentes_adicionales.json` registra capas locales nuevas con esquema `normalizado`: propiedades `codigo_circuito`, `codigo_seccion` y opcionalmente `nombre_seccion`. Los demás datos de registro son `id`, `archivo` (ruta relativa a `circuitos_busqueda/`, o absoluta), `distrito`, `desde`, `hasta`, `documentada`, `alcance`, `esquema`, `crs`, `calidad`, `temporalidad` y `nota`. Un alcance local puede denominarse `actualizacion_local`: no entra como provincia completa, sino mediante su regla de reemplazo.

Ejemplo de **estructura**, no de un cambio aplicado:

```json
{
  "id": "identificador_del_cambio",
  "distrito": "02",
  "desde": 2023,
  "hasta": 2023,
  "versiones": ["documentada", "aproximada"],
  "id_fuente": "capa_local_registrada",
  "selector": {
    "sistemas_codigos": ["galeano"],
    "secciones": ["052"],
    "circuitos": []
  },
  "esperados_retirados": {"documentada": 0, "aproximada": 11},
  "evidencia_url": "URL de la fuente que respalda el cambio",
  "nota": "Alcance, fechas, cobertura y reservas"
}
```

Los archivos de actualización están inicialmente vacíos: no se aplicó una norma nueva sin disponer de la geometría y correspondencia necesarias. El ejemplo no se ejecuta. Un reemplazo local mantiene intactas las demás entidades; **no garantiza por sí solo que los límites exteriores encajen con los vecinos de otra edición**. Esa concordancia debe revisarse antes de dar la actualización por terminada.

## Cambios de códigos frente a cambios de territorio

`cambios/comparacion_2021_2025.json` compara las claves dentro de la misma colección y distingue geometrías codificadas iguales, diferencias geométricas bajo la misma clave y claves presentes solo en uno de los cortes. `candidatos_renumeracion.json` identifica coincidencias geométricas exactas entre claves distintas; son candidatos, no una tabla de equivalencias electorales certificada. Cambios de precisión, sección atribuida, reconstrucción o proyección también generan diferencias.

Ejemplo comprobable en los archivos: la sección 052 bonaerense, General San Martín, pasa de 11 a 12 circuitos entre las dos ediciones; desaparecen 383 y 388 y aparecen 388A, 388B y 388C. El [aviso oficial publicado el 25 de junio de 2025](https://www.boletinoficial.gob.ar/pdf/aviso/primera/321063/20250625) describe ese proyecto y otras modificaciones. Se conserva como evidencia para estudiar la cronología, sin trasladar automáticamente los límites nuevos a los años intermedios.

Otro ejemplo de por qué hay que distinguir fechas: la [Resolución 80/2024 del Ministerio del Interior](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-80-2024-398659/texto), publicada el 29 de abril de 2024, trata subdivisiones de La Capital, Santa Fe, cuyo proyecto había sido aprobado por la CNE en mayo de 2022. Una sola de esas fechas no basta para atribuir la geometría a una elección concreta.

## Reproducibilidad y controles

```
python geometria/circuitos_serie/build.py
python geometria/circuitos_serie/auditar_georreferenciacion.py
python geometria/circuitos_serie/test_serie.py
python geometria/circuitos_serie/finalizar.py
```

El constructor no cambia las fuentes. `--solo-anios=2024,2025,2026` sirve para regenerar años concretos, conservando las salidas verificadas de los demás; una modificación de reglas que alcance años anteriores exige regenerarlos también. `--reanudar` sirve para una generación interrumpida sin cambios de criterio. No usarlo para saltarse años afectados por una regla nueva.

Se controlan conteos GeoJSON/SHP, hashes, lectura de componentes, cobertura por distrito, atribución de fuente y ausencia de extrapolaciones en la documentada. Las pruebas verifican la selección temporal, sustitución local, rechazo de retiros inesperados, conservación de huecos en SHP y retiro de una línea de un punto sin perder el polígono, con el GeoJSON legible por GEOS. Estos controles no validan todos los límites ni resuelven todos los huecos o solapes.

Los originales de fuentes diferentes conservan sus licencias: Galeano CC BY 4.0; GeoDa y el aporte del usuario requieren consultar condiciones originales; CNE, sigE y las fuentes locales mantienen su atribución y condiciones de origen. Esta composición no impone una licencia única a todo el material. Ver el registro de fuentes y los [informes de recolección](../circuitos_busqueda/LEEME.md).
