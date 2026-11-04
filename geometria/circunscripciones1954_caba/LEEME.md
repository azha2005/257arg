# Capital Federal 1954: trazado aproximado, sin numeración oficial

Digitalización del esquema inferior, rotulado **1954**, de la imagen aportada
por el usuario. Se obtienen 14 recintos cerrados. No es un levantamiento de
límites legales ni una cartografía certificada.

## Costa y contorno

Por corrección del usuario, el marco final se toma **del SHP histórico de
Capital, con su detalle nativo**, conservado en la geometría del atlas 1948
(`mapas/mapa1948/units_raw.pkl`, generada por `geom4673`: Capital del SHP de
secciones de 1960). Se unen sus veinte secciones únicamente para obtener el
contorno exterior y la costa; no se usan sus límites internos para 1954.
No se aplica la simplificación de pantalla del SVG, ni se toma la silueta
esquemática de la imagen, ni se agregan rellenos costeros modernos. Esta
decisión sustituye el primer ajuste al contorno simplificado del SVG 1951.

La imagen aporta solamente la organización y los límites interiores. El flujo
deriva del de 1904/1951: vectorización, ajuste afín y RBF de perímetro, recorte
contra el contorno nativo del SHP y cierre exclusivamente geométrico de rendijas.
Los escalones del píxel se suavizan con una simplificación de cobertura de
2 píxeles que mantiene compartidas las fronteras entre polígonos. Se eliminan
los dientes de sierra y se conservan los giros mayores, sin redondearlos como
curvas decorativas. El desplazamiento máximo frente al trazado raster es
1,44 píxeles de la imagen útil y se conservan las 27 vecindades entre las
14 áreas. La costa no participa de esta simplificación.
**Se gira el dibujo 90° antihorarios antes del ajuste.** La orientación se
comprobó comparando el esquema de 1951 de la misma lámina con las geometrías
1951 de nuestro SVG, evaluando giros de 5° y emparejamientos de polígonos por
superficie compartida. El mejor giro fue 270° horarios de imagen (equivalente
a 90° antihorarios): coincidencia media de recintos 0,377 frente a 0,166 sin
giro; coincidencia del contorno 0,884 frente a 0,705 sin giro. La resolución,
el estilo esquemático y un recinto no separado en el raster de 1951 limitan
esas puntuaciones. Es evidencia de orientación, no una identificación legal
de las circunscripciones. Ver `comprobar_orientacion.py` y `ORIENTACION.json`.
La proyección de trabajo es la misma del proyecto, equirectangular con cos(38°)
y 44 píxeles por grado. Para el SHP se invierte esa transformación y se entregan
coordenadas WGS84 / EPSG:4326, listas para abrir en QGIS.

`CONTROL.json` conserva hashes, recorte, umbral, número de polígonos, controles,
validez topológica y comprobación de cobertura. La unión final coincide con el
contorno SHP de referencia; no tiene huecos ni solapamientos de área significativos.

## Identificación y límites de uso

- `id_trazo` 1–14 identifica los polígonos de esta digitalización, como se ve
  en la vista previa. **No es numeración oficial de circunscripciones.**
- `circ_of` queda vacío (`NULL`). La imagen no trae números y no permite
  establecer esa equivalencia de forma fiable.
- No se asignan partidos, ganadores ni votos. Para un atlas electoral falta
  una fuente numerada que permita unir cada polígono con su resultado de 1954.
- La fuente tiene aproximadamente 110 × 100 píxeles útiles para el esquema.
  El grosor de las líneas y la deformación del dibujo impiden precisión de
  calles o parcelas; el trazo interior debe tratarse como aproximado.
- Esto cubre Capital Federal, no todas las circunscripciones del país.

## Archivos

- `shp/caba_1954_trazado_aproximado.shp`, SHX, DBF, PRJ y CPG: 14 polígonos.
- GeoJSON equivalente en la misma carpeta.
- `caba_1954_aproximado.svg`: vector en las coordenadas de póster del proyecto;
  incluye el contorno costero del SHP sin simplificar.
- `vista_previa.png`: comparación con la imagen y correspondencia de `id_trazo`.
- `CABA_1954_SHP_aproximado.zip`: entrega para QGIS.
- `construir.py`: reconstrucción reproducible desde `fuente_aportada.png` y el SVG.

La imagen fue aportada por el usuario sin referencia bibliográfica ni licencia
identificadas. Se conserva su procedencia sin atribuir autoría propia al trazado
histórico; no se publica esta entrega en el sitio ni en Commons. Costa: base
histórica de departamentos/secciones de Rodríguez/CONICET, CC BY 2.5 Argentina,
ya usada por el proyecto. El SVG 1951 de Faustino Sojo se utiliza para el cotejo
de orientación; ver `mapas/mapa1951/LEEME_1951.md` para su atribución y licencias.
