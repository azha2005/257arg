# Atlas de las elecciones presidenciales del 2 de abril de 1922

Archivos: `atlas_1922.html` (autónomo, abrir en el navegador) y `dataset_1922.json`. Se regenera con `python build_1922.py`.

## Qué muestra

- **Departamentos**: votos por partido de electores de presidente, tomados de D. Cantón, *Materiales para el estudio de la sociología política en la Argentina* (1968), t. II, pp. PDF 70–85, transcritos a mano de las imágenes de la página (el OCR del PDF no es confiable). Los datos están en `canton/p_*.txt`.
- **Provincias y total del país**: cuadro por distrito de la Memoria del Interior 1921-22 (pp. 239–310), tal como lo reproduce la Wikipedia (*Elecciones presidenciales de Argentina de 1922*). **No se verificó contra la Memoria** (Google Books no permite buscar dentro del volumen, id `6UpNAQAAIAAJ`). Cada fila cierra: votos de partidos + blancos y diferencia de actas = votantes. Los totales nacionales coinciden con los de la Wikipedia (Alvear 419.170, Piñero 231.102, Repetto 78.472, Laurencena 58.749, Ibarguren 41.841); «otros» da 810 en lugar de 809 por la suma de las filas provinciales.
- **Geometría**: departamentos del censo de 1914 (igual que los atlas de 1928 y 1916).
- Porcentajes sobre votantes (no sobre votos válidos), por eso Alvear figura con 47,76 % y no con el 50,49 % de la Wikipedia, que usa votos de las candidaturas principales.

## Bloques (candidaturas de la Wikipedia)

| Bloque | Candidato | Color (Wikipedia) | Emblema | Listas de Cantón que se suman |
|---|---|---|---|---|
| UCR | Marcelo T. de Alvear | #E10019 | Escudo de la UCR | UCR; en Tucumán, «Radicales opositores» |
| CON | Norberto Piñero | #30D5C8 | sigla CN | Concentración Nacional, Unión Provincial (Salta), Unión Popular (La Rioja), demócratas de Córdoba, liberales (Tucumán, San Luis) |
| SOC | Nicolás Repetto | #FF9900 | Emblema del PS | Socialistas |
| DIS | Miguel Laurencena | #FF5500 | sigla UCRD (no hay emblema en Wikipedia) | Radicales disidentes: principistas, bloquistas (San Juan), rojos (San Luis), intransigentes (Entre Ríos), UCR de Tucumán |
| PDP | Carlos Ibarguren | #005C9E | Escudo del PDP | Demócratas progresistas (Capital Federal y Santa Fe) |

Los colores de cada lista dentro del bloque son los de la tabla de resultados de Wikipedia. Las fuentes de los emblemas están en `../logos_wikipedia/LICENCIAS.md`. El escudo de la UCR tiene su primer uso documentado en 1931.

## Lo que falta o es dudoso

- **Mendoza y Santiago del Estero**: Cantón no trae sus cuadros de 1922 y se buscaron en La Prensa del 2 al 8 y del 12 al 18 de abril de 1922 (Archive.org; faltan los números del 9, 10 y 11): no hay resultados por departamento y partido. Los departamentos quedan en beige; las provincias sí llevan color por el cuadro oficial.
  - Mendoza votó el 2 de abril (16 electores). La junta escrutadora nacional anuló la elección en 189 mesas y 5 no se constituyeron, y el decreto del 17 de abril declara la nulidad total (La Prensa 8 y 14 abr.; la elección de diputados se repitió el 4 de marzo de 1923). La fecha del 14 de mayo que figura en la Wikipedia no se confirma. Lo único departamental publicado son los sufragantes por departamento (La Prensa, 4 y 7 abr.), sin partidos.
  - Santiago del Estero: La Prensa solo informa el avance del recuento de sobres y revisión de urnas; no publica cómputo departamental. Un despacho local indica que concurrieron los radicales «blancos» y la oposición se abstuvo (sin confirmar con otra fuente).
- **Territorios nacionales y Los Andes**: gris, no votaban.
- **Unidades sin dato (gris oscuro)**: Juárez y Tres Arroyos (Buenos Aires), General Roca (Córdoba) y Chimbas (San Juan), filas subsumidas en Cantón; Castro Barros, Independencia, Gobernador Gordillo y San Blas de los Sauces (La Rioja), Cachi y Metán (Salta), Cruz Alta y Chicligasta (Tucumán), solo con inscriptos o votantes.
- **Sin votantes en Cantón** (Catamarca, Jujuy, La Rioja, Salta, San Juan, San Luis): los porcentajes son sobre la suma de los votos de los partidos y no hay participación.
- **Inscriptos «reconstruidos» por Cantón** en Corrientes, Entre Ríos, Jujuy, La Rioja, Salta, San Juan, San Luis y Tucumán: no son los del padrón. La participación de esas provincias hereda esa limitación.
- **Buenos Aires**: los votantes son cifras preliminares de La Prensa (3 de abril) y en muchos partidos son menores que la suma de los partidos; en ese caso porcentajes y participación se calculan sobre la suma.
- **Celdas ilegibles o con `?`**: Yavi (Jujuy, columna Concentración, ¿9 o 2?, no se computa), Humahuaca (Jujuy, mancha de tinta, se lee 0), Burruyacú (Tucumán, Socialista, sin dato).
- **Tres cifras donde la página impresa y Lupu–Stokes difieren** (se conserva la impresa): Valle Viejo (Catamarca) Concentración 322 vs 622; General Pinto (Buenos Aires) Concentración 435 vs 425; Paraná (Entre Ríos) Concentración 5.516 vs 5.517. Las demás sumas por partido coinciden con Lupu–Stokes.

## Tucumán: asignación de listas inferida

Cantón rotula «Unión Cívica Radical» a una lista y «Radicales opositores» a otra. Las sumas de las columnas (sin Cruz Alta ni Chicligasta, que Cantón no trae) son 10.675 y 5.043. La Memoria asigna a Alvear 6.821 votos y a Laurencena 16.671. Como la suma parcial de la lista «UCR» de Cantón (10.675) supera el total de Alvear, no puede ser la de Alvear: se asignó «UCR» de Cantón a los radicales disidentes (Laurencena) y «Radicales opositores» a Alvear. Es una inferencia, no un dato impreso.

## Pendiente

- Las cifras provinciales deberían confrontarse con la Memoria del Interior (HCDN o archivo).
- Cantón se apoya en prensa de la época, de modo que la suma departamental no coincide exactamente con el total provincial oficial.

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
