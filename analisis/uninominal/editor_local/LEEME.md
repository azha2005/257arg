# Distrito 257

Abrí `index.html` en un navegador moderno. Si usás el ZIP, extraelo completo
primero. El mapa, las cifras y el editor funcionan sin conexión y sin servidor.

1. Elegí una jurisdicción, una geografía y una elección. En radios, el punto
   de partida es el plan neutral de 257 que procura mantener juntos los
   circuitos. El modo con los polígonos de circuito arranca vacío.
2. Elegí un distrito de la lista y hacé clic o arrastrá con **Pintar**. Con
   **Circuito vinculado**, cada radio tocado lleva consigo todo su grupo. Para
   sacar del plan una unidad, elegí **Borrar**. La rueda controla el zoom y
   **Mover** permite desplazar el mapa o seleccionar el distrito bajo el cursor.
3. **Deshacer** y **Rehacer** operan por trazo completo. **Inicio del plan**
   lleva a la base o permite empezar en blanco. Ambos cambios se pueden deshacer.
4. El editor intenta guardar el trabajo en el navegador. Usá **Guardar plan**
   para descargar una copia en JSON y **Abrir plan** para recuperarla.

En **Color del mapa**, **Voto por unidad** colorea los radios o circuitos
según su propio resultado. **Lean del plan** usa ese voto como fondo para
las unidades sin asignar y el resultado acumulado para las asignadas.
El distrito cambia de color durante el trazo. Los tonos más fuertes indican
un margen mayor sobre la segunda fuerza, en puntos porcentuales.

El reparto fija un distrito uninominal por banca, dentro de cada provincia o
CABA. La estimación por radio que abre por defecto viene de los atlas del
proyecto. Cubre los 3.820 radios de CABA y los 23.901 de los 135 partidos
bonaerenses. El empalme conserva por código los valores de los 18.101
radios de los atlas AMBA y extiende el mismo método a 9.620 radios en
95 partidos.

- Para Diputados 2025, se usa la variante principal del atlas AMBA, de
  los votos por local de octubre de 2025 a los radios, por distancia
  inversa al cuadrado dentro del partido o comuna. Los locales sin punto
  válido conservan el punto de respaldo del atlas. Para el resto de la
  provincia se usan los puntos de octubre de `mapas/superficiePBA2025/locales_superficie.csv`
  y el cruce mesa a local de DINE, con los votos de todas las listas. Dos
  locales del archivo de superficie usan un punto de respaldo de partido.
- Para la general y el balotaje de 2023 se usan los archivos de la serie
  AMBA. En esas elecciones se parte de los votos por circuito y se usan
  locales y pesos de electores de 2025 como referencia retrospectiva.
  Si no hay un local usable, el reparto parte de un punto del circuito.
  El control detalla los circuitos con respaldo en los 95 partidos. Los votos
  se calculan con los valores fraccionarios de los atlas; solo se
  redondean al mostrar el recuento.
- Fuera de la cobertura geolocalizada, el modo electoral queda sin voto.
  Los distritos con cobertura parcial muestran sus votos disponibles
  en la ficha y quedan fuera del recuento de ganadores. Se puede elegir
  aparte **Reparto por circuito**, con cobertura nacional y el método
  de distribuir por población censal dentro de cada circuito.

En la geografía de circuitos, Diputados 2025 usa los positivos observados
donde existe cobertura. El resto de las elecciones está adaptado a los
límites de 2025. La población por radio es la del Censo 2022 en viviendas
particulares. La de circuito se estima escalando el padrón.

El recuento de fragmentos usa pares con borde compartido en la geometría base.
No incorpora conexiones de Mosaic entre islas. Las líneas del mapa se simplifican
para dibujar más rápido y detectar la unidad bajo el pincel. Las asignaciones y
las cuentas conservan todos los identificadores, población y votos fuente.

Para regenerar desde el paquete de QGIS, ejecutá `construir.py` con el Python
de Mosaic. El constructor escribe la carpeta `outputs/editor_uninominal` y su
ZIP. Con `--con-datos-existentes` vuelve a empaquetar la interfaz sin recalcular
la geometría, y actualiza las estimaciones desde
`mapas/mapaAMBA2025radios/asignacion_idw.pkl`,
`mapas/serieAMBA2005_2023radios/asignacion_2023pres.pkl` y
`mapas/serieAMBA2005_2023radios/asignacion_2023bal.pkl`.
El módulo `pba.py` añade los 95 partidos y comprueba la conservación de
votos por partido y lista. `control_pba.json` resume el resultado.

GitHub Pages publica la interfaz y descomprime `datos.zip` en la misma ruta.
Para actualizar ese archivo de publicación, generá el editor local y corré
`python -m zipfile -c <repo>/analisis/uninominal/editor_local/datos.zip datos`
desde `outputs/editor_uninominal`. Copiá también `control_pba.json` de esa
carpeta para actualizar el resumen publicado.
