# Segunda revisión de 1918 y 1920

3 de noviembre de 2026. Primera transcripción visual: dos subagentes `gpt-6.1-terra`, uno por año. El agente principal hizo controles estructurales, cotejo diagnóstico con Lupu–Stokes y relectura de los casos difíciles. Los transcriptores volvieron a leer las columnas de inscriptos/votantes y documentaron las fuentes impresas. No se realizó una segunda lectura exhaustiva independiente de todas las celdas.

## Cambios después de la primera lectura

Todos en PDF 44, Capital Federal 1918. Registro reproducible en `CORRECCIONES.json` y `revisar.py`:

| Unidad | Columna | Primera lectura | Lectura ampliada |
|---|---:|---:|---:|
| San Nicolás | 4, Demócrata Progresista | 605 | 695 |
| Santa Lucía | 5, Socialista | 4.217 | 4.247 |
| Socorro | 6, Socialista Argentino | ilegible | 1.368 |
| Vélez Sarsfield | 5, Socialista | ilegible | 2.286 |

Los dos valores numéricos corregidos y los dos ilegibles resueltos se leyeron en el escaneo original ampliado. Lupu–Stokes sirvió para señalar diferencias; no se copió una cifra ajena para completar la transcripción.

**Permanece ilegible** el número de inscriptos de Vélez Sarsfield 1918, PDF 44, columna 1. Se consideran candidatos 9.455/9.459, sin decisión segura. JSON conserva `null` y marca `ilegible`; CSV sin valor y con marca. No se reconstruye con participación, votantes ni total provincial.

## Diferencias que se conservan

El cotejo diagnóstico de 1918 contiene 520 comparaciones de familias, 517 exactas. Quedan:

- Balcarce, conservadores, PDF 45: lectura 174 frente a 144 de Lupu. El dígito central es débil; se conserva la lectura del escaneo y se anota la reserva de lectura 144/174 para eventual cotejo primario. No se considera una errata demostrada del libro.
- Capital, Vélez Sarsfield, PDF 44: Demócrata Progresista 235 + Socialista Argentino 1.597 = 1.832; familia `con` de Lupu 1.742. Se conserva 1.597, visible en la imagen, sin atribuir identidad conservadora a esos partidos por la etiqueta de la base académica.
- El Alto, Catamarca, PDF 49, Concentración: 386 en el impreso; 388 en Lupu. Se conserva 386.

1920 tiene 592 comparaciones exactas de 592. Eso valida coincidencia con otra base en esos casos; no comprueba de forma independiente la fuente histórica ni todas las columnas. Hay 30 filas con cifras de cada año sin pareja nominal utilizable con votos en Lupu, listadas en los JSON de cotejo. No se excluyen del archivo transcrito.

El cotejo prueba subconjuntos de columnas por provincia para acercarlos a cada familia. Su elección es **solo un diagnóstico de digitación**: no es una tabla histórica de alianzas, no se debe usar como agrupación para un mapa y no prueba equivalencia política de las columnas.

## Claves y anomalías releídas

- San Luis 1920, PDF 66: confirmadas visualmente las claves 4 «Demócrata» y 5 «Unión Popular». Capital 1920, San Cristóbal Norte: confirmada circunscripción 8.
- Córdoba 1920, Río Segundo, PDF 61: 3.433 inscriptos y 3.591 votantes, como en el impreso. No se corrige el exceso.
- Buenos Aires 1920: Bragado, votantes 3.265; Patagones 259; Salto 2.519. Las sumas partidarias no coinciden, pero las cifras se leen así. La ausencia de otras categorías no se convierte en blancos o anulados.
- Mendoza 1920, PDF 65: Godoy Cruz y Rivadavia repiten las tres primeras cifras partidarias 97, 887 y 213. El cuarto valor es distinto (624/606). Se mantiene la repetición.
- Santa Fe 1918, PDF 54: Garay 1.159 votantes frente a 1.393 en fuerzas; Nueve de Julio 209 frente a 260. Se mantienen ambos excesos.
- Las columnas con `*` general en el encabezado están vacías en las celdas del original. Los datos serializan esa ausencia como `*` por fila y guardan `marcas_columnas`. CSV distingue `origen_marca=encabezado` de `celda`. No son ceros.

## Discordancias cronológicas del original

El principal releyó las fuentes al pie de las tablas de Capital 1918/1920. Los transcriptores las registraron para todas las páginas:

- Capital 1918, PDF 44: encabezado 1918, pero los partidos se atribuyen a números de La Nación de abril de **1922**.
- Santa Fe 1918, PDF 54: encabezado 1918, pero la fuente partidaria cita La Nación del 8 de abril de **1922**.
- Capital 1920, PDF 56: encabezado 1920, pero votantes atribuidos a La Prensa del 24 de marzo de **1924**.

Se transcribe la página bajo el año de su encabezado, con `reserva_cronologica` en el JSON, CSV y Markdown. No se decide que sean simples erratas ni que los votos correspondan necesariamente a esos años posteriores. Antes de usar estos casos para un atlas histórico hay que cotejar la prensa y los resultados provinciales del cargo y año. No trasladar estas cifras para completar 1922 o 1924.

El Anuario Estadístico de Córdoba de 1923, citado en ambos bloques, puede publicar resultados anteriores: su fecha editorial por sí sola no implica una discordancia electoral.

## Entregables y límites

Las 24 páginas asignadas están transcritas: 537 filas y 2.699 celdas; 1.907 números y 792 marcas. No hay vacíos sin marca ni filas duplicadas por distrito. Las bases conservan separadas las fuerzas originales, inscriptos, votantes y tipos de voto publicados. No se agrupan partidos, no se corrigen sumas y no se imputan faltantes. No se modificaron atlas ni totales nacionales.

Los controles aritméticos enumeran las diferencias de suma; una suma menor puede obedecer a categorías no publicadas. Ni una diferencia ni el criterio de selección del autor constituyen por sí solos evidencia de fraude. La entrega es una transcripción de la cobertura del libro, no una base nacional completa ni certificación del escrutinio.
