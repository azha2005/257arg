# Cotejo de nuestros atlas con los mapas por departamento de Wikipedia (14-oct-2026)

## Qué hay en Wikipedia/Commons y qué se pudo comparar

Mapas **por departamento** (todos del usuario N2051, plantilla «Wikipedia 1999», 2491×2140):
1983 (V1), 1989 (V1), 1995, 1999, 2003, 2007, 2011, 2015 (1.ª y 2.ª vuelta), 2019 y 2023 (1.ª y 2.ª vuelta). Más viejos y de otro estilo (AndyCat2453 y otros): 1946, 1958, 1963 y 1973 (no los revisé en detalle; no tenemos atlas de esos años).
Los mapas de 1916, 1922, 1928, 1930, 1985, 1987, 1991 y la constituyente de 1994 de Commons (serie de 2000×4280) son **por provincia** (círculos de bancas o colegio electoral): no se pueden comparar por departamento con nuestros atlas.

| Nuestro atlas | Mapa de Wikipedia por departamento | Cotejo |
|---|---|---|
| 1983, 1989, 1995 | sí (V1 / 1995) | **sí, abajo** |
| 1985, 1987, 1991, 1993, 1994 | no (solo provincias) | no hay con qué |
| 1916, 1922, 1928, 1930 | no (solo provincias) | no hay con qué |
| AMBA 2025 | no | no hay con qué |
| (sin atlas) 1946, 1958, 1963, 1973 | sí | no tenemos atlas ni datos por departamento |
| (sin atlas) 1999, 2003 a 2023 | sí | se cotejó **nuestra base** (xlsx), no un atlas |

## Método
1. La geometría de esos mapas es la del SVG base del skill (538 unidades). Se renderizó ese SVG con un color único por unidad (`labels.png`, `labels_idx.npy`) y se comprobó que cae sobre los PNG de Wikipedia a ~1 px.
2. Por unidad se tomó el tono dominante del interior (erosionado) en el PNG de Wikipedia. Cada candidato usa un tono fijo (los tramos de porcentaje solo cambian saturación y brillo).
3. Nuestras unidades se emparejaron por nombre con las del SVG (491 de 526 en 1983 y 1989, 492 de 530 en 1995; el resto son circunscripciones de Capital y alias sin resolver).
4. Se repitió con otra vía independiente del nombre (polígonos del shapefile propio sobre el PNG): mismo resultado, 66 % contra 64 % en 1983.
5. La concordancia de 2003–2023 se midió contra el ganador por columna de `xlsx_resultados/por_eleccion/<año>_presidente.xlsx`; cada candidato se asigna a su tono modal en Wikipedia y se cuenta cuántas unidades quedan fuera (tolerancia ±4° de matiz).

Scripts: `register.py`, `wikicolors.py`, `cmp2.py`, `modern.py`, `panels.py`, `informe.py`.

## Resultados

### Atlas contra Wikipedia (ganador por unidad)

| Año | Unidades comparadas | Coinciden | Votos de las unidades que difieren |
|---|---|---|---|
| 1983 | 491 | 314 (**64,0 %**) | 35 % de los positivos (incluye partidos provinciales) |
| 1989 | 491 | 375 (**76,4 %**) | 20 % |
| 1995 | 492 | 472 (**95,9 %**) | 8 % |

Imágenes lado a lado (nuestro | Wikipedia | dónde difiere): `informe/panel_1983.png`, `panel_1989.png`, `panel_1995.png`. Listas de unidades: `informe/discrepancias_<año>.csv`.

### 1983 y 1989: las diferencias son grandes y no son de agrupación
- 1983: 147 unidades con UCR y PJ cambiados (77 que nosotros pintamos azul y Wikipedia rojo; 70 al revés). Más 16 donde ganan partidos provinciales que Wikipedia no tiene como color (MPN 11, Bloquista 3, MFP 2) y 14 de Pacto Autonomista-Liberal (nosotros pintamos 16 departamentos de PAL, casi todos en Corrientes; Wikipedia pinta 8 de turquesa y en 11 de los nuestros pone UCR).
- 1989: 88 unidades con MEN/ANG cambiadas (50 y 38), 20 de Alsogaray (14 donde Wikipedia pinta azul, 6 al revés; casi todas Corrientes: el bloque «Alianza de Centro» incluye el Pacto Autonomista-Liberal de Corrientes, como en la tabla de Wikipedia), 7 de MPN y la de Antofagasta de la Sierra.
- Provincias donde más difiere: 1983 Corrientes (16 de 25), Neuquén (14 de 16), San Juan (12 de 19), La Pampa, Salta; Córdoba, La Rioja y Tierra del Fuego coinciden entera. 1989: Corrientes 20 de 25, Córdoba 13 de 26, Salta, Neuquén; sin diferencias en Formosa, La Rioja, San Luis, Santiago del Estero y Tierra del Fuego.
- Las diferencias **no son márgenes ajustados**: en 1983 la mediana de |UCR−PJ| en las unidades que difieren es 11,6 pp (29 con más de 20 pp).
- **¿Quién tiene razón?** Prueba de consistencia con otra tabla de la misma base (diputados nacionales del mismo año, `base8399/ernesto/<año>_diputados`):
  - 1983: el ganador de diputados coincide con nuestro presidente en 98,1 % de las unidades y con el mapa de Wikipedia en 68,6 %. En las 130 unidades donde nuestro atlas y Wikipedia difieren, diputados da la razón a nuestro atlas en **126** y a Wikipedia en 4.
  - 1989: 89,9 % contra 79,4 %; en las 78 discrepancias, 61 a favor nuestro y 17 a favor de Wikipedia.
  - Además, nuestras sumas provinciales y nacionales cierran con la tabla de Wikipedia (ver `LEEME_1983.md` y `LEEME_1989.md`).
  - No es un simple desfasaje de nombres dentro de cada provincia (se probó con corrimientos y reversos: no hay permutación que lo explique).
- Cautela: la prueba con diputados no es independiente de la fuente (Lupu–Stokes y Ernesto salen de la base de Escolar), así que demuestra que **nuestros datos son coherentes entre sí**, no que sean los oficiales. Lo que sí queda claro es que el mapa de Wikipedia no reproduce ninguna de las dos tablas. La página del archivo dice «own work» y no cita fuente; no sabemos de dónde sale su dato por departamento.
- Las versiones de enero de 2025 de 1995, 1999, 2003 y 2019 tienen **la misma partición** que las de septiembre de 2026 («New color» solo cambió tonos). 2015 sí cambió (corrección de errores en las revisiones «Now right»).

### Contraste independiente: Mendoza con la transcripción de UNCuyo (14-oct-2026)
La capa 2 de `base8399` (`elecciones/<año>_presidente/detalle_partidos.csv`) es una transcripción de UNCuyo que **no pasó por la base de Escolar**. Se comparó el ganador por departamento de Mendoza.

| Año | Departamentos | Nuestro atlas = UNCuyo | Mapa de Wikipedia = UNCuyo |
|---|---|---|---|
| 1983 | 18 | **18** | 15 |
| 1989 | 18 | **17** | 11 |

- Los votos de UNCuyo coinciden con los de Ernesto casi cifra por cifra (por ejemplo Luján de Cuyo 1983: 16.390 UCR y 12.755 PJ en ambas), lo que confirma la base con una segunda fuente primaria.
- Los fallos de Wikipedia en Mendoza son claros: 1983 Guaymallén, Maipú y Tunuyán con UCR 55 a 62 % y pintados de PJ; 1989 Capital, Godoy Cruz, Junín, La Paz, Maipú, Rivadavia y San Carlos pintados de UCR donde UNCuyo y nuestro atlas dan Menem.
- **Un error nuestro: Malargüe 1989.** La base de Ernesto trae FREJUPO = 3.864 contra UCR 3.912 y por eso el atlas lo pinta de Angeloz; UNCuyo trae FREJUPO = **3.964** (100 votos más, probable error de tipeo). Con 3.964 gana Menem (y el mapa de Wikipedia lo pinta de Menem). Está sin corregir en `mapa1989/`; es un cambio de un voto en un solo departamento, y la regla del proyecto es dejarlo anotado en la ficha en vez de tocar la base en silencio.

### 1995: casi igual; las 20 diferencias son de agrupación
- 7 de Santa Fe (Rosario, Belgrano, Constitución, Iriondo, San Jerónimo, San Lorenzo, San Martín): la lista FREPASO supera al PJ **solo**, pero nuestro bloque Menem le suma UCeDé y Frente de los Jubilados (en Santa Fe, 744.384 contra 744.576 de la tabla de Wikipedia), y Menem gana. Wikipedia pinta por lista (magenta). Su propio mapa contradice su tabla provincial en esos departamentos.
- 4 de Corrientes (Concepción, General Alvear, San Roque, Sauce): desempates de menos de 3 pp entre el bloque justicialista y el de Bordón.
- Jujuy (3), Salta (Cerrillos), Córdoba (Ischilín, Tulumba) y Chubut (Paso de Indios): pluralidades parecidas, cuyo ganador depende de cómo se agrupan listas chicas.
- Dos que no son de agrupación: **General Guido** (Buenos Aires; UCR 44,2 % contra PJ 10,8 % en la base, Wikipedia pinta azul) y **Vicente López** (PJ 43,2 % contra FREPASO 40,6 %, también por lista, y Wikipedia pinta magenta). En esos dos el mapa de Wikipedia no sigue ni la lista ni el bloque.

### 1999 y 2003–2023: nuestra base contra los mapas actuales
No hay atlas nuestro de estas elecciones; se comparó el ganador por unidad de nuestro xlsx con el color de Wikipedia.

| Elección | Unidades | Concordancia | Con muestra pura (≥95 % de píxeles de un tono) |
|---|---|---|---|
| 1999 (datos de Ernesto, sin bloques) | 435 | 89,9 % | 91,7 % |
| 2003 | 467 | 95,9 % | 96,3 % |
| 2007 | 470 | 98,9 % | 99,8 % |
| 2011 | 489 | 99,8 % | 99,8 % |
| 2015 1.ª vuelta | 475 | 96,2 % | 98,5 % |
| 2015 2.ª vuelta | 485 | 97,3 % | 98,5 % |
| 2019 | 489 | 98,2 % | 99,2 % |
| 2023 1.ª vuelta | 490 | 97,3 % | 98,3 % |
| 2023 2.ª vuelta | 481 | 97,3 % | 98,7 % |

- Las diferencias se concentran en el Gran Buenos Aires (Berisso, Ensenada, Pilar, General Rodríguez, San Vicente, San Isidro: partidos pequeños junto a los marcos del recuadro, donde el muestreo es menos fiable) y en San Juan y Tucumán capital y alrededores (posible diferencia de límites o de alias de nombre; no lo verifiqué).
- San Isidro sale con un color raro en Wikipedia en 2015, 2019 y 2023 (nuestros datos dan Juntos por el Cambio con 43 a 58 %); ahí el error parece del mapa, aunque puede ser también un artefacto del muestreo en un polígono chico.
- 1999: el xlsx es el de Ernesto «sin corregir». En Corrientes el voto justicialista está repartido en cuatro listas (acjc00 a acjc03) y la columna ganadora individual no es el bloque; con las familias sumadas gana el PJ, mientras Wikipedia pinta Alianza. En el Conurbano (24 partidos de Buenos Aires discrepan: Lanús, Lomas, Quilmes, Avellaneda, Tres de Febrero, Tigre, San Martín y otros) el ganador de diputados de la misma base coincide con nuestro dato (38 de 44 discrepancias), no con Wikipedia.
- Los datos se cargan desde el xlsx tal cual; no se corrigió nada.

## Qué no se probó
- 1946, 1958, 1963, 1973: no tenemos atlas ni datos por departamento (Cantón 1946 está sin transcribir).
- Las versiones antiguas (2025, AndyCat2453) de 1983 y 1989 usan otra geometría y no se pudo registrarlas con la base (muestras poco uniformes): no se comparan.
- Los 30 a 35 territorios sin pareja de nombre por año (circunscripciones de Capital, Bartolomé Mitre, 1.º de Mayo y Presidente de la Plaza del Chaco, Islas Malvinas).

## Qué conviene hacer con esto
1. **1983 y 1989**: no tocar nuestros atlas; los datos cierran con las tablas de Wikipedia. Si se suben a Commons, hay que avisar que contradicen el mapa vigente y citar la base (ya figura en el subtítulo).
2. **1995**: decidir si el ganador es por lista (como el mapa de Wikipedia) o por bloque (como su tabla y nuestro atlas). Hoy usamos el bloque. Las 20 unidades están en `informe/discrepancias_1995.csv`.
3. **1999 en adelante**: antes de hacer atlas, agrupar en bloques (Corrientes 1999 por ejemplo) o el ganador por columna no sirve.
