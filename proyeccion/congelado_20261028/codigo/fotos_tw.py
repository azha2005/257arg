"""El mejor modelo para ~30 actas juntadas en Twitter (28-oct-2026). Colecciones simuladas de fotos_sim.py
(«como25»: 25-35 actas, 2/3 del AMBA, un racimo de 10 y dos de 3; «twitter»: racimos de 3, 65 % del AMBA, n = 30) y
variantes del modelo de fotos_modelo.py:
  actual       Goodman encogido al swing uniforme (lam = 0,1), actas repesadas AMBA / resto
  lam          el mismo con otro lam
  racimo a     ademas, el peso de cada acta dividido por (actas de su circuito)^a: un tuit con 10 mesas del mismo
               local no pesa como 10 tuits
  3 estratos   repesado AMBA / interior de Buenos Aires / resto
  huber        Goodman robusto (pesos de Huber, c = 1,5 desvios), por si una foto esta mal leida o es atipica
    python -X utf8 proyeccion/fotos_tw.py 2023p 2025bl --circuito [--reps 1000]
Salida: proyeccion/fotos_sim/tw_<origen>_<destino>.csv y una tabla en pantalla."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fotos_modelo as fm
import fotos_sim as fs

REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 1000
VARIANTES = [("actual", 0.1, "amba", 0, False), ("lam 0,03", 0.03, "amba", 0, False), ("lam 0,3", 0.3, "amba", 0, False),
             ("racimo 0,5", 0.1, "amba", 0.5, False), ("racimo 1", 0.1, "amba", 1, False),
             ("3 estratos", 0.1, "tres", 0, False), ("3 estratos + racimo 0,5", 0.1, "tres", 0.5, False),
             ("huber", 0.1, "amba", 0, True), ("huber + racimo 0,5", 0.1, "amba", 0.5, True)]


def goodman_huber(X, Y, e, nat, src, lam, c=1.5, iters=8):
    """fm.goodman con pesos de Huber sobre los residuos de cada columna (escala: MAD ponderada)."""
    tot = np.zeros(Y.shape[1])
    for j in range(Y.shape[1]):
        k = ~np.isnan(Y[:, j])
        if not k.any():
            tot[j] = np.nan
            continue
        x, y, w0 = X[k], Y[k, j], e[k]
        w = w0.copy()
        for _ in range(iters):
            g0 = np.zeros(X.shape[1])
            g0[src[j]] = 1
            g0 += np.average(y - x @ g0, weights=w)
            A = (x * w[:, None]).T @ x
            L = lam * np.trace(A) / len(A)
            g = np.linalg.solve(A + (L + 1e-9) * np.eye(len(A)), (x * w[:, None]).T @ y + L * g0)
            r = y - x @ g
            s = 1.4826 * np.median(np.abs(r - np.median(r))) + 1e-9
            w = w0 * np.minimum(1, c * s / np.maximum(np.abs(r), 1e-12))
        tot[j] = nat @ g
    return tot


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    Y0, Y1 = args[:2]
    fs.bloques_destino(Y1)
    sys.argv = [sys.argv[0], Y0, Y1] + (["--circuito"] if "--circuito" in sys.argv else [])
    import backtest as bt
    st, info, dcols = bt.state()
    X, Y, e, dist = st["X"], st["Y"], st["e"], st["dist"]
    st["amba"] = fm.region(st["distrito_id"], st["seccion_id"], "amba") == "AMBA"
    oc = [c.replace(" (orig)", "") for c in st["ocols"]]
    sm = fs.SRC.get((Y0, Y1), {})
    src = [[oc.index(o) for o in sm.get(c, [c]) if o in oc] for c in dcols]
    nd = dist.max() + 1
    natd = np.zeros((nd, X.shape[1]))
    np.add.at(natd, dist, X * e[:, None])
    nat = natd.sum(0)
    strat = {"amba": fm.region(st["distrito_id"], st["seccion_id"], "amba")}
    strat["tres"] = np.where(strat["amba"] == "AMBA", "AMBA",
                             np.where(np.asarray(st["distrito_id"]).astype(str) == "02", "BA interior", "resto"))
    share = {k: pd.Series(e).groupby(v).sum().pipe(lambda x: x / x.sum()).to_dict() for k, v in strat.items()}
    pos = st["pos"]
    real = fm.pct(st["Vd"].sum(0), pos)
    top = np.argsort(-real)[:2]
    rm = real[top[0]] - real[top[1]]
    rng = np.random.default_rng(28)
    rows = []
    for scheme in ("como25", "twitter"):
        for rep in range(REPS):
            idx, clus = fs.colecciones(st, rng, scheme, 30)
            nc = pd.Series(clus).map(pd.Series(clus).value_counts()).to_numpy(float)
            for name, lam, ps, alfa, hub in VARIANTES:
                w = fm.poststrat(e[idx], strat[ps][idx], share[ps]) / nc ** alfa
                if hub:
                    tot = goodman_huber(X[idx], Y[idx], w, nat, src, lam)
                else:
                    tot = fm.goodman(X[idx], Y[idx], w, nat, src, lam)
                p = fm.pct(tot, pos)
                rows.append(dict(esquema=scheme, rep=rep, variante=name, err=(p[top[0]] - p[top[1]]) - rm,
                                 mae=np.abs(p - real).mean()))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(fs.OUT, "tw_%s_%s.csv" % (Y0, Y1)), index=False)
    df["abs"] = df.err.abs()
    t = df.pivot_table(index="variante", columns="esquema", values=["abs", "err", "mae"]).round(2)
    print(t.loc[[v[0] for v in VARIANTES]].to_string())


if __name__ == "__main__":
    main()
