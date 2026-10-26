# Búsqueda de diputados nacionales de 1912

Consulta y transcripción: **15 de octubre de 2026**. Resultado parcial de la búsqueda. No es una base nacional completa ni una certificación de todas las cifras. No se construyó un atlas ni se modificaron `mapa*/`, `commons/` o `wikitop.py`.

## Entrega y hallazgos

- **Estado actualizado:** ver [PROGRESO_COMPETITIVAS_1912.md](PROGRESO_COMPETITIVAS_1912.md). Mendoza aporta 16 unidades territoriales y 188 posiciones de mesa; San Juan tiene 107 registros y cuatro candidatos principales, todavía con diferencias contra el resumen provincial. Tucumán queda relegado por decisión del usuario.
- `datos_1912_depto.csv`: **477 filas, 450 numéricas y 27 vacías**. Incluye Capital/Córdoba/Santa Fe, más **65 filas de Mendoza y 128 de San Juan** (32 rótulos territoriales literales). Las reservas se identifican en `nota`; un cierre provincial no convierte una omisión por mesa en cero. Puerto y cinco filas cordobesas sin cifras se conservan explícitamente.
- **Nuevo:** votos por candidato de Rosario, Las Colonias, San Lorenzo, Vera y Belgrano, desde el diario Santa Fe del 18, 20 y 23 de abril. No son votos por lista mutuamente excluyentes. No se reconstruyeron partidos sumando candidatos.
- **Recuperados 13 PDF de expedientes:** diez provincias y Capital/Córdoba, incluyendo ambas variantes 26-P y 26-D de Tucumán. Tres ya estaban en Descargas; diez se descargaron en esta búsqueda. Recuperar un expediente no equivale a haber transcrito o validado todas sus mesas.
- `fuentes.csv`: **36 registros** con localizador, fecha, tamaño, estado y SHA256, incluido un localizador DSCD obtenido por búsqueda interna (sin imagen de página recuperada). `fuentes/diarios_descargas.csv` registra las URL y tamaños de las teselas; `fuentes/dscd_consultas.csv`, las consultas al tomo. Las imágenes compuestas conservan el orden de las teselas.
- `controles_canton.csv`, `sumas_canton.csv` y `comparacion_wikipedia.csv`: controles y diferencias sin corregir las fuentes.
- Nuevos archivos: `mendoza_mesas_candidatos.csv`, `mendoza_mesas_controles.csv`, `mendoza_totales_territoriales.csv`, `mendoza_cotejo_provincial.json`, `san_juan_mesas_candidatos.csv`, `san_juan_mesas_controles.csv`, `santa_fe_participacion_1912.csv`, `santa_fe_participacion_controles.json` y `santa_fe_provincial_25abril.csv`. Los archivos `mendoza_ciudad_*` son el subconjunto de la ciudad; **no concatenarlos** con el archivo provincial, que ya los incluye.
- Scripts de reproducción: `transcribir.py` genera el CSV desde la transcripción manual incorporada; `recuperar.py` recupera expedientes; `diarios.py` recupera las ediciones iniciales 10/23 de abril; otras ediciones y recortes tienen URL registradas en el log. `cerrar.py` actualiza el registro y verifica integridad referencial y aritmética. Ejecutar desde la raíz del proyecto.

El zip previo `canton_diputados_1912_transcripcion.zip` no apareció entre los archivos consultados de raíz/Descargas; se reconstruyó la transcripción directamente desde las imágenes. Coincide en cantidad con las 209 filas/184 cifras anunciadas, pero no se afirma una comparación celda a celda con ese zip ausente.

## Los seis supuestos huecos de Cantón

Revisión visual del tomo II, PDF 17-18, páginas impresas 3-4, y tomo I, PDF 50-51, páginas XLVII-XLVIII. Las imágenes y los dos PDF completos están en `fuentes/`.

| Unidad | Qué dice la fuente | Resultado |
|---|---|---|
| Capital: Puerto | Unidad censal sin aplicación a la división electoral, tomo I XLVII | No es una circunscripción electoral faltante. Sin cifra; no cero. |
| Córdoba: General Roca | Incluido en Juárez Celman, tomo I XLVIII | No se puede desagregar; Juárez Celman tampoco tiene cifra en la tabla de 1912. |
| Córdoba: Presidente Roque Sáenz Peña | Incluido en Juárez Celman, tomo I XLVIII | Mismo límite; no repartir ni duplicar votos. |
| Córdoba: Juárez Celman | `**` en la tabla | Sin cifra en Cantón; el apéndice no identifica una unidad receptora para esta fila. |
| Córdoba: Marcos Juárez | `**` en la tabla | Sin cifra; no es una falla del OCR. |
| Córdoba: Punilla | `**` en la tabla | Sin cifra; no es una falla del OCR. |

La nota `**` significa subsumido en una unidad mayor o no tomado en cuenta. El pedido de completar estas cifras mirando mejor la imagen no puede satisfacerse con esta tabla: las cifras no están impresas.

**Capital requiere una reserva adicional:** el título dice 1912, pero el pie cita La Nación del 7 y 14 de abril de 1916. La clave tipográfica no identifica la columna 4; una anotación manuscrita dice Socialista. Se conserva como `Socialista [columna 4]`, con advertencia en cada fila. El expediente 12-D-1912 recuperado ofrece el cómputo distrital por candidato, pero no valida por sí solo las veinte filas territoriales. No se decidió por cuenta propia que el pie sea una errata.

## Estado por distrito

En esta tabla «revisado» distingue lectura de páginas relevantes e inspección general por miniaturas de una transcripción exhaustiva. No se declara ausente una tabla por haber fallado su descarga o su OCR.

| Distrito | Qué se obtuvo y nivel | Fuente y revisión | Qué falta / descarte / siguiente pista |
|---|---|---|---|
| Buenos Aires | PDF de 6 páginas; cómputo provincial por candidato | `buenos_aires_19-d-1912.pdf`, especialmente PDF 3-5; inspección del documento completo por miniaturas y lectura de PDF 4 | No aparece cuadro por partido en este expediente corto. El resumen dice que hubo mesas sin elección/falta de actas. Buscar actas parciales y diarios, no deducir departamentos de los totales. URL en fuentes.csv. |
| Capital Federal | 20 circunscripciones, 100 cifras de columnas políticas; Puerto sin dato electoral aplicable | Cantón II PDF 17; Cantón I PDF 50; `capital_federal_12-d-1912.pdf` PDF 7 y vista general de 18 páginas | Cotejo de la fecha 1912/1916 y de la columna 4. El acta recuperada es distrital; incluye también senador, que no se mezcló con diputados. |
| Catamarca | Expediente 28-P recuperado, 16 páginas; total provincial y antecedentes de complementarias | `catamarca_28-p-1912.pdf`, PDF 5 leído, vista general | Acta del 3 de mayo incorpora repetición del 28 de abril de once mesas anuladas. No es exclusivamente el escrutinio inicial del 7/4. Ibañez–Alvero ya estaba descartado como tabla departamental en el inventario previo; conserva pistas de archivo/prensa. |
| Córdoba | 21 departamentos con cuatro columnas políticas; cinco filas sin cifra | Cantón II PDF 18 e I PDF 51; `córdoba_3-d-1912.pdf`, PDF 6-8 leídos; vista general 14 páginas | La suma territorial de votantes cierra con Wikipedia, pero los bloques no coinciden. El 3-D resume candidatos provinciales y debates de votos impugnados/complementarias. Buscar Anuario Estadístico provincial 1912 y actas parciales para las cinco filas. |
| Corrientes | Expediente 51-D, 12 páginas; acta general y cómputo por candidato | `corrientes_51-d-1912.pdf`, PDF 8 renderizado e inspección general | No se obtuvo tabla departamental integrada. La portada interna menciona elecciones de marzo: cotejar calendario y actas antes de asignarle 7/4 automáticamente. Solís Carnicer trata mucho de elecciones provinciales: no mezclar. |
| Entre Ríos | Expediente 46-D, 14 páginas; actas y resultado provincial por candidato | `entre_ríos_46-d-1912.pdf`, PDF 9-10 leídos y vista general | PDF 9 remite a actas 31, 53 y suma general, sin una matriz departamental en esas páginas. Revisar actas parciales referidas y El Entre Ríos; La Acción comienza en mayo, según inventario previo. |
| Jujuy | Nuevos localizadores bibliográficos para el escrutinio parlamentario | Etcheverría, `perez_diplomas.pdf`, PDF 6-7, notas 15-16 | DSCD 1912 I **514-523** además de 543/563 indicadas por Wikipedia. No se recuperaron esas páginas primarias. Google Books y búsqueda específica de IA no dieron imágenes/volumen utilizable; no prueba inexistencia. |
| La Rioja | Nuevos localizadores del escrutinio hecho en Diputados | Etcheverría, PDF 6-7, nota 15 | DSCD 1912 I **496-514**, además de 543/563. La junta no completó el escrutinio; revisar el cómputo parlamentario. No se recuperó matriz territorial primaria. |
| Mendoza | **16 unidades, 188 posiciones de mesa; sumas expresas Benegas 15.833/Gaviola 8.247, idénticas al acta** | `mendoza_42-d-1912.pdf`, páginas sustantivas PDF 7-105 leídas visualmente; `mendoza_mesas_*` | Falta cómputo localizado de San Martín 7 y dos cifras individuales no expresas. Menores suman 70 frente a 74: diferencia -4. Complementarias 28/4 sustituyen mesas anuladas. Ver AMPLIACION_1912.md; no certificar todos los votantes/blancos. |
| Salta | Expediente 49-D, 26 páginas, con referencias a mesas y discrepancias de actas/sobres; fuente UNSa descargada | `salta_49-d-1912.pdf` PDF 7-8 leídos y vista general; `salta_unsa.pdf` texto consultado | El acta enumera mesas territoriales; falta transcripción completa por candidato. UNSa confirma `Estadística Electoral 1912-1938`, Juzgado Federal, Secretaría Electoral; no se obtuvo ese registro. Cinco candidatos de Capital en Correa–Quintana siguen pendientes de validación territorial/primaria, como ya decía el inventario. |
| San Juan | **107 registros de mesa, 428 cifras de cuatro candidatos, 128 sumas territoriales** | `san_juan_27-d-1912.pdf`, PDF 5-78 y 81-89; `san_juan_mesas_*`, `san_juan_cotejo_provincial.json` | Diferencias -3/+1/+20/+14 contra resumen provincial; PDF 85 menciona ajustes por diferencias de sobres/actas. Faltan cierre de esas diferencias, votos dispersos y homologación territorial. Complementarias 21/4 sustituyen originales anulados. Ver PROGRESO_COMPETITIVAS_1912.md. |
| San Luis | Expediente 44-D, 16 páginas; acta general y antecedentes | `san_luis_44-d-1912.pdf`, PDF 13 renderizado y vista general | Cotejar con DSCD 1912 I 117-125, 521-525, 581-600, 609-629, localizados en Etcheverría. El cambio Origone/Pastor implica resolución parlamentaria posterior; no equiparar junta y resultado aceptado. Sin nueva matriz departamental. |
| Santa Fe | **Cinco departamentos con votos por candidato; además participación en 19 y crónica provincial de cierre** | Diario Santa Fe 16/4 (6508), 18/4 (6509), 20/4 (6510), 23/4 (6512), 25/4 (6514); imágenes y log de teselas | Los cinco departamentos siguen parciales. Participación: 74.878 sufragantes y 488 mesas cierran; una lectura de inscriptos insegura. Crónica final tiene cifras distintas de Wikipedia y Fernández disminuye respecto de la anterior. No sustituir cifras automáticamente ni distribuir datos provinciales. |
| Santiago del Estero | Sin nueva cifra departamental validada | Guzmán local y resultado académico recuperado por búsqueda; localizador recopilación 1946 I p. 343 del inventario | Los 34 votos socialistas de ciudad capital no precisan suficientemente cargo/unidad: no se integran. Buscar la recopilación y prensa; no reemplazar con elecciones provinciales. |
| Tucumán | 26-P: **117 páginas**, actas originales/complementarias; 26-D: 4 páginas | `TUCUMAN_INVENTARIO.md`; PDF 88-112 cotejados visualmente en esta tanda | **Relegado por decisión del usuario**, para priorizar provincias competitivas. Páginas 108/110 y 109/111 repiten secuencias con variantes: conservar versiones, no sumarlas ni elegir automáticamente la última. Sin nuevas cifras incorporadas. |

Los territorios nacionales no votaban diputados en este comicio: no se añaden como huecos o votos cero.

## Controles y discrepancias

1. **Córdoba:** las 21 filas numéricas cumplen exactamente `UCR + Unión Nacional + Constitucional + Autonomista Nacional = votantes`. Suma provincial de votantes **57.148**, igual al total de la tabla provincial de Wikipedia. Suma de inscriptos **96.489**, frente a **99.929** de Wikipedia: diferencia **-3.440**. No se atribuye el residuo a un departamento.
2. Las columnas cordobesas suman UCR **14.011**, Unión Nacional **12.829**, Constitucional **19.432**, Autonomista Nacional **10.876**. Wikipedia usa máximos provinciales por candidato: **15.690**, **14.850**, **23.582**, respectivamente; no trae una cuarta fila equivalente de PAN. Diferencias respectivas **-1.679**, **-2.021**, **-4.150**. No se reagrupó PAN para forzar el cierre. La igualdad en votantes no valida la equivalencia de bloques.
3. **Capital:** suma de inscriptos **123.936** y votantes **104.450** frente a **126.303** y **106.157** de Wikipedia, diferencias **-2.367** y **-1.707**. Las cinco columnas políticas suman **148.056**, superan los votantes en todas las filas; la propia página lo advierte. No se interpreta como error aritmético que deba corregirse, porque se votaban varios candidatos. Comparación por columna en `comparacion_wikipedia.csv`; además persiste la reserva de fecha del pie.
4. **Santa Fe:** no se publica total de votantes junto a cada cuadro transcrito. No es válido sumar candidatos de una misma lista ni comparar la suma de sólo cinco departamentos con el total provincial. Por eso no se declara cierre provincial. **Belgrano repite Francisco G. Valdez con 183 y 933**: dos filas originales, nunca sumadas ni corregidas. **Rosario/Miguel Coronado y San Lorenzo/Cornelio Casablanca** quedan sin número por lectura insegura. Los candidatos no nombrados en estos cuadros no se convierten en cero.
5. **Mendoza:** PDF 105 da un total general y un saldo en blanco no cuantificado. Se registró el localizador, sin imputar ese saldo. No se mezclaron mesas de documentos duplicados/espejados.

## Cinco cierres más baratos (priorización inicial)

La ampliación ya resolvió la transcripción de la ciudad de Mendoza y añadió departamentos y San Juan. El **orden actualizado** está al final de `AMPLIACION_1912.md`; esta lista conserva la estimación inicial para distinguir lo que ya se abordó.

Estimaciones de trabajo activo, no promesas; se refieren a un resultado concreto y condicionado por legibilidad.

| Orden | Cierre | Estimación |
|---|---|---|
| 1 | Cotejar las dos cifras dudosas de Rosario y San Lorenzo contra otra edición/acta, y la repetición de Valdez en Belgrano | 30-90 min; puede requerir otra fuente si la imagen no mejora |
| 2 | Completar los cuadros santafesinos de otros días de abril, distinguiendo complementarias | 2-5 h para ampliar varios departamentos; no garantiza toda la provincia |
| 3 | Transcribir las 45 mesas de Mendoza ciudad, documentadas desde PDF 7, y su cierre local si aparece | 3-6 h, incluyendo segunda lectura y sumas |
| 4 | Transcribir un departamento pequeño de San Juan con sus mesas explícitamente identificadas | 2-4 h; primero comprobar que están todas las mesas y su resolución |
| 5 | Transcribir un conjunto territorial pequeño de Tucumán en 26-P, quitando páginas duplicadas | 2-4 h; no equiparar localidad y departamento sin evidencia |

Puerto queda explicado sin trabajo adicional; no se cuenta como dato nuevo recuperable. Las cinco filas cordobesas no son cierres baratos de OCR.

## Cinco cierres más caros

| Orden | Cierre | Estimación |
|---|---|---|
| 1 | Buenos Aires completa por partidos: el 19-D sólo ofrece resumen | 2-5 jornadas de búsqueda y transcripción; más si las actas parciales no están digitalizadas |
| 2 | Córdoba: desagregar/completar las cinco filas ausentes mediante Anuario 1912 o actas nuevas | 1-3 jornadas si aparece el volumen; sin plazo fiable si exige archivo presencial |
| 3 | Registro electoral de Salta 1912-1938 y cotejo de escrutinio final | 1-3 jornadas de trabajo tras obtenerlo; acceso externo de duración indeterminada |
| 4 | Jujuy y La Rioja: recuperar DSCD y reconstruir cómputo parlamentario con anulaciones | 1-3 jornadas por distrito tras recuperar páginas; sin garantía de detalle territorial |
| 5 | Santiago del Estero: localizar fuente primaria desagregada | 2-5 jornadas de búsqueda; plazo abierto si sólo existe documentación presencial |

Mendoza, San Juan y Tucumán completos siguen siendo tareas considerables de transcripción, aunque ya no estén bloqueados por falta de PDF.

## Búsqueda y límites de acceso

Se consultaron `AGENTS.md`, `LEEME.md`, la sección 1912 de `INVENTARIO_Y_BUSQUEDA.md`, el wikitext local y los PDF originales. No se utilizó Gemini como dato.

Primer intento de descarga desde la ejecución restringida: rechazo de conexión `WinError 10061`. Un segundo intento con acceso de red autorizado descargó los expedientes. Por tanto el primer error **no demuestra caída del servidor**. El navegador de búsqueda tampoco pudo abrir directamente varios PDF, pero sí pudieron recuperarse por descarga pública. No hubo CAPTCHA ni cuentas de pago en las descargas completadas.

La consulta web a Wayback para 17-D y al índice CDX para 44-D no dio una respuesta utilizable; no se necesitó Wayback una vez recuperados los originales. Google Books `h6VPAQAAMAAJ` páginas 543/563 no ofreció imágenes por la herramienta; sus endpoints públicos dieron `cb({})` y búsqueda sin resultados, guardados como evidencia. La búsqueda de IA `title:(Diario sesiones diputados) AND year:1912` devolvió cero resultados; esa consulta específica no prueba ausencia del tomo en IA. No se buscó saltar restricciones.

Búsquedas académicas: combinaciones de `1912`, `diputados`, `departamentos`, `escrutinio` y Buenos Aires, Santa Fe, Entre Ríos, Corrientes, Tucumán, Mendoza, Catamarca, Jujuy, La Rioja y Santiago. Muchos resultados correspondían a gobernadores, legislaturas provinciales o a 1916/1922: no se integraron. La nueva pista útil es **Etcheverría, Rubén Osvaldo, “La reforma política y los rechazos de legisladores nacionales electos 1912-1930”**, [PDF](https://cdsa.aacademica.org/000-008/2.pdf), notas 15-16, que mejora los localizadores de La Rioja/Jujuy. El nombre local `perez_diplomas.pdf` es sólo un identificador de descarga; no indica autoría.

Pistas abiertas ya identificadas: [UNSa](https://portalderevistas.unsa.edu.ar/index.php/cdh/article/download/611/591/2018), [hemeroteca Santa Fe](https://www.santafe.gov.ar/hemeroteca/diario/6512/?page=1), [Wikipedia 1912](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1912). Las URL individuales de expedientes y copias académicas están en `fuentes.csv`.

No se enviaron consultas a instituciones ni se modificó memoria personal. Las estimaciones y el orden anterior quedan como siguiente trabajo; la entrega actual distingue fuentes recuperadas, cifras transcritas y verificación pendiente.
