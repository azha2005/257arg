"""Lista las celdas sospechosas (suma de partidos != votantes, V+M != T, votantes > inscriptos)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cargar import load
from names import norm
from collections import defaultdict

def kinds(cols):
    ins = [k for k in cols if 'nscript' in cols[k]][0]
    vot = [k for k in cols if 'otante' in cols[k]][0]
    return ins, vot, [k for k in cols if k not in (ins, vot)]

def sospechas(T):
    out = []
    for key, t in sorted(T.items()):
        a, c, p, cat = key
        ins, vot, rest = kinds(t['cols'])
        for u, r in t['rows'].items():
            if not any(isinstance(v, int) for v in r.values()): continue
            if u == 'Observados Adjudicados': continue
            s = sum(r.get(k, 0) for k in rest if isinstance(r.get(k), int))
            if isinstance(r.get(vot), int) and s != r[vot]:
                out.append((key, u, 'suma', s - r[vot], [t['src'].get((u, k)) for k in (vot, rest[0])]))
            if isinstance(r.get(ins), int) and isinstance(r.get(vot), int) and r[vot] > r[ins]:
                out.append((key, u, 'vot>ins', r[vot] - r[ins], [t['src'].get((u, ins))]))
        if cat == 'T' and (a, c, p, 'V') in T:
            V, M = T[(a, c, p, 'V')], T[(a, c, p, 'M')]
            vn = {norm(u): (u, r) for u, r in V['rows'].items()}; mn = {norm(u): (u, r) for u, r in M['rows'].items()}
            for u, r in t['rows'].items():
                if norm(u) not in vn or norm(u) not in mn: continue
                (uv, rv), (um, rm) = vn[norm(u)], mn[norm(u)]
                for k in t['cols']:
                    x, y, z = rv.get(k), rm.get(k), r.get(k)
                    if None in (x, y, z) or not all(isinstance(q, int) for q in (x, y, z)): continue
                    if x + y != z:
                        out.append((key, u, f'V+M col{k}', x + y - z, [V['src'].get((uv, k)), M['src'].get((um, k)), t['src'].get((u, k))], (x, y, z)))
    return out

if __name__ == '__main__':
    import correcciones
    T, _ = load()
    correcciones.aplicar(T)
    S = sospechas(T)
    for s in S: print(*s)
    print(len(S), 'sospechas')
