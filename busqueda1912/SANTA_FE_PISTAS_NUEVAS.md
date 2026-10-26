# Santa Fe 1912: revisión acotada de fuentes

Consulta: 15/10/2026. No se modificaron scripts ni tablas de datos. No se recuperó un nuevo departamento con votos por candidato en esta revisión.

## 17-D-1912: localizadores precisos y una cautela nueva

Original: https://apym.hcdn.gob.ar/uploads/expedientes/pdf/17-d-1912.pdf

- PDF 3, carta de 29/4: Rogelio Araya **36.747**; Benjamín Ávalos **36.513**; Miguel S. Coronado **36.147**. Por tanto, la comparación de AMPLIACION_1912.md entre «Ábalos 36.679» del diario y «36.747 de Wikipedia» compara candidatos distintos: 36.747 es Araya en el diploma. Esto no resuelve por sí solo todas las diferencias del diario del 25/4.
- PDF 13 (folio sellado 6): no funcionaron Ceres mesas 2/4, departamento San Cristóbal, ni El Toba mesas 1/2, departamento Vera. Es cobertura de mesas, no resultado por candidato.
- PDF 15 (folio 7): incidencias de sobres/votantes por mesa de Capital, Rosario y San Lorenzo. No constituye cómputo territorial de candidatos.
- PDF 23-26: resoluciones de validez y protestas; PDF 25 menciona 183 sufragantes y 222 electores de Pueblo Pérez. **No es total del departamento Rosario**.
- PDF 27 (folio sellado 13): lista de mesas anuladas: Rosario sección 3 mesa 6 y Alberdi mesa 3; Las Colonias/Progreso mesa 2; General López/Maggiolo mesa 1; Vera/Jobson mesa 6; Belgrano/Las Rosas mesa 5; San Cristóbal/Calchaquí y Ripamonti mesas únicas; Castellanos/Rafaela mesa 2, Sunchales mesas 1/2 y San Vicente mesa 2; Iriondo/Santa Teresa mesa 3. Convoca nueva elección para el domingo 21 del corriente. **Los cuadros departamentales de diarios anteriores al 21/4 no quedan certificados como definitivos** por transcribirlos bien: requieren cotejo con estas sustituciones.
- PDF 30: sesión reanudada el 26, resolución de impugnados y comienzo del cómputo **provincial** por candidato; continúa PDF 31-34. Las páginas con columnas numéricas no son una matriz de departamentos.

Imágenes auxiliares nuevas: `fuentes/sf_pistas_p13.png`, `sf_pistas_p15.png`, `sf_pistas_p23.png`, `sf_pistas_p25.png`, `sf_pistas_p26.png`, `sf_pistas_p27.png`. Son renders del PDF, no fuentes independientes.

## Hemeroteca: dos comprobaciones adicionales

1. https://www.santafe.gov.ar/hemeroteca/diario/6513/?page=1 — **24/4/1912, página 1, columna central, «Junta Electoral»**. Enumera Garay, Castellanos, General López y Belgrano, pero el primer renglón dice expresamente **elecciones del 31 de marzo**. Incluye electores, senadores y diputados provinciales; se descarta para diputados nacionales del 7/4. Recorte legible: `fuentes/sf_pistas_6513_p1_junta.png`. Teselas: `https://www.santafe.gov.ar/hemeroteca/tile/6513-1-4-X-Y.jpg`, X=6..8, Y=7..11.
2. https://www.santafe.gov.ar/hemeroteca/diario/6511/?page=2 — **21/4/1912**, página de sociales, anuncios y opinión; encabezado impreso «Pág. 3». Inspección visual de página completa: no se localizó cuadro departamental nacional. Archivo: `fuentes/sf_pistas_6511_p2.png`. Teselas: `https://www.santafe.gov.ar/hemeroteca/tile/6511-2-3-X-Y.jpg`, X=0..7, Y=0..7.

La descarga restringida dio WinError 10061; los mismos recortes se recuperaron con acceso de red autorizado. No es evidencia de caída del servidor. El visor web de búsqueda no pudo abrir las páginas; la descarga pública por teselas sí funcionó.

## Búsqueda externa y límite

Consultas web: Santa Fe + 1912 + escrutinio + departamentos; 7 de abril + San Cristóbal + votos; diputados + abril + hemeroteca. Los resultados útiles visibles remiten al mismo archivo o al ensayo provincial del 31/3; no se localizó una nueva tabla primaria nacional desagregada. Esto describe estas consultas, no afirma inexistencia documental.

Prioridad siguiente: las **actas parciales** que el acta general incorpora/referencia y diarios de los días efectivos de escrutinio, manteniendo separado el resultado original del 7/4, la complementaria del 21/4 y el cierre de la Junta del 26/4. No distribuir el total provincial ni sumar candidatos de una lista.

## Segunda pasada: cifras inseguras y diploma

Se verificó **visualmente** PDF 3 mediante `fuentes/sf_pistas_p3.png`: Araya 36.747; Ávalos 36.513; Coronado 36.147; Valdez **35.855**; Pesenti 17.856; de la Torre **17.630**. Las lecturas OCR 35.355 y 17.633 no coinciden con esta imagen.

Se aislaron las filas originales de 18/4 y 20/4 en `fuentes/sf_pistas_rosario_cifras.png` y `fuentes/sf_pistas_sanlorenzo_cifras.png`. Son ampliaciones para inspección del zoom 4 ya conservado, **no mayor resolución ni mejora de contenido**. Rosario/Coronado conserva ambigüedad en el segundo dígito (9?55). En San Lorenzo/Casablanca la lectura visual probable es **1426**, pero se solicita segunda lectura independiente antes de incorporarla: no se confirmó con fuente alternativa.

Intento de zoom 5: los endpoints públicos respondieron texto «Error. No existe el archivo al cual se quiere acceder»; los archivos `sf_pistas_tile_...-5-...jpg` guardan esas respuestas textuales, **no imágenes utilizables**. No se infiere que exista un nivel mayor accesible. URL de ejemplo: https://www.santafe.gov.ar/hemeroteca/tile/6509-1-5-14-9.jpg . No se llenó ninguno de los dos vacíos del CSV ni se usó un residuo.
