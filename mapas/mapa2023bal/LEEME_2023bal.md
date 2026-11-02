# Presidenciales 2023 · Segunda vuelta

Generado con `python comun/atlas_leg2003_2025.py 2023bal`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2023), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2023.txt` del proyecto.
- Mapa: `transferencias\circ_2023b.pkl`, DINE, escrutinio provisorio. Agregado reproducible con `transferencias/agregar_circuitos.py 2023b`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico. Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\serieAMBA2005_2023radios\atlas_2023bal.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 528 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Javier Milei | 14.482.133 | 14.554.560 | -72427 | 356 |
| Sergio Massa | 11.522.645 | 11.598.720 | -76075 | 172 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.

- Antofagasta de la Sierra: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 014, Antofagasta de la Sierra, 7 mesas, categoría Presidente y Vice. Archivo 2023_catamarca_s014.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (1800): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Telsen: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 003, Telsen, 5 mesas, categoría Presidente y Vice. Archivo 2023_chubut_s003.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (1418): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Gastre: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 004, Gastre, 5 mesas, categoría Presidente y Vice. Archivo 2023_chubut_s004.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (1134): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Florentino Ameghino: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 011, Florentino Ameghino, 5 mesas, categoría Presidente y Vice. Archivo 2023_chubut_s011.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (1519): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Valle Grande: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 008, Valle Grande, 14 mesas, categoría Presidente y Vice. Archivo 2023_jujuy_s008.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (2906): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Susques: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 016, Susques, 14 mesas, categoría Presidente y Vice. Archivo 2023_jujuy_s016.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (3479): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Curacó: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 009, Curacó, 3 mesas, categoría Presidente y Vice. Archivo 2023_lapampa_s009.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (892): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.
- Santa Victoria: CNE, consulta de escrutinio definitivo por zona del 19/11/2023, sección completa 010, Santa Victoria, 35 mesas, categoría Presidente y Vice. Archivo 2023_salta_s010.xls; consulta del 2-nov-2026 con localidad y circuito en blanco. Inscriptos (8231): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.

Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
