"""Compara los archivos de commons/<año>/subir/ con los de Commons (SHA1) y dice cuales faltan o estan desactualizados.

    python commons/verificar_commons.py 1930
    python commons/verificar_commons.py 1930 1922
    python commons/verificar_commons.py          # todos los que tengan carpeta subir/

IGUAL = subido y coincide; DISTINTO = subido pero con otro contenido (subir una nueva version); NO SUBIDO = no existe en Commons.
"""
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "atlas-electoral-argentina/1.0 (%s)" % os.environ.get("ATLAS_CONTACT", "sin contacto; definir ATLAS_CONTACT")}


def api(**k):
    k["format"] = "json"
    return json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(k), headers=UA), timeout=60))


def check(year):
    sub = os.path.join(HERE, year, "subir")
    files = sorted(f for f in os.listdir(sub) if f.endswith((".svg", ".png")))
    got = {}
    for i in range(0, len(files), 40):
        r = api(action="query", titles="|".join("File:" + f for f in files[i:i + 40]), redirects=1, prop="imageinfo", iiprop="sha1|timestamp")
        for p in r["query"]["pages"].values():
            got[p["title"][5:]] = p
        for alias in r["query"].get("redirects", []):
            target = got.get(alias["to"][5:])
            if target:
                got[alias["from"][5:]] = target
    n = {"IGUAL": 0, "DISTINTO": 0, "NO SUBIDO": 0}
    for f in files:
        loc = hashlib.sha1(open(os.path.join(sub, f), "rb").read()).hexdigest()
        p = got.get(f)
        if not p or "missing" in p:
            st = "NO SUBIDO"
        else:
            st = "IGUAL" if p["imageinfo"][0]["sha1"] == loc else "DISTINTO"
        n[st] += 1
        print("%-10s %s" % (st, f))
    print(year, n)


if __name__ == "__main__":
    ys = sys.argv[1:] or sorted(d for d in os.listdir(HERE) if os.path.isdir(os.path.join(HERE, d, "subir")))
    for y in ys:
        print("=====", y)
        check(y)
