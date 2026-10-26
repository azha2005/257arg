"""Carga las transcripciones de Cantón (transcripciones/canton5865/transcripcion/p_*.json) y arma
una tabla por (año, cargo, provincia, categoría): {unidad: {columna: valor}}."""
import json, glob, os, re
from collections import defaultdict, OrderedDict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR = os.path.join(ROOT, 'canton5865', 'transcripcion')

def cat_of(c):
    c = (c or '').lower()
    if 'y mujeres' in c or 'total' in c or 'ambos' in c: return 'T'
    if 'mujer' in c: return 'M'
    if 'varon' in c: return 'V'
    return 'T'

ALIAS = {'Paso de los Indios': 'Paso de Indios', 'Martires': 'Mártires', 'Jachal': 'Jáchal',
         'Comandante Fernandez': 'Comandante Fernández', 'Pte. Roque Saénz Peña': 'Pte. Roque Saenz Peña'}

def clean_unit(u):
    u = re.sub(r'\s*\(\d+\)\s*$', '', u.strip())
    u = re.sub(r'\s+', ' ', u)
    return ALIAS.get(u, u)

def pages():
    out = []
    for f in glob.glob(os.path.join(TR, 'p_*.json')):
        p = json.load(open(f, encoding='utf-8'))
        p['_file'] = os.path.basename(f)
        out.append(p)
    out.sort(key=lambda p: p['pagina_pdf'])
    return out

def load(skip=()):
    """tablas[(anio, cargo, prov, cat)] = {'cols': {num: nombre}, 'rows': OrderedDict(unidad -> {num: val}), 'pages': [...]}"""
    T = {}
    conflicts = []
    for p in pages():
        if p['pagina_pdf'] in skip: continue
        cargo = 'P' if 'presid' in p['eleccion'].lower() else 'D'
        key = (p['anio'], cargo, p['provincia'].strip(), cat_of(p['categoria']))
        t = T.setdefault(key, {'cols': {}, 'rows': OrderedDict(), 'pages': [], 'circ': {}, 'src': {}})
        t['pages'].append(p['pagina_pdf'])
        for k, v in p['columnas'].items():
            k = int(k)
            if k in t['cols'] and t['cols'][k] != v:
                conflicts.append((key, p['pagina_pdf'], k, t['cols'][k], v))
            t['cols'][k] = v
        for r in p['filas']:
            u = clean_unit(r['departamento'])
            m = re.search(r'\((\d+)\)', r['departamento'])
            if r.get('circunscripcion') or m:
                t['circ'][u] = r.get('circunscripcion') or int(m.group(1))
            row = t['rows'].setdefault(u, {})
            for k, v in r['valores'].items():
                k = int(k)
                if v is None: continue
                if isinstance(v, str):
                    v = v.replace('.', '').strip()
                    v = int(v) if v.lstrip('-').isdigit() else v
                if k in row and row[k] != v:
                    conflicts.append((key, p['pagina_pdf'], u, k, row[k], v))
                row[k] = v
                t['src'][(u, k)] = p['pagina_pdf']
    return T, conflicts
