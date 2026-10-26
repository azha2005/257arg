"""Renderiza todos los modos de todos los atlas como PNG con fondo transparente (1892x1625, el póster completo).

    python render_transparentes.py [carpeta ...]   -> png_transparentes/<carpeta>/<atlas>_<modo>.png
"""
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
ATLAS = [("mapa1912", "atlas_1912_diputados.html"), ("mapa1914", "atlas_1914_diputados.html"), ("mapa1916dip", "atlas_1916_diputados.html"), ("mapa1916fic", "atlas_1916_alt.html"), ("mapa1922", "atlas_1922.html"),
         ("mapa1928", "atlas_1928.html"), ("mapa1930", "atlas_1930.html"), ("mapa1983", "atlas_1983.html"), ("mapa1985", "atlas_1985.html"), ("mapa1987", "atlas_1987.html"), ("mapa1989", "atlas_1989.html"), ("mapa1991", "atlas_1991.html"), ("mapa1993", "atlas_1993.html"), ("mapa1994", "atlas_1994.html"), ("mapa1995", "atlas_1995.html"), ("mapa1995", "atlas_1995_ucr_frepaso.html"), ("mapa1997", "atlas_1997.html"), ("mapa2001", "atlas_2001.html"), ("mapa2013", "atlas_2013.html"), ("mapaAMBA2025", "atlas_amba2025.html")]
ATLAS.append(("mapa2009", "atlas_2009.html"))
ATLAS.append(("mapa2027", "atlas_2027.html"))
ATLAS.append(("mapa2027kic", "atlas_2027kic.html"))
ATLAS.append(("mapa1985hip", "atlas_1985hip.html"))
ATLAS.extend((f"mapa{y}dip", f"atlas_{y}_diputados.html") for y in (1983, 1989, 1995, 1999))
ATLAS.append(("mapa2001bronca", "atlas_2001bronca.html"))
ATLAS.extend((f"mapa{y}", f"atlas_{y}.html") for y in (1958, 1962, 1965))   # Cantón (canton5865/atlas5865.py)
ATLAS.extend((f"mapa{y}", f"atlas_{y}.html") for y in (2003,2005,2007,2011,2015,2017,2019,2021,2023,2025))
OUT = os.path.join(ROOT, "png_transparentes")
bad = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1800}, color_scheme="light", device_scale_factor=1)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    for folder, fn in [a for a in ATLAS if not sys.argv[1:] or a[0] in sys.argv[1:]]:   # opcional: python render_transparentes.py mapa1995
        url = "file:///" + os.path.join(ROOT, folder, fn).replace("\\", "/")
        pg.goto(url); pg.wait_for_timeout(800)
        modes = pg.evaluate("DATA.modes.map(m=>m.id)")
        os.makedirs(os.path.join(OUT, folder), exist_ok=True)
        for m in modes:
            pg.goto(url + "#m-" + m); pg.reload(); pg.wait_for_timeout(1200)
            on = pg.evaluate("(document.querySelector('#tiles .tile.on')||{dataset:{}}).dataset.mode")
            if on != m: bad.append((folder, m, on))
            pg.add_style_tag(content="html,body{background:transparent!important}")
            out = os.path.join(OUT, folder, "%s_%s.png" % (os.path.splitext(fn)[0], m))
            pg.locator("#atlas").first.screenshot(path=out, omit_background=True)
            print(out, flush=True)
    b.close()
print("errores de página:", errs)
print("modos que no coinciden con el hash:", bad)
