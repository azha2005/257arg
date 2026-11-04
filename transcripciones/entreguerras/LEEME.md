# Atlas de 1926, 1937 y 1940

Construidos el 3 de noviembre de 2026 desde el dibujo del atlas de 1930, de la misma familia que los mapas publicados de 1922 y 1928. Conservan proyección, composición, recuadros históricos y logos centrados con zoom. No se ejecuta ni modifica el constructor de los atlas de referencia.

## Fuentes y cobertura

| Elección | Fuente departamental | Alcance |
|---|---|---|
| Diputados 1926 | Cantón II, PDF 87–103, impresas 83–99 | 372 filas, 342 con votos, 14 distritos; San Luis no renovó diputados |
| Presidente 1937 | Cantón II, PDF 142–145 | Capital Federal, Córdoba, La Rioja y Tucumán; 76 filas, 73 con votos |
| Diputados 1940 | Cantón II, PDF 147–151 | Capital Federal, Córdoba, Entre Ríos, Santa Fe y Tucumán; 91 filas, 88 con votos |

Son resultados observados de las tablas, de varones solamente. No se estiman votos ni se ajustan los departamentos a cifras nacionales. Cantón seleccionó los distritos de 1931–1942 según el criterio editorial de su introducción (I, p. XVI); la presencia de una tabla no certifica ausencia de irregularidades. Fuera de esa selección, beige y pendiente. Los territorios nacionales y los distritos sin renovación van en gris: Catamarca, Jujuy, La Rioja, Salta y San Juan en 1940; San Luis en 1926.

`manual1926.txt` es la transcripción visual de las 17 páginas, con clave provincial, página y marcas `*`/`**`. `canton_1926.csv` y `canton_1926.json` la exportan. Las imágenes de revisión quedan fuera de la redistribución de datos. Para 1937/1940 se usan las transcripciones ya revisadas en `../canton1937_1940/`; no se alteran sus cifras.

Los snapshots `w1926.txt`, `w1937.txt`, `w1940.txt` y sus JSON registran los artículos y revisiones consultados. Torta, barras y métricas nacionales proceden de sus tablas, vía `mapas/mapa<año>/wiki_nacional_<año>.json` y `comun/wikitop.py`. No se confunde la suma de una cobertura parcial con el total nacional.

## Agrupaciones

- 1926: UCR, Partidos Conservadores, UCR Antipersonalista, PS, UCR Unificada, radicalismo disidente, lencinistas, bloquistas e independientes, conforme a los grupos nacionales del artículo. Conservadores suma demócratas, conservadores, Pacto Autonomista–Liberal, Concentración Popular, liberales, Unión Provincial y Concentración Cívica. Disidentes suma Principista, Independiente de Corrientes, Blanca, Roja y Doctor Carranza. Comité Independiente de Buenos Aires va a Independientes, separado de UCR Independiente de Corrientes. Las fichas conservan cada columna original. No se suman partidos menores sin alianza para fabricar un ganador «Otros».
- 1937: Ortiz/Concordancia suma Concordancia, PDN y Junta Renovadora Nacional de Córdoba. Allí PDN + Junta da 97.762, frente a 97.764 de la tabla provincial. Molinari y Defensa Provincial siguen separados. PS no gana ninguna unidad y va a Otros en el cartel nacional, conservándose en las fichas.
- 1940: Concordancia suma las columnas Concordancia, PDN, UCR de Santa Fe, Radical Unificado y Social Independiente. UCR–Frente Popular de Tucumán permanece separada y gana Monteros. Los partidos menores no se agrupan para decidir ganadores.

Los colores y emblemas heredados son los del atlas 1930: bandera bicolor para UCR 1926, monograma antipersonalista, PS y estrella bloquista. En 1937/1940 UCR usa el escudo ya usado en los atlas posteriores a 1931. Concordancia conserva la familia azul del antipersonalismo, más legible que el gris azulado del artículo; disidentes y Frente Popular usan magenta para distinguirse del rojo y el marrón. Sin emblema específico verificado se muestra sigla. No se agregaron logos anacrónicos.

## Geografía y límites

Mismo SHP `Departamentos_1914`, proyección y trazado de 1922/1928/1930, incluyendo las veinte circunscripciones históricas de Capital. Es una base histórica de referencia, no una afirmación de que cada límite de 1937/1940 fuera idéntico al de 1914. `alias_1914.json` hereda las correspondencias documentadas de 1930. Una fila compartida por varios polígonos lleva nota; se suma una sola vez al total provincial. Nunca se reparten votos entre polígonos.

1926 tiene una fila con votos sin polígono: Alberdi, Santiago del Estero, 155 votos positivos. Se conserva en el agregado provincial y en la transcripción. Las unidades no recuperadas quedan beige. No hay recuadro antártico antes de 1946; las Malvinas permanecen grises.

`CONTROL_ATLAS.json` distingue filas de fuente y polígonos con datos. No sumar los valores de las fichas de polígonos compartidos. Los JSON de control guardan diferencias por bloque entre base y Wikipedia y diferencias entre suma de columnas y votantes. Las fuentes omiten categorías y contienen erratas; no se convierten diferencias aritméticas en votos de un partido ni en blancos/nulos.

## Relectura y contraste de 1926

`cotejo1926.py` busca, por provincia y familia de Lupu–Stokes, el subconjunto de columnas publicadas más próximo. Es diagnóstico de transcripción, no una identificación de listas a partir de cuatro familias. En las diez diferencias iniciales se volvió al escaneo ampliado. Se corrigieron cuatro digitaciones: PS San Antonio de Areco 296→206; UCR Valle Viejo 435→485; Carranza Tafí 906→506; Independientes Famaillá 129→29. No se usó Lupu como reemplazo de la imagen.

Se conservan seis discrepancias con Lupu porque el impreso dice lo transcrito: Junín conservadores 2.253 (Lupu 1.253), Concepción de Corrientes antipersonalistas 452 (492), Federación UCR 422 (482), Paraná antipersonalistas 4.858, con anotación manuscrita (4.854), Santa Bárbara antipersonalistas 36 (38), General López PS 136 (134). `COTEJO_LUPU_1926.json` registra todos los emparejamientos.

## Reproducir

Desde la raíz:

```powershell
python transcripciones/entreguerras/datos.py
python transcripciones/entreguerras/cotejo1926.py
python mapas/mapa1926/build_1926.py
python mapas/mapa1937/build_1937.py
python mapas/mapa1940/build_1940.py
python transcripciones/entreguerras/verificar.py
```

Los HTML son autocontenidos. Todos los modos se eligen en la barra; las pestañas del póster muestran los principales y el modo activo. Hay registro en el catálogo y miniaturas locales del sitio. No se subió a GitHub Pages ni se prepararon paquetes de Commons.

## 1918, 1920 y 1924

Las tablas de 1918 (PDF 44–54) y 1920 (PDF 56–68) ya están transcritas en `transcripciones/canton1918/` y `canton1920/`; atlas locales en `mapas/mapa1918/` y `mapas/mapa1920/`. Ver [método y reservas de esos dos atlas](LEEME_1918_1920.md). Lupu–Stokes tiene 228 registros de 1918 en ocho distritos y 245 de 1920 en diez, con familias agrupadas, no una base completa de listas. De 1924 no hay registros en esa exportación ni una transcripción departamental preparada localizada; no implica que los resultados históricos no existan.
