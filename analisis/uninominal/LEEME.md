# Argentina con 257 distritos uninominales (Mosaic)

Ejercicio: la Cámara de Diputados con 257 bancas elegidas en distritos uninominales dibujados por algoritmo dentro de cada provincia, con la población del censo 2022, y quién los ganaría con la general 2023 (presidente), el balotaje 2023 y diputados 2025.

Herramienta: **Mosaic** (Matt Mohn, port a Python de *Mosaic for R*; ReCom de MGGG + recocido simulado), en `C:\Users\JC\Desktop\Escritorio 26\mosaic_python-main`. Se usa su `.venv` (el Python del sistema no tiene geopandas).

## Pasos

```
python analisis/uninominal/reparto.py                       # bancas por provincia
<mosaic>/.venv/Scripts/python.exe analisis/uninominal/construir.py          # circuitos (shp/)
<mosaic>/.venv/Scripts/python.exe analisis/uninominal/construir_radios.py   # radios (shp_radios/)
<mosaic>/.venv/Scripts/python.exe analisis/uninominal/distritar.py [--iter 3000 --tol 0.02] [--modo neutral|proporcional|peronista|lla] [--deptos --tol 0.05] [dd ...]
<mosaic>/.venv/Scripts/python.exe analisis/uninominal/construir_partidos.py # votos de cada partido por radio
<mosaic>/.venv/Scripts/python.exe analisis/uninominal/mapa.py               # mapa_257.html
```

Cada modo escribe en `plan_radios[_<modo>][_deptos]/`. Cuidar la temperatura: 4 procesos como máximo y `herramientas/vigilar_cpu.ps1` corriendo (afinidad a 4 hilos y prioridad baja; anota la temperatura de LibreHardwareMonitor).

`distritar.py` trabaja con radios por defecto; `UNI_SHP=shp UNI_PLAN=plan` corre la versión por circuitos. También copia el grafo a `cache/` de Mosaic, así que cada `shp_radios/<dd>_*.shp` se puede abrir en la interfaz (`run_mosaic.bat`): población = `population`, ID = `pid`, county = `county`, elecciones = `D23/R23`, `D23b/R23b`, `D25/R25`.

## Reparto de bancas (`reparto.py` → `reparto.csv`)

Ley 22.847: un diputado cada 161.000 habitantes o fracción mayor de 80.500, más 3 por distrito, piso de 5 y ningún distrito por debajo de lo que tenía.

- **Literal con 2022**: la Cámara pasaría a 361.
- **257 con la garantía**: el cociente que deja 257 (318.717) devuelve exactamente el reparto actual; la garantía lo congela.
- **257 sin la garantía** (`c257_sin_garantia`, el que se usa): cociente 247.650. Capital baja de 25 a 15 y Santa Fe de 19 a 17; suben Buenos Aires (73), Salta (9), Corrientes, Chaco, Misiones (8), Mendoza (11), Tucumán (10), Neuquén y Río Negro (6).

Población: suma de `POB_TOT_P` de los radios 2022 de CONICET (`geometria/cartografia_argentina/conicet/radios/RADIOS_2022_V2025-1.zip`), 45.618.784 hab. Son personas en viviendas particulares: no incluye viviendas colectivas ni situación de calle (el total oficial es 46.044.703). El reparto no cambia respecto de una versión anterior con otras cifras.

## Unidades: radios censales 2022

- 66.502 radios; cada uno va al circuito electoral 2025 que contiene su punto interior (`geometria/circuitos_serie/por_anio/2025/aproximada`, la capa que mejor empareja: 97,7 % de los electores de 2023, 99,9 % de 2025).
- **Votos**: los de cada circuito se reparten entre sus radios en proporción a la población. El total de cada circuito se conserva (diferencias de redondeo de ±100 votos por provincia), pero dentro del circuito todos los radios tienen el mismo porcentaje: el detalle partidario no es más fino que el circuito, solo la geografía y la población.
- Circuitos más chicos que un radio (rurales; muchos en Formosa y La Rioja) pasan sus votos al radio que más se les superpone.
- `county` = departamento del censo, para que Mosaic evite partir partidos.

### Votos 2023 sobre circuitos 2025 (`construir.py`)

Si el código del circuito existe en 2023 y 2025 y su padrón no cambió más de 0,8–1,25, el voto va directo (96 % de los votos). El resto de cada sección se reparte entre sus otros circuitos con el padrón 2025 y la desviación del circuito en 2025. El total de cada sección de 2023 se conserva. Hace falta porque Santa Fe renumeró circuitos dentro de las secciones (~650.000 electores) y hubo divisiones menores en Buenos Aires, Corrientes y Río Negro.

## Dos bloques

Mosaic es bipartidista (DEM/GOP). Se usa peronismo contra antiperonismo:

| Elección | D (peronismo) | R |
|---|---|---|
| `23` general 2023, presidente | Unión por la Patria | LLA + JxC |
| `23b` balotaje 2023 | Massa | Milei |
| `25` diputados 2025 | Fuerza Patria | La Libertad Avanza (bloques de `mapas/mapa2025/mapeo_listas_2025.csv`) |

El resto (Schiaretti, FIT, Provincias Unidas, provinciales) no cuenta; cada distrito se adjudica por mayoría simple entre los dos bloques. Es una simplificación fuerte en 2025, donde Provincias Unidas y los partidos provinciales ganaron distritos.

## Pesos de Mosaic

Neutrales: aristas cortadas 1, departamentos partidos 50, compacidad Polsby-Popper 100, desvío de población 1; sesgo a no cortar departamentos 2. Ningún peso partidario: las elecciones solo se miran después. Tolerancia de población 2 % (si no hay partición inicial, sube a 3, 4, 6, 8 %). Una corrida con una semilla es *un* mapa posible, no el único: para medir sesgo habría que generar un ensamble (muchas semillas o la cadena sin recocido).

## Resultados

Corrida del 31-oct-2026 (`--iter 3000 --tol 0.02`, semilla 1, ~5 min con 4 procesos): las 24 provincias con tolerancia 2 % (desvío máximo 1,99 %).

| Elección | Peronismo | Antiperonismo | % peronista de los dos bloques |
|---|---|---|---|
| General 2023 (UxP contra LLA + JxC) | 53 | 204 | 40,5 % |
| Balotaje 2023 (Massa contra Milei) | 74 | 183 | 44,3 % |
| Diputados 2025 (FP contra LLA) | 86 | 171 | 45,2 % |

Las bancas peronistas salen sobre todo del conurbano (Buenos Aires: 27 / 42 / 36 de 73), Santiago del Estero (7 de 7), Tucumán, Formosa y Chaco. Capital, Córdoba, Mendoza, Entre Ríos y Neuquén no dan ninguna en las tres. Es el sesgo típico de mayoría simple: el bloque con el voto concentrado gana menos bancas que su porcentaje.

Ver `plan_radios/resumen.csv` (un renglón por provincia) y `plan_radios/<dd>_distritos.csv` (población, desvío y votos de cada distrito).

## Planes

- **Neutral compacto**: los pesos de arriba, sin mirar votos.
- **Proporcional**: busca que las bancas peronistas de cada provincia se acerquen a su porcentaje (elección guía: balotaje 2023 + diputados 2025 sumados), con compacidad más baja (PP 25, departamentos 10, aristas 0,5) y un modelo de bancas casi determinístico (`election_win_prob_at_55` 0,9999, `swing_sigma` 0,005). No llega: el objetivo nacional es 113 bancas y el plan da 79 en la elección guía; ni el gerrymander peronista pasa de 100, porque en Córdoba, Mendoza, Santa Fe o Capital el voto peronista está repartido parejo y no alcanza para ganar distritos razonables.
- **Gerrymander peronista / LLA**: objetivo de todas las bancas (o ninguna) peronistas, peso 30, compacidad 5, departamentos 2, aristas 0,2 y temperatura inicial baja (0,002) para que el recocido no deshaga lo ganado.

### Respetando departamentos (`--deptos`)

Para que el mapa se lea y siga comunidades de interés, con o sin gerrymander. Cada departamento o partido con menos población que una fracción del distrito ideal es una unidad indivisible (fracción 1; si no hay plan posible, 0,5, 0,25 y 0 = radios sueltos); los grandes se cortan por radios. Tolerancia 5 %, departamentos partidos ×20 y sesgo de ReCom 20. Parte del plan de límites libres del mismo modo (cada unidad al distrito donde cae la mayoría de su población, con reparación de contigüidad) y baja el desvío con un trinquete: la tolerancia de cada paso es el peor desvío actual y nunca empeora; mientras haya distritos fuera de la tolerancia la mitad de los pasos recombinan uno de ellos.

## Todos los partidos

`construir_partidos.py` arma los votos de cada fuerza por radio (`radios_partidos.pkl`) con el mismo camino que los dos bloques: general 2023 con los cinco candidatos (UxP, LLA, JxC, Hacemos, FIT) llevada a los circuitos 2025 partido por partido (directo si el circuito es estable, el resto de la sección por padrón 2025, sin la corrección por desviación de los dos bloques), diputados 2025 con los 80 bloques del atlas 2025 (nombres y colores de `mapas/mapa2025/dataset_2025.json`) y reparto a los radios por población. En el mapa («Fuerzas → Todos los partidos») cada distrito lo gana la fuerza más votada, sin juntar a nadie; en la renovación por mitades UxP y Fuerza Patria cuentan como peronismo y la LLA de los dos años junta. Los distritos son los mismos: se dibujaron mirando dos bloques (o ninguno, el neutral).

## Resultados de los ocho primeros planes (cámara completa)

Bancas peronistas con dos bloques, y reparto con todos los partidos por separado (Per = UxP en 2023 / Fuerza Patria en 2025; IF Innovación Federal, PU Provincias Unidas, Neuq La Neuquinidad, PSJ Por San Juan).

| Plan | Límites | 2023 dos bloques | 2023 todos | Balotaje | 2025 dos bloques | 2025 todos |
|---|---|---|---|---|---|---|
| Neutral | libres | 53 | Per 139, LLA 89, JxC 26, Hacemos 3 | 74 | 86 | LLA 160, Per 83, IF 7, PU 3, Neuq 2, PSJ 2 |
| Proporcional | libres | 55 | Per 139, LLA 90, JxC 26, Hacemos 2 | 76 | 91 | LLA 157, Per 88, IF 5, PU 4, PSJ 2, Neuq 1 |
| Gerrymander peronista | libres | 65 | Per 148, LLA 81, JxC 26, Hacemos 2 | 87 | 102 | LLA 142, Per 98, IF 8, PU 4, Neuq 3, PSJ 2 |
| Gerrymander LLA | libres | 47 | Per 143, LLA 92, JxC 19, Hacemos 3 | 57 | 67 | LLA 184, Per 63, PSJ 4, PU 3, Neuq 2, IF 1 |
| Neutral | departamentos | 50 | Per 138, LLA 91, JxC 26, Hacemos 2 | 73 | 90 | LLA 160, Per 87, IF 4, PU 3, PSJ 2, Neuq 1 |
| Proporcional | departamentos | 54 | Per 141, LLA 88, JxC 26, Hacemos 2 | 78 | 88 | LLA 160, Per 84, IF 5, PU 4, Neuq 2, PSJ 2 |
| Gerrymander peronista | departamentos | 61 | Per 144, LLA 86, JxC 24, Hacemos 3 | 87 | 101 | LLA 144, Per 96, IF 8, PU 4, Neuq 3, PSJ 2 |
| Gerrymander LLA | departamentos | 45 | Per 147, LLA 85, JxC 23, Hacemos 2 | 62 | 74 | LLA 174, Per 72, PU 4, IF 3, Neuq 2, PSJ 2 |

Con la general 2023 por separado el peronismo gana la mayoría (138–148 de 257 con el 36,7 % de los votos) porque LLA y JxC se dividen. El gerrymander de LLA, dibujado contra un bloque LLA + JxC, le da a UxP más bancas que el neutral cuando ese bloque no existe: un gerrymander bipartidista falla si cambia el sistema de partidos. En PBA los planes con departamentos parten de más 21 (proporcional) a 61 (gerrymander peronista) departamentos: los gerrymanders necesitaron bajar a radios sueltos (fracción 0).

## Gerrymanders extremos (4-nov-2026, pedido del usuario)

Modos `peronista_extremo` y `lla_extremo` de `distritar.py` (con y sin `--deptos`), inspirados en los mapas actuales de Texas e Illinois: brazos del conurbano hacia el interior y distritos «sumidero». Sin compacidad (Polsby-Popper, aristas y, en límites libres, departamentos en 0): solo población (2 %) y contigüidad. Para evitar el *dummymander*, el modelo de bancas es probabilístico con oscilación: σ = √(swing² + σ₅₅²), con `election_win_prob_at_55` 0,9 y `UNI_SWING` 0,05 (peronista) u 0,08 (LLA: con 0,05 el plan de PBA daba 44 bancas a LLA pero, con 5 puntos a favor del peronismo, 56 al peronismo). Peso 100, temperatura 0,002, y en la segunda mitad pasos *flip* de radios sueltos (`flip_step_ig`, `flip_rate_curve`) además de ReCom. Los extremos de límites libres parten del gerrymander anterior; Buenos Aires peronista desde cero (`UNI_DESDE_CERO=1`, 400.000 iteraciones), porque desde el anterior se estancaba en un óptimo peor. Con departamentos: departamentos partidos ×20 (`UNI_MULT_D`) y desvío ×50.

Elección guía = balotaje 2023 + diputados 2025 sumados. «Firmes» = bancas que se conservan con 5 puntos en contra (uniforme).

| Plan | Límites | 2023 | Balotaje | 2025 | Guía per. | Per. firmes | LLA firmes | Margen mediano |
|---|---|---|---|---|---|---|---|---|
| Neutral | libres | 53 | 74 | 86 | 78 | 51 | 139 | 18,5 |
| Gerrymander peronista | libres | 65 | 87 | 102 | 100 | 49 | 129 | 16,0 |
| **Peronista extremo** | libres | 72 | 100 | 108 | 105 | 61 | 122 | 14,6 |
| Gerrymander LLA | libres | 47 | 57 | 67 | 56 | 45 | 149 | 18,8 |
| **LLA extremo** | libres | 43 | 59 | 72 | 54 | 42 | 153 | 19,6 |
| **Peronista extremo** | departamentos | 66 | 90 | 101 | 97 | 59 | 129 | 15,9 |
| **LLA extremo** | departamentos | 47 | 61 | 73 | 60 | 47 | 150 | 19,3 |

La ganancia en bancas es chica (+5 peronistas, −2 LLA respecto de los gerrymanders anteriores); lo que mejora es la solidez: el peronista extremo tiene 61 bancas que resisten 5 puntos en contra (49 antes). El techo lo pone la geografía: el voto peronista concentrado en el conurbano y repartido parejo en Córdoba, Mendoza, Santa Fe y Capital, y en Buenos Aires LLA con el 49,7 % de la guía.

## Límites por circuitos (`--circuitos`, 4-nov-2026, pedido del usuario)

Los planes de radios libres se veían demasiado dentados. Los mapas de Texas e Illinois siguen los *precincts*, así que esta versión sigue los circuitos electorales. Cada circuito con menos de 0,15 distrito ideal (`UNI_FRAC_C`) es una unidad entera; si así no se llega al 2 %, la escala baja a 0,075, 0,0375 y 0 (radios sueltos). Partir un circuito cuesta (excedente de circuitos partidos, peso `UNI_W_CIRC` 50 en la escala 0.1.0, sesgo de ReCom 20), así que solo se parte para emparejar población. Como los votos dentro de un circuito son uniformes por construcción, partirlo nunca da ventaja partidaria. Cada plan arranca del de límites libres del mismo modo; 30.000 iteraciones, tolerancia 2 %. Buenos Aires terminó con radios sueltos en los extremos (escala 0) y con circuitos de hasta 0,15 en los demás modos. Los departamentos dejan de penalizarse en esta versión. Salida en `plan_radios[_<modo>]_circ/`; `cola_circ.sh` corrió los cuatro modos no extremos. En el mapa: «Límites → Respetan circuitos».

| Plan | Circuitos partidos (libres → circuitos) | 2023 | Balotaje | 2025 | Guía per. | Per. firmes | LLA firmes |
|---|---|---|---|---|---|---|---|
| Neutral | 859 → 49 | 52 | 75 | 87 | 78 | 54 | 142 |
| Proporcional | 854 → 33 | 52 | 73 | 87 | 77 | 52 | 140 |
| Gerrymander peronista | 1.262 → 38 | 63 | 91 | 106 | 97 | 56 | 129 |
| Gerrymander LLA | 1.180 → 38 | 46 | 60 | 75 | 61 | 46 | 146 |
| Peronista extremo | 1.935 → 73 | 61 | 90 | 102 | 97 | 55 | 130 |
| LLA extremo | 2.070 → 66 | 45 | 60 | 80 | 62 | 44 | 150 |

De unos 6.300 circuitos se parten entre 33 y 73. Los gerrymanders pierden poco (peronista 100 → 97 en la guía; LLA 56 → 61). Con circuitos los extremos ya no superan a los comunes: la libertad de forma que los distinguía se pierde. Con 30.000 iteraciones son una sola corrida corta desde el plan libre; más iteraciones podrían recuperar algo.

## Departamentos y circuitos (`--deptos --circuitos`, 4-nov-2026, pedido del usuario)

Las dos cosas en jerarquía: cada departamento con menos de un distrito queda entero; dentro de los grandes, cada circuito de menos de 0,15 distrito también; el resto queda en radios. Se penalizan los departamentos partidos (Mosaic, peso `UNI_W_DEP` 50) y los circuitos partidos (término propio en `score_plan`, `UNI_W_CIRC` 50, misma escala). Si no se llega al 2 %, se aflojan primero los departamentos y los circuitos siguen en 0,15 hasta el final: (1, 0,15), (0,5, 0,15), (0,25, 0,15), (0, 0,15), (0, 0,075), (0, 0). Corte temprano: si el peor desvío no baja en 5.000 iteraciones (`UNI_STALL`), el escalón se abandona. Arranca del plan por circuitos; 30.000 iteraciones (`cola_dc.sh`; Buenos Aires rehecho con `cola_dc_pba.sh`, los seis modos en 5 minutos). Salida en `plan_radios[_<modo>]_dc/`. En el mapa: «Límites → Departamentos y circuitos».

Partidos = departamentos o circuitos repartidos entre más de un distrito (incluye los que por población tienen que partirse).

| Plan | Libres | Departamentos (5 %) | Circuitos | Deptos. y circuitos |
|---|---|---|---|---|
| Neutral | 859 circ. / 209 dep. · 78 | 563 / 89 · 72 | 49 / 244 · 78 | 149 / 112 · 76 |
| Proporcional | 854 / 230 · 79 | 599 / 102 · 77 | 33 / 244 · 77 | 106 / 107 · 74 |
| Gerrymander peronista | 1.262 / 330 · 100 | 870 / 141 · 95 | 38 / 270 · 97 | 132 / 118 · 85 |
| Gerrymander LLA | 1.180 / 311 · 56 | 818 / 124 · 59 | 38 / 268 · 61 | 135 / 119 · 67 |
| Peronista extremo | 1.935 / 405 · 105 | 1.172 / 122 · 97 | 73 / 346 · 97 | 195 / 121 · 89 |
| LLA extremo | 2.070 / 431 · 54 | 1.235 / 117 · 60 | 66 / 329 · 62 | 161 / 120 · 66 |

(circuitos partidos / departamentos partidos · bancas peronistas en la elección guía). Con 2 % de desvío parte tan pocos departamentos como la versión por departamentos al 5 %, y muchos menos circuitos; a cambio es la más atada, y los gerrymanders pierden margen (peronista 100 → 85). **Buenos Aires**: con la primera escala (que achicaba circuitos junto con departamentos) el conurbano cayó a radios sueltos y quedó dentado, y cada escalón fallido agotaba 300.000 iteraciones (unas 3 horas). Con la escala nueva y el corte temprano todos los modos mantienen circuitos de hasta 0,15 enteros salvo los extremos (0,075); departamentos enteros hasta 0,25 en el neutral y el gerrymander peronista, sin protección en los demás.

## Otras elecciones 2011-2023 (4-nov-2026, pedido del usuario)

`construir_elecciones.py` → `radios_elecciones.pkl` y `control_elecciones.json`: diputados 2011, 2013, 2015, 2017, 2019, 2021 y 2023; presidente 2011, 2015 y 2019; balotaje 2015; PASO presidenciales 2015 y 2023 (por precandidato). Fuente: `transferencias/circ_<clave>.pkl` (provisorios de la DINE por circuito). Diputados con los bloques de cada atlas (`mapeo_listas_<año>.csv`, 2013 vía `estimar.mapeo`) y su nombre y color; presidente con las categorías de `estimar.CAT` y la paleta de los mapas presidenciales. Fuerzas con menos de 0,5 % nacional y menos de 10 % en todas las provincias van a «Otros». Los votos de cada año pasan a los circuitos 2025 como en `construir_partidos.py` (directo si el circuito existe y el padrón cambió menos de 0,8-1,25; si no, la sección repartida por el padrón 2025) y de ahí a los radios por población. Se conserva el 99 % de los votos (99,9 % en 2023); circuitos directos: 35 % en 2011, 51 % en 2015, 77 % en 2021 y 91 % en 2023.

`mapa.py` escribe un JSON por elección en `elecciones_257/` (votos por distrito de los 24 planes; 4,4 MB en total) y la página lo carga al elegirlo en «Otras elecciones», sin engordar el HTML. Desde un archivo local no carga (el navegador bloquea `fetch` en `file://`): hay que abrirla publicada o con un servidor. Se puede pintar «Gana la más votada» o el porcentaje de una lista (pleno desde 60 %). Las elecciones ya presentes (general y balotaje 2023, diputados 2025) no se repiten. El sitio copia la carpeta (`sitio/catalogo.py`, `pages.yml`).

Los distritos se dibujaron con la población de 2022 y los dos bloques de 2023-2025; para comparar en serio con elecciones viejas habría que redibujarlos con el censo 2010 y las coaliciones de cada época (pendiente, pedido del usuario para más adelante).

### Mosaic 0.6.2

Desde el 4-nov-2026 `distritar.py` usa Mosaic 0.6.2 (≈20 veces más rápido; la 0.1.0 quedó en `mosaic_python-0.1.0`). Equivalencias para conservar los puntajes viejos: departamentos partidos → `weight_county_excess` + `weight_county_unified` (cada uno ÷10, con `county_data`), desvío de población ÷10. `dem_seats` ya no acepta un objetivo: el término cuadrático hacia el objetivo de bancas se arma aparte con `district_dem_shares` y `p_win_gaussian`. Los planes anteriores no se rehicieron.

## Renovación según la Ley Bases original

El proyecto 0025-PE-2023 (Ley Bases original, títulos de circunscripciones uninominales, arts. 443 a 450) divide cada distrito en tantas circunscripciones como diputados, por mayoría simple, y en el nuevo art. 162 del Código Electoral manda que «La Cámara de Diputados practicará el sorteo de las circunscripciones» que se eligen en la primera renovación parcial. El botón «Ley Bases (sorteo)» del mapa reemplaza la mitad por clase de Mosaic por ese sorteo: misma cantidad por provincia que la renovación real, circunscripciones elegidas al azar con semilla fija (`código de provincia × 1000 + 2023`), reproducible. No se aplicó su fórmula de bancas (art. 450, 1 cada 180.000 o fracción de 90.000 sin tocar los arts. 4 y 5 de la ley 22.847): leída al pie de la letra daría 331 bancas, no 257.

## Gerrymanders antiperonistas sobre 2011 y 2015 (ejercicio local, 5-nov-2026)

`UNI_GUIA=<clave>` hace que `distritar.py` dibuje con los votos reales de otra elección de `radios_elecciones.pkl`, por pluralidad: en cada distrito el FPV contra la fuerza más votada de las demás (todas las fuerzas, no la suma de la oposición). `UNI_INICIO` elige el plan de partida. Modo `lla_extremo` (a favor de quien se opone al peronismo), `--circuitos`, 2 %, `UNI_SWING` 0,05, desde `plan_radios_lla_extremo_circ`; cola `cola_anti.sh`, planes en `plan_g<clave>_lla_extremo_circ/`. Página local aparte: `UNI_ANTI=1 python mapa.py` → `mapa_257_antiperonista.html` + `elecciones_257_anti/` (no se publica; se abre con un servidor local).

Bancas del FPV (pluralidad; firmes = más de 55 % contra el segundo):

| Plan | Pres. 2011 (54,0 %) | Dip. 2015 (37,2 %) | Pres. 2015 (36,9 %) | Balotaje 2015 (48,6 %) |
|---|---|---|---|---|
| Neutral (circuitos) | 237 | 144 | 155 | 127 |
| LLA extremo (guía 2023-25) | 239 | 137 | 146 | 122 |
| Antiperonista guía 2011 | **229** | 140 | 150 | 127 |
| Antiperonista guía dip. 2015 | 237 | **115** (Cambiemos 129) | 132 | 112 |
| Antiperonista guía pres. 2015 | 236 | 120 | **125** (Cambiemos 115) | 109 |
| Antiperonista guía balotaje 2015 | 238 | 124 | 129 | **103** (Macri 154) |

33-58 circuitos partidos, como los demás planes por circuitos. 2011: con la oposición dividida el FPV gana casi todo y el dibujo solo le quita 8 bancas. 2015 general: el FPV pierde la mayoría propia (129) con cualquiera de las dos guías; en diputados Cambiemos queda primero (129 contra 115), sin mayoría. Balotaje: Macri pasa de 130 a 154. Cada plan rinde sobre todo en su propia elección.

2019 (Frente de Todos contra la más votada de las demás):

| Plan | Dip. 2019 (46,5 %) | Pres. 2019 (48,1 %) |
|---|---|---|
| Neutral (circuitos) | 161 | 168 |
| LLA extremo (guía 2023-25) | 159 | 170 |
| Antiperonista guía dip. 2019 | **133** (JxC 122) | 143 |
| Antiperonista guía pres. 2019 | 138 | **143** (JxC 114) |

58 y 67 circuitos partidos. El Frente de Todos conserva la mayoría propia con cualquiera de los dos dibujos: el mejor lo deja en 133 bancas, cuatro arriba de 129.

## Limitaciones

- Votos uniformes dentro de cada circuito (ver arriba). Para más detalle, `mapas/mapaAMBA2025radios/` prueba el método de Poblaciones/La Nación Data (votos por escuela repartidos a los radios por distancia inversa al cuadrado).
- Los distritos siguen radios, no calles ni límites municipales; los departamentos partidos se penalizan pero no se prohíben.
- La capa de circuitos es una composición aproximada (ver `geometria/circuitos_serie/LEEME.md`).
