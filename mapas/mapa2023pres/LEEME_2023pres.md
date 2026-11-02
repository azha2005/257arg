# Presidenciales 2023 · Primera vuelta

Generado con `python comun/atlas_leg2003_2025.py 2023pres`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2023), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2023.txt` del proyecto.
- Mapa: `transferencias\circ_2023p.pkl`, DINE, escrutinio provisorio. Agregado reproducible con `transferencias/agregar_circuitos.py 2023p`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\serieAMBA2005_2023radios\atlas_2023pres.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 528 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Sergio Massa | 9.645.983 | 9.853.492 | -207509 | 325 |
| Javier Milei | 7.884.336 | 8.034.990 | -150654 | 143 |
| Patricia Bullrich | 6.267.152 | 6.379.023 | -111871 | 52 |
| Juan Schiaretti | 1.784.315 | 1.802.068 | -17753 | 8 |
| Myriam Bregman | 709.932 | 722.061 | -12129 | 0 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.



Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
