"""Genera commons/INSERTAR_EN_ARTICULOS.md: instrucciones para poner en cada articulo de es.wikipedia los mapas ya subidos a Commons,
con el wikitext listo para pegar de cada año (nombres de archivo exactos de commons/<año>/subir/).

    python commons/insertar_en_articulos.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as C

FUENTE = {   # fuente corta para el pie de foto (la completa esta en la descripcion de cada archivo en Commons)
    "1912": "Cantón (1968), expedientes de la Cámara de Diputados y prensa de época",
    "1914": "Cantón (1968), expedientes de la Cámara de Diputados y prensa de época",
    "1916": "Cantón (1968) y expedientes de la Cámara de Diputados",
    "1922": "Cantón (1968)", "1930": "Cantón (1968)",
}


HOLD = {
    "contradice_wikipedia_1983": "El mapa contradice el vigente en el artículo/Commons: discutirlo en la página de discusión antes de subir o insertar.",
    "contradice_wikipedia_1989": "El mapa contradice el vigente en el artículo/Commons: discutirlo en la página de discusión antes de subir o insertar.",
    "malargue_1989": "Resolver Malargüe 1989 (corregir o anotar) antes de subir.",
}


def short(a):
    return FUENTE.get(a, "base de datos electorales por departamento (ver la descripción del archivo)")


def main_files(year):
    sub = os.path.join(HERE, year, "subir")
    fs = sorted(f for f in os.listdir(sub) if f.endswith(".svg") and "(solo mapa)" in f)
    res = [f for f in fs if " - Resultados por departamento" in f]
    part = [f for f in fs if " - Participacion por " in f]
    rest = [f for f in fs if f not in res and f not in part]
    return (res[0] if res else None), rest, (part[0] if part else None)


def label(fn):
    m = re.search(r" - (.*?) por departamento", fn)
    return m.group(1) if m else fn


def year_block(year):
    A = C.ATLAS[year]
    art = A["article"]
    res, rest, part = main_files(year)
    geom = C.GEOM_SHORT.get(A["geom"], A["geom"])
    pie = "Resultado por departamento (%s)." % geom
    if A.get("solido"):
        pie += " %s se pintan enteras con su resultado provincial (sin datos departamentales)." % A["solido"][0]
    out = ["### %s" % art, ""]
    out.append("- Artículo: [%s](https://es.wikipedia.org/wiki/%s) · fecha: %s (confirmar con el artículo)." % (art, art.replace(" ", "_"), A["fecha"]))
    held = [HOLD.get(h, h) for h in (A.get("hold") or [])]
    if held:
        out.append("- **EN ESPERA, no insertar todavía:** " + " ".join(held))
    out.append("- Mapa principal: `%s`" % res)
    out += ["", "Sección nueva (o al final de «Resultados», debajo de la tabla de resultados por distrito):", "", "```wikitext",
            "=== Resultados por departamento ===",
            "[[Archivo:%s|miniaturadeimagen|centro|550px|%s Fuente: %s.]]" % (res, pie, short(year)), "",
            "<gallery mode=\"packed\" heights=\"200px\">"]
    for f in rest:
        out.append("Archivo:%s|%s" % (f, "Voto a " + label(f)[len("Voto a "):] if label(f).startswith("Voto a ") else label(f)))
    if part:
        out.append("Archivo:%s|%s" % (part, "Participación por provincia" if "por provincia" in part else "Participación"))
    out += ["</gallery>", "```", ""]
    out.append("Resumen de edición sugerido: `Agrego mapas de resultados por departamento (Commons); ver discusión`")
    out.append("")
    return "\n".join(out)


HEAD = """# Insertar los mapas en los artículos de es.wikipedia

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

"""

TAIL = """
## Sin mapa para insertar

1995 (hay dos versiones del atlas y ya existe un mapa por departamento en Commons), 1916 ficticio (línea temporal alternativa), AMBA 2025 (falta verificar la licencia de la geometría de circuitos) y el escenario 2027 (simulación): no tienen paquete. 1928 se subió desde `commons_1928/`; su bloque se puede armar igual con los nombres de `commons_1928/subir/`.
"""


def main():
    years = [y for y in sorted(C.ATLAS) if os.path.isdir(os.path.join(HERE, y, "subir"))]
    body = "\n".join(year_block(y) for y in years)
    open(os.path.join(HERE, "INSERTAR_EN_ARTICULOS.md"), "w", encoding="utf8", newline="\n").write(HEAD + body + TAIL)
    print("escrito INSERTAR_EN_ARTICULOS.md con", len(years), "años:", years)


if __name__ == "__main__":
    main()
