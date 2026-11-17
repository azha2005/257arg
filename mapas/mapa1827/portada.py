"""og:image (portada.png, 1200x630) y miniaturas del índice del sitio para Buenos Aires 1827.

    python mapas/mapa1827/portada.py
"""
import io, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
URL = (HERE / "atlas_1827.html").as_uri()
MINIS = ROOT / "sitio/miniaturas"


def captura(pg, tema, sel, hash_="#lis"):
    pg.goto("about:blank")
    pg.goto(URL + hash_)
    pg.evaluate(f'document.documentElement.dataset.theme="{tema}"')
    pg.wait_for_timeout(600)
    return Image.open(io.BytesIO(pg.locator(sel).screenshot())).convert("RGB")


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1500, "height": 1300}, device_scale_factor=2)
    mapa_c = captura(pg, "light", "#svg-lis")
    mapa_o = captura(pg, "dark", "#svg-lis")
    hemi = captura(pg, "light", "#hemi-gob", "#gob")
    b.close()

# miniaturas del índice (oscura y clara), como las demás: 640 px de lado mayor
for im, suf in ((mapa_o, ""), (mapa_c, "_claro")):
    t = im.copy(); t.thumbnail((640, 640), Image.LANCZOS)
    t.save(MINIS / f"buenosaires1827__index{suf}.webp", "WEBP", quality=72, method=6)

# portada: mapa a la izquierda, título y hemiciclo a la derecha
W, H = 1200, 630
pap = (252, 252, 250)
por = Image.new("RGB", (W, H), pap)
m = mapa_c.copy(); m.thumbnail((660, 610), Image.LANCZOS)
por.paste(m, (10, (H - m.height) // 2))
h = hemi.copy(); h.thumbnail((470, 260), Image.LANCZOS)
por.paste(h, (W - h.width - 40, H - h.height - 40))
d = ImageDraw.Draw(por)
fb = ImageFont.truetype("arialbd.ttf", 46)
fr = ImageFont.truetype("arial.ttf", 24)
x = 700
d.text((x, 50), "Buenos Aires,", font=fb, fill=(20, 20, 20))
d.text((x, 102), "1827", font=fb, fill=(0, 112, 110))
d.text((x, 172), "La Junta de Representantes que", font=fr, fill=(70, 70, 70))
d.text((x, 202), "eligió gobernador a Dorrego,", font=fr, fill=(70, 70, 70))
d.text((x, 232), "por sección y con voto popular estimado", font=fr, fill=(70, 70, 70))
por.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(HERE / "portada.png", optimize=True)   # liviana para la tarjeta de X
print("listo")
