"""Digitalización aproximada del esquema aportado, sin numeración oficial.

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
from lxml import html
from svgelements import Path as SVGPath
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'mapas/mapa1951'))
from geometria_1951 import polygon, only_polygons, d_path
source=HERE/'fuente_aportada.png'
atlas=ROOT/'mapas/mapa1951/atlas_1951.html'
gray=cv2.imread(str(source),cv2.IMREAD_GRAYSCALE)
# Recorte de la lámina inferior, rotulada 1954. Coordenadas en la imagen aportada.
x0,y0,x1,y1=130,120,249,225
crop=gray[y0:y1,x0:x1]
white=(crop>190).astype('uint8')
n,labels,stats,centers=cv2.connectedComponentsWithStats(white,connectivity=4)
chosen=[i for i in range(1,n)if stats[i,4]>=100 and stats[i,0]>0 and stats[i,1]>0 and stats[i,0]+stats[i,2]<crop.shape[1] and stats[i,1]+stats[i,3]<crop.shape[0]]
chosen=sorted(chosen,key=lambda i:(centers[i,1],centers[i,0]))
assert len(chosen)==14,(len(chosen),stats.tolist())
seed=np.zeros_like(labels,dtype='int16')
for j,i in enumerate(chosen,1):seed[labels==i]=j
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
original=list(shapely.coverage_simplify(original,2.0,simplify_boundary=False))
assert neighbors(original)==adjacency,'El suavizado no debe cambiar las vecindades.'
smooth_displacement=max(a.hausdorff_distance(b)for a,b in zip(raster_original,original))
src=unary_union(original)
preview_original=list(original)
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
x,y,X,Y=src.bounds;a,b,A,B=dst.bounds
sx,sy=(A-a)/(X-x),(B-b)/(Y-y)
affine=[sx,0,0,sy,a-sx*x,b-sy*y]
base=[affine_transform(shapely.segmentize(g,1.5),affine)for g in original]
joined=unary_union(base);sc,tc=joined.centroid,dst.centroid
controls=[];dest=[]
for angle in np.linspace(0,2*np.pi,48,endpoint=False):
    dx,dy=np.cos(angle),np.sin(angle)
    def edge(g,c):
        coords=shapely.get_coordinates(g.boundary.intersection(LineString([(c.x,c.y),(c.x+dx*100,c.y+dy*100)])))
        return max(coords,key=lambda q:np.sum((q-np.array([c.x,c.y]))**2))if len(coords)else None
    s,t=edge(joined,sc),edge(dst,tc)
    if s is not None and t is not None and not any(np.linalg.norm(s-v)<.00001 for v in controls):controls.append(s);dest.append(t)
controls.append(np.array([sc.x,sc.y]));dest.append(np.array([tc.x,tc.y]))
warp=RBFInterpolator(np.array(controls),np.array(dest),kernel='thin_plate_spline',smoothing=.00001)
regions=[];claimed=Polygon()
for g in base:
    g=only_polygons(shapely.make_valid(shapely.transform(g,warp)))
    g=only_polygons(g.intersection(dst).difference(claimed))
    assert not g.is_empty
    regions.append(g);claimed=unary_union([claimed,g])
gap=only_polygons(dst.difference(claimed));unfilled=gap.area
step=.002
while not gap.is_empty and gap.area>1e-10 and step<100:
    for j,g in enumerate(regions):
        added=only_polygons(gap.intersection(g.buffer(step)))
        if not added.is_empty:
            regions[j]=only_polygons(unary_union([g,added]));gap=only_polygons(gap.difference(added))
    step*=2
assert gap.area<1e-8
assert all(g.is_valid and not g.is_empty for g in regions)
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
        props=dict(id_trazo=i,circ_of=None,anio=1954,distrito='Capital Federal',certeza='Trazado aproximado; número oficial no identificado',costa='SHP histórico de Capital; costa nativa sin simplificar')
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
colors=plt.get_cmap('tab20')
for i,(raw,g)in enumerate(zip(preview_original,regions),1):
    center=raw.representative_point();axes[0].text(center.x,center.y,str(i),ha='center',va='center',fontsize=9,color='#9c1313',weight='bold',bbox=dict(facecolor='white',edgecolor='none',alpha=.7,pad=.4))
    for p in [g]if g.geom_type=='Polygon'else g.geoms:
        xy=np.array(p.exterior.coords);axes[1].fill(xy[:,0],xy[:,1],color=colors((i-1)%20),edgecolor='#555',linewidth=.65)
    center=g.representative_point();axes[1].text(center.x,center.y,str(i),ha='center',va='center',fontsize=9,weight='bold')
for p in [dst]if dst.geom_type=='Polygon'else dst.geoms:
    xy=np.array(p.exterior.coords);axes[1].plot(xy[:,0],xy[:,1],color='#111',linewidth=1)
axes[0].set_title('Imagen aportada · esquema de 1954')
axes[1].set_title('Giro 90° antihorario · costa del SHP')
axes[1].invert_yaxis()
for axis in axes:axis.set_aspect('equal');axis.axis('off')
fig.suptitle('Capital Federal, 1954 · digitalización aproximada',fontsize=16)
fig.text(.5,.015,'Los números son identificadores de trazado; NO son números oficiales de circunscripción.',ha='center',fontsize=10)
axes[1].annotate('N',xy=(.94,.94),xytext=(.94,.80),xycoords='axes fraction',ha='center',va='center',fontsize=12,weight='bold',arrowprops=dict(arrowstyle='-|>',color='#111',lw=1.5))
fig.savefig(HERE/'vista_previa.png',dpi=170);plt.close(fig)
report=dict(recintos=14,ids='id_trazo 1–14, sin equivalencia oficial',circ_of=None,crs='EPSG:4326',fuente_imagen=source.name,sha256_imagen=hashlib.sha256(source.read_bytes()).hexdigest(),recorte=[x0,y0,x1,y1],umbral=190,giro_imagen='90 grados antihorarios (270 horarios en coordenadas de imagen)',verificacion_orientacion='Esquema 1951 de la misma lámina frente a SVG 1951; ORIENTACION.json',contorno_shp='Capital Federal, base histórica del atlas 1948 (geom4673)',cache_shp=str(raw_shp.relative_to(ROOT)),sha256_contorno_nativo=hashlib.sha256(coast_geo.wkb).hexdigest(),vertices_costa=int(shapely.get_num_coordinates(coast_geo)),simplificacion_costa=False,suavizado_interiores_pixeles=2.0,desplazamiento_maximo_interiores_pixeles=smooth_displacement,vecindades_conservadas=True,numero_vecindades=len(adjacency),controles_perimetro=len(controls),hueco_antes_cierre_pixeles_poster=unfilled,diferencia_contorno_final=coverage.symmetric_difference(dst).area,solapamiento=overlap,geometrias_validas=True,advertencia='Límites interiores aproximados de una imagen pequeña sin numeración; sin votos asociados.')
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
