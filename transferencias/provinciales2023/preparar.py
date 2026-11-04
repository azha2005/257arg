"""Bases provinciales originales, sin imputación ni cruce de números de mesa.

La unidad común del primer piloto es el departamento administrativo. Los
municipios/localidades provinciales se asignan con Georef; toda excepción
requiere una equivalencia explícita y se conserva para revisión.
"""
from pathlib import Path
import concurrent.futures as cf
import json
import re
import sys
import unicodedata
import numpy as np
import pandas as pd
import pymupdf as pdf
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / 'fuentes'
sys.path.insert(0, str(HERE.parent))
import estimar


def norm(s):
    s = unicodedata.normalize('NFD', str(s)).encode('ascii', 'ignore').decode().upper()
    s = re.sub(r'\bGRAL\b', 'GENERAL', s)
    return re.sub('[^A-Z0-9]', '', s)


def get(name, url):
    f = RAW / name
    if not f.exists():
        r = requests.get(url, timeout=45)
        r.raise_for_status()
        f.write_bytes(r.content)
    return json.loads(f.read_text(encoding='utf-8-sig'))


def georef(prov):
    d = get('georef_' + prov + '.json', 'https://apis.datos.gob.ar/georef/api/localidades?provincia=' + prov + '&max=1000&campos=id,nombre,departamento,municipio')
    out, municipal = {}, {}
    for x in d['localidades']:
        out.setdefault(norm(x['nombre']), set()).add(x['departamento']['nombre'])
        n = (x.get('municipio') or {}).get('nombre')
        if n:
            municipal.setdefault(norm(n), set()).add(x['departamento']['nombre'])
    mapped = {k: list(v)[0] for k, v in out.items() if len(v) == 1}
    for k, v in municipal.items():
        if k not in out and len(v) == 1:
            mapped[k] = list(v)[0]
    return mapped


def nacional(key, dist):
    t, _ = estimar.load(key)
    t = t.loc[dist].copy()
    names = estimar.secnames(key)
    t.index = [norm(names[(dist, s)]) for s, c in t.index]
    return t.groupby(level=0).sum()


def rio_negro():
    ub = json.loads((RAW / 'rn_ubicaciones.json').read_text(encoding='utf8'))
    locs = [x for x in ub if x['clase_ubicacion'] == 'Localidad']
    def fetch(x):
        path = x['id_ubicacion'].replace('.', '/')
        b = 'https://www.jusrionegro.gov.ar/inicio/web/escrutinio-16-04-2023/'
        result = get('rn_' + x['id_ubicacion'] + '.json', b + 'resultados/' + path + '/GOB.json')
        meta = get('rn_meta_' + x['id_ubicacion'] + '.json', b + 'metadata/' + path + '/meta.json')
        e = meta.get('votantes_habilitados_por_cargo', {}).get('GOB', meta.get('votantes_habilitados'))
        row = {z['descripcion_candidatura']: z['cant_votos'] for z in result['resultados'] if z['clase_candidatura'] == 'Lista'}
        row['Blanco y nulo'] = result['cant_votos_negativos']
        row['No votó'] = e - result['cant_votantes']
        row['unidad'] = x['descripcion_ubicacion'].strip()
        row['electores'] = e
        return row
    with cf.ThreadPoolExecutor(5) as p:
        rows = list(p.map(fetch, locs))
    return pd.DataFrame(rows).fillna(0).set_index('unidad')


def salta():
    f = HERE / 'salta_detalle.pkl'
    if f.exists():
        d = pd.read_pickle(f)
    else:
        d = pd.read_excel(RAW / 'salta_2023.xlsx')
        d.to_pickle(f)
    d = d[d['Categoría'].eq('GOBERNADOR')].copy()
    t = d.pivot_table(index='Departamento', columns='Lista', values='Votos', aggfunc='sum', fill_value=0)
    deps = get('salta_departamentos.json', 'https://www.electoralsalta.gov.ar/JSON/departamentos.json')
    audit = []
    for x in deps:
        j = get('salta_dep_%s.json' % x['nDeptoId'], 'https://www.electoralsalta.gov.ar/JSON/Escrutinio/2023G/1/%s.json' % x['nDeptoId'])
        s = j['datos'][0]
        name = x['sDepartamento']
        aliases = {'ROSARIODELAFRONTERA': 'ROSDELAFRONTERA'}
        match = next((n for n in t.index if norm(n) == aliases.get(norm(name), norm(name))), None)
        if match is None:
            raise ValueError(('Salta departamento', name, t.index.tolist()))
        official = {r['sLista'].strip(): r['nVotosDefinitivo'] for r in j['resultados']}
        actual = {str(k).strip(): int(v) for k,v in t.loc[match].items() if str(k).strip() in official}
        assert actual == official, (name, actual, official)
        audit.append(dict(departamento=match, electores=s['nElectores'], positivos=s['nPositivos'], blancos=s['nBlancos'], nulos=s['nNulos']))
    pd.DataFrame(audit).to_csv(HERE / 'control_salta_departamentos.csv', index=False, encoding='utf-8-sig')
    a = pd.DataFrame(audit).set_index('departamento')
    # Los especiales de la planilla se sustituyen por el control del mismo
    # definitivo; el total de cada fuerza ya fue cotejado al voto.
    t = t[[c for c in t if c.strip() in official]]
    t['Blanco y nulo'] = a.blancos + a.nulos
    t['No votó'] = a.electores - a.positivos - a.blancos - a.nulos
    t['electores'] = a.electores
    return t


def neuquen():
    # Columnas fijas del PDF oficial: mesa x<56, lista x<97,
    # denominación 98..210, gobernador 212..264. Cada fila se ancla
    # por su número de mesa y su coordenada vertical.
    rows = []
    with pdf.open(RAW / 'neuquen_mesas.pdf') as d:
        for pi, page in enumerate(d):
            words = page.get_text('words')
            for w in words:
                if w[2] < 56 and w[1] > 52 and w[4].isdigit():
                    y = w[1]
                    same = [v for v in words if abs(v[1] - y) < .4]
                    code = [v[4] for v in same if 56 < v[0] and v[2] < 97]
                    vote = [v[4] for v in same if 211 < v[0] and v[2] < 265]
                    if len(code) == 1 and code[0].isdigit() and vote:
                        assert len(vote) == 1 and vote[0].isdigit(), (pi, same)
                        rows.append(dict(mesa=int(w[4]), lista=int(code[0]), votos=int(vote[0]), pagina=pi+1))
                    elif not code:
                        text = ' '.join(v[4] for v in same if 97 < v[0] < 211)
                        if vote and any(k in text.lower() for k in ['blanco', 'nulo', 'recurrid', 'observad', 'impugnad']):
                            rows.append(dict(mesa=int(w[4]), lista=text, votos=int(vote[0]), pagina=pi+1))
    d = pd.DataFrame(rows)
    d.to_csv(HERE / 'neuquen_extraido_mesas.csv', index=False, encoding='utf-8-sig')
    # Distribución oficial provincial; se usa para agregar, nunca para
    # emparejar individualmente las mesas con el padrón nacional.
    loc = {}
    with pdf.open(RAW / 'neuquen_distribucion.pdf') as doc:
        for page in doc:
            words = page.get_text('words')
            anchors = sorted([w for w in words if 210 < w[0] and w[2] < 239 and w[1] > 64 and w[4].isdigit()], key=lambda w:w[1])
            previous = 64
            for w in anchors:
                n = ' '.join(v[4] for v in sorted(words, key=lambda v:(round(v[1],1),v[0])) if v[2] < 210 and previous-.1 < v[1] <= w[1]+.4)
                loc[int(w[4])] = n
                previous = w[1]+.5
    (HERE / 'neuquen_mesa_localidad.json').write_text(json.dumps(loc, ensure_ascii=False, indent=2), encoding='utf8')
    d['unidad'] = d.mesa.map(loc)
    if d.unidad.isna().any():
        print('NQN MESAS SIN LOCALIDAD', d[d.unidad.isna()].mesa.unique().tolist(), flush=True)
    return d.pivot_table(index='unidad', columns='lista', values='votos', aggfunc='sum', fill_value=0)


def misiones():
    rows = []
    with pdf.open(RAW / 'misiones_municipios.pdf') as d:
        for pi, page in enumerate(d):
            if pi == 0:
                continue
            words = page.get_text('words')
            muni = next(w for w in words if w[4] == 'Municipio')
            name = ' '.join(w[4] for w in words if w[0] > muni[2] and abs(w[1]-muni[1]) < 3)
            pct = next(w for w in words if '%' in w[4])
            gov = next(w for w in words if 'Gobernador' in w[4] and w[1]>pct[3])
            diputado = next(w for w in words if 'Diputado' in w[4] and w[1]>pct[3])
            gc, dc = (gov[0]+gov[2])/2, (diputado[0]+diputado[2])/2
            xmin, xmax = gc-(dc-gc)*.48, gc+(dc-gc)*.48
            row = dict(unidad=name, pagina=pi+1)
            row['participacion_impresa'] = pct[4]
            elect = [w for w in words if 250 < w[0] < 400 and abs((w[1]+w[3])/2-(pct[1]+pct[3])/2)<7 and w[4].isdigit()]
            row['electores'] = int(elect[0][4]) if len(elect)==1 else np.nan
            codes = ['71','644','653','654','900','901','902','903']
            for w in words:
                match = re.search(r'(71|644|643|653|654|900|300|901|902|903|303)-', w[4])
                if w[0] < xmin-20 and w[1] > gov[1] and match:
                    code = {'300':'900','303':'903','643':'644'}.get(match[1], match[1])
                    vals = [v for v in words if xmin < (v[0]+v[2])/2 < xmax and abs((v[1]+v[3])/2-(w[1]+w[3])/2) < 6 and v[4].isdigit()]
                    if len(vals) == 1:
                        row[code] = int(vals[0][4])
            for label, needle in [('blancos','BLANCO'),('nulos','NULOS'),('emitidos','TOTALES')]:
                marks = [w for w in words if needle in w[4].upper().replace('/','') and w[1] > gov[1]]
                if marks:
                    vals = [v for v in words if xmin < (v[0]+v[2])/2 < xmax and abs((v[1]+v[3])/2-(marks[0][1]+marks[0][3])/2) < 6 and v[4].isdigit()]
                    if len(vals) == 1:
                        row[label] = int(vals[0][4])
            # El OCR suele deformar la palabra TOTALES, pero conserva su
            # celda numérica: la primera de gobernador debajo de VOTOS NULOS.
            nulmarks = [w for w in words if w[4]=='NULOS']
            if nulmarks and 'emitidos' not in row:
                vals = sorted([v for v in words if xmin < (v[0]+v[2])/2 < xmax and nulmarks[0][3]+5 < v[1] < nulmarks[0][3]+45 and v[4].isdigit()], key=lambda w:w[1])
                if vals: row['emitidos'] = int(vals[0][4])
            # Celdas cotejadas visualmente con el PDF (revision_celdas_misiones.png).
            fixes = {7:{'nulos':77},11:{'901':377},16:{'nulos':16,'blancos':554},42:{'902':77},58:{'blancos':6416},62:{'644':77,'emitidos':29063},74:{'653':72},76:{'654':0}}
            row.update(fixes.get(pi+1, {}))
            rows.append(row)
    t = pd.DataFrame(rows).set_index('unidad')
    t.to_csv(HERE / 'misiones_extraccion_revision.csv', encoding='utf-8-sig')
    print('Misiones faltantes', t.isna().sum()[t.isna().any()].to_dict(), flush=True)
    print('Misiones totales', t.sum(numeric_only=True).to_dict(), flush=True)
    return t


if __name__ == '__main__':
    for k, fun in [('rn', rio_negro), ('salta', salta), ('neuquen', neuquen), ('misiones', misiones)]:
        t = fun()
        t.to_pickle(HERE / ('prov_' + k + '.pkl'))
        t.to_csv(HERE / ('prov_' + k + '.csv'), encoding='utf-8-sig')
        print(k, t.shape, t.sum(numeric_only=True).to_dict(), flush=True)
