# Legislativas 2003–2025: atlas y paquetes para Commons

Diputados nacionales, compilación 20-oct-2026. Diez atlas nuevos y las referencias 2009/2013. Todos los mapas conservan el estilo del proyecto. No se subieron archivos a Commons.

Colores de las barras/partidos de Wikipedia (no los fondos pastel de los subtotales) y colores ya verificados en los atlas de 2009 y 2013 para las mismas fuerzas. Provincias Unidas 2025 usa naranja **#FF682C**, por pedido del usuario. Los cambios de contraste están en cada LEEME.

| Año | Atlas | Paquete | Cobertura / reservas de datos |
|---|---|---|---|
| 2003 | [Abrir](../mapa2003/atlas_2003.html) · [LEEME](../mapa2003/LEEME_2003.md) | [Carpeta 2003](2003/subir/) · [Instrucciones](2003/LEEME_SUBIDA.md) | Pendiente: Buenos Aires: Magdalena, Buenos Aires: Punta Indio; La Pampa en color provincial sólido |
| 2005 | [Abrir](../mapa2005/atlas_2005.html) · [LEEME](../mapa2005/LEEME_2005.md) | [Carpeta 2005](2005/subir/) · [Instrucciones](2005/LEEME_SUBIDA.md) | Sin departamentos pendientes |
| 2007 | [Abrir](../mapa2007/atlas_2007.html) · [LEEME](../mapa2007/LEEME_2007.md) | [Carpeta 2007](2007/subir/) · [Instrucciones](2007/LEEME_SUBIDA.md) | Pendiente: Jujuy: Valle Grande |
| 2009 | [Abrir](../mapa2009/atlas_2009.html) · [LEEME](../mapa2009/LEEME_2009.md) | [Carpeta 2009](2009/subir/) · [Instrucciones](2009/LEEME_SUBIDA.md) | Referencia existente, cobertura completa |
| 2011 | [Abrir](../mapa2011/atlas_2011.html) · [LEEME](../mapa2011/LEEME_2011.md) | [Carpeta 2011](2011/subir/) · [Instrucciones](2011/LEEME_SUBIDA.md) | Pendiente: Jujuy: Valle Grande |
| 2013 | [Abrir](../mapa2013/atlas_2013.html) · [LEEME](../mapa2013/LEEME_2013.md) | [Carpeta 2013](2013/subir/) · [Instrucciones](2013/LEEME_SUBIDA.md) | Referencia existente: Ramón Lista y Valle Grande sin mesas escrutadas |
| 2015 | [Abrir](../mapa2015/atlas_2015.html) · [LEEME](../mapa2015/LEEME_2015.md) | [Carpeta 2015](2015/subir/) · [Instrucciones](2015/LEEME_SUBIDA.md) | Sin departamentos pendientes |
| 2017 | [Abrir](../mapa2017/atlas_2017.html) · [LEEME](../mapa2017/LEEME_2017.md) | [Carpeta 2017](2017/subir/) · [Instrucciones](2017/LEEME_SUBIDA.md) | Pendiente: Jujuy: Valle Grande |
| 2019 | [Abrir](../mapa2019/atlas_2019.html) · [LEEME](../mapa2019/LEEME_2019.md) | [Carpeta 2019](2019/subir/) · [Instrucciones](2019/LEEME_SUBIDA.md) | Pendiente: Catamarca: Antofagasta de la Sierra |
| 2021 | [Abrir](../mapa2021/atlas_2021.html) · [LEEME](../mapa2021/LEEME_2021.md) | [Carpeta 2021](2021/subir/) · [Instrucciones](2021/LEEME_SUBIDA.md) | Pendiente: Chaco: Tapenagá |
| 2023 | [Abrir](../mapa2023/atlas_2023.html) · [LEEME](../mapa2023/LEEME_2023.md) | [Carpeta 2023](2023/subir/) · [Instrucciones](2023/LEEME_SUBIDA.md) | Sin departamentos pendientes |
| 2025 | [Abrir](../mapa2025/atlas_2025.html) · [LEEME](../mapa2025/LEEME_2025.md) | [Carpeta 2025](2025/subir/) · [Instrucciones](2025/LEEME_SUBIDA.md) | Sin departamentos pendientes |

## Geometría y fuentes

- 2003, 2005 y 2007: shapefile censal de 2001 + 28 circunscripciones de Capital; las circunscripciones son aproximadas y se ajustan al contorno, como en el proyecto.
- 2009: referencia con 15 comunas y Chascomús sin Lezama (elección anterior a su creación).
- 2011 en adelante: departamentos de 2010 + Lezama separado; Tolhuin aparece desde 2019. La ley provincial 1186 que crea el departamento se sancionó el 27-oct-2017, después de la elección legislativa del 22-oct-2017. La ley 892 de 2012 transformaba el municipio, no creaba el departamento. Fuente: https://www.legistdf.gob.ar/lp/leyes/Provinciales/LEYP1186.pdf
- La Paz/Choya conserva el límite histórico de hecho, según la decisión anterior del usuario. Los polígonos modernos de Lezama/Tolhuin se recortan al contorno histórico, sin trasladar ese límite disputado.
- 2003: dat.ar, contrastado por unidad. La Plata: corrección de 21 separadores de miles, original intacto. La Pampa: total provincial definitivo de la DINE; el PDF declara que no se recibieron resultados por departamento. Magdalena y Punta Indio tienen una cifra de lista ausente y quedan pendientes.
- 2005–2007: PolAr/INDRA/Andy Tow. Se completaron los seis departamentos ausentes de La Pampa 2005 y Valle Grande 2005 con las tablas oficiales de la DINE, verificadas visualmente y cerradas al voto.
- 2011–2025: DINE, provisorios por mesa. Santa Fe cambia la numeración de secciones en 2023: se empareja por nombre y no se confunden sus departamentos con antiguas subsecciones de Rosario/La Capital.
- 2009 y 2013 conservan sus fuentes, logos y decisiones ya verificadas. Se regeneran sus PNG y paquetes, sin sustituir sus builds/datasets.
- Las tablas nacionales salen de Wikipedia, nunca de la suma de la base. Los CSV `mapeo_listas` y `control_bloques` conservan el cruce de alianzas y las diferencias. No se imputan votos para forzar igualdad.

## Logos, licencias y publicación

Los emblemas y sus metadatos están en `fuentes_leg2003_2025/`, `mapa<año>/logos_usados.json` y `logos_wikipedia/LICENCIAS.md`. Las variantes con siglas omiten los emblemas con reservas de época, reutilizaciones sin metadatos completos o licencias ShareAlike. Los archivos con logos ShareAlike llevan CC BY-SA 4.0; los demás CC BY 4.0, más CC BY 2.5 Argentina por la geometría de Rodríguez/CONICET.

**Los atlas con faltantes no deben publicarse como completos.** Cada `LEEME_SUBIDA.md` identifica qué versiones están en espera. No se disfrazan votos provinciales de resultados departamentales.

## Verificación

Se verifican los 71 modos de los doce atlas: hash/pestaña activa, ausencia de errores JavaScript y consistencia entre territorios y registros. Se revisaron las capturas de todos los modos. Las hojas de revisión están en `revision_leg2003_2025/`. `commons/chequeo.py` comprueba los SVG exportados y genera renders independientes con resvg.

## Reproducir

```powershell
python atlas_leg2003_2025.py 2025
python validar_render_leg2003_2025.py 2025
python commons/paquete.py 2025
python commons/chequeo.py 2025
python cerrar_leg2003_2025.py
```
