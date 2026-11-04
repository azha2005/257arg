# Atlas 1937: presidencial

Abrir `atlas_1937.html`. Constructor: `python mapas/mapa1937/build_1937.py`, desde la raíz.

- Dibujo de los mapas de la época: familia publicada 1922/1928 y constructor 1930; departamentos de 1914, veinte circunscripciones de Capital, logos centrados con zoom.
- Votos locales observados de Cantón II, varones solamente. Cobertura: Capital Federal, Córdoba, La Rioja y Tucumán.
- 74 polígonos con datos; 73 filas fuente representadas. Una fila compartida por varios polígonos se suma una sola vez. No confundir ambos recuentos.
- Ganadores por polígono: {'UCR': 58, 'CON': 16}.
- Sin polígono: ninguna fila con votos.
- Cartel nacional de la tabla de Wikipedia, snapshot con revisión en `transcripciones/entreguerras/`; nunca se ajustan los votos locales a esa tabla.
- Faltantes beige, sin elección/renovación gris. Se conservan discrepancias aritméticas de las fuentes.

Método, agrupaciones, cotejos y comandos en [LEEME común](../../transcripciones/entreguerras/LEEME.md). Control geométrico en `CONTROL_ATLAS.json`, datos de presentación en `dataset_1937.json`, topline en `wiki_nacional_1937.json`. Verificación numérica, todos los modos y exportaciones reales en `transcripciones/entreguerras/VALIDACION.json`.

Solo entrega local; sin publicación ni paquetes de Commons.

La selección de Cantón para 1931–1942 es editorial y no certifica ausencia de irregularidades. El atlas es parcial; las provincias sin tabla siguen pendientes.
