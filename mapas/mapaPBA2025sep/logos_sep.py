# Logos de la leyenda (se ejecuta dentro del constructor, con CAND ya definido).
# Como el atlas AMBA 2025 por radio: Fuerza Patria = Logo_de_Fuerza_Patria.svg (Commons, CC0) con las franjas en blanco y
# La Libertad Avanza = bloque del mapa presidencial de la Wikipedia (CC0), ambos tomados del atlas legislativo 2025.
# Somos Buenos Aires y el FIT-U van con sigla: el logo de Somos en Commons (JPG) no tiene licencia ni fecha verificadas.
def _from_2025(code, white=False, h=50):
    from PIL import Image
    C = json.load(open(os.path.join(ROOT, "mapa2025", "dataset_2025.json"), encoding="utf8"))["candidates"][code]
    im = Image.open(io.BytesIO(base64.b64decode(C["img"].split(",", 1)[1]))).convert("RGBA")
    if white:
        a = np.array(im); a[..., :3] = 255; im = Image.fromarray(a)
    b = io.BytesIO(); im.save(b, "PNG", optimize=True)
    ar = im.width / im.height
    return dict(img="data:image/png;base64," + base64.b64encode(b.getvalue()).decode(), ar=ar, bl=round(min(1.1, 98 / (ar * h)), 3))


CAND["FP"].update(_from_2025("B02", white=True))
CAND["LLA"].update(_from_2025("B01"))
