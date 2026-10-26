# Atlas 1989, presidente

`python build_1989.py` → `atlas_1989.html` + `dataset_1989.json`. Mismo método que 1983 y 1987: departamentos del censo de 1980, 28 circunscripciones de Capital, los siete recuadros de Wikipedia 1999 (`../insets99.py`), topline de `../wikitop.py`. Los diputados nacionales de 1989 (`../base8399/ernesto/1989_diputados/`) quedan sin hacer.

## Datos
- **Departamentos y provincias**: base de Ernesto Calvo, `../base8399/ernesto/1989_presidente/dpto_partidos.csv` (528 unidades, 24 distritos).
- **Resultado nacional**: tabla de «Elecciones presidenciales de Argentina de 1989» (Wikipedia, `w1989.txt`). Positivos 16.749.128; blancos 222.048; anulados 116.049; diferencia de actas 4.395; votantes 17.091.620; registrados 20.034.252.
- **Fórmulas** (código de la base → fórmula de la tabla de Wikipedia; total de la base contra el de Wikipedia):
  - Menem-Duhalde = `frejupo` + `fcr` (Corriente Renovadora) + `ptp` + `mid` (7.957.796; 7.957.518)
  - Angeloz = `ucr` + `ucrfi` + `ucrmc` + `cfi` + `cfifed` + `fed`, es decir UCR + CFI (6.215.258; 6.213.217)
  - Alsogaray-Natale = `adc` + `paldpml` + `ucd` + `pdp` + `adcucd` (1.199.634; 1.200.172)
  - Estévez Boero-Bravo = `aus` + `us` + `psp` + `ps` + `psd` (241.290; 240.132)
  - MPN, exacto (35.466).
- Control por provincia con la tabla por distrito de Wikipedia (`wiki_dist.json`: Menem, Angeloz, Alsogaray, otros; ya con las 3 imputaciones): 14 de los 24 distritos coinciden con las tres fórmulas a menos de 4 votos. Los mayores desvíos de la base respecto de Wikipedia: Río Negro (+1.154 Menem, +1.377 Angeloz, +786 Alsogaray), San Luis (+1.505 Angeloz), Corrientes (−1.262, −797 y −1.663) y Jujuy (+505 Menem); en Buenos Aires, La Pampa, La Rioja, Santa Cruz, Santiago del Estero y Tierra del Fuego los desvíos son de menos de 200 votos.

## Decisiones
- Leyenda solo con las fuerzas que ganan alguna unidad (Menem 404, Angeloz 101, Alsogaray 15, MPN 7, Estévez Boero 1). Colores distintos entre sí, logos de época (escudo de la UCR, bandera cuadrada del PJ, logo de la UCeDe para la Alianza de Centro) y sigla para el resto (reglas en `../AGENTS.md`).
- **Modos**: Ganó, Menem, Angeloz y Alsogaray. No hay modo de participación: la base no trae el padrón de Santa Fe ni de Tucumán.
- Las barras llevan el nombre del candidato y la torta usa los totales por fórmula de la tabla de Wikipedia.

## Correcciones a la base de Ernesto (3 cifras)
En tres unidades falta la columna de la UCR y el total de positivos de la unidad sí es correcto, así que se imputó el residuo: Rosario de la Frontera (Salta, +4.528), Saladas (Corrientes, +1.591) y 25 de Mayo (San Juan, +1.388). En Salta y San Juan con eso el total provincial de Angeloz coincide con Wikipedia; en Corrientes queda 797 votos corto (el resto no se pudo ubicar). Cada unidad corregida lleva nota en su ficha.
- Esas diferencias no se pudieron atribuir a una unidad y no se corrigieron; tampoco el residuo de 266 votos de «otros» en la circunscripción 18 de Capital.

## Casos que mirar
- **Antofagasta de la Sierra (Catamarca)**: aparece ganada por Unidad Socialista (166 votos de 435 positivos, contra 159 de la UCR-MPC y 105 del FREJUPO). Es lo que trae la base y es coherente con el total provincial de Wikipedia, pero es un resultado raro para el socialismo y es la única unidad que justifica la fila de Estévez Boero en la leyenda; no se pudo contrastar con otra fuente.

## Casos particulares
- Palpalá, Islas del Ibicuy y Tres Lomas se suman a Capital (Jujuy), Gualeguaychú y Pellegrini, como en 1987.
- La Rioja: Chamical = Gobernador Gordillo del mapa de 1980; Coronel Felipe Varela = General Lavalle; Peñaloza, Vera Peñaloza y Quiroga por alias.
- Islas Malvinas: sin dato propio, hereda a Tierra del Fuego.

## Estilo del mapa de 1995 (probado acá)
Recuadro «Área Metropolitana de Buenos Aires», Antártida en marco con arco de 60 S y la tierra coloreada (Natural Earth 1:50m), Malvinas en gris con contorno negro (sin dato, nota en la unidad). Sin globo «Exterior» (1989 no tuvo voto en el exterior). Pendiente: logos de campaña como los de la referencia.
