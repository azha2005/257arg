# Revisión del principal

## Alcance

Primera lectura delegada a tres subagentes `gpt-6.1-terra`, esfuerzo `medium`, como pidió el usuario. El principal hizo revisión focal de anomalías y lectura del acta de circuitos de Tucumán. Esto **no es una segunda transcripción independiente de todas las celdas**.

Las páginas indicadas son las del PDF desde 1. El OCR auxiliar solo localiza contenido. Renders y extracciones originales quedan locales; las fuentes principales se identifican por SHA256 en `CONTROL.json`.

## Santa Fe, 29-OV

- P95, San Lorenzo, José U. Aguirre: se confirma visualmente **2.349**, aunque sus compañeros rondan 2.541. No se cambia.
- P63, Iriondo, Miguel A. Gallitelli: se confirma **2.210**.
- P69, La Capital: se confirman **11.690** para Emilio G. Leiva y **5.903** para Augusto Morisot.
- P99: se cotejaron visualmente los 21 totales nominales provinciales, 9.903 blancos y 263.277 votantes. Coinciden con las sumas del CSV.
- El control inicial de «otros candidatos» daba 143 frente a 133 de p99. El principal revisó los renglones y localizó el error de lectura en **San Martín, p97**: la imagen muestra literalmente **«M 4»**, con 4 claro y M tenue anterior, no un 1 identificable. El subagente confirmó la corrección al releer el recorte. Se retiró el 14 inicial, se conserva `otros_literal="M 4"` y se deja el valor numérico vacío por la marca. Las otras menciones claras suman **129**; si se interpreta ese renglón como 4, suman **133**. Esta comprobación es condicional y no fija por suma la lectura ni convierte las cuatro ausencias de categoría en cero. P55 confirma 10 en Constitución; p99 confirma 133.

La fuente tiene cómputos departamentales finales directos: no fue necesario reconstruirlos restando acumulados. Las afirmaciones iniciales del sondeo sobre esa necesidad quedan superadas por la lectura del acta completa.

## Tucumán, 26-OV

- Se revisaron las páginas 9–67 para ubicar colegios electorales/circuitos y los totales de sobres. `tucuman/acta_departamentos.csv` conserva las dos columnas, **según acta** y **en urna**. Son magnitudes distintas de votos nominales y votos positivos.
- P56: el texto tenue invertido verticalmente permite recuperar circuitos 109–111 y el total de Cruz Alta, **12.617 / 12.592**. Se leyó la imagen ampliada, canal rojo, contraste local, con transformación vertical documentada; no se dedujo el total por diferencia. Los once departamentos suman **94.160 / 94.113**, coincidentes con p67.
- P69: la Junta admite al escrutinio las mesas observadas del circuito 13 de Capital y 65 de Chicligasta. No se excluyeron como anuladas.
- P72, mesa 6, Martínez: se ve **26**, con un «2» desplazado a su izquierda; el subtotal 343 también coincide con la lectura 26. El trazo desplazado se documenta, no se concatena en 226.
- P73, mesa 7, nulos: hay una marca superpuesta al guion; conservar la reserva, sin decidir cero automáticamente.
- P96, mesa 4 del primer bloque, Martínez: se confirma **4** impreso. Las siete filas visibles de la columna dan 190, frente al subtotal impreso **216**. No se sustituye por 30 para cerrar: es una discrepancia de la fuente o de su impresión que debe quedar explícita.
- P102: el principal cotejó visualmente las primeras ocho filas legibles contra las dos lecturas de subagentes; se conservan sus 112 celdas. Los rótulos territoriales siguen fuera del recorte y los trazos inferiores no se elevan a lectura firme.
- P103: se confirman los cuatro proclamados y votos en letras: Prat Gay 32.903, López García 31.432, Martínez 30.964 y Padrós 30.431. Son totales del distrito, no reparto territorial.

La tabla p102 tiene rótulos territoriales fuera del recorte y filas tenues. La correspondencia de circuitos del acta no basta por sí sola para identificar cada fila sin rótulo. Las planillas nominales deben evaluarse según su inventario de cobertura; no usarlas como una base departamental completa mientras existan omisiones o celdas sin resolver.

## Otros expedientes

Ver `sondeo_visual/INVENTARIO.md`: sondeo visual de 49 páginas de ocho expedientes locales. No se encontraron nuevas tablas territoriales. Jujuy 42-OV y 90-D corresponden a la complementaria del 19 de abril; no confundir con la ordinaria del 1 de marzo. Los doce expedientes pequeños ausentes siguen sin examen.

## Tucumán por departamento (5-nov-2026)
Revisión del principal sobre los escaneos de p.98, p.99, p.101 y p.102 (canales R/B, fondo restado, contraste por percentiles; p.101 volteada en vertical). Estados por celda en `tucuman/departamentos.csv`: 112 firmes (filas 1-8), 15 que además cierran con la proclamación o la Wikipedia, 11 leídas igual en dos fuentes, 6 de lectura única, 6 tentativas sin valor y 4 ilegibles. Ninguna cifra se obtuvo por diferencia.
