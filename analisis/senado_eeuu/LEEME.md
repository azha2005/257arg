# Senado con el sistema de EE. UU. (4-nov-2026)

Pedido del usuario: dos senadores por provincia (48), elegidos de a uno por mayoría simple, con mandatos de
seis años y tres clases escalonadas (16 bancas por turno). Sin banca de minoría.

- `python analisis/senado_eeuu/tablas.py`: lee las tablas de senadores y diputados de 2021, 2023 y 2025 de los
  artículos de la Wikipedia (`datos/wikileg/wleg<año>.txt`, escrutinio definitivo) → `tablas.json`.
- `python analisis/senado_eeuu/calcular.py`: bloques, ganadores y totales → `resultado.json`.

## Método
- Cada provincia conserva su turno real de senadores (2021, 2023 o 2025) y suma otro, para que cada clase
  tenga 16. En el turno real se usa su elección de senadores; en el agregado, que no eligió senadores, su
  elección de **diputados nacionales** de ese año (aproximación).
- Dos rotaciones del turno agregado: A = el siguiente (2021→2023→2025→2021), B = el anterior.
- El Senado real de comparación son las 72 bancas que salieron de esas tres elecciones (2 + 1 por provincia),
  contadas por la lista con que se eligieron, no por el bloque en que se sientan hoy.
- Bloques: Peronismo (FdT, UxP, Fuerza Patria y los PJ provinciales de 2025, Frente Cívico por Santiago),
  La Libertad Avanza (con sus alianzas provinciales; Jujuy 2023 «Partido Renovador Federal», como lo rotula la
  Wikipedia), Juntos por el Cambio (Cambia Mendoza, ECO + Vamos Corrientes 2021, Juntos por Entre Ríos, Unión
  por San Luis…), Provincias Unidas / peronismo federal (Hacemos, Vamos Corrientes 2025) y Provinciales (FRC,
  MPN, Por Santa Cruz).

## Bloques actuales
Pedido del usuario: contar con los bloques de hoy (senado.gob.ar, «agrupados por bloques» y «listado por
provincia», consultados el 4-nov-2026), no con la lista por la que entró cada uno.
- Turno real (elección de senadores): la banca va al bloque de quien encabezó la lista ganadora (`CABEZA`):
  Chaco 2025 → Godoy (LLA), Chubut 2021 → Cristina (Frente PRO, la banca de Torres), La Pampa 2021 →
  Kroneberger (UCR), Córdoba 2021 → Juez (LLA), Catamarca 2021 → Corpacci (Justicialista), Tucumán 2021 →
  Manzur (Justicialista), Jujuy 2023 → Atauche (LLA).
- Turno agregado (diputados): la fuerza ganadora va al bloque donde se sientan hoy los senadores de esa fuerza
  en la provincia: peronismo de Corrientes → Provincias Unidas (Espínola), de San Luis → Justicia Social
  Federal (Salino), Tucumán Primero → Convicción Federal (Jaldo), Vamos Corrientes → UCR, JxC de Capital,
  Chubut, Entre Ríos y Misiones → Frente PRO, de Córdoba → LLA, el resto de JxC → UCR. MPN y Juntos Somos Río
  Negro ganan en 2021 pero hoy no tienen senadores.

## Resultado
| Bloque actual | Senado hoy (72) | EE. UU. A (48) | EE. UU. B (48) |
|---|---|---|---|
| Justicialista | 22 | 17 | 16 |
| La Libertad Avanza | 21 | 17 | 15 |
| UCR | 10 | 4 | 8 |
| Frente PRO | 3 | 3 | 3 |
| Convicción Federal | 3 | 0 | 1 |
| Frente Cívico por Santiago | 2 | 2 | 2 |
| Provincias Unidas | 2 | 1 | 0 |
| Movimiento por Misiones | 2 | 1 | 1 |
| Movere Santa Cruz | 2 | 1 | 1 |
| Justicia Social Federal | 1 | 0 | 1 |
| Despierta Chubut, Independencia, La Neuquinidad, Primero los Salteños | 1 c/u | 0 | 0 |
| MPN / JSRN (sin bloque hoy) | 0 | 1 + 1 | 0 |

Ganadores muy parejos (margen menor a un punto): Chaco 2025, San Juan 2023, Río Negro 2025, Chubut 2025,
Buenos Aires 2025 (diputados), La Rioja 2025, Santa Cruz 2025, San Luis 2021. El provisorio de San Juan 2023
daba ganador a LLA; el definitivo, a UxP.
