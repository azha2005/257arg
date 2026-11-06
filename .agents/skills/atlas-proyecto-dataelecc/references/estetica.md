# Estética: correcciones que el usuario ya hizo

Cada punto salió de una corrección concreta. Antes de entregar, revisar el atlas contra esta lista.

## Logos

- Fuente, en orden: el logo que ya usa otro atlas del mismo año o partido (por radio, publicado), el infobox y sus revisiones viejas, los mapas presidenciales de Commons, el artículo del partido. Mirar la fecha de Commons (`extmetadata.DateTimeOriginal`): si es posterior a la elección, sigla. Anotar todo en `logos/LICENCIAS.md`.
- **Solo código para tocar un logo** (quitar fondo, pasar texto a blanco, recortar margen). Nada de generación de imágenes.
- Posición: 1904-1983 centrado con zoom, como el original. Desde 1985, al ras: arranca en el borde izquierdo de la barra, ocupa todo su alto, sin margen entre logo y barra (no recortado como en un marco). Excepciones en `comun/logos_ras_excepciones.json` (todo lo subido a Commons conserva la posición subida, aunque el logo actual sea mejor).
- Revisar que no se corte a la derecha (pasó con UxP, AR, PL Corrientes, JxC): medir el ancho real del recorte.
- Si el logo no se lee sobre la barra, no se cambia el color de la barra: se pasa el logo a blanco (`LOGO_ESTILO` en `comun/leyenda_clara.js`). Ejemplo: texto blanco de Unidad Ciudadana.
- La PASO hereda los logos de la general del año, también para quien no ganó en la general (1País).

## Colores y escalas

- Antes de elegir color, grepear el partido en los builds: tiene que verse igual en todos los años. Colores fijos y excepciones en `AGENTS.md` (UCR #e10019, PJ #318ce7, LLA #6c4c98, PU 2025 #FF682C, peronismo federal #1aff98…).
- Colores bien distintos en la leyenda. Si dos se confunden (Menem y FPV en sus tonos oscuros en el AMBA 2003, Frente Nuevo y FPCyS en 2005), cambiar uno de familia.
- Siete tonos por candidatura, con pasos de luminosidad visibles. Ni demasiado claros (rechazado en 2003alt y FR 2013) ni casi negros (1928 usa `shade_k` más claro). Si el original tiene paleta, derivar la rampa de sus rellenos (`analisis/remake2003/extraer_paletas.py`).
- «Ganó» con cortes cada cinco puntos; coropletas en deciles o tramos parejos; amarillos (PRO/JxC) se oscurecen hacia el ámbar, no al oliva.

## Leyenda, título y pestañas

- Tamaño de barra según las filas (`LEG_SZ`); con muchas fuerzas, las menores al 2 % se pliegan en la ficha.
- Más de cuatro pestañas: comprimir el título hasta la primera pestaña. Botones medidos por su texto, sin amontonarse (`analisis/remake2003/botones.py`).
- Encabezados: «Elecciones presidenciales de Argentina de <año>» o «Elecciones legislativas de Argentina de <año>», subtítulo «<fuente> · deptos. de <año>» o «Diputados nacionales». Subtítulo de 34 caracteres como máximo.
- Subtítulos de partido cortos (`Corrientes`, `y aliados`) para no pisar logos.

## Mapa

- Sin huecos, puntos grises ni bordes dentados: `outline_clean.clean_outline` y `clean_holes`; geometría suave pero fiel a la costa del SHP.
- Malvinas en gris también en el mini de provincias; Capital ampliada en el globo del mini.
- Capital con buena definición (trazo nativo, no el SVG simplificado).

## Sitio y celular

- La capa del sitio la agrega `sitio/armar.py copiar`: «Todos los atlas», «Fuentes y notas» plegable, modo claro u oscuro según el índice, «Ocultar recuadros», modo celular (Mapa, Resultados, Recuadros, Póster). **No meter eso en los HTML de `mapas/`.**
- La ficha no repite la nota general del modo y no debe tapar todo en celular.
- Miniaturas clara y oscura (`python sitio/armar.py miniaturas <filtro>`), regenerar el índice. Que el zoom inicial deje ver los porcentajes.
- Después de cambiar algo del sitio: `python sitio/verificar_rendimiento.py` y, sobre la copia, `--navegador _site`.
