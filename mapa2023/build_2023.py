"""Diputados 2023, constructor compartido derivado de 2009."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(root/'atlas_leg2003_2025.py'),'2023'],check=True,cwd=root)
