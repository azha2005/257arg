# Atlas de retiradas presidenciales de 2003

18 HTML autocontenidos, generados el 31-oct-2026. Abrir `index.html` para elegir la retirada inicial. Cada HTML incluye selectores para cambiar candidatura retirada, modelo, referencia/primera/segunda vuelta, candidato de la coropleta, pareja de balotaje, corte temporal de encuestas y supuestos de exclusión.

**Revisión por el efecto de bloques provinciales:** el valor predeterminado es ahora «Ajuste local». Condiciona el prior nacional de cada matriz a los márgenes de cada departamento/circunscripción en 1999 y 2003. Hay antecedente 1999 compatible con el cruce validado en 528 de 537 unidades; los nueve casos restantes se advierten en sus fichas. Para el libro 2001 no hay margen local de sus ocho categorías: se conserva esa reserva. No se introdujo variación estética ni se forzó un ganador. «Provincial uniforme: comparación» conserva la primera formulación como sensibilidad, no como resultado principal.

**Son simulaciones condicionales.** La segunda preferencia no está identificada por el origen histórico del voto. La leyenda solo incluye ganadores territoriales; los demás candidatos permanecen en las fichas y en Otros de la torta. Los menores usan perfiles agregados y llevan asterisco. El título, las notas y el SVG exportado identifican la simulación y el modelo.

Base de estilo y geometría: `../mapa2003/atlas_2003.html` y su dataset, departamentos de 2001 más 28 circunscripciones de Capital y los siete recuadros del proyecto. Se reutiliza su SVG; **sus datos legislativos se sustituyen por presidenciales 2003 de PolAr**. No se modifica el atlas original.

537 unidades con datos, incluida la Antártida separada. Rinconada y Valle Grande (Jujuy) tienen cero votos en todas las opciones de PolAr y quedan beige como pendientes. Malvinas queda gris. San Rafael conserva votos por candidato, pero su abstención local es no verificable: los emitidos de PolAr superan en 236 al padrón. No se imputa. Los totales nacionales parten de la tabla de Wikipedia conservada en el proyecto, con calibración territorial explícita por candidato.

Modelos: Sankey jerárquico 1999 → 2003 del proyecto, variante nacional Calvo y estimaciones del libro de Calvo y Escolar (2005) con orígenes 1999 y 2001. Las encuestas anteriores al 27 de abril se separan de las de mayo. Los cruces posteriores 2003 → 2005/2007/2009 solo se muestran como contraste en el simulador.

Los logos PJ, Recrear y ARI se reutilizan del atlas de 2003, con sus metadatos ya registrados en `../../logos/LICENCIAS.md`. FPV y MNP llevan sigla, al igual que los menores sin emblema incorporado. La geometría, leyenda y colores de los atlas anteriores no cambian.

El código está en `../../analisis/escenarios2003/`: `preparar_atlas.py` y `atlas.js`. `base_territorial.json` registra los emparejamientos y la base; `control_territorial.json` explica cobertura y cierre. `manifiesto.json` identifica los 18 HTML con SHA256. `revision_automatizada.json` conserva el último control de 648 cambios de modelo/etapa/modo.

Las exportaciones PNG predeterminadas (primera vuelta de cada retirada, modelo principal) están en `../../png_transparentes/mapa2003escenarios/` y `../../png_blanco/mapa2003escenarios/`; desde cualquier HTML se puede descargar el SVG/PNG/CSV de otro estado elegido. No hay paquete Commons: estas son ucronías.

Método, encuestas, reservas y comandos completos: [LEEME del análisis](../../analisis/escenarios2003/LEEME.md). Simulador con Sankey y sensibilidad: [simulador_2003.html](../../analisis/escenarios2003/simulador_2003.html).


**31-oct-2026**: el reparto del retirado es por defecto coherente con los balotajes encuestados (modelo de Luce sobre la afinidad por origen; selector «Reparto del retirado»). Exclusión del balotaje 3 % y Analogías de abril para Menem–Kirchner. Ver `analisis/escenarios2003/LEEME.md`, «Revisión del método».

Tercera pasada (31-oct-2026): el balotaje usa por defecto el ajuste conjunto de las 18 mediciones anteriores al 27 de abril (con los seis cruces de Rouvier de marzo).
