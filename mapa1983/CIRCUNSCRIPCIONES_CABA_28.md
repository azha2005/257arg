# Circunscripciones electorales de la Ciudad de Buenos Aires (28)

Fuente: Anuario Estadístico 2009 de la Ciudad de Buenos Aires, p. 14, mapa de circunscripciones electorales
(https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2015/04/anuario_estadistico_2009.pdf).
La base de Ernesto Calvo numera Capital Federal del 1 al 28; el número se asigna con esta tabla.

1 Vélez Sársfield · 2 San Cristóbal Sud · 3 Santa Lucía · 4 San Juan Evangelista · 5 Flores · 6 San Carlos Sud · 7 San Carlos Norte ·
8 San Cristóbal Norte · 9 Balvanera Oeste · 10 Balvanera Sud · 11 Balvanera Norte · 12 Concepción · 13 Montserrat · 14 San Nicolás ·
15 San Bernardo · 16 Belgrano · 17 Palermo · 18 Las Heras · 19 Pilar · 20 Socorro · 21 San Vicente de Paul · 22 Villa Lugano ·
23 Cristo Obrero · 24 Versalles · 25 San Luis Gonzaga · 26 San José · 27 Nuestra Señora del Carmen · 28 Saavedra

Las 20 primeras coinciden con la numeración que usa Lupu–Stokes (dcode 2000-2020) y con la de nuestras tablas de Cantón.

## Ajuste de la geometría (octubre de 2026)
`caba28.py` ya no usa el ajuste simple por cajas envolventes (IoU 0,869 con el contorno del shapefile de 1980): aplica una escala (0,915 en x, 1,008 en y), un giro mínimo y un desplazamiento hacia el oeste que dan IoU 0,941, recorta las circunscripciones contra el contorno real de Capital y reparte entre las vecinas lo que queda sin cubrir. Los límites internos siguen siendo los del dibujo de Wikipedia (aproximados); el contorno exterior es el del shapefile.
