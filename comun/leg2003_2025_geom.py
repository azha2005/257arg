"""Geometría histórica para diputados 2003–2025; no altera los atlas anteriores."""
from pathlib import Path
import importlib.util, math, pickle, sys
import shapely
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'../mapas/mapa2013'))
from shp import read_shp, read_dbf
spec=importlib.util.spec_from_file_location('geom_base2010',ROOT/'../mapas/mapa2013/geom.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
KX=base.KX
TERR=set()

def load(year):
    shared=ROOT/'../mapas/mapa2025/units_leg2003_2025.pkl'
    if year>=2019 and shared.exists():
        return pickle.load(open(shared,'rb'))
    if year<=2007:
        b=ROOT/'../geometria/Base deptos 1869-2022/Departamentos_2001'
        units=[]
        for g,r in zip(read_shp(str(b)+'.shp'),read_dbf(str(b)+'.dbf')):
            p=base.PROV[r['PROV_COD']];n=r['DEPTO'].strip()
            if p=='Capital Federal' or n=='Sector Antartico':continue
            n=base.FIX.get((p,n),n); gg=base.to_poly(g)
            if p=='Tierra del Fuego' and n=='Islas del Atlantico Sur':n='Islas Malvinas';gg=gg.intersection(base.MALVINAS)
            units.append(dict(prov=p,name=n,kind='partido' if p=='Buenos Aires' else 'departamento',link=[r['LINK_']],geom=gg))
        # El shapefile censal tiene distritos escolares; las elecciones usan 28 circunscripciones.
        for n,(par,g) in pickle.load(open(ROOT/'../mapas/mapa2001/caba28.pkl','rb')).items():
            units.append(dict(prov='Capital Federal',name=f'Circ. {n:02d}',kind='circunscripción',link=[f'CF{n:02d}'],geom=g,parroquia=par))
        acc={}
        for u in units:
            k=(u['prov'],u['name'])
            if k in acc:acc[k]['geom']=unary_union([acc[k]['geom'],u['geom']])
            else:acc[k]=u
        return list(acc.values())
    out=base.load()
    if year>=2019:
        # Departamento creado por ley 1186, sancionada 27-oct-2017 (después de la
        # elección de 22-oct). La transformación municipal de 2012 no lo creó.
        spec=importlib.util.spec_from_file_location('geom_tdf',ROOT/'../mapas/mapa2027/geom.py')
        tdf=importlib.util.module_from_spec(spec);spec.loader.exec_module(tdf)
        out=tdf._split_tdf(out)
    return out

def description(year):
    if year<=2007:return 'Departamentos de 2001 y 28 circunscripciones de Capital Federal (ajustadas al contorno)'
    if year<2019:return 'Departamentos de 2010, 15 comunas de Capital Federal y Lezama separado'
    return 'Departamentos de 2010, 15 comunas, Lezama y Tolhuin separados con polígonos INDEC 2022 recortados al contorno histórico'
