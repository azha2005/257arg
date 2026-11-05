# AGN, Departamento Archivo Intermedio: fondo Dirección Nacional Electoral (DNE01)

Respuesta de María Inés López (archivointermedio@mininterior.gob.ar), 23-oct-2026. El fondo está **completamente digitalizado, pero no hay copia en línea**. Para acceder hay dos vías: llevar un disco externo y copiar las imágenes elegidas, o pedir algo puntual del inventario y darles un espacio en la nube para subirlo, porque las imágenes pesan mucho. La carpeta compartida se borra periódicamente: los originales quedaron en `<carpeta local>/agn\`.

## Qué mandaron (solo instrumentos de descripción, sin imágenes)
- `FINALIZADO-AR-AGN-ISAD-DNE01-De - Inventario a para usuarios.xlsx`: inventario analítico de 777 carpetas. Copia en `inventario_DNE01_De.csv`.
- `FINALIZADO-AR-AGN-ISAD-DNE01_02.docx`: descripción del fondo (ISAD-G). `..._ISAAR...docx`: registro de autoridad.
- `FINALIZADO-AR-AGN-DNE01-Bi- Inventario.xls`: biblioteca de la DNE (1.349 libros y folletos; no son planillas).
- `Usuarios 2026 - Estado de fondos DAI.xlsx`: estado de todos los fondos del Archivo Intermedio.

## El fondo
- Material de la Sección Estadística. Va de 1917 a 1986, sobre todo de 1946 a 1975. Está ordenado por distrito.
- Series y folios: Resultados electorales 16.909, Antecedentes electorales 13.365, Normativa 1.670, Estudios 893 y Empadronamiento 399.
- Acceso y reproducción sin restricciones. Aviso de la ficha: parte de «Resultados» son **borradores sin garantía de autenticidad**.
- **El inventario no dice el nivel de desagregación** (departamento, circuito o solo provincia). Para saberlo hay que ver las imágenes.

## Cobertura de elecciones nacionales, serie «Resultados» (`cobertura_nacionales.csv`)
| Año | Distritos | Carpetas | Folios | Faltan |
|---|---|---|---|---|
| 1946 | 16 | 17 | 658 | territorios nacionales (no votaban) |
| 1948 | 15 | 15 | 1.155 | ídem (constituyentes + diputados) |
| 1951 | 26 | 27 | 1.576 | — |
| 1954 | 26 | 29 | 2.646 | — (vicepresidente + diputados) |
| 1957 | 24 | 30 | 1.515 | Tierra del Fuego (constituyentes) |
| 1958 | 23 | 23 | 1.642 | Tierra del Fuego |
| 1960 | 20 | 21 | 1.087 | Jujuy, Río Negro, San Juan, T. del Fuego |
| 1962 | 16 | 20 | 502 | Buenos Aires, Catamarca, Formosa, La Rioja, San Luis, Santa Cruz, Santa Fe |
| 1963 | 24 | 28 | 1.237 | La Rioja |
| 1965 | 17 | 20 | 771 | Catamarca, Formosa, Jujuy, La Rioja, Misiones, Salta |
| 1973 | 23 | 48 | 2.475 | La Pampa, La Rioja |

Además hay carpetas nacionales de 1940 y 1942 (una cada una) y elecciones provinciales y municipales de casi todos los años entre 1946 y 1973. La serie «Antecedentes» puede tener resultados: no se cruzó carpeta por carpeta.

## Antes de 1946 (revisado el 23-oct-2026)
**En el inventario de la DNE** (todo en las cajas 46 y 47, pocos folios):
- 1912–1931: solo legislación electoral (Catamarca 1912–29, nacional 1926–27, Capital 1927, Santiago del Estero 1930). No hay resultados.
- 1932–1936: provinciales sueltas (San Juan 1932/34, Buenos Aires 1934/35, Entre Ríos 1934 «legislación y resultados», San Luis, Santa Fe y Tucumán 1934).
- Nacionales, con todo el país en una carpeta: diputados 1938 (80 folios), 1940 (75 + 95), 1942 (41 + 126, más Capital 22) y presidenciales 1943, que no llegaron a hacerse (7). Son «Antecedentes», salvo 1940, que es «Resultados». Ninguna carpeta corresponde a 1931, 1934, 1936 ni a la presidencial de 1937.
- Una carpeta de estudios «Presidenciales 1916–1946», de 102 folios, probablemente con totales.

**Fuera del inventario** (según `Usuarios 2026 - Estado de fondos DAI.xlsx`):
- **Ministerio del Interior, serie «Planillas electorales» (AR-AGN-MI01-pe), 1908–1925, 11 m en legajos de expedientes** (piso 3, sector C). Sin instrumento de descripción y sin datos de digitalización. Es el doble del volumen de toda la serie «Resultados» de 1946–1975. La misma ubicación figura como «AR-AGN-DNE01, 1908–1925, 12 m, expedientes», así que probablemente es el mismo material. Cubriría las elecciones de 1912 a 1924 (Sáenz Peña), justo los huecos de 1912, 1914, 1916 y 1922.
- Ministerio del Interior, Series Históricas: «Elecciones Nacionales de 1946» e «Intervención de Correos y Telégrafos en las elecciones de 1946» (inventariadas, sin digitalizar).
- Ministerio del Interior, Oficina de Padrón Electoral, 1870–1935 (sin inventario).
- Fiscalía Nacional de Recuperación Patrimonial, Comisión 42 «Censos, estadísticas y padrones electorales», 1955–1959.

## Correspondencia
- 23-oct-2026: el borrador de respuesta (correo personal del autor), en el hilo del AGN, pide las muestras de Santiago del Estero 1962 (29_056_246a273) y Río Negro 1958 (19_037_238a267). También ofrece la carpeta de Drive «AGN - DNE» del autor (editor con enlace; cerrar el acceso cuando terminen), pide el fondo completo si pueden y consulta por la serie MI01-pe.
- 5-nov-2026: López pide de nuevo el enlace para subir las dos muestras y aclara que «planillas electorales» **no es una serie** del AGN. El material AR-AGN-DNE01 de 1908 a 1925 ingresó hace poco y lo relevaron de forma provisoria: hay tejuelos borrados y paquetes que no abrieron. Mandaron ese inventario, que está en `inventario_provisorio_1908_1925.csv` (71 legajos). Análisis completo en la sección siguiente.

## Inventario provisorio 1908–1925 (5-nov-2026): qué puede servir
Los rótulos dicen «padrones» o «registros electorales». Con las leyes 8130 (1908) y 8871 (1912), en el registro de cada mesa se asentaban el acta de apertura, el acta de cierre y el escrutinio de la mesa, así que **un padrón de mesa puede traer los votos de la mesa**. Hay que confirmarlo con las imágenes. El «Acta de la urna 101, mesa 9» de Añatuya muestra que en el lote hay actas de mesa. Aunque no traigan votos, los padrones dan los **inscriptos reales**.

| Elección | Legajos (provincia: n.º) | Para qué sirve |
|---|---|---|
| Buenos Aires 1880–1885 | Bs. As.: 1 (Fondo M.I., Serie Elecciones) | Elecciones de la década de 1880 (Roca 1880, diputados 1882/84). No hay atlas |
| Diputados 1908 | Bs. As.: 3, 4 y 2 (1908–10); Córdoba: 5 y 6; Entre Ríos: 7 | Posible atlas nuevo de 1908 |
| Registros 1909 (para 1910) | Santa Fe: 2; San Luis: S/N; Corrientes: 14; Tucumán: 9 y 6 («Presidente, Vicepresidente y Diputados»); Salta: S/N (1908–10) | Padrón de la ley 8130 e inscriptos de 1910 |
| Diputados y electores presidenciales 1910 | Córdoba: 7 y 16; Salta: 62 y 10; Tucumán: 23; Bs. As.: S/N; La Rioja: 25 («Electores Presidenciales», con rótulo de 1912) | Posibles atlas nuevos de 1910 (diputados y Sáenz Peña) |
| 1912–1915 | Tejuelo borrado: 30 («Elecciones de Diputados Nacionales. Padrones») | Sin identificar |
| Diputados 1912 | **Santa Fe: 24 y 28** (14 de 19 departamentos en beige); **La Rioja: 16, 28 y 22**; **San Luis: 35 y 10**; **Tucumán: S/N** (las tres en color sólido) | Completa los huecos del atlas 1912 |
| 1913 | Santiago del Estero: 31 (sobres con boletas); Mendoza: S/N | Elecciones complementarias de 1913. Las boletas se pueden contar |
| Diputados 1914 | La Rioja: 53, 56 y 57 (sobres y boletas); Mendoza: S/N | Cotejo de las actas del HCDN que ya se usaron |
| 1916? | Santiago del Estero: tejuelo borrado | Santiago del Estero 1916 está pendiente |
| Diputados 1920 | **Santiago del Estero: 24 (remisión de actas), 26, 21, 19 y 11**; Santa Fe: 29 y 34 | Actas de mesa; Santa Fe da los inscriptos |
| 1922 | **Santiago del Estero: 3 («varios departamentos»), 8, 13, 33 y 39** (sin cómputo departamental); Santa Fe: 13 | Completa Santiago del Estero 1922 |
| 1925 (¿1924 o 1926?) | Santa Fe: 17, 3 (Caseros), 27, 32, 43 y 38; La Rioja: S/N | 1924 no tiene base. Fechar con las imágenes |
| 1894–1925 | «Legajo VS», S/N | ¿Vélez Sarsfield? Ahí falta el inscripto de 1918. Preguntar |
| 1961 | S/N, «Panorama político del país y resultados electorales» | Diputados 1960 y elecciones provinciales de 1961 |
| Sin fecha | Santa Fe: 3 legajos; La Rioja: 4; Santiago del Estero: 1; otros con tejuelo borrado; libros copiadores del Ministerio | Pueden ser 1914 (Santa Fe tiene 5 departamentos en beige) o 1916 (Santiago del Estero) |

Inscriptos reales: en 1922, Cantón «reconstruye» los inscriptos de La Rioja, Salta, San Luis y Tucumán. Los padrones de esas provincias reemplazarían esa reconstrucción.

- **Para el segundo mail** (después de ver las muestras): ofrecer devolverles las tablas transcriptas; preguntar cómo citar el fondo; pedir Corrientes 1958 (18_035_269a328, 60 folios) y las Series Históricas del Ministerio del Interior de 1946; pedir horarios y dirección si hay que ir con un disco.

## Archivos originales en el repo (5-nov-2026)
- `inventario_DNE01_De.csv`: inventario analítico de las 777 carpetas.
- `biblioteca_DNE01_Bi.csv`: biblioteca de la DNE.
- `estado_fondos_DAI_2026.csv`: estado de todos los fondos del Archivo Intermedio.
- `inventario_provisorio_1908_1925.csv`: el lote de 1908 a 1925.

Los .docx ISAD e ISAAR están resumidos arriba. Para los años 30, ver `DECADA_1930.md`: Ministerio del Interior, Expedientes Generales 1931–1941, digitalizado.

## Prioridades
1946, 1948, 1951, 1954, 1957 y 1973 no tienen atlas y Cantón no los cubre igual. Para 1958, 1962 y 1965 serviría para cotejar las correcciones de `canton5865/` y las páginas faltantes.
