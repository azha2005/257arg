"""Generales y balotajes presidenciales: cuatro cruces, CV y 200 bootstrap por par."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = [(o, d) for o in ("2015p", "2015b") for d in ("2023p", "2023b")]
PAIRS += [(o, d) for o in ("2013", "2009") for d in ("2015p", "2015b")]

if __name__ == "__main__":
    if "--solo-2015-2023" in sys.argv:
        PAIRS = PAIRS[:4]
    for origin, destination in PAIRS:
        print(origin, "->", destination, flush=True)
        with (HERE / f"log_{origin}_{destination}.txt").open("w", encoding="utf8") as log:
            subprocess.run([sys.executable, "-X", "utf8", str(HERE / "estimar.py"), origin, destination],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "sankey.py"), origin, destination], check=True)
        print(origin, "->", destination, "OK", flush=True)
