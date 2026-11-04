# Argentina 2021: documentada

Solo cortes o períodos atribuidos explícitamente por las fuentes, sin arrastre temporal. «Documentada» no equivale a oficial ni a validada geométricamente.

5402 entidades GeoJSON; 5402 registros poligonales SHP. 23 distritos con alguna geometría; no implica cobertura total. Ver NOTAS.json para cobertura y limitaciones.

CRS84/EPSG:4326. El GeoJSON conserva los atributos originales y notas completas. El SHP tiene campos breves y un subconjunto de columnas; FUENTE/NOTAS del directorio son parte del conjunto. No se repararon ni disolvieron geometrías; solo se retiraron componentes degenerados (líneas de un punto) que GDAL no puede leer, anotados en depuracion_geometria. Los marcadores sin código se conservan y se identifican.

Campos clave: id_fuente, codigo_distrito, codigo_seccion_fuente, codigo_circuito, anio_fuente_desde/hasta, uso_temporal, calidad_geometria, sistema_codigos. Códigos de sección de fuentes distintas no son intercambiables sin tabla de equivalencias. «Mismo código» no garantiza misma geografía entre años.
