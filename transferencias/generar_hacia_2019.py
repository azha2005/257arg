"""Cuatro cruces hacia 2019, con CV y bootstrap completo del estimador."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = [(2017, "2019p"), (2017, 2019), ("2015p", "2019p"), ("2015b", "2019p")]

if __name__ == "__main__":
    for origin, destination in PAIRS:
        print(origin, "->", destination, flush=True)
        with (HERE / f"log_{origin}_{destination}.txt").open("w", encoding="utf8") as log:
            subprocess.run([sys.executable, "-X", "utf8", str(HERE / "estimar.py"), str(origin), str(destination)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "sankey.py"), str(origin), str(destination)], check=True)
        print(origin, "->", destination, "OK", flush=True)
