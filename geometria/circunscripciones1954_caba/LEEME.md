# Capital Federal 1954: trazado de Primera Plana

**Actualización del 14-nov-2026.** El SHP vigente retraza los 14 recintos de [Primera Plana n.º 312, p. 58](https://ahira.com.ar/wp-content/uploads/2023/03/Primera-Plana_312.pdf#page=62), a partir del recorte nativo de AHIRA. Conserva la costa histórica original y los identificadores de trazado. El campo `circ_of` recoge la numeración impresa. Los límites interiores siguen siendo aproximados. Las secciones siguientes documentan el trazado anterior y el historial de la identificación.

**Auditoría y ajuste del 14-nov-2026 (pedido del usuario: igual a la imagen, rectilíneo, sin aplastar el 13, costa del SHP).** La PDF de AHIRA no tiene más resolución que el recorte (la página es una imagen de 1180 × 1600; el mapa ocupa unos 500 × 370 px). El trazado anterior ajustaba el dibujo al contorno con 16 rayos radiales y una placa delgada sobre puntos densificados: las líneas salían onduladas y corridas (IoU por recinto contra la revista 0,29-0,70; el 13 partido en un brazo). Ahora:

- **Rectas**: cada frontera entre dos nudos se simplifica una sola vez con Douglas-Peucker (1,6 px), que conserva los escalones y quiebres de la revista y quita los microquiebres del píxel. La deformación se aplica solo a los vértices, así que cada tramo recto sigue recto. La simplificación final en el póster bajó de 0,085 a 0,01 (antes borraba quiebres de unos 5 px).
- **Ajuste**: un afín con giro fino que maximiza la coincidencia del contorno (0,948) y una placa delgada exacta anclada en diez puntos del borde: General Paz y Riachuelo, los tres quiebres de General Paz, Núñez, Vuelta de Rocha, Pompeya (con coordenadas fijas), dos esquinas del borde inferior proyectadas a la costa y el punto medio entre Vuelta de Rocha y la muesca de la Dársena. Más puntos de borde (Riachuelo, río) pliegan el sur y parten el 13: se probaron y se descartaron.
- **Costa**: sin cambios, la nativa del SHP histórico. Donde la costa real no coincide con el borde dibujado, el hueco lo completa el recinto más cercano. Después, una apertura morfológica mínima (0,001 de póster) quita las espinas de ancho nulo que dejaba ese relleno (cortes dentro del 13, astilla sobre General Paz) y reparte lo quitado. Con 0,002 ya se pierde el contacto del pasillo del 9 con el 14, así que no se sube.

Controles (`superposicion_primera_plana.png`, SHP llevado de vuelta al marco del PNG invirtiendo exactamente la transformación): IoU medio por recinto 0,86 (1-9 entre 0,88 y 0,94; 10-12 entre 0,82 y 0,84; 14, 0,83; 13, 0,59 porque su lóbulo queda contra la costa real). La tinta del PNG a más de 3 px de nuestras líneas es el 6,5 %, casi toda números impresos y manchas. Proporción de superficie de cada recinto contra la imagen: entre 0,83 (12) y 1,11 (13). Se conservan las 27 vecindades. El visor `mapas/capital_canton/` se regeneró con este SHP.

Digitalización del esquema inferior, rotulado **1954**, de la imagen aportada
por el usuario. Se obtienen 14 recintos cerrados. No es un levantamiento de
límites legales ni una cartografía certificada.

## Costa y contorno

Por corrección del usuario, el marco final se toma **del SHP histórico de
Capital, con su detalle nativo**, conservado en la geometría del atlas 1948
(`mapas/mapa1948/units_raw.pkl`, generada por `geom4673`: Capital del SHP de
secciones de 1960). Se unen sus veinte secciones únicamente para obtener el
contorno exterior y la costa; no se usan sus límites internos para 1954.
No se aplica la simplificación de pantalla del SVG, ni se toma la silueta
esquemática de la imagen, ni se agregan rellenos costeros modernos. Esta
decisión sustituye el primer ajuste al contorno simplificado del SVG 1951.

La imagen aporta solamente la organización y los límites interiores. El flujo
deriva del de 1904/1951: vectorización, ajuste afín y RBF de perímetro, recorte
contra el contorno nativo del SHP y cierre exclusivamente geométrico de rendijas.
Los escalones del píxel se suavizan con una simplificación de cobertura de
2 píxeles que mantiene compartidas las fronteras entre polígonos. Se eliminan
los dientes de sierra y se conservan los giros mayores, sin redondearlos como
curvas decorativas. El desplazamiento máximo frente al trazado raster es
1,44 píxeles de la imagen útil y se conservan las 27 vecindades entre las
14 áreas. La costa no participa de esta simplificación.
**Se gira el dibujo 90° antihorarios antes del ajuste.** La orientación se
comprobó comparando el esquema de 1951 de la misma lámina con las geometrías
1951 de nuestro SVG, evaluando giros de 5° y emparejamientos de polígonos por
superficie compartida. El mejor giro fue 270° horarios de imagen (equivalente
a 90° antihorarios): coincidencia media de recintos 0,377 frente a 0,166 sin
giro; coincidencia del contorno 0,884 frente a 0,705 sin giro. La resolución,
el estilo esquemático y un recinto no separado en el raster de 1951 limitan
esas puntuaciones. Es evidencia de orientación, no una identificación legal
de las circunscripciones. Ver `comprobar_orientacion.py` y `ORIENTACION.json`.
La proyección de trabajo es la misma del proyecto, equirectangular con cos(38°)
y 44 píxeles por grado. Para el SHP se invierte esa transformación y se entregan
coordenadas WGS84 / EPSG:4326, listas para abrir en QGIS.

`CONTROL.json` conserva hashes, recorte, umbral, número de polígonos, controles,
validez topológica y comprobación de cobertura. La unión final coincide con el
contorno SHP de referencia; no tiene huecos ni solapamientos de área significativos.

## Identificación y límites de uso

- `id_trazo` 1–14 identifica los polígonos de esta digitalización, como se ve
  en la vista previa. **No es numeración oficial de circunscripciones.**
- `circ_of` queda vacío (`NULL`). La imagen no trae números y no permite
  establecer esa equivalencia de forma fiable.
- No se asignan partidos, ganadores ni votos. Para un atlas electoral falta
  una fuente numerada que permita unir cada polígono con su resultado de 1954.
- La fuente tiene aproximadamente 110 × 100 píxeles útiles para el esquema.
  El grosor de las líneas y la deformación del dibujo impiden precisión de
  calles o parcelas; el trazo interior debe tratarse como aproximado.
- Esto cubre Capital Federal, no todas las circunscripciones del país.

## Archivos

- `shp/caba_1954_trazado_aproximado.shp`, SHX, DBF, PRJ y CPG: 14 polígonos.
- GeoJSON equivalente en la misma carpeta.
- `caba_1954_aproximado.svg`: vector en las coordenadas de póster del proyecto;
  incluye el contorno costero del SHP sin simplificar.
- `vista_previa.png`: comparación con la imagen y correspondencia de `id_trazo`.
- `CABA_1954_SHP_aproximado.zip`: entrega para QGIS.
- `construir.py`: reconstrucción reproducible desde `fuente_aportada.png` y el SVG.

La imagen fue aportada por el usuario sin referencia bibliográfica ni licencia
identificadas. Se conserva su procedencia sin atribuir autoría propia al trazado
histórico; no se publica esta entrega en el sitio ni en Commons. Costa: base
histórica de departamentos/secciones de Rodríguez/CONICET, CC BY 2.5 Argentina,
ya usada por el proyecto. El SVG 1951 de Faustino Sojo se utiliza para el cotejo
de orientación; ver `mapas/mapa1951/LEEME_1951.md` para su atribución y licencias.

## Resultados de 1954 por circunscripción (6-nov-2026)

La Wikipedia («Elecciones legislativas de Argentina de 1954», `transcripciones/peronismo/wiki/w1954.txt`, líneas 1486 y siguientes) trae Capital por circunscripción, de la 1.ª a la 14.ª, con votos por partido, blancos, anulados y electos. Cita el AGN y el expediente 290-D-1955 de la HCDN. El Partido Peronista gana las 14. Sumadas dan 1.547.876 votos, contra 1.549.416 del CD de Cantón y Jorrat por secciones.

Lo que no trae es qué polígono corresponde a cada número. Probé emparejarlos por perfil, cruzando el CD por las 20 secciones con la superficie de cada recinto y comparando el % peronista, el % comunista y los votos. No alcanza: todos los recintos rondan el 51-57 % peronista y la diferencia entre la mejor opción y la segunda es mínima. Para unir `id_trazo` con `circ_of` sigue haciendo falta una fuente con los números, como el decreto de delimitación, el Boletín Oficial o la lámina original con números. El expediente 290-D-1955 podría traer la descripción de cada circunscripción.

## Lámina numerada: «Distritos capitalinos» (6-nov-2026)

El expediente 290-D-1955 es solo el diploma de Antonio Valerga. Repite la lista de electos y votos por circunscripción, sin límites.

La lámina con números aparece en «El voto uninominal por circunscripciones y su aplicación en la Argentina», *Lecciones y Ensayos* n.º 46 (Facultad de Derecho, UBA), p. 21 del PDF: «Distritos capitalinos, elección noviembre 1951 / elección abril 1954». Está en `lamina_uba/`, con el PDF y una comparación con el trazado.

- En el mapa de 1951 de la lámina los números coinciden con los oficiales del atlas 1951 (`mapas/mapa1951/shp`). Ajustando los rótulos a los centros de las circunscripciones, el error típico es de 0,5 a 1,3 km y cada número cae en la suya. La lámina es confiable y está en la misma orientación que la imagen digitalizada: la girada 90° antihorario queda con el norte arriba.
- En el mapa de 1954 el escaneo perdió el contorno y buena parte de las líneas del oeste y el sur. Se leen 3 a 8, 10 a 14 y dos o tres marcas dudosas; no se ven el 1, el 2 ni el 9.
- Probé alinear automáticamente las líneas punteadas de 1954 con el trazado, con escala, giro y desplazamiento, y no converge: la mejor solución queda en el borde del rango de escala. No se asignó `circ_of`.
- Lo que sí se ve: los números 10 a 13 son franjas apiladas en el sudeste, como los recintos 9, 11, 12 y 13 del trazado; el 14 está junto al río, al norte o noreste; el 4 y el 5 están al oeste, separados por una diagonal larga como la que separa los recintos 1 y 2. Son lecturas a ojo, no una correspondencia.

## Superposición para cotejo manual (6-nov-2026)

En `lamina_uba/overlay_1954_interactivo.html` hay un visor autónomo que superpone la tinta original de la lámina UBA (magenta) al trazado digitalizado (azul, IDs T1–T14). Usa los mismos recintos y el suavizado de cobertura del constructor, antes del giro y la adaptación al contorno geográfico. Un ajuste afín global por ocho referencias visuales inicializa la vista; las referencias son aproximadas, no equivalencias de números. Las proporciones difieren y no coinciden todas las fronteras. Se conservan los trazos y huecos del escaneo, sin reconstruir cifras.

El visor permite desplazar, girar, estirar, cambiar transparencia, alternar capas, anotar correspondencias propuestas y descargar PNG o notas JSON. `overlay_1954_uba_trazado.png` es la vista inicial para Paint; `crear_overlay.py` la reproduce y `overlay_ajuste_inicial.json` guarda los controles. Las notas del visor son propuestas, no se incorporan automáticamente. No se modificaron el SHP, `circ_of`, los votos ni los atlas.

## Correspondencia adoptada para el ensayo del visor Cantón (6-nov-2026)

El usuario eligió T7=1 y, por descarte, T4=2. `numeracion_adoptada.json` distingue esa decisión, las nueve lecturas del usuario y T6=6/T8=8/T9=9 inferidos por vecindad. Solo se aplican en `mapas/capital_canton/`, elección 1954, con votos publicados por circunscripción de Wikipedia (AGN/HCDN). El selector conserva las 20 secciones originales del CD. No se modifica el atlas nacional de 1954 ni se convierte el SHP original sin numeración en cartografía legal verificada. Ver el LEEME del visor y su `CONTROL_CAPITAL_1954.json`.
