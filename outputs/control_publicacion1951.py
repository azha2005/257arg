from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'sitio'))
from armar import preparar
src=ROOT/'mapas/mapa1951/atlas_1951.html'
OUT=ROOT/'outputs/control1951';OUT.mkdir(parents=True,exist_ok=True)
pagefile=OUT/'atlas_1951.html';pagefile.write_text(preparar(src.read_text(encoding='utf8')),encoding='utf8')
data=json.loads((ROOT/'mapas/mapa1951/dataset_1951.json').read_text(encoding='utf8'))
errors=[];measurements=[]
with sync_playwright()as p:
    b=p.chromium.launch(channel='chrome')
    pg=b.new_page(viewport={'width':1440,'height':1000})
    pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto(pagefile.as_uri());pg.wait_for_timeout(150)
    assert pg.locator('#barnote-d').count()==1
    assert not pg.locator('#barnote').is_visible()
    pg.locator('#barnote-d summary').click();assert pg.locator('#barnote').is_visible()
    pg.locator('#barnote-d summary').click()
    for mode in ('gan','pp','ucr','par'):pg.evaluate('(m)=>window.__atlas.setMode(m)',mode)
    pg.evaluate('window.__atlas.setMode("gan")')
    assert pg.locator('#B path.dc').first.evaluate('(e)=>getComputedStyle(e).display')=='inline'
    marker=pg.locator('#B .minor-metro').first
    for zoom in (1,8,20):
        pg.evaluate('(k)=>window.__atlas.zoomAt(1168,715,k)',zoom);pg.wait_for_timeout(230)
        measurements.append(dict(zoom=zoom,width=marker.bounding_box()['width']))
    assert measurements[1]['width']>measurements[0]['width']*2
    assert measurements[2]['width']<measurements[0]['width']*3.8
    pg.evaluate('window.__atlas.resetZoom()');pg.wait_for_timeout(200)
    idx=next(i for i,t in enumerate(data['territories'])if t['p']=='Buenos Aires'and t['n']=='Circunscripción 13.ª')
    pg.evaluate('(i)=>window.__atlas.selectUnit(i,false)',idx)
    assert pg.locator('#card').is_visible()
    assert pg.locator('#card').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
    assert pg.locator('#card .nm').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).whiteSpace==="normal"&&e.scrollWidth<=e.clientWidth+1)')
    pg.locator('#card-x').click()
    pg.screenshot(path=str(OUT/'escritorio.png'))
    pg.set_viewport_size({'width':390,'height':844});pg.reload();pg.wait_for_timeout(150)
    assert pg.locator('body').evaluate('(e)=>e.classList.contains("movil")')
    for label in ('Resultados','Recuadros','Póster','Mapa'):pg.get_by_role('button',name=label,exact=True).click()
    pg.screenshot(path=str(OUT/'movil.png'))
    assert not errors,errors
    b.close()
(OUT/'CONTROL.json').write_text(json.dumps(dict(errores=errors,zoom=measurements,fuentes_plegables=True,nombres_completos=True,caba_visible=True,movil=True),ensure_ascii=False,indent=2),encoding='utf8')
print('Copia con el código de master: fuentes, modos, CABA, zoom, fichas y celular verificados.')
