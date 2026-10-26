"""Arma la carpeta de subida a Commons: copia los PNG con su nombre final y escribe el wikitext de cada archivo.

    python commons_1928/make_descripciones.py   -> commons_1928/subir/<archivo>  y  subir/<archivo>.txt
"""
import os
import shutil
from build_commons_svg import NAMES, filename, BASE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "subir")
USER = "[[User:ItsAHardLife|ItsAHardLife]]"

LOGOS = ("* Emblemas (todos con licencia libre en Commons): [[:File:Flag of Radical Civic Union.svg|]] (bandera bicolor, sin el escudo, que es de 1931), "
         "[[:File:Monograma utilizado por la UCR Antipersonalista.svg|]], [[:File:Emblema del Partido Socialista Argentino.svg|]] y [[:File:Escudo del PDP.svg|]].")

CATS_COMMON = ["1928 Argentine general election", "1928 elections in Argentina", "Election maps of Argentine presidential elections",
               "Maps of Argentina by department", "1928 election maps"]

ES = ("Resultados por departamento de las elecciones presidenciales de Argentina del 1.º de abril de 1928 (solo varones; división departamental de 1914): {what}. "
      "Los bloques siguen la tabla del artículo de la Wikipedia en español. Gris claro: territorios nacionales (no votaban).{dark_es} "
      "Recuadros: Tucumán, Gran San Juan, Gran Mendoza, Resistencia + Corrientes capital, Área Metropolitana de Buenos Aires y Capital Federal (por circunscripción). No lleva recuadro de la Antártida: en 1928 no había sector antártico reclamado ni voto allí.")
EN = ("Results by department of the 1 April 1928 Argentine presidential election (men only; 1914 department boundaries): {what_en}. "
      "Blocs follow the table of the Spanish Wikipedia article. Light grey: national territories (no vote).{dark_en}")
WHAT_EN = {"gan": "winning bloc by department, shade by vote share", "ucr": "share of Hipólito Yrigoyen (UCR)", "opo": "share of the opposition", "par": "turnout (voters over registered)"}


def wikitext(mode, kind):
    what = NAMES[mode][0]
    flat = open(os.path.join(HERE, "svg_plano", "atlas_1928_%s.svg" % mode), encoding="utf8").read()
    dark = (" Gris oscuro: sin dato o cifras subsumidas en otra unidad.", " Dark grey: no data or figures merged into another unit.") if "Sin dato" in flat else ("", "")   # solo si el modo lo usa
    src = ["* Votos: Cantón, Darío (1968). ''Materiales para el estudio de la sociología política en la Argentina'', tomo II, «Elecciones nacionales de electores de presidente y vice, 1928 (varones solamente)». Transcritos a mano desde las imágenes del libro; contraste con Lupu y Stokes (cifras que no cierran, marcadas en la ficha de cada unidad).",
           "* Equivalencias de nombres: Cacopardo (1967), DTS n.º 47, cuadro 1.",
           "* Geometría: Rodríguez, Gonzalo Martín (2022). ''Base cartográfica de departamentos para los censos nacionales de la República Argentina desde 1869 a 2010'' (versión 2026 v2; contribuidor: Pablo Ernesto De Grande). CONICET. Dataset, [http://hdl.handle.net/11336/149867 hdl:11336/149867] ([https://datosdeinvestigacion.conicet.gov.ar/handle/11336/149867 Datos de Investigación CONICET]), licencia CC BY 2.5 Argentina. Departamentos de 1914; se les unieron, simplificaron y recortaron los polígonos.",
           "* Bloques y resultado nacional: [[:es:Elecciones presidenciales de Argentina de 1928]]. Antártida: Natural Earth 1:50m (dominio público).",
           "* Elaborado con código propio y asistido por herramientas de IA; los mapas no son imágenes generadas por IA."]
    if mode == "gan" and kind != "mapa":
        src.insert(4, LOGOS)
    if kind == "mapa":
        src.append("* Cada departamento lleva un elemento <title> con su nombre y resultado; el archivo no contiene texto ni leyenda (como el mapa por departamento de 2019).")
    cats = list(CATS_COMMON) + (["SVG maps of Argentina"] if kind != "png" else [])
    return ("=={{int:filedesc}}==\n{{Information\n|description={{es|1=%s}}\n{{en|1=%s}}\n|date=2026-10-16\n|source={{own}}<br/>\n%s\n|author=%s\n|permission=\n"
            "|other versions=%s\n}}\n\n=={{int:license-header}}==\n{{self|cc-by-4.0}}\n{{Cc-by-2.5-ar}} <!-- base cartográfica de Rodríguez (CONICET), ver |source= -->\n\n%s\n") % (
        ES.format(what=what, dark_es=dark[0]), EN.format(what_en=WHAT_EN[mode], dark_en=dark[1]), "\n".join(src), USER,
        "\n".join("[[:File:%s|]]" % n for n in others(mode, kind)), "\n".join("[[Category:%s]]" % c for c in cats))


def others(mode, kind):
    names = {"png": BASE + NAMES[mode][1] + ".png", "leyenda": filename(mode, "leyenda"), "mapa": filename(mode, "mapa")}
    return [n for k, n in names.items() if k != kind]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for mode in NAMES:
        files = {"png": BASE + NAMES[mode][1] + ".png", "leyenda": filename(mode, "leyenda"), "mapa": filename(mode, "mapa")}
        shutil.copy(os.path.join(ROOT, "../png_transparentes", "mapa1928", "atlas_1928_%s.png" % mode), os.path.join(OUT, files["png"]))
        for kind in ("leyenda", "mapa"):
            shutil.copy(os.path.join(HERE, "svg", files[kind]), os.path.join(OUT, files[kind]))
        for kind, fn in files.items():
            open(os.path.join(OUT, fn + ".txt"), "w", encoding="utf8").write(wikitext(mode, kind))
            print(fn)
