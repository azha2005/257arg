"""Quita el fondo negro y pone las letras en blanco, conservando la bandera."""
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'logos/Luder_Presidente_usuario.png'
target = ROOT / 'logos/Luder_Presidente_transparente.png'
pixels = np.array(Image.open(source).convert('RGBA'))
original_rgb = pixels[:, :, :3].copy()
# Negro y residuos casi negros del fondo: solo se cambia la transparencia.
background = pixels[:, :, :3].max(axis=2) <= 32
pixels[background, 3] = 0
assert np.array_equal(original_rgb, pixels[:, :, :3])
# En el original de 1280 × 218, la banda y el sol ocupan x=389..534.
# Las letras quedan a ambos lados, separadas de la banda por fondo vacío.
assert pixels.shape[:2] == (218, 1280)
text = np.ones(pixels.shape[:2], dtype=bool)
text[:, 389:535] = False
text &= pixels[:, :, 3] > 0
pixels[text, :3] = 255
assert np.array_equal(original_rgb[:, 389:535], pixels[:, 389:535, :3])
Image.fromarray(pixels).save(target)
print(target)
