# Escenario presidencial 1989: Convergencia

Pedido del usuario (1-nov-2026): Casella 55,51 %, Menem 30,10 % y Alsogaray 6,17 %. Se interpreta «PJR + UCR / Convergencia» como la alianza de Juan Manuel Casella. Menem aparece con el PJ, sin el rótulo ni emblema FREJUPO. El resto de las fuerzas suma 8,22 %.

## Método

Se reutiliza el atlas histórico `mapas/mapa1989/` y su constructor sin modificar sus archivos. Los perfiles locales de las tres candidaturas históricas se consolidan antes del ajuste: Angeloz/UCR+CFI como perfil inicial de Casella/Convergencia, Menem/FREJUPO y aliados como perfil inicial de Menem/PJ, Alianza de Centro como perfil de Alsogaray. Se conservan sus agrupaciones originales solo como perfiles estadísticos, no como afirmación de que esas alianzas se mantienen en el escenario.

**La base de 1989 no desagrega un PJR hipotético nacional. No se estima por separado su aporte ni se afirma haber observado una transferencia PJR→Casella.** Convergencia es el nombre de la alianza solicitado por el usuario y usa el perfil radical histórico como punto de partida. Por pedido del usuario lleva el escudo habitual de la UCR (`Escudo_de_la_UCR.svg`), en reemplazo de la sigla CON. Menem usa la bandera cuadrada del PJ (diseño 1946), ya documentada en `logos/LICENCIAS.md`. Los colores se conservan: Convergencia rojo UCR #e10019, PJ #318ce7, Alsogaray violeta #8e6bd8.

IPF ajusta las columnas de la matriz unidad×candidatura a los tres objetivos nacionales. Las otras fuerzas reciben en conjunto el 8,22 %, en proporción a sus totales originales. Conserva ceros estructurales y suma de votos a partidos de cada unidad. Se redondea a enteros por mayores restos dentro de cada unidad: sus positivos se mantienen exactamente; el total de cada candidatura puede apartarse unos votos del objetivo matemático, conservando los porcentajes solicitados a dos decimales. `control.json` documenta el cierre.

Las listas de cada una de las tres candidaturas se muestran consolidadas en las fichas. No se presentan como resultados observados de partidos o alianzas reales. La leyenda contiene solo candidaturas que ganan alguna unidad; otras fuerzas permanecen en las fichas y en «otros» de la torta.

Blancos, nulos y padrón se mantienen históricos. No se crea modo de participación, por las faltas de padrón de Santa Fe y Tucumán del atlas original. Se conservan sus correcciones y reservas de datos, incluida la discrepancia de Malargüe y los desajustes provinciales frente a Wikipedia. La suma de votos a partidos, y no los positivos declarados inconsistentes de ciertas unidades, es la restricción local de esta simulación. Geometría del censo de 1980, circunscripciones aproximadas de Capital y agregaciones territoriales del atlas original. Malvinas gris sin dato propio.

## Regeneración

Desde la raíz:

```powershell
python mapas/mapa1989convergencia/build_1989_convergencia.py
python comun/render_transparentes.py mapa1989convergencia
python comun/render_blanco.py mapa1989convergencia atlas_1989_convergencia.html
```

Salidas: HTML autocontenido `atlas_1989_convergencia.html`, datos `dataset_1989_convergencia.json`, auditoría `control.json`; PNG blanco y transparente de GANÓ, MEN, CAS y ALS. Se verifican cierre nacional a dos decimales, positivos locales conservados, carga de los cuatro modos y selección por pestaña sin errores JavaScript; revisión visual de ganadores. Sin publicación en Commons: es una simulación.
