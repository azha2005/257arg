# Base del INAP (área de Reforma Política), 1995–1999

Origen: `andytow/` en la raíz del proyecto. Son copias de la «Base Estadística de Elecciones y Sistemas Electorales» del INAP (refpol@sfp.gov.ar), la misma fuente de la que salen las bases de Ernesto Calvo.

## Qué hay en `andytow/`
- `base electoral departamental 95-97.xls` (también dentro de `departamental9597.zip`, con `Observaciones y datos faltantes.xls`): **escrutinio definitivo** por departamento, en votos y separado por sexo (sufijos `f` y `m`). Trae presidente y diputados nacionales de 1995, diputados nacionales de 1997, gobernador, diputados y senadores provinciales y bancas asignadas. Capital Federal viene en una sola fila. Donde se cotejó, el PJ da las mismas cifras que Ernesto. San Luis 1997 está vacío: «faltan datos de dip nac en originales».
- `1999 *.xls` (también en `Datos Departamentales 1999.zip`): **escrutinio provisorio** de INDRA, **solo porcentajes** sobre positivos. Trae presidente (todas las provincias, también San Luis y Santa Cruz), diputados nacionales (sin La Rioja, Misiones, Neuquén, San Luis ni Tierra del Fuego), gobernador (7 provincias) y diputados provinciales (8).
- `buenosaires.zip`: las 209 circunscripciones de Capital de 1999 de Andy Tow (polígonos con Alianza, Acción por la República y participación en diputados).
- `FAQ.doc` y `Libro de Código.doc`: documentación de la base de 1995–97.

## CSV de esta carpeta
`python datos/base8399/inap/extraer_1999.py` escribe `1999_<cargo>_pct.csv` (provincia, departamento, sigla, partido, código, pct) con los cuatro archivos de 1999, sin tocar los valores.

## Uso
- `mapas/mapa1999/build_1999.py`: Cavallo y las demás fórmulas en San Luis y Santa Cruz. El residuo de Lupu y Stokes se reparte con estos porcentajes (31-oct-2026).
- Sin usar todavía: Santa Cruz 1999 por departamento en diputados nacionales (solo porcentajes; el atlas `mapa1999dip` la pinta en color sólido y ya está subido) y los votos reales de Deseado 1995 (PJ 16.934 y UCR 4.968; `mapa1995` los imputa).
