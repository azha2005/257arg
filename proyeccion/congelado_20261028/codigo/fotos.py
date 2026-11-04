"""¿Alcanzan unas pocas fotos de actas (25-100 mesas) para proyectar el total nacional? -> proyeccion/fotos_<par>.csv
    python proyeccion/fotos.py 2023p 2023b
    python proyeccion/fotos.py 2019p 2023p --circuito
Seleccion de las mesas (las fotos que suben los usuarios no son al azar):
  azar         mesas al azar;
  nivel        mas probable cuanto mas saca el ganador en la mesa (peso exp(z), z = % del ganador estandarizado);
  cambio       mas probable cuanto mas mejoro el ganador respecto de lo esperado por la eleccion anterior (residuo
               de la matriz nacional ajustada con todas las mesas): es el sesgo que el modelo NO corrige;
  cambio_mixto la mitad de las fotos con sesgo de cambio a favor de cada uno de los dos primeros.
Proyeccion nacional: crudo y D (matriz nacional con tamaño de seccion y circuito, sin la parte por distrito, que con
tan pocas mesas no aporta). Banda: bootstrap + termino sistematico de aguja.py."""
import os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backtest as bt
import aguja

REPS = 300
NS = [25, 50, 100]


def main():
    st, info, dcols = bt.state()
    e, Y, pos, win = st["e"], st["Y"], st["pos"], st["win"]
    n = len(e)
    V = st["Vd"]
    real = 100 * V.sum(0)[pos] / V.sum(0)[pos].sum()
    j = pos.index(win)
    second = pos[np.argsort(-real)[1]]
    F = np.column_stack([st["X"], st["F_tam"]])
    # residuo de cada mesa contra la matriz nacional ajustada con todas (lo «inesperado» de la mesa)
    G = np.linalg.solve((F * e[:, None]).T @ F + 1e-9 * np.eye(F.shape[1]), (F * e[:, None]).T @ Y)
    res = Y - F @ G
    ok = Y[:, pos].sum(1) > 0                                   # mesas sin votos positivos: nadie les saca foto
    share = np.where(ok, Y[:, win] / np.where(ok, Y[:, pos].sum(1), 1), 0)
    z = {"nivel": bt.zscore(share, e), "cambio": bt.zscore(res[:, win], e), "cambio2": bt.zscore(res[:, second], e)}
    z = {k: np.where(ok, v, -50) for k, v in z.items()}
    rng = np.random.default_rng(50)
    rows = []
    for sel in ("azar", "nivel", "cambio", "cambio_mixto"):
        for N in NS:
            for rep in range(REPS):
                if sel == "azar":
                    idx = rng.choice(np.where(ok)[0], N, replace=False)
                elif sel == "cambio_mixto":
                    p1 = np.exp(z["cambio"]); p2 = np.exp(z["cambio2"])
                    a = rng.choice(n, N // 2, replace=False, p=p1 / p1.sum())
                    b = rng.choice(n, N - N // 2, replace=False, p=p2 / p2.sum())
                    idx = np.unique(np.r_[a, b])
                else:
                    p = np.exp(z[sel])
                    idx = rng.choice(n, N, replace=False, p=p / p.sum())
                cnt = np.zeros(n, bool); cnt[idx] = True
                crudo = 100 * V[cnt].sum(0)[pos] / V[cnt].sum(0)[pos].sum()
                boot = aguja.national_boot(st, cnt, F, rng, 100)
                sd = np.sqrt(boot[1:].var(0) + aguja.sistematico(cnt.mean()) ** 2)
                rows.append(dict(seleccion=sel, N=N, err_crudo=crudo[j] - real[j], err_D=boot[0][j] - real[j],
                                 dentro=abs(boot[0][j] - real[j]) <= 1.96 * sd[j], semiancho=1.96 * sd[j],
                                 acierta=int(np.argmax(boot[0]) == np.argmax(real))))
    df = pd.DataFrame(rows)
    tag = "%s_%s%s" % (bt.Y0, bt.Y1, "_circuito" if bt.CIRC else "")
    df.to_csv(os.path.join(HERE, "fotos_%s.csv" % tag), index=False)
    g = df.groupby(["seleccion", "N"])
    t = pd.DataFrame({"crudo_abs": g.err_crudo.apply(lambda s: s.abs().mean()), "D_sesgo": g.err_D.mean(),
                      "D_abs": g.err_D.apply(lambda s: s.abs().mean()), "D_p90": g.err_D.apply(lambda s: s.abs().quantile(.9)),
                      "banda_95": g.semiancho.mean(), "cobertura": g.dentro.mean(), "ganador_ok": g.acierta.mean()}).round(2)
    print(tag, "real", np.round(real, 2))
    print(t.to_string())


if __name__ == "__main__":
    main()
