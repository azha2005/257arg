# Atlas 1926: diputados nacionales

Abrir `atlas_1926.html`. Constructor: `python mapas/mapa1926/build_1926.py`, desde la raíz.

- Dibujo de los mapas de la época: familia publicada 1922/1928 y constructor 1930; departamentos de 1914, veinte circunscripciones de Capital, logos centrados con zoom.
- Votos locales observados de Cantón II, varones solamente. Cobertura: 14 distritos; San Luis no renovó diputados.
- 347 polígonos con datos; 341 filas fuente representadas. Una fila compartida por varios polígonos se suma una sola vez. No confundir ambos recuentos.
- Ganadores por polígono: {'UCR': 160, 'IND': 1, 'CON': 76, 'PS': 2, 'ANT': 31, 'DIS': 8, 'LEN': 16, 'BLO': 16, 'UNIF': 37}.
- Sin polígono: [{'prov': 'Santiago del Estero', 'unidad': 'Alberdi', 'pagina_pdf': 102, 'votos': 155}].
- Cartel nacional de la tabla de Wikipedia, snapshot con revisión en `transcripciones/entreguerras/`; nunca se ajustan los votos locales a esa tabla.
- Faltantes beige, sin elección/renovación gris. Se conservan discrepancias aritméticas de las fuentes.

Método, agrupaciones, cotejos y comandos en [LEEME común](../../transcripciones/entreguerras/LEEME.md). Control geométrico en `CONTROL_ATLAS.json`, datos de presentación en `dataset_1926.json`, topline en `wiki_nacional_1926.json`. Verificación numérica, todos los modos y exportaciones reales en `transcripciones/entreguerras/VALIDACION.json`.

Solo entrega local; sin publicación ni paquetes de Commons.
