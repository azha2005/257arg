# Presidenciales 2015 · Segunda vuelta

Generado con `python comun/atlas_leg2003_2025.py 2015bal`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2015), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2015.txt` del proyecto.
- Mapa: `transferencias\circ_2015b.pkl`, DINE, escrutinio provisorio. Agregado reproducible con `transferencias/agregar_circuitos.py 2015b`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\serieAMBA2005_2023radios\atlas_2015bal.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 527 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Daniel Scioli | 12.217.308 | 12.309.575 | -92267 | 297 |
| Mauricio Macri | 12.907.377 | 12.988.349 | -80972 | 230 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.

- Antofagasta de la Sierra: CNE, consulta de escrutinio definitivo por zona del 22/11/2015, sección completa 014, Antofagasta de la Sierra, 4 mesas, categoría Presidente y Vice. Archivo 2015_catamarca_s014.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (1199): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Valle Grande: CNE, consulta de escrutinio definitivo por zona del 22/11/2015, sección completa 008, Valle Grande, 12 mesas, categoría Presidente y Vice. Archivo 2015_jujuy_s008.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (2642): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Rivadavia: CNE, consulta de escrutinio definitivo por zona del 22/11/2015, sección completa 006, Rivadavia, 76 mesas, categoría Presidente y Vice. Archivo 2015_salta_s006.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (22850): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Santa Victoria: CNE, consulta de escrutinio definitivo por zona del 22/11/2015, sección completa 010, Santa Victoria, 33 mesas, categoría Presidente y Vice. Archivo 2015_salta_s010.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (7896): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.

Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
