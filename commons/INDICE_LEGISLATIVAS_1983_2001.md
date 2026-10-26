# Nuevos paquetes legislativos

Publicados en Commons y en sus artículos el 20 de octubre de 2026. Incluye las diez legislativas de 1983 a 2001, voto bronca y constituyentes de 1994. [Registro y revisiones](ESTADO_LEGISLATIVAS_2026-10-20.md).

| Elección | Atlas | Paquete | Estado |
|---|---|---|---|
| Diputados 1983 | ../mapa1983dip/atlas_1983_diputados.html | 1983dip/subir/ | Listo; 4 celdas en 0 imputadas (Posadas, Salta capital, Andalgalá, Chacabuco SL); UCR y PJ a menos de 0,01 % de Wikipedia |
| Diputados 1989 | ../mapa1989dip/atlas_1989_diputados.html | 1989dip/subir/ | Listo; bloques a menos de 0,1 % de Wikipedia; sin modo de participación |
| Diputados 1995 | ../mapa1995dip/atlas_1995_diputados.html | 1995dip/subir/ | Listo; Deseado extrapolado (pedido del usuario) y Partido Federal de Córdoba imputado, ambos en las descripciones |
| Diputados 1999 | ../mapa1999dip/atlas_1999_diputados.html | 1999dip/subir/ | Listo; San Luis y Santa Cruz en color sólido con el total provincial de Wikipedia (como San Luis 1997) |
| 2001 con voto bronca | ../mapa2001bronca/atlas_2001bronca.html | 2001bronca/subir/ | Variante analítica, distinta del atlas original |

Cada carpeta contiene SVG solo mapa, SVG con leyenda, PNG y wikitext para cada modo, además de LEEME_SUBIDA.md. Los PNG blancos están en png_blanco/ y los transparentes en png_transparentes/; los paquetes de Commons usan estos últimos.

## Revisión del 19-oct-2026

Se corrigió: San Luis y Santa Cruz 1999 de beige a color sólido; celdas en 0 de UCR/PJ imputadas en 1983 cuando el residuo coincide exacto con la tabla provincial; columna del Partido Federal faltante en Córdoba 1995; filas de métricas repetidas en la base (San Juan 1995, Río Negro 1983, Córdoba 1999) que duplicaban positivos o votantes; porcentajes sobre la suma de las fuerzas cuando los positivos declarados no cierran (Capitán Sarmiento 1995 daba más de 100 %); padrones con más votantes que inscriptos marcados como inconsistentes en participación; Cruzada Renovadora con su verde del proyecto (#004d40); MPN rotulado «Movimiento Popular Neuquino / Neuquén» y Alianza 1999 «UCR, FREPASO y aliados» como en 1997; sin clave «Sin votación» para Malvinas (como 1997 y 2001); LEEME y descripciones de Commons reescritos por año.

El caso de Deseado se calculó como el total provincial de Wikipedia menos los otros seis departamentos. Archivo del cálculo con el registro original: mapa1995dip/deseado_extrapolado.json. No es una observación departamental independiente.

Los logos se reutilizan con sus licencias y reservas. PAUBO (1999) y PAUFE (2001) conservan sigla porque no hay emblema verificado disponible en estos atlas; Wikipedia usa una bandera gris genérica para PAUBO. Voto bronca usa un símbolo de urna propio, no un logo histórico.

Antes de publicar seguir INSTRUCCIONES_GENERICAS.md y el LEEME de cada carpeta. No mezclar estos paquetes con los presidenciales de 1983/1989/1995 ni la variante bronca con los resultados de 2001 sobre positivos.

## Validación local

23 modos revisados en el navegador, sin errores de página ni discrepancias con el modo seleccionado. 46 SVG, 23 PNG y 69 descripciones. `tools/validar_nuevos_atlas.py` confirma el dataset incrustado, las candidaturas, la cobertura geométrica, los archivos exportados y las cifras de Deseado y voto bronca. `commons/chequeo.py` no detectó problemas estructurales ni errores de renderizado en los SVG. Se revisaron visualmente los cinco modos de ganadores y las hojas de contacto de todos los modos, además de las rasterizaciones independientes de los SVG.

Estas comprobaciones son locales: no equivalen a una prueba de publicación en Wikimedia Commons. Las discrepancias estadísticas de las fuentes siguen documentadas y no se presentan como resueltas.
