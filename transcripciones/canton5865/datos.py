"""Datos por unidad listos para el atlas: Cantón corregido, partidos con su fila de Wikipedia y su bloque."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import OrderedDict, defaultdict
from cargar import load
from sospechas import kinds
import correcciones, wikiprov, mapeo

CARGO = {1958: 'P', 1962: 'D', 1965: 'D'}
NO_GEO = {'Observados Adjudicados', 'Capital Federal y Tierra del Fuego'}
_W = {1962: ('w1962.txt', '== Resultados por provincia'), 1965: ('w1965.txt', '== Resultados por distrito')}

def cargar_todo():
    T, _ = load(); log = []
    correcciones.aplicar(T, log); correcciones.imputar(T, log)
    return T, log

def unidades(T, anio):
    W = wikiprov.parse(*_W[anio]) if anio in _W else {}
    out = OrderedDict()
    for (a, c, p, cat), t in T.items():
        if (a, c, cat) != (anio, CARGO[anio], 'T'): continue
        ins, vot, rest = kinds(t['cols'])
        for u, r in t['rows'].items():
            if u in NO_GEO: continue
            d = dict(ins=r.get(ins) if ins else None, vot=r.get(vot) if vot else None, bla=0, nul=0,
                     parties=[], bloc=defaultdict(int), imput=u in t.get('imput', ()), pages=t['pages'])
            for k in rest:
                v = r.get(k); n = t['cols'][k]
                if not isinstance(v, int): continue
                if mapeo.es_blanco(n): d['bla'] += v; continue
                if mapeo.es_nulo(n): d['nul'] += v; continue
                f = mapeo.fila(anio, p, n, W.get(p, []))
                b = mapeo.bloque(anio, p, f) if f else None
                d['parties'].append((n, v, b))
                d['bloc'][b or 'OTR'] += v
            out[(p, u)] = d
    return out

def competidores(d):
    """Bloques sumados; los partidos sin bloque compiten cada uno por su cuenta (no como «otros»)."""
    c = {b: v for b, v in d['bloc'].items() if b != 'OTR'}
    for n, v, b in d['parties']:
        if b is None: c['~' + n] = max(c.get('~' + n, 0), 0) + v
    return c

def ganador(d):
    c = competidores(d)
    if not c: return None
    b, v = max(c.items(), key=lambda x: x[1])
    return b if v > 0 else None

if __name__ == '__main__':
    T, log = cargar_todo()
    for Y in (1958, 1962, 1965):
        U = unidades(T, Y)
        g = defaultdict(int); nat = defaultdict(int)
        for k, d in U.items():
            g[ganador(d)] += 1
            for b, v in d['bloc'].items(): nat[b] += v
        print(Y, len(U), 'unidades; ganadores:', dict(g))
        print('   votos por bloque (suma Cantón):', dict(sorted(nat.items(), key=lambda x: -x[1])))
        if Y == 1958:
            o = defaultdict(int)
            for d in U.values():
                for n, v, b in d['parties']:
                    if b is None: o[n] += v
            print('   1958 otros:', sorted(o.items(), key=lambda x: -x[1])[:25])
        for k, d in U.items():
            if (ganador(d) or '').startswith('~') or ganador(d) is None:
                print('   gana OTR:', k, sorted(d['parties'], key=lambda x: -x[1])[:2])
