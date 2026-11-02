# Publicación de los atlas

`python sitio/armar.py copiar _site` prepara la copia de GitHub Pages.
Los HTML de `mapas/` siguen siendo autocontenidos; las adaptaciones del sitio
y las mejoras de interacción se aplican durante esta copia.

## Interacción (2 de noviembre de 2026)

`rendimiento.py` inserta `interaccion.js` dentro del cierre de cada atlas:

- La ficha flotante cambia su contenido solo cuando cambia la unidad o el modo.
  Su posición se actualiza una vez por fotograma, mediante una transformación.
  En celular no se genera la ficha de hover oculta.
- El arrastre y el zoom agrupan sus escrituras en un fotograma. El arrastre no
  cambia las variables de grosor heredadas por miles de radios. El zoom conserva
  el grosor original y las descargas esperan el último ajuste pendiente.
- La selección busca los trazos por índice y actualiza solo los resaltados que
  cambiaron. Los formatos numéricos se reutilizan y no se reescriben colores o
  bordes que ya tienen el valor correspondiente.
- El texto del SVG no se selecciona al arrastrar. Se limpian los gestos al
  cancelar un puntero, perder el foco o empezar un pellizco con dos dedos.
- Los polígonos del AMBA que salen del rectángulo del mapa nacional también
  responden al arrastre y a la rueda del mouse.

`window.__atlas.zoom` expone la escala actual aunque su dibujo esté pendiente,
para conservar todos los movimientos de un pellizco entre dos fotogramas.

Verificación reproducible:

```
python sitio/verificar_rendimiento.py
python sitio/armar.py copiar _site
python sitio/verificar_rendimiento.py --navegador _site
```

La primera comprobación requiere Node para compilar los scripts de los 105
atlas y compara sus datos y su SVG con los originales. La segunda requiere
Playwright y Chrome. Prueba las familias de atlas (históricos, muchas fuerzas,
PASO, escenarios, niveles de AMBA), todos sus modos, la selección, cancelación,
las tres descargas y las cuatro vistas de celular, incluido el pellizco.

En las ráfagas sintéticas de regresión, 120 movimientos pasan de reconstruir
120 fichas a reconstruir una (dos mutaciones si se pliegan fuerzas pequeñas).
Un arrastre de 60 movimientos escribe una transformación y no modifica los
grosores. Estas cifras describen trabajo evitado, no garantizan una tasa de
fotogramas en dispositivos físicos. La geometría detallada sigue teniendo un
costo de dibujo, especialmente en los mapas por radio.

## Segunda revisión para celular

Los recuadros instancian su geometría solo en las vistas Recuadros/Póster o
al exportar. Al volver a Mapa/Resultados se libera esa referencia; las descargas
incluyen los recuadros completos. El buscador ofrece hasta 60 coincidencias
cuando se usa, sin crear miles de opciones al iniciar; busca en toda la base.

Durante un gesto se difiere el ajuste de grosores hasta 160 ms de reposo y,
en mapas con más de 5.000 trazos en celular, se ocultan temporalmente los
bordes finos. Al soltar se recupera el detalle; la exportación lo recupera
sincrónicamente. Las coordenadas del gesto reutilizan la matriz inicial.

La ficha mantiene su contenido y estilo: su altura máxima baja del 52 % al
32 % de la ventana (o el 42 % del espacio disponible bajo la barra, si es
menor), con desplazamiento interno. Un movimiento del dedo superior a 8 px
no selecciona accidentalmente; al arrastrar se cierra la ficha. El botón de
cierre mantiene su aspecto con un área táctil de al menos 44 × 44 px.

Validación adicional: búsqueda de la última unidad de la base, carga y descarga
de los recuadros al cambiar de vista, exportación completa desde celular,
distinción toque/desplazamiento y límite de altura de la ficha. La emulación
de CPU lenta permite comparar versiones, pero no sustituye una prueba en
teléfonos físicos.
