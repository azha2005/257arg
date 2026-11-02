# Presidenciales 2007 en el AMBA, por circuito

Primera entrega solicitada: Capital Federal y los mismos 40 partidos del atlas AMBA 2025. El archivo aportado corresponde a 2007, no a 2025.

## Abrir y regenerar

`atlas_amba2007.html` es autocontenido. Para navegador integrado, servir la raíz por HTTP.

Desde la raíz:

```
python mapas/mapa2007circuitos/preparar.py
python mapas/mapa2007circuitos/build_2007circuitos.py --amba
python mapas/mapa2007circuitos/verificar.py --amba
```

## Datos y alcance

- Votos exclusivamente de `C:/Users/JC/Downloads/Query resultsee1 (2).xlsx`, hoja Sheet1, filas desde la 5. Se conserva el archivo original. Hoja1 es una tabla dinámica con porcentajes y subtotales: no se suma ni se utiliza como segunda fuente.
- Recorte: 597 circuitos en la planilla y 6.933.581 votos positivos; 572 unidades cartográficas, incluidas zonas sin correspondencia y circuitos subdivididos sumados al polígono padre. Una unidad cartográfica puede reunir varios circuitos de la planilla.
- Torta y barras son la suma regional del archivo, sobre votos positivos. No son el resultado nacional. Solo los ganadores sin empate aparecen en la leyenda: FPV, CC y UNA. Las demás candidaturas quedan en Otros y en cada ficha.
- No se añaden electores, blancos ni nulos: faltan en el archivo. No hay participación local.
- PolAr `data__arg_presi_gral2007.csv` aporta nombres para las claves de sección; no aporta votos.

## Cartografía y estilo

Serie local `geometria/circuitos_serie/por_anio/2007/aproximada/circuitos_argentina.geojson`. CABA: capa histórica con referencia 2006, de fecha ambigua; Buenos Aires: aporte histórico 2003 con supuesto de proyección EPSG:22193. No se presenta como cartografía certificada de 2007. Las fichas conservan fuente y reservas. Los códigos INDRA del aporte bonaerense se cruzan por sección y circuito; CABA, por circunscripción y circuito.

Se reutilizan plantilla, paleta, torta, leyenda, búsqueda, zoom y fichas del proyecto. Recuadros regionales como en AMBA 2025: Capital, conurbano y Gran La Plata. Se usan siglas, sin incorporar logos de fecha o licencia incierta. Beige: sin datos o sin correspondencia; gris: empate, sin desempate arbitrario. Se conservan los huecos de la geometría.

Se exportaron los seis modos en PNG blanco y transparente, y las copias blancas a `png_transparentes/all elections white bg/`. Validación de modos, sumas, fichas y clic real en `VALIDACION.json`; revisión visual de los seis modos realizada. No se publicó en Commons.
