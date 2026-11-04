# Plan para afinar la proyección (27-oct-2026)

## Actualización del 28-oct-2026

Implementación y resultados: [validacion_20261028/RESULTADOS.md](validacion_20261028/RESULTADOS.md). Con la autorización posterior de aplicar las correcciones pertinentes, se completaron el universo de evaluación, pesos por fuerza, control de identidad, datos ausentes, votos/bancas compartidos y remuestreo completo. La aguja pasa a D sin benchmarking; el punto 5 histórico de abajo queda reemplazado por esta decisión y su medición. ICG sigue desactivado.

Medidos: 30 mesas al azar y tipo Twitter, actas parciales, 27 actas reales, bancas y cobertura fuera de calibración. Pendientes: resolver la subcobertura bajo selección extrema, validar en más elecciones independientes, mejorar el prior provincial y el reparto de fuerzas menores sin ajustarlos al resultado de 2025, e incorporar horas de llegada observadas. No se afirma mejora uniforme de precisión ni calibración universal del 95 %.

Resultado de buscar modelos parecidos. El punto de partida es `LEEME.md`: el modelo C anda con mesas al azar, pero
entre años se sesga cuando las secciones grandes llegan al final.

## Modelos parecidos y qué tomar de cada uno

| Modelo | Qué hace | Qué tomar |
|---|---|---|
| Pavía-Miralles, *JASA* 2005, «Forecasts from nonrandom samples: the election night case» (Valencia 1995/1999) | Regresión mesa a mesa contra la elección anterior, actualizada con cada mesa que entra; pensada para muestras no aleatorias | Es el mismo enfoque que B/C: confirma la dirección. Leer cómo trata la no aleatoriedad |
| Washington Post, `elex-model` (código abierto en PyPI; Bronner, Johri y Bowers, C+J 2020) | Diferencia contra una línea de base histórica, regresión cuantílica sobre covariables demográficas, intervalos por predicción conformal | **Covariables para el cambio** (arregla el caso entre años) e **intervalos calibrados** |
| New York Times, «la aguja» | Expectativa previa por condado o precinto según demografía; cuando un área se aparta, corrige las áreas parecidas | Lo mismo: el cambio se traslada a las mesas parecidas, no a todas |
| Conteo rápido del INE (México; Mendoza y Nieto-Barajas; Anzarut, Ortiz y González) | Muestra aleatoria estratificada de ~4–5 % de las casillas; modelo multinomial jerárquico bayesiano con muestras censuradas (casillas que no llegan) | **Probabilidad de triunfo**; diseño de muestra si se juntan fotos de actas; tratar las mesas que faltan como censuradas |
| Tesis de Radboud (2014), elecciones neerlandesas | Modelo de tópicos contra modelo lineal | Con 2,5 % de mesas o menos, el lineal es mejor: lo nuestro está bien para la primera hora |
| elecciones-peru.live, prueba de 2022 | Orden de llegada imputado con el patrón de 2026 | Para calibrar el orden «geo» hacen falta horas reales |

## Mejoras, por orden

1. **Covariables del cambio (D).** Sumar a C covariables por sección o circuito: tamaño (log de electores), urbano/rural y
   NBI o educación del censo 2022 por departamento, participación anterior. Primero la versión simple: matrices por
   estrato de tamaño. Se prueba con `backtest.py 2019p 2023p --circuito` y orden «geo»; la meta es bajar el −3,6
   actual por debajo de A (2,1).
2. **Intervalos y probabilidad de triunfo.** Bootstrap por circuito o predicción conformal sobre las mesas contadas.
   Se mide en la prueba la **cobertura** (que el intervalo del 90 % contenga el resultado real en ~90 % de las corridas),
   también con el orden «sesgo».
3. **Orden de llegada real.** Grabar capturas cada pocos minutos de los sitios de resultados en las provinciales de
   2027: es la prueba en vivo y a la vez el dato de horas que falta. Con eso se calibra «geo» y se puede ajustar un
   modelo del tiempo de llegada, como el del INE.
4. **Prueba de diputados 2021 → 2025** por circuito (hace falta llevar las listas a bloques con
   `mapas/mapa<año>/mapeo_listas_<año>.csv`), que es el caso más parecido a 2025 → 2027.

5. **Pendiente decidido por el usuario (27-oct-2026): la aguja queda con D y benchmarking.** El backtest muestra
   que E sin benchmarking es mejor (`LEEME.md`, «Método E»); pasarla exige cambiar `aguja.national_boot` (hoy ajusta
   solo la matriz nacional) y recalibrar `SIS` con `aguja.py --cobertura`. La prioridad es el modelo de fotos.

## Provinciales 2027: dónde probar

Según la prensa de agosto a octubre de 2026 (sin confirmar fechas oficiales): Tucumán el 9 de mayo, Salta en mayo,
Santa Fe probablemente en junio, PASO de Mendoza en julio; Entre Ríos, San Juan y Córdoba también desdoblarían, y en
total podrían desdoblar hasta 20 provincias. Para cada una:

- **Elección de origen**: diputados nacionales 2025 por mesa (`datos_oficiales/2025/`). Las mesas y circuitos son los mismos, aunque
  las fuerzas provinciales sean otras: la matriz de traspasos lo absorbe.
- **Datos en vivo**: ver unas semanas antes si el organismo provincial publica por mesa (API o páginas) y armar el
  grabador. Sin datos por mesa, la proyección queda por sección (como A).
- **Después**: el resultado definitivo cierra la prueba; se agrega al backtest como un par más.

## Cómo llegan los datos en Argentina (búsqueda del 27-oct-2026)

**Nacionales (DINE).** La normativa no permite publicar el provisorio antes de tres horas del cierre (21 h), y para
entonces ya hay mucho cargado:

| elección | avance |
|---|---|
| balotaje 2023 | 86,6 % a las 20:20 (Milei 55,95 %), 94,1 % a las 20:52, 99,25 % a las 22:30, cierre 99,28 % |
| legislativas 2025 | la DINE preveía 40 % a las 21 h; esa noche se llegó al 90 % |
| provincia de Buenos Aires, 7-sep-2025 | 82,2 % a las 21 h |

Consecuencia: con datos oficiales, la aguja nacional arranca entre el 40 y el 90 %, donde el error de D es de décimas
aun con orden sesgado. La parte temprana de la curva (0–40 %) solo existe con fuentes no oficiales (fotos, fiscales),
y ahí vale lo dicho abajo sobre el sesgo de selección.

**Provinciales.** Cada provincia tiene su régimen y su empresa de logística, y en algunas no rige la espera de tres
horas. Ahí la curva temprana sí se ve:

- **Santa Fe 2023**: primeros datos oficiales a las 18:20.
- **Santa Fe 2025** (convencionales): tendencia hacia las 21:30, en elecciones.santafe.gob.ar.
- **Tucumán 2023**: primeros resultados cerca de las 21 h. El provisorio cerró el lunes con 85–89 % de las mesas:
  432 urnas sin cargar, la mitad en la capital, y la página se cayó unos 55 minutos.

Esto último importa: **el provisorio provincial puede no llegar nunca al 100 %, y lo que falta no es al azar**
(estaba concentrado en la capital). Es justo el caso que el modelo resuelve: proyectar las mesas que no entraron.

**Hora de carga por mesa.** No apareció en ningún lado. Los archivos de la DINE no la traen; existe una API histórica
del provisorio (documentada en datos.gob.ar, resultados.mininterior.gob.ar/desarrollo), pero el dominio no responde
desde acá y no se pudo ver si trae marcas de tiempo. Tampoco se encontraron capturas guardadas por terceros de
resultados.gob.ar en 2023 o 2025.

## Cómo adaptarlo

1. **Grabar las provinciales de 2027.** Primero Tucumán (9 de mayo). Copiar cada pocos minutos el JSON o las páginas
   del sitio de resultados, como hace el repositorio que guarda los resultados del condado de Los Ángeles (rdmurphy,
   2024), y armar después la serie por mesa. Es la prueba en vivo y a la vez el dato de horas que falta. Antes de cada
   elección: ver el sitio del simulacro, qué publica por mesa y desde qué hora.
2. **Modelo del tiempo de llegada.** Con las horas grabadas, ajustar cuánto tarda cada mesa según tamaño de sección y
   circuito, distancia a la capital, provincia y urbano/rural (un modelo de supervivencia). Sirve para tres cosas:
   - generar órdenes realistas para el backtest y recalibrar el error sistemático de la banda;
   - dar una línea punteada basada en datos;
   - estimar qué mesas no van a llegar nunca al provisorio (Tucumán 2023).
   No se encontró un modelo publicado de esto para la noche electoral. El INE mexicano trata las casillas que no
   llegan como muestra censurada (Anzarut, Ortiz y González), y Decision Desk HQ esquiva el problema usando solo
   unidades completas o casi completas.
3. **Banda adaptativa.** La cobertura medida en `aguja.py --cobertura` muestra que la banda actual es conservadora:
   con mesas al azar contiene el resultado el 100 % de las veces y es unas 4 veces más ancha de lo necesario. Como de
   cada mesa se sabe cómo votó antes, se puede medir cuán representativo es lo contado (comparar el resultado
   anterior de las mesas contadas con el de todas, y su tamaño). Si lo contado se parece al total, el término
   sistemático se achica.
4. **Para las nacionales**: la aguja oficial arranca tarde (21 h, 40–90 %). La parte temprana solo con una muestra
   propia sorteada (ver abajo).

Fuentes de esta sección: balotaje 2023 en
https://quedigital.com.ar/politica/primeros-resultados-javier-milei-gano-el-balotaje-con-el-55-de-los-votos/ y
https://www.lanacion.com.ar/politica/resultados-en-vivo-como-va-el-balotaje-2023-en-la-argentina-nid19112023/;
2025 en https://www.diariodecuyo.com.ar/argentina/elecciones-legislativas-2025-confirmaron-la-hora-en-que-se-conoceran-los-primeros-resultados-1790831.html
y https://www.lanacion.com.ar/politica/resultados-en-vivo-de-las-elecciones-en-la-argentina-como-van-las-legislativas-2025-nid26102025/;
Buenos Aires 2025 en https://www.lanacion.com.ar/politica/que-se-sabe-de-los-resultados-de-las-elecciones-buenos-aires-2025-nid07092025/;
Santa Fe en https://www.airedesantafe.com.ar/politica/elecciones-santa-fe-2023-las-1820-se-publicaron-los-primeros-datos-oficiales-del-escrutinio-provisorio-n508651
y https://www.infobae.com/politica/2025/04/13/elecciones-santa-fe-2025-en-vivo-las-ultimas-noticias-sobre-los-comicios-en-la-provincia-minuto-a-minuto/;
Tucumán 2023 en https://www.letrap.com.ar/politica/tucuman-alfaro-sufre-el-escrutinio-la-capital-un-ojo-el-cierre-listas-n5400919
y https://www.argentina.gob.ar/sites/default/files/2023/07/tucuman_2023_-_elecciones_provinciales_0.pdf;
API de la DINE en https://datos.gob.ar/dataset/dine-api-publicacion-resultados-electorales;
Decision Desk HQ en https://hdsr.mitpress.mit.edu/pub/zr6hjsfl;
capturas periódicas en https://github.com/rdmurphy/scrape-la-county-election-results-2024.

## Fotos de actas para las nacionales

- **X prohíbe el scraping** sin permiso escrito desde septiembre de 2023, y la API paga es cara (cifras de 2026 de
  vendedores, sin confirmar). Conviene no basar el plan en eso.
- **Sesgo de selección**: las fotos que se suben no son al azar (fiscales que muestran mesas buenas, mesas
  llamativas). El modelo corrige la selección por *nivel* (sabe cómo votó esa mesa antes), pero **no** la selección
  por *cambio*: si se suben las mesas donde un partido mejoró más de lo esperado, la proyección se corre. En el
  backtest el peor caso por nivel deja 1–2 puntos; el sesgo por cambio no está probado y habría que agregarlo como
  orden «sesgo de cambio».
- **Mejor alternativa**: un conteo rápido propio, como el del INE. Se sortea de antemano una muestra estratificada
  de ~500 mesas y se juntan fotos con consentimiento (voluntarios o fiscales, por formulario). Así la muestra es al
  azar por diseño. Hay que leer el número de mesa en la foto para enlazarla con su resultado de 2025.
- **Ventana útil**: las fotos solo sirven antes de que la DINE empiece a publicar; después resultados.gob.ar da cada
  mesa con su telegrama. **Antes de difundir algo, revisar la veda del Código Electoral** sobre la difusión de
  pronósticos o sondeos en las horas posteriores al cierre.

## Fuentes

- Pavía-Miralles (2005): https://academicnewsletter.sufe.edu.cn/info/445759
- Washington Post `elex-model`: https://pypi.org/project/elex-model/2.1.0 y https://cj2021.northeastern.edu/files/2020/02/CJ_2020_paper_27.pdf
- Predicción conformal en el Post: https://news.stanford.edu/stories/2021/03/honesty-statistical-models
- Aguja del NYT: https://www.axios.com/2020/11/03/election-day-news-networks-media
- Conteo rápido del INE: https://arxiv.org/pdf/1901.01559 y https://arxiv.org/pdf/1801.06757
- Tesis de Radboud y algoritmo genético: https://arxiv.org/pdf/1401.4674 y https://theses.ubn.ru.nl/bitstreams/4c2338f0-47b4-4e82-8ff3-7127ec724ee4/download
- Calendario 2027: https://www.cronista.com/economia-politica/elecciones-2027-tras-el-desdoblamiento-en-santa-fe-que-provincias-esperan-para-definir/ y https://www.lanoticiaweb.com.ar/elecciones-2027-casi-todo-el-mapa-provincial-se-despega-de-milei-y-hasta-20-distritos-podrian-votar-antes-de-octubre/
- Telegramas por mesa en resultados.gob.ar: https://www.todojujuy.com/pais/como-voto-mi-mesa-el-paso-paso-verlo-n281287
- Términos de X: https://techcrunch.com/2023/09/08/x-updates-its-terms-to-ban-crawling-and-scraping

## Lo que dejó la noche de Israel (27-oct-2026, `israel/`)

El modelo de Israel se armó con el de acá (Goodman por urna, matrices por grupo encogidas a la nacional y sin recortar
a ≥ 0) y se corrió en vivo. Lo que vale para Argentina:

1. **Ancla para el primer 1–2 %.** Con 128 urnas sesgadas (1 árabe, 2 haredíes) la matriz libre se disparaba
   (Lista Conjunta 20 bancas, Shas afuera). Lo arregló encoger la matriz nacional hacia una matriz «de antecesores»
   con el cambio proporcional observado, y encoger ese cambio hacia 1 con 3000 votos de peso. En el backtest bajó el
   error del bloque de 2,4 a 1,2 bancas al 1 % y la banda de 14 a 5. **Probado en Argentina el mismo día: no sirve
   como regla general** (ver «Ancla de Israel en el modelo C», abajo).
2. **Mínimo y cobertura antes de mostrar.** No proyectar debajo de un mínimo (en Israel, 120 urnas) y mirar cuántas
   mesas hay de cada estrato. Acá: conurbano / interior, y cada provincia grande.
3. **Residuo local (la parte local del método peruano) sí suma; las vecinas no.** Sumar a las mesas sin contar de
   cada localidad el desvío de sus mesas ya contadas, encogido por W / (W + 1500 electores), mejoró la proyección por
   lista con orden geo del 10 % en adelante (0,44 → 0,37 al 10 %, 0,24 → 0,13 al 40 %). Pasar el residuo a las
   localidades vecinas del mismo sector no mejoró y rompió la banda: el cambio no es geográfico sino del grupo. Es
   lo mismo que dice el punto 1 de arriba (covariables, no vecindad). **C ya tiene residuo de circuito: revisar que
   esté encogido por padrón contado** y no usar el componente de secciones vecinas de A.
4. **Backtest con el orden real.** La mejor prueba de la noche fue tomar las urnas exactas de cada archivo
   publicado y buscarlas en las elecciones anteriores (`israel/backtest_7.py`): mide el error con el sesgo de llegada
   de verdad, sin inventar el orden. **En 2027 guardar cada captura del provisorio con su hora** y correr este
   backtest sobre 2023 y 2025 durante la noche: es más informativo que «geo».
5. **El error por partido se concentra en el que está al borde del umbral.** Con el 20 % contado el error medio por
   lista fue 0,4 bancas, pero una lista del 3,8 % quedaba afuera (4 bancas de error); un 20 % más de urnas puede
   empeorar ese caso si entra un grupo raro. Para diputados 2027 la proyección tiene que pasar a **bancas por
   provincia** (D'Hondt con el 3 % del padrón) y marcar las listas cerca de ese corte y del último cociente.
6. **Lo que llega después se proyecta aparte.** El doble sobre (6–10 % de los votos, se cuenta días después) se
   proyecta con cambio proporcional sobre su propio resultado anterior, no con la matriz de las urnas comunes: erra la
   mitad. Acá vale para el voto en el exterior, el de privados de libertad y las mesas que llegan tarde.
7. **Bloques antes que partidos.** Los errores por lista se compensan dentro del bloque (el bloque erró 0,5 bancas, casi lo
   mismo que una lista sola, 0,4). La aguja tiene que mostrar el desenlace y los bloques, y las listas como detalle.
8. **Operación de la noche.** El sitio oficial tenía un desafío antibots (AWS WAF) y no se salteó: alcanzó con bajar
   el CSV a mano y un comando que toma el más reciente de la carpeta, guarda el historial por archivo y regenera la
   aguja, los hemiciclos y el HTML. Para 2027: el mismo esquema, probado antes con capturas viejas, y fuentes
   alternativas conocidas de antemano.

## Ancla de Israel en el modelo C (27-oct-2026)

`python proyeccion/backtest.py <origen> <destino> --ancla` agrega C_ancla, D_ancla y D_sin_ajuste_ancla: la matriz
nacional se encoge hacia la de sucesores con cambio proporcional (`anchor()`, `NP` = 300 mesas, `MP` = 3000 votos;
sucesoras en `SUCESORES`, por defecto la fuerza del mismo nombre). 10 repeticiones por orden; salida en
`<origen>_<destino>[_circuito]_ancla/`. Error absoluto del % del ganador, en puntos:

| Par | Orden | Corte | D | D_ancla | D_sin_ajuste | D_sin_ajuste_ancla |
|---|---|---:|---:|---:|---:|---:|
| 1.ª vuelta → balotaje 2023 | geo | 0,5 % | 0,72 | 1,59 | 0,76 | 1,17 |
| | sesgo | 1 % | 1,36 | 2,76 | 1,19 | 2,61 |
| 1.ª vuelta → balotaje 2015 | geo | 0,5 % | 0,96 | 1,63 | 0,94 | 1,27 |
| | sesgo | 5 % | 1,01 | 0,81 | 0,71 | 0,48 |
| 2019 → 2023 por circuito | geo | 0,5 % | 2,97 | **2,04** | 2,64 | **1,79** |
| | geo | 2 % | 1,89 | 2,23 | 1,56 | 1,74 |
| | sesgo | 1 % | 1,30 | 7,87 | 1,48 | 7,19 |

- **En general empeora.** Con mesas al azar da igual o peor; con el peor orden («sesgo») duplica el error en 2023
  (en 2015 mejora algo desde el 5 %), y en 2019 → 2023 lo multiplica por 3 a 10 al 0,5–2 %.
- **Solo ayuda** entre años con orden geo al 0,2–0,5 % (2019 → 2023: 3,0 → 2,0 puntos), donde ya no sirve
  ningún método.
- **Por qué en Israel sí y acá no.** Allá los grupos de votantes están separados por urna (árabes, haredíes): con
  128 urnas había filas de la matriz sin ningún dato y el ancla las sostenía. Acá todas las fuerzas están en todas
  las mesas y la matriz nacional se identifica con pocas mesas. El cambio proporcional que usa el ancla se mide en
  lo contado, así que con llegada sesgada lleva el mismo sesgo y además empuja a las fuerzas sin sucesora (JxC en
  el balotaje) hacia el reparto de lo contado.
**Con fotos de actas (28-oct-2026).** `fotos_modelo.goodman(..., prop=True)` (`("goodman_prop", lam)`;
`fotos_sim.py --ancla` y `proyectar_fotos.KIND`) cambia el ancla: el swing uniforme pasa a ser cambio
proporcional. Tres pesos: λ = 0,1, el de Israel (300 mesas, λ = 300/actas) y puro.
- **Las 27 actas de 2025** (real LLA 40,7 / FP 33,6, margen +7,1). Margen LLA − FP:

  | Origen | Goodman λ = 0,1 (actual) | Prop. λ = 0,1 | Prop. peso Israel | Prop. puro |
  |---|---:|---:|---:|---:|
  | 2023p | +9,0 | +9,5 | +10,0 | +11,1 |
  | 2021bl | +5,2 | +5,6 | +8,3 | +9,8 |
  | 2023p + 2021bl | **+7,3** | +7,7 | +9,1 | +10,4 |

- **28 actas simuladas** (25–35 «como las de 2025» y 28 al azar; 300 colecciones; `fotos_sim/*_n28_ancla.csv`).
  Error absoluto medio del margen, «como 2025»:

  | Par | Goodman λ = 0,1 | Prop. λ = 0,1 | Prop. peso Israel | Swing uniforme |
  |---|---:|---:|---:|---:|
  | 2023p → 2025bl | 2,87 | 2,79 | 2,45 | 4,12 |
  | 2019p → 2023p | 2,69 | 2,65 | 21,3 | 5,03 |
  | 2021bl → 2023p | 3,02 | 3,14 | 13,0 | 7,41 |
  | 2023p → 2023b | 1,42 | 1,46 | 6,28 | 2,93 |
  | 2015p → 2015b | 1,76 | 1,77 | 2,14 | 2,84 |

- **Resultado.** Con λ = 0,1 da lo mismo que el modelo actual (±0,1). Con el peso de Israel o puro se rompe
  cuando la sucesora es otra fuerza o una suma de varias (2019 → 2023, 2021 → 2023, balotajes): sesgos de 6 a 21
  puntos. Solo mejora un poco 2023 → 2025 (2,87 → 2,45), donde LLA ← LLA + JxC.
- **Se queda el Goodman con λ = 0,1.** Con ~30 actas el límite sigue siendo de dónde vienen, no el ancla.
- **Queda apagada** (sin `--ancla` el backtest es el de antes). Sirve solo si en 2027 alguna fuerza se concentra en
  pocas mesas, por ejemplo una lista provincial en un distrito que todavía no cargó.

## Proyección de Rodrigo Mahlmeister para el balotaje de Brasil 2026 (leída el 28-oct-2026)

Fuente: projecao.2026elections.workers.dev (método y «Detalhes técnicos») y su hilo del 28-oct-2026. Final:
Lula 51,79 %.

**Qué hizo:**
- **Dos modelos, según cuánto haya contado.**
  - Hasta el 5 % del padrón: transferencia desde la 1.ª vuelta de la misma sección. Lula y Flávio conservan sus
    votos y solo se estima cómo se reparten los de los demás candidatos, por estado y separando capital de
    interior.
  - Del 5 al 15 % pasa de a poco al modelo principal: swing del logaritmo de Lula/Flávio respecto del balotaje de
    2022. Es una regresión ponderada sobre el perfil de voto y el tamaño del municipio, con coeficientes Brasil →
    región → estado encogidos (bayes empírico) y una prior en las encuestas finales.
- **En los municipios que ya empezaron a contar,** lo que falta sale de la 1.ª vuelta de esas mismas secciones.
- **2022 por local de votación,** emparejado geográficamente (93 % del padrón exacto).
- **Banda:** bootstrap de municipios, calibrado repitiendo los conteos de 2022 y de la 1.ª vuelta de 2026.
- **La noche publicó otra cosa.** Esperó al 2 % y hasta el 15 % mostró el menor valor de Lula de los dos modelos.
  Después dijo que se arrepentía: con el método planeado habría mostrado 51,80 desde el principio.

**Comparación con nuestra aguja de Brasil** (`aguja_brasil.py`, mismo orden real de llegada; Goodman completo
desde la 1.ª vuelta, matriz por UF encogida a la nacional):

| Contado | Mahlmeister | Nuestra | Real |
|---|---:|---:|---:|
| 0,3 % | 51,84 | 51,26 | 51,79 |
| 2 % | 51,80 | 51,32 | |
| 5 % | 51,72 | 51,40 | |
| 8–30 % | 51,23–51,55 | 51,35–51,47 | |
| 50 % | 51,70 | 51,64 | |
| 70 % | 51,78 | 51,74 | |

- **Al principio él erró ≤ 0,2 y nosotros 0,4–0,5.** La diferencia está en el modelo de transferencia
  restringido: los dos finalistas conservan su voto y solo se estiman los traspasos de los demás. Es otra forma
  de ancla, y en este caso con sentido, porque la lealtad de los finalistas entre vueltas es casi 1. Nuestro
  Goodman completo deja que los datos tempranos «muevan» votos de Lula a Flávio.
- **Del 8 al 30 % los dos erramos lo mismo** (−0,3 a −0,6): su modelo de swing respecto de 2022 tenía el mismo
  sesgo de llegada que nuestro Goodman.

**Para probar:**
1. **Balotaje con lealtad fija.** En el balotaje, proyectar con lealtad fija de los dos finalistas y estimar solo
   la fila de cada tercero (por distrito y capital/interior). Probar en Brasil 2026 con `aguja_brasil.py` y en
   2023 y 2015 con `backtest.py`. Es el caso donde un ancla tiene sentido: el ancla de Israel falló acá porque
   escalaba todas las filas con el cambio proporcional medido en lo contado.
2. **Promediar dos orígenes según lo contado** (la 1.ª vuelta y el balotaje anterior), como ya conviene con las
   fotos.
3. **Swing en log-razón para dos candidatos:** acotado, no da porcentajes negativos.
4. **Prior en las encuestas** para el primer 1 %. Hace falta definir cuánto pesa.
5. **Decidir el método antes de la noche y no cambiarlo.** Si se muestra algo más conservador, decirlo en la
   página.

### Ideas de Mahlmeister probadas (28-oct-2026)

**1. Lealtad fija de los dos finalistas.**
- Implementación: `aguja_brasil.py` con `MODO=leal` / `leal_cap`, `brasil_transferencia.py` (su modelo literal:
  solo válidos, cociente de totales) y `backtest.py --leal`.
- Brasil 2026, orden real del TSE. % de Lula y error medio por tramo (final 51,79):

  | Contado | Él | Goodman (actual) | Lealtad fija | Lealtad, capital/interior | Su modelo literal |
  |---|---:|---:|---:|---:|---:|
  | 0,3 % | 51,84 | 51,26 | 50,75 | 50,75 | 51,43 |
  | 2 % | 51,80 | 51,32 | 51,34 | 51,31 | 51,34 |
  | 5 % | 51,72 | 51,40 | 51,44 | 51,40 | 51,43 |
  | Error medio hasta el 5 % | — | 0,39 | 0,65 | 0,67 | 0,54 |
  | Error medio del 5 al 30 % | — | 0,40 | 0,36 | 0,39 | 0,35 |

  Ni con su modelo literal y nuestros datos se llega a su 51,8 temprano. Lo que le dio ese número no está en el
  modelo de transferencia. Probablemente es el swing respecto del balotaje de 2022 o la prior de encuestas.
  Para probarlo hace falta el TSE 2022 por sección, que no está bajado.
- Balotajes argentinos (10 repeticiones). Lealtad fija contra el modelo actual: igual al azar, peor con
  «capital» y «geo» y mucho peor con «sesgo».
  - 2023, sesgo al 1 %: 2,69 contra 1,28 de D sin ajuste.
  - 2015, sesgo al 1 %: 1,65 contra 0,49 de B.

  Fijar la lealtad saca la única libertad que absorbe el sesgo de llegada.
- **Descartada.**

**2. Swing en log-razón respecto del balotaje anterior y mezcla entre modelos.**
- Implementación: `backtest.py 2023p 2023b --swing 2015b`. El balotaje 2015 se toma por circuito; si el circuito
  se renumeró, se usa la sección o el distrito (14 % de las mesas, sobre todo Santa Fe). La regresión tiene un
  término por tamaño, intercepto por distrito y residuo de circuito.
- Variantes:
  - `mezcla_5_15`: de traspasos a swing entre el 5 y el 15 % contado, como hizo él;
  - `promedio`: mitad y mitad.
- Error medio de todos los cortes:

  | Orden | D sin ajuste | Swing | Mezcla | Promedio |
  |---|---:|---:|---:|---:|
  | azar | **0,07** | 0,53 | 0,09 | 0,27 |
  | capital | **0,36** | 3,54 | 0,69 | 1,89 |
  | geo | **0,43** | 2,02 | 0,61 | 1,02 |
  | sesgo | **1,04** | 1,82 | 1,15 | 1,42 |

- El swing desde 2015 está sesgado aun con mesas al azar (0,5–0,8 puntos): la geografía cambió en ocho años.
  Pasar a él después del 5 % empeora.
- **Descartado para balotaje desde 1.ª vuelta.** Puede servir donde no hay 1.ª vuelta inmediata (una legislativa
  de medio término), pero ahí ya usamos el origen por circuito.

**3. Prior en las encuestas.**
- Promedio de las últimas encuestas del balotaje 2023: Milei 51,0 % de dos partidos (AtlasIntel, CELAG,
  CB Consultora y Proyección; Wikipedia en inglés, «Opinion polling for the 2023 Argentine general election»).
  Real: 55,65.
- Encogiendo la proyección hacia ese número con P mesas de peso:
  - P = 50 ayuda solo con «sesgo» al 0,2 % (1,83 → 0,66) y empeora al azar (0,14 → 0,84);
  - P = 200 empeora todo salvo «sesgo».
- Con encuestas que erraron 4,6 puntos es una mala apuesta. **No se usa.**

**4. Lo que sí queda.** Decidir y publicar el método antes de la noche, y no mostrar una versión «conservadora»
distinta de la planeada.
