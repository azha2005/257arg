"""Las 28 circunscripciones de Capital Federal, extraidas del SVG base de Wikipedia 1999 (CC) y llevadas a lon/lat.

    python caba28.py   ->  caba28.pkl  {numero: (nombre, poligono lon/lat)}

El SVG dibuja cada circunscripcion en un grupo con escala propia; se componen las transformaciones, se aplanan las curvas y se
ajusta una transformacion lineal (cajas envolventes) al contorno de Capital Federal de Departamentos_1980.shp. El ajuste solo
mueve y escala la geometria: es aproximada (el SVG de Wikipedia esta dibujado a mano sobre una base distinta del shapefile).
Numeracion oficial: CIRCUNSCRIPCIONES_CABA_28.md.
"""
import os, re, sys, math, pickle
import xml.etree.ElementTree as ET
import numpy as np, shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "..", ".claude", "skills", "mapa-electoral-wikipedia-1999", "assets", "base_1999_departamentos.svg")
SHP = os.path.join(HERE, "..", "Base deptos 1869-2022", "Departamentos_1980")
sys.path.insert(0, os.path.join(HERE, "..", "mapa1930"))
from shp import read_shp, read_dbf

NUM = {"Vélez Sarsfield": 1, "San Cristóbal Sur": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sur": 6, "San Carlos Norte": 7,
       "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sur": 10, "Balvanera Norte": 11, "Concepción": 12, "Montserrat": 13, "San Nicolás": 14,
       "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18, "Pilar": 19, "Socorro": 20, "San Vicente de Paul": 21, "Villa Lugano": 22,
       "Cristo Obrero": 23, "Versalles": 24, "San Luis Gonzaga": 25, "San José": 26, "Nuestra Señora del Carmen": 27, "Saavedra": 28}
# ids de los trazos del mapa principal (no los del recuadro) tomados de assets/geom_rows.json
IDS = {"Socorro": "path8241", "Pilar": "path8243", "Las Heras": "path8245", "Palermo": "path8249", "Belgrano": "path8336", "Saavedra": "path8338",
       "Nuestra Señora del Carmen": "path8340", "San Bernardo": "path8342", "San José": "path8344", "San Luis Gonzaga": "path8346", "Versalles": "path8348",
       "San Vicente de Paul": "path8350", "Vélez Sarsfield": "path8352", "Villa Lugano": "path8354", "Cristo Obrero": "path8356", "San Cristóbal Sur": "path8358",
       "Santa Lucía": "path8360", "San Juan Evangelista": "path8362", "San Cristóbal Norte": "path8364", "Flores": "path8370", "San Carlos Sur": "path8368",
       "San Carlos Norte": "path8372", "Balvanera Oeste": "path8374", "Balvanera Norte": "path8376", "Balvanera Sur": "path8378", "Concepción": "path8384",
       "Montserrat": "path8382", "San Nicolás": "path8380"}


def mat(tr):
    """transform SVG -> matriz afin 3x3"""
    M = np.eye(3)
    if not tr: return M
    for name, args in re.findall(r"(matrix|translate|scale|rotate)\(([^)]*)\)", tr):
        a = [float(x) for x in re.split(r"[ ,]+", args.strip()) if x]
        if name == "matrix": T = np.array([[a[0], a[2], a[4]], [a[1], a[3], a[5]], [0, 0, 1]])
        elif name == "translate": T = np.array([[1, 0, a[0]], [0, 1, a[1] if len(a) > 1 else 0], [0, 0, 1]])
        elif name == "scale": T = np.array([[a[0], 0, 0], [0, a[1] if len(a) > 1 else a[0], 0], [0, 0, 1]])
        else: raise ValueError("rotate no soportado")
        M = M @ T
    return M


def flatten(d, n=8):
    """d de un path SVG -> lista de anillos (listas de (x,y)); soporta M L H V C S Q Z, absolutos y relativos"""
    toks = re.findall(r"[MmLlHhVvCcSsQqZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
    i, cmd, x, y, sx, sy, rings, cur, last_c = 0, None, 0.0, 0.0, 0.0, 0.0, [], None, None

    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]): cmd = toks[i]; i += 1
        if cmd in "Zz":
            if cur: rings.append(cur); cur = None
            x, y = sx, sy; last_c = None; continue
        rel = cmd.islower(); C = cmd.upper()
        if C == "M":
            if cur: rings.append(cur)
            nx, ny = num(), num()
            x, y = (x + nx, y + ny) if rel else (nx, ny); sx, sy = x, y; cur = [(x, y)]; cmd = "l" if rel else "L"; last_c = None
        elif C == "L":
            nx, ny = num(), num(); x, y = (x + nx, y + ny) if rel else (nx, ny); cur.append((x, y)); last_c = None
        elif C == "H":
            nx = num(); x = x + nx if rel else nx; cur.append((x, y)); last_c = None
        elif C == "V":
            ny = num(); y = y + ny if rel else ny; cur.append((x, y)); last_c = None
        elif C in "CS":
            if C == "C":
                x1, y1, x2, y2, x3, y3 = [num() for _ in range(6)]
                if rel: x1, y1, x2, y2, x3, y3 = x + x1, y + y1, x + x2, y + y2, x + x3, y + y3
            else:
                x2, y2, x3, y3 = [num() for _ in range(4)]
                if rel: x2, y2, x3, y3 = x + x2, y + y2, x + x3, y + y3
                x1, y1 = (2 * x - last_c[0], 2 * y - last_c[1]) if last_c else (x, y)
            for t in np.linspace(0, 1, n + 1)[1:]:
                u = 1 - t
                cur.append((u**3 * x + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3, u**3 * y + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3))
            last_c = (x2, y2); x, y = x3, y3
        elif C == "Q":
            x1, y1, x2, y2 = [num() for _ in range(4)]
            if rel: x1, y1, x2, y2 = x + x1, y + y1, x + x2, y + y2
            for t in np.linspace(0, 1, n + 1)[1:]:
                u = 1 - t; cur.append((u * u * x + 2 * u * t * x1 + t * t * x2, u * u * y + 2 * u * t * y1 + t * t * y2))
            x, y = x2, y2; last_c = None
    if cur: rings.append(cur)
    return rings


def ajustar_al_contorno(out, contorno, paso=0.0003):
    """El SVG esta dibujado a mano y su ajuste es aproximado: las circunscripciones dejan rendijas entre si y a veces se pasan sobre la provincia de Buenos
    Aires o el rio. Se recortan contra el contorno de Capital del shapefile de 1980 (limite exacto con la provincia) y la superficie del contorno que
    queda sin cubrir se reparte entre las vecinas por dilatacion gradual, asi la union de las 28 es el contorno real y no queda ninguna rendija."""
    polys = {n: g.intersection(contorno) for n, (nm, g) in out.items()}
    resto = contorno.difference(unary_union(list(polys.values())))
    k = 0
    while resto.area > 1e-10 and k < 400:
        k += 1
        for n in sorted(polys):
            add = polys[n].buffer(paso).intersection(resto)
            if add.area > 0:
                polys[n] = unary_union([polys[n], add]).buffer(0)
                resto = resto.difference(add)
    # lo que no alcanzo la dilatacion (rincones aislados) va a la circunscripcion mas cercana
    for p in (resto.geoms if hasattr(resto, "geoms") else [resto]):
        if p.area > 1e-10:
            n = min(polys, key=lambda m: polys[m].distance(p))
            polys[n] = unary_union([polys[n], p]).buffer(0)
    print("dilatacion en", k, "pasos; area sin repartir", round(resto.area, 8), file=sys.stderr)
    for n in polys:   # astillas sueltas (menos de 10e-6 grados2; la menor circunscripcion real tiene 135e-6)
        partes = [p for p in (polys[n].geoms if hasattr(polys[n], "geoms") else [polys[n]]) if p.geom_type == "Polygon" and p.area >= 10e-6]
        # sin huecos interiores (son costuras numericas de la union) y con anillos validos
        g = unary_union([Polygon(p.exterior).buffer(0) for p in partes])
        polys[n] = shapely.set_precision(g, 1e-7)   # sin vertices repetidos ni anillos degenerados (coverage_simplify los rechaza)
    return {n: (out[n][0], polys[n]) for n in out}


def main():
    raw = open(SVG, "rb").read().decode("utf8", "replace").encode("utf8")
    root = ET.fromstring(raw)
    parent = {c: p for p in root.iter() for c in p}
    byid = {e.get("id"): e for e in root.iter() if e.get("id")}
    polys = {}
    for nm, pid in IDS.items():
        el = byid[pid]
        M = mat(el.get("transform"))
        p = parent.get(el)
        while p is not None:
            M = mat(p.get("transform")) @ M; p = parent.get(p)
        rings = flatten(el.get("d"))
        geoms = []
        for r in rings:
            a = np.array([(M @ np.array([x, y, 1.0]))[:2] for x, y in r])
            if len(a) >= 4: geoms.append(Polygon(a).buffer(0))
        polys[nm] = unary_union(geoms)
    # ajuste a lon/lat con el contorno de Capital Federal del shapefile de 1980
    sh, db = read_shp(SHP + ".shp"), read_dbf(SHP + ".dbf")
    pts = np.array([pt for g, r in zip(sh, db) if r["PROV_COD"] == "02" for ring in g for pt in ring])
    lx0, ly0, lx1, ly1 = pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()
    ux = unary_union(list(polys.values()))
    sx0, sy0, sx1, sy1 = ux.bounds
    ax, ay = (lx1 - lx0) / (sx1 - sx0), (ly1 - ly0) / (sy1 - sy0)
    print("bbox svg", ux.bounds, "bbox lon/lat", (lx0, ly0, lx1, ly1), "escala x/y", ax, ay, "razon", ax / ay, file=sys.stderr)

    def f(a):
        a = np.asarray(a, float).copy()
        a[:, 0] = lx0 + (a[:, 0] - sx0) * ax
        a[:, 1] = ly1 - (a[:, 1] - sy0) * ay      # el SVG tiene el eje y hacia abajo
        return a
    out = {}
    for nm, g in polys.items():
        out[NUM[nm]] = (nm, shapely.transform(g, f))
    # el ajuste por cajas envolventes sobrestima el ancho (el SVG incluye la costanera): se afina con una escala, un giro y un desplazamiento que
    # maximizan la superficie en comun con el contorno del shapefile (IoU 0,869 -> 0,941; parametros de Nelder-Mead sobre el conjunto de las 28)
    from shapely import affinity
    O = shapely.transform(ux, f).centroid
    for n, (nm, g) in list(out.items()):
        g = affinity.scale(g, 0.914856, 1.007929, origin=O)
        g = affinity.rotate(g, -0.016724, origin=O)
        out[n] = (nm, affinity.translate(g, -0.0075513, 0.00057722))
    # fragmentos sueltos del dibujo (astillas de area casi nula, algunas en la esquina sudeste): se descartan; la menor circunscripcion real tiene 135e-6 grados2
    for n, (nm, g) in list(out.items()):
        partes = [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.area >= 10e-6]
        out[n] = (nm, unary_union(partes))
    import geom
    contorno = unary_union([geom.to_poly(g) for g, r in zip(sh, db) if r["PROV_COD"] == "02"]).buffer(2e-5).buffer(-2e-5)
    out = ajustar_al_contorno(out, contorno)
    pickle.dump(out, open(os.path.join(HERE, "caba28.pkl"), "wb"))
    tot = unary_union([g for _, g in out.values()])
    print("circunscripciones", len(out), "area total (grados2)", round(tot.area, 6), "bounds", [round(v, 4) for v in tot.bounds], file=sys.stderr)


if __name__ == "__main__":
    main()
