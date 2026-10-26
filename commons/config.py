"""Datos por atlas para armar el paquete de Commons (ver paquete.py y INSTRUCCIONES_GENERICAS.md).

Cada entrada: carpeta y HTML del atlas, titulo del articulo de es.wikipedia (es el nombre base de los archivos), tipo de eleccion,
fecha, geometria, fuente de los votos, logos usados (nombres de archivo de Commons) y avisos. `hold` = motivos para NO subir
todavia las versiones con logos o la de todo el atlas; `hold_logos` = lo mismo solo para «con leyenda» y PNG.
"""

GEOM = {
    "1914": "Departamentos de 1914 (censo de 1914)",
    "1980": "Departamentos de 1980 y, para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile",
    "1991": "Departamentos de 1991 y, para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile",
    "1991 (plus 2 de Abril, 2001)": "Departamentos de 1991, con 2 de Abril (Chaco, posterior al censo) tomado del shapefile de 2001 y recortado al contorno de 1991; para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile",
    "1991 and 2001": "Departamentos de 1991 y, para los partidos y departamentos creados después del censo de 1991 (Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas, 2 de Abril y, en 2001, San Salvador), su polígono del shapefile de 2001 recortado al contorno de 1991; para Capital Federal, las 28 circunscripciones del SVG de Wikipedia 1999 ajustadas al contorno del shapefile",
    "2010": "Departamentos de 2010 (con las 15 comunas de Capital Federal) y el partido de Lezama (creado en diciembre de 2009, escindido de Chascomús con el polígono del INDEC 2022 recortado al contorno de Chascomús de 2010)",
}
GEOM_SHORT = {"1914": "división departamental de 1914", "1980": "departamentos de 1980", "1991": "departamentos de 1991", "1991 and 2001": "departamentos de 1991 y 2001", "1991 (plus 2 de Abril, 2001)": "departamentos de 1991 (con 2 de Abril de 2001)", "2010": "departamentos de 2010 (con comunas de CABA y Lezama)"}

CANTON = ("Cantón, Darío (1968). ''Materiales para el estudio de la sociología política en la Argentina'', tomo II, {pp}. "
          "Transcritos a mano desde las imágenes del libro; contraste con Lupu y Stokes.")
CALVO = ("Base de datos electorales por departamento de Ernesto Calvo, hojas por provincia de `{xls}` ({cargo}). Base no publicada: "
         "se contrastó con Lupu y Stokes y, en Mendoza, con la transcripción de la UNCuyo.")
CALVO_PRES_CITA = ("Base de datos electorales por departamento de Ernesto Calvo (elecciones presidenciales). "
                  "Referencia bibliográfica: Calvo, Ernesto; Escolar, Marcelo (2005). "
                  "''La nueva política de partidos en la Argentina: crisis política, realineamientos partidarios y reforma electoral''. "
                  "Buenos Aires: Prometeo Libros / PENT. "
                  "Base no publicada: se contrastó con Lupu y Stokes y, en Mendoza, con la transcripción de la UNCuyo.")

# nombres de archivo de Commons de los emblemas (se comprueba en vivo que existan; los que no existan van sin enlace)
L_UCR_OLD = ["Flag of Radical Civic Union.svg"]
L_PS = ["Emblema del Partido Socialista Argentino.svg"]
L_PDP = ["Escudo del PDP.svg"]

ATLAS = {
    "1912": dict(
        folder="mapa1912", html="atlas_1912_diputados.html", dataset="dataset_1912.json",
        article="Elecciones legislativas de Argentina de 1912", tipo="elecciones legislativas (diputados nacionales)",
        fecha="7 de abril de 1912", varones=True, geom="1914", antartida=False, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        inset_omit=[], solido=("Buenos Aires, Catamarca, Corrientes, Entre Ríos, Jujuy, La Rioja, Salta, San Juan, San Luis, Santiago del Estero y Tucumán", "no hay datos departamentales en la fuente y se pintan enteras con su resultado provincial según la tabla del artículo de la Wikipedia (expedientes de la Cámara de Diputados)"),
        votos=["Capital Federal (20 circunscripciones) y Córdoba (21 de 26 departamentos): Cantón, Darío (1968). ''Materiales para el estudio de la sociología política en la Argentina'', tomo II, elecciones de diputados de 1912. Transcritos a mano desde las imágenes del libro.",
               "Mendoza (16 unidades): suma de las cifras expresas de las 188 mesas del expediente 42-D-1912 de la Cámara de Diputados (apym.hcdn.gob.ar), leídas a mano de las imágenes, con las repeticiones del 28/4 en lugar de las mesas anuladas. Los totales de Benegas (15.833) y Gaviola (8.247) coinciden con los del acta.",
               "Santa Fe (5 de 19 departamentos: Rosario, Las Colonias, San Lorenzo, Vera y Belgrano): diario ''Santa Fe'' (Archivo General de la Provincia, Hemeroteca Digital) del 18, 20 y 23/4/1912, escrutinio anterior al diploma del 29/4.",
               "Resto de las provincias: solo el total provincial de la tabla del artículo de la Wikipedia, sin detalle departamental."],
        logos=L_UCR_OLD + L_PS, hold=[], hold_logos=[],
        avisos=["Las cifras de los expedientes y del diario son lecturas visuales de imágenes de época y no tuvieron una segunda transcripción independiente; los controles y las diferencias están en `busqueda1912/`.",
                "Cobertura departamental parcial: Capital (20 circunscripciones), Córdoba (21 de 26 departamentos), Mendoza (16 unidades) y 5 de 19 departamentos de Santa Fe; las otras once provincias se pintan enteras con su total provincial. Los territorios nacionales no votaban (gris, con clave en la leyenda). Santa Fe, con 14 departamentos en beige.",
                "Cada partido cuenta los votos de su primer candidato (lista incompleta, como la columna «votos al partido» de la Wikipedia). La participación solo existe por provincia.",
                "Los bloques siguen la tabla del artículo: «Partidos Conservadores» suma el Conservador, el Constitucional, el Autonomista Nacional, el Oficial, el Popular, la Coalición, los liberales y autonomistas de Corrientes, la Concentración Cívica y el Liberal de Tucumán; Unión Nacional va aparte (royalblue del artículo, cerca del azul oscuro de la Liga del Sur). Mendoza y San Juan salen de un solo color porque sus dos listas son conservadoras.",
                "La Wikipedia imprime 73,20 % de participación nacional; 654.631 votantes sobre 935.001 inscriptos da 70,0 % y es lo que muestra el mapa. En Capital el título de la tabla de Cantón dice 1912 pero el pie cita La Nación de 1916; los totales coinciden con los de 1912 y se trataron como tales.",
                "No se comparó con el mapa por distrito vigente del artículo (`Elecciones legislativas de Argentina de 1912 - Resultados por distrito.svg`)."]),
    "1914": dict(
        folder="mapa1914", html="atlas_1914_diputados.html", dataset="dataset_1914.json",
        article="Elecciones legislativas de Argentina de 1914", tipo="elecciones legislativas (diputados nacionales)",
        fecha="22 de marzo de 1914", varones=True, geom="1914", antartida=False, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        inset_omit=["Gran San Juan"], solido=("Catamarca, Jujuy, Salta, San Juan, Santiago del Estero y Tucumán", "no hay datos departamentales y se pintan enteras con su resultado provincial según la Wikipedia (expedientes de la Cámara de Diputados y tablas provinciales del artículo)"),
        votos=["Cantón, Darío (1968). ''Materiales para el estudio de la sociología política en la Argentina'', tomo II, elecciones de diputados de 1914 (Buenos Aires, Capital Federal y Entre Ríos). Transcritos a mano desde las imágenes del libro; Buenos Aires se contrastó con Lupu y Stokes en 93 unidades.",
               "Córdoba, Corrientes, La Rioja y Mendoza: actas de la Junta Escrutadora Nacional en los expedientes 26-P-1914, 21-D-1914, 13-P-1914 y 29-P-1914 de la Cámara de Diputados (apym.hcdn.gob.ar; los de Corrientes y Mendoza por la Wayback Machine), leídos a mano de las imágenes de los expedientes, sin una segunda transcripción independiente.",
               "Santa Fe (13 de 19 departamentos): diario ''Santa Fe'' (Archivo General de la Provincia, Hemeroteca Digital), 28/3 a 2/4/1914, y ''La Prensa'' (Buenos Aires, 2/4/1914; Internet Archive) para General López, Caseros y Constitución; escrutinio en curso, anterior al definitivo del 8/4. Tres partidos de Buenos Aires (General San Martín, San Antonio de Areco, San Isidro) se completaron con ''La Prensa'' del 1 y 2/4/1914.",
               "Catamarca, Jujuy, Salta, San Juan, Santiago del Estero y Tucumán: solo el total provincial de la tabla del artículo de la Wikipedia, sin detalle departamental."],
        logos=L_UCR_OLD + L_PS, hold=[], hold_logos=[],
        avisos=["Las cifras de los expedientes y de la prensa son lecturas visuales de imágenes de época y no tuvieron una segunda transcripción independiente; los controles de suma por localidad y por provincia están en `busqueda1914/` (hay diferencias documentadas: p. ej. Corrientes, Córdoba, Mendoza y La Rioja contra el total provincial de la Wikipedia).",
                "Cobertura departamental parcial: 7 provincias completas o casi (Buenos Aires 102 de 120 partidos, Capital 20 de 21 circunscripciones, Entre Ríos 13 de 14), 1 con 13 de 19 departamentos (Santa Fe) y 6 pintadas enteras con su total provincial. San Luis no renovó diputados y los territorios no votaban (gris, con clave en la leyenda).",
                "Santa Fe: son cifras de prensa del escrutinio en curso, no del definitivo (el total provincial de prensa del 2/4 difiere del definitivo del 8/4 en 300 a 500 votos por candidato). Capital es una suma parcial de las localidades publicadas, y la tarjeta lo dice. Faltan 5 departamentos (9 de Julio, Garay, San Javier, San Cristóbal y San Justo) y quedan en beige.",
                "Jujuy: la Cámara rechazó los despachos en la sesión del 24 de julio de 1914 y la elección quedó anulada; el mapa pinta el resultado de la tabla de la Wikipedia y la tarjeta lo aclara. Concepción del Uruguay (Entre Ríos) se pinta con una inferencia por residuo (no es transcripción; la tarjeta lo aclara).",
                "Cada partido cuenta los votos de su primer candidato (como la columna «votos al partido» de la Wikipedia). La participación solo existe por provincia (no hay electores por departamento).",
                "Los bloques siguen la tabla del artículo: «Partidos Conservadores» suma también el Partido Demócrata de Córdoba, la Unión Democrática, el Partido Provincial, la Concentración Cívica y la coalición liberal-autonomista de Corrientes. No se comparó con el mapa por distrito vigente del artículo (`Elecciones legislativas de Argentina de 1914 - Resultados por distrito.svg`)."]),
    "1916": dict(
        folder="mapa1916dip", html="atlas_1916_diputados.html", dataset="dataset_1916.json",
        article="Elecciones legislativas de Argentina de 1916", tipo="elecciones legislativas (diputados nacionales)",
        fecha="2 de abril de 1916", varones=True, geom="1914", antartida=False, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        inset_omit=["Gran San Juan"], solido=("San Juan y Santiago del Estero", "no hay datos departamentales y se pintan enteras con su resultado provincial según la Wikipedia (expedientes 53-D-1916 y 7-D-1916 de la Cámara de Diputados)"),
        votos=[CANTON.format(pp="transcripción de las elecciones de diputados de 1916"),
               "Salta: expediente 58-D-1916 de la Cámara de Diputados (planilla del 15 de abril). Valle Grande, General Lamadrid e Independencia: ''La Prensa'', 8/4/1916, p. 6, y acta de la junta escrutadora de La Rioja (expediente 9-D-1916).",
               "San Juan y Santiago del Estero: solo el total provincial de la Wikipedia (expedientes 53-D-1916 y 7-D-1916 de la Cámara de Diputados), sin detalle departamental."],
        logos=L_UCR_OLD + L_PS + L_PDP, hold=[], hold_logos=[],
        avisos=["San Juan y Santiago del Estero no tienen datos departamentales: el mapa pinta cada provincia entera, con el color de su resultado provincial según la Wikipedia, y sin recuadro de Gran San Juan. Los 10 votos de «otros» de San Juan quedan en «no atribuido» (los porcentajes difieren en centésimas).", "23 filas de Cantón están subsumidas en otra unidad (gris oscuro); la leyenda lo dice.",
                "Hay un atlas ficticio de 1916 (`mapa1916fic/`) que NO se sube: es una línea temporal alternativa y queda fuera de lo que Commons acepta."]),
    "1922": dict(
        folder="mapa1922", html="atlas_1922.html", dataset="dataset_1922.json",
        article="Elecciones presidenciales de Argentina de 1922", tipo="elecciones presidenciales",
        fecha="2 de abril de 1922", varones=True, geom="1914", antartida=False, cats_extra=["Election maps of Argentine presidential elections"],
        inset_omit=["Gran Mendoza"], solido=("Mendoza y Santiago del Estero", "no hay datos departamentales y se pintan enteras con su resultado provincial (Memoria del Interior 1921-22, según la Wikipedia)"),
        votos=[CANTON.format(pp="pp. PDF 70–85, «Elecciones nacionales de electores de presidente y vice, 1922»"),
               "Totales por provincia y del país: Memoria del Interior 1921-22 (pp. 239–310), tal como los reproduce la tabla del artículo de Wikipedia; no se verificaron contra la Memoria. Mendoza y Santiago del Estero: solo ese total provincial, sin detalle departamental."],
        logos=L_UCR_OLD + L_PS + L_PDP, hold=[], hold_logos=[],
        avisos=["Mendoza y Santiago del Estero no tienen datos departamentales: se pintan enteras con su resultado provincial (Memoria del Interior vía Wikipedia), sin recuadro de Gran Mendoza. La elección de Mendoza fue anulada (decreto del 17 de abril de 1922); la tarjeta de la provincia lo aclara.",
                "Los porcentajes por departamento son sobre votantes (no sobre votos válidos): Alvear figura con 47,76 % y no con el 50,49 % de Wikipedia, que usa votos de las candidaturas principales. Conviene decirlo en la discusión.",
                "Los totales nacionales no se verificaron contra la Memoria del Interior."]),
    "1930": dict(
        folder="mapa1930", html="atlas_1930.html", dataset="dataset_1930.json",
        article="Elecciones legislativas de Argentina de 1930", tipo="elecciones legislativas (diputados nacionales)",
        fecha="2 de marzo de 1930", varones=True, geom="1914", antartida=False, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        votos=[CANTON.format(pp="pp. PDF 123–140, «Elecciones nacionales de diputados, año 1930 (varones solamente)»; totales provinciales: tomo I, cap. III, pp. PDF 182–183")],
        logos=L_UCR_OLD + L_PS + L_PDP + ["Logo Partido Socialista Independiente.svg", "Monograma utilizado por la UCR Antipersonalista.svg", "Logo of the Bloquista Party of San Juan (Argentina).png"],
        hold=[], hold_logos=[],
        avisos=["San Luis no votó (el tomo I la marca «sin elecciones»)."]),
    "1983": dict(
        folder="mapa1983", html="atlas_1983.html", dataset="dataset_1983.json",
        article="Elecciones presidenciales de Argentina de 1983", tipo="elecciones presidenciales",
        fecha="30 de octubre de 1983", varones=False, geom="1980", antartida=True, cats_extra=["Election maps of Argentine presidential elections"],
        votos=[CALVO_PRES_CITA],
        logos=["RA chapa.jpg", "Flag of the Justicialist Party (square version).svg", "Pacto Autonomista - Liberal.png", "Estrella bloquista.png", "Logo MPN.png", "Logo Mofepa.jpg"], hold=["contradice_wikipedia_1983"], hold_logos=[],
        avisos=["**Contradice el mapa por departamento vigente en Commons** (`Elecciones presidenciales de Argentina de 1983 - Resultados.V1.png`): el ganador coincide solo en el 64 % de las unidades (cotejo en `cotejo_wikipedia/LEEME_COTEJO.md`). La tabla de diputados de la misma base da la razón a nuestro mapa en 126 de 130 discrepancias, y el contraste independiente de la UNCuyo en Mendoza coincide en 18/18 con el nuestro y en 15/18 con el de Wikipedia. Hay que discutirlo en la página del artículo ANTES de subir o proponer nada.",
                "La Alianza Federal suma 106.773 por la base y 107.188 en la tabla de Wikipedia (415 votos de diferencia).",
                "Capital Federal: las 28 circunscripciones son aproximadas (salen del dibujo de Wikipedia)."]),
    "1985": dict(
        folder="mapa1985", html="atlas_1985.html", dataset="dataset_1985.json",
        article="Elecciones legislativas de Argentina de 1985", tipo="elecciones legislativas (diputados nacionales)",
        fecha="3 de noviembre de 1985", varones=False, geom="1980", antartida=True, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        votos=[CALVO.format(xls="TPDENP1985T.xls", cargo="diputados nacionales")],
        logos=["Escudo de la UCR.svg", "Flag of the Justicialist Party (square version).svg", "UCEDE logo chico.png", "Estrella bloquista.png", "Logo MPN.png", "PRS logo.png"],
        hold=[], hold_logos=[], sin_logo=["REN"], logos_sin_licencia=["Logo FREJUDEPA (sello de las boletas de 1985, aportado por el usuario)"],
        avisos=["Los totales de Ernesto difieren algo de los de Wikipedia (p. ej. positivos); el resultado nacional del cartel sale de la tabla del artículo.",
                "Jujuy, San Juan y Santiago del Estero vienen en la base solo con el código; los nombres se tomaron de la base de 1983."]),
    "1987": dict(
        folder="mapa1987", html="atlas_1987.html", dataset="dataset_1987.json",
        article="Elecciones legislativas de Argentina de 1987", tipo="elecciones legislativas (diputados nacionales)",
        fecha="6 de septiembre de 1987", varones=False, geom="1980", antartida=True, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        votos=[CALVO.format(xls="TPDENP1987T.xls", cargo="diputados nacionales")],
        logos=["Escudo de la UCR.svg", "Flag of the Justicialist Party (square version).svg", "UCEDE logo chico.png", "Estrella bloquista.png", "Logo MPN.png", "Partido Provincial Rionegrino.png"],
        hold=[], hold_logos=[],
        avisos=["La base de 1987 trae 13 cifras corregidas a mano (ver `mapa1987/LEEME_1987.md`) y no tiene el padrón en Buenos Aires y Córdoba, así que no hay mapa de participación.",
                "Tierra del Fuego no votó en 1987 (gris con clave en la leyenda)."]),
    "1989": dict(
        folder="mapa1989", html="atlas_1989.html", dataset="dataset_1989.json",
        article="Elecciones presidenciales de Argentina de 1989", tipo="elecciones presidenciales",
        fecha="14 de mayo de 1989", varones=False, geom="1980", antartida=True, cats_extra=["Election maps of Argentine presidential elections"],
        votos=[CALVO_PRES_CITA],
        logos=["Escudo de la UCR.svg", "UCEDE logo chico.png", "Emblema del Partido Socialista Argentino.svg", "Logo MPN.png"], hold=["contradice_wikipedia_1989", "malargue_1989"], hold_logos=[],
        avisos=["**Contradice el mapa por departamento vigente en Commons** (`Elecciones presidenciales de Argentina de 1989 - Resultados.V1.png`): el ganador coincide solo en el 76 % de las unidades. En Mendoza, el contraste de la UNCuyo coincide con el nuestro en 17/18 unidades y con el de Wikipedia en 11/18 (`cotejo_wikipedia/LEEME_COTEJO.md`). Discutir antes de subir.",
                "**Error conocido a resolver antes de subir:** Malargüe 1989. Ernesto trae FREJUPO 3.864 y la UNCuyo 3.964; con 3.964 gana Menem. Falta decidir si se corrige el dato o se anota.",
                "Antofagasta de la Sierra (Catamarca) figura ganada por Unidad Socialista (166 de 435 positivos): es lo que trae la base y es coherente con el total provincial de Wikipedia, pero es un resultado raro."]),
    "1991": dict(
        folder="mapa1991", html="atlas_1991.html", dataset="dataset_1991.json",
        article="Elecciones legislativas de Argentina de 1991", tipo="elecciones legislativas (diputados nacionales)",
        fecha="8 de septiembre de 1991", varones=False, geom="1991", antartida=True, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        votos=[CALVO.format(xls="TPDENP1991T.xls", cargo="diputados nacionales")],
        logos=["Escudo de la UCR.svg", "Flag of the Justicialist Party (square version).svg", "UCEDE logo chico.png", "Estrella bloquista.png", "Logo MPN.png", "PRS logo.png",
               "Pacto Autonomista - Liberal.png", "Logo Fuerza Republicana.png", "Cruzada Renovadora San Juan.png", "Confederación Federalista Independiente.png"],
        hold=[], hold_logos=[], sin_logo=["MPF"], logos_sin_licencia=["Logo MOPOF (escaneo aportado por el usuario, sin fuente documentada)"],
        avisos=["En 1991 el MPF pasó a un color propio (#0097a7) porque el gris azulado se confundía con Malvinas y «sin dato».",
                "La leyenda tiene más de 10 filas (se compactó para que entren)."]),
    "1993": dict(
        folder="mapa1993", html="atlas_1993.html", dataset="dataset_1993.json",
        article="Elecciones legislativas de Argentina de 1993", tipo="elecciones legislativas (diputados nacionales)",
        fecha="3 de octubre de 1993", varones=False, geom="1991 (plus 2 de Abril, 2001)", antartida=True, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        votos=[CALVO.format(xls="TPDENP1993T.xls", cargo="diputados nacionales")],
        logos=["Escudo de la UCR.svg", "Flag of the Justicialist Party (square version).svg", "Estrella bloquista.png", "Logo MPN.png", "PRS logo.png",
               "Pacto Autonomista - Liberal.png", "Logo Fuerza Republicana.png", "Cruzada Renovadora San Juan.png"],
        hold=[], hold_logos=[], avisos=["Ver `mapa1993/LEEME_1993.md` para los casos particulares de la base."]),
    "1994": dict(
        folder="mapa1994", html="atlas_1994.html", dataset="dataset_1994.json",
        article="Elecciones de convencionales constituyentes de Argentina de 1994", tipo="elecciones de convencionales constituyentes",
        fecha="10 de abril de 1994", varones=False, geom="1991 (plus 2 de Abril, 2001)", antartida=True, cats_extra=["1994 Argentine Constitutional Assembly election"],
        votos=["Base de datos electorales por departamento de Ernesto Calvo (`1994-const.xls`, convencionales constituyentes). Base no publicada: se contrastó con la tabla provincial de Wikipedia."],
        logos=["Escudo de la UCR.svg", "Flag of the Justicialist Party (square version).svg", "Logo MODIN.png", "Logo Fuerza Republicana.png", "Escudo del Partido Demócrata (Argentina).svg",
               "Logo Movimiento Popular Jujeno.png", "PRS logo.png", "Pacto Autonomista - Liberal.png", "Logo MPN.png"],
        hold=[], hold_logos=[], sin_logo=["FG"], logos_sin_licencia=["primer logo del Frente Grande (recorte de una imagen de adnrionegro.com.ar, licencia desconocida)"],
        avisos=["Hay discrepancias entre la base de Ernesto y Wikipedia (ver `mapa1994/LEEME_1994.md`). Los diseños de MODIN y Fuerza Republicana no están verificados como de 1994 (fechas de Commons posteriores o desconocidas)."]),
    "1997": dict(
        folder="mapa1997", html="atlas_1997.html", dataset="dataset_1997.json",
        article="Elecciones legislativas de Argentina de 1997", tipo="elecciones legislativas (diputados nacionales)",
        fecha="26 de octubre de 1997", varones=False, geom="1991 and 2001", antartida=True, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        solido=("San Luis", "la base de Ernesto no trae los diputados nacionales de San Luis de 1997 y se pinta entera con su total provincial según la tabla del artículo de la Wikipedia"),
        votos=["Base de datos electorales por departamento de Ernesto Calvo, hojas por provincia de `TPDENP1997T.xls` (diputados nacionales). Base no publicada: se contrastó con los totales por bloque de la tabla del artículo de la Wikipedia (Alianza −0,07 %, PJ −0,02 % una vez sumada San Luis); no coincide con Lupu y Stokes (solo 69 de 500 unidades), que no se usó. San Luis: la base no trae diputados nacionales de 1997; solo el total provincial de la tabla del artículo, sin detalle departamental."],
        logos=["Alianza.png", "Flag of the Justicialist Party (square version).svg", "Logo Accion por la Republica.svg", "Logo Fuerza Republicana.png", "Escudo del Partido Demócrata (Argentina).svg",
               "Partido Nuevo de Corrientes.png", "Logo MPN.png"],
        hold=[], hold_logos=[],
        avisos=["La Alianza (UCR + FREPASO) cuenta como un solo bloque, como el total de la tabla del artículo, aunque en 13 distritos fueran con listas separadas; en el mapa no se distingue quién de los dos puso los votos. Hay un mapa de ganadores por provincia en el artículo (`Elecciones legislativas 1997 - Argentina.png`), que separa el FREPASO de Neuquén; no se comparó con el nuestro.",
                "San Luis (3 diputados) se pinta entera con el color de su resultado provincial (Frente Justicialista 50,9 %), sin límites departamentales.",
                "Los partidos creados después del censo de 1991 (Ezeiza, Hurlingham, Ituzaingó, Presidente Perón, Punta Indio, San Miguel, José C. Paz, Malvinas Argentinas y 2 de Abril) tienen su propio polígono, tomado del shapefile de 2001 y recortado al contorno de 1991.",
                "Colores de la Wikipedia (Alianza #DC0143, PJ #318CE7, AR #3E5298, PD #1F2F6B, PN #FF8800, PDJ #00FFFF); FR lleva el marrón del proyecto (#7B3F00, como en 1991–1995) porque el azul de la Wikipedia se confunde con el PJ y el MPN, y el MPN el azul marino del proyecto. El logo del Partido Nuevo es el único de Commons y figura de 2018 (diseño de época no verificado).",
                "La base de Ernesto queda a menos de 0,1 % de la tabla en Alianza y PJ una vez sumada San Luis (ver `mapa1997/LEEME_1997.md`)."]),
    "2001": dict(
        folder="mapa2001", html="atlas_2001.html", dataset="dataset_2001.json",
        article="Elecciones legislativas de Argentina de 2001", tipo="elecciones legislativas (diputados nacionales)",
        fecha="14 de octubre de 2001", varones=False, geom="1991 and 2001", antartida=True, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        votos=["Base de datos electorales por departamento de Ernesto Calvo, planillas por provincia de `2001 x DTO/Diputados Nacionales` (diputados nacionales). Base no publicada: se contrastó con las tablas provinciales del artículo de la Wikipedia (queda 0 a 3 % por debajo en casi todas las provincias, 6 % en Salta)."],
        logos=["Flag of the Justicialist Party (square version).svg", "Alianza.png", "Ari Logo.svg", "Logo Accion por la Republica.svg", "Escudo del Partido Demócrata (Argentina).svg", "Logo MPN.png"],
        hold=[], hold_logos=[],
        avisos=["La base de Ernesto trae menos votos que la tabla del artículo: 13,97 millones de positivos contra 14,29 (−2,3 %). El resultado nacional del cartel sale de la tabla; los departamentos, de la base.",
                "Bloques como la tabla del artículo: «Concertación Justicialista» suma el PJ, el Partido Nuevo de Corrientes, Unión por Córdoba (con el UCeDé cordobés), el Frente por un Nuevo País, la Alianza de Centro y demás frentes que la tabla agrega; el Frente Unión por Buenos Aires (Capital) es fila aparte. «Alianza» y «ARI» siguen sus totales. Los grupos de Ernesto que la tabla separa o junta distinto se corrigieron columna por columna (`mapa2001/LEEME_2001.md`).",
                "Colores de la Wikipedia (PJ #318CE7, Alianza #DC0143, ARI #6FB53E, AR #3E5298, PD #1F2F6B, MPN #0070B8). PAUFE lleva el ámbar del proyecto (#F59E0B) en lugar del gris de la Wikipedia, que se confundía con «otros». Excepción: el Frente Unión por Buenos Aires lleva en la tabla el azul del PJ y se le dio uno más claro para distinguirlo. El logo del ARI de Commons figura de 2002 (diseño de época no verificado); el de la Concertación es de 2019 y se usó la bandera del PJ.",
                "En 2001 hubo muchos votos en blanco y nulos (24 %): los porcentajes del mapa son sobre votos positivos, como el resto de los atlas.",
                "Los partidos creados después del censo de 1991 y San Salvador (Entre Ríos) tienen su propio polígono, tomado del shapefile de 2001. Los códigos de departamento de las planillas de Santiago del Estero y San Luis siguen la numeración de 1995 y 1993 (se eligió por la correlación de votos; ver `base8399/ernesto/LEEME.md`).",
                "Dos partidos bonaerenses (Almirante Brown y General San Martín) traen una columna con 1.000 votos de más que no cierra con los positivos: se usó la suma de las listas."]),
    "2013": dict(
        folder="mapa2013", html="atlas_2013.html", dataset="dataset_2013.json",
        article="Elecciones legislativas de Argentina de 2013", tipo="elecciones legislativas (diputados nacionales)",
        fecha="27 de octubre de 2013", varones=False, geom="2010", antartida=True, cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
        votos=["Dirección Nacional Electoral (DINE), ''Resultados Provisionales Elecciones 2013'' (por mesa, publicados en datos.gob.ar: `mesas_2013.csv`, `votos_partidos_2013.csv` y `votos_no_positivos_2013.csv`), agregados por departamento y comuna."],
        logos=["Logo Frente para la Victoria.svg", "Logo FPCyS.png", "Logo del Frente Renovador.png", "Propuesta Republicana.png",
               "Frente de Izquierda y de los Trabajadores Logo.svg", "Logo Union por Cordoba.png", "Frente Renovador de la Concordia Social.png", "ACFederal.png",
               "Partido Acción Chubutense.png", "Logo de Partido Fe.svg", "Logo MPN.png", "Flag of the Justicialist Party (square version).svg", "PRS logo.png", "Logo MIJD.png"],
        hold=[], hold_logos=[],
        avisos=["Los votos por departamento salen del escrutinio provisorio por mesa de la DINE (22.369.514 votos positivos sobre 22.612.238 del definitivo, 98,9 %); el resultado nacional del cartel sale de la tabla definitiva del artículo de la Wikipedia.",
                "Dos departamentos (Ramón Lista en Formosa, 26 mesas; Valle Grande en Jujuy, 11 mesas) tienen 0 mesas escrutadas en el provisorio de la DINE y quedan en beige con clave en la leyenda. En las unidades con escrutinio parcial, la participación se calcula sobre los electores de las mesas computadas y la tarjeta aclara cuántas mesas entraron.",
                "El partido de Lezama (creado en diciembre de 2009) se escindió del polígono de Chascomús del shapefile de 2010 usando el contorno del INDEC de 2022 (`Departamentos_2022_INDEC.shp`, dominio público / datos abiertos INDEC).",
                "En la tabla nacional del artículo de la Wikipedia, el subtotal del Frente Progresista Cívico y Social (5.510.949) no incluye el FAP de Entre Ríos (45.026 votos en el definitivo; 128.431 en el provisorio) y suma en Capital Federal los votos de UNEN a senadores (509.446) en vez de diputados (589.545); por eso la suma provisoria del bloque (5.582.090) supera en 1,29 % al subtotal impreso en la tabla.",
                "El Frente Renovador (color #1B2936 de la tabla de Wikipedia), el Partido Acción Chubutense (#00598C, cambiado de #0087D1 para separarlo del PJ y el Partido Fe), el MPN (#00708B) y el Partido Fe (#1268B3) respetan los colores del artículo o tonos diferenciados dentro de la leyenda."]),
}

# palabras clave de `hold`
GEOM["2009"] = "Departamentos de 2010 y las 15 comunas de Capital Federal; Chascomús incluye Lezama, que aún no existía en junio de 2009. Antártida con resultado departamental propio."
GEOM_SHORT["2009"] = "departamentos vigentes en junio de 2009 y 15 comunas de Capital"
ATLAS["2009"] = dict(
    folder="mapa2009", html="atlas_2009.html", dataset="dataset_2009.json",
    article="Elecciones legislativas de Argentina de 2009", tipo="elecciones legislativas (diputados nacionales)",
    fecha="28 de junio de 2009", varones=False, geom="2009", antartida=True,
    cats_extra=["Election maps of Argentine Chamber of Deputies elections"],
    votos=["PolAr_Data (electorArg), datos provisorios por mesa de INDRA / Atlas Electoral de Andy Tow, agregados por departamento y comuna.",
           "Buenos Aires y Valle Grande (Jujuy): planilla del usuario Merged file (15).xls, hoja Sheet1, DN 2009; cifras compatibles con el definitivo, sin votos auxiliares. Se conservó la copia original y los controles.",
           "Tierra del Fuego: Dirección Nacional Electoral, tierra_del_fuego_28_de_junio_de_2009.pdf, escrutinio definitivo, páginas 6 a 8."],
    logos=["Acuerdo Cívico y Socia.png", "Logo Frente para la Victoria.svg", "Union Pro.png",
           "Flag of the Justicialist Party (square version).svg", "Proyectosur logo.png",
           "Nuevo Encuentro (small).png", "Frente Renovador de la Concordia Social.png", "Logo MPN.png", "Logo Frente Grande.png"],
    hold=[], hold_logos=[],
    avisos=["El resultado nacional sale de la tabla de Wikipedia; el mapa combina las fuentes indicadas. No se ajustaron los votos locales para forzar igualdad con Wikipedia.",
            "Buenos Aires: 134 municipios y todas las listas, incluido Nuevo Encuentro (415.856 votos territoriales frente a 415.961 en el total del distrito). General Alvarado estaba codificado 40, duplicando General Alvear; se restituyó 39 por nombre y contraste con PolAr. San Isidro estaba rotulado S. NICOLAS, pero con su código correcto 106. Siete cifras con separadores de miles mal leídos en General Rodríguez se normalizaron; cada municipio cierra al voto.",
            "La tabla nacional de Wikipedia tiene subtotales que no suman sus componentes: ACyS 5.705.105 frente a 5.875.774; FPV 5.544.069 frente a 5.698.942. Se conservan los subtotales impresos para el cartel y la agrupación de las filas para el mapa. Véase el control por bloque en mapa2009/.",
            "Tierra del Fuego: Ushuaia, Río Grande y Antártida conservan su resultado departamental. Ocho votos impugnados de Orcadas quedaron sin escrutar según el PDF. Los totales territoriales no incluyen exterior ni privados de libertad.",
            "La participación utiliza los electores de PolAr, excepto Tierra del Fuego (DINE definitivo); en Buenos Aires y Valle Grande los votos provienen de la planilla recuperada y el padrón de PolAr.",
            "Logos del artículo de 2009; para FRC, MPN y UdN-FG se usan los emblemas del partido más cercanos disponibles, con diseño de época no verificado, según el criterio del proyecto. Metadatos y licencias registrados en logos_wikipedia/LICENCIAS.md y mapa2009/logos_metadata.json. Peronismo Federal usa violeta en lugar del gris de Wikipedia para distinguirlo de territorios sin voto; UdN-FG ámbar para distinguirlo de FRC."])

HOLD_TEXT = {
    "contradice_wikipedia_1983": "El mapa contradice el vigente en Commons; discutir en el artículo antes de subir.",
    "contradice_wikipedia_1989": "El mapa contradice el vigente en Commons; discutir en el artículo antes de subir.",
    "malargue_1989": "Resolver Malargüe 1989 (corregir o anotar) antes de subir.",
    "datos_faltantes_1999dip": "Faltan los datos departamentales de San Luis y Santa Cruz (beige). No publicar este atlas incompleto hasta recuperarlos.",
}

# Diputados en años que ya tenían un atlas presidencial: claves y carpetas separadas.
_DIP_LOGOS = {
    1983: ['Escudo de la UCR.svg','Flag of the Justicialist Party (square version).svg','Pacto Autonomista - Liberal.png','Estrella bloquista.png','Logo MPN.png','Logo Mofepa.jpg'],
    1989: ['Frejupo logo.png','Escudo de la UCR.svg','UCEDE logo chico.png','Confederación Federalista Independiente.png','Cruzada Renovadora por San Juan.png','Logo Fuerza Republicana.png','Logo MPN.png'],
    1995: ['Flag of the Justicialist Party (square version).svg','Escudo de la UCR.svg','Arg FREPASO logo Remake (cropped).png','Pacto Autonomista - Liberal.png','Logo MPN.png'],
    1999: ['Alianza.png','Concertación Justicialista para el Cambio.png','Logo Accion por la Republica.svg','Escudo del Partido Demócrata (Argentina).svg','Logo MPN.png'],
}
_DIP = {
    1983: dict(fecha='30 de octubre de 1983', geom='1980',
        cmp='UCR −1 voto, PJ −450 (−0,01 %); el resto de los bloques ganadores coincide exacto',
        avisos=['La base trae en 0 a la UCR en Posadas (Misiones) y Chacabuco (San Luis) y al PJ en Salta capital y Andalgalá (Catamarca). En los cuatro casos la diferencia entre los positivos declarados y la suma de las demás fuerzas coincide exactamente con lo que falta frente a la tabla provincial de la Wikipedia, así que se imputa ese residuo (anotado en la ficha). Cambia el ganador de Posadas, Andalgalá y Chacabuco.',
                'Islas del Ibicuy se suma a Gualeguaychú (geometría de 1980). Río Negro trae la fila de votantes repetida en 13 departamentos: se toma una sola vez.',
                'MOFEPA lleva el ámbar del proyecto (#f59e0b); MPN el azul marino (#14306e).']),
    1989: dict(fecha='14 de mayo de 1989', geom='1980',
        cmp='FREJUPO +0,08 %, UCR +0,04 %, Alianza de Centro −0,08 %',
        avisos=['FREJUPO agrupa las listas justicialistas; la UCR incluye sus alianzas provinciales con la CFI y el Partido Federal; la Alianza de Centro incorpora el PAL-PDP de Corrientes, como la tabla nacional.',
                'Islas del Ibicuy se suma a Gualeguaychú, Palpalá a Capital (Jujuy) y Tres Lomas a Pellegrini (geometría de 1980). Sin mapa de participación: la base no trae el padrón en todos los departamentos.',
                'Cruzada Renovadora lleva el verde oscuro del proyecto (#004d40, como en 1991 y 1994).']),
    1995: dict(fecha='14 de mayo de 1995', geom='1991 and 2001',
        cmp='PJ −0,02 %, UCR −0,003 %, FREPASO −0,03 %',
        avisos=['En Tucumán el código fr de la base es el FREPASO y frep es Fuerza Republicana; en Jujuy fr es Fuerza Republicana agrupada con el MODIN. El Partido Federal va con la UCR en Córdoba y con el PJ en los demás distritos, como la tabla nacional.',
                'Córdoba: la base no trae la columna del Partido Federal; el residuo de cada departamento entre positivos declarados y suma de las fuerzas (14.914 votos en total, la Wikipedia da 14.915) se imputa a la UCR, con nota en la ficha. San Juan trae la fila de positivos repetida: se toma la primera, que coincide con la suma de las fuerzas.',
                'Deseado (Santa Cruz): la base trae un registro incompleto; por pedido del usuario se calcula como el total provincial de la Wikipedia menos los otros seis departamentos, fuerza por fuerza y para blancos, nulos, votantes e inscriptos (original y cálculo en `mapa1995dip/deseado_extrapolado.json`). No es un resultado departamental observado.',
                'Los partidos creados después del censo de 1991 tienen su propio polígono, tomado del shapefile de 2001 y recortado al contorno de 1991. El Sector Antártico de la base se suma a Ushuaia.']),
    1999: dict(fecha='24 de octubre de 1999', geom='1991 and 2001',
        cmp='Alianza −0,13 %, Concertación Justicialista −0,03 % una vez sumadas San Luis y Santa Cruz',
        solido=('San Luis y Santa Cruz', 'la base de Ernesto no trae sus departamentos y se pintan enteras con su total provincial según la tabla del artículo de la Wikipedia (gana la Alianza en las dos)'),
        avisos=['San Luis (Alianza 44,6 %) y Santa Cruz (Alianza 45,9 %, PJ 45,6 %) se pintan enteras con el color de su resultado provincial, sin límites departamentales, como San Luis en 1997.',
                'Corrientes: se cuenta el lema ACJC00 una sola vez, sin sumarle otra vez sus sublemas. Córdoba trae la fila de inscriptos repetida: se toma la primera.',
                'Unidad Bonaerense lleva sigla (la Wikipedia usa una bandera gris genérica). Se reutiliza la geometría del atlas de 2001 (con San Salvador separado); el Sector Antártico se suma a Ushuaia.']),
}
_DIP_ES = 'Los votos departamentales vienen de la base de Ernesto Calvo; el resultado nacional del cartel, de la tabla del artículo de la Wikipedia.'
for _year, _d in _DIP.items():
    ATLAS[f'{_year}dip'] = dict(
        year=str(_year),folder=f'mapa{_year}dip',html=f'atlas_{_year}_diputados.html',dataset=f'dataset_{_year}dip.json',
        article=f'Elecciones legislativas de Argentina de {_year}',tipo='elecciones legislativas (diputados nacionales)',fecha=_d['fecha'],
        varones=False,geom=_d['geom'],antartida=True,
        cats_extra=['Election maps of Argentine Chamber of Deputies elections'],
        votos=[f"Base de datos electorales por departamento de Ernesto Calvo, hojas por provincia de `TPDENP{_year}T.xls` (diputados nacionales). Base no publicada: se contrastó con las tablas nacional y provinciales del artículo de la Wikipedia ({_d['cmp']})."],
        logos=_DIP_LOGOS[_year],hold=[],hold_logos=[],avisos=_d['avisos'] + ['Logos reutilizados del proyecto; en varios emblemas provinciales el diseño de época no está verificado (ver `logos_wikipedia/LICENCIAS.md`).'],
        **({'solido': _d['solido']} if 'solido' in _d else {}))

ATLAS['2001bronca'] = dict(ATLAS['2001'],year='2001',folder='mapa2001bronca',html='atlas_2001bronca.html',dataset='dataset_2001bronca.json',
    filename_prefix='Elecciones legislativas de Argentina de 2001 (voto bronca)',
    description_es='Variante analítica: votos en blanco y nulos se agrupan como voto bronca y se comparan con las alianzas. No fue una candidatura real. Todos los porcentajes se calculan sobre positivos + blancos + nulos. El símbolo de urna es un gráfico original del autor, no un logo partidario.',
    description_en='Analytical variant: blank and null ballots are combined as voto bronca and compared with electoral alliances. This was not an actual candidate. All shares use positive + blank + null ballots as denominator. The ballot-box symbol is an original explanatory graphic, not a party logo.',
    avisos=ATLAS['2001']['avisos']+['Variante con blancos + nulos como opción analítica. Denominador nacional: 18.798.991; voto bronca: 4.508.883. El atlas original se conserva. El símbolo de urna fue creado para este mapa.'])

from leg2003_2025_config import register as _register_leg2003_2025
_register_leg2003_2025(ATLAS,GEOM,GEOM_SHORT,HOLD_TEXT)


