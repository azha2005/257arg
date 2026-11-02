"""Controles de datos e interacción de la nueva serie presidencial nacional.

python herramientas/validar_pres2003_2023.py [--render]
--render genera todos los PNG mediante el verificador vigente de diputados.
"""
from pathlib import Path
from collections import Counter
import json, sys, subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'comun'))
from pres2003_2023_data import KEYS, read_atlas
from leg2003_2025_data import D2P
from names import norm

report = []
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome')
    page = browser.new_page(viewport=dict(width=1920,height=1800))
    errors = []
    page.on('pageerror',lambda e:errors.append(str(e)))
    for key in KEYS:
        folder = ROOT/f'mapas/mapa{key}'
        ds = json.loads((folder/f'dataset_{key}.json').read_text(encoding='utf8'))
        ctl = json.loads((folder/'control_cobertura.json').read_text(encoding='utf8'))
        gan = ds['modes'][0]
        assert len({m['id'] for m in ds['modes']}) == len(ds['modes'])
        assert all(len(m['units']) == len(ds['territories']) for m in ds['modes'])
        wins = Counter(r['w'] for r in gan['units'] if 'w' in r)
        assert set(wins) == {c['code'] for c in gan['national']['cands']}
        assert sum(s['v'] for s in gan['national']['slices']) == ctl['national']['positivos']
        assert all(s['v'] > 0 for s in gan['national']['slices'])
        assert len(ds['insets']) == 7
        cne_file=ROOT/'datos/fuentes_leg2003_2025/presidenciales/busqueda_faltantes/cne/CONTROL_INCORPORACION.json'
        cne_rows=json.loads(cne_file.read_text(encoding='utf8')) if cne_file.exists() else []
        for x in cne_rows:
            if key != x['archivo'][:4]+'bal': continue
            matches=[r for t,r in zip(ds['territories'],gan['units'])
                     if t['p']==D2P[x['distrito']] and norm(t['n'])==norm(x['nombre'])]
            assert len(matches)==1,(key,x['nombre'])
            r=matches[0]
            observed={c:n for c,n,*_ in r['lines'] if not c.startswith('P_')}
            assert observed=={q['codigo']:q['votos'] for q in x['partidos']},(key,x['nombre'],observed)
            assert r['w']==max(observed,key=observed.get)
            assert dict(r['metrics'])['Inscriptos']==f"{x['inscriptos_pantalla']:,}".replace(',','.')
            assert dict(r['metrics'])['Votantes']==f"{x['emitidos']:,}".replace(',','.')
            assert x['archivo'] in r['note'] and not r.get('fill')
        for t,r in zip(ds['territories'],gan['units']):
            if t['n'] == 'Islas Malvinas':
                assert r['fill'] == '#a9a9a9' and not r['lines']
                continue
            votes = [n for c,n,*_ in r['lines'] if not c.startswith('P_')]
            assert all(isinstance(n,int) and n >= 0 for n in votes)
            if r.get('w'):
                assert max(votes) == next(n for c,n,*_ in r['lines'] if c == r['w'])
                assert abs(sum(pct for c,n,pct in r['lines'] if not c.startswith('P_')) - 100) < .2
        # 2003: las cinco imágenes y proporciones son exactamente las del atlas por radio.
        if key == '2003pres':
            original = read_atlas(ROOT/'mapas/mapaAMBA2003radios/atlas_amba2003radios.html')['candidates']
            for c in 'MKLRC':
                for field in ('img','ar','bl'):
                    assert ds['candidates'][c][field] == original[c][field], (c,field)
        page.goto((folder/f'atlas_{key}.html').as_uri())
        page.wait_for_function('window.__atlas && document.querySelector("#tiles .on")')
        for m in ds['modes']:
            page.evaluate('(m)=>window.__atlas.setMode(m)',m['id'])
            info = page.evaluate('''()=>{
              const rects=[...document.querySelectorAll('#tiles rect')].map(r=>({x:+r.getAttribute('x'),w:+r.getAttribute('width')}));
              const year=document.querySelector('#yearbox').getBBox();
              const L=document.querySelector('#legend'),b=L.getBBox(),t=L.transform.baseVal.consolidate();
              return {active:document.querySelector('#tiles .on').dataset.mode,tiles:rects,
                yearRight:year.x+year.width,legendBottom:b.y+b.height+(t?t.matrix.f:0)};
            }''')
            assert info['active'] == m['id']
            assert len(info['tiles']) == len(ds['modes'])
            assert info['yearRight'] < info['tiles'][0]['x']
            assert all(a['x']+a['w'] <= b['x'] for a,b in zip(info['tiles'],info['tiles'][1:])), (key,info)
            assert info['legendBottom'] <= 1640
            assert not errors, (key,errors)
        assert page.locator('#otras-elecciones a').count() >= 1
        for a in page.locator('#otras-elecciones a').all():
            assert (folder/a.get_attribute('href')).resolve().exists()
        # Comparar el dibujo real del logo contra su referencia por radio.
        # El desplazamiento vertical de la fila cambia; el zoom y el marco, no.
        page.evaluate('window.__atlas.setMode("gan")')
        geometry_js = '''()=>Object.fromEntries([...document.querySelectorAll('#legend image')].map(e=>[
          e.getAttribute('href'),Object.fromEntries(['x','y','width','height'].map(k=>[k,+e.getAttribute(k)]).concat(
            ['x','width','height'].map(k=>['clip_'+k,+e.parentNode.getAttribute(k)])))]))'''
        rendered = page.evaluate(geometry_js)
        ref_page = browser.new_page(viewport=dict(width=1920,height=1800))
        ref_page.goto((ROOT/ctl['logos_source']).as_uri())
        ref_page.wait_for_function('window.__atlas && document.querySelector("#tiles .on")')
        reference = ref_page.evaluate(geometry_js)
        comparisons = 0
        for c in gan['national']['cands']:
            uri = ds['candidates'][c['code']].get('img')
            if uri and uri in reference:
                assert uri in rendered
                for field,value in reference[uri].items():
                    assert abs(rendered[uri][field]-value) < .01, (key,c['code'],field,rendered[uri],reference[uri])
                comparisons += 1
        ref_page.close()
        report.append(dict(key=key,units=ctl['units'],with_data=ctl['with_data'],missing=ctl['missing'],
                           modes=len(ds['modes']),data_ok=True,js_errors=[],title_and_tabs_ok=True,logos_geometry_matches_radio=comparisons))
        print(key,'datos y modos OK',flush=True)
    browser.close()

# Los doce atlas de diputados siguen en el catálogo, incluidos todos los años presidenciales.
sys.path.insert(0,str(ROOT/'sitio'))
from catalogo import GRUPOS
items = [e for g in GRUPOS for e in g[3]]
for year in range(2003,2026,2):
    route = f'mapas/mapa{year}/atlas_{year}.html'
    assert any(e[0] == route for e in items) and (ROOT/route).exists()
    ds = json.loads((ROOT/f'mapas/mapa{year}/dataset_{year}.json').read_text(encoding='utf8'))
    assert 'legislativ' in ds['title'].lower()
out = ROOT/'analisis/revision_pres2003_2023';out.mkdir(exist_ok=True)
(out/'VALIDACION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--render' in sys.argv:
    subprocess.run([sys.executable,str(ROOT/'herramientas/validar_render_leg2003_2025.py'),*KEYS],check=True,cwd=ROOT)
if '--sitio' in sys.argv:
    site = Path(sys.argv[sys.argv.index('--sitio')+1]).resolve()
    site_report = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome')
        for mobile in (False,True):
            page = browser.new_page(viewport=dict(width=390 if mobile else 1366,height=844 if mobile else 900),
                                    is_mobile=mobile,has_touch=mobile)
            errs = []
            page.on('pageerror',lambda e:errs.append(str(e)))
            for key in KEYS:
                page.goto((site/f'mapas/mapa{key}/atlas_{key}.html').as_uri())
                page.wait_for_function('window.__atlas && document.querySelector("#tiles .on")')
                page.evaluate('document.fonts.ready')
                assert page.locator('a.sitio-ind').count() == 1
                ds = json.loads((ROOT/f'mapas/mapa{key}/dataset_{key}.json').read_text(encoding='utf8'))
                if mobile:
                    assert page.locator('body.movil').count() == 1
                    assert page.locator('#m-modo option').count() == len(ds['modes'])
                    for view in ('res','rec','todo','mapa'):
                        page.locator(f'#m-vis [data-v="{view}"]').click()
                        assert page.locator('body').get_attribute('data-vista') == view
                        assert page.evaluate("document.querySelector('#atlas').getAttribute('viewBox').split(/[ ,]+/).every(n=>Number.isFinite(+n))")
                    for m in ds['modes']:
                        page.locator('#m-modo').select_option(m['id'])
                        assert page.evaluate('window.__atlas.mode') == m['id']
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                else:
                    for m in ds['modes']:
                        page.evaluate('(m)=>window.__atlas.setMode(m)',m['id'])
                        assert page.evaluate('window.__atlas.mode') == m['id']
                page.evaluate('window.__atlas.setMode("gan");window.__atlas.selectUnit(0,false)')
                assert not page.locator('#card').get_attribute('hidden')
                assert page.locator('#card-body').inner_text().strip()
                page.evaluate('window.__atlas.clearSel()')
                if not mobile and key == '2003pres':
                    for button,suffix in [('b-svg','.svg'),('b-png','.png'),('b-csv','.csv')]:
                        with page.expect_download(timeout=30000) as event:
                            page.locator('#'+button).click()
                        download = event.value
                        assert download.suggested_filename.endswith(suffix) and not download.failure()
                        assert Path(download.path()).stat().st_size > 100
                assert not errs, (key,mobile,errs)
                if key in ('2003pres','2023bal'):
                    page.screenshot(path=str(out/f'{key}_{"movil" if mobile else "escritorio"}.png'))
                site_report.append(dict(key=key,mobile=mobile,views_ok=True,modes_ok=True,card_ok=True,js_errors=[]))
                print(key,'sitio', 'celular' if mobile else 'escritorio','OK',flush=True)
            page.close()
        browser.close()
    (out/'VALIDACION_SITIO.json').write_text(json.dumps(site_report,ensure_ascii=False,indent=2),encoding='utf8')
print('Ocho presidenciales y doce atlas de diputados: controles correctos.',flush=True)
