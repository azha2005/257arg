"""Por unidad: ganador de nuestro atlas vs color dominante del mapa de Wikipedia (muestreado dentro del polígono, registrado)."""
import sys, json, csv, collections
import numpy as np
import matplotlib.colors as mc
from PIL import Image, ImageDraw
from common import *
from register import WIKI

CFG = {
    1983: dict(folder="mapa1983", cls={"red": ["ucr"], "blue": ["pj"], "teal": ["pal"]}, name={"red": "UCR", "blue": "PJ", "teal": "PAL"}),
    1989: dict(folder="mapa1989", cls={"blue": ["frejupo", "fcr", "ptp", "mid"], "red": ["ucr", "ucrfi", "ucrmc", "cfi", "cfifed", "fed"],
                                       "purple": ["adc", "paldpml", "ucd", "pdp", "adcucd"]}, name={"blue": "MEN", "red": "ANG", "purple": "ALS"}),
    1995: dict(folder="mapa1995", cls={"blue": None, "magenta": None, "red": None}, name={"blue": "MEN", "magenta": "BOR", "red": "MAS"}),
}
W2CLS = {"MEN": "blue", "ANG": "red", "ALS": "purple", "BOR": "magenta", "MAS": "red", "UCR": "red", "PJ": "blue", "PAL": "teal"}


def hue_class(rgb):
    hsv = mc.rgb_to_hsv(rgb / 255.)
    h = hsv[:, 0] * 360; s = hsv[:, 1]; v = hsv[:, 2]
    ok = (s > 0.35) & (v > 0.2)
    c = np.full(len(rgb), "", dtype=object)
    c[ok & ((h < 20) | (h > 340))] = "red"
    c[ok & (h >= 150) & (h < 195)] = "teal"
    c[ok & (h >= 195) & (h < 245)] = "blue"
    c[ok & (h >= 245) & (h < 290)] = "purple"
    c[ok & (h >= 290) & (h <= 340)] = "magenta"
    c[ok & (h >= 20) & (h < 70)] = "amber"
    c[ok & (h >= 70) & (h < 150)] = "green"
    return c


def run(year):
    cfg = CFG[year]
    ds, paths = load_atlas(cfg["folder"], "atlas_%d.html" % year, "dataset_%d.json" % year)
    T = json.load(open("reg_%d.json" % year))["T"]
    img = Image.open("wp/" + WIKI[year]).convert("RGBA")
    A = np.asarray(img)
    k = img.size[0] / VBW
    sx, sy, tx, ty = T
    units = ds["modes"][0]["units"]
    terr = ds["territories"]
    rows = []
    for i, g in paths.items():
        if g is None: continue
        prov = terr[i]["p"]
        if prov.startswith("Tierra del Fuego") or prov == "Capital Federal": continue
        # polígono transformado a px de la imagen de Wikipedia, erosionado ~1.2 px
        pts = lambda ring: [((x * sx + tx) * k, (y * sy + ty) * k) for x, y in ring]
        polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
        xs = [p[0] for pol in polys for p in pts(pol.exterior.coords)]
        ys = [p[1] for pol in polys for p in pts(pol.exterior.coords)]
        x0, x1, y0, y1 = int(min(xs)) - 2, int(max(xs)) + 3, int(min(ys)) - 2, int(max(ys)) + 3
        if x1 - x0 < 3 or y1 - y0 < 3: continue
        mk = Image.new("L", (x1 - x0, y1 - y0), 0); dr = ImageDraw.Draw(mk)
        for pol in polys:
            dr.polygon([(a - x0, b - y0) for a, b in pts(pol.exterior.coords)], fill=255)
            for h in pol.interiors:
                dr.polygon([(a - x0, b - y0) for a, b in pts(h.coords)], fill=0)
        m = np.asarray(mk) > 0
        # erosionar: quitar píxeles de borde (donde hay trazo blanco/otra unidad)
        from scipy.ndimage import binary_erosion
        me = binary_erosion(m, iterations=3)
        if me.sum() < 8: me = binary_erosion(m, iterations=1)
        if me.sum() < 4: continue
        sub = A[y0:y1, x0:x1][me]
        sub = sub[sub[:, 3] > 200][:, :3]
        if len(sub) < 4: continue
        cl = hue_class(sub.astype(float))
        cnt = collections.Counter([c for c in cl if c])
        if not cnt: continue
        top, n = cnt.most_common(1)[0]
        share = n / sum(cnt.values())
        # nuestro
        u = units[i]
        w = u.get("w"); q = u.get("q")
        lines = u["lines"]
        # votos por bloque de la wiki (para el ganador entre los candidatos de la leyenda de Wikipedia)
        rows.append(dict(i=i, prov=prov, name=terr[i]["n"], wiki=top, wshare=round(share, 2), npx=int(me.sum()), ours_w=w, ours_q=q,
                         area=g.area, lines=lines))
    return ds, rows


if __name__ == "__main__":
    year = int(sys.argv[1])
    ds, rows = run(year)
    cfg = CFG[year]
    agree = dis = 0
    out = []
    for r in rows:
        oc = W2CLS.get(r["ours_w"], "other:" + str(r["ours_w"]))
        r["ours_cls"] = oc
        r["ok"] = (oc == r["wiki"])
    n = len(rows); ok = sum(r["ok"] for r in rows)
    print(year, "unidades muestreadas", n, "coinciden", ok, "(%.1f%%)" % (100. * ok / n))
    # matriz de confusión
    cm = collections.Counter((r["ours_cls"], r["wiki"]) for r in rows)
    for (a, b), v in sorted(cm.items(), key=lambda x: -x[1]): print("  nuestro %-14s wiki %-8s %d" % (a, b, v))
    json.dump(rows, open("cmp_%d.json" % year, "w"), ensure_ascii=False)
