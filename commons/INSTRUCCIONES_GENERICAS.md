# Subir un atlas a Commons: instrucciones genéricas

Valen para cualquier carpeta `commons/<año>/` (1916, 1922, 1930, 1983, 1985, 1987, 1989, 1991, 1993, 1994). Cada carpeta trae `subir/` (archivos con su wikitext `<archivo>.txt`) y su propio `LEEME_SUBIDA.md`, que dice qué se puede subir y qué está en espera. El caso de 1928 (ya subido) está en `commons_1928/`. Usuario de Commons: `ItsAHardLife`.

**Antes de nada**, abrir el `LEEME_SUBIDA.md` del año: si hay algo «en espera» (conflicto con el mapa vigente, logo sin licencia, dato a corregir), resolverlo primero.

## Qué hay en cada carpeta `subir/`
Por cada modo del atlas (ganador, voto de cada bloque, participación) tres versiones:

| Versión | Para qué |
|---|---|
| `(solo mapa).svg` | Sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia. Cada unidad lleva `<title>` con su nombre y resultado. **Es la más segura y la que conviene subir primero.** |
| `(con leyenda).svg` | El cartel completo con leyenda, torta y logos. El texto está a trazados (DejaVu Sans Bold): Commons ignora el ancho fijo del texto vivo y se cortaba el título. |
| `.png` | El cartel del atlas, transparente, con la tipografía tipo DIN de los PNG vigentes de es.wikipedia. |

## 1. Subir un archivo nuevo
1. Entrar en commons.wikimedia.org con `ItsAHardLife`.
2. Abrir `https://commons.wikimedia.org/wiki/Special:Upload` (formulario clásico; el asistente `Special:UploadWizard` no deja pegar el wikitext completo).
3. «Select file» y elegir el archivo de `commons/<año>/subir/`. El nombre de destino debe quedar **igual** al del archivo.
4. En el cuadro de descripción pegar todo el `.txt` del mismo nombre (`....svg.txt` o `....png.txt`).
5. **Licencia del desplegable: «Ninguna seleccionada»** (la primera). El wikitext ya trae `{{self|cc-by-4.0}}` y `{{Cc-by-2.5-ar}}`. Las opciones de «Trabajo propio» agregan GFDL, que no es compatible con CC BY 2.5 AR (la licencia de la base cartográfica), y las de «Licencias libres» son para obras ajenas.
6. «Upload file» y esperar unos segundos.
7. Abrir la página del archivo y mirar:
   - la miniatura se dibuja completa (mapa y recuadros; en «con leyenda» también leyenda, logos y textos; el título no pisa el recuadro del año);
   - la sección «Licencia» dice solo CC BY 4.0 y CC BY 2.5 AR, sin GFDL ni duplicados;
   - abajo aparecen las categorías.
   Si hay GFDL o la licencia está duplicada, «Editar» y dejar solo:
```
{{self|cc-by-4.0}}
{{Cc-by-2.5-ar}}
```
8. Si la miniatura sale rota, mandar una captura.

## 2. Subir una nueva versión de un archivo ya subido
1. En la página del archivo: «Historial del archivo» → «Subir una nueva versión de este archivo».
2. Elegir el archivo del mismo nombre de `subir/`. El nombre no se toca.
3. Poner un comentario que explique el cambio. No hay que pegar el wikitext otra vez: descripción y licencia quedan como están.
4. Mirar la miniatura.

## 3. Comprobar qué está subido
```
python commons/verificar_commons.py 1930
```
Compara el SHA1 de cada archivo de `subir/` con el de Commons: `IGUAL` (subido y al día), `DISTINTO` (subido pero distinto: subir una nueva versión) o `NO SUBIDO`.

## 4. Anunciar en la discusión del artículo
Hacerlo **antes** de poner el mapa en el artículo (es.wikipedia, página de discusión del artículo de la elección; el título está en el `LEEME_SUBIDA.md` del año, con un texto sugerido).
- No se trata de reemplazar los mapas vigentes: proponer **agregar el mapa por departamento en la sección de resultados** y dejar el del infobox, salvo que haya acuerdo.
- Avisar al autor del mapa vigente en su página de discusión (cortesía).
- Esperar unos días por si alguien objeta antes de editar el artículo.
- Si lo revierten, discutir en la página; no volver a poner el mismo cambio.

## 5. Licencias: qué se decidió y por qué
- **Geometría:** Rodríguez, Gonzalo Martín (2022). *Base cartográfica de departamentos para los censos nacionales de la República Argentina desde 1869 a 2010*. CONICET. Dataset, hdl:11336/149867 (`datosdeinvestigacion.conicet.gov.ar/handle/11336/149867`). Contribuidor: Pablo Ernesto De Grande. **CC BY 2.5 Argentina**, acceso abierto, sin restricción NC.
- **Por eso CC BY 4.0 y no BY-SA:** CC BY 2.5 permite derivados solo bajo la misma licencia o una posterior, así que BY 4.0 es lo más seguro. No soy abogado: ante duda, preguntar en el Café de Commons.
- **Votos:** son hechos; igual cada descripción cita la fuente (Cantón 1968 para 1916–1930; base de Ernesto Calvo para 1983–1994, que no está publicada: es lo que más puede preguntarte un revisor).
- **Logos:** solo van en «con leyenda» y PNG. Los de 1985 (sello FREJUDEPA), 1991 (MOPOF) y 1994 (primer logo del Frente Grande) no tienen licencia libre verificada: el usuario decidió subirlos igual (15-oct-2026) porque su aporte pesa más que el riesgo; el wikitext lo declara. Commons puede borrar esos archivos por derechos de autor; los «solo mapa» no llevan logos y no corren ese riesgo.
- **Versiones «con siglas»** (1985, 1991, 1994): el mismo cartel con la sigla del partido en lugar del emblema sin licencia (`(con leyenda y siglas).svg` y `(siglas).png`). Conviene subirlas siempre junto con las versiones con el logo: si Commons borra estas por derechos de autor, las de siglas quedan.
- **«Fair use»:** ni Commons ni es.wikipedia admiten contenido «de uso legítimo»: solo licencias libres. Que la boleta tenga 30 años no la vuelve libre (en Argentina los derechos duran 70 años después de la muerte del autor). La defensa realista de un emblema sin licencia es que sea demasiado simple para tener derechos de autor (`{{PD-textlogo}}` o `{{PD-ineligible}}`), y eso lo decide cada revisor. De ahí las versiones «con siglas».

## 6. Regenerar un paquete
```
python mapa<AÑO>/build_<AÑO>.py          # si cambió algo del atlas
python render_transparentes.py mapa<AÑO>  # PNG
python commons/paquete.py <año>           # SVG + wikitext + LEEME de ese año
```
Si se regenera algo ya subido, usar `verificar_commons.py` para ver qué hay que subir como nueva versión. La configuración de cada año (título del artículo, fuentes, logos, avisos) está en `commons/config.py`.

## 7. Qué no se verificó
- Los archivos nuevos no se probaron en el renderizador real de Commons (librsvg). Con 1928 sí: el «solo mapa» se dibujó bien y el «con leyenda» con texto vivo se cortaba (por eso ahora va a trazados).
- Las fechas de las elecciones están puestas de memoria; confirmarlas con el artículo.
- No se consultó a Rodríguez; la licencia de la página alcanza para Commons, pero un aviso al autor sería cortesía.
