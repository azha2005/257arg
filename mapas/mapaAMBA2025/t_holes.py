from head_amba import *
from shapely.geometry import Polygon, Point
U = unary_union([g.buffer(0.3) for g in G_raw])
polys = [U] if U.geom_type=='Polygon' else list(U.geoms)
holes=[]
for p in polys:
    for h in p.interiors:
        a=Polygon(h).area
        if a>15: holes.append((a,Polygon(h)))
holes.sort(key=lambda t:-t[0])
print(len(holes),'huecos >15 px2')
# todas las geometrias del geojson (cualquier partido) proyectadas
allf={k:proj_geom(g) for k,g in feats.items() if k[0]=='02'}
inv_part={}
for (a,b),n in part_of.items(): inv_part[(a,b)]=n
for a,h in holes[:20]:
    c=h.centroid; lon=LON0+(c.x-X0)/(KX*S); lat=LAT1-(c.y-Y0)/S
    inside=[k for k,g in allf.items() if g.intersects(h) and k not in set(UKEYS)]
    print(round(a),'px2 at (%d,%d) lon %.3f lat %.3f'%(c.x,c.y,lon,lat), 'geom ajenas dentro:',[(k[1],k[2]) for k in inside][:4])
print('---- vecinos de cada hueco')
for a,h in holes[:4]:
    hb=h.buffer(1.5)
    touch=collections.Counter(PART[i] for i,g in enumerate(G_raw) if g.intersects(hb))
    print(round(a),dict(touch))
print('seccion 045 =',part_of[('02','045')])
