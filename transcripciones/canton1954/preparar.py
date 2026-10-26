from pathlib import Path
from PIL import Image,ImageDraw
import json
ROOT=Path(__file__).resolve().parent
def claves(pages,name):
    imgs=[]
    for p in pages:
        im=Image.open(ROOT/f'revision/p_{p}.png').convert('RGB')
        w,h=im.size
        crop=im.crop((0,int(h*.76),int(w*.73),int(h*.94)))
        crop.thumbnail((1000,420))
        frame=Image.new('RGB',(1050,crop.height+30),'white')
        ImageDraw.Draw(frame).text((5,4),f'PDF {p}',fill='red')
        frame.paste(crop,(0,30)); imgs.append(frame)
    out=Image.new('RGB',(1050,sum(i.height for i in imgs)),'white')
    y=0
    for im in imgs: out.paste(im,(0,y)); y+=im.height
    out.save(ROOT/f'revision/{name}.png')
if __name__=='__main__':
    claves([172,175,187,190,193,196],'claves1')
    claves([199,202,205,208,211,214],'claves2')
    claves([217,220,223,226,229,232],'claves3')
    claves([235,236,239,242,245,246],'claves4')
