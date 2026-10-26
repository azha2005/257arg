# Atlas 1987, diputados nacionales

`python build_1987.py` → `atlas_1987.html` + `dataset_1987.json`. Mismo método que 1985 (`../mapa1985/`): departamentos del censo de 1980, 28 circunscripciones de Capital, los siete recuadros de Wikipedia 1999 (`../insets99.py`), topline de `../wikitop.py`.

## Datos
- **Departamentos y provincias**: base de Ernesto Calvo, `../base8399/ernesto/1987_diputados/dpto_partidos.csv`.
- **Resultado nacional**: tabla de «Elecciones legislativas de Argentina de 1987» (Wikipedia, `w1987.txt`). Positivos 16.037.652; blancos 326.959; nulos 77.241; diferencia de actas 14.080; votantes 16.455.932; registrados 19.420.204.
- **Bloques** (código → grupo de la tabla de Wikipedia), con total de la base entre paréntesis y el de Wikipedia después:
  - PJ = `pj` + `fjren` + `fjpart` + `fj` + `fje` + `frejuli` + `fpv` (6.622.158; Wikipedia 6.622.252)
  - UCR = `ucr` + `ucrde` + `ucrcon` + `ucrvp` (5.972.503; 5.972.588)
  - UCeDe y aliados = `ucd` + `ucddpuc` + `ucddem` + `ducd` + `apce` + `ucdmpp` + `adc` + `ucdsr` + `ucddp` (926.990; 926.988)
  - Pacto Autonomista Liberal, MPN, Alianza Bloquista y Partido Provincial Rionegrino: una columna cada uno, exactos. FAP: 98.165 contra 98.249.

## Decisiones
- Leyenda solo con los partidos que ganan alguna unidad (PJ 287, UCR 189, PAL 24, MPN 16, Bloquista 6, FAP 2, UCeDe 1, PPR 1). Colores, logos de época y recuadros como en 1985 (reglas en `../AGENTS.md`).
- **Tierra del Fuego** no renovaba diputados en 1987 (la tabla de bancas de Wikipedia no le asigna renovación): sus dos departamentos, las Malvinas y el recuadro de la Antártida van en gris con la clave «no eligió diputados».
- **Modos**: Ganó, UCR, PJ y UCeDe. No hay modo de participación: la base trae el padrón solo para 372 de 526 unidades y faltan los 126 partidos de Buenos Aires y los 26 departamentos de Córdoba. Las fichas de esas unidades no muestran inscriptos ni participación.

## Correcciones a la base de Ernesto (13 cifras)
Se compararon los totales por partido de cada provincia con la tabla provincial de Wikipedia (`wiki_prov.json`).
1. **Celdas con «9» en lugar del dato (12 unidades).** El total de positivos de la unidad sí es correcto, así que se imputó el residuo (positivos menos el resto de las fuerzas) a la fuerza cuya celda trae el 9: Federación (ER, Frente Justicialista Entrerriano, +10.377), Junín (Mza, PJ, +7.955), 12 de Octubre (Chaco, PJ, +5.478), Curuzú Cuatiá (Ctes, PJ, +4.629), Neuquén capital (MID, +1.145), Rinconada (Jujuy, PJ, +869), Chalileo (La Pampa, PJ, +492), Telsen (Chubut, PJ, +324), circunscripción 5 (Capital, PTP, +176), Conesa (RN, MID, +110), Constitución (SF, Frente Renovador, +68) y Caucete (SJ, FRAL, +39). Con ellas, los totales provinciales de esas fuerzas coinciden con Wikipedia.
2. **La Plata**: el Frente Justicialista Renovador trae 11.919 votos; Wikipedia da 2.706.508 para el frente y la base suma 2.606.524 sin corregir. La diferencia (99.984) cae entera en La Plata, así que se llevó a 111.903. Es una inferencia por el total, no un dato visto.
- Cada unidad corregida lleva una nota en su ficha.
- Quedan diferencias chicas sin corregir: Tucumán (UCR 176.187 contra 176.351; PJ 135.407 contra 135.501; unos 130 votos en total), unos pocos votos por provincia en Buenos Aires y Córdoba (en Córdoba la suma de partidos supera al positivo en 500 votos en Punilla).

## Casos particulares
- **Palpalá** (Jujuy), **Islas del Ibicuy** (Entre Ríos) y **Tres Lomas** (Buenos Aires): la base los trae como unidades aparte; el mapa de 1980 los incluye en Capital, Gualeguaychú y Pellegrini (se comprobó con los polígonos de 1991). Se suman a esas unidades, con nota.
- **Santiago del Estero**: la base de 1987 tiene los códigos de Capital y Aguirre intercambiados respecto de otros años, pero los nombres y los votos corresponden (Capital 93.497 positivos), así que se usó el nombre.
- La Rioja y otras: mismos alias que en 1985.

## Pendientes
- Sin verificación de los departamentos con otra fuente (solo provincias contra Wikipedia).
- La Plata queda como inferencia hasta ver el acta o la planilla original.
