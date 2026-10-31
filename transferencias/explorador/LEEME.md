# Explorador de transferencias (sankey de dos elecciones cualesquiera)

Página local para elegir cualquier par de elecciones del proyecto y ver el sankey al momento, nacional o por provincia.

```
python transferencias/explorador/servidor.py      # abre http://127.0.0.1:8790
```
En Windows también sirve doble clic en `abrir_explorador.bat`. La primera vez lee `MASTER_resultados.xlsx` (~2 min) y lo guarda en `cache/master.pkl`.

## Publicado en Streamlit Community Cloud (gratis)
`streamlit_app.py` es el explorador como app de Streamlit: los selectores y el cálculo van en Python y el sankey lo dibuja `index.html` en modo incrustado (`window.EMBED`), así se ve igual que la página local. Local: `streamlit run transferencias/explorador/streamlit_app.py` (o «sankeys-streamlit» en `.claude/launch.json`).

Streamlit lee el repo público **github.com/azha2005/transferencias-sankey**, que es `space/_build/` (lo arma `space/armar.py`; la carpeta guarda su propio `.git`). Para actualizarlo:
```
python transferencias/explorador/space/armar.py
cd transferencias/explorador/space/_build && git add -A && git commit -m "..." && git push
```
Streamlit vuelve a desplegar solo. Al crear la app en share.streamlit.io: rama `main`, archivo `transferencias/explorador/streamlit_app.py` y, en *Advanced settings*, **Python 3.11** (los `.pkl` son de pandas 1.5.3, que no tiene versión para 3.12 o posterior).

## Publicarlo en Hugging Face Spaces (requiere PRO desde 2026)
`space/` tiene el `Dockerfile`, `requirements.txt` y el `README.md` (con la cabecera que pide Hugging Face) del Space. `space/armar.py` junta en `space/_build/` (fuera de git) el código y solo los datos que lee el explorador, con las mismas rutas del repo (~185 MB: `circ_*.pkl`, `cache/master.pkl` en lugar del xlsx, `dataset_*.json`, `mapeo_listas`, ámbitos de la DINE, correspondencias y los pares ya calculados):
```
python -c "from huggingface_hub import login; login()"                 # una vez, pega un token de escritura
python transferencias/explorador/space/armar.py --subir USUARIO/transferencias
```
Si cambia un dato o el código, se vuelve a correr lo mismo (`--limpiar` borra del Space lo que ya no está). En el Space el servidor escucha en `0.0.0.0:7860` (`HOST` y `PUERTO` del Dockerfile) y sigue haciendo un cálculo por vez.

## Qué elecciones hay (279)
- **Categorías curadas** (`transferencias/circ_<clave>.pkl`, 56): las de los sankeys ya hechos, con los grupos de `CAT` de `estimar.py`. Cuando origen y destino son de este grupo se cruzan **por circuito** con `estimar.prepare` (con las correspondencias revisadas de cada par); cualquier otro par, por departamento.
- **MASTER** (`resultados_xlsx`, 158): todas las elecciones y cargos del índice que tienen votos en la hoja `largo` (quedan afuera AMBA 2025 por circuito, que está en el atlas, y 1985 `otras_cn`, vacía), incluidos gobernador, legislaturas provinciales, senadores y las fuentes complementarias (detalle de Mendoza, Corrientes, Córdoba, Entre Ríos, dat.ar).
- **Atlas** (`mapas/mapa*/dataset_*.json`, 65): lo que muestra cada mapa, incluidas las **PASO de presidente** (por precandidato o por agrupación) **y de diputados** 2011–2023, 1948, 1948c, 1973, 1973s, 2001 bronca, AMBA 2025 (sumado a partido y comuna) y los **escenarios hipotéticos** (1916 ficticio, 1985hip, 1995 UCR + FREPASO, 2023 Massa, 2027 y 2027 Kicillof), en su propio grupo.

## Método
El de `estimar.py` (RxC penalizado de E. Calvo, una matriz por provincia encogida hacia la nacional, penalización por validación cruzada), **sin bootstrap**: es la estimación puntual. «Rápido» usa la penalización fija 2e-6 y no hace validación cruzada. 

### Avisos de confiabilidad (los mismos criterios de `auditar.py` y `sankey.py`)
- `*` **fila no identificada**: la matriz nacional difiere en más de 30 puntos (20 si la fila pesa menos del 5 %) de la variante de una sola matriz nacional sin pesos (la del R de Calvo).
- `†` **fila cerca del promedio**: fila de 5 % o más (no «No votó», «Blanco y nulo» ni «Otros») cuya separación ½·Σ|fila − promedio| es menor a 25 puntos: se reparte casi como el total.
- Aviso rojo **«Matriz poco informativa»**: la separación media de las filas grandes es menor a 25. En la vista provincial, `†` y el aviso se calculan con la matriz de esa provincia; `*` solo existe en la nacional.
- Nota en la vista provincial si la matriz le da a un destino más del 125 % de sus votos reales (+2000).
- El panel «Confiabilidad» muestra la separación y la diferencia con Calvo de cada fila.

A diferencia de `auditar.py`, no hay bootstrap, así que no hay marca por intervalo ancho. Para publicar un par, correr el flujo completo de `transferencias/LEEME.md` (bootstrap, auditoría).

## Cómo se emparejan las unidades
- Por nombre de departamento dentro de cada provincia (`datos.nk`/`nkp`: sin tildes, abreviaturas expandidas, «Cuarta Sección · San Rafael» → «San Rafael», números de E. Calvo quitados), con sinónimos por provincia en `SINONIMOS` (San Luis, Jujuy, Chaco, Formosa, Neuquén, Entre Ríos, Tierra del Fuego) y parecido de nombre ≥ 0,85 para el resto.
- Si los emparejados cubren menos del 75 % de los votos de la provincia en alguna de las dos (y ninguna está cubierta al 95 %), la provincia entra **entera, como una sola unidad**: su matriz es casi la nacional y el selector lo dice. Le pasa a Capital Federal cuando se cruzan épocas con divisiones distintas (secciones de Cantón, 28 circunscripciones, 15 comunas).
- «No votó» solo si las dos elecciones tienen electores en el 90 % de las unidades; si no, todo se hace sobre votos emitidos (y la nota lo dice).
- Se descartan las unidades cuyo tamaño cambia fuera de ×0,5–×2 del cambio mediano.

## Categorías de MASTER y de los atlas
Bloque de la Wikipedia si la elección lo tiene; si no, el partido (en 1983–1999, la familia del código de E. Calvo según `FAMS` de `comun/atlas_leg8399.py` y `FAM` de `build_1997.py`). Entran las de 3 % o más a nivel nacional (hasta 8) y las de 30 % o más en alguna provincia; el resto va a «Otros». En los atlas, cada lista provincial va al bloque de la leyenda cuando el código o el color coinciden con uno solo.

## Archivos
| Archivo | Qué hace |
|---|---|
| `datos.py` | catálogo y tabla por unidad de cada elección; nombres y colores |
| `motor.py` | emparejamiento, ajuste y caché (`cache/pares/`, se invalida cambiando `VERSION`) |
| `servidor.py` | servidor local (un cálculo por vez, prioridad baja) |
| `index.html` | la página: selectores con filtro, vista nacional o provincial, sin «No votó», escala 1:4, SVG y CSV |

Límites: pares de épocas lejanas son comparación de geografías, no traspasos (la nota lo avisa a partir de 12 años); las categorías chicas tienen márgenes grandes; Capital Federal no se cruza entre esquemas distintos de secciones.
