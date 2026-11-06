# Atlas de diputados nacionales 1936

`python mapas/mapa1936/build_1936.py` → `atlas_1936.html`, `dataset_1936.json`, `CONTROL_ATLAS.json`. Usa el constructor de la familia 1922/1928/1930 que ya hace 1926, 1937 y 1940 (`transcripciones/entreguerras/construir.py`): proyección, departamentos de 1914 y recuadros iguales.

## Fuentes

- **Tucumán y Santa Fe por departamento**: actas de las Juntas Escrutadoras en los expedientes de la Cámara de Diputados 26-OV-1936 y 29-OV-1936. Transcripción, controles y reservas en `transcripciones/1936/` (`tucuman/departamentos.csv`, `santa_fe/candidatos.csv`). Cantón no publica 1936 por departamento.
- **Las otras nueve provincias que votaron** (Buenos Aires, Capital, Córdoba, Corrientes, Entre Ríos, Jujuy, Mendoza, San Luis, Santiago del Estero): total provincial de la tabla de la Wikipedia, provincia pintada entera (`DATA.solid`), como 1912/1914.
- Catamarca, La Rioja, Salta y San Juan no renovaron diputados: gris.
- Resultado nacional: tabla del artículo de la Wikipedia (`wiki_nacional_1936.json`).

## Decisiones

- **Votos de una lista = su candidato más votado en la provincia**, como la tabla de la Wikipedia: Tucumán Padrós, Prat Gay, Aragón y E. López; Santa Fe Busaniche, Leiva y Molinas. Esos candidatos están leídos en todos los departamentos. La suma de las listas de Tucumán supera los sobres porque se votaba por candidato (con tachas), por eso la ficha no muestra votantes por departamento.
- **Concordancia** = el «Total Concordancia» del artículo (PDN, UCR de Santa Fe, Concordancia, UCR Unificada, Partido Liberal de Corrientes, PSI, Partido Popular de Jujuy, UCR Provincia de Buenos Aires), como el atlas de 1940. En Santa Fe es la UCR de Santa Fe; en Tucumán, la lista Concordancia.
- UCR Concurrencista (Tucumán, lista Laprida 147) en magenta, como el Frente Popular de Tucumán en 1940, para no confundirse con los tonos claros de la UCR.
- PS no gana ninguna unidad: va en «otros» en la torta y sigue en las fichas.
- **Trancas (Tucumán), extrapolado a pedido del usuario**: nulos 1 y blancos 29, residuo de los 4.383 blancos y anulados de la Wikipedia menos lo leído en los otros diez departamentos, repartido como en Burruyacú y Tafí. Los otros candidatos de Trancas, fuera del mapa, quedan estimados en `departamentos.csv` (columna `votos_con_extrapolacion`). Las listas de Trancas son lecturas, no estimaciones.
- Burruyacú: nulos y blancos bajo la banda del escaneo, sin cifra en la ficha.

## Controles

- 30 departamentos con datos, todos con polígono. Ganadores: UCR 9, UCR Concurrencista 9, PDP 7, Concordancia 5.
- Tucumán: los once departamentos suman la proclamación de los cuatro electos y los 2.506 del PS. Santa Fe: los candidatos suman el total provincial del acta.
- Aragón suma 26.712 contra 26.755 de la Wikipedia; se conserva la lectura.

Sin paquete de Commons, sin catálogo del sitio, sin publicar.
