"""Reparte los votos del 7-sep-2025 de cada local entre los radios censales 2022 del AMBA (metodo de Poblaciones / LN Data),
igual que ../mapaAMBA2025radios/asignar.py (variante «idw», la principal): peso 1/d^2 al centroide de cada radio del mismo partido,
piso de 25 m; los radios que suman menos de 1 voto quedan en 0 y su parte vuelve, en proporcion, a los demas radios del local.
Capital no voto el 7-sep: sus radios no entran. Entrada: mesas_amba.pkl, locales_sep.csv y ../mapaAMBA2025radios/radios_amba2022.geojson.
Salida: asignacion_sep.pkl (fuera de git)."""
import os, re, sys, json, math, collections, unicodedata, pickle
import numpy as np, pandas as pd
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
import cargar
from partidos_sep import bloc_of, slug

DMIN = 25.0
KX = math.cos(math.radians(34.7)) * 111320.0; KY = 110574.0


def nrm(s): return re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode())


d, feats, target = cargar.load("amba")
d["cat"] = np.where(d.votos_tipo == "POSITIVO", [bloc_of(x) or slug(x) if isinstance(x, str) else "x" for x in d.agrupacion_nombre],
                    d.votos_tipo.map({"EN BLANCO": "_BLA", "NULO": "_NUL", "IMPUGNADO": "_IMP", "RECURRIDO": "_IMP", "COMANDO": "_IMP"}))
LAB = {}
for c, n in zip(d.cat, d.agrupacion_nombre):
    if isinstance(n, str) and not c.startswith("_"): LAB.setdefault(c, n)
mes = d.drop_duplicates("mesa")[["mesa", "lk", "sec", "cir", "elec", "estado_final"]].copy()
mes["ok"] = (mes.estado_final == "ESCRUTADO").astype(int)
mes["_ELOK"] = mes.elec * mes.ok
d["lc"] = d.lk + "|" + d.cir
mes["lc"] = mes.lk + "|" + mes.cir
V = d.pivot_table(index="lc", columns="cat", values="v", aggfunc="sum", fill_value=0)
V = V.join(mes.groupby("lc")[["_ELOK", "ok"]].sum().rename(columns={"ok": "_MOK"})).join(mes.groupby("lc").size().rename("_MES")).fillna(0)
CATS = list(V.columns)
VOT = V[[c for c in CATS if c not in ("_ELOK", "_MOK", "_MES")]].sum(1).to_dict()
lcinfo = mes.drop_duplicates("lc").set_index("lc")[["lk", "sec", "cir"]]
part_of = d.drop_duplicates("sec").set_index("sec").seccion_nombre.to_dict()
loc = pd.read_csv(os.path.join(HERE, "locales_sep.csv"), dtype={"sec": str}).set_index("lk")

R = json.load(open(os.path.join(ROOT, "mapas", "mapaAMBA2025radios", "radios_amba2022.geojson"), encoding="utf8"))["features"]
R = [f for f in R if f["properties"]["PROV"] != "02"]   # sin Capital
rg = [shape(f["geometry"]) for f in R]
rp = pd.DataFrame([f["properties"] for f in R])
cen = np.array([[g.centroid.x, g.centroid.y] for g in rg])
rp["pkey"] = [nrm(pa) for pa in rp.partido]
POB = rp.POB_TOT_P.fillna(0).to_numpy(float)
CXY = np.column_stack([cen[:, 0] * KX, cen[:, 1] * KY])


def allocate():
    out = np.zeros((len(rg), len(CATS)))
    groups = collections.defaultdict(list)
    for lc, r in lcinfo.iterrows():
        groups[nrm(part_of[r.sec])].append(lc)
    rad_by_p = rp.groupby("pkey").indices
    assert set(groups) <= set(rad_by_p), set(groups) - set(rad_by_p)
    for pk, lcs in groups.items():
        cand = np.asarray(rad_by_p[pk])
        Wl = []
        for lc in lcs:
            p = loc.loc[lcinfo.at[lc, "lk"]]
            pxy = np.array([p.lon * KX, p.lat * KY])
            dd = np.maximum(np.hypot(*(CXY[cand] - pxy).T), DMIN)
            w = 1 / dd ** 2
            Wl.append((lc, cand, w / w.sum()))
        dead = set()
        for _ in range(20):
            tot = collections.Counter()
            for lc, idx, w in Wl:
                for i, x in zip(idx, w * VOT[lc]): tot[i] += x
            new = {i for i, t in tot.items() if t < 1} - dead
            if not new: break
            dead |= new
            W2 = []
            for lc, idx, w in Wl:
                keep = np.array([i not in dead for i in idx])
                if keep.any(): idx, w = idx[keep], w[keep] / w[keep].sum()
                else: j = np.argmax(w); idx, w = idx[[j]], np.ones(1)
                W2.append((lc, idx, w))
            Wl = W2
        for lc, idx, w in Wl:
            out[idx] += np.outer(w, V.loc[lc].to_numpy(float))
    return out


if __name__ == "__main__":
    A = allocate()
    dv = V.copy(); dv["pk"] = [nrm(part_of[lcinfo.at[i, "sec"]]) for i in V.index]
    err = (pd.DataFrame(A, columns=CATS).groupby(rp.pkey).sum().reindex(dv.groupby("pk")[CATS].sum().index).fillna(0)
           - dv.groupby("pk")[CATS].sum()).abs().to_numpy().max()
    tv = A[:, [i for i, c in enumerate(CATS) if c not in ("_ELOK", "_MOK", "_MES")]].sum(1)
    print("error maximo por partido y categoria:", err, "| radios sin votos:", int((tv < 1e-9).sum()), "de", len(tv),
          "| poblacion en radios sin votos:", int(POB[tv < 1e-9].sum()), file=sys.stderr)
    assert err < 1e-6
    pickle.dump(dict(A=A, CATS=CATS, LAB=LAB, notes={}, radios=rp.drop(columns=["pkey"]), err=err, codes=[f["properties"]["COD_2022"] for f in R]),
                open(os.path.join(HERE, "asignacion_sep.pkl"), "wb"))
