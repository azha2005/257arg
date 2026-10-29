"""Bloque de cada agrupación de las PASO de diputados: el de la misma agrupación en la elección general del mismo
año, ya asignado a la tabla de la Wikipedia por los atlas de diputados (`mapas/mapa<año>/mapeo_listas_<año>.csv`;
2013: `LIST2BLOC` de `build_2013.py`).

La DINE no numera igual las agrupaciones en la PASO y en la general de todos los años (2019: «02-503» y «0135»;
2023: «134» y «20134»; 2015: «ALIANZA CAMBIEMOS» 0135 en la PASO y «CAMBIEMOS BUENOS AIRES» 0145 en la general),
así que se empareja dentro de cada distrito, en este orden:
1. mismo nombre de agrupación (también sin «alianza», «frente», etc.);
2. el nombre de la PASO coincide con el del bloque de la Wikipedia;
3. un nombre contiene entero al otro (sin «alianza», «frente», etc.), salvo que el más corto sea una sola palabra
   genérica o el nombre de una provincia («Popular», «Todos», «Chubut»);
4. mismo número (últimas cifras) y nombres parecidos.
Antes de todo eso, `OVERRIDE` fija a mano los casos que las reglas no ven (con el motivo)."""
from pathlib import Path
import ast, re, difflib, unicodedata
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent
GENERIC = {'todos', 'popular', 'federal', 'juntos', 'libertad', 'nueva', 'union', 'social', 'civico', 'renovador', 'democracia',
           'unidad', 'cambio', 'victoria', 'izquierda', 'trabajadores', 'progresista', 'consenso', 'encuentro', 'accion', 'movimiento',
           'buenos', 'aires', 'catamarca', 'cordoba', 'corrientes', 'chaco', 'chubut', 'entre', 'rios', 'formosa', 'jujuy', 'pampa',
           'rioja', 'mendoza', 'misiones', 'neuquen', 'rio', 'negro', 'salta', 'juan', 'luis', 'santa', 'cruz', 'fe', 'santiago',
           'estero', 'tucuman', 'tierra', 'fuego', 'ciudad', 'socialista', 'socialismo', 'humanista', 'demócrata', 'democrata'}
# (año, distrito, agrupación de la PASO) -> agrupación de la general (misma fuerza con otro nombre)
OVERRIDE = {
    (2011, '08', '0501'): '0626',   # Entre Ríos: «Alianza Frente para la Victoria» = «Alianza Frente Justicialista para la Victoria»
    (2015, '22', '0532'): '0533',   # Santiago: «Frente Cívico y Social» (lista «Celeste y Blanca K Néstor Kirchner») = «Frente Cívico para la Victoria»
}
STOP = r'\b(alianza|frente|partido|por|para|la|el|de|del|los|las|y)\b'


def _n(s):
    s = unicodedata.normalize('NFD', str(s).lower()).encode('ascii', 'ignore').decode()
    s = re.sub(r'\([^)]*\)', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def _core(s):
    return re.sub(r'\s+', ' ', re.sub(STOP, ' ', _n(s))).strip()


def _tail(a):
    d = re.findall(r'\d+', str(a))
    return int(d[-1]) % 1000 if d else None


def general(year):
    """-> lista de dicts (d, a, nombre, codigo, bloque) de la general del año."""
    if year == 2013:
        src = (ROOT / 'mapas/mapa2013/build_2013.py').read_text(encoding='utf8')
        tree = ast.parse(src); ns = {'D2P': {str(n).zfill(2): n for n in range(1, 25)}}
        for node in tree.body:
            seg = ast.get_source_segment(src, node)
            if re.match(r'(LIST2BLOC|for _d in D2P|BLOCS\s*=)', seg or ''): exec(seg, ns)
        return [dict(d=d, a=a, nombre='', codigo=b, bloque=b) for (d, a), b in ns['LIST2BLOC'].items()]
    m = pd.read_csv(ROOT / f'mapas/mapa{year}/mapeo_listas_{year}.csv', dtype=str).fillna('')
    return [dict(d=r.distrito.zfill(2), a=r.lista, nombre=r.nombre, codigo=r.codigo, bloque=r.bloque) for r in m.itertuples() if r.codigo]


def matcher(year, paso):
    """paso: iterable de (d, a, nombre) de la PASO -> ({(d, a): código}, {(d, a): regla usada})"""
    G = general(year); out, how = {}, {}
    for d, a, nm in paso:
        cand = [g for g in G if g['d'] == d]
        if (year, d, a) in OVERRIDE:
            hit = [g for g in cand if g['a'] == OVERRIDE[(year, d, a)]]
            out[(d, a)] = hit[0]['codigo']; how[(d, a)] = 'a mano'; continue
        hit = [g for g in cand if g['nombre'] and _n(g['nombre']) == _n(nm)]
        rule = 'nombre'
        if not hit:   # «Alianza Unión para Vivir Mejor» / «UNION PARA VIVIR MEJOR»
            hit = [g for g in cand if g['nombre'] and _core(g['nombre']) and _core(g['nombre']) == _core(nm)]; rule = 'nombre'
        if not hit:
            hit = [g for g in cand if _core(g['bloque']) and _core(g['bloque']) == _core(nm)]; rule = 'bloque'
        if not hit:   # «Alianza Cambiemos Mendoza» / «ALIANZA CAMBIEMOS»; «Eco + Vamos Corrientes» / «Encuentro por Corrientes - ECO+VAMOS CORRIENTES»
            w = set(_core(nm).split())
            def ok(g):
                x = set(_core(g['nombre']).split()); short = min(x, w, key=len)
                return bool(short) and (x <= w or w <= x) and not (len(short) == 1 and next(iter(short)) in GENERIC)
            sc = [(len(w & set(_core(g['nombre']).split())), i) for i, g in enumerate(cand) if g['nombre'] and ok(g)]
            if sc: hit = [cand[max(sc)[1]]]; rule = 'nombre contenido'
        if not hit:
            hit = [g for g in cand if _tail(g['a']) == _tail(a) and (not g['nombre'] or
                   difflib.SequenceMatcher(None, _core(g['nombre']), _core(nm)).ratio() > 0.6)]; rule = 'número'
        if hit:
            out[(d, a)] = hit[0]['codigo']; how[(d, a)] = rule
    return out, how
