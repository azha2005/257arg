# Superficie del margen FP − LLA en la PBA, septiembre y octubre de 2025

Visualización tipo «surface» de theoelections.com: el margen Fuerza Patria − La Libertad Avanza interpolado sobre toda la provincia, con degradado continuo (bandas de 1 punto hasta ±40), la línea negra del empate y un recuadro del área metropolitana.

- `superficie_pba2025.html`: selector 7 de septiembre / 26 de octubre / corrimiento (PNG embebidos).
- `img/sup_sep.png`, `img/sup_oct.png`, `img/sup_swing.png`.

## Datos
- Septiembre: provisorio por mesa de graficarpba (`../mapaPBA2025sep/mesas_pba.pkl`, fuera de git, no se redistribuye), senadores o diputados provinciales según la sección, nativos y extranjeros. FP 47,28 % / LLA 33,71 % de los positivos.
- Octubre: provisorio por mesa de la DINE, diputados nacionales (`datos_oficiales/2025/x/resultados2025.csv`), mesa → local con `localesDeVotacionyMesas.csv`. FP 40,92 % / LLA 41,45 %.
- Locales: punto del atlas por radio de octubre o de septiembre (AMBA), si no el padrón de escuelas de la DGCyE validado a 1,5 km del circuito, si no el punto interior del circuito (~4–5 % de los votos).

## Método
Grilla de 1 km (250 m en el recuadro). Núcleo gaussiano con ancho adaptativo = distancia hasta juntar 6.000 votos positivos (entre 1,5 y 30 km):
margen = Σ K·(FP − LLA) / Σ K·positivos. Es la proporción de votos suavizada; en el campo, entre pueblos, el color es interpolación.
La barra cuenta circuitos (votos por circuito observados, no la superficie). El corrimiento es la resta de las dos superficies.

## Reservas
- Las elecciones no son del mismo cargo ni con la misma oferta (Somos Buenos Aires en septiembre).
- Lectura visual, no resultado por zona. Sin publicar.

## Regenerar
```
python mapas/superficiePBA2025/preparar_superficie.py   # locales_superficie.csv (necesita mesas_pba.pkl)
python mapas/superficiePBA2025/superficie.py            # PNG y HTML
```
