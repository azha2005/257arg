---
name: transcribir-elecciones
description: Transcribir y cotejar fuentes electorales históricas escaneadas del proyecto dataeleccproyecto, conservando cifras literales, procedencia y reservas. Usar para actas, planillas y tablas de Cantón o archivos; no para construir ni publicar atlas.
---

# Transcripción de fuentes electorales del proyecto

Trabajar desde la raíz de `dataeleccproyecto`. Leer `AGENTS.md` y el `LEEME.md` de la carpeta solicitada antes de elegir fuentes o esquema. Las instrucciones del pedido actual determinan el alcance y si se usan subagentes. No convertir la autorización para transcribir en autorización para mapear, imputar, publicar o modificar atlas.

## Elegir y leer las fuentes

- Usar el inventario existente para ubicar actas y tablas. Una clasificación por OCR o por tamaño no equivale a revisión visual; registrar las páginas realmente examinadas.
- Renderizar el PDF o abrir el TIF y leer la imagen. Usar OCR para localizar páginas, nombres y tablas, y como borrador que se coteja celda por celda.
- Distinguir numeración PDF desde 1, folio manuscrito y número impreso. Registrar al menos la página PDF y el archivo original en toda tabla.
- Si el escaneo es tenue, ampliar y probar rotación/reflejo, canales de color y contraste sobre un recorte local. Conservar el original y anotar la transformación. No usar reconstrucción generativa para leer cifras.
- No confundir texto del reverso, traspaso de tinta o doble imagen con otra tabla. Verificar orientación, encabezados, secuencia y coincidencias antes de incorporar cifras recuperadas.

## Conservar lo que dice el documento

Elegir CSV o JSON según la tabla y conservar la unidad más fina disponible. Incluir fuente, página, unidad territorial, lista/candidato, cifra o marca literal y observación. Separar `votos_literal` de un valor numérico cuando haya marcas o alternativas.

- Cero explícito, guion, asterisco, blanco, dato no publicado, margen cortado e ilegible tienen significados distintos. No convertirlos automáticamente en cero; documentar la convención observada.
- Mantener los votos por candidato cuando la elección permite votar varios nombres. Su suma no es un número de electores. No inventar votos de partido usando suma, máximo o promedio sin una decisión metodológica adicional.
- Separar votantes, sobres de acta, sobres en urna, positivos, blancos, nulos e inscriptos. No deducir el padrón desde participación redondeada.
- Distinguir resultados parciales, acumulados, totales departamentales y provinciales. Buscar primero si existe un total final directo. Si hace falta restar acumulados, guardar ambos operandos, páginas y fórmula; etiquetar el resultado como derivado.
- Preservar nombres históricos y listas separadas. La normalización territorial o partidaria debe tener correspondencias explícitas, sin decidir identidades por semejanza de totales.
- No corregir discrepancias del impreso para que cierre. Guardar lectura original, alternativas y motivo de cualquier corrección de transcripción. Las reservas cronológicas y las impugnaciones forman parte del registro.

## Repartir y revisar

Cuando el usuario pida subagentes, repartir bloques de páginas sin solapamiento de archivos y acordar columnas antes de consolidar. Seguir el modelo/esfuerzo solicitado; no convertir una elección de un pedido en requisito permanente. Cada bloque debe terminar con inventario de páginas, cobertura y dudas precisas. Continuar los bloques incompletos hasta agotar su lectura recuperable.

El principal revisa en la imagen las cifras raras, cierres fallidos, celdas dudosas, cambios de encabezado y fronteras entre bloques. Registrar exactamente qué páginas/celdas cotejó: una revisión focal no es una segunda transcripción completa.

## Controles y entrega

Generar controles reproducibles sobre la base transcrita: duplicados de unidad/página/candidato, cobertura prevista frente a observada, subtotales disponibles y suma de cada candidato frente a su total. Mantener faltantes fuera de sumas completas; no usar `sum()` que oculte nulos sin informar cobertura. Los cierres aritméticos son controles, no prueba de lectura visual ni de limpieza de la elección.

Entregar archivos de datos, un `LEEME.md` con cobertura y reservas, controles y registro de revisión del principal. Separar lectura visual, resultados derivados y comparaciones externas. No llamar completo a un bloque con páginas pendientes ni llamar verificado a todo lo que solo recibió revisión focal. Mantener renders y PDFs pesados fuera de git según las reglas del proyecto; conservar el código necesario para regenerar controles.

Para un ejemplo real de actas con votos nominales y acumulados, consultar `transcripciones/1936/LEEME.md` y sus subcarpetas. No tomar los resultados de ese año como plantilla universal.
