# Buenos Aires: legisladores provinciales 7-sep-2025 → diputados nacionales 26-oct-2025

Inferencia ecológica RxC por circuito (método de E. Calvo, `estimar.py`), solo provincia de Buenos Aires. Sankeys: `sankey_2025s_2025.html` (completo), `_votantes` (sin No votó) y `_reducido` (No votó a escala 1:4).

## Fuentes
- **Septiembre**: escrutinio provisorio por mesa de la Junta Electoral bonaerense, base de Graficar PBA (G. Mastrangelo, pedida por formulario; no se redistribuye). Senadores provinciales en las secciones 1.ª, 4.ª, 5.ª y 7.ª, diputados provinciales en 2.ª, 3.ª, 6.ª y 8.ª: cada mesa vota uno de los dos, así que se usan como un solo cargo legislativo. Agregado con `datos/provinciales/pba2025/agregar.py` → `circ_2025s.pkl`.
- **Octubre**: `circ_2025.pkl` (DINE, provisorio por mesa, diputados nacionales).

## Códigos de la base de septiembre
Deducidos de los datos y verificados contra la DINE (el post de Graficar PBA no los documenta):
- `mesa_key` = `02` + partido (3 dígitos, numeración de la DINE) + mesa (5) + `X` (argentinos) o `E` (extranjeros).
- `circuito_codigo` = `02` + partido (3) + circuito (5, con letra si está subdividido: `0655A`). `seccion_*` es el partido; `municipio_*`, la localidad.
- `code` = número de lista; `census` = electores de la mesa; `totalVotos` = votantes (afirmativos + blancos + recurridos + impugnados + comando).
- `nulos` vale 0 en toda la base y `electores`/`sobres` no son fiables (`electores` = 0 en 7.694 mesas): no se usan.
- Totales: Fuerza Patria 47,28 % y LLA 33,71 % de los afirmativos, iguales al provisorio publicado.

## Decisiones
- **Se excluyen las 2.401 mesas de extranjeros** (`E`): votan en la provincial pero no en la nacional. También las 425 mesas sin votos.
- Categorías de septiembre: Fuerza Patria, La Libertad Avanza (con el PRO), Somos Buenos Aires, FIT-U; el resto en Otros. Octubre: las de 2025 (Provincias Unidas es la continuidad nacional de Somos).
- Emparejamiento por (partido, circuito): 1.043 circuitos comunes, 1.038 usados tras el filtro de padrón (99,99 % del padrón; mediana octubre/septiembre 0,999).
- Con una sola provincia, la matriz provincial y la nacional coinciden; la validación cruzada es casi plana (1,667–1,673 pp) y queda la penalización más fuerte (2e-4).
- Sin nulos en la base de septiembre, quien votó nulo cae en **No votó** de septiembre (padrón − votantes). Afecta poco, pero esa fila mezcla abstención y nulos.

## Resultados (% de la fila; principal / Calvo)
- Fuerza Patria → Fuerza Patria 75 / 79; → LLA 5; → Otros 7; → No votó 7.
- La Libertad Avanza → LLA 92 / 93.
- **Somos Buenos Aires → LLA 63**; → Provincias Unidas solo 5; → No votó 10.
- FIT-U → FIT-U 37 / 45; → Fuerza Patria 49 (dudosa: celda chica, típica sobreasignación ecológica hacia la fuerza dominante del territorio).
- Blanco 2025-09 → LLA 45 / 40.
- No votó → No votó 77 / 83; → Fuerza Patria 8; → Otros 7.

La auditoría no marca filas no identificadas (máxima diferencia con Calvo: 8,0 puntos en FIT-U). Entre variantes cambian 808.282 votos (6,1 % del total modelado). Son estimaciones ecológicas a partir de territorios, no observaciones de voto individual.

## Comparación con la versión por municipio (`pba_prov2025_dn2025`)
La base de `provinciales2025/bases.pkl` usa los 135 municipios del escrutinio definitivo y votos válidos (sin No votó). Para comparar se corrió el mismo ajuste (RxC de Calvo ponderado, una matriz) con sus categorías y su base en tres versiones: (1) la original, (2) esta base sumada a municipio y (3) esta base por circuito (1.041).

| % de la fila | (1) municipios, definitivo | (3) circuitos, provisorio | diferencia |
|---|---|---|---|
| LLA → LLA | 83,1 | 87,6 | +4,4 |
| FP → FP | 73,7 | 76,8 | +3,1 |
| FP → LLA | 8,4 | 6,1 | −2,3 |
| Somos → LLA | 63,3 | 63,4 | 0 |
| Somos → FP | 14,2 | 14,9 | +0,7 |
| Potencia → LLA | 62,2 | 69,9 | +7,7 |
| **FIT-U → FIT-U** | **10,1** | **37,4** | **+27,3** |
| **FIT-U → FP** | **73,6** | **56,0** | **−17,6** |
| Blanco → LLA | 48,1 | 44,4 | −3,7 |

- **Fuente**: (1) y (2) cambian el 0,3 % de los votos de celda. El provisorio por mesa y el definitivo municipal dan lo mismo.
- **Nivel**: (2) contra (3) cambia el 6,7 %. Casi todo es FIT-U: con 135 municipios su voto queda confundido con el del peronismo del conurbano y la versión municipal manda tres cuartos a Fuerza Patria, lo que no cierra con que FIT-U pasara de 349 mil a 439 mil votos. Por circuito retiene el 37 %; sigue siendo una celda débil.
- Somos → LLA (63 %) no depende del nivel.
- Distancia principal–Calvo (puntos ponderados): 4,8 por municipio, 4,2 por circuito.

Reproducir:
```
python datos/provinciales/pba2025/agregar.py
python -X utf8 transferencias/estimar.py 2025s 2025
python -X utf8 transferencias/sankey.py 2025s 2025          # también --votantes y --reducido
python transferencias/2025s_2025/comparar_municipios.py   # comparación con la versión municipal
```
