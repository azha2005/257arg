# Trampas técnicas (cada una costó tiempo)

**SVG / CSS**
- Los selectores del CSS de los trazos deben ser planos (`.d{…}`), **nunca** `#atlas .d{…}`. Dentro del árbol sombra de un `<use>` el selector con ancestro no coincide: el trazo cae a los valores por defecto (relleno negro) y tapa todo. Síntoma: manchas negras con la silueta del país.
- `display:var(--v-clase,none)` + propiedades personalizadas puestas en el `<use>` es lo que permite un solo mapa y muchos insets. Para un `<use>` nuevo hay que declarar `--v-<clase>:inline` de las clases que se quieren ver.
- Ancho de línea en zooms: `stroke-width: calc(var(--sd) / var(--k))`, con `--k` = escala acumulada de los `transform` del trazo (el generador la calcula) y `--sd` = px de pantalla ÷ escala del zoom. Dividir, no multiplicar: con la CABA (grupo con `matrix(0.0127…)`) multiplicar daba líneas finas.
- `getBBox()` de un elemento con `display:none` devuelve 0: antes de medir geometría en el navegador, mostrar las clases.
- El SVG base de Wikipedia tiene bytes que no son UTF-8 en algunas etiquetas. Leer con `errors="replace"` y no usar esas etiquetas (los nombres vienen de `territories.json`).
- Los ids como `ZA`, `SF2`, `path4686-2` son copias del recuadro AMBA o partes de una misma unidad: la clasificación (`classify` en `build_atlas.py`) usa `geom_rows.json` y `territories.json`; no cambiarla sin comparar con el PNG.

**Herramientas en Windows (Git Bash + PowerShell)**
- `h` en PowerShell es alias de `Get-History`: no llamar `H` a una función de pixeles.
- `Add-Type` trata las advertencias como errores: sin variables sin usar.
- `python3 build.py | head -0` mata el proceso por SIGPIPE antes de escribir: no truncar la salida con `head -0`.
- La consola puede mostrar “�” en nombres con tildes aunque el archivo esté bien: comprobar con `[hex(ord(c)) …]`.
- `--allow-file-access-from-files` es necesario para leer un PNG local desde un canvas en una página `file://`.
- Edge headless ejecuta cada búsqueda en un solo hilo: para registrar varios insets lanzar un proceso por inset con `--user-data-dir` propio (6 en paralelo ≈ 2 min en un Ryzen de 8 núcleos).

**Zoom e interacción**
- El zoom es una `transform` sobre un grupo recortado por `#mapclip`: un `path` con `evenodd` que es el rectángulo del mapa **menos** los recuadros. Sin esos huecos el mapa ampliado se ve a través de los insets transparentes (Antártida, Tucumán, San Juan, Exterior). Si se mueve un recuadro, mover también su hueco (los huecos no pueden solaparse: con `evenodd` el solape se invierte).
- Las líneas no deben crecer con el zoom: `applyZoom` reescribe `--sd/--sp/--so` como px ÷ escala en `#mainwrap`.
- Los `<use>` no exponen sus hijos a los eventos (el objetivo es el `<use>`): solo el mapa principal es clicable; los recuadros reflejan la selección porque copian la clase `sel` del original.
- **Todo lo que se dibuja encima del mapa debe tener `pointer-events:none`** (`#frontiers`, `.pb`, `.out`, `.mal`…). Si no, la imagen de fronteras (que cubre toda la zona) captura el mouse y ni el hover ni el clic llegan a los departamentos. Pasó: las pruebas sintéticas daban "ok" porque enviaban el evento directo al `path`; en un navegador real no aparecía nada.
- **Probar la interacción con detección real**: `scripts/functest_hover_click.js` busca el elemento bajo un punto con `document.elementFromPoint` y envía el evento a ese elemento (lo que hace el navegador). Si `topAtPoint` no es un `path.d`, hay una capa interceptando.
- Las pruebas funcionales con Edge headless: inyectar un script que simule eventos y escriba un `<pre>` y leerlo con `--dump-dom`. Escribir ese script con la herramienta de archivos (no en un heredoc de shell: se corrompen las barras invertidas de los saltos de línea; usar `String.fromCharCode(10)` en vez de `'\n'`) y validarlo con `node --check` antes de correrlo.

**Verificación**
- Comparar siempre contra la referencia con `cmp.ps1 -Cmd pair` (lado a lado) y, para el mapa principal, `-Cmd shift` en bloques con muchas líneas internas y capturas sobre fondo negro (`#bare`).
- Las pestañas y el texto de la derecha son interactivos: comprobar con `window.__atlas.setMode(id)` y que no haya errores en consola.

**Datos**
- Pasar los nombres por `match_territories.py`: ignora tildes/mayúsculas pero no resuelve cambios de nombre reales (p. ej. departamentos creados o partidos nuevos de GBA).
- Las sumas de departamentos estimados suelen diferir en unos votos de los totales provinciales por redondeo; usar `resto_mayor` (ver `segunda_vuelta.py`) y no inventar ajustes.
- Las estimaciones y simulaciones se rotulan como tales (barra superior, subtítulo del set, README).
