"""Presidente 2015: constructor vigente de los atlas nacionales."""
from pathlib import Path
import subprocess, sys
root = Path(__file__).resolve().parents[2]
subprocess.run([sys.executable, str(root/'comun/atlas_leg2003_2025.py'), '2015pres'], check=True, cwd=root)
