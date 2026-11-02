# Búsqueda de faltantes presidenciales — 2 de noviembre de 2026

**Actualización: todos los casos resueltos.** Tras la búsqueda inicial, el usuario autorizó expresamente consultar la CNE y un subagente descargó las doce tablas de sección completa de los balotajes. Ya se incorporaron; ver [fuentes CNE y padrón transcrito](cne/LEEME.md) y [control de las doce tablas](cne/CONTROL_INCORPORACION.json). `herramientas/incorporar_cne_balotajes.py` permite repetir la incorporación. El resto de este documento conserva el diagnóstico previo y la lista de consultas que se necesitaban; ya no son faltantes actuales.

## Resuelto: Sarmiento, Santiago del Estero, 2007

Se recuperó el documento original de la DINE `Sgo_Estero_28_Oct_07.pdf` del archivo de Internet:

- [PDF oficial archivado](https://web.archive.org/web/20110902192330id_/http://www.elecciones.gob.ar/estadistica/archivos/2007/Sgo_Estero_28_Oct_07.pdf).
- Archivo local: `sgo_estero2007_definitivo.pdf`; página **31**, columna **PRESIDENTE Y VICE — TOTAL** (ambos sexos), no las columnas de senadores/diputados ni los parciales por sexo.
- Se renderizó y cotejó la página (`sarmiento2007.png`). La tabla cierra: 1424 positivos + 38 blancos + 5 nulos = 1467 votantes; 2615 electores; 56,10 % de participación.
- FPV 1299; CC 45; UNA 33; Sobisch 16 (MPU 10 + MAV 4 + Unión Popular 2); MST 8; Recrear 7; FRAL 6; PTS-MAS 4; FREJULI 2; PO 2; MIJD 2. Los demás no tienen votos en la tabla presidencial.
- Se reemplaza **toda** la tabla dudosa de PolAr. No se reinterpretan los dos 999, ni se imputan cifras por residuo. `../complementos.json` contiene la transcripción y la marca explícita `reemplazar`.
- El atlas `mapa2007pres` queda sin departamentos pendientes. El ensayo por circuito de 2007 continúa fuera del sitio y no fue modificado.

## XLS descargados por el usuario

Se revisaron los encabezados de todos los `zona_*.xls` de `C:/Users/JC/Downloads/`, incluidos los nombres duplicados con `(1)` y `(2)`, y sus copias del proyecto. Fecha, jurisdicción, sección y categorías quedan registradas, con SHA256, en `inventario_xls_descargas.json`.

| Archivo de Descargas | Elección que realmente contiene |
|---|---|
| `zona_secc_00008.xls` | Jujuy, Valle Grande, general 22/10/2017 |
| `zona_muni_0032.xls` | Catamarca, Antofagasta de la Sierra, general 27/10/2019; su columna presidencial ya completa el atlas 2019 |
| `zona_secc_00009.xls` | Chaco, Tapenagá, general 14/11/2021 |
| `zona_muni_0032 (1).xls` | Antofagasta de la Sierra, PASO 11/08/2019 |
| `zona_muni_0032 (2).xls` | Antofagasta de la Sierra, PASO 12/09/2021 |
| `zona_secc_00004.xls` | Chubut, Gastre, PASO 12/09/2021 |
| `zona_secc_00006 (1).xls` | Chaco, Presidencia de la Plaza, PASO 11/08/2019 |
| `zona_secc_00016.xls` | Catamarca, Santa María, PASO 11/08/2019 |
| `zona_secc_00018.xls` | Chaco, General Belgrano, PASO 11/08/2019 |
| `zona_secc_00006.xls`, `zona_circ_0001.xls`, `zona_circ_0502.xls` | Generales 26/10/2025: Presidencia de la Plaza, Comuna 1 y Tolhuin |

No se encontró en esos XLS una segunda vuelta de 2015 o 2023. Los archivos `presentacionDeResultados*.csv` de Descargas contienen PASO 2013, general 2021, general 2023 y balotaje 2023 de Florencio Varela; no completan los departamentos pendientes. `Query resultsee1*.xlsx` corresponde al provisorio presidencial 2007 ya conocido y repite el dato dudoso de Sarmiento.

## Balotajes que siguen pendientes

Se contrastaron el agregado de la DINE y las actas públicas de la CNE. Las cinco actas de segunda vuelta 2023 de Catamarca, Chubut, Jujuy, La Pampa y Salta sólo publican totales provinciales: **no permiten separar los departamentos faltantes**. Los PDF, el índice de origen y sus URL quedaron guardados (`actas2023_fuentes.json`). No se restan provisorios departamentales a un definitivo provincial.

[Actas oficiales de segunda vuelta 2023](https://www.electoral.gov.ar/nuevo/paginas/btn/actas_esc_segvta2023.php).

Consultas departamentales que faltan en [CNE, consulta por zona](https://www.padron.gob.ar/publica/), categoría Presidente y Vice, padrón normal:

| Elección | Distrito | Sección | Departamento |
|---|---|---:|---|
| Segunda vuelta 22/11/2015 | Catamarca (03) | 014 | Antofagasta de la Sierra |
| Segunda vuelta 22/11/2015 | Jujuy (10) | 008 | Valle Grande |
| Segunda vuelta 22/11/2015 | Salta (17) | 006 | Rivadavia |
| Segunda vuelta 22/11/2015 | Salta (17) | 010 | Santa Victoria |
| Segunda vuelta 19/11/2023 | Catamarca (03) | 014 | Antofagasta de la Sierra |
| Segunda vuelta 19/11/2023 | Chubut (07) | 011 | Florentino Ameghino |
| Segunda vuelta 19/11/2023 | Chubut (07) | 004 | Gastre |
| Segunda vuelta 19/11/2023 | Chubut (07) | 003 | Telsen |
| Segunda vuelta 19/11/2023 | Jujuy (10) | 016 | Susques |
| Segunda vuelta 19/11/2023 | Jujuy (10) | 008 | Valle Grande |
| Segunda vuelta 19/11/2023 | La Pampa (11) | 009 | Curacó |
| Segunda vuelta 19/11/2023 | Salta (17) | 010 | Santa Victoria |

La tabla enumera las consultas necesarias; no afirma que cada elección esté disponible en el sistema. Las consultas con captcha son manuales, conforme a la regla del proyecto. Cuando haya un XLS, se leerá la columna presidencial de la fecha exacta y se verificará su cierre antes de incorporarlo. Mientras tanto, los doce casos siguen en beige y rotulados.
