from pathlib import Path
import sys,json,collections,math,statistics
ROOT=Path(__file__).resolve().parent;SRC=ROOT.parent/'circuitos_busqueda'
sys.path.insert(0,str(SRC/'_deps'))
from shapely.geometry import shape,GeometryCollection
from pyproj import Geod
geod=Geod(ellps='WGS84');out=[]
def group(path):
    result=collections.defaultdict(list)
    for f in json.loads(path.read_text(encoding='utf-8'))['features']:
        p=f['properties'];c=str(p.get('circuito') or '')
        if not c[:1].isdigit():continue
        try:
            g=shape(f['geometry'])
            if not g.is_empty:result[(str(p.get('coddepto')),c)].append(g)
        except Exception:pass
    return {k:GeometryCollection(v).centroid for k,v in result.items()}
for p in sorted((SRC/'galeano/2021').glob('*.geojson')):
    a=group(p);b=group(SRC/'galeano/2025'/p.name);vectors=[]
    for k in set(a)&set(b):
        az,_,meters=geod.inv(a[k].x,a[k].y,b[k].x,b[k].y)
        vectors.append((meters*math.sin(math.radians(az)),meters*math.cos(math.radians(az))))
    if not vectors:continue
    dx=statistics.median(v[0] for v in vectors);dy=statistics.median(v[1] for v in vectors);length=math.hypot(dx,dy)
    residual=statistics.median(math.hypot(x-dx,y-dy) for x,y in vectors)
    out.append(dict(distrito_archivo=p.stem,claves_comunes=len(vectors),mediana_delta_este_m=round(dx,2),mediana_delta_norte_m=round(dy,2),desplazamiento_mediano_vector_m=round(length,2),residuo_mediano_m=round(residual,2),alerta_desplazamiento_coherente=len(vectors)>=10 and length>100 and residual<length*.25,nota='Indicio cartográfico, no demostración de causa ni prueba normativa. No se aplica transformación correctora.'))
dest=ROOT/'cambios';dest.mkdir(exist_ok=True);(dest/'auditoria_desplazamientos.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([r for r in out if r['alerta_desplazamiento_coherente']],ensure_ascii=False,indent=2))
