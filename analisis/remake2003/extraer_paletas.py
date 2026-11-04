"""Tonos del mapa de los PNG aportados; no lee ni modifica resultados."""
from collections import Counter,defaultdict
from pathlib import Path
import json
import cv2
import numpy as np
from digitizar import classes
from registrar import ROOT,SOURCE,OUT,units,raster

HERE=Path(__file__).resolve().parent

def palette(counts):
    # Descartar colores de borde/antialias: conservar los rellenos frecuentes.
    cutoff=max(8,max(counts.values())*.04)
    pairs=[(rgb,n) for rgb,n in counts.items() if n>=cutoff]
    if len(pairs)<3:return None
    rgb=np.array([c for c,n in pairs],np.uint8)
    lab=cv2.cvtColor(rgb[None,:,:],cv2.COLOR_RGB2LAB)[0]
    # Agrupar una misma claridad evita dar peso a pequeñas variantes de píxel.
    anchors=[]
    for light in sorted(set(lab[:,0])):
        ix=np.where(lab[:,0]==light)[0]
        j=max(ix,key=lambda j:pairs[j][1]);anchors.append((float(light),rgb[j]))
    low,high=anchors[0][0],anchors[-1][0]
    if high-low<30:return None
    levels=np.linspace(high,low,7)
    values=np.array([c for l,c in anchors]);lights=np.array([l for l,c in anchors])
    colors=[]
    for level in levels:
        # Completar intermedios entre tonos presentes, sin mezclar con blanco.
        c=[round(float(np.interp(level,lights,values[:,j]))) for j in range(3)]
        colors.append('#'+''.join(f'{v:02x}' for v in c))
    return dict(colors=colors,source_anchors=['#'+''.join(f'{int(v):02x}' for v in c) for l,c in anchors],pixels=sum(counts.values()),frequency_cutoff=cutoff)

def main():
    cfg=json.loads((HERE/'escenarios.json').read_text('utf8'))
    U=units();m0=np.array(json.loads((OUT/'registro_inicial.json').read_text('utf8'))['matrix'])
    counts={};pooled=defaultdict(Counter)
    for s in cfg:
        im=cv2.imread(str(SOURCE/s['file']));hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB);codes=[r[0] for r in s['candidates']]
        cl=classes(hsv,s['id'],codes);M=m0.copy();M[:,2]+=np.array(s['main_origin'])-cfg[0]['main_origin']
        mask=raster([u['geom'] for u in U if u['name']!='Islas Malvinas' and u['prov']!='Capital Federal'],M,im.shape[:2])>0
        for j,(code,_,_,_,_,base) in enumerate(s['candidates']):
            keep=mask&(cl==j)
            # Los cianes muy saturados de Kirchner no son el gris azulado de Bilardo.
            if code=='BIL':keep&=hsv[:,:,1]<190
            c=Counter(tuple(map(int,p)) for p in rgb[keep]);counts[s['id'],code]=c;pooled[code,base].update(c)
    result={}
    for s in cfg:
        dest={}
        for code,_,_,_,_,base in s['candidates']:
            c=counts[s['id'],code];p=palette(c) if c and sum(c.values())>=200 else None
            source=s['file']
            if p is None:
                c=pooled[code,base];p=palette(c) if c else None
                source='Otros PNG de la misma candidatura y color base.'
            if p is not None:dest[code]=dict(**p,source=source)
        result[s['id']]=dest
    (HERE/'paletas_originales.json').write_text(json.dumps(dict(method='Rellenos frecuentes del mapa principal; siete niveles entre los tonos observados, sin mezcla con blanco.',scenarios=result),ensure_ascii=False,indent=2),'utf8')
    print('Paletas derivadas del original:',sum(len(v) for v in result.values()))

if __name__=='__main__':main()
