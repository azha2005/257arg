from pathlib import Path
import json
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'dataset_1904.json').read_text(encoding='utf8'))
assert len(data['territories'])==130
gan=data['modes'][0]
ref=json.loads((HERE.parent/'mapa1916fic/dataset_1916fic.json').read_text(encoding='utf8'))
for c,s in [('PAN','CC'),('UCR','UCR'),('PS','PS')]:assert data['candidates'][c]['img']==ref['candidates'][s]['img']
assert sum(u.get('q')is not None for u in gan['units'])==59
assert sum(s['v']for s in gan['national']['slices'])==sum(v or 0 for u in gan['units']for _,v,_ in u.get('lines',[]))
assert sum(u.get('fill')=='#808080' for u in gan['units'])==60
results=[]
with sync_playwright()as p:
    b=p.chromium.launch(channel='msedge',headless=True)
    page=b.new_page(viewport={'width':1920,'height':1700},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((HERE/'atlas_1904.html').as_uri()+'#bare-white-m-gan')
    page.wait_for_timeout(300)
    for mode in data['modes']:
        page.evaluate('(m)=>window.__atlas.setMode(m)',mode['id'])
        page.wait_for_timeout(100)
        assert not errors,errors
        assert page.locator('#B .mal').is_visible()
        assert page.locator('#pv .pfm').is_visible()
        assert page.locator('#B .mal').get_attribute('d')==page.locator('#pv .pfm').get_attribute('d')
        assert page.locator('#legend').evaluate('''e=>[...e.querySelectorAll('svg image')].every(im=>{
          const y=+im.parentElement.getAttribute('y');return ![...e.querySelectorAll('rect')].some(r=>+r.getAttribute('x')===104&&+r.getAttribute('y')===y+32);
        })''')
        box=page.locator('#legend').evaluate('(e)=>{let b=e.getBBox();return {y:b.y,bottom:b.y+b.height}}')
        assert box['bottom']<1700,box
        page.screenshot(path=str(HERE/f'revision_{mode["id"]}.png'))
        results.append(dict(mode=mode['id'],legend=box,errors=list(errors)))
    page.goto((HERE/'atlas_1904.html').as_uri())
    page.evaluate('window.__atlas.selectUnit(0,false)')
    assert page.locator('#card').is_visible()
    page.locator('#card-x').click()
    for button in ('b-svg','b-csv','b-png'):
        with page.expect_download()as dl:page.locator('#'+button).click()
        assert not dl.value.failure()
    b.close()
(HERE/'VALIDACION.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print('1904: 4 modos, 59 registros de votos, 60 sin elección, sumas y descargas verificados.')
