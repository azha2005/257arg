"""Elección de representantes de Buenos Aires del 22 de julio de 1827 y votación del gobernador (12 de agosto).

Fuentes: La Gaceta Mercantil N1096-N1134 y Crónica Política y Literaria 46-80 (Hemeroteca de la BNMM), Galimberti (San Nicolás); transcripciones en
transcripciones/1827/. Geometría: partidos del censo de 1869 (Rodríguez y De Grande, CONICET) agrupados
en las secciones del decreto del 9 de julio de 1827 (N1102).

    "C:/Users/JC/Desktop/Escritorio 26/mosaic_python-main/.venv/Scripts/python.exe" mapas/mapa1827/build_1827.py
"""
import csv, html, json, math, unicodedata, re
from pathlib import Path

import geopandas as gpd
import shapely
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TR = ROOT / "transcripciones/1827"
SHP = ROOT / "geometria/Base deptos 1869-2022/Departamentos_1869.shp"


def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if not unicodedata.combining(c)))


def leer(nombre):
    with open(TR / nombre, encoding='utf-8') as f:
        return list(csv.DictReader(f))


BANCAS = leer('bancas_1827.csv')
ELECTOS = leer('electos_1827.csv')
SECC = [b['seccion'] for b in BANCAS]
NB = {b['seccion']: int(b['bancas']) for b in BANCAS}
assert sum(NB.values()) == 47

# ------------------------------------------------------------------ geometría
g = gpd.read_file(SHP, encoding='utf-8')
g = g[g.PROV_COD.isin(['06', '02'])]
geo = {norm(r.DEPTO): shapely.make_valid(r.geometry).buffer(0) for r in g.itertuples()}
ciudad = [k for k in geo if k.startswith('seccion')]
usados = set()
GEOM = {}
for b in BANCAS:
    if b['seccion'] == 'Ciudad':
        ks = ciudad
    else:
        ks = [norm(x) for x in b['partidos_1869_en_el_mapa'].split(';')]
    for k in ks:
        assert k in geo, (b['seccion'], k)
    usados |= set(ks)
    GEOM[b['seccion']] = unary_union([geo[k] for k in ks]).buffer(0.0004).buffer(-0.0004)
RESTO = unary_union([v for k, v in geo.items() if k not in usados]).buffer(0)
PROV = unary_union(list(geo.values())).buffer(0)

# Frontera de 1826/27: bandas del mapa escolar de avance de la frontera, georreferenciado (frontera.py y georef.py en
# geometria/frontera_bsas_1827/), unidas a la jurisdicción de Buenos Aires de 1788 del HGIS de las Indias, que cubre el
# noreste que el mapa escolar tapa con texto y ríos. Patagones queda como enclave con su partido de 1869.
FR = ROOT / "geometria/frontera_bsas_1827"
_fr = gpd.read_file(FR / "frontera_1826_mapa_escolar.geojson").geometry.iloc[0]
_hg = gpd.read_file(FR / "hgis_indias_jurisdicciones_1787_1788.geojson")
_ba = _hg[_hg.Nombre == 'Buenos Aires'].geometry.iloc[0]
TERR = unary_union([_fr, _ba]).buffer(0.01).buffer(-0.01).intersection(PROV)
for _s in GEOM:
    if _s != 'Patagones':
        GEOM[_s] = GEOM[_s].intersection(TERR).buffer(0)
# Patagones: la Comandancia del HGIS (OBJECTID 1580, vigente de 1787 a 1808, la de 1806-07) tiene dos partes: Carmen, a los
# dos lados del río Negro, y el fuerte San José de la península Valdés, abandonado en 1810. Se usa solo la de Carmen.
_pat = _hg[_hg.Nombre == 'Patagones'].geometry.iloc[0]
_pat = [q for q in getattr(_pat, 'geoms', [_pat]) if q.centroid.y > -41.5]
PAT_1869 = GEOM['Patagones']
GEOM['Patagones'] = unary_union(_pat).buffer(0)
RESTO = RESTO.intersection(TERR).buffer(0)
FUERA = PROV.difference(TERR).difference(GEOM['Patagones']).buffer(0)
LINEA = TERR.boundary.difference(PROV.boundary.buffer(0.1))

LAT0 = -34.6
KX = math.cos(math.radians(LAT0))


def proyector(bbox, w, h, pad=0.04):
    x0, y0, x1, y1 = bbox
    sx = (x1 - x0) * KX
    sy = (y1 - y0)
    s = min(w / (sx * (1 + 2 * pad)), h / (sy * (1 + 2 * pad)))
    ox = (w - sx * s) / 2
    oy = (h - sy * s) / 2

    def p(lon, lat):
        return ox + (lon - x0) * KX * s, oy + (y1 - lat) * s
    return p


def path(geom, p, tol=0.0):
    if geom.is_empty:
        return ''
    if tol:
        geom = geom.simplify(tol, preserve_topology=True)
    out = []
    polys = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for poly in polys:
        if poly.geom_type != 'Polygon':
            continue
        for ring in [poly.exterior, *poly.interiors]:
            pts = [p(*c) for c in ring.coords]
            if len(pts) < 4:
                continue
            out.append('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z')
    return ''.join(out)




# ------------------------------------------------------------------ datos por sección
COL = {
    'Dorrego': '#c8102e', 'Las Heras': '#1c3f94', 'López': '#f59e0b', 'J. J. Anchorena': '#8e6bd8',
    'Presidente (no vota)': '#6b6b6b', 'No figura': '#b5b5b5', 'Incorporado después': '#9fb3c8', 'Elección anulada': '#8a7f6a',
    'Sin identificar': '#e9dcc0',
    'LISTA': '#7b1e3a', 'OTRA': '#1f8a83', 'ANUL': '#8a7f6a',
}
CLAVE_GOB = ['Dorrego', 'J. J. Anchorena', 'López', 'Las Heras', 'Presidente (no vota)', 'No figura', 'Incorporado después',
             'Elección anulada', 'Sin identificar']
CLAVE_LIS = ['LISTA', 'OTRA', 'ANUL', 'Sin identificar']
ROT = {'LISTA': 'En la lista «enemigos del Imperio Brasilero»',
       'OTRA': 'Fuera de esa lista',
       'ANUL': 'Electos fuera de la lista, elección anulada',
       'Dorrego': 'Manuel Dorrego', 'Las Heras': 'Juan Gregorio de Las Heras', 'López': 'Vicente López',
       'J. J. Anchorena': 'Juan José Anchorena', 'Presidente (no vota)': 'Presidía la Sala (no vota)',
       'No figura': 'No figura en la votación', 'Incorporado después': 'Incorporado después del 12 de agosto', 'Elección anulada': 'San Nicolás: elección anulada, sin incorporar',
       'Sin identificar': 'Banca sin identificar'}

por_secc = {s: [] for s in SECC}
sin_secc = []
for e in ELECTOS:
    anul = e['voto_gobernador'] == 'Elección anulada'
    e['lista'] = 'ANUL' if anul else ('LISTA' if e['en_lista_N1103'] == 'si' else 'OTRA')
    e['dudosa'] = e['certeza_seccion'] in ('inferida', 'dudosa')
    (por_secc[e['seccion']] if e['seccion'] in por_secc else sin_secc).append(e)
n_ident = sum(len(v) for v in por_secc.values())
n_vacias = 47 - n_ident - len(sin_secc)
assert n_vacias >= 0

VOTOS_SN = leer('san_nicolas_1827.csv')


def mix(hexc, t):
    """t=1 color pleno, t=0 blanco."""
    r, g_, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % tuple(round(255 + (c - 255) * t) for c in (r, g_, b))


def estado(s, modo):
    ee = por_secc[s]
    nb = NB[s]
    if not ee:
        return dict(fill=COL['Sin identificar'], pat=None)
    anul = all(e['lista'] == 'ANUL' for e in ee)
    if anul:
        return dict(fill=COL['ANUL'], pat='anul')
    if modo == 'lis':
        a = sum(e['lista'] == 'LISTA' for e in ee)
        b = len(ee) - a
        if a == b:
            fill, pat = None, 'empate'
        else:
            k = 'LISTA' if a > b else 'OTRA'
            fill, pat = mix(COL[k], 0.45 + 0.55 * max(a, b) / len(ee)), None
    else:
        ev = [e for e in ee if e['voto_gobernador'] != 'Incorporado después']
        if not ev:   # nadie de la sección estaba en la Sala el 12 de agosto
            fill, pat = COL['Incorporado después'], None
        else:
            d = sum(e['voto_gobernador'] == 'Dorrego' for e in ev)
            share = d / nb if s == 'Ciudad' else d / len(ev)
            fill, pat = mix(COL['Dorrego'], 0.45 + 0.55 * share), None
    if len(ee) < nb:
        pat = pat or 'parcial'
    return dict(fill=fill, pat=pat)


def votos(e):
    v = e.get('votos_cronica68') or e.get('votos_N1114')
    if e['seccion'] == 'Ciudad' and e['votos_N1114'] and e['votos_cronica68'] and e['votos_N1114'] != e['votos_cronica68']:
        return f"{e['votos_N1114']} / {e['votos_cronica68']}"
    return v or ''


def ficha(s):
    b = next(x for x in BANCAS if x['seccion'] == s)
    filas = []
    for e in por_secc[s]:
        marca = ' <span class="warn">(sección inferida)</span>' if e['dudosa'] else ''
        lis = {'LISTA': 'en la lista N1103', 'OTRA': 'fuera de la lista N1103', 'ANUL': 'elección anulada'}[e['lista']]
        filas.append(f"<tr><td><b>{html.escape(e['nombre'])}</b>{marca}<br><span class='nota'>{html.escape(e['voto_gobernador'])} · {lis}</span></td>"
                     f"<td>{votos(e)}</td></tr>")
    falta = NB[s] - len(por_secc[s])
    if falta:
        filas.append(f"<tr><td colspan=2 class='nota'>{falta} banca{'s' if falta > 1 else ''} sin identificar</td></tr>")
    extra = ''
    if s == 'San Nicolás':
        extra = ('<table class="sn"><tr><td></td><td>S. Pedro</td><td>S. Nicolás</td><td>Baradero</td><td>Total</td></tr>'
                 + ''.join(f"<tr><td>{html.escape(r['candidato'])}</td><td>{r['san_pedro']}</td><td>{r['san_nicolas']}</td>"
                           f"<td>{r['baradero']}</td><td><b>{r['total']}</b></td></tr>" for r in VOTOS_SN)
                 + '</table><p class="nota">Galimberti, cuadro 5. La Sala anuló la elección 23 a 7 por la denuncia de coacción del juez de paz de Baradero; '
                   'se repitió el 1 de enero de 1828.</p>')
    pueblos = b['pueblos_decreto'].replace(';', ', ')
    return (f"<b>{html.escape(s)}</b> · {NB[s]} banca{'s' if NB[s] > 1 else ''}<p class='nota'>Pueblos del decreto: {html.escape(pueblos)}</p>"
            f"<table>{''.join(filas)}</table>{extra}<p class='nota'>{html.escape(b['nota'])}</p>")


# ------------------------------------------------------------------ SVG de los mapas
W, H = 760, 640
bb_main = unary_union([GEOM[s] for s in SECC if s not in ('Patagones',)] + [TERR]).bounds
bb_main = (bb_main[0] - 0.15, bb_main[1] - 0.1, bb_main[2] + 0.25, bb_main[3] + 0.1)
P_MAIN = proyector(bb_main, W, H)
bb_city = (-58.62, -34.78, -58.20, -34.42)
P_CITY = proyector(bb_city, 250, 230, pad=0.0)
bb_pat = unary_union([GEOM['Patagones'], PAT_1869]).bounds
P_PAT = proyector(bb_pat, 140, 175, pad=0.06)


def linea(geom, p, tol=0.0):
    if tol:
        geom = geom.simplify(tol)
    ls = geom.geoms if hasattr(geom, 'geoms') else [geom]
    return ''.join('M' + 'L'.join('%.1f,%.1f' % p(*c) for c in l.coords) for l in ls if l.geom_type == 'LineString' and len(l.coords) > 1)


def capa(p, modo, tol, clip_id, caja):
    # solo lo que entra en el recuadro (más un margen): la provincia de 1869 llega a Patagones
    x0, y0, x1, y1 = caja
    mx, my = (x1 - x0) * .8, (y1 - y0) * .3
    ver = shapely.box(x0 - mx, y0 - my, x1 + mx, y1 + my)
    fuera, resto, prov = (g_.intersection(ver) for g_ in (FUERA, RESTO, PROV))
    out = [f'<path class="fuera" d="{path(fuera, p, tol * 2)}"/>', f'<path class="resto" d="{path(resto, p, tol)}"/>']
    for i, s in enumerate(SECC):
        st = estado(s, modo)
        fill = st['fill'] if st['fill'] else f'url(#emp-{modo})'
        gid = f'g-{clip_id}-{i}'   # el trazado va una vez; la sección y su rayado lo usan con <use>
        out.append(f'<defs><path id="{gid}" d="{path(GEOM[s], p, tol)}"/></defs>'
                   f'<use href="#{gid}" class="u" data-s="{html.escape(s)}" fill="{fill}"/>')
        if st['pat'] in ('parcial', 'anul'):
            out.append(f'<use href="#{gid}" class="hatch" fill="url(#{st["pat"]}-{modo})"/>')
    out.append(f'<path class="cont" d="{path(prov, p, tol)}"/>')
    out.append(f'<path class="front" d="{linea(LINEA, p, tol)}"/>')
    return f'<g clip-path="url(#{clip_id})">' + ''.join(out) + '</g>'


def etiquetas(p, nombres, size):
    out = []
    for s in nombres:
        c = GEOM[s].representative_point()
        x, y = p(c.x, c.y)
        out.append(f'<text class="lab" x="{x:.0f}" y="{y:.0f}" font-size="{size}">{html.escape(s)}</text>'
                   f'<text class="lab n" x="{x:.0f}" y="{y + size + 2:.0f}" font-size="{size - 2}">{NB[s]}</text>')
    return ''.join(out)


def mapa(modo):
    defs = f'''<defs>
<pattern id="parcial-{modo}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2.2" height="7" fill="rgba(255,255,255,.55)"/></pattern>
<pattern id="anul-{modo}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="1.6" height="6" fill="rgba(255,255,255,.7)"/></pattern>
<pattern id="emp-{modo}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="{mix(COL['LISTA'], .75)}"/><rect width="5" height="10" fill="{mix(COL['OTRA'], .75)}"/></pattern>
<clipPath id="cm-{modo}"><rect width="{W}" height="{H}"/></clipPath>
<clipPath id="cc-{modo}"><rect width="250" height="230"/></clipPath>
<clipPath id="cp-{modo}"><rect width="140" height="175"/></clipPath>
</defs>'''
    main = capa(P_MAIN, modo, 0.004, f'cm-{modo}', bb_main)
    labs = etiquetas(P_MAIN, ['San Nicolás', 'Arrecifes', 'Pilar', 'Luján', 'Morón', 'Quilmes', 'Chascomús'], 13)
    x1, y1 = P_MAIN(bb_city[0], bb_city[3])
    x2, y2 = P_MAIN(bb_city[2], bb_city[1])
    marco = f'<rect class="mk" x="{x1:.0f}" y="{y1:.0f}" width="{x2 - x1:.0f}" height="{y2 - y1:.0f}"/>'
    city = (f'<g transform="translate({W - 262},8)"><rect class="ins" width="250" height="230"/>{capa(P_CITY, modo, 0.0005, f"cc-{modo}", bb_city)}'
            f'{etiquetas(P_CITY, ["Ciudad", "Flores", "San Isidro"], 11)}<text class="tit" x="6" y="15">Ciudad y alrededores</text></g>')
    pat = (f'<g transform="translate(12,{H - 187})"><rect class="ins" width="140" height="175"/>{capa(P_PAT, modo, 0.003, f"cp-{modo}", bb_pat)}'
           f'<text class="tit" x="6" y="15">Patagones (1 banca)</text></g>')
    return (f'<svg viewBox="0 0 {W} {H}" class="mapa" id="svg-{modo}" role="img" aria-label="Mapa de las secciones electorales de 1827"'
            f'{"" if modo == "lis" else " hidden"}>{defs}{main}{marco}{labs}{city}{pat}</svg>')


# ------------------------------------------------------------------ hemiciclo
def asientos(n=47, filas=4, r0=70, r1=190):
    radios = [r0 + (r1 - r0) * i / (filas - 1) for i in range(filas)]
    tot = sum(radios)
    cuenta = [round(n * r / tot) for r in radios]
    cuenta[-1] += n - sum(cuenta)
    pts = []
    for r, c in zip(radios, cuenta):
        for j in range(c):
            a = math.pi * (1 - j / (c - 1)) if c > 1 else math.pi / 2
            pts.append((a, r))
    pts.sort(key=lambda t: (-t[0], t[1]))
    return [(210 + r * math.cos(a), 205 - r * math.sin(a)) for a, r in pts]


def bancas_modo(modo):
    filas = []
    for e in ELECTOS:
        k = e['voto_gobernador'] if modo == 'gob' else e['lista']
        filas.append((k, e['nombre'], e['seccion']))
    for _ in range(n_vacias):
        filas.append(('Sin identificar', 'Banca de campaña sin identificar', 'Pilar, Arrecifes, Chascomús o Quilmes'))
    orden = CLAVE_GOB if modo == 'gob' else CLAVE_LIS
    filas.sort(key=lambda f: orden.index(f[0]))
    assert len(filas) == 47
    return filas


def hemiciclo(modo):
    out = []
    for (x, y), (k, nom, sec) in zip(asientos(), bancas_modo(modo)):
        t = html.escape(f'{nom} · {sec}')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10.5" fill="{COL[k]}" data-t="{t}"/>')
    return (f'<svg viewBox="0 0 420 222" class="hemi" id="hemi-{modo}"{"" if modo == "lis" else " hidden"}>{"".join(out)}'
            f'<text x="210" y="196" text-anchor="middle" class="hn">47</text>'
            f'<text x="210" y="214" text-anchor="middle" class="hs">representantes</text></svg>')


def barras(modo):
    filas = bancas_modo(modo)
    orden = CLAVE_GOB if modo == 'gob' else CLAVE_LIS
    out = []
    for k in orden:
        n = sum(f[0] == k for f in filas)
        if n:
            out.append(f'<div class="bar"><span class="sw" style="background:{COL[k]}"></span><span class="t">{ROT[k]}</span>'
                       f'<span class="v"><b>{n}</b></span><div class="track"><i style="width:{100 * n / 47:.1f}%;background:{COL[k]}"></i></div></div>')
    return f'<div id="res-{modo}"{"" if modo == "lis" else " hidden"}>' + ''.join(out) + '</div>'


def fmt(x):
    return f'{round(x):,}'.replace(',', '.')


def voto_popular(modo):
    """Votantes equivalentes por agrupación: votos de los electos de cada una sumados y divididos por las bancas
    de la sección (cada votante votaba por tantos nombres como bancas). Sólo secciones con votos publicados."""
    por = {}
    for e in ELECTOS:
        v = e['votos_N1114'] or e['votos_cronica68']
        if not v or e['lista'] == 'ANUL':
            continue
        k = e['voto_gobernador'] if modo == 'gob' else e['lista']
        d = por.setdefault(e['seccion'], {})
        d[k] = d.get(k, 0) + int(v) / NB[e['seccion']]
    tot = {}
    for d in por.values():
        for k, v in d.items():
            tot[k] = tot.get(k, 0) + v
    T = sum(tot.values())
    orden = CLAVE_GOB if modo == 'gob' else CLAVE_LIS
    out = []
    for k in orden:
        if k in tot:
            out.append(f'<div class="bar"><span class="sw" style="background:{COL[k]}"></span><span class="t">{ROT[k]}</span>'
                       f'<span class="v"><b>{f'{100 * tot[k] / T:.1f}'.replace('.', ',')} %</b> · {fmt(tot[k])}</span>'
                       f'<div class="track"><i style="width:{100 * tot[k] / T:.1f}%;background:{COL[k]}"></i></div></div>')
    cab = ''.join(f'<td>{"Dorrego" if k == "Dorrego" else ("Lista" if k == "LISTA" else ("Fuera" if k == "OTRA" else "Otros"))}</td>'
                  for k in (('Dorrego', 'OTROS') if modo == 'gob' else ('LISTA', 'OTRA')))
    filas = []
    for s in SECC:
        if s not in por:
            continue
        d = por[s]
        if modo == 'gob':
            a, b = d.get('Dorrego', 0), sum(v for k, v in d.items() if k != 'Dorrego')
        else:
            a, b = d.get('LISTA', 0), d.get('OTRA', 0)
        filas.append(f'<tr><td>{html.escape(s)}</td><td>{fmt(a)}</td><td>{fmt(b)}</td></tr>')
    if modo == 'lis':
        sn = {r['candidato']: int(r['total']) for r in VOTOS_SN}
        a, b = sn['Francisco Benítez'] / 2, (sn['Valentín San Martín'] + sn['Miguel Rivera']) / 2
        filas.append(f'<tr class="an"><td>San Nicolás (anulada)</td><td>{fmt(a)}</td><td>{fmt(b)}</td></tr>')
    tabla = (f'<table class="vp"><tr class="h"><td>Sección</td>{cab}</tr>{"".join(filas)}'
             f'<tr class="w"><td>Total</td>'
             + (f'<td>{fmt(tot.get("Dorrego", 0))}</td><td>{fmt(T - tot.get("Dorrego", 0))}</td>' if modo == 'gob'
                else f'<td>{fmt(tot.get("LISTA", 0))}</td><td>{fmt(tot.get("OTRA", 0))}</td>')
             + '</tr></table>')
    nota = ('<p class="nota">Estimación. Suma de los votos de los electos de cada agrupación dividida por las bancas de la sección: '
            'cada votante elegía tantos nombres como bancas había (24 en la ciudad, 2 en cada sección de campaña). Sólo cuentan las '
            'secciones con votos publicados (ciudad, Flores, San Isidro, Morón y Luján); faltan Pilar, Arrecifes, Chascomús, Quilmes y '
            'Patagones. Los votos de los candidatos que no salieron electos no se publicaron, salvo en San Nicolás, que no entra '
            'en el total por estar anulada.</p>')
    if modo == 'gob':
        nota += ('<p class="nota">Cada electo lleva sus votos del 22 de julio a lo que votó el 12 de agosto: es el voto popular '
                 'de quienes después eligieron a Dorrego, no un voto por Dorrego.</p>')
    return f'<div id="vp-{modo}"{"" if modo == "lis" else " hidden"}>{"".join(out)}{tabla}{nota}</div>'


# ------------------------------------------------------------------ textos
n_dor = sum(e['voto_gobernador'] == 'Dorrego' for e in ELECTOS)
TXT = {
    'lis': dict(
        sub='Veinte de los 24 electos por la ciudad figuran en la lista «Unos enemigos del Imperio Brasilero» '
            '(<i>Gaceta Mercantil</i> 1103, 11 de julio), la única que proponía también candidatos por la campaña. '
            'El mapa muestra, por sección, cuántos electos estaban en ella.',
        met=f'<span>Bancas <b>47</b></span><span>Identificadas <b>{47 - n_vacias}</b></span><span>Ciudad en la lista <b>20 de 24</b></span>',
        notas='<p class="nota">Ciudad: en la lista y no electos, Tomás Anchorena, Florencio Ramírez, Juan José Cernadas y Manuel Escalada; '
              'electos fuera de ella, Felipe Arana, Pereyra Lucena, Tomás Aguiar y Bernabé Escalada. La lista rivadaviana «Unos Provincianos» '
              '(1104) colocó a Braulio Costa en la ciudad y a Valentín San Martín en San Nicolás, donde la elección se anuló.</p>'
              '<p class="nota">Tono: proporción de electos de cada lado entre los identificados. Rayado blanco: faltan bancas por identificar. '
              'Rayado cruzado: elección anulada.</p>'),
    'gob': dict(
        sub=f'Sesión de la Junta de Representantes del 12 de agosto de 1827, votación nominal: Manuel Dorrego {n_dor}; '
            'Las Heras 2 (Álzaga y Martínez); López 1 (Maza); Juan José Anchorena 1 (Costa). Los que votaron a Dorrego van juntos, como una lista.',
        met=f'<span>Dorrego <b>{n_dor}</b></span><span>Otros <b>4</b></span><span>Presentes <b>36</b></span>',
        notas='<p class="nota">Votaron a Dorrego tres diputados de campaña cuya sección no publican los diarios: Achega, Otamendi y Rivas. '
              'Están en la Sala pero no en el mapa. Haedo y Bernabé Escalada se habían incorporado el 8 de agosto y no figuran en la votación. '
              'La elección de Navarro se devolvió a la mesa central de Chascomús (sesión del 8).</p>'
              '<p class="nota">Incorporados después, sin voto el 12 de agosto: Luis Saavedra y José María Baudriz (Arrecifes; Baudriz '
              'renunció el 2 de octubre) y José María Rojas (Patagones). Desde fines de septiembre también se sientan Anchorena y Viola, '
              'de sección desconocida (¿Nicolás Anchorena, de la lista por Chascomús?): no se cuentan.</p>'
              '<p class="nota">Tono en la ciudad: votos por Dorrego sobre las 24 bancas; en la campaña, sobre los electos identificados.</p>'),
}
MODO_NOMBRE = {'lis': 'por lista', 'gob': 'voto por gobernador'}

SIN = ''.join(f"<div class='key'><span class='sw' style='background:{COL['Dorrego']}'></span>{html.escape(e['nombre'])} "
              f"<span class='nota'>· {html.escape(e['nota'])}</span></div>" for e in sin_secc)

FUENTES = ('<p><b>Diarios</b>: <i>La Gaceta Mercantil</i>, números 1096 a 1134 (2 de julio a 18 de agosto de 1827), y <i>Crónica Política y '
           'Literaria de Buenos Aires</i>, números 46 a 80 (5 de julio a 18 de agosto), Hemeroteca Digital de la Biblioteca Nacional '
           'Mariano Moreno. Decreto y tabla de bancas: <i>Gaceta</i> 1102. Listas: <i>Gaceta</i> 1103 a 1110. Ciudad, Flores y San Isidro: '
           '<i>Gaceta</i> 1114 y <i>Crónica</i> 59-60. Morón y Luján: <i>Crónica</i> 68 (3 de agosto), que también enumera las secciones '
           'que faltaban. Quilmes: «no ha habido eleccion, por no haberse reunido los electores» (<i>Crónica</i> 59). Sesiones preparatorias: '
           '<i>Gaceta</i> 1123-1128, <i>Crónica</i> 71, 73, 74 y 76. Gobernador: <i>Gaceta</i> 1131 y <i>Crónica</i> 77.</p>'
           '<p><b>Diario de Sesiones</b> de la H. Junta de Representantes, tomo 2 (Hemeroteca Digital de la BNMM; el tomo 1, de agosto y '
           'septiembre, no está digitalizado): número 22 (renuncia de Baudriz, Arrecifes), 23 (acta de Patagones, José María Rojas, '
           'sin cifras), 29 (incorporación de Saavedra, Arrecifes) y 21 y 29 (elección complementaria de dos representantes por la '
           'ciudad, anulada por la mesa central el 15 de octubre, sin votos publicados). El sumario de Baradero (San Nicolás) va en '
           'los números 20, 23, 24 y 32.</p>'
           '<p><b>San Nicolás</b>: votos por pueblo de Galimberti (UNLP, cuadro 5, del Diario de Sesiones). La <i>Crónica</i> 63 publica una '
           'carta del 23 de julio sobre la disputa entre voto verbal y papeletas en San Nicolás.</p>'
           '<p><b>Votos de la ciudad</b>: la <i>Gaceta</i> 1114 y la <i>Crónica</i> 68 difieren en tres electos (Maza 881/911, del Pino '
           '970/980, José María Escalada 963/873); la ficha muestra las dos cifras. San Isidro: la <i>Crónica</i> 60 dice José Pacheco; '
           'la 68 y la <i>Gaceta</i>, Jorge.</p>'
           '<p><b>Secciones inferidas</b>: Arraga (Pilar) y Viamont (Chascomús) se sientan en la Sala y la lista de la <i>Gaceta</i> 1103 '
           'los proponía por esas secciones; no se vio el acta. Wright (Quilmes) es dudoso: Quilmes no votó el 22 de julio y él se '
           'incorporó el 8 de agosto con las últimas actas de campaña.</p>'
           '<p><b>Geometría</b>: partidos del censo de 1869 (Rodríguez y De Grande, CEUR-CONICET, CC BY 2.5 Argentina) agrupados en las '
           'secciones del decreto. Los partidos creados después de 1827 van con el que los contenía (Belgrano con San Isidro; Merlo, '
           'Moreno y San Martín con Morón; Zárate con Pilar; Chivilcoy y Suipacha con Luján; Ramallo con San Nicolás; Barracas al Sud y '
           'La Paz con Quilmes). Monsalvo, sobre la costa atlántica, aparece separado del resto de la sección de Chascomús. La ciudad es la '
           'de 1869. Límites aproximados.</p>'
           '<p><b>Frontera</b>: la línea de 1826 sale de un mapa escolar del avance de la frontera (aportado por el usuario, autor sin '
           'identificar), georreferenciado con ocho ciudades (ajuste afín, residuos de 6 km o menos), unida a la jurisdicción de Buenos '
           'Aires de 1788 del HGIS de las Indias (CC BY-NC-SA), que completa el noreste. Las secciones se recortan a esa línea; en gris '
           'oscuro, los partidos de 1869 dentro de la frontera que no tenían sección en el decreto; en gris claro, la tierra de la provincia '
           'de 1869 que estaba fuera. Patagones, enclave, con su partido de 1869. Es una línea de época de escala escolar, no un trazado '
           'documental.</p>')

FICHAS = {s: ficha(s) for s in SECC}

CSS = '''
:root{color-scheme:light;
 --space-2xs:4px;--space-xs:8px;--space-sm:12px;--space-md:16px;--space-lg:24px;--space-xl:40px;--gutter:40px;
 --text-xs:.8125rem;--text-sm:.875rem;--text-md:1rem;--text-display:clamp(1.7rem,3.2vw,2.6rem);
 --color-paper:oklch(99.5% .003 100);--color-paper-2:oklch(97% .004 100);--color-paper-3:oklch(94% .006 100);
 --color-ink:oklch(16% 0 0);--color-ink-2:oklch(28% 0 0);--color-muted:oklch(44% 0 0);
 --color-rule:oklch(89% .004 100);--color-accent:oklch(50% .095 188);--color-accent-ink:oklch(99.5% .003 100);--color-focus:oklch(50% .095 188);
 --font-display:"Epilogue",ui-sans-serif,system-ui,sans-serif;--radius:10px;--radius-pill:999px;
 --resto:#d9d6cf;--fuera:#efede8;--borde:#ffffff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;
 --color-paper:oklch(17% .004 250);--color-paper-2:oklch(21% .005 250);--color-paper-3:oklch(25% .006 250);
 --color-ink:oklch(95% 0 0);--color-ink-2:oklch(85% 0 0);--color-muted:oklch(72% 0 0);--color-rule:oklch(32% .006 250);
 --color-accent:oklch(74% .1 188);--color-accent-ink:oklch(17% .004 250);--color-focus:oklch(74% .1 188);
 --resto:#3a3b3e;--fuera:#26272a;--borde:oklch(17% .004 250)}}
:root[data-theme="dark"]{color-scheme:dark;
 --color-paper:oklch(17% .004 250);--color-paper-2:oklch(21% .005 250);--color-paper-3:oklch(25% .006 250);
 --color-ink:oklch(95% 0 0);--color-ink-2:oklch(85% 0 0);--color-muted:oklch(72% 0 0);--color-rule:oklch(32% .006 250);
 --color-accent:oklch(74% .1 188);--color-accent-ink:oklch(17% .004 250);--color-focus:oklch(74% .1 188);
 --resto:#3a3b3e;--fuera:#26272a;--borde:oklch(17% .004 250)}
*,*::before,*::after{box-sizing:border-box}
html,body{overflow-x:clip}
::selection{background:var(--color-accent);color:var(--color-accent-ink)}
body{margin:0;background:var(--color-paper);color:var(--color-ink);font-family:var(--font-display);font-size:var(--text-md);line-height:1.5;-webkit-font-smoothing:antialiased}
:focus-visible{outline:2px solid var(--color-focus);outline-offset:3px}
a{color:inherit;text-underline-offset:.16em}
button{font:inherit}
.tope{position:sticky;top:0;z-index:300;background:var(--color-paper);border-bottom:1px solid var(--color-rule)}
.fila{display:flex;align-items:center;gap:var(--space-sm) var(--space-md);flex-wrap:wrap;min-height:64px;padding:var(--space-xs) var(--gutter)}
.marca{font-weight:700;letter-spacing:-.02em;white-space:nowrap;margin-right:var(--space-xs)}
.pill{border:1px solid var(--color-rule);background:transparent;color:var(--color-ink);border-radius:var(--radius-pill);padding:var(--space-2xs) var(--space-sm);min-height:32px;font-size:var(--text-sm);cursor:pointer;transition:background var(--dur-short,180ms)}
.pill:hover{background:var(--color-paper-2)}.pill:active{background:var(--color-paper-3)}
a.pill{text-decoration:none;display:inline-flex;align-items:center}
.pill.on{background:var(--color-ink);color:var(--color-paper);border-color:var(--color-ink)}
.seg{display:inline-flex;gap:var(--space-2xs)}
#tema{margin-left:auto}
.cab{padding:var(--space-lg) var(--gutter) var(--space-sm)}
h1{margin:0;font-size:var(--text-display);font-weight:700;letter-spacing:-.035em;line-height:1.04;text-wrap:balance}
h1 .y{color:var(--color-accent)}
.sub{color:var(--color-muted);font-size:var(--text-sm);margin-top:var(--space-xs);max-width:80ch}
main{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:var(--space-lg);padding:0 var(--gutter) var(--space-xl)}
#mapa{min-width:0}
svg{width:100%;height:auto;display:block}
svg[hidden],div[hidden]{display:none}
.mapa{max-height:84vh}
.mapa .resto{fill:var(--resto);stroke:var(--borde);stroke-width:.5}
.mapa .fuera{fill:var(--fuera);stroke:none}
.front{fill:none;stroke:var(--color-ink-2);stroke-width:1.6;stroke-dasharray:5 3;pointer-events:none}
.u{stroke:var(--borde);stroke-width:1.1;cursor:pointer}
.u:hover,.u.sel{stroke:var(--color-ink);stroke-width:2.2}
.hatch{pointer-events:none}
.cont{fill:none;stroke:var(--color-ink-2);stroke-width:.8;pointer-events:none}
.ins{fill:var(--color-paper);stroke:var(--color-rule)}
.mk{fill:none;stroke:var(--color-ink-2);stroke-width:1;stroke-dasharray:3 2}
.tit{font:600 11px var(--font-display);fill:var(--color-ink)}
.lab{font-family:var(--font-display);font-weight:600;text-anchor:middle;fill:#1d1b18;paint-order:stroke;stroke:rgba(255,255,255,.8);stroke-width:3px;pointer-events:none}
.lab.n{font-weight:400}
.hemi{max-width:360px;margin:0 auto}
.hemi circle{stroke:var(--color-paper);stroke-width:1.5}
.hemi circle:hover{stroke:var(--color-ink)}
.hemi .hn{font:700 30px var(--font-display);fill:var(--color-ink)}.hemi .hs{font:13px var(--font-display);fill:var(--color-muted)}
aside{font-size:var(--text-sm);line-height:1.45;min-width:0}
aside h2{font-size:var(--text-sm);color:var(--color-muted);margin:var(--space-lg) 0 var(--space-xs);font-weight:600;padding-top:var(--space-sm);border-top:1px solid var(--color-rule)}
aside h2:first-child{margin-top:0}
.met{display:flex;gap:var(--space-2xs) var(--space-md);flex-wrap:wrap;color:var(--color-muted);font-variant-numeric:tabular-nums}.met b{color:var(--color-ink);font-weight:600}
.bar{display:grid;grid-template-columns:14px minmax(0,1fr) auto;gap:var(--space-xs);align-items:center;margin:var(--space-2xs) 0}
.sw{width:14px;height:14px;border-radius:3px;flex:none}
.bar .t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar .v{font-variant-numeric:tabular-nums;color:var(--color-muted)}.bar .v b{color:var(--color-ink)}
.track{grid-column:2/4;height:4px;background:var(--color-rule);border-radius:2px;margin:0 0 var(--space-2xs)}.track i{display:block;height:4px;border-radius:2px}
.key{display:flex;align-items:center;gap:var(--space-xs);margin:var(--space-2xs) 0;color:var(--color-muted)}
.key .sw.r{background:repeating-linear-gradient(45deg,#7b1e3a 0 4px,#fff 4px 6px)}
.key .sw.a{background:repeating-linear-gradient(-45deg,#8a7f6a 0 3px,#fff 3px 5px)}
#ficha{border:1px solid var(--color-rule);border-radius:var(--radius);padding:var(--space-sm) var(--space-md);background:var(--color-paper-2)}
#ficha table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums;margin:var(--space-2xs) 0}
#ficha td{padding:3px 0;vertical-align:top}#ficha td+td{text-align:right;padding-left:var(--space-xs);white-space:nowrap}
table.vp{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums;margin:var(--space-xs) 0}
table.vp td{padding:2px 0;border-bottom:1px solid var(--color-rule)}table.vp td+td{text-align:right}
table.vp tr.h td{color:var(--color-muted)}table.vp tr.w td{font-weight:700;border-bottom:0}table.vp tr.an td{color:var(--color-muted);font-style:italic}
#ficha table.sn td{text-align:right;padding-left:var(--space-xs)}#ficha table.sn td:first-child{text-align:left;padding-left:0}
.nota{color:var(--color-muted);font-size:var(--text-xs);margin:var(--space-2xs) 0;text-wrap:pretty}
.warn{color:var(--color-accent);font-weight:400}
#tip{position:fixed;pointer-events:none;background:var(--color-ink);color:var(--color-paper);font-size:12.5px;padding:4px 8px;border-radius:6px;display:none;z-index:400}
.pie{border-top:1px solid var(--color-rule);padding:var(--space-lg) var(--gutter) var(--space-xl);color:var(--color-muted);font-size:var(--text-sm)}
.pie p{max-width:80ch;margin:0 0 var(--space-xs)}
@media (max-width:60rem){:root{--gutter:16px}main{grid-template-columns:minmax(0,1fr)}#tema{margin-left:0}}
@media (max-width:40rem){.tope{position:static}.marca{width:100%}}
@media (prefers-reduced-motion:reduce){*{transition-duration:.01ms!important}}
'''

JS = '''(()=>{
const F=%s,T=%s;const $=id=>document.getElementById(id);const tip=$("tip");
let modo="lis";
function poner(m){modo=m;
 document.querySelectorAll("[data-m]").forEach(b=>{const on=b.dataset.m===m;b.classList.toggle("on",on);b.setAttribute("aria-pressed",on)});
 ["svg","hemi","res","vp"].forEach(p=>["lis","gob"].forEach(k=>{$(p+"-"+k).toggleAttribute("hidden",k!==m)}));
 $("hModo").textContent=T[m].nombre;$("hSub").innerHTML=T[m].sub;$("met").innerHTML=T[m].met;$("notas").innerHTML=T[m].notas;
 $("sinsec").toggleAttribute("hidden",m!=="gob");
 history.replaceState(null,"",m==="gob"?"#gob":"#lis");}
document.querySelectorAll("[data-m]").forEach(b=>b.onclick=()=>poner(b.dataset.m));
const ver=(e,t)=>{tip.style.display="block";tip.textContent=t;tip.style.left=e.clientX+12+"px";tip.style.top=e.clientY+12+"px"};
document.querySelectorAll(".u").forEach(p=>{
 p.onclick=()=>{document.querySelectorAll(".u.sel").forEach(x=>x.classList.remove("sel"));
  document.querySelectorAll('.u[data-s="'+p.dataset.s+'"]').forEach(x=>x.classList.add("sel"));$("ficha").innerHTML=F[p.dataset.s]};
 p.onmouseenter=()=>{$("ficha").innerHTML=F[p.dataset.s]};
 p.onmousemove=e=>ver(e,p.dataset.s);p.onmouseleave=()=>tip.style.display="none"});
document.querySelectorAll(".hemi circle").forEach(c=>{c.onmousemove=e=>ver(e,c.dataset.t);c.onmouseleave=()=>tip.style.display="none"});
const oscuro=()=>{const r=document.documentElement;return r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches};
const rotTema=()=>{$("tema").textContent=oscuro()?"Modo claro":"Modo oscuro"};
$("tema").onclick=()=>{const r=document.documentElement;r.dataset.theme=oscuro()?"light":"dark";try{localStorage.setItem("tema",r.dataset.theme)}catch(_){};rotTema()};rotTema();
poner(location.hash==="#gob"?"gob":"lis");
})();''' % (json.dumps(FICHAS, ensure_ascii=False),
            json.dumps({m: dict(nombre=MODO_NOMBRE[m], **TXT[m]) for m in TXT}, ensure_ascii=False))

page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Buenos Aires 1827</title>
<meta name="description" content="La elección de la Junta de Representantes de Buenos Aires del 22 de julio de 1827 por sección, y cómo votó la Sala al gobernador Manuel Dorrego.">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://azha2005.github.io/257arg/buenosaires1827/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Atlas electorales argentinos">
<meta property="og:locale" content="es_AR">
<meta property="og:url" content="https://azha2005.github.io/257arg/buenosaires1827/">
<meta property="og:title" content="Buenos Aires, 1827: la Junta que eligió a Dorrego">
<meta property="og:description" content="La elección de la Junta de Representantes del 22 de julio de 1827 por sección, el voto popular estimado y cómo votó la Sala a Manuel Dorrego.">
<meta property="og:image" content="https://azha2005.github.io/257arg/buenosaires1827/portada.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Mapa de la provincia de Buenos Aires en 1827 con las secciones electorales coloreadas por la lista de sus electos, la frontera de 1826 y el hemiciclo de la Sala de 47 bancas">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Buenos Aires, 1827: la Junta que eligió a Dorrego">
<meta name="twitter:description" content="La elección de la Junta de Representantes del 22 de julio de 1827 por sección, el voto popular estimado y cómo votó la Sala a Manuel Dorrego.">
<meta name="twitter:image" content="https://azha2005.github.io/257arg/buenosaires1827/portada.png">
<meta name="twitter:image:alt" content="Mapa de la provincia de Buenos Aires en 1827 con las secciones electorales coloreadas por la lista de sus electos, la frontera de 1826 y el hemiciclo de la Sala de 47 bancas">
<meta name="theme-color" content="#fcfcfa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141619" media="(prefers-color-scheme: dark)">
<link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;600;700&display=swap" rel="stylesheet">
<script>try{{const t=localStorage.getItem("tema");if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<style>{CSS}</style>
</head>
<body>
<header class="tope"><div class="fila">
 <a class="pill" href="https://azha2005.github.io/257arg/">Todos los atlas</a>
 <span class="marca">Buenos Aires, 1827</span>
 <span class="seg"><button class="pill on" data-m="lis" aria-pressed="true">Por lista</button><button class="pill" data-m="gob" aria-pressed="false">Voto por gobernador</button></span>
 <button class="pill" id="tema" aria-label="Cambiar entre modo claro y oscuro">Modo oscuro</button>
</div></header>
<div class="cab">
 <h1>Junta de Representantes de Buenos Aires, <span class="y">1827</span>, <span id="hModo"></span></h1>
 <p class="sub" id="hSub"></p>
</div>
<main>
 <div id="mapa">{mapa('lis')}{mapa('gob')}</div>
 <aside>
  <h2>La Sala</h2>
  <div class="met" id="met"></div>
  {hemiciclo('lis')}{hemiciclo('gob')}
  {barras('lis')}{barras('gob')}
  <h2>Voto popular estimado</h2>
  {voto_popular('lis')}{voto_popular('gob')}
  <h2>Referencias</h2>
  <div class="key"><span class="sw r"></span>Rayado blanco: faltan bancas por identificar</div>
  <div class="key"><span class="sw a"></span>Elección anulada (San Nicolás)</div>
  <div class="key"><span class="sw" style="background:{COL['Sin identificar']}"></span>Sin electos identificados</div>
  <div class="key"><span class="sw" style="background:var(--resto)"></span>Dentro de la frontera, sin sección en el decreto</div>
  <div class="key"><span class="sw" style="background:var(--fuera)"></span>Fuera de la frontera de 1826 (provincia de 1869)</div>
  <div class="key"><svg width="22" height="10" aria-hidden="true"><path class="front" d="M1,5L21,5"/></svg>Frontera de 1826, aproximada</div>
  <div id="sinsec" hidden><h2>En la Sala, sin sección conocida</h2>{SIN}</div>
  <h2>Sección</h2>
  <div id="ficha"><span class="nota">Pasá el cursor o tocá una sección del mapa.</span></div>
  <h2>Notas</h2>
  <div id="notas"></div>
 </aside>
</main>
<footer class="pie">{FUENTES}</footer>
<div id="tip"></div>
<script>{JS}</script>
</body>
</html>'''

(HERE / 'atlas_1827.html').write_text(page, encoding='utf-8')
control = {
    'bancas': NB, 'identificados_con_seccion': n_ident, 'sin_seccion': len(sin_secc), 'bancas_sin_identificar': n_vacias,
    'gobernador': {k: sum(e['voto_gobernador'] == k for e in ELECTOS) for k in CLAVE_GOB},
    'lista': {k: sum(e['lista'] == k for e in ELECTOS) for k in ('LISTA', 'OTRA', 'ANUL')},
}
(HERE / 'CONTROL_1827.json').write_text(json.dumps(control, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps(control, ensure_ascii=False))
