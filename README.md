# Atlas electorales argentinos

*English summary below · [Versión en español](#atlas-electorales-de-argentina-1904-2025)*

## In English

**Interactive maps and data for Argentine elections.** The national series spans 1904-2025 and covers presidential elections, national deputies, runoffs, PASO primaries and the 1994 constituent assembly. Historical coverage varies by election. Four earlier presidential atlases (1868, 1874, 1880 and 1886) map Buenos Aires province and city by district and parish from period press and returns, with the other provinces coloured by their electoral-college vote. The repository also includes:

- a [historical viewer for Buenos Aires city](https://azha2005.github.io/257arg/capital/), 1864-2007, with [election data in JSON](mapas/capital_canton/elecciones_1864_2007.json) and parish-level maps for selected nineteenth-century elections. More recent city results are covered by the national and AMBA series and the [2025 city election data](transferencias/provinciales2025/base_caba.csv);
- [model-based estimates by census tract for Greater Buenos Aires](mapas/serieAMBA2005_2023radios/INDICE.html), 2003-2025;
- hypothetical election scenarios and an experiment with 257 single-member districts;
- ecological-inference estimates of vote transfers between elections, using a Python port of Ernesto Calvo's RxC method, with Sankey diagrams;
- maps published on Wikimedia Commons and scripts for preparing uploads;
- a spreadsheet with every department-level result the project gathers (`resultados_xlsx/`), including the 1868-1886 atlases and the 104 Buenos Aires city elections of 1864-2007 from Cantón and Jorrat's CD.

No Argentine public body publishes this compilation: the electoral authority publishes polling-station data only from 2011, and earlier years are scattered across books, archives and private datasets.

Website with all atlases: <https://azha2005.github.io/257arg/>

### Coverage

| Period | Elections | Sources | Notes |
|---|---|---|---|
| 1868-1886 | President (1868, 1874, 1880, 1886) | Period press and returns (*La Nación*, *La Prensa*, *Nación Argentina*), Cantón and Jorrat's city CD for the capital | Popular-vote figures exist mainly for Buenos Aires (province by district, city by parish) and a few provinces (San Juan, La Rioja, Tucumán, San Luis in some years); the rest are painted by the electors each ticket won, per Wikipedia. Press tables are kept as printed, without adjusting them to the official total. |
| 1904-1973 | President and national deputies (1904, 1912, 1914, 1916, 1918, 1920, 1922, 1926, 1928, 1930, 1936, 1937, 1940, 1946, 1948, 1951, 1954, 1958, 1962, 1965, 1973) | Own transcriptions of Darío Cantón's *Materiales* (1968), of Chamber of Deputies files and of period press; Lupu & Stokes for 1948 and 1973; 1904 and 1951 from the Wikipedia constituency tables | Coverage is partial in several years; provinces with only a provincial total are painted in a solid colour. 1904 and 1951 are mapped by single-member constituency, with constituencies redrawn from published maps and the literature. Archival sheets from the Archivo General de la Nación are being added (Santiago del Estero 1962 so far). |
| 1983-2001 | President, national deputies, 1994 constituent assembly | Mainly Ernesto Calvo's department base, completed with Lupu & Stokes and INAP; cross-checked against the provincial tables | Some years have only provincial totals (San Luis 1997; San Luis and Santa Cruz 1999). Registers with more voters than registered electors are flagged, not corrected. |
| 2003-2025 | National deputies, president, runoffs, PASO primaries | DINE provisional count by polling station; PolAr for 2003-2009 | Missing departments were filled from DINE final results recovered via the Wayback Machine and from CNE queries. General elections for national deputies have departmental coverage throughout. Some presidential elections, runoffs and PASO primaries still have gaps documented in their atlas notes. |
| 2003-2025 (AMBA) | Census-tract estimates | DINE polling-station results, polling-place locations, CONICET census tracts | Votes are allocated from polling places to tracts: a model, not observed data. |

- **Geometry**: each election uses the departments of the nearest census (1914, 1960, 1980, 1991, 2001 or 2010), from the historical department base of Rodríguez and De Grande (CEUR-CONICET). Boundaries are not harmonised across censuses. Departments created after a census get their own polygon taken from a later shapefile; they are never merged.
- **National totals** come from the Spanish Wikipedia tables; the maps come from the local data, and differences are explained in each atlas's `LEEME`.
- **Estimates**: hypothetical scenarios, census-tract results and vote transfers are models, not observed data, and are labelled as such.
- **Gaps**: what could not be found is left blank (beige on the maps) and documented, never imputed.

Each `mapas/mapa<YEAR>/LEEME_<YEAR>.md` (in Spanish) gives the sources, coverage and decisions for that atlas.

### Reproducing

Every atlas, PNG and transfer estimate is rebuilt from the data by scripts. Run them from the repository root (Python 3.11):

```
python -m pip install -r requirements.txt
python -m playwright install chromium            # only for PNGs and Commons packages
python mapas/mapa1983/build_1983.py              # one atlas: atlas_1983.html and dataset_1983.json
python mapas/mapa2023/build_2023.py              # national deputies 2003-2025
python transcripciones/canton5865/atlas5865.py 1962   # 1958, 1962, 1965 (Cantón)
python comun/render_transparentes.py mapa1983    # PNG of every mode
```

From 2003 on, the builders need the DINE polling-station files (downloaded from datos.gob.ar, not stored in the repository). The full list of builders, data downloads, the transfer pipeline and the required User-Agent setting are in the Spanish sections [Instalación](#instalación), [Regenerar un atlas](#regenerar-un-atlas) and [Regenerar las transferencias](#regenerar-las-transferencias).

### How to cite

> Rodríguez Paolini, Juan Cruz. *Atlas electorales de Argentina 1904-2025*. <https://github.com/azha2005/257arg>

Please also cite the original source of each series you use (Calvo; Lupu and Stokes; Cantón; DINE; CNE) and the geometry (Rodríguez and De Grande, CEUR-CONICET). GitHub's "Cite this repository" button uses [`CITATION.cff`](CITATION.cff).

### Licences

- **Code**: MIT ([`LICENSE`](LICENSE)).
- **The project's own data, maps and texts**: CC BY 4.0 ([`LICENSE-DATA.md`](LICENSE-DATA.md)).
- **Third-party data, geometry and logos** keep their own terms (the department shapefiles are CC BY 2.5 AR; logos are listed in [`logos/LICENCIAS.md`](logos/LICENCIAS.md)). No licence is claimed over them.

---

## Atlas electorales de Argentina 1868-2025

Atlas interactivos y datos de elecciones argentinas. La serie nacional abarca 1904-2025, principalmente por departamento, con mapas por circunscripción en 1904 y 1951. La cobertura territorial de las elecciones históricas varía según las fuentes disponibles. Antes hay cuatro atlas presidenciales del siglo XIX (1868, 1874, 1880 y 1886, en `mapas/mapa1868/` a `mapas/mapa1886/`): Buenos Aires por partido y parroquia con cuadros de prensa y actas de época, algunas provincias con su acta o su cuadro (San Juan y La Rioja en 1874, Tucumán en 1880) y las demás en color sólido según los electores que ganó cada fórmula. El proyecto incluye además:

- datos de la ciudad de Buenos Aires entre 1864 y 2025, con el [visor histórico de Cantón y Jorrat](https://azha2005.github.io/257arg/capital/) para 1864-2007 y sus [datos en JSON](mapas/capital_canton/elecciones_1864_2007.json). Los resultados posteriores se consultan en las series nacional y del AMBA y en la [base de la elección porteña de 2025](transferencias/provinciales2025/base_caba.csv);
- [estimaciones por radio censal para el AMBA](mapas/serieAMBA2005_2023radios/INDICE.html), 2003-2025;
- [escenarios electorales hipotéticos](https://azha2005.github.io/257arg/mapas/mapa2003alt/), con sus supuestos y fuentes documentados;
- una planilla con todos los resultados por departamento que reúne el proyecto, con los atlas de 1868 a 1886 y las 104 elecciones porteñas de 1864 a 2007 del CD de Cantón y Jorrat;
- estimaciones de transferencias de voto entre elecciones por inferencia ecológica, con [diagramas de Sankey provinciales](transferencias/provinciales/INDICE.html);
- un ejercicio con la Cámara de Diputados en 257 distritos uninominales dibujados por algoritmo sobre el censo 2022 (`analisis/uninominal/`);
- los paquetes para subir los mapas a Wikimedia Commons.

Sitio con todos los atlas: <https://azha2005.github.io/257arg/>. Los 257 distritos: <https://azha2005.github.io/257arg/uninominal/>.

Cada atlas es un HTML autocontenido con pestañas por modo (ganador, porcentaje de cada fuerza, participación), descripción de cada unidad al pasar el mouse y descarga en SVG y PNG.

## Estructura

| Ruta | Qué hay |
|---|---|
| `mapas/mapa<AÑO>/` | Un atlas por elección: `build_<AÑO>.py`, `atlas_<AÑO>.html`, `dataset_<AÑO>.json` y `LEEME_<AÑO>.md` (fuentes, decisiones, pendientes). Sufijos: `dip` diputados, `fic` ficticio, `hip` hipotético, `kic` escenario 2027 Kicillof-Milei. |
| `comun/` | Código compartido por los atlas: constructores de las legislativas (`atlas_leg8399.py`, `atlas_leg2003_2025.py`), totales de Wikipedia (`wikitop.py`, `bloques_wiki.py`), recuadros (`insets99.py`), partidos nuevos (`newpartidos.py`), limpieza del contorno (`outline_clean.py`), renderizado a PNG y exportación a xlsx. |
| `transcripciones/` | Transcripciones propias por departamento: Cantón (`canton5865/` con el constructor de 1958, 1962 y 1965; `canton1937_1940/`, `canton1946/`, `canton1954/`…), expedientes y prensa de 1912, 1914 y 1916 (`busqueda1912/`, `busqueda1914/`, `1916dip/`) y Mendoza 1922 (`mdz22/`). |
| `transferencias/` | Inferencia ecológica RxC (port a Python del código R de E. Calvo), matrices, bootstrap, auditorías y Sankeys. Ver `transferencias/LEEME.md`. |
| `datos/` | Bases de terceros ya preparadas (`base8399/`, `preparados/`, `canton_ciudad/` con la lectura del CD de Cantón y Jorrat), tablas de la Wikipedia (`wikileg/`), fuentes de las legislativas 2003-2025 y del AGN, y los agregadores de la DINE y PolAr (`agregar_dine.py`, `agregar_polar.py`). |
| `geometria/` | Shapefiles de departamentos históricos (`Base deptos 1869-2022/`, Rodríguez, CEUR-CONICET; CC BY 2.5 AR), parroquias porteñas de 1864 a 1898 reconstruidas (`parroquias_capital_1864_1898/`), el informe de fuentes sobre los límites de 1868-1886 (`fronteras_1868_1886/`) y datos de los recuadros (`insets_data/`). |
| `logos/` | Emblemas usados y `LICENCIAS.md` con el origen y la licencia de cada uno. |
| `resultados_xlsx/` | `MASTER_resultados.xlsx` (todas las elecciones en formato largo, incluidas las transcripciones de 1912 a 1965, los atlas de 1868 a 1886 y Capital 1864-2007) y una planilla por elección en `por_eleccion/`. |
| `commons/` | Scripts y textos para Wikimedia Commons (incluido `commons_1928/`, ya subido); los paquetes se regeneran (ver abajo). |
| `analisis/` | Estudios puntuales: Cuyo 1928, fraude en San Juan, huella partidaria, cotejo con los mapas de la Wikipedia, revisión de las legislativas 2003-2025. |
| `herramientas/` | Scripts de descarga, control y preparación de datos, y un [visor de atlas para terminal](herramientas/atlas_terminal/atlas.mjs). |
| `.claude/skills/mapa-electoral-wikipedia-1999/` | Plantilla HTML del atlas, SVG base y territorios. |
| `AGENTS.md` | Flujo de trabajo detallado, reglas de estilo y trampas conocidas. **Leer antes de tocar un atlas.** |

Algunos `LEEME` y notas anteriores a la reorganización del 26-oct-2026 todavía nombran rutas viejas: `mapa<AÑO>/` es `mapas/mapa<AÑO>/`, `xlsx_resultados/` es `resultados_xlsx/`, `logos_wikipedia/` es `logos/`, `base8399/` y `wikileg/` están en `datos/`, `canton*/` y `busqueda*/` en `transcripciones/`, `Base deptos 1869-2022/` en `geometria/`, y los módulos sueltos de la raíz (`wikitop.py`, `insets99.py`…) en `comun/`.

## Instalación

```
python -m pip install -r requirements.txt
python -m playwright install chromium   # solo para PNG y paquetes de Commons
```

Python 3.11. En Windows, las capturas usan Edge sin cabeza (`msedge.exe --headless=new`).

Los scripts que consultan la API de Wikipedia o Commons mandan un User-Agent con un contacto. Definilo antes de correrlos:

```
set ATLAS_CONTACT=tu-usuario-o-correo
```

## Regenerar un atlas

```
python mapas/mapa1983/build_1983.py            # presidenciales 1983 a 2001, 2009, 2013, 2027…
python mapas/mapa2023/build_2023.py            # legislativas 2003-2025 (usa comun/atlas_leg2003_2025.py)
python transcripciones/canton5865/atlas5865.py 1962   # 1958, 1962, 1965
python comun/render_transparentes.py mapa1983    # PNG de todos los modos
python comun/render_blanco.py mapa1983 atlas_1983.html
python mapas/mapa1874/build_1874.py            # siglo XIX: 1868, 1874, 1880 y 1886 (necesitan geopandas)
python comun/exportar_xlsx.py                    # resultados_xlsx/ (transcripciones_xlsx.py agrega solo las transcripciones)
python comun/historicos_xlsx.py                  # agrega 1868-1886 y Capital 1864-2007 al MASTER y a por_eleccion/
python commons/paquete.py 1983                   # paquete para Commons en commons/1983/subir/
```

Los comandos se corren desde la raíz del repositorio. La primera corrida de cada build arma la caché `units_raw.pkl` (o `units_leg2003_2025.pkl`) desde los shapefiles; tarda unos minutos.

**Atlas que necesitan datos que no están en el repositorio:**
- **2003 a 2025, AMBA 2025, escenarios 2027 y transferencias.** Usan los resultados por mesa de la DINE. Hay que bajar los zip de «Resultados Provisionales Elecciones <año>» de datos.gob.ar a `datos_oficiales/<año>/` y correr `python datos/agregar_dine.py <año>`. Para 2003 a 2009 se usa además PolAr_Data (github.com/electorArg/PolAr_Data) en `datos_oficiales/polar/` y `python datos/agregar_polar.py`.
- **1983 a 2001.** Usan la base de Ernesto Calvo (`datos/base8399/ernesto/`), que no se redistribuye. Los atlas ya generados (`atlas_*.html` y `dataset_*.json`) sí están en el repositorio.
- **AMBA 2025 y el cruce de Capital Federal en las transferencias.** Necesitan los GeoJSON de `circuitos_electorales_AR`: definí `CIRCUITOS_AR_GEOJSON` con la carpeta `geojson`.

## Regenerar las transferencias

```
python transferencias/agregar_circuitos.py 2021 2025
python transferencias/estimar.py 2021 2025
python transferencias/sankey.py 2021 2025
python -X utf8 transferencias/auditar.py
```

Detalle de cada par, supuestos y advertencias en `transferencias/LEEME.md` y `transferencias/AUDITORIA.md`. Son estimaciones ecológicas a partir de territorios, no observaciones de voto individual.

## Fuentes

- **Dirección Nacional Electoral**: resultados provisorios por mesa 2011-2025 (datos.gob.ar) y definitivos en PDF.
- **Darío Cantón**, *Materiales para el estudio de la sociología política en la Argentina* (1968), tomos I y II: resultados por departamento de 1912 a 1965. Transcripción y correcciones propias, con página y motivo de cada corrección.
- **Darío Cantón y Jorge Raúl Jorrat**, *Elecciones en la ciudad* (t. III, 2007), CD con las planillas de la Capital de 1864 a 2007 por parroquia y circunscripción.
- **Prensa de 1868 a 1886** (*La Nación*, *La Prensa*, *Nación Argentina*, *El Nacional*): cuadros de escrutinio y actas de las juntas para los atlas del siglo XIX.
- **Ernesto Calvo**: bases por departamento y circuito, 1983-2001, y el código R de transferencias.
- **Noam Lupu y Susan Stokes**, *Argentina Ecological Dataset* (1912-2003).
- **PolAr_Data** (electorArg), a partir del Atlas Electoral de Andy Tow: 2003-2009 por mesa.
- **Honorable Cámara de Diputados de la Nación**: expedientes de elecciones de 1912 a 1922; diarios de época (*La Prensa*, *La Vanguardia*).
- **Wikipedia en español**: tablas de resultados nacionales y provinciales, agrupación en bloques y colores (CC BY-SA 4.0).
- **Rodríguez (CEUR-CONICET)**: departamentos históricos 1869-2010 (CC BY 2.5 AR, https://datosdeinvestigacion.conicet.gov.ar/handle/11336/149867). INDEC: departamentos 2022.
- **Natural Earth**: costa antártica 1:50m (dominio público).

Cada `LEEME_<AÑO>.md` detalla las fuentes, la cobertura y las decisiones de ese atlas.

## Qué no está en el repositorio

| Excluido | Motivo |
|---|---|
| `datos_oficiales/` (≈ 6 GB) | Datos públicos de la DINE y PolAr; se bajan de la fuente (ver arriba). Varios CSV superan los 100 MB. |
| `Bases Ernesto/`, `datos/base8399/ernesto/*.csv`, `datos/base8399/elecciones/`, `raw/`, `*.zip`, `*.dta`, `*.sav`, `*.mdb` | Entregas personales y bases de terceros sin permiso de redistribución documentado. |
| Logos sin licencia libre (FREJUDEPA, MOPOF, primer logo del Frente Grande, Por Santa Cruz, escenarios 2027 y AMBA 2025) | Escaneos o recortes sin licencia verificada. Los atlas que los usan se publican con el emblema embebido; ver `logos/LICENCIAS.md`. |
| Planillas originales del CD de Cantón y Jorrat (`datos/canton_ciudad/cd/`) | Material editado de terceros; en el repositorio va su lectura (`cd_largo.csv`, `cd_elecciones.json`). El build de 1880 las necesita para la Capital. |
| PDFs, escaneos y páginas de Cantón, de los expedientes de la HCDN y de los diarios | Fuentes primarias pesadas; cada LEEME indica de dónde se bajaron. |
| `*.pkl` de caché (`units_*.pkl`, `agregado*.pkl`, mesas por circuito) | Se regeneran al correr los builds. |
| PNG de los modos (`png_*`, `mapas/*/img/`) y paquetes de Commons (`commons/<año>/subir/`) | Salidas regenerables. |
| Videos (`salta_desmembramiento/`, `video_atlas*`) | Proyectos aparte, con `node_modules` y mp4 de cientos de MB. |
| Borradores de correo y transcripciones de conversaciones | Privados. |

## Licencia

- **Código**: MIT.
- **Datos, mapas y documentación propios**: CC BY 4.0.
- **Geometría**: además, cita obligatoria de la base de Rodríguez (CC BY 2.5 AR).
- **Logos**: cada uno conserva su licencia.

Detalle en [`LICENSE`](LICENSE) (MIT) y [`LICENSE-DATA.md`](LICENSE-DATA.md) (datos, excepciones y bases de terceros, que conservan sus propios términos). Para citar el proyecto: [`CITATION.cff`](CITATION.cff).

Si usás los mapas en Wikimedia Commons, llevan CC BY 4.0 más `{{Cc-by-2.5-ar}}`.
