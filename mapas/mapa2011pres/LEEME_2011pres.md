# Presidenciales 2011 · Primera vuelta

Generado con `python comun/atlas_leg2003_2025.py 2011pres`.

- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_2011), snapshot `datos\fuentes_leg2003_2025\presidenciales\wpres2011.txt` del proyecto.
- Mapa: `transferencias\circ_2011p.pkl`, DINE, escrutinio provisorio. Agregado reproducible con `transferencias/agregar_circuitos.py 2011p`. Son votos observados; no se calibran al total de Wikipedia.
- Geometría: Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado. Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.
- Logos y colores: `mapas\serieAMBA2005_2023radios\atlas_2011pres.html`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.
- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.
- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.

Cobertura: 527 unidades con positivos. Pendientes: ninguna.

| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |
|---|---:|---:|---:|---:|
| Cristina Fernández de Kirchner | 11.594.489 | 11.865.055 | -270566 | 506 |
| Hermes Binner | 3.624.545 | 3.684.970 | -60425 | 10 |
| Ricardo Alfonsín | 2.395.329 | 2.443.016 | -47687 | 0 |
| Alberto Rodríguez Saá | 1.714.394 | 1.745.354 | -30960 | 9 |
| Eduardo Duhalde | 1.264.619 | 1.285.830 | -21211 | 2 |
| Jorge Altamira | 497.085 | 503.372 | -6287 | 0 |
| Elisa Carrió | 396.177 | 399.685 | -3508 | 0 |

Las diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.

- Entre Ríos: subsección 002 sumada a 001.
- Santa Fe: subsección 010 sumada a 009.
- Santa Fe: subsección 014 sumada a 013.
- Santa Fe: subsección 015 sumada a 013.
- Valle Grande: DINE, escrutinio definitivo, resultados_nacionales_2011_jujuy.pdf (copia archivada), página 10, columna PV. No incluye exterior ni privados de libertad; padrón definitivo de la sección: 2360.

Atlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.
