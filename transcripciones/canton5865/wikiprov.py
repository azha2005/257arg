"""Tablas provinciales de los artículos de Wikipedia (wiki/w1962.txt, wiki/w1965.txt) -> {provincia: [(partido, votos)]}."""
import re, os
HERE = os.path.dirname(os.path.abspath(__file__))
PROV = ['Buenos Aires', 'Capital Federal', 'Catamarca', 'Córdoba', 'Corrientes', 'Chaco', 'Chubut', 'Entre Ríos', 'Formosa', 'Jujuy',
        'La Pampa', 'La Rioja', 'Mendoza', 'Misiones', 'Neuquén', 'Río Negro', 'Salta', 'San Juan', 'San Luis', 'Santa Cruz', 'Santa Fe',
        'Santiago del Estero', 'Tucumán']

def clean(c):
    c = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", c)
    c = re.sub(r"<[^>]+>", "", c).replace("'''", "")
    return c.strip()

def parse(fn, start_marker):
    L = open(os.path.join(HERE, 'wiki', fn), encoding='utf-8').read().splitlines()
    i0 = next(i for i, l in enumerate(L) if l.startswith(start_marker))
    out, prov, i = {}, None, i0
    while i < len(L):
        l = L[i]
        if l.startswith('== ') and i > i0: break
        m = re.match(r"!\s*colspan=7\s*\|(.*)", l)
        if m:
            t = clean(m.group(1))
            prov = next((p for p in PROV if p in t), t)
            out.setdefault(prov, [])
        elif re.match(r"\|\s*bgcolor", l) and prov:
            name = clean(L[i + 1].split('|', 2)[-1]) if 'align=left' in L[i + 1] else None
            v = L[i + 2].strip('| ').replace('.', '')
            if name and v.isdigit(): out[prov].append((name, int(v)))
        elif 'colspan=3' in l and prov and re.search(r'Total|blanco|nulo|v[aá]lidos|positivos|registrados', l, re.I):
            lab = clean(l.split('|')[-1]); v = L[i + 1].strip('| ').replace('.', '')
            if v.isdigit(): out[prov].append(('#' + lab, int(v)))
        i += 1
    return out

if __name__ == '__main__':
    import sys
    for fn, mk in (('w1962.txt', '== Resultados por provincia'), ('w1965.txt', '== Resultados por distrito')):
        P = parse(fn, mk)
        print('###', fn, len(P))
        for p, rows in P.items(): print(' ', p, rows)
