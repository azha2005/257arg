# Catálogo de datos abiertos de la Provincia de Buenos Aires

`elecciones-generales-2005-2023.csv`: «Resultados Generales nivel provincial 2005-2023» del conjunto
`resultados-electorales-provinciales` (Ministerio de Gobierno), bajado el 29-oct-2026 de
https://catalogo.datos.gba.gob.ar/dataset/0db2279b-b3d0-44a8-b985-261fc2e1f0dc/resource/7920d25d-d822-4b19-ae76-45b6379ec143/download/elecciones-generales-2005-2023.csv

Por municipio, lista y cargo (diputados y senadores provinciales, concejales...), con `votantes_habilitados` (incluye
extranjeros, por eso supera al padrón nacional). Codificación latin-1. Los nombres de municipio difieren de los de la
DINE en tres casos (25 de Mayo, General Madariaga, Partido de la Costa): `ALIAS` en `proyeccion/provincial/config.py`.

El catálogo también tiene PASO provinciales 2011–2021 y nacionales 2011–2023 por municipio. Nada de 2025 (consultado
por la API CKAN, `api/3/action/package_search?q=elecciones`).
