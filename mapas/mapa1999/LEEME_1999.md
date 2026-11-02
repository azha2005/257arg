# Atlas 1999, presidente

`python mapas/mapa1999/build_1999.py` → `atlas_1999.html` y `dataset_1999.json`. Cuatro pestañas: Ganó, De la Rúa (DLR), Duhalde (DUH) y Cavallo (CAV). Se armó a partir de `build_1995.py` con la geometría de `mapa2001` (29-oct-2026). El topline está en `comun/wikitop.py`, con la clave `1999`.

## Datos
- **Base de Ernesto Calvo**, `datos/base8399/ernesto/1999_presidente/dpto_partidos.csv`: votos por departamento en 22 provincias y las 28 circunscripciones de Capital. **No es el escrutinio provisorio**: los totales por provincia coinciden con la tabla «Resultados por distrito» de la Wikipedia a menos de 0,5 % del total provincial. Solo Formosa difiere en 1 punto en De la Rúa (cotejo en `transferencias/presidente_1999.py`, función `cotejo`).
- **San Luis y Santa Cruz** no están en esa base. La Alianza (`ucr`), la Concertación (`pj`) y el total de positivos salen de Lupu y Stokes por departamento (`datos/base8399/elecciones/1999_presidente/lupu_stokes.csv`). **Cavallo y los demás** (31-oct-2026): el resto de Lupu y Stokes (total − Alianza − PJ) se reparte con los porcentajes por departamento del escrutinio provisorio de INDRA publicados por el INAP (área de Reforma Política, «Datos Departamentales 1999»; copia en `andytow/` y CSV en `datos/base8399/inap/1999_presidente_pct.csv`, generado con `extraer_1999.py`). El reparto es proporcional a los porcentajes y los votos se redondean por resto mayor. En los 16 departamentos, los porcentajes de la Alianza y el PJ del INAP coinciden con Lupu y Stokes a 0,03 puntos. Son **votos estimados** y la ficha lo dice. No hay blancos, nulos ni inscriptos para estas dos provincias.
- **Inscriptos**: la base no los trae para Buenos Aires, Catamarca, Córdoba ni Tierra del Fuego. Por eso no hay modo de participación; el anillo usa el dato nacional de la Wikipedia.
- **Nacional** (torta y barras): tabla del artículo «Elecciones presidenciales de Argentina de 1999» (`w1999.txt`, copia de `transferencias/fuentes/w1999p.txt`). Positivos 18.953.704, blancos 708.876, anulados 186.761, votantes 19.849.341 e inscriptos 24.111.270.
- Totales de la base contra la Wikipedia:

  | Fórmula | Base | Wikipedia |
  |---|---|---|
  | De la Rúa | 9.164.533 | 9.167.220 |
  | Duhalde | 7.249.377 | 7.253.902 |
  | Cavallo | 1.937.130 | 1.937.544 |

  Con San Luis y Santa Cruz estimados, Cavallo queda a 414 votos de la tabla (antes faltaban 24.725). Por provincia: San Luis 16.477 (tabla 16.707) y Santa Cruz 7.834 (tabla 7.845).

## Listas → fórmulas
Se usa la tabla «Acceso a boletas» del artículo, la misma que en `transferencias/presidente_1999.py`:
- **De la Rúa**: Alianza y sus nombres provinciales (`ali`, `ali00`, `alisal`, `alisj`, `alifcso`, `aftod`), FREPASO de Catamarca, PDP de Santa Fe (`adp`) y PAL-PDP de Corrientes.
- **Duhalde**: Concertación Justicialista y sus variantes (`acjc`, `cjc`, `cjcer`, `cjccha`, `cjccat`, `apj`, `afjes`, `pj`), Frente de Integración Federal (`afifed`, `fifnc`), Partido Federal de Mendoza y la UCeDé **salvo en Santa Fe**.
- **Cavallo**: Acción por la República y sus alianzas (`apr`, `aapr`, `aaprf`, `aaprmpatp`) y la UCeDé de Santa Fe.
- En Corrientes y Santiago del Estero, `acjc00` es el total del lema de la Concertación. Se cuentan los sublemas `acjc01` a `acjc03` y no el lema, para no duplicar.
- **Tierra del Fuego**: la Wikipedia repite en «otros» la cifra de Cavallo (8.707); la base da 1.307 para otros, que es lo correcto. De ahí sale el −13,6 % del cotejo.

## Decisiones
- **Leyenda**: De la Rúa gana 340 unidades y Duhalde 198. Cavallo no gana ninguna, pero va en la leyenda como tercera fuerza, con 10,22 %. Es una excepción a la regla 3, pedida por el usuario el 29-oct-2026. Su fila no lleva franja de tonos.
- Provincias: De la Rúa gana 20 y Duhalde 4 (Formosa, La Rioja, Misiones y Santiago del Estero), igual que la Wikipedia.
- **Colores**: los mismos de los otros atlas. Alianza #dc0143 (1997, 2001 y 1999 diputados), PJ #318ce7 y Acción por la República #3e5298.
- **Logos**: el ancho se calcula con barras de 50 px (hasta cinco filas); con 42, como en 1995, el logo de Acción por la República se cortaba. Son `Alianza.png`, la bandera cuadrada del PJ y `Logo_Accion_por_la_Republica.svg`; los tres ya figuran en `logos/LICENCIAS.md` por 1997 y 2001.
- **Geometría**: departamentos de 1991. Los partidos del GBA creados después, 2 de Abril y San Salvador (Entre Ríos, que en 1999 ya vota aparte) llevan polígono propio (`newpartidos.apply(..., desde2001=True)`, como `mapa2001`).
- **Antártida**: la base la trae como fila aparte (153 votantes). Se suma a Ushuaia, porque el mapa no tiene esa unidad, y se anota en la ficha. El recuadro de la Antártida se pinta con su propio resultado (`DATA.antRec`, Duhalde 92 a 23) y no con el de la provincia, que ganó De la Rúa.
- Malvinas, en gris.

## Diferencia con el mapa de Commons
El mapa por departamento que usa el artículo («Resultados de las Elecciones presidenciales de Argentina de 1999 (por departamento).svg») da De la Rúa 284 y Duhalde 243. Este atlas da 340 y 198 sobre 538 unidades: incluye las 28 circunscripciones de Capital y los partidos nuevos. Todavía no se cotejó unidad por unidad. Según su autor, ese mapa usa solo los porcentajes del provisorio.

## Archivos
`img/m_*.png` (capturas de control), `png_transparentes/mapa1999/`, `png_blanco/mapa1999/` y la carpeta `all elections white bg/`. Paquete de Commons en `commons/1999/` (29-oct-2026, sin subir). **No se regeneró** después de cargar a Cavallo en San Luis y Santa Cruz (31-oct-2026): su modo Cavallo todavía muestra esas provincias en beige. `commons/config.py` ya tiene los avisos nuevos; falta correr `python commons/paquete.py 1999`.
