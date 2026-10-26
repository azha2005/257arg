# Atlas legislativo de 1983 (diputados nacionales)

Atlas de las elecciones de diputados nacionales del 30 de octubre de 1983, por departamento. Es independiente del atlas presidencial del mismo año. 525 de 526 unidades con votos de la base; las Islas Malvinas en gris.

## Reproducir

```
python mapa1983dip/build_1983dip.py
python render_transparentes.py mapa1983dip
python render_blanco.py mapa1983dip atlas_1983_diputados.html
python commons/paquete.py 1983dip
python tools/documentar_leg8399.py
```

## Fuentes

- Votos por departamento: base de Ernesto Calvo, `base8399/ernesto/1983_diputados/dpto_partidos.csv` (hojas de `TPDENP1983T.xls`).
- Resultado nacional del cartel (torta, barras, métricas): tabla del artículo [Elecciones legislativas de Argentina de 1983](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1983), clave `1983_diputados` de `wikitop.py`.
- Copias del artículo en esta carpeta: `w1983.txt`, `wiki.html`, `wiki_rows.json` (tabla nacional) y `wiki_prov_listas.json` (tablas provinciales).
- Geometría: departamentos del censo de 1980 (`mapa1983/units_raw.pkl`).
- Constructor: `atlas_leg8399.py` (compartido con los otros tres años). `FAMS[1983]` asigna cada código de la base a un bloque de la tabla nacional; `bloc()` tiene las excepciones por provincia.

## Decisiones

- La base trae en 0 a la UCR en Posadas (Misiones) y Chacabuco (San Luis) y al PJ en Salta capital y Andalgalá (Catamarca). En los cuatro casos la diferencia entre los positivos declarados y la suma de las demás fuerzas coincide exactamente con lo que falta frente a la tabla provincial de la Wikipedia, así que se imputa ese residuo (anotado en la ficha). Cambia el ganador de Posadas, Andalgalá y Chacabuco.
- Islas del Ibicuy se suma a Gualeguaychú (geometría de 1980). Río Negro trae la fila de votantes repetida en 13 departamentos: se toma una sola vez.
- MOFEPA lleva el ámbar del proyecto (#f59e0b); MPN el azul marino (#14306e).
- Logos reutilizados del proyecto; en varios emblemas provinciales el diseño de época no está verificado (ver `logos_wikipedia/LICENCIAS.md`).

## Bloques: base contra Wikipedia

| Bloque | Base | Wikipedia | Diferencia |
|---|---:|---:|---:|
| UCR | 7.104.747 | 7.104.748 | -1 |
| PJ | 5.697.160 | 5.697.610 | -450 |
| PAL | 113.482 | 113.482 | +0 |
| BLO | 61.737 | 61.737 | +0 |
| MPN | 36.168 | 36.168 | +0 |
| MPJ | 26.535 | 26.535 | +0 |
| MFP | 16.490 | 16.490 | +0 |
| AF | 169.025 | 169.585 | -560 |
| UCD | 251.541 | 251.541 | +0 |
| PI | 411.865 | 411.883 | -18 |
| MID | 223.057 | 223.763 | -706 |
| PC | 182.296 | 182.296 | +0 |
| PDC | 139.881 | 139.881 | +0 |
| ADS | 124.897 | 125.085 | -188 |

La base incluye las imputaciones de abajo. Las diferencias restantes no se reparten entre departamentos.

## Imputaciones

| Provincia | Departamento | Bloque | Votos |
|---|---|---|---:|
| Catamarca | andalgala | PJ | 2.564 |
| Misiones | capital | UCR | 35.749 |
| Salta | capital | PJ | 43.652 |
| San Luis | chacabuco | UCR | 3.232 |

## Positivos declarados distintos de la suma de las fuerzas

Los porcentajes se calculan sobre la suma de las fuerzas; el valor declarado queda en la ficha.

| Provincia | Departamento | Declarados | Suma |
|---|---|---:|---:|
| Córdoba | cruz del eje | 27.388 | 27.362 |
| Corrientes | concepcion | 6.249 | 5.581 |
| Chaco | chacabuco | 9.397 | 9.387 |
| Chubut | gastre | 806 | 356 |
| Entre Ríos | diamante | 21.682 | 21.653 |
| Formosa | matacos | 2.223 | 2.221 |
| Jujuy | humahuaca | 7.723 | 7.685 |
| La Pampa | catrilo | 3.317 | 3.312 |
| Mendoza | guaymallen | 97.254 | 97.108 |
| Neuquén | collon cura | 1.066 | 1.060 |
| Río Negro | el cuy | 1.443 | 1.435 |
| Santiago del Estero | atimisqui | 3.707 | 3.130 |
| Santa Cruz | deseado | 16.690 | 16.662 |
| Santa Fe | castellanos | 71.120 | 71.011 |
| Tucumán | cruz alta | 54.325 | 54.137 |

Filas de métricas repetidas en la base (se toma la primera): 13 departamentos de Río Negro.

Padrón inconsistente (más votantes que inscriptos; gris claro en participación y sin ese dato en la ficha): avellaneda (Río Negro, 10.049 votantes / 1.156 inscriptos), pichi mahuida (Río Negro, 5.380 votantes / 3.059 inscriptos), pilcaniyeu (Río Negro, 1.800 votantes / 1.025 inscriptos), san antonio (Río Negro, 9.191 votantes / 5.269 inscriptos), valcheta (Río Negro, 2.871 votantes / 1.469 inscriptos), guasayan (Santiago del Estero, 3.632 votantes / 1.158 inscriptos).

## Modos y leyenda

Pestañas: GANÓ, UCR, PJ, PI, PART.

Ganadores (unidades): Unión Cívica Radical 291; Partido Justicialista 196; Pacto Autonomista (Liberal · Corrientes) 20; Movimiento Popular Neuquino (Neuquén) 12; Federalista Pampeano (MOFEPA) 3; Partido Bloquista 3.

La leyenda lleva solo las fuerzas que ganan alguna unidad; las demás van a «otros» en la torta y siguen en la ficha de cada unidad. Logos y reservas de época en `logos_wikipedia/LICENCIAS.md`.

## Pendientes

- Nada pendiente en la cobertura; las diferencias con la Wikipedia están arriba.

## Commons

Paquete local en `commons/1983dip/subir/` (sin subir). Ver `commons/1983dip/LEEME_SUBIDA.md`.
