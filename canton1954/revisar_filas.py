from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'revision/sumas_filas.json').read_text(encoding='utf-8'))
rows=[r for r in rows if not r['visual']]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for off in range(0,len(rows),14):
    group=rows[off:off+14]
    out=Image.new('RGB',(1580,len(group)*92),'white');d=ImageDraw.Draw(out)
    for i,ref in enumerate(group):
        p=ref['pagina'];page=json.loads((ROOT/f'transcripcion/p_{p}.json').read_text(encoding='utf-8'))
        row=next(r for r in page['filas'] if r['departamento']==ref['unidad'])
        src=row.get('pagina_fuente',p);y=row['y']
        crop=Image.open(ROOT/f'revision/p_{src}.png').crop((50,round(y)-24,1620,round(y)+26))
        d.text((0,i*92),f"{i+1}. PDF {src} / registro {p}: {ref['unidad']} | lectura actual: "+' '.join(str(v) for v in ref['valores']),fill='red',font=font)
        out.paste(crop,(0,i*92+30))
    out.save(ROOT/f'revision/filas_{off//14+1:02}.png')
