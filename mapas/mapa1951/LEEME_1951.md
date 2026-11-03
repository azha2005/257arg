# Diputados y delegados de 1951 por circunscripción

`python mapas/mapa1951/build_1951.py` genera el HTML, dataset, CSV y las capas GIS.
`python datos/circunscripciones1951_1954/preparar1951.py` vuelve a leer las tablas
de Wikipedia preservadas. No descarga ni cambia una fuente al reconstruir.

## Fuentes y alcance

- [Resultados de Wikipedia](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1951):
  snapshot HTML en `datos/circunscripciones1951_1954/wiki1951.html` y transcripción
  estructurada `resultados1951.json`, con partido original, candidatura, votos y
  métricas. El guion seguido de `0.00 %` en una candidatura se interpreta como
  cero y se conserva el literal; los signos negativos de las diferencias se conservan.
- [SVG de circunscripciones](https://commons.wikimedia.org/wiki/File:Mapa_de_las_elecciones_legislativas_de_Argentina_de_1951_por_circunscripci%C3%B3n.svg):
  Faustino Sojo, CC BY-SA 4.0; original y metadatos de Commons en la misma carpeta.
  Agradecimiento en las fuentes del HTML.
- El PDF aportado por el usuario, `186.-Confirmacion-electoral-de-la-voluntad-justicialista-del-pueblo-argentino.pdf`,
  está en Descargas. **Corresponde a las elecciones del 11 de noviembre de 1951**,
  como dice el índice (página PDF 5). No es cartografía de 1954. Las páginas 20 y 28
  contienen Capital y Buenos Aires; 39, 41, 47, 50, 52, 54, 56, 59, 62, 64, 66, 72 y
  75 las restantes provincias; 84–85 los territorios con delegados. Se inspeccionaron
  las láminas de Capital, Buenos Aires y territorios. No se afirma un cotejo visual
  completo de cada voto del artículo con las 87 páginas del PDF.

150 unidades con resultados: 139 circunscripciones de diputados y 11 de delegados.
Chaco y La Pampa quedan grises porque no eligieron diputados nacionales en esa fecha.
No se agregan aquí los comicios provinciales, constituyentes o parciales posteriores
que el artículo también describe. Se conserva la Gobernación Militar de Comodoro
Rivadavia como distrito distinto de Chubut y Santa Cruz.

## Puntitos de minoría

Los diez puntos rotulados `Minoría` en el SVG son **bancas adicionales**, no otras
elecciones. Están en Buenos Aires 11/17, Capital 7/28, Córdoba 2/12, Entre Ríos 1/4
y Santa Fe 4/7. Ocho corresponden a UCR y dos a PP (Capital 28 y Córdoba 12).
Se muestran en el partido de la candidatura no ganadora, con borde negro. Cada
punto selecciona la misma circunscripción; su ficha identifica candidato, partido
y votos de la banca adicional. Se colocan dentro de la circunscripción adaptada,
como símbolos de representación, sin reclamar ubicación geográfica precisa.

No crean unidades nuevas ni duplican votos en torta, agregados o CSV. Los archivos
`bancas_minoria_1951.json` y la capa de puntos GIS permiten examinarlos por separado.
Control: ganadores geográficos, PP 144 / UCR 6; sumando las bancas adicionales,
PP 146 / UCR 14 (incluidos los 11 delegados). El resultado nacional de Wikipedia
conserva las bancas como magnitud distinta de las circunscripciones ganadas.

## Votos y cierres

Corrección visual del 2-nov-2026: CABA se muestra también en el mapa principal.
Los puntos crecen suavemente al acercar, con un máximo para no tapar el mapa;
los metropolitanos usan radio de 1 píxel de póster en el principal hasta un
máximo de 3,2 con zoom, y 1,4 en recuadros, con borde fino incluso
al seleccionar. Las métricas de fichas/hover se distribuyen en tres columnas y
varias filas; la banca adicional se explica en la nota, evitando una columna
larga que desborde. El validador comprueba zoom 8×/20× y ambos tipos de ficha
sobre la copia con el formato del sitio.

Torta y barras: tabla nacional de Wikipedia, registrada en `comun/wikitop.py`,
sin ajustarla a la suma de datos locales. PP incluye PP Femenino; UCR incluye
Unionistas. Las fichas mantienen partidos y candidaturas originales. Ganó usa
la candidatura individual más votada. Escala habitual de siete tonos para Ganó;
coropletas PP/UCR por deciles; participación según votantes e inscriptos publicados.

Discrepancias conservadas y visibles en fuentes/fichas:

- Santa Fe 4.ª: partidos suman 79.140, positivos publicados 79.160.
- Positivos locales publicados suman 7.206.893, 20 más que el nacional (7.206.873).
  La suma de candidaturas sí da 7.206.873.
- PS local 74.370 frente a 73.927 nacionales; PC local 70.681 frente a 71.124.
  Diferencia de 443 en sentidos opuestos, sin trasladarla de un partido al otro.
- PP, UCR y los restantes partidos coinciden exactamente con sus agregados nacionales.
- Se conservan las diferencias de votos declaradas por el artículo, incluso negativas;
  no se interpretan como votos a una candidatura.

## SVG → SHP y proyección

`geometria_1951.py` deriva directamente de `mapas/mapa1904/geometria_1904.py`:
poligoniza los trazos, elimina copias ampliadas y símbolos de minoría del área
geográfica, ajusta el marco provincial con afín + RBF de perímetro y recorta al
contorno histórico. Cierra exclusivamente rendijas geométricas. **No convierte
las circunscripciones en departamentos ni reparte sus votos.**

El SHP aporta los contornos de la base 1947, con Buenos Aires 1955 ya usada en el
proyecto (`mapa1948/units_raw.pkl`, regenerable mediante `geom4673`). Los departamentos
de la Gobernación Militar que conserva la base 1947 se reúnen como marco de ese
distrito; no se suman resultados departamentales. Los contornos se proyectan con
la fórmula habitual de 1904/1912: equirectangular, cos(38°), 44 píxeles por grado.
Malvinas reutiliza exactamente el trazo del atlas 1904/1912, gris, sin votos.

Capital conserva las 28 circunscripciones de 1951 del SVG. **No** se sustituyen
por las veinte divisiones del SHP ni por las 28 de 1973. Para Buenos Aires se
añaden controles en el entrante porteño, necesarios para conservar Vicente López
al ajustar el litoral. Precisión geométrica de overlay de 0,00001 píxeles evita
errores topológicos; no representa precisión legal de los límites.

Es cartografía adaptada **aproximada**, no una delimitación legal certificada.
`CONTROL_GEOMETRIA.json` registra el ajuste y la cobertura antes de simplificar.
Los recuadros usan las mismas geometrías que el mapa. Los logos mantienen el dibujo
centrado del atlas 1954, sin modificar los archivos ni los logos de ese atlas.

## QGIS y licencias

En `shp/`:

- `circunscripciones_1951.shp` (+ SHX, DBF, PRJ y CPG), 152 polígonos; equivalentes
  en GeoJSON. Incluye 150 circunscripciones/distritos con votos y dos provincias sin elección.
- `bancas_minoria_1951.shp`, 10 símbolos de bancas. Sus votos ya forman parte de los
  polígonos: no sumarlos otra vez.
- `malvinas_referencia.shp`, marco de referencia, sin datos electorales.

Las capas se entregan en WGS84 / EPSG:4326, invirtiendo la proyección del póster.
La adaptación del SVG conserva CC BY-SA 4.0; contornos SHP de Rodríguez/CONICET,
CC BY 2.5 Argentina. Datos de Wikipedia, CC BY-SA 4.0, con la fuente impresa citada.
No se creó paquete ni publicación en Wikimedia Commons.

## Formato del sitio, igual que 1904

El HTML fuente permanece autocontenido. La versión que debe abrirse para ver
el formato de GitHub Pages se prepara con el mismo `sitio/armar.py` que 1904:

```
python sitio/armar.py copiar outputs/sitio_local
```

Abrir `outputs/sitio_local/mapas/mapa1951/atlas_1951.html`: incluye **Fuentes y
notas** cerrado por defecto, el enlace **Todos los atlas**, el botón para
ocultar recuadros, el tema del índice y las cuatro vistas de celular. El índice
y los demás atlas se copian también para que la navegación funcione. GitHub
Pages aplica esta misma preparación al publicar. `verificar_1951.py` comprueba
el toggle de fuentes y los controles del sitio, además de los datos.

## 1954

Se preserva el atlas departamental existente en `mapas/mapa1954/`. La tabla de
1954 está archivada por separado, pero los límites cambiaron (Capital tiene 14
circunscripciones en esa renovación). No se presenta el SVG o el PDF de 1951 como
si fueran una delimitación de 1954. Hay una digitalización aproximada de Capital
en `geometria/circunscripciones1954_caba/`, todavía sin numeración oficial ni votos;
no reemplaza los límites de 1954 del resto del país que siguen pendientes.
