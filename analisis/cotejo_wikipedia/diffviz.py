import sys, json
import numpy as np
from PIL import Image, ImageDraw
from common import *
from register import WIKI
year=int(sys.argv[1]); folder={1983:"mapa1983",1989:"mapa1989",1995:"mapa1995"}[year]
ds,paths=load_atlas(folder,"atlas_%d.html"%year,"dataset_%d.json"%year)
T=json.load(open("reg_%d.json"%year))["T"]; rows={r["i"]:r for r in json.load(open("cmp_%d.json"%year))}
img=Image.open("wp/"+WIKI[year]).convert("RGBA")
bg=Image.new("RGBA",img.size,(255,255,255,255)); bg.alpha_composite(img)
k=img.size[0]/VBW; sx,sy,tx,ty=T
dr=ImageDraw.Draw(bg)
for i,g in paths.items():
    r=rows.get(i)
    if r is None: continue
    col=(0,170,0,255) if r["ok"] else (255,0,255,255)
    for p in (g.geoms if hasattr(g,"geoms") else [g]):
        if p.geom_type!="Polygon": continue
        pts=[((x*sx+tx)*k,(y*sy+ty)*k) for x,y in p.exterior.coords]
        dr.line(pts,fill=col,width=3 if not r["ok"] else 1)
x0,x1,y0,y1=[int(v*k) for v in (560,1420,90,1500)]
bg.crop((x0,y0,x1,y1)).convert("RGB").save("scratch_diff_%d.png"%year)
