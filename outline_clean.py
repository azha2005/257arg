"""Limpia el contorno del país (class="out") antes de dibujarlo.

El contorno se dibuja con un trazo gris grueso; los anillos diminutos (huecos entre polígonos dentro del país, islotes de la costa,
sobre todo la bahía Samborombón y el Delta) quedan como puntos grises. Se quitan los huecos de menos de `hole_max` y los islotes de
menos de `island_min` (unidades de mapa^2; 1 unidad^2 ~ 7,8 km^2), y los islotes pegados a la costa de menos de 40. Las islas grandes (Tierra del Fuego, Isla de los Estados) se conservan.
"""
from shapely.geometry import Polygon
from shapely.ops import unary_union


def clean_outline(g, hole_max=6.0, island_min=0.6, coast_island_min=40.0, coast_dist=25.0):
    """hole_max: huecos interiores menores a esto se rellenan; island_min: islotes menores a esto se descartan;
    coast_island_min: islotes pegados a la costa (a menos de coast_dist del continente) menores a esto se descartan.
    Los islotes lejos del continente (Malvinas) no se tocan salvo por island_min."""
    polys = [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.geom_type == "Polygon"]
    big = max(polys, key=lambda p: p.area)
    out = []
    for p in polys:
        if p is not big:
            if p.area < island_min:
                continue
            if p.area < coast_island_min and p.distance(big) < coast_dist:
                continue
        out.append(Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area >= hole_max]))
    return unary_union(out)


def clean_holes(g, hole_max=6.0, name=""):
    """Rellena los huecos interiores de menos de `hole_max` de un polígono de provincia (rendijas entre departamentos): si no,
    el trazo blanco de límite provincial los dibuja como puntos blancos (San Luis, Buenos Aires)."""
    polys = [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.geom_type == "Polygon"]
    out = []
    for p in polys:
        for h in p.interiors:
            if Polygon(h).area < hole_max and name:
                print("hueco rellenado en", name, round(Polygon(h).area, 3), file=__import__("sys").stderr)
        out.append(Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area >= hole_max]))
    return unary_union(out)
