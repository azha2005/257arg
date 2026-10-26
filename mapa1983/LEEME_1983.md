# Atlas de las elecciones presidenciales del 30 de octubre de 1983

Archivos: `atlas_1983.html` (autónomo; pestañas GANÓ, UCR, PJ y PART) y `dataset_1983.json`. Se regenera con `python build_1983.py`.
Misma maqueta, agrupación, colores y emblemas que los atlas de 1916 a 1930 (regla de `atlas-estilo-wikipedia`).

## Fuentes
- **Departamentos y provincias**: base de Ernesto Calvo, hojas por provincia de `TPDENP1983T.xls`, a través de `../base8399/ernesto/1983_presidente/dpto_partidos.csv`. Porcentajes sobre votos positivos; blancos y anulados sobre emitidos.
- **Resultado nacional** (torta, barras y métricas): tabla de «Elecciones presidenciales de Argentina de 1983» de la Wikipedia en español, cargada en `../wikitop.py`.
- **Geometría**: departamentos del censo de 1980 (`Base deptos 1869-2022/Departamentos_1980.shp`, nombres de la base corregidos en `geom.py`) y, para Capital Federal, las **28 circunscripciones** del SVG de Wikipedia 1999 (`caba28.py`, numeración oficial en `CIRCUNSCRIPCIONES_CABA_28.md`).
- Leyenda solo con los partidos que ganan alguna unidad (UCR 298, PJ 196, PAL 16, MPN 11, BLO 3, MFP 2); PI, MID, Alianza Federal y el resto van en «otros». Colores distintos entre sí (los de Wikipedia para PJ, MPN y MFP eran varios azules parecidos: MPN azul marino, MFP ámbar).
- Emblemas de época: UCR (escudo de 1931) y PJ (bandera cuadrada, diseño de 1946). PAL, Bloquista, MPN y MOFEPA llevan sigla, porque sus archivos de Commons son de 2018 a 2025; licencias en `../logos_wikipedia/LICENCIAS.md`.
- Los siete recuadros de Wikipedia 1999 (Tucumán, Gran San Juan, Gran Mendoza, Resistencia + Corrientes capital, Gran Buenos Aires, Antártida y Capital Federal), generados por `../insets99.py`. La Antártida se dibuja con el «Sector Antártico» del shapefile de 1980 en proyección polar austral, más Georgias y Sandwich del Sur en gris, y toma el color de Tierra del Fuego.

## Comprobaciones
- Las 525 unidades de la base se emparejaron con un polígono cada una (`ALIAS` de nombres en `build_1983.py`). Queda un polígono sin dato propio: Islas Malvinas, que muestra el resultado de Tierra del Fuego.
- Los totales nacionales de UCR, PJ, PI, MID, Pacto Autonomista-Liberal, Bloquista, MPN y Movimiento Federalista Pampeano coinciden voto a voto con la tabla de Wikipedia. La Alianza Federal suma 106.773 por la base y 107.188 en la tabla (415 votos de diferencia): su bloque es Alianza Federal, Partido Federal, Demócratas de Mendoza, Córdoba y Entre Ríos y Movimiento Línea Popular (siglas `af`, `pf`, `fed`, `pd`, `demer`, `mlp`).
- UCR, PJ, PI y MID coinciden con la tabla «Resultados por distrito» de Wikipedia en las 24 provincias. La fila «Otros» de Buenos Aires de esa tabla (356.099) es incoherente con su porcentaje (2,28 %, o sea 127.607); Tucumán difiere en 1 voto. Los blancos (334.946) y anulados (87.728) coinciden; los positivos difieren en 1 voto (14.927.513 contra 14.927.512).
- Padrón (`electores`): 17.901.325 en la base contra 17.929.951 registrados en Wikipedia (28.626 menos). La participación por departamento usa el de la base.

## Límites
- **Circunscripciones de Capital**: la forma sale del dibujo de Wikipedia, ajustado por cajas envolventes al contorno de Capital del shapefile de 1980. Es aproximada y algo más ancha que la real.
- **Bloques de la leyenda**: UCR, PJ, PI, MID y Alianza Federal (las cinco candidaturas del artículo), más los cuatro partidos provinciales que ganan al menos un departamento (Pacto Autonomista-Liberal en Corrientes, Bloquista en San Juan, MPN en Neuquén, Movimiento Federalista Pampeano en La Pampa). El resto (UCD, DC, MAS, etc.) figura en las tarjetas.
- Los límites de 1980 no son los de 1983 (por ejemplo, los partidos de Buenos Aires creados después, como Hurlingham o Ituzaingó, aún no existen en el mapa).
- La Antártida no se dibuja; el polígono de Malvinas es el de la base de 1980 recortado.

## Padrones inconsistentes (19-oct-2026)
La base presidencial de Ernesto Calvo trae menos inscriptos que votantes en seis departamentos: Avellaneda (1.156 inscriptos, 10.049 votantes), Pichi Mahuida (3.059 / 5.380), Pilcaniyeu (1.025 / 1.800), San Antonio (5.269 / 9.191) y Valcheta (1.469 / 2.871) en Río Negro, y Guasayán (1.158 / 3.632) en Santiago del Estero. Su ficha no muestra participación y lleva la nota «padrón inconsistente»; en el modo «PART» se pintan en gris claro (#cfcfcf) con la clave «Padrón inconsistente en la base», y la participación provincial de Río Negro y Santiago del Estero se calcula solo con los departamentos de padrón consistente (Río Negro: 86,0 %). Es el mismo arreglo que `atlas_leg8399.py` aplica a los atlas de diputados. La base presidencial no tiene filas de métricas repetidas (el «total» duplicado de Río Negro es de la base de diputados). PNG y paquete `commons/1983/` regenerados.
