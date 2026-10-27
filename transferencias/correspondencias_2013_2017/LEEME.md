# Correspondencias históricas de circuitos

Revisión del 26-oct-2026. Se usan los identificadores realmente presentes en los CSV del provisorio DINE. `catalogo_2013.csv` y `catalogo_2017.csv` preservan las claves originales, incluidos circuitos sin electores de mesas escrutadas. Los campos `circuito_nombre` vienen vacíos: no se inventaron nombres.

## Diputados 2013 → 2017

| Provincia | Correspondencia aplicada | Respaldo |
|---|---|---|
| Santa Fe | Sección 10 → 9; secciones 14 y 15 → 13. Se conserva cada código de circuito. | Res. CNE 66/2022, considerando 1, que cita la decisión del 9-12-2014, expte. S 130/2014. |
| Santa Fe | Venado Tuerto: 399 de 2013 se compara con la suma 399 + 399A + 399B + 399C de 2017. | Res. 543/2015. El circuito 399 conservó código pero perdió territorio. |
| Río Negro | Viedma: 1 frente a la suma 101–122; Bariloche: 41 frente a 4101–4131. | Res. 613/2015; Disp. 194/2015. Los números resultantes se cotejan con DINE. |
| Río Negro | General Roca: 63 frente a la suma 6301–6315. | Identificadores y electores en DINE 2017, corroborados por la nómina judicial contemporánea `16-Habiles_Mesas.pdf`; la Res. 92/2024 documenta la ascendencia de 63. |
| San Luis | Unión de 1001 + 1007 + 1008 + 1009 frente a 1001A–C + 1007 + 1008A–E + 1009. | Disp. 38/2015, con límites en su propio texto, y Res. 651/2016. Se incluyen 1007 y 1009 porque cambiaron de límites. |
| San Luis | 3001 frente a 3001A + 3001B. | Res. 376/2018, que registra la aprobación CNE del 30-3-2017. El filtro de cambio de padrón posteriormente excluye este grupo. |
| Tierra del Fuego | Se conserva cada circuito común de Río Grande y las bases antárticas; la sección Ushuaia se compara como una unidad en ambos años. | Disp. 8-E/2017 con anexo de límites y Res. 291-E/2017. **No se obtuvo una equivalencia interna entre los siete circuitos anteriores y los nuevos U001–U014.** |

Una subdivisión se resuelve **sumando** circuitos completos hasta obtener un territorio común. No se reparten votos por superficie, por padrón ni por semejanza de resultados. `correspondencias.csv` en la carpeta del par enumera cada transformación y sus fuentes. La conservación de cada categoría se comprueba antes y después de la suma.

Las normas posteriores a 2017 no se presentan como vigentes en 2017: sirven para documentar relaciones padre/hijos cuando los códigos nuevos ya están efectivamente en la base. En General Roca, la Res. 92/2024 también menciona 6300 y 71B; **no se agregan** porque no existen en el extracto DINE 2017 utilizado. Para 5 → 5A/B y 93 → 93A/B de San Luis, la Res. 187/2022 es posterior y menciona aprobación CNE en 2019; quedan pendientes de una verificación contemporánea y no se aplican a 2013–2017. Tampoco se adivinan las equivalencias de pequeños circuitos rurales desaparecidos de Río Negro.

Resultado usado: **4.587 circuitos + 6 grupos**, sin agrupar provincias enteras por departamento. Los grupos admitidos son Viedma, Bariloche, General Roca, la unión de cuatro circuitos de San Luis, Venado Tuerto y Ushuaia. El filtro de padrón y las inconsistencias de electores se mantienen. La cobertura es **96,41 %** del padrón de origen; su descenso desde 96,77 % se debe a que ahora se filtran circuitos individuales que antes quedaban ocultos en totales departamentales.

## Presidenciales 2015 → 2023

- Santa Fe: `santa_fe_2022.csv`, extraído del anexo oficial de la Res. CNE 66/2022. Contiene 521 equivalencias con página de procedencia. Se usan las secciones y códigos completos, no la regla aproximada de multiplicar por diez. Los identificadores sin correspondencia quedan fuera del cruce.
- Río Negro: Cipolletti 65 se compara con la suma 6501–6524, documentada en la Res. 186/2022.
- Santa Cruz: Caleta Olivia 3 frente a 300 + 310 + 320 (Res. CNE 68/2022); Río Gallegos 18 frente a 1800 + 1810 + 1820 + 1830 + 1840 + 1850 (Res. 28/2024, con aprobación CNE del 12-7-2022).
- Neuquén conserva el respaldo por departamento: no se obtuvo una tabla completa, documentada y validada para sus recodificaciones y cambios de límites. La Disp. 154-E/2016 describe límites nuevos; **no basta para afirmar correspondencias uno a uno** con los códigos anteriores.
- Tierra del Fuego: Ushuaia + Río Grande de 2015 se comparan con Ushuaia + Río Grande + Tolhuin de 2023 como una sola unidad insular; Antártida queda separada. La ley provincial 1186/2017 cambió la división territorial. Se evita emparejar por nombre un Río Grande de extensión diferente, o dejar los votos de Tolhuin solamente en el origen. No es una equivalencia por circuito y el gráfico lo cuenta como grupo agregado.

## Diputados 2009 / 2013 → general / balotaje 2015

Se reutilizan las fusiones de secciones de Santa Fe, la unión de Venado Tuerto, Viedma, Bariloche, General Roca y los cuatro circuitos afectados de San Luis. No se aplica la subdivisión de Villa Mercedes aprobada en 2017 ni la recircuitación de Ushuaia de 2017 a estos pares anteriores: los circuitos de 2015 conservan en esos casos su clave original. Los votos de 2009 vienen de PolAr por mesa, con sus límites de cobertura ya documentados en el LEEME general; no se sustituyen por los complementos departamentales del atlas.

## PASO / general / balotaje 2015 → diputados 2025

Se conserva la tabla de **521 equivalencias calculadas de Santa Fe**, con los mismos códigos originales y páginas de la CNE. En los siete departamentos con códigos posteriores ausentes de esa tabla se usa la sección completa; los otros doce siguen por circuito. No se vuelve toda la provincia a departamento. [Decisiones específicas y archivos de fuente](../FUENTES_2015_2025.md). Neuquén mantiene su respaldo departamental, y se suman completas las secciones de Río Negro, San Luis y Santa Cruz con cambios internos pendientes de correspondencia. Los controles por par guardan todos los registros aplicados.

## Fuentes primarias

## Extensión a 2019

Se completaron 2017 diputados → 2019 presidente, 2017 diputados → 2019 diputados, 2015 general → 2019 general y 2015 balotaje → 2019 general. Cada par tiene su `RESUMEN.md` y está enlazado desde `../INDICE_NUEVOS_CRUCES.md`.

En Tierra del Fuego, Ushuaia 2017/2019 conserva sus circuitos normalizando el cero de relleno (U001/U1). El circuito 21 de Tolhuin pasa de la sección 2 de 2017 a la sección 5 de 2019: se conserva ese circuito completo y no se mezcla con Río Grande. En 2015→2019 se agrega Ushuaia por la recircuitación de 2017. No se agrega la isla completa en estos pares: el archivo de ámbitos de la DINE permite conservar Río Grande y Tolhuin. Para Venado Tuerto se suman 399 y 399A/B/C en 2015→2019. Neuquén mantiene el respaldo por departamento por falta de una equivalencia interna completa verificada.

Cobertura del padrón de origen: 97,95 % (2017→2019p), 97,95 % (2017→2019d), 96,40 % (2015p→2019p) y 96,94 % (2015b→2019p). Se verificaron los cuatro gráficos y sus 100 vistas nacionales/provinciales contra las matrices. Fuentes de las claves: archivos de ámbitos DINE 2017/2019 y [documentación judicial de la sección Tolhuin en 2019](https://old.pjn.gov.ar/cne/secelec/document/otros/24-PASO%202019%20-%20AUTORIDADES%20DE%20MESA%20DEFINITIVAS.pdf), además de las normas ya archivadas de Ushuaia y Venado Tuerto. No se copiaron los nombres personales de la nómina judicial.

### Archivo de fuentes

Se guardan HTML y texto de las normas, anexos PDF cuando están enlazados, URL, fecha de consulta y SHA-256 en `fuentes.json`. Las descargas fallidas se registran como tales. La nómina antigua de PJN fue consultada mediante el índice web; el acceso directo al servidor no respondió.

- [Santa Fe, CNE 66/2022 y anexo](https://www.argentina.gob.ar/normativa/nacional/norma-373111/texto)
- [Venado Tuerto, 543/2015](https://www.argentina.gob.ar/normativa/nacional/norma-246080/texto)
- [Viedma, 613/2015](https://www.argentina.gob.ar/normativa/nacional/norma-246380/texto)
- [Bariloche, Disp. 194/2015](https://www.argentina.gob.ar/normativa/nacional/norma-246982/texto)
- [General Roca, 92/2024](https://www.argentina.gob.ar/normativa/nacional/norma-399114/texto)
- [Nómina judicial de electores y mesas de Río Negro de 2017](https://old.pjn.gov.ar/cne/secelec/document/otros/16-Habiles_Mesas.pdf)
- [San Luis, Disp. 38/2015](https://www.argentina.gob.ar/normativa/nacional/norma-248942/texto)
- [San Luis, 651/2016](https://www.argentina.gob.ar/normativa/nacional/norma-261558/texto)
- [Villa Mercedes, 376/2018](https://www.argentina.gob.ar/normativa/nacional/norma-312228/texto)
- [San Luis, 187/2022, reserva temporal](https://www.argentina.gob.ar/normativa/nacional/norma-376149/texto)
- [Ushuaia, Disp. 8-E/2017 y anexo](https://www.argentina.gob.ar/normativa/nacional/norma-271231/texto)
- [Ushuaia, 291-E/2017](https://www.argentina.gob.ar/normativa/nacional/norma-274819/texto)
- [Cipolletti, 186/2022](https://www.argentina.gob.ar/normativa/nacional/norma-376317/texto)
- [Caleta Olivia, CNE 68/2022](https://www.boletinoficial.gob.ar/detalleAviso/primera/272295/20220923)
- [Río Gallegos, 28/2024](https://www.argentina.gob.ar/normativa/nacional/norma-402921/texto)
- [Neuquén, Disp. 154-E/2016](https://www.argentina.gob.ar/normativa/nacional/norma-271230/texto)
