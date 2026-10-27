# Transferencias de voto entre legislativas (diputados nacionales)

**Actualización territorial, 26-oct-2026:** [revisión con Cacopardo de los cruces existentes y de los mapas 1912/1914/1916](revision_cacopardo_1967/LEEME.md). Se corrigieron Escobar, Hipólito Yrigoyen y San Cayetano en 1954d→1965d y 1958d→1962d. Las nuevas versiones usan 374 y 349 unidades; los conteos y resultados anteriores que aparecen más abajo corresponden al cálculo previo, conservado como respaldo. El nuevo [1914d→1916d](fuentes_1914_1916/LEEME.md) tiene cobertura parcial y solo cifras observadas en su principal.

Pares hechos: **presidente 2023 (PASO, general y balotaje) → diputados 2025**, **2009 → 2011**, **2011 → 2023**, **2013 → 2025**, **2019 → 2023** (diputados y **presidente**), **presidente 2011 → 2023**, **balotaje 2023** (desde la primera vuelta 2023, desde 2019 y desde 2011), **2019 → 2025**, **2021 → 2025**, **2023 → 2025**, **presidente 2003 → diputados 2005**, **presidente 2003 → 2007**, **presidente 2003 → diputados 2009**, **2009 → 2013**, **presidente 2011 → 2015** y **balotaje 2015** (desde la 1.ª vuelta 2015 y desde 2011), **diputados 1954 → presidente 1958**, **presidente 1958 → diputados 1962**, **diputados 1954 → 1965** y **diputados 1930, presidente 1937 y diputados 1940 → presidente 1946** (por departamento, con Cantón); **Córdoba presidente 1999 → 2003 y diputados 1991 → 1995** por circuito (base de E. Calvo); **presidente 1999 → 2003 nacional** como Calvo y Escolar (por departamento, Córdoba por circuito, votos emitidos). Para otro par: `agregar_circuitos.py <año>` y la entrada del año en `CAT` de `estimar.py` (con su color en `sankey.py`).

Inferencia ecológica RxC a nivel **circuito electoral** con el método de Ernesto Calvo: mínimos cuadrados penalizados sobre un logit multinomial. Es un port a Python del «Código Transferencias PASO-General para R-2019», que estaba en Descargas.

```
python transferencias/agregar_circuitos.py 2021 2023 2025   # una vez: circ_<año>.pkl desde los provisorios por mesa de la DINE
python transferencias/estimar.py 2021 2025                   # matrices, bootstrap y controles en 2021_2025/
python transferencias/estimar.py 2023 2025
python transferencias/sankey.py 2021 2025                    # sankey_<o>_<d>.svg (nacional) y .html (selector nacional / provincia, de por_provincia.csv; al pasar el mouse por una cinta: votos, % del origen y % del destino; agregar #04 a la URL abre Córdoba). PNG con Edge sin cabeza
python transferencias/auditar.py                             # AUDITORIA.md: filas no identificadas y controles por provincia
```

## Diputados 2013 → 2017 (26-oct-2026)

Resultados en `2013_2017/`: matrices nacional y provincial, variante Calvo, intervalos bootstrap (200 remuestreos), controles y Sankey SVG/HTML/PNG.

- Fuentes locales: `circ_2013.pkl` y `circ_2017.pkl`, agregados del provisorio DINE por mesa. Agrupaciones de `LIST2BLOC` de 2013 y `mapa2017/mapeo_listas_2017.csv`; los bloques menores van a Otros.
- **Revisado con correspondencias históricas**: 4.587 circuitos + 6 grupos de circuitos, 29.328.195 de 30.421.290 electores de origen (**96,41 %**). Ninguna provincia se pasa entera a departamento. La versión anterior (3.904 circuitos + 42 departamentos, 96,77 %) está preservada en `2013_2017/anterior_por_departamento/`.
- Equivalencias, documentos y pendientes en [correspondencias_2013_2017/LEEME.md](correspondencias_2013_2017/LEEME.md). Santa Fe conserva circuitos al corregir la sección; se suman las subdivisiones de Viedma, Bariloche, General Roca y Venado Tuerto, y los circuitos afectados de San Luis. **Ushuaia sigue agregada**, porque no hay equivalencia interna verificada; Río Grande y las bases antárticas se mantienen por circuito.
- Penalización elegida por validación cruzada: **2e-7**; separación de filas grandes **43,7 puntos**, sin alertas provinciales por destinos que reciban más del 125 % de su voto real más 2.000 votos.
- **Filas no identificadas**: PRO, FIT y Blanco y nulo. **Frente Renovador: cerca del promedio (†)**; Cambiemos recibe 29,7 / 57,6 % (principal / Calvo). El resultado cambió al recuperar desagregación territorial: no conservar como firmes las cifras de la versión anterior.
- Entre variantes cambian **7.853.395 votos (24,9 % del total modelado)**. Son estimaciones ecológicas a partir de territorios, no observaciones de transferencias individuales; el bootstrap no abarca esta sensibilidad al modelo ni el cambio de padrón.

Reproducir: `python transferencias/estimar.py 2013 2017`, `python -X utf8 transferencias/auditar.py` y `python transferencias/sankey.py 2013 2017`.

## Nuevos cruces con generales y balotajes de 2015 y 2023

`python transferencias/generar_2015_2023.py` calcula ocho pares, con validación cruzada y 200 remuestreos bootstrap: `2015p_2023p`, `2015p_2023b`, `2015b_2023p`, `2015b_2023b`, `2013_2015p`, `2013_2015b`, `2009_2015p` y `2009_2015b`. `p` es general presidencial y `b`, balotaje; 2009 y 2013 son diputados nacionales. Los HTML tienen selector nacional y de los 24 distritos. Cada par incluye matrices, intervalos, controles y `correspondencias.csv`.

Se aplican únicamente las correspondencias documentadas para cada período. En 2015–2023, Santa Fe se cruza con el anexo oficial CNE 66/2022 y las subdivisiones de Cipolletti, Caleta Olivia y Río Gallegos se suman a sus antecesores. **Neuquén queda por departamento; Tierra del Fuego usa una unidad insular común**, sin mezclar la Antártida, por el cambio territorial de Tolhuin y la falta de equivalencias internas verificadas. Para 2009/2013–2015 no se aplican cambios de circuitos posteriores a 2015. Ver [detalle de fuentes y reservas](correspondencias_2013_2017/LEEME.md).

## Datos y categorías
- Votos: escrutinio provisorio por mesa de la DINE (`datos_oficiales/<año>/x/`), cargo diputados nacionales, sumados por circuito. Los electores son los de las mesas con algún voto, porque las mesas no escrutadas no cuentan.
- Bloques: los de la tabla de Wikipedia, tomados de `mapa<año>/mapeo_listas_<año>.csv` (los mismos de los atlas). Las listas sin bloque van a «Otros».
- Categorías:
  - 2021: Frente de Todos, Juntos por el Cambio, Libertarios (Avanza Libertad + LLA), FIT-U, Tercera Vía / PF.
  - 2023: Unión por la Patria, La Libertad Avanza, Juntos por el Cambio, Hacemos, FIT-U.
  - 2025: La Libertad Avanza (con sus alianzas, p. ej. con el PRO), Fuerza Patria, Provincias Unidas, FIT-U.
  - En todos los años: Otros, Blanco y nulo (con recurridos, impugnados y comando) y **No votó** (electores menos votos).
- Emparejamiento: por (distrito, sección, circuito). Se descartan los circuitos cuyo padrón cambia más de −25 % / +33 %. Si los circuitos comunes cubren menos del 90 % del padrón de una provincia, esa provincia se trabaja **por sección (departamento) emparejada por nombre**:
  - **Santa Fe** renumeró todos sus circuitos en 2023 (en 2021→2025 no hay ninguno en común; «Villa Constitución» = «Constitución»).
  - **Santa Cruz** y **Tierra del Fuego** en 2021→2025.
  - Santa Fe también en 2023→2025.
- Cobertura: 2021→2025 usa 32,8 M de 34,0 M electores de 2021; 2023→2025 usa 34,3 M de 34,9 M.

- **Presidente** (`agregar_circuitos.py 2019p 2023p`, `estimar.py 2019p 2023p`, carpeta `2019p_2023p/`): la agrupación se toma por nombre, porque es la misma en todo el país.
  - 2019: Frente de Todos, Juntos por el Cambio, Consenso Federal, FIT-U, y NOS + Unite (Gómez Centurión y Espert juntos).
  - 2023: UxP, LLA, JxC, Hacemos, FIT-U.
  - No hay «Otros», porque en las dos elecciones compitieron solo esas listas.
- **Presidente 2011** (`2011p`): Frente para la Victoria, FAP, UDESO (UCR), Compromiso Federal, Frente Popular, FIT y CC-ARI. No hay «Otros».
- **Balotaje 2023** (`2023b`; carpetas `2023p_2023b/`, `2019p_2023b/` y `2011p_2023b/`): `2023_segundavuelta.zip` de la DINE (provisorio por mesa; datos.gob.ar, «Resultados provisionales Elecciones 2023»), bajado el 26-oct-2026 a `datos_oficiales/2023_balotaje/`. Categorías: Unión por la Patria, La Libertad Avanza, Blanco y nulo y No votó. Comandos: `agregar_circuitos.py 2023b`, `estimar.py 2023p 2023b` y `sankey.py 2023p 2023b`.
- **2003–2007** (PolAr por mesa; `agregar_polar_circuitos.py 2003p 2005 2007p`). **No hay diputados 2003 por mesa** (PolAr trae presidente 2003 y 2007 y diputados desde 2005; el atlas de 2003 usa dat.ar por departamento), por eso el par es **presidente 2003 → diputados 2005**. Además, las legislativas de 2003 fueron en fechas distintas según la provincia. Códigos de lista nacionales en presidente (`listas__listas_presi_gral<año>.csv`).
  - Presidente 2003: Kirchner (FPV), Menem (Frente por la Lealtad), López Murphy (Recrear), Rodríguez Saá (Movimiento Popular), Carrió (ARI); el resto (UCR de Moreau 2,3 %, izquierda) en «Otros».
  - Diputados 2005 (bloques de `mapa2005/mapeo_listas_2005.csv`): Frente para la Victoria, UCR y aliados, Peronismo Federal (incluye a Chiche Duhalde en Buenos Aires), ARI y aliados, PRO, FPCyS (Santa Fe).
  - Presidente 2007: Cristina Kirchner (FPV), Carrió (CC), Lavagna (UNA), Rodríguez Saá (FREJULI).
  - Chaco pasa a sección en los dos pares y La Pampa en 2003 → 2005 (menos del 90 % del padrón en circuitos comunes). Se usan 4.989 y 4.867 circuitos, el 98 % y 97 % del padrón de 2003. Para 2009 se reutiliza `circ_2009.pkl` (ver abajo).
- **Presidente 2015** (`2015p`, zip de generales ya bajado) y **balotaje 2015** (`2015b`): `2015-provisorios_ballotage.zip` de la DINE (argentina.gob.ar/node/29809, «Resultados provisorios»), bajado el 26-oct-2026 a `datos_oficiales/2015_balotaje/`. Primera vuelta: Frente para la Victoria, Cambiemos, UNA (Massa), FIT, Progresistas, Compromiso Federal. Balotaje: Frente para la Victoria, Cambiemos. Comandos: `agregar_circuitos.py 2015p 2015b`, `estimar.py 2011p 2015p`, `2015p 2015b`, `2011p 2015b`.
- 2009: Frente para la Victoria, Acuerdo Cívico y Social (UCR, PS, ARI), PRO / Unión-PRO (con De Narváez y Solá), Peronismo Federal, Proyecto Sur. Los votos salen de **PolAr** por mesa (`agregar_polar_circuitos.py`) y los grupos, de `mapa2009/mapeo_listas_2009.csv` (`grupo_wiki`). PolAr trae casi toda Buenos Aires (el atlas la completó con otra planilla) y solo una parte de Tierra del Fuego. Sus códigos de sección son los de la DINE.
- 2013: Frente para la Victoria, FPCyS / UNEN (UCR, socialismo, CC-ARI y aliados), Frente Renovador, PRO, FIT, Unión por Córdoba. 2013 no tiene `mapeo_listas`: se lee `LIST2BLOC` de `mapa2013/build_2013.py` (la asignación exacta del atlas).
- 2011: Frente para la Victoria, UDESO (UCR), FAP, Frente Popular / PRO (la alianza informal de la tabla), Compromiso Federal, CC-ARI, FIT. 2019: Frente de Todos, Juntos por el Cambio, Consenso Federal, FIT-U.
- El filtro de padrón es **relativo al crecimiento mediano** del par (×1,14 en 2011→2023, ×1,05 en 2019→2025): se descarta el circuito que crece o pierde mucho más que el resto.
- Pasan a sección: 2011→2023: Misiones, Neuquén, San Luis, Santa Cruz, Santa Fe y Tierra del Fuego; 2019→2025: Neuquén, Santa Cruz, Santa Fe y Tierra del Fuego. Ajustes de nombres en `ALIAS`:
  - San Luis: «Pringles» = «Coronel Pringles», etc.
  - Santa Fe: «Nueve de Julio» = «9 de Julio».
  - San Luis 2013: «Gobernador Dupuy» = «Dupuy».
  - Las secciones sin nombre de Santa Fe 2011 y 2013 están en `SECFIX`: la 10 es de La Capital, la 14 y la 15 son de Rosario, deducido por el padrón.
- 2013→2025 pasa a sección en las mismas seis provincias que 2011→2023.
- Cobertura del padrón de origen: 2009→2011 99 % (Santa Fe por sección); 2019→2023 96 %; 2013→2025 87 %; 2011→2023 85 % (en Corrientes, Catamarca, Formosa, La Rioja, Jujuy, Santiago del Estero y Tucumán ~70 %, por circuitos partidos en doce años); 2019→2025 94 %.

- **Perfil de un votante** (`python transferencias/perfil_votante.py` → `perfil_votante.csv`): ordena los circuitos de 2025 por la probabilidad de que un votante al azar vote una secuencia dada (`PERFIL`, 2003–2025 por circuito y Alianza 1997 por departamento), sumando el log de la proporción de cada opción. Para «dónde es más probable que viva» se multiplica por los electores del circuito. Supone votos independientes entre elecciones, así que concentra de más.

## Método
1. **Principal** (`matriz_votos.csv`, `matriz_pct.csv`, `por_provincia.csv`): primero una matriz nacional con los circuitos ponderados por electores. Después una matriz **por provincia**, penalizada hacia la nacional. Los conteos son el padrón del año de destino de cada circuito, repartido según cómo votó el circuito en el año de origen. El cambio de padrón (jóvenes, fallecidos, mudanzas) queda dentro de la hipótesis de que el circuito es «la misma gente».
   - **Penalización elegida por validación cruzada** (26-oct-2026; `LAMBDAS` en `estimar.py`, resultado en `control.json`): los circuitos de cada provincia se reparten en 5 grupos y se mide el error fuera de muestra de cada penalización. Se queda la más fuerte cuyo error está a menos del 1 % del mínimo: 2e-6 o 2e-7 según el par. La anterior, fija en 2e-4, era tan fuerte que todas las provincias copiaban la matriz nacional (FIT-U 2019 → JxC 95 % en las 24) y repartía a JxC → Hacemos de manera pareja por todo el país. `LAMBDA=<valor>` en el entorno la fija a mano.
   - **Destinos ausentes en cero**: en cada provincia, una fuerza que no se presentó (columna sin votos) no recibe flujo. Antes heredaba la forma de la matriz nacional, y Hacemos, por ejemplo, recibía 12.800 votos en Buenos Aires en diputados 2019→2023 sin tener lista.
2. **Variante Calvo** (`calvo_nacional.csv`): idéntica al R, con una sola matriz nacional, circuitos sin ponderar y penalización 0,001 hacia cero.
3. **Bootstrap** (`intervalos.csv`): 200 remuestreos de circuitos dentro de cada provincia, con percentiles 5 y 95.
4. **Validación del port**: con los datos del zip 2019 (PASO → general presidente, 92.751 mesas), el port llega a una función objetivo menor que la del resultado del R (431,5 contra 443,5). El R arranca en valores al azar y sin gradiente. Las dos soluciones difieren en el 3,7 % de los votos, sobre todo en lo que pasó después con los votantes de Macri en la PASO.
5. **Velocidad** (26-oct-2026): la pérdida es cuadrática en la matriz, así que `rxc_calvo.fit` la evalúa con dos matrices resumen (X'WX y X'WY) en vez de recorrer todos los circuitos en cada iteración. Llega al mismo óptimo: en presidente 2019→2023 la pérdida da 85,44966 con las dos versiones y las celdas difieren en menos de 0,1 punto. El bootstrap pesa cada circuito por la cantidad de veces que sale en el remuestreo en vez de copiar filas. La validación cruzada y el bootstrap corren en `WORKERS` procesos (4 por defecto, para no recalentar la CPU). Los ocho pares tardan unos 7 minutos.
6. **Auditoría** (`python auditar.py` → `AUDITORIA.md`): por fila, peso en el padrón, máxima diferencia entre la principal y la de Calvo, y ancho del intervalo. Una fila es **no identificada** si las variantes difieren en más de 30 puntos en alguna celda, o en más de 20 si pesa menos del 5 % del padrón. También controla, por provincia, que ningún destino reciba más del 125 % de sus votos reales. En los sankeys, las filas no identificadas llevan asterisco y una nota al pie (las cintas conservan el color del partido).

## Resultados (% de cada fila; principal / variante Calvo)
Solo filas identificadas; el resto está en `AUDITORIA.md`. Entre las dos variantes cambian de 3,8 M a 5,8 M de votos por par: una celda solo es firme si las dos coinciden.

**2021 → 2025**
- Frente de Todos → Fuerza Patria: 69 / 84; → No votó: 13 / 7.
- Juntos por el Cambio → LLA: 63 / 63; → No votó: 13 / 20.
- No identificadas: Libertarios, FIT-U, Tercera Vía / PF, Otros y Blanco y nulo, todas de menos del 5 %. Libertarios → LLA da 77 / 63; el «→ Fuerza Patria 33 %» de la versión anterior bajó a 9 / 37 y sigue sin ser creíble.

**2023 → 2025**
- Unión por la Patria → Fuerza Patria: 73 / 84; → No votó: 10 / 8.
- LLA 2023 → LLA: 57 / 51; → No votó: 17 / 20; → Otros: 13 / 20.
- Juntos por el Cambio → LLA: 72 / 66; → Provincias Unidas: 7 / 12; → No votó: 8 / 19.
- FIT-U → FIT-U: 57 / 51.
- Blanco y nulo 2023 → LLA: 19 / 36; → No votó: 38 / 25.
- No identificadas: Hacemos (→ Provincias Unidas 52 / 78: el sentido coincide, la proporción no) y Otros.

**Presidente 2023 (PASO, general y balotaje) → diputados 2025** (26-oct-2026; carpetas `2023pp_2025/`, `2023p_2025/`, `2023b_2025/`). La PASO (`2023pp`) sale de `datos_oficiales/2023_paso/2023-PROVISORIOS_PASO.zip`, leído sin extraer (`agregar_circuitos.py 2023pp`; 24,0 M de votos), **por lista**: Massa, Grabois, Milei, Bullrich, Larreta, Schiaretti y FIT-U (sus dos listas juntas); el resto en Otros. Santa Fe va por sección en los tres (renumeró circuitos en 2023: en la PASO 77 % de cobertura por circuito). Cobertura 98–99 % del padrón de origen; penalización 2e-7 en los tres.
- PASO: Massa → Fuerza Patria 87 / 100. Grabois → Fuerza Patria 81 / 67. Milei → LLA 53 / 47; → No votó 17 / 14; → Otros 16 / 25. **Bullrich → LLA 90 / 87**; **Larreta → LLA 50 / 57**, → Provincias Unidas 14 / 14, → Fuerza Patria 5 / 22 (esta celda no es firme). FIT-U → FIT-U 56 / 54. No identificadas: Schiaretti (→ Provincias Unidas 53 / 88), Otros y Blanco y nulo.
- General: UxP → Fuerza Patria 70 / 79; → No votó 13 / 12. LLA → LLA 53 / 54; → No votó 23 / 17. JxC → LLA 73 / 69. No identificadas: Hacemos (→ Provincias Unidas 37 / 80) y FIT-U (→ FIT-U 55 / 27).
- **Versión sin «No votó»** (pedido del usuario, ocupaba mucho espacio): `sankey.py <o> <d> --votantes` → `sankey_<o>_<d>_votantes.svg/.html/.png`. Es la misma estimación; solo se quitan la fila y la columna «No votó», y los porcentajes pasan a ser sobre quienes votaron en las dos elecciones. Sirve para cualquier par. **Versión reducida**: `--reducido` → `sankey_<o>_<d>_reducido.*`, con «No votó» y sus cintas dibujados a escala 1:4 (`REDUCIDO` en `sankey.py`) y las cifras reales en las etiquetas y en el pie.
- Balotaje: Massa → Fuerza Patria 64 / 69; → Otros 12; → No votó 10 / 15. Milei → LLA 60 / 59; → No votó 17 / 13; → Provincias Unidas 6 / 10. No identificada: Blanco y nulo (→ LLA 54 / 1).

**2019 → 2025**
- Frente de Todos → Fuerza Patria: 51 / 64; → No votó: 25 / 21.
- Juntos por el Cambio → LLA: 64 / 67; → No votó: 16 / 22.
- No identificadas: Consenso Federal (→ Provincias Unidas 24 / 75), FIT-U y Otros.

**2009 → 2011** (legislativa a presidencial: en 2011 votó mucha más gente)
- Frente para la Victoria → FPV: 94 / 86.
- Acuerdo Cívico y Social → UDESO: 31 / 39; → FAP: 21 / 14; → No votó: 18 / 19.
- PRO / Unión-PRO → muy repartido: FPV 25 / 29, Frente Popular / PRO 23 / 13, Compromiso Federal 11 / 9.
- Peronismo Federal → FPV: 40 / 28; → Compromiso Federal: 14 / 44 (en el límite de no identificada).
- No votó 2009 → FPV: 21 / 28. Es la movilización de 2011.
- No identificadas: Proyecto Sur y Blanco y nulo.

**2019 → 2023**
- Frente de Todos → Unión por la Patria: 67 / 73; → LLA: 15 / 8.
- Juntos por el Cambio → Juntos por el Cambio: 56 / 56; → LLA: 25 / 33.
- Blanco y nulo 2019 → LLA: 47 / 45.
- No identificadas: Consenso Federal (→ Hacemos 21 / 76) y FIT-U.

**Presidente 2019 → 2023** (96 % del padrón; más limpio que diputados, porque las listas son las mismas en todo el país)
- Frente de Todos (Fernández) → Unión por la Patria (Massa): 67 / 72; → LLA (Milei): 17 / 14.
- Juntos por el Cambio (Macri) → JxC (Bullrich): 52 / 49; → LLA: 30 / 32; → Hacemos (Schiaretti): 8 / 16. Con la penalización vieja daba 14 % y salía parejo incluso donde Hacemos casi no existió. Ahora se concentra donde Hacemos sacó votos (Tierra del Fuego 25 %, Santa Fe 19 %, Córdoba 17 %), y los totales provinciales de Hacemos cierran con su voto real.
- NOS + Unite → LLA: 90 / 99.
- No identificadas: Consenso Federal (Lavagna → LLA 41 / 96), FIT-U (→ UxP 59 / 0: ninguna de las dos es creíble) y Blanco y nulo.

**Presidente 2023, primera vuelta → balotaje** (99,6 % del padrón; la matriz más firme de todas: entre variantes cambian 0,8 M de 35,1 M votos)
- Unión por la Patria → Massa: 98 / 99. La Libertad Avanza → Milei: 99 / 100.
- Juntos por el Cambio (Bullrich) → Milei: 82 / 80; → Massa: 7 / 6; → blanco: 6 / 5; → No votó: 5 / 9.
- Hacemos (Schiaretti) → Milei: 56 / 55; → Massa: 28 / 32; → blanco: 8 / 6.
- Blanco y nulo → No votó: 64 / 61 (el resto se reparte).
- No votó → Massa: 6 / 7.
- No identificada: FIT-U (→ Massa 62 / 37; → blanco 20 / 34). Las dos variantes coinciden en que casi no fue a Milei.

**Presidente 2019 → balotaje 2023**
- Frente de Todos → Massa: 69 / 77; → Milei: 17 / 14; → No votó: 13 / 8.
- Juntos por el Cambio (Macri) → Milei: 86 / 89.
- NOS + Unite → Milei: 91 / 99.
- No identificadas: Consenso Federal, FIT-U y Blanco y nulo.

**Presidente 2011 → 2023** (primera vuelta; doce años, misma reserva que en diputados; 85 % del padrón de 2011)
- Frente para la Victoria (Cristina Kirchner) → Massa: 56 / 61; → Milei: 19 / 22; → No votó: 14 / 11.
- FAP (Binner) → Bullrich: 62 / 69; → Milei: 14 / 15.
- UDESO (Alfonsín) → Milei: 46 / 37; → Bullrich: 41 / 40; → Schiaretti: 12 / 21.
- Compromiso Federal (Rodríguez Saá) → Milei: 59 / 65.
- CC-ARI (Carrió) → Bullrich: 99 / 99 (fila chica, pero las dos variantes coinciden).
- No identificadas: Frente Popular (Duhalde), FIT y Blanco y nulo.

**Presidente 2011 → balotaje 2023** (misma reserva de doce años)
- Frente para la Victoria → Massa: 61 / 62; → Milei: 20 / 21; → No votó: 18 / 16.
- UDESO → Milei: 92 / 94. Compromiso Federal → Milei: 87 / 99. Frente Popular → Milei: 69 / 61.
- FAP → Milei: 68 / 89 (el sentido coincide, la proporción no).
- No identificadas: FIT, CC-ARI y Blanco y nulo.

**2013 → 2025** (doce años, misma reserva que 2011 → 2023)
- Frente para la Victoria → Fuerza Patria: 56 / 71; → No votó: 21 / 10.
- FPCyS / UNEN → LLA: 47 / 52; → Provincias Unidas: 11 / 14; → No votó: 24 / 26.
- PRO → LLA: 75 / 63.
- Frente Renovador (Massa) → LLA 35 / 53; → Fuerza Patria 25 / 20; → No votó 30 / 21. Las dos variantes coinciden en que se partió, no en la proporción.
- Unión por Córdoba → Provincias Unidas: 47 / 59.
- No identificada: FIT (el «→ LLA ~52 %» de antes era un artefacto).

**2011 → 2023** (leer como «dónde rindió cada fuerza de 2023 según el mapa de 2011», ver reservas)
- Frente para la Victoria → Unión por la Patria: 54 / 63; → LLA: 17 / 14.
- UDESO (UCR) → Juntos por el Cambio: 48 / 45; → LLA: 22 / 29.
- FAP → Juntos por el Cambio: 64 / 54; → LLA: 17 / 22; → Hacemos: 4 / 21.
- Frente Popular / PRO → Juntos por el Cambio: 61 / 48.
- No identificadas: Compromiso Federal, CC-ARI, FIT y Blanco y nulo.

**Presidente 2003 → diputados 2005** (por circuito; PolAr)
- Kirchner → FPV: 59 / 63; → Peronismo Federal: 16 / 0; → UCR y aliados: 6 / 17. Las dos variantes coinciden en que la mayoría siguió al FPV, no en el resto: el «→ Peronismo Federal» de la principal es Buenos Aires, donde Kirchner 2003 tuvo el aparato de Duhalde y en 2005 Chiche Duhalde compitió contra el FPV.
- Menem → FPV: 44 / 52; → No votó: 21 / 19; → Otros: 10 / 17; → Peronismo Federal: 9 / 8.
- López Murphy → PRO: 28 / 21; → UCR y aliados: 18 / 1; → ARI: 11 / 10; → FPCyS: 10 / 19; → Blanco y nulo: 13 / 14. Se dispersó.
- Carrió → ARI y aliados: 36 / 25; → Otros: 31 / 25 (en 2005 el ARI no fue con el mismo sello en todas partes).
- No identificadas: Rodríguez Saá (50 % al FPV en la principal, 42 % al Peronismo Federal en la de Calvo: concentrado en San Luis, no se separa), Otros y Blanco y nulo.
- Penalización 2e-6; las variantes difieren en 6,1 M de 25,3 M votos (es un par mal identificado: cargos distintos y muchas fuerzas).

**Presidente 2003 → 2007** (por circuito; PolAr)
- Kirchner → Cristina Kirchner: 70 / 79. Menem → Cristina Kirchner: 65 / 69; → No votó: 18 / 18.
- López Murphy → Carrió: 49 / 41; → Lavagna: 42 / 53. Carrió → Carrió: 73 / 86.
- Otros → Lavagna: 38 / 39; → No votó: 32 / 26.
- No identificadas: Rodríguez Saá (→ Cristina 50 / 16; → FREJULI 21 / 55) y Blanco y nulo.
- Penalización 2e-6; las variantes difieren en 3,6 M de 25,8 M votos.

**Presidente 2003 → diputados 2009** (por circuito; PolAr)
- **Capital Federal por circunscripción** (`caba_cruce.py`, se aplica solo en pares que cruzan 2008). Las 28 circunscripciones de 1973 rigieron hasta 2008; la Res. 1507/2008 del Ministerio del Interior (11-dic-2008) creó 15 secciones (= comunas) y 167 circuitos nuevos, descriptos por calles y sin equivalencias con los anteriores. Por eso: 2003 se suma por circunscripción (la sección de PolAr es el número de circunscripción) y cada circuito de 2009 se reparte entre las circunscripciones que pisa, según la superficie compartida (circuitos de `circuitos_electorales_AR` contra `mapa1983/caba28.pkl`). Con superficie sola, las circunscripciones densas del centro quedaban con 25 a 35 % menos electores que en 2003 (Monserrat, San Nicolás, Socorro), así que los pesos de los circuitos compartidos se calibran con el padrón de 2003 (ajuste proporcional iterativo); 93 de los 167 circuitos caen más del 90 % en una sola circunscripción. Después del ajuste, el padrón 2009/2003 de cada circunscripción queda entre 0,95 y 0,98, como la caída del padrón porteño.
- Chaco por sección. Se usan 4.414 unidades, el 95 % del padrón de 2003.
- Kirchner → FPV: 60 / 65; → Peronismo Federal: 10 / 0; → PRO / Unión-PRO: 8 / 18.
- Menem → FPV: 33 / 49; → PRO / Unión-PRO: 24 / 0; → No votó: 14 / 25. Las variantes no coinciden en cuánto del menemismo fue a De Narváez (Unión-PRO).
- López Murphy → Acuerdo Cívico y Social: 68 / 67; → PRO: 24 / 31.
- Carrió → Acuerdo Cívico y Social: 42 / 35; → Otros: 17 / 20; → Proyecto Sur: 10 / 0.
- Rodríguez Saá → FPV 24 / 5, Peronismo Federal 11 / 36: no llega al umbral de «no identificada» (25 puntos), pero no es firme.
- Capital (matriz provincial): Kirchner → FPV 37, Proyecto Sur 25, PRO 16; Menem → PRO 84; López Murphy → ACyS 51, PRO 49; Carrió → Proyecto Sur 76, ACyS 23.
- No identificadas: Otros y Blanco y nulo. Penalización 2e-6; las variantes difieren en 6,2 M de 26,0 M votos.

**2009 → 2013** (diputados; 98 % del padrón de 2009; Santa Fe por sección)
- Frente para la Victoria → FPV: 80 / 81.
- Acuerdo Cívico y Social → FPCyS / UNEN: 65 / 68.
- Peronismo Federal → Unión por Córdoba: 28 / 49; → PRO: 21 / 9.
- No identificadas: PRO / Unión-PRO (→ Frente Renovador 49 / 81: se sabe que fue a Massa, no cuánto), Proyecto Sur y Otros.
- Penalización 2e-6; las variantes difieren en 6,7 M de 29,4 M votos.

**Presidente 2011 → 2015** (96 % del padrón de 2011; Río Negro y Santa Fe por sección)
- FPV → FPV (Scioli): 66 / 68; → UNA (Massa): 19 / 17.
- FAP → Cambiemos: 77 / 100; → UNA: 11 / 0. UDESO (UCR) → Cambiemos: 88 / 85.
- Frente Popular (Duhalde) → Cambiemos 58 / 41, → UNA 31 / 47. CC-ARI → Cambiemos: 92 / 73.
- No identificadas: Compromiso Federal y FIT. Las variantes difieren en 3,9 M de 29,9 M votos.

**Presidente 2015, 1.ª vuelta → balotaje** (99 % del padrón)
- FPV → FPV: 98 / 96. Cambiemos → Cambiemos: 100 / 100.
- UNA (Massa) → Cambiemos: 54 / 61; → FPV: 33 / 27; → No votó: 10 / 9.
- FIT → FPV: 81 / 70 (pese al llamado al voto en blanco; las dos variantes coinciden, pero es una fila chica).
- Progresistas → Cambiemos: 63 / 44. Compromiso Federal → Cambiemos 53 / 50, FPV 35 / 38.
- No identificada: Blanco y nulo. Las variantes difieren en 1,4 M de 31,6 M votos.

**Presidente 2011 → balotaje 2015** (96 % del padrón)
- FPV → FPV: 85 / 80; → Cambiemos: 6 / 8.
- FAP, UDESO, Frente Popular, CC-ARI y Compromiso Federal → Cambiemos: entre 85 y 97 en las dos variantes (Compromiso Federal 94 / 75).
- No identificada: FIT. Penalización 2e-7.

**Diputados 1954 → presidente 1958** (por departamento; Cantón)
- Partido Peronista → UCRI (Frondizi): 66 / 50; → Blanco y nulo: 13 / 11; → Otros: 11 / 23; → UCRP: 3 / 9. El orden coincide con el pacto Perón–Frondizi: la mayoría del peronismo fue a Frondizi y una parte votó en blanco; el reparto entre UCRI y Otros (neoperonistas, conservadores) es menos firme.
- UCR → UCRP (Balbín): 79 / 69; → UCRI: 18 / 29.
- Otros → Otros: 76 / 85. No votó → UCRP 27 / 29, Otros 34 / 8, No votó 28 / 35.
- No identificada: Blanco y nulo (1,8 % del padrón).
- Penalización 2e-4 (la más fuerte; con 406 departamentos la validación cruzada no pide menos). Las variantes difieren en 1,6 M de 9,1 M votos.

**Diputados 1954 → diputados 1965** (por departamento; Cantón; carpeta `1954d_1965d/`)
- Se eligió 1965 y no 1962 porque tiene más cobertura: 451 unidades en 21 distritos contra 403 en 16 (en 1962 no votaron por departamento Catamarca, Formosa, La Rioja, Misiones, San Luis, Santa Cruz y Santiago del Estero).
- Partido Peronista → UP y neoperonistas: 50 / 43; → UCRP: 11 / 16; → Otros: 11 / 14; → No votó: 17 / 16; → Blanco y nulo: 5 / 5.
- UCR → UCRP: 57 / 56; → Otros: 21 / 16; → UP y neoperonistas: 7 / 10; → MID: 6 / 3; → UCRI: 2 / 7. La UCR de 1954 (unida) aparece mayormente en la UCRP; lo que fue a la UCRI y al MID se distingue mal entre sí.
- No identificadas: Otros y Blanco y nulo.
- **Unión Popular y neoperonistas van juntos**: separados, las dos variantes se contradecían (Calvo daba UCR → UP 36 %), porque se reemplazan según la provincia (donde corre un partido neoperonista provincial no corre la UP). Juntos, las filas grandes difieren en menos de 8 puntos.
- Once años: buena parte del padrón de 1965 no votaba en 1954 (se triplicó en el conurbano). Por eso «No votó → No votó» es bajo y el filtro de padrón es `RATIO=0.6,2.7`, para no perder Merlo, Moreno, General Sarmiento y Florencio Varela. Se descartan Chaco General Belgrano y Tapenagá, Florentino Ameghino y Cura-Có; se usan 378 departamentos (8,42 M de 8,51 M inscriptos de 1954).
- Penalización 2e-5 por validación cruzada.

**Presidente 1958 → diputados 1962** (por departamento; Cantón; carpeta `1958d_1962d/`)
- UCRI (Frondizi) → UP y neoperonistas: 51 / 43; → UCRI: 14 / 29; → Otros: 13 / 8; → No votó: 13 / 15. Es la vuelta al peronismo de quienes votaron a Frondizi por el pacto con Perón: las dos variantes coinciden en que fue más de 4 de cada 10.
- UCRP (Balbín) → UCRP: 59 / 69; → UCRI: 35 / 18 (en el reparto UCRP/UCRI de este electorado las variantes difieren).
- Blanco y nulo 1958 (el voto en blanco peronista que desobedeció la orden de votar a Frondizi) → UP y neoperonistas: 76 / 74. La fila más firme del par.
- Otros → FNPC 24 / 26, Otros 25 / 15, UCRI 18 / 18. No votó → No votó: 43 / 70.
- Ninguna fila «no identificada»; penalización 2e-4 (la validación cruzada es casi plana). Las variantes difieren en 1,7 M de 9,9 M votos.

**Caveats de los datos de 1958 → 1962**
- **Cargos distintos**: presidente en 1958, diputados nacionales en 1962 (en 1962 se votaban también gobernadores en muchas provincias).
- **1958**: el peronismo estaba proscripto y Perón ordenó votar a Frondizi; el voto en blanco (8 % del padrón) es en buena parte peronista. «UCRI» incluye la UCR Bloquista de San Juan, como en el atlas.
- **1962**: el peronismo compitió con la Unión Popular y partidos neoperonistas provinciales (bloque «Frente Justicialista» del atlas de 1962). La elección **fue anulada**: el gobierno intervino las provincias donde ganó el peronismo y Frondizi fue derrocado el 29 de marzo; los resultados no llegaron a regir, pero son votos efectivamente emitidos.
- **Cobertura: 14 provincias, 355 departamentos.** Fuera: Catamarca, Formosa, La Rioja, Misiones, San Luis y Santa Cruz (no eligieron diputados nacionales en marzo de 1962), Santiago del Estero (Cantón no trae sus diputados de 1962), Corrientes y Río Negro (sin presidente 1958 por departamento) y Florencio Varela (1962 sin inscriptos; nueve celdas imputadas en `canton5865/correcciones.py`).
- **Partidos nuevos de 1959-61** sumados al partido de 1958 que los contenía (en Cantón 1958 figuran sin datos): Berazategui → Quilmes, Tres de Febrero → General San Martín, Escobar → Pilar, Hipólito Yrigoyen → Pehuajó, San Cayetano → Necochea, Capitán Sarmiento → Bartolomé Mitre.
- Los dos años salen de Cantón t. II **corregido** (`canton5865/correcciones.py`: 80 correcciones con página y motivo; ver `canton5865/LEEME.md`).
- Por departamento, no por circuito: el sesgo ecológico es mayor que en los pares recientes. Categorías: 1958 UCRI, UCRP, Otros (conservadores, PDC, socialistas, PDP, etc.), Blanco y nulo, No votó; 1962 UP y neoperonistas, UCRI, UCRP, FNPC (centro), Otros (PSD, PDP, etc.), Blanco y nulo, No votó.
- Comandos: `python transferencias/canton_1958_1962.py` y `RATIO=0.6,2.3 python transferencias/estimar.py 1958d 1962d`.

**Diputados 1930, presidente 1937 y diputados 1940 → presidente 1946** (por departamento; Cantón; carpetas `1930d_1946d/`, `1937d_1946d/`, `1940d_1946d/`)
- **1930 → 1946: matriz poco informativa, no se lee como transferencia** (14 distritos, 339 departamentos). Todas las filas salen parecidas (UCR → Perón 44 / 42, Conservadores 46 / 33, Antipersonalistas 42 / 43, Socialistas 47 / 49) porque repiten el resultado promedio de 1946 (Perón 44 %, UD 36 %): es la huella de la falta de señal, no un hallazgo. Los votos de 1930 casi no predicen los de 1946: correlación de cada partido con la proporción de Perón de −0,21 a +0,17 en el país y de −0,15 a +0,28 dentro de cada provincia; dentro de provincia el origen explica el 21 % de la variación del voto a Perón, contra 60 % en 1958 → 1962 y 81 % en 2011 → 2015. Con una matriz sin información, la mejor solución de mínimos cuadrados es justamente «todas las filas iguales al promedio», y las dos variantes coinciden, así que el criterio de «no identificada» no lo detecta (de ahí el control nuevo de `auditar.py`, «separación de las filas»: 9,5 puntos acá, 29,5 o más en todos los pares que se leen bien). Lo único que dice el par es que la geografía de 1946 no es la de 1930 (además, 16 años de padrón nuevo).
- **1937 → 1946** (solo Capital, Córdoba, La Rioja y Tucumán: 73 departamentos). Acá sí hay señal (dentro de provincia el origen explica el 49 % del voto a Perón), pero con 11 a 24 unidades por provincia la validación cruzada eligió casi sin penalización (2e-6) y las matrices provinciales quedaron en las esquinas (Concordancia → UD 99 % en Capital y Córdoba, → Perón 99 % en Tucumán): sobreajuste. Con penalización fija 2e-4 y 2e-3 (prueba de sensibilidad, no se guardó): UCR (Alvear) → Perón 66 y 62, → UD 30 y 35 — **la fila radical es estable: unos dos tercios a Perón** (principal 68, Calvo 56). Concordancia → UD 73 y 63 en el total, pero con destinos opuestos según la provincia (Capital y Córdoba → UD; Tucumán → Perón 54 a 99): por eso no se identifica a nivel nacional. Socialista → Perón 89 a 98 no es creíble como conducta (el PS estaba en la UD): es la geografía de clase de Capital, donde las circunscripciones obreras eran a la vez socialistas y radicales en 1937 y peronistas en 1946, y el modelo no puede separar las dos filas.
- **1940 → 1946** (Capital, Córdoba, Entre Ríos, Santa Fe y Tucumán: 87 departamentos): separación de las filas 19,9, por debajo del umbral, así que también se marca como **poco informativa**. La señal está casi toda en **Córdoba** (UCR con la proporción de Perón r = 0,80; matriz provincial UCR → Perón 81, Concordancia → UD 71) y algo en Entre Ríos; en Capital y Santa Fe el voto de 1940 a UCR y Concordancia casi no se correlaciona con Perón (r entre −0,08 y 0,07) y las filas repiten el promedio. El total nacional (UCR → Perón 66 / 51; Concordancia → UD 54 / 40; Socialista mitad y mitad con intervalo de 50 puntos) mezcla esas situaciones. Lo que en Capital sí predice a Perón es Otros (Concentración Obrera, r = 0,58) → Perón 91 / 96.
- Penalización por validación cruzada: 2e-4 (1930, 1940) y 2e-6 (1937).

**Caveats de los datos de 1930–1946**
- **Selección de Cantón**: para 1931–1942 publicó por departamento solo los distritos donde ganó la oposición, por presunción de fraude en el resto (t. I, p. XVI). 1937 y 1940 no son una muestra del país sino de los distritos más competitivos; 1930 y 1946 sí están completos (salvo San Luis, que no votó en 1930).
- **Cargos distintos**: diputados en 1930 y 1940, electores de presidente en 1937 y 1946. Todas las tablas son **solo varones** (el voto femenino es de 1951).
- **Plazos largos**: 16 años entre 1930 y 1946 (el padrón crece 48 % en la mediana). El método reparte a los nuevos electores como votó su departamento antes: es comparación de geografías electorales, no seguimiento de votantes. El filtro de padrón es `RATIO=0.5,2`.
- **Blanco y nulo** = votantes menos la suma de las fuerzas publicadas, si es positivo. Muchas tablas (toda 1946, Capital 1937 y 1940) no traen blancos ni anulados, así que esa categoría junta blancos, nulos y lo que Cantón no desglosa. Las filas cuyas fuerzas suman más que los votantes se conservan como están impresas.
- **Categorías**. 1930: los bloques del atlas (UCR = UCR + Situacionista de Catamarca; Conservadores = Confederación de las Derechas; Antipersonalistas = Unificada, Antipersonalista, Figueroísta, etc.; Socialistas = PS + PSI; el resto, Otros). 1937: UCR (Alvear), Concordancia (con el Demócrata Nacional de Córdoba), Socialista y Otros (UCR Molinari, Junta Renovadora Nacional, Defensa Provincial). 1940: UCR (con la UCR Capital), Concordancia (con el Demócrata Nacional y la UCR Santa Fe, antipersonalista y oficialista), Socialista y Otros (Concentración Obrera, Partido Radical, Agrupación Defensiva, Social Independiente, Radical Unificado, Conservador, UCR Frente Popular, Agrario). 1946: Perón (Conjunción Peronista, Laborista y UCR Junta Renovadora), Unión Democrática (con la UCR Comité Nacional de Catamarca, Entre Ríos y Salta), Demócrata Nacional (Buenos Aires y Entre Ríos, que corrieron aparte) y Otros (UCR Lencinista, Bloquista, de Santiago del Estero e Irigoyenista de Tucumán).
- **Unidades**: los «\*\*» (cifras subsumidas en otra unidad) son los mismos partidos en los cuatro años y quedan fuera; los nombres coinciden uno a uno (solo Nueve de Julio de Santa Fe cambia de grafía). San Luis 1946 no tiene contraparte en 1930.
- Fuentes: 1930, `mapa1930/canton/` (la transcripción del atlas, cotejada con Lupu–Stokes); 1937, 1940 y 1946, `canton1937_1940/` y `canton1946/` (imágenes en `canton1938_1946/`).
- Comandos: `python transferencias/canton_1930_1946.py` y `RATIO=0.5,2 python transferencias/estimar.py 1937d 1946d` (ídem `1940d 1946d` y `1930d 1946d`).

**Córdoba: presidente 1999 → 2003** (por circuito; base de Ernesto Calvo y PolAr; carpeta `1999pc_2003pc/`)
- Alianza (De la Rúa) → López Murphy 37 / 38, → Rodríguez Saá 18 / 19, → Kirchner 18 / 10, → Carrió 11 / 6, → Otros 12 / 20. El voto de la Alianza se reparte entre cuatro candidatos; López Murphy es el destino principal en las dos variantes.
- PJ (Duhalde) → Menem 64 / 72, → Rodríguez Saá 26 / 18. Kirchner apenas toma del PJ cordobés de 1999 (2 / 9): en Córdoba sacó 10 %.
- AR (Cavallo) → López Murphy 44 / 26, → Carrió 38 / 34, → Kirchner 14 / 25: las variantes difieren 18 puntos; leer el rango.
- UCeDé → Menem 90 / 69. No identificadas: Otros y Blanco y nulo (pesan 2 % y 4 %).
- Separación de las filas 38,6: la matriz es informativa. 619 circuitos comunes, 542 usados (99 % de los votos de 1999); penalización 2e-4.
- **Sobre votos emitidos**: la base de Córdoba no trae electores por circuito (solo 1991), así que no hay «No votó» en ninguno de los dos años; 2003 se usa igual (`circ_2003pc.pkl`, Córdoba de PolAr sin electores) para que los dos lados sean comparables. Los flujos de abstención no se pueden estimar.
- Comandos: `python transferencias/cordoba_circuitos.py` y `python transferencias/estimar.py 1999pc 2003pc` (sufijo `c` = Córdoba por circuito).

**Córdoba: diputados 1991 → 1995** (por circuito; base de Ernesto Calvo; carpeta `1991c_1995c/`)
- UCR → UCR 74 / 82, → PJ 9 / 4, → Blanco y nulo 12 / 11, → FREPASO 3 / 1.
- PJ → PJ 88 / 94. CFI (Cavallo-Fuerza Independiente) → PJ 75 / 85.
- UCeDé → UCeDé 34 / 49, → FREPASO 17 / 25, → Blanco y nulo 27 / 14: la UCeDé pierde la mitad de su voto y no hay un destino único.
- El FREPASO (11 %) sale de Otros de 1991 (Convocatoria, democristianos, izquierda: 95 / 58, fila no identificada), de Blanco y nulo (65 / 75) y de la UCeDé; casi no toma del voto radical. Es un resultado ecológico: si el voto del FREPASO viene de circuitos radicales que también perdieron votos por otro lado, el método puede subestimar ese flujo.
- Separación 46,5. 566 circuitos comunes, 503 usados (98 % de los votos de 1991; los descartados cambian mucho de tamaño entre los dos años); penalización 2e-4.
- Sobre votos emitidos, como 1999 → 2003 (1991 trae electores, pero 1995 no).

**Presidente 1999 → 2003, nacional como Calvo y Escolar** (por departamento, con Córdoba por circuito, sobre votos emitidos; carpeta `1999pe_2003pe/`, sufijo `e`)
- Arma `presidente_1999.py`: la base de Ernesto por departamento, sumada por candidato según la tabla «Acceso a boletas» del artículo de la Wikipedia (`fuentes/w1999p.txt`). La UCeDé va con Duhalde salvo en Santa Fe, donde va con Cavallo; el PDP de Santa Fe y el PAL-PDP de Corrientes, con De la Rúa. En Corrientes y Santiago se descarta `acjc00`, que es el total de los sublemas `acjc01`–`03` (contarlo duplicaba a Duhalde).
- **Cotejo con la Wikipedia** por provincia: coincide a menos de 0,5 % salvo Formosa (De la Rúa −1 %) y Tierra del Fuego (Otros −14 %: falta alguna lista menor).
- **San Luis y Santa Cruz** no están en la base de Ernesto: van de Lupu–Stokes (Alianza y PJ por departamento coinciden con la Wikipedia a menos de 0,5 %). Cavallo y Otros vienen juntos en el resto, así que se reparten, igual que los blancos y nulos, con las proporciones provinciales de la Wikipedia: esas dos celdas no tienen variación propia en los 16 departamentos.
- **Córdoba por circuito** (630 circuitos de `circ_1999pc.pkl`, con la UCeDé sumada a Duhalde). Lo demás, por departamento: 2003 (PolAr por circuito) se suma por departamento fuera de Córdoba. Nombres emparejados por normalización y parecido, con `ALIAS` para los que fallan (p. ej. Bartolomé Mitre → Arrecifes, General Las Heras → Las Heras).
- Resultado (principal / Calvo, % de la fila): Alianza → López Murphy 21 / 29, Carrió 23 / 10, Kirchner 17 / 15, Rodríguez Saá 14 / 20, Menem 10 / 0; PJ → Menem 46 / 73, Kirchner 32 / 21, Rodríguez Saá 12 / 3; AR → López Murphy 64 / 45, Carrió 14 / 32, Rodríguez Saá 12 / 21. Las variantes difieren 5,2 M de 19,8 M de votos; la fila de la Alianza queda **cerca del promedio** (†), y Otros y Blanco y nulo, no identificadas.
- **Córdoba por circuito o por departamento casi no cambia el total nacional** (`agregacion_1999pe_2003pe/`, 1,8 puntos de media): Córdoba es el 9 % del voto. En la variante Calvo sí cambia (11,5), lo que confirma que esa variante es inestable.
- **Contra el libro** (fig. 6.12, p. 202; `comparacion_libro.csv`, con Otros + Blanco y nulo de 2003 como su «No estimado»):

| Fila | Versión | Menem | Kirchner | López Murphy | Rodríguez Saá | Carrió | No estimado |
|---|---|---|---|---|---|---|---|
| Alianza | Libro | 5 | 18 | 27 | 23 | 23 | 5 |
| | Principal | 10 | 17 | 21 | 14 | 23 | 16 |
| | Calvo, todo por departamento | 1 | 24 | 20 | 17 | 13 | 26 |
| PJ | Libro | 59 | 37 | 1 | 2 | 1 | 0 |
| | Principal | 46 | 32 | 0 | 12 | 1 | 10 |
| | Calvo, todo por departamento | 72 | 28 | 0 | 0 | 0 | 1 |
| AR | Libro | 0 | 2 | 35 | 28 | 26 | 9 |
| | Principal | 5 | 4 | 64 | 12 | 14 | 1 |
| | Calvo, todo por departamento | 0 | 1 | 57 | 24 | 16 | 2 |

  La dirección general coincide: el PJ de Duhalde se parte entre Menem y Kirchner; la Alianza se dispersa entre López Murphy, Carrió, Rodríguez Saá y Kirchner; AR va sobre todo a López Murphy. Las cifras no, y ninguna versión lo reproduce. El libro solo tiene tres filas (sin Otros ni Blanco y nulo de 1999) y casi nada en «No estimado», o sea que obliga a que todo el voto vaya a los cinco candidatos; acá Otros y Blanco y nulo de 2003 son destinos propios. Tampoco dice si filtró departamentos (para replicar a Gervasoni usaron los de más de 10.000 votantes) ni con qué datos de San Luis y Santa Cruz.
- **Qué acerca al libro** (`replica_libro.py` → `replica_libro_1999pe_2003pe/RESUMEN.md`; todo por departamento, ocho combinaciones de tres cambios). Distancia media con el libro (½ Σ |diferencia|, ponderada por sus votos), variante Calvo: base 21,3; solo departamentos de más de 10.000 votantes 16,0; solo tres filas de origen 16,1; destinos forzados a los cinco candidatos 18,4; los tres juntos **10,5** (312 departamentos). Con los tres cambios y la variante de Calvo (una matriz nacional sin ponderar, como su código), las filas grandes casi coinciden: Alianza → Menem 8 / Kirchner 22 / López Murphy 22 / Rodríguez Saá 25 / Carrió 24 (libro 5 / 18 / 27 / 23 / 23, distancia 9) y PJ → Menem 65 / Kirchner 33 (libro 59 / 37, distancia 6). **AR no se reproduce** con ninguna combinación (distancia 15 a 51): da López Murphy 59 y Carrió 2 contra 35 y 26 del libro. Es la fila chica (10 %) y la más inestable. Con la especificación principal (matrices provinciales) ningún cambio baja de 15,5. Lectura: el libro corresponde a una sola matriz nacional, sobre los departamentos grandes, con solo los tres candidatos de 1999 y los cinco de 2003. Esas restricciones mueven las cifras tanto como los datos.
- **Cuál se acerca más a la realidad: dos controles** (`controles_1999.py` → `replica_libro_1999pe_2003pe/CONTROLES.md`).
  1. *Ajuste fuera de muestra*: cada versión se estima sin un quinto de los departamentos (5 grupos al azar, 3 repeticiones) y predice el reparto entre los cinco candidatos de 2003 en los que quedaron afuera. Error (puntos, ponderado por votos): **principal sin restricciones 4,9**; las otras versiones principales, 5,0 a 5,3; todas las variantes de una sola matriz nacional, 9,1 a 10,0. La más parecida al libro (los tres cambios con la variante Calvo), 9,6: casi el doble de error.
  2. *Córdoba por circuito*: estimación con los 630 circuitos de Córdoba con las mismas categorías, contra lo que cada versión dice para Córdoba (reparto entre los cinco candidatos de las filas De la Rúa, Duhalde y Cavallo). Distancia media: **principal sin restricciones 13,7**; el resto, 23 a 36; la más parecida al libro, 34,4. Los circuitos de Córdoba dan PJ → Menem 80 y Kirchner 4: una provincia muy distinta del promedio nacional, que una sola matriz nacional no puede reflejar. La principal parte con ventaja, porque usa una matriz propia de Córdoba.
  - Lectura: los dos controles prefieren la estimación principal sin las restricciones del libro, y la versión que reproduce el libro es de las peores en ambos. No prueba que sus flujos sean los reales, pero es la que mejor encaja con los datos.
- Comandos: `python transferencias/presidente_1999.py`, `python transferencias/estimar.py 1999pe 2003pe`, `NAZAR=5 python transferencias/agregacion.py 1999pe 2003pe`, `python transferencias/replica_libro.py`, `python transferencias/controles_1999.py` y `python transferencias/sankey.py 1999pe 2003pe`.

### Datos de Córdoba por circuito (Ernesto Calvo)
- `Bases Ernesto/Cordoba x circuito/`: un archivo por elección en once formatos distintos, que `cordoba_circuitos.py` lee todos y guarda en `circ_<año>c.pkl` (presidente: `circ_<año>pc.pkl`). Clave: número de circuito sin ceros a la izquierda (1, 4A, 10L); la sección sale de PolAr 2003.
- Años: 1983 (presidente y diputados), 1985, 1987, 1991, 1993, 1995 (presidente y diputados), 1997, 1999 (presidente y diputados) y 2001 (diputados). 1994 (constituyentes) y 1998 (provincial, en Access) no se cargaron. **No hay 1989.**
- Control contra la base departamental de Ernesto: 1991, 1993, 1995 y 1999 coinciden casi exactos (diferencias de menos de 600 votos); a 1983 y 1987 les falta 2–3 %; **1985 no trae Capital ni San Justo** (la mitad de los votos); 1997 no tiene el número de circuito y se empareja por nombre con 1995 y 1999 (561 circuitos, 1,43 M de votos).
- Los archivos de 1995 traen al final subtotales por departamento con códigos de tres cifras; se descartan (solo códigos de cuatro cifras).
- Otros archivos por circuito de `Bases Ernesto/` no sirven para el presidente de 1999: `Santa Fe x circuito/sfe_91_01_circ.xls` trae las provinciales del 8-ago-1999 (gobernador, no presidente) y diputados nacionales de 1993, 1997 y 2001; `E Rios x Circuito/` solo tiene tablas de correspondencia de circuitos entre años; `Circuitos Pais 1999.xls` es una lista de códigos sin votos; `MENDOZA99PARASP.xls`, `neuquen99.xls`, `santafe.xls` y `tdf.xls` son por departamento.
- `Bases Ernesto/Buenos Aires x circuito/` no tiene votos: son listas de los circuitos de cada partido por año (1985–1997). No hay datos de la provincia de Buenos Aires por circuito antes de 2003.

### Datos de 1954 → 1958 y 1954 → 1965
- **1954**: `canton1954/canton_1954.csv` (transcripción del usuario de Cantón t. II, PDF pp. 171–248), tabla «varones y mujeres». En 1954 se votaba diputados (uninominales) y vicepresidente; en los territorios, delegados. Categorías: Partido Peronista, UCR, Otros, Blanco y nulo, No votó. **1958**: presidente, Cantón corregido de `canton5865/` (el mismo del atlas): UCRI (con la UCR Bloquista de San Juan), UCRP, Otros, Blanco y nulo, No votó.
- `python transferencias/canton_1954_1958.py` arma `circ_1954p.pkl` y `circ_1958p.pkl` (unidad = departamento, con el nombre de 1958). Después `RATIO=0.6,2.3 python transferencias/estimar.py 1954p 1958p`: el filtro de padrón se abre porque entre 1954 y 1958 hubo cambios de límites y el padrón creció de manera dispar (mediana 0,99, pero territorios provincializados crecen mucho más).
- **Unidades «\*\*»** de 1954 (subsumidas en una mayor): se suman en 1958 a la que las contenía, inferido de la geografía y confirmado con el padrón (el cociente 1958/1954 queda cerca de la mediana provincial; Necochea ⊃ Tres Arroyos + Juárez + González Chaves da 1,01). Grupos en `GRUPO`: Lanús → Avellaneda; Berisso y Ensenada → La Plata; C. de M. Leonardo Rosales → Bahía Blanca; Leandro N. Alem → Lincoln; General Roca y Pte. Roque Sáenz Peña → Juárez Celman (Córdoba); General José de San Martín → Orán; General Alvear y Malargüe → San Rafael; Chimbas → Capital (San Juan).
- **Nombres peronistas de 1954** pasados a los de 1958 (`NOMBRE`): 12 de Abril → 12 de Octubre, Cabo Mayor Farina → Mayor Luis J. Fontana, 24 de Febrero → Tapenagá (Chaco), y variantes de escritura (Leventué/Loventué, Corpe-Aike/Corpen Aike, Paso de los Indios, Ischilín, etc.).
- **Fuera del análisis**: San Luis y Tucumán (Cantón da solo varones), Corrientes y Río Negro (sin 1958 por departamento), la zona militar de Comodoro Rivadavia (sin inscriptos en 1954; con ella Escalante, Sarmiento y Río Senguerr de Chubut y Deseado y Lago Buenos Aires de Santa Cruz en los dos años), y Susques, Los Andes y Zonda (1958 sin contraparte). El filtro de padrón descarta además Chaco General Belgrano y Tapenagá (más votantes que inscriptos en 1954, ya avisado en el original), Florentino Ameghino y Cura-Có. Se usan 406 departamentos, 8,37 M de los 8,38 M inscriptos de 1954 en las provincias incluidas.
- **Correcciones solo en el análisis** (la transcripción no se tocó): cuando el total impreso de una celda no cierra su fila y varones + mujeres sí, se usa varones + mujeres (12 celdas, lista que imprime el script; p. ej. Chaco San Fernando blanco 2.944 → 1.944, Capital Monserrat UCR 22.212 → 22.112, Misiones Capital votantes 19.061 → 19.611). Misiones Concepción usa varones + mujeres porque su total repite las cifras de San Ignacio.
- **1965** (`python transferencias/canton_1954_1958.py 1965`, sufijo `d`: `circ_1954d.pkl` y `circ_1965d.pkl`; después `RATIO=0.6,2.7 python transferencias/estimar.py 1954d 1965d`): diputados, Cantón corregido de `canton5865/` con los bloques del atlas de 1965. Categorías: UP y neoperonistas (UP + MPP), UCRP, MID, UCRI, FNPC (centro), Otros (PDP, UCR Bloquista, socialistas, etc.), Blanco y nulo y No votó. Fuera: San Luis y Tucumán (1954 solo varones), Jujuy y Salta (no votaron en 1965); Catamarca y La Rioja entran con los departamentos que trae Cantón 1965 (5 y 9). Corrientes y Río Negro sí entran. Partidos nuevos de 1965 sumados a su partido de 1954 (`GRUPO65`, controlado con el padrón): Berazategui → Quilmes, Tres de Febrero → General San Martín, Escobar → Pilar, Hipólito Yrigoyen → Pehuajó, San Cayetano → Necochea, Capitán Sarmiento → Bartolomé Mitre, Salliqueló → Pellegrini, General Alvear (Corrientes) → San Martín (cociente 1,01). **Misiones** se redividió (17 departamentos contra 11): va como una sola unidad en los dos años.
- La auditoría de la transcripción está en `canton1954/AUDITORIA_1954.md` (`python canton1954/auditar_1954.py`).

## Reservas
- **1954 → 1958** mezcla cargos (diputados/vicepresidente contra presidente) y el peronismo estaba proscripto en 1958: «Partido Peronista → Blanco» es la orden de Perón cumplida por una parte de sus votantes. Es por departamento, no por circuito, así que el sesgo ecológico es mayor que en los pares recientes.
- **2011 → 2023 y 2013 → 2025 son doce años.** Cerca de un cuarto de los electores de 2023 no estaba en el padrón de 2011: jóvenes (desde 2013 votan desde los 16) y mudanzas, mientras otros murieron o se fueron. El método los reparte según cómo votó su circuito en 2011. Por eso es más una comparación de geografías electorales que un seguimiento de votantes. Lo mismo vale, en menor grado, para 2019 → 2025.
- **El bootstrap subestima la incertidumbre.** Sus intervalos son angostos, pero cambiar la especificación (principal contra Calvo) mueve entre 3,8 M y 5,8 M de votos. Una celda es confiable solo si las dos variantes coinciden. Condición necesaria, no suficiente: si el origen no predice el destino, las dos variantes coinciden en repetir el promedio en todas las filas (1930 → 1946). `auditar.py` lo marca como «matriz poco informativa» (separación media de las filas grandes respecto del promedio menor a 25 puntos) y el sankey lo avisa en rojo bajo el título. Lo mismo se mide por fila (columna «Sep.» de `AUDITORIA.md`, principal / Calvo): una fila de 5 % o más del padrón a menos de 25 puntos del promedio va marcada **cerca del promedio** y con † en el sankey. Hoy son 11 pares: Peronismo Federal (2009 → 2011), Frente Renovador (2013 → 2025), Hacemos (balotaje 2023), Partido Peronista (1954 → 1965), Menem (2003 → 2005), Rodríguez Saá (2003 → 2009), UNA (balotaje 2015), UCRI (1958 → 1962, justo en el límite) y las filas grandes de 1930, 1937 y 1940 → 1946. Puede ser un electorado que de verdad se repartió como el total o falta de señal; si la variante de Calvo también queda cerca, lo segundo es más probable.
- **Filas chicas** (FIT, Otros, Blanco y nulo, terceras fuerzas de menos del 5 %): casi no mueven el ajuste, así que su destino lo decide la especificación y no los datos. No es un problema de cómputo: con más penalización copian la matriz nacional, y sin ella se van a cualquier columna que se les parezca en el mapa.
- Los votos son del escrutinio provisorio, no del definitivo.
- **Departamento en vez de circuito** (los pares de Cantón): ver la prueba de abajo. Las filas grandes se mueven 1 a 3 puntos; las chicas y la abstención, 5 a 10.

## Prueba: matrices provinciales contra una sola matriz nacional (pares de Cantón)
`python transferencias/fuera_de_muestra.py [par ...]` (≈ 5 min los seis) → `fuera_de_muestra/RESUMEN.md` y `resumen.csv`. Cada variante se estima sin un quinto de los departamentos (5 grupos al azar, 3 repeticiones; mismo filtro de padrón y λ que la estimación publicada) y predice el reparto de destino de los que quedaron afuera, con todas las categorías. Error en puntos, ponderado por electores de destino. Dos referencias que no miran la elección de origen: el reparto medio de la provincia («sin origen») y el del país.

| Par | Deptos. | Principal | Una matriz nacional (Calvo) | Media provincial | Media nacional |
|---|---|---|---|---|---|
| Diputados 1930 → presidente 1946 | 339 | 5,4 | 6,4 | **5,3** | 6,6 |
| Presidente 1937 → presidente 1946 | 73 | **3,7** | 5,6 | 4,7 | 6,2 |
| Diputados 1940 → presidente 1946 | 87 | **4,7** | 5,4 | 5,0 | 6,1 |
| Diputados 1954 → presidente 1958 | 406 | **4,0** | 4,8 | 4,7 | 5,6 |
| Diputados 1954 → diputados 1965 | 378 | **3,7** | 6,4 | 4,3 | 7,0 |
| Presidente 1958 → diputados 1962 | 355 | **3,9** | 5,7 | 4,6 | 6,3 |

- **La principal gana en cinco de seis**; la única matriz nacional es la peor de los tres ajustes en todos. La matriz nacional sí aprende algo del origen (baja de 0,4 a 1,3 puntos el error de la media nacional), pero menos de lo que se pierde por ignorar las diferencias entre provincias: el promedio de cada provincia, sin mirar el origen, ya predice mejor que ella. Solo con el reparto entre fuerzas (sin No votó) el orden es el mismo.
- **1930 → 1946**: la principal no le gana a la media provincial (5,4 contra 5,3). El voto de 1930 no predice el de 1946 dentro de cada provincia; coincide con la «matriz poco informativa» de `AUDITORIA.md`. Ese par describe geografía, no traspasos.
- Lectura: con datos solo por departamento conviene la matriz provincial encogida. La idea de que una matriz nacional rinde más cuando hay pocas unidades no se sostiene acá, ni siquiera en 1937 (73 departamentos, 4 provincias), donde la ventaja de la principal es la mayor (21 % menos error que la media provincial). Como en 1999, un mejor ajuste no prueba que los flujos sean los reales.

## Prueba: circuitos contra departamentos (1.ª vuelta 2023 → balotaje 2023)
`python transferencias/agregacion.py` (≈ 10 min; `resumen` solo rehace el informe). Salida en `agregacion_2023p_2023b/RESUMEN.md` y `resumen.csv`. Se toman los 5.510 circuitos usados en `2023p_2023b/` y se agrupan **después** del filtro, así las tres versiones tienen los mismos votantes:
- **departamento**: circuitos sumados por sección de la DINE (520 unidades);
- **azar**: dentro de cada provincia, los circuitos repartidos al azar en grupos con la misma cantidad de circuitos que los departamentos (20 réplicas). Mismo número y tamaño de unidades, sin geografía. Si los coeficientes son parejos dentro de la provincia, agrupar al azar no sesga (solo agranda el ruido); lo que el departamento se aparta del azar más allá de la dispersión entre réplicas es sesgo de agregación geográfica.

Distancia por fila (½ Σ |diferencia|, en puntos del voto de la fila), media ponderada: departamento contra circuito 2,4; azar contra circuito 2,0; departamento contra azar 1,6. Variante Calvo, departamento contra circuito: 4,1.

| Fila | Peso % | Dpto. vs. circ. | Azar vs. circ. | Dpto. vs. azar | Dispersión del azar |
|---|---|---|---|---|---|
| Unión por la Patria | 27,7 | 0,4 | 1,0 | 0,6 | 0,4 |
| La Libertad Avanza | 22,6 | 0,6 | 1,1 | 0,5 | 0,2 |
| Juntos por el Cambio | 18,0 | 2,5 | 1,4 | 1,7 | 0,7 |
| Hacemos | 5,1 | 9,4 | 4,1 | 7,9 | 2,3 |
| FIT-U | 2,0 | 6,9 | 7,0 | 8,0 | 2,9 |
| Blanco y nulo | 2,3 | 9,5 | 12,2 | 3,7 | 2,5 |
| No votó | 22,3 | 3,8 | 2,6 | 1,5 | 0,7 |

- **Las filas grandes resisten**: UxP y LLA cambian menos de 1 punto; JxC 2,5 (→ Milei 82 contra 81, → No votó 5 contra 7).
- **Hacemos y el FIT tienen sesgo geográfico**, no solo ruido: el departamento se aparta del azar 8 puntos con una dispersión de 2–3. Por departamento Hacemos va más a la abstención (16 % contra 7 %) y menos a Massa (22 contra 28); el FIT, más a Milei (17 contra 11).
- **Blanco y nulo** se mueve casi lo mismo con grupos al azar (12) que por departamento (9,5): es sobre todo pérdida de unidades, no geografía.
- **La abstención por departamento sale más «mezclada»** (No votó → No votó 87,5 contra 91,4; Blanco y nulo → No votó 54 contra 64).
- La variante Calvo (una matriz nacional, sin ponderar) se deforma el doble que la principal; el FIT se va 30 puntos.
- 20 de las 28 celdas por departamento caen fuera del intervalo 5–95 del bootstrap por circuito: otra señal de que esos intervalos miden solo el muestreo de circuitos, no la especificación.
- Es un par de un mes con el mismo padrón: es el mejor caso. En pares de cuatro años (los de Cantón) el sesgo de agregación puede ser mayor. Lectura práctica para 1930–1965: confiar en las filas grandes con un margen de ±3 puntos y tomar las chicas y la abstención como orientativas (±10).

## Comparación con Calvo y Escolar (2005)

## Nuevos cruces solicitados en octubre de 2026

**Brasil 2026, primera vuelta presidencial → balotaje:** [Sankey nacional y por UF](brasil_2026p_2026b/sankey_brasil_2026p_2026b.html), [informe y controles](brasil_2026p_2026b/RESUMEN.md). TSE por sección; 497.147 secciones, 27 UFs y exterior, 99,62 % del padrón de destino. RxC jerárquico (centro nacional → UF → región geográfica del IBGE, `brasil2026_regiones.py`): penalizaciones y nivel por validación cruzada con municipios enteros, prueba fuera de muestra contra la matriz por UF, la nacional y Calvo, 200 bootstrap por local que recalculan centro y penalizaciones, rango entre especificaciones en `intervalos.csv` y alerta de celdas en el borde (‡). Sankey con el mismo `sankey.py` que los cruces argentinos (`python sankey.py brasil2026p 2026b`), filas en [AUDITORIA.md](AUDITORIA.md). Adaptador y scripts `brasil2026_*.py`; las bases originales quedan en `datos_oficiales/brasil2026/` (regiones del IBGE en `ibge/`).

[Índice con HTML, resúmenes, cobertura y controles](INDICE_NUEVOS_CRUCES.md). Incluye los cruces 2013–2017, presidenciales 2015–2023, 2009/2013 diputados hacia 2015, los cuatro pares hacia 2019 y los históricos 1983–1997. Todos tienen selector provincial; las ausencias de Tierra del Fuego en 1987 y San Luis en 1997 están documentadas. [Fuentes y utilidad de los históricos; Deseado 1995 extrapolado](historicos_1989/LEEME.md).

### Antecedente metodológico
En *La nueva política de partidos en la Argentina*, cap. 6, las matrices nacionales (1989→1995, 1999→2003, 2001→2003) están estimadas **por departamento** con todos los votos emitidos (nota 72, p. 186). Para replicar a Gervasoni (1998) usaron solo los departamentos con más de 10.000 votantes. Los circuitos los usan en el cap. 7 (seis provincias). Su categoría «No estimado» es el residuo; acá en su lugar va «No votó» como categoría explícita.
