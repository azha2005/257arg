from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw
import sys
root=Path(__file__).resolve().parent
out=root/'inspeccion';out.mkdir(exist_ok=True)
for path in (root/'fuentes').glob('*.pdf'):
    if len(sys.argv)>1 and not any(s in path.stem for s in sys.argv[1:]): continue
    doc=fitz.open(path)
    for start in range(0,len(doc),12):
        sheet=Image.new('RGB',(1800,2440),'#cccccc');draw=ImageDraw.Draw(sheet)
        for j in range(start,min(start+12,len(doc))):
            page=doc[j];pix=page.get_pixmap(matrix=fitz.Matrix(.72,.72))
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            im.thumbnail((590,580))
            x=(j-start)%3*600;y=(j-start)//3*610
            sheet.paste(im,(x,y+25));draw.text((x+4,y+4),f'{path.stem} PDF {j+1}',fill='black')
        sheet.save(out/f'{path.stem}_{start+1:03}.jpg',quality=90)
    print(path.name,len(doc),flush=True)
