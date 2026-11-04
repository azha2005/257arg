"""Control matemático e inspección de todos los modos en el navegador real."""
from pathlib import Path
import copy,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'mapas/mapa2003alt'
OUT=ROOT/'outputs/2003alt'

def main():
    manifests=json.loads((DEST/'manifiesto.json').read_text('utf8'))
    errors=[];checks=[]
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome')
        pg=b.new_page(viewport=dict(width=1920,height=1800),device_scale_factor=1,color_scheme='light')
        pg.on('pageerror',lambda e:errors.append(str(e)))
        for s in manifests:
            ds=json.loads((DEST/f'dataset_2003alt_{s["id"]}.json').read_text('utf8'))
            codes=list(s['national_target']);vals=np.array([[dict((v[0],v[1]) for v in u['lines']).get(c,0) for c in codes] for u in ds['modes'][0]['units']])
            err=float(np.max(np.abs(vals.sum(axis=0)-np.array(list(s['national_target'].values())))))
            assert err<.01,(s['id'],err)
            if ds['reconstruction']['fit'].get('rounding'):
                assert err==0,(s['id'],err)
                for m in ds['modes']:
                    assert all(type(v[1]) is int for r in m['units']+list(m.get('prov',{}).values()) for v in r['lines']),s['id']
                for prov,r in ds['modes'][0]['prov'].items():
                    expected={c:sum(dict((v[0],v[1]) for v in u['lines']).get(c,0) for t,u in zip(ds['territories'],ds['modes'][0]['units']) if t['p']==prov) for c in codes}
                    assert all(expected.get(v[0],0)==v[1] for v in r['lines']),(s['id'],prov)
            for i,r in ds['reconstruction']['reading'].items():
                if r.get('readable'):assert ds['modes'][0]['units'][int(i)]['w']==r['reading']['w']
            url=(DEST/s['html']).as_uri()
            pg.goto(url);pg.wait_for_timeout(200)
            assert pg.evaluate('DATA.modes.length')==len(ds['modes'])
            paths=[]
            for mode in ds['modes']:
                pg.evaluate('(m)=>window.__atlas.setMode(m)',mode['id']);pg.wait_for_timeout(70)
                selected=pg.evaluate('(document.querySelector("#tiles .tile.on")||{}).dataset?.mode')
                assert selected==mode['id'],(s['id'],mode['id'],selected)
                for transparent,folder in [(False,'png_blanco'),(True,'png_transparentes')]:
                    dest=ROOT/folder/'mapa2003alt';dest.mkdir(exist_ok=True)
                    out=dest/f'atlas_2003alt_{s["id"]}_{mode["id"]}.png'
                    pg.add_style_tag(content='html,body,#atlas{background:'+('transparent' if transparent else '#fff')+'!important}')
                    pg.locator('#atlas').screenshot(path=str(out),omit_background=transparent)
                    if not transparent and mode['id']=='gan':paths.append(str(out))
            # Logo completo, año/título/pestañas y ficha probados en cada atlas.
            pg.evaluate('window.__atlas.setMode("gan")')
            boxes=pg.evaluate('''()=>{let r=document.querySelector('#tiles rect');return {tabs:+r.getAttribute('x'),text:document.querySelector('#legend').textContent,images:[...document.querySelectorAll('#legend image')].map(x=>({width:+x.getAttribute('width'),height:+x.getAttribute('height')}))}}''')
            assert boxes['images'] and all(x['width']>0 and x['height']>0 for x in boxes['images'])
            checks.append(dict(id=s['id'],modes=len(ds['modes']),national_error=err,screenshots=paths,legend=boxes))
        b.close()
    assert not errors,errors
    (OUT/'validacion.json').write_text(json.dumps(dict(atlases=checks,page_errors=errors),ensure_ascii=False,indent=2),'utf8')
    sheet=Image.new('RGB',(1600,2*390),'#f6f4ef');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    for j,s in enumerate(manifests):
        im=Image.open(ROOT/'png_blanco/mapa2003alt'/f'atlas_2003alt_{s["id"]}_gan.png').convert('RGB');im.thumbnail((395,680))
        x=j%4*400;y=j//4*390
        sheet.paste(im,(x,y+35));draw.text((x+8,y+8),s['title'],fill='#202522',font=font)
    sheet.save(OUT/'ocho_remakes.jpg',quality=90)
    print('Verificados',len(checks),'atlas,',sum(s['modes'] for s in checks),'modos; errores JS:',len(errors),flush=True)

if __name__=='__main__':main()
