# Investigación de diputados nacionales de 1914

**Santa Fe, relectura de prensa (15/10/2026):** se agregaron totales impresos de Castellanos, Belgrano e Iriondo (1/4, id7323 p3); los parciales globales son 196 filas/194 cifras/2 vacíos y el principal no cambia (1.192/1.094/98). Santa Fe: 10 departamentos con total de prensa y 2 con suma parcial; faltan La Capital, 9 de Julio, Garay, San Javier, San Cristóbal, General López, Caseros, Constitución y San Justo. Ver `fase3/santa_fe_prensa/LEEME.md`: esas tablas no están en el diario *Santa Fe* del 24/3 al 8/4.

**Santa Fe, revisión de fase3:** selección ampliada a diez departamentos, siete con resúmenes publicados y tres sólo con sumas parciales (Capital,Castellanos,General López).152 filas/150 cifras/2 vacíos; componentes de respaldo separados. Se confirmó Lagos/San Jerónimo1354 y se corrigió el control Lucero: HCDN14948 frente Wikipedia14943. Trece cifras de una mesa complementaria de Roldán se conservan aparte. Los parciales globales son ahora166 filas/164 cifras/2 vacíos; el principal no cambia. Estado actual y límites: `fase3/santa_fe/LEEME.md`. Los recuentos y descripciones anteriores de Santa Fe que siguen corresponden a entregas previas.

**Actualización posterior al cierre,15/10/2026:** por pedido del usuario se continuó Santa Fe y se calculó el residuo de Concepción del Uruguay. Santa Fe mantiene siete departamentos parciales: la ampliación de prensa no aportó nuevas cifras verificadas (`fase2/santa_fe/CONTINUACION.md`). Para Concepción se guardaron **UCR2900, Provinciales3859 y Carbosistas687** como inferencia condicional separada (`fase2/entre_rios/INFERENCIA_CONCEPCION.md` e `inferencia_concepcion.csv`). No cambian los recuentos de observaciones ni se presentan los residuos como transcripción. La instrucción previa de no imputar tiene esta excepción expresamente solicitada por el usuario.

Consulta: **15/10/2026**. Elección principal: **22/3/1914**, con complementarias y cómputos posteriores identificados por fuente. San Luis no renovó diputados y los territorios nacionales no elegían diputados: no son huecos ni ceros.


## Resultado y archivos

El consolidado principal contiene **1.192 filas: 1.094 cifras y 98 ausencias explícitas, en siete distritos**. Sus238 rótulos territoriales incluyen unidades sin cifras y nombres históricos: no equivalen a238 departamentos completos ni a cobertura nacional.

Frente a la entrega anterior (974 filas,874 cifras), se agregan La Rioja y Mendoza y se reemplaza Córdoba por una derivación con complementarias, conservando la principal aparte. Son **220 cifras adicionales en la selección principal**, con magnitudes y estados de cómputo distintos según fuente.

- `datos_1914_depto.csv`: selección territorial. Buenos Aires, Capital y Entre Ríos de Cantón; Corrientes por candidato con complementarias; Córdoba derivada de principal más complementaria; La Rioja según mesas declaradas válidas por Comisión; Mendoza sólo principal. Las notas identifican el alcance. **No sumar candidatos de una lista como electores.**
- `datos_1914_parciales.csv`:120 filas,117 cifras y3 vacíos. Santa Fe:106 filas de prensa anterior al definitivo; Tucumán:7 cifras provinciales/mesas citadas en debate; Jujuy:7 cifras sobre deducciones o anulaciones. **No concatenarlo ni sumarlo al principal:** mezcla niveles y estados deliberadamente identificados.
- `datos_1914_canton_comparacion.csv`:590 filas de las cuatro tablas originales; archivo comparativo, no otra capa sumable.
- `fuentes.csv`: manifiesto integrado de fase1 y fase2, con URL, archivo, consulta, tamaño, método y localizador. Conserva intentos fallidos y registros originales; varios identificadores pueden remitir al mismo documento o a una derivación identificada.
- `control_consolidacion.json`, `inventario_pdfs.csv` y `CONTROL_INTEGRACION.md`: recuentos, integridad de PDF y comprobaciones de estructura/referencias. No certifican por sí solos la exactitud electoral.
- `partes/` y `fase2/`: originales, matrices, imágenes, variantes, fuentes e informes particulares. En Mendoza,46 filas de complementarias permanecen en `fase2/mendoza/datos_complementaria.csv`, sin sumarlas automáticamente a la principal.

## Estado por provincia

Los márgenes proceden de la copia local del artículo de Wikipedia y sirven para priorizar; no son conciliaciones propias de las actas.

| Distrito | Margen (pp) | Cobertura y fuente | Estado y pendiente |
|---|---:|---|---|
| Jujuy |2,70*|23-P-1914; debate24/7;3-D y460-P de fase2. Seis deducciones y una anulación anterior documentadas.|*Margen de propuesta de Comisión, no resultado firme. Diploma Bustamante rechazado24/7; libro de Junta devuelto al juzgado30/7. Buscar ese libro y la votación completa; no convertir3874/3817 derivados en cifras publicadas.|
| Córdoba |4,39|25 departamentos,200 filas,166 cifras;26-P-1914 PDF45-101; derivación principal22/3 + complementaria5/4.|Reemplaza la selección anterior, no se anexa a ella. +10 Salas y−43 Del Viso frente al final. Adiciones23/4 sin departamento aparte. General Roca separado. Presidente Roque Sáenz Peña se creó en1937; su ausencia no es un hueco de1914.|
| Capital Federal |4,54|Cantón II PDF20:20 circunscripciones con cifras; Puerto sin cifras.|Cada fila difiere de votantes; no armonizar. La Prensa7/19 abril y La Razón6/13 abril citadas por Cantón siguen pendientes.|
| Buenos Aires |5,86|Cantón II PDF21-24:120 rótulos,304 cifras,56 vacíos; cotejo con93 unidades Lupu.|Diferencias ante Wikipedia: UCR−100, conservadores−3567, PS coincide. No reconstruir subsunciones/vacíos por residuo.21-P y29-D son actas provinciales.|
| Entre Ríos |8,42|Cantón II PDF26:13 departamentos con cifras; Concepción del Uruguay sin cifras. Fase2 revisó seis diplomas adicionales y prensa/bibliografía.|0 cifras nuevas en fase2. La Nación24/29/31 marzo no accesible en colección pública examinada; La Acción31/3 y archivo provincial son pistas.24-P catalogado entrerriano enlaza un PDF de Santa Fe.|
| Tucumán |17,74|Google Books PA485-494;17-P y54/56/59/60-D correctamente identificados. Tres totales provinciales y cuatro cifras de comicios impugnados.|Paz11563/Uttinger11456, diferencia107. PA493 confirma diploma Paz aprobado52 votos entre88. No prueba anulación formal de las mesas debatidas; no restarlas. Las actas anunciadas faltan en los PDF.|
| Catamarca |28,05|42-D-1914 PDF3/13 totales;5-11 incidencias.|Sin tabla departamental. Ibañez-Alvero no aporta1914. Buscar paquete sellado de actas o prensa de Biblioteca Sarmiento.|
| Corrientes |28,93|24 departamentos por doce candidatos,287 cifras y un guion;21-D-1914 PDF3-5 recuperado por Wayback.|Incluye complementaria12/4. Soto+60 y Acosta+1 en sumas; conservar literales. Acta37632 sufragantes frente37496 del artículo; no asignar136 a blancos/nulos.|
| Santa Fe |35,66|Siete resúmenes de Rosario,Vera,San Martín,General Obligado,San Jerónimo,Las Colonias,San Lorenzo; diario31/3,1/4,2/4.106 filas,103 cifras.|Archivo parcial separado. Prensa2/4 difiere del final8/4 HCDN27-D PDF15/16: Araya−480. Tres celdas ilegibles vacías. Buscar publicación posterior y demás departamentos; no repartir diferencias.|
| Mendoza |37,11|16 resúmenes departamentales explícitos del29-P,149 filas principales;46 cifras complementarias aparte.|**Complementaria5/4, no19/4 como decía el informe anterior**: ver PDF7. Principal+complementaria difiere del general en Silveti+180, Ortiz+120, Diógenes+1. Rafael y blancos cierran. No corregir subtotales para forzar cierre.|
| San Juan |51,53|19-P-1914,72 páginas manuscritas; resumenPDF11.|Sin transcripción territorial nueva. Leer mesas/circuitos; no declarar ausencia de detalle por revisión incompleta.|
| La Rioja |83,16|18 departamentos,69 filas agregadas;77 mesas de Comisión en13-P PDF29-47. Cinco anuladas aparte.|García6599,Luna500,otros235 cierran; blancos651 frente646 (+5). Anuladas752 frente729 (+23). «Válidas» describe Comisión, no certifica resolución final de Cámara.|
| Salta |91,79|27-P-1914,84 páginas; resumen5/7,complementarias73/74.|Sin transcripción exhaustiva. Correa-Quintana trae1912; no trasladarlo. Pista: Estadística Electoral1912-1938.|
| Santiago del Estero |95,22|18-P-1914 PDF3-9,acta provincial.|Sin cuadro departamental recuperado. Artículo del socialismo y5-D-1915 no completan este comicio. Buscar actas/prensa.|
| San Luis |—|No renovó diputados.|No es hueco ni cero.|
| Territorios nacionales |—|No elegían diputados.|No son provincias faltantes.|

## Diferencias y límites de uso

Cantón declara partidos; los originales pueden registrar candidaturas y las tablas provinciales usar candidatos representantes de listas. No se convierten esas magnitudes automáticamente. Tampoco se confunden sumas de cifras observadas con ceros para categorías ausentes.

Córdoba conserva la principal, la variante del resumen97 y las adiciones sin departamento. El derivado seleccionado explica cada componente y las diferencias finales. La Rioja conserva las cinco mesas anuladas y una cifra de blancos ilegible de San Blas: el agregado mantiene sólo cifras observadas. Mendoza conserva principal, complementaria y general separados; las diferencias se documentan sin decidir todavía entre error del subtotal, de mesa o del resumen general.

Jujuy sigue incluido en la investigación, con sus tres estados separados: Junta, propuesta de Comisión y Cámara. Tucumán ya tiene confirmación del diploma, pero sus cifras controvertidas siguen siendo testimonios del debate. Santa Fe aporta cobertura documental real de siete departamentos, aunque anterior al definitivo: no se presenta como base final.

## Cinco huecos de menor costo para la próxima tanda

Tiempos de trabajo efectivo aproximados, sin garantía de resolver discrepancias.

1. **Córdoba: segunda lectura puntual de+10/−43.** Original y componentes listos;30-90min. Puede confirmar contradicción sin resolverla.
2. **La Rioja: blancos+5 y anuladas+23.** Páginas y matrices listas;30-90min para cotejo localizado, luego actas originales si persiste.
3. **Santa Fe: tres cifras dañadas y publicación posterior al8/4.**1-3h. Priorizar resumen final y conservar versiones cronológicas.
4. **Mendoza: cotejar subtotales/complementaria contra general.**2-4h, centrado en Silveti/Ortiz/Diógenes; no rehacer todo el manuscrito sin necesidad.
5. **Tucumán: localizar anexos anunciados por17-P y diplomas correctos.**1-3h de catálogo/colección digital si existe copia; de no aparecer, pasa a gestión archivística.

## Cinco huecos de mayor costo

1. **Jujuy:** libro devuelto al juzgado y sesión completa24/7;1-3 jornadas, posible gestión archivística. No excluir la provincia.
2. **Entre Ríos:** Concepción del Uruguay en La Nación24/29/31 marzo, La Acción31/3 o actas originales;1-3 jornadas si requiere sala.
3. **Capital:** resolver criterio de cómputo de Cantón frente a votantes con prensa original;1-3 jornadas.
4. **Catamarca:** actas de mesa remitidas o prensa no digitalizada;1-3 jornadas.
5. **San Juan/Santiago:** manuscrito territorial de San Juan o nuevas fuentes de Santiago;1-3 jornadas según acceso y legibilidad.

Salta también requiere lectura extensa o conseguir la Estadística Electoral. Ninguna búsqueda negativa prueba inexistencia universal.

## Reproducción y cierre

`python busqueda1914/consolidar.py` reproduce la selección principal, el comparativo, los parciales, el manifiesto y controles. Los generadores particulares de Córdoba, La Rioja, Mendoza y Santa Fe conservan matrices y referencias; `fase2/tucuman/cerrar_revision.py` normaliza sus registros y genera las siete filas, incluyendo las fuentes de la continuación pública del debate.

Las sumas y discrepancias están en cada informe; la revisión visual no equivale a una segunda transcripción independiente de cada cifra de fase1. No se construyó atlas ni se modificaron `mapa*/`, `commons/` o `wikitop.py`.
