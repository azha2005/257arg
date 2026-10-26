# Cantón 1958, 1962 y 1965: revisión de la transcripción y atlas

Fuente: D. Cantón, *Materiales para el estudio de la sociología política en la Argentina* (1968), t. II. Las páginas
transcriptas están en `scratch/transcripcion/p_*.json` (imágenes en `scratch/canton_pages/p_NNN.png`).

| Archivo | Qué hace |
|---|---|
| `cargar.py` | lee los JSON → `T[(año, cargo, provincia, categoría)]` (V varones, M mujeres, T total) |
| `sospechas.py` | controles: suma de partidos + blancos + anulados = votantes, votantes ≤ inscriptos, V + M = T (1958) |
| `correcciones.py` | **cada corrección con su página y su motivo**; `aplicar()` falla si el valor transcripto no es el esperado. `IMPUTA`: celdas que faltan en la página |
| `mapeo.py` | partido de Cantón → fila de la tabla de Wikipedia → bloque del atlas |
| `cotejo_wiki.py` | suma Cantón por provincia y fila y la compara con las tablas provinciales de Wikipedia (1962, 1965) |
| `datos.py` | unidades listas para el atlas (Cantón corregido + bloques) y ganador por unidad |
| `geom60.py` | geometría: Departamentos_1960 + secciones de Capital + polígonos tomados de 1970 y 1947 |
| `atlas5865.py <año>` | construye `mapa<año>/atlas_<año>.html` |
| `exportar_xlsx.py` | `xlsx_resultados/por_eleccion/*canton*` con las correcciones aplicadas (hojas `bloques` y `correcciones`) |
| `zoom.py`, `capturas.sh` | recorte de filas de una página; capturas de los modos con Edge |

## Cómo se corrigió
1. **1958** tiene varones, mujeres y total: una celda se corrige sola cuando un único valor hace cerrar a la vez la suma de
   la fila y V + M = T (41 casos; varios son erratas del propio libro, que se anotan como tales).
2. Los casos ambiguos y los de **1962/1965** (solo totales) se releyeron en la imagen; se corrigió únicamente si la cifra
   releída es compatible con la imagen y hace cerrar la fila. Capital 1965 (p. 411) es un escaneo desvaído: 15 celdas.
3. Correcciones manuscritas del ejemplar (Capital 1958, Corrientes 1962) se toman como válidas.
4. Cotejo con las tablas provinciales de Wikipedia: tres celdas donde el error de la fila y el del total provincial coinciden
   (Santa Fe 1962 Belgrano; Mendoza 1965 Rivadavia y Tupungato).
5. Total: 80 correcciones y 9 celdas imputadas (ver `correcciones.py` o la hoja `correcciones` de los xlsx).

## Lo raro que se encontró
- **Páginas**: p_355 es copia exacta de p_382 (libro 389); p_356 y p_357 son las dos «Santa Fe 1958 varones»; faltan
  p_375 y p_409. p_379 (Buenos Aires 1962) está cortada al pie: Florencio Varela no tiene las columnas 1 a 11.
  Se imputaron las columnas 3 a 11 como residuo contra la tabla provincial de Wikipedia (después del arreglo, Buenos Aires
  cierra con diferencias de 1 a 10 votos); inscriptos y votantes quedan vacíos.
- **Capital 1958**: la página de varones escribe Flores 12 / Concepción 5 (al revés que mujeres y total); los valores van
  con los nombres impresos (una nota manuscrita lo confirma).
- **Corrientes 1958**: solo hay escrutinio de diputados (muchas filas no cierran); el atlas presidencial usa el total
  provincial de Wikipedia. **Río Negro 1958** no está en Cantón: idem.
- **Tierra del Fuego 1958**: Cantón suma sus votos presidenciales a Capital («Capital Federal y Tierra del Fuego»).
- **Misiones 1958**: once departamentos anteriores a la división de 1960 (polígonos de 1947).
- **1962 sin elección de diputados** (tabla de bancas de Wikipedia): Catamarca, Formosa, La Rioja, Misiones, San Luis y
  Santa Cruz. **Santiago del Estero 1962** eligió, pero Cantón no la trae: color sólido con la tabla de Wikipedia.
- **1965: Catamarca, Formosa, La Rioja y Misiones sí votaron diputados nacionales.** La tabla nacional de la Wikipedia las
  omite, pero el resumen nacional del t. I de Cantón (p. 239-246 impresas; «Resultados Electorales de 1965. Ministerio del
  Interior») las incluye y marca «NO HUBO ELECCIONES» solo en Jujuy y Salta. Votantes del t. II = t. I; los inscriptos de las
  cuatro (292.202) son justo lo que le falta a la Wikipedia para dar el total del t. I (11.460.766). En el atlas van
  coloreadas y el resultado nacional es Wikipedia + estas cuatro. Al cotejar con el t. I salieron 3 correcciones más
  (La Rioja Capital, Misiones Capital y Guaraní).
- **Nota 15 del t. I** («en 1916 y 1958 [...] los datos departamentales (Tomo II) corresponden a elecciones de diputados»):
  no vale para 1958, salvo Corrientes. Los encabezados del t. II dicen «Elecciones Nacionales de Presidente y Vice. Año 1958»
  y la suma coincide exacto con la tabla presidencial de la Wikipedia (URB y Partido Populista). El atlas 1958 sigue siendo
  presidencial.
- **Errores de Wikipedia** que muestra el cotejo: Santa Fe 1965 MID 198.473 (Cantón 189.473, dos cifras invertidas);
  San Luis 1965 UCRI 1.599 (Cantón 4.328; la Wikipedia copió el valor de Santa Cruz); Capital 1965 «Alianza de la Justicia
  Social» (Cantón: «Alianza de la Juventud Socialista»). La tabla de Corrientes 1965 de Wikipedia repite las filas.
- **Diferencias chicas que quedan como están impresas** (aritmética del libro): Capital 1965 San Bernardo −780 y Santa Lucía
  −863; Chaco 1965 Libertad +270; Córdoba 1965 San Alberto +1.855 y San Justo −2.000 (y Unión Popular provincial +1.000
  contra Wikipedia, sin resolver); votantes de Santa Fe 1962; inscriptos V + M ≠ T en Carlos Tejedor, Tandil, Villarino,
  San Vicente, General Roca (Córdoba) y Junín (Mendoza) 1958; Catamarca 1958 El Alto con más votantes que inscriptos.
  Las fichas del atlas lo señalan cuando la suma no cierra por más de 1 %.

## Bloques de la base contra la tabla nacional de Wikipedia
- **1958**: UCRI −108.639 y UCRP −35.280 son Corrientes y Río Negro (fuera de Cantón). Conservadores −128.314: la tabla
  nacional trae una fila «Partido Conservador» (Reynaldo Pastor, 128.226) sin contrapartida en Cantón. URB y Partido
  Populista, exactos.
- **1962**: FJ −70.482, UCRI −50.615, UCRP −56.357 y FNPC −5.374 son Santiago del Estero (Wikipedia: 70.243, 50.392,
  56.057 y 5.284); PSD −5, PDP exacto.
- **1965**: la tabla nacional de Wikipedia no coincide con la suma de sus tablas provinciales en la FNPC (+70.010) y en los
  movimientos populares provinciales (+15.497); Cantón coincide con las provinciales. UCRI +2.619 es el error de San Luis;
  MID −9.076, el de Santa Fe. El resto, a menos de 0,2 %.

## Faltantes y otras fuentes (revisión del 21-oct-2026)
`atlas5865.py` escribe `mapa<año>/faltantes_<año>.json` con cada unidad beige o en color sólido y su motivo.
- **Beige que son huecos del libro, no de la transcripción**: La Rioja 1965 trae 11 de 18 departamentos (General Belgrano y
  General Roca con asteriscos) y Catamarca 1965, 5 de 16 («no hubo elecciones en todos los departamentos»). El total
  provincial del t. I es la suma de esas filas, y Lupu–Stokes trae exactamente las mismas unidades.
- **Partidos que en 1958 todavía no existían** (Escobar, Tres de Febrero, Hipólito Yrigoyen, San Cayetano) y unidades sin
  electores propios (Isla Martín García, Zona Nacional Puerto La Plata): fila vacía en Cantón y 0 en Lupu–Stokes.
  Antofagasta de la Sierra 1958: no figura en Cantón y Lupu–Stokes la trae en 0.
- **1962 sin elección**: el t. I (p. 211-215 impresas) confirma «NO HUBO ELECCIONES» en Catamarca, Formosa, La Rioja,
  Misiones, San Luis y Santa Cruz. **Santiago del Estero 1962** tiene total provincial en el t. I (igual a la Wikipedia) pero
  ningún desglose departamental en Cantón.
- **1957 (constituyentes), 1960 y 1963**: Cantón no los incluyó por departamento a propósito (t. I, p. XVII: 1960 y 1963 «parecían
  menos significativos»; 1957 ya publicado por Zalduendo, *Geografía electoral de la Argentina*, 1958). El t. I sí trae los
  cuadros provinciales de **1960 diputados** (PDF 278-289) y **1963 presidente** (PDF 306-317); de 1957 no hay cuadro.
- **Lupu–Stokes** (`preparados/lupu_stokes_1912_2003_exportacion.csv`) tiene filas departamentales para 1957, 1960, 1962
  (incluida Santiago del Estero), 1963 (presidente y diputados) y Corrientes 1958, pero solo en cuatro familias (`ucr`, `pj`,
  `soc`, `con`): suma UCRI y UCRP, así que no sirve para decir quién ganó entre los dos radicalismos. En Santiago del Estero
  1962 su `ucr` (54.465) no coincide con UCRI + UCRP de la Wikipedia (106.449).
- **Fuentes originales por buscar**: Ministerio del Interior, *Elecciones Nacionales 1954, 1957 y 1958. Resultados
  electorales comparativos* (circa 1959) y Zalduendo (1958) para 1957; para 1960 y 1963, las publicaciones del Departamento
  Electoral del Ministerio del Interior; prensa provincial (*El Liberal*) para Santiago del Estero 1962.

### Búsqueda de fuentes originales (21-oct-2026)
**Actualización de la búsqueda:** se encontraron fuentes numéricas locales en línea para 1957, 1960 y 1963, y se descargaron Snow y el OCR de Rowe desde Anna’s Archive. El detalle, las reservas y los originales están en [`busqueda_1957_1963/LEEME_BUSQUEDA.md`](busqueda_1957_1963/LEEME_BUSQUEDA.md). Esta revisión corrige las conclusiones anteriores sobre la hemeroteca de Santa Fe (sí cubre estos años), sobre Zalduendo (hay evidencia de Buenos Aires por departamento) y sobre Texas (se pudo abrir y revisar su colección concreta de Archive-It). No hay todavía una base nacional completa ni desglose de Santiago del Estero 1962.

- **Ministerio del Interior, «Escrutinio definitivo de resultados electorales por departamento»** (varios años): es la fuente
  que citan Lupu y Stokes (LARR 44(1), 2009, apéndice A) para sus filas por departamento de 1957 a 1965, junto con Cantón y
  Zalduendo. No se encontró copia digital. Lupu y Stokes agrupan en familias: los blancos de 1957, 1960 y 1963 van en `pj`,
  y la `ucr` mezcla UCRI y UCRP (en 1965 suman el MID a los radicales).
- **Archivo General de la Nación** (fondo DNE01, Dirección Nacional Electoral, serie «Resultados electorales» 1934-1975,
  https://atom.mininterior.gob.ar/index.php/resultados-electorales): planillas por provincia y sexo con inscriptos, votantes y
  votos por partido; según la serie, el detalle llega a departamento, sección o mesa según la carpeta. Hay carpeta por
  provincia para constituyentes 1957, legislativas 1960, legislativas 1962 (Santiago del Estero: `AR AGN
  DNE01-De-ane-29_056_203a245`, 43 folios, más otras dos carpetas) y presidenciales y legislativas 1963. Existen copias
  digitales en el Departamento Archivo Intermedio, **pero no están en línea**: hay que registrarse como usuario del AGN y
  pedirlas (en línea o en sala).
- **Zalduendo, *Geografía electoral de la Argentina* (Ancora, 1958, 238 p., con mapas)**: según su índice, la Capital va por
  secciones y circuitos; las provincias, sin detalle departamental visible; 1957 solo por provincia y partido (apéndice 3).
  Ficha en CeDInPe-UNSAM; sin copia digital encontrada.
- **Archivo web de la DINE en la Universidad de Texas** (repositories.lib.utexas.edu, handle 2152/17166; p. ej. «Elecciones
  nacionales de 1962»): bloqueado desde aquí (CloudFront 403); probablemente cuadros provinciales.
- **Prensa**: no hay hemeroteca digital abierta de *El Liberal* (Santiago del Estero) ni de los diarios nacionales para
  1957-1963. La hemeroteca de Santa Fe solo cubre años anteriores.
- **Otros**: J. W. Rowe, *The Argentine elections of 1963: an analysis* (1964), con cuadros (alcance sin verificar); P. Snow,
  «Parties and Politics in Argentina: The Elections of 1962 and 1963» (1965).
