# Presidenciales 2003 · Primera vuelta

Generado con `python comun/atlas_leg2003_2025.py 2003pres`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2003), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2003.txt` del proyecto.
- Mapa: `transferencias\circ_2003p.pkl`, PolAr / Atlas Electoral de Andy Tow. Agregado reproducible con `transferencias/agregar_polar_circuitos.py 2003p`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2001 y 28 circunscripciones de Capital Federal (ajustadas al contorno). Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\mapaAMBA2003radios\atlas_amba2003radios.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 539 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Carlos Menem | 4.779.482 | 4.741.200 | +38282 | 286 |
| Néstor Kirchner | 4.296.229 | 4.313.131 | -16902 | 151 |
| Ricardo López Murphy | 3.185.919 | 3.173.584 | +12335 | 35 |
| Adolfo Rodríguez Saá | 2.820.057 | 2.736.091 | +83966 | 57 |
| Elisa Carrió | 2.782.851 | 2.723.207 | +59644 | 10 |
| Leopoldo Moreau | 466.315 | 453.373 | +12942 | 0 |
| Patricia Walsh | 347.234 | 332.703 | +14531 | 0 |
| Alfredo Bravo | 225.153 | 217.387 | +7766 | 0 |
| Jorge Altamira | 148.882 | 139.402 | +9480 | 0 |
| Enrique Venturino | 152.097 | 129.782 | +22315 | 0 |
| Guillermo Sullings | 111.984 | 105.705 | +6279 | 0 |
| José Carlos Arcagni | 69.296 | 63.384 | +5912 | 0 |
| Mario Mazzitelli | 54.596 | 50.303 | +4293 | 0 |
| Carlos Zaffore | 53.437 | 47.954 | +5483 | 0 |
| Manuel Herrera | 53.717 | 47.755 | +5962 | 0 |
| Gustavo Breide Obeid | 51.914 | 42.461 | +9453 | 0 |
| Juan Ricardo Mussa | 43.825 | 39.507 | +4318 | 0 |
| Ricardo Terán | 36.683 | 31.766 | +4917 | 0 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.

- Rinconada: dat.ar, categoría Presidente, Jujuy/Rinconada. Las listas suman los 824 positivos declarados y cierran con 880 votantes; sin padrón publicado. Menem incluye UCeDé; Rodríguez Saá, Unión y Libertad; Arcagni, Unión Popular.
- Valle Grande: dat.ar, categoría Presidente, Jujuy/Valle Grande. Las listas suman los 1325 positivos declarados y cierran con 1339 votantes; sin padrón publicado. Menem incluye UCeDé; Rodríguez Saá, Unión y Libertad; Arcagni, Unión Popular.

Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
