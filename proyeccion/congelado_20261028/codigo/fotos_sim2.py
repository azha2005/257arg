"""¿Conviene proyectar las fotos con dos elecciones de origen y promediar? (como el Estadão, que compara con la
eleccion anterior y con la 1.a vuelta). Mismas colecciones que fotos_sim.py, modelo Goodman lam=0,1 + AMBA/resto.
    python proyeccion/fotos_sim2.py 2019p 2021bl 2023p        # presidente 2019 y diputados 2021 -> presidente 2023
Salida: proyeccion/fotos_sim/dos_origenes_<o1>_<o2>_<destino>.csv y una tabla en pantalla."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
O1, O2, D = [a for a in sys.argv[1:] if not a.startswith("--")][:3]
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 600
sys.argv = [sys.argv[0], O1, D, "--circuito"]
import fotos_modelo as fm
import fotos_sim as fs
import backtest as bt


def main():
    fs.bloques_destino(D)
    st, info, dcols = bt.state()                     # destino con el origen O1
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
    real = fm.pct(st["Vd"].sum(0), pos)
    top = np.argsort(-real)[:2]
    rm = real[top[0]] - real[top[1]]
    rng = np.random.default_rng(7)
    rows = []
    for scheme, n in [("azar", 30), ("como25", 30), ("twitter", 30), ("estrat", 50), ("twitter", 50)]:
        for rep in range(REPS):
            idx, _ = fs.colecciones(st, rng, scheme, n)
            idx = idx[has2[idx]]
            w = fm.poststrat(e[idx], strat[idx], share)
            spec = ("goodman", 0.1)
            p1 = fm.pct(fm.project(spec, st["X"][idx], st["Y"][idx], w, dist[idx], natd1, ed, src1), pos)
            p2 = fm.pct(fm.project(spec, X2[idx], st["Y"][idx], w, dist[idx], natd2, ed, src2), pos)
            for name, p in ((O1, p1), (O2, p2), ("promedio", (p1 + p2) / 2)):
                rows.append(dict(esquema=scheme, n=n, rep=rep, origen=name, err=(p[top[0]] - p[top[1]]) - rm))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(fs.OUT, "dos_origenes_%s_%s_%s.csv" % (O1, O2, D)), index=False)
    df["abs"] = df.err.abs()
    print(df.pivot_table(index="origen", columns=["esquema", "n"], values="abs").round(2).to_string())
    print(df.pivot_table(index="origen", columns=["esquema", "n"], values="err").round(2).to_string())


if __name__ == "__main__":
    main()
