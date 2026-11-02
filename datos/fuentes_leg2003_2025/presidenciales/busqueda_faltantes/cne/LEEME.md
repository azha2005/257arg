# Consulta CNE de secciones pendientes

Las doce secciones ya están incorporadas a los atlas nacionales de balotaje 2015 y 2023. Reproducción: `python herramientas/incorporar_cne_balotajes.py`, seguida de los constructores `2015bal` y `2023bal`. Votos, fecha, identidad, cierre, participación y SHA256 de cada XLS se verifican en `CONTROL_INCORPORACION.json`.

Fuente: [Consulta de Escrutinios Definitivos](https://www.padron.gob.ar/publica/), consultada el 2 de noviembre de 2026. Filtros: distrito indicado, segunda vuelta de la fecha indicada, «Consulta por Zona», sección electoral indicada y localidad o circuito en blanco (toda la sección). Categoría Presidente y Vice. Cada XLS es la exportación «A OpenOffice Calc», renombrada para conservar elección, distrito y sección sin sobrescribir otras descargas.

La pantalla muestra los inscriptos, pero los XLS descargados dejan vacía esa cifra. Los valores de inscriptos de la tabla siguiente fueron transcritos de la pantalla de resultados, no calculados a partir de la participación. Votos y total pueden cotejarse además en los XLS. Recurridos e impugnados son cero en las doce consultas.

| Año | Distrito y sección | FPV / UP | Cambiemos / LLA | Blancos | Nulos | Total emitido | Inscriptos |
|---|---|---:|---:|---:|---:|---:|---:|
| 2015 | Catamarca 014 Antofagasta de la Sierra | FPV 413 | Cambiemos 348 | 1 | 4 | 766 | 1199 |
| 2015 | Jujuy 008 Valle Grande | FPV 1098 | Cambiemos 755 | 8 | 55 | 1916 | 2642 |
| 2015 | Salta 006 Rivadavia | FPV 14005 | Cambiemos 1767 | 42 | 50 | 15864 | 22850 |
| 2015 | Salta 010 Santa Victoria | FPV 3351 | Cambiemos 1206 | 26 | 56 | 4639 | 7896 |
| 2023 | Catamarca 014 Antofagasta de la Sierra | UP 431 | LLA 465 | 13 | 16 | 925 | 1800 |
| 2023 | Chubut 003 Telsen | UP 350 | LLA 360 | 5 | 20 | 735 | 1418 |
| 2023 | Chubut 004 Gastre | UP 276 | LLA 265 | 8 | 12 | 561 | 1134 |
| 2023 | Chubut 011 Florentino Ameghino | UP 378 | LLA 544 | 17 | 18 | 957 | 1519 |
| 2023 | Jujuy 008 Valle Grande | UP 1276 | LLA 624 | 23 | 39 | 1962 | 2906 |
| 2023 | Jujuy 016 Susques | UP 960 | LLA 1134 | 19 | 109 | 2222 | 3479 |
| 2023 | La Pampa 009 Curacó | UP 396 | LLA 229 | 1 | 8 | 634 | 892 |
| 2023 | Salta 010 Santa Victoria | UP 2436 | LLA / Ahora Patria 2050 | 36 | 60 | 4582 | 8231 |
