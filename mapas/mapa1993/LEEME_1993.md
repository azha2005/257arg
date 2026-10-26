# Elecciones legislativas del 3 de octubre de 1993 (diputados nacionales)

`atlas_1993.html` (`python build_1993.py`; generado desde `mapa1994/build_1994.py`). Departamentos del censo de 1991 + 28 circunscripciones de Capital. Modos: ganador, PJ, UCR.

## Datos
- Base de Ernesto Calvo: `base8399/ernesto/1993_diputados/dpto_partidos.csv` (24 provincias, 530 unidades). Nacional: tabla de «Elecciones legislativas de Argentina de 1993» (`w1993.txt`, `../wikitop.py`).
- Mapeo código → grupo en `mapeo_1993.py` (PJ y aliados, UCR y aliados, MODIN, Frente Grande y aliados, UCeDé, Unidad Socialista, PO y aliados, y partidos provinciales). La leyenda lleva los 8 grupos que ganan alguna unidad: PJ 380, UCR 112, PAL 20, MPN 10, ACHA 4, PRS 2, FR 1, CI 1.
- Santa Cruz: las columnas `fjpsc01` y `fjpsc02` repiten votos del FJPSC (la suma de las fuerzas supera en 38.486 a los positivos); se descartan.
- 2 de Abril (Chaco) se suma a 12 de Octubre (departamento posterior al censo).
- La Pampa: los positivos superan en 2.999 a la suma de las fuerzas (falta alguna columna); se usa el positivo de la base como denominador.

## Base vs. tabla de Wikipedia (sin corregir)
PJ 7.087.589 vs 7.112.922 (−25.333); UCR 4.921.449 vs 4.946.281 (−24.832); FR 227.723 vs 227.727; PRS 120.658 vs 120.669. PAL, ACHA, MPN y CI coinciden.

## Logos
UCR (escudo) y PJ (bandera cuadrada). El resto lleva sigla (ver LEEME_1991.md).

- **Geometría (15-oct-2026):** 2 de Abril (Chaco) tiene polígono propio (de `Departamentos_2001`, recortado al contorno de 1991) en lugar de sumarse a 12 de Octubre (`../newpartidos.py`). La base de 1993 no trae los partidos nuevos del GBA (se crearon en 1994-95).
