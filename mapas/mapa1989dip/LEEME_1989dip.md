# Atlas legislativo de 1989 (diputados nacionales)

Atlas de las elecciones de diputados nacionales del 14 de mayo de 1989, por departamento. Es independiente del atlas presidencial del mismo año. 525 de 526 unidades con votos de la base; las Islas Malvinas en gris.

## Reproducir

```
python mapa1989dip/build_1989dip.py
python render_transparentes.py mapa1989dip
python render_blanco.py mapa1989dip atlas_1989_diputados.html
python commons/paquete.py 1989dip
python tools/documentar_leg8399.py
```

## Fuentes

- Votos por departamento: base de Ernesto Calvo, `base8399/ernesto/1989_diputados/dpto_partidos.csv` (hojas de `TPDENP1989T.xls`).
- Resultado nacional del cartel (torta, barras, métricas): tabla del artículo [Elecciones legislativas de Argentina de 1989](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1989), clave `1989_diputados` de `wikitop.py`.
- Copias del artículo en esta carpeta: `w1989.txt`, `wiki.html`, `wiki_rows.json` (tabla nacional) y `wiki_prov_listas.json` (tablas provinciales).
- Geometría: departamentos del censo de 1980 (`mapa1989/units_raw.pkl`).
- Constructor: `atlas_leg8399.py` (compartido con los otros tres años). `FAMS[1989]` asigna cada código de la base a un bloque de la tabla nacional; `bloc()` tiene las excepciones por provincia.

## Decisiones

- FREJUPO agrupa las listas justicialistas; la UCR incluye sus alianzas provinciales con la CFI y el Partido Federal; la Alianza de Centro incorpora el PAL-PDP de Corrientes, como la tabla nacional.
- Islas del Ibicuy se suma a Gualeguaychú, Palpalá a Capital (Jujuy) y Tres Lomas a Pellegrini (geometría de 1980). Sin mapa de participación: la base no trae el padrón en todos los departamentos.
- Cruzada Renovadora lleva el verde oscuro del proyecto (#004d40, como en 1991 y 1994).
- Logos reutilizados del proyecto; en varios emblemas provinciales el diseño de época no está verificado (ver `logos_wikipedia/LICENCIAS.md`).

## Bloques: base contra Wikipedia

| Bloque | Base | Wikipedia | Diferencia |
|---|---:|---:|---:|
| PJ | 7.466.517 | 7.460.488 | +6.029 |
| UCR | 4.867.648 | 4.865.835 | +1.813 |
| ADC | 1.794.823 | 1.796.271 | -1.448 |
| CFI | 565.147 | 565.080 | +67 |
| IU | 581.447 | 580.943 | +504 |
| US | 451.194 | 451.177 | +17 |
| FR | 213.967 | 213.957 | +10 |
| CR | 87.273 | 87.273 | +0 |
| MPN | 49.070 | 49.070 | +0 |
| BLO | 39.171 | 39.171 | +0 |
| ACHA | 45.298 | 45.298 | +0 |
| MPF | 2.305 | 2.309 | -4 |
| PPR | 22.516 | 22.331 | +185 |

La base incluye las imputaciones de abajo. Las diferencias restantes no se reparten entre departamentos.

## Positivos declarados distintos de la suma de las fuerzas

Los porcentajes se calculan sobre la suma de las fuerzas; el valor declarado queda en la ficha.

| Provincia | Departamento | Declarados | Suma |
|---|---|---:|---:|
| San Luis | capital | 53.701 | 53.222 |
| San Luis | ayacucho | 8.589 | 8.588 |
| San Luis | chacabuco | 7.987 | 7.984 |
| San Luis | junin | 7.005 | 6.987 |
| San Luis | pedernera | 44.809 | 44.479 |
| San Luis | pringles | 6.235 | 6.201 |

Padrón inconsistente (más votantes que inscriptos; gris claro en participación y sin ese dato en la ficha): Balcarce (Buenos Aires, 24.392 votantes / 2.834 inscriptos), l gran san martin (Misiones, 29.581 votantes / 17.350 inscriptos).

## Modos y leyenda

Pestañas: GANÓ, PJ, UCR, ADC. Sin participación: la base no trae el padrón en todos los departamentos.

Ganadores (unidades): FREJUPO (Frentes justicialistas) 431; Unión Cívica Radical 55; Alianza de Centro (UCeDé y aliados) 22; Movimiento Popular Neuquino (Neuquén) 7; Cruzada Renovadora 7; Fuerza Republicana 2; Confederación Federalista (Independiente) 1.

La leyenda lleva solo las fuerzas que ganan alguna unidad; las demás van a «otros» en la torta y siguen en la ficha de cada unidad. Logos y reservas de época en `logos_wikipedia/LICENCIAS.md`.

## Pendientes

- Nada pendiente en la cobertura; las diferencias con la Wikipedia están arriba.

## Commons

Paquete local en `commons/1989dip/subir/` (sin subir). Ver `commons/1989dip/LEEME_SUBIDA.md`.
