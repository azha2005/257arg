"""Coteja una transcripción de Cantón (1930) con Lupu–Stokes, fila por fila.
    python check.py            -> todas las jurisdicciones de spec.SPEC
    python check.py "San Juan" -> una sola
Avisa cuando la UCR, el PS o la suma de partidos no coinciden con Lupu, y cuando la suma de
partidos se aparta más de 3 % de los votantes (si la página no trae columna de blancos)."""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pandas as pd
from names import norm
from spec import SPEC

d = pd.read_csv(os.path.join(HERE, '..', '..', '../datos/preparados', 'lupu_stokes_1912_2003_exportacion.csv'))
L = d[(d.year == 1930) & (d.dip == 1)]
PN = {'Cordoba': 'Córdoba', 'Entre Rios': 'Entre Ríos', 'Tucuman': 'Tucumán'}
AL = {'eumahuaca': 'humahuaca', 'yavi': 'yavi', 'mburcuya': 'mburucuya', 'valleviego': 'valleviejo', "camapana": "campana", "chascomis": "chascomus", 'nuevedejuli': '9dejulio', 'nuevedejulio': 'nuevedejulio', '9dejulio': 'nuevedejulio', 'trenquelanguen': 'trenquelauquen'}


def read(path):
    rows = []
    for ln in open(path, encoding='utf8'):
        if ln.startswith('#') or '|' not in ln:
            continue
        n, v = ln.rstrip('\n').split('|')
        rows.append((n, None if v.strip() == '-' else [(None if x == '?' else int(x)) for x in v.split()]))
    return rows


def main(prov):
    sp = SPEC[prov]; cols = sp['cols']
    R = read(os.path.join(HERE, sp['file']))
    g = L[L.province.map(lambda s: PN.get(s, s)) == prov]
    lk = {AL.get(norm(r.department), norm(r.department)): r for _, r in g.iterrows()}
    seen, bad = set(), 0
    for n, v in R:
        if v is None:
            continue
        issues = []
        if len(v) != len(cols):
            print('   LARGO', n, len(v), 'columnas, se esperaban', len(cols)); bad += 1; continue
        P = {}
        for c, x in zip(cols, v):
            if c not in ('INS', 'VOT') and x is not None:
                P[c] = P.get(c, 0) + x
        s = sum(x for c, x in P.items())
        ins, vot = v[cols.index('INS')], v[cols.index('VOT')]
        if vot and not (0.97 * vot <= s <= 1.03 * vot) and 'BLA' in cols:
            issues.append('suma %d vs votantes %d' % (s, vot))
        if vot and s > 1.03 * vot:
            issues.append('partidos %d > votantes %d' % (s, vot))
        if ins and vot and vot > ins:
            issues.append('votantes>inscriptos')
        k = norm(n); seen.add(AL.get(k, k))
        r = lk.get(AL.get(k, k))
        if r is not None and r.total > 0:
            sv = s - P.get('BLA', 0)
            u = sum(P.get(c, 0) for c in sp.get('ucr', ['UCR']))
            if not math.isnan(r.ucr) and r.ucr != u: issues.append('ucr %d lupu %d' % (u, r.ucr))
            if not math.isnan(r.soc) and r.soc > 0 and r.soc != P.get('SOC', 0): issues.append('soc %d lupu %d' % (P.get('SOC', 0), r.soc))
            if r.total not in (s, sv): issues.append('suma %d (sin blanco %d) lupu %d' % (s, sv, r.total))
        elif r is None:
            issues.append('sin fila en Lupu')
        if issues:
            bad += 1; print('  ', n, v, '|', '; '.join(issues))
    only = [r.department for k, r in lk.items() if k not in seen and r.total > 0]
    print(prov, '| filas', len(R), '| con alerta', bad, '| en Lupu y no en Canton:', only)


if __name__ == '__main__':
    for p in (sys.argv[1:] or SPEC):
        main(p)
