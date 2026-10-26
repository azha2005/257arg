"""Geometría de los atlas 1958, 1962 y 1965: Departamentos_1960 + secciones electorales de Capital.

Pedido del usuario: las unidades con datos que el mapa de 1960 no tiene llevan polígono propio, tomado de otro
shapefile y recortado al contorno de 1960 (nunca se fusionan):
  - Berazategui (1960, de Quilmes), Capitán Sarmiento (1961) y Salliqueló (1961): Departamentos_1970, en los años en que
    Cantón los trae aparte (1962 y 1965; Salliqueló solo 1965).
  - Misiones 1958: once departamentos anteriores a la división de 1960, tomados de Departamentos_1947.
"""
import os, sys, math
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'mapa1930'))
import shapely
from shapely.ops import unary_union
from shp import read_shp, read_dbf
from geom import to_poly
from names import norm

B = os.path.join(H, '..', 'Base deptos 1869-2022')
PROV = {'02':'Capital Federal','06':'Buenos Aires','10':'Catamarca','14':'Córdoba','18':'Corrientes','22':'Chaco','26':'Chubut','30':'Entre Ríos','34':'Formosa','38':'Jujuy','42':'La Pampa','46':'La Rioja','50':'Mendoza','54':'Misiones','58':'Neuquén','62':'Río Negro','66':'Salta','70':'San Juan','74':'San Luis','78':'Santa Cruz','82':'Santa Fe','86':'Santiago del Estero','90':'Tucumán','94':'Tierra del Fuego'}
LAT0 = -38.0
KX = math.cos(math.radians(LAT0))
MALVINAS = shapely.box(-62.0, -53.0, -57.0, -51.0)   # del polígono «Sector Antártico e Islas del Atlántico Sur» se conserva solo Malvinas

# (año desde, provincia, nombre en 1970) -> nombre para mostrar
STEAL70 = [(1962, 'Buenos Aires', 'Berazetegui', 'Berazategui'), (1962, 'Buenos Aires', 'Capitan Sarmiento', 'Capitán Sarmiento'),
           (1965, 'Buenos Aires', 'Salliquelo', 'Salliqueló')]
# Misiones 1958: polígono de 1947 -> nombre de Cantón
MIS47 = {'Apóstoles': 'Apóstoles', 'Cainguas': 'Cainguás', 'Candelaria': 'Candelaria', 'Capital': 'Capital', 'Concepción': 'Concepción',
         'Guaraní': 'Guaraní', 'Iguazú': 'Iguazú', 'San Ignacio': 'San Ignacio', 'San javier': 'San Javier', 'San Pedro': 'San Pedro',
         'Frontera': 'General Manuel Belgrano'}
MIS_NOTE = {'General Manuel Belgrano': 'Polígono del departamento Frontera del mapa de 1947 (cabecera en Bernardo de Irigoyen), que en 1958 Cantón llama General Manuel Belgrano; asignación por nombre de cabecera, no verificada.',
            'San Pedro': 'Polígono de San Pedro del mapa de 1947 (hoy, sobre todo, Montecarlo); los límites de 1958 no se pudieron verificar.'}


def _read(f):
    out = {}
    for g, r in zip(read_shp(os.path.join(B, f + '.shp')), read_dbf(os.path.join(B, f + '.dbf'))):
        out.setdefault((PROV[r['PROV_COD']], r['DEPTO'].strip()), []).append((to_poly(g).buffer(0), r['LINK_']))
    return {k: (unary_union([g for g, _ in v]), [l for _, l in v]) for k, v in out.items()}


def _split(units, R_idx, pieces):
    """Reparte la unión de units[R_idx] entre `pieces` [(nombre, geom)] recortadas a esa unión; lo que sobra va a la pieza más cercana."""
    R = unary_union([units[i]['geom'] for i in R_idx]).buffer(0)
    P = [[n, g.intersection(R)] for n, g in pieces]
    rest = R.difference(unary_union([g for _, g in P]))
    for q in (rest.geoms if hasattr(rest, 'geoms') else [rest]):
        if q.is_empty or q.area <= 0: continue
        j = min(range(len(P)), key=lambda k: P[k][1].distance(q))
        P[j][1] = unary_union([P[j][1], q])
    return P


def load(anio):
    S60 = _read('Departamentos_1960_2026v2')
    units = []
    for (prov, nm), (g, link) in S60.items():
        if prov == 'Capital Federal': continue          # distritos escolares: se usan las secciones electorales
        if prov == 'Tierra del Fuego' and nm.startswith('Sector Antartico'):
            g = g.intersection(MALVINAS); nm = 'Islas Malvinas'
        kind = 'partido' if prov == 'Buenos Aires' else 'departamento'
        if prov == 'Tierra del Fuego': kind = 'territorio nacional'
        units.append(dict(prov=prov, name=nm, kind=kind, link=link, geom=g))
    for (prov, nm), (g, link) in _read('Departamentos_1960_secc CF_2026v2').items():
        n = int(nm.split()[-1])
        units.append(dict(prov='Capital Federal', name='Circ. %02d' % n, circ=n, kind='circunscripción', link=link, geom=g))
    # polígonos propios para partidos posteriores a 1960 (shapefile de 1970)
    S70 = None
    for y, prov, n70, disp in STEAL70:
        if anio < y: continue
        S70 = S70 or _read('Departamentos_1970')
        g70 = S70[(prov, n70)][0]
        hit = [i for i, u in enumerate(units) if u['prov'] == prov and u['geom'].intersection(g70).area > 0.02 * g70.area]
        R = unary_union([units[i]['geom'] for i in hit])
        new = g70.intersection(R).buffer(0)
        for i in hit:
            units[i]['geom'] = units[i]['geom'].difference(new).buffer(0)
            units[i].setdefault('cedio', []).append(disp)
        units.append(dict(prov=prov, name=disp, kind='partido', link=S70[(prov, n70)][1], geom=new,
                          nota_geo='Partido creado después del censo de 1960: polígono tomado del mapa de 1970 y recortado al de %s.' %
                                   ' y '.join(units[i]['name'] for i in hit)))
    if anio == 1958:
        mis = [i for i, u in enumerate(units) if u['prov'] == 'Misiones']
        S47 = _read('Departamentos_1947_2026v2')
        P = _split(units, mis, [(MIS47[nm], g) for (prov, nm), (g, _) in S47.items() if prov == 'Misiones' and nm in MIS47])
        units = [u for i, u in enumerate(units) if i not in set(mis)]
        for n, g in P:
            units.append(dict(prov='Misiones', name=n, kind='departamento', link=[], geom=g.buffer(0),
                              nota_geo=MIS_NOTE.get(n, 'Departamento anterior a la división de 1960: polígono del mapa de 1947.')))
    return units


if __name__ == '__main__':
    for y in (1958, 1962, 1965):
        U = load(y)
        print(y, len(U), [(u['name'], round(u['geom'].area, 4)) for u in U if 'nota_geo' in u or 'cedio' in u])
