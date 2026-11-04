"""Adapta los trazos de circunscripción, sin convertirlos en departamentos.

El SVG aporta las divisiones internas. El SHP histórico aporta contornos y
proyección. La adaptación es cartográfica aproximada, no una delimitación legal.
"""
from collections import defaultdict
import copy, math, pickle
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from shapely.affinity import affine_transform
from scipy.interpolate import RBFInterpolator

def polygon(path):
    rings=[]
    for sub in path.as_subpaths():
        pts=[]
        for seg in sub:
            if seg.start is None or seg.end is None: continue
            if type(seg).__name__=='Move':continue
            steps=1 if type(seg).__name__ in ('Line','Close') else max(3,int(abs(seg.end-seg.start)/3))
            pts.extend((seg.point(k/steps).x,seg.point(k/steps).y)for k in range(steps))
        if len(pts)>2:
            g=shapely.make_valid(Polygon(pts))
            if not g.is_empty:rings.append(g)
    return unary_union(rings)

def only_polygons(g):
    if g.geom_type in ('Polygon','MultiPolygon'): return g
    return unary_union([p for p in getattr(g,'geoms',[]) if p.geom_type in ('Polygon','MultiPolygon')])

def d_path(g,precision=2):
    def ring(r):return 'M'+'L'.join(f'{x:.{precision}f} {y:.{precision}f}'for x,y in r.coords)+'Z'
    return ''.join(ring(p.exterior)+''.join(ring(h)for h in p.interiors)for p in ([g]if g.geom_type=='Polygon'else getattr(g,'geoms',[]))if p.geom_type=='Polygon')

def build(units, paths, root):
    # Misma proyección que el atlas 1912: equirectangular, cos(38°), 44 px/grado.
    raw=pickle.load(open(root/'mapas/mapa1948/units_raw.pkl','rb'))
    def project(a):
        a=a.copy();a[:,0]=(a[:,0]+73.5708041)*math.cos(math.radians(38))*44+643
        a[:,1]=(-21.7807776-a[:,1])*44+150
        return a
    target=defaultdict(list)
    terr={'La Pampa','Río Negro','Chubut','Neuquén','Misiones','Formosa','Chaco','Santa Cruz','Tierra del Fuego'}
    for u in raw:
        name,prov=u['name'],u['prov']
        if name in ('Antártida Argentina','Islas Malvinas','Islas del Atlántico Sur') or u['geom'].bounds[1]<-60:continue
        # La base 1947 conserva los departamentos de la gobernación militar,
        # aunque los agrupa bajo los nombres provinciales actuales.
        military={'Sarmiento','Alto Rio Mayo','Alto Rio Senguer','Camarones',
                  'Comodoro Rrivadavia','Los Huemules','Paso Rio Mayo','Pico Salamanca',
                  'Colonia Las Heras','Lago Buenos Aires I','Pico Truncado','Puerto Deseado'}
        key='Comodoro Rivadavia' if prov in ('Chubut','Santa Cruz') and name in military else prov
        target[key].append(shapely.transform(u['geom'],project))
    target={p:shapely.make_valid(unary_union(gs)).buffer(.05).buffer(-.05).simplify(.08,preserve_topology=True)for p,gs in target.items()}
    original=[only_polygons(unary_union([polygon(paths[i])for i in u['ids']]))for u in units]
    out=[None]*len(units);audit=[]
    keys=defaultdict(list)
    for i,u in enumerate(units):keys[u['n']if u['k']=='territorio nacional'else u['p']].append(i)
    for p,indices in keys.items():
        print('Ajustando circunscripciones:',p,flush=True)
        # Las 28 divisiones porteñas de 1951 son las del SVG y del PDF,
        # distintas de las 20 del SHP y de las 28 usadas desde 1973.
        src=unary_union([original[i]for i in indices]);dst=target[p]
        x,y,X,Y=src.bounds;a,b,A,B=dst.bounds
        sx,sy=(A-a)/(X-x),(B-b)/(Y-y)
        affine=[sx,0,0,sy,a-sx*x,b-sy*y]
        base=[affine_transform(original[i],affine)for i in indices]
        if len(indices)==1:
            out[indices[0]]=only_polygons(dst)
            audit.append(dict(provincia=p,circunscripciones=1,ajuste='Contorno SHP; unidad indivisa.'))
            continue
        # Controles de perímetro por dirección desde el centro: conservan la
        # ubicación relativa de los trazos internos, ajustando el marco provincial.
        joined=unary_union(base);sc=joined.centroid;tc=dst.centroid
        controls=[];dest=[]
        for angle in np.linspace(0,2*np.pi,40,endpoint=False):
            dx,dy=np.cos(angle),np.sin(angle)
            def edge(g,c):
                pts=shapely.get_coordinates(g.boundary.intersection(LineString([(c.x,c.y),(c.x+dx*3000,c.y+dy*3000)])))
                if not len(pts):return None
                return max(pts,key=lambda q:(q[0]-c.x)**2+(q[1]-c.y)**2)
            s,t=edge(joined,sc),edge(dst,tc)
            if s is not None and t is not None and not any(np.linalg.norm(s-v)<.01 for v in controls):controls.append(s);dest.append(t)
        controls.append(np.array([sc.x,sc.y]));dest.append(np.array([tc.x,tc.y]))
        if p=='Buenos Aires':
            # El entrante porteño no es visible desde el centro provincial en
            # todos los rayos. Fija también su perímetro: evita que el ajuste
            # costero desplace Vicente López dentro del recorte de Capital.
            capital_src=affine_transform(unary_union([original[j] for j,u in enumerate(units) if u['p']=='Capital Federal']),affine)
            capital_dst=target['Capital Federal']
            for angle in np.linspace(0,2*np.pi,20,endpoint=False):
                dx,dy=np.cos(angle),np.sin(angle)
                s,t=edge(capital_src,capital_src.centroid),edge(capital_dst,capital_dst.centroid)
                if s is not None and t is not None and not any(np.linalg.norm(s-v)<.01 for v in controls):controls.append(s);dest.append(t)
        warp=RBFInterpolator(np.array(controls),np.array(dest),kernel='thin_plate_spline',smoothing=.5)
        dst=shapely.set_precision(only_polygons(dst),.00001)
        regions=[];claimed=Polygon()
        for g in base:
            g=shapely.set_precision(only_polygons(shapely.make_valid(shapely.transform(g,warp))),.00001)
            g=only_polygons(g.intersection(dst).difference(claimed))
            regions.append(g);claimed=unary_union([claimed,g])
        gap=only_polygons(dst.difference(claimed));gap_area=gap.area
        # Cierra rendijas de contorno exclusivamente geométricas. No agrega
        # unidades, ni reparte o modifica votos, candidatos o afiliaciones.
        step=.25
        while not gap.is_empty and gap.area>.001 and step<1024:
            for j,g in enumerate(regions):
                added=only_polygons(gap.intersection(g.buffer(step)))
                if not added.is_empty:regions[j]=only_polygons(unary_union([g,added]));gap=only_polygons(gap.difference(added))
            step*=2
        if not gap.is_empty:
            for piece in ([gap]if gap.geom_type=='Polygon'else getattr(gap,'geoms',[])):
                if piece.area>0:
                    j=min(range(len(regions)),key=lambda j:regions[j].distance(piece))
                    regions[j]=unary_union([regions[j],piece])
        for i,g in zip(indices,regions):
            assert not g.is_empty,(p,units[i]['n'])
            out[i]=only_polygons(shapely.make_valid(g)).simplify(.001 if p=='Capital Federal' else .12,preserve_topology=True)
        audit.append(dict(provincia=p,circunscripciones=len(indices),controles=len(controls),area_ajustada_al_contorno=gap_area,
                          cobertura_shp=unary_union(regions).area/dst.area))
    assert all(g is not None and not g.is_empty for g in out)
    return out,audit,target
