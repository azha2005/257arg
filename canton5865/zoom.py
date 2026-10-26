"""Recorta filas de una página escaneada de Cantón para cotejar a ojo.
uso: python zoom.py <pdf> <unidad>[,<unidad>...]  -> $ZOUT/zz_<pdf>.png
Las filas están a paso de máquina de escribir (~33,5 px); se recorta una ventana de
unas tres filas alrededor de la estimada, con el encabezado de columnas arriba."""
import sys, json, os
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('ZOUT', '.')

def first_row(a):
    d = (a[:, 60:300] < 140).sum(1) > 1
    # salta el encabezado: busca la primera línea con texto tras una franja vacía de >20 px por debajo de y=150
    y = 150; empty = 0
    while y < 400:
        if d[y]:
            if empty > 20: return y
            empty = 0
        else: empty += 1
        y += 1
    return 210

if __name__ == '__main__':
    pdf = int(sys.argv[1]); names = sys.argv[2].split(',')
    pitch = float(sys.argv[3]) if len(sys.argv) > 3 else 33.5
    p = json.load(open(f'{ROOT}/scratch/transcripcion/p_{pdf}.json', encoding='utf-8'))
    im = Image.open(f'{ROOT}/scratch/canton_pages/p_{pdf}.png'); a = np.asarray(im.convert('L'), float)
    y0 = first_row(a)
    crops = [im.crop((0, 100, im.size[0], y0 - 5))]
    for nm in names:
        i = [r['departamento'] for r in p['filas']].index(nm)
        yc = y0 + 5 + i * pitch
        crops.append(im.crop((0, int(yc - 45), im.size[0], int(yc + 50))))
        print(i, nm, p['filas'][i]['valores'])
    H = sum(c.size[1] for c in crops) + 6 * len(crops)
    out = Image.new('RGB', (im.size[0], H), 'red'); y = 0
    for c in crops: out.paste(c, (0, y)); y += c.size[1] + 6
    out.resize((int(out.size[0] * 1.4), int(H * 1.4))).save(os.path.join(OUT, f'zz_{pdf}.png'))
