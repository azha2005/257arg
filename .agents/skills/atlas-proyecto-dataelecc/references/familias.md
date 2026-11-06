# Familias de atlas: qué copiar y cómo se valida

Cada familia tiene su constructor compartido. Un atlas nuevo de esa época se agrega al constructor (una clave nueva y sus datos), no se escribe un build desde cero. Las rutas son desde la raíz.

## Entreguerras, 1912-1940 (1918, 1920, 1926, 1936, 1937, 1940)

- `transcripciones/entreguerras/construir.py <año>`; datos en `datos.py` (cartel nacional, `NATIONAL`) y `atlas_datos.py` (`prepare`). `mapas/mapa<año>/build_<año>.py` solo lo llama con `runpy`. Para un año nuevo: agregarlo al `assert Y in (...)`, a `datos.py` y a `atlas_datos.py`.
- Dibujo de la familia publicada 1922/1928 (constructor 1930): proyección de 1912-1930, `Departamentos_1914`, las veinte circunscripciones históricas de Capital, recuadros de 1916-1930 (sin Antártida), logos **centrados con zoom**. No se ejecuta ni modifica el constructor de 1922/1928/1930.
- Fuentes: Cantón transcripto (`manual<año>.txt`, `canton_<año>.json/csv`), expedientes de la Cámara (1936: `transcripciones/1936/`), Lupu-Stokes solo como cotejo (`cotejo1926.py`), nunca como reemplazo de la imagen.
- Provincias sin tabla: `DATA.solid` con el total de la Wikipedia (1936) o beige si Cantón no la publica (1937, 1940). Fila compartida por varios polígonos: nota, se suma una vez.
- Reservas de época (prensa citada en el propio libro, fechas dudosas) se conservan en nota, fichas y CSV con `reserva_cronologica`; no se trasladan datos a otro año sin cotejo primario.
- Validar: `python transcripciones/entreguerras/verificar.py` (números, navegación y exportaciones en navegador). Controles en `CONTROL_<año>.json`.
- UCR: bandera bicolor hasta 1930, escudo desde 1931.

## Peronismo y proscripción, 1946-1973

- `python transcripciones/peronismo/atlas4673.py <clave>` (`1946`, `1948`, `1948c`, `1954`, `1973`, `1973s`); lectores en `fuentes4673.py`, pensado para cambiar a datos del AGN agregando un lector.
- Buenos Aires con el shp de partidos de 1955 (`geometria/shapefile1955/shapefile1955_corregido/`). Topline con claves de texto en `wikitop.py`.
- Lo repartido desde «otros» de Lupu-Stokes se rotula «(est.)».
- AGN: una planilla nueva va a `PLANILLAS` en `transcripciones/agn_dne/agn.py` (ejemplo: Santiago del Estero 1962).

## Cantón 1958-1965

- `python transcripciones/canton5865/atlas5865.py <año>`; correcciones con página y motivo en `correcciones.py`, sospechas en `sospechas.py`. Geometría `Departamentos_1960` + secciones de Capital (`geom60.py`).

## 1983-2001

- Presidente: `mapas/mapa<año>/build_<año>.py` (1983, 1989, 1995 con variante `union`, 1999). Diputados: `comun/atlas_leg8399.py` (1983, 1989, 1995, 1999) o builds propios (1985, 1987, 1991, 1993, 1997, 2001).
- Base de Ernesto (`datos/base8399/ernesto/<año>_<cargo>/dpto_partidos.csv`), completada con Lupu-Stokes y la base del INAP (`datos/base8399/inap/`). Revisar duplicados de filas de métricas y padrones con más votantes que inscriptos (gris claro en participación, nota en la ficha).
- Departamentos de 1980 hasta 1989, de 1991 desde 1991, con `newpartidos.apply(...)` para los partidos nuevos. Recuadros con `comun/insets99.py` (`style95=True`).
- Casi todos ya están en Commons: no regenerar sin pedido.

## 2003-2025: diputados, PASO, presidente y balotaje

- Un solo constructor: `python comun/atlas_leg2003_2025.py <clave>`. Claves: `<año>` (diputados), `<año>paso` (PASO presidencial o de diputados en años legislativos), `<año>pasodip`, `<año>pres`, `<año>bal`. Los `build_<clave>.py` de cada carpeta solo lo llaman.
- Datos: `comun/leg2003_2025_data.py` (PolAr 2003-2009, DINE provisorio por mesa 2011-2025), `comun/paso_data.py` + `paso_bloques.py`, `comun/pres2003_2023_data.py`. Complementos con fuente y página en `datos/fuentes_leg2003_2025/` (`complementos_departamentales.json`, `presidenciales/complementos.json`, `padron_publica/`).
- Leyenda de `comun/leyenda_clara.js` (barras macizas, `LEG_SZ(n)` según filas, `LOGO_ESTILO` para pasar logos a blanco), bloques de los mapas presidenciales de Commons en `comun/bloques_wiki.py`.
- **Presidenciales y balotajes heredan logos, posición, marco y zoom de su atlas por radio**; 2003 copia exactamente los del AMBA 2003 por radio. No aplicarles otra vez `logos_al_ras.py`.
- Validar: `python herramientas/validar_render_leg2003_2025.py <clave>` y, para los presidenciales, `python herramientas/validar_pres2003_2023.py --render`.

## Por circunscripción desde un SVG (1904, 1951)

- `mapas/mapa1904/geometria_1904.py` adapta el SVG de Commons al contorno del SHP histórico y a nuestra proyección (caché con hash de SVG, código y SHP). 1951 copia el método (`geometria_1951.py`).
- **Por circunscripción, no por municipio**: no repartir votos. Capital con las circunscripciones del SHP histórico, trazo nativo de alta resolución. Malvinas del SHP en gris, también en el mini de provincias.
- Uninominal: «Ganó» por candidato; torta y barras por afiliación partidaria cercana, con cobertura parcial explícita.
- Puntos (bancas de minoría 1951): radio limitado que crece suave con el zoom, `min(3.2, 1 + 0.6*log2(zoom))`, borde fino, visibles en Capital.
- Créditos al autor del SVG en las fuentes (Faustino Sojo). Validar con `verificar_<año>.py`.

## AMBA y PBA por circuito o radio censal

- Método de Poblaciones/LN Data: votos por local de votación, local geolocalizado (padrones de escuelas DGCyE/GCBA, LN 2021, georef), reparto 1/d² a los centroides de los radios del mismo partido o comuna. Totales por partido exactos.
- Sin tabla mesa → local (antes de 2025): cada circuito se reparte entre las escuelas de 2025 que caen dentro, según sus electores (AMBA 2003, serie 2005-2023). Decirlo siempre: es estimación.
- Selector «Nivel: Partido / Circuito / Radio»: partido = suma de radios; circuito = votos observados; zonas sin circuito beige.
- Serie: `python mapas/serieAMBA2005_2023radios/construir.py [clave] [--sin-preparar] [--sin-png]`; AMBA 2025: `build_amba2025radios.py [idw|pob]`; PBA septiembre 2025: `mapas/mapaPBA2025sep/`.
- Logos de la serie: `logos_serie.py`, auditoría en `AUDITORIA_LOGOS.json`. Los de radios 2025 (Fuerza Patria con franjas blancas, LLA con el bloque del águila) son el modelo que el usuario prefiere.
- geopandas está en el `.venv` de Mosaic (`C:\Users\JC\Desktop\Escritorio 26\mosaic_python-main`), no en el Python del sistema.

## Escenarios hipotéticos y ucronías

- Copiar el build real del año y reemplazar los votos por un ajuste IPF a los totales pedidos, conservando los positivos locales; el resto proporcional entre las demás fuerzas. Control en `control.json`, método en el LEEME.
- Si la imagen del usuario da ganadores provinciales, el ajuste los respeta (freno provincial, 2023massa). Ganadores locales legibles de una imagen se conservan; lo ilegible queda beige (2003alt).
- **Votos enteros** con redondeo controlado (`analisis/remake2003/enteros.py`): totales nacionales exactos y mismos ganadores.
- Créditos del autor original en datos, fuentes y barra: `comun/creditos_escenarios.py`.
- Subtítulo «Hipotético · …» o «Ucronía · …». No van a Commons.
