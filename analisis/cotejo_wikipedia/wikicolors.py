"""Color dominante que puso Wikipedia en cada una de las 538 unidades de su mapa base (V1 de N2051), por clase de matiz."""
import sys, json, collections
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion
import matplotlib.colors as mc

FILES = {
    1983: "Elecciones_presidenciales_de_Argentina_de_1983_-_Resultados.V1.png",
    1989: "Elecciones_presidenciales_de_Argentina_de_1989_-_Resultados.V1.png",
    1995: "Elecciones_presidenciales_de_Argentina_de_1995_-_Resultados.png",
    1999: "Elecciones_presidenciales_de_Argentina_de_1999_-_Resultados.png",
}


def hue_class(rgb):
    hsv = mc.rgb_to_hsv(rgb / 255.)
    h = hsv[:, 0] * 360; s = hsv[:, 1]; v = hsv[:, 2]
    ok = (s > 0.35) & (v > 0.2)
    c = np.full(len(rgb), "", dtype=object)
    c[ok & ((h < 20) | (h > 340))] = "red"
    c[ok & (h >= 20) & (h < 70)] = "amber"
    c[ok & (h >= 70) & (h < 150)] = "green"
    c[ok & (h >= 150) & (h < 195)] = "teal"
    c[ok & (h >= 195) & (h < 245)] = "blue"
    c[ok & (h >= 245) & (h < 290)] = "purple"
    c[ok & (h >= 290) & (h <= 340)] = "magenta"
    return c


def run(year, dy=2):
    L = np.load("labels_idx.npy").astype(int); L[(L < 0) | (L >= 538)] = -1
    im = Image.open("wp/" + FILES[year]).convert("RGBA")
    A = np.asarray(im)
    k = im.size[0] / 1920.
    Hh, Ww = A.shape[:2]
    # etiqueta por pixel de la imagen de Wikipedia (con el corrimiento medido de +dy px de viewBox)
    ys, xs = np.mgrid[0:Hh, 0:Ww]
    vy = np.clip(np.round(ys / k - dy).astype(int), 0, L.shape[0] - 1); vx = np.clip(np.round(xs / k).astype(int), 0, L.shape[1] - 1)
    LP = L[vy, vx]
    out = {}
    for i in range(538):
        m = LP == i
        if m.sum() < 30: continue
        me = binary_erosion(m, iterations=2)
        if me.sum() < 10: me = m
        px = A[me]
        px = px[px[:, 3] > 200][:, :3].astype(float)
        if len(px) < 5: continue
        cl = hue_class(px)
        cnt = collections.Counter([c for c in cl if c])
        if not cnt: continue
        top, n = cnt.most_common(1)[0]
        out[i] = dict(cls=top, share=round(n / sum(cnt.values()), 2), rgb=[int(v) for v in np.median(px, axis=0)], npx=int(me.sum()))
    return out


if __name__ == "__main__":
    for y in (1983, 1989, 1995, 1999):
        r = run(y)
        json.dump(r, open("wiki_colors_%d.json" % y, "w"))
        print(y, len(r), collections.Counter(v["cls"] for v in r.values()))
