# Revisión territorial con Cacopardo (1967), 26 de octubre de 2026

Se inventariaron los **52 cruces calculados** que tienen `control.json` en `transferencias/`. La selección y las marginales se cotejaron contra los datos actuales; el inventario distingue esa reproducción aritmética de una validación histórica de límites. [Inventario CSV](inventario_selecciones.csv), [JSON](inventario_selecciones.json). Los cruces anteriores a 1967 se revisaron además contra los cuadros pertinentes de `DTS 47_Cacopardo_1967.pdf`, las tablas de Cantón y los scripts de correspondencias.

Los cambios posteriores a 1960 no quedan certificados por ese PDF: los cruces modernos conservan las correspondencias específicas ya documentadas en sus informes. La reproducción de una matriz o de sus totales tampoco certifica por sí sola que una geografía sea correcta.

## Dos cruces corregidos

| Cruce | Antes | Ahora | Padrón de origen utilizado antes/después | Resultado |
|---|---:|---:|---:|---|
| [1954 diputados → 1965 diputados](../1954d_1965d/sankey_1954d_1965d.html) | 378 unidades | 374 unidades | 8.420.919 / 8.420.919 | Dos uniones completas en PBA |
| [1958 presidente → 1962 diputados](../1958d_1962d/sankey_1958d_1962d.html) | 355 unidades | 349 unidades | 8.967.491 / 8.967.491 | Tres uniones completas en PBA |

Se conservó el padrón utilizado; se redujo el número de observaciones porque se agregaron territorios completos. Se reajustaron las matrices y la validación cruzada, y se repitieron los 200 bootstrap. El filtro anterior se conservó: 0,6–2,7 para 1954–1965 y 0,75–1,33 para 1958–1962. Este último reproduce exactamente la selección que estaba guardada, aunque un comando antiguo del LEEME mencionaba un rango más amplio.

Las correcciones salen del Anexo del Cuadro 1, revisado visualmente:

- **Escobar:** PDF67, impresa64, dice Pilar y Tigre. Las claves intermedias del proyecto sumaban Escobar a Pilar; ahora se agregan **Pilar + Tigre + Escobar** donde corresponda en los dos extremos. No se compara el Tigre antiguo, más extenso, con el Tigre recortado como si fueran iguales.
- **Hipólito Yrigoyen:** PDF68, impresa65, dice Bolívar, Carlos Casares, Caseros y Pehuajó. Ahora se comparan esas cuatro unidades de origen y su descendiente como un territorio común. La asignación intermedia a Pehuajó por sí sola no bastaba.
- **San Cayetano:** PDF67, impresa64, dice González Chaves, Necochea y Tres Arroyos. En 1958–1962 se agrega la unión completa. En 1954–1965 la base de 1954 ya tenía el dato de Necochea compartido con esos partidos y Juárez; su agregación anterior ya cubría ese territorio amplio.

No se repartieron votos ni electores por superficie o por proporciones. `correspondencias.apply_pair` aplica las uniones antes de filtrar y estimar, conservando exactamente cada categoría de votos y padrón. Los archivos intermedios heredados pueden mantener una asignación de un hijo a un padre: la unión final documentada es la que entra a la inferencia.

El mayor cambio por celda en las filas partidarias grandes es 0,034 puntos en 1954–1965 y 4,118 puntos en 1958–1962. La geografía incorrecta no se justifica por que cambie poco una cifra: se corrigió en ambos casos. [Verificación y cambios por fila](verificacion_recalculados.json), [cambios 1954–1965](../1954d_1965d/cambio_vs_antes_cacopardo_pp.csv), [cambios 1958–1962](../1958d_1962d/cambio_vs_antes_cacopardo_pp.csv).

La auditoría del modelo conserva una alerta en 1958–1962: en Jujuy el destino Otros queda sobreestimado (2.334 votos modelados frente a 15 registrados). Es una limitación del ajuste, distinta de las correspondencias territoriales. Está indicada en los controles y en la auditoría general; no se corrigió inventando votos.

## Los demás cruces históricos anteriores a 1967

- **1930d→1946d, 1937d→1946d y 1940d→1946d:** se comprobaron las unidades de los archivos, sus alias y exclusiones. Las tablas usadas contienen las mismas veinte denominaciones electorales de Capital; no se sustituyeron por secciones censales. Las unidades subsumidas sin cifra propia ya estaban excluidas. No apareció una corrección territorial adicional sustentada por este PDF. Esto no elimina los límites de cobertura de Cantón ni convierte sus filas en votantes individuales seguidos a través de los años.
- **1954→1958:** se revisaron las agregaciones de Avellaneda–Lanús, La Plata–Berisso–Ensenada, Bahía Blanca–Rosales, Lincoln–Alem, Necochea y sus unidades subsumidas, Juárez Celman–General Roca–Roque Sáenz Peña, San Rafael–Alvear–Malargüe y Capital–Chimbas. Las agregaciones previas ya reunían las unidades de los dos extremos; no requirió un cambio adicional por este examen.
- **Formosa, Chaco, La Pampa y Misiones:** el propio Cuadro 1 advierte en varios casos que una redivisión no permite equivalencias exactas por departamento. No se generaron equivalencias nuevas por semejanza del nombre. Las exclusiones y la agregación provincial de Misiones que ya existían se conservaron.

## Mapas de 1912, 1914 y 1916

Se revisaron `mapa1912/LEEME_1912.md`, `mapa1914/LEEME_1914.md`, `mapa1916dip/LEEME_1916.md`, los builds y los tres datasets actuales. Son atlas sobre 444 polígonos, con coberturas y tratamientos de fuentes distintos:

- **1912:** once provincias en color sólido, sin observaciones departamentales propias para inferir transferencias. Córdoba tiene unidades subsumidas sin cifra; Santa Fe solo cinco departamentos con datos. No existía un cruce calculado 1912–1914 o 1912–1916 en el inventario.
- **1914:** seis provincias sólidas. Necochea comparte un dato con tres polígonos. Ese recurso visual no produce tres observaciones independientes. Las cifras inferidas y de prensa se mantienen identificadas en el atlas.
- **1916:** San Juan y Santiago del Estero en sólido. Necochea comparte un dato con tres polígonos y Juárez Celman con dos; las lecturas reconstruidas o estimadas tienen sus notas. Para la inferencia se usaron las celdas de origen, no las copias del dataset del mapa.

El Cuadro 1 confirma cambios nominales como Ciudad/Capital de Mendoza, Juárez Celman/Gobernador Gordillo en La Rioja y Tercero Abajo/General San Martín en Córdoba. También distingue partidos bonaerenses ya creados en 1913 de González Chaves, creado en 1916. Un faltante `*` no equivale a un dato subsumido `**`: Esteban Echeverría o Roque Pérez no se rellenan agregándolos arbitrariamente a un vecino.

[1914→1916: fuentes, decisiones por territorio y límites](../fuentes_1914_1916/LEEME.md). Los mapas siguen mostrando sus datos y advertencias; el cruce cuenta cada dato compartido una sola vez y separa las variantes de fuente.

## Evidencia, respaldo y reproducción

El PDF original se conserva en la raíz. Se extrajo su texto para localizar pasajes y se revisaron visualmente páginas completas, especialmente Cuadro 1 y Anexo. Las páginas PDF67–68 se renderizaron también con Poppler y se comprobaron las llaves de los cuatro orígenes de Hipólito y los tres de San Cayetano. Las capturas y el SHA-256 están en `../fuentes_1914_1916/`.

Los resultados completos anteriores de los dos pares corregidos están preservados en `anteriores/`, junto con el primer inventario. Los cruces no afectados conservan sus matrices. [Verificación de las 35 vistas recalculadas](verificacion_recalculados.json).

Para reproducir:

1. `python transferencias/auditar_geografia.py`
2. `RATIO=0.6,2.7 python transferencias/estimar.py 1954d 1965d`
3. `RATIO=0.75,1.33 python transferencias/estimar.py 1958d 1962d`
4. `python transferencias/verificar_revision_cacopardo.py`

Las asignaciones `RATIO=...` del ejemplo son variables de entorno; en PowerShell se establece `$env:RATIO` antes de ejecutar y se elimina después. El filtro efectivo queda guardado en los nuevos controles.
