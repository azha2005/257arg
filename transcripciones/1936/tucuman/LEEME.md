# Tucumán 1936: acta y planillas nominales

Fuente local: `../expedientes_hcdn/26-ov-1936.pdf`, 104 páginas. Las referencias son páginas PDF desde 1. La primera lectura se repartió entre dos subagentes Terra con esfuerzo medio; otro realizó una lectura independiente del resumen y un índice de bloques. El principal revisó el acta territorial y cifras focales; detalle en `../REVISION.md`.

## Qué se puede usar

- `acta_departamentos.csv`: once colegios electorales, rangos de circuitos y totales de sobres **según acta** y **en urna**. `circuitos_departamentos.csv` registra los circuitos y bis. Los totales cierran con p67; son sobres, no votos positivos por lista.
- `celdas.csv`: consolidación de las lecturas del **frente identificado** de las planillas pp72–101. Conserva candidato/categoría, mesa literal, página y fila de lectura. `valor_numerico` solo se rellena cuando el literal son dígitos: eso no significa revisión independiente de la celda. El guion se conserva y no se convierte en cero; `?` significa no resuelto. El archivo incluye subtotales impresos y mesas: **no sumar todos sus renglones**.
- `parte_a/` y `parte_b/`: lecturas originales, inventarios de páginas y reservas. Las pistas de cara u orientación inciertas se conservan aparte y no entran en la consolidación. Los inventarios dan mínimos o tramos cuando el escaneo impide contar filas con seguridad.
- `resumen_independiente/resumen_p102.csv`: resumen con primeras ocho filas legibles, novena parcial y pistas inferiores. Sus rótulos territoriales quedaron fuera del escaneo. Las pistas inferiores no son valores confirmados y pueden confundirse con doble imagen. No entran en `celdas.csv`.
- `bloques_planillas.csv`: índice de localización visual, no una correspondencia territorial completa. Se ancla p72 a Capital circuito 1 y comienzo de p73 a 1 bis por el texto de continuación. Las demás filas sin circuito no se atribuyeron por semejanza de votos ni por orden supuesto.

## Límites de la lectura

La consolidación final registra **310 renglones de lectura y 4.340 celdas**: 3.313 números leídos, 463 guiones literales y 564 celdas sin resolver. Son registros de mesas, suplementarias y subtotales, no un conteo de todas las mesas del distrito. Las pistas de cara incierta quedan excluidas. El resumen p102 y el acta de sobres son archivos separados.

Esta es una transcripción **parcial** de las planillas: hay márgenes recortados, superposición de frente/reverso y celdas que no pueden aislarse. Se examinó el material con ampliación, JPEG internos y contraste local por canales, sin síntesis de imagen. No se certifica cobertura exhaustiva de las zonas superpuestas ni se rellenan huecos por totales. Las cifras tenues firmes para el primer lector siguen sujetas a revisión.

Se mantienen los doce candidatos en sus cuatro listas. Sus votos nominales no son electores únicos y no deben sumarse para calcular positivos. Blancos, nulos y sobres son categorías distintas. Números de mesa y «Sup.» se repiten entre circuitos: la identidad técnica de una fila de lectura no establece identidad territorial.

P96 imprime 4 para Martínez en una mesa aunque la suma de su columna difiere en 26 del subtotal; se conserva 4 con reserva. P72 tiene un 2 desplazado junto a 26 de Martínez. P73 tiene una marca en nulos de mesa 7. Ver el cotejo focal en `../REVISION.md`.

P103 proclama a Prat Gay (32.903), López García (31.432), Martínez (30.964) y Padrós (30.431), cifras del distrito cotejadas por el principal. No sirven para imputar las celdas faltantes.

## Regeneración

Desde cualquier directorio:

```powershell
python C:/Users/JC/Downloads/dataeleccproyecto/transcripciones/1936/revision/registrar_acta_tucuman.py
python C:/Users/JC/Downloads/dataeleccproyecto/transcripciones/1936/tucuman/consolidar.py
python C:/Users/JC/Downloads/dataeleccproyecto/transcripciones/1936/verificar.py
```

`CONTROL_CELDAS.json` cuenta lo registrado y conserva hashes de las dos entradas; no es certificación de cobertura del impreso. `../CONTROL.json` conserva hashes de fuentes y controles de Santa Fe y del acta de Tucumán. No se construyeron ni modificaron atlas.
