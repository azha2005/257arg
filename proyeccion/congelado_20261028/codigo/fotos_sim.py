"""Calibracion del modelo de fotos de actas con elecciones ya terminadas: se simulan colecciones de fotos como las
que se juntan la noche de la eleccion y se mide el error y la cobertura de la banda.
    python proyeccion/fotos_sim.py 2023p 2025bl --circuito     # presidente 2023 -> diputados 2025 (bloques)
    python proyeccion/fotos_sim.py 2019p 2023p --circuito      # presidente 2019 -> 2023
    python proyeccion/fotos_sim.py 2023p 2023b                 # 1.a vuelta -> balotaje, mesa a mesa
    python proyeccion/fotos_sim.py 2015p 2015b
Colecciones (n = 25, 50 y 100 mesas):
  azar       mesas sueltas al azar en todo el pais.
  estrat     mesas sueltas, repartidas entre distritos en proporcion a los electores (lo que se puede pedir a mano).
  racimos    de a 3 mesas del mismo circuito (fotos del mismo local), circuitos al azar segun electores.
  twitter    racimos, con el 65 % en el AMBA (Capital y los 24 partidos): como las fotos de 2025 (20 de 29).
  como25     armado como las fotos de 2025: entre 25 y 35 mesas (n se ignora), un racimo de 10 mesas seguidas y dos de 3
             en el AMBA, otras ~6 mesas sueltas del AMBA y el resto sueltas en el interior.
Metodos (fotos_modelo.py): swing uniforme y Goodman encogido al swing, con y sin postestratificar (las fotos se
repesan para que el AMBA, o cada una de ocho regiones, pese lo que pesa en el padron).
Banda: bootstrap de los grupos (circuitos), 95 %. Se mide su cobertura del margen entre los dos primeros y el factor
por el que habria que multiplicarla para cubrir el 95 % de las veces.
Salida: proyeccion/fotos_sim/<origen>_<destino>.csv y RESUMEN.md (todas las corridas que haya)."""
import os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "fotos_sim")
os.makedirs(OUT, exist_ok=True)
import fotos_modelo as fm

args = [a for a in sys.argv[1:] if not a.startswith("--")]
Y0, Y1 = args[:2]
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 200
NBOOT = 100
NS = [25, 50, 100]
SCHEMES = ["azar", "estrat", "racimos", "twitter"]
if "--ns" in sys.argv:                                   # p. ej. --ns 30 --esquemas azar,twitter,como25
    NS = [int(x) for x in sys.argv[sys.argv.index("--ns") + 1].split(",")]
if "--esquemas" in sys.argv:
    SCHEMES = sys.argv[sys.argv.index("--esquemas") + 1].split(",")
TAG = ("_n" + "-".join(map(str, NS)) if "--ns" in sys.argv else "") + ("_ancla" if "--ancla" in sys.argv else "")
# (nombre, modelo, postestratificacion): la primera tanda (27-oct-2026) probo tambien swing por distrito (k=5 y 20) y
# Goodman lam=1; no ganaban en ningun caso
METHODS = [("swing uniforme", ("swing", np.inf), None), ("Goodman lam=0,3", ("goodman", 0.3), None),
           ("Goodman lam=0,1", ("goodman", 0.1), None), ("Goodman lam=0,1 + AMBA/resto", ("goodman", 0.1), "amba"),
           ("Goodman lam=0,1 + regiones", ("goodman", 0.1), "region"),
           ("swing uniforme + regiones", ("swing", np.inf), "region")]
if "--ancla" in sys.argv:                                 # ancla de Israel (cambio proporcional), 28-oct-2026
    METHODS = [m for m in METHODS if m[0] in ("swing uniforme", "Goodman lam=0,1 + AMBA/resto")] + [
        ("Prop. lam=0,1 + AMBA/resto", ("goodman_prop", 0.1), "amba"),
        ("Prop. lam=300/n + AMBA/resto", ("goodman_prop", "np"), "amba"),
        ("Prop. puro + AMBA/resto", ("goodman_prop", np.inf), "amba")]
BANDA = ["Goodman lam=0,1", "Goodman lam=0,1 + AMBA/resto", "swing uniforme + regiones"]
# antecesor de cada fuerza de destino (nombres de origen sin " (orig)"); lo que no esta: el mismo nombre
SRC = {("2023p", "2025bl"): {"LLA": ["LA LIBERTAD AVANZA", "JUNTOS POR EL CAMBIO"], "FP": ["UNION POR LA PATRIA"],
                             "PU": ["HACEMOS POR NUESTRO PAIS"],
                             "FIT": ["FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD"]},
       ("2019p", "2023p"): {"UNION POR LA PATRIA": ["FRENTE DE TODOS"], "LA LIBERTAD AVANZA": ["FRENTE NOS", "OTRAS LISTAS"],
                            "HACEMOS POR NUESTRO PAIS": ["CONSENSO FEDERAL"]},
       ("2021bl", "2023p"): {"UNION POR LA PATRIA": ["FdT"], "JUNTOS POR EL CAMBIO": ["JxC"], "LA LIBERTAD AVANZA": ["LLA"],
                             "HACEMOS POR NUESTRO PAIS": ["Tercera Via"],
                             "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": ["FIT"]},
       ("2021bl", "2025bl"): {"LLA": ["LLA", "JxC"], "FP": ["FdT"], "PU": ["Tercera Via"]},
       ("2015p", "2015b"): {"CAMBIEMOS": ["ALIANZA CAMBIEMOS"], "FRENTE PARA LA VICTORIA": ["ALIANZA FRENTE PARA LA VICTORIA"]}}


def bloques_destino(arg):
    """mesas_<año>bl.pkl (diputados en bloques) con bloques.py si falta."""
    if arg.endswith("bl") and not os.path.exists(os.path.join(HERE, "mesas_%s.pkl" % arg)):
        import bloques
        bloques.main(arg[:-2])


def colecciones(st, rng, scheme, n):
    """Indices de las mesas fotografiadas y el grupo (circuito) de cada una."""
    e, circ, dist = st["e"], st["circ"], st["dist"]
    N = len(e)
    if scheme == "azar":
        idx = rng.choice(N, n, replace=False)
    elif scheme == "estrat":
        ed = np.bincount(dist, weights=e)
        q = n * ed / ed.sum()
        k = np.floor(q).astype(int)
        k[np.argsort(-(q - k))[:n - k.sum()]] += 1
        idx = np.concatenate([rng.choice(np.where(dist == d)[0], k[d], replace=False) for d in range(len(k)) if k[d]])
    elif scheme == "como25":
        ce = np.bincount(circ, weights=e)
        amba = np.zeros(len(ce), bool)
        amba[circ[st["amba"]]] = True
        n = int(rng.integers(25, 36))
        pa = np.where(amba, ce, 0) / ce[amba].sum()
        idx = []
        for size in (10, 3, 3):
            c = rng.choice(len(ce), p=pa)
            mm = np.where(circ == c)[0]
            s = rng.integers(len(mm))
            idx += list(mm[np.arange(s, s + size) % len(mm)][:min(size, len(mm))])
        ia, ir = np.where(st["amba"])[0], np.where(~st["amba"])[0]
        na = max(0, int(round(2 / 3 * n)) - len(idx))
        idx += list(rng.choice(ia, na, replace=False)) + list(rng.choice(ir, n - len(idx) - na, replace=False))
        idx = np.unique(np.array(idx))
    else:
        ce = np.bincount(circ, weights=e)
        amba = np.zeros(len(ce), bool)
        amba[circ[st["amba"]]] = True
        nclus = int(np.ceil(n / 3))
        if scheme == "racimos":
            cs = rng.choice(len(ce), nclus, replace=False, p=ce / ce.sum())
        else:
            na = int(round(.65 * nclus))
            pa, pr = np.where(amba, ce, 0), np.where(amba, 0, ce)
            cs = np.concatenate([rng.choice(len(ce), na, replace=False, p=pa / pa.sum()),
                                 rng.choice(len(ce), nclus - na, replace=False, p=pr / pr.sum())])
        idx = []
        for c in cs:
            mm = np.where(circ == c)[0]
            s = rng.integers(len(mm))
            idx += list(mm[np.arange(s, s + 3) % len(mm)][:min(3, len(mm))])
        idx = np.array(idx[:n])
    return idx, circ[idx]


def main():
    bloques_destino(Y1)
    sys.argv = [sys.argv[0], Y0, Y1] + [a for a in ("--circuito", "--ancla") if a in sys.argv]
    import backtest as bt
    st, info, dcols = bt.state()
    X, Y, e, dist = st["X"], st["Y"], st["e"], st["dist"]
    st["amba"] = fm.region(st["distrito_id"], st["seccion_id"], "amba") == "AMBA"
    oc = [c.replace(" (orig)", "") for c in st["ocols"]]
    sm = SRC.get((Y0, Y1), {})
    src = [[oc.index(o) for o in sm.get(c, [c]) if o in oc] for c in dcols]
    print("antecesores:", {c: [oc[i] for i in s] for c, s in zip(dcols, src)}, flush=True)
    nd = dist.max() + 1
    natd = np.zeros((nd, X.shape[1]))
    np.add.at(natd, dist, X * e[:, None])
    ed = np.bincount(dist, weights=e)
    strat = {k: fm.region(st["distrito_id"], st["seccion_id"], k) for k in ("amba", "region")}
    share = {k: pd.Series(e).groupby(v).sum().pipe(lambda x: x / x.sum()).to_dict() for k, v in strat.items()}
    pos = st["pos"]
    real = fm.pct(st["Vd"].sum(0), pos)
    top = np.argsort(-real)[:2]
    rmarg = real[top[0]] - real[top[1]]
    print("real", dict(zip([dcols[p] for p in pos], real.round(2))), flush=True)
    rng = np.random.default_rng(2027)
    rows = []
    t0 = time.time()
    for scheme in SCHEMES:
        for n in NS:
            for rep in range(REPS):
                idx, clus = colecciones(st, rng, scheme, n)
                Xi, Yi, ei, di = X[idx], Y[idx], e[idx], dist[idx]
                for name, spec, ps in METHODS:
                    if ps:
                        ei = fm.poststrat(e[idx], strat[ps][idx], share[ps])
                    else:
                        ei = e[idx]
                    p = fm.pct(fm.project(spec, Xi, Yi, ei, di, natd, ed, src), pos)
                    r = dict(esquema=scheme, n=n, rep=rep, metodo=name, err_margen=(p[top[0]] - p[top[1]]) - rmarg,
                             err_1=p[top[0]] - real[top[0]], err_2=p[top[1]] - real[top[1]],
                             mae=np.abs(p - real).mean())
                    if name in BANDA and rep < REPS // 2 and "--ancla" not in sys.argv:
                        bs = fm.bootstrap(lambda k: fm.pct(fm.project(
                            spec, Xi[k], Yi[k], fm.poststrat(e[idx][k], strat[ps][idx][k], share[ps]) if ps else ei[k],
                            di[k], natd, ed, src), pos), clus, NBOOT, rng)
                        mb = bs[:, top[0]] - bs[:, top[1]]
                        lo, hi = np.percentile(mb, [2.5, 97.5])
                        r.update(cubre=lo <= rmarg <= hi, semiancho=(hi - lo) / 2,
                                 z=abs((p[top[0]] - p[top[1]]) - rmarg) / max((hi - lo) / 2, 1e-9))
                    rows.append(r)
            print(scheme, n, "%.0f s" % (time.time() - t0), flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "%s_%s%s.csv" % (Y0, Y1, TAG)), index=False)
    report()


def report():
    L = ["# Fotos de actas: calibración con elecciones terminadas", "",
         "Generado por `proyeccion/fotos_sim.py` (ver el encabezado del script). Error del **margen entre los dos "
         "primeros** en puntos (sobre votos positivos). `cobertura` = veces que la banda del 95 % por bootstrap de "
         "circuitos contiene el margen real; `factor` = por cuánto multiplicar la banda para que cubra el 95 %.", ""]
    for f in sorted(os.listdir(OUT)):
        if not f.endswith(".csv") or f.startswith(("dos_origenes", "fuerzas")):
            continue
        df = pd.read_csv(os.path.join(OUT, f))
        df["abs"] = df.err_margen.abs()
        L += ["## %s" % f[:-4].replace("_", " → "), "", "Error absoluto medio del margen:", ""]
        t = df.pivot_table(index="metodo", columns=["esquema", "n"], values="abs", aggfunc="mean")
        t = t[[c for c in t.columns]]
        L.append("| Método | " + " | ".join("%s %d" % c for c in t.columns) + " |")
        L.append("|---|" + "---:|" * len(t.columns))
        for m, r in t.iterrows():
            L.append("| %s | " % m + " | ".join("%.2f" % v for v in r) + " |")
        L += ["", "Sesgo medio del margen (signo +: sobrestima al primero):", ""]
        t = df.pivot_table(index="metodo", columns=["esquema", "n"], values="err_margen", aggfunc="mean")
        L.append("| Método | " + " | ".join("%s %d" % c for c in t.columns) + " |")
        L.append("|---|" + "---:|" * len(t.columns))
        for m, r in t.iterrows():
            L.append("| %s | " % m + " | ".join("%+.2f" % v for v in r) + " |")
        b = df.dropna(subset=["cubre"]) if "cubre" in df else df.iloc[:0]
        if len(b):
            g = b.groupby(["metodo", "esquema", "n"])
            c = pd.DataFrame({"cobertura": g.cubre.mean() * 100, "semiancho": g.semiancho.mean(),
                              "factor": g.z.quantile(.95)}).reset_index()
            L += ["", "Banda del 95 % (bootstrap de circuitos):", "",
                  "| Método | esquema | n | cobertura % | semiancho medio | factor |", "|---|---|---:|---:|---:|---:|"]
            for r in c.itertuples():
                L.append("| %s | %s | %d | %.0f | %.2f | %.2f |" % (r.metodo, r.esquema, r.n, r.cobertura, r.semiancho,
                                                                   r.factor))
        L.append("")
    open(os.path.join(OUT, "RESUMEN.md"), "w", encoding="utf-8").write("\n".join(L))
    print("RESUMEN en", OUT)


if __name__ == "__main__":
    main()
