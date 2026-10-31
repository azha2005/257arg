---
title: Transferencias de votos (Argentina)
emoji: 🗳️
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: false
short_description: Sankey de transferencias entre dos elecciones argentinas
---

# Explorador de transferencias de votos

Elegí dos elecciones argentinas cualesquiera (279: presidenciales, legislativas, PASO, gobernadores y legislaturas
provinciales, de 1912 a 2025) y la página estima al momento la matriz de transferencias de votos entre ellas,
nacional o de cada provincia, con un sankey.

**Método**: inferencia ecológica RxC penalizada (port a Python del código R de Ernesto Calvo), una matriz por provincia
encogida hacia la nacional, penalización por validación cruzada. Es la estimación puntual, sin intervalos. Las marcas
`*` (fila no identificada), `†` (fila cerca del promedio) y el aviso «Matriz poco informativa» siguen los mismos
criterios que los sankeys publicados del proyecto.

Pares de épocas lejanas son comparación de geografías, no traspasos de votantes. Las categorías chicas (<5 %) tienen
márgenes de error grandes.

Código y datos: [github.com/azha2005/257arg](https://github.com/azha2005/257arg) (`transferencias/explorador/`).
Este Space se arma con `python transferencias/explorador/space/armar.py`.
