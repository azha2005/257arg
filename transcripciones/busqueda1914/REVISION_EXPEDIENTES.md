# Revisión de expedientes y prioridades

Consulta: 15 de octubre de 2026. Las páginas PDF se cuentan desde 1. Se descargaron los originales públicos, se abrieron con PyMuPDF y se produjeron hojas de contacto en `inspeccion/`. Una inspección de estructura no equivale a transcribir íntegramente un manuscrito. Las conclusiones siguientes explicitan ese límite.

## Prioridad solicitada: competitividad provincial

Orden por diferencia entre los dos primeros porcentajes publicados en la tabla provincial de `scratch_w1914_leg.txt`, cotejada con el artículo accesible en https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1914 : Jujuy 2,70; Córdoba 4,39; Capital 4,54; Buenos Aires 5,86; Entre Ríos 8,42; Tucumán 17,74; Catamarca 28,05; Corrientes 28,93; Santa Fe 35,66; Mendoza 37,11; San Juan 51,53; La Rioja 83,16; Salta 91,79; Santiago del Estero 95,22 puntos porcentuales. Diferencias de porcentajes redondeados, no estimaciones de probabilidad de alternancia.

**Jujuy requiere una excepción:** los 3.806 y 3.606 votos son una propuesta de comisión tras deducciones. Wikipedia indica que ambos despachos se rechazaron y la elección se anuló el 24 de julio de 1914. El margen sirve como pista de controversia, no como certificación de resultado definitivo. En Tucumán el segundo renglón es Eduardo Paz, rotulado «Otros» por Wikipedia; no se agrega a otra fuerza por conjetura.

## Descargas y alternativas

13 de los 15 localizadores buscados devolvieron PDF; Corrientes 21-D-1914 y Mendoza 29-P-1914 devolvieron HTTP 404. **Ambos originales se recuperaron por Wayback**:

- https://web.archive.org/web/20220509003432id_/https://apym.hcdn.gob.ar/uploads/expedientes/pdf/21-d-1914.pdf
- https://web.archive.org/web/20220509003441id_/https://apym.hcdn.gob.ar/uploads/expedientes/pdf/29-p-1914.pdf

Se ensayaron también 21-P y 29-D para comprobar la letra: ambos son Buenos Aires, no sustitutos para Corrientes/Mendoza. Los nombres originales de descarga se conservan para auditar el ensayo; su asignación real queda en el inventario. No confundir el nombre de archivo provisional con evidencia de provincia.

## Observaciones por expediente

| Distrito buscado | Expediente y páginas | Hallazgo y alcance de la revisión |
|---|---|---|
| Capital | 13-D-1914, 8 páginas; PDF 5 y 7 | Diploma de Antonio Zaccagnini y acta general del distrito Capital. Inspección de las ocho imágenes: cómputo provincial por candidatos y narrativa, sin cuadro por circunscripciones. No completa Puerto ni concilia por sí solo la tabla de Cantón. |
| Buenos Aires | 21-P-1914, 20 páginas; 29-D-1914, 16 páginas | Ambos originales alternativos corresponden a Buenos Aires; acta general de 13 de abril. No usarlos como Corrientes/Mendoza. El trabajo departamental procede de Cantón; ver parte Buenos Aires. |
| Córdoba | 26-P-1914, 102 páginas | Planillas por candidato desde PDF 45; resumen territorial PDF 97, complementarias PDF 99, total general PDF 101. Transcripción y discrepancias en `partes/cordoba_hcdn/`. No sustituir la lista incompleta por suma de candidatos. |
| Entre Ríos | 19-D-1914, 18 páginas | Portada/diploma de Emilio Marcó; acta general manuscrita PDF 7-17, totales por candidato PDF 14-16. Inspección de todas las hojas de contacto: sin tabla departamental. Hay incidencias de mesas, que no equivalen a votos de fuerzas por departamento. Falta Concepción del Uruguay en Cantón; no se obtiene como residuo provincial. |
| Jujuy | 23-P-1914, 28 páginas | Votos de tres mesas propuestos para anulación y dictamen controvertido; sin cuadro departamental completo. Se conservan fuera del CSV consolidado de resultados. Ver `partes/jujuy/`. |
| Tucumán | 343-D-1914, 12-D-1915 y 5-D-1915 | Descartados para el comicio general tucumano: son elecciones parciales de Entre Ríos, Jujuy y Santiago, respectivamente. Es un error de asignación del prompt; Wikipedia los ubica en su material de elecciones parciales. Ver revisión regional. |
| Catamarca | 42-D-1914, 14 páginas; PDF 3 y 13, 5-11 | Confirmados Catamarca y elección de 22 de marzo + complementaria 5 de abril. Las dos actas finales repiten cómputo provincial por candidato; hojas intermedias narran aprobación/anulación de mesas. No hay cuadro departamental en las 14 imágenes inspeccionadas. El acta refiere el envío de actas/listas en paquete sellado, lo que deja una pista archivística. |
| Corrientes | 21-D-1914 vía Wayback, 6 páginas; PDF 3-5 | Tabla departamental por doce candidatos, con totales y acta. Nueva provincia con detalle territorial; transcripción en `partes/corrientes/`. Incluye complementarias de 12 de abril. |
| Santa Fe | 27-D-1914, 22 páginas | Revisión regional: incidencias territoriales y totales provinciales por candidatos, sin cuadro departamental. Hemeroteca recuperada como pista; no como votos. |
| Mendoza | 29-P-1914 vía Wayback, 70 páginas | Confirmado distrito electoral de Mendoza; PDF 7: elecciones de 22 de marzo y 5 de abril, y complementarias de 19 de abril. PDF 11-69 es acta mecanografiada con resultados de urnas por mesa/circuito y referencias a departamentos. Inspección de estructura de las 70 imágenes, **sin transcripción íntegra ni agregado**. Es una fuente recuperada útil para reconstruir, no ausencia documental. Se pospone el agregado frente a Córdoba/Corrientes por la nueva prioridad. |
| San Juan | 19-P-1914, 72 páginas | Confirmado Juzgado Federal de San Juan. PDF 11 tiene resumen mecanografiado; manuscrito de escrutinio desde PDF 7 hasta 72. Sólo reconocimiento de estructura y páginas finales: requiere lectura por mesa/circuito, no se afirma que carezca de desglose. |
| La Rioja | 13-P-1914, 50 páginas | **Fuente territorial recuperada**: PDF impares 29-47 traen planillas mecanografiadas de mesa y circuito bajo colegios/departamentos (Capital, Chilecito, Famatina, Arauco y otros); PDF 25/27 contienen cómputos e incidencias. Inspeccionadas esas hojas: listas explícitas por candidato, blancos y «varios». Pendiente transcribir y cotejar su estado frente a actas anuladas; no sumar sin determinar ese alcance. No se priorizó sobre distritos competitivos. |
| Salta | 27-P-1914, 84 páginas | Confirmado distrito electoral de Salta; resumen PDF 5/7; acta manuscrita e incidencias. PDF 73/74 incluye cómputos provinciales de complementarias. Sólo reconocimiento inicial/final, no transcripción exhaustiva. No completar por la tabla de 1912 del artículo académico. |
| Santiago | 18-P-1914, 12 páginas | Confirmado Santiago, acta de ordinaria y complementaria de 22 de marzo y 12 de abril. Inspeccionadas doce imágenes: acta general manuscrita y total provincial, sin tabla departamental visible. PDF 5-D-1915 corresponde a otra elección y no cierra este hueco. |

## Otras consultas de acceso

Se intentaron mediante el lector web https://books.google.com/books?id=tK9PAQAAMAAJ&pg=PA487 y https://babel.hathitrust.org/cgi/pt?id=uiug.30112063835463&seq=412 : ambos devolvieron error interno de recuperación en ese canal. Esto no prueba que los libros sean de pago ni que falten las páginas. **El segundo localizador tampoco es Tucumán:** el wikitext local lo cita en la elección parcial de Córdoba de abril/mayo de 1915 (línea 2565). Sólo Google Books PA487 sigue siendo pista de la elección general tucumana. No se transcribieron números de un resultado de búsqueda. No se sortearon restricciones ni captchas.

No se creó atlas ni se modificaron `mapa*/`, `commons/` o `wikitop.py`. No se escribió memoria persistente: la nota de investigación queda en esta carpeta del proyecto.
