"""Utilidades del cotejo atlas propio vs mapa por departamento de Wikipedia (Commons, N2051)."""
import re, json, os
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VBW, VBH = 1920, 1649


def parse_d(d):
    """path 'M x y L x y ... Z M ...' -> lista de anillos"""
    rings = []
    for sub in d.split("M")[1:]:
        pts = re.findall(r"(-?[\d.]+)[ ,](-?[\d.]+)", sub)
        if len(pts) >= 3:
            rings.append([(float(x), float(y)) for x, y in pts])
    return rings


def rings_to_geom(rings):
    """even-odd: anillos exteriores y huecos"""
    polys = [Polygon(r).buffer(0) for r in rings]
    polys = [p for p in polys if not p.is_empty]
    polys.sort(key=lambda p: -p.area)
    g = None
    for p in polys:
        g = p if g is None else g.symmetric_difference(p)
    return g


def load_atlas(folder, html, dataset):
    h = open(os.path.join(ROOT, "mapas", folder, html), encoding="utf8").read()
    ds = json.load(open(os.path.join(ROOT, folder, dataset), encoding="utf8"))
    paths = {}
    for m in re.finditer(r'<path class="d" data-i="(\d+)" d="([^"]+)"', h):
        paths[int(m.group(1))] = rings_to_geom(parse_d(m.group(2)))
    return ds, paths


def wiki_mask(img, region):
    """máscara de mainland de la imagen de Wikipedia (alfa>0) dentro de la ventana region=(x0,y0,x1,y1) en px de viewBox"""
    a = np.asarray(img.convert("RGBA"))[:, :, 3] > 200
    k = img.size[0] / VBW
    x0, y0, x1, y1 = [int(v * k) for v in region]
    m = np.zeros_like(a)
    m[y0:y1, x0:x1] = a[y0:y1, x0:x1]
    return m
