# Bordes de 1868-1886: de hecho y de derecho

Informe de fuentes (8-nov-2026, pedido del usuario). No hay geometría todavía, solo fuentes y criterio.

## Lo que hoy usan los atlas

- 1868, 1874 y 1880: `Departamentos_1869.shp` (Gonzalo M. Rodríguez, CEUR-CONICET, CC BY 4.0).
- 1886: `Departamentos_1895.shp`.
- Los dos dibujan las provincias con los **límites que fijaron después las leyes 947 (1878) y 1532 (1884)**, no con la frontera de la época. Se ve en unidades enormes del SHP de 1869: Buenos Aires «Frontera» con 59.763 km², Mendoza «Frontera» con 65.389 km² y Santa Fe «La Capital» con 74.321 km², que llega a los 28° S.
- Las fronteras con otros países son las actuales: Chile según 1881/1902, Brasil en Misiones según el laudo de 1895, Paraguay en el Pilcomayo según 1876/1878.
- El SHP de 1869 excluye la Puna de Atacama (unos 62.400 km²), y está bien. **El de 1895 la incluye dentro de La Poma (Salta, 67.497 km²)**, y en 1886 la Puna era boliviana de derecho y estaba ocupada por Chile. Esto es un error para el atlas de 1886.

## De derecho en 1868: no había límites fijados

- Constitución de 1853/60, art. 64 inc. 14 (art. 67 desde 1860): el Congreso fija los límites de las provincias. **No lo hizo hasta 1878-1884.**
- Ley 28 (1862): son nacionales «todos los territorios fuera de los límites o posesiones de las provincias». No dice cuáles son esos límites.
- Ley 215 (13-ago-1867): fija la frontera militar sobre los ríos Neuquén y Negro. Era un objetivo, no se ocupó hasta 1879. El texto del art. 1 difiere entre transcripciones: hay que cotejarlo con el Registro Nacional.
- Ley 947 (1878): fija el límite de las tierras nacionales por fuera de las fronteras de Buenos Aires, Santa Fe, Córdoba y San Luis.
- Ley 1532 (1884): organiza los territorios nacionales «sin perjuicio» de una ley general de límites posterior.
- Reclamos provinciales: la constitución de Buenos Aires de 1854, en su art. 2, declaró límites propios. Falta el texto literal; ver Aramburo en *Nuevo Mundo Mundos Nuevos*.
- **Consecuencia:** una versión «de derecho 1868» de una sola capa sin superposiciones no existe. Lo honesto es rotular la geometría actual como «límites legales posteriores (leyes 947/1878 y 1532/1884)».

Referencia: Godio, L. M. A. (2024), «Los límites interprovinciales en la Constitución Nacional», *El Derecho* (UCA): https://repositorio.uca.edu.ar/bitstream/123456789/18737/1/limites-interprovinciales.pdf

## De hecho en 1868-1869: fuentes primarias

| Fuente | Qué cubre | Dónde |
|---|---|---|
| **Czetz y Hoffmeister, *Plano general de la frontera de la República al norte y este del territorio de la Pampa*, 1869**, por orden del ministro de Guerra Gainza | Toda la frontera sur, del río Tercero al río Negro: Buenos Aires, Santa Fe, Córdoba, San Luis y Mendoza. Fuertes y fortines con distancias, líneas anteriores a 1869 en azul, las de 1869 en rojo y las «variables» en punteado | Original en la Biblioteca Nacional Mariano Moreno (colección de mapas). Copia en dominio público en viejosmapas.com (unos 3,8 MB): https://viejosmapas.com/plano-general-de-la-frontera-de-la-republica-argentina-al-norte-y-este-del-territorio-de-la-pampa-1869/ |
| *Memoria del Ministerio de Guerra y Marina*, 1869 y 1870 | Informes de Czetz (agosto de 1869) sobre las fronteras oeste, centro, sur y costa sur de Buenos Aires. Frontera norte de Santa Fe, Córdoba y Santiago del Estero a cargo de Manuel Obligado (desde el 13-ene-1870; fortines Juárez, Bolívar, Capibara; pp. 214-220 según la cita) | Hemerotecas (BNMM, Biblioteca del Congreso); falta ubicar la copia digital |
| Martin de Moussy, *Carte de la Confédération Argentine* (compilada en 1867, publicada en 1873, 1:5.600.000) y láminas provinciales del *Atlas* | El país entero, con provincias, territorios y tribus | David Rumsey: https://www.davidrumsey.com/maps5111.html |
| Mansilla, frontera del río Quinto (1869) | Córdoba sur | Della Mattia y Mollo (2005), *El mapa de Mansilla* |

Para después de 1869 (útil en 1874 y 1880): Wysocki, planos de la nueva línea de 1876-77 (AGN e Internet Archive); Melchert 1876, *Carta topográfica de la pampa y de la línea de defensa*; Seelstrang y Tourmente 1875, *Mapa de la República Argentina* (NYU, Commons).

**Lo que falta:** un plano de la frontera del Chaco en Santiago del Estero, Salta y Tucumán en 1868-1870. Lo más cercano es de 1873: la Comandancia de la Frontera del Chaco, con Napoleón Uriburu, en Salta.

## Reconstrucciones actuales del plano de Czetz (búsqueda del 8-nov-2026)

No encontré ninguna digitalización pública de la línea: ni shapefile, ni GeoJSON, ni visor georreferenciado. Lo que hay:

- **Mollo, N. (2022)**, «Determinación geográfica de los sitios de interés histórico y arqueológico mediante la utilización de técnicas cartográficas», *Teoría y Práctica de la Arqueología Histórica Latinoamericana* 3 (UNR, CC BY-NC-SA). Georreferenció el plano con OziExplorer y QGIS, pero **solo para ubicar topónimos ranqueles**, no la línea. Advierte que las cartas militares de la época tienen errores de construcción y que, al georreferenciarlas, los parajes quedan «a mucha distancia del lugar real». Lo corrige con mensuras e imágenes satelitales. Cita una copia del plano fechada en **1868** en la Dirección General de Catastro de La Pampa. https://teoriaypracticaah.unr.edu.ar/index.php/tpahl/article/download/155/150/276
- **Mollo, «Contribuciones de la cartografía antigua…»** (revista *SPAS*, UNRC) y *Recuperación de toponimia ranquel en el área central de Argentina*: mismo enfoque, toponimia.
- **Della Mattia y Mollo (2005)**, *El mapa de Mansilla*: frontera de Córdoba.
- **Dispossessions in the Americas** (UPenn): escaneo de la copia de la BNMM (50 × 62 cm) con comentario, sin georreferenciar y sin licencia declarada. https://dia.upenn.edu/en/content/ARG0046Y/
- **Thill, J. P. y Puigdomenech, J. A. (2003)**, *Guardias, fuertes y fortines de la frontera sur. Historia, antecedentes y ubicación catastral* (Servicio Histórico del Ejército). Es el catálogo de referencia para **ubicar cada fuerte y fortín sobre el catastro**. Lo cita Leoni et al. (2013), *Anuario de Arqueología* (Rosario) 5:149-168. No está en línea: hay que conseguirlo en biblioteca.
- **Leoni et al. (2013)** advierten que la «línea de frontera» dibujada como trazo continuo es una convención cartográfica. En el terreno eran fuertes y fortines separados por leguas, con potreros alrededor.

**Implicancia:** conviene reconstruir la línea a partir de las **posiciones de los fuertes** (Thill y Puigdomenech, mensuras, sitios arqueológicos ya ubicados) uniéndolos en el orden del plano de Czetz, en vez de calcar el trazo del plano georreferenciado. El plano define qué puestos formaban la línea de 1869. El catálogo da dónde estaban.

## Propuesta para dos versiones

1. **Límites legales posteriores**: es la de hoy. Solo cambia el rótulo, y en 1886 hay que sacar la Puna.
2. **De hecho**: recortar cada provincia por la línea roja de 1869 del plano de Czetz (sur) y por la línea de Obligado/de Moussy (norte). Lo que queda afuera va gris, «territorio indígena (fuera de la línea de frontera de 1869)». Los votos no cambian: los partidos de frontera votaban desde el fuerte o el pueblo, que queda dentro.
   Para 1874 convendría la línea de 1869-1875, y para 1880 la de Alsina de 1876-77 (Wysocki) más el avance de 1879.
   Trabajo: georreferenciar el plano de Czetz con los fuertes de coordenadas conocidas, digitalizar la línea a mano y documentar el error.
