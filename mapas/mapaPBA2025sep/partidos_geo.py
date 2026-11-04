"""Poligonos de los 135 partidos bonaerenses de Departamentos_2022_INDEC (WGS84), con la clave de nombre de la base.
La union de los circuitos de la capa 2021 deja huecos y rendijas entre partidos; para los niveles Partido y Seccion se usa esta capa."""
import os, re, unicodedata
import shapefile
from shapely.geometry import shape

SHP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "geometria", "Base deptos 1869-2022", "Departamentos_2022_INDEC")
ALIAS = {"coroneldemarinalrosales": "coroneldemarinaleonardorosales", "nuevedejulio": "9dejulio", "veinticincodemayo": "25demayo"}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def load(partidos):
    r = shapefile.Reader(SHP, encoding="latin1")
    G = {norm(rec["nam"]): shape(sh.__geo_interface__) for sh, rec in zip(r.shapes(), r.records()) if rec["cpr"] == "06"}
    out = {}
    for p in partidos:
        k = norm(p); k = ALIAS.get(k, k)
        assert k in G, ("partido sin poligono INDEC", p)
        out[p] = G[k]
    return out
