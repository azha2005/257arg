"""PNG de control de un atlas de esta carpeta: cada modo en cada nivel del selector, con fondo blanco.
    python mapas/mapaPBA2025sep/render.py atlas_pba2025sep.html [modo ...]  -> img/<atlas>_<nivel>_<modo>.png (img/ fuera de git)
Informa errores de la pagina y comprueba que los totales de cada nivel coincidan."""
import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
fn = sys.argv[1]; only = sys.argv[2:]
OUT = os.path.join(HERE, "img"); os.makedirs(OUT, exist_ok=True)
url = "file:///" + os.path.join(HERE, fn).replace("\\", "/")
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1800}, device_scale_factor=1)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(1000)
    modes = pg.evaluate("DATA.modes.map(m=>m.id)")
    levels = pg.evaluate("[...document.querySelectorAll('#niv button')].map(b=>b.dataset.n)") or ["-"]
    for m in (only or modes):
        for lv in levels:
            pg.goto(url + ("#nv-" + lv + "-" if lv != "-" else "#") + "m-" + m); pg.reload(); pg.wait_for_timeout(1500)
            pg.add_style_tag(content="html,body{background:#fff!important}#atlas{background:#fff!important}")
            out = os.path.join(OUT, "%s_%s_%s.png" % (os.path.splitext(fn)[0], lv, m))
            pg.locator("#atlas").first.screenshot(path=out)
            print(out, flush=True)
    b.close()
print("errores de pagina:", errs)
