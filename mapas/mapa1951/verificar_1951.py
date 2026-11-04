"""Control de procedencia, sumas, geometría GIS e interacción real."""
from pathlib import Path
from collections import Counter
import hashlib, json, pickle, sys, zipfile
import shapely, shapefile
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SRC=ROOT/'datos/circunscripciones1951_1954'
d=json.loads((HERE/'dataset_1951.json').read_text(encoding='utf8'))
raw=json.loads((SRC/'resultados1951.json').read_text(encoding='utf8'))
minorities=json.loads((HERE/'bancas_minoria_1951.json').read_text(encoding='utf8'))
gan=d['modes'][0]
assert len(d['territories'])==152 and len(raw)==150
assert len(minorities)==10 and Counter(c['codigo']for c in minorities)=={'PP':2,'UCR':8}
assert Counter(r.get('w')for r in gan['units'])=={'PP':144,'UCR':6,None:2}
local=Counter()
for r in raw:
    for c in r['candidatos']:local[c['codigo']]+=c['votos']
assert local['PP']==4482973 and local['UCR']==2396833
assert sum(local.values())==sum(s['v']for s in gan['national']['slices'])==7206873
assert sum(r['metricas']['Votos positivos']for r in raw)==7206893
assert len({(r['provincia'],r['numero'])for r in raw})==150
for r in raw:
    idx=next(i for i,t in enumerate(d['territories'])if t['p']==r['provincia'] and (t['n']==f"Circunscripción {r['numero']}.ª" or t['k']=='territorio nacional'))
    assert sum(line[1]for line in gan['units'][idx]['lines'])==sum(c['votos']for c in r['candidatos'])
assert len(shapefile.Reader(str(HERE/'shp/circunscripciones_1951')))==152
assert len(shapefile.Reader(str(HERE/'shp/bancas_minoria_1951')))==10
assert len(shapefile.Reader(str(HERE/'shp/malvinas_referencia')))==1
geoms,audit,provinces=pickle.loads((HERE/'geometria_adaptada.pkl').read_bytes())['data']
assert all(g.is_valid and not g.is_empty for g in geoms)
assert all(abs(a['cobertura_shp']-1)<1e-5 for a in audit if 'cobertura_shp'in a)
errors=[];checks=[]
with sync_playwright()as p:
    browser=p.chromium.launch(channel='chrome')
    page=browser.new_page(viewport={'width':1920,'height':1700})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((HERE/'atlas_1951.html').as_uri()+'#bare-white-m-gan')
    page.wait_for_timeout(200)
    assert page.locator('#B circle[data-minority]').count()==10
    assert page.locator('#B > path[data-i]').count()==152
    for mode in d['modes']:
        page.evaluate('(m)=>window.__atlas.setMode(m)',mode['id'])
        page.wait_for_timeout(80)
        assert not errors,errors
        box=page.locator('#legend').evaluate('(e)=>{const b=e.getBBox();return {y:b.y,bottom:b.y+b.height}}')
        assert box['bottom']<1649,box
        assert page.locator('#B .mal').get_attribute('d')==page.locator('#pv .pfm').get_attribute('d')
        assert 'bancas adicionales de minoría' in page.locator('#legend').text_content()
        sub=page.locator('#sub').evaluate('(e)=>{const b=e.getBBox();return {x:b.x,right:b.x+b.width}}')
        assert sub['right']<1920,sub
        checks.append(dict(modo=mode['id'],leyenda=box,subtitulo=sub))
        page.locator('#atlas').screenshot(path=str(HERE/f'revision_{mode["id"]}.png'))
    # Cada punto del recuadro de Capital debe seleccionar su circunscripción.
    page.goto((HERE/'atlas_1951.html').as_uri())
    page.wait_for_timeout(100)
    for c in [c for c in minorities if c['provincia']=='Capital Federal']:
        overlay=page.locator(f'#insets svg circle[data-i="{c["indice"]}"]').last
        box=overlay.bounding_box();assert box
        page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
        assert page.locator('#card').is_visible(),errors
        assert 'Banca de minoría' in page.locator('#card').inner_text()
        assert c['nombre'] in page.locator('#card').inner_text()
        page.locator('#card-x').click()
    for button in ('b-svg','b-csv','b-png'):
        with page.expect_download()as download:page.locator('#'+button).click()
        assert download.value.failure()is None
        if button=='b-csv':
            text=Path(download.value.path()).read_text(encoding='utf-8-sig')
            assert len(text.splitlines())==153, len(text.splitlines())
    # Prueba sobre la copia para el sitio, sin modificar HTML fuente.
    sys.path.insert(0,str(ROOT/'sitio'))
    from armar import preparar
    site_file=HERE/'revision_sitio.html'
    site_file.write_text(preparar((HERE/'atlas_1951.html').read_text(encoding='utf8')),encoding='utf8')
    page.goto(site_file.as_uri());page.wait_for_timeout(150)
    assert page.locator('#barnote-d summary').inner_text()=='Fuentes y notas'
    assert not page.locator('#barnote-d').evaluate('(e)=>e.open')
    assert not page.locator('#barnote').is_visible()
    page.locator('#barnote-d summary').click()
    assert page.locator('#barnote').is_visible()
    page.locator('#barnote-d summary').click()
    assert page.locator('.sitio-ind').inner_text()=='Todos los atlas'
    page.locator('#b-rec').click()
    assert page.locator('body').evaluate('(e)=>e.classList.contains("sin-rec")')
    page.locator('#b-rec').click()
    page.screenshot(path=str(HERE/'revision_sitio_escritorio.png'))
    assert page.locator('#B path.dc').first.evaluate('(e)=>getComputedStyle(e).display')=='inline'
    marker=page.locator('#B circle.minor-metro').first
    width=marker.bounding_box()['width']
    for zoom in (8,20):
        page.evaluate('(k)=>window.__atlas.zoomAt(1168,715,k)',zoom)
        page.wait_for_timeout(220)
        # Crecen suavemente hasta un límite visible; nunca se multiplican
        # directamente por el zoom ni quedan microscópicos al acercar.
        assert width*2<marker.bounding_box()['width']<width*3.8,(zoom,width,marker.bounding_box())
    page.screenshot(path=str(HERE/'revision_zoom_amba.png'))
    page.evaluate('window.__atlas.resetZoom()');page.wait_for_timeout(220)
    er4=next(i for i,t in enumerate(d['territories'])if t['p']=='Entre Ríos' and t['n']=='Circunscripción 4.ª')
    page.evaluate('(i)=>window.__atlas.selectUnit(i,false)',er4)
    assert page.locator('#card .c-met').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
    assert page.locator('#card').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
    assert page.locator('#card .nm').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).whiteSpace==="normal"&&e.scrollWidth<=e.clientWidth+1)')
    page.screenshot(path=str(HERE/'revision_ficha.png'))
    page.locator('#card-x').click()
    page.locator(f'#B path[data-i="{er4}"]').dispatch_event('mousemove',dict(clientX=550,clientY=500))
    page.wait_for_timeout(60)
    assert page.locator('#tip .c-met').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
    assert page.locator('#tip .nm').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).whiteSpace==="normal"&&e.scrollWidth<=e.clientWidth+1)')
    page.mouse.move(0,0)
    page.set_viewport_size({'width':390,'height':844})
    page.goto(site_file.as_uri());page.wait_for_timeout(250)
    assert page.locator('body').evaluate('(e)=>e.classList.contains("movil")')
    page.evaluate('(i)=>window.__atlas.selectUnit(i,false)',er4)
    assert page.locator('#card .nm').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).whiteSpace==="normal"&&e.scrollWidth<=e.clientWidth+1)')
    page.locator('#card-x').click()
    page.screenshot(path=str(HERE/'revision_movil.png'))
    assert not errors,errors
    browser.close()
report=dict(unidades=152,resultados=150,puntos_minoria=10,votos_nacionales=7206873,control_gis=True,geometrias_validas=True,errores_js=errors,modos=checks,descargas=['SVG','CSV (152 unidades, sin votos duplicados por puntos)','PNG'],formato_sitio=dict(fuentes_plegables=True,enlace_todos_los_atlas=True,ocultar_recuadros=True,caba_visible_en_mapa=True,puntos_crecimiento_limitado_zoom_8_y_20=True,ficha_y_hover_sin_desborde=True),movil=True)
(HERE/'VALIDACION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
with zipfile.ZipFile(HERE/'circunscripciones_1951_QGIS.zip','w',zipfile.ZIP_DEFLATED)as z:
    for f in (HERE/'shp').iterdir():z.write(f,'shp/'+f.name)
    z.write(HERE/'LEEME_1951.md','LEEME_1951.md')
print('1951: votos, 152 polígonos, 10 minorías, 4 modos, clic en puntos, móvil y descargas verificados.')
