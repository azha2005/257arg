"""Validación numérica, navegación y exportaciones reales en navegador de los tres atlas."""
from pathlib import Path
from collections import Counter
import json, shutil, subprocess, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
from datos import ROOT, HERE, load

YEARS=tuple(map(int,sys.argv[1:])) or (1926,1937,1940)
SUFFIX='_'+'_'.join(map(str,YEARS)) if sys.argv[1:] else ''
results=[];thumbs=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome')
    pg=b.new_page(viewport={'width':1920,'height':1800},color_scheme='light',accept_downloads=True)
    errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
    for y in YEARS:
        src=ROOT/f'mapas/mapa{y}/atlas_{y}.html';url=src.as_uri()
        pg.goto(url+'#bare-white');pg.wait_for_timeout(250)
        ds=pg.evaluate('DATA')
        nat=json.loads((src.parent/f'wiki_nacional_{y}.json').read_text(encoding='utf-8'))
        assert sum(v['votes'] for v in ds['modes'][0]['national']['cands'])+nat['otros']==nat['positivos']
        assert len(ds['modes'][0]['units'])==len(ds['territories'])==444
        wins={r['w'] for r in ds['modes'][0]['units'] if r.get('w')}
        assert wins==set(nat['blocs'])
        if y in (1918,1920):
            assert all('imput' not in m.get('tile','').lower() for m in ds['modes'])
            for i,r in enumerate(ds['modes'][0]['units']):
                prov=ds['territories'][i]['p']
                if r.get('lines') and ((y==1918 and prov in ('Capital Federal','Santa Fe')) or (y==1920 and prov=='Capital Federal')):
                    assert 'Reserva de fuente:' in r.get('note',''),(y,prov,'falta reserva')
                if y==1920 and prov=='Jujuy':
                    assert not r.get('w') and r.get('fill') in ('#e6dcc3','#cfcfcf')
        # El agregado provincial conserva exactamente las columnas originales y no duplica polígonos.
        for prov in {r['prov'] for r in load(y)}:
            raw=sum(sum(r['P'].values()) for r in load(y) if r['prov']==prov)
            shown=sum(row[1] for row in ds['modes'][0]['prov'][prov].get('lines',[]) if row[0] not in ('P_BLA','P_NUL'))
            assert raw==shown,(y,prov,raw,shown)
        checks=[]
        for mode in ds['modes']:
            mid=mode['id'];pg.goto(url+'#bare-white-m-'+mid);pg.reload();pg.wait_for_timeout(150)
            assert pg.locator('#tiles .tile.on').get_attribute('data-mode')==mid,(y,mid)
            layout=pg.evaluate('''()=>{
              const g=document.querySelector('#legend').getBBox(), t=document.querySelector('#t1').getBBox();
              const tiles=[...document.querySelectorAll('#tiles rect')].map(e=>e.getBBox());
              return {legend:{x:g.x,y:g.y,x2:g.x+g.width,y2:g.y+g.height},title_x2:t.x+t.width,first_tile:Math.min(...tiles.map(r=>r.x)),
                      unfilled:document.querySelectorAll('#B .d:not([fill])').length};}''')
            assert layout['legend']['y2']<=1649 and layout['legend']['x2']<560,(y,mid,layout)
            assert layout['title_x2']<layout['first_tile'] and layout['unfilled']==0,(y,mid,layout)
            target=ROOT/f'png_blanco/mapa{y}/atlas_{y}_{mid}.png';target.parent.mkdir(parents=True,exist_ok=True)
            pg.locator('#atlas').screenshot(path=str(target))
            im=Image.open(target).convert('RGB');im.thumbnail((384,330));thumbs.append((f'{y} · {mid}',im.copy()))
            pg.add_style_tag(content='html,body,#atlas{background:transparent!important}')
            target=ROOT/f'png_transparentes/mapa{y}/atlas_{y}_{mid}.png';target.parent.mkdir(parents=True,exist_ok=True)
            pg.locator('#atlas').screenshot(path=str(target),omit_background=True)
            checks.append(dict(modo=mid,activo=True,layout=layout))
        pg.goto(url);pg.wait_for_timeout(150)
        exports=[]
        for ext in ('csv','svg','png'):
            with pg.expect_download(timeout=30000) as d:pg.locator('#b-'+ext).click()
            download=d.value;dest=ROOT/f'outputs/entreguerras_exportaciones/{y}.{ext}';dest.parent.mkdir(exist_ok=True)
            download.save_as(str(dest));assert dest.stat().st_size>1000
            if ext=='png':
                im=Image.open(dest);assert min(im.size)>1000
            if ext=='csv' and y in (1918,1920):
                assert 'fuente_y_reservas' in dest.read_text(encoding='utf-8-sig').splitlines()[0]
            exports.append(dict(formato=ext,bytes=dest.stat().st_size))
        results.append(dict(anio=y,modos=checks,exportaciones=exports))
        print(y,len(checks),'modos y CSV/SVG/PNG verificados',flush=True)
    assert not errors,errors
    b.close()
sheet=Image.new('RGB',(384*5,355*((len(thumbs)+4)//5)),'white');draw=ImageDraw.Draw(sheet)
for i,(label,im) in enumerate(thumbs):
    x,y=(i%5)*384,(i//5)*355;draw.text((x+8,y+5),label,fill='black');sheet.paste(im,(x,y+24))
sheet.save(ROOT/f'outputs/entreguerras_contacto{SUFFIX}.png')
(HERE/f'VALIDACION{SUFFIX}.json').write_text(json.dumps(dict(ok=True,errores_js=errors,atlas=results),ensure_ascii=False,indent=2),encoding='utf-8')
print('OK',sum(len(r['modos']) for r in results),'modos; sin errores de JavaScript',flush=True)
