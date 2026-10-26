# Atlas legislativo de 1999 (diputados nacionales)

Atlas de las elecciones de diputados nacionales del 24 de octubre de 1999, por departamento. Es independiente del atlas presidencial. 522 de 539 unidades con votos de la base; San Luis, Santa Cruz en color sólido con el total provincial de la Wikipedia; las Islas Malvinas en gris.

## Reproducir

```
python mapa1999dip/build_1999dip.py
python render_transparentes.py mapa1999dip
python render_blanco.py mapa1999dip atlas_1999_diputados.html
python commons/paquete.py 1999dip
python tools/documentar_leg8399.py
```

## Fuentes

- Votos por departamento: base de Ernesto Calvo, `base8399/ernesto/1999_diputados/dpto_partidos.csv` (hojas de `TPDENP1999T.xls`).
- Resultado nacional del cartel (torta, barras, métricas): tabla del artículo [Elecciones legislativas de Argentina de 1999](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1999), clave `1999_diputados` de `wikitop.py`.
- Copias del artículo en esta carpeta: `w1999.txt`, `wiki.html`, `wiki_rows.json` (tabla nacional) y `wiki_prov_listas.json` (tablas provinciales).
- Geometría: departamentos de 1991 con los partidos nuevos con polígono propio (`mapa2001/units_raw.pkl`).
- Constructor: `atlas_leg8399.py` (compartido con los otros tres años). `FAMS[1999]` asigna cada código de la base a un bloque de la tabla nacional; `bloc()` tiene las excepciones por provincia.

## Decisiones

- San Luis (Alianza 44,6 %) y Santa Cruz (Alianza 45,9 %, PJ 45,6 %) se pintan enteras con el color de su resultado provincial, sin límites departamentales, como San Luis en 1997.
- Corrientes: se cuenta el lema ACJC00 una sola vez, sin sumarle otra vez sus sublemas. Córdoba trae la fila de inscriptos repetida: se toma la primera.
- Unidad Bonaerense lleva sigla (la Wikipedia usa una bandera gris genérica). Se reutiliza la geometría del atlas de 2001 (con San Salvador separado); el Sector Antártico se suma a Ushuaia.
- Logos reutilizados del proyecto; en varios emblemas provinciales el diseño de época no está verificado (ver `logos_wikipedia/LICENCIAS.md`).

## Bloques: base contra Wikipedia

| Bloque | Base | Wikipedia | Diferencia |
|---|---:|---:|---:|
| ALI | 8.485.667 | 8.497.076 | -11.409 |
| PJ | 7.151.862 | 7.153.786 | -1.924 |
| AR | 1.501.991 | 1.502.732 | -741 |
| UBO | 289.825 | 289.860 | -35 |
| PD | 235.357 | 235.357 | +0 |
| FR | 99.703 | 99.572 | +131 |
| MPN | 89.798 | 89.798 | +0 |
| IU | 150.217 | 150.493 | -276 |
| MPF | 4.559 | 4.562 | -3 |
| PH | 144.590 | 144.712 | -122 |

La base incluye San Luis y Santa Cruz con su total provincial y las imputaciones de abajo. Las diferencias restantes no se reparten entre departamentos.

Filas de métricas repetidas en la base (se toma la primera): 26 departamentos de Córdoba.

Padrón inconsistente (más votantes que inscriptos; gris claro en participación y sin ese dato en la ficha): ullum (San Juan, 3.469 votantes / 2.474 inscriptos).

## Modos y leyenda

Pestañas: GANÓ, ALI, PJ, AR. Sin participación: la base no trae el padrón en todos los departamentos.

Ganadores (unidades, cada provincia sólida cuenta una): Alianza (UCR, FREPASO y aliados) 295; Concertación Justicialista 207; Movimiento Popular Neuquino (Neuquén) 15; Partido Demócrata 4; Acción por la República 2; Unidad Bonaerense 1.

La leyenda lleva solo las fuerzas que ganan alguna unidad; las demás van a «otros» en la torta y siguen en la ficha de cada unidad. Logos y reservas de época en `logos_wikipedia/LICENCIAS.md`.

## Pendientes

- San Luis y Santa Cruz: buscar los resultados por departamento (escrutinio definitivo o prensa provincial).

## Commons

Paquete local en `commons/1999dip/subir/` (sin subir). Ver `commons/1999dip/LEEME_SUBIDA.md`.
