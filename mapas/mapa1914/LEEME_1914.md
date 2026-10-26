# Diputados nacionales 1914 — atlas por departamento (15-oct-2026)

`python build_1914.py` regenera `atlas_1914_diputados.html` (HTML autónomo, 1,5 MB) y `dataset_1914.json`. Está hecho en el estilo del atlas de 1916
(`../mapa1916dip/build_1916.py`: misma geometría de 1914, mismos recuadros, mismo cartel) con otra capa de datos. Vistas: GANÓ (bloque más votado),
UCR, CON (conservadores) y PART (participación **provincial**: no hay electores por departamento).

Los datos salen de `../busqueda1914/` (consolidado, ver `LEEME_1914.md` de esa carpeta) y de las tablas provinciales de la Wikipedia.
El paquete para Commons está en `../commons/1914/` (8 SVG + 4 PNG, sin subir). PNG: `../png_transparentes/mapa1914/` y `../png_blanco/mapa1914/`.

## Cobertura (qué se pinta y con qué)

| Qué | Unidades | Fuente |
|---|---|---|
| Buenos Aires | 105 de 120 partidos con cifra (3 completados con La Prensa) | Cantón (1968), t. II; La Prensa 1 y 2/4/1914 |
| Capital Federal | 20 de 21 circunscripciones (Puerto no tiene polígono) | Cantón |
| Entre Ríos | 14 de 14 (Concepción del Uruguay **inferida** por residuo) | Cantón; `busqueda1914/fase2/entre_rios/inferencia_concepcion.csv` |
| Córdoba, Corrientes, La Rioja, Mendoza | todos los departamentos | actas del HCDN (26-P, 21-D, 13-P, 29-P) |
| Santa Fe | **13 de 19**: 10 con total del diario *Santa Fe*, 3 de La Prensa (General López, Caseros, Constitución) y Capital como suma parcial; 5 en beige | diario *Santa Fe*, *La Prensa* (31/3 a 2/4) |
| Catamarca, Jujuy, Salta, San Juan, Santiago del Estero, Tucumán | provincia entera en un color (`DATA.solid`) | total provincial de la Wikipedia |
| San Luis, territorios, Los Andes | gris (no votaban / no renovó) | — |

## Decisiones que conviene revisar

1. **Bloques como la Wikipedia.** «Partidos Conservadores» (#30D5C8) suma las 13 filas del total (249.345): conservadores, Demócrata de Córdoba, Unión
   Democrática, Partido Provincial, Partido Popular, Oficialista, Unión Provincial, Concentración Cívica, Carbosistas, Constitucional y la coalición
   liberal-autonomista (+ Liberal Disidente) de Corrientes. En 1916 los liberales de Corrientes iban aparte; acá siguen la infobox de 1914. Unión Cívica
   (Capital), Liga del Sur (Santa Fe) y PS van como bloques propios. Un departamento de Córdoba ganado por Peña (independiente, «Otros» en la Wikipedia) va
   en gris con clave. El gráfico y las barras nacionales salen de `../wikitop.py` (`WIKI[1914]`), que cierra con los 591.598 votos positivos.
2. **Cada partido = votos de su primer candidato** (la columna «votos al partido» de la Wikipedia). Córdoba, Corrientes y Mendoza se leen por candidato:
   se descartan los acompañantes de lista.
3. **Santa Fe es prensa del escrutinio en curso, no el definitivo del 8/4** (el total provincial de prensa difiere del definitivo en 300 a 500 votos por
   candidato). Capital y General López son sumas parciales; la tarjeta lo dice. Belgrano y San Martín las gana la Liga del Sur (689 contra 680; 1.300 contra 925).
4. **Jujuy** se pinta con la tabla de la Wikipedia (Oficialista 3.806 contra UCR 3.606) aunque la elección quedó anulada el 24/7/1914; la tarjeta lo aclara.
5. **Concepción del Uruguay** se pinta con la inferencia por residuo que pidió el usuario (Provinciales 3.859, UCR 2.900, Carbosistas 687): no es una transcripción y la tarjeta lo dice
   (`../busqueda1914/fase2/entre_rios/INFERENCIA_CONCEPCION.md`).
6. **Cifras subsumidas** (Cantón, t. I, Apéndice C), igual que 1916: Necochea lleva los datos de Juárez, Tres Arroyos y Gonzáles Chaves, repartidos en los tres
   polígonos; Juárez Celman/General Roca no se repite en 1914 (cada uno con su fila).
7. **Participación**: solo hay dato provincial; cada departamento lleva el color de su provincia y la tarjeta lo aclara.
8. **Totales por provincia (tarjetas de provincia y mini «Provincias») = tablas de la Wikipedia**, no la suma de los departamentos.

## Control: suma de los departamentos contra la Wikipedia (diferencias documentadas, no corregidas)

| Provincia | Departamentos (consolidado) | Wikipedia |
|---|---|---|
| Buenos Aires | UCR 55.605 · Conservador 59.495 · PS 6.719 | 55.705 · 63.062 · 6.719 |
| Capital | PS 43.267 · UCR 37.517 · UC 21.131 · Const. 15.284 | 44.335 · 38.722 · 20.222 · 15.193 |
| Entre Ríos | UCR 23.047 · Prov. 17.480 · Carb. 5.928 | 25.947 · 21.339 · 6.615 (falta Concepción) |
| Córdoba | UCR 16.872 | 16.862 (+10 Salas) |
| Corrientes | UCR 8.836 | 8.776 (+60 Soto) |
| Mendoza | Popular 15.350 · UCR 6.588 | 15.453 · 6.871 |

La suma de las tarjetas de Buenos Aires da más porque Necochea se repite en tres polígonos. Todo viene de lecturas visuales sin segunda transcripción
independiente (ver los controles de `../busqueda1914/CONTROL_INTEGRACION.md`).

## Pendientes

- Santa Fe: faltan 9 de Julio, Garay, San Javier, San Cristóbal y San Justo (en La Prensa tampoco están). Buenos Aires: siguen vacíos Esteban Echeverría y Roque Pérez (no figuran en las tablas de La Prensa);
  Tres Arroyos podría separarse de Necochea con La Prensa (`../busqueda1914/fase3/pba_laprensa/LEEME.md`). Ver `../busqueda1914/LEADS_PRIORIZADOS.md`.
- Mirar el mapa por distrito vigente en Commons/Wikipedia («Resultados por distrito.svg») para comparar ganadores por provincia: no se hizo.
- Logos: solo la UCR (bandera antigua bicolor) y el PS tienen emblema; Partidos Conservadores, UC y LDS llevan sigla.
