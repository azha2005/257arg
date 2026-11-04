# Proyección del escrutinio provisorio con pocas mesas

## Elecciones provinciales (29-oct-2026)

Adaptador en [provincial/LEEME.md](provincial/LEEME.md): el mismo motor con una provincia, sus secciones electorales como unidad, sus estratos y el reparto de bancas provincial. Falta la PBA de septiembre de 2025 por mesa (pedido a graficarpba).

## Validación temporal y congelamiento (28-oct-2026)

Versión conservada en [congelado_20261028/LEEME.md](congelado_20261028/LEEME.md), con ZIP y manifiesto SHA256. El protocolo de PASO 2021 está en [paso2021_ciego/PROTOCOLO.md](paso2021_ciego/PROTOCOLO.md): selección con 2017, calibración con 2019, predicción con antecedentes 2019/2017 y resultado de septiembre de 2021 reservado para el evaluador. Se comparan 700 colecciones de 30 mesas, siete diseños, baselines y ablaciones. Las generales de noviembre de 2021 y elecciones posteriores no se admiten como entradas.

El aislamiento retrospectivo de datos no elimina el conocimiento de 2023/2025 usado para diseñar el método original. Las 1.000 remuestras anteriores y las nuevas colecciones de una misma elección no equivalen a otras tantas elecciones independientes. Israel aporta evidencia de transporte a otro sistema, pero su calibración no puede trasladarse automáticamente a Argentina. La prueba prospectiva con código fijado antes de una próxima elección sigue siendo necesaria.

Resultados terminados: [paso2021_ciego/RESULTADOS.md](paso2021_ciego/RESULTADOS.md). La selección temporal volvió a elegir λ=0,1 y calibró factor=1,5, sin tocar constantes con el destino. MAE del margen: azar 2,332 puntos; padrón por distrito 2,064; racimos 4,604; Twitter 3,683; Twitter parcial 3,689; circuitos pequeños 3,563; sesgo histórico 7,215. Supera a swing y al crudo ponderado en los siete diseños. La cobertura del margen con factor temporal va de 81 a 99 %, pero LIB en circuitos pequeños tiene solo 29 % de cobertura. Hay señal predictiva fuera de 2025 y fallos de incertidumbre que impiden afirmar calibración general. Se conservaron predicciones y parámetros sellados; la única enmienda del evaluador representa como ausentes las coberturas no calculadas de los baselines.

## Estado vigente: correcciones y backtests del 28-oct-2026

El informe actual es [validacion_20261028/RESULTADOS.md](validacion_20261028/RESULTADOS.md), con scripts, resultados por muestra y copia del código anterior. Las secciones posteriores conservan el desarrollo histórico; sus métricas y decisiones no sustituyen esta validación.

Se corrigieron la pérdida de mesas sin cruce histórico, los pesos AMBA/resto por fuerza en actas parciales, duplicados y contradicciones, la distinción entre votos desconocidos y cero, las frecuencias de primer puesto y la coherencia entre votos nacionales y bancas. El marco de electores de destino es común a los orígenes. La aguja masiva usa ahora **D sin benchmarking**, remuestrea el modelo completo y conserva los votos ya escrutados. El ICG queda desactivado; su prior predeterminado usa solo años anteriores y la opción retrospectiva se identifica aparte.

Se compararon 1.000 muestras por versión, cada una con 30 mesas de entrada: azar, tipo Twitter (20 AMBA/10 resto y racimos) y Twitter con actas parciales, en cuatro elecciones destino. La versión anterior retenía 28–30; la nueva conserva las 30. En diputados 2025 el error medio del margen pasa de 2,023 a 1,913 puntos al azar y de 2,895 a 2,868 tipo Twitter. Con parciales queda prácticamente igual (3,111 a 3,117), aunque el error medio por fuerza baja 5,3 %. No hay mejora uniforme en bancas ni en todos los márgenes.

Las 27 actas reales dan, con corrección provincial coherente con Congreso, LLA 41,55 %, FP 34,30 % y margen +7,25, frente a +7,05 del provisorio disponible. Proyectan 62/49/8/3/5 bancas para LLA/FP/PU/FIT/otras; la referencia es 64/47/8/3/5. La [evolución con fotos](img/aguja_fotos_2025.png) muestra el escenario **sin prior provincial**, con margen final +7,00.

**Límite medido:** las bandas siguen sin cubrir adecuadamente el estrés de selección extrema. En la prueba de la aguja 2023→2025, fuera de la calibración 2019→2023, la cobertura es 66,7 % para LLA y 41,7 % para OTRAS bajo ese orden. Son bandas nominales y frecuencias condicionales al modelo; no una garantía del 95 % para cualquier selección.

Para regenerar las actas reales y el Congreso:

```powershell
python -X utf8 proyeccion/proyectar_fotos.py proyeccion/fotos25/actas.csv --origen 2023p,2021bl --real 2025bl --congreso 2025
python -X utf8 proyeccion/aguja_fotos.py
```

Para otra elección, revisar catálogo y antecesores y proporcionar `--marco` (columnas `distrito_id,seccion_id,circuito,e`) y `--fuerzas`. Congreso requiere además padrón y listas del año. Pruebas: `python -X utf8 proyeccion/test_correcciones.py` (11 pasan). Comandos completos y reservas en el informe enlazado.

## Desarrollo histórico

Prueba con elecciones viejas de cómo proyectar el resultado final la noche de la elección a partir de las primeras
mesas que entran, pensada para 2027 (nacionales y provinciales). Surgió de mirar
[elecciones-peru.live](https://elecciones-peru.live/) y su código
([chubakueno/Elecciones2026](https://github.com/chubakueno/Elecciones2026)).

## Qué hace el sitio peruano (método A)

Leído en `proyectar_resultados.py` y `margen_error.py` (27-oct-2026):

- Distrito con algo contado: los votos se escalan por la fracción de actas contadas.
- Distrito sin actas: copia los votos por acta de los 2 distritos contados más cercanos (centroide, peso 1/distancia).
- No usa la elección anterior ni la primera vuelta. El «margen» es (diferencia entre los dos) / (votos que faltan),
  sin intervalo.

Acá se reproduce con la sección electoral de la DINE en lugar del distrito peruano y las mesas en lugar de las actas.
Los centroides de las secciones salen de los polígonos del atlas legislativo 2023 (`centroides.py`), porque los
locales de votación de la DINE no traen coordenadas.

## Métodos propios

- **B**: matriz de traspasos nacional (regresión de Goodman) ajustada con las mesas contadas contra el resultado de
  la misma mesa en la elección anterior. Cada mesa que falta = su resultado anterior × la matriz.
- **C**: B más una matriz por distrito encogida hacia la nacional y el residuo de las mesas contadas de la misma
  sección y circuito. El total nacional se lleva al de B (*benchmarking*), así que C solo cambia el reparto entre
  distritos.

Dos decisiones salieron de las pruebas:

1. **Matriz sin restringir.** Con las filas forzadas a ser proporciones (no negativas, suma 1), la matriz por
   distrito con pocas mesas queda sesgada: +0,65 puntos con 1 % de mesas en 2019 → 2023. Sin restricción, el sesgo
   de B es de 0,00 a 0,11 puntos.
2. **Benchmarking.** Las correcciones locales corrigen del todo las unidades con muchas mesas contadas y casi nada las
   chicas; si unas y otras se desvían en sentidos opuestos, el total se corre (−0,2 a +0,5 puntos con 1 % de mesas).
   Es el problema conocido de la estimación por áreas chicas, y la solución estándar es ajustar al total directo.

## Orden de llegada

Los archivos de la DINE no traen la hora de carga de cada mesa, así que el orden se simula:

- **azar**: todas las mesas al azar.
- **geo**: primero las secciones chicas y al final las grandes (conurbano, capitales), con ruido por distrito,
  sección, circuito y mesa. Es el patrón habitual, pero **no está calibrado con horas reales**.
- **sesgo**: el peor caso. Entran primero las secciones donde más saca el ganador.

## Resultados (27-oct-2026, 20 repeticiones por orden)

Error absoluto medio del % nacional del ganador, en puntos (B da lo mismo que C en el total nacional). Tablas
completas, con p90, error por distrito y distritos acertados, en cada `RESUMEN.md`.

| prueba | orden | mesas | crudo | A (Perú) | C |
|---|---|---|---|---|---|
| 1.ª vuelta → balotaje 2023 (mesa a mesa) | azar | 205 (0,2 %) | 0,78 | 0,74 | **0,13** |
| | azar | 1023 (1 %) | 0,45 | 0,21 | **0,09** |
| | geo | 1023 (1 %) | 2,80 | 2,26 | **0,49** |
| | sesgo | 1023 (1 %) | 20,05 | 16,10 | **1,86** |
| 1.ª vuelta → balotaje 2015 (mesa a mesa) | azar | 916 (1 %) | 0,30 | 0,20 | **0,11** |
| | geo | 916 (1 %) | 6,60 | 2,81 | **0,90** |
| | sesgo | 916 (1 %) | 24,25 | 20,06 | **0,91** |
| 2019 → general 2023 (por circuito) | azar | 916 (1 %) | 0,23 | 0,29 | **0,19** |
| | geo | 916 (1 %) | 4,89 | **2,14** | 3,55 |
| | geo | 4581 (5 %) | 3,21 | **0,82** | 2,50 |
| | sesgo | 916 (1 %) | 37,19 | 27,63 | **1,38** |

Lectura:

- **Dentro de la misma elección** (1.ª vuelta → balotaje, mismas mesas) la elección anterior lo resuelve casi todo:
  con 200 mesas al azar el error es de una décima, y aun con el peor orden queda en 1–2 puntos (A, 16–20).
  En distritos, C acierta el ganador en 23–24 de 24 con 1 % de mesas.
- **Entre años** (el caso de la primera elección de 2027, que se proyecta desde 2025): con mesas al azar C sigue
  siendo el mejor (0,19 con 1 %), pero si las secciones grandes llegan al final («geo»), **C queda peor que A** y
  con sesgo (−3,6 con 1 %, −2,5 con 5 %). El cambio de 2019 a 2023 fue muy distinto en las secciones grandes que en
  las chicas, y la matriz se aprende con las chicas. Con el mismo orden y mesas de la misma elección no pasa porque
  ahí el cambio es parejo.
- **Pendiente**: calibrar el orden «geo» con horas reales (capturas de resultados.gob.ar, si alguien las guardó, o
  las que grabemos en las provinciales de 2027).

### Método D: tamaño de sección y circuito (27-oct-2026)

D = C con la matriz nacional dependiente del log de electores de la sección y del circuito (interacciones con el
origen, encogidas a 0 con el peso de N0S = 400 mesas). Se probaron también solo la sección, cuatro estratos de
sección y N0S de 2 a 1500. Con N0S chico, D extrapola de más cuando las secciones grandes todavía no tienen mesas y
empeora la misma elección; 400 es el mejor punto medio. Se agregó el orden **geo_circ** (el retraso lo manda el
tamaño del circuito) para no probar solo con la variable que el modelo ya conoce.

Error absoluto medio del % nacional (20 repeticiones):

| prueba | orden | 1 % | 5 % | 25 % |
|---|---|---|---|---|
| 2019 → 2023 | geo | A 2,14 · C 3,55 · **D 3,33** | A 0,82 · C 2,50 · **D 1,64** | A 0,39 · C 1,19 · **D 0,66** |
| | geo_circ | A 1,41 · C 2,18 · **D 1,67** | A 0,48 · C 1,37 · **D 0,92** | A 0,23 · C 0,60 · **D 0,46** |
| 2023 balotaje | geo | A 2,26 · C 0,49 · **D 0,70** | A 0,93 · C 0,34 · **D 0,54** | A 0,29 · C 0,17 · **D 0,22** |
| 2015 balotaje | geo_circ | A 2,56 · C 1,11 · **D 0,96** | A 0,90 · C 0,78 · **D 0,56** | A 0,35 · C 0,46 · **D 0,25** |

Con mesas al azar D = C en todas las pruebas. Entre años D mejora a C, pero **A sigue siendo mejor con orden «geo»**:
copia el cambio de las secciones vecinas, y el cambio de 2019 a 2023 fue regional además de por tamaño. Siguiente
paso: para las secciones sin mesas contadas, tomar el residuo de las secciones vecinas contadas (lo que el Estadão
llama «tipo de lugar»). El Estadão además usa dos elecciones anteriores a la vez (2.º turno 2022 y 1.º turno 2026);
acá sería sumar las columnas de las dos elecciones de origen.

### Aguja (`aguja.py`)

Repite una elección pasada con un orden simulado y la muestra como la del Estadão: escrutado (línea llena),
proyección en cada momento (línea fina), escrutado esperado de ahí al 100 % (punteada) y banda del 95 % con la
probabilidad de salir primero. La línea punteada no es ilustrativa: ordena las mesas que faltan por lo avanzada
que está su sección (encogida hacia el distrito) y acumula su voto proyectado.

La banda suma dos cosas: el bootstrap de los circuitos contados, que solo mide el azar de qué mesas entraron, y un
error sistemático por el orden de llegada, a·(1−f)·f^−b con f = fracción contada. Ese término está ajustado con el
p95 de los errores de D en los órdenes geo y geo_circ: a = 0,52 y b = 0,20 dentro de la misma elección; a = 0,60 y
b = 0,32 entre años. Solo con el bootstrap, la banda contenía el resultado el 95–100 % de las veces con mesas al
azar, pero el 16–67 % con los órdenes sesgados.

Cobertura de la banda del 95 % con el término sistemático (`aguja.py --cobertura`, 6 repeticiones por orden):

| orden | 2023 balotaje | 2019 → 2023 |
|---|---|---|
| azar | 100 % (sobra: ~4 veces más ancha de lo necesario) | 100 % (ídem) |
| geo | 100 % | 84–100 % |
| geo_circ | 100 % | 89–100 % |
| sesgo (peor caso) | 100 % | 100 % hasta el 5 %; después 0–36 % |

Es conservadora a propósito, porque la noche de la elección no se sabe en qué orden llegan las mesas; en
`PLAN_MEJORAS.md` está cómo achicarla cuando lo contado se parece al total. El término sistemático está ajustado con
los mismos órdenes simulados con que se mide: no es una prueba fuera de muestra.

```
python proyeccion/aguja.py 2023p 2023b --orden geo
python proyeccion/aguja.py 2019p 2023p --circuito --orden geo
python proyeccion/aguja.py 2023p 2023b --cobertura
```

Capturas en `img/`.

### Mesas y circuitos testigo (`testigos.py`)

- **Mesa por mesa no hay testigo**: una mesa tiene unos 300 votantes y se mueve ±3 puntos solo por azar. Las 1000
  mesas más parecidas al país en la 1.ª vuelta 2023 quedaron a 3,1 puntos del nacional en el balotaje (todas: 11,1).
  Sumadas, en cambio, dieron 44,58 % contra 44,31 % real.
- **Circuitos elegidos con 2011–2019, probados en 2023**: los 50 más parecidos al país dieron el % peronista con
  error de 0,05 (general) y 0,32 (balotaje); el parecido persiste (Spearman 0,65). Pero es una sola selección y con
  otros N el error sube a 2–4 puntos; el «swing testigo» no persiste (0,1–0,2).
- **Para la noche electoral sirve más el modelo con lo que entre**: 50 circuitos al azar + swing desde 2019 erran
  0,8–0,9 puntos, y C con mesas al azar, una décima. Los testigos no llegan cuando uno quiere.

### Pocas fotos de actas (`fotos.py`, 300 repeticiones)

Error absoluto medio del % nacional del ganador con D (proyección nacional), según cómo se eligen las mesas:

| selección | 2023 balotaje, 50 mesas | 2019 → 2023, 50 mesas |
|---|---|---|
| al azar | 0,41 (crudo 1,65) | 0,88 (crudo 1,63) |
| sesgo de nivel (fotos de mesas donde gana fuerte el ganador) | 0,79 (crudo 11,76) | 2,14 (crudo 17,31) |
| sesgo de cambio mitad y mitad (cada partido sube donde le fue mejor de lo esperado) | 4,62 | 1,13 |
| sesgo de cambio de un solo lado | 12,86 | 6,51 |

Con 25 y 100 mesas, mismas conclusiones (al azar: 0,62 y 0,27 en 2023). El modelo corrige el sesgo de nivel
porque sabe cómo votó antes cada mesa; el sesgo de cambio no lo puede corregir, y la banda tampoco lo cubre. La
intensidad del sesgo simulado (peso exp(z) sobre el residuo de cada mesa) es un supuesto.

## Archivos

| Archivo | Qué hace |
|---|---|
| `mesas.py` | tabla ancha por mesa desde los zip de la DINE → `mesas_<elección>.pkl` |
| `centroides.py` | centroide de cada sección → `centroides_secciones.csv` |
| `backtest.py` | la prueba → `<origen>_<destino>[_circuito]/RESUMEN.md` y `corridas.csv` |
| `testigos.py` | circuitos y mesas testigo → `testigos/RESUMEN.md` |
| `aguja.py` | repetición con aguja → `aguja_<origen>_<destino>_<orden>.html`; `--cobertura` → `cobertura_*.csv` |
| `fotos.py` | proyección con 25–100 mesas elegidas con distintos sesgos → `fotos_*.csv` |
| `PLAN_MEJORAS.md` | modelos parecidos, cómo llegan los datos en Argentina y qué sigue |

```
python proyeccion/mesas.py 2023p 2023b 2015p 2015b
python proyeccion/centroides.py
python proyeccion/backtest.py 2023p 2023b
python proyeccion/backtest.py 2015p 2015b
python proyeccion/backtest.py 2019p 2023p --circuito
python proyeccion/testigos.py
```

Cada corrida tarda unos 2 minutos con un solo proceso.

## Fotos de actas 2025 con solo los datos de 2023 (`fotos25.py`, 27-oct-2026)
Las fotos que juntó el usuario en `fotos25/` (22 archivos, 29 mesas ubicadas: 10 de un tuit de Villa Lynch con solo
LLA y FP) transcriptas a mano en `FOTOS`, controladas contra el provisorio (`fotos25/control_transcripcion.csv`) y
proyectadas con el presidente 2023 por circuito como origen. Cada columna de destino se ajusta con las mesas donde se
conoce, con una regresión de Goodman encogida hacia el swing uniforme (`lam`). Resultado en `fotos25/RESUMEN.md`:
swing uniforme o Goodman con `lam=1` dan LLA 43,1–43,4 / FP 35,1–35,2 contra 40,7 / 33,6 real (margen +0,9 a +1,3 puntos);
Goodman sin encoger no sirve con tan pocas mesas. PU y las listas provinciales salen bajas porque no hay fotos de
Córdoba ni Santa Fe. Con 28 mesas al azar en todo el país el error medio de LLA y FP es 1,4–1,5 puntos; al azar solo
en el conurbano, 3,3 a 4,1.

## Método E y orden «capital primero» (`backtest.py`, 27-oct-2026)
- **Orden `capital`**: en cada distrito la sección más grande carga primero y el interior después (el caso de
  Tucumán capital al 90 % con el interior al 20 %).
- **E**: D más el residuo de las 3 secciones contadas más cercanas del mismo distrito, prestado a las secciones sin
  mesas contadas (peso 1/(distancia + 5 km), encogido con K). Con el ajuste del total nacional al de la matriz
  (benchmarking) E da exactamente lo mismo que D, porque el ajuste anula el cambio. Por eso se prueba también
  **sin ajuste** (`E_sin_ajuste`, y `D_sin_ajuste` para separar los dos efectos).
- Error absoluto medio del % del ganador, promedio de los cortes 0,5–25 % y de los cinco órdenes, 20 repeticiones:

| Par | A | D | D sin ajuste | E sin ajuste |
|---|---:|---:|---:|---:|
| 2023 1.ª vuelta → balotaje | 3,61 | 0,55 | 0,44 | **0,40** |
| 2015 1.ª vuelta → balotaje | 4,24 | 0,74 | 0,58 | **0,52** |
| 2019 → 2023 por circuito | 4,91 | 1,29 | 1,00 | **0,92** |

  Casi todo lo que se gana viene de sacar el ajuste: con las covariables de tamaño (D) ya no hace falta, y al
  azar E sin ajuste no tiene sesgo (≤0,1 punto desde 0,2 % de mesas). Con «capital» al 5 %: 0,19 / 0,46 / 0,75
  contra 0,37 / 1,22 / 1,20 de D. Lo que E no arregla: 2019 → 2023 con orden «geo» y ≤1 % de mesas (2,5–3,7
  puntos, peor que A con 2,1–2,8), porque el cambio regional de un año a otro no se ve hasta que entran las
  secciones grandes. El promedio fijo A + E empeora en todos los demás casos: si se combinan, los pesos tienen
  que aprenderse en la noche (ver `PLAN_MEJORAS.md`).
- `aguja.py` sigue con D y el ajuste: falta pasarla a E sin ajuste y recalibrar la banda.

## Variantes probadas con las fotos 2025 (27-oct-2026)
Swing proporcional en PU y FIT, swing por provincia encogido (k = 5) y el balotaje 2023 como origen: ninguna mejora
(ver `fotos25/RESUMEN.md` y `fotos25/RESUMEN_2023b.md`; con el balotaje el margen LLA−FP sale +6 puntos). Con ~30
mesas el límite es el ruido de muestreo (1,4 puntos aun al azar) y la cobertura (sin fotos de Córdoba ni Santa Fe,
PU y las listas provinciales salen bajas), no la forma del modelo.

## Fotos de actas: modelo calibrado y herramienta para la noche (27-oct-2026)
**Uso (la noche de la elección):** cargar las actas en un CSV y correr
`python proyeccion/proyectar_fotos.py actas.csv --origen 2023p,2025bl` (en 2027: promedio de la última presidencial
y la última legislativa; antes, revisar `ANTECESORES` con los bloques que se presenten). El CSV lleva una fila por
acta y fuerza: `foto, distrito_id, seccion_id, circuito, mesa, completa, bloque, votos` (circuito vacío si la foto no
lo muestra; `completa = no` para tuits que dan solo algunas fuerzas; `bloque = BLANCO` o `NULO` para esos votos).
Ejemplo: `fotos25/actas.csv`. Sale `<csv>_proyeccion.md` con la proyección, la banda, la probabilidad de que gane el
primero y de qué regiones faltan actas.

**Modelo** (`fotos_modelo.py`): cada acta contra su circuito (o su sección) en la elección de origen; Goodman por
fuerza encogido hacia el swing uniforme (λ = 0,1), con las actas repesadas para que el AMBA y el resto del país pesen
lo que pesan en el padrón (el AMBA es el 29 %). Banda: bootstrap de circuitos × 1,4.

**Cómo se eligió** (`fotos_sim.py`, `fotos_sim2.py`, resultados en `fotos_sim/RESUMEN.md`): colecciones simuladas
de 25 a 100 actas en cinco pares (presidente 2019 y diputados 2021 → presidente 2023, presidente 2023 → diputados 2025,
1.ª vuelta → balotaje 2023 y 2015), con cuatro esquemas: al azar, repartidas por provincia según el padrón, de a 3 por
local y «Twitter» (65 % del AMBA); y uno armado como las fotos de 2025 (25–35 actas, 2/3 del AMBA, un racimo de 10 y
dos de 3), 1000 veces cada uno, para no ajustar el método a las fotos que hay.
- Lo que más pesa es **de dónde vienen las actas**. Repartidas por provincia, 50 actas dan ±0,9–1,3 puntos de error
  del margen. Las de Twitter sin corregir sesgan el margen 2 a 5 puntos, y el sesgo no baja con más actas.
- **Repesar AMBA / resto** saca ese sesgo (de +2–5 a <1 punto) y baja el error a la mitad en los pares entre años.
  Al azar no cambia nada; en el balotaje 2023 empeora un poco (1,12 → 1,30 con 50). Repesar por ocho regiones
  corrige menos: con 25–50 actas los pesos por región son muy ruidosos.
- **Goodman con λ = 0,1** le gana al swing uniforme en los cinco pares. El swing por provincia, el swing proporcional
  y λ = 1 no mejoran.
- **Dos orígenes promediados**: el error baja un 5 % hacia 2023 y un 10–20 % hacia 2025, porque los sesgos de los
  dos orígenes van en sentidos opuestos.
- Con ~30 actas armadas como las de 2025 el error típico del margen es de 2,7–3,1 puntos (1,9 si fueran al azar). El
  bootstrap solo cubre el 84–88 % de las veces; por eso se multiplica × 1,4.
- **Fotos 2025 con la herramienta** (solo lo que se ve en cada foto, electores de la mesa estimados con 2023):
  margen +9,0 con origen 2023p y +7,3 con 2023p + 2021bl; el real fue +7,1. Que este caso dé casi exacto es suerte:
  lo esperable es ±3.

**Qué fotos juntar** (lo que más mejora la proyección): pocas por local y repartidas como el padrón. Para 50 actas,
más o menos: AMBA 15, Córdoba + Santa Fe + Entre Ríos 10, interior de Buenos Aires 7, NOA 6, NEA 5, Cuyo 4,
Patagonia 3. Sin actas del Centro, PU y las listas provinciales salen bajas (en 2025: PU 4,6 contra 7,7).

`bloques.py <año>` deja diputados en bloques por mesa y por circuito (`mesas_<año>bl.pkl`, `circ_<año>bl.pkl`), para
usarlos de origen o destino; hecho para 2021 y 2025.

## ~30 actas de Twitter: variantes del modelo (`fotos_tw.py`, 28-oct-2026)
Colecciones de 30 actas «como25» (25–35 actas, 2/3 del AMBA, un racimo de 10 y dos de 3) y «twitter» (racimos de 3,
65 % del AMBA), con 500 colecciones en cada uno de los cinco pares (`fotos_sim/tw_*.csv`). Variantes sobre el modelo
actual (Goodman λ = 0,1 encogido al swing uniforme, repesado AMBA / resto):
- λ = 0,03 o 0,3;
- bajar el peso de los racimos: cada acta dividida por (actas de su circuito)^a, con a = 0,5 o 1;
- tres estratos (AMBA / interior de Buenos Aires / resto);
- Goodman robusto con pesos de Huber.

Error absoluto medio del margen, promedio de los cinco pares:

| Variante | como25 | twitter |
|---|---:|---:|
| Huber | **2,22** | **2,78** |
| Actual | 2,24 | 2,83 |
| λ = 0,03 | 2,25 | 2,89 |
| 3 estratos | 2,26 | 2,84 |
| λ = 0,3 | 2,29 | 2,87 |
| Racimo a = 0,5 | 2,55 | 2,83 |
| Racimo a = 1 | 2,89 | 2,83 |

- **La forma del modelo ya no es el límite.** Todas las variantes razonables quedan a ±0,05 del modelo actual.
- **Bajar el peso de los racimos empeora.** El racimo de 10 mesas aporta información y no conviene descontarlo.
- **Huber gana muy poco** (0,02–0,05 en el margen) y empeora el error medio por fuerza en «como25» (1,15 → 1,18).
  No se pasa a `proyectar_fotos.py`. Sí conviene si se sospecha una foto mal transcripta.
- **Lo que sí mueve el error es de dónde vienen las actas.** Las mismas 30 al azar dan ~1,9 de margen contra 2,2–2,8
  de las de Twitter. Dos orígenes promediados bajan un 5–20 % más (ya está en la herramienta).
- **Para la noche:** usar la herramienta como está (`--origen 2023p,2025bl`) y pedir o buscar actas de Córdoba, Santa
  Fe, el interior de Buenos Aires y el NOA hasta acercarse al reparto del padrón.

## Cámara de Diputados con las fotos (`congreso.py`, `proyectar_fotos.py --congreso <año>`, 28-oct-2026)
```
python proyeccion/proyectar_fotos.py actas.csv --origen 2023p,2025bl --congreso 2027
```
Además del informe, escribe `<csv>_congreso.html` con:
- el hemiciclo de las bancas que se renuevan;
- el de la cámara completa (257, mayoría 129);
- un mapa por provincia con la fuerza más votada (Capital ampliada; el detalle aparece al pasar el puntero);
- al final, la tabla nacional (% y banda; bancas, banda del 90 %, las que no se renuevan, cámara) y la tabla por
  distrito.

Cómo se arma:
- **Proyección por distrito:** los mismos coeficientes de Goodman de la proyección nacional, aplicados al origen de
  cada distrito (`fotos_modelo.goodman(..., natd=...)`) y promediados entre los dos orígenes.
- **Reparto de bancas:**
  - D'Hondt por distrito, con el umbral del 3 % del padrón;
  - bancas por distrito de la tabla de la Wikipedia (127 en 2025, 2021…; 130 en 2023, 2027…);
  - OTRAS se parte entre las listas menores **oficializadas** del distrito (se cuentan, no se miran sus votos) con un
    perfil de Zipf: la k-ésima lista saca ∝ k^−1,6 (`congreso.ZIPF`, exponente ajustado en 2021; en 2019 da 1,05).
    Sin el mapeo de listas del año (2027 antes de oficializar) se usa el número de listas de cuatro años antes;
  - banda: 300 remuestras por bootstrap de circuitos, ensanchadas × 1,4 como la nacional.
- **Electas en la elección de referencia:** D'Hondt sobre `mapas/mapa<año>/mapeo_listas_<año>.csv`. Reproduce
  exactamente la ficha de la Wikipedia de 2025: LLA 64, FP 47, PU 8, FIT 3 y 5 de otras fuerzas.
- **Bancas que no se renuevan:** en 2025, los bloques **de la cámara** antes del 10 de diciembre, no las alianzas de
  2023 (Juntos por el Cambio ya estaba partido en PRO, UCR, Democracia para Siempre, Coalición Cívica, Encuentro
  Federal...). Salen de la tabla «Bancas por bloque» de la última revisión del artículo anterior a esa fecha
  (`datos/wikileg/revisiones/wleg2025_rev170886514.txt`, `congreso.REVISION`): totales menos las que se renovaban,
  130 en total. Para un año sin revisión guardada, las electas hace dos años por alianza.
- **Hemiciclo:** disposición en arco del generador de diagramas de la Wikipedia (Parliament diagram tool,
  ArchDiagram), con las bancas ordenadas por ángulo y los colores de los atlas legislativos. Con más de 8 bloques la
  leyenda va más chica.

**Partir OTRAS.** La primera versión repartía OTRAS en proporción a las listas menores de la legislativa anterior.
En 2023 casi no hubo listas menores (las cinco alianzas cubrían casi todo), así que OTRAS quedaba casi entera en una
sola lista. Con los votos reales de 2025 por distrito, sin proyectar nada, esa regla daba 16 bancas provinciales
(reales: 5) y 11 bancas mal asignadas. Con los mismos votos reales:

| Regla para partir OTRAS | LLA | FP | PU | FIT | Otras | Mal asignadas |
|---|---:|---:|---:|---:|---:|---:|
| listas menores de 2023 (antes) | 58 | 45 | 6 | 2 | 16 | 11 |
| listas menores de 2021 | 60 | 46 | 7 | 2 | 12 | 9 |
| partes iguales entre las oficializadas | 65 | 50 | 9 | 3 | 0 | 5 |
| **Zipf 1,6 sobre las oficializadas** | 63 | 47 | 8 | 2 | 7 | **2** |
| reparto real de 2025 | 64 | 47 | 8 | 3 | 5 | 0 |

Las dos que quedan son de Buenos Aires: OTRAS tenía 11 listas y estaba más repartido de lo que supone el perfil.
Los nombres de las listas casi nunca se repiten entre elecciones, así que no sirve usarlos como prior.

**Prueba con 30 mesas al azar** (`congreso_sim.py`, 28-oct-2026, 40 colecciones por esquema, origen
2023p + 2021bl). Mesas reales de 2025 armadas como el CSV de fotos: «azar» (30 del país) y «twitter» (25 a 35,
2/3 del AMBA, un racimo de 10 y dos de 3). Salida en `fotos_sim/congreso_sim.csv`; con la regla vieja en
`fotos_sim/congreso_sim_regla_vieja.csv`.

| Fuerza (real) | Azar: media | Error abs. | Cubre banda 90 % | Twitter: media | Error abs. | Cubre banda 90 % | Regla vieja (azar) |
|---|---:|---:|---:|---:|---:|---:|---:|
| LLA (64) | 65,8 | 2,6 | 95 % | 66,2 | 3,2 | 90 % | 60,6 |
| FP (47) | 49,2 | 2,5 | 92 % | 49,0 | 2,8 | 92 % | 46,3 |
| PU (8) | 5,6 | 2,5 | 57 % | 6,0 | 2,6 | 62 % | 5,1 |
| FIT (3) | 2,0 | 1,0 | 90 % | 1,9 | 1,1 | 90 % | 1,7 |
| Otras (5) | 4,4 | 1,8 | 92 % | 3,9 | 2,2 | 90 % | 13,3 |

- LLA sale primera en las 80 colecciones.
- La diferencia LLA − FP promedia +16,6 y +17,2 bancas (real +17); con la regla vieja daba +14,3.
- Provincias Unidas queda corta (−2 a −2,5) y su banda la cubre poco: su voto está concentrado en Córdoba, Santa Fe,
  Corrientes, Jujuy y Chubut, y 30 mesas casi nunca caen ahí.
- (Ver abajo «Fuerzas de los gobernadores»: con esa tabla PU deja de quedar corta.)
- Con las 27 actas reales, la regla vieja daba Otras 8 por suerte: subestimaba la proyección de OTRAS en los
  distritos provinciales y el error de partirla se compensaba. Con Zipf da LLA 66 (62–72), FP 53, PU 4, FIT 3 y
  Otras 1 (reales: 64, 47, 8, 3 y 5).

### Fuerzas de los gobernadores (`provinciales.csv`, solo legislativas, 28-oct-2026)
La proyección por distrito no ve a los partidos de los gobernadores. Con las 27 actas, OTRAS daba 21 % en Misiones
(real 52), 18 en Neuquén (49), 21 en Salta (40) y 6 en San Juan (36); PU, que en 2025 eran sobre todo alianzas de
gobernadores, daba 1 % en Corrientes (34), 2 en Chubut (20) y 3 en Jujuy (20). La legislativa anterior no sirve de
prior: esos partidos cambian de envase (Sáenz fue dentro del Frente de Todos en 2021 y de UxP en 2023; La Neuquinidad
no existía).

**Regla.** `provinciales.csv` tiene, por distrito, la fuerza del gobernador en la elección que se proyecta:
- una lista propia «PROV:<nombre>» (sale de OTRAS) o una columna proyectada (PU);
- el patrón del nombre de la lista en las actas;
- el % del gobernador en su última elección, que es anterior a la noche (Corrientes 2025 fue en agosto).

Nivel esperado = retención × % del gobernador. La retención (0,53) es el promedio de % legislativo / % gobernador en
las filas de años anteriores. Es decir, 2021 sobre 2019: Misiones 0,51, Neuquén 0,73, Río Negro 0,71, Córdoba 0,44 y
Chubut 0,24. Los porcentajes de gobernador salen de las fichas de la Wikipedia
(`herramientas/bajar_gobernadores_wiki.py` → `datos/gobernadores_wiki/`).
- Si hay actas del distrito, el nivel se mezcla con lo que muestran, con 3000 votos de pseudoconteo (`K_FOTOS`).
- El voto se saca primero de OTRAS; si el gobernador fue aliado de una fuerza en la elección anterior (`toma_de`:
  FP en Misiones, Salta y Tierra del Fuego, aliados de UxP en 2023), hasta la mitad de lo que falta sale de ella; el
  resto, de todas en proporción.
- En las remuestras, la retención de cada distrito se sortea con la dispersión relativa de la calibración (38 %),
  así la banda cuenta el error del prior.
- No se usa en la proyección presidencial: con la boleta de presidente esos partidos casi no compiten.

Prior contra real en 2025 (% del distrito): Misiones 34 / 30, Neuquén 19 / 32, Río Negro 22 / 26, Salta 25 / 33,
San Juan 26 / 31, Tierra del Fuego 34 / 21, Córdoba 24 / 28, Corrientes 27 / 34, Chubut 19 / 20, Jujuy 26 / 20,
Santa Cruz 18 / 16, Santa Fe 31 / 18. El error medio es 6,5 puntos; la proyección sin la tabla erraba unos 20.

**Bancas, 30 mesas al azar** (`congreso_sim.py`, 40 colecciones; error absoluto medio, entre paréntesis el error
medio con signo):

| Fuerza (real) | Sin tabla | Con tabla, proporcional | Con tabla y `toma_de` | Cubre banda 90 %: sin → con |
|---|---:|---:|---:|---:|
| LLA (64) | 2,6 (+1,8) | 3,9 (−3,9) | 3,0 (−3,0) | 95 → 95 % |
| FP (47) | 2,5 (+2,2) | 1,6 (+0,4) | 1,6 (−0,6) | 92 → 100 % |
| PU (8) | 2,5 (−2,4) | 1,9 (+1,9) | 1,9 (+1,9) | 57 → 98 % |
| FIT (3) | 1,0 | 1,0 | 1,0 | 90 → 90 % |
| Otras (5) | 1,8 (−0,6) | 2,8 (+2,7) | 2,8 (+2,7) | 92 → 95 % |

El error sumado de las cinco fuerzas casi no cambia (10,4 → 10,3 bancas). Lo que cambia es de dónde viene:
- sin la tabla, los errores de distritos con gobernador fuerte se compensaban entre sí;
- con la tabla, esos distritos quedan bien (Misiones, Salta, Neuquén, San Juan, Corrientes) y las bandas cubren;
- lo que queda es Buenos Aires (OTRAS con 11 listas: el perfil de Zipf le da 1,5 bancas de más a las chicas y se las
  saca a LLA) y el prior alto de Santa Fe y Tierra del Fuego.

Con las 27 actas reales: LLA 62, FP 49, PU 8, FIT 3, Otras 5 (reales 64, 47, 8, 3, 5): 2 bancas mal asignadas, contra
8 sin la tabla.

**Para 2027:** agregar las filas de 2027 a `provinciales.csv` (la fuerza del gobernador en cada distrito, el % de su
última elección y, si fue aliado de una fuerza nacional en 2025, `toma_de`). La calibración pasa a usar también 2025.

## El ICG de la UTDT como prior del oficialismo (`icg/`, 28-oct-2026)
Informe completo en `icg/icg_prior.html` (`python -X utf8 proyeccion/icg/informe_icg.py`).

**Datos.** Serie y microdatos de la Escuela de Gobierno de la UTDT, en `datos/icg/`. Son unas 317 mil entrevistas
desde noviembre de 2001, con fecha y ciudad. Los microdatos reproducen la serie publicada (correlación 0,9995). La
planilla bajada de la web y la de Descargas tienen los mismos valores.

**Ajuste** (`icg/icg_voto.py`, `icg/elecciones.csv`). Variable a explicar: voto al oficialismo en las 12 elecciones
nacionales de 2003 a 2025 (1.ª vuelta o diputados). El ICG del mes anterior correlaciona 0,78. Error dejando una
elección afuera:

| Prior | Error medio |
|---|---:|
| ICG del mes anterior + presidencial, sin 2003 | **3,8** |
| ICG del mes de la elección + presidencial | 4,1 |
| Ventana de 45 a 7 días antes + presidencial | 4,0 |
| Solo presidencial | 6,0 |
| Promedio histórico | 5,3 |

El mes anterior es el mejor, como dijo el usuario. Los peores años: 2011 (−7), 2015 (+6), 2017 (+6) y 2025 (−5,2:
prior 35,4 contra 40,7).

**Mezcla con las fotos** (`icg/icg_fotos.py`). Oficialismo = w × prior + (1 − w) × fotos; las demás fuerzas en
proporción. w = σ²fotos / (σ²fotos + σ²prior), de 0,05 (al azar) a 0,17 (tipo Twitter).

En 300 colecciones de 30 actas por par (error medio del oficialismo, fotos → fotos + ICG):

| Par | Azar | Twitter |
|---|---|---|
| 2019p → 2023p | 0,99 → 0,95 | 1,68 → 1,51 |
| 2021bl → 2023p | 1,09 → 1,04 | 1,93 → 1,66 |
| 2023p → 2025bl | 1,09 → 1,06 | 2,38 → 1,96 |

El margen también mejora en Twitter: 3,2 → 3,0, 3,8 → 3,4 y 3,25 → 2,98.

**En las bancas de 2025** (`congreso_sim.py --icg`) empeora LLA: −3,0 → −3,8 al azar y −2,4 → −4,0 tipo Twitter. El
prior quedó bajo y las bancas ya subestimaban a LLA.

**Las 27 actas:**
- LLA pasa de 43,0 a 41,7 (real 40,6);
- el margen LLA − FP empeora: de 7,3 a 5,1 (real 7,0);
- bancas: LLA 62 → 60, PU 8 → 9 y Otras 5 → 6 (reales 64, 8 y 5).

**Lectura.** Sirve como prior antes de que haya fotos, y para corregir un poco las colecciones sesgadas. Pero su error
(~4 puntos) es mucho mayor que el de 30 actas (1–2), así que su peso queda chico. Cuando el prior erra como en 2025,
el reparto proporcional le pasa votos al segundo y achica el margen. No se activó por defecto en `proyectar_fotos.py`.
No se probó en `backtest.py` (conteo de la noche): con más del 1 % de mesas el peso del prior sería todavía menor.
