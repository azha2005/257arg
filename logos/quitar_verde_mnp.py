"""Quita el halo del fondo verde del PNG usado en el atlas, sin redibujarlo.

El emblema es gris: se recuperan el gris y el alfa de los píxeles mezclados
con el fondo, estimado por fila a partir de sus píxeles ya transparentes.
"""
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
src = HERE / 'Logo_MNP_Rodriguez_Saa_2003.png'
out = HERE / 'Logo_MNP_Rodriguez_Saa_2003_sin_verde.png'
im = Image.open(src).convert('RGBA')
a = np.asarray(im).astype(float)
rgb = a[..., :3]
alpha = a[..., 3] / 255
background = np.empty((im.height, 3))
for y in range(im.height):
    clear = (alpha[y] == 0) & ((rgb[y, :, 1] - rgb[y, :, 0]) > 40)
    background[y] = np.median(rgb[y, clear], axis=0) if clear.any() else [26, 255, 152]

bg = background[:, None, :]
green = np.maximum(0, rgb[..., 1] - rgb[..., 0])
fraction = np.clip(green / (bg[..., 1] - bg[..., 0]), 0, 1)
fraction[green <= 4] = 0
coverage = 1 - fraction
gray = np.divide(rgb[..., 0] - fraction * bg[..., 0], coverage,
                 out=np.zeros_like(coverage), where=coverage > 1e-6)
gray = np.rint(np.clip(gray, 0, 255)).astype('uint8')
result = np.zeros_like(a, dtype='uint8')
result[..., :3] = gray[..., None]
result[..., 3] = np.rint(alpha * coverage * 255).astype('uint8')
result[result[..., 3] == 0, :3] = 0
Image.fromarray(result, 'RGBA').save(out, optimize=True)
print(out, im.size)
