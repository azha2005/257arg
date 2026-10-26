#!/usr/bin/env python3
"""Controles de la capa Ernesto (base8399/ernesto): consistencia interna y contraste con Lupu-Stokes.

    python control_ernesto.py      ->  ernesto/control_interno.csv, ernesto/control_vs_lupu.csv

control_interno: por unidad, suma de agrupaciones contra `pos` (positivos) y contra `tot` (agrupaciones + blancos + nulos).
control_vs_lupu: total de Ernesto contra `total` de Lupu-Stokes, cargos presidente y diputados. La definición de `total` de
                 Lupu se dedujo contrastando (96-100 % de las unidades): presidente = agrupaciones + blancos + nulos (= columna `tot`);
                 diputados = agrupaciones + blancos (sin nulos). Capital Federal se compara solo por provincia (Lupu trae circuitos).
"""
import csv, os, re, glob, collections, unicodedata
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.join(HERE, "ernesto")
LUPU = os.path.join(HERE, "..", "preparados", "lupu_stokes_1912_2003_exportacion.csv")


def un(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def et_de(cargo, c):
    if cargo == "diputados": return c["agrupacion"] + c["blancos"]
    return c["total"] if c["n_total"] else c["agrupacion"] + c["blancos"] + c["nulos"]


def unidades(path):
    S = collections.OrderedDict()
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        k = (r["provincia"], r["departamento"])
        d = S.setdefault(k, collections.Counter())
        d[r["tipo_fila"]] += float(r["votos"]); d["n_" + r["tipo_fila"]] += 1
    return S


def main():
    L = pd.read_csv(LUPU)
    interno, vslupu = [], []
    for d in sorted(glob.glob(os.path.join(E, "*_*"))):
        if not os.path.isdir(d): continue
        y, cargo = os.path.basename(d).split("_", 1)
        y = int(y)
        S = unidades(os.path.join(d, "dpto_partidos.csv"))
        for (p, dp), c in S.items():
            tot_calc = c["agrupacion"] + c["blancos"] + c["nulos"] + c["impugnados_recurridos"]
            interno.append([y, cargo, p, dp, int(c["agrupacion"]), int(c["positivos"]) if c["n_positivos"] else "", int(c["blancos"]),
                            int(c["nulos"]), int(c["total"]) if c["n_total"] else "", int(c["electores"]) if c["n_electores"] else "",
                            int(c["agrupacion"] - c["positivos"]) if c["n_positivos"] else "",
                            int(tot_calc - c["total"]) if c["n_total"] else ""])
        flag = {"presidente": "pres", "diputados": "dip"}.get(cargo)
        if not flag: continue
        l = L[(L.year == y) & (L[flag] == 1)]
        lk = {}
        for _, r in l.iterrows():
            lk.setdefault((un(r.province), un(r.department)), []).append(float(r.total))
        lprov = l.groupby(l.province.map(un)).total.sum()
        eprov = collections.defaultdict(float)
        for (p, dp), c in S.items():
            et = et_de(cargo, c)
            eprov[p] += et
            if p == "Capital Federal": continue
            v = lk.get((un(p), un(dp)))
            lv = sum(v) if v else None
            vslupu.append([y, cargo, p, dp, int(et), "" if lv is None else int(lv), "" if lv is None else int(et - lv),
                           "sin_fila_lupu" if lv is None else ("igual" if abs(et - lv) <= 0.001 * max(et, 1) + 2 else "difiere")])
        for p, et in eprov.items():
            lv = lprov.get(un(p))
            vslupu.append([y, cargo, p, "(PROVINCIA)", int(et), "" if lv is None else int(lv), "" if lv is None else int(et - lv),
                           "sin_fila_lupu" if lv is None else ("igual" if abs(et - lv) <= 0.001 * max(et, 1) + 2 else "difiere")])
    with open(os.path.join(E, "control_interno.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["anio", "cargo", "provincia", "departamento", "agrupaciones", "positivos", "blancos", "nulos", "total", "electores", "dif_agr_menos_pos", "dif_agr_bla_nul_menos_tot"])
        w.writerows(interno)
    with open(os.path.join(E, "control_vs_lupu.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["anio", "cargo", "provincia", "departamento", "total_ernesto", "total_lupu", "dif", "estado"])
        w.writerows(vslupu)
    c = collections.Counter((r[0], r[1], r[7]) for r in vslupu if r[3] != "(PROVINCIA)")
    for k in sorted(c): print(k, c[k])


if __name__ == "__main__":
    main()
