"""Registra el mapa principal propio sobre el de Wikipedia (afín sx, sy, tx, ty) maximizando el IoU de las máscaras."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import minimize
from common import *

WIKI = {
    1983: "Elecciones_presidenciales_de_Argentina_de_1983_-_Resultados.V1.png",
    1989: "Elecciones_presidenciales_de_Argentina_de_1989_-_Resultados.V1.png",
    1995: "Elecciones_presidenciales_de_Argentina_de_1995_-_Resultados.png",
    1999: "Elecciones_presidenciales_de_Argentina_de_1999_-_Resultados.png",
}
# ventana del mapa principal en px de viewBox (sin recuadros, sin Antártida ni Malvinas); se afina mirando la imagen
REGION = (560, 90, 1420, 1495)


def excl(shape, scale):
    X = np.arange(shape[1])[None, :] / scale; Y = np.arange(shape[0])[:, None] / scale
    return ((X < 670) & (Y < 1000)) | ((X > 1235) & (Y > 780)) | (Y > 1495)


def our_mask(paths, T, scale=0.5):
    """máscara de nuestras unidades aplicando T=(sx,sy,tx,ty) a coords del viewBox -> viewBox de Wikipedia"""
    sx, sy, tx, ty = T
    W, H = int(VBW * scale), int(VBH * scale)
    im = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for g in paths.values():
        if g is None: continue
        for p in (g.geoms if hasattr(g, "geoms") else [g]):
            if p.geom_type != "Polygon": continue
            dr.polygon([((x * sx + tx) * scale, (y * sy + ty) * scale) for x, y in p.exterior.coords], fill=255)
    m = np.asarray(im) > 0
    return m & ~excl(m.shape, scale)


def fit(paths, wmask_full, ds, scale=0.5):
    # wmask a escala
    k = wmask_full.shape[1] / VBW
    im = Image.fromarray((wmask_full * 255).astype("uint8")).resize((int(VBW * scale), int(VBH * scale)), Image.BILINEAR)
    wm = np.asarray(im) > 127
    wm = wm & ~excl(wm.shape, scale)
    # solo mainland+TdF de nuestro mapa: unidades dentro del bbox principal de nuestro mapa (coords > 600..1330, < 1500)
    pm = {i: g for i, g in paths.items() if g is not None and not ds["territories"][i]["p"].startswith("Tierra del Fuego")}
    # bbox iniciales
    ob = unary_union([g for g in pm.values()]).bounds
    ys, xs = np.where(wm)
    wb = (xs.min() / scale, ys.min() / scale, xs.max() / scale, ys.max() / scale)
    sx0 = (wb[2] - wb[0]) / (ob[2] - ob[0]); sy0 = (wb[3] - wb[1]) / (ob[3] - ob[1])
    T0 = [sx0, sy0, wb[0] - ob[0] * sx0, wb[1] - ob[1] * sy0]
    def neg_iou(T):
        om = our_mask(pm, T, scale)
        inter = (om & wm).sum(); uni = (om | wm).sum()
        return -inter / uni
    best = minimize(neg_iou, T0, method="Nelder-Mead", options=dict(xatol=0.05, fatol=1e-5, maxiter=400, initial_simplex=None))
    return best.x, -best.fun, T0, -neg_iou(T0)


if __name__ == "__main__":
    year = int(sys.argv[1]); folder = {1983: "mapa1983", 1989: "mapa1989", 1995: "mapa1995"}[year]
    ds, paths = load_atlas(folder, "atlas_%d.html" % year, "dataset_%d.json" % year)
    img = Image.open("wp/" + WIKI[year])
    wm = wiki_mask(img, REGION)
    Image.fromarray((wm * 255).astype("uint8")).save("scratch_wmask_%d.png" % year)
    T, iou, T0, iou0 = fit(paths, wm, ds)
    print(year, "iou0=%.3f" % iou0, "iou=%.3f" % iou, T)
    json.dump(dict(T=list(map(float, T)), iou=float(iou)), open("reg_%d.json" % year, "w"))
