# Atlas electorales argentinos por departamento

Mapas de resultados electorales de la Argentina por departamento (y por circunscripción en Capital Federal), de 1912 a 2025, en el estilo del mapa de la Wikipedia de las presidenciales de 1999. Incluye además:

- una planilla con todos los resultados por departamento que reúne el proyecto;
- estimaciones de transferencias de voto entre elecciones por inferencia ecológica, con diagramas de Sankey;
- los paquetes para subir los mapas a Wikimedia Commons.

Cada atlas es un HTML autocontenido con pestañas por modo (ganador, porcentaje de cada fuerza, participación), descripción de cada unidad al pasar el mouse y descarga en SVG y PNG.

## Estructura

| Ruta | Qué hay |
|---|---|
| `mapas/mapa<AÑO>/` | Un atlas por elección: `build_<AÑO>.py`, `atlas_<AÑO>.html`, `dataset_<AÑO>.json` y `LEEME_<AÑO>.md` (fuentes, decisiones, pendientes). Sufijos: `dip` diputados, `fic` ficticio, `hip` hipotético, `kic` escenario 2027 Kicillof–Milei. |
| `comun/` | Código compartido por los atlas: constructores de las legislativas (`atlas_leg8399.py`, `atlas_leg2003_2025.py`), totales de Wikipedia (`wikitop.py`, `bloques_wiki.py`), recuadros (`insets99.py`), partidos nuevos (`newpartidos.py`), limpieza del contorno (`outline_clean.py`), renderizado a PNG y exportación a xlsx. |
| `transcripciones/` | Transcripciones propias por departamento: Cantón (`canton5865/` con el constructor de 1958, 1962 y 1965; `canton1937_1940/`, `canton1946/`, `canton1954/`…), expedientes y prensa de 1912, 1914 y 1916 (`busqueda1912/`, `busqueda1914/`, `1916dip/`) y Mendoza 1922 (`mdz22/`). |
| `transferencias/` | Inferencia ecológica RxC (port a Python del código R de E. Calvo), matrices, bootstrap, auditorías y Sankeys. Ver `transferencias/LEEME.md`. |
| `datos/` | Bases de terceros ya preparadas (`base8399/`, `preparados/`), tablas de la Wikipedia (`wikileg/`), fuentes de las legislativas 2003–2025 y del AGN, y los agregadores de la DINE y PolAr (`agregar_dine.py`, `agregar_polar.py`). |
| `geometria/` | Shapefiles de departamentos históricos (`Base deptos 1869-2022/`, Rodríguez, CEUR-CONICET; CC BY 2.5 AR) y datos de los recuadros (`insets_data/`). |
| `logos/` | Emblemas usados y `LICENCIAS.md` con el origen y la licencia de cada uno. |
| `resultados_xlsx/` | `MASTER_resultados.xlsx` (todas las elecciones en formato largo, incluidas las transcripciones de 1912 a 1965) y una planilla por elección. |
| `commons/` | Scripts y textos para Wikimedia Commons (incluido `commons_1928/`, ya subido); los paquetes se regeneran (ver abajo). |
| `analisis/` | Estudios puntuales: Cuyo 1928, fraude en San Juan, huella partidaria, cotejo con los mapas de la Wikipedia, revisión de las legislativas 2003–2025. |
| `herramientas/` | Scripts de una sola vez (descargas, controles, preparación de datos) que quedaron como registro. |
| `.claude/skills/mapa-electoral-wikipedia-1999/` | Plantilla HTML del atlas, SVG base y territorios. |
| `AGENTS.md` | Flujo de trabajo detallado, reglas de estilo y trampas conocidas. **Leer antes de tocar un atlas.** |

Los `LEEME` de cada carpeta se escribieron antes de esta organización y pueden nombrar rutas viejas: `mapa<AÑO>/` es ahora `mapas/mapa<AÑO>/`, `xlsx_resultados/` es `resultados_xlsx/`, `logos_wikipedia/` es `logos/`, `base8399/` y `wikileg/` están en `datos/`, `canton*/` y `busqueda*/` en `transcripciones/`, `Base deptos 1869-2022/` en `geometria/`, y los módulos sueltos de la raíz (`wikitop.py`, `insets99.py`…) en `comun/`.

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
python mapas/mapa2023/build_2023.py            # legislativas 2003–2025 (usa comun/atlas_leg2003_2025.py)
python transcripciones/canton5865/atlas5865.py 1962   # 1958, 1962, 1965
python comun/render_transparentes.py mapa1983    # PNG de todos los modos
python comun/render_blanco.py mapa1983 atlas_1983.html
python comun/exportar_xlsx.py                    # resultados_xlsx/ (transcripciones_xlsx.py agrega solo las transcripciones)
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

- **Dirección Nacional Electoral**: resultados provisorios por mesa 2011–2025 (datos.gob.ar) y definitivos en PDF.
- **Darío Cantón**, *Materiales para el estudio de la sociología política en la Argentina* (1968), tomos I y II: resultados por departamento de 1912 a 1965. Transcripción y correcciones propias, con página y motivo de cada corrección.
- **Ernesto Calvo**: bases por departamento y circuito, 1983–2001, y el código R de transferencias.
- **Noam Lupu y Susan Stokes**, *Argentina Ecological Dataset* (1912–2003).
- **PolAr_Data** (electorArg), a partir del Atlas Electoral de Andy Tow: 2003–2009 por mesa.
- **Honorable Cámara de Diputados de la Nación**: expedientes de elecciones de 1912 a 1922; diarios de época (*La Prensa*, *La Vanguardia*).
- **Wikipedia en español**: tablas de resultados nacionales y provinciales, agrupación en bloques y colores (CC BY-SA 4.0).
- **Rodríguez (CEUR-CONICET)**: departamentos históricos 1869–2010 (CC BY 2.5 AR, https://datosdeinvestigacion.conicet.gov.ar/handle/11336/149867). INDEC: departamentos 2022.
- **Natural Earth**: costa antártica 1:50m (dominio público).

Cada `LEEME_<AÑO>.md` detalla las fuentes, la cobertura y las decisiones de ese atlas.

## Qué no está en el repositorio

| Excluido | Motivo |
|---|---|
| `datos_oficiales/` (≈ 6 GB) | Datos públicos de la DINE y PolAr; se bajan de la fuente (ver arriba). Varios CSV superan los 100 MB. |
| `Bases Ernesto/`, `datos/base8399/ernesto/*.csv`, `datos/base8399/elecciones/`, `raw/`, `*.zip`, `*.dta`, `*.sav`, `*.mdb` | Entregas personales y bases de terceros sin permiso de redistribución documentado. |
| Logos sin licencia libre (FREJUDEPA, MOPOF, primer logo del Frente Grande, Por Santa Cruz, escenarios 2027 y AMBA 2025) | Escaneos o recortes sin licencia verificada. Los atlas que los usan se publican con el emblema embebido; ver `logos/LICENCIAS.md`. |
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

Detalle en [`LICENSE`](LICENSE).

Si usás los mapas en Wikimedia Commons, llevan CC BY 4.0 más `{{Cc-by-2.5-ar}}`.
