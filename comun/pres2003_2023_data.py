"""Presidenciales observadas por departamento; cartel nacional de Wikipedia.

Usa el constructor vigente de diputados, sin alterar sus datos ni geometrías.
python comun/atlas_leg2003_2025.py 2003pres  (una clave por invocación)
"""
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
import copy
import hashlib
import json
import re
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT/'comun'), str(ROOT/'datos/wikileg')]
from leg2003_2025_data import D2P, ALIASES, PROV_ALIASES, BEIGE, GREY, num, dump
from leg2003_2025_geom import description
from names import norm
from parse_wleg import rows

KEYS = ['2003pres', '2007pres', '2011pres', '2015pres', '2015bal', '2019pres', '2023pres', '2023bal']


def read_atlas(path):
    t = path.read_text(encoding='utf8')
    start = t.index('const DATA=') + len('const DATA=')
    return json.JSONDecoder().raw_decode(t[start:])[0]


def candidates(year, bal):
    """Mismas imágenes, proporciones y paleta de los atlas por radio revisados."""
    source = (ROOT/'mapas/mapaAMBA2003radios/atlas_amba2003radios.html' if year == 2003 else
              ROOT/f'mapas/serieAMBA2005_2023radios/atlas_{year}{"bal" if bal else "pres"}.html')
    cand = {c: copy.deepcopy(r) for c, r in read_atlas(source)['candidates'].items()
            if not c.startswith('P_') and c != 'OTR'}
    if year == 2003:
        sys.path.insert(0, str(ROOT/'analisis/escenarios2003'))
        from preparar import CANDIDATOS
        lookup = {a: c for c, _, _, a, _, _ in CANDIDATOS}
        for c, name, _, _, _, color in CANDIDATOS:
            cand.setdefault(c, dict(n=name, base=color, logo=c[:6]))
    elif year == 2007:
        # Sobisch se presentó por MPU, Unión Popular, MAV y MODIN.
        # Cada boleta es una vía del mismo candidato, no candidaturas distintas.
        lookup = {'0134':'FPV', '0059':'CC', '0131':'UNA', '0133':'FREJULI',
                  '0030':'PSA', '0048':'RECR', '0056':'SOB', '0023':'SOB', '0057':'SOB', '0254':'SOB',
                  '0038':'MST', '0014':'PO', '0135':'FITS', '0132':'FRAL',
                  '0060':'MIJD', '0051':'PPR', '0037':'CLP'}
        for c in list(cand):
            if c.startswith('L'): del cand[c]
        for c, name, party, color in [
            ('MST','Vilma Ripoll','Movimiento Socialista de los Trabajadores','#c62828'),
            ('PO','Néstor Pitrola','Partido Obrero','#a60020'),
            ('FITS','José Montes','PTS-MAS-Izquierda Socialista','#db3355'),
            ('FRAL','Luis Ammann','Frente Amplio hacia la Unidad Latinoamericana','#d87526'),
            ('MIJD','Raúl Castells','Movimiento Independiente de Jubilados y Desocupados','#776655'),
            ('PPR','Gustavo Breide Obeid','Partido Popular de la Reconstrucción','#84654f'),
            ('CLP','Juan Ricardo Mussa','Confederación Lealtad Popular','#808080')]:
            cand[c] = dict(n=name, sub=party, base=color, logo=c)
        cand['FREJULI']['n'] = 'Alberto Rodríguez Saá'
    else:
        aliases = {
            'FPV':['frenteparalavictoria'], 'FAP':['frenteamplioprogresista'],
            'UDESO':['unionparaeldesarrollosocial'], 'CF':['compromisofederal' if year < 2019 else 'consensofederal'],
            'FP':['frentepopular'], 'FIT':['frentedeizquierda'], 'CC':['coalicioncivica'],
            'CAM':['cambiemos'], 'UNA':['unidosporunanuevaalternativa'], 'PROG':['progresistas'],
            'FDT':['frentedetodos'], 'JXC':['juntosporelcambio'], 'NOS':['frentenos'], 'UNITE':['uniteporlalibertad'],
            'UP':['unionporlapatria'], 'LLA':['lalibertadavanza'], 'HXNP':['hacemospornuestropais']}
        lookup = {a:c for c in cand for a in aliases[c]}
    for c, r in cand.items():
        r.setdefault('logo', c[:6])
    cand['P_BLA'] = dict(n='Votos en blanco', base='#b5b5b5')
    cand['P_NUL'] = dict(n='Nulos, recurridos e impugnados', base='#8a8a8a')
    return cand, lookup, source


def national_table(year, bal, cand):
    path = ROOT/f'datos/fuentes_leg2003_2025/presidenciales/wpres{year}.txt'
    text = path.read_text(encoding='utf8')
    tables = [b.split('\n|}')[0] for b in text.split('{|')[1:]
              if 'Electores registrados' in b.split('\n|}')[0]]
    rs = rows(tables[1 if bal else 0])
    def metric(fragment):
        matches = [r['votos'] for r in rs if fragment in norm(r['nombre'])]
        assert len(matches) == 1, (year, bal, fragment, matches)
        return matches[0]
    pos = metric('votosafirmativos' if year >= 2019 else 'votospositivos')
    metrics = dict(positivos=pos, blancos=metric('votosenblanco'), dif=metric('votosnulos' if year >= 2019 else 'votosanulados'),
                   total=metric('participacion'), inscriptos=metric('electoresregistrados'))
    if year == 2003:
        from preparar import CANDIDATOS
        totals = {c:n for c, _, _, _, n, _ in CANDIDATOS}
        assert all(n in [r['votos'] for r in rs] for n in totals.values())
    else:
        fragments = {
            2007: {'FPV':'frenteparalavictoria','CC':'coalicioncivica','UNA':'concertacionparaunanacion',
                   'FREJULI':'frentejusticia','PSA':'partidosocialistaautentico','RECR':'recrear', 'SOB':'totalsobisch',
                   'MST':'movimientosocialistadelos','PO':'partidoobrero','FITS':'frentedeizquierdaylos',
                   'FRAL':'frenteampliohaciala','MIJD':'movimientoindependiente','PPR':'partidopopulardelareconstruccion', 'CLP':'confederacionlealtad'},
            2011: {'FPV':'frenteparalavictoria','FAP':'frenteamplioprogresista','UDESO':'unionparaeldesarrollosocial',
                   'CF':'compromisofederal','FP':'frentepopular','FIT':'frentedeizquierda','CC':'coalicioncivica'},
            2015: {'FPV':'frenteparalavictoria','CAM':'cambiemos','UNA':'unidosporunanuevaalternativa',
                   'FIT':'frentedeizquierda','PROG':'progresistas','CF':'compromisofederal'},
            2019: {'FDT':'frentedetodos','JXC':'juntosporelcambio','CF':'consensofederal','FIT':'frentedeizquierda',
                   'NOS':'frentenos','UNITE':'uniteporlalibertad'},
            2023: {'UP':'unionporlapatria','LLA':'lalibertadavanza','JXC':'juntosporelcambio',
                   'HXNP':'hacemos','FIT':'frentedeizquierda'}}
        if bal and year == 2023:
            # La tabla agrega el número de lista después del nombre: rows() lo toma como etiqueta.
            fragments[2023] = {'LLA':'135', 'UP':'134'}
        totals = {c:metric(f) for c, f in fragments[year].items() if c in cand}
    # No corregir silenciosamente inconsistencias editoriales de la tabla.
    discrepancy = sum(totals.values()) - pos
    assert abs(discrepancy) <= 10, (year, bal, 'suma de candidatos', discrepancy)
    return totals, metrics, path, discrepancy


def prepare(key, U):
    assert key in KEYS, key
    year = int(key[:4]); bal = key.endswith('bal')
    folder = ROOT/f'mapas/mapa{key}'; folder.mkdir(exist_ok=True)
    cand, lookup, logo_source = candidates(year, bal)
    totals, metrics, wiki_source, wiki_discrepancy = national_table(year, bal, cand)
    source = ROOT/f'transferencias/circ_{year}{"b" if bal else "p"}.pkl'
    v, e = pd.read_pickle(source)
    v = v.copy()
    v['d'] = v.distrito_id.astype(int).map('{:02d}'.format)
    v['s'] = v.seccion_id.astype(int).map('{:03d}'.format)
    v = v[v.d.isin(D2P) & (v.votos_tipo != 'COMANDO')].copy()
    def mapped(a):
        if year <= 2007: return lookup[str(a).zfill(4)]
        hits = {c for alias, c in lookup.items() if alias in norm(a)}
        assert len(hits) == 1, (key, a, hits)
        return hits.pop()
    v['code'] = [mapped(a) if t == 'POSITIVO' else '' for a, t in zip(v.agrupacion_id, v.votos_tipo)]
    assert v.v.notna().all() and (v.v >= 0).all()
    assert (v.v == v.v.round()).all(), (key, 'votos fraccionarios')
    # Nombres del nomenclador, sin sustituir votos ni padrón por los de diputados.
    if year <= 2007:
        ns = pd.read_csv(ROOT/f'transferencias/secciones_{year}.csv', dtype=str)
        names = {(r.distrito_id.zfill(2), str(int(r.seccion_id)).zfill(3)):r.depto for r in ns.itertuples()}
    else:
        vv, _ = pd.read_pickle(ROOT/f'datos_oficiales/{year}/agregado.pkl')
        names = {(str(int(r.distrito_id)).zfill(2), str(int(r.seccion_id)).zfill(3)):str(r.seccion_nombre)
                 for r in vv[['distrito_id','seccion_id','seccion_nombre']].dropna().drop_duplicates().itertuples()}
    elect = {(str(int(d)).zfill(2), str(int(s)).zfill(3)):int(n)
             for (d, s), n in e.groupby(level=[0,1]).sum().items()}
    sections = {}
    for (d, s), sub in v.groupby(['d','s']):
        votes = {c:int(n) for c,n in sub[sub.votos_tipo == 'POSITIVO'].groupby('code').v.sum().items()}
        sections[d,s] = dict(d=d,s=s,name=names.get((d,s),''),v=votes,pos=sum(votes.values()),
            bla=int(sub[sub.votos_tipo.isin(['EN BLANCO','BLANCO'])].v.sum()),
            nul=int(sub[sub.votos_tipo.isin(['NULO','RECURRIDO','IMPUGNADO'])].v.sum()),
            el=elect.get((d,s),0),note='')
    changes = []
    for k, target in {('08','002'):'001',('21','010'):'009',('21','014'):'013',('21','015'):'013'}.items():
        if k not in sections: continue
        src = sections[k]
        if src['name'] and norm(src['name']) not in ('suburbios','paranacampana','rosariosecciones','rosariosuburbios','lacapitalsuburbios','lacapitalcamp','rosariobarr','rosariocamp'):
            continue  # Santa Fe renumera sus departamentos en 2023.
        dst = sections[(k[0],target)]
        for q in ('pos','bla','nul','el'): dst[q] += src[q]
        for c,n in src['v'].items(): dst['v'][c] = dst['v'].get(c,0) + n
        dst['note'] += f' Incluye la subsección electoral {k[1]}.'
        changes.append(f'{D2P[k[0]]}: subsección {k[1]} sumada a {target}.')
        del sections[k]
    ant = sections.pop(('24','003'), None)
    compath = ROOT/'datos/fuentes_leg2003_2025/presidenciales/complementos.json'
    extra_sources = [compath]
    for x in json.loads(compath.read_text(encoding='utf8')):
        if x['key'] != key: continue
        assert sum(x['v'].values()) == x['pos'] and all(c in cand for c in x['v']), x
        old = sections.get((x['d'],x['s']))
        assert not old or old['pos'] == 0 or x.get('reemplazar'), (key,x['name'],'complemento sobre unidad con votos')
        sections[x['d'],x['s']] = {q:x[q] for q in ('d','s','name','v','pos','bla','nul','el')}
        sections[x['d'],x['s']]['note'] = x['nota']
        sections[x['d'],x['s']]['definitivo'] = True
        changes.append(x['name']+': '+x['nota'])
        extra_sources.append(ROOT/x['archivo'])
        if x.get('archivo_inscriptos'): extra_sources.append(ROOT/x['archivo_inscriptos'])
    if year == 2007 and not sections[('22','026')].get('definitivo'):
        r = sections[('22','026')]
        r['invalid'] = True
        r['note'] = ('Pendiente de cotejo: PolAr registra 999 votos al PO en cada una de las mesas 729 y 731, '
                     'que superan sus 450 y 270 electores. Esas cifras hacen que el PO resulte primero en Sarmiento. '
                     'Se conserva el registro original, pero no se adjudica ganador ni se colorean porcentajes.')
        changes.append('Santiago del Estero, Sarmiento: '+r['note'])
    idx = {(u['prov'],norm(u['name'])):i for i,u in enumerate(U) if u['name'] != 'Islas Malvinas'}
    linked = {}; unmapped = []
    for (d,s),r in sections.items():
        p = D2P[d]
        nn = norm(('Circ. %02d' if year <= 2007 else 'Comuna %d') % int(s)) if d == '01' else norm(r['name'])
        k = (p,nn)
        if k not in idx: k = (p,PROV_ALIASES.get(k,ALIASES.get(nn,nn)))
        i = idx.get(k)
        if i is None: unmapped.append([p,s,r['name']])
        else:
            assert i not in linked, (key,p,s,'duplicado')
            linked[i] = r
    dump(folder/'sin_poligono.json',unmapped)
    assert not unmapped, (key,'sin polígono',unmapped)
    wins = Counter(); missing = []; ties = []
    def winner(r):
        if not r or not r['pos'] or r.get('invalid'): return None
        best = max(r['v'].values()); first = [c for c,n in r['v'].items() if n == best]
        return first[0] if len(first) == 1 else None
    for i,u in enumerate(U):
        if u['name'] == 'Islas Malvinas': continue
        r = linked.get(i)
        if not r or not r['pos'] or r.get('invalid'): missing.append(f"{u['prov']}: {u['name']}")
        elif winner(r): wins[winner(r)] += 1
        else: ties.append(f"{u['prov']}: {u['name']}")
    if winner(ant): wins[winner(ant)] += 1
    win_codes = sorted(wins,key=lambda c:-totals[c])
    W = dict(art=f'Elecciones presidenciales de Argentina de {year}',blocs={c:totals[c] for c in win_codes},
             otros=metrics['positivos']-sum(totals[c] for c in win_codes),**metrics,
             lab_pos='Votos positivos',lab_bla='Votos en blanco',lab_nul='Votos nulos / anulados')
    assert W['otros'] >= 0
    dump(folder/f'wiki_nacional_{key}.json',W)
    import wikitop
    wikitop.WIKI[key] = W
    cs,slices,partp,met = wikitop.national(key)
    nat = dict(cands=cs,slices=[s for s in slices if s['v']],partp=partp,metrics=met)
    prov = {}
    for r in list(linked.values()) + ([ant] if ant else []):
        p = D2P[r['d']]
        q = prov.setdefault(p,dict(v={},pos=0,bla=0,nul=0,el=0,note='Suma de los votos locales disponibles de la fuente.'))
        for k in ('pos','bla','nul','el'): q[k] += r[k]
        for c,n in r['v'].items(): q['v'][c] = q['v'].get(c,0) + n
    def record(r):
        if not r or not r['pos']:
            return dict(lines=[],metrics=[],fill=BEIGE,note='Pendiente: la fuente no aporta votos positivos. No se imputan resultados.')
        emit = r['pos']+r['bla']+r['nul']
        lines = [[c,n,round(100*n/r['pos'],2)] for c,n in sorted(r['v'].items(),key=lambda x:-x[1]) if n]
        for c,k in [('P_BLA','bla'),('P_NUL','nul')]:
            if r[k]: lines.append([c,r[k],round(100*r[k]/emit,2)])
        met = [['Votos positivos',num(r['pos'])],['Votantes',num(emit)]]
        note = r['note']
        if r['el']:
            met.insert(0,['Inscriptos' if r.get('definitivo') else 'Electores de mesas con votos',num(r['el'])])
            if emit <= r['el']: met.append(['Participación' if r.get('definitivo') else 'Participación en mesas con votos',f"{100*emit/r['el']:.2f}".replace('.',',')+' %'])
            else: note += ' Votantes mayores que el padrón disponible: no se calcula participación.'
        w = winner(r)
        if r.get('invalid'): return dict(lines=lines,metrics=met,note=note,fill=BEIGE)
        if w: return dict(lines=lines,metrics=met,note=note,w=w,q=round(100*r['v'][w]/r['pos'],2))
        return dict(lines=lines,metrics=met,note=note+' Empate en el primer puesto.',fill='#dcdcdc')
    unit = [record(linked.get(i)) for i in range(len(U))]
    for i,u in enumerate(U):
        if u['name'] == 'Islas Malvinas': unit[i] = dict(lines=[],metrics=[],fill=GREY,note='Sin voto argentino: islas bajo administración británica.')
    ant_rec = record(ant)
    kind = 'PolAr / Atlas Electoral de Andy Tow' if year < 2011 else 'DINE, escrutinio provisorio'
    note = f'Nacional: tabla de Wikipedia, {"segunda" if bal else "primera"} vuelta. Mapa: {kind}, votos observados por mesa agregados por departamento, con complementos definitivos documentados. {description(year)}. No se imputan votos. El padrón del provisorio incluye las mesas con votos; los complementos llevan su padrón definitivo publicado. Diferencias y cobertura en LEEME.'
    keys = [[BEIGE,'Sin dato utilizable / pendiente'],['#dcdcdc','Empate']]
    modes = [dict(id='gan',tile='GANÓ',note=note,units=unit+[ant_rec],prov={p:record(r) for p,r in prov.items()},national=nat,legend=dict(keys=keys))]
    # Una coropleta para cada candidato con victoria local; en 2003 son cinco.
    abbr = {'M':'MENEM','K':'KIRCH.','L':'L.MUR.','R':'R. SAÁ','C':'CARRIÓ',
            'FPV':'SCIOLI' if year == 2015 else 'CRIST.','CC':'CARRIÓ','UNA':'MASSA' if year == 2015 else 'LAVAG.',
            'FREJULI':'R. SAÁ','SOB':'SOBIS.','FAP':'BINNER','CF':'R. SAÁ' if year <= 2015 else 'LAVAG.',
            'FP':'DUHAL.','CAM':'MACRI','FDT':'ALBER.','JXC':'BULLR.' if year == 2023 else 'MACRI',
            'UP':'MASSA','LLA':'MILEI','HXNP':'SCHIA.'}
    specs = [(c.lower(), abbr.get(c,c[:6]),
              lambda r,c=c:100*r['v'].get(c,0)/r['pos'],cand[c]['base'],'% '+cand[c]['n']) for c in win_codes]
    specs.append(('par','PART',lambda r:100*(r['pos']+r['bla']+r['nul'])/r['el'] if r['el'] and r['pos']+r['bla']+r['nul']<=r['el'] else None,
                  '#2a6f97','Participación en mesas con votos (%)'))
    for mid,tile,fn,col,title in specs:
        edges = [0,50,60,65,70,75,80] if mid == 'par' else [0,10,20,30,40,50,60]
        rgb = [int(col[j:j+2],16) for j in (1,3,5)]
        cols = ['#'+''.join(f'{round(x*k):02x}' for x in rgb) for k in (1,.85,.7,.55,.4,.3,.2)]
        def chor(rec,r):
            out = {k:v for k,v in rec.items() if k not in ('w','q','fill')}
            q = fn(r) if r and r['pos'] and not r.get('invalid') else None
            ix = max([i for i,e in enumerate(edges) if q >= e] or [0]) if q is not None else 0
            out['fill'] = cols[ix] if q is not None else BEIGE
            return out
        un = [chor(unit[i],linked.get(i)) if u['name'] != 'Islas Malvinas' else unit[i] for i,u in enumerate(U)]
        modes.append(dict(id=mid,tile=tile,note=note,units=un+[chor(ant_rec,ant)],prov={p:chor(record(r),r) for p,r in prov.items()},national=nat,
                          legend=dict(title=title,stops=[[c,('+' if i == 6 else '')+str(e)+'%'] for i,(c,e) in enumerate(zip(cols,edges))],bars=False,keys=keys)))
    control = [dict(codigo=c,candidato=cand[c]['n'],base=sum(r['v'].get(c,0) for r in sections.values())+(ant['v'].get(c,0) if ant else 0),
                    wikipedia=n,ganadas=wins[c]) for c,n in totals.items()]
    for r in control: r['diferencia'] = r['base']-r['wikipedia']
    pd.DataFrame(control).to_csv(folder/f'control_bloques_{key}.csv',index=False,encoding='utf-8-sig')
    source_hashes = {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (source,wiki_source,logo_source,*extra_sources)}
    report = dict(key=key,year=year,cargo='presidente',subtitle='Segunda vuelta' if bal else 'Primera vuelta',
        geometry=description(year),units=len(U)+1,with_data=sum(bool(r and r['pos'] and not r.get('invalid')) for r in linked.values())+bool(ant and ant['pos']),
        missing=missing,antartida_sin_dato=not bool(ant and ant['pos']),ties=ties,winners={cand[c]['n']:n for c,n in wins.items()},
        national=W,base_positivos=sum(r['base'] for r in control),wiki_suma_candidatos_menos_positivos=wiki_discrepancy,
        corrections=changes,logos_source=str(logo_source.relative_to(ROOT)),sources_sha256=source_hashes)
    dump(folder/'control_cobertura.json',report)
    dump(folder/'logos_usados.json',[dict(codigo=c,nombre=cand[c]['n'],origen=report['logos_source'],imagen=cand[c].get('logo_file',cand[c].get('blk','imagen incrustada heredada')))
                                    for c in win_codes if cand[c].get('img')])
    s = f'# Presidenciales {year} · {report["subtitle"]}\n\nGenerado con `python comun/atlas_leg2003_2025.py {key}`.\n\n'
    s += f'- Cartel nacional: tabla de [Wikipedia](https://es.wikipedia.org/wiki/Elecciones_presidenciales_de_Argentina_de_{year}), snapshot `{wiki_source.relative_to(ROOT)}` del proyecto.\n'
    s += f'- Mapa: `{source.relative_to(ROOT)}`, {kind}. Agregado reproducible con `transferencias/agregar_{"polar_" if year < 2011 else ""}circuitos.py {year}{"b" if bal else "p"}`. Son votos observados; no se calibran al total de Wikipedia.\n'
    s += f'- Geometría: {description(year)}. Los recuadros usan la composición vigente del atlas de diputados 2003; sus acercamientos son aproximados.\n'
    s += f'- Logos y colores: `{logo_source.relative_to(ROOT)}`, copiados sin descargar ni rediseñar imágenes. Se hereda también el dibujo de la leyenda por radio: posición, tamaño y zoom de sus logos, sin ampliación adicional. En 2003 se conserva el tratamiento propio de su atlas por radio. Licencias de origen en `logos/LICENCIAS.md`.\n'
    s += '- Leyenda: sólo candidatos que ganan una unidad. Todos los candidatos permanecen en las fichas; el resto integra Otros en el cartel nacional. Empates en gris claro; sin dato en beige; Antártida separada; Malvinas gris.\n'
    s += '- Participación local: sobre los electores de mesas con votos del agregado, no el padrón completo del departamento. Si votantes supera ese padrón, no se calcula. La participación nacional usa la tabla de Wikipedia.\n'
    s += f'\nCobertura: {report["with_data"]} unidades con positivos. Pendientes: '+('; '.join(missing) or 'ninguna')+'.\n'
    if report['antartida_sin_dato']: s += 'Antártida: sin dato positivo, queda beige.\n'
    s += '\n| Candidato | Base local | Wikipedia | Diferencia | Unidades ganadas |\n|---|---:|---:|---:|---:|\n'
    for r in control: s += f'| {r["candidato"]} | {num(r["base"])} | {num(r["wikipedia"])} | {r["diferencia"]:+d} | {r["ganadas"]} |\n'
    s += '\nLas diferencias se conservan: las fuentes locales y el definitivo nacional tienen cobertura y revisiones distintas. Los SHA256 de los insumos están en `control_cobertura.json`.\n'
    if wiki_discrepancy: s += f'La suma de candidatos de la propia tabla de Wikipedia difiere en {wiki_discrepancy:+d} de sus positivos declarados. Se conservan las cifras de la tabla.\n'
    s += '\n'+ '\n'.join('- '+x for x in changes)+'\n\nAtlas integrado al catálogo local de GitHub Pages. La publicación requiere el push y el despliegue del sitio. Sin paquete de Commons.\n'
    (folder/f'LEEME_{key}.md').write_text(s,encoding='utf8')
    print(key,'con datos',report['with_data'],'pendientes',missing,'ganadores',report['winners'],flush=True)
    return SimpleNamespace(CAND=cand,MODES=modes,disp={i:(f"{u['name']} · {u['parroquia']}" if 'parroquia' in u else u['name']) for i,u in enumerate(U)},ANT_I=len(U),report=report)
