# Fuentes para 1936 (diputados nacionales, 1 de marzo de 1936)

## Transcripción iniciada el 5-nov-2026

El relevamiento de fuentes que sigue se conserva como registro del sondeo previo. La lectura visual posterior precisó lo siguiente:

- **Santa Fe:** `santa_fe/candidatos.csv` tiene los 19 departamentos y 21 candidatos por departamento (399 cifras nominales); `totales.csv` conserva votantes, blancos y menciones de otros candidatos. Todos los candidatos, los blancos y los votantes suman el total provincial del acta. Hay resultados finales directos para todos los departamentos: **no hizo falta reconstruirlos restando acumulados**. El principal retiró una lectura errónea de 14 en «otros candidatos» de San Martín: el literal es «M 4», conservado sin normalizar. Ver la reserva y el cotejo condicional en `REVISION.md`.
- **Tucumán:** `tucuman/acta_departamentos.csv` y `circuitos_departamentos.csv` conservan los once colegios electorales, circuitos y totales de sobres del acta, leídos por el principal. `tucuman/celdas.csv` consolida 310 renglones de lectura (mesas, suplementarias y subtotales): 3.313 números, 463 guiones y 564 celdas sin resolver. Las planillas nominales de `parte_a/` y `parte_b/` y la lectura independiente del resumen p102 conservan datos parciales y reservas por recorte/superposición; consultar sus inventarios antes de agregar. No confundir votos por candidato con electores ni reemplazar celdas ilegibles por cero.
- **Tucumán por departamento (5-nov-2026):** `tucuman/departamentos.csv` (de `departamentos.py`), los once colegios × 12 candidatos + nulos y blancos, con fuente y estado por celda. Filas 1-8 del resumen p.102 visibles; Burruyacú, Trancas y Tafí (bajo la banda del escaneo) leídas en p.102 y en el total de cada planilla (p.98, p.99, p.101). **144 de 154 celdas con cifra; los once departamentos de Padrós, Prat Gay, Martínez y López García suman exacto la proclamación de p.103, y Emilio López los 2.506 del PS de la Wikipedia.** Faltan diez: Fioretti, Mendoza Padilla, Lozano Muñoz, Vischi, Fornes, nulos y blancos de Trancas, Fioretti de Tafí y nulos/blancos de Burruyacú (literales dudosos conservados). Aragón suma 26.712, no los 26.755 de la Wikipedia. `celdas_departamento.csv` es la copia de `celdas.csv` con el departamento por página; los circuitos siguen sin asignar. Control en `tucuman/CONTROL_DEPARTAMENTOS.json`.
- **Sondeo visual adicional:** ocho expedientes, 49 páginas, sin nuevas tablas territoriales; alcance en `sondeo_visual/INVENTARIO.md`. Los doce archivos pequeños ausentes no fueron examinados. Jujuy 42-OV y 90-D corresponden a la complementaria del 19 de abril.
- **Revisión:** `REVISION.md` identifica las cifras cotejadas por el principal y las discrepancias que se conservaron. `python transcripciones/1936/verificar.py` regenera `CONTROL.json`, con controles de sumas y SHA256 de las dos fuentes principales. Revisión focal, no segunda lectura integral.
- **Skill del proyecto:** `.agents/skills/transcribir-elecciones/SKILL.md`, creado a partir de este procedimiento. Transcripción local; no se construyeron atlas ni se publicó.

## Relevamiento previo

Relevamiento del 5-nov-2026. Renovaron 11 distritos: Buenos Aires, Capital, Córdoba, Corrientes, Entre Ríos, Jujuy, Mendoza, San Luis, Santa Fe, Santiago del Estero y Tucumán (los de la tabla de `wleg1936.txt`, el wikitext de «Elecciones legislativas de Argentina de 1936»).

**Cantón no publica 1936 por departamento** (lo omite por presunción de fraude); el tomo I trae solo los totales provinciales.

**AGN**: no hay resultados. Ministerio del Interior, Expedientes Generales 1 de 1936, solo logística (ubicación de mesas, convocatorias, custodia de urnas, complementarias); fondo DNE, solo una carpeta de antecedentes provinciales 1935-36.

## Expedientes de la HCDN citados por la Wikipedia
Bajados en `expedientes_hcdn/` (los PDF no van a git).

| Expediente | Distrito | Qué trae | ¿Por departamento? |
|---|---|---|---|
| **26-OV (104 pp.)** | Tucumán | Acta de la Junta Escrutadora: pp. 9-67 circuito por circuito y mesa por mesa (votos del acta y de la urna, con totales por departamento: Capital, Monteros, Chicligasta, Graneros, Leales, Burruyacú, Trancas…); **pp. 72-102, planillas impresas mesa por mesa con los votos de cada candidato** (Concordancia, UCR lista Laprida 147, UCR lista 24 de Setiembre 460, Partido Socialista), nulos y blancos. | **Sí, por mesa.** Hay que sumarla por departamento. |
| 48-D (26 pp.) | Buenos Aires | Acta general impresa de la Junta (3-abr-1936): totales por candidato y un informe largo sobre el fraude, partido por partido (mesas sin fiscales, presidentes sustituidos, vuelco de padrones; p. ej. Balcarce: 81 votos opositores contra 2.800). | Solo menciones sueltas; no hay tabla. |
| 42-D (27 pp.) | Mendoza | Acta de escrutinio mecanografiada, larga, con impugnaciones. | Por ver: es texto corrido. |
| 41-D (6 pp.) | Corrientes | Acta general impresa (elección del 1.º y complementaria del 15 de marzo); nombra mesas anuladas por departamento. | No. |
| 30-D, 28-D, 32-D, 11-D, 25-D, 24-D (4-6 pp.) | Córdoba, Entre Ríos, Santa Fe, Capital, San Luis, Mendoza | Diploma y acta con totales. | No. |
| 42-OV (10 pp.), 62-D (10 pp.) | Jujuy, Santiago del Estero | Acta (Santiago del Estero manuscrita). | No. |

## Expedientes no citados (sondeo del 5-nov-2026)
`sondeo_raw.txt`: 186 expedientes `n-d-1936` (1-140) y `n-ov-1936` (1-70) responden; 24 no existen. Se bajaron los más pesados y se buscó en la capa de texto (OCR del PDF), sin mirar página por página:

| Expediente | Qué es | ¿Votos por unidad? |
|---|---|---|
| **29-OV (104 pp.)** | Santa Fe: acta de la Junta Escrutadora Nacional (3-abr-1936) | **Sí, por departamento.** Va departamento por departamento («El Departamento San Lorenzo… arrojó los siguientes cómputos») con los votos de cada candidato, blancos y votantes; algunos tramos dan totales acumulados (Belgrano, Caseros, Castellanos y Constitución juntos; La Capital sumada a lo anterior), que se separan por diferencia. OCR malo: transcribir de la imagen. |
| 64-D y 65-D (27-28 pp.) | Mendoza: copias del acta de escrutinio (11-12 de marzo) | Solo totales por candidato y mesas anuladas. |
| 32-OV y 92-D | Buenos Aires: copias del acta general impresa | Solo totales e informe de fraude. |
| 35-OV, 10-OV, 4-D, 94-D, 106-D, 126-D, 136-D | Asuntos oficiales varios | No electorales. |
| 96-D (188 pp., 308 MB) | Asuntos constitucionales | No electoral. |

Nota: la Wikipedia enlaza «24-D-1936» al PDF del 42-D; los dos están bajados.

## Siguiente
- Transcribir Tucumán 26-OV, pp. 72-102 (mesa por mesa, con circuito → departamento de las pp. 9-67).
- Transcribir Santa Fe 29-OV por departamento (19 departamentos).

## Todos los expedientes de 1936 (revisión del 5-nov-2026)
Se bajaron los 174 de más de 3 MB y se buscó en su texto (capa OCR del PDF) votos, mesas, circuitos, departamentos, escrutinio y diplomas: `indice_expedientes.tsv`. Resultado:
- **Solo 26-OV (Tucumán) y 29-OV (Santa Fe) traen votos por unidad.**
- Unos 75 son diplomas de diputados electos con el acta resumida (totales del distrito). Los de Buenos Aires (46-D a 92-D, 32-OV) son copias del mismo acta general impresa, con el informe del fraude.
- 95 no son electorales.
- Límite: algunos de 4-10 páginas (San Luis, Jujuy, Tucumán 17-D) son manuscritos sin texto reconocible; por la extensión no pueden traer cuadros departamentales completos, pero no se miraron. Tampoco se bajaron los 12 de menos de 3 MB.

## Otras fuentes buscadas
- **Hemeroteca Digital de Santa Fe** (*El Orden*, *El Litoral*, marzo de 1936): fuera de servicio (HTTP 503). La Wayback Machine tiene las páginas de los ejemplares, pero no las imágenes, que el visor carga aparte. Volver a probar cuando vuelva: es la mejor fuente para Santa Fe y para resúmenes de otras provincias.
- **Memorias del Ministerio del Interior**: en Commons/Wikisource (Academia Nacional de la Historia) llegan hasta 1928.
- **Internet Archive**: nada de 1936. **HathiTrust** bloquea pedidos automáticos; desde el navegador, la búsqueda en texto completo sirve para ubicar páginas de Memorias o del Diario de Sesiones 1936 aunque estén en «solo búsqueda».
- **Capital**: Cantón y Jorrat, *Elecciones en la ciudad*, t. II (1912-1973), por sección; solo en papel. También su artículo «Continuidad y cambio en las elecciones de la Capital Federal: 1931-1954».
- **Diario de Sesiones 1936, t. I** (sesiones preparatorias, abril): Biblioteca del Congreso; la biblioteca de la DNE solo tiene el t. II.
- **AGN**: sin resultados (ver arriba).
- Capital: Cantón y Jorrat; Buenos Aires: prensa (*El Orden* 11 y 12-mar-1936 en la Hemeroteca Digital de Santa Fe).
