"""Vistas previas PNG (1920x1650, fondo transparente) de la línea alternativa:  python preview.py [modo ...]"""
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
modes = sys.argv[1:] or ["gan"]
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1800}, color_scheme="light", device_scale_factor=1)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    for m in modes:
        pg.goto("file:///" + HERE.replace("\\", "/") + "/atlas_1916_alt.html#m-" + m); pg.reload(); pg.wait_for_timeout(1500)
        pg.add_style_tag(content="html,body{background:transparent!important}")
        out = os.path.join(HERE, "vista_1916alt_%s.png" % m)
        pg.locator("#atlas").first.screenshot(path=out, omit_background=True); print(out)
    print("errores:", errs)
    b.close()
