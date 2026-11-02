"""Franja JxC completa, sin volver transparente el amarillo del propio emblema."""
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'datos/fuentes_leg2003_2025/presidenciales/originales/Elecciones_presidenciales_de_Argentina_de_2023_-_Resultados.png'
out=Path(__file__).resolve().parent/'jxc23_franja_completa.png'
im=Image.open(src).convert('RGBA').crop((121,1881,292,1943))
assert im.getextrema()[3]==(255,255)
im.save(out,optimize=True)
print(out,im.size)
