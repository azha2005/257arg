# Atlas presidencial de 1886

`"C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/mapa1886/build_1886.py`. Visor, proyección y plantilla del atlas de 1874. Departamentos del censo de 1895 y la Capital con las 14 parroquias de 1872-1886.

## Dos modos para la Capital

- **P.U.**: versión de los Partidos Unidos (los coaligados).
- **POLICÍA**: versión de la policía, que favorece a los juaristas.

La fuente es el CD de Cantón y Jorrat, planilla 11 (`CF1886PRV.xls`, exportada a `capital_1886.csv`), que la toma de *El Diario* del 12 de abril de 1886 «a pesar de sus inconsistencias». En las parroquias con mesas dobles cada versión computa solo la mesa de su bando. Esas parroquias van en tono claro, con la cifra y sin porcentaje. San Cristóbal no trae cifras en la versión policial.

El recorte aportado por el usuario (`img/recorte_provincia_capital_1886.webp`) trae el mismo cuadro. Leído en la imagen de baja resolución daba varias cifras distintas (por ejemplo San Miguel 304 en vez de 394), así que se usó la planilla del CD.

## Provincia de Buenos Aires por partido

Viene del mismo recorte: «El resultado de las elecciones del Domingo en la Provincia», datos del comité rochista (c = coaligados, j = juaristas). Transcripción en `provincia_1886.csv`.

- 71 filas. Tres dicen «no hubo»: Bolívar, Lomas de Zamora y Maipú. Patagones figura sin cifras.
- Las filas suman **21.773 coaligados y 3.043 juaristas**; el diario imprime 21.070 y 3.028. La imagen es de baja resolución: algún dígito puede estar mal leído (Chacabuco 802 explicaría casi toda la diferencia si fuera 102). No se ajustó. **Conviene cotejar con un escaneo mejor.**
- Merlo: el primer dígito de los coaligados es poco legible.
- Alias con el mapa de 1895: Ajó es General Lavalle, Ranchos es General Paz, Juárez es Benito Juárez, Suárez es Coronel Suárez, etc. (ver `ALIAS`).
- Belgrano y San José de Flores se anexaron a la Capital en 1887: toman el polígono de 1869, recortado.
- Ensenada (530 c, 6 j) no tiene polígono propio en 1895 y va en la nota.
- Los partidos que no figuran en el recorte quedan en beige.

## Resto del país

Cada provincia lleva, en tono claro, el color de quien ganó sus electores según la Wikipedia:

- Juárez Celman: 168 electores en total, incluidos los 22 de la Capital.
- Partidos Unidos: Buenos Aires (31, Ocampo) y Tucumán (13 Irigoyen y 1 Ocampo).
- Salta no votó.

**San Luis**: un telegrama del corresponsal del 13 de abril (aportado por el usuario) estima en la ciudad más de 800 votantes de los Partidos Unidos y unos 500 juaristas. Todas las mesas eran juaristas, la elección fue protestada y el resultado fue favorable a Juárez Celman. Va en la ficha del departamento La Capital, sin porcentaje y fuera de la torta.

## Torta

Suma el total impreso de la provincia de Buenos Aires y la Capital en la versión del modo elegido:

- **Versión P.U.**: PU 28.074, Juárez Celman 6.988 (80,1 %).
- **Versión policial**: PU 26.376, Juárez Celman 11.633 (69,4 %).

Juárez Celman ganó el colegio electoral con 168 electores.
