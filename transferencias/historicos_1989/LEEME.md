# Diez cruces históricos de 1983 a 1999

Los diez están terminados con selector provincial, SVG, PNG, matrices, bootstrap de 200 remuestreos, variante nacional de Calvo y controles. [Índice de todos los cruces solicitados](../INDICE_NUEVOS_CRUCES.md).

Son inferencias ecológicas sobre unidades territoriales: describen asociaciones compatibles con los resultados agregados, no cambios de voto observados de personas. En seis años cambian también la composición del electorado y la participación. No se puede interpretar una cinta como seguimiento individual.

## Cuánto sirven

| Par | Unidades usadas | Cobertura del voto desglosado de origen | Separación de filas grandes | RMSE modelo / promedio provincial, puntos | Mejora del error |
|---|---:|---:|---:|---:|---:|
| [1989 presidente → 1995 presidente](../1989p_1995p/sankey_1989p_1995p.html) | 503 | 97,13 % | 27,4 | 3,83 / 4,83 | 20,7 % |
| [1989 diputados → 1994 constituyentes](../1989d_1994c/sankey_1989d_1994c.html) | 514 | 99,53 % | 32,2 | 2,32 / 3,01 | 22,7 % |
| [1985 diputados → 1987 diputados](../1985d_1987d/sankey_1985d_1987d.html) | 507 | 96,44 % | 46,8 | 1,61 / 3,26 | 50,7 % |
| [1983 presidente → 1989 presidente](../1983p_1989p/sankey_1983p_1989p.html) | 501 | 98,73 % | 37,7 | 2,05 / 4,13 | 50,5 % |
| [1987 diputados → 1989 presidente](../1987d_1989p/sankey_1987d_1989p.html) | 508 | 97,75 % | 47,7 | 2,17 / 4,05 | 46,4 % |
| [1985 diputados → 1989 presidente](../1985d_1989p/sankey_1985d_1989p.html) | 506 | 98,86 % | 41,0 | 2,21 / 4,06 | 45,4 % |
| [1989 presidente → 1997 diputados](../1989p_1997d/sankey_1989p_1997d.html) | 497 | 98,02 % | 30,0 | 2,92 / 3,73 | 21,7 % |
| [1995 presidente → 1997 diputados](../1995p_1997d/sankey_1995p_1997d.html) | 517 | 97,07 % | 33,5 | 2,53 / 3,70 | 31,5 % |
| [1995 presidente → 1999 presidente](../1995p_1999p/sankey_1995p_1999p.html) | 506 | 96,59 % | 35,8 | 3,09 / 4,71 | 34,5 % |
| [1983 presidente → 1985 diputados](../1983p_1985d/sankey_1983p_1985d.html) | 519 | 99,33 % | 33,7 | 2,26 / 2,99 | 24,4 % |

**1989p–1995p sirve como comparación descriptiva, con reservas.** Las filas grandes de Menem y Angeloz conservan señal territorial, y el modelo mejora el error frente al promedio provincial. Está cerca del umbral de separación de la auditoría (25 puntos). La Alianza de Centro no queda identificada: su reparto cambia hasta 55,1 puntos según la variante. Blanco y nulo tampoco queda identificado. Entre el modelo provincial ponderado y Calvo nacional cambia el reparto del 19,70 % del volumen modelado; aun las filas grandes difieren hasta 15,5 y 12,1 puntos en alguna celda. Por eso no respalda porcentajes precisos de retención individual ni afirmaciones fuertes sobre Alsogaray.

**1989d–1994c sirve para explorar la recomposición de los bloques grandes, con mayor sensibilidad de especificación.** Mejora frente al promedio provincial, pero cambia el reparto del 29,83 % del volumen al pasar a Calvo nacional. Alianza de Centro, CFI, Unidad Socialista, Fuerza Republicana, MPN y blanco/nulo están marcados como no identificados. También se comparan cargos distintos.

**1985d–1987d es el más informativo de los tres en este diagnóstico.** Separa mejor las filas grandes y reduce aproximadamente a la mitad el error frente al promedio provincial. El reparto de Frente del Pueblo, PRS y blanco/nulo es inestable. La base de 1987 tiene errores documentados; se excluyen las unidades con grandes discrepancias, sin inventar cifras para corregirlas. Cambia el reparto del 12,90 % del volumen entre variantes.

**Los tres cruces adicionales hacia 1989 muestran señal descriptiva en las fuerzas grandes.** La sensibilidad global principal/Calvo es 8,45 % para 1983p, 11,09 % para 1987d y 10,63 % para 1985d. Permanecen sin identificar PI, MID, MOFEPA y Otros en 1983p; FAP y Bloquista en 1987d; PAL en 1985d. El cambio de cargo en los dos cruces legislativo–presidencial limita su interpretación como continuidad de un partido.

**1989p–1997d sirve para una exploración general, con reservas fuertes.** Mejora el error territorial 21,7 % frente al promedio provincial, pero cambia el reparto del 29,81 % del volumen entre especificaciones. Alianza de Centro, Unidad Socialista, MPN, Otros y blanco/nulo no quedan identificados. La Alianza de 1997 agrupa UCR y FREPASO según la tabla del atlas, incluso donde presentaron listas separadas: una cinta hacia «Alianza» no distingue entre ambas fuerzas. San Luis no tiene desglose departamental en esta base y queda fuera; no se distribuye artificialmente su total provincial. El intervalo de ocho años implica una renovación del electorado importante.

**1995p–1997d y 1995p–1999p muestran señal descriptiva en las candidaturas principales.** Reducen el error territorial frente al promedio provincial un 31,5 % y un 34,5 %, respectivamente. La sensibilidad global principal/Calvo es del 23,86 % y del 12,05 % del volumen. En ambos quedan sin identificar Otros y blanco/nulo. La coincidencia es mayor en 1995p–1999p; las filas de las candidaturas principales no superan el umbral de inestabilidad de la auditoría, pero eso no equivale a certeza individual.

**1983p–1985d merece una lectura específica de Buenos Aires.** Nacionalmente mejora un 24,4 % frente al promedio provincial y tiene sensibilidad global principal/Calvo del 23,63 %. Las filas pequeñas son inestables: PI, MID, Alianza Federal, Bloquista, MOFEPA, Otros y blanco/nulo aparecen marcados. En PBA se conservan los **125 partidos**, sin las fusiones necesarias para otros pares de este proyecto, con cobertura del **100 % de los votos desglosados de origen**. Para la fila Luder 1983, el principal provincial estima 47,4 % hacia el peronismo renovador y 23,1 % hacia PJ en 1985; el ajuste Calvo solo en PBA da 50,2 % y 20,8 %. La fila Alfonsín hacia UCR da 72,6 % y 75,8 %. [Tabla provincial, intervalos y reservas](../1983p_1985d/PBA.md), [abrir el gráfico de PBA](../1983p_1985d/sankey_1983p_1985d.html#02). El diagnóstico interno de PBA reduce el error un 27,0 % frente al promedio provincial; describe asociaciones territoriales entre resultados, no seguimiento de personas.

El diagnóstico usa cinco particiones de unidades dentro de cada provincia. En cada partición se vuelve a estimar el centro nacional exclusivamente con entrenamiento; con cinco o más unidades de entrenamiento se estima la matriz provincial. La referencia es el promedio provincial de entrenamiento. Se evalúan todas las categorías con pesos por votos de destino. La penalización se mantiene fija en la elegida previamente: es un diagnóstico interno, no una validación externa independiente, y el error territorial no valida transferencias individuales. El bootstrap mantiene fijo el centro nacional y no incorpora toda la incertidumbre territorial o de especificación. [Resultados y sensibilidad por fila](diagnostico.json).

## Datos y denominador

Se leen directamente los CSV de `base8399/ernesto/`, conservando los originales: `1983_presidente`, `1989_presidente`, `1995_presidente`, `1989_diputados`, `1994_constituyentes`, `1985_diputados`, `1987_diputados`, `1997_diputados` y `1999_presidente`. [Rutas y SHA-256](fuentes.json), [fuentes auxiliares y sus SHA-256](fuentes_auxiliares.json). Las agrupaciones siguen las tablas de correspondencias de los atlas locales: [mapeos exportados por elección](bloques_1989p.csv); los otros ocho archivos `bloques_*.csv` están en esta carpeta. En 1997 los códigos `pos`/`pos19` son métricas de positivos, aunque la base los etiquete como agrupación: se excluyen de las fuerzas. Si hay más de una cifra declarada de positivos, se toma para control la más cercana a la suma de partidos, como hace el atlas; los votos partidarios no se modifican.

En 1999 se reutiliza exclusivamente la función de clasificación de candidaturas de `../presidente_1999.py`: UCeDé con Duhalde salvo Santa Fe, donde acompaña a Cavallo; listas de la Alianza y sus aliados con De la Rúa. `acjc00` es el subtotal de sublemas de Corrientes y Santiago del Estero: se excluye para no duplicar sus hijos. **No se ejecuta `base99()` ni `sl_sc()`**, que en el cruce antiguo 1999–2003 complementan provincias y reparten categorías menores. Este nuevo cruce usa solo datos originales de Ernesto: faltan San Luis y Santa Cruz, con 22 distritos utilizables. En 1997 falta San Luis, con 23 distritos. Deseado 1995 participa en 1995p–1997d, pero no en 1995p–1999p por faltar Santa Cruz en destino.

No hay una serie completa y consistente de electores en todos los años y provincias. Por eso el denominador es **suma de votos partidarios + blancos + nulos + impugnados/recurridos registrados**, sin abstención. En 1994 los impugnados y recurridos se incluyen en la categoría visual «Blanco y nulo». Los totales declarados se conservan como control, no se usan para inventar un partido residual. [Cifras originales y diferencias](control_datos_originales.csv).

Los campos heredados `electores_*` y `crecimiento_padron_mediano` de `control.json` representan aquí votos desglosados; `base_medida` lo señala. La cobertura informada en estos cruces **no es cobertura del padrón**. El origen se escala al volumen de votos de destino por unidad, como en los demás modelos; sus porcentajes en el Sankey son esos volúmenes modelados.

Se excluyen unidades si el desglose de partidos difiere de los positivos declarados en más de 100 votos y más del 1 % de los positivos. Además se excluye La Plata 1987 por el error documentado PJ 11.919/111.903. Se mantiene también el filtro general del proyecto: razón de volúmenes entre 0,75 y 1,33 del crecimiento mediano. [Exclusiones por calidad](exclusiones.json); las exclusiones adicionales por razón de volúmenes están en cada `control.json`. Las discrepancias menores quedan registradas, sin imputación.

## Deseado presidencial 1995: extrapolación autorizada

Por pedido explícito del usuario se calcula, para cada una de las tres candidaturas principales, **total de Santa Cruz en la tabla provincial − votos de los otros seis departamentos**:

| Candidatura | Total provincial | Otros seis | Deseado extrapolado | Original en la base | Agregado |
|---|---:|---:|---:|---:|---:|
| Menem | 41.666 | 24.732 | 16.934 | 144 | 16.790 |
| Bordón | 16.342 | 11.761 | 4.581 | 19 | 4.562 |
| Massaccesi | 12.374 | 7.406 | 4.968 | 55 | 4.913 |

Se usa `mapa1995/wiki_prov.json`, respaldado por `mapa1995/w1995.txt`. El cálculo reproduce el residuo ya documentado en `mapa1995/LEEME_1995.md`. Las fuerzas menores, blancos y nulos quedan como en la base; no se distribuye el resto del total declarado de Deseado. [Originales, operación y resultado](deseado_1995_extrapolado.json).

Deseado entra efectivamente al ajuste. Al retirarlo y reajustar con la misma penalización, la máxima variación por celda nacional es 0,066 puntos en las filas partidarias y 1,722 en blanco/nulo. Es una comprobación de sensibilidad a esa unidad, no prueba de exactitud de la extrapolación.

## Correspondencias territoriales

Se usan nombres revisados, no equivalencias automáticas INDRA–INDEC. [Todas las claves de origen y destino](correspondencias.csv). Capital conserva sus 28 circunscripciones; el contador técnico «departamentos» incluye esas circunscripciones y las uniones completas. Los atlas y sus polígonos no se modifican.

- 1989p–1995p: General Sarmiento con San Miguel/José C. Paz/Malvinas Argentinas; Morón con Hurlingham/Ituzaingó; General Pinto con Florentino Ameghino; Magdalena con Punta Indio. Esteban Echeverría, San Vicente y Florencio Varela se comparan como unión conjunta con esos tres más Ezeiza y Presidente Perón, porque este último recibió partes de los tres municipios antiguos.
- 1989d–1994c: General Pinto + Florentino Ameghino, 12 de Octubre + 2 de Abril, y Ushuaia + Sector Antártico Argentino. No se agrega una escisión que todavía no aparece en esa base.
- 1985d–1987d: Pellegrini + Tres Lomas y Capital de Jujuy + Palpalá. En Jujuy, San Juan y Santiago del Estero los nombres de 1985 se recuperan por código INDRA de la propia base de 1983. Pilagá/Pilagás e Ibarra/Matará llevan alias explícitos. Tierra del Fuego no eligió diputados en 1987: hay 23 distritos y no se fabrica una matriz para ese territorio.
- 1983p/1987d/1985d→1989p: se llevan los dos extremos a las mismas uniones completas; se agrega Capital–Palpalá y Pellegrini–Tres Lomas. En 1983 también Gualeguaychú–Islas del Ibicuy. No se emparejan departamentos separados contra una sola unidad agregada. Tierra del Fuego no está en 1987 y en los pares con origen 1983/1985 sus dos unidades superan el filtro de crecimiento: se informa esa ausencia, con 23 distritos.
- 1989p→1997d: las uniones de las nuevas divisiones bonaerenses y 2 de Abril son las mismas que en 1989p→1995p. Se corrigen únicamente alias de escritura revisados (Conorel Dorrego, Tres Arrollos, Adolofo Alsina, etc.). San Luis, ausente de la base, no se completa con una estimación departamental.
- 1995p→1997d / 1999p y 1983p→1985d usan los archivos `raw_<año>.pkl` de esta carpeta, preparados sin agregaciones heredadas de otros pares. Para PBA 1983–1985 no hace falta ninguna unión: los 125 partidos se conservan individualmente. Para 1995–1997 se conservan las divisiones bonaerenses nuevas porque ya existen en ambos extremos; General Guido se excluye por calidad de la fuente de 1995. En 1995–1999 también se excluye Pinamar por el filtro de crecimiento. Los alias de 1999 son explícitos; se quitan los códigos añadidos al nombre tras un guion en Misiones y Río Negro.
- San Salvador se creó con partes de **Colón, Concordia y Villaguay**, según la [Municipalidad de San Salvador](https://sansalvadorer.gob.ar/ciudad/departamento/) y la [Dirección de Estadística de Entre Ríos](https://www.entrerios.gov.ar/dgec/wp-content/uploads/2024/05/Entre-Rios-los-cambios-en-la-estructura-por-sexo-y-edad-segun-Censos-siglo-XXI-1.pdf). En los dos nuevos cruces desde 1995 se comparan las uniones completas de esos tres departamentos, sumando San Salvador donde la base lo separa. No se supone que todo el departamento nuevo salió de Concordia. El CSV de 1997 no separa San Salvador y por eso también se agregan allí los tres departamentos de origen. En 1995–1999 Ushuaia y Antártida se agregan para conservar territorio común. En 1983–1985 se agrega Gualeguaychú con Islas del Ibicuy en Entre Ríos.

Cada `correspondencias.csv` de los tres pares nuevos lleva `departamento_original`, clave normalizada y clave común. El archivo global de esta carpeta conserva también `circuito_normalizado`, para reconstruir los alias sin depender de la clave agregada que usan los cruces anteriores.

Fuentes territoriales: [Ley bonaerense 11.480, Presidente Perón](https://www.rpba.gob.ar/files/Normas/Leyes/Ley-11480-BsAs.pdf), [Disposición INDEC 84/1996 que documenta los tres partidos de origen](https://www.argentina.gob.ar/normativa/nacional/disposici%C3%B3n-84-1996-34645/texto), [Ley 11.610, Hurlingham e Ituzaingó](https://www.rpba.gob.ar/files/Normas/Leyes/Ley-11610-BsAs.pdf), [Florentino Ameghino, Disposición INDEC 16/1991](https://www.argentina.gob.ar/normativa/nacional/disposici%C3%B3n-16-1991-185427/texto), [Palpalá, documentación del Ministerio de Economía](https://cdi.mecon.gov.ar/bases/docelec/br1022.pdf), además de las decisiones territoriales documentadas en los atlas locales 1985, 1987, 1989, 1994 y 1995.

## Reproducir

1. `python transferencias/historicos_1989.py`: prepara bases y controles; no edita los CSV originales.
2. `python transferencias/generar_historicos_1989.py`: ajusta los diez pares, cinco penalizaciones y 200 bootstrap. `--tanda95` procesa solo los tres últimos.
3. `python transferencias/diagnostico_historicos.py`: diagnóstico de utilidad y sensibilidad a Deseado.
4. `python transferencias/verificar_nuevos_cruces.py --solo-historicos`: verifica matrices, selector, porcentajes y genera PNG.
5. Para la última tanda, ejecutar `python transferencias/diagnostico_historicos.py --tanda95`, `python transferencias/revisar_pba_1983_1985.py` y `python transferencias/verificar_nuevos_cruces.py --tanda95`. La revisión PBA añade 200 remuestreos provinciales con centro nacional fijo.

Los resultados individuales y las alertas de cada fila están en `RESUMEN.md` de cada par y en `../AUDITORIA.md`.
