import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
L = np.load("labels_idx.npy").astype(int); L[(L < 0) | (L >= 538)] = -1
COL = {"red": (214, 40, 57), "blue": (36, 99, 200), "teal": (30, 190, 170), "purple": (130, 90, 200), "magenta": (170, 60, 170), "amber": (240, 160, 20), "green": (70, 150, 70)}
GRAY = (200, 200, 200)
def font(sz):
    try: return ImageFont.truetype("arial.ttf", sz)
    except: return ImageFont.load_default()
def panel(colors):
    img = np.full(L.shape + (3,), 255, "uint8")
    for i, c in colors.items():
        img[L == i] = c
    return Image.fromarray(img).crop((560, 100, 1420, 1500))
for y, title in ((1983, "1983"), (1989, "1989"), (1995, "1995")):
    rows = json.load(open("cmp2_%d.json" % y, encoding="utf8"))
    wc = json.load(open("wiki_colors_%d.json" % y))
    ours, wik, diff = {}, {}, {}
    for r in rows:
        b = r["base"]
        oc = r["ours"]
        ours[b] = COL.get(oc, COL["amber"]) if not oc.startswith("otro") else (60, 60, 60)
        wik[b] = COL.get(r["wiki"], GRAY)
        diff[b] = (60, 160, 60) if r["ours"] == r["wiki"] else (230, 30, 30)
    # unidades de la base sin pareja en nuestro atlas: gris claro en los 3
    base_gray = {int(i): GRAY for i in wc if int(i) not in ours}
    panels = [panel({**base_gray, **ours}), panel({**{int(i): COL.get(v["cls"], GRAY) for i, v in wc.items()}}), panel({**base_gray, **diff})]
    W, H = panels[0].size
    out = Image.new("RGB", (W * 3 + 40, H + 70), "white")
    d = ImageDraw.Draw(out)
    names = ["Nuestro atlas (ganador por unidad)", "Mapa de Wikipedia (Commons, V1)", "Coincide (verde) / difiere (rojo)"]
    for k, (p, n) in enumerate(zip(panels, names)):
        out.paste(p, (k * (W + 20), 60)); d.text((k * (W + 20) + 10, 15), n, fill=(30, 30, 30), font=font(30))
    d.text((W * 3 - 480, H + 35), "gris = sin pareja; oscuro = partido provincial (solo nuestro)", fill=(80, 80, 80), font=font(22))
    out.save("informe/panel_%d.png" % y)
    print(y, out.size)
