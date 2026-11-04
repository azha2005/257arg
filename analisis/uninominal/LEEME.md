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

## Resultados de los ocho planes (cámara completa)

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

## Limitaciones

- Votos uniformes dentro de cada circuito (ver arriba). Para más detalle, `mapas/mapaAMBA2025radios/` prueba el método de Poblaciones/La Nación Data (votos por escuela repartidos a los radios por distancia inversa al cuadrado).
- Los distritos siguen radios, no calles ni límites municipales; los departamentos partidos se penalizan pero no se prohíben.
- La capa de circuitos es una composición aproximada (ver `geometria/circuitos_serie/LEEME.md`).
