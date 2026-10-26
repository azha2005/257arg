"""Cuyo 1928: San Juan (gobierno bloquista) contra Mendoza (gobierno lencinista).
Lee las transcripciones de Cantón y escribe resultados.json."""
import json, os
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))

def leer(rel, cols):
    out = []
    for l in open(os.path.join(BASE, rel), encoding='utf-8'):
        if '|' not in l or l.strip().endswith('-'):
            continue
        n, v = l.rstrip('\n').split('|')
        out.append(dict(dept=n, **{c: (None if x == '?' else int(x)) for c, x in zip(cols, v.split())}))
    return out

R = {}
# San Juan: oficialismo = bloquistas (Melo) + listas Ferrocarril (Matienzo)
sj = []
for r in leer('mapa1928/canton/p_SJ.txt', ['INS', 'VOT', 'SOC', 'BLA', 'VAR', 'BLO', 'FCAL', 'FJAC']):
    fer = r['FCAL'] + r['FJAC']
    sj.append(dict(dept=r['dept'], ins=r['INS'], vot=r['VOT'], part=r['VOT'] / r['INS'],
                   gob=(r['BLO'] + fer) / r['VOT'], top=max(r['BLO'], fer, r['SOC']) / r['VOT'],
                   opo=(r['SOC'] + r['BLA']) / r['VOT']))
# Mendoza: oficialismo = UCR Lencinista; sin columna de blancos (residuo = votantes - partidos)
mz = []
for r in leer('mapa1928/canton/p_MZA.txt', ['INS', 'VOT', 'UCR', 'SOC', 'COM', 'LIB', 'LEN']):
    part_sum = r['UCR'] + r['SOC'] + r['COM'] + r['LIB'] + r['LEN']
    mz.append(dict(dept=r['dept'], ins=r['INS'], vot=r['VOT'], part=r['VOT'] / r['INS'],
                   gob=r['LEN'] / r['VOT'], top=max(r['UCR'], r['LEN']) / r['VOT'],
                   ucr=r['UCR'] / r['VOT'], res=(r['VOT'] - part_sum) / r['VOT'],
                   opo=(r['VOT'] - r['LEN']) / r['VOT']))
R['sj'], R['mz'] = sj, mz

def resumen(rows):
    ins = sum(r['ins'] for r in rows); vot = sum(r['vot'] for r in rows)
    return dict(n=len(rows), part=vot / ins, part_min=min(r['part'] for r in rows), part_max=max(r['part'] for r in rows),
                top_max=max(r['top'] for r in rows), n95=sum(r['top'] > .95 for r in rows),
                gob=sum(r['gob'] * r['vot'] for r in rows) / vot,
                rho=stats.spearmanr([r['part'] for r in rows], [r['gob'] for r in rows])[0],
                rho_p=stats.spearmanr([r['part'] for r in rows], [r['gob'] for r in rows])[1])
R['res_sj'], R['res_mz'] = resumen(sj), resumen(mz)

# Mendoza 1916 -> 1928: crecimiento del padrón contra voto lencinista
d16 = json.load(open(os.path.join(BASE, 'mapa1916dip/dataset_1916.json'), encoding='utf-8'))
ins16 = {}
for t, u in zip(d16['territories'], d16['modes'][0]['units']):
    if t['p'] == 'Mendoza' and u and u.get('metrics'):
        m = {k: v for k, v in u['metrics']}
        if m.get('Inscriptos'):
            ins16[t['n']] = int(m['Inscriptos'].replace('.', ''))
pad = [dict(dept=r['dept'], ins16=ins16[r['dept']], ins28=r['ins'], crec=r['ins'] / ins16[r['dept']] - 1, gob=r['gob'])
       for r in mz if r['dept'] in ins16]
R['padron_mz'] = pad
R['padron_rho'] = stats.spearmanr([p['crec'] for p in pad], [p['gob'] for p in pad])[0]
R['padron_tot'] = dict(ins16=sum(p['ins16'] for p in pad), ins28=sum(p['ins28'] for p in pad))

# Mendoza: mismo día, electores de presidente contra diputados nacionales
# electores: Memoria del Interior vía Cantón; diputados: Wikipedia, «Elecciones legislativas de Argentina de 1928»
R['corte'] = [('UCR (Yrigoyen)', 27323, 26506), ('UCR Lencinista', 20166, 20287),
              ('Partido Liberal', 1407, 1974), ('Partido Socialista', 1558, 1641), ('Partido Comunista', 52, 54)]

# La Puna: unanimidad rural fuera de San Juan
R['puna'] = [
    ('Jujuy', 1922, 'Cochinoca', 'UCR 649 · Concentración 1'), ('Jujuy', 1922, 'Humahuaca', 'UCR 740 · Concentración 0'),
    ('Jujuy', 1922, 'Rinconada', 'UCR 297 · Concentración 0'), ('Jujuy', 1922, 'Santa Catalina', 'UCR 418 · Concentración 0'),
    ('Jujuy', 1928, 'Cochinoca', 'UCR 392 · Antipersonalistas 499'), ('Jujuy', 1928, 'Rinconada', 'UCR 134 · Antipersonalistas 187'),
    ('Salta', 1928, 'Santa Victoria', 'UCR 10 · Antipersonalistas 813'), ('Salta', 1928, 'Iruya (vecino)', 'UCR 293 · Antipersonalistas 430'),
]
json.dump(R, open(os.path.join(AQUI, 'resultados.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k in ('res_sj', 'res_mz', 'padron_rho', 'padron_tot'):
    print(k, R[k])
