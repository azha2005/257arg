import numpy as np, json
import shapely.geometry as sg
from shapely.ops import unary_union
cp={'Buenos Aires':((367,124),(-58.38,-34.60)),'Dolores':((410,270),(-57.68,-36.31)),'Tandil':((305,348),(-59.13,-37.32)),
 'Mar del Plata':((405,410),(-57.55,-38.00)),'Bahia Blanca':((95,456),(-62.27,-38.72)),'Olavarria':((227,306),(-60.32,-36.89)),
 'Tres Arroyos':((229,432),(-60.28,-38.38)),'Necochea':((324,451),(-58.74,-38.55))}
A=np.array([[x,y,1] for (x,y),_ in cp.values()]);L=np.array([g for _,g in cp.values()])
cx,*_=np.linalg.lstsq(A,L[:,0],rcond=None);cy,*_=np.linalg.lstsq(A,L[:,1],rcond=None)
res=A@np.c_[cx,cy]-L
for k,r in zip(cp,res): print(f'{k:14s} {r[0]*91:6.1f} {r[1]*111:6.1f} km')
from shapely import affinity
m=np.load('frontera_mask.npy').astype(int)
polys=[]
for y in range(m.shape[0]):
    r=m[y];d=np.diff(np.r_[0,r,0]);st=np.where(d==1)[0];en=np.where(d==-1)[0]
    polys+= [sg.box(a,y,b,y+1) for a,b in zip(st,en)]
pix=unary_union(polys)
print(pix.area,pix.geom_type);polys=[affinity.affine_transform(pix,[cx[0],cx[1],cy[0],cy[1],cx[2],cy[2]])]
print(polys[0].area,polys[0].is_valid);p=unary_union(polys).buffer(0.01).buffer(-0.01).simplify(0.01)
json.dump({'type':'Feature','properties':{'fuente':'mapa escolar de avance de la frontera, línea de 1826, georreferenciado a ojo con 8 ciudades'},'geometry':sg.mapping(p)},open('hgis/frontera1826.geojson','w'))
print(p.geom_type,p.bounds,round(p.area,3))
