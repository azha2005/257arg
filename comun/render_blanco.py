"""Renderiza todos los modos de un atlas como PNG con fondo blanco (el póster completo, mismo recorte que render_transparentes.py).

    python comun/render_blanco.py mapa1985 atlas_1985.html    -> png_blanco/<carpeta>/<atlas>_<modo>.png
"""
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder, fn = sys.argv[1], sys.argv[2]
OUT = os.path.join(ROOT, "png_blanco", folder)
os.makedirs(OUT, exist_ok=True)
url = "file:///" + os.path.join(ROOT, "mapas", folder, fn).replace("\\", "/")
bad, errs = [], []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1800}, color_scheme="light", device_scale_factor=1)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(800)
    for m in pg.evaluate("DATA.modes.map(m=>m.id)"):
        pg.goto(url + "#m-" + m); pg.reload(); pg.wait_for_timeout(1200)
        on = pg.evaluate("(document.querySelector('#tiles .tile.on')||{dataset:{}}).dataset.mode")
        if on != m: bad.append((m, on))
        pg.add_style_tag(content="html,body{background:#fff!important}#atlas{background:#fff!important}")
        out = os.path.join(OUT, "%s_%s.png" % (os.path.splitext(fn)[0], m))
        pg.locator("#atlas").first.screenshot(path=out, omit_background=False)
        print(out, flush=True)
    b.close()
print("errores de página:", errs)
print("modos que no coinciden con el hash:", bad)
