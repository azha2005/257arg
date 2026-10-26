# Paquetes para Commons

Una carpeta por atlas, cada una con `subir/` (archivos + wikitext) y su `LEEME_SUBIDA.md`. **Todas sin subir** salvo 1928, que se subió desde `../commons_1928/` (ver `../commons_1928/LEEME_SUBIDA.md`).

**Procedimiento común (subir, nueva versión, discusión, licencias):** [`INSTRUCCIONES_GENERICAS.md`](INSTRUCCIONES_GENERICAS.md).

| Año | Artículo de es.wikipedia | Archivos | Estado |
|---|---|---|---|
| [1912](1912/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1912 | 8 SVG + 4 PNG | Se puede subir; **cobertura departamental parcial** (Capital, Córdoba, Mendoza y 5 de 19 departamentos de Santa Fe; 11 provincias pintadas enteras): leer los avisos antes |
| [1914](1914/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1914 | 8 SVG + 4 PNG | Se puede subir; **cobertura departamental parcial** (7 provincias, Santa Fe con 13 de 19 departamentos de prensa y 6 pintadas enteras): leer los avisos antes |
| [1916](1916/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1916 | 8 SVG + 4 PNG | Se puede subir |
| [1922](1922/LEEME_SUBIDA.md) | Elecciones presidenciales de Argentina de 1922 | 8 SVG + 4 PNG | Se puede subir |
| [1930](1930/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1930 | 10 SVG + 5 PNG | Se puede subir |
| [1983](1983/LEEME_SUBIDA.md) | Elecciones presidenciales de Argentina de 1983 | 8 SVG + 4 PNG | **En espera:** El mapa contradice el vigente en Commons; discutir en el artículo antes de subir. |
| [1985](1985/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1985 | 15 SVG + 10 PNG | Se puede subir; «con leyenda» y PNG llevan un logo sin licencia libre (riesgo asumido) y hay versiones «con siglas» sin ese logo |
| [1987](1987/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1987 | 8 SVG + 4 PNG | Se puede subir |
| [1989](1989/LEEME_SUBIDA.md) | Elecciones presidenciales de Argentina de 1989 | 8 SVG + 4 PNG | **En espera:** El mapa contradice el vigente en Commons; discutir en el artículo antes de subir.; Resolver Malargüe 1989 (corregir o anotar) antes de subir. |
| [1991](1991/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1991 | 12 SVG + 8 PNG | Se puede subir; «con leyenda» y PNG llevan un logo sin licencia libre (riesgo asumido) y hay versiones «con siglas» sin ese logo |
| [1993](1993/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1993 | 6 SVG + 3 PNG | Se puede subir |
| [1994](1994/LEEME_SUBIDA.md) | Elecciones de convencionales constituyentes de Argentina de 1994 | 15 SVG + 10 PNG | Se puede subir; «con leyenda» y PNG llevan un logo sin licencia libre (riesgo asumido) y hay versiones «con siglas» sin ese logo |
| [1997](1997/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 1997 | 8 SVG + 4 PNG | Se puede subir; San Luis en color sólido (sin datos departamentales); la Alianza suma UCR y FREPASO |
| [2001](2001/LEEME_SUBIDA.md) | Elecciones legislativas de Argentina de 2001 | 8 SVG + 4 PNG | Se puede subir; la base trae un 2,3 % menos de votos que la tabla del artículo (leer los avisos) |

No hay paquete de 1995 (hay dos versiones del atlas, por lista y por bloque, y ya existe un mapa por departamento en Commons), de 1916 ficticio (línea temporal alternativa, fuera de lo que acepta Commons) ni de AMBA 2025 (falta verificar la licencia de la geometría de circuitos).

## Orden sugerido
1. **1930, 1922 y 1916**: misma fuente y geometría que 1928 (Cantón; base de 1914 de Rodríguez). En Commons hay solo mapas por provincia.
2. **1987, 1993**: sin logos dudosos, pero con la base de Ernesto, que no está publicada (un revisor puede pedir de dónde sale cada cifra).
3. **1985, 1991, 1994**: igual; las versiones con leyenda y PNG llevan un logo sin licencia libre (riesgo asumido). Cada una tiene además una versión «con siglas» sin ese logo: subirla también, así, si Commons borra la del logo, no se pierde todo.
4. **1983 y 1989**: antes hay que discutirlo en el artículo (contradicen los mapas vigentes) y, en 1989, resolver Malargüe.

## Herramientas
- `INSERTAR_EN_ARTICULOS.md` (generado por `insertar_en_articulos.py`): cómo poner los mapas ya subidos en cada artículo de es.wikipedia, con el wikitext listo por año y qué hacer si la discusión no tiene respuesta.
- `paquete.py <año>`: regenera la carpeta de un año (necesita el atlas construido y los PNG de `png_transparentes/`).
- `verificar_commons.py [año]`: compara con Commons (SHA1): igual / distinto / no subido.
- `chequeo.py [año]`: revisa que los SVG no tengan nada que MediaWiki rechace y los dibuja con resvg en `chequeo/`.
- `config.py`: título del artículo, fecha, fuentes, logos y avisos de cada año. `flatten.js`: el script que aplana el SVG del atlas en el navegador.
