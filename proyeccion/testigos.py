"""¿Hay mesas o circuitos «testigo» que anticipen el resultado nacional? -> proyeccion/testigos/RESUMEN.md
    python proyeccion/testigos.py
Cifra: % del peronismo sobre votos positivos (FPV 2011/2015, FdT 2019, UxP 2023), que es la unica fuerza presente
con el mismo perfil en todas las presidenciales. Datos: transferencias/circ_<eleccion>.pkl (por circuito) y
proyeccion/mesas_2023p.pkl / mesas_2023b.pkl (por mesa).
1. Circuitos testigo elegidos SOLO con 2011-2019 y probados en 2023 (general y balotaje):
   nivel  = los N circuitos cuyo % mas se parecio al nacional en 2011, 2015 (1.a y 2.a vuelta) y 2019;
   swing  = los N circuitos cuyo cambio entre elecciones mas se parecio al cambio nacional;
   contra N circuitos al azar (sorteados con probabilidad proporcional a sus votos, como mesas al azar) con
   promedio crudo o con swing desde 2019. 500 sorteos por N.
2. Mesas: ¿la mesa que se parecio al nacional en la 1.a vuelta 2023 se parece tambien en el balotaje?"""
import os, re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.join(HERE, "..", "transferencias")
OUT = os.path.join(HERE, "testigos")
PJ = re.compile(r"FRENTE PARA LA VICTORIA|FRENTE DE TODOS|UNION POR LA PATRIA")
TRAIN = ["2011p", "2015p", "2015b", "2019p"]
TEST = ["2023p", "2023b"]
NS = [5, 10, 25, 50, 100, 250]
DRAWS = 500
KEY = ["distrito_id", "seccion_id", "circuito"]


def shares(arg):
    v, _ = pd.read_pickle(os.path.join(TR, "circ_%s.pkl" % arg))
    v = v[v.votos_tipo.str.upper().str.startswith("POSITIVO")]
    pos = v.groupby(KEY).v.sum()
    pj = v[v.agrupacion_id.str.contains(PJ)].groupby(KEY).v.sum().reindex(pos.index, fill_value=0)
    return pd.DataFrame({"pj_" + arg: 100 * pj / pos, "pos_" + arg: pos})


def names():
    """Nombre de seccion y circuito, de la planilla del balotaje 2023."""
    import glob
    f = glob.glob(os.path.join(HERE, "..", "datos_oficiales", "2023_balotaje", "x", "*", "Resultados*.csv"))[0]
    n = pd.read_csv(f, dtype=str, usecols=["distrito_nombre", "distrito_id", "seccion_id", "seccion_nombre", "circuito_id", "circuito_nombre"]).drop_duplicates()
    n["distrito_id"] = n.distrito_id.astype(int).map("{:02d}".format)
    n["seccion_id"] = n.seccion_id.astype(int)
    n["circuito"] = n.circuito_id.fillna("").str.strip().str.upper().str.lstrip("0").replace("", "0")
    return n.drop_duplicates(KEY).set_index(KEY)[["distrito_nombre", "seccion_nombre", "circuito_nombre"]]


def main():
    os.makedirs(OUT, exist_ok=True)
    elections = TRAIN + TEST
    full = {a: shares(a) for a in elections}
    nat = {a: (full[a]["pj_" + a] * full[a]["pos_" + a]).sum() / full[a]["pos_" + a].sum() for a in elections}
    df = pd.concat(full.values(), axis=1, join="inner").dropna()
    df = df[(df[["pos_" + a for a in elections]] >= 100).all(axis=1)]   # circuitos minimos: puro ruido
    dev = pd.DataFrame({a: df["pj_" + a] - nat[a] for a in elections})
    df["nivel"] = np.sqrt((dev[TRAIN] ** 2).mean(axis=1))
    sw = pd.DataFrame({b: dev[b] - dev[a] for a, b in zip(TRAIN, TRAIN[1:])})
    df["swing"] = np.sqrt((sw ** 2).mean(axis=1))
    for a in TEST:
        df["dev_" + a] = dev[a]
        df["swdev_" + a] = dev[a] - dev["2019p"]
    L = ["# Circuitos y mesas testigo", "",
         "Generado por `python proyeccion/testigos.py`. Cifra: %% del peronismo (FPV, FdT, UxP) sobre positivos. "
         "%d circuitos presentes con 100 votos o mas en las seis elecciones (los circuitos que cambiaron de codigo, "
         "como Santa Fe en 2023, quedan afuera)." % len(df), "",
         "Nacional: " + ", ".join("%s %.2f %%" % (a, nat[a]) for a in elections), ""]

    # ---- 1. testigos elegidos con 2011-2019 contra circuitos al azar ----
    rng = np.random.default_rng(2027)
    w = df["pos_2019p"].to_numpy(float)
    p = w / w.sum()
    rows = []
    for a in TEST:
        y = df["pj_" + a].to_numpy()
        prev = df["pj_2019p"].to_numpy()
        for N in NS:
            for score in ("nivel", "swing"):
                top = df.nsmallest(N, score)
                est = top["pj_" + a].mean() if score == "nivel" else nat["2019p"] + (top["pj_" + a] - top["pj_2019p"]).mean()
                rows.append(dict(eleccion=a, N=N, metodo="testigos " + score, err_abs=abs(est - nat[a]), err_p90=abs(est - nat[a])))
            e_raw, e_sw = [], []
            for _ in range(DRAWS):
                i = rng.choice(len(df), N, replace=False, p=p)
                ww = w[i]
                e_raw.append((y[i] * ww).sum() / ww.sum() - nat[a])
                e_sw.append(nat["2019p"] + ((y[i] - prev[i]) * ww).sum() / ww.sum() - nat[a])
            for m, e in (("azar crudo", e_raw), ("azar + swing 2019", e_sw)):
                e = np.abs(e)
                rows.append(dict(eleccion=a, N=N, metodo=m, err_abs=e.mean(), err_p90=np.quantile(e, .9)))
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(OUT, "testigos_vs_azar.csv"), index=False)
    L += ["## 1. Testigos elegidos con 2011-2019, probados en 2023", "",
          "Error absoluto en puntos del %% nacional. Para los testigos hay una sola seleccion (err_p90 = err_abs); "
          "al azar, %d sorteos." % DRAWS, ""]
    for a in TEST:
        L += ["### %s (real %.2f %%)" % (a, nat[a]), "", "| N circuitos | " + " | ".join(t.metodo.unique()) + " |",
              "|---|" + "---|" * t.metodo.nunique()]
        for N in NS:
            s = t[(t.eleccion == a) & (t.N == N)].set_index("metodo")
            L.append("| %d | " % N + " | ".join("%.2f (p90 %.2f)" % (s.err_abs[m], s.err_p90[m]) for m in t.metodo.unique()) + " |")
        L.append("")
    # ¿el puntaje de 2011-2019 predice la cercania en 2023?
    L += ["**¿Persisten?** Correlacion (Spearman) entre el puntaje de 2011-2019 y la distancia al nacional en 2023: " +
          ", ".join("%s nivel %.2f, swing %.2f" % (a, df.nivel.corr(df["dev_" + a].abs(), method="spearman"),
                                                  df.swing.corr(df["swdev_" + a].abs(), method="spearman")) for a in TEST) + ".", ""]

    # ---- lista de testigos ----
    nm = names()
    top = df.nsmallest(25, "nivel").join(nm)
    top[["distrito_nombre", "seccion_nombre", "circuito_nombre", "nivel", "dev_2023p", "dev_2023b", "pos_2023b"]].round(2).to_csv(
        os.path.join(OUT, "testigos_nivel_top25.csv"), encoding="utf-8")
    L += ["## Los 25 circuitos mas parecidos al pais en 2011-2019", "",
          "`nivel` = desvio cuadratico medio 2011-2019; despues, la diferencia con el nacional en 2023.", "",
          "| distrito | seccion | circuito | nivel | 2023 general | 2023 balotaje | votos |", "|---|---|---|---|---|---|---|"]
    for r in top.itertuples():
        L.append("| %s | %s | %s | %.2f | %+.2f | %+.2f | %d |" % (r.distrito_nombre, r.seccion_nombre, r.circuito_nombre, r.nivel, r.dev_2023p, r.dev_2023b, r.pos_2023b))
    L.append("")

    # ---- 2. mesas ----
    mp = pd.read_pickle(os.path.join(HERE, "mesas_2023p.pkl"))
    mb = pd.read_pickle(os.path.join(HERE, "mesas_2023b.pkl"))
    k = ["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]
    pos_cols = lambda m: [c for c in m.columns if c not in k + ["e", "BLANCO", "NULO", "OTROS"]]
    m = mp[k].copy()
    m["pj_p"] = 100 * mp["UNION POR LA PATRIA"] / mp[pos_cols(mp)].sum(axis=1)
    m["pos_p"] = mp[pos_cols(mp)].sum(axis=1)
    mb2 = mb[k].copy()
    mb2["pj_b"] = 100 * mb["UNION POR LA PATRIA"] / mb[pos_cols(mb)].sum(axis=1)
    m = m.merge(mb2, on=k).dropna()
    m = m[m.pos_p >= 100]
    m["dp"] = (m.pj_p - nat["2023p"]).abs()
    m["db"] = (m.pj_b - nat["2023b"]).abs()
    L += ["## 2. Mesas: 1.a vuelta 2023 -> balotaje", "",
          "%d mesas con 100 votos positivos o mas; distancia media de todas al nacional del balotaje: %.2f puntos. "
          "Correlacion (Spearman) entre la distancia en una y otra vuelta: %.2f." % (len(m), m.db.mean(), m.dp.corr(m.db, method="spearman")), "",
          "| mesas mas cercanas en la 1.a vuelta | distancia en la 1.a | distancia media en el balotaje | %% del grupo sumado en el balotaje (real %.2f) |" % nat["2023b"],
          "|---|---|---|---|"]
    for n in (10, 100, 1000, 5000):
        best = m.nsmallest(n, "dp")
        pooled = (best.pj_b * best.pos_p).sum() / best.pos_p.sum()
        L.append("| %d | %.2f | %.2f | %.2f |" % (n, best.dp.mean(), best.db.mean(), pooled))
    L += ["", "Una mesa tiene unos 300 votantes: solo por azar su % se mueve unos ±3 puntos, asi que una mesa sola no "
          "sirve de testigo; un grupo de mesas elegido con la eleccion anterior si, pero esas mesas no llegan cuando uno "
          "quiere. Por eso el modelo de proyeccion tiene que funcionar con las mesas que entren, al azar o no.", ""]
    open(os.path.join(OUT, "RESUMEN.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
