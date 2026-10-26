# base8399 — stub mixto 1983–1999, separado por elección

Generado con `python -I construir.py <carpeta del zip extraído>` (origen: `recopilacion_completa_electoral_1983_1999.zip`, 11-oct-2026).
Una carpeta por elección (`elecciones/AAAA_presidente` o `AAAA_diputados`), 13 en total. No se corrige ni imputa nada.

## Capas dentro de cada carpeta
| Archivo | Qué es | Cobertura |
|---|---|---|
| `lupu_stokes.csv` | Capa 1. Base Lupu–Stokes sin tocar (columnas originales). `ucr` y `pj` son **familias agrupadas**, no listas. | Todo el país (23–24 distritos, ~512–539 unidades) |
| `detalle_partidos.csv` | Capa 2. Votos absolutos por departamento y partido/lista tal como figuran en la fuente. Esquema común: provincia, anio, cargo, departamento, codigo_fuente, partido_fuente, votos, tipo_fila, fuente. | Solo las provincias de la tabla |

`manifest.csv` resume filas y provincias por elección.

## Capa 2 por elección
| Elección | Provincias con detalle |
|---|---|
| 1983 pres/dip, 1985, 1987, 1989 pres/dip | Mendoza |
| 1991 dip | Mendoza, Corrientes, Entre Ríos (15 dptos, falta Feliciano) |
| 1993 dip | Mendoza, Corrientes |
| 1995 pres/dip | Mendoza, Corrientes |
| 1997 dip | Mendoza, Corrientes, Entre Ríos (16 unidades, falta San Salvador) |
| 1999 pres/dip | Mendoza, Corrientes, Córdoba |

## Advertencias que pasan al stub
- **Lupu–Stokes** (corroborado por Lupu el 12-oct-2026): los datos de 1983–1999 vienen de la base de Escolar (PEEL-UTDT), no recuerda por qué faltan las filas de San Luis (dip 1997 y 1999) y confirma que faltan otras provincias. Esas ausencias son de la fuente y no se rellenan. En Capital las filas son circuitos.
- **Mendoza** (transcripción UNCuyo): discrepancias con DINE no resueltas: PJ presidente 1995 −38.000 (Godoy Cruz = 4.224, sospechoso); AAR presidente 1999 +180; Federal diputados 1999 −581 (¿cargo mal asignado?).
- **Córdoba 1999**: `tipo_fila` distingue agrupación / tipo_voto (blancos, nulos, impugnados, recurridos) / total. No sumar `total` con el resto. Nombre `ROQUE SAENZ PEÐA` sin normalizar. Incluye la unidad EMBAJADAS-CONSULADOS.
- **Corrientes**: `tipo_fila=subtotal_alianza` y `total` conviven con las agrupaciones: **no sumar**.
- **Entre Ríos**: este stub toma solo `votos_nacionales_departamentales.csv`; las tablas completas están en los `er_*.csv` de `provincias_iteracion`. Hay celdas vacías de votos que no son cero.
- Totgen95/99 y Río Negro son totales provinciales: sirven de control, no están en el stub.

## Sin cobertura de detalle (solo capa 1)
Todas las demás provincias, incluidos Buenos Aires, Santa Fe, Capital y Tucumán. Dependen de la base de Escolar / CD Calvo–Abal Medina. Mail a Escolar pendiente.

## Capa 3 (13-oct-2026): bases de Ernesto Calvo
`ernesto/` trae la base nacional por departamento y partido de 1983 a 1999 (archivos TPDENP de la carpeta «Bases Ernesto»), con presidente, diputados nacionales y categorías provinciales, para 23–24 provincias por elección. Es el equivalente de la base de Escolar que faltaba en la capa 1: el `total` de Lupu–Stokes se reconstruye con ella. Ver `ernesto/LEEME.md` (cobertura, anomalías y contraste con Lupu). Se genera con `construir_ernesto.py` y `control_ernesto.py`.
