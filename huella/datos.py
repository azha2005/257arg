"""Departamentos de 1916, 1922 y 1928: participación y % del ganador / de la UCR.
Lee los dataset_*.json de los atlas y escribe huella.json."""
import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = [(1916, 'mapa1916dip/dataset_1916.json'), (1922, 'mapa1922/dataset_1922.json'), (1928, 'mapa1928/dataset_1928.json')]
NOVAL = {'P_BLA', 'P_ANU'}

def num(s):
    s = str(s or '').replace('.', '')
    return int(s) if s.isdigit() else None

out, vistos = [], set()
for anio, f in FUENTES:
    d = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
    nombres = {k: v['n'] for k, v in d['candidates'].items()}
    for t, u in zip(d['territories'], d['modes'][0]['units']):
        if not u or not u.get('lines'):
            continue
        m = {k: v for k, v in u.get('metrics', [])}
        ins, vot = num(m.get('Inscriptos')), num(m.get('Votantes'))
        listas = [(c, v) for c, v, *_ in u['lines'] if c not in NOVAL and v]
        val = sum(v for _, v in listas)
        if not ins or not vot or not val or vot > ins * 1.02 or vot < 50:
            continue
        clave = (anio, t['p'], ins, vot, tuple(v for _, v in listas))
        if clave in vistos:          # varios polígonos de 1914 que repiten una misma fila
            continue
        vistos.add(clave)
        c_top, v_top = max(listas, key=lambda x: x[1])
        out.append(dict(a=anio, p=t['p'], d=t['n'], ins=ins, vot=vot, part=round(vot / ins, 4),
                        gan=round(v_top / val, 4), gl=c_top.replace('P_', ''),
                        ucr=round(sum(v for c, v in listas if c == 'P_UCR') / val, 4)))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'huella.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
from collections import Counter
print(len(out), Counter(x['a'] for x in out))
print(sorted(Counter(x['p'] for x in out).items()))
