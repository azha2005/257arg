"""Datos y controles de los atlas de las PASO 2011–2023 (escrutinio provisorio de la DINE por mesa).

Presidenciales (2011, 2015, 2019, 2023): cargo presidente; agrupaciones y precandidatos de la tabla de la Wikipedia
(`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.
Legislativas (2013, 2017, 2021): diputados nacionales; cada agrupación lleva el bloque de la misma agrupación en la
general del mismo año (`paso_bloques.py`), con el color y el logo del atlas de esa general. Las que no siguieron a la
general y ganan alguna unidad llevan bloque propio con el color de la DINE.
El ganador de cada unidad es la agrupación (suma de sus listas internas); la ficha detalla cada lista."""
from pathlib import Path
from collections import Counter, defaultdict
from types import SimpleNamespace
import sys, re, json, zipfile, glob, difflib, unicodedata
import pandas as pd
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '../datos/wikipaso'))
import parse_paso
import paso_bloques
from leg2003_2025_data import D2P, ALIASES, PROV_ALIASES, BEIGE, GREY, num, dump, short
from leg2003_2025_geom import description
from names import norm

PRES = {2011, 2015, 2019, 2023}
FECHA = {2011: '14 de agosto de 2011', 2013: '11 de agosto de 2013', 2015: '9 de agosto de 2015', 2017: '13 de agosto de 2017',
         2019: '11 de agosto de 2019', 2021: '12 de septiembre de 2021', 2023: '13 de agosto de 2023'}
# Paleta de los mapas presidenciales de la Wikipedia (la misma que usan las legislativas 2003–2025, ver AGENTS.md)
PAL = {2011: [('victoria', '#50ade6'), ('amplio progresista', '#ff6600'), ('desarrollo social', '#d31515'), ('frente popular', '#b73c96'),
              ('compromiso federal', '#1aff98'), ('coalición cívica', '#74b744')],
       2015: [('victoria', '#50ade6'), ('cambiemos', '#f4ce00'), ('nueva alternativa', '#231f20'), ('compromiso federal', '#1aff98'),
              ('progresistas', '#ff6600')],
       2019: [('frente de todos', '#2ea3ff'), ('juntos por el cambio', '#f4ce00'), ('consenso federal', '#2f3b81')],
       2023: [('unión por la patria', '#009ce4'), ('libertad avanza', '#6c4c98'), ('juntos por el cambio', '#fcbc00'),
              ('hacemos', '#283084')]}
INT_PAL = ['#c62828', '#2e7d32', '#6a1b9a', '#ef6c00', '#00838f']   # internas: segundo, tercero... precandidato


def _fold(s):
    s = unicodedata.normalize('NFD', str(s).lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def load(year, pres):
    v, m = pd.read_pickle(ROOT / f'../datos_oficiales/{year}_paso/agregado.pkl')
    pat = 'PRESIDENT' if pres else 'DIPUTAD'
    v = v[v.cargo_nombre.str.upper().str.contains(pat)].copy(); m = m[m.cargo_nombre.str.upper().str.contains(pat)].copy()
    for df in (v, m):
        df['d'] = df.distrito_id.astype(int).astype(str).str.zfill(2)
        df['s'] = df.seccion_id.astype(int).astype(str).str.zfill(3)
    # el número de agrupación tal como viene (2019: «02-503»; 2023: «134»); sólo se rellenan con ceros los numéricos
    a = v.agrupacion_id.fillna('0').astype(str).str.strip()
    v['a'] = a.where(~a.str.fullmatch(r'\d+'), a.str.zfill(4))
    v['l'] = v.lista_numero.fillna('').astype(str).str.strip()
    v['t'] = v.votos_tipo.str.upper().str.strip()
    v['v'] = pd.to_numeric(v.v).astype(int)
    v = v[v.t != 'COMANDO']
    m['e'] = pd.to_numeric(m.mesa_electores, errors='coerce').fillna(0).astype(int)
    return v, m


def dine_colors(year):
    z = zipfile.ZipFile(glob.glob(str(ROOT / f'../datos_oficiales/{year}_paso/*.zip'))[0])
    n = next((x for x in z.namelist() if 'colores' in x.lower()), None)
    if not n: return {}
    c = pd.read_csv(z.open(n), dtype=str)
    return {(r.distrito_id.zfill(2), str(r.idAgrupacion).zfill(4)): r.color for r in c.itertuples()}


def _num4(a):
    d = re.findall(r'\d+', str(a))
    return str(int(d[-1]) % 1000).zfill(4) if d else ''


def titlecase(n):
    small = {'de', 'del', 'la', 'las', 'los', 'y', 'por', 'para', 'el', 'en', 'con', 'a'}
    w = n.lower().split()
    return ' '.join(x if (i and x in small) else x[:1].upper() + x[1:] for i, x in enumerate(w))


# nombres con tildes de las agrupaciones que la DINE escribe en mayúsculas sin acentos
NOMBRE = {'union por la republica frente por la justicia': 'Unión por la República – Frente por la Justicia',
          'juntos somos rio negro': 'Juntos Somos Río Negro', 'movimiento popular fueguino': 'Movimiento Popular Fueguino'}


COLOR_OWN = {'unidos por la libertad y el trabajo': ('#EE2225', 'color de su fila en la tabla de las legislativas de 2013 de la Wikipedia'),
             'union por la republica frente por la justicia': ('#4a148c', 'violeta oscuro: sin color en la Wikipedia ni en la DINE, y el magenta se confundía con el PACh y Salta Somos Todos'),
             'alianza justicialista': ('#1f3a93', 'azul oscuro: el celeste de la DINE se confundía con el FPV')}


def otro_atlas(nombre):
    """La misma fuerza en otro atlas de diputados 2003–2025 (color y logo ya revisados) -> (año, candidato) o None."""
    for y in (2021, 2023, 2019, 2017, 2015, 2013, 2011, 2025, 2009, 2007, 2005, 2003):
        f = ROOT / f'../mapas/mapa{y}/dataset_{y}.json'
        if not f.exists(): continue
        for k, c in json.loads(f.read_text(encoding='utf8'))['candidates'].items():
            if not k.startswith('P_') and _fold(c.get('n', '')) == _fold(nombre):
                return y, {q: x for q, x in c.items() if q not in ('logpal', 'logcov', 'sub')}
    return None


def prepare(key, U):
    year = int(key[:4]); pres = year in PRES and not key.endswith('dip')   # <año>pasodip: diputados en un año presidencial
    folder = ROOT / f'../mapas/mapa{key}'; folder.mkdir(exist_ok=True)
    v, m = load(year, pres)
    pos = v[v.t == 'POSITIVO']
    changes = []
    CAND = {}; listname = {}; agr_code = {}; bloc_total = Counter(); bloc_rows = {}
    if pres:
        W = parse_paso.presidente(year)
        num2code = {}
        for i, ag in enumerate(W['agr'], 1):
            code = f'B{i:02d}'
            n0 = re.match(r'(\d+)', ag['listas'][0]['codigo']).group(1)
            num2code[n0.zfill(4)] = code
            col = next((c for f, c in PAL[year] if f in ag['nombre'].lower()), None) or '#717274'
            CAND[code] = dict(n=re.sub(r'\s*\([^)]*\)', '', ag['nombre']), base=col, logo=short(ag['nombre']))
            bloc_total[code] = ag['total']; bloc_rows[code] = ag
        for (a, l, ln), sub in pos.groupby(['a', 'l', 'lista_nombre']):
            code = num2code.get(_num4(a)); agr_code[('', a)] = code
            ag = bloc_rows.get(code)
            if not ag: continue
            best = None
            if len(ag['listas']) == 1: best = ag['listas'][0]
            else:
                f = _fold(ln + ' ' + l)
                sc = [(difflib.SequenceMatcher(None, _fold(x['lista']), f).ratio() + (1 if _fold(x['lista']) in f else 0)
                       + (1 if _fold(x['pres']).split()[-1] in f else 0)
                       + (.5 if re.search(r'\b%s\b' % re.escape(x['codigo'].split()[-1].lower()), f) else 0), j) for j, x in enumerate(ag['listas'])]
                best = ag['listas'][max(sc)[1]]
            listname[(a, l)] = (best['pres'], best['vice'])
        # cada precandidato de la Wikipedia debe tener exactamente una lista de la DINE
        for code, ag in bloc_rows.items():
            got = [k for k, p in listname.items() if num2code.get(_num4(k[0])) == code]
            assert len({listname[k] for k in got}) == len(ag['listas']) or not got, (year, ag['nombre'], got)
        def bloc_of(d, a): return num2code.get(_num4(a))
        metrics = dict(pos=W['afirmativos'], bla=W['blancos'], nul=W['nulos'], total=W['total'], ins=W['inscriptos'],
                       src=f'tabla presidencial de «Elecciones primarias de Argentina de {year}» en la Wikipedia en español')
    else:
        M, how = paso_bloques.matcher(year, {(d, a, n) for d, a, n in zip(pos.d, pos.a, pos.agrupacion_nombre)})
        G = {k: (c, '') for k, c in M.items()}
        cov = pos.assign(r=[how.get(k, 'sin bloque') for k in zip(pos.d, pos.a)]).groupby('r').v.sum()
        changes.append('Emparejamiento con la general (votos): ' + '; '.join(f'{r} {100 * x / cov.sum():.1f} %' for r, x in cov.sort_values(ascending=False).items()) + '.')
        gen = json.loads((ROOT / f'../mapas/mapa{year}/dataset_{year}.json').read_text(encoding='utf8'))['candidates']
        dcol = dine_colors(year)
        def bloc_of(d, a): return G.get((d, a), (None, None))[0]
        # agrupaciones sin bloque en la general que ganan alguna unidad: bloque propio
        sec = pos.groupby(['d', 's', 'a']).v.sum().reset_index()
        win = sec.loc[sec.groupby(['d', 's']).v.idxmax()]
        own = sorted({(d, a) for d, a in zip(win.d, win.a) if not bloc_of(d, a)}); own_notes = {}
        for d, a in own:
            nm = pos[(pos.d == d) & (pos.a == a)].agrupacion_nombre.iloc[0]
            code = f'X{d}{a}'; G[(d, a)] = (code, nm)
            nice = NOMBRE.get(_fold(nm), titlecase(nm))
            ref = otro_atlas(nice)
            if ref:
                CAND[code] = dict(ref[1], sub=D2P[d])
                own_notes[code] = (f'{nice} ({D2P[d]}, agrupación {a}): no tiene bloque en la general de {year} y gana alguna unidad; '
                                   f'lleva bloque propio con el color y el logo del atlas de diputados {ref[0]} ({CAND[code]["base"]}).')
            else:
                col, src = COLOR_OWN.get(_fold(nm)) or ((dcol[(d, a)], 'color de la DINE') if (d, a) in dcol else ('#717274', 'gris: sin color en la DINE'))
                CAND[code] = dict(n=nice, base=col, logo=short(nice), sub=D2P[d])
                own_notes[code] = (f'{nice} ({D2P[d]}, agrupación {a}): no tiene bloque en la general de {year} y gana alguna unidad; '
                                   f'lleva bloque propio ({col}, {src}).')
        for code in {c for c, _ in G.values()}:
            if code in gen and code not in CAND:
                CAND[code] = {k: x for k, x in gen[code].items() if k not in ('logpal', 'logcov')}
        for (d, a), sub in pos.groupby(['d', 'a']):
            c = bloc_of(d, a)
            if c: bloc_total[c] += int(sub.v.sum())
        tv = v.groupby('t').v.sum()
        mp = dict(pos=int(tv.get('POSITIVO', 0)), bla=int(sum(x for t, x in tv.items() if 'BLANCO' in t)),
                  nul=int(sum(x for t, x in tv.items() if re.match(r'NULO|RECURRID|IMPUGNAD', t))))
        mp['total'] = mp['pos'] + mp['bla'] + mp['nul']
        mp['ins'] = int(m.drop_duplicates(['d', 's', 'circuito_id', 'mesa_id']).e.sum())
        metrics = dict(mp, src='suma del escrutinio provisorio de la DINE (la Wikipedia no trae tabla nacional de esta PASO)')
        if year == 2017:
            wm = parse_paso.metricas(2017, '=== Diputados ===')
            metrics = dict(pos=wm['afirmativos'], bla=wm['blancos'], nul=wm['nulos'], total=wm['total'], ins=wm['inscriptos'],
                           src='métricas de la tabla nacional de diputados de «Elecciones primarias de Argentina de 2017» en la Wikipedia; votos por bloque, suma del provisorio de la DINE')
    # nombres de las líneas de la ficha (una por lista interna)
    for (d, a, l), sub in pos.groupby(['d', 'a', 'l']):
        r = next(sub.itertuples()); c = bloc_of(d, a)
        k = f'P_{a}_{l}' if pres else f'P_{d}_{a}_{l}'
        if k in CAND: continue
        if pres and (a, l) in listname:
            nm = '%s – %s' % (listname[(a, l)][0], CAND[c]['n'])
        else:
            ag = titlecase(r.agrupacion_nombre)
            ln = re.sub(r'^\s*(lista)\s*', '', str(r.lista_nombre or ''), flags=re.I).strip()
            nm = ag if not ln or _fold(ln) == _fold(r.agrupacion_nombre) else f'{ag} – {titlecase(ln)}'
        CAND[k] = dict(n=nm, base=CAND[c]['base'] if c in CAND else '#8c8c8c')
    CAND['P_BLA'] = dict(n='Votos en blanco', base='#b5b5b5'); CAND['P_NUL'] = dict(n='Nulos, recurridos e impugnados', base='#8a8a8a')

    elect = m.drop_duplicates(['d', 's', 'circuito_id', 'mesa_id']).groupby(['d', 's']).e.sum().to_dict()
    sections = {}
    for (d, s), sub in v.groupby(['d', 's']):
        names = sub.seccion_nombre.dropna().astype(str); name = next((n for n in names if n and n.lower() != 'nan'), '')
        p = sub[sub.t == 'POSITIVO']
        lines = p.groupby(['a', 'l']).v.sum().to_dict(); b = defaultdict(int); bl = defaultdict(lambda: defaultdict(int))
        for (a, l), n in lines.items():
            c = bloc_of(d, a) or f'L_{d}_{a}'
            b[c] += int(n); bl[c][(a, l)] += int(n)
        sections[(d, s)] = dict(d=d, s=s, name=name, v={(f'P_{a}_{l}' if pres else f'P_{d}_{a}_{l}'): int(n) for (a, l), n in lines.items()},
                                b=dict(b), bl={c: dict(x) for c, x in bl.items()}, pos=int(p.v.sum()),
                                bla=int(sub[sub.t.str.contains('BLANCO')].v.sum()), nul=int(sub[sub.t.str.match(r'NULO|RECURRID|IMPUGNAD')].v.sum()),
                                el=int(elect.get((d, s), 0)), note='', invalid=False)
    merges = {('08', '002'): '001', ('21', '010'): '009', ('21', '014'): '013', ('21', '015'): '013'}
    for k, target in merges.items():
        if k not in sections: continue
        src = sections[k]
        if src['name'] and norm(src['name']) not in ('', 'suburbios', 'paranacampana', 'rosariosecciones', 'rosariosuburbios', 'lacapitalsuburbios', 'lacapitalcamp', 'rosariobarr', 'rosariocamp'): continue
        dst = sections.setdefault((k[0], target), dict(src, s=target, v={}, b={}, bl={}, pos=0, bla=0, nul=0, el=0, note=''))
        for q in ('pos', 'bla', 'nul', 'el'): dst[q] += src[q]
        for q in ('v', 'b'):
            for a, n in src[q].items(): dst[q][a] = dst[q].get(a, 0) + n
        for c, x in src['bl'].items():
            for kk, n in x.items(): dst['bl'].setdefault(c, {})[kk] = dst['bl'].get(c, {}).get(kk, 0) + n
        dst['note'] += ' Incluye la subsección electoral ' + k[1] + '.'
        del sections[k]
    ant = sections.pop(('24', '003'), None)
    idx = {(u['prov'], norm(u['name'])): i for i, u in enumerate(U) if u['name'] != 'Islas Malvinas'}
    linked = {}; unmapped = []
    for (d, s), rec in sections.items():
        p = D2P[d]
        if p == 'Capital Federal': k2 = (p, norm('Comuna %d' % int(s)))
        else:
            nn = norm(rec['name']); k2 = (p, nn)
            if k2 not in idx: k2 = (p, PROV_ALIASES.get((p, nn), ALIASES.get(nn, nn)))
        i = idx.get(k2)
        if i is None: unmapped.append((p, s, rec['name']))
        else:
            assert i not in linked, ('Secciones duplicadas', p, s); linked[i] = rec
    dump(folder / 'sin_poligono.json', unmapped)
    if unmapped: raise ValueError(('Sin polígono', key, unmapped))

    # ganadores
    wins = Counter(); missing = []
    for i, u in enumerate(U):
        if u['name'] == 'Islas Malvinas': continue
        r = linked.get(i)
        if not r or not r['pos']: missing.append(f"{u['prov']}: {u['name']}"); continue
        wins[max(r['b'], key=r['b'].get)] += 1
    if ant and ant['pos']: wins[max(ant['b'], key=ant['b'].get)] += 1
    bad = [c for c in wins if c not in CAND]
    if bad: raise ValueError(('Ganadores sin bloque', key, bad))
    if not pres: changes += [t for c, t in own_notes.items() if wins[c]]
    win_codes = sorted(wins, key=lambda c: -bloc_total[c])
    blocs = {c: int(bloc_total[c]) for c in win_codes}
    W = dict(art=f'Elecciones primarias de Argentina de {year}', blocs=blocs, otros=metrics['pos'] - sum(blocs.values()), positivos=metrics['pos'],
             blancos=metrics['bla'], dif=metrics['nul'], total=metrics['total'], inscriptos=metrics['ins'],
             lab_pos='Votos afirmativos' if pres else 'Votos positivos', lab_bla='Votos en blanco', lab_nul='Votos nulos / anulados')
    assert W['otros'] >= 0, W
    dump(folder / f'wiki_nacional_{key}.json', W)
    import wikitop
    wikitop.WIKI[key] = W
    cands, slices, partp, nmet = wikitop.national(key)
    nat = dict(cands=cands, slices=slices, partp=partp, metrics=nmet)
    # logos: legislativas, los del atlas de la general (ya revisados); presidenciales, bloques de los mapas de la Wikipedia
    if pres:
        from bloques_wiki import aplicar
        logo_info = [dict(code=c, bloque=b) for c, b in aplicar({c: CAND[c] for c in win_codes}, year)]
    else:
        logo_info = [dict(code=c, origen=f'atlas de diputados {year}') for c in win_codes if CAND[c].get('img')]

    # control base contra la Wikipedia (presidenciales) / contra la general (legislativas)
    control = []
    for c in sorted(bloc_total, key=lambda c: -bloc_total[c]):
        base = int(sum(r['b'].get(c, 0) for r in sections.values()) + (ant['b'].get(c, 0) if ant else 0))
        control.append(dict(codigo=c, bloque=CAND.get(c, {}).get('n', c), base_dine=base, referencia=int(bloc_total[c]), diferencia=base - int(bloc_total[c]), ganadas=wins[c]))
    pd.DataFrame(control).to_csv(folder / f'control_bloques_{key}.csv', index=False, encoding='utf-8-sig')

    cargo = 'presidente' if pres else 'diputados nacionales'
    note = (f'PASO del {FECHA[year]} ({cargo}). Nacional: {metrics["src"]}. Mapa: DINE, escrutinio provisorio por mesa, ganador por agrupación '
            f'(suma de sus listas internas). {description(year)}. No se imputan votos.')
    prov = {}
    def add(r):
        p = D2P[r['d']]; q = prov.setdefault(p, dict(d=r['d'], s='', name=p, v={}, b={}, bl={}, pos=0, bla=0, nul=0, el=0, note='', invalid=False))
        for k in ('pos', 'bla', 'nul', 'el'): q[k] += r[k]
        for k in ('v', 'b'):
            for a, n in r[k].items(): q[k][a] = q[k].get(a, 0) + n
        for c, x in r['bl'].items():
            for kk, n in x.items(): q['bl'].setdefault(c, {})[kk] = q['bl'].get(c, {}).get(kk, 0) + n
    for r in linked.values(): add(r)
    if ant: add(ant)

    def record(r):
        if not r or not r['pos']:
            return dict(lines=[], metrics=[], fill=BEIGE, note='Sin mesas en el escrutinio provisorio. No se imputan votos.')
        lines = [[c, n, round(100 * n / r['pos'], 2)] for c, n in sorted(r['v'].items(), key=lambda x: -x[1]) if n]
        emit = r['pos'] + r['bla'] + r['nul']
        for c, k in [('P_BLA', 'bla'), ('P_NUL', 'nul')]:
            if r[k]: lines.append([c, r[k], round(100 * r[k] / emit, 2)])
        met = [['Votos ' + ('afirmativos' if pres else 'positivos'), num(r['pos'])], ['Votantes', num(emit)]]
        msg = r['note']
        if r['el']:
            met.insert(0, ['Inscriptos', num(r['el'])])
            if emit <= r['el']: met.append(['Participación', f"{100 * emit / r['el']:.2f}".replace('.', ',') + ' %'])
        w = max(r['b'], key=r['b'].get)
        return dict(lines=lines, metrics=met, note=msg.strip(), w=w, q=round(100 * r['b'][w] / r['pos'], 2))
    unit_records = [record(linked.get(i)) for i in range(len(U))]
    for i, u in enumerate(U):
        if u['name'] == 'Islas Malvinas': unit_records[i] = dict(lines=[], metrics=[], fill=GREY, note='Sin voto argentino: islas bajo administración británica.')
    ant_record = record(ant)
    keys = [[BEIGE, 'Sin mesas en el provisorio']]
    modes = [dict(id='gan', tile='GANÓ', note=note, units=unit_records + [ant_record], prov={p: record(r) for p, r in prov.items()}, national=nat, legend=dict(keys=keys))]

    def strip(rec): return {k: x for k, x in rec.items() if k not in ('w', 'q', 'fill')}
    def unit_src(i): return linked.get(i)
    # internas presidenciales: color del precandidato que gana dentro de la agrupación
    internas = []
    if pres:
        for c in win_codes:
            ag = bloc_rows[c]
            if len([x for x in ag['listas'] if x['votos'] >= 0.02 * ag['total']]) >= 2: internas.append(c)
        internas = internas[:2]
    specs = []
    for c in internas:
        ag = bloc_rows[c]; order = [x['pres'] for x in sorted(ag['listas'], key=lambda x: -x['votos'])]
        col = {p: (CAND[c]['base'] if j == 0 else INT_PAL[j - 1]) for j, p in enumerate(order)}
        def fill_int(r, c=c, col=col):
            x = (r or {}).get('bl', {}).get(c)
            if not x or not sum(x.values()): return None
            (a, l), _ = max(x.items(), key=lambda t: t[1])
            p = listname.get((a, l), (None,))[0]
            return col.get(p)
        mk = [[col[p], p] for p in order] + [['#dcdcdc', 'Sin votos de la agrupación'], [BEIGE, 'Sin mesas en el provisorio']]
        def cf(rec, r, f=fill_int):
            out = strip(rec)
            out['fill'] = (f(r) or '#dcdcdc') if r and r['pos'] else rec.get('fill', BEIGE)
            return out
        un = [cf(unit_records[i], unit_src(i)) if u['name'] != 'Islas Malvinas' else unit_records[i] for i, u in enumerate(U)] + [cf(ant_record, ant)]
        modes.append(dict(id='int' + c.lower(), tile='I-' + CAND[c]['logo'][:3], note=note + ' Interna: precandidato más votado dentro de ' + CAND[c]['n'] + '.',
                          units=un, prov={p: cf(record(r), r) for p, r in prov.items()}, national=nat,
                          legend=dict(title='Interna de ' + CAND[c]['n'], bars=False, keys=mk)))
    nchor = 4 - len(internas)
    for c in win_codes[:nchor]:
        specs.append((c.lower(), CAND[c]['logo'][:5], lambda r, c=c: 100 * r['b'].get(c, 0) / r['pos'], CAND[c]['base'], '% ' + CAND[c]['n']))
    specs.append(('par', 'PART', lambda r: 100 * (r['pos'] + r['bla'] + r['nul']) / r['el'] if r['el'] and r['pos'] + r['bla'] + r['nul'] <= r['el'] else None,
                  '#2a6f97', 'Participación sobre el padrón (%)'))
    def tone(base, k):
        rgb = [int(base[j:j + 2], 16) for j in (1, 3, 5)]; return '#' + ''.join(f'{round(x * k):02x}' for x in rgb)
    for mid, tile, fn, color, title in specs:
        edges = [0, 50, 60, 65, 70, 75, 80] if mid == 'par' else [0, 10, 20, 30, 40, 50, 60]
        cols = [tone(color, k) for k in (1, .85, .7, .55, .4, .3, .2)]
        def chor(rec, r, fn=fn, cols=cols, edges=edges):
            out = strip(rec)
            q = fn(r) if r and r['pos'] else None
            ix = max([i for i, e in enumerate(edges) if q >= e] or [0]) if q is not None else 0
            out['fill'] = cols[ix] if q is not None else rec.get('fill', BEIGE)
            return out
        un = [chor(unit_records[i], unit_src(i)) if u['name'] != 'Islas Malvinas' else unit_records[i] for i, u in enumerate(U)] + [chor(ant_record, ant)]
        modes.append(dict(id=mid, tile=tile, note=note, units=un, prov={p: chor(record(r), r) for p, r in prov.items()}, national=nat,
                          legend=dict(title=title, stops=[[c, ('+' if i == 6 else '') + str(e) + '%'] for i, (c, e) in enumerate(zip(cols, edges))], bars=False, keys=keys)))
    # el orden de las pestañas: GANÓ, coropletas, internas, participación
    modes = [modes[0]] + [x for x in modes if x['id'] not in ('gan', 'par') and not x['id'].startswith('int')] + \
            [x for x in modes if x['id'].startswith('int')] + [x for x in modes if x['id'] == 'par']
    disp = {i: u['name'] for i, u in enumerate(U)}
    report = dict(key=key, year=year, cargo=cargo, geometry=description(year), units=len(U) + 1,
                  with_data=sum(bool(r and r['pos']) for r in linked.values()) + bool(ant and ant['pos']), missing=missing,
                  antartida_sin_dato=not bool(ant and ant['pos']), winners={CAND[c]['n']: n for c, n in wins.items()}, logos=logo_info,
                  corrections=changes, national=W, metrics_src=metrics['src'], internas=[CAND[c]['n'] for c in internas])
    dump(folder / 'control_cobertura.json', report)
    readme(key, folder, report, control)
    print(key, 'unidades', report['units'], 'con datos', report['with_data'], 'pendientes', missing, 'ganadores', report['winners'], flush=True)
    return SimpleNamespace(CAND=CAND, MODES=modes, disp=disp, ANT_I=len(U), report=report)


def readme(key, folder, report, control):
    y = report['year']
    s = f"# PASO {y}: {report['cargo']}\n\nElecciones primarias del {FECHA[y]}. Generado con `python comun/atlas_leg2003_2025.py {key}` (29-oct-2026).\n\n"
    s += f"- Datos: `datos_oficiales/{y}_paso/agregado.pkl` (escrutinio provisorio de la DINE por mesa, agregado con `datos/agregar_dine_paso.py`; fuente en `FUENTE.json`).\n"
    s += f"- Geometría: {report['geometry']}.\n- Resultado nacional (torta, barras, métricas): {report['metrics_src']}.\n"
    s += "- Ganador de cada unidad: la agrupación (suma de sus listas internas). La ficha muestra cada lista por separado.\n"
    if report['cargo'] == 'presidente':
        s += "- Agrupaciones y precandidatos: tabla de la Wikipedia (`datos/wikipaso/parse_paso.py`), emparejados con la DINE por número de agrupación y nombre de lista.\n"
        if report['internas']: s += f"- Modos de interna: {', '.join(report['internas'])} (color del precandidato más votado dentro de la agrupación).\n"
    else:
        s += f"- Bloques: el de la misma agrupación en la general de {y} (`comun/paso_bloques.py`), con color y logo del atlas de diputados {y}.\n"
    s += '\n| Bloque | Base DINE | Referencia | Diferencia | Unidades ganadas |\n|---|---:|---:|---:|---:|\n'
    for r in control:
        if r['ganadas']: s += f"| {r['bloque']} | {num(r['base_dine'])} | {num(r['referencia'])} | {r['diferencia']:+,} | {r['ganadas']} |\n".replace(',', '.')
    s += '\nReferencia: tabla de la Wikipedia (presidenciales, escrutinio definitivo: el provisorio no trae todas las mesas, de ahí la diferencia negativa) o la misma suma de la DINE (legislativas, diferencia 0 por construcción).\n'
    s += '\nSin mesas (beige, sin imputar): ' + ('; '.join(report['missing']) or 'ninguna') + '.\n'
    if report['antartida_sin_dato']: s += 'Antártida sin resultado separado: beige.\n'
    if report['corrections']: s += '\n' + '\n'.join('- ' + c for c in report['corrections']) + '\n'
    s += '\nEstado: generado localmente, sin PNG transparentes ni paquete de Commons.\n'
    (folder / f'LEEME_{key}.md').write_text(s, encoding='utf8')
