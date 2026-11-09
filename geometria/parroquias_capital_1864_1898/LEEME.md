# Parroquias electorales de la Ciudad de Buenos Aires, 1864-1898

Cinco capas, una por cada configuración parroquial usada en las elecciones de la ciudad. Son las mismas geometrías del visor `mapas/capital_canton/capital_1864_2007.html`.

| Capa | Vigencia | Parroquias | Método |
|---|---|---|---|
| `parroquias_1864` | 1864-1869 | 12 | Calco municipal adaptado al límite de 1869. Barracas al Norte agrupada y Balvanera anterior a San Cristóbal reconstruida |
| `parroquias_1872` | 1872-1886 | 14 | Calco municipal, límite occidental del SHP de 1869 y Riachuelo de la lámina |
| `parroquias_1890` | 1890-1895 | 16 | Calco municipal con el área de San Bernardo reintegrada según el cruce con las secciones de 1895 |
| `parroquias_1896` | marzo de 1896 | 17 | Calco de la lámina municipal cotejado con Cantón y Jorrat, *Elecciones en la ciudad*, t. I, apéndices 2 y 4 |
| `parroquias_1898` | 1898 | 22 | Lámina municipal para Carmen, Vélez Sársfield y San Carlos; decretos de 1896 para Las Heras y Balvanera Norte/Sur |

Cada versión viene en dos trazos (campo `trazo`):

- **`lamina`** (`parroquias_<año>.shp`): el borde exterior tal como lo dibuja la lámina municipal, con su Riachuelo y su costa.
- **`base`** (`parroquias_<año>_base.shp`): las mismas parroquias recortadas al contorno de la base de Rodríguez y De Grande (secciones de 1869 hasta 1886, de 1895 desde 1890). Los huecos que deja el recorte, sobre todo la franja costera, pasan a la parroquia vecina con más borde en común, y los pedazos sueltos de una parroquia, a su vecina. Los límites interiores no cambian. Es la que encaja sin huecos ni solapes con los departamentos de esa base.

Desde 1890 cada capa incluye además un polígono «Diques y dársenas» (`tipo = puerto`), que no es parroquia electoral.

## Archivos

- `parroquias_<año>.shp` y `parroquias_<año>_base.shp`: un shapefile por versión y trazo (UTF-8).
- `parroquias_capital_1864_1898.gpkg`: las diez capas en un GeoPackage.
- `parroquias_capital_1864_1898_shp.zip`: los shapefiles, este LEEME y el control.
- `CONTROL.json`: cantidad de parroquias, superficie de cada una (km², UTM 21S) y solapes.

Campos: `parroquia`, `tipo`, `version`, `vigencia`, `trazo`, `metodo`, `reserva`. Sistema de referencia: el de la *Base cartográfica de departamentos para los censos nacionales de la República Argentina desde 1869 a 2010* (Rodríguez y De Grande, CONICET, hdl:11336/149867).

## Reservas

Son reconstrucciones aproximadas, no delimitaciones legales. Los límites anteriores a 1887, el reparto anterior a la creación de San Bernardo y los cortes de 1898 son los más inciertos. El contorno del calco de 1896 coincide con las secciones de 1895 de la base de Rodríguez y De Grande con un IoU de 0,94; las diferencias vienen de la lámina municipal. Cerca de La Boca y Barracas el Riachuelo coincide con la base; río arriba, frente a Flores y Vélez Sársfield, la lámina dibuja los meandros a ojo y se sale del límite unos 6,7 km². Sobre el Río de la Plata la costa de la lámina queda más adentro y deja una franja de unos 5,2 km² sin parroquia. El trazo `lamina` conserva esas diferencias; el trazo `base` las elimina.

Las geometrías son válidas, contiguas, sin huecos ni enclaves; los solapes son menores a 1 m².

## Regenerar

```
"C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/capital_canton/exportar_parroquias.py
```

Fuentes del calco y del cotejo: `mapas/capital_canton/LEEME.md`.

Autoría: Juan Cruz Rodríguez Paolini, *Atlas electorales de Argentina 1904-2025*, github.com/azha2005/257arg.
