# Presidenciales 2015 · Primera vuelta

Generado con `python comun/atlas_leg2003_2025.py 2015pres`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2015), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2015.txt` del proyecto.
- Mapa: `transferencias\circ_2015p.pkl`, DINE, escrutinio provisorio. Agregado reproducible con `transferencias/agregar_circuitos.py 2015p`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\serieAMBA2005_2023radios\atlas_2015pres.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 527 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Daniel Scioli | 9.002.242 | 9.338.490 | -336248 | 330 |
| Mauricio Macri | 8.382.610 | 8.601.131 | -218521 | 171 |
| Sergio Massa | 5.211.705 | 5.386.977 | -175272 | 19 |
| Nicolás del Caño | 798.031 | 812.530 | -14499 | 0 |
| Margarita Stolbizer | 619.051 | 632.551 | -13500 | 0 |
| Adolfo Rodríguez Saá | 407.202 | 412.578 | -5376 | 7 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.



Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
