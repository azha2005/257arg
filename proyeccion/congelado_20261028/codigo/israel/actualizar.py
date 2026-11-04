"""Un paso: baja el conteo de smilganir y regenera la proyeccion y la aguja.
    python -X utf8 proyeccion/israel/actualizar.py
Salida: proyeccion/israel/vivo_<hora>.md y proyeccion/img/aguja_israel_vivo.png."""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
py = [sys.executable, "-X", "utf8"]
subprocess.run(py + [os.path.join(HERE, "smilganir.py")], check=True)
subprocess.run(py + [os.path.join(HERE, "vivo.py"), os.path.join(HERE, "vivo_datos")], check=True)
