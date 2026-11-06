# Tucumán 1936, lectura parcial de planillas

Fuente: expediente HCDN 26-OV-1936, páginas PDF 72–87, render a 130 dpi. Lectura visual directa de las filas cargadas; no se usó OCR para los valores. `lectura_parcial.csv` tiene una fila por candidato o categoría, con texto literal; `-` es guion de la fuente y `?` una celda que no se pudo leer, no cero. TOTAL es transcripción de la línea impresa, no suma calculada. Sin atribución de circuito por corte del margen, pendiente del cotejo con acta.

**Cobertura incompleta:** se cargaron filas visibles y algunas filas tenues de las pp. 72–87; faltan celdas y posiblemente filas, especialmente en las franjas degradadas. Las bandas de color no implican automáticamente ilegibilidad: requieren examen ampliado y de canales. El borde derecho de p. 72 corta las celdas de blancos individuales; el total 107 sí aparece. En p. 73 mesa 7, nulos lleva marca sobre el guion. En p. 72 mesa 6, Martínez tiene un 2 desplazado junto a 26. En p. 75 se ha puesto 11? para una mesa de número parcialmente cortado. Algunas páginas contienen textos traslucidos del reverso: distinguirlos de la planilla del frente. P. 87 también carece de margen identificador, por lo que no establece por sí sola el circuito que continúa en p. 88.

Estos datos son una primera lectura, no revisada independientemente. No están listos para agregación territorial ni para afirmar cierre o cobertura completa. No se modificaron atlas ni se publicaron resultados.

## Actualización de lectura
Se incorporaron filas de todas las páginas 72–87, incluidas filas tenues leídas mediante contraste localizado del canal rojo. En su estado actual el CSV suma 2.310 celdas de 165 filas, entre ellas 257 con `?`; no es cobertura completa: quedan partes tenues y la identidad de circuitos, además de la revisión independiente. Las filas se ordenaron de arriba hacia abajo; véase la nota de orden, que no cubre filas omitidas. Son frecuentes varias filas «Sup.» y «TOTAL» en una misma página, correspondientes a circuitos distintos todavía no identificados; no agruparlas. Por su falta de identificación y lectura parcial, este archivo no debe sumarse ni usarse para construir un mapa.

## Orden y secuencia
`fila_orden_pdf` numera las filas **cargadas** de arriba hacia abajo por página. La numeración no identifica filas omitidas; no es número de mesa ni establece secuencia entre páginas. Las filas tenues añadidas se ubican tras las claras porque corresponden a la zona inmediatamente inferior del frente. Circuito 1 de p. 72 se atribuye por secuencia, no por lectura del margen: el pie anuncia que se continúa con circuito 1 Bis en Capital; verificar con el acta.

Ver INVENTARIO.md para el examen de cobertura por página: hay filas adicionales superpuestas sin identificar y no es una transcripción exhaustiva. Los identificadores de mesa con ? y algunos subtotales en las zonas de doble imagen requieren revisión.

Las 13 filas adicionales bajo superposición intensa se trasladaron a `pistas_cara_incierta.csv`: orientación y pertenencia al frente requieren comprobación; no se deben consolidar con la lectura principal. Ver INVENTARIO.md.
