# Buenos Aires 1827: Junta de Representantes y elección de Dorrego

`atlas_1827.html`, generado con el Python del venv de Mosaic (geopandas):

    "C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/mapa1827/build_1827.py

Estilo del visor de Capital 1864-2007 (Ink, Epilogue, modo oscuro con la clave `tema`). Dos pestañas:

- **Por lista**: por sección, cuántos electos estaban en la lista «Unos enemigos del Imperio Brasilero» (*Gaceta Mercantil* 1103).
- **Voto por gobernador**: cómo votó cada electo el 12 de agosto (Dorrego 31; Las Heras 2; López 1; J. J. Anchorena 1). Los que votaron a Dorrego van juntos, como una lista.

En el panel de las dos: hemiciclo de 47 bancas, conteo por agrupación y **voto popular estimado**.

## Datos
`transcripciones/1827/`: `bancas_1827.csv`, `electos_1827.csv` (con votos de la *Gaceta* 1114 y de la *Crónica* 68 y la fecha de incorporación), `lista_N1103_enemigos_del_imperio.csv`, `listas_resumen.csv`, `san_nicolas_1827.csv` (Galimberti, cuadro 5) y `fuentes_1827.md`.

## Voto popular estimado (pedido del usuario: extrapolar por las agrupaciones)
En cada sección se suman los votos de los electos de cada agrupación y se dividen por las bancas de la sección. Cada votante elegía tantos nombres como bancas había. Sólo entran la ciudad, Flores, San Isidro, Morón y Luján. San Nicolás se muestra aparte y no suma, porque se anuló.
Resultado: lista N1103 59,9 % (1.520) y fuera de ella 40,1 % (1.016). Los que después votaron a Dorrego suman 89,6 % (2.272).
El segundo número no es un voto por Dorrego. Es el voto popular del 22 de julio de quienes lo eligieron el 12 de agosto.

## Por parroquia
Ni la *Gaceta* ni la *Crónica* revisadas publican el escrutinio de la ciudad por parroquia, sólo el total de los electos. El único desglose por mesa es el de San Nicolás (San Pedro, San Nicolás y Baradero), que va en la ficha. El dato por parroquia estaría en las actas (AGN, Sala X) o en el Diario de Sesiones.

Relectura completa en prosa (17-nov-2026) de la *Gaceta* 1096-1134, la *Crónica* 46-80 y el *Correo Político y Mercantil*: tampoco hay votos por parroquia ni por pueblo en notas, correspondencia o sesiones. Lo que sí sale de la prosa:

- La ciudad votó en «ocho puntos» (*Crónica* 66) y «en la mayor parte de las parroquias ha sido numeroso el concurso» (*Crónica* 59). En Quilmes «no ha habido eleccion, por no haberse reunido los electores» (*Crónica* 59).
- Las actas de la campaña llegaron tarde y se aprobaron en bloque y sin cifras en las sesiones preparatorias del 4, 7 y 8 de agosto; la de Navarro «había venido suelta» y se devolvió a la mesa central de Chascomús (*Crónica* 71, 73 y 74; *Gaceta* 1128). El 12 de agosto el Ejecutivo avisó que faltaban las actas «restantes de la campaña, y Patagones» (*Crónica* 77, *Gaceta* 1131).
- Rivadavia no salió electo (*Gaceta* 1132).
- La elección complementaria de septiembre tuvo una protesta en la Catedral (16 de septiembre), con votos apuntados «por rayas» (*Correo* 13). La tropa de línea quedó excluida del voto por la ley del 15 de septiembre (*Correo* 50 y 61). El número 62 del *Correo* no está digitalizado (el PDF rotulado 62 es otra copia del 61).
- Listas de candidatos: además de las ya cargadas, la *Gaceta* 1108 trae una nómina sin firma para elegir (48 nombres) y la lista «Un Patriota antes del año 10», y la 1109 la de «Un Porteño Imparcial» (30). Agregadas a `listas_resumen.csv` (17-nov-2026). En la nómina de 1108, «Bernardo Escalada» y «Manuel H. Aguirre» no se cuentan como electos (podrían ser Bernabé Escalada y Aguirre de Lajarrota).

## Frontera de 1826 (pedido del usuario, 17-nov-2026)
`geometria/frontera_bsas_1827/`: la línea de 1826 sale del mapa escolar de avance de la frontera que aportó el usuario (`avance_frontera_mapa_escolar.png`, autor sin identificar). `frontera.py` separa por color las bandas hasta 1826 y `georef.py` las georreferencia con ocho ciudades (ajuste afín, residuos de 6 km o menos) → `frontera_1826_mapa_escolar.geojson`. El mapa tapa el noreste con texto y ríos: se une a la jurisdicción de Buenos Aires de 1788 del HGIS de las Indias (capa 7, OBJECTID 1768, CC BY-NC-SA; `hgis_indias_jurisdicciones_1787_1788.geojson`). El polígono de Patagones del HGIS llega a 43° S y no se usa: Patagones usa la Comandancia del HGIS (ver abajo).

En el atlas, las secciones se recortan a ese territorio (Arrecifes pierde 12 % hacia el oeste; Morón y Luján 1-2 %); dentro de la frontera y sin sección (solo Martín García desde la asignación estimada), gris oscuro; la provincia de 1869 fuera de la frontera, gris claro; la línea, punteada. Es una línea de escala escolar, no un trazado documental.

## Diario de Sesiones, tomo 2 (17-nov-2026)
La Hemeroteca Digital de la BNMM tiene el *Diario de Sesiones de la H. Junta de Representantes* de 1827 desde el número 21 (29 de septiembre); el tomo 1 (números 1 a 18, agosto y septiembre), que cita Galimberti para San Nicolás, no está digitalizado (en papel en la biblioteca del AGN). En Google Books, `2V07AQAAMAAJ` y `aAtXAAAAMAAJ` (vista completa) son de 1852 y 1854 (reedición de 1883), no el tomo 1; sin revisar: `n4I4AAAAMAAJ`, `O084AAAAMAAJ`, `s4Q4AAAAMAAJ`, `TL4itwAACAAJ`. Lo que interesa del tomo 1: la sesión 10 (pp. 17-18, San Nicolás por pueblo, la que cita Galimberti) y las actas de campaña de las sesiones 1 a 18. Las actas de Morón, Pilar y San Isidro pasaron por el Congreso nacional: *Documentos del Congreso General Constituyente 1824-1827* (AHPBA; Google Books `MC7VAAAAMAAJ`) y Ravignani, *Asambleas Constituyentes Argentinas*, t. III (1826-27): en HathiTrust todas las copias son «solo búsqueda» por derechos de autor. Del tomo 2 salen:

- **Arrecifes**: Luis Saavedra («electo representante de Arrecifes», aprobado el 12 de septiembre, incorporado el 20 de octubre, número 29) y José María Baudriz («electo representante por el partido de S. Antonio de Areco», renuncia admitida el 2 de octubre, número 22). Los dos iban en la lista de la *Gaceta* 1103.
- **Patagones**: José María Rojas, «por pluralidad de sufragios», sin cifras (acta leída el 3 de octubre, número 23). La lista no proponía a nadie por Patagones.
- Los tres no votaron al gobernador: categoría «Incorporado después» en ese modo.
- Desde fines de septiembre se sientan también **Anchorena** y **Viola**; su sección sale del decreto de convocatoria (ver abajo).
- La ciudad tuvo una elección complementaria de dos representantes en septiembre-octubre, con una mesa por parroquia (Catedral, Colegio, San Nicolás, Concepción, Socorro...); la mesa central la declaró nula el 15 de octubre por irregularidades en la Concepción. No se publican votos (números 21 y 29).
- Los PDF quedan fuera del repo (dominio público, en la Hemeroteca: `render.php?url=000981043/1827/BNA_S000981043_<fecha>N000<nn>.pdf`).

## Representantes por sección: decreto de convocatoria (17-nov-2026)
El *Registro Nacional de la República Argentina*, t. II (1880), número 2197, p. 201 (Google Books `gjsoAQAAMAAJ`, vista completa; leído en la imagen), copia el decreto del 1 de agosto de 1827 que convoca a la Junta para el 3, con los representantes por sección:

- Ciudad: los 24 ya cargados («Manuel H. de Aguirre», que acá figura como Aguirre de Lajarrota; «Rafael P. de Lucena»).
- Morón, Matanzas y Conchas: Valle y Zelaya. San Isidro: Jorge Pacheco y Eusebio Medrano. Flores: Echevarría y Terrero. Luján, su Guardia y Lobos: Celestino Vidal y Fortunato **Miró** (antes «Miñó»).
- **Pilar**: Domingo Achega y José Vicente Arraga.
- **Ensenada, Quilmes y Magdalena**: Juan José Viamont, Santiago Rivas, Agustín Francisco Wright y Eladio Otamendi.
- **Arrecifes, Salto, Pergamino, etc.**: José Julián Viola, José María Baudrix, Luis Dorrego y Luis Saavedra.
- **Chascomús, Ranchos, etc.**: Nicolás Anchorena.

Adolfo E. Rodríguez, *El régimen electoral en el lapso 1827-1828* (1965), p. 66 (Google Books `YqJMAAAAMAAJ`, fragmentos), da la misma lista. Cambios en `electos_1827.csv` (certeza `decreto`): Viamont pasa de Chascomús (inferido por la lista N1103, que lo proponía por San Vicente y Cañuelas) a Quilmes; Achega, Otamendi y Rivas dejan de estar «sin sección»; se agregan Viola, Luis Dorrego y Nicolás Anchorena (ninguno votó el 12 de agosto; Luis Dorrego no figura en la Sala). Bancas sin identificar: de 4 a 1, la segunda de Chascomús (la elección de Navarro, devuelta a la mesa central). El voto popular estimado no cambia (59,9 % y 89,6 %), porque estas secciones no tienen votos publicados.

Reservas: la *Crónica* 59 dice que Quilmes no votó el 22 de julio, así que su elección fue después y sin cifras publicadas. El decreto es del 1 de agosto, pero las actas de Arrecifes llegaron a la Sala el 18 (acta de esa sesión, número 2202 del mismo tomo): el Registro pudo completar la lista al compilarse. Son nombres por sección, no votos.

## Partidos sin pueblo en el decreto: estimado (pedido del usuario, 17-nov-2026)
Los partidos de 1869 que no salen de ningún pueblo del decreto se asignan por estimación (`transcripciones/1827/genealogia_1869_1827.csv`, con criterio y fuente por fila); antes quedaban en gris y Monsalvo aparecía suelto:
- **Sur del Salado, a Monsalvo (sección Chascomús)**: Dolores, Castelli, Tordillo, Pila, Ajó, Tuyú, Vecino, Mar Chiquita, Tandil, Lobería, Balcarce, Ayacucho, Arenales, Rauch, Las Flores, y lo de Azul y Tapalqué dentro de la frontera. Base: Cacopardo y Da Orden («Territorio, sociedad y Estado en la Provincia de Buenos Aires: una aproximación desde los mapas, 1830-1890», *Registros* 5, 2008, p. 35, con la Dirección General de Estadística de 1915): hacia 1830, de los 31 partidos, solo Monsalvo abarcaba lo ocupado al sur del Salado. Genealogía de cada uno en el anexo de partidos de la Wikipedia.
- **Rivadavia, a Magdalena (Quilmes)**: el Rivadavia antiguo (1864, Punta Indio) salió de Magdalena y volvió a ella en 1890.
- **Por vecindad** (sin partido de origen en las fuentes; sección con la que comparte más borde): San Andrés de Giles, Bragado, Saladillo y 25 de Mayo a Luján; Chacabuco y Junín a Arrecifes; Las Heras a Chascomús (Navarro).
- Queda sin sección solo la isla Martín García.

Así las once secciones son contiguas (Morón conserva islas del Delta). Son límites de 1869 agrupados, no los de 1827.

## Bordes y costa (17-nov-2026)
Bordes suavizados con topología compartida (`suavizar()` en el build): la red de límites se corta en arcos entre nodos, cada arco se simplifica y se redondea con Chaikin (extremos fijos) una sola vez, y las piezas se reasignan a la cara con más superficie en común: los vecinos no se separan ni se pisan. Costa y límite provincial solo se aligeran. Los recortes chicos entre la frontera georreferenciada y la costa vuelven adentro: la costa es la del shapefile de 1869. Cada sección se recorta a su vista antes de dibujar (HTML de 2,7 MB a ~210 KB).

## Recursos buscados para los límites de 1827 (17-nov-2026)
- **Registro Gráfico de octubre de 1831** (y el de septiembre de 1830), Departamento Topográfico, Archivo de Geodesia del MOP bonaerense (La Plata): según Cacopardo y Da Orden «inscribe una división político-administrativa». Única fuente con partidos dibujados cerca de 1827; no está digitalizado (la lámina del artículo es ilegible).
- **Registro Gráfico de 1833** (Bacle, 4 hojas, ÖAW, CC BY-SA 4.0, IIIF `AC16342027`) y **Parish/Arrowsmith 1836** (David Rumsey 10476.000, georreferenciado): catastrales, sin líneas de partido.
- **Galimberti**, *Anuario IEHS* 36(1), 2021, cuadro 7: votantes por partido rural 1815-1830 agrupados en diez secciones (I San Nicolás, San Pedro, Baradero; II Arrecifes, Pergamino, Salto, S. A. de Areco, F. de Areco, Rojas; III Pilar, Exaltación, Villa de Luján; IV Lobos, Guardia de Luján; V San Fernando, Conchas, Morón, Matanza; VI San Isidro; VII Flores; VIII Magdalena, Quilmes, Ensenada, San Vicente; IX Ranchos, Monte, Chascomús, Navarro, Cañuelas, Monsalvo; X Patagones). No coincide con el decreto de 1827 (San Vicente, Luján): no se usa para las bancas.
- Dmitruk 2017 (*Notas de Población*, padrón de 1827): demográfico, sin límites. Catálogo de la Sala de Representantes 1821-1852 (AHPBA, PDF en Drive): sin leer.

## Selector de listas de la prensa (pedido del usuario, 17-nov-2026)
En «Por lista», el selector «Lista de la prensa» pinta el mapa, el hemiciclo, las barras y el voto estimado con cualquiera de las 14 listas transcriptas: la de «Unos enemigos del Imperio Brasilero» (*Gaceta* 1103, ciudad y campaña, la de siempre) y las 13 de la ciudad de `transcripciones/1827/listas_prensa_1827.csv` (armado por `listas_prensa.py`: candidatos en el orden impreso y a qué electo corresponde cada uno). Enlace directo: `#lis-<id>`, p. ej. `#lis-N1105-6` (Amantes del orden); `#lis` es la lista de siempre.
- Las listas de la ciudad no proponían candidatos de campaña: esas secciones van en gris claro («Campaña, con una lista que solo proponía candidatos por la ciudad»). Un electo de campaña que figuraba en la lista de la ciudad cuenta en la Sala, no en el mapa, y la nota lo marca «(electo por X)».
- Voto estimado de una lista de la ciudad: solo la ciudad, con los votos de sus candidatos que salieron electos. Es el piso de la lista (los votos de sus no electos no se publicaron).
- Lecturas: el «Un Porteño» de la *Gaceta* 1103 tiene 24 nombres (no 21); las dos mitades de la *Gaceta* 1110 son una sola lista de «Unos Porteños» (25 nombres); Manuel H. Aguirre se cuenta como Aguirre de Lajarrota; Bernardo Escalada no se cuenta como electo (nota en el CSV).
- Al pasar el cursor, la ficha compacta de la sección sale junto al cursor; «Sección» quedó debajo de las barras y «Fuentes y notas» se pliega.

## Patagones con el HGIS
La sección de Patagones usa la Comandancia de Patagones del HGIS de las Indias (capa 7, OBJECTID 1580, vigente de 1787 a 1808, es decir la de 1806-07), sin la parte del fuerte San José de la península Valdés, abandonado en 1810. El resto del partido de 1869 va como fuera de la frontera.

## Pendientes y reservas
- Una banca de campaña sin identificar: la segunda de Chascomús (Navarro). Las demás secciones de campaña tienen nombres (decreto 2197), pero no votos.
- Pacheco: Jorge en la *Gaceta* 1114 y la *Crónica* 68; José en la *Crónica* 60.
- Votos de la ciudad que difieren entre la *Gaceta* 1114 y la *Crónica* 68: Maza, del Pino y José María Escalada.
- Límites de partido estimados (ver «Partidos sin pueblo en el decreto»). El Registro Gráfico de 1831 (Archivo de Geodesia, La Plata) los dibuja: pedirlo y calcarlo si se consigue.
- Sin catálogo, PNG para Commons ni commit.
