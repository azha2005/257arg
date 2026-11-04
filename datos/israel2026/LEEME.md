# Israel: resultados de elecciones a la Knesset

## Elección del 27 de octubre de 2026

Consulta del 27 de octubre de 2026, alrededor de las 20:30 UTC. El portal de la
Comisión Electoral Central, abierto en el navegador, mostraba «esperando el
recuento de votos». Advierte que los resultados pueden cambiar y que los
definitivos se publicarán a más tardar el 4 de noviembre.

- Portal: https://votes26.bechirot.gov.il/cityresults?lang=he
- Archivo por localidad, enlazado por el portal: https://media26.bechirot.gov.il/files/expc.csv
- Archivo por mesa, enlazado por el portal: https://media26.bechirot.gov.il/files/expb.csv

Los dos archivos devolvieron HTTP 404 en la conexión directa y los enlaces del
portal se intentaron también en el navegador. No se obtuvo ningún resultado
de 2026. El host `cdn-votes26` mostraba previamente un **entorno de pruebas**:
sus cifras no deben confundirse con el escrutinio real.

`python datos/israel2026/descargar_2026.py` intenta guardar ambos CSV cuando
estén disponibles, con fecha UTC y SHA-256 en `instantaneas/`. Rechaza páginas
HTML y archivos muy pequeños; aun así se debe comprobar el contenido y su
carácter provisional. Los archivos se guardan sin alterar su codificación.
La ruta `expb.csv` se confirmó en el enlace del sitio oficial; su contenido
solo podrá verificarse cuando esté disponible.

## Histórico oficial

El catálogo https://data.gov.il/api/3/action/package_show?id=votes-knesset
ofrece 17 recursos de las Knesset 16 a 25: por mesa en todos los casos y por
localidad para las Knesset 19 a 25. `catalogo_ckan.json` conserva los metadatos
del catálogo e `inventario.json` relaciona cada recurso con su archivo,
cantidad de filas y SHA-256. Los resultados de `historico_ckan/` son JSON UTF-8
con los campos y registros devueltos por la API; no son los CSV originales.
Incluyen los nombres y códigos en hebreo tal como los publica la fuente.

La API usada es `https://data.gov.il/api/3/action/datastore_search` con
`resource_id`, `limit` y `offset`; se paginaron todos los registros y se
comparó el número descargado con el `total` informado por la API. Para repetir:
`python datos/israel2026/descargar_historico.py`. La descarga histórica no
contiene la elección de 2026 y no debe interpretarse como resultado actual.
