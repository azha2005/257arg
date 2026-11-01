"""Imagenes para Twitter del atlas por radio (mismo poster que atlas_amba2025radios.html, a mas resolucion).
  python exportar_tw.py   -> tw/1_principal_gan.png (tuit) y tw/2..5_*.png (los otros modos, para la respuesta)
Twitter acepta hasta 4096 px por lado y pasa a JPEG los PNG de mas de 5 MB (y el JPEG mancha los bordes finos):
se renderiza a 4080 px de ancho y se guarda con paleta de 256 colores (el mapa usa pocos tonos)."""
import os, io, sys
from playwright.sync_api import sync_playwright
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tw")
os.makedirs(OUT, exist_ok=True)
URL = "file:///" + os.path.join(HERE, "atlas_amba2025radios.html").replace("\\", "/")
DPR = 4080 / 1920
SHOTS = [("1_principal_gan", "gan"), ("2_fuerza_patria", "fp"), ("3_la_libertad_avanza", "lla"), ("4_frente_de_izquierda", "fit"), ("5_participacion", "par")]


def save(png, path):
    im = Image.open(io.BytesIO(png)).convert("RGB")
    q = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(path, optimize=True)
    print(path, im.size, round(os.path.getsize(path) / 1e6, 2), "MB", flush=True)


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1800}, color_scheme="light", device_scale_factor=DPR)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    for name, mode in SHOTS:
        pg.goto(URL + "#m-" + mode); pg.reload(); pg.wait_for_timeout(2500)
        pg.add_style_tag(content="html,body{background:#fff!important}#atlas{background:#fff!important}")
        # a 2,1x el borde de 0,3 px de los radios aclaraba el conurbano: en la exportacion va mas fino
        pg.evaluate("document.getElementById('mainwrap').style.setProperty('--sd','0.18px')")
        pg.wait_for_timeout(500)
        save(pg.locator("#atlas").first.screenshot(omit_background=False), os.path.join(OUT, name + ".png"))
    b.close()
print("errores de pagina:", errs)
