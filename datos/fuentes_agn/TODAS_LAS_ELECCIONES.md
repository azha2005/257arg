# Todas las elecciones nacionales hasta 1983: atlas y dónde están los datos (5-nov-2026)

Pedido del usuario: todos los años y todas las elecciones. De 1983 en adelante hay atlas de todas; los huecos que quedan están en sus LEEME.

Siglas:
- **DNE**: fondo DNE01, inventario `inventario_DNE01_De.csv`, digitalizado.
- **Lote**: AGN DNE01 1908–1925, `inventario_provisorio_1908_1925.csv`.
- **Eg1**: Ministerio del Interior, Expedientes Generales 1 (AR-AGN-MI01-Eg1), en papel (solo el inventario está digitalizado, mail del 5-nov), con inventario analítico de 1867, 1868, 1908, 1931–1941 y 1942–1946.
- **Padrón**: Ministerio del Interior, Oficina de Padrón Electoral, 1870–1935, sin inventario.
- **HCDN**: expedientes de diplomas (`apym.hcdn.gob.ar/uploads/expedientes/pdf/<n>-d-<año>.pdf`).
- **DS**: Diario de Sesiones de Diputados, tomo de sesiones preparatorias (en la biblioteca DNE, `biblioteca_DNE01_Bi.csv`, o en la Biblioteca del Congreso).
- **Memoria**: Memoria del Ministerio del Interior (Academia Nacional de la Historia, Wikisource/Commons).
- **Cantón**: tomo II por departamento.
- **LS**: Lupu y Stokes.

| Elección | Atlas | Qué falta | Dónde buscar |
|---|---|---|---|
| Diputados y electores de 1854 a 1902 | — | todo | Eg1 (inventario de 1867 y 1868), Padrón, Memorias (escaneadas de 1870, 1872, 1893, 1894…), HCDN si hay diplomas, lote (Buenos Aires 1880–1885, «Legajo VS» 1894–1925) |
| Diputados 1904 | `mapa1904` | Catamarca 2; padrón y participación | HCDN (ya se usó), Memoria 1904, Padrón |
| Diputados 1906 | — | todo | HCDN `n-d-1906`, Memoria, Padrón |
| Presidente 1904 (electores) | — | todo | HCDN o actas de la Asamblea, Memoria |
| Diputados 1908 | — | todo | **lote** (Buenos Aires, Córdoba, Entre Ríos, Salta), **Eg1 (inventario de 1908)**, HCDN, Memoria |
| Diputados y presidente 1910 | — | todo | **lote** (Córdoba, Salta, Tucumán, Buenos Aires, La Rioja; registros de 1909 de Santa Fe, San Luis, Corrientes y Tucumán), HCDN, Memoria |
| Diputados 1912 | `mapa1912` | Santa Fe 14/19; 11 provincias en color sólido | **lote** (Santa Fe, La Rioja, San Luis, Tucumán), HCDN, Padrón |
| Complementarias 1913 | — | todo | **lote** (Santiago del Estero con boletas, Mendoza), HCDN |
| Diputados 1914 | `mapa1914` | Santa Fe 5; 6 provincias en color sólido | lote (La Rioja y Mendoza; Santa Fe sin rótulo), HCDN |
| Diputados 1916 | `mapa1916dip` | San Juan (salvo Capital) y Santiago del Estero | lote (Santiago del Estero sin rótulo), HCDN, DS 1916 t. I (biblioteca DNE n.º 356) |
| Presidente 1916 | — (solo `mapa1916fic`) | atlas real | Cantón t. II, Memoria, HCDN |
| Diputados 1918 | `mapa1918` | inscriptos de Vélez Sarsfield; Balcarce 144/174 | lote («Legajo VS»?), HCDN, Padrón |
| Diputados 1920 | `mapa1920` | Jujuy por identidad de listas | **lote** (Santiago del Estero 24: remisión de actas; Santa Fe), HCDN |
| Presidente y diputados 1922 | `mapa1922` | Santiago del Estero y Mendoza sin departamentos; La Rioja con 4 unidades; inscriptos reconstruidos por Cantón | **lote** (Santiago del Estero 3, 8, 13, 33 y 39; Santa Fe 13), HCDN, Padrón |
| Diputados 1924 | — | todo | **Memoria 1924–1925 (Wikisource)**, lote (¿Santa Fe 1925?), HCDN |
| Diputados 1926 | `mapa1926` | Alberdi (Santiago del Estero) sin polígono | lote (¿Santa Fe 1925?) para cotejo |
| Presidente y diputados 1928 | `mapa1928` | Balvanera Norte, votantes | Cantón y Jorrat, HCDN, DS 1928 t. I (biblioteca DNE n.º 571) |
| Diputados 1930 | `mapa1930` | San Carlos Norte, PSI | Cantón y Jorrat, HCDN |
| Presidente y diputados 1931 | — | todo | **Eg1 (1931–1941)**, HCDN (Mendoza y La Rioja por mesa, ver `transcripciones/1931/`), DS 1932 (biblioteca DNE n.º 191) |
| Complementarias 1932 | — | todo | Eg1, HCDN `n-ov-1932`, DNE (provinciales de 1932) |
| Diputados 1934 | — | todo | **Eg1**, HCDN, DS 1934 t. I (biblioteca DNE n.º 825), DNE (provinciales de 1934) |
| Diputados 1936 | — | todo | **Eg1**, HCDN, DS 1936 (Congreso) |
| Presidente 1937 | `mapa1937` | todo salvo 4 provincias | **Eg1**, DNE (provinciales de 1937), HCDN o Asamblea |
| Diputados 1938 | — | todo | **Eg1**, DNE 46_091_23a102, HCDN (24-D-1938: Buenos Aires), Memoria 1938 |
| Diputados 1940 | `mapa1940` | todo salvo 5 distritos | **DNE 46_091_144a218 (resultados)** y 219a313, Eg1 |
| Diputados 1942 | — | todo | **Eg1 (1942–1946)**, DNE 47_092, HCDN |
| Presidente y diputados 1946 | `mapa1946` | cotejo | DNE (17 carpetas), Eg1 (1942–1946), Series Históricas MI «Elecciones Nacionales de 1946» |
| Diputados y constituyentes 1948 | `mapa1948`, `mapa1948c` | «otros» estimados; 23 partidos de Buenos Aires y otros en beige; Córdoba, Corrientes y Mendoza en color sólido (1948c) | **DNE** (15 distritos, 1.155 folios) |
| Presidente y diputados 1951 | `mapa1951` (por circunscripción) | atlas departamental | DNE (27 carpetas) |
| Complementarias 1953 | — | todo | DNE (resultados de 1953) |
| Vicepresidente y diputados 1954 | `mapa1954` | cotejo | DNE (29 carpetas) |
| Constituyentes 1957 | — | todo | **DNE (30 carpetas, 1.515 folios)**, Zalduendo 1958 |
| Presidente y diputados 1958 | `mapa1958` | Corrientes y Río Negro en color sólido | **DNE** (18_035_269a328, 19_037_238a267) |
| Diputados 1960 | — | todo | **DNE (21 carpetas, 1.087 folios)** |
| Complementarias 1961 | — | todo | DNE (2 carpetas), lote («Panorama 1961») |
| Diputados 1962 | `mapa1962` | Santiago del Estero en color sólido | **DNE** (29_056_246a273 y 200a202) |
| Presidente y diputados 1963 | — | todo | **DNE (28 carpetas, 1.237 folios)** |
| Diputados 1965 | `mapa1965` | La Rioja 11/18 y Catamarca 5/16 (no votaron todos) | DNE para cotejo |
| Presidente marzo 1973 | `mapa1973` | «otros» estimados; GBA, circunscripción 21, Entre Ríos y Tierra del Fuego | **DNE (48 carpetas, 2.475 folios)** |
| Diputados marzo 1973 | — | todo | **DNE** (mismas carpetas) |
| Presidente septiembre 1973 | `mapa1973s` | ídem | DNE |
| Diputados, constituyentes y presidente desde 1983 | todos | ver cada LEEME | DINE, CNE |

## Geometría
En `geometria/Base deptos 1869-2022/` están los departamentos de los censos de 1869 (291 unidades) y 1895 (424). Uso:
- 1854–1866: la de 1869, como aproximación.
- 1868–1890: la de 1869.
- 1892–1910: la de 1895.
- 1912–1930: la de 1914.

## Elecciones provinciales y municipales
El fondo DNE tiene provinciales de casi todos los años entre 1932 y 1987: unas 400 carpetas, sobre todo de 1946 a 1973. Hoy no hay atlas provinciales anteriores a 2023. Es una línea entera nueva. Copiarlas con el disco junto con las nacionales.

## Qué pedir y qué hacer, en orden
1. Por mail: el enlace de las dos muestras y **los inventarios analíticos de Eg1** (1867, 1868, 1908, 1931–1941 y 1942–1946). Preguntar si el lote 1908–1925 está digitalizado.
2. En la visita, con un disco de 1 o 2 TB: el fondo DNE entero (las cinco series), las partes de Eg1 que salgan del inventario y fotos del lote 1908–1925 (ver `PLAN_VISITA.md`).
3. Desde la PC, de a uno: sondeo de expedientes de la HCDN para cada año de 1904 a 1942, como el de `transcripciones/1931/`.
4. En Wikisource y Commons, todas las Memorias del Interior que haya: 1870–1894 y 1924–1928 ya aparecen; buscar las de 1904 a 1943.
5. Bibliotecas: Cantón y Jorrat para Capital en todos los años; tomos de sesiones preparatorias en el Congreso; tesis de Ferrari; hemerotecas para lo que falte.
