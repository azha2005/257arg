"""Prepara cruces históricos sin imputar votos ni padrones ausentes."""
from pathlib import Path
import ast
import hashlib
import json
import re
import unicodedata
import pandas as pd
import estimar

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCES = {'1989p': '1989_presidente', '1995p': '1995_presidente',
           '1989d': '1989_diputados', '1994c': '1994_constituyentes',
           '1985d': '1985_diputados', '1987d': '1987_diputados'}
SOURCES['1983p'] = '1983_presidente'
SOURCES['1997d'] = '1997_diputados'
SOURCES['1999p'] = '1999_presidente'
NEW_PAIRS = [('1995p','1997d'),('1995p','1999p'),('1983p','1985d')]

def norm(s):
    s = unicodedata.normalize('NFD', str(s).upper()).encode('ascii', 'ignore').decode()
    s = re.sub(r'\bGRAL\b', 'GENERAL', s)
    return re.sub('[^A-Z0-9]', '', s)

# Alias revisados contra los nombres de las cuatro bases y los atlas locales.
ALIASES = {
'02': {'SALIQUELO':'SALLIQUELO', 'ESTEBANECHEVARRIA':'ESTEBANECHEVERRIA', 'GENERALJUANMADARIAGA':'GENERALMADARIAGA', 'AGCHAVEZ':'ADOLFOGONZALESCHAVES'},
'05': {'BERONASTRADA':'BERONDEESTRADA', 'EMPREDADO':'EMPEDRADO', 'SANLUISPALMAR':'SANLUISDELPALMAR'},
'06': {'FRAYJUSTOSANTAMARIA':'FRAYJUSTOSANTAMARIADEORO', 'PTEDELAPLAZA':'PRESIDENCIADELAPLAZA', 'PRESIDENTEDELAPLAZA':'PRESIDENCIADELAPLAZA'},
'07': {'VIEDMA':'BIEDMA', 'PASODELOSINDIOS':'PASODEINDIOS', 'FAMEGHINO':'FLORENTINOAMEGHINO'},
'08': {'ISLASDEIBICUY':'ISLASDELIBICUY'},
'10': {'BELGRANO':'CAPITAL'},
'11': {'LACAPITAL':'CAPITAL', 'CHAPADLEUFU':'CHAPALEUFU', 'CONHELLO':'CONHELO'},
'12': {'CORONELFELIPEVARELA':'FELIPEVARELA', 'GENERALORTIZOCAMPO':'GENERALOCAMPO', 'GENERALSARMIENTO':'VINCHINA', 'GENERALANGELVPENALOZA':'PENALOZA', 'ANGELVERAPENALOZA':'PENALOZA', 'JUANFQUIROGA':'QUIROGA', 'ROSARIOVERAPENALOZA':'VERAPENALOZA'},
'14': {'GENERALMBELGRANO':'GENERALMANUELBELGRANO', 'LGRANSANMARTIN':'LIBERTADORGENERALSANMARTIN'},
'15': {'CATALLIL':'CATANLIL', 'COLLUNCURA':'COLLONCURA', 'HUILINCHES':'HUILICHES'},
'16': {'CAPITAL':'ADOLFOALSINA', 'SANCARLOSDEBARILOCHE':'BARILOCHE', 'VEINTICINCODEMAYO':'25DEMAYO'},
'17': {'RDELAFRONTERA':'ROSARIODELAFRONTERA', 'RDELERMA':'ROSARIODELERMA'},
'18': {'NUEVEDEJULIO':'9DEJULIO'},
'19': {'GDORDUPUY':'GOBERNADORDUPUY'},
'21': {'LACAPITAL':'CAPITAL'},
'22': {'ATIMISQUI':'ATAMISQUI', 'GIMENEZ':'JIMENEZ', 'MARIANOMORENO':'MORENO', 'VILLASALAVINA':'SALAVINA', 'BRIGJFIBARRA':'MATARA'}
}

def canonical(d, name):
    n = norm(name)
    extra = {'06':{'SANFERNANDO':'CAPITAL'},'12':{'FACUNDOQUIROGA':'QUIROGA','GENERALANGELPENALOZA':'PENALOZA','GENERALLAVALLE':'FELIPEVARELA','GOBERNADORGORDILLO':'CHAMICAL'},'17':{'GUACHAPAS':'GUACHIPAS'}}
    extra.setdefault('02',{}).update({'3DEFEBRERO':'TRESDEFEBRERO','CONORELDORREGO':'CORONELDORREGO','TRESARROLLOS':'TRESARROYOS'})
    extra.setdefault('05',{})['BERONDEASTRADA']='BERONDEESTRADA'
    extra.setdefault('10',{})['DRMANUELBELGRANO']='CAPITAL'
    extra['12']['GENERALJUANFQUIROGA']='QUIROGA'
    extra.setdefault('16',{})['ADOLOFOALSINA']='ADOLFOALSINA'
    extra['17']['GENERALJOSEDESANMARTIN']='SANMARTIN'
    extra.setdefault('22',{})['QUEBRACHOS']='QUEBRACHO'
    n = extra.get(d,{}).get(n,n)
    return ALIASES.get(d, {}).get(n, n)

def canonical_1999(d,name):
    # Las hojas de Misiones y Río Negro añaden el código después de un guion.
    clean = re.sub(r'\s*-\s*\d+\s*$', '', str(name))
    n = canonical(d,clean)
    aliases = {
      '02':{'AMEGHINO':'FLORENTINOAMEGHINO','CNELDORREGO':'CORONELDORREGO','CNELPRINGLES':'CORONELPRINGLES','CNELROSALES':'CORONELDEMARINALROSAL','CNELSUAREZ':'CORONELSUAREZ','GONZALESCHAVEZ':'ADOLFOGONZALESCHAVES','JUAREZ':'BENITOJUAREZ','MALVINASARGENTINA':'MALVINASARGENTINAS','NUEVEDEJULIO':'9DEJULIO','PERON':'PRESIDENTEPERON','TORDILLIO':'TORDILLO','TRENQUELAUNQUEN':'TRENQUELAUQUEN','VEINTICINCODEMAYO':'25DEMAYO'},
      '04':{'RSAENZPENA':'ROQUESAENZPENA'},'05':{'SLDELPALMAR':'SANLUISDELPALMAR'},
      '11':{'QUEMU':'QUEMUQUEMU'},'12':{'FVARELA':'FELIPEVARELA','GENERALORTIZDEOCAMPO':'GENERALOCAMPO'},
      '15':{'CONFLUENCIA':'CAPITAL'},'24':{'USHUIA':'USHUAIA'}}
    return aliases.get(d,{}).get(n,n)

def literal(file, variable):
    tree = ast.parse((ROOT / file).read_text(encoding='utf8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == variable for t in node.targets):
            if variable == 'FAMS':
                value = node.value.values[[ast.literal_eval(k) for k in node.value.keys].index(1989)]
                return {1989: {kw.arg: ast.literal_eval(kw.value) for kw in value.keywords}}
            return ast.literal_eval(node.value)
    raise KeyError(variable)

def mapping(year):
    if year == '1999p': return {}   # Por candidatura y provincia: presidente_1999.candidato.
    if year == '1997d':
        fam = literal('mapa1997/build_1997.py','FAM')
        return {c:b for b,cs in fam.items() for c in cs.split()}
    if year == '1983p': return literal('mapa1983/build_1983.py', 'CODE2BLOC')
    if year in ('1985d','1987d'):
        return literal(f'mapa{year[:4]}/build_{year[:4]}.py', 'CODE2BLOC')
    if year == '1989p':
        return literal('mapa1989/build_1989.py', 'CODE2BLOC')
    if year == '1995p':
        return {c: label for var, label in [('MEN_C','MEN'), ('BOR_C','BOR'), ('MAS_C','MAS')]
                for c in literal('mapa1995/build_1995.py', var)}
    if year == '1989d':
        fam = literal('atlas_leg8399.py', 'FAMS')[1989]
        return {c: b for b, codes in fam.items() for c in codes.split()}
    return literal('mapa1994/build_1994.py', 'CODE2BLOC')

def territory(d, n, year):
    # Uniones comunes completas: no se reparte un departamento entre descendientes.
    groups = {
      '02': [('GENERAL SARMIENTO','SAN MIGUEL','JOSE C PAZ','MALVINAS ARGENTINAS'),
             ('MORON','HURLINGHAM','ITUZAINGO'), ('GENERAL PINTO','FLORENTINO AMEGHINO'),
             ('MAGDALENA','PUNTA INDIO'),
             ('ESTEBAN ECHEVERRIA','SAN VICENTE','FLORENCIO VARELA','PRESIDENTE PERON','EZEIZA')],
      '06': [('12 DE OCTUBRE','2 DE ABRIL')],
      '24': [('USHUAIA','SECTOR ANTARTICO ARGENTINO')]}
    if year in ('1989d','1994c'):
        groups['02'] = [('GENERAL PINTO','FLORENTINO AMEGHINO')]
    if year in ('1985d','1987d'):
        groups = {'02':[('PELLEGRINI','TRES LOMAS')], '10':[('CAPITAL','PALPALA')]}
    for group in groups.get(d, []):
        names = [canonical(d, x) for x in group]
        if n in names:
            return 'S:UNION_' + names[0]
    return 'S:' + n

def main():
    out = HERE / 'historicos_1989'
    out.mkdir(exist_ok=True)
    ids = {norm(n): d for d,n in estimar.DISTRITOS.items()}
    ids['CAPITALFEDERAL'] = '01'
    manifest, controls, records, excluded = [], [], [], []
    for year, source in SOURCES.items():
        path = ROOT / 'base8399/ernesto' / source / 'dpto_partidos.csv'
        df = pd.read_csv(path)
        if year == '1999p':
            # acjc00 contiene el total de sublemas acjc01–03: no sumar ambos.
            df.loc[df.codigo_partido=='acjc00','tipo_fila'] = 'subtotal_sublemas'
        if year == '1997d': df.loc[df.codigo_partido.isin(['pos','pos19']),'tipo_fila'] = 'positivos'
        if year == '1985d':
            reference = pd.read_csv(ROOT/'base8399/ernesto/1983_diputados/dpto_partidos.csv',dtype={'codigo_indra':str})
            lookup = reference.drop_duplicates('codigo_indra').set_index('codigo_indra').departamento.to_dict()
            df['departamento'] = [lookup[str(code).zfill(5)] if str(name).isdigit() and len(str(name))==5 else name
                                  for code,name in zip(df.codigo_indra,df.departamento)]
        codes = mapping(year)
        votes, mapping_rows = [], []
        for (province, name), group in df.groupby(['provincia','departamento'], sort=True):
            d = ids[norm(province)]
            n = canonical(d, name)
            if year == '1999p': n=canonical_1999(d,name)
            if d == '09' and n == 'PILAGAS': n = 'PILAGA'
            if d == '22' and n == 'IBARRA': n = 'MATARA'
            key = territory(d, n, year)
            record = dict(anio=year, distrito=d, seccion=0, circuito=name, seccion_comun=0,
                          circuito_comun=key, circuito_normalizado='S:'+n,
                          motivo='Nombre normalizado o unión territorial completa', fuente_id=source)
            records.append(record)
            metrics = group[group.tipo_fila != 'agrupacion'].drop_duplicates('tipo_fila').set_index('tipo_fila').votos.to_dict()
            positive_candidates = group.loc[group.tipo_fila=='positivos','votos'].tolist()
            if positive_candidates:
                actual = group.loc[group.tipo_fila=='agrupacion','votos'].sum()
                metrics['positivos'] = min(positive_candidates,key=lambda value:abs(value-actual))
            components = 0
            positive = 0
            for row in group.itertuples():
                if row.tipo_fila == 'agrupacion':
                    bloc = codes.get(row.codigo_partido, 'OTROS')
                    if year == '1995p' and row.codigo_partido == 'fed': bloc = 'MAS' if d == '04' else 'MEN'
                    if year == '1995p' and row.codigo_partido == 'fr' and d == '23': bloc = 'BOR'
                    if year == '1994c' and row.codigo_partido == 'fes' and d in ('18','23'): bloc = 'PJ'
                    if year == '1985d' and row.codigo_partido == 'flib': bloc = 'REN' if d == '01' else 'FDP'
                    if year == '1999p':
                        from presidente_1999 import candidato
                        bloc = candidato(province,row.codigo_partido)
                        assert bloc is not None
                    kind = 'POSITIVO'
                    mapping_rows.append(dict(provincia=province,codigo=row.codigo_partido,bloque=bloc))
                    positive += row.votos
                elif row.tipo_fila in ('blancos','nulos','impugnados_recurridos'):
                    bloc, kind = '', 'NO_POSITIVO'
                    # En algunas hojas hay métricas repetidas: se cuentan una vez.
                    if group[group.columna_fuente == row.columna_fuente].index[0] != row.Index: continue
                else:
                    continue
                components += row.votos
                votes.append(dict(distrito_id=d, seccion_id=0, circuito=key, circuito_original='S:'+n, agrupacion_id=bloc, votos_tipo=kind, v=row.votos))
            controls.append(dict(anio=year, provincia=province, departamento=name, votos_desglosados=components,
                                 **{k:metrics.get(k) for k in ('positivos','total','electores')},
                                 diferencia_total=metrics.get('total', components)-components))
            gap = metrics.get('positivos', positive)-positive
            if abs(gap) > max(100, .01 * max(positive, metrics.get('positivos',0))):
                excluded.append(dict(anio=year,distrito=d,circuito=key,circuito_original='S:'+n,motivo='Desglose no cierra con positivos',diferencia=gap))
            if year == '1987d' and d == '02' and n == 'LAPLATA':
                excluded.append(dict(anio=year,distrito=d,circuito=key,circuito_original='S:'+n,motivo='PJ 11919: error documentado en LEEME_1987; no imputado',diferencia=99984))
        frame = pd.DataFrame(votes)
        keys = ['distrito_id','seccion_id','circuito','agrupacion_id','votos_tipo']
        raw = frame.drop(columns='circuito').rename(columns={'circuito_original':'circuito'}).groupby(keys,as_index=False).v.sum()
        v = frame.groupby(keys,as_index=False).v.sum()
        if year == '1995p':
            provincial = json.loads((ROOT/'mapa1995/wiki_prov.json').read_text())['Santa Cruz']
            extrapolation = []
            for code, field in [('MEN','men'), ('BOR','bor'), ('MAS','mas')]:
                others = v[(v.distrito_id=='20') & (v.circuito!='S:DESEADO') & (v.agrupacion_id==code)].v.sum()
                mask = (v.distrito_id=='20') & (v.circuito=='S:DESEADO') & (v.agrupacion_id==code)
                original = int(v.loc[mask,'v'].sum())
                result = int(provincial[field]-others)
                assert result >= 0
                v.loc[mask,'v'] = result
                raw.loc[(raw.distrito_id=='20') & (raw.circuito=='S:DESEADO') & (raw.agrupacion_id==code),'v'] = result
                extrapolation.append(dict(bloque=code,total_provincial=provincial[field],otros_departamentos=int(others),deseado_original=original,deseado_extrapolado=result,agregado=result-original))
            (out/'deseado_1995_extrapolado.json').write_text(json.dumps({'fuente':'mapa1995/wiki_prov.json; Wikipedia presidencial 1995, tabla por distrito','calculo':extrapolation},ensure_ascii=False,indent=2),encoding='utf8')
        e = v.groupby(['distrito_id','seccion_id','circuito']).v.sum()
        pd.to_pickle((v,e), HERE / f'circ_{year}.pkl')
        pd.to_pickle((raw,raw.groupby(['distrito_id','seccion_id','circuito']).v.sum()),out/f'raw_{year}.pkl')
        pd.DataFrame(mapping_rows).drop_duplicates().to_csv(out/f'bloques_{year}.csv',index=False,encoding='utf-8-sig')
        manifest.append(dict(anio=year, fuente=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), unidades=len(e)))
    pd.DataFrame(controls).to_csv(out/'control_datos_originales.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(records).to_csv(out/'correspondencias.csv',index=False,encoding='utf-8-sig')
    (out/'exclusiones.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'fuentes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    auxiliaries = ['mapa1983/build_1983.py','mapa1985/build_1985.py','mapa1987/build_1987.py',
                   'mapa1989/build_1989.py','mapa1994/build_1994.py','mapa1995/build_1995.py',
                   'mapa1997/build_1997.py','atlas_leg8399.py','mapa1995/wiki_prov.json',
                   'mapa1995/w1995.txt','base8399/ernesto/1983_diputados/dpto_partidos.csv']
    auxiliaries += ['transferencias/presidente_1999.py','transferencias/fuentes/w1999p.txt']
    (out/'fuentes_auxiliares.json').write_text(json.dumps([
        dict(fuente=relative,sha256=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest())
        for relative in auxiliaries],ensure_ascii=False,indent=2),encoding='utf8')
    for a,b in [('1989p','1995p'),('1989d','1994c'),('1985d','1987d')]:
        A = pd.read_pickle(HERE/f'circ_{a}.pkl')[1]
        B = pd.read_pickle(HERE/f'circ_{b}.pkl')[1]
        print(a,b,'solo origen',A.index.difference(B.index).tolist(),'solo destino',B.index.difference(A.index).tolist())

if __name__ == '__main__': main()
