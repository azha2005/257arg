"""Termina los SVG planos de export_svg.py para subirlos a Commons. Dos variantes por modo:

    python commons_1928/build_commons_svg.py   -> commons_1928/svg/<archivo>.svg

- «solo mapa» (como el mapa de 2019 de es.wikipedia, de Faustino Sojo): sin ningun texto ni leyenda; cada unidad lleva <title> con su
  nombre y resultado. Sin tipografias: no hay nada que reemplazar.
- «con leyenda»: el cartel completo; el texto va a trazados (DejaVu Sans Bold, libre, estirada al ancho de la tipografia del atlas),
  porque Commons ignora textLength y con texto vivo el titulo pisaba el recuadro del año.

En las dos: logos SVG en data-URI -> contenido inline (MediaWiki no admite data:image/svg+xml); colores rgb()/rgba() -> hex + opacidad;
sin CSS, sin ids sueltos, sin comentarios del atlas; sombra feDropShadow -> filtro clasico.
"""
import base64
import io
import json
import os
import re
import sys
import tempfile
from lxml import etree
import numpy as np
from PIL import Image
import resvg_py
import matplotlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "http://www.w3.org/2000/svg"
XL = "http://www.w3.org/1999/xlink"
Q = lambda t: "{%s}%s" % (NS, t)
FONTS = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")

NAMES = {   # modo -> (descripcion corta, nombre base del archivo)
    "gan": ("bloque ganador por departamento", "Resultados por departamento"),
    "ucr": ("porcentaje de Hipólito Yrigoyen (UCR) por departamento", "Voto a Yrigoyen por departamento"),
    "opo": ("porcentaje de la oposición por departamento", "Voto a la oposicion por departamento"),
    "par": ("participación (votantes sobre inscriptos) por departamento", "Participacion por departamento"),
}
VARIANTS = {"mapa": " (solo mapa)", "leyenda": " (con leyenda)"}
BASE = "Elecciones presidenciales de Argentina de 1928 - "


def filename(mode, variant):
    return BASE + NAMES[mode][1] + VARIANTS[variant] + ".svg"


def to_hex(v):
    """'rgb(1, 2, 3)' / 'rgba(..)' -> ('#010203', alpha) ; otros valores sin cambio."""
    m = re.match(r"rgba?\(([^)]+)\)$", v.strip())
    if not m:
        return v, None
    p = [float(x) for x in m.group(1).replace("/", ",").replace(" ", ",").split(",") if x != ""]
    a = p[3] if len(p) > 3 else 1.0
    return "#%02x%02x%02x" % tuple(int(round(c)) for c in p[:3]), (a if a < 1 else None)


class Face:
    def __init__(self, fn):
        self.f = TTFont(os.path.join(FONTS, fn))
        self.gs = self.f.getGlyphSet(); self.cmap = self.f.getBestCmap(); self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def advance(self, ch):
        return self.hmtx[self.cmap.get(ord(ch), ".notdef")][0]

    def path(self, s, size, x0, y, sx, ls):
        """trazado del texto s: base en (x0, y), estirado sx en horizontal, letter-spacing ls (px)."""
        k = size / self.upm
        pen = SVGPathPen(self.gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        penx = 0.0
        for ch in s:
            g = self.cmap.get(ord(ch), ".notdef")
            self.gs[g].draw(TransformPen(pen, Transform(sx * k, 0, 0, -k, x0 + sx * k * penx, y)))
            penx += self.advance(ch) + ls / k
        return pen.getCommands()

    def width(self, s, size, ls):
        return sum(self.advance(c) for c in s) * size / self.upm + ls * len(s)


BOLD, BOLDI = Face("DejaVuSans-Bold.ttf"), Face("DejaVuSans-BoldOblique.ttf")


def text_to_path(t, info):
    """El texto pasa a trazados (DejaVu Sans Bold, licencia libre) estirados al ancho que tenia con la tipografia del atlas:
    Commons (librsvg) ignora textLength y con texto vivo el titulo se corria sobre el recuadro del año."""
    s = "".join(t.itertext())
    face = BOLDI if info["it"] else BOLD
    ls = info["ls"]
    target = float(info["tl"]) if info["tl"] else info["w"]
    nat = face.width(s, info["fs"], ls)
    sx = target / nat if nat else 1.0
    x = float(t.get("x", 0)); y = float(t.get("y", 0))
    x0 = x - (target / 2 if info["anchor"] == "middle" else target if info["anchor"] == "end" else 0)
    p = etree.Element(Q("path"))
    p.set("d", face.path(s, info["fs"], x0, y, sx, ls))
    for a in ("fill", "stroke", "stroke-width", "stroke-linejoin", "stroke-linecap", "stroke-opacity", "fill-opacity", "opacity", "paint-order", "transform"):
        if t.get(a) is not None:
            p.set(a, t.get(a))
    etree.SubElement(p, Q("title")).text = s
    p.tail = t.tail
    return p


def inline_logo(img, idx):
    """<image href=data:image/svg+xml...> -> <svg x y width height viewBox> con el logo adentro."""
    href = img.get("href") or img.get("{%s}href" % XL)
    m = re.match(r"data:image/svg\+xml;base64,(.*)$", href, re.S)
    if not m:
        return None
    root = etree.fromstring(base64.b64decode(m.group(1)))
    assert root.find(".//" + Q("style")) is None and root.find(".//" + Q("script")) is None, "logo con <style>/<script>"
    vb = root.get("viewBox")
    if not vb:
        vb = "0 0 %s %s" % (re.sub(r"[a-z%]+$", "", root.get("width")), re.sub(r"[a-z%]+$", "", root.get("height")))
    out = etree.Element(Q("svg"))
    for a in ("x", "y", "width", "height"):
        out.set(a, img.get(a))
    out.set("viewBox", vb)
    if img.get("preserveAspectRatio"):
        out.set("preserveAspectRatio", img.get("preserveAspectRatio"))
    ids = {e.get("id"): "logo%d_%s" % (idx, e.get("id")) for e in root.iter() if e.get("id")}
    for e in list(root.iter()):
        if e is not root and (not isinstance(e.tag, str) or etree.QName(e).namespace != NS):
            e.getparent().remove(e)
    for e in root.iter():
        for k, v in list(e.attrib.items()):
            if k == "id":
                e.set("id", ids[v])
            elif k in ("href", "{%s}href" % XL) and v.startswith("#"):
                e.set(k, "#" + ids[v[1:]])
            elif "url(#" in v:
                e.set(k, re.sub(r"url\(#([^)]+)\)", lambda mm: "url(#%s)" % ids[mm.group(1)], v))
            elif k.startswith("{") and etree.QName(k).namespace != NS:
                del e.attrib[k]
    for ch in list(root):
        if isinstance(ch.tag, str) and etree.QName(ch).localname not in ("metadata", "namedview"):
            out.append(ch)
    return out


def content_bbox(svg_text, margin=12):
    """caja ocupada por el dibujo (se renderiza con resvg) -> (x, y, w, h) en unidades del viewBox"""
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf8") as f:
        f.write(svg_text); fn = f.name
    try:
        im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_path=fn, width=1920, height=1649)))).convert("RGBA")
    finally:
        os.remove(fn)
    a = np.asarray(im)[:, :, 3] > 8
    ys, xs = np.where(a)
    x0, x1, y0, y1 = max(xs.min() - margin, 0), min(xs.max() + margin, 1919), max(ys.min() - margin, 0), min(ys.max() + margin, 1648)
    return int(x0), int(y0), int(x1 - x0 + 1), int(y1 - y0 + 1)


def process(mode, variant):
    infos = json.load(open(os.path.join(HERE, "svg_plano", "textos_%s.json" % mode)))
    root = etree.parse(os.path.join(HERE, "svg_plano", "atlas_1928_%s.svg" % mode), etree.XMLParser(remove_comments=True, huge_tree=True)).getroot()
    if variant == "mapa":   # sin textos, titulo, torta ni leyenda
        for i in ("title", "yearbox", "pie", "legend"):
            for e in root.iter(Q("g"), Q("rect")):
                if e.get("id") == i:
                    e.getparent().remove(e); break
        for t in list(root.iter(Q("text"))):
            t.getparent().remove(t)
    else:
        for t in list(root.iter(Q("text"))):
            t.getparent().replace(t, text_to_path(t, infos[int(t.get("data-t"))]))
    for i, img in enumerate(list(root.iter(Q("image")))):
        new = inline_logo(img, i)
        if new is not None:
            img.getparent().replace(img, new)
    for e in list(root.iter()):
        if not isinstance(e.tag, str):
            continue
        if e.get("data-title") and e.tag == Q("path"):
            ti = etree.Element(Q("title")); ti.text = e.get("data-title"); e.insert(0, ti)
        for a in ("fill", "stroke"):
            v = e.get(a)
            if v:
                h, al = to_hex(v); e.set(a, h)
                if al is not None:
                    k = a + "-opacity"; e.set(k, "%g" % (float(e.get(k, 1)) * al))
        for a in list(e.attrib):
            if a.startswith("data-"):
                del e.attrib[a]
        if e.tag == Q("path") and e.get("fill") == "none" and e.get("stroke") == "none":
            e.getparent().remove(e)
    for f in root.iter(Q("filter")):
        for ch in list(f):
            f.remove(ch)
        for tag, at in (("feGaussianBlur", {"in": "SourceAlpha", "stdDeviation": "1.6"}), ("feOffset", {"dx": "0", "dy": "1", "result": "b"})):
            etree.SubElement(f, Q(tag), at)
        ct = etree.SubElement(f, Q("feComponentTransfer"))
        etree.SubElement(ct, Q("feFuncA"), {"type": "linear", "slope": ".35"})
        mg = etree.SubElement(f, Q("feMerge"))
        etree.SubElement(mg, Q("feMergeNode")); etree.SubElement(mg, Q("feMergeNode"), {"in": "SourceGraphic"})
    xml = etree.tostring(root, encoding="unicode")
    refs = set(re.findall(r"url\(#([^)]+)\)", xml)) | set(re.findall(r'href="#([^"]+)"', xml))
    for e in root.iter():
        if isinstance(e.tag, str) and e.get("id") and e.get("id") not in refs:
            del e.attrib["id"]
    if variant == "mapa":   # las zonas de zoom (mapclip) no hacen falta sin interaccion, pero el recorte es inocuo
        pass
    for e in list(root.findall(Q("title")) + root.findall(Q("desc"))):
        root.remove(e)
    ti = etree.Element(Q("title")); ti.text = "Elecciones presidenciales de Argentina de 1928: " + NAMES[mode][0]
    de = etree.Element(Q("desc")); de.text = ("Mapa por departamento (división de 1914) de las elecciones presidenciales argentinas del 1.º de abril de 1928. "
                                            "Votos: D. Cantón (1968), tomo II. Geometría: G. M. Rodríguez, CEUR-CONICET. Ver la página del archivo en Commons.")
    root.insert(0, ti); root.insert(1, de)
    s = etree.tostring(root, encoding="unicode")
    s = re.sub(r">\s+<", "><", s)
    if variant == "mapa":   # se recorta el lienzo al dibujo
        x, y, w, h = content_bbox(s)
        root.set("viewBox", "%d %d %d %d" % (x, y, w, h)); root.set("width", str(w)); root.set("height", str(h))
        s = re.sub(r">\s+<", "><", etree.tostring(root, encoding="unicode"))
    os.makedirs(os.path.join(HERE, "svg"), exist_ok=True)
    out = os.path.join(HERE, "svg", filename(mode, variant))
    open(out, "w", encoding="utf8").write('<?xml version="1.0" encoding="UTF-8"?>\n' + s)
    print(mode, variant, os.path.getsize(out), "bytes", flush=True)
    return out


if __name__ == "__main__":
    for fn in os.listdir(os.path.join(HERE, "svg")) if os.path.isdir(os.path.join(HERE, "svg")) else []:
        os.remove(os.path.join(HERE, "svg", fn))   # los de la primera version (texto a trazados) ya no valen
    for m in NAMES:
        for v in VARIANTS:
            process(m, v)
