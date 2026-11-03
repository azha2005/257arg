"""Registro de las imágenes aportadas; coordenadas del PNG, no cartografía legal."""
from pathlib import Path
import json, pickle
import cv2
import numpy as np
from scipy.optimize import differential_evolution, minimize
from scipy.ndimage import map_coordinates
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/2003alt'
SOURCE=Path(__file__).resolve().parent/'originales'
if not SOURCE.exists():SOURCE=Path(r'C:\Users\JC\Downloads\2003alt')

def units():
    raw=pickle.load(open(ROOT/'mapas/mapa2003pres/units_leg2003_2025.pkl','rb'))
    return sorted(raw,key=lambda u:(u['prov'],int(u['name'].split()[1]) if u['prov']=='Capital Federal' else u['name']))

def rings(g):
    for p in (g.geoms if hasattr(g,'geoms') else [g]):
        if p.geom_type=='Polygon':
            yield np.asarray(p.exterior.coords)
            for h in p.interiors: yield np.asarray(h.coords)

def raster(geoms,M,shape,lines=False):
    im=np.zeros(shape,np.uint8)
    for g in geoms:
        for a in rings(g):
            pts=np.round(a@M[:,:2].T+M[:,2]).astype(np.int32)
            if lines: cv2.polylines(im,[pts],True,255,1)
            else: cv2.fillPoly(im,[pts],255)
    return im

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    U=units()
    gg=[u['geom'] for u in U if u['prov'] not in ('Capital Federal','Tierra del Fuego')]
    im=cv2.imread(str(SOURCE/'9iq9fwmljc1c1.png'))
    x0,y0=440,1710
    im=im[y0:2310,x0:780]
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    mask=((hsv[:,:,1]>65)&(hsv[:,:,2]>12)).astype('uint8')*255
    # Quitar el globo del exterior, separado del territorio continental.
    closed=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,labels,stats,_=cv2.connectedComponentsWithStats(closed)
    major=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
    target=(labels==major).astype('uint8')*255
    ge=unary_union(gg).simplify(.025,preserve_topology=True)
    # Primera aproximación a partir de los extremos del mapa continental.
    bounds=ge.bounds
    ys,xs=np.where(target)
    sx=(xs.max()-xs.min())/(bounds[2]-bounds[0]);sy=(ys.max()-ys.min())/(bounds[3]-bounds[1])
    init=np.array([sx,-sy,xs.min()-sx*bounds[0],ys.min()+sy*bounds[3],0,0])
    def matrix(p):return np.array([[p[0],p[4],p[2]],[p[5],p[1],p[3]]])
    def loss(p):
        z=raster([ge],matrix(p),target.shape)>0;t=target>0
        return 1-(z&t).sum()/(z|t).sum()
    # Coordenadas centradas permiten buscar escala sin grandes cancelaciones.
    def trans(q):
        p=init.copy();p[0]*=q[0];p[1]*=q[1];p[2]+=q[2]+(p[0]-init[0])*65;p[3]+=(p[1]-init[1])*38+q[3]
        return p
    fit=differential_evolution(lambda q:loss(trans(q)),[(.93,1.07),(.93,1.07),(-12,12),(-12,12)],seed=42,popsize=10,maxiter=70,tol=1e-6)
    M=matrix(trans(fit.x))
    # Guardar para inspección visual antes de clasificar colores.
    overlay=im.copy();edge=raster(gg,M,target.shape,True)
    overlay[edge>0]=(80,0,255)
    cv2.imwrite(str(OUT/'registro_macri.png'),cv2.resize(overlay,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
    M[:,2]+=[x0,y0]
    (OUT/'registro_inicial.json').write_text(json.dumps(dict(matrix=M.tolist(),silhouette_iou=1-fit.fun),indent=2),'utf8')
    print('IoU',1-fit.fun,'matrix',M.tolist(),flush=True)

if __name__=='__main__':main()
