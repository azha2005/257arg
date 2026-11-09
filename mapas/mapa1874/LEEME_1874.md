# Atlas presidencial de 1874

Avellaneda (Alsina-Avellaneda, PAN) contra Mitre (Partido Nacionalista), elección de electores del 12 de abril de 1874.

```
"C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/mapa1874/build_1874.py
```

Salida: `atlas_1874.html`, `dataset_1874.json`, `CONTROL_1874.json`; capturas en `img/`.

## Datos

- **Buenos Aires, por partido y parroquia**: cuadro de prensa del 17 de mayo de 1874 (recortes aportados por el usuario), transcripto en `cuadro_17mayo1874.csv`: 14 parroquias de la ciudad y 69 partidos de la campaña. Se conservan las marcas del original: «Nula» (Balvanera), «Falsificada» (Chacabuco), «No hubo elección» (Necochea) van en gris; las filas alsinistas que el diario marca como falsificadas quedan solo en la nota de la ficha. Un guion es cifra ausente, no cero; «Nada» es cero. Doce unidades tienen cifra de un solo bando: color claro propio, sin porcentaje ni ganador.
- **Resultados provisorios fuera de Buenos Aires**. San Luis capital (382 Mitre, 92 Avellaneda, La Prensa del 14 de abril) se muestra en el polígono del departamento La Capital como aproximación. Guaymallén, La Paz, Junín, Rosario y San Carlos (La Nación del 17 de abril) se colorean por ganador informado, sin porcentajes. El resto queda beige. Los electores figuran como contexto en las métricas generales.
- **Territorios** (Chaco, Pampa, Patagonia, Tierra del Fuego) en gris, sin elección. Misiones estaba bajo jurisdicción de Corrientes hasta 1881: gris, con nota.

## Total provisorio (torta y barras)

Pedido del usuario: a falta de cifras de votos para todo el país, la torta y las barras usan el **total impreso del cuadro bonaerense**: Mitre 14.971 (55,30 %), Alsina-Avellaneda 12.103 (44,70 %). No representa al país: Avellaneda ganó el colegio electoral 145 a 79 (4 no votaron). Las métricas muestran ambas cosas.

Las filas del recorte suman Mitre 14.469 y Alsina-Avellaneda 9.040. La diferencia con el total impreso (502 y 3.063) incluye las filas alsinistas marcadas como falsificadas (2.398 entre Vecino, Tuyú, Juárez, Monsalvo y San Andrés de Giles) y partidos que el recorte no trae. No se ajusta ninguna cifra. La Wikipedia da 25.800 votantes para todo el país (Statistical Abstract of Latin America), menos que el total del cuadro bonaerense: no se usa.

El cuadro es de un diario y la elección fue muy disputada (revolución mitrista de septiembre de 1874); las marcas de fraude son del diario.

## Geometría

- Departamentos del censo de 1869 (Rodríguez y De Grande, CONICET), con la proyección de los atlas 1912-1940.
- Ciudad: las 14 parroquias de 1872-1886 con el trazo ajustado a la base (`geometria/parroquias_capital_1864_1898/parroquias_1872_base.shp`).
- Correspondencias: Lomas de Zamora = La Paz y General Lavalle = Ajó en el censo de 1869. General Alvear (creado en 1869) no tiene polígono en ese censo: toma el de 1895, descontado de Saladillo (44 % de su superficie).
- Partidos bonaerenses sin fila en el recorte, en beige: Arenales, Frontera, Frontera (costa), Martín García, Patagones, Rivadavia y San Martín.

## Estilo

- Colores (pedido del usuario): PAN celeste claro #74acdf (el de los atlas de 1904), mitristas azul oscuro #1c3f94. Siglas PAN y PN: no se buscó logo de época.
- Para que se distingan (pedido del usuario), cada uno tiene su propia rampa de siete tonos (`ramp` en `CAND`, leída por un parche a `shade()`): el PAN queda siempre en celestes pálidos (hasta #7dbbe6) y Mitre siempre en azules oscuros (desde #2b4196 al 50 %). Las unidades con una sola cifra van rayadas en el color de ese bando, no en un tono liso. Como el ganador de un mano a mano siempre pasa del 50 %, los dos rangos no se cruzan. Las coropletas usan las mismas rampas.
- Recuadros: alrededores de la ciudad y Ciudad de Buenos Aires; sin Tucumán (provincia sólida) ni Antártida (anterior a 1946).
- Tres modos: Ganó, % Mitre y % Avellaneda (sobre los votos de ambos bandos).

## Pendiente

- Identificar el diario del cuadro y completar los partidos que faltan.
- Fichas al hacer clic: no se probaron en el navegador.
- Sin PNG transparentes, catálogo del sitio ni Commons.
- `mapas/mapa1874pres/` es el mapa simple anterior (sin commitear); este atlas lo reemplaza.
- El visor de la ciudad (`mapas/capital_canton/`) sigue con alsinismo rojo y mitrismo azul real en 1874.

## Incorporaciones del 8-nov-2026 (cotejadas sobre los PDF de La Nación del repo)

- **San Juan**: acta de la Junta Escrutadora del 12 de mayo (*La Nación*, 2 de junio, p. 1, col. 3): Mitre 1.365, Avellaneda 916. Incluye 88 votos expresados de Albardón, cuyo registro anota 166 sufragantes; la Junta dejó al Congreso los 78 restantes. Color sólido con la cifra provincial.
- **La Rioja**: cuadro «Cópia del escrutinio practicado el día 12 de Abril» de un corresponsal mitrista (*La Nación*, 29 de mayo, p. 1, cols. 6–7). Columnas Mitre / Avellaneda en mesas legales / Avellaneda en mesas impugnadas: 1.265 / 1.224 / 1.054, y cierran por fila. La provincia lleva el total de la Junta: Avellaneda 2.278, Mitre 1.265 (saldo de 1.013). Arauco, Guandacol y Belgrano solo tienen mesas impugnadas: gris. Chilecito y San Martín se calculan con las mesas legales, y las impugnadas van en la ficha. Costa del Medio (Tama), 0 a 196, no tiene polígono en 1869 y queda en la nota provincial.
- **Buenos Aires**: el acta de la Junta del 16 de mayo (*La Nación*, 29 de mayo, p. 1, col. 4) da 14.971 para Mitre, 12.103 para Alsina y una diferencia de 2.868. Coincide con el total impreso que ya se usaba.
- **Patagones**: 55 para Mitre y guion para Alsina en el cuadro del 17 de mayo (`fuentes/hemeroteca/la_nacion_1874/cuadro_17mayo_cotejado.csv`). Faltaba en el CSV del atlas.

Correcciones al reporte externo que traía estos datos. **La Rioja**: Capital es 255–259, no 242–289, y Chilecito trae 409 para Mitre, no 000. Con esas lecturas las columnas cierran exactamente. **Buenos Aires**: el acta no dice 12.750 ni 647. **Bragado y Ayacucho**: ya figuraban en el cuadro con 319–281 y 120–32. **Rauch**: *La Nación* del 16 de abril da 40 para Mitre y no da una cifra alsinista legible. Se conserva el 259–40 del cuadro.

**8-nov-2026, segunda pasada**: las provincias y departamentos sin voto popular completo llevan un tono claro con el color de quien ganó sus electores según la Wikipedia: celeste para Avellaneda y lavanda para Mitre (Santiago del Estero). Los datos departamentales de prensa se conservan. La torta suma el voto popular conocido de Buenos Aires, San Juan y La Rioja (Junta): Mitre 17.601, Avellaneda 15.297.

## Variantes agregadas el 8-nov-2026
En la ficha, sin cambiar el cuadro: San Antonio de Areco 77 Mitre / 59 Alsina (*La Nación*, 23 de abril) y San Miguel 281 Mitre / 172 Alsina (*La Nación*, 15 de abril). Vienen de un informe externo y no se cotejaron con el escaneo.
