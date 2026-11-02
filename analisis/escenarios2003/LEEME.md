# Escenarios presidenciales de 2003

Trabajo local del 31-oct-2026. **Simulación condicional**, no reconstrucción identificada de lo que habría sucedido. Se retira una candidatura por vez, poco antes de la primera vuelta y sin apoyo explícito a otra fórmula. El simulador incluye las 18 candidaturas y cuatro modelos de afinidad.

## Revisión territorial: ajuste local predeterminado

A partir de la observación del usuario sobre provincias que parecían votar «en bloque», el cálculo predeterminado **ya no aplica un reparto único por provincia**. Para cada unidad se condiciona el prior nacional de la matriz histórica a su resultado local de 2003 y, cuando existe una correspondencia válida, a su composición electoral local de 1999. El ajuste IPF conserva ambos márgenes y luego se aplica la hipótesis de sustitución al retirado. No se añade ruido, no se cambian ganadores a mano y no se interpola entre polígonos para producir variedad visual.

Los antecedentes provienen de `estimar.prepare('1999pe','2003pe')`, con los mismos cruces y filtros que el Sankey, no de sumar circuitos sin validar. Hay antecedente local en **528 de las 537 unidades con votos de 2003**. En las nueve restantes el prior nacional se condiciona solo al resultado observado de 2003 y la ficha advierte que el origen histórico no está observado en el cruce. La composición de 1999 conserva las reservas de su base original, incluidas las celdas estimadas de fuerzas menores en San Luis y Santa Cruz; «antecedente disponible» no significa que toda celda haya sido observada sin correcciones.

Las variantes del libro 1999 usan las categorías compatibles de ese antecedente. Para las ocho categorías del libro 2001 no hay margen local equivalente preparado: se condiciona el prior nacional a los datos locales 2003, sin presentar un origen 2001 local como observado. Esta reserva se repite en las fichas.

El prior nacional no determina el porcentaje de cada unidad: el IPF incorpora sus márgenes locales, con piso numérico 1e-8 para no tratar ceros redondeados de una estimación como imposibilidades. Esto sigue siendo una **hipótesis de escenario**, no una identificación de segundas preferencias. Los datos locales de 2003 se usan como referencia de una retirada tardía, no como un resultado contrafáctico conocido.

El selector «Provincial uniforme: comparación» conserva la primera especificación para medir cuánto cambia el escenario; dejó de ser el valor predeterminado. Las explicaciones sobre ese reparto provincial que siguen abajo describen esa comparación. La segunda vuelta conserva su calibración nacional de encuestas; sus diferencias territoriales surgen de la composición local simulada, no de inventar encuestas provinciales.

`control_ajuste_local.json` registra antecedentes y convergencia por unidad/modelo. `heterogeneidad_local.json` verifica que el reparto ya no es constante dentro de la provincia: 118 de 120 combinaciones de provincia y retiro principal tienen al menos un destino con dispersión interna superior a un punto. Es un control contra la uniformidad mecánica, **no una validación predictiva** ni un objetivo al que se ajustó el modelo.

## Abrir

En el navegador integrado, usar `http://127.0.0.1:8793/mapas/mapa2003escenarios/index.html` y `http://127.0.0.1:8793/analisis/escenarios2003/simulador_2003.html`. El iniciador `../../abrir_escenarios2003.cmd` levanta el servidor local si hace falta y abre el índice. Los enlaces a rutas del disco pueden abrir un editor o no navegar desde Codex; la apertura HTTP se verificó con selección de candidatura y vuelta. Se mantienen los HTML autocontenidos para abrirlos directamente en un navegador externo.

- `simulador_2003.html`: Sankey de tres etapas, votos esperados, comparación de las 18 retiradas, sensibilidad entre cuatro modelos, provincias, edición de transferencias, fuentes y descargas CSV/JSON. Funciona sin servidor ni conexión.
- `../../mapas/mapa2003escenarios/index.html`: índice de 18 atlas autocontenidos. Cada atlas abre una retirada distinta y permite cambiarla, alternar modelo, referencia/primera/segunda vuelta, coropleta de candidato, margen y cruce de balotaje.
- `escenarios_predeterminados.csv`: 18 retiradas × cuatro modelos, con los supuestos predeterminados. Las cifras son votos/proporciones esperados, no observaciones individuales.

## Fuentes y separación temporal

1. **Base presidencial de 2003:** PolAr por mesa agregado por circuito (`transferencias/circ_2003p.pkl` y `secciones_2003.csv`). No se usan los votos legislativos del atlas `mapa2003`. De ese atlas se reutilizan SVG, geometría, recuadros, interfaz y leyenda.
2. **Tabla nacional conservada de Wikipedia:** `datos/fuentes_leg2003_2025/presidenciales/wpres2003.txt`. Los 18 candidatos suman 19.388.695; blancos/nulos 542.214; abstenciones 5.550.501; padrón 25.481.410. La infobox local añade dos votos a Menem, pero la tabla y su suma cierran con 4.741.200. No se corrigen los archivos originales.
3. **Nuestro Sankey 1999 → 2003:** `transferencias/1999pe_2003pe/`, matriz nacional de flujos y matrices provinciales de la estimación principal. Variante de una sola matriz nacional en `calvo_nacional.csv`. El motor original es RxC penalizado; aquí se reutilizan sus resultados, no se ajusta una elección contrafáctica inexistente como si hubiese sido observada.
4. **Calvo y Escolar (2005):** *La nueva política de partidos en la Argentina*. Se revisó el PDF local de `Downloads/rec8399/libro_calvo_escolar/`. Figura 6.11, p. 201: votos legislativos 2001 → presidenciales 2003; figura 6.12, p. 202: presidenciales 1999 → 2003; figura 6.15, p. 206: procedencia del voto recibido en 2003. La variante 1999 utiliza directamente los perfiles receptores de la figura 6.15, evitando confundir P(destino|origen) con su inversa. `libro_p201.png` y `libro_p202.png` son recortes de consulta visual de las páginas, no materiales para publicar.
5. **Encuestas de época:** 31 mediciones de balotaje (22 anteriores a la primera vuelta) de cruces numéricos, más tres filas OPSM y tres porcentajes parciales de Rouvier por origen. Transcripción, fecha de publicación, campo, tamaño, denominador y enlaces en `encuestas.json`. Las notas periodísticas son fuentes contemporáneas; no se obtuvieron microdatos ni fichas completas de todas las submuestras.

### Encuestas verificadas

- Equis, campo 9–13 de febrero, publicación 16-feb-2003: Kirchner frente a Menem, Rodríguez Saá, Carrió y López Murphy. Muestra 1.067 en AMBA y determinadas provincias; no cubre nominalmente todas las provincias. [Nota original](https://www.pagina12.com.ar/diario/elpais/1-16660-2003-02-16.html).
- Sondeo atribuido a Ibope por la nota del 23-mar-2003, campo 18–21 de marzo, 1.100 casos en 65 localidades: cuatro cruces de Kirchner y López Murphy–Menem. **La propia nota mezcla la atribución Ibope con una descripción de la consultora de Zuleta Puceiro**; la inconsistencia queda consignada, no resuelta. También describe otros cruces cualitativamente, sin publicar todos sus niveles numéricos. [Nota original](https://www.pagina12.com.ar/diario/elpais/1-17941-2003-03-23.html).
- Equis, 8-may-2003: Kirchner–Menem, 3.110 casos en 13 distritos, 86,3 % del padrón, voto proyectado entre las dos fórmulas. [Nota original](https://www.pagina12.com.ar/diario/elpais/1-19867-2003-05-08.html).
- OPSM, Equis, Analogías y Rouvier, 11-may-2003: cuatro mediciones de voto neto/proyectado. Se conservan separadas; no se inventa un promedio ni un tamaño muestral para Equis de ese día. [Cuadro contemporáneo](https://www.pagina12.com.ar/diario/elpais/subnotas/20000-7701-2003-05-11.html), [otra nota de la época con tamaños y bases](https://www.lanacion.com.ar/politica/amplia-ventaja-para-kirchner-nid495350/).
- OPSM, 11-may-2003: cruces para votantes de Carrió, Rodríguez Saá y López Murphy. Las filas publicadas suman 97,7, 99,1 y 99,6: se conserva el residuo como **no publicado**, no se reasigna. [Cuadro original](https://www.pagina12.com.ar/diario/elpais/subnotas/20000-7703-2003-05-11.html).

- Enrique Zuleta Puceiro (Ibope/OPSM), campo del 12 al 19 de febrero, 800 casos ([La Nación, 22-feb-2003](https://www.lanacion.com.ar/politica/kirchner-sigue-primero-y-cada-vez-hay-menos-indecisos-nid475718/)): Rodríguez Saá 49,6–Menem 21,2; Carrió 53,1–Menem 25,7; Kirchner 53,1–Menem 17,7; López Murphy 38,1–Menem 25,7.
- Ricardo Rouvier y Asociados, campo 1–9 de marzo, 1.550 casos, publicado en el [informe del Real Instituto Elcano](https://www.realinstitutoelcano.org/analisis/informe-elecciones-presidenciales-argentinas-2003/) del 14-abr-2003: Kirchner 52–Menem 20,4; Kirchner 42,1–Carrió 29,2; Kirchner 42,1–Rodríguez Saá 25,5; **Carrió 37,9–Rodríguez Saá 30,9** (el único cruce sin Kirchner ni Menem); Carrió 40,1–Menem 29,9; Rodríguez Saá 38,9–Menem 20,3. En la página las cifras vienen pegadas («42.129.2») y se separaron.
- Research International–Analogías, abril (Página/12 del 6-abr-2003 confirma la medición, 1.800 casos, y un margen de Kirchner sobre Menem de «27 puntos»): K 47,0–M 20,5, Carrió 40,6–Menem 24,4 y Rodríguez Saá 36,5–Menem 20,9. **Los niveles salen de una nota retrospectiva** ([NewsDigitales, 2026](https://www.newsdigitales.com/nota/329857/kirchner-vs-menem-2003-a-23-anos-de-una-encuesta-demoledora/)); el margen coincide con el publicado en 2003. [Nota de 2003](https://www.pagina12.com.ar/diario/elpais/1-18473-2003-04-06.html).

El selector predeterminado utiliza la última cifra **localizada** para cada pareja publicada antes del 27 de abril, no garantiza que sea la última encuesta que existió. El usuario puede elegir explícitamente mayo para Menem–Kirchner. Los Sankey 2003 → 2005, 2007 y 2009 se muestran como contraste retrospectivo y **no ingresan al cálculo predeterminado**.

No se encontró una matriz completa de segundas preferencias ante la retirada de cada candidato. La ausencia no prueba que nunca se haya publicado. Las encuestas de balotaje, el rechazo y la intención de voto de primera vuelta no son mediciones intercambiables.

## Método de retirada

Las columnas de las matrices históricas se ajustan al total de cada candidatura en la base de simulación; se preserva su composición estimada de orígenes. Dentro de cada provincia, para el retirado r:

`P(j | retirada r) = Σ_h P(h | r) × F[h,j] / Σ_{k≠r} F[h,k]`.

La suma interior solo incluye candidatos disponibles. Es una hipótesis de sustitución dentro de cada origen histórico, no una propiedad deducida de las transferencias observadas. Los demás votantes permanecen en su candidatura. Blanco/nulo y abstención del retirado son controles independientes, inicialmente cero; deben sumar hasta 100 %. El reparto positivo también se puede editar manualmente.

En el proyecto los trece candidatos menores comparten la composición del agregado Otros. En el libro, que no ofrece perfiles separados para esos candidatos y el blanco/nulo de 2003, se aplica una mezcla no informativa de los orígenes de los cinco principales. No se transforma «No estimado» en abstención ni en voto a menores. **No hay estimación individual identificada para esos trece perfiles.** En los atlas llevan asterisco y la reserva figura también en el SVG exportable.

En la comparación provincial uniforme, la variante principal utiliza sus flujos provinciales y las variantes del libro y Calvo parten de sus perfiles nacionales. La afinidad de destino se vuelve a ponderar por la oferta provincial y se aplica a todos sus departamentos. Ese supuesto produce el efecto de bloques provinciales observado por el usuario. En la especificación local predeterminada se sustituye por las matrices condicionadas a márgenes locales descritas al principio. Los totales nacionales y provinciales se obtienen sumando las simulaciones locales.

## Balotaje

Las afinidades históricas generan probabilidades para cada candidatura de origen. Para los propios finalistas se parte de 98 % de fidelidad como **supuesto**, que la calibración puede mover. Si existe una encuesta numérica para la pareja, un desplazamiento logístico común reproduce `A/(A+B)` en el electorado real de primera vuelta; no pretende identificar una matriz única de flujos. El resto hasta 100 de una encuesta no se considera automáticamente abstención.

Con OPSM de mayo se pueden fijar sus tres filas **entre respuestas por uno de los dos candidatos**; el residuo, otra respuesta e indecisos permanecen documentados y no se asignan como si fueran votos observados. Las demás filas completan la calibración del agregado. Si el objetivo no es compatible se muestra una advertencia.

La matriz resultante se aplica a la primera vuelta simulada. Por defecto, los votantes redistribuidos actúan como los del candidato que eligieron en esa simulación; el selector alternativo conserva sus preferencias reales de origen. Es una sensibilidad estructural importante. La exclusión del voto positivo en segunda vuelta (3 % por defecto) es otro **supuesto editable**; se aplica igual a todos y no cambia los porcentajes, solo votos y participación. No se moviliza la abstención ni el blanco/nulo de base.

Si el escenario cruza los umbrales de los artículos 97/98 de la [Constitución](https://www.argentina.gob.ar/normativa/nacional/804/texto), se marca triunfo en primera vuelta y el balotaje se rotula exploratorio. No se redondea para evaluar los umbrales.

## Territorio, faltantes y calibración

Los votos por candidato de PolAr y el blanco/nulo se calibran por separado al total de la tabla nacional. Se conserva la proporción territorial de cada columna; por ello, **la referencia del simulador no es el escrutinio definitivo local sin ajustar**. Los factores son reproducibles en `preparar.py` / `preparar_atlas.py`. No se altera ninguna base original.

Geometría y orden de unidades: exactamente los del SVG y `dataset_2003.json` del atlas legislativo de 2003, departamentos de 2001 más 28 circunscripciones de Capital, con los siete recuadros del proyecto. No se introducen Lezama, Tolhuin ni límites de 2022.

- 537 unidades con votos presidenciales utilizables, incluida la Antártida por separado.
- Rinconada y Valle Grande (Jujuy): todas las opciones en cero y sin padrón utilizable en PolAr. Quedan **beige, pendientes**; no se distribuyen votos para completarlas.
- Islas Malvinas: gris, sin voto registrado en la base.
- San Rafael (Mendoza): emitidos mayores al padrón en 236. Se conservan sus votos por candidato; **abstención local ausente**. La implementación usa cero solo como sumando neutro interno y no lo publica como una estimación de abstención; la ficha dice «No verificable». En segunda vuelta su conteo fuera del positivo es un mínimo conocido. La abstención provincial/nacional se conserva desde sus totales agregados, por lo que no se exige cierre de esa columna local desconocida. Los votos positivos, blanco/nulo y ganadores sí cierran territorialmente.

## Interpretación y controles

El cruce principal 1999 → 2003 ya advierte Alianza cerca del promedio y Otros/blanco-nulo no identificados. Cambiar de especificación altera millones de flujos. Una concentración territorial llamativa de receptores menores puede ser efecto de esos perfiles agregados, no evidencia histórica de una segunda preferencia.

`verificar.js`: conservación del padrón en 608 combinaciones (especificación local y provincial), sumas nacionales/provinciales, retirado en cero, no negatividad, 96 calibraciones de encuestas y casos invariantes al conservar el origen. Los 18 retiros se exportan con cuatro modelos. `revisar_atlas.cjs`: 18 páginas × cuatro modelos × tres etapas × tres modos, agregación departamental y manejo de controles. Los informes JSON registran los resultados efectivos de la última ejecución.

No hay bootstrap ni probabilidad de victoria para estos escenarios: no hay una elección contrafáctica observada que permita validar esas cantidades. La dispersión entre modelos es sensibilidad, no intervalo de confianza.

## Revisión de supuestos (31-oct-2026)

Se cotejaron las 14 mediciones con las notas originales: todas las cifras están bien transcriptas. Cambios:

1. **Menem–Kirchner antes del 27 de abril**: se agrega Analogías de abril (ver arriba). Como el predeterminado toma la última cifra localizada, los retiros de López Murphy, Rodríguez Saá y Carrió calibran ahora a K 69,6 % entre los dos (antes Ibope de marzo, 74,9 %). Las cuatro encuestas de mayo dan 68,4 a 72,9, así que la de marzo era la más alta de todas. Kirchner sigue ganando en todos los casos, por unos 5 puntos menos.
2. **Exclusión del balotaje 10 % → 3 %**. En los dos balotajes argentinos el voto positivo cambió +0,45 % (2015) y −2,38 % (2023), y en la OPSM de mayo de 2003 respondían «otro» (blanco, impugnado, no sabe o no irá) el 3,6 % de los votantes de Carrió, el 2,4 % de los de Rodríguez Saá y el 6,6 % de los de López Murphy. El 10 % era tres o cuatro veces eso. Como se aplica igual a todos, **no cambia ningún porcentaje**, solo votos y participación.
3. **Ibope de marzo**: la nota no se contradice; la presenta como «la encuestadora que dirige Enrique Zuleta Puceiro», que en mayo firma como OPSM. Se conserva la atribución publicada.
4. **Control provincial (no entra al cálculo)**: Equis del 8 de mayo publica tres distritos. Con la calibración OPSM de mayo el simulador da Kirchner sobre Kirchner+Menem 77,7–78,6 % en la Ciudad (Equis 83,1), 66,3–67,0 % en Córdoba (64,3) y 69,5–70,2 % en Santa Fe (67,9): el gradiente territorial sale bien, con la Ciudad algo menos kirchnerista que en la encuesta. Equis no proyecta indecisos en esas filas.
5. Quedan como texto, sin calibrar (no publican niveles): Rodríguez Saá le gana a López Murphy por 0,8 puntos (Ibope, marzo); Römer y Equis, ventaja de Kirchner sobre Menem de más de 20 puntos; 65 % de rechazo a Menem. Se buscaron cruces de balotaje en las encuestas de fines de abril (Giacobbe, Catterberg, Mora y Araujo, OPSM): solo los describen cualitativamente.

Se mantienen: los umbrales de los artículos 97 y 98 (más de 45 %, o 40 % con 10 puntos de diferencia, sobre votos positivos), cero de salida a blanco o abstención del retirado (las encuestas no miden una retirada en la primera vuelta) y 98 % de fidelidad inicial de los finalistas (la calibración lo mueve).

### Revisión del método (31-oct-2026, segunda pasada)

**Verificado y correcto:**
- Los 18 totales coinciden con la tabla de la Wikipedia. Los del libro difieren en cientos de votos (p. ej. Kirchner 4.312.517).
- La figura 6.11 (p. 201) está bien transcripta, con orígenes, destinos y votos de 2001.
- Los perfiles receptores de la figura 6.15 coinciden con los que se derivan de la 6.12, con una diferencia de 1 a 2 puntos.
- El texto del libro dice 47 % y 57 % donde su propia tabla dice 49 % y 59 %. Se usa la tabla.
- El padrón cierra: 19.388.695 + 542.214 + 5.550.501 = 25.481.410.
- El IPF local y la agregación de los atlas pasan los controles (`revisar_atlas.cjs`: 18 atlas, 648 cambios de modo, error máximo 3,6e-7).

**Corregido: la retirada contradecía el balotaje del propio simulador.** El voto del retirado se repartía según lo que hicieron los votantes de 2003 con su mismo origen de 1999, sin mirar las encuestas, mientras el balotaje sí se calibraba con ellas. Sin Kirchner, el 44–52 % de su voto iba a Menem, contra el 65 % de rechazo a Menem, las filas de OPSM y el propio libro (p. 201–202: sin Kirchner «el voto al ARI posiblemente hubiera crecido significativamente»). Entre López Murphy y Menem, sus votantes elegían 80 % Menem en la 1.ª vuelta y 79 % López Murphy en el balotaje.

Ahora (`tilt()` en `motor.js`, selector «Reparto del retirado», predeterminado coherente) el reparto entre los cinco principales sigue un modelo de Luce: P(j | r) ∝ afinidad(j | r) · exp(u_j). Los u se ajustan por mínimos cuadrados para que, en cada par con encuesta, los votantes del retirado elijan entre esos dos como en el balotaje calibrado de ese par. Detalles:
- La porción que va a los menores no cambia.
- Los u son nacionales; cada unidad conserva su afinidad local.
- Con tres pares (retiro de Menem o de Kirchner) el ajuste es exacto. Con cinco, el sistema está sobredeterminado y queda un desvío de hasta 11 puntos en el peor caso (Calvo, sin López Murphy, par Kirchner–Rodríguez Saá).
- Sumando las unidades locales, el desvío máximo es de 9 puntos; `verificar.js` lo controla.
- La opción «Solo afinidad por origen» conserva la versión anterior. Con «Sin encuesta» no se ajusta nada.

**Lo que sigue sin información:** López Murphy, Rodríguez Saá y Carrió entre sí no tienen cruce encuestado (salvo el +0,8 de Rodríguez Saá sobre López Murphy, sin cifras). Ese reparto sigue siendo afinidad por origen corrida por un mismo desplazamiento. Por eso, sin Carrió, el 49 % de sus votantes va a López Murphy (origen Alianza 1999) y solo el 24 % a Kirchner. No hay una encuesta que lo contradiga ni que lo confirme.

Otra diferencia: tras la calibración, los votantes de López Murphy prefieren a Kirchner sobre Menem en un 85 % y los de Carrió en un 89 %. OPSM de mayo da 72 % y 99 %. El corrimiento logístico común achata el orden entre orígenes. La opción «cruces OPSM» lo corrige, pero solo con la medición de mayo.

### Ajuste conjunto de encuestas (31-oct-2026, tercera pasada)

Por pedido del usuario («más tipo encuestas»), el predeterminado del balotaje ya no toma la última encuesta de cada par:
- **El ajuste:** las 18 mediciones anteriores al 27 de abril (Equis, febrero; Rouvier e Ibope, marzo; Analogías, abril) se ajustan juntas con un atractivo β por candidato principal (Menem = 0), ponderado por muestra (`jointFit()` en `motor.js`).
- **Los votantes de cada candidato:** en el par (a, b), eligen a con σ(logit(afinidad) + β_a − β_b).
- **Pares con varias encuestas:** usan su promedio.
- **Pares sin encuesta** (López Murphy contra Rodríguez Saá o contra Carrió): reciben un valor coherente con los demás.
- **Coherencia con la retirada:** se toman los seis pares del ajuste. Como la afinidad por origen no es exactamente un modelo de Luce, no todos se cumplen a la vez; el desvío máximo es de 11 puntos y `verificar.js` lo acota.

Residuos del Sankey del proyecto (observado y ajustado, % del primero del par):

| Encuesta | Obs. | Aj. |
|---|---|---|
| Equis feb K–M / K–R / K–C / K–L | 70,0 / 57,8 / 55,6 / 62,9 | 69,8 / 64,3 / 60,2 / 58,5 |
| Rouvier mar K–M / K–C / K–R / C–R / C–M / R–M | 71,8 / 59,0 / 62,3 / 55,1 / 57,3 / 65,7 | 69,8 / 60,2 / 64,3 / 46,5 / 66,0 / 61,6 |
| Ibope mar K–M / K–R / K–C / K–L / L–M | 74,9 / 67,7 / 65,5 / 55,9 / 71,3 | 69,8 / 64,3 / 60,2 / 58,5 / 69,0 |
| Analogías abr K–M / C–M / R–M | 69,6 / 62,5 / 63,6 | 69,8 / 66,0 / 61,6 |

El peor ajuste es Carrió–Rodríguez Saá (Rouvier 55,1, modelo 46,5), porque la afinidad por origen acerca a Rodríguez Saá. Las encuestas entre sí ya difieren de 5 a 10 puntos en el mismo par.

**Lo que las encuestas no pueden dar:** se buscó y no se encontró ninguna medición de segundas preferencias de los votantes de Menem. Los lugares revisados fueron Página/12 (25 y 28-abr, 11-may), La Nación (17, 23, 24 y 25-abr), Infobae (25-ene, 25-abr) y el informe de Elcano.

Lo único es cualitativo:
- los votantes de Menem eran los más fieles (Equis, OPSM y Haime);
- Rouvier dice que Menem «suma muy poco» de otros candidatos.

Por eso, sin Menem, el reparto de su voto (Kirchner 44 %, Rodríguez Saá 21 %) sigue saliendo de la afinidad por origen PJ 1999. Las encuestas fijan el nivel general de cada candidato, no esa fila.

La opción «Última por par antes del 27/4» conserva el método anterior.

### Barrido de encuestas (31-oct-2026)

Se leyeron todas las notas de encuestas que cita el artículo de la Wikipedia y las que aparecieron buscando en Página/12, Infobae, Clarín, La Nueva y el informe del Real Instituto Elcano. La lista de notas sin cruces numéricos está en `encuestas.json` → `ajuste_conjunto.busquedas_sin_resultado`. Novedades:
- **Zuleta Puceiro, febrero** (arriba): cuatro cruces contra Menem que **entran al ajuste** (ahora 22 mediciones).
- **Posteriores a la primera vuelta**, solo como referencia; no entran al ajuste ni a «Incluir mayo»:
  - OPSM 30-abr: Kirchner 65,4–Menem 12,8 (600 casos).
  - Equis 30-abr (Capital y GBA): 59,2–24,1.
  - OPSM 5-may: 65,3–26,1 (1.100 casos).
  - Equis 5-may (Capital y GBA, 1.064 casos): 61,7–20,6.
  - Equis 5-may, por voto anterior, el porcentaje que iría a Kirchner: López Murphy 67,6, Carrió 78,5, Rodríguez Saá 71 ([La Nación](https://www.lanacion.com.ar/politica/el-gobernador-de-santa-cruz-ganaria-por-cuarenta-puntos-nid493878/)).
- **Rechazo** (respuesta única, «a quién jamás votaría»):
  - Ibope, enero: Menem 54,9, Carrió 17,0, López Murphy 7,8, Rodríguez Saá 2,1, Kirchner 1,7.
  - OPSM, abril: Menem 52,3, Carrió 16,0, Moreau 7,0, López Murphy 6,6, Kirchner 1,7, Rodríguez Saá 0,2.
  
  Al ser respuesta única no da la proporción de rechazo de cada candidato. No entra en el ajuste.
- **Sin resultado:** Clarín (Poliarquía, Nueva Mayoría) y los diarios provinciales no tienen notas en línea con cifras de balotaje. Lo que faltaría está en papel o en hemerotecas pagas. Ninguna fuente publica segundas preferencias de los votantes de Menem.

El peor residuo nuevo es López Murphy–Menem de Zuleta en febrero: 59,7 observado contra 67,8 ajustado, cuando López Murphy todavía era poco conocido.

## Reproducir

Desde la raíz, Python 3.11 con las dependencias ya usadas por el proyecto y Node:

```powershell
python -X utf8 analisis/escenarios2003/preparar.py
node analisis/escenarios2003/verificar.js
node analisis/escenarios2003/verificar_local.cjs
python -X utf8 analisis/escenarios2003/preparar_atlas.py
node analisis/escenarios2003/revisar_pagina.cjs
node analisis/escenarios2003/revisar_atlas.cjs
python -X utf8 analisis/escenarios2003/renderizar.py
```

Los scripts de revisión del navegador usan la instalación local de playwright-core del equipo y Edge; ajustar esa ruta en otra computadora. El simulador y los 18 HTML finales no necesitan Node, Python ni archivos externos. `datos.json`, `encuestas.json` y los manifiestos registran las entradas. No se envió ni publicó material en servicios externos, no se generaron paquetes Commons y no se actualizó memoria.
