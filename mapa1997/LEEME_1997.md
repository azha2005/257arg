# Elecciones legislativas del 26 de octubre de 1997 (diputados nacionales)

`atlas_1997.html` (`python build_1997.py`; generado desde `mapa1993/build_1993.py`). Departamentos del censo de 1991 + 28 circunscripciones de Capital. Modos: ganador, Alianza, PJ, AR.

## Datos
- Base de Ernesto Calvo: `base8399/ernesto/1997_diputados/dpto_partidos.csv` (23 provincias, 528 unidades). **San Luis no tiene diputados nacionales en la base** (su hoja de observaciones dice «Faltan Datos DN»): se pinta entera, en color sólido (`DATA.solid`), con el total provincial de la tabla de Wikipedia (Frente Justicialista 77.389, Alianza 59.655, PDL 6.013, Acción Cívica 5.521, Frente Solidario 3.582; `SAN_LUIS` en el build).
- La columna de positivos viene como «agrupación» con código `pos19` (`pos` en Corrientes, La Pampa y Santiago del Estero); el build la toma como positivos. Con eso la suma de las listas cierra con los positivos en las 528 unidades.
- Nacional: tabla de «Elecciones legislativas de Argentina de 1997» (`w1997.txt`, `../wikitop.py`). Los bloques son los «Total» de la tabla: Alianza (UCR + FREPASO + aliados, **sumados aunque en 13 distritos fueran separados**), PJ y aliados, Acción por la República y aliados; más FR, PD, Partido Nuevo, PDJ (San Juan) y MPN, que ganan alguna unidad.
- Base vs. tabla (San Luis ya incluido con su total provincial): Alianza 8.091.618 vs 8.097.301 (−5.683, −0,07 %); PJ 6.272.859 vs 6.274.385 (−1.526); AR 661.935 vs 662.403 (−468); FR 247.109 vs 247.129; PN 223.660 vs 223.668; PD, PDJ y MPN coinciden. Positivos: base 17.094.103 + San Luis 152.160 = 17.246.263 vs 17.251.484 de la tabla.

## Geometría: partidos nuevos con polígono propio
Pedido del usuario (15-oct-2026): **no fusionar** los partidos creados después de 1991 con el partido de origen, sino tomar su polígono de un shapefile posterior. `../newpartidos.py` toma de `Departamentos_2001` Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas y 2 de Abril (Chaco), recortados a la unión de los polígonos de 1991 del grupo (así el contorno exterior no cambia) y reparte las rendijas entre vecinos. San Salvador (Entre Ríos) es posterior a 1997: acá sigue dentro de Concordia (la base de 1997 lo trae así). 538 unidades.
El resto de los builds (1993, 1994, 1995…) todavía fusionan esos partidos; pasarlos a `newpartidos` es trabajo pendiente.

## Colores y logos
Colores de la Wikipedia (pedido del usuario): Alianza #DC0143, PJ #318CE7, AR #3E5298, PD #1F2F6B, PN #FF8800, PDJ #00FFFF. Excepción: FR lleva el marrón del proyecto #7B3F00 (el azul #0070B8 de la Wikipedia se confunde con el PJ y el MPN), igual que en 1991–1995; el MPN, el azul marino del proyecto. Logos: Alianza y AR (Commons, fecha 1997), PJ (bandera cuadrada), PD, FR, MPN; el Partido Nuevo es el único de Commons y figura de 2018 (no verificado); PDJ lleva sigla. Ver `logos_wikipedia/LICENCIAS.md`.

## Pendientes
- No se comparó con el mapa por provincia de es.wikipedia (`Elecciones legislativas 1997 - Argentina.png`), que separa el FREPASO de Neuquén.
- Paquete de Commons en `commons/1997/` (sin subir).
