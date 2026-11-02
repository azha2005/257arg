"""Construye los 18 atlas y el simulador, conservando los atlas anteriores."""
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parents[2]
for name in ['preparar.py','preparar_atlas.py']:
    subprocess.run([sys.executable,'-X','utf8',str(root/'analisis/escenarios2003'/name)],cwd=root,check=True)
