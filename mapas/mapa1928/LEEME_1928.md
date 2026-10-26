# Mapa electoral 1928 (estilo Wikipedia 1999) — fuente principal: Cantón (1968)

`atlas_1928.html` — HTML autónomo, 4 pestañas: GANÓ (bloque ganador por tramos de %), UCR (% Yrigoyen), OPO (% oposición) y PART (participación). Hover = mini ventana, clic = tarjeta con **todas las columnas de partido de Cantón**, zoom/arrastre, buscador, descargas SVG/PNG/CSV.
Regenerar: `python build_1928.py` (necesita `shapely`).

## Fuentes
- **Votos:** D. Cantón, *Materiales para el estudio de la sociología política en la Argentina* (1968), tomo II, pp. PDF 105–122: «Elecciones nacionales de electores de presidente y vice, 1928 (varones solamente)». Transcrito **a mano desde las imágenes** a `canton/p_*.txt` (una por jurisdicción, con la leyenda de columnas de cada página).
- **Geometría:** `Departamentos_1914.shp` (censo de 1914).
- **Equivalencias de nombres:** Cacopardo (1967), DTS n.º 47, Cuadro 1.
- **Lupu–Stokes:** solo como control cruzado y para resolver celdas borrosas.

## ¿Es confiable el OCR?  No.
Contra los valores de Lupu (que coinciden con la imagen en las 60 celdas de Capital que verifiqué), el texto OCR del PDF acierta entre 0 % y 70 % de los números según la provincia (Corrientes, Jujuy, Mendoza, San Juan y Tucumán: 0 %); además descoloca filas y nombres. Por eso no se usó el OCR para ningún voto.

## Validación de la transcripción
- 1.802.111 inscriptos (oficial 1.807.566) y 1.461.018 votantes (≈ 1.461.600).
- UCR 838.465 vs 839.140 oficiales (99,9 %).
- 15 jurisdicciones contrastadas fila por fila con Lupu (`canton/check.py`): coinciden salvo 11 celdas borrosas (`canton/dudosas.txt`, resueltas con el valor de Lupu que cierra con el resto de la fila) y una diferencia que se conserva como impresa (Córdoba/Unión).
- Hay inconsistencias propias de la fuente (la suma de partidos no coincide con los votantes en Chascomús, Coronel Pringles, Coronel Suárez, General Arenales, Graneros): se conservan y la tarjeta lo avisa.

## Qué aporta Cantón respecto de Lupu
Lupu cubría 83 % de los votos. Cantón agrega unidades que a Lupu le faltan (Avellaneda, La Plata, Quilmes, Bahía Blanca, Necochea, Caseros, Orán, San Rafael, General Pedernera y La Capital de San Luis, Colón, Concordia, La Paz y Villaguay de Entre Ríos…), inscriptos y votantes (participación), y las columnas que Lupu descartaba (Frente Único Melo–Gallo, liberales, lencinistas, comunistas, blanco). Lupu no tenía ninguna unidad con votos que Cantón no tenga: no quedó ningún hueco por rellenar con Lupu.

## Agrupación para el mapa (las fórmulas de la Wikipedia)
Se sigue la tabla de resultados de «Elecciones presidenciales de Argentina de 1928» (es.wikipedia), con sus colores:
- **Hipólito Yrigoyen** (#E10019): UCR.
- **Leopoldo Melo** (#76ACDC): Confederación de las Derechas. Suma a la UCR Antipersonalista, el Frente Único, los conservadores, la UCR Unificada, los lencinistas, los bloquistas y los liberales. Da 430.354 votos, contra 430.050 en Wikipedia.
- **Mario Bravo** (#FF9900): Partido Socialista.
- **José N. Matienzo** (rosa): las listas «UCR Ferrocarril a Jáchal / a Calingasta» de San Juan. Da 6.000 votos, igual que Wikipedia.
- **Partido Demócrata Progresista** (#005C9E): no presentó fórmula.
- Los comunistas y los varios van a «otros».

## Límites
- Sin polígono en 1914: Alberdi (Sgo. del Estero, 955 votantes). Sus votos están en los totales provinciales, no en el mapa.
- Cantón marca como «subsumidas» Berisso, Ensenada, Escobar, Lanús, Tres Arroyos, Benito Juárez, General Roca (Córdoba), Chimbas, etc.: sus polígonos salen en gris oscuro.
- Antofagasta de la Sierra, Susques, Pastos Grandes y San Antonio de los Cobres eran el Territorio Nacional de Los Andes (no votaba): gris claro, igual que los demás territorios.
- Asignaciones aproximadas: Rawson ↔ Trinidad, Capital de San Juan → tres polígonos, Güemes ↔ Campo Santo.
- Santa María (Córdoba): inscriptos y votantes ilegibles/incoherentes; se usa la suma de partidos.
- Capital Federal: ahora por circunscripción (las 20 de Cantón coinciden con las `Circ. 01–20` de 1914 por número).

## Emblemas de la leyenda
Son los que usa Wikipedia, tomados de `../logos_wikipedia/` (ver `LICENCIAS.md` allí):
- **Yrigoyen:** escudo de la UCR.
- **Melo:** monograma de la UCR Antipersonalista.
- **Bravo:** emblema del PS.
- **PDP:** escudo del PDP.
- **Matienzo:** no tiene emblema en Wikipedia, así que lleva la sigla MC.

Aviso: el escudo de la UCR tiene su primer uso documentado en 1931.

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
