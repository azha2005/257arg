"""Inventario de lectura: busca 2009 y partidos faltantes sin modificar originales."""
from pathlib import Path
import json, re
import pandas as pd

paths = set()
for fn in ('inventario_E_planillas_2009.txt', 'inventario_externo_2009.txt'):
    raw = Path(fn).read_bytes()
    txt = raw.decode('utf-16') if raw.startswith(b'\xff\xfe') else raw.decode('utf-8-sig')
    paths.update(x for x in txt.splitlines() if x.lower().endswith(('.xls', '.xlsx', '.xlsm')))
out = []
for f in sorted(paths):
    if any(x in f.lower() for x in ('santilan', 'steamapps', 'conta 1', 'manada', 'funciones test', 'supermercado', 'tabla de alumnos')):
        continue
    rec = {'path': f, 'sheets': []}
    try:
        xl = pd.ExcelFile(f)
        for s in xl.sheet_names:
            d = pd.read_excel(xl, sheet_name=s, header=None)
            text = d.astype(str)
            mask = text.apply(lambda c: c.str.contains(r'2009|sabbatell|nuevo\s*encuentro|NEP|nuev.*enc.*pop', case=False, regex=True))
            hits = []
            for i in mask.any(axis=1)[lambda x: x].index[:12]:
                hits.append({'row': int(i)+1, 'values': text.loc[i].tolist()[:35]})
            rec['sheets'].append({'sheet': s, 'shape': list(d.shape), 'head': text.head(2).iloc[:,:24].values.tolist(), 'hits': hits})
        print(f, [(s['sheet'], s['shape'], len(s['hits'])) for s in rec['sheets']], flush=True)
    except Exception as e:
        rec['error'] = str(e)
    out.append(rec)
Path('busqueda_planillas_2009.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf8')
