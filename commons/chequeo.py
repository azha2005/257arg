"""Revisa los SVG de commons/<año>/subir/: construcciones que MediaWiki no admite y render con resvg del modo `gan`.

    python commons/chequeo.py 1930 1916      # sin argumentos: todos

Salida: lista de problemas por archivo y PNG de muestra en commons/chequeo/<año>_gan_<variante>.png (sobre blanco).
"""
import io
import os
import re
import sys

import resvg_py
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BAD = [r"<style", r"<use [^>]*href=\"#B\"", r"<image[^>]*data:image/svg", r"var\(", r"calc\(", r"foreignObject", r"<script", r"javascript:", r"\son\w+=",
       r"https?://(?!www\.w3\.org)", r"rgba?\(", r"class=", r"data-", r"font-family"]


def run(year):
    sub = os.path.join(HERE, year, "subir")
    os.makedirs(os.path.join(HERE, "chequeo"), exist_ok=True)
    for f in sorted(os.listdir(sub)):
        if not f.endswith(".svg"):
            continue
        t = open(os.path.join(sub, f), encoding="utf8").read()
        bad = {k: len(re.findall(k, t)) for k in BAD if re.search(k, t)}
        npng = t.count("data:image/png")
        solo = "(solo mapa)" in f
        msg = ("PROBLEMAS " + str(bad)) if bad else "ok"
        print("%s | %.1f MB | texto:%d logosPNG:%d | %s | %s" % (year, os.path.getsize(os.path.join(sub, f)) / 1e6, t.count("<text"), npng, msg, f[len(f) - 60:]))
        if "Resultados por departamento" in f:
            try:
                png = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_path=os.path.join(sub, f), width=1400 if solo else 1920)))).convert("RGBA")
                bg = Image.new("RGBA", png.size, (255, 255, 255, 255)); bg.alpha_composite(png)
                bg.convert("RGB").save(os.path.join(HERE, "chequeo", "%s_gan_%s.png" % (year, "mapa" if solo else "leyenda")))
            except Exception as e:
                print("   ERROR resvg:", e)


if __name__ == "__main__":
    for y in (sys.argv[1:] or sorted(d for d in os.listdir(HERE) if os.path.isdir(os.path.join(HERE, d, "subir")))):
        run(y)
