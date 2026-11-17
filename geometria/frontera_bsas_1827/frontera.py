import numpy as np
from PIL import Image
from scipy import ndimage as ndi
im=np.asarray(Image.open('../images/2.png').convert('RGB')).astype(float)
pal={'y1':(253,237,150),'y2':(247,220,123),'o1':(244,185,69),'o2':(240,165,38),
     'o3':(237,146,6),'o4':(218,135,7),'o5':(199,122,6),'agua':(205,230,245),'gris':(220,220,220),'blanco':(255,255,255)}
names=list(pal);P=np.array([pal[k] for k in names])
d=((im[:,:,None,:]-P[None,None])**2).sum(-1);cls=d.argmin(-1);dm=d.min(-1)
dentro=np.isin(cls,[names.index(k) for k in ('y1','y2','o1','o2')])&(dm<900)
prov=np.isin(cls,[names.index(k) for k in ('y1','y2','o1','o2','o3','o4','o5')])&(dm<900)
# solo la provincia (limitar al área del mapa)
dentro[:, :0]=False
m=ndi.binary_closing(dentro,iterations=4);m=ndi.binary_fill_holes(m)
lab,n=ndi.label(m);sz=ndi.sum(m,lab,range(1,n+1));m=lab==(1+sz.argmax())
np.save('frontera_mask.npy',m)
o=(np.asarray(Image.open('../images/2.png').convert('RGB'))*0.5).astype(np.uint8);o[m]=[255,0,0]
Image.fromarray(o).save('z/frontera_mask.png');print(m.sum())
