"""Comprueba todos los modos y genera PNG transparentes/blancos y hojas de revisión."""
from pathlib import Path
import json,sys,shutil,io
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
YEARS=list(map(int,sys.argv[1:])) or list(range(2003,2026,2))
OUT=ROOT/'revision_leg2003_2025';OUT.mkdir(exist_ok=True)
allerrs=[];report=[];winners=[]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome')
    page=browser.new_page(viewport={'width':1920,'height':1800},device_scale_factor=1)
    page.on('pageerror',lambda e:allerrs.append(str(e)))
    for year in YEARS:
        folder=ROOT/f'mapa{year}';url=(folder/f'atlas_{year}.html').as_uri()
        ds=json.loads((folder/f'dataset_{year}.json').read_text(encoding='utf8'))
        assert all(len(m['units'])==len(ds['territories']) for m in ds['modes'])
        assert len({m['id'] for m in ds['modes']})==len(ds['modes'])
        frames=[]
        for mode in ds['modes']:
            mid=mode['id'];page.goto(url+'#m-'+mid);page.reload();page.wait_for_timeout(350)
            page.evaluate('document.fonts.ready')
            active=page.evaluate("document.querySelector('#tiles .tile.on').dataset.mode")
            assert active==mid,(year,mid,active)
            assert not allerrs,(year,mid,allerrs)
            bad_imgs=page.evaluate("[...document.querySelectorAll('#bars image')].filter(e=>!e.getAttribute('href')).length")
            assert not bad_imgs
            box=page.evaluate("(()=>{const b=document.querySelector('#legend').getBBox();return {x:b.x,y:b.y,right:b.x+b.width,bottom:b.y+b.height}})()")
            assert box['bottom']<=1640,(year,mid,'Leyenda cortada',box)
            page.add_style_tag(content='html,body,#atlas{background:transparent!important}')
            dest=ROOT/'png_transparentes'/f'mapa{year}';dest.mkdir(exist_ok=True)
            out=dest/f'atlas_{year}_{mid}.png'
            page.locator('#atlas').first.screenshot(path=str(out),omit_background=True)
            im=Image.open(out).convert('RGBA')
            bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);white=bg.convert('RGB')
            dwhite=ROOT/'png_blanco'/f'mapa{year}';dwhite.mkdir(exist_ok=True)
            white.save(dwhite/out.name)
            copies=ROOT/'png_transparentes/all elections white bg';copies.mkdir(exist_ok=True)
            shutil.copy2(dwhite/out.name,copies/out.name)
            img=white.copy();img.thumbnail((630,550));frame=Image.new('RGB',(640,580),'white');frame.paste(img,((640-img.width)//2,25));ImageDraw.Draw(frame).text((10,8),f'{year} - {mid}',fill='black');frames.append(frame)
            if mid=='gan':winners.append(frame.copy())
            report.append({'year':year,'mode':mid,'active':active,'png':str(out),'js_errors':[]})
        contact=Image.new('RGB',(640*3,580*2),'#ddd')
        for j,f in enumerate(frames):contact.paste(f,((j%3)*640,(j//3)*580))
        contact.save(OUT/f'{year}_modos.jpg',quality=90)
        print(year,'modos OK',len(frames),flush=True)
    browser.close()
contact=Image.new('RGB',(640*4,580*3),'#ddd')
for j,year in enumerate(range(2003,2026,2)):
    source=ROOT/'png_blanco'/f'mapa{year}'/f'atlas_{year}_gan.png'
    if not source.exists():continue
    f=Image.open(source).convert('RGB');f.thumbnail((630,550))
    frame=Image.new('RGB',(640,580),'white');frame.paste(f,((640-f.width)//2,25));ImageDraw.Draw(frame).text((10,8),str(year),fill='black')
    contact.paste(frame,((j%4)*640,(j//4)*580))
contact.save(OUT/'todos_ganadores.jpg',quality=93)
vp=OUT/'validacion.json'
previous=json.loads(vp.read_text(encoding='utf8')) if vp.exists() else []
report=[x for x in previous if x['year'] not in YEARS]+report
report.sort(key=lambda x:(x['year'],x['mode']))
vp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
assert not allerrs
print('Todos los modos, hashes y JavaScript OK',flush=True)
