# Insertar los mapas en los artículos de es.wikipedia

Para cuando los archivos de `commons/<año>/subir/` **ya estén subidos a Commons** (se comprueba con `python commons/verificar_commons.py <año>`: tienen que salir `IGUAL`). Antes de eso el wikitext de abajo muestra un enlace rojo. Usuario: `ItsAHardLife` (la cuenta unificada de Wikimedia sirve para Commons y es.wikipedia).

Generado por `commons/insertar_en_articulos.py` a partir de `config.py` y de los nombres reales de `subir/`; si se regenera un paquete, volver a correrlo.

## Criterio

- **Se agrega, no se reemplaza.** Los artículos traen en el cuadro de resultados (`{{Ficha de elección}}`) un mapa por distrito (provincia) en `|mapa =`. Los mapas nuevos van en una sección «Resultados por departamento» y no tocan ese. Solo si alguien en la discusión lo pide, se cambia el de la ficha:
  ```wikitext
  |mapa_título = Resultados por departamento
  |mapa        = Archivo:<archivo solo mapa de Resultados>
  |mapa_tamaño = 280px
  ```
- **Usar siempre las versiones «solo mapa»** (SVG sin texto, cada departamento con su `<title>`): son las más seguras, no llevan logos y se leen bien en miniatura. Las «con leyenda» y los PNG se enlazan desde la galería de Commons (la categoría del archivo) y no hace falta ponerlos en el artículo.
- **Un solo mapa grande** (el de «Resultados») y una galería con los demás (voto a cada bloque y participación). Si el artículo ya es largo, dejar solo el grande.
- **Lugar:** debajo de la tabla de resultados nacional/por distrito, antes de la sección de composición del Congreso o de las repercusiones. Si no hay sección de resultados por distrito, al final de «Resultados».
- **Pie de foto:** dice qué es, la geometría usada y la fuente; los datos completos y las licencias ya están en la página del archivo en Commons.
- **No insertar** los años «en espera» de abajo.

## Paso a paso (cada artículo)

1. Confirmar que el archivo existe en Commons con el nombre exacto (mayúsculas, espacios y paréntesis).
2. Abrir el artículo en es.wikipedia → «Editar código» (o «Editar»).
3. Pegar el bloque del año en el lugar elegido. Para ver la página antes de guardar: «Mostrar previsualización»; la miniatura tiene que dibujarse completa (mapa y recuadros).
4. Resumen de edición: el sugerido en cada bloque. Marcar «Edición menor» **no**: agrega contenido.
5. Guardar. Abrir el historial y controlar que no haya conflicto de edición.
6. Dejar una línea en la página de discusión, si no se hizo antes (ver abajo), con el enlace a la edición (`Especial:Diff/<número>`).

## Si Wikipedia no responde en la discusión

La falta de respuesta no es un permiso, pero tampoco una objeción. Procedimiento prudente:

1. **Esperar** unos 7 días desde el mensaje en la discusión (plazo sugerido; no es una regla de Wikipedia). Mirar el historial del artículo: si hubo ediciones recientes de otros usuarios, pueden haber visto el mensaje.
2. **Avisar** una vez más, breve, en la discusión: «Pasada una semana sin objeciones, agrego los mapas en una sección nueva sin tocar los existentes. Cualquiera puede revertir y discutirlo acá.» También avisar al autor del mapa vigente en su página de discusión (cortesía).
3. **Ser valiente** ([Wikipedia:Sé valiente al editar páginas](https://es.wikipedia.org/wiki/Wikipedia:S%C3%A9_valiente_al_editar_p%C3%A1ginas)): agregar la sección nueva, que es un cambio chico y fácil de revertir, sin borrar nada.
4. **Si lo revierten:** no volver a poner el mismo cambio ni entrar en guerra de ediciones; contestar en la discusión con la razón del revertido y buscar consenso ([Wikipedia:Consenso](https://es.wikipedia.org/wiki/Wikipedia:Consenso)). Se puede pedir una segunda opinión en el Café de es.wikipedia (`Wikipedia:Café`).
5. **Si el artículo está protegido** (candado): una cuenta nueva no puede editarlo. Dejar el pedido en la discusión con la plantilla de edición protegida (buscar «Editar protegida» / «Editar semiprotegida» entre las plantillas de es.wikipedia; el nombre exacto no se verificó) con el wikitext exacto del bloque.
6. **Dato que conviene tener a mano si preguntan:** de dónde salen los votos (fuente en la descripción de cada archivo; en 1983-1994 es la base de Ernesto Calvo, no publicada), de dónde sale la geometría (Rodríguez, CONICET, CC BY 2.5 AR) y que los bloques siguen la tabla del propio artículo.

## Reglas de estilo que ya se siguieron

- Texto del pie en español, sin etiquetas personalistas en las elecciones legislativas (partido o frente, no candidato).
- Los colores son los de la tabla del artículo, con tonos distintos entre sí; si alguien objeta un color, se corrige en el atlas y se sube una nueva versión del mismo archivo (el nombre no cambia y el artículo se actualiza solo).

## Por año

### Elecciones legislativas de Argentina de 1912

- Artículo: [Elecciones legislativas de Argentina de 1912](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1912) · fecha: 7 de abril de 1912 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1912 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1912 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (división departamental de 1914). Buenos Aires, Catamarca, Corrientes, Entre Ríos, Jujuy, La Rioja, Salta, San Juan, San Luis, Santiago del Estero y Tucumán se pintan enteras con su resultado provincial (sin datos departamentales). Fuente: Cantón (1968), expedientes de la Cámara de Diputados y prensa de época.]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1912 - Voto a Partidos Conservadores por departamento (solo mapa).svg|Voto a Partidos Conservadores
Archivo:Elecciones legislativas de Argentina de 1912 - Voto a UCR por departamento (solo mapa).svg|Voto a UCR
Archivo:Elecciones legislativas de Argentina de 1912 - Participacion por provincia (solo mapa).svg|Participación por provincia
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1914

- Artículo: [Elecciones legislativas de Argentina de 1914](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1914) · fecha: 22 de marzo de 1914 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1914 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1914 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (división departamental de 1914). Catamarca, Jujuy, Salta, San Juan, Santiago del Estero y Tucumán se pintan enteras con su resultado provincial (sin datos departamentales). Fuente: Cantón (1968), expedientes de la Cámara de Diputados y prensa de época.]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1914 - Voto a Partidos Conservadores por departamento (solo mapa).svg|Voto a Partidos Conservadores
Archivo:Elecciones legislativas de Argentina de 1914 - Voto a UCR por departamento (solo mapa).svg|Voto a UCR
Archivo:Elecciones legislativas de Argentina de 1914 - Participacion por provincia (solo mapa).svg|Participación por provincia
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1916

- Artículo: [Elecciones legislativas de Argentina de 1916](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1916) · fecha: 2 de abril de 1916 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1916 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1916 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (división departamental de 1914). San Juan y Santiago del Estero se pintan enteras con su resultado provincial (sin datos departamentales). Fuente: Cantón (1968) y expedientes de la Cámara de Diputados.]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1916 - Voto a Concentracion Conservadora por departamento (solo mapa).svg|Voto a Concentracion Conservadora
Archivo:Elecciones legislativas de Argentina de 1916 - Voto a UCR (Comite Nacional) por departamento (solo mapa).svg|Voto a UCR (Comite Nacional)
Archivo:Elecciones legislativas de Argentina de 1916 - Participacion por departamento (solo mapa).svg|Participación
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones presidenciales de Argentina de 1922

- Artículo: [Elecciones presidenciales de Argentina de 1922](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_1922) · fecha: 2 de abril de 1922 (confirmar con el artículo).
- Mapa principal: `Elecciones presidenciales de Argentina de 1922 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones presidenciales de Argentina de 1922 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (división departamental de 1914). Mendoza y Santiago del Estero se pintan enteras con su resultado provincial (sin datos departamentales). Fuente: Cantón (1968).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones presidenciales de Argentina de 1922 - Voto a Alvear (UCR) por departamento (solo mapa).svg|Voto a Alvear (UCR)
Archivo:Elecciones presidenciales de Argentina de 1922 - Voto a Pinero y afines por departamento (solo mapa).svg|Voto a Pinero y afines
Archivo:Elecciones presidenciales de Argentina de 1922 - Participacion por departamento (solo mapa).svg|Participación
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1930

- Artículo: [Elecciones legislativas de Argentina de 1930](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1930) · fecha: 2 de marzo de 1930 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1930 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1930 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (división departamental de 1914). Fuente: Cantón (1968).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1930 - Voto a Confederacion de las Derechas por departamento (solo mapa).svg|Voto a Confederacion de las Derechas
Archivo:Elecciones legislativas de Argentina de 1930 - Voto a Union Civica Radical por departamento (solo mapa).svg|Voto a Union Civica Radical
Archivo:Elecciones legislativas de Argentina de 1930 - Voto a radicalismo antipersonalista por departamento (solo mapa).svg|Voto a radicalismo antipersonalista
Archivo:Elecciones legislativas de Argentina de 1930 - Participacion por departamento (solo mapa).svg|Participación
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones presidenciales de Argentina de 1983

- Artículo: [Elecciones presidenciales de Argentina de 1983](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_1983) · fecha: 30 de octubre de 1983 (confirmar con el artículo).
- **EN ESPERA, no insertar todavía:** El mapa contradice el vigente en el artículo/Commons: discutirlo en la página de discusión antes de subir o insertar.
- Mapa principal: `Elecciones presidenciales de Argentina de 1983 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones presidenciales de Argentina de 1983 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1980). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones presidenciales de Argentina de 1983 - Voto a Alfonsin (UCR) por departamento (solo mapa).svg|Voto a Alfonsin (UCR)
Archivo:Elecciones presidenciales de Argentina de 1983 - Voto a Luder (PJ) por departamento (solo mapa).svg|Voto a Luder (PJ)
Archivo:Elecciones presidenciales de Argentina de 1983 - Participacion por departamento (solo mapa).svg|Participación
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1985

- Artículo: [Elecciones legislativas de Argentina de 1985](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1985) · fecha: 3 de noviembre de 1985 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1985 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1985 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1980). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1985 - Voto a PJ (FREJULI y afines) por departamento (solo mapa).svg|Voto a PJ (FREJULI y afines)
Archivo:Elecciones legislativas de Argentina de 1985 - Voto a UCR y aliados por departamento (solo mapa).svg|Voto a UCR y aliados
Archivo:Elecciones legislativas de Argentina de 1985 - Voto a peronismo renovador por departamento (solo mapa).svg|Voto a peronismo renovador
Archivo:Elecciones legislativas de Argentina de 1985 - Participacion por departamento (solo mapa).svg|Participación
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1987

- Artículo: [Elecciones legislativas de Argentina de 1987](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1987) · fecha: 6 de septiembre de 1987 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1987 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1987 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1980). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1987 - Voto a PJ (frentes justicialistas) por departamento (solo mapa).svg|Voto a PJ (frentes justicialistas)
Archivo:Elecciones legislativas de Argentina de 1987 - Voto a UCR y aliados por departamento (solo mapa).svg|Voto a UCR y aliados
Archivo:Elecciones legislativas de Argentina de 1987 - Voto a UCeDe y aliados por departamento (solo mapa).svg|Voto a UCeDe y aliados
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones presidenciales de Argentina de 1989

- Artículo: [Elecciones presidenciales de Argentina de 1989](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_1989) · fecha: 14 de mayo de 1989 (confirmar con el artículo).
- **EN ESPERA, no insertar todavía:** El mapa contradice el vigente en el artículo/Commons: discutirlo en la página de discusión antes de subir o insertar. Resolver Malargüe 1989 (corregir o anotar) antes de subir.
- Mapa principal: `Elecciones presidenciales de Argentina de 1989 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones presidenciales de Argentina de 1989 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1980). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones presidenciales de Argentina de 1989 - Voto a Alsogaray (Alianza de Centro) por departamento (solo mapa).svg|Voto a Alsogaray (Alianza de Centro)
Archivo:Elecciones presidenciales de Argentina de 1989 - Voto a Angeloz (UCR + CFI) por departamento (solo mapa).svg|Voto a Angeloz (UCR + CFI)
Archivo:Elecciones presidenciales de Argentina de 1989 - Voto a Menem - Duhalde por departamento (solo mapa).svg|Voto a Menem - Duhalde
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1991

- Artículo: [Elecciones legislativas de Argentina de 1991](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1991) · fecha: 8 de septiembre de 1991 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1991 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1991 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1991). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1991 - Voto a PJ y aliados por departamento (solo mapa).svg|Voto a PJ y aliados
Archivo:Elecciones legislativas de Argentina de 1991 - Voto a UCR y aliados por departamento (solo mapa).svg|Voto a UCR y aliados
Archivo:Elecciones legislativas de Argentina de 1991 - Voto a UCeDe y aliados por departamento (solo mapa).svg|Voto a UCeDe y aliados
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1993

- Artículo: [Elecciones legislativas de Argentina de 1993](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1993) · fecha: 3 de octubre de 1993 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1993 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1993 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1991 (con 2 de Abril de 2001)). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1993 - Voto a PJ y aliados por departamento (solo mapa).svg|Voto a PJ y aliados
Archivo:Elecciones legislativas de Argentina de 1993 - Voto a UCR y aliados por departamento (solo mapa).svg|Voto a UCR y aliados
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones de convencionales constituyentes de Argentina de 1994

- Artículo: [Elecciones de convencionales constituyentes de Argentina de 1994](https://es.wikipedia.org/wiki/Elecciones_de_convencionales_constituyentes_de_Argentina_de_1994) · fecha: 10 de abril de 1994 (confirmar con el artículo).
- Mapa principal: `Elecciones de convencionales constituyentes de Argentina de 1994 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones de convencionales constituyentes de Argentina de 1994 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1991 (con 2 de Abril de 2001)). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones de convencionales constituyentes de Argentina de 1994 - Voto a Frente Grande por departamento (solo mapa).svg|Voto a Frente Grande
Archivo:Elecciones de convencionales constituyentes de Argentina de 1994 - Voto a MODIN por departamento (solo mapa).svg|Voto a MODIN
Archivo:Elecciones de convencionales constituyentes de Argentina de 1994 - Voto a PJ (frentes justicialistas) por departamento (solo mapa).svg|Voto a PJ (frentes justicialistas)
Archivo:Elecciones de convencionales constituyentes de Argentina de 1994 - Voto a UCR y aliados por departamento (solo mapa).svg|Voto a UCR y aliados
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 1997

- Artículo: [Elecciones legislativas de Argentina de 1997](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_1997) · fecha: 26 de octubre de 1997 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 1997 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 1997 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1991 y 2001). San Luis se pintan enteras con su resultado provincial (sin datos departamentales). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 1997 - Voto a Accion por la Republica por departamento (solo mapa).svg|Voto a Accion por la Republica
Archivo:Elecciones legislativas de Argentina de 1997 - Voto a Alianza (UCR, FREPASO y aliados) por departamento (solo mapa).svg|Voto a Alianza (UCR, FREPASO y aliados)
Archivo:Elecciones legislativas de Argentina de 1997 - Voto a PJ y aliados por departamento (solo mapa).svg|Voto a PJ y aliados
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 2001

- Artículo: [Elecciones legislativas de Argentina de 2001](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2001) · fecha: 14 de octubre de 2001 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 2001 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 2001 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 1991 y 2001). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 2001 - Voto a ARI y socios por departamento (solo mapa).svg|Voto a ARI y socios
Archivo:Elecciones legislativas de Argentina de 2001 - Voto a Alianza (UCR, FREPASO y aliados) por departamento (solo mapa).svg|Voto a Alianza (UCR, FREPASO y aliados)
Archivo:Elecciones legislativas de Argentina de 2001 - Voto a Concertacion Justicialista por departamento (solo mapa).svg|Voto a Concertacion Justicialista
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 2009

- Artículo: [Elecciones legislativas de Argentina de 2009](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2009) · fecha: 28 de junio de 2009 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 2009 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 2009 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos vigentes en junio de 2009 y 15 comunas de Capital). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 2009 - Voto a Acuerdo Civico y Social y aliados por departamento (solo mapa).svg|Voto a Acuerdo Civico y Social y aliados
Archivo:Elecciones legislativas de Argentina de 2009 - Voto a Frente para la Victoria y aliados por departamento (solo mapa).svg|Voto a Frente para la Victoria y aliados
Archivo:Elecciones legislativas de Argentina de 2009 - Voto a Peronismo Federal y aliados por departamento (solo mapa).svg|Voto a Peronismo Federal y aliados
Archivo:Elecciones legislativas de Argentina de 2009 - Voto a Union PRO y aliados por departamento (solo mapa).svg|Voto a Union PRO y aliados
Archivo:Elecciones legislativas de Argentina de 2009 - Participacion por departamento (solo mapa).svg|Participación
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

### Elecciones legislativas de Argentina de 2013

- Artículo: [Elecciones legislativas de Argentina de 2013](https://es.wikipedia.org/wiki/Elecciones_legislativas_de_Argentina_de_2013) · fecha: 27 de octubre de 2013 (confirmar con el artículo).
- Mapa principal: `Elecciones legislativas de Argentina de 2013 - Resultados por departamento (solo mapa).svg`

Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):

```wikitext
=== Resultados por departamento ===
[[Archivo:Elecciones legislativas de Argentina de 2013 - Resultados por departamento (solo mapa).svg|miniaturadeimagen|centro|550px|Resultado por departamento (departamentos de 2010 (con comunas de CABA y Lezama)). Fuente: base de datos electorales por departamento (ver la descripción del archivo).]]

<gallery mode="packed" heights="200px">
Archivo:Elecciones legislativas de Argentina de 2013 - Voto a Frente Progresista Civico y Social y aliados por departamento (solo mapa).svg|Voto a Frente Progresista Civico y Social y aliados
Archivo:Elecciones legislativas de Argentina de 2013 - Voto a Frente Renovador y aliados por departamento (solo mapa).svg|Voto a Frente Renovador y aliados
Archivo:Elecciones legislativas de Argentina de 2013 - Voto a Frente para la Victoria y aliados por departamento (solo mapa).svg|Voto a Frente para la Victoria y aliados
Archivo:Elecciones legislativas de Argentina de 2013 - Voto a Union PRO y aliados por departamento (solo mapa).svg|Voto a Union PRO y aliados
Archivo:Elecciones legislativas de Argentina de 2013 - Participacion por departamento (solo mapa).svg|Participación
</gallery>
```

Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`

## Sin mapa para insertar

1995 (hay dos versiones del atlas y ya existe un mapa por departamento en Commons), 1916 ficticio (línea temporal alternativa), AMBA 2025 (falta verificar la licencia de la geometría de circuitos) y el escenario 2027 (simulación): no tienen paquete. 1928 se subió desde `commons_1928/`; su bloque se puede armar igual con los nombres de `commons_1928/subir/`.
