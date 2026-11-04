# Ocho remakes de mapas alternativos de 2003

Reconstrucción local solicitada el 2-nov-2026. **Escenarios hipotéticos, no resultados observados ni recuperación de la base perdida del autor.**

Escenarios y mapas originales de **[u/Alarmed_Rope5383](https://www.reddit.com/user/Alarmed_Rope5383/)**, autor identificado por el usuario. El proyecto realizó el remake interactivo y la estimación territorial. La publicación en GitHub Pages fue autorizada el 3-nov-2026, con un índice de colección estilo Hallmark Ink, ocho miniaturas de póster y una portada de enlace social. Los créditos figuran en la portada, el pie del índice y la barra y las fuentes de cada atlas.

Abrir `index.html` o `abrir_2003alt.cmd` en la raíz del proyecto. La versión con la capa habitual del sitio está en `outputs/sitio_local/mapas/mapa2003alt/`.

Las pestañas de los ocho remakes miden el ancho real de su texto, tienen un margen interior de diez píxeles y una separación de ocho. Se alinean hasta x=1490; el título y el año se ajustan hasta la primera pestaña y el subtítulo conserva su espacio. Implementado en `analisis/remake2003/botones.py`, integrado al constructor. `outputs/2003alt/control_botones.json` comprueba todos los modos sin solapes ni texto fuera de los botones.

## Escalas de color revisadas (2-nov-2026)

Los ocho remakes usan siete tonos con mayor separación entre claros y oscuros. Tras la corrección del usuario sobre los tonos demasiado pálidos, las paletas se derivan de los rellenos frecuentes de los mapas originales: `extraer_paletas.py` los separa por candidatura y genera siete niveles entre los tonos observados, completando intermedios sin mezclarlos con blanco. Procedencia, tonos de referencia y paletas en `analisis/remake2003/paletas_originales.json`. Si una candidatura no tiene suficientes píxeles, se reutilizan los de la misma candidatura y color base en los otros originales; sin referencia utilizable, se aplica una gama de respaldo sin tonos pastel. Se conserva el color base de cada candidatura en barras y torta. El visor usa explícitamente `candidates[c].ramp`, que antes estaba definido pero no era leído por la función de color.

En «Ganó» los cortes son de cinco puntos: primera vuelta, 30/35/40/45/50/55 %; balotajes, 55/60/65/70/75/80 %. Las coropletas conservan sus deciles, con la nueva paleta; «Lectura» conserva su color plano anterior. Bilardo ocupa cinco tonos de ganador y Hilda cuatro. No se recalcularon votos: un SHA256 del contenido excluyendo exclusivamente las propiedades de color/cortes verifica identidad de votos, porcentajes, ganadores, logos y colores base antes y después en `outputs/2003alt/control_escalas.json`.

Para reproducir las paletas: `python -X utf8 analisis/remake2003/extraer_paletas.py`. Para reaplicar solamente el color: `python -X utf8 analisis/remake2003/escalas.py`. El constructor también lo aplica al regenerar los atlas. El control verifica asimismo que los cortes y sus etiquetas permanecen idénticos a la revisión de cinco puntos. Se actualizaron HTML, PNG blancos/transparentes y la copia local con capa de Pages. La autorización del 3-nov-2026 incorpora la colección al catálogo de publicación.

## Material aportado y alcance

La carpeta `C:\Users\JC\Downloads\2003alt` contiene ocho imágenes individuales y un collage de esos mismos ocho escenarios. Se conservan las individuales en `analisis/remake2003/originales/`; sus hashes, el hash de la base histórica y los coeficientes del modelo están en `analisis/remake2003/insumos.json`.

| Escenario | Vuelta visible | Ganadores locales leídos y conservados |
|---|---|---:|
| Macri–Menem | Balotaje | 507 |
| Álvarez–Cavallo–Duhalde | Primera | 500 |
| Bilardo | Primera | 492 |
| Kirchner–Menem | Balotaje | 508 |
| Rodríguez Saá–López Murphy | Balotaje | 507 |
| Lemas | Primera, por candidato | 503 |
| Menem–Kirchner | Balotaje | 510 |
| Reutemann–Menem | Balotaje | 504 |

Cada escenario tiene 539 unidades modeladas: 538 departamentos/circunscripciones del mapa principal y la Antártida. Malvinas permanece gris. Las primeras vueltas alternativas de los cinco balotajes no están representadas en los PNG; los selectores dibujados en la imagen no permiten recuperar sus otras vistas. El modo por lema tampoco está presente en la imagen: se reconstruye la vista por candidato que sí se ve.

## Qué se conserva y qué se estima

- Cifras nacionales de candidaturas y porcentajes: transcripción de cada imagen, no Wikipedia histórica. En Álvarez, Rodríguez Saá y Carrió tienen porcentajes pero no votos nacionales legibles: sus votos se estiman aplicando esos porcentajes al denominador aproximado del escenario. Se los distingue de las cifras transcritas en `escenarios.json` (votos `null`).
- Ganadores departamentales/circunscripciones: lectura automática de familias de color del mapa principal, del AMBA y de Capital. Antártida: lectura visual del recuadro. No se recuperaron porcentajes locales exactos.
- Los recuadros originales del AMBA aportan 38–39 partidos legibles por escenario. El recorte corresponde a los 40 partidos de nuestro AMBA salvo Brandsen. Capital usa las mismas 28 circunscripciones aproximadas del atlas presidencial publicado: 26–28 resultan legibles según el escenario.
- La vista **LECTURA** usa color plano para la identidad leída y beige donde no hubo lectura suficiente. Sus fichas aclaran que sus valores numéricos son los del modelo. **GANÓ** y las coropletas muestran la estimación completa, incluidas las unidades sin lectura; éstas quedan identificadas en la ficha.
- La miniatura provincial también se usa como restricción agregada. Se conservan sus 24 ganadores y los conteos de distritos de la infobox. Tucumán es demasiado pequeño en tres miniaturas (Macri, Álvarez y Bilardo): su identidad provincial se infiere por el cierre del conteo impreso; no se presenta como lectura departamental ni se rellena con ella el mapa de lecturas.

## Lectura de colores

`registrar.py` ajusta un registro afín entre la cartografía y el PNG de referencia. El registro continental alcanza un IoU de contorno de aproximadamente 0,985; Capital, 0,953; AMBA, 0,946. Son medidas geométricas del registro, **no porcentajes de acierto electoral**.

`digitizar.py` clasifica familias cromáticas en HSV. Bilardo/Kirchner y De la Sota/Rodríguez Saá requieren también saturación por su proximidad de tono. Se evita el trazo de borde cuando hay interior suficiente. Una lectura local se acepta con al menos seis píxeles clasificados y acuerdo mínimo del 80 %. Estos umbrales son reglas operativas, no probabilidades estadísticas. Los tonos originales no se interpretan como porcentajes exactos; se conserva la identidad del ganador y se usa la escala habitual del proyecto para los porcentajes modelados.

La baja resolución y la cartografía aproximada de Capital pueden producir errores de lectura. Los registros, las cuentas de píxeles y las unidades no aceptadas quedan en `analisis/remake2003/lecturas.json`. Las coincidencias de la tabla son un control de que el modelo respeta las lecturas aceptadas, no una validación independiente de ellas.

## Estimación de votos locales

Referencia: `mapas/mapa2003pres/dataset_2003pres.json`, con los votos presidenciales PolAr y los complementos documentados de Rinconada y Valle Grande. No se usan los votos de diputados de 2003. La geometría, los siete recuadros y la interfaz vienen del HTML presidencial de ese atlas; las aproximaciones cartográficas siguen vigentes.

1. Se toman las composiciones locales observadas de 2003. Las candidaturas que existieron conservan su propio perfil. Las exclusivas de las ucronías usan combinaciones explícitas de esos perfiles; los coeficientes están en `PROFILES`, dentro de `analisis/remake2003/construir.py`, y en `insumos.json`. Los refuerzos heurísticos de De la Sota en Córdoba/Entre Ríos, Reutemann en Santa Fe e Hilda Duhalde en Buenos Aires también quedan registrados. No son transferencias observadas ni preferencias identificadas.
2. La masa de candidaturas modeladas se reparte entre las unidades en proporción a sus positivos históricos. Por eso se conserva el peso relativo de esas unidades, no sus absolutos históricos ni una participación local contrafáctica conocida.
3. Se ajustan los márgenes nacionales mediante una proyección de entropía con restricciones de ganador. Se deja una separación mínima relativa de 1,02 entre el ganador leído y sus rivales; es un supuesto numérico, no un margen recuperado del mapa.
4. El ajuste es jerárquico: ajuste nacional con ganadores locales; ajuste de los márgenes provinciales para conservar los ganadores de las miniaturas; ajuste local dentro de cada provincia. Mantiene las masas locales, los totales nacionales y todos los ganadores aceptados.
5. El ajuste produce valores fraccionarios intermedios, que se convierten a **votos enteros por redondeo controlado** (`analisis/remake2003/enteros.py`). Cada celda toma su piso o techo; los totales locales se redondean por restos mayores y se conservan exactamente los totales nacionales por candidatura y todos los ganadores locales y provinciales. Cada cifra cambia menos de un voto. Las fichas, el JSON y los CSV usan los mismos enteros; los porcentajes locales se recalculan a partir de ellos. No se convierten por ello en votos observados. El control está en `outputs/2003alt/control_enteros.json` y en cada `control_<escenario>.json`.

Los resultados no son únicos: muchas distribuciones locales producen las mismas cifras nacionales y ganadores. Es una solución reproducible, condicionada a los originales, no una estimación validada del comportamiento de esos votantes en una elección alternativa.

## Cierres del original

Se conservan los porcentajes impresos aunque no sumen 100 %. Para obtener una referencia del resto sin desglose se aproxima el denominador a `padrón × participación` redondeado, ambos impresos. No se identifica ese resto automáticamente con blancos o nulos y **no se lo distribuye territorialmente**. En las primeras vueltas también puede contener candidaturas no detalladas.

Álvarez tiene una inconsistencia adicional: 4.713.099 votos de Hilda Duhalde corresponden aproximadamente al 23,82 % de ese denominador, frente al 23,84 % impreso. Se conservan ambos datos y se registra la diferencia. Sus cinco porcentajes impresos suman 100,01 %. La torta se construye con votos, mientras que la leyenda conserva los porcentajes impresos; no se corrige silenciosamente el original.

La fidelidad se refiere a las cifras transcritas y a identidades territoriales leídas. Las intensidades de los colores y las participaciones locales no se copiaron como datos observados.

## Logos

Menem, VICTORIA, Recrear, MNP y ARI se heredan del atlas presidencial publicado, que los hereda del AMBA 2003 por radio, con las mismas imágenes y proporciones. Para Macri, Álvarez, Cavallo, Hilda Duhalde, Bilardo, De la Sota y Reutemann se recorta el bloque del logo de la imagen aportada, sin redibujarlo. Los originales son pequeños: se conserva esa limitación de calidad.

Registro de archivo, fuente y coordenadas: `analisis/remake2003/logos_usados.json`. Licencias de los recursos reutilizados: `logos/LICENCIAS.md`. Los montajes aportados se acreditan a u/Alarmed_Rope5383; no se les atribuye una licencia de Commons no documentada.

## Reproducir y comprobar

Desde la raíz del proyecto:

```powershell
python -X utf8 analisis/remake2003/registrar.py
python -X utf8 analisis/remake2003/digitizar.py
python -X utf8 analisis/remake2003/construir.py
python -X utf8 analisis/remake2003/verificar_renderizar.py
```

Los controles verifican cierres nacionales exactos tras el redondeo, identidad de todos los ganadores locales aceptados, los ganadores provinciales, navegación de todos los modos e imágenes de los logos. Hay PNG blancos y transparentes de cada modo en `png_blanco/mapa2003alt/` y `png_transparentes/mapa2003alt/`; el resumen visual está en `outputs/2003alt/ocho_remakes.jpg` y el control de navegador en `outputs/2003alt/validacion.json`. La publicación corresponde a GitHub Pages, sin paquete de Commons. Los ocho PNG de entrada permanecen en el archivo local: para reproducir la lectura de imagen se necesitan esos insumos; no se sustituyen por cifras originales inexistentes.
