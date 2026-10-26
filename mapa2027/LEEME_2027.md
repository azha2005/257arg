# Escenario hipotético 2027 (presidenciales, 1.ª vuelta y balotaje)

`atlas_2027.html` (`python prep27.py` una vez y después `python build_2027.py`). **No es un resultado ni una encuesta**: es una inferencia por departamento a partir de 2023 con una matriz de traspasos de voto que el usuario propuso y yo completé. Los totales nacionales son los del escenario de la imagen del usuario.

Modos: 1.ª vuelta (`gan`, `mil`, `bre`, `kic`, `vil`) y balotaje (`gan2`, `bre2`, `mil2`; pestaña «2ª V.»).

## Totales nacionales del escenario (fijos, el modelo los reproduce exactos)
| Candidatura | 1.ª vuelta | Balotaje |
|---|---:|---:|
| Milei (LLA, Santilli) | 9.864.273 · 35,48 % | 14.698.960 · 61,90 % |
| Bregman (Frente Popular, Siley) | 4.271.410 · 15,36 % | 9.048.802 · 38,10 % |
| Kicillof (Derecho al Futuro) | 4.154.804 · 14,94 % | |
| Villarruel (Todo por Argentina, Gómez Centurión) | 3.232.384 · 11,63 % | |
| Scioli (Una Argentina Renovada, Jalil) | 2.435.301 · 8,76 % | |
| Manes (Consenso Federal) | 2.326.723 · 8,37 % | |
| Schiaretti (Provincias Unidas) | 1.517.454 · 5,46 % | |

Inscriptos y participación (79,18 % y 68,32 %) son los de la imagen; no se modelan por departamento (no hay modo de participación).

## Datos de partida (todo DINE, escrutinio provisorio por mesa)
- Generales 2023 (`datos_oficiales/2023/agregado.pkl`): Milei, Massa+Grabois, Bullrich+Larreta, Schiaretti, Bregman (FIT-U). 26.291.718 positivos.
- **PASO 2023 por lista** (`datos_oficiales/2023_paso/`, descargado el 16-oct-2026 de la copia de Wayback Machine de `argentina.gob.ar/sites/default/files/dine-resultados/2023-PROVISORIOS_PASO.zip`, 88 MB; ya no está en el sitio oficial): listas 3005 Massa, 3006 Grabois, 3007 Larreta, 3008 Bullrich. Sirve para partir UxP en Massa/Grabois y JxC en Bullrich/Larreta en cada departamento (nacional: Grabois 21,5 % de UxP, Larreta 39,9 % de JxC). El agregado por sección está en `presidente_paso_por_lista_seccion.csv` (`<disco externo>/REGIONES/...\PASO 2023` solo trae las coaliciones, sin internas).
- Generales 2019 (`datos_oficiales/2019/agregado.pkl`): Frente NOS (Gómez Centurión) como inclinación local de Villarruel.
- Geometría: la de `mapa2013` (Departamentos_2010 + comunas + Lezama) con dos retoques propios en `mapa2027/geom.py` (16-oct-2026): (1) **La Paz (Catamarca)** traía en el shapefile de 2010 un rectángulo que se metía en Santiago del Estero; se recorta al límite de 2022 y los trozos pasan al departamento vecino que corresponde; (2) **Tierra del Fuego con tres departamentos** (Río Grande, Tolhuin y Ushuaia, redibujados con el límite de 2022 dentro del contorno de 2010). 527 unidades con dato; Antártida se suma a Ushuaia en los datos (el recuadro de la Antártida usa el color de la provincia). Las Malvinas se dibujan en gris también en el mini «Provincias». Esos retoques **no están** en `mapa2013`, `mapa2009` ni en otros atlas que usen `Departamentos_2010`. Santa Fe tiene otra numeración en 2019: se empareja por nombre. Antofagasta de la Sierra no está en el 2019 de la DINE: usa el valor de Catamarca.

## Método (`escenario27.py`, todo editable)
1. Grupos de origen por departamento: **LLA** (Milei 23), **B** (JxC × (1−l), Bullrich), **L** (JxC × l, Larreta), **M** (UxP × (1−g), Massa), **G** (UxP × g, Grabois), **H** (Schiaretti), **F** (FIT-U). `g` y `l` salen de la PASO de ese departamento.
2. Matriz a priori `TAU` (filas = origen). Lo que fijó el usuario: Bregman = FIT + Grabois + 15 % de Milei 23 (rango pedido 15-25 %); Milei = casi todo Bullrich 23 + menos de la mitad de su propio voto; Villarruel se lleva parte del voto de Milei 23 y de Bullrich, con inclinación por Centurión 2019. Lo que completé yo: Massa → Kicillof 50 %, Scioli 27 %, Manes 16 %; Schiaretti conserva ~80 % de Hacemos; Larreta es el voto menos fiel a Milei.
3. Inclinaciones locales: Villarruel × (Centurión 2019 relativo)^0,5; Bregman desde Milei × (potencial FIT + Grabois)^0,6; Manes × (peso de JxC)^0,5 desde Massa y Hacemos; Kicillof ×1,25 en Buenos Aires; Scioli ×1,6 Catamarca y ×1,3 Tucumán (Jalil); Schiaretti ×1,15 Córdoba, ×1,25 Santa Fe y Chubut.
4. **IPF**: las filas (origen × departamento) conservan sus votos y las columnas se ajustan hasta clavar los totales de la tabla. Se supone el mismo electorado que en 2023, escalado ×1,0575 al total del escenario (27.802.349).
5. Balotaje Milei-Bregman: cada candidatura de la 1.ª vuelta se reparte en [Milei, Bregman, abstención] (`R2`), con un corrimiento logístico de 0,3 por cada 10 puntos de Milei sobre el promedio, y dos escalares globales que clavan 14.698.960 y 9.048.802.

### Matriz efectiva tras el ajuste (% de cada origen)
| | Milei | Bregman | Kicillof | Villarruel | Scioli | Manes | Schiaretti |
|---|---:|---:|---:|---:|---:|---:|---:|
| Milei 23 | 44,3 | 15,3 | 1,0 | 33,0 | 1,0 | 3,4 | 2,0 |
| Bullrich | 94,0 | 0 | 0 | 4,4 | 0 | 1,1 | 0,5 |
| Larreta | 80,4 | 0 | 0 | 3,6 | 1,9 | 11,2 | 2,9 |
| Massa | 2,1 | 2,2 | 49,1 | 1,9 | 27,1 | 17,1 | 0,5 |
| Grabois | 0 | 93,6 | 5,5 | 0 | 0,9 | 0 | 0 |
| Schiaretti 23 | 6,7 | 0 | 1,5 | 3,0 | 6,3 | 17,8 | 64,6 |
| FIT 23 | 0 | 100 | 0 | 0 | 0 | 0 | 0 |

Con esto los números de la imagen cierran de una forma bastante particular: Milei = ~89 % de JxC + ~44 % de su propio voto, y Villarruel sale casi toda del voto de Milei 23 (un tercio). La alternativa «85 % Bullrich y 80 % Milei» que propuso el usuario deja a Milei en ~44 % y a Villarruel en alrededor de 5 %, así que no cierra con la imagen.

## Resultado del escenario
- 1.ª vuelta, por departamento: Milei 459, Kicillof 58, Bregman 6 (Bariloche, Ensenada, Cushamen, Cochinoca, Ñorquín, El Cuy), Villarruel 3 (Florentino Ameghino, Pehuenches y Tolhuin), Schiaretti 1 (Minas, Córdoba); Scioli y Manes ninguno. Por provincia: Milei 23 y Kicillof 1 (Santiago del Estero).
- Balotaje: Milei gana las 24 jurisdicciones y 439 departamentos; Bregman 88 (sur y oeste del conurbano, Formosa, norte de Chaco y Salta, Jujuy, Santa Cruz y parte de Río Negro).
- Regla 3: la leyenda lleva a Milei, Bregman, Kicillof, Villarruel y Schiaretti; Scioli y Manes van a «Otros» (17,13 %) en la torta y siguen en el detalle de cada departamento.

## Supuestos a revisar
- **Santiago del Estero** (`R2_PROV_B = 0,3`): sin ese freno Bregman ganaba la provincia en el balotaje (con β=0,5 llegaba a 65 %); el escenario del usuario dice que no gana ninguna. Es un ajuste a mano.
- Los 6 departamentos de Bregman en la 1.ª vuelta ganan con 25-29 % y por pocos puntos; cualquier cambio de los traspasos los mueve.
- No se modela abstención por departamento ni cambios de padrón; las cifras absolutas por departamento son las de 2023 × 1,0575.
- Colores: LLA, FIT y Provincias Unidas como en AMBA 2025; Kicillof en el azul del PJ; Villarruel magenta, Scioli turquesa, Manes verde (sin antecedente en el proyecto). Logos: recortes de AMBA 2025 para LLA, FIT y Provincias Unidas; MDF (Kicillof) y la V de Villarruel son recortes de las imágenes que pasó el usuario (`logos_wikipedia/Logo_MDF_Kicillof.png`, `Logo_Villarruel_V.png`, fondo quitado; origen y licencia sin verificar); Scioli y Manes llevan sigla (UAR, CF). La barra de Villarruel es magenta oscuro (#6d0f45) para que se lea la V rosa. Los nombres de las fuerzas de Kicillof, Villarruel, Scioli y Manes salen de la imagen del usuario (traducidos del inglés).
- No hay paquete de Commons: es una simulación.

PNG en `../png_transparentes/mapa2027/` y `../png_blanco/mapa2027/`.

Nota: el recorte de La Paz de 2027 usa el límite de la ley 22.742 (zona en disputa con Santiago del Estero, ver `AGENTS.md`); los atlas anteriores a 2022 conservan el límite de hecho. Los votos de esa franja (Las Palmitas) los cuenta la DINE en La Paz.
