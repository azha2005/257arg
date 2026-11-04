"""ICG del mes anterior como prior del voto al oficialismo, combinado con la proyección de las fotos (28-oct-2026).
Prior de cada elección: regresión voto ~ ICG del mes anterior + presidencial, ajustada SIN esa elección y sin 2003
(icg_voto.py / elecciones.csv). Combinación: oficialismo = w × prior + (1 − w) × fotos, las demás fuerzas en
proporción; w = σf² / (σf² + σp²), con σp el error del prior dejando una elección afuera y σf el error típico de las
fotos en la proporción del oficialismo (de fotos_sim: margen 1,9 al azar y 2,7–3,1 tipo Twitter; proporción ≈
margen / 1,6). Además se muestra una grilla de w.
    python -X utf8 proyeccion/icg/icg_fotos.py 2023p 2025bl --circuito [--reps 300]
Salida: proyeccion/icg/sim_<origen>_<destino>.csv."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.join(HERE, "..")
sys.path.insert(0, PROY)
sys.path.insert(0, HERE)

OFI = {"2025bl": ("LLA", "2025-10-26"), "2023p": ("UNION POR LA PATRIA", "2023-10-22")}
SIGMA_F = {"azar": 1.2, "como25": 1.8, "twitter": 1.8}
GRILLA = [0, 0.1, 0.2, 0.3, 0.5]


def prior(fecha, base=None, modo="temporal"):
    """(predicción, σ) usando solo elecciones anteriores. modo=loo para diagnostico retrospectivo."""
    import icg_voto as iv
    df = pd.read_csv(os.path.join(HERE, "elecciones.csv")) if base is None else base
    select = df.fecha < fecha if modo == "temporal" else df.fecha != fecha
    df = df[(df.fecha > "2004") & select].reset_index(drop=True)
    if len(df) < 4:
        raise ValueError("Historia insuficiente para calibrar el prior ICG antes de " + fecha)
    X = np.c_[np.ones(len(df)), df.mes_anterior, df.pres]
    b = np.linalg.lstsq(X, df.voto.to_numpy(float), rcond=None)[0]
    t = pd.read_csv(os.path.join(HERE, "elecciones.csv")).set_index("fecha").loc[fecha]
    s = np.sqrt((iv.loo(df, ["mes_anterior", "pres"]) ** 2).mean())
    return float(np.r_[1, t.mes_anterior, t.pres] @ b), float(s)


def mezclar(p, j, pri, w):
    """p = % por fuerza (suma 100), j = índice del oficialismo."""
    q = p.copy()
    q[j] = w * pri + (1 - w) * p[j]
    o = np.arange(len(p)) != j
    q[o] = p[o] * (100 - q[j]) / p[o].sum()
    return q


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    Y0, Y1 = args[:2]
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 300
    import fotos_modelo as fm
    import fotos_sim as fs
    fs.bloques_destino(Y1)
    sys.argv = [sys.argv[0], Y0, Y1] + (["--circuito"] if "--circuito" in sys.argv else [])
    import backtest as bt
    st, info, dcols = bt.state()
    X, Y, e, dist = st["X"], st["Y"], st["e"], st["dist"]
    st["amba"] = fm.region(st["distrito_id"], st["seccion_id"], "amba") == "AMBA"
    oc = [c.replace(" (orig)", "") for c in st["ocols"]]
    sm = fs.SRC.get((Y0, Y1), {})
    src = [[oc.index(o) for o in sm.get(c, [c]) if o in oc] for c in dcols]
    natd = np.zeros((dist.max() + 1, X.shape[1]))
    np.add.at(natd, dist, X * e[:, None])
    nat = natd.sum(0)
    s_f = fm.region(st["distrito_id"], st["seccion_id"], "amba")
    share = pd.Series(e).groupby(s_f).sum().pipe(lambda x: x / x.sum()).to_dict()
    pos = st["pos"]
    names = [dcols[i] for i in pos]
    ofi, fecha = OFI[Y1]
    j = names.index(ofi)
    real = fm.pct(st["Vd"].sum(0), pos)
    top = np.argsort(-real)[:2]
    pri, sp = prior(fecha)
    print("%s -> %s: oficialismo %s real %.2f, prior ICG %.2f (σ %.2f)" % (Y0, Y1, ofi, real[j], pri, sp))
    rng = np.random.default_rng(28)
    rows = []
    for scheme in ("azar", "como25", "twitter"):
        w0 = SIGMA_F[scheme] ** 2 / (SIGMA_F[scheme] ** 2 + sp ** 2)
        for rep in range(reps):
            idx, clus = fs.colecciones(st, rng, scheme, 30)
            w = fm.poststrat(e[idx], s_f[idx], share)
            p = fm.pct(fm.goodman(X[idx], Y[idx], w, nat, src, 0.1), pos)
            for tag, ww in [("w óptimo", w0)] + [("w %.1f" % g, g) for g in GRILLA]:
                q = mezclar(p, j, pri, ww)
                rows.append(dict(par="%s→%s" % (Y0, Y1), esquema=scheme, rep=rep, variante=tag, w=ww,
                                 err_ofi=q[j] - real[j], err_margen=(q[top[0]] - q[top[1]]) - (real[top[0]] - real[top[1]]),
                                 mae=np.abs(q - real).mean()))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "sim_%s_%s.csv" % (Y0, Y1)), index=False)
    g = df.assign(a_ofi=df.err_ofi.abs(), a_mar=df.err_margen.abs()).groupby(["esquema", "variante"], sort=False)
    print(g[["w", "a_ofi", "err_ofi", "a_mar", "mae"]].mean().round(2).to_string())


if __name__ == "__main__":
    main()
