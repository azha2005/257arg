"""Chequeo y recaptura del modo Ganó tras incorporar logos de Wikipedia."""
from pathlib import Path
import sys,json
from PIL import Image
from playwright.sync_api import sync_playwright
from serie import ROOT,HERE,KEYS,dump

keys=sys.argv[1:] or KEYS+['2023pasointernas']
report=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome')
    page=b.new_page(viewport={'width':1920,'height':1800},color_scheme='light')
    for key in keys:
        errs=[]
        handler=lambda e:errs.append(str(e))
        page.on('pageerror',handler)
        page.goto((HERE/f'atlas_{key}.html').as_uri()+'#m-gan')
        # Medir los elementos realmente dibujados, en cada modo del visor.
        frames=page.evaluate('''()=>DATA.modes.map(m=>{
            window.__atlas.setMode(m.id);
            const images=Array.from(document.querySelectorAll('#legend svg image')).map(im=>{
                const f=im.parentElement,b=im.getBBox();
                return {x:b.x,y:b.y,w:b.width,h:b.height,
                    marco_w:+f.getAttribute('width'),marco_h:+f.getAttribute('height')};
            });
            return {modo:m.id,imagenes:images};
        })''')
        assert all(i['x']>=3.99 and i['y']>=2.99 and
                   i['x']+i['w']<=i['marco_w']-3.99 and i['y']+i['h']<=i['marco_h']-2.99
                   for m in frames for i in m['imagenes']),(key,frames)
        page.evaluate('window.__atlas.setMode("gan")')
        checks=page.evaluate('''()=>DATA.modes[0].national.cands.filter(c=>c.code!=='OTR').map(c=>{
            const n=DATA.candidates[c.code];
            const t=Array.from(document.querySelectorAll('#legend text')).find(e=>e.textContent===n.n);
            const box=t.getBBox();
            return {code:c.code,logo:!!n.img,bloque:n.blk,x:box.x,width:box.width};
        })''')
        assert all((c['logo'] or key.endswith('dip')) and c['x']>=207 for c in checks),(key,checks)
        legend_bottom=page.evaluate('(()=>{const b=document.querySelector("#legend").getBBox();return b.y+b.height})()')
        assert legend_bottom<=1645,(key,legend_bottom)
        page.add_style_tag(content='html,body{background:transparent!important}')
        name=f'atlas_{key}_gan.png'
        trans=ROOT/'png_transparentes/serieAMBA2005_2023radios'/name
        page.locator('#atlas').screenshot(path=str(trans),omit_background=True)
        with Image.open(trans).convert('RGBA') as im:
            bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
            for target in ['png_blanco/serieAMBA2005_2023radios','png_transparentes/all elections white bg']:
                bg.convert('RGB').save(ROOT/target/name)
        assert not errs,(key,errs)
        report.append(dict(key=key,logos=checks,marcos_por_modo=frames,errores_js=errs,leyenda_hasta_y=legend_bottom))
        page.remove_listener('pageerror',handler)
        print('LOGOS OK',key,flush=True)
    b.close()
out=HERE/'VALIDACION_LOGOS.json'
previous={x['key']:x for x in json.loads(out.read_text(encoding='utf8'))} if out.exists() else {}
previous.update({x['key']:x for x in report})
dump(out,list(previous.values()))
