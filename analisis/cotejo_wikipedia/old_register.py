"""Registra la etiqueta base (viewBox 1920x1649) sobre la versión vieja (AndyCat2453, 2025) y muestrea colores por unidad."""
import sys, json, collections
import numpy as np
from PIL import Image
from scipy.optimize import minimize
from scipy.ndimage import binary_erosion
import matplotlib.colors as mc
from wikicolors import hue_class

OLD = {1983: "Elecciones_presidenciales_de_Argentina_de_1983_-_Resultados.png",
       1989: "Elecciones_presidenciales_de_Argentina_de_1989_-_Resultados.png"}
L = np.load("labels_idx.npy").astype(int); L[(L < 0) | (L >= 538)] = -1
H, W = L.shape
X = np.arange(W)[None, :]; Y = np.arange(H)[:, None]
excl = ((X < 670) & (Y < 1000)) | ((X > 1235) & (Y > 780)) | (Y > 1495) | (Y < 100) | (X < 560) | (X > 1420)
lm = (L >= 0) & ~excl


def sat_mask(im):
    a = np.asarray(im.convert("RGB")).astype(float) / 255
    hsv = mc.rgb_to_hsv(a)
    return (hsv[:, :, 1] > 0.3) & (hsv[:, :, 2] > 0.2)


def fit(img_mask, region_guess):
    # img_mask en px de imagen; buscamos (s, tx, ty) que llevan coords viewBox -> px imagen
    ys, xs = np.where(img_mask)
    # grilla gruesa sobre bbox
    sub = lm[::2, ::2]
    pts = np.argwhere(sub) * 2  # (y,x) en viewBox
    def score(p):
        s, tx, ty = p
        px = (pts[:, 1] * s + tx).astype(int); py = (pts[:, 0] * s + ty).astype(int)
        ok = (px >= 0) & (px < img_mask.shape[1]) & (py >= 0) & (py < img_mask.shape[0])
        return -(img_mask[py[ok], px[ok]].mean() * ok.mean())
    best = None
    for s in np.arange(0.9, 1.5, 0.02):
        for tx in range(-400, 400, 20):
            for ty in range(-100, 400, 20):
                v = score((s, tx, ty))
                if best is None or v < best[0]: best = (v, s, tx, ty)
    r = minimize(score, [best[1], best[2], best[3]], method="Nelder-Mead", options=dict(xatol=0.05, fatol=1e-6))
    return r.x, -r.fun


if __name__ == "__main__":
    for y, f in OLD.items():
        im = Image.open("wp/" + f)
        m = sat_mask(im)
        p, sc = fit(m, None)
        print(y, im.size, "s,tx,ty", p, "score", sc)
        json.dump(list(map(float, p)), open("oldreg_%d.json" % y, "w"))
