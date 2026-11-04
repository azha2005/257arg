from pathlib import Path
import hashlib,json
import requests
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
BASE='https://azha2005.github.io/257arg/'
URL=BASE+'mapas/mapa1951/atlas_1951.html'
r=requests.get(URL,timeout=30);r.raise_for_status()
assert 'Math.min(3.2,1+.6*dotGrowth)'in r.text
assert 'white-space:normal;overflow:visible;text-overflow:clip'in r.text
thumbs={}
for name in ('mapa1951__atlas_1951.webp','mapa1951__atlas_1951_claro.webp'):
    q=requests.get(BASE+'miniaturas/'+name,timeout=30);q.raise_for_status()
    assert hashlib.sha256(q.content).digest()==hashlib.sha256((ROOT/'sitio/miniaturas'/name).read_bytes()).digest()
    thumbs[name]=q.status_code
index=requests.get(BASE,timeout=30);index.raise_for_status()
assert 'mapas/mapa1951/atlas_1951.html'in index.text
errors=[]
with sync_playwright()as p:
    b=p.chromium.launch(channel='chrome');pg=b.new_page(viewport={'width':1440,'height':1000})
    pg.on('pageerror',lambda e:errors.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(250)
    assert pg.locator('#barnote-d summary').inner_text()=='Fuentes y notas'
    assert not pg.locator('#barnote').is_visible()
    pg.locator('#barnote-d summary').click();assert pg.locator('#barnote').is_visible()
    pg.locator('#barnote-d summary').click()
    assert pg.locator('#B .dc').first.evaluate('(e)=>getComputedStyle(e).display')=='inline'
    assert pg.locator('#B circle[data-minority]').count()==10
    for mode in ('gan','pp','ucr','par'):pg.evaluate('(m)=>window.__atlas.setMode(m)',mode)
    pg.evaluate('window.__atlas.setMode("gan")')
    pg.screenshot(path=str(ROOT/'outputs/1951_publicado.png'))
    assert not errors,errors
    b.close()
report=dict(url=URL,commit='37232033779cda64fd488370c61498b3634a4d39',atlas_http=r.status_code,indice_http=index.status_code,miniaturas=thumbs,fuentes_plegables=True,caba_visible=True,puntos=10,modos=4,errores_js=errors)
(ROOT/'outputs/PUBLICACION_1951.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
