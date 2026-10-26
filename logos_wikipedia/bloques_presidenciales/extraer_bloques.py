from PIL import Image
import numpy as np,sys,os
_ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')
SRC=os.path.join(_ROOT,'fuentes_leg2003_2025','presidenciales','originales')
OUT=os.path.join(_ROOT,'logos_wikipedia','bloques_presidenciales')
ROWS={2003:[1696,1788,1880,1972,2064],2007:[1696,1788,1880,1972,2064],2011:[1696,1788,1861,1953,2045],
      2015:[1696,1788,1880,1972],2019:[1696,1788,1861],2023:[1696,1788,1880,1972]}
NAMES={2003:['menem','fpv03','recrear','mnp','ari'],2007:['fpv07','cc','una07','frejuli07','pu07'],
       2011:['fpv11','fap','udeso','cf11','fp11'],2015:['fpv15','cambiemos','una15','cf15'],
       2019:['fdt','sisepuede','consenso'],2023:['up','lla','jxc23','hacemos']}
sheet=[]
for y,rows in ROWS.items():
    a=np.array(Image.open(os.path.join(SRC,f'Elecciones_presidenciales_de_Argentina_de_{y}_-_Resultados.png')).convert('RGBA')).astype(int)
    for r,nm in zip(rows,NAMES[y]):
        blk=a[r:r+64,120:290].copy()             # bloque del logo: 131 unidades de plantilla de ancho
        key=np.median(a[r+1:r+4,470:540,:3].reshape(-1,3),axis=0)   # color de la barra (franja superior, sobre el texto)
        blk[...,3]=np.where(np.abs(blk[:,:,:3]-key).sum(axis=2)<=36,0,blk[...,3])
        W={'una15':140,'cf11':120,'cf15':120,'hacemos':120,'udeso':155,'recrear':132}.get(nm)   # donde empieza el nombre del candidato
        if W: blk[:,W:,3]=0
        im=Image.fromarray(blk.astype('uint8'),'RGBA');im.save(os.path.join(OUT,nm+'.png'))
        print(y,nm,im.size,key)
        sheet.append(im)
S=Image.new('RGBA',(200*4,80*((len(sheet)+3)//4)),(90,90,90,255))
for i,im in enumerate(sheet):S.alpha_composite(im,((i%4)*200,(i//4)*80))
S.save(os.path.join(OUT, '_hoja.png'))
