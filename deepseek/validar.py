#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controles de cierre del atlas ucrónico de 1987.

    python deepseek/validar.py

Lee el xlsx y el dataset generado, y comprueba los totales que el build ya asegura:
provincias, partidos, electores, unidades ganadas y la torta. No escribe archivos.
"""
import json
import os
import sys
import collections
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "Argentina 1987.xlsx")
DATA = os.path.join(HERE, "dataset_1987_ucronia.json")
HTML = os.path.join(HERE, "atlas_1987_ucronia.html")
PARTIES = ["PJ", "UCR", "MON", "PDS", "PI", "MID", "OTROS"]


def leer_xlsx():
    ws = openpyxl.load_workbook(XLSX, data_only=True)["1987"]
    out = {}
    for row in ws.iter_rows(min_row=3, max_row=26, values_only=True):
        if not row[0]:
            continue
        prov = str(row[0]).strip()
        prov = {"Neuquen": "Neuquén", "Rio Negro": "Río Negro"}.get(prov, prov)
        votes = {p: int(row[i]) for p, i in zip(PARTIES, (1, 4, 7, 10, 13, 16, 19))}
        elect = {p: int(row[i]) for p, i in zip(PARTIES, (3, 6, 9, 12, 15, 18, 21))}
        total = int(row[22])
        assert sum(votes.values()) == total, (prov, votes, total)
        out[prov] = dict(votes=votes, elect=elect, total=total)
    return out


def main():
    x = leer_xlsx()
    d = json.load(open(DATA, encoding="utf8"))
    assert len(x) == 24, len(x)
    assert sum(v["total"] for v in x.values()) == 17_068_061
    assert sum(sum(v["elect"].values()) for v in x.values()) == 600

    modes = {m["id"]: m for m in d["modes"]}
    assert list(modes) == ["gan", "mon", "ucr", "pj", "pds"], list(modes)
    m = modes["gan"]
    assert len(m["units"]) == len(d["territories"]) == 526

    # unidades: sumas por provincia y por fuerza
    by_prov = collections.defaultdict(lambda: collections.Counter())
    wins = collections.Counter()
    sin_dato = 0
    for t, u in zip(d["territories"], m["units"]):
        if not u.get("lines"):
            sin_dato += 1
            continue
        if u.get("w"):
            wins[u["w"]] += 1
        for code, v, _ in u["lines"]:
            by_prov[t["p"]][code[2:]] += v
    assert wins == {"MON": 214, "UCR": 179, "PJ": 133}, wins
    assert sin_dato == 0, sin_dato

    malv = [u for t, u in zip(d["territories"], m["units"]) if t["n"] == "Islas Malvinas"]
    assert len(malv) == 1 and malv[0]["w"] == "MON", malv
    assert sum(v for _, v, _ in malv[0]["lines"]) == 656, malv

    for p, votes in x.items():
        got = by_prov[p]
        assert sum(got.values()) == votes["total"], (p, sum(got.values()), votes["total"])
        for b in PARTIES:
            assert got[b] == votes["votes"][b], (p, b, got[b], votes["votes"][b])

    # nacional
    nat = {c["code"]: c["votes"] for c in m["national"]["cands"]}
    assert nat == {"MON": 5_391_282, "UCR": 5_369_706, "PJ": 4_940_601}, nat
    assert [s.get("v") for s in m["national"]["slices"]] == [5_391_282, 5_369_706, 4_940_601, 1_366_472]
    assert any("ninguna fuerza" in (n or "") for n in [m.get("note")])

    # provincias ganadas
    pw = collections.Counter(v["w"] for v in m["prov"].values() if v.get("w"))
    assert pw == {"MON": 13, "UCR": 5, "PJ": 6}, pw

    # logo de MON embebido
    html = open(HTML, encoding="utf8").read()
    assert '"MON":{"n":"Movimiento de Opinión Nacional"' in html
    assert html.count("data:image/png;base64,") >= 5

    print("OK: 24 provincias, 526 unidades, 17.068.061 positivos, 600 electores")
    print("    ganadores por unidad:", dict(wins))
    print("    ganadores por provincia:", dict(pw))
    print("    torta: MON/UCR/PJ + Otros 1.366.472")
    print("    sin dato:", sin_dato)
    print("    Malvinas: 656 votos estimados, gana MON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
