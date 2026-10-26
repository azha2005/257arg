# Elecciones legislativas del 27 de octubre de 2013 (diputados nacionales)

`atlas_2013.html` (`python build_2013.py`). Departamentos del censo de 2010 (con las 15 comunas de Capital Federal) + el partido de Lezama escindido de Chascomús. Modos: ganador (`gan`), Frente para la Victoria (`fpv`), Frente Progresista Cívico y Social (`fpcys`), Frente Renovador (`fr`), Propuesta Republicana (`pro`) y participación (`par`).

## Datos
- **Base por departamento y comuna:** escrutinio provisorio por mesa de la DINE (`datos_oficiales/2013/`: `mesas_2013.csv`, `votos_partidos_2013.csv`, `votos_no_positivos_2013.csv`, `codigos_2013.json`), preagregado en `datos_oficiales/agregado_dine.pkl` (`agregar_dine.py`) y `datos_oficiales/2013/mesas_depto.pkl` (mesas computadas y electores por sección). 526 unidades (511 departamentos/partidos + 15 comunas de CABA).
- **Dos departamentos sin mesas escrutadas en el provisorio (`0 mesas`):** **Ramón Lista** (Formosa, 0 de 26 mesas; 5.016 electores) y **Valle Grande** (Jujuy, 0 de 11 mesas; 2.008 electores). Quedan en beige (`#e6dcc3`) con clave en la leyenda y nota en su tarjeta. En las unidades con escrutinio parcial, la participación se calcula sobre los electores de las mesas computadas (`el_ok`) y la tarjeta informa cuántas mesas y electores entraron.
- **Resultado nacional (torta, barras, métricas):** tabla del escrutinio definitivo en «Elecciones legislativas de Argentina de 2013» (`wikileg/wleg2013.txt`, cargado en `../wikitop.py`).

## Bloques (provisorio DINE vs. definitivo de Wikipedia)
Las listas se agrupan en los bloques de la tabla nacional de Wikipedia mediante `wikileg/bloques_leg.py` y `wikileg/overrides.py`. Quedan en la leyenda los **15 bloques** que ganan al menos una unidad:

| Bloque | Nombre en leyenda | DINE (provisorio) | Wikipedia (definitivo) | Dif. % | Unidades ganadas |
|---|---|---:|---:|---:|---:|
| `FPV` | Frente para la Victoria (PJ, F. Cívico por Santiago y aliados) | 7.325.289 | 7.425.261 | −1,35 % | 211 |
| `FPCyS` | Frente Progresista Cívico y Social (UCR, PS, CC-ARI, UNEN y aliados) | 5.582.090 | 5.510.949 | +1,29 % | 96 |
| `FR` | Frente Renovador (Frente Renovador y aliados) | 4.053.822 | 4.087.402 | −0,82 % | 106 |
| `PRO` | Propuesta Republicana (Unión PRO y aliados) | 1.961.709 | 1.974.049 | −0,63 % | 16 |
| `FIT` | Frente de Izquierda (PO, PTS e Izquierda Socialista) | 1.211.743 | 1.211.252 | +0,04 % | 1 |
| `UxC` | Unión por Córdoba (Córdoba) | 530.714 | 532.702 | −0,37 % | 17 |
| `FRC` | Frente Renovador de la Concordia (Misiones) | 259.044 | 260.034 | −0,38 % | 16 |
| `CF` | Compromiso Federal (San Luis y aliados) | 256.754 | 259.195 | −0,94 % | 9 |
| `PACh` | Partido Acción Chubutense (Chubut) | 152.736 | 153.395 | −0,43 % | 14 |
| `FE` | Partido Fe (Unión con Fe · Buenos Aires) | 151.403 | 149.169 | +1,50 % | 1 |
| `MPN` | Movimiento Popular Neuquino (Neuquén) | 133.903 | 133.952 | −0,04 % | 16 |
| `SST` | Salta Somos Todos (Salta) | 112.580 | 113.404 | −0,73 % | 4 |
| `PJ` | Partido Justicialista (La Pampa, Santa Cruz y T. del Fuego) | 105.355 | 105.412 | −0,05 % | 15 |
| `PARES` | Partido Renovador de Salta (Salta) | 37.406 | 37.649 | −0,65 % | 1 |
| `MIJD` | Mov. Indep. de Justicia y Dignidad (Salta) | 23.455 | 23.470 | −0,06 % | 1 |

- **Diferencia en `FPCyS` (+1,29 %):** el subtotal impreso en la tabla nacional de Wikipedia (5.510.949) tiene dos omisiones respecto de sus propias tablas provinciales: no suma el Frente Amplio Progresista de Entre Ríos (45.026 votos en el definitivo; 128.431 en el provisorio de la DINE) y en Capital Federal suma los votos de UNEN a senadores (509.446) en lugar de diputados (589.545). En el mapa se incluye el FAP de Entre Ríos dentro de `FPCyS` como corresponde a la alianza nacional.
- **Unidades únicas:** el `FIT` gana en Salta Capital (mediante el Partido Obrero, 29,21 %); el `Partido Fe` gana en Necochea (35,05 %); el `PARES` gana en Metán (24,52 %); el `MIJD` gana en Guachipas (35,66 %); `Salta Somos Todos` gana en Cerrillos, Chicoana, Rosario de la Frontera y Rosario de Lerma.

## Geometría
- Base: `Base deptos 1869-2022/Departamentos_2010.shp` (Rodríguez, CONICET), que ya trae las **15 comunas de Capital Federal** (en lugar de las 28 circunscripciones históricas) y los partidos creados hasta 2010.
- **Lezama (Buenos Aires):** creado por ley provincial en diciembre de 2009, vota separado de Chascomús en 2013 (`seccion_id=135` en la DINE), pero todavía figura unido a Chascomús en `Departamentos_2010.shp`. En `geom.py` (`_split_lezama`) se toma el polígono de Lezama de `Departamentos_2022_INDEC.shp`, se recorta al contorno de Chascomús de 2010 y se resta de este.

## Colores y logos
- **Ajuste del 16-oct-2026 (regla 4, colores bien distintos):** `CF` pasó a verde `#43a047` (la menta se confundía con `UxC`), `PACh` a frambuesa `#c2185b` (era azul marino, igual que `FRC`), `FE` a marrón `#8d5524` (azul parecido a `PJ`/`FPV`), `SST` a rosa `#ff69b4` (dorado igual que `PRO`) y `PARES` a violeta `#8e44ad` (azul igual que `PJ`). La leyenda arranca en y=1022 (antes 994) para no pisar el mini «Provincias». Los colores de abajo son los de la tabla de Wikipedia, salvo estos cinco.
- Colores de la tabla de Wikipedia: `FPV` `#4F97D1`, `FPCyS` `#FF8800`, `FR` `#1B2936`, `PRO` `#FFD700`, `FIT` `#DF013A`, `UxC` `#0093AF`, `FRC` `#1F469C`, `CF` `#00A550`, `PACh` `#00598C` (ajustado desde `#0087D1` para diferenciarlo de `PJ` y `FE`), `FE` `#1268B3`, `MPN` `#00708B`, `SST` `#B59410`, `PJ` `#318CE7`, `PARES` `#0087D1`, `MIJD` `#9DC209`.
- Con 15 bloques ganadores más la fila de clave beige, la leyenda se compactó a `h=23` (`step=25,5`, arranque en `y=994`) y 6 pestañas arriba a la derecha.
- Logos: todos de Commons (ver `logos_wikipedia/LICENCIAS.md`); `Salta Somos Todos` y `MIJD` llevan sigla.

## Salidas y paquete de Commons
- PNG transparentes en `png_transparentes/mapa2013/` y fondo blanco en `png_blanco/mapa2013/` y `png_transparentes/all elections white bg/`.
- Paquete de Commons en `commons/2013/` (`python commons/paquete.py 2013` y `python commons/chequeo.py 2013`).
