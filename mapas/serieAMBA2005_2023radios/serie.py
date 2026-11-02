"""Serie AMBA por radio: preparación y controles reproducibles, sin alterar fuentes.

python mapas/serieAMBA2005_2023radios/serie.py [2005dip 2007pres ...]
python mapas/serieAMBA2005_2023radios/render.py 2023bal
"""
from pathlib import Path
from collections import defaultdict, Counter
import sys, re, json, pickle, math, unicodedata, io, zipfile, ast
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = HERE / 'cache'
CACHE.mkdir(exist_ok=True)
KEYS = [f'{y}dip' for y in range(2005, 2024, 2)] + [f'{y}pres' for y in (2007, 2011, 2015, 2019, 2023)] + ['2015bal', '2023bal']
KEYS += ['2023pasofuerza','2023pasocand']
KX = math.cos(math.radians(34.7)) * 111320
KY = 110574


def norm(s):
    n = re.sub('[^a-z0-9]', '', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower())
    return {'matanza': 'lamatanza', 'jcpaz': 'josecpaz', 'lasheras': 'generallasheras',
            'ciudadautonomadebuenosaires': 'ciudaddebuenosaires', 'capitalfederal': 'ciudaddebuenosaires'}.get(n, n)


def cir(s):
    return str(s).strip().upper().lstrip('0') or '0'


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf8')


def census(year):
    return 2001 if year <= 2009 else 2010 if year <= 2021 else 2022


def radios(cen):
    f = CACHE / f'radios_{cen}.pkl'
    if f.exists():
        return pd.read_pickle(f)
    if cen in (2001, 2022):
        old = ROOT / f'mapas/mapaAMBA{2003 if cen == 2001 else 2025}radios/radios_amba{cen}.geojson'
        features = json.loads(old.read_text(encoding='utf8'))['features']
    else:
        import shapefile
        from pyproj import Transformer, CRS
        dep = json.loads((ROOT / 'mapas/mapaAMBA2025radios/depto_pba_georef.json').read_text(encoding='utf8'))['departamentos']
        amba = {norm(x['properties']['partido']) for x in radios(2001)[0]}
        dep = {x['id'][2:]: x['nombre'] for x in dep if norm(x['nombre']) in amba}
        assert len(dep) == 40
        z = zipfile.ZipFile(ROOT / 'geometria/cartografia_argentina/conicet/radios/RADIOS_2010_V2025-1.zip')
        stem = next(x[:-4] for x in z.namelist() if x.endswith('.shp'))
        reader = shapefile.Reader(**{e: io.BytesIO(z.read(stem+'.'+e)) for e in ('shp', 'shx', 'dbf')}, encoding='latin1')
        tr = Transformer.from_crs(CRS.from_wkt(z.read(stem+'.prj').decode()), 4326, always_xy=True)
        features = []
        for i, record in enumerate(reader.iterRecords()):
            p = record.as_dict()
            if p['PROV'] != '02' and not (p['PROV'] == '06' and p['DEPTO'] in dep):
                continue
            g = shape(reader.shape(i).__geo_interface__)
            g = shapely.transform(g, lambda xy: np.column_stack(tr.transform(xy[:, 0], xy[:, 1])))
            p = dict(COD=p['COD_2010'], PROV=p['PROV'], DEPTO=p['DEPTO'], POB=p['B_POB_TOT'],
                     partido='Ciudad de Buenos Aires' if p['PROV'] == '02' else dep[p['DEPTO']])
            features.append(dict(type='Feature', properties=p, geometry=mapping(g)))
    for ft in features:
        p = ft['properties']
        p['COD'] = p.get('COD', p.get(f'COD_{cen}'))
        p['POB'] = p.get('POB', p.get('POB_TOT_P', p.get('POB_TOT', 0)))
    rp = pd.DataFrame([x['properties'] for x in features])
    gs = [shapely.make_valid(shape(x['geometry'])) for x in features]
    pd.to_pickle((features, rp, gs), f)
    print('radios', cen, len(rp), int(rp.POB.sum()), flush=True)
    return features, rp, gs


def section_names(year):
    f = ROOT / f'datos_oficiales/{year}/' / ('agregado_polar.pkl' if year < 2011 else 'agregado.pkl')
    v, _ = pd.read_pickle(f)
    v = v[v.distrito_id.astype(int).isin([1, 2])].copy()
    return {(f'{int(d):02d}', f'{int(s):03d}'): n for d, s, n in v[['distrito_id','seccion_id','seccion_nombre']].drop_duplicates().itertuples(index=False, name=None)}


def candidates(key):
    if 'paso' in key:
        from paso2023 import candidates as paso_candidates
        return paso_candidates(key)
    year = int(key[:4])
    ds = json.loads((ROOT / f'mapas/mapa{year}/dataset_{year}.json').read_text(encoding='utf8'))
    cand = {k: dict(v) for k, v in ds['candidates'].items() if not k.startswith('P_')}
    lookup, labels = {}, {}
    if key.endswith('dip'):
        path = ROOT / f'mapas/mapa{year}/mapeo_listas_{year}.csv'
        if year not in (2009, 2013):
            for r in pd.read_csv(path, dtype=str).fillna('').itertuples():
                if r.distrito in ('01', '02'):
                    lookup[r.distrito, r.lista] = r.codigo or f'X{r.distrito}_{r.lista}'
                    labels[r.distrito, r.lista] = r.nombre
        elif year == 2013:
            source = ast.parse((ROOT / 'mapas/mapa2013/build_2013.py').read_text(encoding='utf8'))
            for node in source.body:
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == 'LIST2BLOC':
                    lookup.update(ast.literal_eval(node.value.args[0]))
            lookup.update({('01', '0501'): 'FPV', ('02', '0501'): 'FPV'})
        else:
            # Reusar el cruce auditado de 2009; no reutilizar sus votos municipales.
            sys.path[:0] = [str(ROOT / 'comun'), str(ROOT / 'mapas/mapa2009'), str(ROOT / 'mapas/mapa2013')]
            from datos_2009 import LIST2BLOC
            lookup.update(LIST2BLOC)
        v, _ = pd.read_pickle(ROOT / f'datos_oficiales/{year}/' / ('agregado_polar.pkl' if year < 2011 else 'agregado.pkl'))
        named = {(d, norm(n)): lookup.get((d, a)) for (d, a), n in labels.items()}
        for r in v[v.votos_tipo == 'POSITIVO'].itertuples():
            d, a = f'{int(r.distrito_id):02d}', str(r.agrupacion_id).zfill(4)
            labels[d, a] = r.agrupacion_nombre
            if (d, a) not in lookup and named.get((d, norm(r.agrupacion_nombre))):
                lookup[d, a] = named[d, norm(r.agrupacion_nombre)]
        for (d, a), n in labels.items():
            c = lookup.setdefault((d, a), f'X{d}_{a}')
            if c not in cand:
                cand[c] = dict(n=n, base='#808080', logo='OTR')
    else:
        # Paleta y fuerzas del atlas presidencial/legislativo de cada época.
        tables = {
            2007: [('FPV','Cristina Fernández de Kirchner','Frente para la Victoria','#50ade6',['0134']), ('CC','Elisa Carrió','Coalición Cívica','#74b744',['0059']), ('UNA','Roberto Lavagna','Concertación UNA','#e10019',['0131']), ('FREJULI','Alberto Rodríguez Saá','FREJULI','#1aff98',['0133']), ('PSA','Fernando Solanas','Proyecto Sur','#389b00',['0030']), ('RECR','Ricardo López Murphy','Recrear','#f4ce00',['0048']), ('SOB','Jorge Sobisch','Movimiento Provincias Unidas','#0070b8',['0056','0057','0254'])],
            2011: [('FPV','Cristina Fernández de Kirchner','Frente para la Victoria','#50ade6',['frenteparalavictoria']), ('FAP','Hermes Binner','Frente Amplio Progresista','#ff6600',['frenteamplioprogresista']), ('UDESO','Ricardo Alfonsín','UDESO','#e10019',['unionparaeldesarrollosocial']), ('CF','Alberto Rodríguez Saá','Compromiso Federal','#1aff98',['compromisofederal']), ('FP','Eduardo Duhalde','Frente Popular','#8e6bd8',['frentepopular']), ('FIT','Jorge Altamira','Frente de Izquierda','#f65058',['frentedeizquierda']), ('CC','Elisa Carrió','Coalición Cívica','#74b744',['coalicioncivica'])],
            2015: [('FPV','Daniel Scioli','Frente para la Victoria','#50ade6',['frenteparalavictoria']), ('CAM','Mauricio Macri','Cambiemos','#f4ce00',['cambiemos']), ('UNA','Sergio Massa','UNA','#231f20',['unidosporunanuevaalternativa']), ('FIT','Nicolás del Caño','Frente de Izquierda','#f65058',['frentedeizquierda']), ('PROG','Margarita Stolbizer','Progresistas','#ee4d8b',['progresistas']), ('CF','Adolfo Rodríguez Saá','Compromiso Federal','#1aff98',['compromisofederal'])],
            2019: [('FDT','Alberto Fernández','Frente de Todos','#2ea3ff',['frentedetodos']), ('JXC','Mauricio Macri','Juntos por el Cambio','#f4ce00',['juntosporelcambio']), ('CF','Roberto Lavagna','Consenso Federal','#2f3b81',['consensofederal']), ('FIT','Nicolás del Caño','Frente de Izquierda','#f65058',['frentedeizquierda']), ('NOS','Juan José Gómez Centurión','Frente NOS','#307fe2',['frentenos']), ('UNITE','José Luis Espert','Unite','#4cb0e4',['uniteporlalibertad'])],
            2023: [('UP','Sergio Massa','Unión por la Patria','#009ce4',['unionporlapatria']), ('LLA','Javier Milei','La Libertad Avanza','#6c4c98',['lalibertadavanza']), ('JXC','Patricia Bullrich','Juntos por el Cambio','#fcbc00',['juntosporelcambio']), ('HXNP','Juan Schiaretti','Hacemos por Nuestro País','#283084',['hacemospornuestropais']), ('FIT','Myriam Bregman','Frente de Izquierda','#f65058',['frentedeizquierda'])]
        }
        cand = {c: dict(n=n, sub=sub, base=color, logo=c) for c, n, sub, color, _ in tables[year]}
        for c, _, _, _, aliases in tables[year]:
            for a in aliases:
                lookup[a] = c
        # Las candidaturas menores de 2007 conservan sus nombres del nomenclador.
        if year == 2007:
            names = pd.read_csv(ROOT/'datos_oficiales/polar/listas__listas_presi_gral2007.csv', dtype=str)
            for r in names.itertuples():
                a = r.vot_parCodigo.strip().zfill(4)
                c = lookup.setdefault(a, 'L'+a)
                cand.setdefault(c, dict(n=r.parDenominacion.strip(), base='#808080', logo='OTR'))
    # Siglas y emblemas ya documentados en el proyecto, sin nuevas descargas.
    for c, value in cand.items():
        if len(value.get('logo', '')) > 6:
            value['logo'] = value['logo'][:6]
        if key.endswith('dip'):
            value['sub'] = ''
    return cand, lookup, labels


def load_votes(key, lookup, labels):
    year = int(key[:4]); suffix = '' if key.endswith('dip') else 'b' if key.endswith('bal') else 'p'
    if 'paso' in key:suffix='pp'
    v, e = pd.read_pickle(ROOT / f'transferencias/circ_{year}{suffix}.pkl')
    ns = section_names(year)
    amba = {norm(p) for p in radios(census(year))[1].partido.unique()}
    allowed = {k for k, n in ns.items() if k[0] == '01' or norm(n) in amba}
    v = v[v.distrito_id.isin(['01','02'])].copy()
    v['sec'] = v.seccion_id.map(lambda s: f'{int(s):03d}')
    v = v[[ (d,s) in allowed for d,s in zip(v.distrito_id,v.sec) ]].copy()
    assert len({s for d,s in allowed if d == '02'}) == 40
    def cat(r):
        if r.votos_tipo == 'POSITIVO':
            if 'paso' in key:
                assert r.agrupacion_id in lookup,r.agrupacion_id
                return lookup[r.agrupacion_id]
            if key.endswith('dip'):
                aid=str(r.agrupacion_id).split('.')[0]
                return lookup.get((r.distrito_id, aid), f'X{r.distrito_id}_{aid}')
            if year == 2007:
                return lookup[str(r.agrupacion_id)]
            hits = [c for a,c in lookup.items() if a in norm(r.agrupacion_id)]
            assert len(set(hits)) == 1, (key, r.agrupacion_id, hits)
            return hits[0]
        if r.votos_tipo in ('EN BLANCO','BLANCO','BLANCOS'): return '_BLA'
        if r.votos_tipo in ('NULO','NULOS'): return '_NUL'
        return '_IMP'
    v['cat'] = [cat(r) for r in v.itertuples()]
    v['ck'] = list(zip(v.distrito_id,v.sec,v.circuito.map(cir)))
    V = v.pivot_table(index='ck',columns='cat',values='v',aggfunc='sum',fill_value=0).astype(float)
    V.index = pd.MultiIndex.from_tuples(V.index, names=['d','s','c'])
    ed = {(str(d),f'{int(s):03d}',cir(c)):float(x) for (d,s,c),x in e.items()}
    V['_ELOK'] = [ed.get(k,0) for k in V.index]
    for c in ('_BLA','_NUL','_IMP'):
        if c not in V: V[c] = 0.
    meta = dict(source=f'transferencias/circ_{year}{suffix}.pkl',source_kind='PolAr / Atlas Electoral de Andy Tow' if year < 2011 else 'DINE, escrutinio provisorio',
                sections={f'{d}_{s}':n for (d,s),n in ns.items() if (d,s) in allowed},
                missing_list_pba=year == 2009,
                valid_partidos=40 if year != 2009 else 0)
    if 'paso' in key:
        meta.update(tipo_eleccion='PASO presidencial 2023',desagregacion='candidato' if key.endswith('cand') else 'fuerza',
                    source_kind='DINE, PASO presidencial del 13 de agosto de 2023, escrutinio provisorio',
                    listas_nacionales=27,listas_presentes_amba=int(v[v.votos_tipo=='POSITIVO'].agrupacion_id.nunique()))
    # 1-nov: el usuario autorizó estimar NE desde los totales municipales y excluir sus ganadores.
    if year == 2009:
        meta['positivos_incompletos_pba'] = int(V.loc[[k[0]=='02' for k in V.index],[c for c in V if not c.startswith('_')]].to_numpy().sum())
        from datos_2009 import AG
        municipal=AG[0]
        municipal=municipal[(municipal.distrito_id=='02') & municipal.seccion_id.isin({s for d,s in allowed if d=='02'})]
        targets=defaultdict(Counter)
        for r in municipal.itertuples():
            if r.votos_tipo=='POSITIVO':
                c=lookup.get(('02',r.agrupacion_id),f'X02_{r.agrupacion_id}')
            elif r.votos_tipo in ('BLANCO','EN BLANCO','BLANCOS'):c='_BLA'
            elif r.votos_tipo in ('NULO','NULOS'):c='_NUL'
            else:c='_IMP'
            targets[r.seccion_id][c]+=float(r.v)
        assert len(targets)==40
        if 'NE' not in V:V['NE']=0.
        adjustments=[]
        for s,t in targets.items():
            idx=[k for k in V.index if k[:2]==('02',s)]
            assert idx,s
            for c in (set(V.columns)|set(t))-{'_ELOK','NE'}:
                if c not in V:V[c]=0.
                before=float(V.loc[idx,c].sum());after=float(t.get(c,0))
                factor=after/before if before else 0.
                no_profile=before==0 and after>0
                if no_profile:
                    pc=[x for x in V if not x.startswith('_') and x not in ('NE',c)]
                    w=V.loc[idx,pc].sum(axis=1)
                    assert w.sum()>0,(s,c)
                    V.loc[idx,c]=w/w.sum()*after
                else:V.loc[idx,c]*=factor
                adjustments.append(dict(seccion=s,categoria=c,polar=before,municipal=after,factor=factor,
                                        sin_perfil_circuital=no_profile))
        meta.update(missing_list_pba=False,valid_partidos=40,NE_estimado_municipal=True,
                    metodo_NE='Misma proporción de NE sobre positivos en todos los radios asignados de cada municipio; sin información intracircuital de NE.',
                    ne_totales_municipales={s:float(t.get('NE',0)) for s,t in targets.items()},
                    municipales_2009={s:dict(t) for s,t in targets.items()},
                    fuente_totales_pba='datos_oficiales/2009/complementos/merged_file_15_original.xls, hoja Sheet1; preparación auditada de mapas/mapa2009/datos_2009.py')
        dump(HERE/'ajustes_2009_municipales.json',adjustments)
    return V, ns, meta


def circuitos(year):
    # 2005/2007: aporte 2003 conserva los códigos INDRA y circunscripciones.
    y = 2003 if year <= 2007 else year
    f = ROOT / f'geometria/circuitos_serie/por_anio/{y}/aproximada/circuitos_argentina.geojson'
    features = json.loads(f.read_text(encoding='utf8'))['features']
    if year==2009:
        # CABA 2009 ya usa comunas y circuitos nuevos; la capa histórica de circunscripciones no corresponde.
        later=json.loads((ROOT/'geometria/circuitos_serie/por_anio/2011/aproximada/circuitos_argentina.geojson').read_text(encoding='utf8'))['features']
        features=[ft for ft in features if ft['properties']['codigo_distrito']!='01']+[ft for ft in later if ft['properties']['codigo_distrito']=='01']
    return [ft for ft in features if ft['properties']['codigo_distrito'] in ('01','02') and ft['properties'].get('codigo_circuito')]


def spatial(year, V, ns, rp, gs):
    features = circuitos(year)
    by = defaultdict(list)
    for ft in features:
        p=ft['properties']; d=p['codigo_distrito']; s=str(p['codigo_seccion_fuente']).zfill(3); c=cir(p['codigo_circuito'])
        # Buenos Aires: número de circuito único provincial; validar partido por nombre o código INDRA.
        k=(d,s if d=='01' and year <= 2007 else '',c)
        by[k].append(ft)
    CG, provenance, missing = {}, {}, []
    for k in V.index:
        d,s,c=k; q=(d,s if d=='01' and year<=2007 else '',c)
        fs=by.get(q,[])
        if not fs:
            fs=by.get((q[0],q[1],re.sub('[A-Z]+$','',c)),[])
        valid=[]
        for ft in fs:
            p=ft['properties']
            if d=='02':
                if p['sistema_codigos']=='usuario':
                    ok=str(p['codigo_seccion_fuente']).zfill(3)==s
                elif p.get('nombre_seccion'):
                    ok=norm(p['nombre_seccion'])==norm(ns[d,s])
                else:
                    ok=str(p['codigo_seccion_fuente']).zfill(3)==s
                if not ok: continue
            valid.append(ft)
        if valid:
            CG[k]=unary_union([shapely.make_valid(shape(ft['geometry'])) for ft in valid])
            provenance[k] = sorted({ft['properties']['id_fuente'] for ft in valid})
        else: missing.append(k)
    # Sin polígono: no se crea una ubicación ficticia. El volumen queda en el control.
    keys=list(CG); tree=shapely.STRtree([CG[k] for k in keys])
    reps=shapely.points([(g.representative_point().x,g.representative_point().y) for g in gs])
    hits=tree.query(reps,predicate='intersects'); r2c={}
    def ukey(k):
        return ('01',k[1]) if k[0]=='01' else ('02',norm(ns[k[:2]]))
    for i,j in zip(*hits):
        k=keys[j]
        if (rp.PROV[i]=='02' and k[0]=='01') or (rp.PROV[i]=='06' and k[0]=='02' and norm(rp.partido[i])==norm(ns[k[:2]])):
            r2c.setdefault(int(i),k)
    units=[]
    for i in range(len(rp)):
        if rp.PROV[i] != '02': units.append(('02',norm(rp.partido[i]))); continue
        # Comunas desde 2009: radio 2010 DEPTO 001..015; 2022, 007..105.
        if year>=2009:
            if census(year)==2001:
                # El censo 2001 es anterior a las comunas: asignación por punto a los circuitos de 2009.
                if i in r2c: units.append(ukey(r2c[i])); continue
            else:
                s=int(rp.DEPTO[i]) // (7 if census(year)==2022 else 1)
                units.append(('01',f'{s:03d}')); continue
        if i in r2c: units.append(ukey(r2c[i])); continue
        ks=[k for k in keys if k[0]=='01']
        if ks:
            nearest=min(ks,key=lambda k:CG[k].distance(reps[i]))
            units.append(ukey(nearest))
        else: units.append(('01','SIN_DATO'))
    # Excluir asociaciones de radio a circuito de otra comuna.
    r2c={i:k for i,k in r2c.items() if units[i]==ukey(k)}
    return CG, provenance, missing, units, r2c, ukey


def approximate_seats(CG, ns, ukey):
    loc=pd.read_csv(ROOT/'mapas/mapaAMBA2025radios/locales_amba2025.csv',dtype={'dist':str,'sec':str})
    loc=loc[loc.fuente!='centro_circuito'].copy()
    keys=list(CG); tree=shapely.STRtree([CG[k] for k in keys]); seats=defaultdict(list)
    # Un local se usa una sola vez aunque el polígono padre represente subdivisiones con letras.
    for r in loc.itertuples():
        hits=tree.query(Point(r.lon,r.lat),predicate='intersects')
        valid=[keys[j] for j in hits if keys[j][0]==r.dist and (r.dist=='01' or norm(ns[keys[j][:2]])==norm(r.seccion))]
        for k in valid:
            seats[k].append((r.lon,r.lat,float(r.electores)))
    no=[]
    for k in keys:
        if not seats[k]:
            p=CG[k].representative_point();seats[k]=[(p.x,p.y,1.)];no.append(k)
    return seats,no


def recover_seats(missing, ns):
    """Circuitos sin polígono: solo escuelas con código coincidente y partido verificado.
    Sigue siendo una referencia retrospectiva de 2025, no una localización histórica comprobada.
    """
    loc=pd.read_csv(ROOT/'mapas/mapaAMBA2025radios/locales_amba2025.csv',dtype={'dist':str,'sec':str})
    loc=loc[loc.fuente!='centro_circuito']
    found={}
    for k in missing:
        d,s,c=k
        rows=loc[(loc.dist==d)&(loc.sec==s)]
        rows=rows[[c in [cir(x) for x in re.split('[,;| ]+',str(v))] for v in rows.circuitos]]
        rows=rows[[d=='01' or norm(n)==norm(ns[d,s]) for n in rows.seccion]]
        if len(rows):found[k]=[(r.lon,r.lat,float(r.electores)) for r in rows.itertuples()]
    return found


def allocate(V, rp, gs, units, ukey, seats, r2c, variant='idw'):
    cats=list(V); A=np.zeros((len(rp),len(cats)))
    positive=[i for i,c in enumerate(cats) if not c.startswith('_')]
    voters=V[[c for c in V if c!='_ELOK']].sum(axis=1)
    centers=np.array([(g.centroid.x*KX,g.centroid.y*KY) for g in gs])
    byu=defaultdict(list); byc=defaultdict(list)
    for i,u in enumerate(units):byu[u].append(i)
    for i,k in r2c.items():byc[k].append(i)
    groups=defaultdict(list)
    for k in seats:groups[ukey(k)].append(k)
    fallback=0
    for u,ks in groups.items():
        idx=np.array(byu[u],dtype=int)
        assert len(idx),u
        weights=[]
        for k in ks:
            if variant=='pob':
                parent=(k[0],k[1],k[2].split('@')[0])
                ri=np.array(byc[parent],dtype=int);w=rp.POB.to_numpy(float)[ri]
                if not len(ri) or not w.sum():
                    lon,lat,_=seats[k][0];ri=idx[[np.argmin(np.hypot(*(centers[idx]-[lon*KX,lat*KY]).T))]];w=np.ones(1);fallback+=1
                weights.append((k,ri,w/w.sum(),1.));continue
            total=sum(s[2] for s in seats[k])
            for lon,lat,e in seats[k]:
                dd=np.maximum(np.hypot(*(centers[idx]-[lon*KX,lat*KY]).T),25.)
                w=1/dd**2;weights.append((k,idx,w/w.sum(),e/total))
        # Corte de un voto, como 2003/2025. Se conserva el aporte de cada circuito/local.
        for _ in range(30):
            total=np.zeros(len(rp))
            for k,ri,w,frac in weights:total[ri]+=w*frac*voters[k]
            dead=(total>0)&(total<1)
            if not dead.any():break
            changed=False;new=[]
            for k,ri,w,frac in weights:
                keep=~dead[ri]
                if keep.any() and not keep.all():ri=ri[keep];w=w[keep];w=w/w.sum();changed=True
                new.append((k,ri,w,frac))
            weights=new
            if not changed:break
        for k,ri,w,frac in weights:A[ri]+=np.outer(w*frac,V.loc[k,:].to_numpy(float))
    # Conservación por unidad y categoría contra la fuente, antes de redondear fichas.
    expected=defaultdict(lambda:np.zeros(len(cats)))
    for k in seats:expected[ukey(k)]+=V.loc[k,:].to_numpy(float)
    err=max((np.max(np.abs(A[byu[u]].sum(0)-v)) for u,v in expected.items()),default=0.)
    assert err<1e-6,err
    return A,float(err),fallback


def prepare(key):
    assert key in KEYS
    year=int(key[:4]);cen=census(year)
    _,rp,gs=radios(cen);rp=rp.copy()
    cand,lookup,labels=candidates(key)
    V,ns,meta=load_votes(key,lookup,labels)
    for c in V:
        if not c.startswith('_') and c not in cand:
            cand[c]=dict(n=c,base='#808080',logo='OTR')
    CG,provenance,missing,units,r2c,ukey=spatial(year,V,ns,rp,gs)
    seats,no=approximate_seats(CG,ns,ukey)
    recovered=recover_seats(missing,ns)
    seats.update(recovered)
    unresolved=[k for k in missing if k not in recovered]
    pending_units={ukey(k) for k in unresolved if V.loc[k,:].drop('_ELOK').sum()>0}
    # No mostrar el ganador de una unidad a la que le faltan votos de algún circuito.
    seats={k:v for k,v in seats.items() if ukey(k) not in pending_units}
    no=[k for k in no if k in seats]
    original_V=V.copy()
    local_stats={}
    if year==2015:
        from locales2015 import load
        tables,points,props,lctrl=load()
        d=tables['balotaje' if key.endswith('bal') else 'general'].copy()
        d=d[d.cargo_nombre.str.contains('DIPUTAD' if key.endswith('dip') else 'PRESIDENTE')].copy()
        d['parent']=list(zip(d.dist,d.sec,d.cir))
        d=d[d.parent.isin(V.index)].copy()
        def category(r):
            if r.votos_tipo=='POSITIVO':
                if key.endswith('dip'):return lookup.get((r.dist,str(r.agrupacion_id).zfill(4)),f'X{r.dist}_{str(r.agrupacion_id).zfill(4)}')
                return next(c for a,c in lookup.items() if a in norm(r.agrupacion_nombre))
            if r.votos_tipo in ('EN BLANCO','BLANCO','BLANCOS'):return '_BLA'
            if r.votos_tipo in ('NULO','NULOS'):return '_NUL'
            return '_IMP'
        d['cat']=[category(r) for r in d.itertuples()]
        # La tabla se usa solo para puntos con rangos cotejados y próximos a su circuito.
        invalid=set()
        for r in d[d.local>=0].drop_duplicates(['parent','local']).itertuples():
            if r.parent not in CG or CG[r.parent].distance(Point(*points[r.local]))*111320>300:
                invalid.add((r.parent,r.local))
        d.loc[[(r.parent,r.local) in invalid for r in d.itertuples()],'local']=-1
        d['ck']= [(p[0],p[1],p[2]+'@'+str(int(l))) for p,l in zip(d.parent,d.local)]
        NV=d.pivot_table(index='ck',columns='cat',values='v',aggfunc='sum',fill_value=0).astype(float)
        NV.index=pd.MultiIndex.from_tuples(NV.index,names=['d','s','c'])
        m=d.groupby(['dist','sec','cir','mid','mesa_tipo']).agg(el=('mesa_electores','first'),votes=('v','sum'),ck=('ck','first')).reset_index()
        m['el']=pd.to_numeric(m.el);m['el']=m.el*(m.votes>0)
        em=m.groupby('ck').el.sum()
        NV['_ELOK']=[em.get(k,0) for k in NV.index]
        NV=NV.reindex(columns=V.columns,fill_value=0)
        # Cotejo de categorías y electores con el agregado por circuito ya auditado.
        grouped=NV.copy();grouped.index=pd.MultiIndex.from_tuples([(a,b,c.split('@')[0]) for a,b,c in NV.index])
        grouped=grouped.groupby(level=[0,1,2]).sum()
        delta=(grouped.reindex(V.index).fillna(0)-V).abs().to_numpy().max()
        assert delta<1e-6,(key,delta)
        newseats={}
        for k in NV.index:
            parent=(k[0],k[1],k[2].split('@')[0]);local=int(k[2].split('@')[1])
            if local>=0:newseats[k]=[(*points[local],1.)]
            else:newseats[k]=seats[parent]
        local_stats=dict(locales_fuente_2015_verificados=lctrl['locales_identicos_2015'],
                         locales_2015_usados=len(set(d.loc[d.local>=0,'local'])),
                         proporcion_votos_con_local_2015=float(d.loc[d.local>=0,'v'].sum()/d.v.sum()),
                         error_cotejo_circuitos_2015=float(delta),
                         locales_fuera_de_circuito=len(invalid))
        V,seats=NV,newseats
    A,err,fallback=allocate(V,rp,gs,units,ukey,seats,r2c)
    P,perr,pfallback=allocate(V,rp,gs,units,ukey,seats,r2c,'pob')
    if year==2009:
        ni=list(V.columns).index('NE');posidx=[i for i,c in enumerate(V) if not c.startswith('_') and c!='NE']
        extra=[]
        for s,total in meta['ne_totales_municipales'].items():
            u=('02',norm(ns['02',s]));ri=np.array([i for i,x in enumerate(units) if x==u],int)
            for matrix in (A,P):
                w=matrix[np.ix_(ri,posidx)].sum(axis=1)
                assert w.sum()>0,(s,'sin perfil para NE')
                matrix[ri,ni]=w/w.sum()*total
            row=np.zeros(len(V.columns));row[ni]=total
            extra.append((('02',s,'NE_MUNICIPAL'),row))
        neframe=pd.DataFrame([v for _,v in extra],index=pd.MultiIndex.from_tuples([k for k,_ in extra],names=V.index.names),columns=V.columns)
        V=pd.concat([V,neframe])
        # Cotejo independiente contra cada total municipal, incluidas las listas menores y NE.
        for s,targets in meta['municipales_2009'].items():
            ri=[i for i,u in enumerate(units) if u==('02',norm(ns['02',s]))]
            for c,total in targets.items():
                j=list(V.columns).index(c)
                err=max(err,float(abs(A[ri,j].sum()-total)))
                perr=max(perr,float(abs(P[ri,j].sum()-total)))
        assert max(err,perr)<1e-6
    cats=list(V);pi=[i for i,c in enumerate(cats) if not c.startswith('_')]
    pos=A[:,pi].sum(1);ppos=P[:,pi].sum(1)
    ok=(pos>0)&(ppos>0)
    winners=np.array([cats[pi[i]] for i in A[:,pi].argmax(1)])
    pwin=np.array([cats[pi[i]] for i in P[:,pi].argmax(1)])
    ctrl=dict(key=key,censo=cen,radios=len(rp),poblacion=int(rp.POB.sum()),metodo='circuitos_escuelas2025_idw',
              circuitos=len(original_V),circuitos_con_geometria=len(CG),sin_geometria=[list(k) for k in unresolved],
              circuitos_sin_poligono_con_escuela2025=[list(k) for k in recovered],
              unidades_pendientes=[list(u) for u in sorted(pending_units)],
              votos_sin_geometria=float(V.loc[unresolved].drop(columns='_ELOK').to_numpy().sum()) if unresolved else 0,
              circuitos_sin_escuela=len(no),votantes_sin_escuela=float(original_V.loc[no].drop(columns='_ELOK').to_numpy().sum()) if no else 0,
              error_max_unidad_categoria=err,error_control_poblacion=perr,
              positivos_fuente=float(V[[c for c in V if not c.startswith('_')]].to_numpy().sum()),
              positivos_asignados=float(pos.sum()),radios_sin_votos=int((pos<.5).sum()),
              ganadores=dict(Counter(winners[pos>=.5])),
              coincidencia_ganador_control=float(np.mean(winners[ok]==pwin[ok])) if ok.any() else None,
              poblacion_en_radios_sin_votos=int(rp.POB[pos<.5].sum()),
              reservas=['Votos estimados por radio; no son resultados observados.',
                        'Escuelas y ponderadores de electores de 2025 aplicados retrospectivamente.',
                        'Cartografía de circuitos aproximada; no certifica vigencia histórica.',
                        'El control por población mide sensibilidad entre métodos; no valida acierto electoral.'],**meta,**local_stats)
    if local_stats:ctrl['metodo']='locales2015_verificados_y_respaldo2025_idw'
    if year==2009:
        excluded=(winners=='NE')&(pos>=.5)
        ctrl.update(metodo='perfiles_circuitales_ajustados_a_municipales_NE_proporcion_municipal',
                    radios_excluidos_NE=int(excluded.sum()),poblacion_radios_excluidos_NE=int(rp.POB[excluded].sum()),
                    NE_excluidos_por_partido=dict(Counter(rp.partido[excluded])),
                    positivos_estimados_radios_excluidos_NE=float(pos[excluded].sum()))
    rp['unit']=units
    data=dict(A=A,CATS=cats,radios=rp,candidates=cand,ctrl=ctrl,year=year,censo=cen,key=key,
              total_vector=V.sum().to_numpy(float),
              part_totals={p:V.loc[[k for k in V.index if ('Ciudad de Buenos Aires' if k[0]=='01' else norm(ns[k[:2]]))==p]].sum().to_numpy(float)
                           for p in ['Ciudad de Buenos Aires']+sorted({norm(ns[k[:2]]) for k in V.index if k[0]=='02'})},
              circuns={s:ns.get(('01',s),s) for d,s in set(units) if d=='01'},
              prov_circuitos={str(k):v for k,v in provenance.items()})
    pd.to_pickle(data,HERE/f'asignacion_{key}.pkl')
    dump(HERE/f'control_{key}.json',ctrl)
    print(key,json.dumps({k:ctrl[k] for k in ('radios','positivos_asignados','radios_sin_votos','error_max_unidad_categoria','circuitos_sin_escuela') }),flush=True)
    return data


if __name__=='__main__':
    for key in sys.argv[1:] or KEYS:prepare(key)
