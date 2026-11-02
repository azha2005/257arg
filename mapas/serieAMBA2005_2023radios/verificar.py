"""Verifica la serie y exporta PNG blancos/transparentes de todos los modos.
python mapas/serieAMBA2005_2023radios/verificar.py [2005dip ...]
"""
from pathlib import Path
import json,sys,math
from PIL import Image, ImageOps, ImageDraw
from playwright.sync_api import sync_playwright
from serie import KEYS,HERE,ROOT,dump

selected=sys.argv[1:] or KEYS
report=[];thumbs=[]
previous={x['key']:x for x in json.loads((HERE/'VALIDACION.json').read_text(encoding='utf8'))} if (HERE/'VALIDACION.json').exists() else {}
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel='chrome')
    page=browser.new_page(viewport={'width':1920,'height':1800},color_scheme='light',device_scale_factor=1)
    for key in selected:
        errors=[]
        listener=lambda e:errors.append(str(e))
        page.on('pageerror',listener)
        ds=json.loads((HERE/f'dataset_{key}.json').read_text(encoding='utf8'))
        control=json.loads((HERE/f'control_{key}.json').read_text(encoding='utf8'))
        assert control['error_max_unidad_categoria']<1e-6
        # Después de los radios van los partidos y circuitos del selector de nivel (render.py).
        nradios=sum(1 for t in ds['territories'] if t.get('k','radio')=='radio');assert nradios==control['radios']
        assert all(t.get('k','radio')=='radio' for t in ds['territories'][:nradios])
        national=ds['modes'][0]['national']
        assert sum(c['votes'] for c in national['cands'])==round(control['positivos_fuente'])
        winners={u.get('w') for u in ds['modes'][0]['units'][:nradios] if u.get('w')}
        assert {c['code'] for c in national['cands'] if c['code']!='OTR'}==winners
        assert len(ds['modes'])<=5 or control.get('desagregacion')=='candidato'
        for m in ds['modes']:assert len(m['units'])==len(ds['territories'])
        url=(HERE/f'atlas_{key}.html').as_uri()
        modes=[]
        trans=ROOT/'png_transparentes/serieAMBA2005_2023radios';trans.mkdir(exist_ok=True)
        white=ROOT/'png_blanco/serieAMBA2005_2023radios';white.mkdir(exist_ok=True)
        copies=ROOT/'png_transparentes/all elections white bg';copies.mkdir(exist_ok=True)
        page.goto(url+'#m-gan')
        page.add_style_tag(content='html,body{background:transparent!important}')
        for m in ds['modes']:
            if m['id']!='gan':
                if page.locator('#paso-mode').count():page.locator('#paso-mode').select_option(m['id'])
                else:page.locator('#tiles .tile[data-mode="'+m['id']+'"]').click()
            active=page.evaluate('document.querySelector("#tiles .tile.on")?.dataset.mode')
            assert active==m['id'],(key,m['id'],active)
            assert page.locator('#mainwrap path.d').count()==control['radios']
            assert page.evaluate('Array.from(document.querySelectorAll("path.d")).every(p=>p.getAttribute("fill")!=="#NaNNaNNaN")')
            filename=f'atlas_{key}_{m["id"]}.png'
            page.locator('#atlas').screenshot(path=str(trans/filename),omit_background=True)
            # Fondo blanco de la misma captura; sin cambiar trazos ni colores.
            with Image.open(trans/filename).convert('RGBA') as im:
                bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
                bg.convert('RGB').save(white/filename)
                bg.convert('RGB').save(copies/filename)
            modes.append(dict(id=m['id'],active=active))
            if m['id']=='gan':thumbs.append((key,white/filename))
        # Ficha de un radio del mapa principal, con un clic real.
        page.locator('#tiles .tile[data-mode="gan"]').click()
        clicked=False
        for x,y in [(1000,600),(950,700),(1100,650)]:
            page.mouse.click(x,y)
            if not page.locator('#card').get_attribute('hidden') is None:
                continue
            if page.locator('#card-body').inner_text().strip():clicked=True;break
        assert clicked,(key,'ficha no abierta')
        assert 'Radio' in page.locator('#card-body').inner_text()
        assert not errors,(key,errors)
        report.append(dict(key=key,modes=modes,radios=control['radios'],clic_ficha=True,errores_js=errors,
                           resultado_regional=national['metrics'],parcial=control['missing_list_pba'],
                           radios_excluidos_NE=control.get('radios_excluidos_NE',0)))
        if control.get('NE_estimado_municipal'):
            baseline=ds['modes'][0]['units']
            excluded=[i for i,u in enumerate(baseline[:nradios]) if 'Excluido por pedido' in u.get('note','')]
            assert len(excluded)==control['radios_excluidos_NE']
            assert not any(u.get('w')=='NE' for u in baseline)
            for m in ds['modes']:
                assert all(m['units'][i].get('fill')=='#e6dcc3' and not m['units'][i].get('w') for i in excluded)
        page.remove_listener('pageerror',listener)
        previous[key]=report[-1]
        dump(HERE/'VALIDACION.json',[previous[k] for k in KEYS if k in previous])
        print('OK',key,len(modes),'modos',flush=True)
    browser.close()

thumbs=[(k,ROOT/'png_blanco/serieAMBA2005_2023radios'/f'atlas_{k}_gan.png') for k in KEYS
        if (ROOT/'png_blanco/serieAMBA2005_2023radios'/f'atlas_{k}_gan.png').exists()]
cols=4;cellw=430;cellh=410
sheet=Image.new('RGB',(cols*cellw,math.ceil(len(thumbs)/cols)*cellh),'#e9e9e9')
draw=ImageDraw.Draw(sheet)
for i,(key,path) in enumerate(thumbs):
    im=Image.open(path);im.thumbnail((cellw-12,cellh-28))
    x=(i%cols)*cellw+(cellw-im.width)//2;y=(i//cols)*cellh+23
    sheet.paste(im,(x,y));draw.text(((i%cols)*cellw+10,(i//cols)*cellh+5),key,fill='black')
sheet.save(HERE/'CONTACTO.png')
print('Verificados',len(report),'atlas; fondo blanco y transparente.',flush=True)
