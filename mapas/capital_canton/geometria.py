"""Trazos SVG de las geometrías de Capital que usa el visor del CD de Cantón.

Correr con el Python del venv de Mosaic (geopandas):
  "C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/capital_canton/geometria.py

- g20: las 20 circunscripciones históricas (Departamentos_1914.shp, «Circ. 01»-«Circ. 20»;
       idénticas en los shp de 1947 y 1960), 1904-1970 salvo 1951.
- g51: las 28 circunscripciones de la ley 14.032 del atlas 1951 (mapas/mapa1951/shp).
- g54: 14 recintos aproximados con numeración provisional adoptada por el usuario.
- g28: las 28 circunscripciones de caba28.pkl (las de los atlas 1983 en adelante), 1973-2007.
Salida: mapas/capital_canton/geometria.json
"""
import json, math, os, pickle, sys
import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import polylabel, unary_union

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(R, "geometria", "Base deptos 1869-2022")

g20 = gpd.read_file(os.path.join(B, "Departamentos_1914.shp"))
g20 = {int(r.DEPTO.split()[-1]): r.geometry for r in g20[g20.PROV_COD == "02"].itertuples()}
g51 = gpd.read_file(os.path.join(R, "mapas", "mapa1951", "shp", "circunscripciones_1951.shp"))
g51 = {int(r.circ): r.geometry for r in g51[g51.provincia.str.contains("Capital")].itertuples()}
c28 = pickle.load(open(os.path.join(R, "mapas", "mapa1983", "caba28.pkl"), "rb"))
n28 = {int(k): v[0] for k, v in c28.items()}
g28 = {int(k): v[1] for k, v in c28.items()}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capital1954
g54 = {u['circ']: u['geom'] for u in capital1954.geometria([])}

todo = unary_union(list(g20.values()) + list(g28.values()) + list(g51.values()))
x0, y0, x1, y1 = todo.bounds
lat0 = (y0 + y1) / 2
k = math.cos(math.radians(lat0))
W = 760
esc = W / ((x1 - x0) * k)
H = (y1 - y0) * esc


def pt(x, y):
    return f"{(x - x0) * k * esc:.1f},{(y1 - y) * esc:.1f}"


def path(g, proyectado=False):
    if not proyectado:
        g = g.simplify(0.00012, preserve_topology=True)
    formato = (lambda x, y: f"{x:.2f},{y:.2f}") if proyectado else pt
    polys = list(g.geoms) if isinstance(g, MultiPolygon) else [g]
    out = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            if len(cs) < 4:
                continue
            out.append("M" + "L".join(formato(*c) for c in cs) + "Z")
    return "".join(out)


def centro(g):
    c = g.representative_point()
    return [round((c.x - x0) * k * esc, 1), round((y1 - c.y) * esc, 1)]


res = {"W": W, "H": round(H, 1)}
for nom, d in (("g20", g20), ("g51", g51), ("g28", g28), ("g54", g54)):
    res[nom] = {str(i): {"d": path(g), "c": centro(g)} for i, g in sorted(d.items())}
    res[nom + "_contorno"] = path(unary_union(list(d.values())).buffer(0.00003))
res["nombres28"] = n28

# Secciones policiales para el contorno anterior a la anexión y la capa de consulta.
municipios = {}
for anio in (1869, 1895):
    g = gpd.read_file(os.path.join(B, f"Departamentos_{anio}.shp"))
    g = g[(g.PROV_COD.astype(str) == "02") & g.DEPTO.str.startswith("SECCION")]
    municipios[anio] = unary_union(list(g.geometry))
    res[f"s{anio}"] = {r.DEPTO.split()[-1]: {"d": path(r.geometry), "c": centro(r.geometry)}
                       for r in g.itertuples()}

import parroquias1896


def proyectar(x, y):
    return (np.asarray(x) - x0) * k * esc, (y1 - np.asarray(y)) * esc


secciones1895 = {r.DEPTO.split()[-1]: r.geometry for r in g.itertuples()}
parroquias, control1896, contorno1896 = parroquias1896.reconstruir(secciones1895, proyectar)
etapas = parroquias1896.variantes(parroquias, contorno1896, municipios[1869], secciones1895, proyectar)
bases = parroquias1896.contornos_base(municipios[1869], list(secciones1895.values()), proyectar)
trazos = {}
for clave, (caras, limite) in etapas.items():
    trazos[clave] = (caras, limite)
    # Trazo «base»: recortado al contorno de la base de Rodríguez y De Grande.
    trazos[clave + "b"] = (parroquias1896.ajustar_a_base(caras, bases[clave]), bases[clave])
for clave, (caras, limite) in trazos.items():
    res[clave] = {}
    for u, p in caras.items():
        etiqueta = polylabel(max(getattr(p, "geoms", [p]), key=lambda q: q.area), tolerance=2)
        res[clave][u] = {"d": path(p, proyectado=True), "c": [round(etiqueta.x, 1), round(etiqueta.y, 1)]}
    res[f"{clave}_contorno"] = path(limite, proyectado=True)
    # Misma vista para los dos trazos, así el botón no mueve el mapa.
    raiz = clave.rstrip("b")
    izq, arriba, der, abajo = unary_union([trazos[raiz][1], trazos[raiz + "b"][1]]).bounds
    res[f"{clave}_vista"] = [math.floor(izq) - 12, math.floor(arriba) - 12,
                            math.ceil(der - izq) + 26, math.ceil(abajo - arriba) + 26]
res["control1896"] = control1896
json.dump(res, open(os.path.join(os.path.dirname(__file__), "geometria.json"), "w", encoding="utf-8"),
          ensure_ascii=False)
print({k: len(v) for k, v in res.items() if isinstance(v, dict)}, "W", W, "H", round(H))
