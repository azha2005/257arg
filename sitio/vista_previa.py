"""Imagen para compartir el índice del sitio (og:image, 1200x630) -> sitio/vista_previa.png (4-nov-2026).
    python sitio/vista_previa.py
Cuatro pósters «Ganó» de png_blanco/ (1904, 1946, balotaje 2023 y AMBA 2025 por radio) junto al título del sitio.
El número de atlas sale de catalogo.py. Playwright con el Chrome del sistema; Epilogue de mapas/mapa2003alt/assets/."""
import base64, io, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from catalogo import GRUPOS

POSTERS = ["png_blanco/mapa1904/atlas_1904_gan.png", "png_blanco/mapa1946/atlas_1946_gan.png",
           "png_blanco/mapa2023bal/atlas_2023bal_gan.png", "png_blanco/mapaAMBA2025radios/atlas_amba2025radios_gan.png"]


def uri(path, ancho=None):
    if ancho:
        im = Image.open(os.path.join(ROOT, path)).convert("RGB"); im.thumbnail((ancho, ancho), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=92)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    return "data:font/woff2;base64," + base64.b64encode(open(os.path.join(ROOT, path), "rb").read()).decode()


def main():
    n = sum(len(g[3]) for g in GRUPOS)
    fuentes = "".join(f'@font-face{{font-family:E;font-weight:{w};src:url("{uri(f"mapas/mapa2003alt/assets/epilogue-{w}.woff2")}") format("woff2")}}'
                      for w in (400, 600, 700))
    imgs = "".join(f'<div class="p"><img src="{uri(p, 900)}" alt=""></div>' for p in POSTERS)
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{fuentes}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#fcfcfa;font-family:E,sans-serif;color:#1b1b1b}}
.t{{display:grid;grid-template-columns:480px 1fr;height:630px}}
.izq{{display:flex;flex-direction:column;justify-content:center;gap:20px;padding:0 24px 0 52px}}
h1{{margin:0;font-size:54px;font-weight:700;letter-spacing:-.045em;line-height:.98}}
.r{{font-size:40px;font-weight:700;letter-spacing:-.03em;color:#13756f;font-variant-numeric:tabular-nums}}
.d{{font-size:22px;line-height:1.4;color:#5a5a56}}
.u{{margin-top:14px;padding-top:16px;border-top:1px solid #dcdcd6;font-size:21px;font-weight:600}}
.g{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:10px;padding:14px 14px 14px 0}}
.p{{background:#fff;border:1px solid #e2e2dc;border-radius:6px;overflow:hidden;display:flex;align-items:center;justify-content:center}}
.p img{{width:100%;height:100%;object-fit:contain;display:block}}</style></head><body><div class="t">
<div class="izq"><h1>Atlas electorales de la Argentina</h1><div class="r">1904-2025</div>
<div class="d">{n} mapas interactivos por circunscripción, departamento, circuito y radio censal. PASO, escenarios y 257 distritos uninominales.</div>
<div class="u">azha2005.github.io/257arg</div></div>
<div class="g">{imgs}</div></div></body></html>"""
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=2)
        pg.set_content(doc); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB").resize((1200, 630), Image.LANCZOS)
        im.save(os.path.join(HERE, "vista_previa.png"), optimize=True)
        b.close()
    print("sitio/vista_previa.png:", n, "atlas")


if __name__ == "__main__":
    main()
