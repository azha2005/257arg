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

## Frontera de 1826 (pedido del usuario, 17-nov-2026)
`geometria/frontera_bsas_1827/`: la línea de 1826 sale del mapa escolar de avance de la frontera que aportó el usuario (`avance_frontera_mapa_escolar.png`, autor sin identificar). `frontera.py` separa por color las bandas hasta 1826 y `georef.py` las georreferencia con ocho ciudades (ajuste afín, residuos de 6 km o menos) → `frontera_1826_mapa_escolar.geojson`. El mapa tapa el noreste con texto y ríos: se une a la jurisdicción de Buenos Aires de 1788 del HGIS de las Indias (capa 7, OBJECTID 1768, CC BY-NC-SA; `hgis_indias_jurisdicciones_1787_1788.geojson`). El polígono de Patagones del HGIS llega a 43° S y no se usa: Patagones usa la Comandancia del HGIS (ver abajo).

En el atlas, las secciones se recortan a ese territorio (Arrecifes pierde 12 % hacia el oeste; Morón y Luján 1-2 %); dentro de la frontera y sin sección, gris oscuro; la provincia de 1869 fuera de la frontera, gris claro; la línea, punteada. Es una línea de escala escolar, no un trazado documental.

## Diario de Sesiones, tomo 2 (17-nov-2026)
La Hemeroteca Digital de la BNMM tiene el *Diario de Sesiones de la H. Junta de Representantes* de 1827 desde el número 21 (29 de septiembre); el tomo 1 (números 1 a 18, agosto y septiembre), que cita Galimberti para San Nicolás, no está digitalizado (en papel en la biblioteca del AGN). Del tomo 2 salen:

- **Arrecifes**: Luis Saavedra («electo representante de Arrecifes», aprobado el 12 de septiembre, incorporado el 20 de octubre, número 29) y José María Baudriz («electo representante por el partido de S. Antonio de Areco», renuncia admitida el 2 de octubre, número 22). Los dos iban en la lista de la *Gaceta* 1103.
- **Patagones**: José María Rojas, «por pluralidad de sufragios», sin cifras (acta leída el 3 de octubre, número 23). La lista no proponía a nadie por Patagones.
- Los tres no votaron al gobernador: categoría «Incorporado después» en ese modo. Bancas sin identificar: de 7 a 4.
- Desde fines de septiembre se sientan también **Anchorena** y **Viola**, de sección desconocida; no se cuentan (Nicolás Anchorena iba en la lista por Chascomús, pero no hay acta).
- La ciudad tuvo una elección complementaria de dos representantes en septiembre-octubre, con una mesa por parroquia (Catedral, Colegio, San Nicolás, Concepción, Socorro...); la mesa central la declaró nula el 15 de octubre por irregularidades en la Concepción. No se publican votos (números 21 y 29).
- Los PDF quedan fuera del repo (dominio público, en la Hemeroteca: `render.php?url=000981043/1827/BNA_S000981043_<fecha>N000<nn>.pdf`).

## Patagones con el HGIS
La sección de Patagones usa la Comandancia de Patagones del HGIS de las Indias (capa 7, OBJECTID 1580, vigente de 1787 a 1808, es decir la de 1806-07), sin la parte del fuerte San José de la península Valdés, abandonado en 1810. El resto del partido de 1869 va como fuera de la frontera.

## Pendientes y reservas
- Siete bancas de campaña sin identificar: Pilar, Arrecifes, Chascomús, Quilmes y Patagones. Achega, Otamendi y Rivas están en la Sala sin sección conocida.
- Arraga (Pilar) y Viamont (Chascomús) son inferidos. Wright (Quilmes) es dudoso: Quilmes no votó el 22 de julio.
- Pacheco: Jorge en la *Gaceta* 1114 y la *Crónica* 68; José en la *Crónica* 60.
- Votos de la ciudad que difieren entre la *Gaceta* 1114 y la *Crónica* 68: Maza, del Pino y José María Escalada.
- Monsalvo (1869) queda separado del resto de la sección de Chascomús.
- Sin catálogo, PNG para Commons ni commit.
