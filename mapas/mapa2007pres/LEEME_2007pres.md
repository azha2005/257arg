# Presidenciales 2007 · Primera vuelta

Generado con `python comun/atlas_leg2003_2025.py 2007pres`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2007), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2007.txt` del proyecto.
- Mapa: `transferencias\circ_2007p.pkl`, PolAr / Atlas Electoral de Andy Tow. Agregado reproducible con `transferencias/agregar_polar_circuitos.py 2007p`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2001 y 28 circunscripciones de Capital Federal (ajustadas al contorno). Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\serieAMBA2005_2023radios\atlas_2007pres.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 539 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Cristina Fernández de Kirchner | 8.478.219 | 8.652.293 | -174074 | 467 |
| Elisa Carrió | 4.313.306 | 4.403.642 | -90336 | 41 |
| Roberto Lavagna | 3.178.380 | 3.230.236 | -51856 | 15 |
| Alberto Rodríguez Saá | 1.459.551 | 1.459.174 | +377 | 13 |
| Fernando Solanas | 302.539 | 301.543 | +996 | 0 |
| Ricardo López Murphy | 274.927 | 273.406 | +1521 | 0 |
| Jorge Sobisch | 302.427 | 268.401 | +34026 | 3 |
| Vilma Ripoll | 145.268 | 142.528 | +2740 | 0 |
| Néstor Pitrola | 119.098 | 116.688 | +2410 | 0 |
| José Montes | 107.569 | 84.694 | +22875 | 0 |
| Luis Ammann | 82.856 | 69.787 | +13069 | 0 |
| Raúl Castells | 59.526 | 48.878 | +10648 | 0 |
| Gustavo Breide Obeid | 47.364 | 45.318 | +2046 | 0 |
| Juan Ricardo Mussa | 11.661 | 10.558 | +1103 | 0 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.
La suma de candidatos de la propia tabla de Wikipedia difiere en +6 de sus positivos declarados. Se conservan las cifras de la tabla.

- Sarmiento: DINE, escrutinio definitivo, Sgo_Estero_28_Oct_07.pdf, página 31, columna PRESIDENTE Y VICE, TOTAL ambos sexos. Tabla cotejada visualmente: 1424 positivos, 38 blancos, 5 nulos, 1467 votantes y 2615 electores. Sobisch suma MPU 10, MAV 4 y Unión Popular 2. Reemplaza íntegramente el registro dudoso de PolAr (PO 2000, FPV 193), sin corregirlo por residuo ni imputar votos.
- Valle Grande: DINE, escrutinio definitivo, Jujuy_28_Oct_07.pdf (copia archivada), página 15, columna PRESIDENTE Y VICE, ambos sexos. Sobisch suma MPU y MAV (1 voto cada uno).

Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
