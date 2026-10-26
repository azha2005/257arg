# Salta, elección nacional de 1916: expediente 58-D-1916 y cruce territorial

## Resultado y alcance

El expediente permite recuperar una planilla de diputados nacionales por **38 colegios electorales** y los sufragantes de cada colegio. Se digitalizaron las 16 columnas de candidatos: las cifras expresas, los guiones y los espacios vacíos se conservan por separado. Las celdas vacías **no se convirtieron en cero**. Es una transcripción visual de trabajo, no una segunda transcripción independiente ni un resultado definitivo por departamento.

También se transcribieron los resultados provinciales definitivos de los **16 candidatos a diputado** y de los **30 candidatos a elector de presidente y vicepresidente**, proclamados el 1 de mayo. No se encontró en este expediente una planilla territorial completa de electores presidenciales. El listado provincial no permite reconstruir por sí solo los votos presidenciales por colegio.

No se suman candidatos de una misma lista para obtener votos de partido: las unidades de cuenta son votos nominales, y un sufragante podía votar más de un nombre. No se asignan partidos a candidatos sin una nómina documentada.

## Qué fuente contiene cada dato

Todas las páginas indicadas son páginas digitales del PDF, contadas desde 1.

| Documento | Páginas | Contenido utilizado |
|---|---|---|
| 58-D-1916 | 5 y 15 | Acta del 15 de abril; 38 colegios y 18.229 sufragantes; anulación de mesa 5 de Rivadavia |
| 58-D-1916 | 6 | Planilla de votos por colegio para diputados; 16 candidatos |
| 58-D-1916 | 11-14 | Acta del 1 de mayo; escrutinio complementario del 23 de abril; proclamación definitiva |
| 58-D-1916 | 16-22 y 31-54 | Incidencias de mesas y resoluciones; no son otra planilla territorial completa |
| 58-D-1916 | 55 | Recorte de decreto nacional del 8 de marzo de 1916; sólo fragmentos de ubicaciones de mesas |
| Cacopardo, DTS 47, 1967 | 40-42; impresas 35-37 | Cuadro 1, correspondencias de departamentos de Salta entre censos |
| Base deptos 1869-2022 | Departamentos_1914.shp | Geometrías históricas reconstruidas; la provincia está codificada con referencia actual |

La fecha de la página 6 se interpreta por continuidad con el acta del 15 de abril que la precede. No debe reemplazarse su etapa por la del acta definitiva del 1 de mayo.

## Cotejo de votos

| Candidato | Total escrito en planilla p.6 | Definitivo 1 de mayo, p.12 | Cambio |
|---|---:|---:|---:|
| Agustín Usandivaras | 11.257 | 11.339 | +82 |
| Julio Cornejo | 10.885 | 10.967 | +82 |
| Carlos Outes | 6.723 | 6.723 | 0 |
| Abraham Echazú | 6.369 | 6.369 | 0 |

Las sumas de las 38 filas para Usandivaras y Cornejo coinciden con los totales de la planilla del 15 de abril. Las cifras de sufragantes suman **18.229**, y los primeros veinte colegios suman **10.786**, coincidiendo con el transporte escrito en el acta.

**Lecturas que siguen abiertas:** en Campo Santo, colegio 4, se proponen 151 para Outes y 157 para Echazú. El último trazo es ambiguo entre 1 y 7. Esa combinación concilia ambas columnas con sus totales escritos, pero la conciliación aritmética no constituye una prueba independiente de lectura. Se guardaron las alternativas en `lecturas_dudosas`. No publicar estas dos celdas como verificadas sin otro cotejo o copia más clara. Los dos primeros candidatos no dependen de estas lecturas.

Para Piniella, las cifras expresas de la planilla suman **120**, coincidiendo con la proclamación definitiva. Sin embargo, el total escrito al pie de su columna parece **121**: se conserva como discrepancia del total manuscrito, sin alterar las filas para hacerlo coincidir. Las cifras minoritarias expresas concilian con la proclamación. Esto no convierte automáticamente todos los espacios vacíos en ceros.

El expediente documenta que se anuló y repitió la mesa 5 del colegio 11 de Rivadavia el 23 de abril. El +82 de los dos primeros candidatos es compatible con esa complementaria. **No se distribuyó ese incremento automáticamente a Rivadavia:** se debe comprobar el resultado de la mesa y el tratamiento de las otras incidencias antes de producir una fila departamental definitiva. Las resoluciones anteriores al 15 de abril tampoco deben sumarse otra vez a la planilla si ya estaban incluidas.

Los 360 votos en blanco y 99 anulados aparecen al cierre de la lista de electores en p.13. Se mantienen fuera de las tablas de diputados por falta de desglose inequívoco por categoría.

## Cruce territorial con Cacopardo

Cacopardo permite reconocer **21 departamentos de Salta en el censo de 1914**. Es la referencia histórica de partida, no una certificación de todos los límites electorales vigentes en abril de 1916. El cruce de nombres no acredita que cada colegio tenga el mismo perímetro que una localidad o que un departamento censal.

| Departamento de referencia 1914 | Colegios candidatos del expediente | Estado |
|---|---|---|
| Anta | 9 Anta; 10 Chañar Muyo | Nominal para 9; agrupación de 10 pendiente |
| Cachi | 34 Cachi | Correspondencia nominal |
| Cafayate | 29 Cafayate | Correspondencia nominal |
| Caldera / La Caldera | 3 Caldera | Correspondencia nominal |
| Campo Santo | 4 Campo Santo; 5 Güemes | Agrupación pendiente; no duplicar como dos departamentos |
| Candelaria / La Candelaria | 28 Candelaria (Tala) | Distinguir del colegio 2 |
| Cerrillos | 18 Cerrillos; 19 La Merced | Agrupación pendiente |
| Capital | 1 Rectoral (Cap.); 2 Candelaria (Cap.) | La abreviatura y el signo de repetición del acta respaldan Capital |
| Chicoana | 20 Chicoana; 21 Carril | Agrupación pendiente |
| Guachipas | 24 Guachipas; 25 Carahuasi | Agrupación pendiente |
| Iruya | 16 Iruya | Correspondencia nominal |
| La Viña | 22 La Viña; 23 Coronel Moldes | Agrupación pendiente |
| Molinos | 32 Molinos; 33 Luracatao | Agrupación pendiente |
| Orán | 12 Orán; 13 San Andrés; 14 Luna Muerta; 15 Campo Durán | Pendiente, especialmente el homónimo Luna Muerta |
| La Poma | 38 La Poma | Correspondencia nominal; no incluir San Antonio de los Cobres |
| Rivadavia | 11 Rivadavia | Correspondencia nominal; complementaria pendiente de conciliación |
| Rosario de Lerma | 35 Rosario de Lerma; 36 Silleta; 37 Quebrada del Toro | Agrupación pendiente |
| Rosario de la Frontera | 26 Rosario de la Frontera; 27 Las Mercedes | Agrupación pendiente |
| San Carlos | 30 San Carlos; 31 Angastaco | Agrupación pendiente |
| Metán | 6 Metán; 7 Galpón; 8 San José de Orquera | Agrupación pendiente; Orquera respaldado por documentación oficial posterior |
| Santa Victoria | 17 Santa Victoria | Correspondencia nominal |

Las agrupaciones son **hipótesis explícitas**, no datos departamentales finales. No se generó una suma departamental que esconda esa incertidumbre.

Cambios y exclusiones documentados por Cacopardo:

- **Campo Santo → General Martín de Güemes:** el cuadro conserva Campo Santo en 1947 y presenta el nombre posterior en 1960. No establece en esta fila la fecha exacta del cambio.
- **Orán → Orán + General J. de San Martín:** el cuadro muestra la separación entre las columnas de 1947 y 1960. No usar automáticamente las dos geometrías actuales para dividir votos de 1916.
- **Payogasta → La Poma:** Payogasta figura en 1869 y La Poma en 1895 y 1914.
- **Ciudad → Salta → Capital:** cambios de nombre censal entre 1869, 1895 y 1914.
- **San José de Metán → Metán:** nombre censal antiguo y posterior.
- **Los Andes:** el pie de cuadro indica que San Antonio de los Cobres pasó de La Poma al Territorio de Los Andes; la unidad incorporada después a Salta incluía Pastos Grandes. Los dos polígonos de 1914 que hoy tienen código provincial 66 no deben incorporarse a la elección salteña de 1916.

## Apoyo externo y precauciones con homónimos

- [Boletín Oficial de Salta n.º 615, 1916, p.2](https://boletinoficialsalta.gob.ar/pdfs/1916/615.pdf): el decreto del 3 de agosto de 1916 agrupa Luna Muerta y Campo Durán con el distrito policial de Embarcación. Apoya la identificación norteña, pero **no acredita por sí mismo los límites de los colegios electorales**.
- [Boletín Oficial n.º 609, 1916](https://boletinoficialsalta.gob.ar/pdfs/1916/609.pdf): un edicto indexado menciona lotes llamados Luna Muerta en Rivadavia. No se ha identificado ese homónimo con el colegio 14; exige cotejar el decreto de mesas o el padrón. No basta geocodificar el topónimo.
- [Senado de Salta, 1 de octubre de 2015](https://senadosalta.gob.ar/versiones-taquigraficas/versiones-taquigraficas-2015/01-10-2015/): identifica San José de Orquera en El Galpón, departamento Metán. Es apoyo para una correspondencia candidata; la fecha posterior no demuestra continuidad exacta desde 1916.

## Qué falta para cerrar la incorporación

1. Cotejar las dos celdas dudosas de Campo Santo con otra copia, acta de mesas o cuadro publicado.
2. Cotejar el total manuscrito de Piniella (121 frente a 120 sumados) y el resultado de la mesa complementaria de Rivadavia sin doble cómputo.
3. Recuperar completo el decreto nacional del 8 de marzo de 1916 sobre división y ubicaciones de mesas, o el padrón que delimita los 38 colegios. El recorte de p.55 no conserva todas las definiciones.
4. Confirmar las agrupaciones dentro de los 21 departamentos históricos, con especial atención a Luna Muerta, Chañar Muyo y Las Mercedes.
5. Para presidente por departamento, localizar el cuadro por colegio de **electores presidenciales**: no inferirlo a partir de diputados.

## Archivos y convenciones

Los JSON y CSV tienen el mismo contenido. Los CSV son UTF-8 con BOM. `diputados_por_colegio_todas_columnas` contiene 608 posiciones (38×16); las posiciones vacías llevan `votos=null` en JSON y campo vacío en CSV. `colegios_diputados_15abril` ofrece los cuatro candidatos principales y sufragantes para inspección rápida. `correspondencias_colegios` y `cruce_cacopardo_capa1914` separan las propuestas territoriales de los resultados electorales. `incidencias` reúne cuatro asuntos prioritarios; no pretende reemplazar la lectura íntegra de todas las resoluciones.

`transcribir.py` reproduce los datos desde la lectura manual y el inventario geográfico previo. Las imágenes seleccionadas se incluyen como evidencia para cotejar las cifras y los encabezados. Los PDF originales son los archivos aportados por el usuario, no se alteraron.
