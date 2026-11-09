# Atlas presidencial de 1868

`python mapas/mapa1868/build_1868.py` (después de construir `mapas/mapa1874/`, del que toma el visor, la geometría del censo de 1869 y los recuadros).

## Qué muestra

No hay voto popular por departamento ni total nacional. Cada provincia va en color sólido según quién ganó sus electores. Fuente: la tabla «Resultados por Provincia» del artículo de la Wikipedia, que cita el escrutinio de la Asamblea del 16 de agosto de 1868 (Diario de Sesiones del Senado de 1868, pp. 360–365).

- Sarmiento, 79 electores: Buenos Aires (24, más 3 para Rawson y 1 para Vélez Sarsfield), Córdoba, Jujuy, La Rioja, Mendoza, San Juan y San Luis.
- Urquiza, 26: Entre Ríos, Salta y Santa Fe.
- Elizalde, 22: Catamarca y Santiago del Estero.
- Corrientes no votó (gris). En Tucumán no se conservan las actas (beige).

La torta y las barras son electores, no votos. Rawson y Vélez Sarsfield van en gris.

Colores de la Wikipedia: Urquiza #B31B1B y Elizalde #35AAE0. Sarmiento va en gris pizarra #3d4652 en lugar del negro, para que se lean los bordes. Logos con sigla.

## Voto popular de Buenos Aires

- **Ciudad**, como un solo total, sin parroquias: *Nación Argentina*, 17 de abril de 1868, p. 2, «Eleccion de electores». Cabezas de lista: Club Popular 1.186 votos por elector, Club Libertad 862, con algunas cifras intermedias. No se escrutaron Catedral al Norte y Barracas al Norte. Las 14 parroquias se pintan con ese total.
- **Campaña** por partido: *Nación Argentina*, 21 de abril de 1868, p. 2, «Elecciones en la Campaña» (`fuentes/hemeroteca/pruebas_presidenciales/18680421.pdf`), transcripto en `campana_21abril1868.csv` con el texto literal de cada fila. Cotejado sobre el escaneo.
  - Hay 45 filas. Seis dicen «no hubo» elección: Matanza, Quilmes, San Nicolás, Ramallo, Baradero y Lobos. Mercedes y Zárate dan las dos listas. El resto da solo la lista ganadora: tono claro, sin porcentaje.
  - «La misma» se resolvió con la fila anterior. Así, San José de Flores queda para el Club Libertad, porque sigue a Las Heras.
  - Las filas suman **5.081 para el Club Popular y 894 para el Club Libertad**; el diario imprime 4.273 y 739. Se conservan las dos cifras, sin ajustar.
  - Los partidos que no figuran en el cuadro quedan en beige.
- El Club Popular (autonomistas de Alsina, cuyos electores votaron a Sarmiento) va con el color de Sarmiento. El Club Libertad (mitristas) va con el de Elizalde.
- La torta y las barras suman la ciudad y los totales impresos de campaña: **Sarmiento 5.459 (77,3 %), Elizalde 1.601 (22,7 %)**. Urquiza aparece con 0 % porque gana provincias por electores.

## Pendiente

Resultados por departamento en las otras provincias. Para 1868 conviene empezar por el Diario de Sesiones del Senado de 1868 (pp. 360–365), *La Tribuna* y *El Nacional* de abril de 1868 y los cuadros tucumanos que publicó Amenta.

## Agregados del 8-nov-2026
- 9 de Julio, Lobería y Ajó (General Lavalle): «no tuvo lugar la elección por falta de sufragantes» (*Nación Argentina*, 24 de abril de 1868, p. 2). Gris oscuro, no hubo elección.
- Tucumán: tono claro de Elizalde. Ganó la lista del club El Pueblo y la Legislatura proclamó a sus 10 electores; las actas del colegio llegaron tarde y la Wikipedia no las computa (Amenta; *Nación Argentina*, 30 de abril).
- San Luis: nota con el voto popular (Elizalde ganó por 163 votos, *Nación Argentina*, 30 de abril), sin cifras por lista; el color sigue siendo el de sus electores (Sarmiento).
- Pendiente: Mercedes, Club Libertad, 37 en el CSV contra 57 en un informe externo; el OCR del 21 de abril no se lee.
