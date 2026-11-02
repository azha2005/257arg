# Presidenciales 2019 · Primera vuelta

Generado con `python comun/atlas_leg2003_2025.py 2019pres`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2019), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2019.txt` del proyecto.
- Mapa: `transferencias\circ_2019p.pkl`, DINE, escrutinio provisorio. Agregado reproducible con `transferencias/agregar_circuitos.py 2019p`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\serieAMBA2005_2023radios\atlas_2019pres.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 528 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Alberto Fernández | 12.474.255 | 12.946.037 | -471782 | 385 |
| Mauricio Macri | 10.471.056 | 10.811.586 | -340530 | 143 |
| Roberto Lavagna | 1.599.718 | 1.649.322 | -49604 | 0 |
| Nicolás del Caño | 561.223 | 579.228 | -18005 | 0 |
| Juan José Gómez Centurión | 443.513 | 457.956 | -14443 | 0 |
| José Luis Espert | 382.827 | 394.207 | -11380 | 0 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.

- Antofagasta de la Sierra: CNE, consulta por zona descargada manualmente por el usuario; localidad 0032, que cubre la sección 14. Columna PRESIDENTE Y VICE: 1127 votantes, cinco mesas. Sin inscriptos en la planilla: no se calcula participación.

Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
