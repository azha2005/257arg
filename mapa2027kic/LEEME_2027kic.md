# Escenario hipotético 2027: balotaje Kicillof – Milei

`atlas_2027kic.html` (`python prep27kic.py` una vez y después `python build_2027kic.py`). **No es un resultado ni una encuesta.** Es un segundo escenario, distinto de `mapa2027/` (Milei–Bregman), a partir de la imagen que pasó el usuario (infobox «2027 Argentine general election»).

## Datos de la imagen
Balotaje del 21-nov-2027: **Kicillof** (PJ, Derecho al Futuro, compañero Martín Lousteau) 14.283.190 (50,09 %) contra **Milei** (La Libertad Avanza, compañera Patricia Bullrich) 14.231.862. Participación 79,41 % (1.ª vuelta 79,05 %). Diferencia: 51.328 votos. La imagen rotula 49,90 % para Milei; con los votos da 49,91 % y el atlas muestra 49,91 %. La imagen no trae inscriptos ni la primera vuelta, por eso el atlas es solo del balotaje (no hay modo de participación ni de 1.ª vuelta).

## Método (`escenario27kic.py`)
1. Punto de partida: balotaje 2023 por departamento (Milei–Massa), `xlsx_resultados/por_eleccion/2023_presidente_balotaje.xlsx` (DINE provisorio; 14.476.462 / 11.516.142, igual al oficial).
2. Un corrimiento logístico común (δ = +0,246) al voto de Massa lleva a Kicillof al 50,09 % nacional; el electorado se escala ×1,0967 al total de positivos del escenario (28.515.052). Redondeo por resto mayor: ambos totales cierran al voto.
3. `PROV_LOGIT` (vacío) permite un ajuste propio por provincia.
4. Ocho unidades sin mesas en el balotaje 2023 de la base (Antofagasta de la Sierra, Florentino Ameghino, Gastre, Telsen, Susques, Valle Grande, Curacó, Santa Victoria) se estimaron desde las generales 2023 (JxC 85 % Milei / 10 % Massa, Hacemos 35 % / 45 %, FIT-U 15 % / 50 %); la ficha lo dice.

## Resultado del escenario
Kicillof gana 10 provincias (Buenos Aires 56,7 %, Formosa, Santiago del Estero, Chaco, Tucumán, Catamarca, Tierra del Fuego, Corrientes, La Rioja, Río Negro) y 277 departamentos; Milei 14 jurisdicciones y 250 departamentos. Es un swing uniforme: no modela efecto candidato por provincia ni las denuncias de fraude de los titulares (Formosa y Buenos Aires); la nota del mapa dice «sin certificar».

Modos: GANÓ, KICI. y MILEI. Título «Elecciones presidenciales de Argentina de 2027» y leyenda como las legislativas 2003-2025 (`leyenda_clara.js`). Colores de las legislativas 2023 (Unión por la Patria #009ce4, La Libertad Avanza #6c4c98); Milei con el emblema completo de LLA (`AMBA2025_lla_del_png_original.png`; el bloque `lla.png` de la Wikipedia es un recorte y no entraba entero en la barra) y Kicillof con el logo MDF, ambos enteros dentro de la barra (pedido del usuario; recorte de su imagen, licencia sin verificar). Geometría y recuadros: los de `mapa2027` (Departamentos_2010 + Lezama + Tolhuin). PNG en `png_transparentes/mapa2027kic/` y `png_blanco/mapa2027kic/`. Sin paquete de Commons: es una simulación.
