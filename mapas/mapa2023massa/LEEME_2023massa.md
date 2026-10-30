# Escenario hipotético 2023: Massa gana en primera vuelta con 40,21 %

`atlas_2023massa.html` (`python mapas/mapa2023massa/build_2023massa.py`). **No es un resultado.** Ucronía a partir de la imagen que pasó el usuario (29-oct-2026): zócalo de C5N «Massa revirtió el resultado de las PASO en 9 provincias», 98,41 % de mesas, #MassaPresidente, e infobox de Massa como 58.º presidente.

## Datos de la imagen
Massa 40,21 %, Milei 28,13 %, Bullrich 21,27 %, Schiaretti 5,31 %, Bregman 5,08 % (suman 100,00). Con más de 40 % y 12 puntos de ventaja, Massa gana sin balotaje. La imagen no da votos, inscriptos ni participación: se usan los votos positivos reales de las generales 2023 (26.291.718, escrutinio provisorio DINE) y la participación real (27.100.675 votantes de 35.410.080 inscriptos, 76,53 %).

## Método (`escenario23massa.py`)
1. Punto de partida: generales 2023 reales por departamento (las cinco fórmulas), de `mapas/mapa2027/base27.pkl` (DINE provisorio ya emparejado a las unidades del mapa).
2. Cada departamento conserva sus votos positivos; un ajuste proporcional (IPF) con un multiplicador nacional por candidato lleva los totales exactamente a los de la imagen: Massa ×1,10, Milei ×0,94, Bullrich ×0,89, Schiaretti ×0,78 y Bregman ×1,88 (de 2,7 % a 5,08 %).
3. **Nueve provincias revertidas.** Con el ajuste uniforme Massa ganaba 20 provincias y revertía la PASO en 15. En las seis donde su ventaja era más chica (Jujuy 0,8 puntos, Neuquén 0,9, Santa Fe 2,5, Misiones 2,7, Chubut 3,0, Salta 3,7) la celda de Massa lleva un factor provincial común (0,855: el más cercano a 1 que lo deja segundo por al menos 1 punto en las seis). Massa igual sube o queda igual que en 2023 en esas provincias. Se probó y se descartó otra variante: concentrar la suba donde Massa ya era fuerte. Para llegar a 9 provincias pedía γ = 2,48, y Massa caía de 13 % a 2 % en Córdoba.
4. Redondeo por resto mayor en cada candidato. Los totales nacionales cierran al voto, y los positivos de cada departamento pueden moverse uno o dos votos.

## Resultado del escenario
- Provincias: Massa 14, Milei 9, Bullrich 1 (Capital Federal). Massa revierte la PASO en Corrientes, Entre Ríos (allí había ganado JxC), La Pampa, La Rioja, Río Negro, San Juan, Santa Cruz, Tierra del Fuego y Tucumán (allí había ganado LLA). La ficha de cada una lo dice.
- Departamentos: Massa 399, Milei 109, Bullrich 16 y Schiaretti 3. Bregman no gana ninguno, pero tiene fila propia en la leyenda, como en la imagen de referencia del usuario (pedido del 29-oct-2026, excepción a la regla 3).
- Ganador de la PASO por provincia (agrupación): el de `mapas/mapa2023paso` (LLA 16, UxP 5, JxC 3).

## Estilo
Igual que los atlas 2023 y PASO 2023: paleta y bloques de logo del mapa presidencial 2023 de la Wikipedia (`logos/bloques_presidenciales/`: `up`, `lla`, `jxc23`, `hacemos`; pedido del usuario), y, para Bregman, el emblema FIT-U de la Wikipedia (`logos/Logo_FIT_Unidad.png`, el `.svg` pasado a PNG con Edge; el mapa de la Wikipedia 2023 no trae fila del FIT). Colores: UxP #009ce4, LLA #6c4c98, JxC #fcbc00, Hacemos #283084 y FIT #f65058, con la leyenda de `comun/leyenda_clara.js`. Con 5 filas lleva barras de 48 px, el alto de las de la Wikipedia 2023 (`LEG_SZ`, ver `AGENTS.md`), y la fila de Bregman, que no tiene franja de tonos porque no gana ninguna unidad, deja el mismo espacio arriba que las demás. La geometría y los recuadros son los de `mapa2027`: Departamentos_2010 con comunas, Lezama, Tolhuin y La Paz con el límite de 2022. Tolhuin no era departamento en 2023, pero el mapa de 2027 lo trae con su propio dato de 2023, porque la DINE publica la sección por separado.

Modos: GANÓ, MASSA, MILEI y BULL. Hay PNG en `png_transparentes/mapa2023massa/` y en `png_blanco/mapa2023massa/`. No hay paquete de Commons, porque es una simulación.
