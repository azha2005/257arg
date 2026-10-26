# Convencionales constituyentes 1994 (10 de abril de 1994)

Atlas `atlas_1994.html` (`python build_1994.py`), departamentos del censo de 1991 (`Departamentos_1991.shp`, 530 unidades con las 28 de Capital; `geom.py` y `insets99.SHP` apuntan a ese archivo) + 28 circunscripciones de Capital. Modos: ganador, UCR, PJ, FG, MODIN. Sin modo de participación (la base no trae padrón completo).

## Datos
- Fuente: `Bases Ernesto/País x Departamento/1994-const.xls` (una hoja por provincia). Se extrajo con `base8399/construir_const94.py` a `base8399/ernesto/1994_constituyentes/dpto_partidos.csv` (+ `anomalias.csv`). Solo columnas `..94cn` (convencionales nacionales); las `..94cp` se descartan.
- Anomalías de formato resueltas en el script (Chaco con dos `pos94cn`, La Rioja con sufijo `dn`, Mendoza `vot`, Neuquén `totales`, Santa Cruz `pj0094cn`, fila Sector Antártico de TdF, Capital por circunscripción).
- Códigos INDRA ≠ INDEC: el emparejamiento es por nombre. Con el mapa de 1991 casi todas las unidades de la base tienen polígono propio (Islas del Ibicuy, Palpalá, Tres Lomas y Florentino Ameghino ya no se fusionan, como sí hubo que hacer con el de 1980). Quedan dos fusiones: 2 de Abril → 12 de Octubre (Chaco, creado después del censo) y Sector Antártico → Ushuaia. Los nombres del mapa de 1991 vienen abreviados («Gnral.», «Pdte.», «Sn.»): se emparejan por nombre normalizado más una lista de alias en `build_1994.py`.
- Guer Aike (Santa Cruz): faltaban 26 votos de PJ en la base; se imputó el residuo (positivos − resto), con nota en la unidad.
- Capital: el artículo de Wikipedia tiene datos de Capital, aunque la hoja «Codigos» de Ernesto dice «No elige Convencionales» (los datos existen igual).

## Grupos (tabla de Wikipedia)
PJ = FJUFE, PJ, Frejupo, FJ, FPV, Fjuvi, FJR y el Frente de la Esperanza de Tucumán y San Juan. UCR = UCR y alianzas provinciales (UCRP, FCIV, FTPRO). Además FG, MODIN, PD (Mendoza), PAL (Corrientes), Fuerza Republicana (Tucumán/Jujuy), MPN, MPJ, PRS (Salta) y CI. La leyenda muestra solo las 10 fuerzas que ganan al menos un polígono (CI queda en «otros»).

## Diferencias base de Ernesto vs. Wikipedia (sin corregir)
| Grupo | Ernesto | Wikipedia | Dif. |
|---|---|---|---|
| PJ | 6.059.288 | 6.072.335 | −13.047 |
| UCR | 3.162.345 | 3.114.166 | +48.179 |
| FG | 2.071.679 | 2.082.622 | −10.943 |
| MODIN | 1.458.021 | 1.461.451 | −3.430 |
| MPN | 57.562 | 47.023 | +10.539 |

Por provincia: Córdoba +98.933 positivos en la base (UCR +50.071, UCD +31.449); Neuquén MPN +10.539; San Luis −6,7 mil; Entre Ríos FG −10 mil; Buenos Aires ≈ −10 mil. Causa desconocida; el topline (torta y barras) usa la tabla de Wikipedia, el mapa usa la base.

## Logos
UCR (escudo), PJ (bandera cuadrada), FG, MODIN y Fuerza Republicana de la infobox de Wikipedia; la fecha de diseño de los tres últimos no está verificada (ver `logos_wikipedia/LICENCIAS.md`). El resto lleva sigla.

- **Geometría (15-oct-2026):** 2 de Abril (Chaco) tiene polígono propio (de `Departamentos_2001`, recortado al contorno de 1991) en lugar de sumarse a 12 de Octubre (`../newpartidos.py`). La base no trae los partidos nuevos del GBA (se crearon a fines de 1994).
