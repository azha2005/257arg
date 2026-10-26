"""Paleta resumida de un logo (colores dominantes de los píxeles opacos con su peso), para que la leyenda
decida si el logo se confunde con su barra y hay que usar la versión monocroma (como hace la Wikipedia)."""


def paleta(im, n=8):
    im = im.convert("RGBA")
    sm = im.copy(); sm.thumbnail((160, 60))
    px = [p[:3] for p in sm.getdata() if p[3] > 128]
    if not px:
        return []
    from PIL import Image
    q = Image.new("RGB", (len(px), 1)); q.putdata(px)
    q = q.quantize(colors=n)
    pal = q.getpalette()
    out = []
    for cnt, idx in sorted(q.getcolors(), reverse=True):
        r, g, b = pal[idx * 3:idx * 3 + 3]
        out.append(["#%02x%02x%02x" % (r, g, b), round(cnt / len(px), 3)])
    return out


def cobertura(im):
    """Fracción de píxeles opacos dentro del recorte: alta = logo con caja o fondo propio (no se pasa a monocromo)."""
    im = im.convert("RGBA"); bb = im.getbbox()
    if bb: im = im.crop(bb)
    a = im.getchannel("A").getdata()
    return round(sum(1 for v in a if v > 128) / max(1, len(a)), 3)
