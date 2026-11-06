# Ucronía 1987 — «The Shining Austral Pearl»

Atlas electoral presidencial de Argentina por departamento, en el estilo de Wikipedia 1999, para la
ucronía en la que Argentina gana la guerra de Malvinas. Todos los archivos de este atlas viven en
`deepseek/`; no se modificó ningún archivo existente del repositorio.

- **Escenario**: elección presidencial de 1987, Colegio Electoral de 600 miembros.
- **Fuente de los totales**: `deepseek/Argentina 1987.xlsx`, aportado por el usuario.
- **Reparto departamental**: estimación, no voto observado (ver «Método»).
- **Generador**: `python deepseek/build_deepseek.py`.
- **Salidas**: `deepseek/atlas_1987_ucronia.html` y `deepseek/dataset_1987_ucronia.json`.
- **Capturas**: `deepseek/img/m_gan.png`, `m_mon.png`, `m_ucr.png`, `m_pj.png`, `m_pds.png`.

## Resultado nacional

| Fuerza | Candidatos | Votos | % | Electores |
|---|---|---:|---:|---:|
| MON — Movimiento de Opinión Nacional | Frúgoli / Ubieto | 5.391.282 | 31,59 | 212 |
| UCR — Unión Cívica Radical | Pugliese / López | 5.369.706 | 31,46 | 185 |
| PJ — Partido Justicialista | Matera / Bárbaro | 4.940.601 | 28,95 | 183 |
| PDS — Partido por la Democracia Social | Fracassi / Lezama | 899.078 | 5,27 | 20 |
| PI — Partido Intransigente | Alende / Viale | 189.085 | 1,11 | 0 |
| MID — Movimiento de Integración y Desarrollo | Frigerio / Salonia | 182.660 | 1,07 | 0 |
| Otros | — | 95.649 | 0,56 | 0 |
| **Total** | | **17.068.061** | **100,00** | **600** |

Los porcentajes se calculan sobre votos positivos. El xlsx no trae inscriptos, blancos ni nulos, así que
el atlas no muestra participación ni anillo de participación.

**Colegio Electoral**: se necesitan 301 votos. MON ganó el voto popular y obtuvo 212 electores, pero
ninguna fuerza alcanzó la mayoría: UCR 185, PJ 183 y PDS 20. El Colegio no eligió presidente en la
primera votación; el atlas muestra el resultado de la elección popular y del colegio, no una segunda
votación.

### Una diferencia con la imagen de la ucronía

La imagen del escenario dice **5.291.282** votos para MON; el xlsx dice **5.391.282**. Se usa el xlsx
(la fuente que aportó el usuario para este trabajo) y la diferencia de 100.000 votos queda anotada en
la nota del atlas. No se ajustó ninguna otra cifra.

## La fuente provincial

`Argentina 1987.xlsx`, hoja `1987`, filas 3 a 26: 24 provincias (incluida Tierra del Fuego), con tres
columnas por fuerza —votos, electores y un tercer campo— y el total provincial. El generador lee las
columnas 1/4/7/10/13/16/19 (votos) y 3/6/9/12/15/18/21 (electores), y verifica que la suma de las
siete fuerzas sea exactamente el total de la fila.

Los electores del xlsx **no son estrictamente proporcionales** a los votos provinciales. Ejemplo:
Chubut, PJ 32,12 % y 6 electores contra UCR 38,64 % y 5; Santa Fe reparte 14/14/12 entre MON, UCR y
PJ. Se muestran tal como vienen y se usan para el total del Colegio y para la nota de cada provincia;
no se usan para pintar departamentos (el color sale del voto popular estimado).

## Método del reparto departamental

El xlsx solo tiene totales provinciales. Para bajar el resultado a los departamentos se usó un perfil
local y un ajuste de márgenes; **no son votos observados por departamento**.

1. **Base**: `datos/base8399/ernesto/1987_diputados/dpto_partidos.csv`, la base de diputados de 1987
   por departamento (la misma que usa el atlas `mapas/mapa1987/`). Se suman los códigos de partido en
   los bloques del escenario (ver «Bloques»).
2. **Correcciones y fusiones**: se repiten las correcciones documentadas en `mapas/mapa1987/LEEME_1987.md`
   —imputaciones de residuos, La Plata 1987 con 99.984 votos extra— y se fusionan Islas del Ibicuy en
   Gualeguaychú, Palpalá en Capital (Jujuy) y Tres Lomas en Pellegrini, porque la geometría de 1980 no
   los separa. No se tocó el build de 1987; las correcciones se repiten en `build_deepseek.py`.
3. **Perfil por fuerza**: para cada provincia se calcula la proporción departamental de cada bloque en
   la base de 1987. Las fuerzas con menos del 3 % de la provincia usan `0,30 × perfil propio + 0,70 ×
   perfil uniforme`; así un pico local aislado (el MID de Andalgalá) no inventa una victoria
   departamental. Las fuerzas grandes usan `0,85 × propio + 0,15 × uniforme`.
4. **PDS**: el Partido por la Democracia Social no tiene lista propia en la base de 1987. El único
   código `pds` de la base es Formosa 1983 (257 votos), demasiado chico y de otro año para servir de
   perfil. Por eso se le asigna **una proporción uniforme dentro de cada provincia**: su porcentaje
   provincial sale del xlsx, pero no se le inventa un patrón geográfico. En consecuencia no gana
   ningún departamento; conserva sus 20 electores.
5. **Totales por unidad**: los positivos de 1987 de cada departamento se escalan al total provincial
   del xlsx con el método del mayor resto.
6. **IPF**: se ajusta la matriz departamentos × fuerzas a los márgenes de fila (total de cada
   departamento) y de columna (total de cada fuerza en la provincia) con iteración proporcional.
   El PDS se excluye del ajuste y se asigna antes, para que su proporción quede plana; las demás
   fuerzas se ajustan a los totales que deja el PDS.
7. **Redondeo controlado**: cada celda se lleva a `floor` o `ceil` resolviendo un problema de
   transporte (scipy `linprog`) para que las filas y las columnas sumen exactamente. No hay residuos
   ni votos imputados a mano.
8. **Tierra del Fuego y Malvinas**: la base de 1987 no incluye Tierra del Fuego. Se usa el perfil de
   Río Grande y Ushuaia del presidential de 1989 (`1989_presidente/dpto_partidos.csv`), escalado al
   total provincial del xlsx, con el mismo tratamiento uniforme del PDS. El atlas de 1987 ya usaba esa
   base para el territorio. **Las Malvinas votaron en la ucronía**: se agregan como tercera unidad de
   Tierra del Fuego con un **5 % estimado** del total provincial (656 votos) y el perfil promedio
   provincial; el resto se reparte entre Río Grande y Ushuaia. No se suman votos fuera del total
   provincial del xlsx.
9. **Controles**: el build verifica que cada provincia cierre al total del xlsx y que cada fuerza
   cierre al total provincial; además imprime ganadores por unidad y por provincia.

### Bloques

| Bloque | Códigos de la base de 1987 |
|---|---|
| PJ | `pj`, `fjren`, `fjpart`, `fj`, `fje`, `frejuli`, `fpv` |
| UCR | `ucr`, `ucrde`, `ucrcon`, `ucrvp` |
| MON | `ucd`, `ucddpuc`, `ucddem`, `ducd`, `apce`, `ucdmpp`, `adc`, `ucdsr`, `ucddp`, `mpn`, `ablo`, `pd`, `prs`, `pri`, `ach`, `paldpml`, `dpbb`, `pca`, `cp`, `fed`, `auton`, `tyc`, `mrf`, `alpa`, `ays`, `mur` |
| PI | `pi` |
| MID | `mid`, `midcr` |
| PDS | sin código en 1987 (uniforme por provincia) |
| Otros | todo lo demás |

La asignación de MON es interpretativa: la ucronía agrupa en el Movimiento de Opinión Nacional a la
UCeDé y aliados con los partidos provinciales conservadores o de gobierno (PDP de Mendoza, MPN,
Bloquista, PRS, PAL de Corrientes, Acción Chubutense, etc.). No es una lista única de la base de 1987.

## Mapa, colores y logos

- **Unidades**: 526 — departamentos de 1980 y las 28 circunscripciones de Capital Federal, con la
  geometría de `mapas/mapa1987/units_raw.pkl` (proyección y contornos del atlas de 1987).
- **Provincias**: 24. **Islas Malvinas** se pinta con MON: en la ucronía votó y se le asigna un 5 %
  estimado del total de Tierra del Fuego (656 votos), documentado en la ficha y en la nota.
- **Recuadros**: los siete del estilo 1999 —Tucumán, Gran San Juan, Gran Mendoza, Resistencia +
  Corrientes capital, Área Metropolitana de Buenos Aires, Antártida Argentina y Capital Federal—.
  La Antártida se pinta con el color de la provincia de Tierra del Fuego, como en el atlas de 1987;
  no tiene votos propios.
- **Modos**: `GANÓ` y una coropleta por fuerza (`MON`, `UCR`, `PJ`, `PDS`). No hay modo de
  participación porque el xlsx no trae inscriptos, blancos ni nulos.
- **Leyenda**: solo MON, UCR y PJ, que son las fuerzas que ganan al menos una unidad (regla 3 del
  proyecto). PDS, PI, MID y Otros van juntos en la torta como «Otros» (1.366.472 votos, 8,00 %) y
  siguen discriminados en la ficha de cada unidad y en la nota. El PDS tiene fila propia en las
  métricas nacionales por sus 20 electores.

Colores:

| Fuerza | Color | Logo |
|---|---|---|
| MON | `#00838f` (verde azulado) | `deepseek/logos/Logo_Mon.svg` (aportado por el usuario) |
| UCR | `#e10019` (rojo) | `logos/Escudo_de_la_UCR.svg` |
| PJ | `#318ce7` (azul) | `logos/Flag_of_the_Justicialist_Party_(square_version).svg` |
| PDS | `#2e7d32` (verde) | sigla `PDS` |
| PI | `#d10047` (magenta) | `logos/Emblema_Partido_Intransigente.svg` |
| MID | `#0f2b3d` (azul petróleo) | `logos/Logo_MID.svg` |
| Otros | `#9a9a9a` (gris) | — |

El logo de MON se copió a `deepseek/logos/Logo_Mon.svg` para no depender de una ruta externa. Es el
archivo que aportó el usuario; su procedencia y licencia no están documentadas en el repositorio, así
que este atlas es de uso local y **no se preparó para Commons**. Los logos de UCR, PJ, PI y MID son
los de época ya usados por los atlas del proyecto; PDS no tiene logo de época y lleva sigla.

## Ganadores

- **Por unidad**: MON 214, UCR 179, PJ 133 (526 unidades en total). La victoria 214 de MON es
  Malvinas, estimada.
- **Por provincia**: MON 13, UCR 5, PJ 6.

Provincias ganadas: MON en Catamarca, Corrientes, Entre Ríos, Formosa, Jujuy, La Pampa, Mendoza,
Neuquén, Salta, San Juan, San Luis, Santa Fe y Tierra del Fuego; UCR en Buenos Aires, Capital
Federal, Chubut, Córdoba y Río Negro; PJ en Chaco, La Rioja, Misiones, Santa Cruz, Santiago del Estero
y Tucumán.

## Totales provinciales usados

| Provincia | MON | UCR | PJ | PDS | PI + MID + otros | Total | Electores |
|---|---:|---:|---:|---:|---:|---:|---|
| Buenos Aires | 1.722.118 | 1.909.446 | 1.781.399 | 368.136 | 147.918 | 5.929.017 | 144 |
| Capital Federal | 616.054 | 729.158 | 497.620 | 43.623 | 85.624 | 1.972.079 | 54 |
| Catamarca | 46.030 | 31.531 | 28.526 | 6.540 | 5.641 | 118.268 | 14 |
| Chaco | 114.537 | 111.857 | 142.958 | 17.540 | 19.123 | 406.015 | 18 |
| Chubut | 34.825 | 52.729 | 43.832 | 1.651 | 3.425 | 136.462 | 14 |
| Córdoba | 319.490 | 696.162 | 399.514 | 79.267 | 18.304 | 1.512.737 | 40 |
| Corrientes | 216.137 | 98.706 | 46.603 | 12.343 | 10.728 | 384.517 | 18 |
| Entre Ríos | 214.535 | 112.707 | 152.769 | 27.248 | 15.742 | 523.001 | 22 |
| Formosa | 66.609 | 30.702 | 39.297 | 6.748 | 9.313 | 152.669 | 14 |
| Jujuy | 94.241 | 29.407 | 57.889 | 14.331 | 5.415 | 201.283 | 16 |
| La Pampa | 76.132 | 13.466 | 40.841 | 4.913 | 3.045 | 138.397 | 14 |
| La Rioja | 20.999 | 22.202 | 58.196 | 0 | 2.302 | 103.699 | 14 |
| Mendoza | 366.888 | 94.867 | 187.344 | 28.249 | 25.368 | 702.716 | 24 |
| Misiones | 76.052 | 89.387 | 98.210 | 18.955 | 8.560 | 291.164 | 18 |
| Neuquén | 81.398 | 20.593 | 24.048 | 4.755 | 4.688 | 135.482 | 14 |
| Río Negro | 106.525 | 190.938 | 120.118 | 23.199 | 12.325 | 453.105 | 14 |
| Salta | 141.556 | 98.899 | 84.587 | 15.594 | 6.521 | 347.157 | 18 |
| San Juan | 123.494 | 63.706 | 51.873 | 12.427 | 6.317 | 257.817 | 16 |
| San Luis | 60.681 | 35.270 | 25.957 | 8.661 | 2.475 | 133.044 | 14 |
| Santa Cruz | 7.586 | 20.624 | 29.105 | 1.940 | 1.217 | 60.472 | 14 |
| Santa Fe | 497.789 | 483.369 | 413.571 | 102.933 | 36.356 | 1.534.018 | 42 |
| Santiago del Estero | 123.320 | 131.246 | 252.107 | 27.550 | 12.409 | 546.632 | 18 |
| Tierra del Fuego | 6.328 | 3.153 | 1.918 | 1.209 | 518 | 13.126 | 4 |
| Tucumán | 257.958 | 299.581 | 362.319 | 71.266 | 24.060 | 1.015.184 | 22 |

Malvinas no tiene fila propia porque su total está dentro de Tierra del Fuego. El reparto estimado de
sus 656 votos es: MON 301, UCR 169, PJ 104, PDS 61, PI 6, MID 11 y otros 4.

La Rioja tiene 0 votos de PDS en el xlsx; por eso su departamento no se pinta en el modo PDS (queda en
el tono más claro, 0 %). Los electores por fuerza de cada provincia están en la ficha provincial.

## Advertencias

- **Es una estimación**, no un escrutinio por departamento. El xlsx solo tiene totales provinciales;
  la geografía departamental es un prior de 1987 y el PDS es una asignación uniforme.
- **El PDS no tiene datos locales**. Su reparto plano dentro de cada provincia es una decisión de
  método, no un resultado observado. Cualquier lectura geográfica del PDS en este atlas es un
  artefacto del supuesto, no información.
- **Los electores del xlsx no cierran con los votos** en varios distritos (Chubut, Santa Fe). Se
  respetan; no se recalcularon.
- **La imagen de la ucronía y el xlsx difieren en 100.000 votos de MON**. Se usa el xlsx y se anota.
- **La base de 1987 tiene correcciones**: imputaciones de residuos y La Plata con 99.984 votos extra,
  repetidas desde `mapas/mapa1987/LEEME_1987.md`. No se modificó aquel atlas.
- **No hay participación**: el xlsx no trae inscriptos, blancos ni nulos. Tampoco se inventaron.
- **Malvinas** es una estimación dentro de Tierra del Fuego: 656 votos (5 % del total provincial),
  perfil promedio provincial, sin votos adicionales. La Antártida del recuadro se colorea con Tierra
  del Fuego, sin votos propios.
- **Sin publicación**: no se agregó al catálogo de Pages, no se generó paquete de Commons y no se
  commiteó nada. El logo de MON es un archivo aportado por el usuario y no tiene licencia documentada.

## Cómo regenerar

```
python deepseek/build_deepseek.py
python deepseek/validar.py
```

`validar.py` vuelve a leer el xlsx y el dataset y comprueba provincias, fuerzas, electores, unidades
ganadas, la torta y que no queden unidades sin dato; no escribe archivos.

Requiere `openpyxl`, `numpy`, `scipy`, `shapely`, `resvg_py` y `Pillow` (los mismos que usan los
constructores del proyecto). El build lee la plantilla y la geometría del repositorio, escribe el HTML
y el dataset en `deepseek/`, y aplica `comun/logos_al_ras.py` solo al HTML generado. No escribe en
`mapas/`, `comun/` ni `sitio/`.

Para volver a tomar las capturas:

```
msedge.exe --headless=new --hide-scrollbars --window-size=1920,1700 --virtual-time-budget=8000 \
  --screenshot=deepseek/img/m_gan.png \
  "file:///.../deepseek/atlas_1987_ucronia.html#bare-white-m-gan"
```

(el hash `#bare-white-m-<modo>` fuerza el fondo blanco; sin él, el visor usa el tema del navegador).
