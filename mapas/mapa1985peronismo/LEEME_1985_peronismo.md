# Legislativas 1985: peronismo unido con traspaso de 8,6 puntos a UCR

Escenario hipotético solicitado y confirmado por el usuario el 1-nov-2026: sumar FREJULI/PJ y Frente Renovador y aliados; quitar 8,6 puntos porcentuales del total nacional al bloque unido y sumarlos a UCR.

Resultado nacional: UCR 52,18 %; peronismo unido 26,41 %. El resto mantiene sus votos históricos. El nacional parte de la tabla de Wikipedia guardada en `comun/wikitop.py`, modificada expresamente para esta simulación: UCR 6.678.647 + 1.317.908 = 7.996.555; peronismo unido 3.753.194 + 1.611.441 − 1.317.908 = 4.046.727, sobre 15.324.510 votos positivos.

## Distribución territorial

Se reutilizan datos y geometría del atlas histórico `mapas/mapa1985/`, sin modificarlo. Se suman `frejuli`, `pj`, `frejuchu`, `fren`, `cbt`, `lab`, `fupop` y `flib` solo en Capital Federal. `flib` fuera de Capital sigue en el Frente del Pueblo, conforme al mapeo histórico. UCR conserva también su alianza `ucrmpc`.

Se calcula el equivalente al 8,6 % del total de positivos de la base, y se reparte la quita en proporción al voto peronista original de cada unidad, con redondeo por restos mayores para cerrar el total transferido al voto. En cada unidad ese número pasa directamente a `ucr`; se mantiene exactamente la suma original de votos a partidos y cada voto de las demás fuerzas. No es una quita uniforme de 8,6 puntos en cada departamento, ni una estimación de movimientos individuales observados.

La base departamental carece de 896 votos de fuerzas menores en Formosa respecto de Wikipedia; por ello la transferencia territorial es 77 votos menor que la nacional (1.317.831 frente a 1.317.908). Se mantiene esta reserva de la fuente, sin inventar los votos faltantes. Los positivos, blancos, nulos, votantes e inscriptos se conservan tal como están en la base histórica. Capital usa las 28 circunscripciones aproximadas y la geometría general es del censo de 1980. Malvinas permanece gris y sin dato propio.

Los códigos de las listas peronistas se consolidan como `P_frejuli` en las fichas para mostrar la alianza simulada; no se presentan como resultados reales de cada lista. La leyenda conserva solo fuerzas ganadoras de una unidad. Se usan colores y emblemas ya incorporados en el atlas de 1985, con sus reservas documentadas en `logos/LICENCIAS.md`. La candidatura conjunta usa la bandera del PJ y se rotula «FREJULI + Renovadores». No se usa el logo presidencial de Luder, porque es una simulación legislativa.

## Archivos y regeneración

```powershell
python mapas/mapa1985peronismo/build_1985_peronismo.py
python comun/render_transparentes.py mapa1985peronismo
python comun/render_blanco.py mapa1985peronismo atlas_1985_peronismo.html
```

`atlas_1985_peronismo.html` es autocontenido, con modos GANÓ, UCR, PJ unido y PART. `dataset_1985_peronismo.json` contiene los datos del atlas y `control.json` detalla la transferencia en las 525 unidades con datos. El constructor reutiliza el build original mediante cambios en memoria y requiere sus dependencias locales.

Controles: transferencia nacional territorial al voto; quita nunca superior al voto peronista local; conservación exacta de votos a partidos por unidad; carga y selección de cuatro modos sin errores JavaScript; revisión visual de la imagen de ganadores. Sin paquete ni publicación en Commons, por tratarse de una simulación.
