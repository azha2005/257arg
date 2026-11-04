"""Backtest con el orden real de esta noche: las urnas contadas en un expb.csv de 2026 (p. ej. el del 7 %) se buscan
en cada eleccion de 2019-2022 (misma localidad y numero de urna; si en esa localidad faltan, se completan al azar
con otras urnas de la misma localidad hasta la misma cantidad) y se proyecta desde la eleccion anterior con varias
variantes del modelo (KR: residuo por localidad; KV: residuo de vecinas).
    python -X utf8 proyeccion/israel/backtest_7.py "C:/Users/JC/Downloads/expb (4).csv"
Salida: proyeccion/israel/backtest_7.csv y un resumen en pantalla."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import datos as dt
import modelo as md

PARES = [(21, 22), (22, 23), (23, 24), (24, 25)]
VARIANTES = [("base (ancla)", 0, 0), ("+ localidad", 1500, 0), ("+ vecinas 1500", 1500, 1500),
             ("+ vecinas 5000", 1500, 5000), ("+ vecinas 15000", 1500, 15000)]
REPS = 8
if os.environ.get("SOLO"):
    VARIANTES = [v for v in VARIANTES if v[0] == os.environ["SOLO"]]
NBOOT = 200


def main():
    d26 = pd.read_csv(sys.argv[1], encoding="utf-8-sig")
    d26 = d26[(d26["מצביעים"] > 0) & ~d26["סמל ישוב"].isin(dt.DOBLE)]
    pedido = d26.groupby("סמל ישוב")["קלפי"].apply(lambda s: set(s.astype(float).astype(int)))
    rows, por_lista = [], []
    for o, de in PARES:
        st = md.preparar(o, de)
        ac = dt.ACUERDOS.get(de, ())
        v, p = dt.cargar(de)
        real = dt.bancas(v[p].sum().to_dict(), ac)
        rs = np.array([[real[x] for x in st["listas"]]])
        rb = md.bloques(st, rs, dt.BLOQUE[de])
        rres = md.resultado(rb["bibi"], rb["oposicion"])[0]
        ri = np.array([real[x] > 0 for x in st["listas"]])
        loc, kal = st["loc"], st["kalpi"]
        Yv = st["Y"] * st["w"][:, None]
        for rep in range(REPS):
            rng = np.random.default_rng(100 * de + rep)
            cnt = []
            for l, ks in pedido.items():
                idx = np.flatnonzero(loc == l)
                if not len(idx):
                    continue
                exact = idx[np.isin(kal[idx], list(ks))]
                resto = np.setdiff1d(idx, exact)
                falta = min(len(ks), len(idx)) - len(exact)
                cnt += list(exact) + (list(rng.choice(resto, falta, replace=False)) if falta > 0 else [])
            cnt = np.array(sorted(cnt))
            frac = st["w"][cnt].sum() / st["w"].sum()
            vc = Yv[cnt].sum(0)
            sc = dt.bancas({st["dcols"][i]: vc[i] for i in range(len(st["dcols"]) - 1)}, ac)
            bc = md.bloques(st, np.array([[sc[x] for x in st["listas"]]]), dt.BLOQUE[de])
            for nom, kr, kv in VARIANTES:
                md.KR, md.KV = kr, kv
                s, _ = md.proyectar(st, cnt, np.random.default_rng(rep), NBOOT, ac)
                b = md.bloques(st, s, dt.BLOQUE[de])
                res = md.resultado(b["bibi"], b["oposicion"])
                lo, hi = np.percentile(b["bibi"][1:], [5, 95])
                plo, phi = np.percentile(s[1:], [5, 95], axis=0)
                for i, x in enumerate(st["listas"]):
                    por_lista.append(dict(par="%d→%d" % (o, de), rep=rep, variante=nom, lista=x, real=rs[0, i],
                                          proy=s[0, i], conteo=sc[x], cubre90=plo[i] <= rs[0, i] <= phi[i]))
                rows.append(dict(par="%d→%d" % (o, de), rep=rep, variante=nom, urnas=len(cnt), fraccion=frac,
                                 err_bibi=b["bibi"][0] - rb["bibi"][0], err_arabe=b["arabe"][0] - rb["arabe"][0],
                                 err_bibi_conteo=bc["bibi"][0] - rb["bibi"][0],
                                 mae_listas=np.abs(s[0] - rs[0]).mean(), umbral_ok=((s[0] > 0) == ri).mean(),
                                 cubre90=lo <= rb["bibi"][0] <= hi, ancho90=hi - lo, desenlace_ok=res[0] == rres))
            print(o, de, rep, len(cnt), "%.3f" % frac, flush=True)
    df = pd.DataFrame(rows)
    suf = os.environ.get("SUF", "")
    df.to_csv(os.path.join(HERE, "backtest_7%s.csv" % suf), index=False)
    pd.DataFrame(por_lista).to_csv(os.path.join(HERE, "backtest_7%s_listas.csv" % suf), index=False)
    df["abs_bibi"], df["abs_arabe"], df["abs_conteo"] = df.err_bibi.abs(), df.err_arabe.abs(), df.err_bibi_conteo.abs()
    pd.set_option("display.width", 200)
    print(df.groupby(["par", "variante"], sort=False)[["urnas", "fraccion", "abs_bibi", "abs_arabe", "mae_listas",
                                                        "umbral_ok", "cubre90", "ancho90", "desenlace_ok",
                                                        "abs_conteo"]].mean().round(2).to_string())
    print(df.groupby("variante", sort=False)[["abs_bibi", "abs_arabe", "mae_listas", "umbral_ok", "cubre90",
                                              "ancho90", "desenlace_ok"]].mean().round(3).to_string())


if __name__ == "__main__":
    main()
