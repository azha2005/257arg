from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,sys
ROOT=Path(__file__).resolve().parent
PREFIX=sys.argv[1] if len(sys.argv)>1 else 'b'
items=json.loads((ROOT/'revision/cotejo_sexos.json').read_text(encoding='utf-8'))
def checked(item):
    for p in item['paginas'][:2]:
        page=json.loads((ROOT/f'transcripcion/p_{p}.json').read_text(encoding='utf-8'))
        row=next(r for r in page['filas'] if r['departamento']==item['unidad'])
        if page['estado']!='transcripción visual' and item['columna'] not in row.get('celdas_revisadas',[]):return False
    return True
items=[x for x in items if not checked(x)]
pages={};images={};raws={}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for p in {p for x in items for p in x['paginas'][:2]}:
    pages[p]=json.loads((ROOT/f'transcripcion/p_{p}.json').read_text(encoding='utf-8'))
    images[p]=Image.open(ROOT/f'revision/p_{p}.png')
    raws[p]=json.loads((ROOT/f'revision/p_{p}_celdas.json').read_text(encoding='utf-8'))
for offset in range(0,len(items),28):
    group=items[offset:offset+28]
    out=Image.new('RGB',(1360,len(group)*65+35),'white');draw=ImageDraw.Draw(out)
    draw.text((0,0),f'HOJA {offset//28+1}: unidad / columna | varones | mujeres | total impreso',fill='black',font=font)
    for i,item in enumerate(group):
        yy=i*65+35
        draw.text((2,yy),f"{i+1}. {item['unidad']} [c{item['columna']}]",fill='black',font=font)
        draw.text((2,yy+22),f"PDF {item['paginas'][0]}/{item['paginas'][1]}",fill='red',font=font)
        for j,p in enumerate(item['paginas'][:2]):
            row=next(r for r in pages[p]['filas'] if r['departamento']==item['unidad'])
            sourcep=row.get('pagina_fuente',p)
            if sourcep not in images:
                images[sourcep]=Image.open(ROOT/f'revision/p_{sourcep}.png')
                raws[sourcep]=json.loads((ROOT/f'revision/p_{sourcep}_celdas.json').read_text(encoding='utf-8'))
            y=row.get('y',0); c=int(item['columna']); xs=raws[sourcep]['limites_x']
            # Original printed row label plus the relevant numeric cell.
            label=images[sourcep].crop((max(0,xs[0]),round(y)-20,xs[1],round(y)+22))
            cell=images[sourcep].crop((xs[c]+3,round(y)-20,xs[c+1]-3,round(y)+22))
            out.paste(label,(350+j*440,yy));out.paste(cell,(665+j*440,yy))
        draw.text((1235,yy+8),str(item['lecturas'][2]),fill='blue',font=font)
        draw.line((0,yy+62,1360,yy+62),fill='#cccccc')
    out.save(ROOT/f'revision/hoja_{PREFIX}{offset//28+1:02}.png')
    (ROOT/f'revision/hoja_{PREFIX}{offset//28+1:02}.json').write_text(json.dumps(group,ensure_ascii=False,indent=2),encoding='utf-8')
print('Hojas',(len(items)+27)//28,'celdas',len(items))
