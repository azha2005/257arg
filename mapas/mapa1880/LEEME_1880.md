# Presidencial de 1880

Atlas local del voto popular para elegir electores el 11 de abril. Usa la geometría de 1869 y el visor de 1874, con sus recuadros porteños. Regenerar desde la raíz con python mapas/mapa1880/build_1880.py (requiere xlrd).

- Ciudad. Planilla 9 de Cantón y Jorrat, basada en La Prensa del 13 de abril de 1880, portada. La torta y las barras se limitan a estas 14 parroquias. El CD suma 5.907 a 603. El impreso da 5.907 a 598. Se mantiene la diferencia.
- Campaña. Transcripción visual de las 53 filas de la misma portada. Se ubican 52. Brandsen se conserva en el CSV y queda pendiente de geometría. Los guiones quedan literales. Los totales discordantes de las filas se muestran en las fichas. En Luján la lectura del total queda abierta.
- Interior. Los triunfos por provincia son partes provisorios, sin votos. En Mendoza se colorea el departamento Capital para representar la ciudad mencionada. La campaña mendocina figura como resultado agregado en la ficha provincial. Totoral no tiene ganador propio publicado.
- Los porcentajes locales usan las dos cifras de cada fila cuando ambas están publicadas. El sombreado para ganadores sin dos cifras refleja el relato de la portada. La asociación entre las listas del cuadro y las candidaturas sigue la terminología del diario.

## La Rioja. Escrutinio del 12 de mayo

El Bien Público (Montevideo, 15 de mayo de 1880) reproduce un despacho de La Rioja fechado el 12. La Junta Nacional Escrutadora presidida por el juez Molina proclamó a la lista tejedorista al escrutar la elección popular del 11 de abril. El parte no da cifras. https://anaforas.fic.edu.uy/jspui/bitstream/123456789/98026/1/EBP_00450_18800515.pdf

La Hemeroteca Digital Brasileña indexa una segunda publicación del parte, traducida al portugués. Coinciden el juez, la fecha, la lista proclamada y la entrega de diplomas. La redacción indica que probablemente reproduce el mismo despacho. El servidor devolvió 403 al intentar bajar el PDF, por lo que la comparación se hizo con el texto indexado. https://hemeroteca-pdf.bn.gov.br/713120/per713120_1880_00200.pdf

Pendiente cotejar el acta y cualquier cómputo nominal. Mantener separado del voto de los electores en junio.

## Cierre impreso de campaña

La Prensa, 13 de abril de 1880, p. 1, imprime literalmente 10932 para el Partido Liberal, 905 para los irigoyenistas y 19937 como total general. Los subtotales impresos suman 11837. La suma mecánica de las cifras presentes en las 53 filas da 19029 y 905 (19934 en conjunto). Un subtotal liberal de 19032 sería compatible con el total general, pero es una hipótesis de errata y difiere en tres votos de las filas. El diario advierte que faltan partidos. El recorte cotejado es fuentes/hemeroteca/pruebas_presidenciales/18800413_cierre_campana.png.

## Cómputo porteño con un voto para Sarmiento

La renovación presidencial de 1880, p. impresa 80 (PDF 84), registra 5907 conciliados, 598 irigoyenistas y 1 voto para Sarmiento. La nota 30 cita La Prensa del 13 de abril de 1880. El voto suelto suma 6506 en esta lectura, sin parroquia identificada. No se mezcla con la planilla del CD ni se asigna a una parroquia. https://sedici.unlp.edu.ar/handle/10915/3124

## Cotejo de las filas porteñas

En la portada de La Prensa del 13 de abril, la columna irigoyenista da 1 en San Miguel y 42 en Piedad. La planilla 9 del CD da 2 y 47, respectivamente. San Juan Evangelista y Santa Lucía llevan guion en el impreso y cero en el CD. Las cifras irigoyenistas visibles suman 597 frente al subtotal impreso de 598 y los 603 del CD. Las dos diferencias numéricas de fila suman seis. El voto para Sarmiento referido por la tesis se conserva como dato distinto. Véase fuentes/hemeroteca/pruebas_presidenciales/18800413_ciudad_detalle.png.

## Incorporaciones del 8-nov-2026

- **Tucumán**: 2.184 votos para los electores roquistas, sin lista opositora (Navajas, tesis, p. 178, nota 385, que cita AHT, AL, caja 33, leg. 2242; cotejado en `fuentes/hemeroteca/pruebas_presidenciales/navajas_tucuman.txt`). Color sólido roquista con la cifra en la ficha.
- **Almirante Brown**: *La Prensa*, 14 de abril, p. 1, «Un detalle curioso» (cotejado sobre el escaneo): según un escrutador, sufragaron 41 ciudadanos. **El diario no dice por qué lista votaron**, así que no se asigna ganador. El partido no tiene polígono en la base de 1869 y va en la nota de Buenos Aires.
- **Quilmes** (59–4, *El Quilmero*, 15 de abril) coincide con el CSV. **Las Heras**: *El Porteño* del 12 de abril imprime 00/00 en su primer cuadro telegráfico; se conserva el 119–12 de *La Prensa* con nota. *El Porteño* atribuye 900 votantes irigoyenistas a la ciudad, contra 598 en *La Prensa* y 603 en el CD.
- **Salta, Santiago del Estero, Córdoba y Corrientes**: notas en la ficha provincial (acta de *La Reforma* del 22 de mayo sin cifras; telegramas de *El Porteño* del 14 de abril). Los colores no cambian. Los partes de Corrientes («ni un voto en contra», 110 votantes) contradicen el color tejedorista. Queda anotado para revisar.
- **Asamblea del 9 de octubre** (*La Prensa*, 10 de octubre): no trató la elección primaria y escrutó solo los colegios (155 Roca, 70 Tejedor).

Los escaneos de *El Porteño*, *El Quilmero* y *La Reforma* no están en el repositorio. Esas lecturas vienen del reporte aportado y no se cotejaron aquí.

**8-nov-2026, segunda pasada**: las provincias llevan el color de quien ganó sus electores según la Wikipedia (Roca 155, Tejedor 70; Tejedor solo en Buenos Aires y Corrientes). La Rioja pasa a Roca (7 electores); el despacho tejedorista del 12 de mayo queda en la ficha. El candidato `PAN` del visor pasa a ser Roca, con los irigoyenistas de Buenos Aires. La torta suma la ciudad, las filas de campaña con cifra y Tucumán.
