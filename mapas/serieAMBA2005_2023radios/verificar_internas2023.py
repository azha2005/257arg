"""Verifica aislamiento de cada interna, porcentajes, CSV y exporta las 20 vistas."""
import json,io,csv,sys
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
from serie import ROOT,HERE,dump

KEY='2023pasointernas'
data=json.loads((HERE/f'dataset_{KEY}.json').read_text(encoding='utf8'))
report=[];thumbs=[]
previous={x['id']:x for x in json.loads((HERE/'VALIDACION_INTERNAS2023.json').read_text(encoding='utf8'))} if (HERE/'VALIDACION_INTERNAS2023.json').exists() else {}
wanted=set(sys.argv[1:]) if sys.argv[1:] else None
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome')
    pg=b.new_page(viewport={'width':1920,'height':1800},color_scheme='light')
    errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto((HERE/f'atlas_{KEY}.html').as_uri()+'#m-gan')
    assert pg.evaluate('DATA.candidates.C132_A.base')=='#e10019'
    pg.add_style_tag(content='html,body{background:transparent!important}')
    for m in data['modes']:
        if wanted is not None and m['id'] not in wanted:continue
        if pg.locator('#internal-group').input_value()!=m['set']:
            pg.locator('#internal-group').select_option(m['set'])
        pg.locator('#internal-view').select_option(m['id'])
        assert pg.locator('#tiles .tile.on').get_attribute('data-mode')==m['id']
        result=pg.evaluate('''()=>{
          const M=DATA.modes.find(m=>m.id===document.querySelector('#internal-view').value);
          const allowed=M.national.cands.map(c=>c.code);
          let maxerr=0,bad=false;
          for(const u of M.units){if(!u.lines?.length)continue;
            if(u.lines.some(l=>!allowed.includes(l[0])||l[1]!==null))bad=true;
            maxerr=Math.max(maxerr,Math.abs(u.lines.reduce((s,l)=>s+l[2],0)-100));}
          const box=document.querySelector('#legend').getBBox();
          return {bad,maxerr,allowed,partp:M.national.partp,metrics:M.national.metrics.length,bottom:box.y+box.height};
        }''')
        assert not result['bad'] and result['maxerr']<=.011,(m['id'],result)
        assert result['partp'] is None and result['metrics']==0
        assert result['bottom']<1645,(m['id'],result)
        # La ficha real también queda limitada a los competidores de esta interna.
        pg.mouse.click(1000,600)
        assert pg.locator('#card').get_attribute('hidden') is None
        shown=pg.locator('#card-body .c-row .nm').all_text_contents()
        allowed_names={data['candidates'][c]['n'] for c in result['allowed']}
        assert all(n in allowed_names for n in shown),(m['id'],shown)
        assert pg.locator('#card-body .vt:visible').count()==0
        pg.locator('#card-x').click();pg.mouse.move(10,10)
        filename=f'atlas_{KEY}_{m["id"]}.png'
        trans=ROOT/'png_transparentes/serieAMBA2005_2023radios'/filename
        pg.locator('#atlas').screenshot(path=str(trans),omit_background=True)
        with Image.open(trans).convert('RGBA') as im:
            bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
            for target in ['png_blanco/serieAMBA2005_2023radios','png_transparentes/all elections white bg']:
                bg.convert('RGB').save(ROOT/target/filename)
        if m['id']=='gan' or m['id'].endswith('_gan'):
            thumbs.append((data['sets'][m['set']]['label'],ROOT/'png_blanco/serieAMBA2005_2023radios'/filename))
            with pg.expect_download() as download:
                pg.locator('#b-csv').click()
            raw=Path(download.value.path()).read_text(encoding='utf-8-sig')
            rows=list(csv.reader(io.StringIO(raw)))
            assert len(rows)==len(data['territories'])+1
            assert rows[0]==['partido','radio']+[data['candidates'][c['code']]['n']+' (%)' for c in m['national']['cands']]
        assert not errors,errors
        report.append(dict(id=m['id'],grupo=m['set'],candidatos=result['allowed'],max_error_redondeo=result['maxerr'],
                           ficha_solo_interna=True,errores_js=list(errors)))
        previous[m['id']]=report[-1]
        dump(HERE/'VALIDACION_INTERNAS2023.json',[previous[m['id']] for m in data['modes'] if m['id'] in previous])
        print('OK',m['id'],flush=True)
    b.close()

thumbs=[(data['sets'][m['set']]['label'],ROOT/'png_blanco/serieAMBA2005_2023radios'/f'atlas_{KEY}_{m["id"]}.png')
        for m in data['modes'] if m['id']=='gan' or m['id'].endswith('_gan')]
sheet=Image.new('RGB',(3*500,2*455),'#eee');draw=ImageDraw.Draw(sheet)
for i,(name,path) in enumerate(thumbs):
    im=Image.open(path);im.thumbnail((490,420));sheet.paste(im,(i%3*500+(500-im.width)//2,i//3*455+25));draw.text((i%3*500+5,i//3*455+5),name,fill='black')
sheet.save(HERE/'CONTACTO_INTERNAS2023.png')
print('Verificadas',len(report),'vistas y sus CSV internos.',flush=True)
