"""Tablas de las PASO en la Wikipedia en español (wpaso<año>.txt, bajados con la API).

presidente(año) -> dict(agr=[{nombre, color, total, listas:[{pres, vice, codigo, lista, votos}]}],
                        afirmativos, blancos, nulos, total, inscriptos)
metricas(año, seccion) -> métricas nacionales de una tabla (positivos, blancos, nulos, total, inscriptos)."""
import os, re
H = os.path.dirname(os.path.abspath(__file__))


def _txt(y):
    return open(os.path.join(H, 'wpaso%d.txt' % y), encoding='utf8').read()


def _clean(c):
    c = re.sub(r'<ref[^>]*/>|<ref.*?</ref>', '', c, flags=re.S)
    c = re.sub(r'\{\{[Rr]efn.*?\}\}', '', c)
    c = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', c)
    c = re.sub(r"'''?", '', c)
    return c.strip()


def _attr_val(c):
    """«align=left|texto» -> «texto»; deja la celda sin atributos tal cual."""
    if '[[' in c.split('|', 1)[0] or '{{' in c.split('|', 1)[0]: return c
    m = re.match(r'^\s*((?:[\w-]+\s*=\s*("[^"]*"|[^\s|]+)\s*)+)\|(.*)$', c, re.S)
    return m.group(3) if m else c


def _num(c):
    c = _clean(_attr_val(c))
    return int(c.replace('.', '')) if re.fullmatch(r'\d{1,3}(\.\d{3})+|\d{1,3}', c) else None


def _color(c):
    m = re.search(r'bgcolor\s*=\s*"?\s*(\{\{[Cc]olor político\|[^}]*\}\}|#?[\w]+)', c)
    return m.group(1) if m else None


def _table(y, start, end):
    t = _txt(y)
    i = t.index(start); i = t.index('{|', i); j = t.index('\n|}', i)
    if end and end in t[i:j]: j = t.index(end, i)
    return t[i:j]


def _rows(tbl):
    out = []
    for blk in re.split(r'\n\|-[^\n]*', tbl)[1:]:
        cells = []
        for line in blk.split('\n'):
            if line.startswith('!') or line.startswith('|'):
                cells += [c for c in re.split(r'\|\||!!', line[1:])]
        out.append(cells)
    return out


def _metric_rows(rows):
    m = {}
    for cells in rows:
        txt = ' '.join(cells)
        lab = re.search(r'(Votos afirmativos|Votos positivos|Votos en blanco|Votos válidos|Votos anulados|Votos nulos|Participación|Electores registrados)', txt)
        if not lab: continue
        nums = [x for x in (_num(c) for c in cells) if x is not None and x > 100]
        if nums: m[lab.group(1)] = nums[0]
    pos = m.get('Votos afirmativos') or m.get('Votos positivos')
    return dict(afirmativos=pos, blancos=m.get('Votos en blanco', 0), nulos=m.get('Votos anulados', m.get('Votos nulos', 0)),
                total=m.get('Participación'), inscriptos=m.get('Electores registrados'))


def presidente(y):
    tbl = _table(y, '=== Elecciones presidenciales', None)
    rows = _rows(tbl)
    agr, cur = [], None
    for cells in rows:
        txt = ' '.join(cells)
        if re.search(r'Votos (afirmativos|positivos)|bgcolor=#333333', txt): break
        cs = [c for c in cells]
        if not cs: continue
        nums = [_num(c) for c in cs]
        nums = [x for x in nums if x is not None and x >= 100]
        texts = [_clean(_attr_val(c)) for c in cs]
        code_i = next((i for i, c in enumerate(cs) if re.search(r"'''\s*\d+\s*\w{0,4}\s*'''", c)), None)
        if code_i is None: continue
        head = 'bgcolor' in cs[0] and not re.search(r"'''", cs[0])
        if head:
            name = texts[1]
            pres, vice = texts[2], texts[3]
            cur = dict(nombre=name, color=_color(cs[0]), total=None, listas=[])
            agr.append(cur)
        else:
            pres, vice = texts[code_i - 2], texts[code_i - 1]
        codigo = re.sub(r'\s+', ' ', texts[code_i]).strip()
        lista = texts[code_i + 1] if code_i + 1 < len(texts) else ''
        cur['listas'].append(dict(pres=pres, vice=vice, codigo=codigo, lista=lista, votos=nums[0]))
        if head: cur['total'] = nums[1] if len(nums) > 1 else nums[0]
    out = dict(agr=agr, **_metric_rows(rows))
    s = sum(a['total'] for a in agr)
    assert s == out['afirmativos'], (y, s, out['afirmativos'])
    for a in agr:
        assert sum(l['votos'] for l in a['listas']) == a['total'], (y, a['nombre'])
    return out


def metricas(y, start):
    return _metric_rows(_rows(_table(y, start, None)))


if __name__ == '__main__':
    import sys
    for y in [int(a) for a in sys.argv[1:]] or [2011, 2015, 2019, 2023]:
        P = presidente(y)
        print('==', y, {k: v for k, v in P.items() if k != 'agr'})
        for a in P['agr']:
            print('  %-45s %10d %s' % (a['nombre'][:45], a['total'], a['color']))
            for l in a['listas']: print('      %-28s %-8s %-30s %9d' % (l['pres'][:28], l['codigo'], l['lista'][:30], l['votos']))
