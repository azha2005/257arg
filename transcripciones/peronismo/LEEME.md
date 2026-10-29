# Atlas peronistas 1946–1973 (29-oct-2026)

Seis atlas con un solo constructor:

```
python transcripciones/peronismo/atlas4673.py <clave>    # 1946, 1948, 1948c, 1954, 1973, 1973s
```

| Clave | Elección | Fuente departamental | Geometría |
|---|---|---|---|
| 1946 | presidente (24-feb-1946) | Cantón t. II (`canton_1946.csv`) | Departamentos_1947 + PBA 1955 + Capital 1960 |
| 1948 | diputados (7-mar-1948) | Lupu y Stokes | ídem |
| 1948c | convencionales constituyentes (5-dic-1948) | Lupu y Stokes | ídem |
| 1954 | diputados (25-abr-1954) | Cantón t. II (`canton_1954.csv`) | Departamentos_1960 + PBA 1955 |
| 1973 | presidente, 1.ª vuelta (11-mar-1973) | Lupu y Stokes | Departamentos_1970 + 28 circunscripciones |
| 1973s | presidente (23-sep-1973) | Lupu y Stokes | ídem |

Salida en `mapas/mapa<clave>/`: `atlas_<clave>.html`, `dataset_<clave>.json`,
`faltantes_<clave>.json` (unidades beige o sólidas y por qué), `sin_poligono_<clave>.json`,
`img/m_gan.png`. El topline nacional sale de la tabla de la Wikipedia (`comun/wikitop.py`,
claves de texto `"1946"`… `"1973s"`; wikitext en `wiki/`, bajado con `bajar_wiki.py`).

## Archivos

- `geom4673.py`: geometría por año. Buenos Aires sale siempre de `geometria/shapefile1955/shapefile1955_corregido/1955pba.shp`
  (aportado por el usuario; el dbf está en latin1 y se lee con un lector propio).
- `fuentes4673.py`: lectores de Cantón y de Lupu y Stokes, partidos → bloques, reparto de «otros».
  **Para cambiar a datos del AGN** basta agregar ahí otra función que devuelva el mismo formato
  (`{(provincia, unidad): {"votes": {partido: votos}, "bloc": {...}, ...}}`) y elegirla en `CFG[clave]["src"]`
  de `atlas4673.py`; el resto (geometría, alias, leyenda) no cambia.
- `wikiprov4673.py`: tablas provinciales de la Wikipedia (por provincia en 1948/1948c, fila única en 1973/1973s).
- `alias_1947.json`, `alias_1960.json`, `alias_1970.json`: nombre de la fuente → nombre del polígono
  (`null` = sin lugar en el mapa; queda en `sin_poligono_*.json`).

## Buenos Aires: shapefile de 1955 contra los datos

Los partidos del shp de 1955 coinciden con las unidades de Cantón. Las que Cantón marca con `**`
(sin cifras propias) son las del Apéndice C del t. I, incluidas en otra unidad; se pintan con el
resultado de la unidad que las contiene y la ficha lo dice (`SUBSUME` en `fuentes4673.py`):
Coronel Rosales → Bahía Blanca; González Chaves, Juárez y Tres Arroyos → Necochea;
Lanús → Avellaneda; Leandro N. Alem → Lincoln; Córdoba: Pte. Roque Sáenz Peña y General Roca → Juárez Celman;
Corrientes: General Alvear → General San Martín; Mendoza: General Alvear y Malargüe → San Rafael;
San Juan: Chimbas → Concepción, Zonda → Rivadavia; Catamarca 1946: Antofagasta → Belén.
Cacopardo: lo único encontrado (Cacopardo y Da Orden, 2008) es cartografía de 1830–1890; no sirve para 1955.

## «Otros» estimados (Lupu y Stokes)

Lupu y Stokes solo traen cuatro columnas de partido (`ucr`, `pj`, `soc`, `con`) y el total.
Para no dejar todo lo demás como «otros», por provincia:

1. `soc` y `con` se asignan primero por nombre (soc → PS/PSD/PST, con → PD); si no hay partido así en la
   tabla provincial, al de proporción más parecida al voto peronista; si ninguno se acerca (error > 0,35),
   se rotula «Otro partido (columna x de Lupu-Stokes)» sin bloque.
2. El resto (total − columnas) se reparte entre los partidos restantes de la tabla provincial de la
   Wikipedia en proporción a sus votos provinciales. Si el total de LS parece votantes y no positivos,
   entra también «En blanco, anulados y diferencias».
3. Los partidos estimados llevan «(est.)» en la ficha y una nota.

**Consecuencia**: en 1973 las victorias de la Alianza Republicana Federal (20 unidades: Corrientes y
San Juan) y de la Alianza Popular Federalista (6) salen del reparto estimado, no de un dato propio.
Que un partido «gane» un departamento con votos estimados quiere decir que en la provincia era fuerte y
LS no traen su columna. En 1948 y 1973s las victorias son todas de partidos con columna propia.

## Dónde consiguieron Lupu y Stokes los datos de 1948 y 1973

La página de datos (noamlupu.com/data) no da la fuente por elección; remite al artículo
Lupu y Stokes (2009), «The Social Bases of Political Parties in Argentina, 1912–2003», *Latin American
Research Review* 44(1). No se pudo leer la sección de fuentes del artículo en esta sesión. Para 1948
la candidata obvia es la Dirección Nacional Electoral (el fondo DNE del AGN, ver memoria `agn-dne01`);
para 1973, las publicaciones del Ministerio del Interior. **Sin confirmar.**

## Casos particulares

- **San Luis 1946**: los rótulos de Cantón contradicen la Wikipedia y el colegio electoral (PER y UD
  invertidos). Se dejan las cifras de Cantón con nota en la ficha.
- **1954, solo varones**: Cantón publica solo el voto masculino de San Luis y Tucumán; la ficha lo aclara.
- **Chaco 1954**: nombres peronistas de los departamentos. «24 de Febrero» → Mayor Luis J. Fontana,
  «Güemes» → General Güemes (por votantes); «Cabo Mayor Farina» y «12 de Abril» sin correspondencia
  segura: 12 de Octubre y Tapenaga quedan beige.
- **Zona Militar de Comodoro Rivadavia** (1946, 1954): sus filas se reparten a Chubut y Santa Cruz con nota.
- **San Juan, Desamparados** (1948, 1948c) y **Salta, General San Martín** (1948c): el shp de 1947 no los
  tiene; Desamparados se pinta en el polígono de Capital y General San Martín en Orán, con nota.
- **Territorios nacionales**: sin elección en 1946, 1948, 1948c y 1954 (gris). En 1948 tampoco votaron
  diputados Catamarca, Jujuy, La Rioja y Salta.
- **Provincias sin detalle** (color sólido con el total de la Wikipedia): 1948c Córdoba, Corrientes y
  Mendoza; 1973 y 1973s Tierra del Fuego.
- **Lupu y Stokes incompletos**: en 1948 faltan 23 partidos de Buenos Aires (entre ellos La Plata, Quilmes,
  Morón, General San Martín y General Sarmiento), Colón, Concordia, La Paz y Villaguay (Entre Ríos),
  Zonda y La Capital y General Pedernera (San Luis). En 1973 faltan ocho partidos del GBA, la
  circunscripción 21 de Capital y cuatro departamentos de Entre Ríos. Quedan beige.

## Pendiente

- Reemplazar Lupu y Stokes (1948, 1973) y Cantón por los datos del AGN cuando estén.
- Fuente primaria de Lupu y Stokes para 1948 y 1973.
- Sin paquete de Commons ni PNG transparentes.
