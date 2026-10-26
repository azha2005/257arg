# Mapa electoral 1930, diputados nacionales (estilo Wikipedia 1999), según Cantón (1968)

`atlas_1930.html` es un HTML autónomo con 5 pestañas:
- **GANÓ:** bloque ganador.
- **UCR:** % alianza UCR.
- **CD:** % Confederación de las Derechas.
- **UCRA:** % radicalismo antipersonalista.
- **PART:** participación.

Se usa igual que el atlas 1928: hover, tarjeta con todas las columnas de Cantón, zoom, buscador y descargas.
Para regenerarlo: `python build_1930.py`. El control fila por fila contra Lupu–Stokes se corre con `python canton/check.py`.

## Fuentes
- **Votos:** D. Cantón, *Materiales…* (1968), tomo II, pp. PDF 123–140: «Elecciones nacionales de diputados, año 1930 (varones solamente)», elección del 2 de marzo de 1930.
  - Se transcribió a mano desde las imágenes (`img/p123–p140.png`) a `canton/p_*.txt`. No se usó OCR.
- **Totales provinciales:** tomo I, cap. III, pp. PDF 182–183 (`img/t1_p182.png`, `t1_p183.png`).
- **Geometría y equivalencias de nombres:** las mismas del atlas 1928 (departamentos de 1914 y Cacopardo 1967).

## Cobertura
- Hay 14 jurisdicciones y 391 filas.
- **San Luis no votó.** El cuadro del tomo I la marca «sin elecciones» y Lupu no tiene filas para ella.
- Capital Federal está por circunscripción. En Buenos Aires hay 120 partidos (Lupu trae 95).

## Validación
- **Contra Lupu, fila por fila (`canton/check.py`):**
  - Coinciden la UCR, el PS y el total en todas las filas que Lupu trae, salvo tres:
    - Rivadavia (BA): ±2.
    - Tupungato (Mza.): Liberal 128 impreso contra 178 en Lupu.
    - Choya (SdE): +18.
  - Lupu suma en «ucr» todas las fracciones radicales, por eso `spec.py` tiene una lista `ucr=` por provincia. Las fracciones sumadas son:
    - lencinistas y Rojo (Mendoza);
    - bloquistas (San Juan);
    - Caballero y Unificada (Santa Fe);
    - Unificada y Corvalanista (SdE);
    - Opositora y UCR de Tucumán (Tucumán);
    - Situacionista (Catamarca);
    - J. y P. (Jujuy).
- **Contra el tomo I:**
  - Inscriptos 1.981.289 contra 1.981.246.
  - Votantes 1.481.343 contra 1.481.855.
  - La columna UCR da 624.608 (sin la Figueroísta, 618.050) contra 618.411 (+6.197). La diferencia está toda en cuatro provincias, donde el propio Cantón no cierra entre su cuadro departamental y el provincial:

    | Provincia | Diferencia | Explicación |
    |---|---|---|
    | Santa Fe | +3.129 | Las filas coinciden con Lupu |
    | Buenos Aires | +1.590 | Inscriptos y votantes coinciden exactos |
    | Corrientes | +1.000 exactos | San Martín 1.264 es nítido |
    | Córdoba | +481 | Es la corrección manuscrita de General San Martín |

- Los casos que se conservan tal como están impresos, con su motivo, están en `canton/dudosas.txt`.

## Inconsistencias propias de la fuente (se conservan; la tarjeta las avisa)
- **La suma de partidos excede a los votantes:**
  - San Cristóbal Sud (Capital);
  - Luján (Mza.);
  - Garay y San Javier (SF). En San Javier también excede a los inscriptos.
  - Aguirre, Moreno, Quebrachos, Robles y Salavina (SdE);
  - Cruz Alta y Trancas (Tuc.).

  En todos los casos Lupu coincide en los partidos.
- **Necochea:** 23.952 inscriptos para 8.235 votantes, quizá 13.952. El total provincial del tomo I incluye el 23.952.
- **Correcciones manuscritas que se usan:**
  - General San Martín y Juárez Celman (Córdoba);
  - votantes de Calingasta (San Juan, 444);
  - inscriptos de la Capital de Tucumán (29.369).

## Agrupación para el mapa (la de Wikipedia)
Se sigue la tabla de «Elecciones legislativas de Argentina de 1930» (es.wikipedia), con sus colores:
- **Unión Cívica Radical** (#E10019): UCR + UCR Situacionista (Catamarca).
- **Confederación de las Derechas** (#30D5C8):
  - Conservador (BA);
  - Partido Demócrata de Córdoba (Cantón lo rotula «Conservador» en el t. II y «Demócrata Progresista» en el cuadro del t. I);
  - liberales de Corrientes, Mendoza y Tucumán;
  - Coalición Autonomista (Corrientes);
  - Unión Provincial (Salta).
- **Radicalismo Antipersonalista** (#76ACDC):
  - UCR Unificada (SF, SdE) y UCR Antipersonalista (ER);
  - Caballerista, Opositora, Corvalanista, Principista, Roja, UCR de Tucumán;
  - **UCR Figueroísta:** la columna que Cantón rotula «UCR» en Catamarca (6.558 votos, igual cifra en Wikipedia);
  - **UCR Disidente:** la «J. y P.» de Jujuy (3.394).
- **Van aparte:** PS (#FF9900), PSI (#FFC0CE), PDP (#005C9E), UCR Lencinista (#FF5500), UCR Bloquista (#44944A).
- **«Otros»:** Bandera Blanca, Agrario, Salud Pública, Popular y comunistas.

Totales nacionales del atlas contra Wikipedia:

| Bloque | Atlas | Wikipedia |
|---|---|---|
| UCR | 628.017 | 622.961 |
| CD | 295.899 | 296.854 |
| Radicalismo Antipersonalista | 166.214 | 164.654 |

El bloque ganador suma listas que compitieron por separado (por ejemplo, Liberal y Autonomista en Corrientes). La tarjeta muestra cada lista.

## Límites
- **Alberdi (SdE):** no tiene polígono en 1914; sus 717 votantes están en el total provincial.
- **San Cayetano (BA):** Cantón no trae datos.
- **Cifras «subsumidas» (gris oscuro):**
  - Berisso, Ensenada, Escobar, Lanús, Tres Arroyos, Juárez, Gonzáles Chaves, Hipólito Irigoyen, Leandro N. Alem, 3 de Febrero y C. de M. Leonardo Rosales (BA);
  - General Roca y Pte. Roque Sáenz Peña (Córdoba);
  - Antofagasta (Catamarca), General Alvear (Corrientes), Susques (Jujuy);
  - General Alvear y Malargüe (Mza.);
  - General San Martín y Los Andes (Salta);
  - Chimbas y Zonda (San Juan).
- Las asignaciones aproximadas de nombres son las mismas que en 1928.

## Emblemas de la leyenda
Son los que usa Wikipedia, tomados de `../logos_wikipedia/` (ver `LICENCIAS.md` allí):
- **UCR:** escudo de la UCR.
- **CD:** solo la sigla, por decisión del usuario.
- **Radicalismo antipersonalista:** monograma de la UCR Antipersonalista.
- **PS y PSI:** sus logos.
- **PDP:** escudo del PDP.
- **Bloquistas:** estrella bloquista.
- **Lencinistas:** no tienen emblema en Wikipedia, así que llevan la sigla UCRL.

## Resultado nacional (topline)
La torta, las barras y las métricas nacionales salen de la tabla de resultados del artículo de Wikipedia, cargada en `../wikitop.py`, para que el atlas diga lo mismo que el artículo. Los porcentajes de esa tabla son sobre votos positivos (válidos).

Los departamentos y las provincias siguen saliendo de Cantón, y ahora también se calculan sobre votos positivos: la suma de los partidos, sin blancos. Los blancos y los votos no atribuidos se muestran sobre los votos emitidos. La participación es votantes sobre inscriptos.

La suma de los departamentos no tiene por qué dar la cifra nacional. Las fuentes son distintas: Cantón por un lado, y el escrutinio de la Cámara o la Memoria del Interior que cita Wikipedia por el otro.

## Unidades «subsumidas» (Cantón, t. I, Apéndice C)
La nota de Cantón «cifras subsumidas bajo una unidad mayor o no tomadas en cuenta» remite al Apéndice C del tomo I («Lista de unidades geográficas sin datos electorales»). Para que sus datos fueran comparables entre 1912 y 1954, Cantón los sumó a una unidad vecina. El mapa reparte ese dato en los polígonos de 1914 correspondientes:
- **Necochea** incluye Juárez, Tres Arroyos y Gonzáles Chaves. Gonzáles Chaves se creó en 1916 y no existe en la base de 1914.
- **Juárez Celman** incluye General Roca y Pte. Roque Sáenz Peña. Pte. Roque Sáenz Peña es posterior a 1914.
- **Concepción** incluye Chimbas (San Juan). En esta base Concepción recibe el dato de la Capital.

El mismo apéndice da otros destinos que no cambian el mapa:
- C. de M. L. Rosales en Bahía Blanca, Lanús en Avellaneda y L. N. Alem en Lincoln: son partidos posteriores a 1914.
- General Alvear de Corrientes en General San Martín.
- General Alvear y Malargüe de Mendoza en San Rafael.
- Zonda en Rivadavia.
- Berisso, Ensenada, Escobar, Hipólito Yrigoyen, San Cayetano y Tres de Febrero: se crearon después de 1954.

En la tarjeta, el dato compartido lo dice («Dato único compartido por N polígonos»).
