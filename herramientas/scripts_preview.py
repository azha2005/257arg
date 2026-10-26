"""Genera un PNG de vista previa (modo GANÓ, fondo claro) para cada atlas.
    python scripts_preview.py      (necesita el servidor local: python -m http.server 8765)"""
import os
from playwright.sync_api import sync_playwright

ATLAS = [("mapas/mapa1916dip/atlas_1916_diputados.html", "mapas/mapa1916dip/vista_1916.png"),
         ("mapas/mapa1922/atlas_1922.html", "mapas/mapa1922/vista_1922.png"),
         ("mapas/mapa1928/atlas_1928.html", "mapas/mapa1928/vista_1928.png"),
         ("mapas/mapa1930/atlas_1930.html", "mapas/mapa1930/vista_1930.png")]
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1800}, color_scheme="light", device_scale_factor=1)
    for src, out in ATLAS:
        pg.goto("http://127.0.0.1:8765/" + src); pg.wait_for_timeout(1500)
        svg = pg.locator("#atlas").first
        svg.screenshot(path=out)
        print(out, os.path.getsize(out))
    b.close()
