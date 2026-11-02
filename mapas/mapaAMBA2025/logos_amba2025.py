# logos recortados del PNG original del usuario (G4eHOGhWYAAJOcT.jpg): FIT y PU en color; fondo quitado
# FP (2-nov-2026, pedido del usuario): el mismo logo que el atlas por radio, Logo_de_Fuerza_Patria.svg (Commons, CC0)
# tomado del atlas legislativo 2025 y con las franjas en blanco, en vez del recorte del PNG original.
def _fp_blanco(h=50):
    import json, numpy as np
    from PIL import Image
    C = json.load(open(os.path.join(ROOT, "mapa2025", "dataset_2025.json"), encoding="utf8"))["candidates"]["B02"]
    im = Image.open(io.BytesIO(base64.b64decode(C["img"].split(",", 1)[1]))).convert("RGBA")
    a = np.array(im); a[..., :3] = 255; im = Image.fromarray(a)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); ar = im.width / im.height
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))
CAND["FP"].update(_fp_blanco())
# LLA (2-nov-2026, pedido del usuario): también como el atlas por radio, el bloque del águila del mapa presidencial
# de la Wikipedia (CC0) tomado del atlas legislativo 2025, con la barra violeta de ese atlas.
def _de_2025(code, h=50):
    import json
    C = json.load(open(os.path.join(ROOT, "mapa2025", "dataset_2025.json"), encoding="utf8"))["candidates"][code]
    from PIL import Image
    ar = Image.open(io.BytesIO(base64.b64decode(C["img"].split(",", 1)[1]))).size
    ar = ar[0] / ar[1]
    return dict(img=C["img"], ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))
CAND["LLA"].update(_de_2025("B01"), bar="#5a3f80", txt="#5a3f80")
CAND["FIT"].update(_logo_raster("AMBA2025_fit_del_png_original.png"))
CAND["PU"].update(_logo_raster("AMBA2025_pu_del_png_original.png"))
