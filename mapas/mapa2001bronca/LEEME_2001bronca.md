# Legislativas de 2001 con voto bronca

Variante analítica del atlas histórico de 2001, sin modificarlo. Ejecutar `python mapa2001bronca/build_2001bronca.py`.

Voto bronca = blancos + nulos. Se trata como una opción de comparación capaz de ganar unidades, no como una candidatura histórica. Todos los porcentajes de votos de los cinco modos usan positivos + blancos + nulos; la participación conserva su denominador de inscriptos. Los blancos y nulos se agrupan una sola vez en las fichas.

Los datos territoriales y la agrupación provincial de alianzas proceden exactamente del atlas original de 2001 y de sus reglas MAPCOL/GROUP2BLOC/OVERRIDE. El gráfico nacional conserva las cifras de Wikipedia: 2.022.587 blancos + 2.486.296 nulos = 4.508.883 votos bronca; denominador 18.798.991; 23,98 %. El mapa hereda las discrepancias entre los votos territoriales y nacionales documentadas en mapa2001/LEEME_2001.md. No se ajustaron esos votos.

Los bloques que pierden todas sus unidades al introducir el voto bronca pasan a otros en la torta. Se conservan en el detalle local. El símbolo de urna es un gráfico original explicativo, no un emblema histórico; SVG en logos_wikipedia/Voto_bronca_urna.svg. Los demás logos y sus reservas se conservan del atlas de 2001.

PAUFE usa el ámbar #f59e0b, igual que el atlas original de 2001 (unificado el 19-oct-2026 a pedido del usuario; la Wikipedia usa un gris que se confundía con el voto bronca #5b5b5b).

Paquete local: commons/2001bronca/subir/. Los nombres de los archivos incluyen «voto bronca» para distinguirlos de los resultados sobre positivos. Las descripciones en español e inglés explican el denominador y la naturaleza analítica. Todo sin subir.

Auditoría:
{
  "ganadores": {
    "PJ": 322,
    "BRONCA": 96,
    "ARI": 2,
    "ALI": 99,
    "PAUFE": 1,
    "PD": 4,
    "MPN": 14
  },
  "bronca_nacional": 4508883,
  "denominador_nacional": 18798991,
  "porcentaje": 23.9847,
  "provincias_ganadas": [
    "Capital Federal",
    "Santa Fe",
    "Tierra del Fuego"
  ]
}
