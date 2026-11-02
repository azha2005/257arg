# Escenario presidencial hipotético de 1983

Pedido: Alfonsín 41,58 %, Luder 50,33 % sobre votos positivos; otras fuerzas 8,09 %.

Se reutilizan geometría, estilos, emblemas y base territorial del atlas histórico `mapas/mapa1983/`, sin modificarlo. El HTML autocontenido es `atlas_1983_hipotetico.html`.

## Método y límites

IPF sobre la matriz de 525 departamentos y circunscripciones por partido. Conserva los ceros originales y la suma de votos a partidos de cada unidad. Fija los totales nacionales pedidos para UCR y PJ; reparte el 8,09 % entre las demás fuerzas en proporción a sus totales originales. No es una estimación de transferencias individuales ni un resultado histórico. Existen otras distribuciones territoriales compatibles con los mismos porcentajes nacionales.

Tras converger, redondea a votos enteros por mayores restos dentro de cada unidad. El total local se mantiene exactamente; los totales nacionales pueden apartarse unos pocos votos del objetivo matemático, pero los dos porcentajes solicitados cierran a dos decimales. `control.json` registra convergencia, totales y error de redondeo.

La suma de votos a partidos es 14.927.513, un voto más que los positivos nacionales históricos de Wikipedia: se conserva esa suma de la base para el escenario. Blancos, anulados, electores y participación se mantienen históricos, con sus reservas originales; el modo PART es contexto histórico, no una participación nueva simulada. Malvinas permanece gris sin dato propio. Capital usa las circunscripciones aproximadas del atlas original.

La leyenda incluye solo las fuerzas que ganan una unidad. El resto sigue visible en las fichas y agregado como otros en la torta. La fuente del resultado nacional es el objetivo hipotético del usuario, excepción explícita a la regla de Wikipedia para atlas históricos.

## Regenerar

Desde la raíz:

```powershell
python mapas/mapa1983hipotetico/build_1983_hipotetico.py
python comun/render_transparentes.py mapa1983hipotetico
python comun/render_blanco.py mapa1983hipotetico atlas_1983_hipotetico.html
```

El constructor aplica modificaciones en memoria al constructor histórico y guarda los resultados únicamente en esta carpeta. Depende de los archivos originales del atlas 1983.

Actualización visual del 1-nov-2026: título habitual «Elecciones presidenciales de Argentina de 1983», con aclaración hipotética en subtítulo y fuentes; logo de Luder aportado por el usuario, conservado íntegro en `logos/Luder_Presidente_usuario.png`. PAL se dimensiona según la altura real de la fila (50 px), para que sus dos emblemas entren completos en el marco. Solo se cambia este escenario.

Logo de Luder sin fondo: `python mapas/mapa1983hipotetico/preparar_logo_luder.py` genera `logos/Luder_Presidente_transparente.png` únicamente con código a partir del original. Pone alfa cero donde el máximo de RGB es ≤32. Por pedido posterior del usuario, las letras se pintan de blanco; la banda argentina y el sol conservan sus RGB originales (columnas 389..534). Se amplía a 170 px de ancho en su barra sin alterar los colores del atlas. No se utiliza la variante generada por ImageGen.

Verificado: cierre nacional a dos decimales, conservación de positivos por unidad, carga de cuatro modos sin errores JavaScript y correspondencia de las pestañas; revisión visual de capturas. No se prepara ni publica en Commons, por ser una simulación.
