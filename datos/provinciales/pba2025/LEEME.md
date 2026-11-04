# PBA, 7 de septiembre de 2025, por mesa

Base por mesa del provisorio pedida a graficarpba (llegó el 3-nov-2026 como
`drive-download-20261104T051010Z-1-001.zip`). **No se versiona** (`.gitignore`:
`resultados_*.csv`); para regenerar, descomprimir el zip en esta carpeta:

| archivo | tamaño | uso |
|---|---|---|
| `resultados_senadores_provinciales.csv` | 197 MB | `agregar.py` (secciones 1.ª, 4.ª, 5.ª y 7.ª) |
| `resultados_diputados_provinciales.csv` | 199 MB | `agregar.py` (secciones 2.ª, 3.ª, 6.ª y 8.ª) |
| `resultados_concejales.csv` | 302 MB | sin usar todavía |

```
python datos/provinciales/pba2025/agregar.py
```

escribe `circuitos.csv` (versionado, una fila por circuito y tipo de mesa) y
`transferencias/circ_2025s.pkl`, que usa `transferencias/2025s_2025/` (sankeys
PBA septiembre → diputados nacionales octubre 2025). Códigos de la base y
decisiones en el docstring de `agregar.py`.

Control (4-nov-2026): los CSV del zip reproducen exactamente `circuitos.csv` y
`circ_2025s.pkl` generados en la otra PC.

`proyeccion/provincial/ingestar.py pba2025` todavía espera un `mesas.csv` en
formato largo (seccion, circuito, mesa, lista, votos…; ver
`proyeccion/provincial/config.py`, `ELECCIONES["pba2025"]`): falta adaptar el
ingestor a estas columnas (`mesa_key`, `circuito_codigo`, `name`, `votos`,
`census`, `totalVotos`).
