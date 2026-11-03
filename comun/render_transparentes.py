"""Renderiza todos los modos de todos los atlas como PNG con fondo transparente (1892x1625, el póster completo).

    python comun/render_transparentes.py [carpeta ...]   -> png_transparentes/<carpeta>/<atlas>_<modo>.png
"""
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATLAS = [("mapa1912", "atlas_1912_diputados.html"), ("mapa1914", "atlas_1914_diputados.html"), ("mapa1916dip", "atlas_1916_diputados.html"), ("mapa1916fic", "atlas_1916_alt.html"), ("mapa1922", "atlas_1922.html"),
         ("mapa1928", "atlas_1928.html"), ("mapa1930", "atlas_1930.html"), ("mapa1983", "atlas_1983.html"), ("mapa1985", "atlas_1985.html"), ("mapa1987", "atlas_1987.html"), ("mapa1989", "atlas_1989.html"), ("mapa1991", "atlas_1991.html"), ("mapa1993", "atlas_1993.html"), ("mapa1994", "atlas_1994.html"), ("mapa1995", "atlas_1995.html"), ("mapa1995", "atlas_1995_ucr_frepaso.html"), ("mapa1999", "atlas_1999.html"), ("mapa1997", "atlas_1997.html"), ("mapa2001", "atlas_2001.html"), ("mapa2013", "atlas_2013.html"), ("mapaAMBA2025", "atlas_amba2025.html")]
ATLAS.append(("mapa2009", "atlas_2009.html"))
ATLAS.append(("mapa1904", "atlas_1904.html"))
ATLAS.append(("mapa1951", "atlas_1951.html"))
ATLAS.append(("mapa2027", "atlas_2027.html"))
ATLAS.append(("mapa2027kic", "atlas_2027kic.html"))
ATLAS.append(("mapa2023massa", "atlas_2023massa.html"))
ATLAS.extend((f"mapa{k}", f"atlas_{k}.html") for k in
             ("2003pres", "2007pres", "2011pres", "2015pres", "2015bal", "2019pres", "2023pres", "2023bal"))
ATLAS.append(("mapa1985hip", "atlas_1985hip.html"))
ATLAS.append(("mapa1983hipotetico", "atlas_1983_hipotetico.html"))
ATLAS.append(("mapa1985peronismo", "atlas_1985_peronismo.html"))
ATLAS.append(("mapa1989convergencia", "atlas_1989_convergencia.html"))
ATLAS.extend((f"mapa{y}dip", f"atlas_{y}_diputados.html") for y in (1983, 1989, 1995, 1999))
ATLAS.append(("mapa2001bronca", "atlas_2001bronca.html"))
ATLAS.extend((f"mapa{y}", f"atlas_{y}.html") for y in (1958, 1962, 1965))   # Cantón (canton5865/atlas5865.py)
ATLAS.extend((f"mapa{y}", f"atlas_{y}.html") for y in (2003,2005,2007,2011,2015,2017,2019,2021,2023,2025))
ATLAS.extend(("mapa2003escenarios", f"atlas_2003_sin_{c}.html") for c in
             ("m","k","l","r","c","moreau","walsh","bravo","altamira","venturino",
              "sullings","arcagni","mazzitelli","zaffore","herrera","breide","mussa","teran"))
ATLAS.extend(("mapaAMBA2025radios", f) for f in ("atlas_amba2025radios.html", "atlas_amba2025radios_pob.html"))   # por radio censal (método de Poblaciones)
ATLAS.extend(("mapaAMBA2003radios", f) for f in ("atlas_amba2003radios.html", "atlas_amba2003radios_pob.html"))   # presidenciales 2003 por radio 2001 (escuelas 2025)
ATLAS.extend([("mapaAMBA2007", "atlas_amba2007.html"), ("mapa2007circuitos", "atlas_2007circuitos.html")])
OUT = os.path.join(ROOT, "png_transparentes")
ATLAS.extend(("serieAMBA2005_2023radios", f"atlas_{k}.html") for k in
             [f"{y}dip" for y in range(2005, 2024, 2)] +
             [f"{y}pres" for y in (2007, 2011, 2015, 2019, 2023)] + ["2015bal", "2023bal", "2023pasofuerza", "2023pasocand"])
ATLAS.append(("serieAMBA2005_2023radios", "atlas_2023pasointernas.html"))
bad = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1800}, color_scheme="light", device_scale_factor=1)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    for folder, fn in [a for a in ATLAS if not sys.argv[1:] or a[0] in sys.argv[1:]]:   # opcional: python render_transparentes.py mapa1995
        url = "file:///" + os.path.join(ROOT, "mapas", folder, fn).replace("\\", "/")
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
