# Post para X/Twitter: 257 distritos uninominales

Dos tuits.

---

**1/** (imagen: `analisis/uninominal/portada.png`)

En honor a las elecciones de ayer en Estados Unidos, quise averiguar cómo se vería la Argentina con diputados elegidos por distritos uninominales (como tuvimos en 1904 y 1951, entre otros). ¡Fíjense!
https://azha2005.github.io/257arg/uninominal/

**2/** (imágenes: `img/post_2025_todos.png`, `img/post_2023_todos.png`, `img/post_gerrymander_lla.png`)

Método: cada provincia tiene las bancas de la ley 22.847 con el censo 2022 (sin el piso de 1983). Un algoritmo (Mosaic: ReCom y recocido simulado) dibujó los distritos sobre radios censales sin mirar votos, y en cada uno gana el más votado con los resultados de 2023 y 2025.

---

## Texto alternativo de las imágenes

- `portada.png`: «Mapa de la Argentina dividida en 257 distritos uninominales, coloreados por la fuerza que gana cada uno con los votos de diputados 2025, y un hemiciclo: La Libertad Avanza 160 bancas, Fuerza Patria 83, Innovación Federal 7, Provincias Unidas 3, La Neuquinidad 2 y Por San Juan 2.»
- `post_2025_todos.png`: «Diputados 2025 con cada partido por separado: LLA 160 bancas con el 40,8 % de los votos, Fuerza Patria 83 con el 33,7 %, Innovación Federal 7, Provincias Unidas 3, La Neuquinidad 2 y Por San Juan 2. Mapa del país y del AMBA.»
- `post_2023_todos.png`: «General 2023 con cada partido por separado: Unión por la Patria 139 bancas, mayoría propia, con el 36,7 % de los votos; LLA 89, JxC 26 y Hacemos 3. Mapa del país y del AMBA.»
- `post_gerrymander_lla.png`: «Distritos dibujados a favor de LLA, diputados 2025 con dos bloques: LLA 190 bancas y Fuerza Patria 67 con el 54,8 % y el 45,2 % de los votos de los dos.»

Cifras verificadas en la página (plan neutral, límites libres, salvo el gerrymander). Las capturas salen de `python analisis/uninominal/imagenes_post.py`.
