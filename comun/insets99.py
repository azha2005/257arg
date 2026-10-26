"""Los recuadros del atlas Wikipedia 1999 para los atlas sobre departamentos de 1980 (1983, 1985).

Wikipedia 1999 trae siete: Tucumán, Gran San Juan, Gran Mendoza, Resistencia + Corrientes capital, Área Metropolitana, Antártida y Ciudad de Buenos Aires.
Los marcos (`f`) son los de la plantilla; las ventanas (`win`) se calculan sobre nuestras unidades.

    import insets99
    extra = insets99.build(U, G_raw, window, bbox_of)    # -> dict(sj=, mza=, res=, ant=, ant_body="<path .../>", marks=[...])
"""
import os, sys, math
import shapely
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../mapas/mapa1930"))
sys.path.insert(0, os.path.join(HERE, "../mapas/mapa1983"))
from shp import read_shp, read_dbf
import importlib.util as _iu
_sp = _iu.spec_from_file_location('geom1980', os.path.join(HERE, '../mapas/mapa1983', 'geom.py')); geom = _iu.module_from_spec(_sp); _sp.loader.exec_module(geom)   # las utilidades de geom 1980 (to_poly, MALVINAS), aunque el atlas traiga su propio geom
from names import norm

SHP = os.path.join(HERE, "../geometria/Base deptos 1869-2022", "Departamentos_1980")
# centro del dibujo de la Antártida, fuera de la página (en la plantilla el recuadro es lo único que lo muestra)
AX, AY, K = 1500.0, 2500.0, 15.0


def _f2(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


def _d(g):
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type != "Polygon":
            continue
        for ring in [p.exterior] + list(p.interiors):
            pts = list(ring.coords)[:-1]
            out.append("M" + "L".join("%s %s" % (_f2(x), _f2(y)) for x, y in pts) + "Z")
    return "".join(out)


def _polar(lon, lat, lon0=-50.0):
    """polar austral: el polo abajo, el meridiano lon0 hacia arriba; K px por grado de colatitud"""
    r = (90.0 + lat) * K
    a = math.radians(lon - lon0)
    return AX + r * math.sin(a), AY - r * math.cos(a)


def _antarctic(style95=False):
    sh, db = read_shp(SHP + ".shp"), read_dbf(SHP + ".dbf")
    ant = isl = None
    for g, r in zip(sh, db):
        if r["PROV_COD"] != "94":
            continue
        if r["DEPTO"].strip() == "Sector Antartico":
            ant = geom.to_poly(g)
        elif r["DEPTO"].strip() == "Islas del Atlantico Sur":
            isl = geom.to_poly(g)
    isl = isl.difference(geom.MALVINAS)            # Georgias y Sandwich del Sur (las Malvinas ya estan en el mapa principal)

    def pr(g):
        # se densifica antes de proyectar: los lados rectos del sector son meridianos y paralelos, que en polar son curvos
        g = shapely.segmentize(g, 0.25)
        return shapely.transform(g, lambda a: __import__("numpy").array([_polar(x, y) for x, y in a]))
    if not style95:
        return pr(ant).simplify(0.15), pr(isl).simplify(0.15)
    # estilo del mapa de 1995: el sector es solo el marco (meridianos 74 O y 25 O, desde el arco de 60 S hasta el polo) y se colorea la tierra;
    # costa de Natural Earth 1:50m (dominio publico). Georgias y Sandwich del Sur (al norte del arco) van en gris.
    import json
    from shapely.geometry import shape, Polygon, box
    lons = [-74 + 49 * i / 98 for i in range(99)]
    wedge = Polygon([(x, -60.0) for x in lons] + [(-25.0, -90.0), (-74.0, -90.0)])
    land_all = shape(json.load(open(os.path.join(HERE, "../geometria/insets_data", "antartida_ne50m.geojson"), encoding="utf8"))["geometry"])
    land = land_all.intersection(wedge)
    isl = land_all.intersection(box(-42, -60, -24, -52))
    return pr(wedge).simplify(0.15), pr(isl).simplify(0.05), pr(land).simplify(0.05)


def _build(U, G_raw, window, bbox_of, style95=False, sj_names=None, chaco_names=None, antarctic=True):
    idx = lambda prov, names: [i for i, u in enumerate(U) if u["prov"] == prov and norm(u["name"]) in {norm(n) for n in names}]   # por nombre normalizado: los mapas de 1980 y 1991 escriben distinto
    sj = idx("San Juan", sj_names or {"Capital", "Santa Lucia", "Chimbas", "Rivadavia", "Rawson", "Pocito", "Zonda", "Albardon"})
    mza = idx("Mendoza", {"Capital", "Godoy Cruz", "Guaymallen", "Las Heras", "Lujan de Cuyo", "Maipu"})
    res = idx("Chaco", chaco_names or {"San Fernando"}) + idx("Corrientes", {"Capital"})
    assert (sj_names or len(sj) == 8) and len(mza) == 6 and len(res) == 2, (len(sj), len(mza), len(res))
    land = None
    win_sj, win_mza, win_res = window(bbox_of(sj), 321 / 159, 0.10), window(bbox_of(mza), 224 / 187, 0.10), window(bbox_of(res), 464 / 209, 0.55)
    if not antarctic:   # antes de 1946 la Argentina no tenia sector antartico reclamado ni voto alli: sin recuadro
        return dict(
            sj=dict(id="sj", label="Gran San Juan", f=[328, 545, 321, 159], win=win_sj, show=["d", "pb"], sd=2.6, sp=3.2),
            mza=dict(id="mza", label="Gran Mendoza", f=[328, 783, 224, 187], win=win_mza, show=["d", "pb"], sd=2.6, sp=3.2),
            res=dict(id="res", label="Resistencia + Corrientes capital", f=[1413, 499, 464, 209], win=win_res, show=["d", "pb"], sd=2.6, sp=3.2),
            ant=None, ant_body="", marks=[("sj", win_sj), ("mza", win_mza), ("res", win_res)])
    if style95:
        ant, isl, land = _antarctic(True)
    else:
        ant, isl = _antarctic()
    ab = shapely.total_bounds([ant, isl])
    aspect = 330 / 452
    x0, y0, x1, y1 = ab
    ww, hh = (x1 - x0) * 1.06, (y1 - y0) * 1.06
    if ww / hh < aspect: ww = hh * aspect
    else: hh = ww / aspect
    awin = [round((x0 + x1) / 2 - ww / 2, 2), round((y0 + y1) / 2 - hh / 2, 2), round(ww, 2), round(hh, 2)]
    outline = "".join("M" + "L".join("%s %s" % (_f2(x), _f2(y)) for x, y in list(p.exterior.coords)[:-1]) + "Z" for p in (ant.geoms if hasattr(ant, "geoms") else [ant]))
    body = ('<path class="ant" d="%s"/><path class="antg" d="%s"/><path class="antf" d="%s"/>' % (_d(land if style95 else ant), _d(isl), outline))
    win_sj, win_mza, win_res = window(bbox_of(sj), 321 / 159, 0.10), window(bbox_of(mza), 224 / 187, 0.10), window(bbox_of(res), 464 / 209, 0.55)
    return dict(
        sj=dict(id="sj", label="Gran San Juan", f=[328, 545, 321, 159], win=win_sj, show=["d", "pb"], sd=2.6, sp=3.2),
        mza=dict(id="mza", label="Gran Mendoza", f=[328, 783, 224, 187], win=win_mza, show=["d", "pb"], sd=2.6, sp=3.2),
        res=dict(id="res", label="Resistencia + Corrientes capital", f=[1413, 499, 464, 209], win=win_res, show=["d", "pb"], sd=2.6, sp=3.2),
        ant=dict(id="ant", label="Antártida Argentina", f=[1247, 1166, 330, 452], win=awin, show=["ant", "antg", "antf"], sf=3, fit="meet", noframe=not style95),
        ant_body=body, marks=[("sj", win_sj), ("mza", win_mza), ("res", win_res)])


def build(U, G_raw, window, bbox_of, style95=False, sj_names=None, chaco_names=None, antarctic=True, omit=()):
    """omit: ids de recuadros que no se dibujan ("sj", "mza", "res"); p. ej. cuando la provincia se pinta de un solo color por falta de datos departamentales."""
    d = _build(U, G_raw, window, bbox_of, style95=style95, sj_names=sj_names, chaco_names=chaco_names, antarctic=antarctic)
    for k in omit:
        d[k] = None
    d["marks"] = [m for m in d["marks"] if m[0] not in omit]
    return d
