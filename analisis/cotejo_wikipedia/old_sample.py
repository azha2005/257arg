import json, collections, numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion
from wikicolors import hue_class
from old_register import OLD, L
out_all = {}
for y, f in OLD.items():
    s, tx, ty = json.load(open("oldreg_%d.json" % y))
    im = Image.open("wp/" + f).convert("RGB"); A = np.asarray(im)
    out = {}
    H, W = L.shape
    for i in range(538):
        m = (L == i)
        if m.sum() < 30: continue
        me = binary_erosion(m, iterations=2)
        if me.sum() < 8: me = m
        ys, xs = np.nonzero(me)
        px = (xs * s + tx).astype(int); py = (ys * s + ty).astype(int)
        ok = (px >= 0) & (px < A.shape[1]) & (py >= 0) & (py < A.shape[0])
        rgb = A[py[ok], px[ok]].astype(float)
        cl = hue_class(rgb)
        cnt = collections.Counter([c for c in cl if c])
        if not cnt: continue
        top, n = cnt.most_common(1)[0]
        out[i] = dict(cls=top, share=round(n / sum(cnt.values()), 2), rgb=[int(v) for v in np.median(rgb, axis=0)])
    json.dump(out, open("wiki_colors_old_%d.json" % y, "w"))
    print(y, len(out), collections.Counter(v["cls"] for v in out.values()))
