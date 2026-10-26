import sys, re, math
sys.path.insert(0, '..')
import pandas as pd
from names import norm
d = pd.read_csv('../../preparados/lupu_stokes_1912_2003_exportacion.csv')
L = d[(d.year == 1922) & (d.pres == 1)]
PN = {'Cordoba': 'Córdoba', 'Entre Rios': 'Entre Ríos', 'Tucuman': 'Tucumán'}

def read(path):
    rows = []
    for ln in open(path, encoding='utf8'):
        if ln.startswith('#') or '|' not in ln: continue
        n, v = ln.rstrip('\n').split('|')
        rows.append((n, None if v.strip() == '-' else [(None if x == '?' else int(x)) for x in v.split()]))
    return rows

def main(path, prov, spec):
    S = {k: [int(x) for x in v.split(',') if x] for k, v in (p.split('=') for p in spec.split(';'))}
    conc = S.get('con', [])
    R = read(path); g = L[L.province.map(lambda s: PN.get(s, s)) == prov]
    AL = {'camapana':'campana','chascomis':'chascomus','clavarria':'olavarria','trenquelanguen':'trenquelauquen','nuevedejuli':'9dejulio','eumahuaca':'humahuaca','valleviego':'valleviejo','mburcuya':'mburucuya'}
    lk = {AL.get(norm(r.department), norm(r.department)): r for _, r in g.iterrows()}
    seen = set(); bad = 0
    for n, v in R:
        if v is None: continue
        if len(v) < S['n'][0]: print('  CORTA', n, v); continue
        hole = any(x is None for x in v[2:]); s = sum(x for x in v[2:] if x is not None); issues = []
        if S.get('blank') and not hole and v[1] is not None and not (0.97 * v[1] <= s <= 1.03 * v[1]) and v[1] > 0: issues.append('suma partidos %d vs votantes %d' % (s, v[1]))
        if v[0] is not None and v[1] is not None and v[1] > v[0]: issues.append('votantes>inscriptos')
        r = lk.get(norm(n)); seen.add(norm(n))
        if r is not None and r.total > 0 and not hole:
            if r.ucr != sum(v[i-1] for i in S['ucr']): issues.append('ucr canton %d lupu %d' % (sum(v[i-1] for i in S['ucr']), r.ucr))
            if not math.isnan(r.soc) and r.soc != sum(v[i-1] for i in S['soc']): issues.append('soc canton %d lupu %d' % (sum(v[i-1] for i in S['soc']), r.soc))
            c = sum(v[i - 1] for i in conc)
            if conc and not math.isnan(r.con) and r.con != c: issues.append('con canton %d lupu %d' % (c, r.con))
            if r.total != s: issues.append('total canton(suma) %d lupu %d' % (s, r.total))
        if issues: bad += 1; print('  ', n, v, '|', '; '.join(issues))
    only = [r.department for k, r in lk.items() if k not in seen and r.total > 0]
    print(prov, 'filas', len(R), 'con datos', sum(v is not None for _, v in R), 'con alerta', bad, '| Lupu con votos y no en Canton:', only)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
