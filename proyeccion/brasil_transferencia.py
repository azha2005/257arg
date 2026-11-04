"""Modelo de transferencia de la proyeccion de Rodrigo Mahlmeister (Brasil 2026, hasta el 5 % contado), repetido con
el orden real de llegada del TSE. Solo votos validos: cada seccion que falta conserva los votos de Lula y Flavio de
la 1.a vuelta, y los de los demas candidatos se reparten entre los dos en la proporcion medida en lo ya contado
(cociente de totales, sin regresion), por grupo con encogimiento hacia el nacional:
    lula_2 = lula_1 + a * otros_1,   flavio_2 = flavio_1 + b * otros_1
con a = (sum lula_2 - sum lula_1) / sum otros_1 en lo contado del grupo.
    python -X utf8 proyeccion/brasil_transferencia.py
Grupos: nacional, UF, UF x capital/interior. Salida: proyeccion/brasil_transferencia.csv y una tabla en pantalla."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "..", "transferencias", "brasil_2026p_2026b")
K = 20000.0                 # votos de otros con que el cociente del grupo se encoge hacia el nacional
REAL = 51.79


def main():
    A, B, meta = pd.read_pickle(os.path.join(DIR, "pareadas.pkl"))
    d = pd.read_pickle(os.path.join(DIR, "detalle.pkl")).xs("2", level=0)
    t = pd.to_datetime(d.DT_PRIM_TOT_PARCIAL_HOR_TSE.reindex(A.index), format="%d/%m/%Y %H:%M:%S")
    ok = t.notna().to_numpy()
    A, B, t = A[ok], B[ok], t[ok]
    o = np.argsort(t.to_numpy(), kind="stable")
    a = A.to_numpy(float)[o]
    fl1, lu1, ot1 = a[:, 0], a[:, 1], a[:, 2:13].sum(1)          # 1.a vuelta: Flavio, Lula, demas (validos)
    b = B.to_numpy(float)[o]
    lu2, fl2 = b[:, 0], b[:, 1]
    uf = pd.factorize(A.index.get_level_values(0).to_numpy()[o])[0]
    cap = pd.read_csv(os.path.join(HERE, "..", "datos_oficiales", "brasil2026", "ibge", "municipios_brasileiros_tse.csv"),
                      dtype={"codigo_tse": str})
    caps = set(cap.loc[cap.capital == 1, "codigo_tse"].str.lstrip("0"))
    esc = np.isin(pd.Series(A.index.get_level_values(1).to_numpy()[o]).str.lstrip("0"), list(caps))
    grupos = {"nacional": np.zeros(len(a), int), "UF": uf, "UF x capital": pd.factorize(uf * 2 + esc)[0]}
    n = len(a)
    fr = np.unique(np.r_[np.geomspace(0.001, 0.05, 22), np.linspace(0.06, 1, 48)])
    rows = []
    for c in np.unique(np.round(fr * n).astype(int)):
        cnt = np.zeros(n, bool)
        cnt[:c] = True
        r = dict(fraccion=c / n, conteo=100 * lu2[cnt].sum() / (lu2[cnt] + fl2[cnt]).sum())
        for nom, g in grupos.items():
            ng = g.max() + 1
            so = np.bincount(g[cnt], ot1[cnt], ng)
            da = np.bincount(g[cnt], (lu2 - lu1)[cnt], ng)
            db = np.bincount(g[cnt], (fl2 - fl1)[cnt], ng)
            a0, b0 = da.sum() / so.sum(), db.sum() / so.sum()
            ag, bg = (da + K * a0) / (so + K), (db + K * b0) / (so + K)
            L = lu2[cnt].sum() + (lu1 + ag[g] * ot1)[~cnt].sum()
            F = fl2[cnt].sum() + (fl1 + bg[g] * ot1)[~cnt].sum()
            r[nom] = 100 * L / (L + F)
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "brasil_transferencia.csv"), index=False)
    for f in (0.003, 0.017, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 0.9):
        r = df.iloc[(df.fraccion - f).abs().argmin()]
        print("%.3f conteo %.2f  " % (r.fraccion, r.conteo) + "  ".join("%s %.2f" % (k, r[k]) for k in grupos))
    for lo, hi in ((0, .05), (.05, .3), (.3, 1)):
        s = df[(df.fraccion > lo) & (df.fraccion <= hi)]
        print("%.0f-%.0f %%: " % (100 * lo, 100 * hi) + "  ".join("%s %.2f" % (k, (s[k] - REAL).abs().mean()) for k in grupos))


if __name__ == "__main__":
    main()
