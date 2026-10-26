# Presidenciales hipotéticas de 1985

Escenario del usuario fechado el 10 de marzo de 1985. No son resultados históricos. Ejecutar `python mapa1985hip/build_1985hip.py` desde la raíz.

El atlas reutiliza el HTML y la geometría del atlas histórico de 1985 (departamentos de 1980 y 28 circunscripciones de Capital). No modifica ese atlas ni wikitop.py. Los totales provinciales y nacionales proceden de la copia adjunta `1985_completo.docx`; los perfiles departamentales proceden de las filas partidarias de `mapa1985/dataset_1985.json`, generado con la base de Ernesto de diputados de 1985.

## Reparto

- Massera/Bajczman: PJ ortodoxo y renovador (`pj`, `frejuli`, `frejuchu`, `fren`, `cbt`, `lab`, `fupop`; `flib` en Capital).
- Nadra/Íscaro: PC y alianzas del Frente del Pueblo (`frepu`, `frepun`, `pc`, `mas`; `flib` fuera de Capital). Se toma la alianza completa porque sus componentes no están desagregados.
- Manrique/Rawson: UCeDé y aliados, demócratas locales, PDC y PDP (`ucd`, `adc`, `unpop`, `apce`, `pd`, `dl`, `dj`, `adi`, `dc`, `tbdc`, `pdp`, `palfdp`). El PAL se incluye como alianza local liberal y demócrata progresista.
- Alfonsín/Cafiero: todas las agrupaciones restantes.

Por autorización expresa del usuario, cada candidatura se ajusta por separado al margen provincial del DOCX, conservando el peso relativo de sus votos reales por unidad. Redondeo por restos mayores: cada suma provincial cierra al voto. No se impone un total de positivos por departamento adicional. En Catamarca no existe perfil de Manrique: sus 1.298 votos se reparten según los positivos reales. Es una estimación del escenario, no recuperación de datos ausentes.

Blancos, nulos, votantes e inscriptos se ajustan de manera independiente. Las diferencias internas del documento se conservan en `auditoria.json`: especialmente Misiones (-2.681) y Chubut (-59), además de diferencias menores. La suma de provincias coincide con cada cifra de la fila TOTAL. Los porcentajes se recalculan de los votos, no se copian los porcentajes redondeados del documento.

Malvinas no recibe votos propios; por pedido del usuario del 19-oct-2026 se colorea con el resultado provincial de Tierra del Fuego en cada modo, también en el mini provincial. Su ficha no duplica cifras ni se suma a los totales. El mapa adjunto sirve de referencia de colores y ganadores provinciales, no como fuente departamental. MCN magenta #91316b; FDS azul gris #4d5976; AF ámbar; PC rojo. Se reutilizan los emblemas RA de 1983, bandera del PJ, Alianza Federal de 1983 y FREPU de 1985 como referencias visuales de MCN, FDS, AF y PC/aliados. Ver logos_wikipedia/LICENCIAS.md. Nadra no aparece en la leyenda de ganadores porque no gana unidades. La leyenda de ganadores incluye MCN, FDS y AF; PC está en su modo propio y en cada ficha, sin ganar unidades.

## Salidas

- `atlas_1985hip.html`: atlas autocontenido con ganadores y cuatro coropletas.
- `dataset_1985hip.json`: datos usados en el atlas.
- `estimaciones_departamentales.csv`: 525 unidades con estimaciones.
- `auditoria.json`: mapeo, márgenes, discrepancias y ganadores.
- PNG en `png_transparentes/mapa1985hip/` y `png_blanco/mapa1985hip/`.

No se prepara paquete para Commons: es una simulación.

