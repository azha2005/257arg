# Atlas legislativo de 1995 (diputados nacionales)

Atlas de las elecciones de diputados nacionales del 14 de mayo de 1995, por departamento. Es independiente del atlas presidencial del mismo año. 537 de 538 unidades con votos de la base; las Islas Malvinas en gris.

## Reproducir

```
python mapa1995dip/build_1995dip.py
python render_transparentes.py mapa1995dip
python render_blanco.py mapa1995dip atlas_1995_diputados.html
python commons/paquete.py 1995dip
python tools/documentar_leg8399.py
```

## Fuentes

- Votos por departamento: base de Ernesto Calvo, `base8399/ernesto/1995_diputados/dpto_partidos.csv` (hojas de `TPDENP1995T.xls`).
- Resultado nacional del cartel (torta, barras, métricas): tabla del artículo [Elecciones legislativas de Argentina de 1995](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1995), clave `1995_diputados` de `wikitop.py`.
- Copias del artículo en esta carpeta: `w1995.txt`, `wiki.html`, `wiki_rows.json` (tabla nacional) y `wiki_prov_listas.json` (tablas provinciales).
- Geometría: departamentos de 1991 con los partidos nuevos con polígono propio (`mapa1995/units_raw.pkl`).
- Constructor: `atlas_leg8399.py` (compartido con los otros tres años). `FAMS[1995]` asigna cada código de la base a un bloque de la tabla nacional; `bloc()` tiene las excepciones por provincia.

## Decisiones

- En Tucumán el código fr de la base es el FREPASO y frep es Fuerza Republicana; en Jujuy fr es Fuerza Republicana agrupada con el MODIN. El Partido Federal va con la UCR en Córdoba y con el PJ en los demás distritos, como la tabla nacional.
- Córdoba: la base no trae la columna del Partido Federal; el residuo de cada departamento entre positivos declarados y suma de las fuerzas (14.914 votos en total, la Wikipedia da 14.915) se imputa a la UCR, con nota en la ficha. San Juan trae la fila de positivos repetida: se toma la primera, que coincide con la suma de las fuerzas.
- Deseado (Santa Cruz): la base trae un registro incompleto; por pedido del usuario se calcula como el total provincial de la Wikipedia menos los otros seis departamentos, fuerza por fuerza y para blancos, nulos, votantes e inscriptos (original y cálculo en `mapa1995dip/deseado_extrapolado.json`). No es un resultado departamental observado.
- Los partidos creados después del censo de 1991 tienen su propio polígono, tomado del shapefile de 2001 y recortado al contorno de 1991. El Sector Antártico de la base se suma a Ushuaia.
- Logos reutilizados del proyecto; en varios emblemas provinciales el diseño de época no está verificado (ver `logos_wikipedia/LICENCIAS.md`).

## Bloques: base contra Wikipedia

| Bloque | Base | Wikipedia | Diferencia |
|---|---:|---:|---:|
| PJ | 8.369.164 | 8.371.132 | -1.968 |
| UCR | 3.718.797 | 3.718.920 | -123 |
| FREP | 3.598.791 | 3.599.764 | -973 |
| MOD | 311.891 | 311.987 | -96 |
| PDP | 158.786 | 158.857 | -71 |
| PAL | 158.271 | 158.269 | +2 |
| FR | 119.546 | 119.546 | +0 |
| PD | 114.581 | 114.581 | +0 |
| MPN | 60.781 | 60.781 | +0 |
| SUR | 84.218 | 83.434 | +784 |
| MPF | 7.672 | 7.683 | -11 |

La base incluye las imputaciones de abajo. Las diferencias restantes no se reparten entre departamentos.

## Imputaciones

| Provincia | Departamento | Bloque | Votos |
|---|---|---|---:|
| Córdoba | Calamuchita | UCR | 172 |
| Córdoba | Capital | UCR | 5.198 |
| Córdoba | Colon | UCR | 691 |
| Córdoba | Cruz del Eje | UCR | 282 |
| Córdoba | General Roca | UCR | 270 |
| Córdoba | General San Martin | UCR | 805 |
| Córdoba | Ischilin | UCR | 199 |
| Córdoba | Juarez Celman | UCR | 409 |
| Córdoba | Marcos Juarez | UCR | 899 |
| Córdoba | Minas | UCR | 4 |
| Córdoba | Pocho | UCR | 23 |
| Córdoba | Punilla | UCR | 692 |
| Córdoba | Rio Cuarto | UCR | 1.236 |
| Córdoba | Rio Primero | UCR | 152 |
| Córdoba | Rio Seco | UCR | 23 |
| Córdoba | Rio Segundo | UCR | 378 |
| Córdoba | Roque Saenz Peña | UCR | 188 |
| Córdoba | San Alberto | UCR | 60 |
| Córdoba | San Javier | UCR | 139 |
| Córdoba | San Justo | UCR | 1.215 |
| Córdoba | Santa Maria | UCR | 363 |
| Córdoba | Sobremonte | UCR | 4 |
| Córdoba | Tercero Arriba | UCR | 776 |
| Córdoba | Totoral | UCR | 30 |
| Córdoba | Tulumba | UCR | 11 |
| Córdoba | Union | UCR | 695 |

## Positivos declarados distintos de la suma de las fuerzas

Los porcentajes se calculan sobre la suma de las fuerzas; el valor declarado queda en la ficha.

| Provincia | Departamento | Declarados | Suma |
|---|---|---:|---:|
| Buenos Aires | Capitan Sarmiento | 650 | 6.314 |
| La Pampa | Rancul | 5.496 | 5.497 |

Filas de métricas repetidas en la base (se toma la primera): 19 departamentos de San Juan.

Padrón inconsistente (más votantes que inscriptos; gris claro en participación y sin ese dato en la ficha): Baradero (Buenos Aires, 25.521 votantes / 20.193 inscriptos), Diamante (Entre Ríos, 25.099 votantes / 14.920 inscriptos).

## Modos y leyenda

Pestañas: GANÓ, PJ, UCR, FREP, PART.

Ganadores (unidades): Partido Justicialista 465; Unión Cívica Radical 34; Pacto Autonomista (Liberal · Corrientes) 20; Frente País Solidario (FREPASO) 9; Movimiento Popular Neuquino (Neuquén) 9.

La leyenda lleva solo las fuerzas que ganan alguna unidad; las demás van a «otros» en la torta y siguen en la ficha de cada unidad. Logos y reservas de época en `logos_wikipedia/LICENCIAS.md`.

## Pendientes

- Deseado (Santa Cruz) es un cálculo, no un dato observado: reemplazarlo si aparece el registro departamental.

## Commons

Paquete local en `commons/1995dip/subir/` (sin subir). Ver `commons/1995dip/LEEME_SUBIDA.md`.
