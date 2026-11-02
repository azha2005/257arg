"""Construye y verifica todos los atlas o una selección.

python mapas/serieAMBA2005_2023radios/construir.py
python mapas/serieAMBA2005_2023radios/construir.py 2023pres --sin-preparar
"""
import argparse,subprocess,sys,time
from pathlib import Path
from serie import KEYS,HERE

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('elecciones',nargs='*',metavar='ELECCION',help=', '.join(KEYS))
p.add_argument('--sin-preparar',action='store_true',help='Reutilizar las asignaciones existentes')
p.add_argument('--sin-png',action='store_true',help='Omitir las capturas de navegador')
args=p.parse_args()
if any(k not in KEYS for k in args.elecciones):p.error('Elección desconocida')
keys=args.elecciones or KEYS
def run(file,*values):
    # Windows a veces bloquea un momento los HTML grandes recién escritos (Errno 22): se reintenta.
    for intento in range(3):
        if subprocess.run([sys.executable,str(HERE/file),*values]).returncode==0:return
        time.sleep(20)
    raise SystemExit(f'falló {file} {" ".join(values)}')
if not args.sin_preparar:run('serie.py',*keys)
for key in keys:run('render.py',key)
if '2023pasocand' in keys:run('internas2023.py')
run('indice.py')
if not args.sin_png:run('verificar.py',*keys)
if not args.sin_png and '2023pasocand' in keys:run('verificar_internas2023.py')
