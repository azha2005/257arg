# Diputados nacionales 2025 en el AMBA, por radio censal 2022

Estimación de los votos de cada radio censal con el método de Poblaciones / LN Data. Es el mismo atlas que `../mapaAMBA2025/` (por circuito) cambiando la unidad. **El voto no se registra por radio**: cada valor del mapa es una estimación, y solo los totales por partido (y comuna) son exactos.

## Cómo se regenera
```
python mapas/mapaAMBA2025radios/geocodificar.py        # una vez: ubica los locales (consulta georef; cache en georef_cache.json)
"<venv de Mosaic>/python.exe" mapas/mapaAMBA2025radios/radios_amba.py   # una vez: radios del AMBA (necesita geopandas)
python mapas/mapaAMBA2025radios/asignar.py             # reparto -> asignacion_idw.pkl y asignacion_pob.pkl
python mapas/mapaAMBA2025radios/build_amba2025radios.py        # atlas_amba2025radios.html      (Poblaciones)
python mapas/mapaAMBA2025radios/build_amba2025radios.py pob    # atlas_amba2025radios_pob.html  (variante por población)
python mapas/mapaAMBA2025radios/diagnostico.py         # controles -> diagnostico.json
python comun/render_transparentes.py mapaAMBA2025radios
python comun/render_blanco.py mapaAMBA2025radios atlas_amba2025radios.html   # y el _pob
```
El constructor toma la parte del medio y la cola de `../mapaAMBA2025/` (`mid_amba.py`, `tail_amba.py`) y les aplica reemplazos (`load_part` exige que cada texto aparezca una sola vez). Si se cambia el atlas por circuito, este lo sigue; si un reemplazo falla, cambió el texto de origen.

## Datos
- **Votos**: escrutinio provisorio por mesa de la DINE (`datos_oficiales/2025/elecciones_legislativas_2025.zip`), los mismos 35.868 mesas y 8.179.068 votos positivos del atlas por circuito (`../mapaAMBA2025/dip_amba_mesas.pkl`). Las 360 mesas sin escrutar no aportan votos.
- **Local de cada mesa**: `localesDeVotacionyMesas.csv` del mismo zip (código, nombre, dirección y localidad del local; **las columnas de latitud y longitud vienen vacías**). En el AMBA hay 5.487 locales. El CSV está en UTF-8.
- **Radios**: `geometria/cartografia_argentina/conicet/radios/RADIOS_2022_V2025-1.zip` (CONICET, censo 2022, `POB_TOT_P`). AMBA = Capital (3.820 radios) + los 40 partidos del atlas por circuito: 18.101 radios y 16.384.621 habitantes. Los códigos INDEC de los partidos salen de georef (`depto_pba_georef.json`).
- **Circuitos** (solo para validar los puntos y para la variante por población): la capa 2021 de circuitos_electorales_AR (`geometria/circuitos_busqueda/galeano_snapshot_2021/geojson`), con los circuitos que la base subdivide con letras juntos en el polígono de origen, como en el atlas por circuito.

> Los GeoJSON crudos de escuelas no están en el repo (traen teléfonos y correos institucionales). Para regenerar: bajar `establecimientos-educativos-26102026.zip` de catalogo.datos.gba.gob.ar (descomprimir el `.geojson` en `datos/escuelas/pba/`) y `establecimientos_educativos_WGS84.geojson` de cdn.buenosaires.gob.ar/datosabiertos (en `datos/escuelas/caba/`).

## Ubicación de los locales (`geocodificar.py`, `escuelas.py` → `locales_amba2025.csv`)
Igual que LN Data, se ubica cada local con un padrón de escuelas con coordenadas:
- **Provincia**: `datos/escuelas/pba/establecimientos-educativos-26102026.geojson` (DGCyE, catalogo.datos.gba.gob.ar, 21.592 establecimientos).
- **Ciudad**: `datos/escuelas/caba/establecimientos_educativos_WGS84.geojson` (Ministerio de Educación GCBA, cdn.buenosaires.gob.ar/datosabiertos, 2.828).

El emparejamiento se hace dentro del mismo partido (o comuna) por dirección (calle en común y altura a menos de 30), por tipo y número de escuela (EP 39, ES 25, EST 3, JI 912, EE 531) o por nombre muy parecido. Si no hay escuela, se usan los puntos de establecimientos de La Nación 2021 (`establecimientos-ln.geojson`, emparejados por nombre y dirección) y georef (apis.datos.gob.ar, la API oficial de normalización de direcciones). **Todo punto se valida contra el circuito de sus mesas**: se toma el primero que cae a menos de 300 m del circuito y, si ninguno, el primero dentro del partido y a menos de 1,5 km (sufijo `_cerca` en la columna `fuente`; la capa de circuitos es de 2021 y en algunos lugares está corrida).

| fuente | locales | % de electores |
|---|---|---|
| escuela (dirección, código o nombre) | 4.872 | 89,5 % |
| La Nación 2021 | 161 | 3,1 % |
| georef | 287 | 4,7 % |
| centro del circuito (sin punto válido) | 167 | 2,7 % |

Los 167 locales sin punto válido (clubes, facultades, sociedades de fomento, el Barrio 31; 35 en Almirante Brown y 23 en La Plata) van al punto interior de su circuito. El 548 de Gral. Las Heras no tiene polígono: su escuela se acepta con estar dentro del partido.

## Reparto (`asignar.py`)
- **Variante Poblaciones (`idw`, la principal por decisión del usuario del 31-oct-2026)**: cada local reparte sus votos entre todos los radios de su partido (comuna en Capital) con peso 1/d², donde d es la distancia al centroide del radio, con un piso de 25 m (sin piso, el radio que contiene la escuela se llevaba casi todo). Los votos nunca cruzan el límite del partido o la comuna. Los radios que suman menos de 1 voto quedan en 0 y su parte vuelve, en proporción, a los demás radios del local (con esto los totales por partido cierran). La descripción viene de la metodología de Poblaciones para su mapa presidencial de 2023 (obra 263401, De Grande, Correa y Bouret, CC BY 4.0). No se pudo leer el PDF, así que el piso de distancia y la renormalización son decisiones propias.
- **Variante por población (`pob`)**: peso POB_TOT_P / d², solo entre los radios del circuito de las mesas (el radio va al circuito que contiene su punto interior). La IDW pura ignora cuánta gente vive en cada radio; esta no, pero dibuja los límites de circuito por construcción.
- Se reparten todas las categorías con el mismo peso: listas, blancos, nulos, impugnados y electores de las mesas escrutadas (de ahí la participación estimada).

## Controles
- **Totales**: la suma de los radios por partido y categoría coincide con la DINE (error máximo 1e-11 en `idw` y 2e-12 en `pob`; `assert` en `asignar.py`).
- **Radios sin votos**: 1 en `idw` (2 habitantes) y 414 en `pob` (200.198 habitantes: radios cuyo punto interior cae fuera de los circuitos con mesas, más los que quedaron por debajo de 1 voto). Van en beige.
- **Ganadores**: en `idw`, LLA 9.224 radios y FP 8.876; en `pob`, LLA 9.163 y FP 8.516. FIT y PU no ganan ninguno y quedan fuera de la leyenda (regla 3), pero el modo FIT sigue.
- **¿Los cambios de color siguen los circuitos?** (`diagnostico.json`, pares de radios vecinos dentro del mismo partido): en `idw` el 25,6 % de los cambios de ganador cae sobre un límite de circuito, contra el 17,1 % de todos los pares. Es un exceso leve: el método no usa circuitos, y estos siguen barrios reales. En `pob` cae ahí el 69,2 %, por construcción. **Los cortes netos del mapa `idw` son los límites de partido**, que el método no cruza.

## Estilo
- Colores y logos del atlas legislativo 2025 (paleta de los mapas presidenciales de la Wikipedia): LLA #6c4c98 con el bloque del león, Fuerza Patria #009ce4 con `Logo_de_Fuerza_Patria.svg` en blanco, PU #FF682C y FIT #f65058 con sigla. El atlas por circuito (`mapaAMBA2025`) conserva sus colores y logos anteriores.
- **Degradado del modo «Ganó» más fino** (pedido del usuario): cortes en 42, 45, 47, 50, 55 y 60 %, porque por radio el ganador saca entre 41 y 58 % en el 90 % de los casos. FP % y LLA %: cortes en 25, 32, 38, 44, 50 y 56.
- Bordes de radio de 0,3 px (con 1,5 px el conurbano quedaba blanco). **Comunas de Capital como divisores**, con el mismo trazo que los partidos (pedido del usuario).
- Los modos de coropleta no repiten las fichas de los radios: el navegador las copia del modo «Ganó» (si no, el HTML pesaba 80 MB; así pesa 17).

## Pendiente
- Revisar a mano los 167 locales sin punto válido (`fuente = centro_circuito`), sobre todo Almirante Brown y La Plata.
- No va a Commons salvo pedido.

## Para Twitter
`python exportar_tw.py` renderiza el mismo póster (modo «Ganó») a 4021×3453 px (Twitter acepta hasta 4096 por lado) y los otros cuatro modos para la respuesta, en `tw/`. Se guardan como PNG de paleta de 256 colores (1,5 a 1,7 MB): por encima de 5 MB Twitter los pasa a JPEG y se manchan los bordes finos. En la exportación el borde de los radios baja a 0,18 px. Se probó un acercamiento al conurbano y otro encuadre: el usuario prefirió el diseño del póster.
