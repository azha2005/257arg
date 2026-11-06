# Handoff — 5 de noviembre de 2026

El usuario pidió cortar por límite de uso y escribir este handoff. **No seguir trabajando hasta que pida retomar.** No hubo commit, publicación ni cambios a atlas. Los subagentes fueron interrumpidos al cerrar.

## Pedido y trabajo terminado

Pedido inicial: leer LEEME de esta carpeta, transcribir con subagentes Terra medium y cotejo del principal; crear skill del proyecto. Se usaron tres subagentes `gpt-6.1-terra`, esfuerzo medium. Skill creado y validado: `.agents/skills/transcribir-elecciones/SKILL.md`.

Santa Fe terminado en primera lectura: `santa_fe/candidatos.csv`, 19 departamentos × 21 candidatos = 399 cifras. Todos los candidatos, blancos (9.903) y votantes (263.277) suman el total provincial. El principal cotejó cifras raras y totales de p99. Corrección importante: San Martín «otros candidatos» NO es 14: literal **M 4**, conservado sin valor numérico por la marca; las otras menciones suman129, con lectura4 sumarían133 del resumen. Ver `REVISION.md`, `CONTROL.json`, `verificar.py`. No fue necesario restar acumulados: existen totales departamentales directos.

Tucumán primera lectura parcial consolidada: `tucuman/celdas.csv`, **310 renglones, 4.340 celdas: 3.313 números, 463 guiones, 564 sin resolver**. Incluye mesas y subtotales: NO sumar todos los renglones. Las pistas de cara incierta están separadas. `consolidar.py` regenera desde `parte_a/lectura_parcial.csv` y `parte_b/lectura_consolidada.csv`. Los números de fila son ordinales de lectura por página, a veces decimales. Fuente `expedientes_hcdn/26-ov-1936.pdf`, páginas PDF desde1. PDFs y renders locales fuera de git.

Sondeo visual adicional: 49 páginas de ocho expedientes sin nuevas tablas territoriales; Jujuy42-OV/90-D son complementaria del19abril, no ordinaria1marzo. Ver inventario.

## Segundo pedido, EN CURSO

Usuario señaló: para tener Tucumán por departamento hay que asignar bloques de planillas a circuitos, usando los votantes por mesa de pp9–67. Se inició ese cruce. **Aún no se escribieron asignaciones definitivas ni agregados departamentales.**

### Archivos nuevos útiles

- `tucuman/acta_mesas_a.csv`: lectura visual de pp9–33, 239 filas de mesas, 55 circuitos incluidos bis. `acta_totales_a.csv`, `NOTAS_ACTA_A.md`. Sus sumas cierran exactamente Capital26516/26506, Famaillá9943/9937, Monteros9110/9112 (acta/urna). También cierran44 totales impresos de circuito. Circuito1 continúa p11: no confundir subtotal1600 de p9 con total2413/2411.
- `tucuman/acta_mesas_b.csv`: pp35–67, 282 filas, circuitos55–134 y bis. Pendiente revisión final y controles del subagente B. Conservar dudas de109 y discrepancias de fuente. Puede haber archivos de notas/totales adicionales escritos al momento del corte: comprobar sin asumir que terminó.
- `tucuman/anclajes_departamentos.csv`, `LEEME_ANCLAJES.md`: textos de reanudación recuperados de bandas tenues. **P90 identifica explícitamente circuito78, mesa1 y suplementaria, colegio Graneros**. P72 anuncia Capital1bis (inicio p73). P91 cierreGraneros y p93 cierreLeales coinciden con filas6 y7 del resumen102.
- `tucuman/cotejo_bloques_a.csv`: cotejo independiente de32 bloques72–84; confianza y reservas. Mensaje final adicional del agente A confirma límites departamentales descritos abajo.
- `tucuman/renglones_revision.json`: agrupación auxiliar de las celdas por página/fila, candidatos en orden, blancos/nulos.
- `tucuman/alinear_exploratorio.py`, `propuestas_alineamiento.csv`: **EXPLORATORIO, NO ES ASIGNACIÓN CERTIFICADA**. Alineamiento monotónico de mesas con huecos; compara etiquetas y huella aproximada. Usa medias/medianas intralista y guiones0 SOLO como huella de búsqueda, nunca como votos imputados. No convertir ese proxy en votantes reales. El algoritmo puede saltar de circuito dentro de un bloque que tiene subtotal; eso es un error de correspondencia que exige restricciones por bloque/revisión manual.

### Límites departamentales avalados por secuencia/patrones

Para las filas YA registradas, los departamentos se pueden delimitar mucho mejor que antes:

- Capital: pp72–78. P78 último bloque compatible circuito19 (1+sup,2,3); p79 empiezaFamaillá22.
- Famaillá: pp79–81. P79 primero22, luego23 y comienzo24; p80 continuación24,25 y otro bloque; p81 primero29, luego30, siguiente31. P82 comienzaMonteros.
- Monteros: pp82–84. P82 primer bloque compatible35 (single), luego36 (3filas),37 (3filas), comienzo38; p83 termina38. P84 continúaMonteros. Circuitos individuales de bloques tenues aún tienen reservas.
- Chicligasta: pp85–87. **P85 primer bloque55 (1+sup,2,3,4–5), segundo56 (1+sup,2,3–4), tercero largo57**, confirmado por agente A con acta p35. P87 bloques66,67,68 muy compatibles por agrupaciones y perfiles.
- Río Chico: p88 y parte superior/central89; bloques69 y72–75, faltan filas intermedias por bandas. P90 texto arrancaGraneros78.
- Graneros: fila de p90 bajo texto y p91. P91 cuatro mesas compatibles82 y total departamental coincide resumen102fila6.
- Leales: pp92–93. P92 bloques83,84,85,86,87; p93 sendas mesas fusionadas90bis y91, total coincide resumen102fila7.
- Cruz Alta: filas registradas pp95–96. P95 bloques102,103,104,105,106; p96 bloques107,108,109 (último requiere revisar acta56).
- Burruyacú: pp97–98. P97 primero112 (5mesas), segundo113 (4mesas), último bloque probablemente117 (NO114, hipótesis inicial corregida). **P98 superior es120**, perfil201/158/138 coincide exactamente con acta120, NO117. Luego121,122,123,124 singles.
- Trancas: p99 bloques125,125bis,126,127. TotalPadrós98+108+79+163=448, también total departamental impreso p99. Resumen102fila10 leído inicialmente443? debe cotejar con448 visible en planilla. No imputar por suma.
- Tafí: p100 primer bloque128 (4mesas agrupadas4–5). P101 primer bloque final130 (8–12,13–14,sup), luego131,132,133,134. Faltan filas129 y principio130 bajo bandas p100.

Estos límites aún deben formalizarse con evidencia y reserva, sin presentar las sumas de mesas incompletas como totales departamentales completos. Los cierres departamentales impresos y resumen102 pueden dar totales directos aunque falten mesas.

### Circuitos concretos: hallazgos y trampas del algoritmo

- P74 superior **3**, no3bis: perfil de7mesas se ajusta mejor al acta3. P75 superior final3bis (8,9,10y11,sup) confirmado.
- P75 filas6–13 pertenecen a un mismo bloque **4**: subtotal dePadrós356 es suma64+62+57+41+37+51+44. Algoritmo incorrectamente manda últimas filas a6. Mantener unido el bloque; última etiqueta8? es agrupación7y8 en acta.
- P76 superior8; p77 bloques10,11 y probablemente12. Algoritmo puede mandar segunda fila del último bloque a18 por valores desconocidos: no aceptar ese salto dentro del bloque con subtotal.
- P80 filas10–13: hipótesis inicial27 NO firme; huella parcial mejor coincide26 (237,174,178,166) y algoritmo actualizado26. Revisar bloque completo.
- P83 últimas filas11–12: probablemente41, no43. CampoLaprida está ? pero imagen realzada deja ver primerPratGay≈121 y segundo≈84; con patrón y votantes244/172 favorece41. **No se actualizaron esas lecturas en CSV**; no tratarlas como cifras firmes. Renders `revision/asignacion/p83_bloque41.png`.
- P85 bloque55 debe quedar unido: algoritmo salta50/54/55 si no se restringe por bloque.
- P86 dos filas superiores probablemente62, no65: perfil190/168 coincide191/169 del62. Falta resto del bloque y otros en bandas.
- Usar suma nominal/3 + blancos/nulos como identidad es incorrecto: incluso anclaje explícito p73primera1bis no da268exacto; hay diferencias entre nombres, blancos, sobres y errores de fuente. Es una huella auxiliar y no motivo para rechazar automáticamente una correspondencia por diferencia3/10.

### Dudas del acta B a revisar

Antes del corte, sumando solo celdas enteras del CSV B: Chicligasta8300/8300, RíoChico8244/8240, Burruyacú4293/4301, Trancas1731/1732 cierran. Graneros daba urna3587 frente3589; Leales3885/3881 frente3888/3882. Se pidió al agente B cotejar y documentar esas diferencias, sin forzar cierre.

Tafí filas urna5912 frente5922: agente B leyó circuito130 mesa11 **179/168**, y subtotal urna2462 excede10 su suma de filas; preservar si es original.

CruzAlta109 en página56 tenue invertida: CSV B contiene1sup165/165 (el principal ve primer número más bien152/153 en recorte, **discrepancia pendiente**), mesa2=154?/153?, mesa3=152/152, mesa4=?/?. No fijar esos valores por diferencia. Los totales departamentales12617/12592 sí fueron leídos y cierran con los otros departamentos. Circuitos110 y111 se leen en56 (110total500/500;111335acta?/335urna, cotejar literal). Render ampliado `revision/asignacion/c109_local.png`, JPEG `p56.jpg`, frente recuperado `p56_frente_recuperado.png`. Se recuperó mediante volteo vertical, canalR y contraste local, sin síntesis.

## Próximo trabajo autorizado al retomar

1. Revisar archivos finales que pudieron guardar agentes, en particular B y eventual lectura de cierres departamentales de SantaFe. Verificar controles y discrepancias anteriores.
2. Crear correspondencias POR BLOQUE, mantener unidos renglones/subtotal; usar texto explícito, agrupaciones de mesas, perfil de sobres y secuencia. Dejar circuito vacío si solo departamento firme.
3. Añadir columnas de departamento/circuito/evidencia a una copia de celdas (preservar crudos). No sumar subtotales junto con mesas.
4. Cotejar resumen102: primeras8filas completas112celdas ya revisadas por principal; etiquetas fuera del recorte. Orden probable Capital,Famaillá,Monteros,Chicligasta,RíoChico,Graneros,Leales,CruzAlta,Burruyacú,Trancas,Tafí. Formalizar atribución con cierres/mesas, no solo por orden supuesto. Últimas filas son tenues y sus pistas NO firmes.
5. Producir tabla departamental con totales directos y/o derivados documentados, cobertura y faltantes. No inventar cifras ni pasar votos nominales a votos de lista. Actualizar LEEME/REVISION/CONTROL cuando corresponda; hoy esos documentos aún reflejan la etapa anterior sin asignaciones.

No construir atlas, commitear ni publicar con esta autorización. No actualizar memoria global (no solicitado). Mantener distinción lectura firme, interpretación territorial, hipótesis exploratoria y datos faltantes.

## Retomado (5-nov-2026, otra sesión): tabla departamental hecha

- `tucuman/departamentos.py` → `departamentos.csv`, `celdas_departamento.csv`, `CONTROL_DEPARTAMENTOS.json`.
- Atribución de p.102: el orden del acta se confirma porque las filas 6 y 7 coinciden con los cierres de p.91 (Graneros) y p.93 (Leales), la fila 9 con el total de p.98 (Burruyacú), la 10 con el de p.99 (Trancas) y la 11 con el de p.101 (Tafí, impreso invertido bajo la banda). El tamaño de cada fila también es coherente con los sobres del acta.
- Correcciones a las pistas tentativas de p.102: Trancas Padrós **448** (no 443), Martínez **701** (no 731); Tafí Aragón **1566** (no 1766), Mendoza Padilla 1573.
- Controles: Padrós, Prat Gay, Martínez y López García suman exacto la proclamación de p.103; E. López suma 2.506 = PS en la Wikipedia. Aragón 26.712 frente a 26.755 de la Wikipedia (total impreso de p.102 compatible con 26.712).
- Pendientes: diez celdas (ver LEEME); circuitos por bloque (la tabla departamental no los necesita).

## Atlas (5-nov-2026, pedido del usuario: «extrapola para trancas y fue»)
`mapas/mapa1936/atlas_1936.html`; ver `mapas/mapa1936/LEEME_1936.md`. Trancas: `departamentos.py` agrega `votos_con_extrapolacion` y `extrapolacion`.
