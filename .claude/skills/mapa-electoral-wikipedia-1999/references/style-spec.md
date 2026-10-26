# Especificación del estilo (medida sobre `1999.png`, lienzo 1920×1649, fondo transparente)

Todo está en px del lienzo. Si hay que rehacer o ajustar algo, medir con `scripts/measure_png.ps1` y comparar con `scripts/cmp.ps1`.

## Color y tipografía
- Texto y marcos: gris `#616262` (marcos de insets `#616261`, 3 px). Familia DIN (Bahnschrift en Windows), negrita. Los rótulos sobre los insets: 24 px centrados, línea base = borde superior del marco − 9.
- **Paleta de 7 tonos por candidato** (se deduce del rojo `#dc0143` y el azul `#1c5ece` de la leyenda de 1999):
  - tono 0 (“30 %”): base mezclada 15 % con blanco → rojo `#e1275f`
  - tono 1 (“40 %”): la base → `#dc0143`
  - tonos 2…6 (“50 %”…“+90 %”): base × 0,85 / 0,70 / 0,55 / 0,40 / 0,25 → `#bb0139 #9a012f #780025 #59001a #360011`
  - el tono depende del % del ganador sobre válidos: <40, 40–50, 50–60, 60–70, 70–80, 80–90, ≥90.
- Tercer candidato de 1999: `#30519c`. Gris “otros” del pie `#717274`, “blanco/nulo” `#dfe0e5`.
- Líneas internas: blancas finas (≈1,5 px entre departamentos); provincias blancas más gruesas (≈3 px). Fronteras con países vecinos, ríos limítrofes y costas chilenas de Tierra del Fuego: gris `#616261` ≈3 px (arte fijo `assets/frontiers.png`, también trae “BOLIVIA, PARAGUAY, BRASIL, URUGUAY, CHILE” y los rectángulos que marcan el origen de los zooms).

## Composición
| Elemento | Posición |
|---|---|
| Título | texto en x=22, línea base y=78, 57 px; ancho 1088 para 41 caracteres (`textLength`) |
| Caja del año | x=1123 (justo tras el título), 114×62 en y=28; franjas `#74acdf` / blanco / `#74acdf` (22 px, 18 px, 22 px) con sombra suave; el año en negro, 57 px |
| Íconos de la derecha | 3 recuadros de ~50×62 en x=1262, 1320, 1378 (en 1999: retrato, urnas, helicóptero). Acá son las pestañas de modo |
| Pie | centro (184,374), radio 107; anillo blanco r=111; anillo de participación r=116, grosor 10 (`#484848` participación / `#dedede` resto). Rebanadas desde las 12, sentido horario, ganador primero |
| Textos del pie | “Proporción de votos por candidato” y “Anillo exterior: Participación”, itálica 17 px, y=210 y 231 |
| Mapa principal | `matrix(0.5425 0 0 0.5425 544.2 228.1)` sobre las coordenadas del SVG base (calibrado con ajuste local de ±1 px) |
| Insets (marco x,y,w,h) | Tucumán 450,300,200,185 · Gran San Juan 328,545,321,159 · Gran Mendoza 328,783,224,187 · Resistencia + Corrientes capital 1413,499,464,209 · AMBA 1247,785,647,320 · Antártida 1247,1166,330,452 · CABA (sin marco) 1632,1187,191,232 |
| Mini “Provincias” | `matrix(0.1448 0 0 0.1448 55.7 599.8)`; rótulo en (182,563) |
| Exterior | globo en (1054,1263) r=41 con aro negro; rótulo “Exterior” 38 px en y=1349 |
| Malvinas | gris `#a9a9a9` con trazo oscuro, `matrix(0.5425 0 0 0.5425 520.4 230)` (en 1999 está desplazada ~22 px respecto del mapa principal) |
| Leyenda | “Resultados” 20 px en (93,1266); rampa de 7 tonos a y=1292 (altura 9; 43,5 de ancho cada 46,2) con rótulos itálicos 14 px 6 px arriba; barra de 50 px a +15; franja lateral clara en x=80 (5 px); barra x=93 (431 de ancho la ganadora con bloque oscuro 429–524 para el %, 337 las demás); nombre 21 px y subtítulo 15 px alineados a la derecha en x=424; % de la ganadora 26 px blanco centrado en x=477, “GANÓ” 10 px itálica; % de las demás 23 px del color del candidato |

## Qué se dibuja y qué es arte fijo
- Dinámico (depende del dataset): colores del mapa, insets, mini de provincias, pie, anillo, leyenda, título y año, pestañas.
- Fijo: geometría (`base_1999_departamentos.svg`), `frontiers.png`, marcos y rótulos de insets, globo y Malvinas.
- Los recuadros de la Antártida y de CABA se alimentan de los colores de “Tierra del Fuego” y “Capital Federal” de `prov`, no de las `units`.
