"""Atlas histórico 1918: dibujo de la serie publicada 1922/1928."""
import runpy,sys
from pathlib import Path
p=Path(__file__).resolve().parents[2]/"transcripciones/entreguerras/construir.py"
sys.path.insert(0,str(p.parent));sys.argv=[str(p),"1918"];runpy.run_path(str(p),run_name="__main__")
