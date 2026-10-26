#!/usr/bin/env python3
"""Empareja las filas de un CSV propio (provincia + departamento) con el indice de territorios del mapa base.

    python3 match_territories.py datos.csv [--prov-col provincia] [--name-col departamento] [--out indice.json]

Imprime cuantas filas se emparejaron y lista las que no, junto con los territorios del mapa que quedaron sin dato.
Escribe un JSON {"<fila>": indice}. Con ese indice se arma `units` del dataset (una entrada por territorio, en el orden
de territories.json). La comparacion ignora acentos, mayusculas y signos, y prueba variantes frecuentes
("Cnel." / "Coronel", "Gral." / "General", "Gran Buenos Aires" en partidos, comunas de CABA, etc.).

Los 538 territorios son: departamentos / partidos y, en la Ciudad de Buenos Aires, circunscripciones (kind != "departamento").
"""
import argparse, csv, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
TERR = os.path.join(HERE, "..", "assets", "territories.json")

ALIAS = [(r"\bcnel\b", "coronel"), (r"\bgral\b", "general"), (r"\bsta\b", "santa"), (r"\bsto\b", "santo"),
         (r"\bpte\b", "presidente"), (r"\bdr\b", "doctor"), (r"\bcap\b", "capital"), (r"\bj\b", "juan"),
         (r"\bdepartamento\b", ""), (r"\bpartido de\b", ""), (r"\bpartido\b", "")]
PROV_ALIAS = {"ciudad autonoma de buenos aires": "capital federal", "caba": "capital federal", "ciudad de buenos aires": "capital federal",
              "pcia de buenos aires": "buenos aires", "provincia de buenos aires": "buenos aires",
              "tierra del fuego antartida e islas del atlantico sur": "tierra del fuego"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    for a, b in ALIAS:
        s = re.sub(a, b, s)
    return re.sub(r"\s+", " ", s).strip()


def nprov(s):
    n = norm(s)
    return PROV_ALIAS.get(n, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--prov-col", default="provincia")
    ap.add_argument("--name-col", default="departamento")
    ap.add_argument("--out", default=None)
    ap.add_argument("--encoding", default="utf-8-sig")
    ap.add_argument("--delimiter", default=",")
    a = ap.parse_args()

    units = json.load(open(TERR, encoding="utf8"))["units"]
    key = {}
    for u in units:
        key.setdefault((nprov(u["prov"]), norm(u["name"])), u["i"])
    rows = list(csv.DictReader(open(a.csv, encoding=a.encoding), delimiter=a.delimiter))
    found, miss = {}, []
    for n, r in enumerate(rows):
        k = (nprov(r[a.prov_col]), norm(r[a.name_col]))
        if k in key:
            found[n] = key[k]
        else:
            miss.append((n, r[a.prov_col], r[a.name_col]))
    used = set(found.values())
    dup = len(found) - len(used)
    print("filas: %d  emparejadas: %d  sin pareja: %d  duplicadas: %d" % (len(rows), len(found), len(miss), dup))
    for n, p, d in miss[:40]:
        print("  sin pareja  fila %d: %s / %s" % (n, p, d))
    sin = [u for u in units if u["i"] not in used]
    print("territorios del mapa sin dato: %d" % len(sin))
    for u in sin[:40]:
        print("  falta  [%d] %s / %s (%s)" % (u["i"], u["prov"], u["name"], u["kind"]))
    if a.out:
        json.dump(found, open(a.out, "w", encoding="utf8"))
        print("indice escrito en", a.out)


if __name__ == "__main__":
    main()
