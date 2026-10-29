"""Datos por unidad de los atlas 1946-1973, en el formato de canton5865/datos.py:
    {(provincia, unidad): dict(ins, vot, bla, nul, parties=[(nombre, votos, bloque)], bloc, imput, cargo, est)}

  1946, 1954 : Cantón (1968), t. II, transcripciones de transcripciones/canton1946 y canton1954 (cifras tal cual).
  1948, 1948c, 1973, 1973s : Lupu y Stokes (2009), raw/lupu_stokes_1912_2003.dta. Solo trae cuatro familias (UCR, peronismo,
               socialistas, conservadores) y el total; el resto («otros») se reparte, por pedido del usuario, entre los partidos
               de la tabla provincial de la Wikipedia en proporción a sus votos provinciales (estimación, marcada como tal).
"""
import os, re, sys
from collections import OrderedDict, defaultdict
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(H, '..', '..')

# ---------------------------------------------------------------- Cantón 1946 y 1954
BLOQUE_CANTON = {
    '1946': {'Conjunción Peronista': 'PER', 'Laborista': 'PER', 'Partido Laborista': 'PER',
             'Unión Democrática': 'UD', 'Unión Cívica Radical (Comité Nacional)': 'UD',
             'Demócrata Nacional': 'PDN', 'Unión Cívica Radical Bloquista': 'UCRB',
             'Unión Cívica Radical (Santiago del Estero)': 'UCRSE', 'Unión Cívica Radical Lencinista': 'LEN'},
    '1954': {'Partido Peronista': 'PP', 'Unión Cívica Radical': 'UCR', 'Partido Demócrata': 'PD', 'Partido Comunista': 'PC',
             'Partido Socialista (Revolución Nacional)': 'PSRN', 'Partido Demócrata Progresista': 'PDP', 'Concentración Obrera': 'CO'},
}
# Cantón, t. I, Apéndice C: unidades sin cifras propias en 1912-1954 y la unidad mayor que las incluye.
SUBSUME = {('Buenos Aires', 'C. de M. Leonardo Rosales'): 'Bahía Blanca', ('Buenos Aires', 'González Chaves'): 'Necochea',
           ('Buenos Aires', 'Gonzales Chaves'): 'Necochea', ('Buenos Aires', 'Juárez'): 'Necochea', ('Buenos Aires', 'Tres Arroyos'): 'Necochea',
           ('Buenos Aires', 'Lanús'): 'Avellaneda', ('Buenos Aires', 'Leandro N. Alem'): 'Lincoln',
           ('Córdoba', 'Pte. Roque Saenz Peña'): 'Juárez Celman', ('Córdoba', 'General Roca'): 'Juárez Celman',
           ('Corrientes', 'General Alvear'): 'General San Martín', ('Mendoza', 'General Alvear'): 'San Rafael',
           ('Mendoza', 'Malargüe'): 'San Rafael', ('San Juan', 'Chimbas'): 'Concepción', ('San Juan', 'Zonda'): 'Rivadavia'}
SUBSUME_YEAR = {('Catamarca', 'Antofagasta de la Sierra'): ('1946', 'Belén')}
# territorios del 1954: la Zona Militar de Comodoro Rivadavia, repartida en los polígonos de 1960
ZONA_CR = {'Escalante': 'Chubut', 'Sarmiento': 'Chubut', 'Río Senguerr': 'Chubut', 'Deseado': 'Santa Cruz', 'Lago Buenos Aires': 'Santa Cruz'}
PROV_ALIAS = {'Comodoro Rivadavia': None}


def _num(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def canton(key):
    f = os.path.join(ROOT, 'transcripciones', 'canton%s' % key, 'canton_%s.csv' % key)
    d = pd.read_csv(f, encoding='utf-8-sig')
    B = BLOQUE_CANTON[key]
    out = OrderedDict()
    for prov, dp in d.groupby('provincia', sort=False):
        cats = set(dp.categoria)
        cat = 'varones y mujeres' if 'varones y mujeres' in cats else 'varones solamente'
        dp = dp[dp.categoria == cat]
        for u, g in dp.groupby('unidad', sort=False):
            vals = {r.concepto: _num(r.valor) for r in g.itertuples()}
            rec = dict(ins=vals.pop('Inscriptos', None), vot=vals.pop('Votantes', None), bla=0, nul=0, parties=[], bloc=defaultdict(int),
                       imput=False, cargo=g.eleccion.iloc[0], solo_varones=(cat == 'varones solamente' and key != '1946'),
                       pages=sorted(set(g.pagina_pdf)), est=False)
            for n, v in vals.items():
                if v is None: continue
                if re.search('blanco', n, re.I): rec['bla'] += v; continue
                b = B.get(n)
                rec['parties'].append((n, v, b)); rec['bloc'][b or 'OTR'] += v
            p = prov
            if prov == 'Comodoro Rivadavia':
                p = ZONA_CR[u]; rec['zona_cr'] = True
                if (p, u) in out:     # Deseado y Lago Buenos Aires: la parte santacruceña ya tiene fila propia
                    out[(p, u)].setdefault('zona_cr_extra', []).append(rec); continue
            out[(p, u)] = rec
    return out


# ---------------------------------------------------------------- Lupu y Stokes 1948 y 1973
LS_SEL = {'1948': (1948, 3, 'dip'), '1948c': (1948, 12, 'dip'), '1973': (1973, 3, 'pres'), '1973s': (1973, 9, 'pres')}
LS_FAM = {  # columna -> (nombre en la ficha, bloque)
    '1948': [('pj', 'Partido Peronista', 'PP'), ('ucr', 'Unión Cívica Radical', 'UCR'), ('soc', 'Partido Socialista', 'PS'), ('con', 'Partido Demócrata (conservadores)', 'PD')],
    '1948c': [('pj', 'Partido Peronista', 'PP'), ('ucr', 'Unión Cívica Radical', 'UCR'), ('soc', 'Partido Socialista', 'PS'), ('con', 'Conservadores', 'PD')],
    '1973': [('pj', 'FREJULI (Cámpora)', 'FJL'), ('ucr', 'UCR (Balbín)', 'UCR'), ('soc', 'Socialistas', 'PSD'), ('con', 'Conservadores', 'CON')],
    '1973s': [('pj', 'FREJULI (Perón)', 'FJL'), ('ucr', 'UCR (Balbín)', 'UCR'), ('soc', 'Socialistas', 'PST'), ('con', 'Conservadores', 'CON')],
}
LS_PROV = {'Cordoba': 'Córdoba', 'Entre Rios': 'Entre Ríos', 'Neuquen': 'Neuquén', 'Rio Negro': 'Río Negro', 'Tucuman': 'Tucumán'}


def lupu_stokes(key, reparto=None, colmap=None):
    """reparto[provincia] = [(partido, votos provinciales en la Wikipedia, bloque)] de los partidos que Lupu-Stokes no
    distingue: el residuo de cada unidad (total - familias) se reparte en esa proporción y se marca como estimado."""
    y, m, cargo = LS_SEL[key]
    d = pd.read_stata(os.path.join(ROOT, 'raw', 'lupu_stokes_1912_2003.dta'), convert_categoricals=False)
    d = d[(d.year == y) & (d.month == m) & (d[cargo] == 1)]
    out = OrderedDict()
    for r in d.itertuples():
        prov = LS_PROV.get(r.province, r.province)
        tot = _num(r.total) or 0
        rec = dict(ins=None, vot=None, bla=0, nul=0, parties=[], bloc=defaultdict(int), imput=False, cargo=cargo, est=False,
                   tot=tot, dcode=int(r.dcode))
        if tot <= 0:
            out[(prov, str(r.department))] = rec; continue
        fam = 0
        for col, n, b in LS_FAM[key]:
            if colmap is not None and col in ('soc', 'con'):
                if col not in colmap.get(prov, {}): n, b = n, None
                else: n, b = colmap[prov][col]
            v = _num(getattr(r, col))
            if not v: continue
            rec['parties'].append((n, v, b)); rec['bloc'][b or 'OTR'] += v; fam += v
        resto = tot - fam
        rec['resto'] = resto
        R = (reparto or {}).get(prov)
        if resto > 0 and R:
            s = sum(v for _, v, _ in R)
            acc = 0
            for i, (n, v, b) in enumerate(R):
                x = round(resto * v / s) if i < len(R) - 1 else resto - acc
                acc += x
                if x > 0 and b == '__BLA': rec['bla'] += x
                elif x > 0:
                    rec['parties'].append((n + ' (est.)', x, b)); rec['bloc'][b or 'OTR'] += x
            rec['est'] = True
        elif resto > 0:
            rec['parties'].append(('Otros (sin desagregar)', resto, None)); rec['bloc']['OTR'] += resto
        out[(prov, str(r.department))] = rec
    return out


# ---------------------------------------------------------------- reparto de «otros» con las tablas provinciales de la Wikipedia
def bloque_wiki(key, n):
    s = n.lower()
    if 'izquierda popular' in s: return 'FJL' if key == '1973s' else 'FIP'
    if 'peronista' in s or 'frejuli' in s: return 'FJL' if key.startswith('1973') else 'PP'
    if s.startswith('unión cívica radical') or s == 'ucr': return 'UCR'
    if 'trabajadores' in s: return 'PST'
    if 'socialista democrático' in s: return 'PSD'
    if 'socialista' in s: return 'PS'
    if 'demócrata progresista' in s: return 'PDP'
    if s == 'partido demócrata': return 'PD'
    if 'comunista' in s: return 'PC'
    if 'popular federalista' in s: return 'APF'
    if 'popular revolucionaria' in s: return 'APR'
    if 'republicana federal' in s: return 'ARF'
    if 'nueva fuerza' in s: return 'NF'
    if 'obrero de la revoluci' in s: return 'POR'
    if 'frente obrero revolucionario' in s: return 'FOR'
    if 'concentración obrera' in s: return 'CO'
    return None


def reparto_ls(key):
    """-> colmap[prov][col] = (nombre, bloque) para las columnas soc/con de Lupu-Stokes, reparto[prov] = [(partido, votos, bloque)]
    para el residuo y notas[prov]. Las columnas soc/con se identifican con el partido de la tabla provincial cuya proporción
    respecto del peronismo es la más parecida (en Santa Fe 1948 «con» es el PDP; en Mendoza y Corrientes 1973, la APF)."""
    import wikiprov4673
    W = wikiprov4673.provincial(key)
    y, m, cargo = LS_SEL[key]
    d = pd.read_stata(os.path.join(ROOT, 'raw', 'lupu_stokes_1912_2003.dta'), convert_categoricals=False)
    d = d[(d.year == y) & (d.month == m) & (d[cargo] == 1)]
    colmap, reparto, notas = {}, {}, {}
    for prov0, g in d.groupby('province'):
        prov = LS_PROV.get(prov0, prov0)
        rows = W.get(prov)
        if not rows: continue
        parties = [(n, v) for n, v in rows if not n.startswith('#') and v]
        tot = {n[1:].lower(): v for n, v in rows if n.startswith('#') and v}
        pj_w = next(v for n, v in parties if bloque_wiki(key, n) in ('PP', 'FJL') and 'izquierda' not in n.lower())
        S = {c: float(g[c].fillna(0).sum()) for c in ('total', 'pj', 'ucr', 'soc', 'con')}
        used = {n for n, v in parties if bloque_wiki(key, n) in ('PP', 'FJL', 'UCR') and 'izquierda' not in n.lower()}
        cm = {}
        for c in ('soc', 'con'):
            if S[c] <= 0 or S['pj'] <= 0: continue
            r = S[c] / S['pj']
            sem = [n for n, v in parties if n not in used and bloque_wiki(key, n) in (('PS', 'PSD', 'PST') if c == 'soc' else ('PD',))]
            if sem:   # la columna tiene el sentido que le da su nombre
                n = max(sem, key=lambda n: dict(parties)[n])
                cm[c] = (n, bloque_wiki(key, n)); used.add(n); continue
            cand = [(abs(v / pj_w - r) / max(r, 1e-9), n) for n, v in parties if n not in used]
            err, n = min(cand) if cand else (9, None)
            if err > 0.35:
                notas.setdefault(prov, []).append('columna «%s» de Lupu-Stokes sin partido identificable en la tabla de la Wikipedia (%.0f votos)' % (c, S[c]))
                cm[c] = ('Otro partido (columna «%s» de Lupu-Stokes)' % c, None); continue
            cm[c] = (n, bloque_wiki(key, n)); used.add(n)
        colmap[prov] = cm
        resto = [(n, v, bloque_wiki(key, n)) for n, v in parties if n not in used]
        pos_w = tot.get('votos válidos') or tot.get('votos positivos') or sum(v for _, v in parties)
        vot_w = tot.get('total de votos') or tot.get('votantes')
        bla_w = (vot_w - pos_w) if vot_w else 0
        # ¿el total de Lupu-Stokes es de votos positivos o de votantes? (cambia según la provincia)
        r = S['total'] / S['pj']
        if vot_w and abs(vot_w / pj_w - r) < abs(pos_w / pj_w - r) and bla_w > 0:
            resto.append(('En blanco, anulados y diferencias', bla_w, '__BLA'))
            notas.setdefault(prov, []).append('el total de Lupu-Stokes incluye blancos y anulados')
        reparto[prov] = resto
    return colmap, reparto, notas


if __name__ == '__main__':
    for k in ('1946', '1954'):
        D = canton(k)
        nat = defaultdict(int)
        for v in D.values():
            for b, x in v['bloc'].items(): nat[b] += x
        print(k, len(D), dict(nat))
    sys.path.insert(0, H)
    for k in LS_SEL:
        cm, rp, nt = reparto_ls(k)
        D = lupu_stokes(k, rp, cm)
        nat = defaultdict(int)
        for v in D.values():
            for b, x in v['bloc'].items(): nat[b] += x
        print(k, len(D), dict(nat)); print('   columnas:', cm); print('   notas:', nt)
