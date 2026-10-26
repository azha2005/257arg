import json
from PIL import Image,ImageDraw,ImageFont
from exportar import ROOT,PROJECT,load

data=json.loads((ROOT/'cotejo/diferencias.json').read_text(encoding='utf-8'))
pages={p['pagina_pdf']:p for p in load()}
items=[]
for r in data:
    if 'manual' not in r or len(r['manual'])!=len(r['ocr']):continue
    if not all(v is not None for v in r['manual']):continue
    if any(list(q['valores'].values())==r['ocr'] for q in pages[r['pagina']]['filas']):continue
    real=[]
    for c,(m,o) in enumerate(zip(r['manual'],r['ocr']),1):
        if o is None or m==o:continue
        ms,os=str(m),str(o)
        if len(os)==len(ms)+1 and any(os[:i]+os[i+1:]==ms for i,t in enumerate(os) if t in '06'):continue
        real.append(c)
    if real:
        r['columnas']=real;items.append(r)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for off in range(0,len(items),16):
    chunk=items[off:off+16]
    out=Image.new('RGB',(1651,len(chunk)*111),'white');d=ImageDraw.Draw(out)
    for i,r in enumerate(chunk):
        p=r['pagina'];y=r['y'];folder=PROJECT/'canton1946' if p>=153 else ROOT
        im=Image.open(folder/f'revision/p_{p}.png')
        out.paste(im.crop((0,round(y)-26,1651,round(y)+27)),(0,i*111))
        d.text((10,i*111+55),f"{i+1}. PDF {p} {r['unidad']} c{r['columnas']} | Manual: "+' '.join(map(str,r['manual'])),fill='blue',font=font)
        d.text((10,i*111+79),'OCR: '+' '.join(map(str,r['ocr'])),fill='red',font=font)
    n=off//16+1
    out.save(ROOT/f'cotejo/hoja_{n:02}.png')
    (ROOT/f'cotejo/hoja_{n:02}.json').write_text(json.dumps(chunk,ensure_ascii=False,indent=2),encoding='utf-8')
print('Filas para segunda revisión:',len(items))
