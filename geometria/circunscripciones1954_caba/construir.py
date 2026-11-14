"""Digitalización del esquema numerado de Primera Plana, n.º 312, p. 58.

La costa exterior se toma del SHP histórico de Capital, no de la imagen pequeña.
"""
from pathlib import Path
import hashlib, json, math, sys, zipfile, pickle
import cv2, numpy as np, shapely, shapefile
from shapely.geometry import Polygon, LineString, box, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.affinity import affine_transform, rotate
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import distance_transform_edt
from pyproj import CRS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'mapas/mapa1951'))
from geometria_1951 import only_polygons, d_path
source = HERE / 'primera_plana_312_p58.png'
crop = cv2.imread(str(source), cv2.IMREAD_GRAYSCALE)
assert crop is not None
threshold = 150
white = (crop >= threshold).astype('uint8')
_, labels, stats, _ = cv2.connectedComponentsWithStats(white, connectivity=4)

# Puntos dentro de cada recinto, en orden de numeración impresa (x, y).
anchors = [(168,147), (195,85), (244,105), (289,59), (319,117),
           (324,173), (370,164), (310,227), (208,213), (210,242),
           (217,278), (212,307), (222,344), (384,219)]
components = [int(labels[y,x]) for x,y in anchors]
interior = {i for i in range(1,len(stats)) if i != labels[0,0] and stats[i,4] > 250}
assert len(components) == len(set(components)) == 14 and set(components) == interior
numbering = json.loads((HERE/'numeracion_adoptada.json').read_text(encoding='utf8'))
by_trazo = {r['id_trazo']:r['circ_adoptada'] for r in numbering['correspondencias']}
assert set(by_trazo) == set(by_trazo.values()) == set(range(1,15))
seed = np.zeros_like(labels, dtype='int16')
for trazo, circ in by_trazo.items():
    seed[labels == components[circ-1]] = trazo
contours,_=cv2.findContours(1-white,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
outer=max(contours,key=cv2.contourArea)
mask=np.zeros_like(white);cv2.drawContours(mask,[outer],-1,1,cv2.FILLED)
# Reparte únicamente el grosor de la tinta entre recintos vecinos. No hay votos.
_,nearest=distance_transform_edt(seed==0,return_indices=True)
partition=seed[tuple(nearest)]*mask
original=[]
for j in range(1,15):
    rectangles=[]
    for y in range(partition.shape[0]):
        row=(partition[y]==j).astype('int8')
        edges=np.flatnonzero(np.diff(np.r_[0,row,0]))
        for a,b in zip(edges[::2],edges[1::2]):rectangles.append(box(a,y,b,y+1))
    original.append(unary_union(rectangles))
# Suaviza escalones del píxel con simplificación de cobertura: una frontera
# compartida se simplifica una sola vez, sin abrir huecos entre vecinos.
def neighbors(gs):
    return {(i+1,j+1)for i in range(len(gs))for j in range(i+1,len(gs))if gs[i].boundary.intersection(gs[j].boundary).length>1e-7}
raster_original=list(original)
adjacency=neighbors(original)
# Douglas-Peucker por tramo: cada frontera entre dos nudos se simplifica una
# sola vez, conservando sus extremos y los quiebres que se apartan más de
# DP_TOL píxeles (los escalones de la revista). Queda rectilínea, sin los
# microquiebres del píxel. Después se poligoniza y cada cara vuelve a su recinto.
DP_TOL=1.6
def dp_coverage(polys,tol):
    net=shapely.line_merge(unary_union([g.boundary for g in polys]))
    segs=[shapely.simplify(e,tol,preserve_topology=False) for e in getattr(net,'geoms',[net])]
    faces=list(shapely.polygonize(segs).geoms)
    out=[[] for _ in polys]
    for f in faces:
        q=f.representative_point();j=max(range(len(polys)),key=lambda k:polys[k].intersection(f).area)
        out[j].append(f)
    return [unary_union(o) for o in out]
original=dp_coverage(original,DP_TOL)
assert abs(sum(g.area for g in original)-unary_union(original).area)<1e-6
assert neighbors(original)==adjacency,"El Douglas-Peucker no debe cambiar las vecindades."
assert neighbors(original)==adjacency,'El suavizado no debe cambiar las vecindades.'
smooth_displacement=max(a.hausdorff_distance(b)for a,b in zip(raster_original,original))
src=unary_union(original)
src_before_rotation_centroid=src.centroid
preview_original=list(original)
district13 = next(t for t,n in by_trazo.items() if n == 13)
assert preview_original[district13-1].geom_type == 'Polygon'
# El paso angosto del 13 se cierra artificialmente con un umbral de 170.
# A 150, el lóbulo rotulado 13 y el brazo en zigzag pertenecen al mismo recinto.
assert labels[344,222] == labels[318,288] == components[12]
# La lámina está girada respecto al norte del SVG. El esquema 1951 de la
# misma lámina se coteja con las 28 geometrías 1951 en ORIENTACION.json:
# 270° en coordenadas de imagen = 90° antihorarios vistos en pantalla.
original=[rotate(g,270,origin=src.centroid)for g in original]
src=unary_union(original)

raw_shp=ROOT/'mapas/mapa1948/units_raw.pkl'
raw_units=pickle.loads(raw_shp.read_bytes())
coast_geo=unary_union([u['geom']for u in raw_units if u['prov']=='Capital Federal'])
def project(a):
    a=a.copy();a[:,0]=(a[:,0]+73.5708041)*math.cos(math.radians(38))*44+643
    a[:,1]=(-21.7807776-a[:,1])*44+150
    return a
dst=only_polygons(shapely.make_valid(shapely.transform(coast_geo,project)))
coast_path=d_path(dst,9)
assert dst.is_valid and not dst.is_empty
# Costa nativa del SHP, sin la simplificación de pantalla del SVG.
# Ajuste del dibujo al contorno real (14-nov-2026, auditoría).
# 1) Afín con giro fino que maximiza la coincidencia de los contornos.
# 2) Esquinas del contorno de la revista emparejadas con su punto del contorno
#    real (General Paz, Núñez, Riachuelo); entre esquinas, correspondencia
#    densa por fracción de longitud. La costa real se cierra solo para medir
#    longitudes (dársenas); el recorte final usa la costa nativa sin cambios.
from scipy.optimize import minimize
c_rot=src_before_rotation_centroid
def affine_params(v):
    th,sx,sy,tx,ty=v;c,s=math.cos(th),math.sin(th)
    return [sx*c,-sy*s,sx*s,sy*c,tx,ty]
x,y,X,Y=src.bounds;a,b,A,B=dst.bounds
v0=[0,(A-a)/(X-x),(B-b)/(Y-y),0,0]
cx,cy=src.centroid.x,src.centroid.y
def placed(v,g):
    g=affine_transform(g,[1,0,0,1,-cx,-cy]);g=affine_transform(g,affine_params(v))
    return affine_transform(g,[1,0,0,1,dst.centroid.x+v[3],dst.centroid.y+v[4]])
v0[3]=v0[4]=0
def cost(v):
    g=placed(v,src);return 1-g.intersection(dst).area/g.union(dst).area
fit=minimize(cost,v0,method='Nelder-Mead',options=dict(xatol=1e-4,fatol=1e-6,maxiter=4000))
outline_iou=1-fit.fun
base=[placed(fit.x,g)for g in original]
joined=unary_union(base)
size=math.sqrt(dst.area)
# Esquinas del contorno de la revista (píxeles de la imagen) y su punto en el
# contorno real (lon, lat), leído sobre la costa nativa del SHP. Solo estas
# esquinas deforman el dibujo: el resto sigue el afín, así el interior
# queda como en la revista y no se ondula.
landmarks=[
    ((78,135),(-58.4608,-34.7046)),   # General Paz y Riachuelo (Puente La Noria)
    ((202,20),(-58.5286,-34.6546)),   # General Paz, quiebre sur
    ((290,25),(-58.5301,-34.6160)),   # General Paz, Liniers
    ((423,95),(-58.4998,-34.5490)),   # General Paz, quiebre norte
    ((456,175),(-58.4580,-34.5285)),  # General Paz y el río (Núñez)
    ((222,352),(-58.3584,-34.6387)),  # Vuelta de Rocha
    ((303,330),None),  # muesca del borde inferior: al punto de costa más cercano
    ((349,324),None),  # esquina del borde inferior: ídem
    ((158,218),(-58.4233,-34.6626)),  # quiebre del Riachuelo (Pompeya)
]
def to_base(pt):
    q=rotate(shapely.Point(pt),270,origin=c_rot);return placed(fit.x,q)
controls=[];dest=[]
coast_line=max(getattr(dst,'geoms',[dst]),key=lambda p:p.area).exterior
for px,ll in landmarks:
    bp=to_base(px)
    q=project(np.array([ll]))[0] if ll else np.array(shapely.get_coordinates(coast_line.interpolate(coast_line.project(bp)))[0])
    controls.append((bp.x,bp.y));dest.append(tuple(q))
# Puntos intermedios del borde: en el dibujo, a la fracción f del tramo recto
# entre dos esquinas; en la costa real, a la misma fracción de longitud sobre
# la costa suavizada (las dársenas no cuentan) y llevados a la costa nativa.
coast_smooth=dst.buffer(.03*size,join_style=2).buffer(-.03*size,join_style=2)
smooth_line=max(getattr(coast_smooth,'geoms',[coast_smooth]),key=lambda p:p.area).exterior
between=[((222,352),(303,330),.5)]
target={tuple(px):np.array(d) for (px,_),d in zip(landmarks,dest)}
for p0,p1,f in between:
    s0=smooth_line.project(shapely.Point(target[p0]));s1=smooth_line.project(shapely.Point(target[p1]))
    L=smooth_line.length
    if abs(s1-s0)>L/2: s1=s1+L if s1<s0 else s1-L
    q=smooth_line.interpolate((s0+f*(s1-s0))%L);q=coast_line.interpolate(coast_line.project(q))
    px=(p0[0]+f*(p1[0]-p0[0]),p0[1]+f*(p1[1]-p0[1]));bp=to_base(px)
    controls.append((bp.x,bp.y));dest.append((q.x,q.y))
# Deformación de placa delgada exacta en las esquinas; se aplica solo a los
# vértices, de modo que cada tramo recto del dibujo sigue recto.
warp=RBFInterpolator(np.array(controls),np.array(dest),kernel='thin_plate_spline',smoothing=0)
regions=[];claimed=Polygon()
for g in base:
    g=only_polygons(shapely.make_valid(shapely.transform(g,warp)))
    g=only_polygons(g.intersection(dst).difference(claimed))
    assert not g.is_empty
    regions.append(g);claimed=unary_union([claimed,g])
def fill(regions,gap,step=.002):
    while not gap.is_empty and gap.area>1e-10 and step<100:
        for j,g in enumerate(regions):
            added=only_polygons(gap.intersection(g.buffer(step,join_style=2)))
            if not added.is_empty:
                regions[j]=only_polygons(unary_union([g,added]));gap=only_polygons(gap.difference(added))
        step*=2
    return gap
gap=only_polygons(dst.difference(claimed));unfilled=gap.area
gap=fill(regions,gap)
assert gap.area<1e-8
# Rectifica las fronteras compartidas después del ajuste al contorno.
# Conserva el contorno y las uniones entre recintos.
before_straightening = regions
final_tolerance = 0.01
regions = list(shapely.coverage_simplify(regions, final_tolerance, simplify_boundary=False))
assert neighbors(regions) == neighbors(before_straightening)
# Quita espinas y astillas de ancho casi nulo que deja el relleno (apertura
# morfológica mínima) y reparte lo quitado entre los vecinos, sin tocar la costa.
SPIKE=.001
for j,g in enumerate(regions):
    regions[j]=only_polygons(g.buffer(-SPIKE,join_style=2).buffer(SPIKE,join_style=2).intersection(g))
gap=only_polygons(dst.difference(unary_union(regions)))
gap=fill(regions,gap,step=.0005)
assert gap.area<1e-8
assert neighbors(regions) == neighbors(before_straightening)
assert unary_union(regions).symmetric_difference(dst).area < 1e-8
assert all(g.is_valid and not g.is_empty for g in regions)
parts13 = list(getattr(regions[district13-1], 'geoms', [regions[district13-1]]))
assert max(part.area for part in parts13) > .99 * regions[district13-1].area

coverage=unary_union(regions)
assert coverage.symmetric_difference(dst).area<1e-8
overlap=sum(g.area for g in regions)-coverage.area
assert abs(overlap)<1e-8,overlap
def inverse(a):
    a=a.copy();a[:,0]=(a[:,0]-643)/(math.cos(math.radians(38))*44)-73.5708041
    a[:,1]=-21.7807776-(a[:,1]-150)/44
    return a
out=HERE/'shp';out.mkdir(exist_ok=True)
features=[]
with shapefile.Writer(str(out/'caba_1954_trazado_aproximado'),shapeType=shapefile.POLYGON,encoding='utf8')as writer:
    for name,typ,size in [('id_trazo','N',3),('circ_of','N',3),('anio','N',4),('distrito','C',40),('certeza','C',80),('costa','C',80)]:writer.field(name,typ,size)
    for i,g in enumerate(regions,1):
        geo=shapely.set_precision(only_polygons(shapely.make_valid(shapely.transform(g,inverse))),1e-9);parts=[]
        for p in [geo]if geo.geom_type=='Polygon'else geo.geoms:
            p=orient(p,sign=-1);parts.append(list(p.exterior.coords));parts.extend(list(r.coords)for r in p.interiors)
        writer.poly(parts)
        props=dict(id_trazo=i,circ_of=by_trazo[i],anio=1954,distrito='Capital Federal',certeza='Número impreso en Primera Plana; trazado aproximado',costa='SHP histórico de Capital; costa nativa sin simplificar')
        writer.record(*props.values())
        features.append(dict(type='Feature',properties=props,geometry=mapping(geo)))
(out/'caba_1954_trazado_aproximado.prj').write_text(CRS.from_epsg(4326).to_wkt(version='WKT1_ESRI'),encoding='ascii')
(out/'caba_1954_trazado_aproximado.cpg').write_text('UTF-8',encoding='ascii')
(out/'caba_1954_trazado_aproximado.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False,separators=(',',':')),encoding='utf8')
# Mantiene un contorno SVG idéntico, separado del dibujo de los recintos.
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+f'{a-.3} {b-.3} {A-a+.6} {B-b+.6}'+'">'
for i,g in enumerate(regions,1):svg+=f'<path id="trazo_{i:02d}" d="{d_path(g,7)}" fill="hsl({i*137.5%360:.1f},45%,80%)" stroke="#333" stroke-width=".018"/>'
svg+=f'<path id="costa_svg_referencia" d="{coast_path}" fill="none" stroke="#111" stroke-width=".035"/></svg>'
(HERE/'caba_1954_aproximado.svg').write_text(svg,encoding='utf8')

fig,axes=plt.subplots(1,2,figsize=(11,6),layout='constrained')
axes[0].imshow(crop,cmap='gray',vmin=0,vmax=255)
from shapely.ops import polylabel
comparison_regions=[rotate(g,90,origin=dst.centroid) for g in regions]
comparison_coast=rotate(dst,90,origin=dst.centroid)
for i,(raw,g)in enumerate(zip(preview_original,comparison_regions),1):
    x,y=anchors[by_trazo[i]-1];axes[0].text(x,y,str(by_trazo[i]),ha='center',va='center',fontsize=9,color='#9c1313',weight='bold',bbox=dict(facecolor='white',edgecolor='none',alpha=.7,pad=.4))
    for p in [g]if g.geom_type=='Polygon'else g.geoms:
        xy=np.array(p.exterior.coords);axes[1].fill(xy[:,0],xy[:,1],color='#f1a54a' if by_trazo[i] == 13 else '#dce9f3',edgecolor='#555',linewidth=.65)
    largest=max(g.geoms,key=lambda p:p.area) if g.geom_type=='MultiPolygon' else g
    center=polylabel(largest,tolerance=.01);axes[1].text(center.x,center.y,str(by_trazo[i]),ha='center',va='center',fontsize=9,weight='bold',bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=1))
for p in [comparison_coast] if comparison_coast.geom_type=='Polygon' else comparison_coast.geoms:
    xy=np.array(p.exterior.coords);axes[1].plot(xy[:,0],xy[:,1],color='#111',linewidth=1)
axes[0].set_title('Primera Plana n.º 312, p. 58')
axes[1].set_title('Retrazado · orientación de la revista')
axes[1].invert_yaxis()
for axis in axes:axis.set_aspect('equal');axis.axis('off')
fig.suptitle('Capital Federal, 1954 · digitalización aproximada',fontsize=16)
fig.text(.5,.015,'Numeración de Primera Plana. Límites interiores aproximados.',ha='center',fontsize=10)
fig.savefig(HERE/'vista_previa.png',dpi=170);plt.close(fig)
report=dict(recintos=14,ids='id_trazo conservado; circ_of según Primera Plana',circ_of=by_trazo,crs='EPSG:4326',fuente_imagen=source.name,sha256_imagen=hashlib.sha256(source.read_bytes()).hexdigest(),pagina_impresa=58,pagina_pdf=62,anclas=anchors,umbral=threshold,giro_imagen='90 grados antihorarios (270 horarios en coordenadas de imagen)',verificacion_orientacion='Orientación de Primera Plana cotejada con el trazado anterior',contorno_shp='Capital Federal, base histórica del atlas 1948 (geom4673)',cache_shp=str(raw_shp.relative_to(ROOT)),sha256_contorno_nativo=hashlib.sha256(coast_geo.wkb).hexdigest(),vertices_costa=int(shapely.get_num_coordinates(coast_geo)),simplificacion_costa=False,tolerancia_rectificacion_poster=final_tolerance,simplificacion_douglas_peucker_pixeles=DP_TOL,apertura_espinas_poster=SPIKE,desplazamiento_maximo_interiores_pixeles=smooth_displacement,vecindades_conservadas=True,numero_vecindades=len(adjacency),controles_perimetro=len(controls),esquinas_contorno=[[list(px),ll] for px,ll in landmarks],coincidencia_contorno_afin=outline_iou,hueco_antes_cierre_pixeles_poster=unfilled,diferencia_contorno_final=coverage.symmetric_difference(dst).area,solapamiento=overlap,geometrias_validas=True,advertencia='Límites interiores aproximados del esquema de Primera Plana.')
(HERE/'CONTROL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
reader=shapefile.Reader(str(out/'caba_1954_trazado_aproximado'))
assert len(reader)==14
from shapely.geometry import shape
assert all(shape(s.__geo_interface__).is_valid for s in reader.shapes())
with zipfile.ZipFile(HERE/'CABA_1954_SHP_aproximado.zip','w',zipfile.ZIP_DEFLATED)as z:
    for f in out.iterdir():z.write(f,f.name)
    for name in ('LEEME.md','CONTROL.json','ORIENTACION.json','vista_previa.png'):
        if (HERE/name).exists():z.write(HERE/name,name)
print(json.dumps(report,ensure_ascii=False,indent=2))
