"""Tablas provinciales de la Wikipedia en español (wiki/w<clave>.txt) -> {provincia: [(partido, votos)] + totales con «#»}."""
import os, re
H = os.path.dirname(os.path.abspath(__file__))
PROVS = ['Buenos Aires', 'Capital Federal', 'Catamarca', 'Córdoba', 'Corrientes', 'Chaco', 'Chubut', 'Entre Ríos', 'Formosa', 'Jujuy',
         'La Pampa', 'La Rioja', 'Mendoza', 'Misiones', 'Neuquén', 'Río Negro', 'Salta', 'San Juan', 'San Luis', 'Santa Cruz', 'Santa Fe',
         'Santiago del Estero', 'Tucumán', 'Tierra del Fuego']
SKIP = re.compile(r'votos|total|blanco|diferencia|anulad|registrad|nulos|abstenc|participaci', re.I)


def _txt(k):
    t = open(os.path.join(H, 'wiki', 'w%s.txt' % k), encoding='utf8').read()
    return re.sub(r'\{\{[Cc]olor político\|[^}]*\}\}', '#ccc', t)


def _clean(c):
    c = re.sub(r'<ref.*?(</ref>|/>)', '', c)
    c = re.sub(r'\{\{refn.*?\}\}', '', c)
    c = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', c)
    if re.match(r'^\s*[\w-]+\s*=.*?\|', c) and not c.startswith('[['):
        c = c.split('|', 1)[1] if '|' in c else c
    return c.replace("'''", '').strip()


def _int(c):
    c = _clean(c)
    return int(c.replace('.', '')) if re.fullmatch(r'\d{1,3}(\.\d{3})*', c) else None


def _prov(h):
    if 'Capital Federal' in h: return 'Capital Federal'   # «[[Buenos Aires|Capital Federal]]»
    for p in PROVS:
        if p in h: return p
    if 'Eva Perón' in h: return 'La Pampa'
    if 'Presidente Perón' in h: return 'Chaco'
    return None


def secciones(k, start=None, end=None):
    """Tablas una por provincia (1948, 1948c): encabezado con el nombre y filas por partido."""
    lines = _txt(k).split('\n')
    a = next(i for i, l in enumerate(lines) if re.match(r'==+ *Resultados por (provincia|distrito)', l))
    out, prov, block = {}, None, []

    def flush():
        if not prov or not block: return
        party, nums = None, []
        cells = block
        for j, c in enumerate(cells):
            if re.fullmatch(r'\s*(rowspan=\d+\s*)?bgcolor=[^|]*\|\s*', c) and j + 1 < len(cells):
                party = _clean(cells[j + 1]); nums = [x for x in (_int(z) for z in cells[j + 2:]) if x is not None]
                break
        if party is None:
            for j, c in enumerate(cells):
                if 'align=left' in c and not SKIP.search(c):
                    pass
            m = [c for c in cells if 'colspan' in c and 'align=left' in c]
            if m:
                lab = _clean(m[0]); nums = [x for x in (_int(z) for z in cells) if x is not None]
                if nums: out[prov].append(('#' + lab, nums[0]))
            return
        if not nums or SKIP.search(party): return
        out[prov].append((party, nums[-1] if k == '1948' and len(nums) > 1 else nums[0]))

    for l in lines[a:]:
        if l.startswith('==') and 'Resultados' not in l and out: break
        if l.startswith('!') and ('[[Provincia' in l or '[[Capital Federal' in l or 'Capital Federal' in l and 'colspan' in l):
            flush(); block = []
            prov = _prov(l)
            if prov in out: prov = None    # segunda tabla del mismo distrito (complementarias): se ignora
            elif prov: out[prov] = []
            continue
        if l.startswith('|-') or l.startswith('|}'):
            flush(); block = []
            if l.startswith('|}'): prov = None
            continue
        if l.startswith('|') and prov:
            block.extend(re.split(r'\|\|', l[1:]))
    return out


def filas(k, cols):
    """Tabla única con una fila por provincia (1973, 1973s): cols = nombres de las columnas de votos, en orden."""
    lines = _txt(k).split('\n')
    a = next(i for i, l in enumerate(lines) if re.match(r'==+ *Resultados por provincia', l))
    out, row = {}, []
    for l in lines[a:]:
        if l.startswith('|-') or l.startswith('|}'):
            if row and _prov(row[0]):
                vals = [_int(c) for c in row[1:]]
                v = [x for i, x in enumerate(vals) if i % 2 == 0]   # votos, %, votos, %...
                out[_prov(row[0])] = list(zip(cols, v))
            row = []
            if l.startswith('|}') and out: break
            continue
        if l.startswith('|'):
            row.extend(re.split(r'\|\|', l[1:]))
    return out


COLS = {'1973': ['FREJULI', 'UCR', 'Alianza Popular Federalista', 'Alianza Popular Revolucionaria', 'Alianza Republicana Federal',
                 'Nueva Fuerza', 'Partido Socialista Democrático', 'Partido Socialista de los Trabajadores', 'Frente de Izquierda Popular',
                 '#Blanco', '#Nulo', '#Votantes'],
        '1973s': ['FREJULI', 'Frente de Izquierda Popular', '#Total Perón', 'UCR', 'Alianza Popular Federalista',
                  'Partido Socialista de los Trabajadores', '#Blanco', '#Nulo', '#Votantes']}


def provincial(k):
    return filas(k, COLS[k]) if k in COLS else secciones(k)


if __name__ == '__main__':
    import sys, json
    for k in sys.argv[1:] or ['1948', '1948c', '1973', '1973s']:
        P = provincial(k)
        print('==', k, len(P))
        for p, r in P.items(): print('  ', p, r)
