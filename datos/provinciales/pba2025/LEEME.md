# PBA, 7 de septiembre de 2025, por mesa (pendiente)

Acá va el archivo por mesa pedido a graficarpba, como `mesas.csv`. Lo lee `proyeccion/provincial/ingestar.py pba2025`
(configuración en `proyeccion/provincial/config.py`, `ELECCIONES["pba2025"]`).

Formato que espera, una fila por mesa y lista (si viene ancho, una columna por lista, hay que pasarlo a largo antes):

| columna | qué es |
|---|---|
| `seccion` | partido: nombre («Almirante Brown») o código de la DINE (3) |
| `circuito` | circuito electoral, con o sin ceros a la izquierda |
| `mesa` | número de mesa |
| `mesa_tipo` | opcional; `EXTRANJEROS` para las mesas de residentes extranjeros |
| `electores` | opcional; si falta, sale del padrón nacional 2025 de la misma mesa |
| `cargo` | opcional; senadores o diputados provinciales |
| `lista` | nombre de la lista, o «votos en blanco», «nulos», «recurridos»... |
| `tipo` | opcional; positivo / blanco / nulo / recurrido |
| `votos` | votos |

Si las columnas se llaman distinto, se renombran con `columnas` en la configuración (p. ej. `{"partido": "seccion"}`).
Los nombres de partido que no coincidan con los de la DINE van a `ALIAS` en `config.py`.

La primera corrida sin `listas.csv` escribe `listas_plantilla.csv` con todas las listas y sus votos: se completa la
columna `bloque` (FP, LLA, SB, FIT; las demás vacías van a OTRAS) con la tabla de la Wikipedia y se guarda como
`listas.csv`. Si una lista cambia de bloque según la sección, se agrega la columna `seccion` (1 a 8).
