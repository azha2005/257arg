# Diputados nacionales 1916 — atlas por departamento

`python build_1916.py` regenera `atlas_1916_diputados.html` (HTML autónomo, 1,5 MB) y `dataset_1916.json`.
Vistas: GANÓ (bloque más votado), UCR, CON (conservadores y afines) y PART (participación). Las tarjetas muestran las columnas partidarias de Cantón de cada unidad.

## Fuentes

| Qué | De dónde |
|---|---|
| 11 provincias + Capital Federal | `../1916dip/canton_diputados_1916/` (transcripción de Cantón 1968, t. II) |
| Salta | `../1916dip/` (expediente 58-D-1916, planilla del 15 de abril, 38 colegios) |
| Geometría | `Departamentos_1914` (censo de 1914), cache `units_raw.pkl` |
| Equivalencias de nombres | Cacopardo (1967), Cuadro 1; mismas que el atlas de 1928 |
| Cifras ilegibles | Lupu–Stokes (`cotejo_lupu_1916.csv`), solo para rellenar |
| Valle Grande, General Lamadrid, Independencia | *La Prensa*, 8/4/1916, p. 6; acta de la Junta Escrutadora de La Rioja (exp. 9-D-1916) |

## Cobertura

- **Con datos (13 de 15 jurisdicciones; Salta con partidos):** Buenos Aires, Capital Federal, Catamarca, Córdoba, Corrientes, Entre Ríos, Jujuy, La Rioja, Mendoza, Salta, San Luis, Santa Fe, Tucumán.
- **Pendientes (beige en el mapa):** San Juan y Santiago del Estero. Cuando haya cuadros, agregarlos en `build_1916.py` (capa de datos) y quitarlos de `PENDIENTES`.
- Los territorios nacionales y Los Andes no votaban (gris claro).
- 23 filas de Cantón no traen cifras porque están subsumidas en otra unidad (doble asterisco; p. ej. Tres Arroyos, Berisso, Lanús, Escobar): gris oscuro. «Puerto» (Capital) no tiene polígono.
- Otras 3 filas tienen «*» (sin datos) en Cantón y también están vacías en Lupu–Stokes. Se completaron con el escrutinio oficial (ver «Unidades sin datos en Cantón»).

## Decisiones que conviene revisar

1. **Bloques.** UCR = «Unión Cívica Radical» + Santa Fe «Radical situacionista (Comité Nacional)». Radicales disidentes (Santa Fe) van aparte. Conservadores y afines = Concentración, Conservador, Provincialista, Unión Popular, Unión Provincial (Salta), Liberal, Autonomista y «Demócrata» de Córdoba y San Luis. Socialista (PS) y Socialista Argentino (PSA, Capital) son bloques distintos: el PSA no es el PS (corrección del usuario) y Lupu–Stokes lo mete con los conservadores.
2. **«Demócrata» de Santa Fe = Partido Demócrata Progresista** (confirmado por el usuario). En Capital el rótulo ya es «Demócrata Progresista».
3. **Salta** (partidos confirmados por el usuario con la Wikipedia): lista Usandivaras–Cornejo = Unión Provincial (bloque conservador), Outes–Echazú = UCR, Lesser–Piniella = Socialista. Se usa el primer candidato de cada lista, de la planilla del 15 de abril; los 38 colegios se agrupan en 21 departamentos con la hipótesis de `correspondencias_colegios.csv`; Campo Santo usa la lectura 151 para Outes (ambigua frente a 157); no se aplica la elección complementaria de Rivadavia (+82 a los dos primeros). Salta suma sufragantes pero no hay inscriptos, así que queda fuera de la participación nacional.
4. **Cifras ilegibles.** Cantón tiene 94 celdas con «?». Se reconstruyeron así: 45 con Lupu–Stokes cuando encaja con los dígitos legibles; 1 por resto de la fila (Córdoba y San Luis, donde los partidos suman exactamente los votantes); 48 por estimación (el valor compatible con la lectura más cercano a lo esperable según votantes y la razón típica de la provincia). Cada tarjeta lo declara. Las estimaciones afectan a 10 cifras partidarias y 38 de inscriptos/votantes; el resto de la fila se conserva tal cual. Un «?» final puede ser un dígito ilegible o una marca de duda: se consideran ambas lecturas.
5. **Totales nacionales parciales.** El gráfico y las barras suman las 13 jurisdicciones con datos (sin San Juan ni Santiago del Estero); la UCR queda en 44,7 %, cerca del 44,76 % que cita la Wikipedia para todo el país, pero no es comparable estrictamente. La participación nacional excluye Capital y Salta (no hay inscriptos).
6. Cada columna de Cantón puede ser el candidato más votado de una lista y no el total del partido.

## Diferencias que no se resolvieron

Paclín (Concentración 294 vs 284 de Lupu), Tunuyán (Conservador 381 vs 361) y Paraná (UCR 6.205 vs 6.206) siguen como en el paquete de origen; Córdoba–Punilla y San Justo, donde Lupu no encaja con la lectura parcial (395 vs «33?», 1.823 vs «122?»), usan la estimación y no el valor de Lupu.

## Bloques, colores y emblemas (los de Wikipedia)

Desde el 11-oct-2026 el atlas sigue la tabla y el infobox de «Elecciones legislativas de Argentina de 1916» (es.wikipedia), pensando en subir los mapas allí. Las fuentes de los emblemas están en `../logos_wikipedia/LICENCIAS.md`.

| Bloque | Color | Emblema | Listas que suma |
|---|---|---|---|
| Unión Cívica Radical | #E10019 | Escudo de la UCR | UCR y radicales situacionistas (Comité Nacional) |
| Concentración Conservadora | #30D5C8 | sigla CC | Concentración, conservadores, demócratas (Córdoba, San Luis), Autonomista de Corrientes, provincialistas, Unión Popular, Unión Provincial |
| Demócrata Progresista | #005C9E | Escudo del PDP | PDP (y «Demócrata» de Santa Fe) |
| Partido Socialista | #FF9900 | Emblema del PS | Socialistas |
| Partido Socialista Argentino | #FF6700 | sigla PSA | Capital |
| UCR Disidente | #A52A2A | sigla UCRD | Santa Fe |
| Concentración Cívica | #35AAE0 | Pacto Autonomista Liberal | Liberales de Corrientes (16.837; Wikipedia, 17.910) |

**Aviso de anacronismo.** La versión anterior evitaba los emblemas posteriores a 1916 (una bandera blanca y roja para la UCR, campo rojo con la sigla para el PS). Ahora se usan los de Wikipedia. El escudo de la UCR tiene su primer uso documentado en 1931, y el logo del Pacto Autonomista-Liberal es moderno.

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

## Unidades sin datos en Cantón («*»)
Tres departamentos tienen en Cantón solo los inscriptos (o ni eso). Lupu–Stokes les da 0 votos. No son «subsumidos»: Cantón no los incluye en ninguna otra unidad. Se completaron con el escrutinio oficial, leído a ojo en las imágenes (sin OCR), con los votos del primer candidato de cada lista:

| Departamento | Provincialista / Conservador | UCR | Votantes | Fuente |
|---|---|---|---|---|
| Valle Grande (Jujuy) | 165 | 111 | — (319 inscriptos en Cantón) | *La Prensa*, 8/4/1916, p. 6, despacho de Jujuy del 7/4 |
| Independencia (La Rioja) | 203 | 64 | 266 | Expediente 9-D-1916, Cámara de Diputados, pp. PDF 65–67 (acta de la Junta Escrutadora Nacional, 3 mesas) |
| General Lamadrid (La Rioja) | 150 | 155 | 308 | Ídem, pp. PDF 163–165 («General La Madrid», 2 mesas) |

- **Valle Grande:** el despacho cierra con el acumulado que publica: Puch pasa de 3.425 a 4.162 y Claros llega a 3.106, con dos urnas de Humahuaca, Cochinoca (407 y 386, igual que Lupu) y Valle Grande.
- **Detalle por mesa:**
  - Independencia: de la Colina contra Baigorri, 75–24, 69–15 y 59–25.
  - Lamadrid: 90–112 y 60–43.
- **Inscriptos:** en las dos riojanas Cantón los tiene ilegibles. En La Rioja tampoco hay votantes impresos para estimarlos, así que la tarjeta no da participación.
- El expediente está en la Wayback Machine: `web.archive.org/web/20220502022911/https://apym.hcdn.gob.ar/uploads/expedientes/pdf/9-d-1916.pdf` (142 MB, 190 pp.). La HCDN ya no lo sirve.
- **Pendiente:** en La Rioja el cuadro departamental de Cantón queda lejos del total que la Junta proclamó y que cita Wikipedia. Aun con estos dos departamentos, faltan 900 votos radicales y 2.333 conservadores (UCR 4.561 y provincialistas 4.409, contra 5.461 y 6.742), así que el cuadro está incompleto en general, no solo en estos dos departamentos. El acta del expediente trae todas las mesas de la provincia y permitiría rehacer La Rioja entera.
