"""Cobertura territorial por distrito de cada versión anual: qué parte de la provincia tiene algún circuito.

Necesita geopandas (no está en circuitos_busqueda/_deps). Referencia: Departamentos_2010 de CEUR-CONICET
disuelto por provincia. Mide superficie, no electores: un circuito urbano chico puede tener casi todo el padrón.
Escribe COBERTURA.json y COBERTURA.md.
"""
from pathlib import Path
import json,warnings
import geopandas as gpd
from shapely import make_valid
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parent
NAMES=['CABA','Buenos Aires','Catamarca','Córdoba','Corrientes','Chaco','Chubut','Entre Ríos','Formosa','Jujuy','La Pampa','La Rioja','Mendoza','Misiones','Neuquén','Río Negro','Salta','San Juan','San Luis','Santa Cruz','Santa Fe','Santiago del Estero','Tucumán','Tierra del Fuego']
# Código electoral de distrito (01 CABA ... 24 Tierra del Fuego) -> código INDEC de provincia
INDEC='02 06 10 14 18 22 26 30 34 38 42 46 50 54 58 62 66 70 74 78 82 86 90 94'.split()
EA='+proj=aea +lat_1=-25 +lat_2=-45 +lat_0=-35 +lon_0=-65 +datum=WGS84'
UMBRAL=90
prov=gpd.read_file(ROOT.parent/'Base deptos 1869-2022/Departamentos_2010.shp')
# Tierra del Fuego se mide sobre la Isla Grande: el Sector Antártico (950.000 km²) taparía todo lo demás.
prov=prov[~prov.DEPTO.isin(['Sector Antartico','Islas del Atlantico Sur'])].dissolve('PROV_COD').to_crs(EA)
prov=prov.geometry.buffer(0)
cache={};rows=[]
for year in range(2003,2027):
    for mode in ['documentada','aproximada']:
        g=gpd.read_file(ROOT/'por_anio'/str(year)/mode/'circuitos_argentina.geojson')
        if not len(g):continue
        g=g[g.geometry.notna()].to_crs(EA);g['geometry']=g.geometry.apply(make_valid)
        for d,sub in g.groupby('codigo_distrito'):
            # La misma combinación de fuentes da la misma cobertura: se calcula una vez.
            key=(d,tuple(sorted(set(zip(sub.id_fuente,sub.indice_fuente)))))
            if key not in cache:
                area=prov[INDEC[int(d)-1]];u=sub.union_all()
                cache[key]=round(100*u.intersection(area).area/area.area,1)
            rows.append(dict(anio=year,version=mode,distrito=d,nombre=NAMES[int(d)-1],cobertura_superficie_pct=cache[key],fuentes=sorted(set(sub.id_fuente))))
        print(year,mode,flush=True)
(ROOT/'COBERTURA.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
years=list(range(2003,2027))
table={(r['distrito'],r['anio']):r['cobertura_superficie_pct'] for r in rows if r['version']=='aproximada'}
low=sorted({r['distrito'] for r in rows if r['version']=='aproximada' and r['cobertura_superficie_pct']<UMBRAL})
lines=['# Cobertura territorial de la versión aproximada','',f'Porcentaje de la superficie de cada provincia (Departamentos_2010, CEUR-CONICET) cubierto por algún circuito; en Tierra del Fuego, solo la Isla Grande (Río Grande y Ushuaia). Mide superficie, no electores. Se listan los distritos que en algún año quedan por debajo del {UMBRAL} %; el resto supera ese valor en todos los años. Detalle de ambas versiones en [COBERTURA.json](COBERTURA.json). Generado con `cobertura.py`.','','| Distrito | '+' | '.join(str(y) for y in years)+' |','|---|'+'---:|'*len(years)]
for d in low:lines.append(f'| {NAMES[int(d)-1]} | '+' | '.join(f'{table.get((d,y),"")}' for y in years)+' |')
(ROOT/'COBERTURA.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('distritos bajo el umbral:',[NAMES[int(d)-1] for d in low])
