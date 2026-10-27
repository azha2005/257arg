"""Presidenciales 2015 (PASO por lista, general, balotaje) hacia diputados 2025."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = [('2015p', 2025), ('2015b', 2025), ('2015pp', 2025)]

if __name__ == '__main__':
    for origin, destination in PAIRS:
        if not (HERE / f'circ_{origin}.pkl').exists():
            subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'agregar_circuitos.py'), origin], check=True)
        with (HERE / f'log_{origin}_{destination}.txt').open('w', encoding='utf8') as log:
            subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'estimar.py'), origin, str(destination)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'sankey.py'), origin, str(destination)], check=True)
        subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'sankey.py'), origin, str(destination), '--votantes'], check=True)
        print(origin, '->', destination, 'OK', flush=True)
