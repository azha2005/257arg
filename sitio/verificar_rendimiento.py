"""Regresión de los parches de publicación; no necesita datos externos.

python sitio/verificar_rendimiento.py
python sitio/verificar_rendimiento.py --navegador scratch_perf/despues
La segunda opción usa Playwright y Chrome instalados y un sitio ya construido.
"""
import argparse
import glob
import json
from pathlib import Path
import re
import subprocess

from armar import ROOT, entradas, preparar
from catalogo import EXTRA
from rendimiento import MARCA


def verificar_fuentes():
    rutas = {str(Path(ROOT) / e[0]) for e in entradas()}
    for patron in EXTRA:
        rutas.update(glob.glob(str(Path(ROOT) / patron)))
    total = 0
    scripts = []
    for ruta in sorted(rutas):
        original = Path(ruta).read_text(encoding="utf8")
        nuevo = preparar(original)
        assert preparar(nuevo) == nuevo, f"No es idempotente: {ruta}"
        if 'svg.addEventListener("mousemove",ev=>{' not in original:
            assert nuevo == original, ruta
            continue
        assert MARCA in nuevo, ruta
        # Datos electorales y geometría del póster, idénticos byte por byte.
        a = original.index('const DATA=') + len('const DATA=')
        b = nuevo.index('const DATA=') + len('const DATA=')
        largo = original.index('const START_MODE=', a) - a
        assert original[a:a+largo] == nuevo[b:b+largo], f"Cambió DATA: {ruta}"
        for patron in (r'<svg id="atlas".*</svg>',):
            x = re.search(patron, original[:a], re.S)
            y = re.search(patron, nuevo[:b], re.S)
            assert x and y and x[0] == y[0], f"Cambió el SVG: {ruta}"
        # Compilar también todos los cierres específicos (PASO, niveles, sets…),
        # omitiendo únicamente el literal DATA que ya se comparó arriba.
        sin_datos = nuevo[:b] + '{};\n' + nuevo[b+largo:]
        bloques = re.findall(r'<script>(.*?)</script>', sin_datos, re.S)
        scripts.extend((ruta, s) for s in bloques)
        total += 1
    checker = "const vm=require('node:vm');let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',c=>s+=c);process.stdin.on('end',()=>{for(const [filename,code] of JSON.parse(s))new vm.Script(code,{filename});});"
    subprocess.run(['node', '-e', checker], input=json.dumps(scripts), text=True,
                   encoding='utf8', check=True)
    print(f"{total} atlas: datos, geometría, idempotencia y sintaxis JS correctos.", flush=True)


def verificar_navegador(destino, solo_movil=False):
    from playwright.sync_api import sync_playwright
    rutas = [
        'mapas/mapa1983/atlas_1983.html',
        'mapas/mapa1965/atlas_1965.html',
        'mapas/mapa2027/atlas_2027.html',
        'mapas/mapa2003escenarios/atlas_2003_sin_k.html',
        'mapas/serieAMBA2005_2023radios/atlas_2023pasointernas.html',
        'mapas/serieAMBA2005_2023radios/atlas_2023pasocand.html',
        'mapas/mapaAMBA2025radios/atlas_amba2025radios.html',
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome')
        casos = ([] if solo_movil else [(False, r) for r in rutas]) + [(True, rutas[0]), (True, rutas[-1])]
        for movil, ruta in casos:
            pg = browser.new_page(viewport={'width': 390 if movil else 1366, 'height': 844 if movil else 900},
                                  has_touch=movil, is_mobile=movil)
            errores = []
            pg.on('pageerror', lambda e: errores.append(str(e)))
            pg.goto((Path(destino).resolve() / ruta).as_uri(), timeout=120000)
            pg.wait_for_timeout(150)
            info = pg.evaluate('''async () => {
              const frame=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
              const sv=document.querySelector('#atlas'),api=window.__atlas;
              const nodes=[...sv.querySelectorAll('#mainwrap [data-i]')];
              const target=nodes.find(e=>{let r=e.getBoundingClientRect();return r.width>2&&r.height>2});
              const i=+target.dataset.i;
              const body=document.body, mobile=body.classList.contains('movil');
              if(mobile)for(const vista of ['res','rec','todo','mapa']){
                document.querySelector('#m-vis [data-v="'+vista+'"]').click();await frame();
                if(!sv.getAttribute('viewBox').split(/[ ,]+/).every(x=>Number.isFinite(+x)))throw Error('viewBox inválido');
              }
              for(const mode of DATA.modes){
                api.setMode(mode.id);await frame();
                if(api.mode!==mode.id)throw Error('No cambió el modo');
              }
              for(const level of document.querySelectorAll('#niv button')){level.click();await frame();}
              const radio=document.querySelector('#niv [data-n="r"]');if(radio)radio.click();
              api.setMode(DATA.modes[0].id);await frame();
              api.selectUnit(i,false);await frame();
              if(document.querySelector('#card').hidden)throw Error('No abrió la ficha');
              api.selectProv(DATA.territories[i].p,false);await frame();
              if(!sv.querySelector('.dim')&&new Set(DATA.territories.map(t=>t.p)).size>1)throw Error('No destacó la provincia');
              api.clearSel();await frame();
              if(sv.querySelector('.sel,.dim'))throw Error('No limpió el resaltado');
              api.zoomAt(900,800,2);await frame();
              let transforms=0,strokes=0;
              const z=sv.querySelector('#zoomg'),mw=sv.querySelector('#mainwrap');
              const observer=new MutationObserver(ms=>{for(const m of ms)if(m.target===z)transforms++;else strokes++;});
              observer.observe(z,{attributes:true,attributeFilter:['transform']});
              observer.observe(mw,{attributes:true,attributeFilter:['style']});
              const pt=new DOMPoint(900,800).matrixTransform(sv.getScreenCTM());
              const pe=(type,x)=>new PointerEvent(type,{bubbles:true,pointerId:1,pointerType:'mouse',button:0,clientX:pt.x+x,clientY:pt.y});
              sv.dispatchEvent(pe('pointerdown',0));
              for(let n=0;n<60;n++)window.dispatchEvent(pe('pointermove',n+6));
              window.dispatchEvent(pe('pointerup',66));await frame();observer.disconnect();
              if(transforms!==1||strokes!==0)throw Error('Arrastre sin agrupar: '+transforms+'/'+strokes);
              if(window.getSelection().toString())throw Error('Seleccionó texto al arrastrar');
              if(getComputedStyle(sv.querySelector('text')).userSelect!=='none')throw Error('Texto seleccionable');
              // Cancelar el puntero no puede dejar un arrastre pendiente.
              const cancelBefore=z.getAttribute('transform');
              sv.dispatchEvent(pe('pointerdown',0));window.dispatchEvent(pe('pointercancel',0));
              window.dispatchEvent(pe('pointermove',60));await frame();
              if(z.getAttribute('transform')!==cancelBefore)throw Error('Arrastre después de pointercancel');
              let rebuilds=0;const tip=document.querySelector('#tip');
              const to=new MutationObserver(ms=>rebuilds+=ms.filter(m=>m.target===tip&&m.type==='childList').length);to.observe(tip,{childList:true});
              for(let n=0;n<120;n++)target.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:700+n%4,clientY:300}));
              await frame();to.disconnect();
              if(rebuilds>(mobile?0:2))throw Error('Fichas redundantes: '+rebuilds);
              api.resetZoom();await frame();
              if(mobile){
                const touch=(id,x)=>new Touch({identifier:id,target:sv,clientX:x,clientY:300});
                const pinch=(type,d)=>sv.dispatchEvent(new TouchEvent(type,{bubbles:true,cancelable:true,touches:[touch(1,150-d/2),touch(2,150+d/2)]}));
                pinch('touchstart',100);pinch('touchmove',120);pinch('touchmove',150);
                sv.dispatchEvent(new TouchEvent('touchend',{bubbles:true,touches:[]}));await frame();
                if(Math.abs(api.zoom-1.5)>.001)throw Error('Se perdió parte del pellizco: '+api.zoom);
                api.resetZoom();await frame();
              }
              return {mobile,modes:DATA.modes.length,paths:sv.querySelectorAll('path').length,transforms,strokes,rebuilds};
            }''')
            assert not errores, (ruta, errores)
            # Verificar las tres descargas con un visor representativo.
            if ruta == rutas[0] and not movil:
                for button, suffix in [('b-svg','.svg'),('b-png','.png'),('b-csv','.csv')]:
                    with pg.expect_download(timeout=30000) as descarga:
                        pg.locator('#'+button).click()
                    assert descarga.value.suggested_filename.endswith(suffix)
                    assert not descarga.value.failure()
            if (ruta == rutas[0] and not movil) or (ruta == rutas[-1] and movil):
                pg.mouse.move(0, 0)
                pg.screenshot(path=str(Path(destino).resolve().parent / ('qa_movil.png' if movil else 'qa_escritorio.png')))
            print(ruta, json.dumps(info), flush=True)
            pg.close()
        browser.close()


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--navegador')
    args.add_argument('--solo-movil', action='store_true')
    opts = args.parse_args()
    verificar_fuentes()
    if opts.navegador:
        verificar_navegador(opts.navegador, opts.solo_movil)
