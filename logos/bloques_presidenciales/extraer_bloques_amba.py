"""Recortes opacos: no borrar colores del emblema iguales al fondo de la barra.

Son derivados nuevos para la serie AMBA; no sobrescriben los recortes históricos.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'datos/fuentes_leg2003_2025/presidenciales/originales'
OUT = Path(__file__).resolve().parent
for year, name, box in [
    (2015, 'cambiemos_franja_completa', (121, 1789, 290, 1852)),
    (2019, 'sisepuede_franja_completa', (121, 1789, 290, 1852)),
]:
    im = Image.open(SRC / f'Elecciones_presidenciales_de_Argentina_de_{year}_-_Resultados.png').convert('RGBA').crop(box)
    assert im.getextrema()[3] == (255, 255)
    im.save(OUT / (name + '.png'), optimize=True)
    print(name, im.size)
