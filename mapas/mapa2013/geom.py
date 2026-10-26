"""Geometria 2010 (Departamentos_2010.shp, con las 15 comunas de Capital Federal) + partido de Lezama (escindido de Chascomus en dic. 2009)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shp import read_shp, read_dbf

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, '..', '../geometria/Base deptos 1869-2022', 'Departamentos_2010')
B2022 = os.path.join(HERE, '..', '../geometria/Base deptos 1869-2022', 'Departamentos_2022_INDEC')
PROV = {'02':'Capital Federal','06':'Buenos Aires','10':'Catamarca','14':'Córdoba','18':'Corrientes','22':'Chaco','26':'Chubut','30':'Entre Ríos','34':'Formosa','38':'Jujuy','42':'La Pampa','46':'La Rioja','50':'Mendoza','54':'Misiones','58':'Neuquén','62':'Río Negro','66':'Salta','70':'San Juan','74':'San Luis','78':'Santa Cruz','82':'Santa Fe','86':'Santiago del Estero','90':'Tucumán','94':'Tierra del Fuego'}
TERR = set()
LAT0 = -38.0
KX = math.cos(math.radians(LAT0))


def to_poly(rings):
    outers, holes = [], []
    for r in rings:
        if len(r) < 4: continue
        a = 0.5 * sum(x0*y1 - x1*y0 for (x0, y0), (x1, y1) in zip(r, r[1:]))
        (outers if a < 0 else holes).append(Polygon(r))
    g = unary_union([p.buffer(0) for p in outers])
    if holes: g = g.difference(unary_union([p.buffer(0) for p in holes]))
    return g


FIX = {('Buenos Aires', 'Berazetegui'): 'Berazategui', ('Buenos Aires', 'Crnel de marina Leonardo Rosales'): 'Coronel de Marina Leonardo Rosales',
       ('Buenos Aires', 'Salliquelo'): 'Salliqueló', ('Chubut', 'Caiman'): 'Gaiman', ('Chubut', 'Castre'): 'Gastre', ('Chubut', 'Rio Senguerr'): 'Río Senguer',
       ('Córdoba', 'lschllin'): 'Ischilín', ('Entre Ríos', 'Vrllaguay'): 'Villaguay', ('Formosa', 'Berme¡o'): 'Bermejo', ('Formosa', 'Ramorr Lista'): 'Ramón Lista',
       ('La Rioja', 'Chileclto'): 'Chilecito', ('Misiones', 'lguazu'): 'Iguazú', ('Salta', 'Rosario de Ja Frontera'): 'Rosario de la Frontera',
       ('San Juan', 'Ullun'): 'Ullum', ('Santiago del Estero', 'Brigadier J. Felipe lbarra'): 'Brigadier J. Felipe Ibarra'}
MALVINAS = shapely.box(-62.0, -53.0, -57.0, -51.0)


def _split_lezama(out):
    """Divide Chascomus (censo 2010) en Chascomús y Lezama (creado en dic. 2009, ley prov. 14.087) recortando al contorno de 2010."""
    idx = [i for i, u in enumerate(out) if u['prov'] == 'Buenos Aires' and u['name'].lower().startswith('chascom')]
    if not idx: return out
    i0 = idx[0]
    R = out[i0]['geom'].buffer(0)
    sh22, db22 = read_shp(B2022 + '.shp'), read_dbf(B2022 + '.dbf')
    pieces = []
    for g, r in zip(sh22, db22):
        if r.get('cde') in ('06218', '06466'):
            disp = 'Chascomús' if r['cde'] == '06218' else 'Lezama'
            pieces.append([disp, to_poly(g).buffer(0).intersection(R), r['cde']])
    rest = R.difference(unary_union([p[1] for p in pieces]))
    for q in (rest.geoms if hasattr(rest, 'geoms') else [rest]):
        if q.is_empty or q.area <= 0: continue
        j = min(range(len(pieces)), key=lambda k: pieces[k][1].distance(q))
        pieces[j][1] = unary_union([pieces[j][1], q])
    res = [u for i, u in enumerate(out) if i != i0]
    for disp, g, link in pieces:
        res.append(dict(prov='Buenos Aires', name=disp, kind='partido', link=[link], geom=g.buffer(0)))
    return res


def load():
    sh, db = read_shp(B + '.shp'), read_dbf(B + '.dbf')
    units = {}
    for g, r in zip(sh, db):
        prov = PROV[r['PROV_COD']]
        nm = r['DEPTO'].strip()
        if prov == 'Tierra del Fuego' and nm == 'Sector Antartico': continue
        nm = FIX.get((prov, nm), nm)
        if prov == 'Capital Federal':
            num = int(nm.split()[-1])
            nm = 'Comuna %d' % num
            kind = 'comuna'
        elif prov == 'Buenos Aires':
            kind = 'partido'
        else:
            kind = 'departamento'
        k = (prov, nm)
        u = units.setdefault(k, dict(prov=prov, name=nm, kind=kind, link=[], geoms=[]))
        gg = to_poly(g)
        if prov == 'Tierra del Fuego' and nm == 'Islas del Atlantico Sur':
            gg = gg.intersection(MALVINAS); nm = 'Islas Malvinas'; u['name'] = nm
        u['link'].append(r['LINK_']); u['geoms'].append(gg)
    out = []
    for u in units.values():
        u['geom'] = unary_union(u['geoms']); del u['geoms']; out.append(u)
    return _split_lezama(out)
