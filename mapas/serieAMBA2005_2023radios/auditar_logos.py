"""Inventario de los emblemas que aparecen en alguna leyenda de la serie.

Incluye todos los grupos del visor de internas; genera contacto para revisión visual.
"""
import base64, hashlib, io, json
from PIL import Image, ImageDraw
from serie import HERE, dump

logos = {}
for path in sorted(HERE.glob('dataset_*.json')):
    data = json.loads(path.read_text(encoding='utf8'))
    visible = {c['code'] for m in data['modes'] for c in m.get('national',{}).get('cands',[]) if c['code'] != 'OTR'}
    for code in sorted(visible):
        c = data['candidates'][code]
        if not c.get('img'): continue
        raw = base64.b64decode(c['img'].split(',',1)[1]); key = hashlib.sha256(raw).hexdigest()
        im = Image.open(io.BytesIO(raw)).convert('RGBA')
        if key not in logos:
            logos[key] = dict(nombre=c['n'],archivo=c.get('logo_file') or c.get('blk'),
                              ancho=im.width,alto=im.height,usos=[],_im=im)
        logos[key]['usos'].append(dict(atlas=path.stem.replace('dataset_',''),codigo=code))

sheet = Image.new('RGB',(800,112*len(logos)),'#eee');draw = ImageDraw.Draw(sheet)
report = []
for i,(key,item) in enumerate(logos.items()):
    im=item.pop('_im');draw.text((5,112*i+3),f"{i+1}. {item['nombre']} ({im.width}×{im.height})",fill='black')
    for j,col in enumerate(['#666','#ffc000','#4daee4']):
        box=Image.new('RGBA',(215,78),col); preview=im.copy();preview.thumbnail((205,68))
        box.alpha_composite(preview,((215-preview.width)//2,(78-preview.height)//2))
        sheet.paste(box.convert('RGB'),(10+225*j,112*i+25))
    report.append(dict(sha256=key,**item))
dump(HERE/'AUDITORIA_LOGOS.json',report)
sheet.save(HERE/'AUDITORIA_LOGOS.png')
print(len(report),'emblemas distintos;',sum(len(x['usos']) for x in report),'apariciones en atlas')
