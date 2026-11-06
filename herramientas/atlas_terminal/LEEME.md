# Atlas electorales en la terminal

Prototipo local inspirado en la idea de [VoteHub CLI](https://github.com/de-bayes/votehub-cli): mapa ANSI con medios bloques, fichas y navegación por teclado. Implementación propia; no incorpora código ni datos de ese repositorio (su `package.json` declara `UNLICENSED`).

Desde la raíz del proyecto, con Node.js 18 o posterior, sin instalar paquetes:

```powershell
.\abrir_atlas_terminal.cmd
.\abrir_atlas_terminal.cmd 2025
node herramientas/atlas_terminal/atlas.mjs --list
node herramientas/atlas_terminal/atlas.mjs 1983 --print
node herramientas/atlas_terminal/atlas.mjs 1918 --search Jujuy --print
node herramientas/atlas_terminal/atlas.mjs 2023bal --view closest --print
node herramientas/atlas_terminal/atlas.mjs 2023bal --search "La Matanza" --json
```

El iniciador funciona desde cualquier carpeta y abre una ventana de **PowerShell** con UTF-8. Sin pasar una clave, arranca en el selector: escribí un año o nombre, movete con las flechas y abrí con **un solo Enter**, o hacé clic en una fila. Por ejemplo, `2023 balotaje` filtra por ambas palabras. Las flechas siguen funcionando mientras se escribe. Los comandos directos de Node mantienen su salida redirigible y no abren ventanas adicionales.

Windows Terminal o una terminal con ANSI RGB y UTF-8 ofrece la mejor presentación; `--no-color` dibuja símbolos de ganador y su leyenda (las coropletas requieren color). La salida redirigida imprime una sola vez sin secuencias de control; `--color` permite guardarlas deliberadamente.

La vista inicial se pinta **por provincia**, con los resultados provinciales del HTML. Un clic en una provincia amplía su mapa y muestra sus departamentos, circunscripciones o radios; otro clic abre la ficha de una unidad. `Esc` vuelve de la ficha a la provincia, y de la provincia al país. El mapa usa el fondo de la terminal, sin rectángulo de color alrededor.

En la consola clásica de Windows se inicia un pequeño adaptador con el PowerShell incluido en Windows (`ConsoleMouse.cs`, compilado en memoria). Detecta clics únicamente sobre la ventana de consola activa y los traduce a celdas; no consume las teclas del visor ni cambia la configuración de la consola. Se cierra al salir del visor. Windows Terminal usa sus eventos SGR directamente.

La pantalla se actualiza por celdas modificadas y agrupa los eventos próximos: al recorrer una lista no se borra la pantalla ni se repinta el mapa. Se reserva un margen derecho y se desactiva temporalmente el salto automático de líneas para evitar desajustes en la consola.

El dibujo conserva las proporciones X/Y de las geometrías SVG. En la consola clásica de Windows se mide la relación alto/ancho de la celda real de la fuente, y se vuelve a medir si cambia. Esto evita estirar o achatar el mapa por suponer que medio carácter siempre es un cuadrado. Otras terminales usan una relación inicial de 2; se puede indicar la real con `--aspect 1.8`, por ejemplo (alto de celda dividido por ancho).

**AMBA y Capital:** `b` acerca directamente el recuadro metropolitano; `d`, Capital Federal. Esos rótulos también son botones en la barra inferior. Ambos muestran las unidades locales para poder seleccionarlas. `+` y `-` permiten acercar más. La búsqueda `/` abre fichas aunque la unidad sea demasiado pequeña para ocupar un píxel.

## Controles

| Tecla | Acción |
|---|---|
| `a` | Filtrar y elegir atlas; flechas y Enter o clic en una fila |
| `[` / `]` | Atlas anterior / siguiente |
| `m` | Siguiente modo del HTML |
| `b` / `d` | Acercar AMBA / Capital Federal, también con botones clicables |
| `n` | Volver al mapa provincial y al resultado nacional o regional |
| `p` | Lista provincial; Enter abre ficha y acerca su geometría |
| `c` | Unidades con menor diferencia entre las dos primeras filas partidarias |
| `/` | Buscar unidades por nombre o provincia, sin distinguir tildes |
| `Enter` | Abrir inmediatamente la fila elegida, incluso mientras se filtra |
| `↑` / `↓`, `j` / `k` | Recorrer listas o desplazar fichas |
| `RePág` / `AvPág` | Desplazar diez filas |
| Clic en mapa | Ampliar provincia; dentro de ella, abrir ficha local |
| `i` | Recorrer ventanas de recuadros del atlas |
| `+` / `-` | Acercar / alejar |
| `H` / `J` / `K` / `L` | Desplazar mapa a izquierda / abajo / arriba / derecha |
| `r` | Restablecer mapa por provincia |
| `f` | Fuentes y reservas del modo |
| `o` | Abrir el HTML local en el navegador habitual |
| `Esc` | De ficha local a provincia; de provincia a mapa general |
| `q` / `Ctrl+C` | Salir y restaurar la terminal |

## Datos y límites

- Lee `sitio/catalogo.py`, sus entradas existentes y las variantes estáticas de `EXTRA`. Los índices que no contienen un atlas se omiten. También se omiten las 18 retiradas de `mapa2003escenarios`: calculan sus datos al abrirse en el navegador y todavía no tienen lector de terminal. Los ocho remakes de `mapa2003alt` sí son compatibles. La inclusión aquí no publica archivos.
- Extrae el objeto JSON `DATA` y los polígonos `M/L/Z` con `data-i` de `#B` directamente del HTML generado. No ejecuta JavaScript del HTML, no vuelve a descargar fuentes y no recalcula ni modifica votos.
- El resultado nacional sale de `mode.national`, tal como lo muestra el atlas; los atlas AMBA conservan su agregado regional. Las fichas provinciales salen de `mode.prov`, sin reconstruirlas sumando polígonos.
- En el panorama inicial, cada provincia usa su ficha de `mode.prov`, tanto para el ganador como para las coropletas. Sus divisiones interiores no se dibujan. Al ampliarla, se muestran únicamente las geometrías locales de esa provincia, con sus propias cifras y reservas. Malvinas mantiene su relleno gris propio en ambos niveles.
- **GANÓ usa los colores base planos** para facilitar la lectura con pocos caracteres. Las coropletas conservan los `fill` explícitos del HTML. Los bordes se oscurecen y la selección se ilumina. Es una adaptación de terminal, no un render del póster con sus siete tonos, logos y tipografía.
- Mantiene los rellenos explícitos (pendiente, empate, exclusiones), las reservas por unidad y las provincias declaradas `solid`. Una provincia sólida no crea resultados departamentales: su ficha territorial sigue siendo la del HTML.
- `c` compara porcentajes de las dos primeras filas de partido/candidato, excluyendo categorías de blancos, nulos y otros. Usa únicamente unidades con ganador explícito, sin relleno de exclusión, ni provincias sólidas. La diferencia se calcula sobre los porcentajes ya redondeados del HTML. No constituye un pronóstico ni un cálculo de bancas; las agrupaciones de las fichas pueden ser más detalladas que las del mapa.
- Los escenarios y los radios censales siguen siendo hipótesis o estimaciones, según sus notas originales. El visor no convierte esos datos en resultados observados.
- La resolución de terminal puede omitir unidades diminutas. Buscar por nombre abre su ficha aunque no haya un píxel visible. El mapa inicial encuadra el principal; la Antártida conserva su ventana de recuadro, accesible con `i`. `i` permite acercar los recuadros originales; se muestra la ventana geográfica, sin trasladar o agrandar puntos. No se representan las bancas de minoría de 1951 como elecciones separadas.
- Admite la familia de atlas con `DATA.territories`, `DATA.modes[].units` y geometría poligonal `#B`. Una familia diferente muestra un error explícito al abrirla. No hay actualizaciones en vivo, tendencias entre geometrías de años diferentes ni cartograma de bancas.

## Verificación

```powershell
node --test herramientas/atlas_terminal/test_atlas.mjs
```

Las pruebas contrastan los votos con el JSON de los HTML, comprueban faltantes/exclusiones, provincias sólidas, agujeros de polígonos, selección, búsqueda, clics en listas, acceso al AMBA/Capital, actualizaciones parciales y salida sin ANSI. No se requiere conexión ni un servidor local.

Referencia de implementación revisada por pedido del usuario: clon local de VoteHub CLI en `scratch/refs/votehub-cli/`, especialmente `frame()` y `run()` en `bin/votehub.js`. Se tomaron como referencia el mapa de zonas clicables, el margen derecho, la desactivación del salto automático y el tratamiento separado de las teclas y los clics. El selector y el motor de diferencias de celdas de este visor son implementaciones propias.
