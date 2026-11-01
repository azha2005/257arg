# Presidenciales 2003 en el AMBA, por radio censal 2001

Estimación de los votos de cada radio censal 2001 en la elección presidencial del 27 de abril de 2003. Sigue el método del atlas `../mapaAMBA2025radios/` (Poblaciones / LN Data), con una diferencia: **no hay registro de en qué local votó cada mesa en 2003**, así que los locales son aproximados. Cada valor del mapa es una estimación; solo los totales por circuito, partido y circunscripción son exactos.

## Cómo se regenera
```
"<venv de Mosaic>/python.exe" mapas/mapaAMBA2003radios/radios_amba2001.py   # una vez: radios 2001 del AMBA (necesita geopandas)
python mapas/mapaAMBA2003radios/asignar.py                 # reparto -> asignacion_idw.pkl, asignacion_pob.pkl, control_asignacion.json
python mapas/mapaAMBA2003radios/build_amba2003radios.py        # atlas_amba2003radios.html      (escuelas 2025, principal)
python mapas/mapaAMBA2003radios/build_amba2003radios.py pob    # atlas_amba2003radios_pob.html  (control: solo población)
python comun/render_transparentes.py mapaAMBA2003radios
python comun/render_blanco.py mapaAMBA2003radios atlas_amba2003radios.html   # y el _pob
```
Antes de `asignar.py` tiene que existir `../mapaAMBA2025radios/locales_amba2025.csv` (escuelas 2025 ya ubicadas). La cola del constructor (plantilla y parches) se toma de `../mapaAMBA2025/tail_amba.py` con reemplazos.

## Datos
- **Votos**: PolAr `datos_oficiales/polar/data__arg_presi_gral2003.csv` (Atlas Electoral de Andy Tow, por mesa). AMBA = Capital + los mismos 40 partidos del atlas 2025 (PolAr escribe «Las Heras», «J.C.Paz» y «Matanza»). 23.947 mesas, 231 sin votos; 571 circuitos; 7.478.822 votantes y 7.314.818 votos positivos. Candidatos por código según la tabla nacional de la Wikipedia (la de `analisis/escenarios2003/preparar.py`).
- **Circuitos de 2003**: `geometria/circuitos_serie/por_anio/2003/aproximada/` (aporte del usuario: `caba_circuitos.shp` y `bsas_circuitos03.shp`, sin PRJ; se supuso EPSG:22193). Usan los mismos códigos INDRA que PolAr: **empalman los 571 circuitos**, sin alias.
- **Radios**: `geometria/cartografia_argentina/conicet/radios/RADIOS_2001_V2025-1.zip` (CONICET, censo 2001, `POB_TOT`). 13.392 radios y 13.174.170 habitantes (Capital 2.776.138).
- **Escuelas**: los 5.320 locales de 2025 con punto propio de `../mapaAMBA2025radios/locales_amba2025.csv` (se dejan afuera los 167 que allí iban al centro de su circuito 2025).

## Por qué escuelas de 2025
Se buscó una tabla mesa → local de 2003, 2007 o 2011 (1-nov-2026): no está en PolAr ni en los provisorios de la DINE de 2011 a 2023, que van de circuito a mesa. El único listado anterior encontrado, «centros de votación 2015» de la DINE en dat.ar, ya no se puede descargar. Wayback no respondía para buscar el padrón de 2003. Aun con un listado de otro año no se podría ubicar cada mesa de 2003: el padrón se renumera en cada elección y en 2003 las mesas eran de varones o de mujeres. Lo que aporta cualquier listado es qué escuelas hay en cada circuito y cuántos electores vota en cada una, y eso ya está en 2025.

## Reparto (`asignar.py`)
1. Cada escuela de 2025 se asigna al circuito de 2003 que contiene su punto. Las 5.320 caen en algún circuito; 2 se descartan porque el circuito es de otro partido (la capa está algo corrida en los bordes).
2. **Variante principal (`idw`)**: cada circuito reparte sus votos entre sus escuelas en proporción a los electores de 2025 de cada una, y cada escuela los reparte entre los radios de su partido (en Capital, de su circunscripción de 2003) con peso 1/d² al centroide del radio, con piso de 25 m. Los radios que suman menos de 1 voto quedan en 0 y su parte vuelve, en proporción, al resto. Mediana de 7 escuelas por circuito; 65 circuitos con una sola. **39 circuitos sin ninguna escuela** (77.005 votantes, 1 %) usan su punto interior.
3. **Control (`pob`)**: sin escuelas; cada circuito reparte entre los radios cuyo punto interior cae en él, en proporción a la población 2001. Dibuja los límites de circuito por construcción.
4. Se reparten con el mismo peso todas las categorías: candidatos, blancos, nulos y electores de las mesas con votos (de ahí la participación estimada de cada radio).

Capital se restringe por circunscripción (las 28 secciones electorales de 2003; las comunas son de 2005). Los radios de Capital se asignan a la circunscripción del circuito 2003 que contiene su punto interior; 4 radios caen fuera de un circuito de su distrito (4.574 habitantes) y van a la circunscripción más cercana o a su partido.

## Controles
- **Totales**: la suma de los radios por partido o circunscripción y categoría coincide con PolAr (error máximo 1e-11 en `idw`, 0 en `pob`; `assert` en `asignar.py`).
- **Radios sin votos**: 0 en `idw`; 14 en `pob` (4.576 habitantes), en beige.
- **Ganadores**: `idw`: Kirchner 8.055 radios, López Murphy 2.793, Menem 1.529, Carrió 1.002, Rodríguez Saá 13. `pob`: 7.719, 2.872, 1.535, 1.213 y 37.
- **Las dos variantes coinciden en el ganador** en el 90,7 % de los radios (92,0 % de la población).
- AMBA sobre positivos: Kirchner 24,82 %, Menem 19,19 %, López Murphy 17,37 %, Carrió 16,68 %, Rodríguez Saá 12,01 %.

## Reservas
- Se supone que en 2003 se votaba en las mismas escuelas que en 2025 y con el mismo peso relativo. No se puede comprobar. Escuelas abiertas después de 2003 y barrios que crecieron desde entonces reciben votos de 2003 en proporción a sus electores de hoy.
- La capa de circuitos 2003 tiene proyección inferida (sin PRJ) y no es cartografía certificada.
- Radios de 2001 y escuelas de 2025: 24 años de diferencia entre el padrón de los pesos y la población.

## Estilo
- Paleta del mapa presidencial 2003 de la Wikipedia, la misma de las legislativas 2003–2005 del proyecto: Menem #1c5ece, Kirchner #50ade6, López Murphy #f4ce00, Rodríguez Saá #1aff98, Carrió #74b744. Logos: bloques del mismo mapa (`logos/bloques_presidenciales/menem.png`, `fpv03.png`, `recrear.png`, `mnp.png`, `ari.png`; CC0).
- Modos: Ganó, % Kirchner, % Menem, % López Murphy y % Carrió (la plantilla admite cinco pestañas; la participación sale en las fichas y en el anillo). Las rampas de los porcentajes van de casi blanco al color del candidato y después más oscuro, porque los colores de 2003 son claros.
- **Cortes según la distribución por radio** (pedido del usuario, como en 2025): con cinco fuerzas el ganador saca entre 22 y 37 % en el 90 % de los radios (mediana 27), así que «Ganó» usa 22, 24, 27, 30, 33 y 37 %. Las coropletas siguen los percentiles 10 a 95 de cada candidato: Kirchner 17–36, Menem 14–28, López Murphy 8–35 y Carrió 10–23. Con los cortes de 10 puntos casi todo caía en el primer tono. En los tonos oscuros del modo «Ganó» los azules de Menem y Kirchner se parecen, como en el mapa de la Wikipedia.
- Recuadro de Capital más arriba y más bajo que en 2025: la leyenda tiene seis filas y arranca en y=1024. Circunscripciones de Capital como divisores.
- No va a Commons salvo pedido.

## Para Twitter
`python exportar_tw.py` (copia del de `../mapaAMBA2025radios/`) renderiza el póster del modo «Ganó» a 4021×3453 px y los modos de Kirchner, Menem, López Murphy y Carrió para la respuesta, en `tw/`. Se guardan como PNG de paleta de 256 colores (1,2 a 1,4 MB), con el borde de los radios a 0,18 px. `tw/texto_respuesta.txt` tiene el texto del segundo tuit con la metodología (266 caracteres), en el formato del de 2025.
