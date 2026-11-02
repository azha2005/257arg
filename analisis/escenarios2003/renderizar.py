"""Renderizadores oficiales del proyecto, limitados a los 18 atlas nuevos."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FOLDER='mapa2003escenarios'
manifest=json.loads((ROOT/'mapas'/FOLDER/'manifiesto.json').read_text(encoding='utf8'))
commands=[[sys.executable,'-X','utf8',str(ROOT/'comun/render_transparentes.py'),FOLDER]]
commands.extend([sys.executable,'-X','utf8',str(ROOT/'comun/render_blanco.py'),FOLDER,m['html']] for m in manifest)
with (HERE/'render.log').open('w',encoding='utf8') as log:
    for i,command in enumerate(commands,1):
        print(f'Render {i}/{len(commands)}: {command[-1]}',flush=True)
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
destination=ROOT/'png_transparentes/all elections white bg'
destination.mkdir(exist_ok=True)
for p in (ROOT/'png_blanco'/FOLDER).glob('*.png'):shutil.copy2(p,destination/p.name)
print('PNG transparentes y blancos terminados; copiados a all elections white bg.',flush=True)
