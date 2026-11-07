# Capital Federal 1864-2007 (CD de Cantón y Jorrat)

Visor `capital_1864_2007.html`, con las elecciones de la ciudad por parroquia (1864-1898) y por circunscripción (1904-2007). Usa la página del sitio, estilo Ink del índice, con modo oscuro.

```
python datos/canton_ciudad/leer_cd.py              # CD -> cd_largo.csv, cd_elecciones.json, cd_control.json
"C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/capital_canton/geometria.py
python mapas/capital_canton/construir.py           # -> capital_1864_2007.html y control.json
```

## Datos

Las fuentes son las 106 planillas del CD de Darío Cantón y Jorge Raúl Jorrat, *Elecciones en la ciudad*, tomo III (2007), en `datos/canton_ciudad/cd/`. Se copian tal como están, sin corregir ni imputar. De las 106 entran **104**. Quedan afuera 1880 diputados (n.º 7) y 1889 senador (n.º 12), cuyas planillas no traen cifras.

- **Columnas.** `partidos.py` separa inscriptos (o electores o empadronados), votantes, blancos y nulos (con impugnados y recurridos) de los partidos. «Varios» y «otras listas» no pueden ganar una unidad.
- **Varones y mujeres (1951-1960 y 1973-2007).** El total es varones + mujeres. Las dos hojas nombran distinto a las mismas listas («U. C. R.» y «UCR», «JUSTICIALISTA» y «PJ»). Cuando tienen la misma cantidad de columnas se emparejan por posición y quedan los nombres de varones. En 1995 senador la hoja de mujeres no trae Demócrata Cristiano, así que ahí se empareja por nombre. Si a una unidad le falta una celda en una de las dos hojas, el total de esa celda queda sin dato.
- **1886 (diputados y presidente).** El CD trae tres versiones que no cierran entre sí: la de los Partidos Unidos, la del juarismo y la de la policía. Se usa la de la policía.
- **Porcentajes.** Se calculan sobre la suma de los votos a partidos. El total de la ciudad sale de la fila TOTAL de la planilla y, para cada sexo, de la suma de las unidades.
- **Advertencias del propio CD.** Hasta mediados del siglo XX el voto de un partido es el de su candidato más votado. Los blancos por circunscripción son claros recién desde 1951. En 1973, diputados y presidente de septiembre traen solo votos a listas, sin inscriptos.
- **Cierres.** `datos/canton_ciudad/cd_control.json` lista las columnas cuya suma por unidad no da la fila TOTAL. Son 42, en cinco elecciones: 1886, 1919 senador, 1960 mujeres, 1997 mujeres y 2003 presidente. La más grande es 1997 mujeres: la fila de Cristo Obrero (23) casi duplica la de varones. Se deja como viene y la página lo avisa en «Fuente y notas».

## Geometría

| Período | Unidades | Fuente |
|---|---|---|
| 1864–1869 | 12 parroquias | Calco municipal adaptado al límite de 1869. Agrupación de Barracas al Norte y reconstrucción de Balvanera anterior a San Cristóbal |
| 1872–1886 | 14 parroquias | Calco municipal, límite occidental del SHP de 1869 y Riachuelo de la lámina |
| 1890–1895 | 16 parroquias | Calco municipal, con el área de San Bernardo reintegrada según el cruce con las secciones de 1895 |
| Marzo de 1896 | 17 parroquias | Calco de la lámina municipal cotejado con Cantón y Jorrat, t. I, apéndices 2 y 4 |
| 1898 | 22 parroquias | Lámina municipal para Carmen, Vélez Sársfield y San Carlos. Decretos de 1896 para Las Heras y Balvanera Norte/Sur |
| 1904-1970 (salvo 1951 y la vista nueva de 1954) | 20 circunscripciones | `Departamentos_1914.shp`, idénticas en 1947 y 1960 (IoU 1,0) |
| 1951 | 28 circunscripciones de la ley 14.032 | `mapas/mapa1951/shp` (los ganadores del CD coinciden uno a uno). En diputados, los dos puntos de las bancas de minoría del atlas 1951 (`bancas_minoria_1951.shp`): UCR en la 7 y PP en la 28 (`minoria51` en `geometria.json`) |
| 1954, vista por defecto | 14 circunscripciones, numeración provisional | `geometria/circunscripciones1954_caba/`, `numeracion_adoptada.json`; votos Wikipedia (AGN/HCDN) |
| 1973-2007 | 28 circunscripciones | `mapas/mapa1983/caba28.pkl` |

El botón «Contorno censal» cambia al trazo recortado al contorno de la base de Rodríguez y De Grande (1869 hasta 1886, 1895 desde 1890): saca los meandros de la lámina que se salen del límite y reparte la franja costera entre las parroquias vecinas, sin tocar los límites interiores (`p<año>b` en `geometria.json`, `ajustar_a_base()` en `parroquias1896.py`; en la URL, `&t=base`). Los dos trazos se exportan como SHP en `geometria/parroquias_capital_1864_1898/` con `exportar_parroquias.py`.

Las cinco variantes usan caras contiguas y conservan la ribera histórica del Riachuelo. Las secciones policiales quedan como capa de referencia. Los límites anteriores a 1887, el reparto anterior a San Bernardo y los cortes de 1898 son reconstrucciones aproximadas. Las comprobaciones de `parroquias1896.py` exigen polígonos válidos, sin enclaves, huecos ni solapes cartográficamente relevantes.

### Diputados de 1896

- Se cruzaron los identificadores de celdas del apéndice 2 de *Elecciones en la ciudad*, t. I (pp. 455–459, PDF 443–447). Las 17 parroquias de la tabla coinciden con la planilla 21. `canton1895.json` conserva los porcentajes por sección, la población de cada parroquia y el total impreso. El total publicado excluye la sección 29 (diques y dársenas), población fluvial y Martín García. Cacopardo (1967, pp. 13–14) confirma el origen de las secciones 22–26 y la identificación de la 29.
- El apéndice 4 (pp. 466–471, PDF 454–459), el [plano topográfico municipal de 1895](https://commons.wikimedia.org/wiki/File:Plano_topografico_ciudad_buenos_aires_1895.jpg) y el [plano parroquial del anuario](https://revista.estadisticaciudad.gob.ar/ojs/index.php/poblacionba/article/download/146/196/687#page=3) aportan las referencias. El plano parroquial incluye divisiones posteriores a la elección, entre ellas San Carlos y Vélez Sársfield. Se adoptaron las unidades de la planilla y el cruce del apéndice 2. Las guías del casco siguen la orientación de las calles citadas, como Piedad, Cuyo, Potosí y México.
- `trazo_municipal1895.json` guarda ocho referencias de registro, San Bernardo y el Riachuelo. `limites_lamina1895.json` agrega el resto del perímetro y la red de límites, interpretada en el casco donde las líneas se confunden con los rótulos. Para representar marzo de 1896, el dibujo integra el Carmen con Belgrano y el sector dibujado como Vélez Sársfield y San Carlos con Flores. La franja portuaria se calca en beige. El original en la reproducción de *Población de Buenos Aires* (p. 83) es una imagen de 305 × 281 píxeles. El [catálogo de Estadística y Censos](https://www.estadisticaciudad.gob.ar/pergamo/documento.php?id=PERGAMO.1.6003&recno=6003&ui=1) registra el anuario, sin ofrecer allí la lámina en mayor resolución.
- `parroquias1896.py` forma las caras a partir de líneas compartidas y registra el calco en la proyección del visor. Comprueba la validez, continuidad, cobertura y ausencia de enclaves. `geometria.json` guarda en `control1896` las áreas de intersección medidas contra el SHP; los porcentajes de Cantón y Jorrat quedan como referencia. Por ejemplo, San Bernardo ocupa el 62,0 % de la sección 24 en el calco y el 64,6 % en la tabla. El botón «Secciones de 1895» superpone el SHP recortado al perímetro del calco.
- Los votos, votantes e inscriptos proceden de la planilla 21 del CD. La población del censo de 1895 por parroquia fue estimada por Cantón y Jorrat al redistribuir por superficie los datos censales por sección policial. Se conservan las cifras impresas. La suma de las 17 filas da 663.756 habitantes y 48.024 varones argentinos de más de 18 años, frente a 663.757 y 47.973 en la fila TOTAL. El panel de ciudad usa esta última. «Participación» es votantes sobre inscriptos. Los otros dos cocientes comparan votantes de 1896 con la población total y con los varones argentinos de más de 18 del censo anterior.

### Electorado potencial

`electorado.py` identifica la norma de cada comicio. Para diputados de 1864 y 1873 rige la Ley nacional 75 y para diputados de 1874, la Ley 623. La Ley nacional 893 de 1877 y sus modificatorias rigen los comicios nacionales de fines del XIX. La Ley 4161 y sus reformas restablecen el umbral nacional de 18 años. Las elecciones bonaerenses de 1869 y 1872 siguen la Constitución provincial de 1854, con umbral general de 21 años y excepciones. La Ley provincial 1067 rige las de 1879 y 1880. La Ley 13.010 reconoció el sufragio femenino en 1947 y el padrón de mujeres se usó desde 1951. Los comicios porteños de 1996 siguieron el Código Electoral Nacional por la Ley 24.620, y los locales desde 2000 incorporan las reglas para extranjeros de la Ley 334.

El denominador de 1890–1898 usa los 51.089 de Paula Alonso (censo de 1895). En marzo de 1896 el numerador de la planilla 21 es 21.317 y el cociente es 41,7 %. El registro de 24.200 estudiado por Alonso tiene otra cobertura parroquial. Por parroquia, el modo de 1896 muestra el cociente sobre los varones argentinos de más de 18 años publicados por Cantón y Jorrat.

Para las demás elecciones se interpolan las cifras entre censos de `censos_ciudad.csv`, con población nacida en Argentina y una fracción uniforme del grupo de edad en el umbral. En 1887 se usan edades simples del censo municipal. Para estimar la ciudad previa a la anexión se ajustan las bases de 1869 y 1887 por la proporción de habitantes del municipio antiguo (177.787 de 187.126 y 407.990 de 433.375). El cuadro de edades de 1970 se escala al total censal de 2.972.453. Los censos no permiten aplicar todas las exclusiones ni identificar a todos los naturalizados. El cociente puede superar 100 % cuando el padrón supera la base estimada de población censada.

Se omite el cociente con padrón incompleto, en las 11 circunscripciones de diputados de 1904, en las dos provinciales de 1869 y 1872 (faltan las excepciones al corte de 21 años) y en los comicios locales desde 2000 (falta cruzar la elegibilidad de los extranjeros con el censo). El visor indica el motivo.

### Diputados de 1904 en el visor porteño

Para el 13 de marzo, «Por candidato» usa el CSV nominal del atlas nacional y abre por defecto. «Por fuerza» muestra la planilla 24 de Cantón y Jorrat, que cita el expediente 1046 del Ministerio del Interior (AGN). Ambas vistas cubren las 11 circunscripciones en elección. Las otras nueve figuran en gris.

Cambian las primeras posiciones en las circunscripciones 2, 4 y 8. En la 4, San Juan Evangelista, la columna PAN de Cantón y Jorrat suma 949 y el PS figura con 830. La fuente nominal registra a Alfredo Palacios primero con 831 y a los dos candidatos del PAN con 572 y 357. La suma de votos publicados también difiere entre las dos fuentes, 19.977 por fuerza y 19.618 nominales. El visor presenta cada total con su fuente.

## Colores

Son los de los atlas nacionales de la misma época: UCR #e10019, PJ #318ce7, PS #ff9900, PDP #005c9e, UCRI #f4845f, PSD #ffad00, conservadores #1f2f6b, UCeDé #8e6bd8, FREPASO #a349a4, Alianza #dc0143, AR #3e5298, PRO #f4ce00, ARI/CC #74b744, FPV #50ade6, entre otros. Hay algunas decisiones propias:

| Partido | Color | Motivo |
|---|---|---|
| Socialista Argentino (Palacios) | naranja oscuro #e65100 | se separa del PS |
| Mitrismo y Partidos Unidos | #4169e1 | |
| Alsina y autonomismo hasta 1886 | #c0504d | rojo, para no confundirlo con Mitre |
| Fuerza Porteña / Ibarra 2003 | naranja #f8771e | el de la Wikipedia 2003, pedido del usuario |
| Compromiso para el Cambio / Macri 2003 | azul #3e5fa9 | el de la Wikipedia 2003, pedido del usuario (el amarillo del PRO queda desde 2005) |

Los demás llevan un color de respaldo: las facciones de 1864-1873, Coalición 1906 y Esperanza Porteña 2003. Ver `control.json`.

## Pendiente

- Cotejar los totales con la Wikipedia y con los atlas nacionales, para Capital en los años que se superponen. Ya hecho para 1936 y 1973: ver abajo.
- Las láminas del tomo II para verificar las 20 y 28 circunscripciones.
## Publicación (7-nov-2026)

Va al sitio como `capital/index.html` (`DESTINO` y `DATOS_APARTE` en `sitio/catalogo.py`, grupo «Ciudad de Buenos Aires, 1864 a 2007»; los datos van aparte en `capital/datos.js`). La plantilla trae título, descripción, canónica, Open Graph, tarjeta de X y JSON-LD, y el enlace «Todos los atlas». `portada.py` hace la og:image (`portada.png`) y las miniaturas del índice. Revisado con Hallmark (`sloplint --scope app`: 0 FAIL; renuncias a 22 y 38iii anotadas en el sello): sin puntos medios ni rayas en el texto (la raya del cuadro de 1874 pasa a «sin cifra»), flechas en SVG, colores en tokens, títulos del panel en minúscula. Tuits en `POST_TWITTER.md`.

## Uso en los atlas nacionales (6-nov-2026)

- **1936** (`mapas/mapa1936/`): Capital ya no va en color sólido. `load_1936()` de `transcripciones/entreguerras/datos.py` lee la planilla 50 y pinta las 20 circunscripciones (gana la UCR en todas).
- **1973 y 1973s**: `cd_capital()` de `transcripciones/peronismo/fuentes4673.py` reemplaza a Lupu y Stokes en Capital con las planillas 72 y 74. Así entra la circunscripción 21, que faltaba, y las listas menores pasan de estimadas a observadas.
- Los demás atlas con Capital por unidad (1904-1930, 1937, 1940, 1946-1965, 1983 en adelante) no se tocaron ni se cotejaron uno por uno contra el CD.

- **1954, prueba adoptada el 6-nov-2026**: el CD trae la planilla 62 por las 20 secciones de 1914, no por las 14 circunscripciones de 1954. No se trasladan esos votos por superficie. La vista inicial de 1954 usa la tabla por circunscripción de Wikipedia, que cita al AGN y el expediente HCDN 290-D-1955; las 14 filas cierran individualmente y suman 1.547.876 votos, contra 1.549.416 del CD. No se ajusta esa diferencia de 1.540 ni se infiere padrón. No hay desglose por sexo en la tabla de 14 circunscripciones.

  La numeración del trazado es provisional: nueve lecturas del usuario sobre la lámina de Derecho UBA, T6=6/T8=8/T9=9 por el supuesto de vecindad de los números consecutivos y T7=1 por decisión del usuario (por descarte, T4=2). Se conserva en `geometria/circunscripciones1954_caba/numeracion_adoptada.json`, con origen por recinto. No equivale a una delimitación legal verificada. Gana el PP en las 14.

  El selector «20 secciones del CD» conserva íntegros los datos originales y sus vistas Total/Varones/Mujeres; «14 circunscripciones de 1954» vuelve a la prueba. `capital1954.py` lee las cifras de `transcripciones/peronismo/wiki/w1954.txt`; `CONTROL_CAPITAL_1954.json` guarda filas, cierres y SHA256 de la fuente. Solo cambió la elección 62; las otras 103 elecciones y todas las geometrías anteriores se compararon y quedaron idénticas. Por corrección explícita del usuario, el atlas nacional `mapas/mapa1954/` conserva sus 20 secciones y datos anteriores. Sin publicación ni commit.
