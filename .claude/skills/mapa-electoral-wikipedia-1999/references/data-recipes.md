# Recetas según el tipo de dato

En todos los casos el paso común es: emparejar territorios (`scripts/match_territories.py`) → armar `units`/`prov`/`national` → `build_atlas.py` → mirar la captura. `scripts/example_prepare_1976.py` es una preparación completa de referencia.

| Dato disponible | Qué armar |
|---|---|
| **Ganador por departamento con votos por candidato** | `units[i] = {w, q, lines}` con `q` = % del ganador sobre votos válidos. `prov` y `national` salen de los totales provinciales y nacionales. |
| **Solo totales provinciales** | repetir el dato de cada provincia en todas sus `units`; `prov` igual. Aclarar en `note` que cada departamento hereda la provincia. |
| **Varias variantes del mismo cálculo** (p. ej. dos extrapolaciones) | un `mode` por variante con el mismo `set`: cada una es una pestaña. |
| **Dos vueltas / escenarios** | un `set` por vuelta (`sets`), con `subtitle` en el segundo; las pestañas del set actual más un botón para pasar al otro. |
| **Segunda vuelta simulada con traspasos** | `assets/segunda_vuelta.py`: editar `REGLAS` (a qué candidato va cada fracción) y `DISCRECION` (reparto de lo indeciso entre blanco/nulo/abstención). `provincia()` y `departamento()` aplican las mismas reglas y `resto_mayor()` redondea sin perder votos. Verificar contra la tabla del usuario si existe: con las reglas de 1976 coincide voto por voto. |
| **Elección con otros candidatos / más de 4** | `candidates` libre; la leyenda crece hacia abajo (4 filas con rampa caben holgadas; más de 6 exige achicar el paso `y`). Elegir `base` distinguibles en fondo oscuro y claro. |
| **Métrica que no es “ganador”** (participación, margen, % de un candidato, voto en blanco…) | `units[i] = {fill, lines}` con el color ya calculado (escala secuencial o divergente) y `legend:{title, stops, bars:false}` para dibujar la escala. |
| **Porcentaje de un solo candidato** | un `fill` por escala de ese candidato (`shade`-like: mezclar con blanco hasta su `base`), `legend.stops` con los cortes. |
| **Resultados con empates o sin dato** | `fill:"#bdbdbd"` y `lines` vacío; el territorio queda gris. |
| **Otra elección con otros límites departamentales** | el mapa base es el de 1999 (CABA en 28 circunscripciones; 510 departamentos/partidos). Si el dato usa otra división (comunas, departamentos nuevos), agrupar o repartir antes de armar `units`, o decir que no es exacto. |

## Candidatos y colores
- Rojo `#dc0143` y azul `#1c5ece` son los de 1999; para más candidatos elegir colores con luminosidad parecida a esos dos y revisar que los tonos oscuros (× .25) se distingan.
- Si la barra de leyenda necesita ser más oscura que la base (amarillos, verdes claros), usar `bar` y `txt`.
