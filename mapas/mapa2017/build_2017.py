"""Diputados 2017, constructor compartido derivado de 2009."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(root/'../comun/atlas_leg2003_2025.py'),'2017'],check=True,cwd=root)
