# Knesset: proyección durante el conteo y aguja de bloques

Adaptación a Israel de la proyección de la noche electoral (27-oct-2026, día de la elección de la Knéset 26).

## Datos

- `datos_oficiales/israel/k<N>_expb.csv` (por urna) y `k<N>_expc.csv` (por localidad) del Comité Central Electoral: `https://media<N>.bechirot.gov.il/files/expb.csv`, N = 21 (abril 2019), 22 (septiembre 2019), 23 (2020), 24 (2021), 25 (2022). Bajados el 27-oct-2026. A esa hora `media26` y `votes26` daban 404.
- Una fila por urna (`קלפי`): localidad (`סמל ישוב`), padrón (`בזב`), votantes, válidos (`כשרים`) y una columna por letra de boleta. Están en cp1255 o en UTF-8, según el año.
- **Doble sobre** (soldados, diplomáticos, presos, hospitales): es la localidad 9999 (99999 en abril de 2019). No tiene padrón propio y fue el 6–10 % de los votos válidos (459.000 en 2022). Se cuenta días después, así que durante la noche siempre se proyecta.

## Reparto de bancas (`datos.py`)

- Umbral del 3,25 % de los válidos.
- D'Hondt (Bader-Ofer) entre unidades: una pareja con acuerdo de excedentes cuenta como una sola unidad si las dos listas pasan el umbral.
- Después, D'Hondt dentro de cada pareja.
- **Validación:** reproduce exactamente las bancas oficiales de 2021 y 2022. Para 2019 y 2020 no cargué los acuerdos, así que esos años dan bancas aproximadas.

## Modelo (`modelo.py`)

- **Origen de cada urna:** la misma urna (localidad + número entero) en la elección anterior. Si no se encuentra, la localidad. La numeración coincide en el 93–97 % de las urnas entre 2019 y 2021, pero solo en el 69 % en 2022.
- **Matrices:** Goodman nacional con las urnas contadas, y una matriz por sector encogida hacia la nacional con 150 urnas de peso. Los sectores salen de la composición de origen de cada localidad: árabe, haredí, derecha religiosa, localidades chicas y ciudades.
- **Sin recortar la matriz a ≥ 0.** El recorte inflaba a las listas chicas, que son las que están al borde del umbral. Con él, 2022 daba 5–6 bancas de error en el bloque; ahora se recorta solo lo proyectado de cada sector. Es la misma lección que en Argentina.
- **Ancla (agregada en vivo el 27-oct-2026, con 128 urnas):** la matriz nacional se encoge hacia una matriz de antecesores.
  - Cada lista de 2022 pasa a su sucesora con el cambio proporcional observado. Ese cambio se encoge hacia 1 con 3000 votos de peso (`MP`).
  - El ancla pesa como 300 urnas (`NP`).
  - Sin ancla, con 1 urna árabe y 2 haredíes, la proyección daba 20 bancas a la Lista Conjunta y dejaba a Shas fuera.
  - Backtest (`RESUMEN_BACKTEST.md` ya es con ancla), orden geo:

    | Urnas contadas | Error del bloque, sin ancla | Con ancla | Ancho de la banda del 90 %, sin ancla | Con ancla |
    |---|---:|---:|---:|---:|
    | 1 % | 2,4 | 1,2 | 13,9 | 5,2 |
    | 2 % | 1,8 | 0,95 | — | — |
    | 5–10 % | ~1,0 | ~1,1 | — | — |

  - En orden al azar queda igual.
- **Residuo por localidad** (`KR`, agregado en vivo el 27-oct-2026; es la parte local del método peruano de `proyeccion/`):
  - El desvío de las urnas contadas de cada localidad respecto del modelo se suma a sus urnas sin contar.
  - Se encoge por W / (W + 1500), donde W es el padrón ya contado en esa localidad.
  - Backtest de 2019–2022, orden geo, error medio por lista en bancas:

    | Urnas contadas | Sin residuo | Con residuo |
    |---|---:|---:|
    | 10 % | 0,44 | 0,37 |
    | 20 % | 0,32 | 0,23 |
    | 40 % | 0,24 | 0,13 |

  - Al 1–5 % da igual. En orden al azar empeora 0,03.
  - Probé 1500, 5000 y 15 000: `backtest_kr*.csv`.
- **Vecinas** (`KV`, residuo del concejo regional o subdistrito del mismo sector para las localidades sin nada contado):
  - Tabla de localidades del CBS en `datos_oficiales/israel/localidades_cbs.csv`, de data.gov.il.
  - **No se usa** (`KV` = 0).
  - En `backtest_7.py`, con las urnas exactas del archivo del 7 %, no mejora nada y la banda deja de cubrir en 2020 → 2021: cubre en 25 % de los casos, contra 88–100 % sin vecinas.
- **`backtest_7.py`:** repite, en cada elección de 2019–2022, las urnas de un `expb.csv` de 2026: misma localidad y número de urna, completando al azar dentro de la localidad.
  - Con el archivo del 7 % (908 urnas), error medio de las bancas del bloque de Netanyahu: 0,9 con solo el ancla, 0,56 con el residuo por localidad.
  - Peor caso: 2020 → 2021, cuando cambió el voto árabe (Raam se separó y la participación árabe se desplomó). Ahí el bloque erró 2 bancas y los árabes 3.
  - El conteo crudo de esas mismas urnas erraba 11–14 bancas.
  - El desenlace acertó en todos los casos.
- **Doble sobre:** cambio proporcional. Para cada lista: su porcentaje en el doble sobre anterior (el de su antecesor) × su cambio en las urnas comunes. Erra la mitad que aplicar la matriz nacional (0,55–0,9 puntos por lista contra 1–1,5). El error que queda va a la banda: ×exp(N(0; 0,25)) por lista y ±6 % en el total.
- **Banda:** bootstrap de grupos de urnas (la localidad, y bloques de 20 urnas en las ciudades). Cada remuestra se pasa a bancas y a bloques.
- **Desenlace:** Netanyahu ≥ 61, oposición judía ≥ 61, o ninguno (la mayoría depende de las listas árabes).

## Backtest (`backtest.py` → `RESUMEN_BACKTEST.md`)

Cuatro pares de elecciones (2019a→2019b, 2019b→2020, 2020→2021 y 2021→2022), con dos órdenes de llegada simulados. No hay hora de llegada por urna, así que los órdenes son inventados:
- **azar:** urnas en cualquier orden;
- **geo:** localidades chicas primero, ciudades grandes y localidades árabes después.

Resultados:
- **Error en las bancas del bloque de Netanyahu:**

  | Urnas contadas | Modelo, azar | Modelo, geo | Conteo parcial tal cual |
  |---|---:|---:|---:|
  | 5 % | 0,2–0,6 | 0,6–1,6 | 0,8–6,4 |
  | 10 % | 0–0,6 | 0,4–2,2 | 0,8–5,4 |

- **Desenlace:** acertado en las cuatro elecciones desde el 2 % contado. Con el 1 %, falla una de cada cinco veces en 2022.
- **Probabilidad del desenlace real:** con el 10 % contado, el modelo le daba 88–100 %.
- **Banda del 90 % del bloque:** contiene el resultado real en el 100 % de los casos desde el 2 % contado. Es ancha en 2022 (3–6 bancas), porque Meretz (3,16 %) y Balad (2,91 %) estaban al borde del umbral.

## Aguja (`aguja_israel.py` → `../img/aguja_israel_2022.png`)

Repetición de la noche de 2022 desde 2021, con orden geo. El dial marca las bancas del bloque de Netanyahu, con la mayoría (61) arriba. Debajo van las probabilidades de los tres desenlaces y la evolución de las bancas del bloque y de la oposición judía a lo largo del conteo.

## Esta noche (`vivo.py`)

```
python -X utf8 proyeccion/israel/vivo.py https://media26.bechirot.gov.il/files/expb.csv --padron <electores 2026 sin el exterior>
python -X utf8 proyeccion/israel/vivo.py --prueba 0.1      # ensayo con 2022
```

- **Supuestos:**
  - el archivo de 2026 tiene el mismo formato que el de 2019–2022, pero la URL es una suposición;
  - las urnas contadas son las filas con votantes;
  - lo que falta, por localidad: su padrón de 2022 × el crecimiento, menos lo ya contado.
- **`letras26.csv` completado** con la plantilla `{{אותיות רשימה}}` de la Wikipedia en hebreo (38 listas).
  - Juntos es `רק`, Yashar `דרך`, Otzma `ב`, Noam `ני`, Lista Conjunta `ודם`, Reservistas `די` y Amcha Yisrael `ך`.
  - **`פה` (Yesh Atid en 2022) y `ד` (Balad en 2022) son ahora de listas menores.** Las letras que no están en la tabla quedan sin antecesor y no heredan los votos de 2022.
- **Descarga:** `media26.bechirot.gov.il/files/expb.csv` responde 202 vacío a los scripts (desafío antibots de AWS WAF).
  - Se baja con el navegador y se le pasa a `vivo.py` el archivo o la carpeta. Con una carpeta, toma el `expb*.csv` más reciente.
  - No se salta el desafío.
- **Otras fuentes oficiales:**
  - `votes26.bechirot.gov.il`: páginas nacionales, por localidad y por urna. Se leen con el navegador y tienen los mismos enlaces a `expb.csv` y `expc.csv`.
  - `elections.govmap.gov.il`, el mapa oficial:
    - `data/votes/elections.json` trae las letras y los nombres de 2026, que coinciden con `letras26.csv`. Kajol Lavan no figura.
    - `data/votes/latest/municipal_data.json` es por localidad, con `totals.kalpi_counted`, y se refresca cada 5 minutos.
    - También tiene el desafío WAF, así que solo sirve leído desde el navegador.
- **Boca de urna:** el informe trae la del Canal 12 como referencia: bibi 50, oposición 52, árabes 18.
- **Antecesores y bloques de 2026** (`datos.LISTAS26`), con fuentes en el código: Wikipedia (2026 Israeli legislative election y Party lists for the 2026 Israeli legislative election), Times of Israel (38 listas presentadas) y Haaretz (listas finales).
  - **Juntos (Bennett-Lapid)** ← Yesh Atid.
  - **Likud** ← Likud. Nueva Esperanza, que se fusiona con el Likud, iba en 2022 dentro de Unidad Nacional; no se reparte.
  - **Sionismo Religioso-Zehut, Otzma Yehudit y Noam** ← la lista común de 2022.
  - **Los Demócratas** ← Laborismo + Meretz.
  - **Yashar (Eisenkot)** ← Unidad Nacional.
  - **Reservistas** ← Unidad Nacional + Hogar Judío.
  - **Amcha Yisrael** sin antecesor; el Times of Israel la ubica en el bloque de Netanyahu.
  - **Lista Conjunta** ← Hadash-Taal + Balad.
  - **Raam** ← Raam.
- **Acuerdos de excedentes 2026:** Juntos–Israel Beitenu, Yashar–Demócratas, Lista Conjunta–Raam, Likud–Sionismo Religioso y Shas–UTJ.
- **Riesgos:**
  - Es la primera vez que se arma una lista común Bennett–Lapid, y Yashar es un partido nuevo. Los antecesores son aproximados, y al principio de la noche la proyección de esas listas es poco confiable.
  - Kajol Lavan anunció que se retiraba, pero sigue en la boleta.
  - El orden de llegada real de 2026 puede ser distinto del simulado.


## Actualización del 28-oct-2026

Smilganir devolvió el corte oficial de las 05:57 de Israel (5.037 urnas). Su rama pública gh-pages conserva 17 revisiones del bundle: los conteos encontrados ya estaban representados por archivos locales; igual número de urnas no garantiza idénticos votos. El último archivo oficial aportado por el usuario, `expb (14).csv`, contiene 11.542 urnas y 5.024.919 votos válidos. `vivo.py` fue ejecutado sobre ese archivo: 97,6 % del padrón estimado; el doble sobre sigue proyectado. Bloques proyectados: Netanyahu 53, oposición judía 49, listas árabes 18. No son resultados definitivos. La historia conserva los cortes anteriores y excluye la segunda copia del corte de 5.037 urnas agregada durante esta revisión. `historial_smilganir_recuperado.json` contiene los commits consultados. El título muestra el nombre de fuente, evitando confundir la hora local de ejecución con una hora oficial de actualización.
