"""Geometria 1980 (Departamentos_1980.shp) + 28 circunscripciones de Capital (caba28.pkl) -> unidades proyectables."""
import sys, re, math, pickle, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shp import read_shp, read_dbf

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, '..', 'Base deptos 1869-2022', 'Departamentos_1980')
PROV = {'02':'Capital Federal','06':'Buenos Aires','10':'Catamarca','14':'Córdoba','18':'Corrientes','22':'Chaco','26':'Chubut','30':'Entre Ríos','34':'Formosa','38':'Jujuy','42':'La Pampa','46':'La Rioja','50':'Mendoza','54':'Misiones','58':'Neuquén','62':'Río Negro','66':'Salta','70':'San Juan','74':'San Luis','78':'Santa Cruz','82':'Santa Fe','86':'Santiago del Estero','90':'Tucumán','94':'Tierra del Fuego'}
TERR = set()          # en 1983 las 24 jurisdicciones votan
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


# errores de tipeo de los nombres del shapefile de 1980 (letras mal leidas del original)
FIX = {('Buenos Aires', 'Berazetegui'): 'Berazategui', ('Buenos Aires', 'Crnel de marina Leonardo Rosales'): 'Coronel de Marina Leonardo Rosales',
       ('Buenos Aires', 'Salliquelo'): 'Salliqueló', ('Chubut', 'Caiman'): 'Gaiman', ('Chubut', 'Castre'): 'Gastre', ('Chubut', 'Rio Senguerr'): 'Río Senguer',
       ('Córdoba', 'lschllin'): 'Ischilín', ('Entre Ríos', 'Vrllaguay'): 'Villaguay', ('Formosa', 'Berme¡o'): 'Bermejo', ('Formosa', 'Ramorr Lista'): 'Ramón Lista',
       ('La Rioja', 'Chileclto'): 'Chilecito', ('Misiones', 'lguazu'): 'Iguazú', ('Salta', 'Rosario de Ja Frontera'): 'Rosario de la Frontera',
       ('San Juan', 'Ullun'): 'Ullum', ('Santiago del Estero', 'Brigadier J. Felipe lbarra'): 'Brigadier J. Felipe Ibarra'}
MALVINAS = shapely.box(-62.0, -53.0, -57.0, -51.0)   # el poligono de 1980 «Islas del Atlantico Sur» incluye Georgias y Sandwich; se conserva solo Malvinas


def load():
    sh, db = read_shp(B + '.shp'), read_dbf(B + '.dbf')
    units = {}
    for g, r in zip(sh, db):
        if r['PROV_COD'] == '02': continue                     # Capital: se reemplaza por las 28 circunscripciones
        prov = PROV[r['PROV_COD']]
        nm = r['DEPTO'].strip()
        if prov == 'Tierra del Fuego' and nm == 'Sector Antartico': continue   # la Antartida no se dibuja (igual que en los otros atlas)
        nm = FIX.get((prov, nm), nm)
        kind = 'partido' if prov == 'Buenos Aires' else 'departamento'
        k = (prov, nm)
        u = units.setdefault(k, dict(prov=prov, name=nm, kind=kind, link=[], geoms=[]))
        gg = to_poly(g)
        if prov == 'Tierra del Fuego' and nm == 'Islas del Atlantico Sur':
            gg = gg.intersection(MALVINAS); nm = 'Islas Malvinas'; u['name'] = nm
        u['link'].append(r['LINK_']); u['geoms'].append(gg)
    out = []
    for u in units.values():
        u['geom'] = unary_union(u['geoms']); del u['geoms']; out.append(u)
    for n, (nm, g) in pickle.load(open(os.path.join(HERE, 'caba28.pkl'), 'rb')).items():
        out.append(dict(prov='Capital Federal', name='Circ. %02d' % n, kind='circunscripción', link=['CF%02d' % n], geom=g, parroquia=nm))
    return out
