"""San Juan 1922/1928: pruebas de integridad electoral por departamento.
Lee las transcripciones de Cantón (mapa1922/canton, mapa1928/canton) y la tabla
nacional de 1928 (mapa1928/dataset_1928.json). Escribe resultados.json."""
import json, random, collections, os
from math import comb
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def leer(path, cols):
    out = {}
    for l in open(path, encoding='utf-8'):
        if '|' not in l or l.strip().endswith('-'):
            continue
        n, v = l.rstrip('\n').split('|')
        out[n] = {c: (None if x == '?' else int(x)) for c, x in zip(cols, v.split())}
    return out

d22 = leer(os.path.join(BASE, 'mapa1922/canton/p_SJ.txt'), ['INS', 'VOT', 'UCR', 'SOC', 'BLO', 'CNC'])
d28 = leer(os.path.join(BASE, 'mapa1928/canton/p_SJ.txt'), ['INS', 'VOT', 'SOC', 'BLA', 'VAR', 'BLO', 'FCAL', 'FJAC'])
R = {}

# ---- 1928: estructura por departamento
filas = []
for n, r in d28.items():
    fer = r['FCAL'] + r['FJAC']
    gob = r['BLO'] + fer                      # aparato oficialista: Melo (bloquistas) + listas Ferrocarril (Matienzo)
    top = max(r['BLO'], fer, r['SOC'])
    grupo = 'ferrocarril' if fer > r['BLO'] else ('unanime' if r['BLO'] / r['VOT'] > 0.95 else 'competitivo')
    filas.append(dict(dept=n, ins=r['INS'], vot=r['VOT'], part=r['VOT'] / r['INS'], blo=r['BLO'], fer=fer,
                      fcal=r['FCAL'], fjac=r['FJAC'], soc=r['SOC'], bla=r['BLA'],
                      top_sh=top / r['VOT'], gob_sh=gob / r['VOT'], opo_sh=(r['SOC'] + r['BLA']) / r['VOT'], grupo=grupo))
R['d28'] = filas
tot = collections.Counter()
for r in d28.values():
    tot.update(r)
R['tot28'] = dict(tot)
R['fer_total'] = tot['FCAL'] + tot['FJAC']
grandes = [f for f in filas if f['fer'] > 100]
R['fer_grandes'] = sum(f['fer'] for f in grandes)
R['fer_sueltos'] = {f['dept']: f['fer'] for f in filas if 0 < f['fer'] <= 100}

# Electores por lista incompleta (10: 7 a la primera, 3 a la segunda)
R['sin_ferrocarril'] = 'Si las 6.000 boletas Ferrocarril no hubieran existido, la segunda lista habría sido la socialista (3.463).'

# Participación por grupo
g = collections.defaultdict(lambda: [0, 0])
for f in filas:
    g[f['grupo']][0] += f['vot']; g[f['grupo']][1] += f['ins']
R['part_grupo'] = {k: v[0] / v[1] for k, v in g.items()}
R['spearman_part_gob'] = stats.spearmanr([f['part'] for f in filas], [f['gob_sh'] for f in filas])[0]
R['spearman_part_top'] = stats.spearmanr([f['part'] for f in filas], [f['top_sh'] for f in filas])[0]

# ---- 1928: comparación nacional de unanimidad (deptos con >200 votantes, lista ganadora > 95 % de los votantes)
nat = json.load(open(os.path.join(BASE, 'mapa1928/dataset_1928.json'), encoding='utf-8'))
vistos, cnt, unan_resto = set(), collections.Counter(), []
for t, u in zip(nat['territories'], nat['modes'][0]['units']):
    if not u or not u.get('lines'):
        continue
    m = {k: v for k, v in u.get('metrics', [])}
    try:
        vot = int(m['Votantes'].replace('.', ''))
    except Exception:
        continue
    clave = (t['p'], vot, tuple(x[1] for x in u['lines']))
    if clave in vistos:                     # polígonos que repiten una misma fila de Cantón
        continue
    vistos.add(clave)
    if vot < 200:
        continue
    partidos = [x[1] for x in u['lines'] if x[0] != 'P_BLA']
    grupo = 'SJ' if t['p'] == 'San Juan' else 'resto'
    cnt[grupo + '_n'] += 1
    if max(partidos) / vot > 0.95:
        cnt[grupo + '_u95'] += 1
        if grupo == 'resto':
            unan_resto.append((t['p'], t['n'], round(max(partidos) / vot, 3)))
R['unanimidad'] = dict(cnt)
R['unanimes_resto'] = unan_resto

# Listas provinciales de 1928 con total múltiplo de 1000
redondas, n_listas = [], 0
for p, v in nat['modes'][0]['prov'].items():
    for c, n, *_ in v.get('lines', []):
        if c in ('P_BLA', 'P_OTR', 'P_VAR') or n < 1000:
            continue
        n_listas += 1
        if n % 1000 == 0:
            redondas.append((p, c, n))
R['listas_1928'] = n_listas
R['listas_redondas'] = redondas
R['p_alguna_redonda'] = 1 - (1 - 1 / 1000) ** n_listas

# ---- 1922 -> 1928: oposición yrigoyenista que desaparece
cmp = []
for n in d28:
    a = d22.get(n)
    if not a:
        continue
    val = a['UCR'] + a['SOC'] + a['BLO'] + a['CNC']
    f = next(x for x in filas if x['dept'] == n)
    cmp.append(dict(dept=n, ucr22=a['UCR'] / val, blo22=a['BLO'] / val, val22=val,
                    opo28=f['opo_sh'], gob28=f['gob_sh'], grupo=f['grupo']))
R['cmp'] = cmp

# ---- 1922: empates exactos entre partidos de un mismo departamento (prueba de permutación)
cols = ['UCR', 'SOC', 'BLO', 'CNC']
def empates(tab):
    return sum(1 for r in tab for i in range(4) for j in range(i + 1, 4)
               if r[i] == r[j] and r[i] >= 20)
tab = [[d22[n][c] for c in cols] for n in d22]
obs = empates(tab)
random.seed(1)
sims = []
for _ in range(20000):
    cols_perm = [random.sample([r[k] for r in tab], len(tab)) for k in range(4)]
    sims.append(empates(list(zip(*cols_perm))))
R['empates22'] = dict(obs=obs, media=sum(sims) / len(sims), p=sum(s >= obs for s in sims) / len(sims),
                      casos=[(n, c1, c2, d22[n][c1]) for n in d22 for i, c1 in enumerate(cols) for c2 in cols[i + 1:]
                             if d22[n][c1] == d22[n][c2] and d22[n][c1] >= 20])

# ---- Último dígito (cifras >= 10, sin inscriptos ni votantes)
def digitos(dd, keys):
    v = [r[k] % 10 for r in dd.values() for k in keys if r[k] is not None and r[k] >= 10]
    o = [v.count(i) for i in range(10)]
    return dict(n=len(v), obs=o, p=stats.chisquare(o)[1])
R['dig22'] = digitos(d22, cols)
R['dig28'] = digitos(d28, ['SOC', 'BLA', 'BLO', 'FCAL', 'FJAC'])

json.dump(R, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=float)
for k in ['tot28', 'fer_total', 'fer_grandes', 'fer_sueltos', 'part_grupo', 'spearman_part_gob', 'spearman_part_top',
          'unanimidad', 'unanimes_resto', 'listas_1928', 'listas_redondas', 'p_alguna_redonda', 'empates22', 'dig22', 'dig28']:
    print(k, R[k])
for c in cmp:
    print(c)
