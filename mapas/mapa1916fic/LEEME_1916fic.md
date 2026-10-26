# Presidenciales 1916, línea alternativa (ficticia): atlas por departamento

`python build_1916fic.py` regenera `atlas_1916_alt.html` (HTML autónomo, 2,4 MB) y `dataset_1916fic.json`. `python preview.py gan ucr pdp ps cc par` saca las vistas PNG.
Vistas: GANÓ, UCR, PDP | PS, CC, PART (dos juegos de pestañas).

## Fuentes
| Qué | De dónde |
|---|---|
| Resultado por provincia (votos, electores, blancos, inscriptos) | `lore_1916.docx` → `tabla.py` → `tabla_1916fic.json` |
| Forma geográfica de cada departamento | votos reales de diputados nacionales 1916 (Cantón 1968, t. II; Salta: exp. 58-D-1916), los mismos del atlas `../mapa1916dip` |
| Geometría | departamentos del censo de 1914 |
| Logos | los del cartel: PDP y PS de `../logos_wikipedia`; bandera circular de la UCR (repetida en la UCR Disidente) y escarapela P.A.N. redibujadas a partir del cartel (`logos/`) |
| Colores y estilo | los del atlas (Wikipedia); la UCR Disidente usa el color del cartel (#dd8a59) |

## Cómo se arma cada departamento
1. Se parte de los votos reales de Cantón del departamento: UCR (UCR + radicales situacionistas), socialistas, y la columna conservadora.
2. Cada columna se **reescala** hasta que la provincia dé *exactamente* la cifra de la tabla (restos mayores, enteros). La UCR baja o sube según la provincia; los votos que se le sacaron no pasan a nadie: quedan en los blancos (que se reparten según los votos del departamento) y en los que no votaron (los inscriptos de la tabla).
3. **Qué columna conservadora es De la Torre y cuál la Concentración Conservadora (ex-PAN):**
   - Corrientes: liberales de Cantón = De la Torre; autonomistas = ex-PAN (las sumas casi coinciden con la tabla).
   - San Luis: «Demócrata» = De la Torre; Unión Popular = ex-PAN (las sumas coinciden con la tabla a 30 votos).
   - Santa Fe: PDP = De la Torre; radicales disidentes = UCR Disidente; radicales situacionistas = UCR.
   - **Buenos Aires, Jujuy y Tucumán**: Cantón trae una sola lista conservadora. El reparto De la Torre / ex-PAN es **una estimación mía**: la parte de De la Torre sube con el tamaño del departamento (curva logística, pendiente `SPLIT_B = 1.2`, calibrada para que la provincia dé la tabla). Si se quiere otra geografía, se cambia `split_share()`.
   - Resto de las provincias: toda la columna conservadora = De la Torre.
4. Los socialistas de Capital salen de la columna PS de Cantón (no del PSA, que no es el PS); donde Cantón no trae PS pero la tabla sí (Entre Ríos, Córdoba, etc.) se reparte según el tamaño del departamento.
5. Inscriptos: los de Cantón reescalados al total de la tabla; donde eran ilegibles o menores que los votos reescalados (La Rioja, cuyo cuadro de Cantón está incompleto; San Juan, con el padrón de 1922), el departamento se fija en el mínimo con participación 92 % y el resto se reescala (`fit_reg()`).

## San Juan y Santiago del Estero
No hay cuadro departamental de 1916 en las fuentes (ver `sanjuan-sde-1916-busqueda` en la memoria). La forma geográfica sale de la presidencial más cercana de Cantón, con el mismo reescalado que el resto:
- **San Juan: presidencial 1922** (`../mapa1922/canton/p_SJ.txt`, t. II p. PDF 82). Radicales (UCR + bloquistas) → Yrigoyen; Concentración → De la Torre; socialistas → Justo. La Capital da un solo dato para Capital, Concepción, Desamparados y Chimbas (Cantón subsume Chimbas); Zonda no tiene polígono de 1914. De la Torre gana 16 de 20 polígonos.
- **Santiago del Estero: presidencial 1928** (`../mapa1928/canton/p_SGO.txt`, t. II p. PDF 121). Cantón **no trae 1922** para esa provincia y La Prensa de abril de 1922 tampoco da cómputo departamental. UCR → Yrigoyen; antipersonalistas → ex-PAN; socialistas → Justo. La tabla no le da votos a De la Torre en Santiago. La UCR gana 12 departamentos y el ex-PAN 14. 1930 (`../mapa1930/canton/p_SDE.txt`) es la alternativa, pero parte la UCR en tres listas.
- Cada tarjeta de estos departamentos lo aclara. Los inscriptos de San Juan son los «reconstruidos» de Cantón 1922.

Territorios nacionales y Los Andes: gris, no votaban. Unidades subsumidas por Cantón (Tres Arroyos, Berisso…): gris oscuro.

## La tabla del docx: tres erratas
- Fila **Total**: UCR 340.996, pero la suma de las provincias da **339.996** (y el texto del docx dice «339k»). Se usa 339.996: UCR 47,14 %, De la Torre 32,71 %, Justo 9,25 %, ex-PAN 6,99 %, UCR Disidente 3,90 %. El cartel dice 47,11 / 32,71 / 9,26 / 6,97 / 3,90.
- Fila **Total**: blancos 26.356, la suma da **26.256**.
- **Jujuy**: la participación está impresa «8..993»; los votos suman 8.996 (3.501 + 3.970 + 1.298 + 227). Se usa 8.996, así que el total nacional de votantes es 747.474, no 747.471.
- El «38,83» de la fila Total (columna UCR Santa Fe) no es un porcentaje coherente; se calcula de nuevo.

## Aproximaciones
Los departamentos son estimaciones sobre datos de diputados, no resultados presidenciales observados. Los logos de la UCR y del ex-PAN son redibujos, no los originales.

## Addendum: el Colegio Electoral
- **Póster (SVG, sale en los PNG y en la descarga SVG):** dos hemiciclos de 300 puntos (electores por lista y votación final), la votación final (De la Torre 159, Yrigoyen 127, Justo 14; 151 para la presidencia), una barra con la composición de los 159 (PDP 121 + ex-PAN 19 + UCR Disidente 19) y el texto que aclara que Yrigoyen ganó el voto popular y De la Torre fue electo por coalición. El primer lugar de la leyenda dice «MÁS VOTADO», no «GANÓ».
- **Página HTML (debajo del póster, oculta en `#bare`):** tabla por provincia con los electores de cada lista y su voto final. En la tarjeta de cada provincia hay una sección «Votación final del Colegio Electoral».
- Los electores y su votación final son los del docx/cartel; el ex-PAN y la UCR Disidente votan por De la Torre.
