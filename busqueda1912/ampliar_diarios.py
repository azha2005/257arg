"""Descarga reproducible del visor público; conserva teselas y registra cada solicitud."""
from pathlib import Path
import sys,urllib.request,concurrent.futures,csv,io,json,re
from PIL import Image
from diarios import tile,F
def get(idx,page,z,x0,x1,y0,y1):
    specs=[(idx,page,z,x,y) for x in range(x0,x1) for y in range(y0,y1)]
    canvas=Image.new('RGB',((x1-x0)*256,(y1-y0)*256),'white');log=[]
    cache=F/'teselas';cache.mkdir(exist_ok=True)
    def cached(sp):
        path=cache/('-'.join(map(str,sp))+'.jpg')
        if path.exists():return sp,path.read_bytes(),''
        sp,b,e=tile(sp)
        if b:
            try:Image.open(io.BytesIO(b)).verify();path.write_bytes(b)
            except Exception:e='respuesta no es imagen';b=b''
        return sp,b,e
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for sp,b,e in ex.map(cached,specs):
            i,p,zz,x,y=sp
            log.append([f'https://www.santafe.gov.ar/hemeroteca/tile/{i}-{p}-{zz}-{x}-{y}.jpg','2026-10-15',len(b),'descargado/cache' if b else e])
            if b:canvas.paste(Image.open(io.BytesIO(b)),((x-x0)*256,(y-y0)*256))
    dest=F/f'santa_fe_{idx}_p{page}_z{z}_{x0}-{x1}_{y0}-{y1}.png';canvas.save(dest)
    with (F/'diarios_descargas.csv').open('a',encoding='utf-8',newline='') as f:csv.writer(f).writerows(log)
    print(dest.name,'fallos',sum(bool(r[3]!='descargado/cache') for r in log),flush=True)
if __name__=='__main__':
    args=list(map(int,sys.argv[1:]))
    if len(args)==7:get(*args)
    else:
        for idx in args:
            url=f'https://www.santafe.gov.ar/hemeroteca/diario/{idx}/?page=1'
            b=urllib.request.urlopen(url,timeout=25).read();(F/f'santa_fe_{idx}.html').write_bytes(b)
            for page in [1,2]:get(idx,page,2,0,4,0,4)
