# La Época, abril de 1916 (NewspaperARCHIVE vía Wikipedia Library)

Fuente nueva para San Juan y Santiago del Estero 1916. *La Época* (diario yrigoyenista, Buenos Aires) está en NewspaperARCHIVE de 1915 a 1924; abril de 1916 completo salvo el 9. Acceso por la Wikipedia Library (proxy `access-newspaperarchive-com.wikipedialibrary.idm.oclc.org`, sesión del usuario en su Chrome). El mismo sitio tiene *La Prensa* 1857–1928 con el 3, 5 y 14 de abril de 1916 (los que fallaban en Archive.org).

Las cifras se leen en la imagen, no en el OCR. Cada recorte queda en `img/`, **fuera de git** (`.gitignore`): los términos de NewspaperARCHIVE prohíben redistribuir su contenido (uso personal no comercial) y los de la Wikipedia Library prohíben el scraping y la descarga automática. Se lee ejemplar por ejemplar en el visor, a mano; las cifras transcriptas sí van al repositorio. Para citar, usar un *clipping* del sitio (enlace de acceso abierto, como recomienda la Library).

**Cómo buscar:** la búsqueda del sitio (`/tags/?...&pt=19914&ndt=by&py=1916&pey=1916&pep=<frase>`, publicación La Época, año 1916) encuentra los telegramas por su encabezado («san-juan-abril», «santiago-del-estero-abril») o por un nombre poco común («desamparados», «chimbas»). El OCR pierde algunos encabezados (el del 5-abr salió solo buscando «Desamparados»). La caja «Find on page» del visor busca **solo en la página abierta**.

## San Juan

### Capital (4-abr, p. 1 y p. 4)

Telegrama del 3-abr (p. 4): «Esta noche se escrutaron dos distritos que faltaban de la ciudad, obteniéndose el siguiente resultado». El cuadro de la p. 1, «SAN JUAN (Capital)», trae las mismas cifras completas. Se lee como el departamento Capital terminado. Reserva: el telegrama agrega «los radicales llevan una mayoría de 263 votos», y 1132 − 873 = 259.

| Diputados | Votos |
|---|---:|
| M. V. Quiroga, radical | 1132 |
| A. de la Rosa Ponte, radical | 1112 |
| R. Vidart, conservador | 873 |
| H. C. Videla, conservador | 836 |
| A. Cantoni, socialista | 78 |
| F. Soldati, socialista | 76 |

Electores: radicales 1132, concentración 873, socialista 78. Imagen: `img/1916-04-04_p1_sanjuan_capital.png`.

### Chimbas y Desamparados, parcial (5-abr, p. 4)

Telegrama del 5-abr: «Escrutóse la urna de Chimbas, que tiene los sellos rotos por descuido, dando 54 votos a los oficialistas y 84 a los radicales. Escrutáronse tres mesas de Desamparados, dando la primera 51 oficialistas y 88 radicales; 2.a, oficialistas 60 y 90 radicales; 3.a, empate, 76 por 76. Mañana se seguirá el escrutinio de Desamparados.»

| Unidad | Oficialistas (concentración) | Radicales | Nota |
|---|---:|---:|---|
| Chimbas (urna) | 54 | 84 | ¿única urna del departamento? Cantón (Apéndice C) pone Chimbas dentro de Concepción |
| Desamparados, mesa 1 | 51 | 88 | |
| Desamparados, mesa 2 | 60 | 90 | |
| Desamparados, mesa 3 | 76 | 76 | |
| Desamparados, 3 mesas | 187 | 254 | parcial; el resto, el 6-abr (sin hallar) |

Sin columna socialista ni nombre de candidato: «oficialistas» y «radicales» son las dos listas.

### Grupo de cinco departamentos (7-abr, p. 1)

Telegrama del 7-abr, 1.35 a. m.: «Continuó el escrutinio de las mesas de Caucete, 25 de Mayo, Angaco Sud, Albardón y Ullum, dando el total de 1955 votos para la concentración oficialista y 1406 para los radicales.»

Restando Caucete según La Prensa (862 C / 475 R, `../laprensa_abril1916/RECONSTRUCCION_SANJUAN.md`) quedan 1093 C / 931 R para 25 de Mayo + Angaco Sud + Albardón + Ullum. Es cerca de la diferencia C − B de La Prensa (+1087 / +948), que no incluía Ullum. Que el total incluya Caucete entero no es seguro.

Misma página, cómputo provincial: Vidart 6658, Videla 6595, Quiroga 5771, de la Rosa Ponte 5719; electores concentración 6642, radicales 5734.

### Provincia (8 y 18-abr)

- 8-abr, p. 16 (cierre provisional): Vidart 9057, Videla 8982, electores 9019; Quiroga 7626, de la Rosa Ponte 7562, electores 7609; socialistas 382.
- 18-abr, p. 4: urna anulada del Alto de la Sierra: Quiroga 115, de la Rosa Ponte 115, electores radicales 115; Videla 80, Vidart 80, electores concentración 80. Proclamación con el escrutinio definitivo, igual al acta (Vidart 9244, Videla 9170, Quiroga 7742, de la Rosa Ponte 7697, Cantoni 383, Soldati 381).

## Santiago del Estero

Revisados el 7-abr (p. 16) y el 12-abr (p. 2): igual que en La Prensa, cuentas por tandas de mesas («resultados en siete mesas escrutadas») y diferencias provinciales, **sin departamentos**. Quedan otros 13 telegramas sin abrir (2, 11, 12, 14, 15 y 17-abr), pero los resúmenes no muestran cifras departamentales.

## Pendiente
- Telegramas de San Juan del 6-abr (resto de Desamparados y lo que se escrutó ese día): hay que recorrer las páginas del ejemplar una por una porque el OCR no encuentra el encabezado.
- La Prensa del 3, 5 y 14-abr en NewspaperARCHIVE.
- Decidir con el usuario si Capital (completo) entra al atlas y cómo se rotulan los parciales.
