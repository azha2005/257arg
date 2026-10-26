# Elecciones legislativas del 8 de septiembre de 1991 (diputados nacionales)

`atlas_1991.html` (`python build_1991.py`; el build se genera de `mapa1994/build_1994.py`). Departamentos del censo de 1991 (`Departamentos_1991.shp`, 530 unidades con las 28 circunscripciones de Capital). Modos: ganador, PJ, UCR, UCeDé.

## Datos
- Base de Ernesto Calvo: `base8399/ernesto/1991_diputados/dpto_partidos.csv` (24 provincias, 529 unidades). Resultado nacional (torta, barras, métricas): tabla de «Elecciones legislativas de Argentina de 1991» (`w1991.txt`, `../wikitop.py`).
- Los grupos son las filas «Total … y aliados» de la tabla de Wikipedia; el mapeo código → grupo está en `mapeo_1991.py` (PJ y aliados, UCR y aliados, UCeDé y aliados, Unidad Socialista y aliados, CFI, Izquierda Unida, FR y partidos provinciales sueltos). La leyenda lleva solo los 11 grupos que ganan al menos una unidad: PJ 363, UCR 99, PAL 20, MPN 15, CFI 13, UCeDé 4, BLO 5, CR 5, FR 2, MPF 1, CI 1. El CFI de la tabla incluye al Partido Renovador de Salta, al Frente Independiente (Buenos Aires) y al MPJ, por eso gana unidades en Salta y Jujuy.
- Nombres de unidades: el mapa de 1991 los abrevia («Gnral.», «Pdte.»); se emparejan por nombre normalizado más alias (`build_1991.py`, `EALIAS`). Quedan 0 unidades de la base sin polígono; Malvinas hereda el dato de Tierra del Fuego.
- Cosas de la base resueltas en el build: Corrientes trae dos columnas de positivos (se usa la que coincide con la suma de las fuerzas); San Luis no trae positivos (se usa la suma de las fuerzas).

## Base vs. tabla de Wikipedia (sin corregir)
| Grupo | Ernesto | Wikipedia | Dif. |
|---|---|---|---|
| PJ | 6.405.771 | 6.425.437 | −19.666 |
| UCR | 4.536.413 | 4.539.967 | −3.554 |
| UCeDé | 981.450 | 981.611 | −161 |
| CFI | 490.162 | 490.099 | +63 |
| FR | 274.057 | 282.478 | −8.421 |
PAL, MPN, BLO, CR, MPF y CI coinciden al voto. La torta y las barras usan la tabla de Wikipedia.

## Logos
UCR (escudo de 1931), PJ (bandera cuadrada, diseño de 1946) y UCeDé (infobox del artículo de 1991). El resto lleva sigla: los logos de Wikipedia de MPN (2018), PAL (2023), Bloquista (2025), PRS, CR, etc. son modernos o de fecha desconocida. Pendiente: encontrar emblemas de época de los partidos provinciales.
