"""Capturas para el segundo tuit del post (4-nov-2026): mapa, bancas y AMBA de tres vistas de mapa_257.html.
    python analisis/uninominal/imagenes_post.py   ->  analisis/uninominal/img/post_<vista>.png"""
import os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "file:///" + os.path.join(HERE, "mapa_257.html").replace(os.sep, "/")
VISTAS = {"2025_todos": ("modo=0&dep=0&ren=full&elec=2&pt=1&dl=1", "Diputados 2025 · cada partido por separado · plan neutral"),
          "2023_todos": ("modo=0&dep=0&ren=full&elec=0&pt=1&dl=1", "General 2023 · cada partido por separado · plan neutral"),
          "gerrymander_lla": ("modo=3&dep=0&ren=full&elec=2&pt=0&dl=1", "Diputados 2025 · dos bloques · distritos dibujados a favor de LLA")}
# rótulo arriba (la imagen se lee sola en X) y dirección abajo
ROTULO = """([t]) => { const m = document.querySelector('main');
  const d = document.createElement('div'); d.style.cssText = 'grid-column:1/-1;display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap';
  d.innerHTML = `<h2 style="font-size:1.6rem">257 distritos uninominales: ${t}</h2><span style="font-weight:600;color:var(--color-muted)">azha2005.github.io/257arg/uninominal</span>`;
  m.prepend(d); }"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1360, "height": 1000}, device_scale_factor=2)
    for k, (h, t) in VISTAS.items():
        pg.goto("about:blank"); pg.goto(SRC + "#" + h)
        pg.wait_for_selector("#res .hemi svg"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(1200)
        pg.evaluate(ROTULO, [t]); pg.wait_for_timeout(300)
        r = pg.locator("main").bounding_box()   # sin el margen de abajo, donde asoma la tabla por provincia
        pg.screenshot(path=os.path.join(HERE, "img", f"post_{k}.png"), full_page=True,
                      clip={"x": r["x"], "y": r["y"], "width": r["width"], "height": r["height"] - 24})
        print(k, pg.evaluate("[...document.querySelectorAll('#res tbody tr')].map(t=>t.cells[0].textContent+' '+t.cells[1].textContent).join(', ')"))
    b.close()
