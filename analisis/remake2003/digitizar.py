"""Lee familias de color por unidad; conserva evidencias y confianza de lectura."""
from pathlib import Path
from collections import Counter
import json
import cv2
import numpy as np
from scipy.optimize import differential_evolution
from shapely.ops import unary_union
from registrar import ROOT,OUT,SOURCE,units,raster

GBA={'Almirante Brown','Avellaneda','Berazategui','Berisso','Ensenada','Escobar','Esteban Echeverría','Ezeiza','Florencio Varela','General San Martín','Hurlingham','Ituzaingó','José C. Paz','La Matanza','La Plata','Lanús','Lomas de Zamora','Malvinas Argentinas','Merlo','Moreno','Morón','Pilar','Presidente Perón','Quilmes','San Fernando','San Isidro','San Miguel','San Vicente','Tigre','Tres de Febrero','Vicente López'}

def fit_inset(im,indices,U,box,name):
    x,y,x1,y1=box;patch=im[y:y1,x:x1]
    h=cv2.cvtColor(patch,cv2.COLOR_BGR2HSV)
    mask=((h[:,:,1]>65)&(h[:,:,2]>12)).astype('uint8')*255
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    _,lab,st,_=cv2.connectedComponentsWithStats(mask)
    mask=(lab==(1+np.argmax(st[1:,4]))).astype('uint8')*255
    ge=unary_union([U[i]['geom'] for i in indices]).simplify(.0005,preserve_topology=True)
    b=ge.bounds;yy,xx=np.where(mask)
    sx=(xx.max()-xx.min())/(b[2]-b[0]);sy=-(yy.max()-yy.min())/(b[3]-b[1]);cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
    mx=(xx.min()+xx.max())/2;my=(yy.min()+yy.max())/2
    def matrix(q):
        a=sx*q[0];d=sy*q[1]
        return np.array([[a,0,mx-a*cx+q[2]],[0,d,my-d*cy+q[3]]])
    def loss(q):
        r=raster([ge],matrix(q),mask.shape)>0;t=mask>0
        return 1-(r&t).sum()/(r|t).sum()
    f=differential_evolution(loss,[(.88,1.12),(.88,1.12),(-6,6),(-6,6)],seed=17,maxiter=40,popsize=7,tol=1e-5)
    M=matrix(f.x);edge=raster([U[i]['geom'] for i in indices],M,mask.shape,True)
    patch[edge>0]=(80,0,255)
    cv2.imwrite(str(OUT/f'registro_{name}.png'),cv2.resize(patch,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST))
    M[:,2]+=[x,y]
    print(name,'IoU',1-f.fun,flush=True)
    return dict(matrix=M.tolist(),silhouette_iou=1-f.fun,indices=indices)

def classes(h,key,codes):
    H,S,V=[h[:,:,i].astype(float) for i in range(3)]
    ix=np.full(H.shape,-1,int)
    def put(code,cond):ix[cond]=codes.index(code)
    valid=(S>65)&(V>12)
    if key=='macri':
        put('MAC',valid&(H<45));put('M',valid&(H>90)&(H<130))
    elif key in ('kirchner','menem'):
        put('K',valid&(H>=85)&(H<102));put('M',valid&(H>=102)&(H<130))
    elif key=='reutemann':
        put('M',valid&(H>=80)&(H<105));put('REU',valid&(H>=105)&(H<130))
    elif key=='rodriguezsaa':
        put('R',valid&(H>=65)&(H<94));put('L',valid&(H>=94)&(H<130))
    elif key=='alvarez':
        for c,lo,hi in [('ALV',155,180),('CAV',125,155),('HIL',90,125),('R',65,90),('C',35,65)]:put(c,valid&(H>=lo)&(H<hi))
    elif key=='bilardo':
        put('L',valid&(H<38));put('C',valid&(H>=38)&(H<67));put('R',valid&(H>=67)&(H<88))
        put('BIL',valid&(H>=88)&(H<107))
        put('K',valid&(H>=88)&(H<102)&(S>165)&(V>160))
        put('M',valid&(H>=107)&(H<130))
    elif key=='lemas':
        put('L',valid&(H<38));put('C',valid&(H>=38)&(H<74))
        put('DLS',valid&(H>=74)&(H<89));put('R',valid&(H>=74)&(H<89)&(S>195))
        put('K',valid&(H>=89)&(H<103));put('M',valid&(H>=103)&(H<130))
        put('TERR',valid&(H>=155)&(H<174));put('MOREAU',valid&(H>=174))
    return ix

def read_unit(im,cl,g,M,code_names,layer):
    # Raster con subpíxeles no inventa resolución: se vota sólo con los píxeles originales.
    b=g.bounds
    pts=np.array([[b[0],b[1]],[b[2],b[3]]])@M[:,:2].T+M[:,2]
    x0=max(0,int(pts[:,0].min())-2);y0=max(0,int(pts[:,1].min())-2)
    x1=min(im.shape[1],int(pts[:,0].max())+3);y1=min(im.shape[0],int(pts[:,1].max())+3)
    if x0>=x1 or y0>=y1:return None
    m=M.copy();m[:,2]-=[x0,y0]
    mask=raster([g],m,(y1-y0,x1-x0))
    # Evitar el trazo y los píxeles de frontera, donde el color puede ser vecino.
    er=cv2.erode(mask,np.ones((3,3),np.uint8))
    if np.count_nonzero(er)>=4:mask=er
    vals=cl[y0:y1,x0:x1][mask>0];vals=vals[vals>=0]
    if len(vals)<3:return None
    count=np.bincount(vals,minlength=len(code_names));j=int(count.argmax())
    return dict(w=code_names[j],pixels=int(len(vals)),agreement=round(float(count[j]/len(vals)),4),layer=layer,counts={code_names[i]:int(n) for i,n in enumerate(count) if n})

def main():
    cfg=json.loads((Path(__file__).parent/'escenarios.json').read_text('utf8'))
    U=units();base=json.loads((OUT/'registro_inicial.json').read_text('utf8'))
    if (OUT/'registros_recuadros.json').exists():insets=json.loads((OUT/'registros_recuadros.json').read_text('utf8'))
    else:
        im=cv2.imread(str(SOURCE/cfg[0]['file']))
        caba=[i for i,u in enumerate(U) if u['prov']=='Capital Federal']
        import unicodedata
        norm=lambda s:''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
        ps={norm(t['p']) for t in json.loads((ROOT/'mapas/mapaAMBA2003radios/dataset_amba2003radios.json').read_text('utf8'))['territories']}
        # El recuadro del original contiene el AMBA de 40 partidos salvo Brandsen.
        gba=[i for i,u in enumerate(U) if (u['prov']=='Buenos Aires' and norm(u['name']) in ps and u['name']!='Brandsen') or u['prov']=='Capital Federal']
        insets=dict(caba=fit_inset(im.copy(),caba,U,(818,1758,915,1860),'caba'),gba=fit_inset(im.copy(),gba,U,(788,1922,949,2074),'gba'))
        (OUT/'registros_recuadros.json').write_text(json.dumps(insets,indent=2),'utf8')
    if 'prov' not in insets:
        im=cv2.imread(str(SOURCE/cfg[0]['file']))
        idx=[i for i,u in enumerate(U) if u['prov']!='Capital Federal' and u['name']!='Islas Malvinas']
        insets['prov']=fit_inset(im,idx,U,(270,1890,404,2120),'provincias_tdf')
        (OUT/'registros_recuadros.json').write_text(json.dumps(insets,indent=2),'utf8')
    allrows={};provrows={}
    # Miniatura provincial: el recuadro incluye Capital como un punto separado.
    # Las tres lecturas pequeñas de Tucumán se resuelven por el conteo impreso de distritos.
    cap={'macri':'MAC','alvarez':'ALV','bilardo':'BIL','kirchner':'K','rodriguezsaa':'L','lemas':'L','menem':'K','reutemann':'REU'}
    tuc={'macri':'MAC','alvarez':'CAV','bilardo':'BIL'}
    pg={p:unary_union([u['geom'] for u in U if u['prov']==p and u['name']!='Islas Malvinas']) for p in {u['prov'] for u in U} if p!='Capital Federal'}
    for s in cfg:
        im=cv2.imread(str(SOURCE/s['file']));h=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        codes=[r[0] for r in s['candidates']];cl=classes(h,s['id'],codes)
        shift=np.array(s['main_origin'])-np.array(cfg[0]['main_origin'])
        M=np.array(base['matrix']);M[:,2]+=shift
        rows=[]
        for i,u in enumerate(U):
            if u['name']=='Islas Malvinas':rows.append(dict(i=i,excluded=True));continue
            r=read_unit(im,cl,u['geom'],M,codes,'principal')
            for k,v in insets.items():
                if k not in ('caba','gba'):continue
                if i not in v['indices'] or v['silhouette_iou']<.85:continue
                mi=np.array(v['matrix']);mi[:,2]+=shift
                q=read_unit(im,cl,u['geom'],mi,codes,k)
                if q and (not r or q['pixels']>r['pixels']):r=q
            # Los píxeles mezclados se dejan sin restricción; no se decide por mayoría mínima.
            readable=bool(r and r['pixels']>=6 and r['agreement']>=.8)
            rows.append(dict(i=i,p=u['prov'],n=u['name'],readable=readable,reading=r))
        allrows[s['id']]=rows
        pv={}
        if 'prov' in insets:
            pm=np.array(insets['prov']['matrix']);pm[:,2]+=shift
            for p,g in pg.items():pv[p]=read_unit(im,cl,g,pm,codes,'miniatura provincial')
            pv['Capital Federal']=dict(w=cap[s['id']],layer='CABA: recuadro y conteo impreso',agreement=1,pixels=None)
            if s['id'] in tuc:
                pv['Tucumán'].update(w=tuc[s['id']],inferred=True,note='Unidad muy pequeña: identidad inferida por el cierre del conteo de provincias impreso, sin presentarla como lectura departamental.')
        provrows[s['id']]=pv
        print(s['id'],'legibles',sum(r.get('readable',False) for r in rows),'de',len(U)-1,Counter(r['reading']['layer'] for r in rows if r.get('readable')),flush=True)
    dest=ROOT/'analisis/remake2003/lecturas.json'
    dest.write_text(json.dumps(dict(registration=base,insets=insets,scenarios=allrows),ensure_ascii=False,indent=2),'utf8')
    (ROOT/'analisis/remake2003/lecturas_provincias.json').write_text(json.dumps(provrows,ensure_ascii=False,indent=2),'utf8')

if __name__=='__main__':main()
