# Diputados nacionales 2025 en el AMBA, por circuito

`python agregar.py` (ya corrido) y `python build_amba2025.py` generan `atlas_amba2025.html` y `dataset_amba2025.json`.
`build_amba2025.py` se arma con `head_amba.py` + `mid_amba.py` + `tail_amba.py` (la cola son los parches a la plantilla, copiados de `build_1994.py`); si se edita una parte hay que volver a concatenarlas.

## Datos
- **Votos**: escrutinio **provisorio** por mesa de la Dirección Nacional Electoral, `elecciones_legislativas_2025.zip` de datos.mininterior.gob.ar (en `../datos_oficiales/2025/`, 13,5 MB el zip, 457 MB el CSV `resultados2025.csv`). Se filtró `DIPUTADO NACIONAL` de Capital y Buenos Aires y se agregó por circuito. El mismo portal publica 2011 a 2023 (PASO, generales y ballotage): `datos.gob.ar`, buscar «Resultados Provisionales Elecciones <año>» (2017 incluido).
- **No es el escrutinio definitivo**: 360 de 35.868 mesas figuran sin escrutar (44 en Capital, 316 en Buenos Aires). Esas mesas no suman votos ni electores (la participación se calcula sobre las mesas escrutadas).
- **padron.gob.ar/publica** (escrutinio definitivo) exige un captcha en cada consulta; no se automatiza ni se saltea. Para cerrar esos huecos hay que pedir el definitivo a la Cámara Nacional Electoral o a la Junta Electoral bonaerense, o consultar a mano los circuitos que más pesen.
- **AMBA** = Capital + 24 partidos del GBA + 16 (Berisso, Brandsen, Campana, Cañuelas, Ensenada, Escobar, Exaltación de la Cruz, Gral. Las Heras, Gral. Rodríguez, La Plata, Luján, Marcos Paz, Pilar, Presidente Perón, San Vicente, Zárate). Total: 8.179.068 votos positivos.
- Bloques: FP (Alianza Fuerza Patria), LLA, FIT-U, PU (Alianza Provincias Unidas en Buenos Aires; **Ciudadanos Unidos** en Capital, es la lista de Provincias Unidas). Solo FP y LLA ganan circuitos; FIT y PU están en la leyenda porque así era el mapa original del usuario, aunque la regla 3 diría solo ganadores.

## Geometría
- Circuitos CNE/INDEC de 2021 (`<disco externo>/REGIONES/circuitos_electorales_AR-main\geojson`: `CABA.geojson` 167 y `PBA.geojson` 1.066). Clave `(coddepto, circuito)`; Capital usa solo el circuito.
- La base de 2025 subdivide circuitos con letras (`0364A`...): se suman en el polígono del circuito de origen (184 circuitos de la base). 1 circuito (Gral. Las Heras, 045/00548, 935 votos) no está en la capa de polígonos: se dibuja el hueco que dejan sus vecinos de la sección (inferido, con nota en la ficha).
- 7 polígonos del AMBA no tienen mesas en la base (deltas, zonas despobladas): beige con leyenda.

## Logos
Wikipedia 2025: `Homeland_Force_logo.png` (Fuerza Patria), `Logo_La_Libertad_Avanza_sin_aguila.svg` (versión en blanco `..._blanco.svg` para el fondo violeta), `Logo_FIT_Unidad.svg`, `Logo_Provincias_Unidas.svg`. Todos de dominio público según Commons/es-Wikipedia.

## Pendiente
- Definitivo para las mesas sin escrutar.
- Verificar si los 7 polígonos beige son circuitos realmente sin electores.

## Huecos blancos
Quedan 3 huecos chicos (entre Almirante Brown, Lomas de Zamora y Quilmes; en Berazategui; entre San Isidro y Vicente López): zonas que la capa de circuitos de la CNE no cubre (ningún polígono ajeno cae adentro). Probablemente predios sin electores; no se identificó cuáles.
