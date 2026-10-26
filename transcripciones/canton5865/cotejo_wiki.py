"""Suma Cantón por provincia y fila de Wikipedia y lo compara con las tablas provinciales (1962, 1965)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import defaultdict
from cargar import load
from sospechas import kinds
import correcciones, wikiprov, mapeo

W = {1962: wikiprov.parse('w1962.txt', '== Resultados por provincia'), 1965: wikiprov.parse('w1965.txt', '== Resultados por distrito')}

def sumas(T, Y, p, skip=()):
    t = T[(Y, 'D', p, 'T')]; ins, vot, rest = kinds(t['cols'])
    S = defaultdict(int)
    for u, r in t['rows'].items():
        if u in skip: continue
        for k in rest:
            if isinstance(r.get(k), int): S[t['cols'][k]] += r[k]
    return S

def cotejo(T, Y, p, skip=()):
    wr = W[Y].get(p)
    S = sumas(T, Y, p, skip)
    got, bad = defaultdict(int), []
    for n, v in S.items():
        if mapeo.es_blanco(n) or mapeo.es_nulo(n): continue
        f = mapeo.fila(Y, p, n, wr)
        if f is None: bad.append((n, v)); continue
        got[f] += v
    wd = dict(wr)
    dif = {f: v - wd.get(f, 0) for f, v in got.items() if v != wd.get(f)}
    miss = [(n, v) for n, v in wr if not n.startswith('#') and n not in got]
    return got, dif, bad, miss

if __name__ == '__main__':
    T, _ = load(); correcciones.aplicar(T); correcciones.imputar(T)
    for Y in (1962, 1965):
        print('\n######', Y)
        for (a, c, p, cat) in sorted(T):
            if (a, cat) != (Y, 'T') or p not in W[Y]: continue
            got, dif, bad, miss = cotejo(T, Y, p)
            print('##', p, '| sin fila:', bad, '| Wikipedia sin Cantón:', miss)
            for f, d in dif.items(): print('   %s: Cantón - Wikipedia = %+d' % (f, d))
