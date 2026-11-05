# Elecciones nacionales de los años 30: qué hay y dónde buscar (5-nov-2026)

Pedido del usuario: tener todas las elecciones de la década. Elecciones nacionales:

| Elección | Atlas | Cantón t. II por departamento | Estado |
|---|---|---|---|
| Diputados, 2-mar-1930 | `mapas/mapa1930/` | sí | hecho |
| Presidente y diputados, 8-nov-1931 | — | **no**: lo omite por presunción de fraude (t. I, p. XVI) | fuentes relevadas en `transcripciones/1931/LEEME.md` |
| Complementarias de 1932 (Santa Fe, entre otras) | — | no | expedientes `n-ov-1932` de la HCDN |
| Diputados, 4-mar-1934 | — | no | sin relevar |
| Diputados, 1-mar-1936 | — | no (el índice no la trae) | sin relevar |
| Presidente, 5-sep-1937 | `mapas/mapa1937/` | solo Capital, Córdoba, La Rioja y Tucumán | parcial |
| Diputados, 6-mar-1938 | — | no (el índice no la trae) | sin relevar |
| Diputados, 3-mar-1940 | `mapas/mapa1940/` | solo Capital, Córdoba, Entre Ríos, Santa Fe y Tucumán | parcial |
| Diputados, 1-mar-1942 | — | no | sin relevar |

Lupu y Stokes solo trae 1930, 1937 y 1940: son las mismas unidades que Cantón.

## Fuentes, de la más rendidora a la menos

1. **Expedientes de diplomas de la HCDN** (`apym.hcdn.gob.ar/uploads/expedientes/pdf/<n>-d-<año>.pdf`).
   - Son uno por diputado electo y traen una copia del acta de la junta escrutadora.
   - En 1931 algunos traen el acta mesa por mesa: Mendoza 113-D y La Rioja 67-D.
   - Para 1938 aparece al menos el 24-D-1938, con el acta de escrutinio de Buenos Aires de marzo de 1938 (salió en una búsqueda web).
   - Hay que hacer el mismo sondeo de `transcripciones/1931/` para 1932, 1934, 1936, 1938 y 1942. **Bajar de a uno y con pausas**: en 2026 la HCDN respondió 403 después de unas 370 consultas en paralelo. Si no, usar Wayback (`web.archive.org/web/2022id_/...`).
   - Desde las sesiones en la nube la HCDN está bloqueada por la red: hay que habilitarla o bajarla desde la PC.
   - Los electores presidenciales de 1931 y 1937 se proclaman ante la Asamblea Legislativa. Buscar también expedientes `n-ov` y `n-pe` de esos años.
2. **AGN, fondo DNE**.
   - El catálogo está en línea en AtoM: `atom.mininterior.gob.ar` (bloqueado en esta sesión; desde la PC anda).
   - Carpetas de la década:
     - 46_090: elecciones provinciales de 1932 a 1935. Santa Fe 1934 son «Resultados»; Entre Ríos trae «legislación y resultados».
     - 46_091_1a22: provinciales de 1937.
     - 46_091_23a102: **nacionales de 1938**. Son «Antecedentes»: convocatoria y listas, quizás con resultados.
     - 46_091_103a143: 1939.
     - 46_091_144a218 y 219a313: nacionales de 1940.
     - 47_092: 1941, 1942 y 1943.
     - Estudios: 01_001_95a196 («Presidenciales 1916–1946») y 51_101 («Elecciones 1946–1951 (1916–1939)»). Probablemente traen totales provinciales.
   - La ficha AtoM de 1938 dice que **hay copias digitales** en el Archivo Intermedio.
   - Del lote de 1908 a 1925 no hay nada de los años 30.
3. **Memorias del Ministerio del Interior.**
   - La Wikipedia cita la Memoria presentada al Congreso en 1938 como fuente de las legislativas de 1938.
   - Las escaneó la Academia Nacional de la Historia y están en Wikisource y Commons: «BaANH… Memoria del Ministerio del Interior (año)».
   - Hay al menos 1924-1925 (sirve para el hueco de 1924), 1926-1927 y 1927-1928. Falta ver si hay volúmenes de 1931 a 1943.
   - Para leerlas desde la nube hay que habilitar `commons.wikimedia.org` y `es.wikisource.org`.
4. **Cantón y Jorrat, *Elecciones en la Ciudad*, t. II (1912–1973)**: Capital Federal en todos los años, por circunscripción. En papel, por ejemplo en la UNSAM.
5. **Prensa**: Hemeroteca Digital de Santa Fe (*El Orden*, *El Litoral*), *La Prensa* y *La Nación* en la Biblioteca Nacional o la de la UNLP, y diarios provinciales. Para Buenos Aires, *El Día* de La Plata.
6. **Bibliografía con tablas posibles**: Melón Pirro sobre la «ley trampa» y el fraude ([PDF](https://historiapolitica.com/datos/biblioteca/decadatreinta_melon.pdf)); Walter, *La provincia de Buenos Aires en la política argentina 1912–1943*; tesis de Ferrari (Buenos Aires 1913–1934); Ignacio López sobre las intervenciones de Ortiz.

## Reglas para estos atlas
- Son elecciones con fraude conocido en varias provincias. Se mapea el resultado oficial y se avisa, como en 1937 y 1940. No se corrige el fraude.
- Lo que no se consiga va en beige (regla 8). Las provinciales del mismo día solo se usan como aproximación rotulada, y se decide caso por caso (ver 1931).
- Geometría y estilo de la familia 1930/1937/1940 (`transcripciones/entreguerras/`).

## Revisión del 5-nov-2026 con los cinco archivos originales del AGN
- **Biblioteca de la DNE** (`biblioteca_DNE01_Bi.csv`, 1.349 títulos): casi todo es derecho y diarios de sesiones. No hay publicaciones de resultados anteriores a 1946. Sirven los **tomos de sesiones preparatorias del Diario de Sesiones de Diputados**, porque ahí se aprueban los diplomas con un resumen de cada acta:
  - n.º 356: 1916, t. I, abril a julio. Elección de 1916.
  - n.º 571: 1928, t. I. Elección de 1928.
  - n.º 191: período 1932. Diplomas de 1931.
  - n.º 825: 1934, t. I, abril a agosto. Elección de 1934.
  - Para 1936 y 1938, la biblioteca solo tiene tomos de mitad de año (n.º 357 y 158). Los tomos de abril están en la Biblioteca del Congreso.
- **Descripción del fondo DNE (ISAD):** la ley obligaba a guardar las actas solo 15 años. Por eso el fondo se concentra entre 1946 y 1975 y **no trae las actas de los años 30**. Remite a fondos relacionados del Ministerio del Interior: «Expedientes generales» y el fondo Ministerio de Gobierno, serie «Censos y padrones».
- **Estado de fondos** (`estado_fondos_DAI_2026.csv`): la pista clave para los años 30 es **Ministerio del Interior, Expedientes Generales 1 (AR-AGN-MI01-Eg1)**.
  - 1867–1941: 295 m, piso 3, sector B. **En papel**: según la respuesta del 5-nov-2026 solo está digitalizado el instrumento de descripción. Tiene **inventario analítico de 1867, 1868, 1908 y 1931–1941**.
  - 1942–1946: 23 m, en papel, con inventario analítico (digitalizado).
  - Las juntas electorales remitían sus actas al Ministerio del Interior, así que ahí deberían estar los expedientes de las elecciones de 1931 a 1942 (y los de 1908).
  - **Pedir esos inventarios analíticos** es lo primero.
  - Otros fondos para mirar:
    - Intervenciones Federales, Memorias, 1861–1940: provincias intervenidas que organizaron elecciones.
    - Mesa de Entradas, Libros de registro de expedientes, 1931–1957: índice para buscar números de expediente.
    - Expedientes secretos, confidenciales y reservados, 1932–1983: sin digitalizar.
