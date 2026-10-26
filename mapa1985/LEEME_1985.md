# Atlas 1985, diputados nacionales

`python build_1985.py` → `atlas_1985.html` + `dataset_1985.json`. Mismo método que 1983 (`../mapa1983/`): departamentos del censo de 1980, 28 circunscripciones de Capital Federal, plantilla Wikipedia 1999, topline de `../wikitop.py`.

## Datos
- **Departamentos y provincias**: base de Ernesto Calvo, `../base8399/ernesto/1985_diputados/dpto_partidos.csv`.
- **Resultado nacional** (torta, barras, métricas): tabla de «Elecciones legislativas de Argentina de 1985» (Wikipedia, `w1985.txt`). Válidos 15.324.510; blancos 205.406; anulados 96.353; total 15.626.269; registrados 18.653.487.
- **Bloques** (códigos de la base → grupo de la tabla de Wikipedia), cada suma coincide al voto con el total de Wikipedia:
  - UCR = `ucr` + `ucrmpc` (6.678.647)
  - PJ = `frejuli` + `pj` + `frejuchu` (3.753.194)
  - Peronismo renovador = `fren` + `cbt` + `lab` + `fupop` + `flib` solo en Capital (1.611.441)
  - UCeDe y aliados = `ucd` + `adc` + `unpop` + `apce` (570.490)
  - Frente del Pueblo = `frepu` + `frepun` + `pc` + `mas` + `flib` fuera de Capital (353.165)
  - PAL (`palfdp`), PRS, Bloquista, MPN: una columna cada uno.

## Decisiones
- **La leyenda solo trae los partidos que ganan alguna unidad** (UCR 366, PJ 115, PAL 25, MPN 11, REN 4, PRS 2, BLO 2, UCeDe 1). PI, Frente del Pueblo, PF, Unidad Socialista, PDP y el resto van en «otros» en la torta; siguen visibles en el detalle de cada unidad.
- **Colores distintos entre sí**, no los de `{{Color político}}`: UCR rojo, PJ azul, renovador ámbar, UCeDe violeta, PAL turquesa, PRS magenta, Bloquista verde, MPN azul marino. Los de Wikipedia para PJ, renovador, UCeDe, PRS y MPN eran todos azules parecidos.
- **Recuadros**: los siete de Wikipedia 1999 (`../insets99.py`), igual que en 1983.
- **Logos de época**: UCR (escudo), PJ (bandera cuadrada, diseño de 1946) y UCeDe (el del infobox del artículo). PAL, Bloquista y MPN llevan sigla porque los archivos de la Wikipedia son de 2018 a 2025. El atlas de 1983 se corrigió con las mismas reglas.

## Control contra Wikipedia
- Los 24 distritos: todos los totales por partido de la tabla provincial de Wikipedia (`wiki_prov.json`) aparecen exactos en la base, salvo Formosa: faltan 511 votos del PSP y 385 del PS de Formosa (896 votos).
- Capital Federal son 28 circunscripciones; la base trae el número de circunscripción.

## Casos particulares
- **Islas del Ibicuy** (Entre Ríos): la base de 1985 la trae como departamento; el mapa de 1980 la incluye en Gualeguaychú. Se suman las dos (nota en la unidad).
- **Jujuy, San Juan y Santiago del Estero**: la hoja de 1985 trae solo el código INDRA; los nombres se toman de la base de 1983 (mismos códigos). La base de 1985 no trae Palpalá como departamento (15 unidades en Jujuy, igual que en 1983 y que el mapa de 1980).
- **La Rioja**: Felipe Varela = General Lavalle del mapa de 1980; Peñaloza, Vera Peñaloza y Quiroga por alias.
- **Islas Malvinas**: sin dato propio, hereda a Tierra del Fuego.

## Pendientes
- Sin verificación con otra fuente de los departamentos (solo provincias contra Wikipedia).
