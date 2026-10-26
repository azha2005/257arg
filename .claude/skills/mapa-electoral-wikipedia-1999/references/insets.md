# Insets (ventanas de zoom)

Cada inset es un `<svg>` anidado con `viewBox` = una ventana del mismo mapa base, que contiene `<use href="#B">`. No hay geometría duplicada: cambiar los datos recolorea todos los insets a la vez.

## Cómo se controla qué se ve en cada uno
El CSS decide con propiedades personalizadas heredadas por el `<use>`: `display: var(--v-CLASE, none)`. Cada trazo del SVG tiene una clase:

| Clase | Qué es | Dónde se muestra |
|---|---|---|
| `d` | departamento/partido del mapa principal | mapa principal, Tucumán, San Juan, Mendoza, Resistencia |
| `dc` | las 28 circunscripciones de CABA (mapa principal) | mapa principal y recuadro de CABA |
| `pb` | borde provincial (relleno `none`) | mapa principal y zooms con `show:["pb"]` |
| `rcb` | partidos del recuadro AMBA (geometría ampliada) | recuadro AMBA |
| `cabab` | contorno único de CABA (en 1999 el AMBA la muestra como un solo polígono) | recuadro AMBA |
| `rcc` | circunscripciones de CABA del recuadro AMBA (no usado hoy) | — |
| `ant`, `antg`, `antf` | Antártida, islas Georgias/Sandwich, marco y cuña | recuadro de la Antártida |
| `mal` | Malvinas | `<use>` propio, desplazado |
| `out`, `out2` | contornos del país (no se muestran: las fronteras vienen de `frontiers.png`) | — |

`INSETS` en `template.html` define para cada uno: `f` (marco en el lienzo), `win` (ventana en coordenadas del SVG base), `show` (clases visibles), `sd`/`sp` (grosor de línea en px de pantalla; se divide por la escala del zoom), `fit` (`slice` por defecto, `meet`, o `none` para estirar a la caja).

## Elegir la ventana
1. Buscar la unidad central (p. ej. “Capital” de San Juan) en `assets/geom_rows.json` (cada fila: tag, id, etiqueta, provincia, grupo, caja `[x0,y0,x1,y1]` en coordenadas del SVG).
2. Estimar la escala viendo cuántos px ocupa esa unidad en `1999.png` ÷ su ancho en unidades.
3. `win = [x0, y0, ancho_marco/k, alto_marco/k]` con la unidad central en la misma posición relativa que en el PNG.
4. Comparar con `scripts/cmp.ps1 -Cmd pair` y retocar.

## Lo que no se puede igualar
`scripts/regsearch.js` (lanzado con `runreg1.sh`, uno por inset y en paralelo) busca la ventana minimizando la distancia entre líneas blancas. Funciona bien para AMBA, San Juan y CABA, pero para Tucumán, Gran Mendoza y Resistencia los costos quedan altos (>3 px): **el 1999 usa para esos tres otra geometría**, no la del mapa base. Ahí la ventana se elige a ojo y el resultado es parecido, no idéntico. Decirlo al usuario.

CABA: el recuadro usa las 28 circunscripciones del mapa principal estiradas con `fit:"none"` a la caja medida (191×232); sin ese estirado la proporción no coincide con la de 1999.
