import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlas_leg8399 import build
build(1999)
