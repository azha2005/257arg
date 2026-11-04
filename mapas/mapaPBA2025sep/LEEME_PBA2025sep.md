# Legislativas bonaerenses del 7 de septiembre de 2025

Tres atlas con la plantilla estilo Wikipedia 1999 y un selector **Nivel** (`#nv-<tecla>-m-<modo>`):

| Atlas | Niveles | Unidades |
|---|---|---|
| `atlas_pba2025sep.html` | Sección / Partido / Circuito | 8 secciones, 135 partidos, 1.069 circuitos |
| `atlas_amba2025sep.html` | Partido / Circuito | 40 partidos del AMBA, 379 circuitos |
| `atlas_amba2025sep_radios.html` | Partido / Circuito / Radio | 40 partidos, 379 circuitos, 14.281 radios 2022 |

Modos: Ganó, % Fuerza Patria, % La Libertad Avanza, % Somos Buenos Aires y participación.

## Datos

- **Votos**: escrutinio provisorio por mesa de la base de graficarpba (`datos/provinciales/pba2025/`, ver su LEEME). La base se recibió a pedido y **no se redistribuye**: los CSV y los `mesas_*.pkl` quedan fuera de git. 41.189 mesas, incluidas las de extranjeros.
- **Cargo**: senadores provinciales en las secciones 1.ª, 4.ª, 5.ª y 7.ª y diputados en las demás, sumados como un solo cargo legislativo, igual que la tabla de la Wikipedia (`wpba2025.txt`).
- **Agrupación**: Fuerza Patria, La Libertad Avanza, Somos Buenos Aires con su lista ligada «Espacio Abierto…» y FIT-U (`partidos_sep.py`). Usan los colores de los atlas de octubre; Somos va en rosa #FE9AC3, el de la Wikipedia.
- **Totales**: cada nivel suma exactamente los votos de la base. Los porcentajes se calculan sobre los positivos, porque la base no informa los nulos. Participación = votantes / electores de las mesas con votos.
- **Geometría**:
  - circuitos de la provincia del `PBA.geojson` (galeano 2021), donde los circuitos con letra van con el polígono del circuito madre;
  - partidos de `Departamentos_2022_INDEC` (`partidos_geo.py`), simplificados en conjunto (`coverage_simplify`) para que los bordes compartidos coincidan, y secciones como uniones de esos partidos. En el nivel Partido no se marca aparte el límite de sección. La unión de los circuitos de 2021 dejaba huecos y rendijas, así que no se usa para este nivel;
  - radios censales 2022 de CONICET (Rodríguez), los mismos del atlas `mapaAMBA2025radios`.
- **Capital** no votó ese día (su elección local fue el 18 de mayo): en los atlas del AMBA aparece en gris, sin datos.

## Reparto por radio (estimación)

Es el método de Poblaciones / LN Data, el mismo del atlas de octubre:

- Cada local de votación reparte sus votos entre los radios de su partido con peso 1/d² al centroide, con un mínimo de 25 m.
- Los radios con menos de 1 voto quedan en 0.
- Ubicación de los locales (`locales_sep.csv`, 4.768 locales), en proporción de electores:
  - 91,6 %: coordenadas del atlas de octubre, que usa la misma codificación de locales de la DINE;
  - 6,3 %: padrón de escuelas de la DGCyE, validado contra el circuito de sus mesas;
  - 2,1 %: centro del circuito.
- **No es un resultado observado**: el voto no se registra por radio. El nivel Circuito del atlas por radio muestra las fichas observadas del atlas por circuito.

## Reservas

- **Beige en el atlas provincial**: 101 circuitos rurales sin mesas, que tampoco tuvieron mesas en octubre. Se votó en otro circuito del mismo partido. No se imputan.
- **Beige en el AMBA**: los mismos 7 circuitos sin mesas del atlas de octubre.
- Es un **provisorio**: no se cotejó con el escrutinio definitivo de la Junta Electoral bonaerense.
- Somos Buenos Aires y el FIT-U van con sigla, porque no hay logo con licencia o fecha verificada. Fuerza Patria y LLA usan los logos del atlas legislativo 2025.

## Regenerar

Correr desde la raíz:

```
python mapas/mapaPBA2025sep/preparar.py         # CSV de graficarpba -> mesas_pba.pkl, mesas_amba.pkl
python mapas/mapaPBA2025sep/locales_sep.py      # locales_sep.csv
python mapas/mapaPBA2025sep/asignar_sep.py      # asignacion_sep.pkl (radios)
python mapas/mapaPBA2025sep/build_circuitos.py pba
python mapas/mapaPBA2025sep/build_circuitos.py amba
python mapas/mapaPBA2025sep/build_radios.py     # necesita el atlas amba por circuito
python mapas/mapaPBA2025sep/render.py atlas_pba2025sep.html   # PNG de control en img/
```

Sin publicar en el sitio ni en Commons.
