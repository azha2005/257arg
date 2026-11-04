"""Compara el esquema 1951 de la misma lámina con el SVG ya georreferenciado."""
from pathlib import Path
import cv2, json, pickle
import numpy as np
from scipy.optimize import linear_sum_assignment
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.affinity import rotate, affine_transform
import shapely
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
im=cv2.imread(str(HERE/'fuente_aportada.png'),0)[25:131,195:311]
white=(im>210).astype('uint8')
n,labels,stats,centers=cv2.connectedComponentsWithStats(white,connectivity=4)
source=[]
for i in range(1,n):
    x,y,w,h,area=stats[i]
    if area<20 or x==0 or y==0 or x+w>=116 or y+h>=106:continue
    cs,_=cv2.findContours((labels==i).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    g=shapely.make_valid(Polygon(max(cs,key=cv2.contourArea)[:,0,:])).buffer(.7)
    source.append(g)
contours,_=cv2.findContours(1-white,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
outer=Polygon(max(contours,key=cv2.contourArea)[:,0,:])
cached=pickle.loads((ROOT/'mapas/mapa1951/geometria_adaptada.pkl').read_bytes())['data'][0]
ds=json.loads((ROOT/'mapas/mapa1951/dataset_1951.json').read_text(encoding='utf8'))
ref=[g for g,u in zip(cached,ds['territories'])if u['p']=='Capital Federal']
reference=unary_union(ref)
def normalized(g,bounds):
    x,y,X,Y=bounds
    return affine_transform(g,[1/(X-x),0,0,1/(Y-y),-x/(X-x),-y/(Y-y)])
ref=[normalized(g,reference.bounds)for g in ref]
reference=normalized(reference,reference.bounds)
scores=[]
for angle in range(0,360,5):
    frame=rotate(outer,angle,origin=outer.centroid)
    units=[normalized(rotate(g,angle,origin=outer.centroid),frame.bounds)for g in source]
    matrix=np.array([[a.intersection(b).area/a.union(b).area for b in ref]for a in units])
    a,b=linear_sum_assignment(-matrix)
    frame_iou=normalized(frame,frame.bounds).intersection(reference).area/normalized(frame,frame.bounds).union(reference).area
    scores.append(dict(giro_horario_imagen=angle,coincidencia_recintos=float(matrix[a,b].mean()),coincidencia_contorno=frame_iou))
scores=sorted(scores,key=lambda s:s['coincidencia_recintos'],reverse=True)
report=dict(recintos_detectados_lamina1951=len(source),recintos_referencia=28,metodo='IoU de polígonos con asignación húngara, rotación 0–355 en pasos de 5 grados; sin usar números de circunscripción.',mejores=scores[:8],cuartos=[s for s in scores if s['giro_horario_imagen']in (0,90,180,270)])
(HERE/'ORIENTACION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
