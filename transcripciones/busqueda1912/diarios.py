from pathlib import Path
import urllib.request, concurrent.futures, io, csv
from PIL import Image
F=Path(__file__).resolve().parent/'fuentes'
def tile(spec):
    idx,page,z,x,y=spec
    url=f'https://www.santafe.gov.ar/hemeroteca/tile/{idx}-{page}-{z}-{x}-{y}.jpg'
    try:
        data=urllib.request.urlopen(url,timeout=25).read()
        return spec,data,''
    except Exception as e:return spec,b'',repr(e)
if __name__=='__main__':
    log=[]
    for idx in [6512,6504]:
        for page in [1,2,3]:
            z=2;canvas=Image.new('RGB',(1024,1024),'white')
            specs=[(idx,page,z,x,y) for x in range(4) for y in range(4)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
                for (i,p,zz,x,y),data,err in ex.map(tile,specs):
                    url=f'https://www.santafe.gov.ar/hemeroteca/tile/{i}-{p}-{zz}-{x}-{y}.jpg'
                    log.append([url,'2026-10-15',len(data),'descargado' if data else err])
                    if data:canvas.paste(Image.open(io.BytesIO(data)),(x*256,y*256))
            canvas.save(F/f'santa_fe_{idx}_p{page}_z{z}.png')
            print(idx,page,flush=True)
    with (F/'diarios_descargas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['url','fecha_consulta','tamano','estado']);w.writerows(log)
