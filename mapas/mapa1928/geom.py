"""Geometria 1914 -> unidades proyectadas, simplificadas, con topologia coherente."""
import sys, re, math, pickle
sys.path.insert(0, '.')
import shapely
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shp import read_shp, read_dbf
import os
from names import norm

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'geometria', 'Base deptos 1869-2022', 'Departamentos_1914')
PROV = {'02':'Capital Federal','06':'Buenos Aires','10':'Catamarca','14':'Córdoba','18':'Corrientes','22':'Chaco','26':'Chubut','30':'Entre Ríos','34':'Formosa','38':'Jujuy','42':'La Pampa','46':'La Rioja','50':'Mendoza','54':'Misiones','58':'Neuquén','62':'Río Negro','66':'Salta','70':'San Juan','74':'San Luis','78':'Santa Cruz','82':'Santa Fe','86':'Santiago del Estero','90':'Tucumán','94':'Tierra del Fuego'}
TERR = {'Chaco','Chubut','Formosa','La Pampa','Misiones','Neuquén','Río Negro','Santa Cruz','Tierra del Fuego'}
LAT0 = -38.0
KX = math.cos(math.radians(LAT0))

def to_poly(rings):
    outers, holes = [], []
    for r in rings:
        if len(r) < 4: continue
        a = 0.5 * sum(x0*y1 - x1*y0 for (x0, y0), (x1, y1) in zip(r, r[1:]))
        (outers if a < 0 else holes).append(Polygon(r))   # shapefile: exterior en sentido horario
    g = unary_union([p.buffer(0) for p in outers])
    if holes: g = g.difference(unary_union([p.buffer(0) for p in holes]))
    return g

def load():
    sh, db = read_shp(B + '.shp'), read_dbf(B + '.dbf')
    units = {}
    for g, r in zip(sh, db):
        prov = PROV[r['PROV_COD']]
        nm = r['DEPTO'].strip()
        if prov == 'Tucumán': nm = re.sub(r'\s+(I|II)$', '', nm)
        if prov == 'Capital Federal': kind = 'circunscripción'
        elif prov in TERR: kind = 'territorio nacional (sección)'
        elif prov == 'Buenos Aires': kind = 'partido'
        else: kind = 'departamento'
        k = (prov, nm)
        u = units.setdefault(k, dict(prov=prov, name=nm, kind=kind, link=[], geoms=[]))
        u['link'].append(r['LINK_']); u['geoms'].append(to_poly(g))
    out = []
    for u in units.values():
        u['geom'] = unary_union(u['geoms']); del u['geoms']; out.append(u)
    return out
