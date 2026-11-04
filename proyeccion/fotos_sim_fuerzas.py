"""% estimado de cada fuerza con colecciones simuladas de ~30 fotos (las mismas de fotos_sim.py y fotos_sim2.py, sin
la banda): para cada origen solo y para el promedio de los dos, con el swing uniforme y con el modelo elegido
(Goodman lam=0,1 + AMBA/resto).
    python proyeccion/fotos_sim_fuerzas.py 2019p 2021bl 2023p
    python proyeccion/fotos_sim_fuerzas.py 2023p 2021bl 2025bl
Salida: proyeccion/fotos_sim/fuerzas_<o1>_<o2>_<destino>.csv (una fila por coleccion, metodo y fuerza) y
fotos_sim/FUERZAS.md (todas las corridas que haya)."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
O1, O2, D = [a for a in sys.argv[1:] if not a.startswith("--")][:3]
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 1000
sys.argv = [sys.argv[0], O1, D, "--circuito"]
import fotos_modelo as fm
import fotos_sim as fs
import backtest as bt

CORTO = {"UNION POR LA PATRIA": "UxP", "LA LIBERTAD AVANZA": "LLA", "JUNTOS POR EL CAMBIO": "JxC",
         "HACEMOS POR NUESTRO PAIS": "Hacemos", "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "FIT",
         "OTRAS LISTAS": "OTRAS"}
ESQUEMAS = {"azar": "al azar", "como25": "como las fotos de 2025", "twitter": "twitter (65 % AMBA, racimos)"}


def main():
    fs.bloques_destino(D)
    st, info, dcols = bt.state()
    e, dist = st["e"], st["dist"]
    st["amba"] = fm.region(st["distrito_id"], st["seccion_id"], "amba") == "AMBA"
    key = pd.DataFrame({"distrito_id": st["distrito_id"], "seccion_id": st["seccion_id"], "circuito": st["circuito"]})
    o2 = bt.load_circ(O2, 0.01)
    ocol2 = [c for c in o2.columns if c.endswith("(orig)")]
    X2 = key.merge(o2, on=["distrito_id", "seccion_id", "circuito"], how="left")[ocol2].to_numpy(float)
    has2 = ~np.isnan(X2).any(1)
    nd = dist.max() + 1
    natd1 = np.zeros((nd, st["X"].shape[1]))
    np.add.at(natd1, dist, st["X"] * e[:, None])
    natd2 = np.zeros((nd, X2.shape[1]))
    np.add.at(natd2, dist[has2], X2[has2] * e[has2, None])
    ed = np.bincount(dist, weights=e)
    natd2 *= (ed / np.maximum(np.bincount(dist[has2], weights=e[has2], minlength=nd), 1))[:, None]
    oc1 = [c.replace(" (orig)", "") for c in st["ocols"]]
    oc2 = [c.replace(" (orig)", "") for c in ocol2]
    src1 = [[oc1.index(o) for o in fs.SRC.get((O1, D), {}).get(c, [c]) if o in oc1] for c in dcols]
    src2 = [[oc2.index(o) for o in fs.SRC.get((O2, D), {}).get(c, [c]) if o in oc2] for c in dcols]
    strat = fm.region(st["distrito_id"], st["seccion_id"], "amba")
    share = pd.Series(e).groupby(strat).sum().pipe(lambda x: x / x.sum()).to_dict()
    pos = st["pos"]
    names = [CORTO.get(dcols[p], dcols[p]) for p in pos]
    real = fm.pct(st["Vd"].sum(0), pos)
    rng = np.random.default_rng(11)
    rows = [dict(esquema="real", rep=0, metodo="real", fuerza=f, pct=v) for f, v in zip(names, real)]
    for scheme in ESQUEMAS:
        for rep in range(REPS):
            idx, _ = fs.colecciones(st, rng, scheme, 30)
            idx = idx[has2[idx]]
            X1i, X2i, Yi, di = st["X"][idx], X2[idx], st["Y"][idx], dist[idx]
            w = fm.poststrat(e[idx], strat[idx], share)
            sw = ("swing", np.inf)
            gm = ("goodman", 0.1)
            p = {"swing %s" % O1: fm.pct(fm.project(sw, X1i, Yi, e[idx], di, natd1, ed, src1), pos),
                 "swing %s" % O2: fm.pct(fm.project(sw, X2i, Yi, e[idx], di, natd2, ed, src2), pos),
                 "elegido %s" % O1: fm.pct(fm.project(gm, X1i, Yi, w, di, natd1, ed, src1), pos),
                 "elegido %s" % O2: fm.pct(fm.project(gm, X2i, Yi, w, di, natd2, ed, src2), pos)}
            p["elegido promedio"] = (p["elegido %s" % O1] + p["elegido %s" % O2]) / 2
            for m, v in p.items():
                rows += [dict(esquema=scheme, rep=rep, metodo=m, fuerza=f, pct=x) for f, x in zip(names, v)]
        print(scheme, flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(fs.OUT, "fuerzas_%s_%s_%s.csv" % (O1, O2, D)), index=False)
    report()


def report():
    L = ["# Fotos de actas: % estimado de cada fuerza con ~30 fotos", "",
         "Generado por `proyeccion/fotos_sim_fuerzas.py`. 1.000 colecciones simuladas de 25 a 35 mesas por esquema; "
         "% sobre votos positivos. Cada celda: **promedio de las 1.000 proyecciones** y, entre paréntesis, el rango "
         "donde cae el 90 % de ellas (percentiles 5 y 95). «elegido» = Goodman λ = 0,1 + AMBA/resto; «promedio» = "
         "el elegido con los dos orígenes promediados (lo que hace `proyectar_fotos.py`).", ""]
    for f in sorted(os.listdir(fs.OUT)):
        if not f.startswith("fuerzas_"):
            continue
        df = pd.read_csv(os.path.join(fs.OUT, f))
        o1, o2, d = f[8:-4].split("_")
        real = df[df.esquema == "real"].set_index("fuerza").pct
        order = list(real.sort_values(ascending=False).index)
        L += ["## %s y %s → %s" % (o1, o2, d), ""]
        for scheme, lab in ESQUEMAS.items():
            s = df[df.esquema == scheme]
            if not len(s):
                continue
            g = s.groupby(["metodo", "fuerza"]).pct
            mean, lo, hi = g.mean(), g.quantile(.05), g.quantile(.95)
            L += ["**%s**" % lab.capitalize(), "", "| Método | " + " | ".join(order) + " |",
                  "|---|" + "---:|" * len(order), "| **real** | " + " | ".join("**%.1f**" % real[x] for x in order) + " |"]
            for m in s.metodo.unique():
                L.append("| %s | " % m + " | ".join("%.1f (%.1f–%.1f)" % (mean[m, x], lo[m, x], hi[m, x])
                                                     for x in order) + " |")
            L.append("")
    open(os.path.join(fs.OUT, "FUERZAS.md"), "w", encoding="utf-8").write("\n".join(L))
    print("->", os.path.join(fs.OUT, "FUERZAS.md"))


if __name__ == "__main__":
    main()
