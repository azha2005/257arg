"""Geometría de los atlas 1946, 1948, 1954 y 1973.

  1946 y 1948 : Departamentos_1947 (territorios nacionales incluidos, aunque no votaban).
  1954        : Departamentos_1960 (el Chaco ya con los 24 departamentos de 1953) y Misiones con los departamentos de 1947,
                como el atlas de 1958 (canton5865/geom60.py).
  Buenos Aires: en 1946, 1948 y 1954, el shapefile de 1955 aportado por el usuario (geometria/shapefile1955/): son los 112
                partidos de 1947 con los códigos de La Plata y Tigre corregidos y el límite Tigre-San Fernando retocado.
  Capital     : secciones electorales (circunscripciones 1 a 20) del shapefile de 1960, como 1958-1965.
  1973        : Departamentos_1970 y las 28 circunscripciones de Capital de los atlas de 1983 (mapas/mapa1983/caba28.pkl).
"""
import os, sys, pickle
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'canton5865'))
sys.path.insert(0, os.path.join(H, '..', '..', 'mapas', 'mapa1930'))
import shapely
from shapely.ops import unary_union
import geom60
from geom60 import _read, PROV, MALVINAS, KX
from shp import read_shp, read_dbf
from geom import to_poly

ROOT = os.path.join(H, '..', '..')
PBA55 = os.path.join(ROOT, 'geometria', 'shapefile1955', 'shapefile1955_corregido', '1955pba')


def _pba55():
    """partido -> geometría; los nombres del dbf de 1955 vienen en latin-1 (se releen así)."""
    import struct
    f = open(PBA55 + '.dbf', 'rb').read()
    n = struct.unpack('<I', f[4:8])[0]; hl = struct.unpack('<H', f[8:10])[0]; rl = struct.unpack('<H', f[10:12])[0]
    fields, o = [], 32
    while f[o] != 0x0D:
        fields.append((f[o:o + 11].split(b'\0')[0].decode(), f[o + 16])); o += 32
    rows = []
    for i in range(n):
        r, p, d = f[hl + i * rl + 1: hl + (i + 1) * rl], 0, {}
        for nm, l in fields:
            d[nm] = r[p:p + l].decode('latin1').strip(); p += l
        rows.append(d)
    out = {}
    for g, r in zip(read_shp(PBA55 + '.shp'), rows):
        out.setdefault(r['DEPTO'].replace('  ', ' '), []).append(to_poly(g).buffer(0))
    return {k: unary_union(v) for k, v in out.items()}


def _kind(prov):
    return 'partido' if prov == 'Buenos Aires' else ('territorio nacional' if prov == 'Tierra del Fuego' else 'departamento')


def _capital_1960(units):
    for (prov, nm), (g, link) in _read('Departamentos_1960_secc CF_2026v2').items():
        n = int(nm.split()[-1])
        units.append(dict(prov='Capital Federal', name='Circ. %02d' % n, circ=n, kind='circunscripción', link=link, geom=g))


def load(key):
    year = int(key[:4])
    units = []
    if year == 1973:
        S70 = _read('Departamentos_1970')
        for (prov, nm), (g, link) in S70.items():
            if prov == 'Capital Federal': continue
            if prov == 'Tierra del Fuego' and nm.startswith('Sector Antartico'):
                g = g.intersection(MALVINAS); nm = 'Islas Malvinas'
            units.append(dict(prov=prov, name=nm, kind=_kind(prov), link=link, geom=g))
        for n, (nm, g) in pickle.load(open(os.path.join(ROOT, 'mapas', 'mapa1983', 'caba28.pkl'), 'rb')).items():
            units.append(dict(prov='Capital Federal', name='Circ. %02d' % n, circ=n, kind='circunscripción', link=[], geom=g))
        return units
    if year == 1954:
        units = [u for u in geom60.load(1958) if u['prov'] != 'Buenos Aires']
    else:
        for (prov, nm), (g, link) in _read('Departamentos_1947_2026v2').items():
            if prov in ('Capital Federal', 'Buenos Aires'): continue
            if prov == 'Tierra del Fuego' and nm.startswith('Sector Antartico'):
                g = g.intersection(MALVINAS); nm = 'Islas Malvinas'
            units.append(dict(prov=prov, name=nm, kind=_kind(prov), link=link, geom=g))
        _capital_1960(units)
    for nm, g in _pba55().items():
        units.append(dict(prov='Buenos Aires', name=nm, kind='partido', link=[], geom=g))
    return units


if __name__ == '__main__':
    for k in ('1946', '1954', '1973'):
        U = load(k)
        from collections import Counter
        print(k, len(U), dict(Counter(u['prov'] for u in U)))
    print(sorted(_pba55())[:120])
