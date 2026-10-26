# Atlas 1995, presidente (dos versiones)

`python build_1995.py` → `atlas_1995.html` (la elección tal cual: Menem, Bordón/FREPASO, Massaccesi/UCR). `python build_1995.py union` → `atlas_1995_ucr_frepaso.html` (hipotética: Bordón y Massaccesi sumados, 5 pestañas: Ganó, Menem, Suma, FREPASO, UCR). Se generó a partir de `build_1994.py` (departamentos del censo de 1991, recuadros de 1995, mismos parches de plantilla); topline en `../wikitop.py` (`1995` y `"1995u"`).

## Datos
- Base de Ernesto Calvo `../base8399/ernesto/1995_presidente/dpto_partidos.csv`; nacional de la tabla de «Elecciones presidenciales de Argentina de 1995» (`w1995.txt`): positivos 17.395.284, blancos 653.443, anulados 125.112, dif. de actas 30.085, votantes 18.203.924, inscriptos 22.178.201.
- Fórmulas (código de la base → candidatura), contrastadas con la tabla por distrito de Wikipedia (`wiki_prov.json`): Menem = pj, afju, afjen, frejupo, ucd, afjupo, fjuvi, afreet, afcbio, fjub, prs, acha, blo, mpj, mapjuj, mpchu, afjuso + fed (Capital); Bordón = afpaso, fpaso, acfg, fg, afpais, mizq + fr de Tucumán; Massaccesi = ucr, aucrpu, ucrp, aucrmid, mid, ucrfci, ucrfsol + fed de Córdoba. 20 de 24 provincias coinciden exacto o a menos de 700 votos. Totales de la base: Menem 8.685.779 (Wikipedia 8.687.511), Bordón 5.095.318 (5.096.104), Massaccesi 2.955.794 (2.956.137).
- «fr» (Fuerza Republicana) en Tucumán son 167.796 votos que coinciden exacto con Bordón en Tucumán de Wikipedia: la columna está mal rotulada en la base; se cuenta como FREPASO. El «fr» de Jujuy (15.602) es de Rico y va a otros. Rico (MODIN) no gana ninguna unidad.

## Correcciones
- **Deseado (Santa Cruz)**: la base trae 221 positivos con 34.173 electores. Se imputaron 26.265 votos (PJ 16.790, FREPASO 4.562, UCR 4.913) para que Menem, Bordón y Massaccesi de Santa Cruz coincidan con la tabla provincial. Nota en la unidad. Las demás fuerzas quedan como en la base.
- **Chaco**: la tabla provincial de Wikipedia tiene un error (Menem 207.857 y Massaccesi 101.763; la suma de las provincias no da el total nacional). La base da 227.857 y 91.763, que con las otras provincias suman exactamente el total de Wikipedia (8.687.511 y 2.956.137), y los porcentajes de Bordón coinciden: se mantuvo la base.
- Partidos del GBA creados en 1994-95 que el mapa de 1991 aún no tiene: Ezeiza → Esteban Echeverría, Hurlingham e Ituzaingó → Morón, Presidente Perón → San Vicente, Punta Indio → Magdalena, San Miguel + José C. Paz + Malvinas Argentinas → General Sarmiento; 2 de Abril → 12 de Octubre (Chaco). Cada ficha lo dice.

## Decisiones
- Colores: Menem #318ce7 (PJ), Bordón #a349a4 (el de Wikipedia para el Frente País Solidario), Massaccesi #e10019 (UCR). La suma lleva verde #2e9e6b (no se pisa con ninguna de las otras familias).
- Logos: PJ (bandera cuadrada) y UCR (escudo de 1931). **FREPASO: `Logo_FREPASO_remake.png`, una recreación de Commons de 2025 (CC0) que usa el infobox de Wikipedia; el diseño de época no está verificado** (la boleta de 1995 muestra otro recuadro, «Frente País Solidario», con una figura). La suma usa un compuesto UCR + FREPASO (`Logo_UCR_mas_FREPASO.svg`).
- La versión sumada es hipotética: no dice qué habría pasado, solo suma dos candidaturas. Gana la suma en 174 unidades (de 530) y 6 provincias; en votos Menem seguiría arriba (8.687.511 contra 8.052.241). En la versión real Menem gana 491 unidades y 23 provincias, Bordón 24 (19 circunscripciones de Capital, 4 departamentos de Corrientes, 1 de Santa Fe; la Capital es su única provincia), Massaccesi 14 (5 de Río Negro, 5 de Misiones, 2 de Chubut, 1 de Buenos Aires, 1 de Córdoba).
- Sin modo de participación (la leyenda usa el de Wikipedia).

## Archivos
`png_blanco/mapa1995/`, `png_transparentes/mapa1995/` y la carpeta `all elections white bg/`.

- **Geometría (15-oct-2026):** Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas y 2 de Abril tienen polígono propio (de `Departamentos_2001`, recortado al contorno de 1991) en lugar de sumarse al partido de origen (`../newpartidos.py`). Las cifras por bloque no cambian.

- **Padrón inconsistente (19-oct-2026):** la base presidencial trae a Diamante (Entre Ríos) con 14.920 inscriptos y 25.099 votantes. Su ficha ya no muestra participación (antes 168 %) y lleva la nota «padrón inconsistente»; la participación provincial de Entre Ríos se calcula sin Diamante. Baradero, inconsistente en la base de diputados, está bien en la presidencial, y la presidencial no tiene filas de métricas repetidas. El atlas de 1995 no tiene modo de participación, así que el mapa no cambia; PNG regenerados (no hay paquete de Commons de 1995).
