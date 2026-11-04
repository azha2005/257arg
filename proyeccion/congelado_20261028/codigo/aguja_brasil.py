"""Aguja al estilo del New York Times (2020) para el balotaje de Brasil 2026 (Lula - Flavio Bolsonaro), repetida con el
orden REAL de llegada: el TSE publica la hora de la primera totalizacion parcial de cada seccion
(DT_PRIM_TOT_PARCIAL_HOR_TSE, hora de Brasilia).
    python -X utf8 proyeccion/aguja_brasil.py
Necesita transferencias/brasil_2026p_2026b/pareadas.pkl y detalle.pkl (brasil2026_datos.py --preparar y
brasil2026_estimar.py --preparar).
Modelo en cada paso: Goodman con las secciones ya contadas (origen = 1.a vuelta de la misma seccion: Flavio, Lula,
Cury, Renan, Caiado, otros, blanco/nulo, no voto; destino = Lula, Flavio, blanco/nulo, no voto), una matriz por UF
encogida hacia la nacional (N0 secciones de peso); lo que falta se proyecta con la matriz de su UF (o la nacional si
la UF no tiene nada contado). Banda: bootstrap de municipios (pesos de Poisson) mas el error sistematico por el orden
de llegada de aguja.py (SIS de mesa, calibrado en Argentina).
Salida: proyeccion/img/aguja_brasil_2026.png y proyeccion/aguja_brasil_2026.csv."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aguja_dibujo as ad

DIR = os.path.join(HERE, "..", "transferencias", "brasil_2026p_2026b")
N0 = 200                   # secciones de peso de la matriz nacional en cada UF
NBOOT = 300
SIS = (0.523, 0.203)       # aguja.py, "mesa"
LULA, FLAVIO = "#c4161c", "#1b3a8c"
# Variante (28-oct-2026, idea de la proyeccion de Rodrigo Mahlmeister): MODO=leal fija la lealtad de los dos finalistas
# (Flavio -> Flavio y Lula -> Lula con coeficiente 1) y estima solo las filas de los demas; MODO=leal_cap ademas separa
# capital e interior de cada UF. Con MODO distinto de goodman solo escribe aguja_brasil_2026_<MODO>.csv.
MODO = os.environ.get("MODO", "goodman")
FIJAS = {0: 1, 1: 0}       # fila de origen (Flavio, Lula) -> columna de destino (Flavio, Lula)


def resolver(S, T, L, G0):
    """(S + L I) G = T + L G0 por grupo; con MODO leal*, las filas FIJAS valen 1 en su columna y se resuelven las
    demas: (S_FF + L) G_F = T_F - S_F,fijas P + L G0_F."""
    k, q = S.shape[-2], T.shape[-1]
    eye = np.eye(k)
    if MODO == "goodman":
        return np.linalg.solve(S + L * eye, T + L * G0)
    fr = [i for i in range(k) if i not in FIJAS]
    fx = list(FIJAS)
    P = np.zeros((len(fx), q))
    for r, (i, j) in enumerate(FIJAS.items()):
        P[r, j] = 1
    Lf = L[..., :len(fr), :len(fr)] if np.ndim(L) else L
    Gf = np.linalg.solve(S[..., fr, :][..., :, fr] + Lf * np.eye(len(fr)),
                         T[..., fr, :] - S[..., fr, :][..., :, fx] @ P + Lf * np.broadcast_to(G0, T.shape)[..., fr, :])
    G = np.zeros(np.broadcast_shapes(S.shape[:-2], T.shape[:-2]) + (k, q))
    G[..., fr, :] = Gf
    G[..., fx, :] = P
    return G


def main():
    A, B, meta = pd.read_pickle(os.path.join(DIR, "pareadas.pkl"))
    d = pd.read_pickle(os.path.join(DIR, "detalle.pkl")).xs("2", level=0)
    t = pd.to_datetime(d.DT_PRIM_TOT_PARCIAL_HOR_TSE.reindex(A.index), format="%d/%m/%Y %H:%M:%S")
    ok = t.notna().to_numpy()
    print("secciones sin hora:", int((~ok).sum()), flush=True)
    A, B, meta, t = A[ok], B[ok], meta[ok], t[ok]
    o = np.argsort(t.to_numpy(), kind="stable")
    a = A.to_numpy(float)[o]
    a = np.c_[a[:, :5], a[:, 5:13].sum(1), a[:, 13:15]]        # Flavio, Lula, Cury, Renan, Caiado, otros, BN, no voto
    y = B.to_numpy(float)[o]                                     # Lula, Flavio, BN, no voto
    t = t.to_numpy()[o]
    w = y.sum(1)
    X, Y = a / a.sum(1, keepdims=True), y / w[:, None]
    uf = pd.factorize(A.index.get_level_values(0).to_numpy()[o])[0]
    if MODO == "leal_cap":                                       # grupo = UF x (capital / interior)
        cap = pd.read_csv(os.path.join(HERE, "..", "datos_oficiales", "brasil2026", "ibge", "municipios_brasileiros_tse.csv"),
                          dtype={"codigo_tse": str})
        cap = set(cap.loc[cap.capital == 1, "codigo_tse"].str.lstrip("0"))
        esc = np.isin(A.index.get_level_values(1).to_numpy()[o].astype(str), [c.zfill(5) for c in cap] + list(cap))
        uf = pd.factorize(uf * 2 + esc)[0]
    mun = pd.factorize(meta.municipio.to_numpy()[o])[0]
    nuf, nmun, k, q = uf.max() + 1, mun.max() + 1, X.shape[1], Y.shape[1]
    mun_uf = np.zeros(nmun, int)
    mun_uf[mun] = uf
    Xw = X * w[:, None]
    n = len(w)
    real = 100 * (y[:, 1].sum() - y[:, 0].sum()) / (y[:, 0].sum() + y[:, 1].sum())
    print("real: Flavio - Lula = %+.2f" % real, flush=True)
    # estadisticos por municipio, acumulados a medida que llegan las secciones
    Sm = np.zeros((nmun, k, k))
    Tm = np.zeros((nmun, k, q))
    Ufalta = np.zeros((nuf, k))
    np.add.at(Ufalta, uf, Xw)
    cont = np.zeros(q)
    fr = np.unique(np.r_[np.geomspace(0.001, 0.05, 22), np.linspace(0.06, 1, 48)])
    cortes = np.unique(np.round(fr * n).astype(int))
    rng = np.random.default_rng(26)
    rows, prev = [], 0
    for c in cortes:
        s = slice(prev, c)
        np.add.at(Sm, mun[s], Xw[s][:, :, None] * X[s][:, None, :])
        np.add.at(Tm, mun[s], Xw[s][:, :, None] * Y[s][:, None, :])
        np.add.at(Ufalta, uf[s], -Xw[s])
        cont += y[s].sum(0)
        prev = c
        f = c / n
        vis = np.unique(mun[:c])
        Wb = np.ones((NBOOT + 1, len(vis)))
        Wb[1:] = rng.poisson(1, (NBOOT, len(vis)))
        Su = np.zeros((NBOOT + 1, nuf, k, k))
        Tu = np.zeros((NBOOT + 1, nuf, k, q))
        for u in np.unique(mun_uf[vis]):
            m = mun_uf[vis] == u
            Su[:, u] = np.einsum("bm,mij->bij", Wb[:, m], Sm[vis[m]])
            Tu[:, u] = np.einsum("bm,mij->bij", Wb[:, m], Tm[vis[m]])
        Sn, Tn = Su.sum(1), Tu.sum(1)
        wb = np.einsum("bm,m->b", Wb, np.bincount(mun[:c], w[:c], nmun)[vis])
        eye = np.eye(k)
        G0 = resolver(Sn, Tn, 1e-6 * np.trace(Sn, axis1=1, axis2=2)[:, None, None], np.zeros((k, q)))
        L = N0 * (np.trace(Sn, axis1=1, axis2=2) / wb / k * w[:c].mean())[:, None, None, None]
        Gu = resolver(Su, Tu, L, G0[:, None])
        tiene = Su[0].trace(axis1=1, axis2=2) > 0
        G = np.where(tiene[None, :, None, None], Gu, G0[:, None])
        tot = cont[None] + np.einsum("ui,buij->bj", Ufalta, np.maximum(G, 0))
        mg = 100 * (tot[:, 1] - tot[:, 0]) / (tot[:, 0] + tot[:, 1])
        sis = SIS[0] * (1 - f) * f ** -SIS[1] if f < 1 else 0
        mb = mg[0] + (mg[1:] - mg[1:].mean()) + rng.normal(0, sis / 1.96, NBOOT)
        esc = 100 * (cont[1] - cont[0]) / (cont[0] + cont[1])
        rows.append(dict(hora=t[c - 1], fraccion=f, secciones=c, margen=mg[0], p25=np.percentile(mb, 25),
                         p75=np.percentile(mb, 75), p2=np.percentile(mb, 2.5), p97=np.percentile(mb, 97.5),
                         prob=(mb > 0).mean(), escrutado=esc,
                         lula=100 * tot[0, 0] / (tot[0, 0] + tot[0, 1])))
        r = rows[-1]
        print("%s %5.1f %% escrutado %+.2f proyeccion %+.2f [%+.2f, %+.2f] P(Lula) %.2f" % (
            pd.Timestamp(r["hora"]).strftime("%H:%M"), 100 * f, esc, r["margen"], r["p2"], r["p97"], 1 - r["prob"]),
            flush=True)
    df = pd.DataFrame(rows)
    if MODO != "goodman":
        df.to_csv(os.path.join(HERE, "aguja_brasil_2026_%s.csv" % MODO), index=False)
        return
    df.to_csv(os.path.join(HERE, "aguja_brasil_2026.csv"), index=False)
    # momento de la foto: cuando el conteo daba a Flavio su mayor ventaja (si la aguja ya daba a Lula con >= 95 %)
    cand = df[(df.escrutado > 0) & (df.prob <= 0.05)]
    r = cand.loc[cand.escrutado.idxmax()] if len(cand) else df.iloc[(df.fraccion - 0.1).abs().argmin()]
    temprano = df[pd.to_datetime(df.hora) < pd.Timestamp(df.hora.iloc[-1]).normalize() + pd.Timedelta(hours=19)]
    df = df[~df.index.isin(temprano.index) & (df.fraccion < 1)]   # sin las secciones de las 17 h ni la cola hasta las 23 h
    hh = pd.Timestamp(r.hora).strftime("%H:%M")
    ad.dibujar(
        os.path.join(HERE, "img", "aguja_brasil_2026.png"),
        titulo="Brasil 2026, segundo turno: la aguja a las %s" % hh,
        subtitulo="Con el %s %% de las secciones totalizadas el conteo daba adelante a Flávio Bolsonaro (%s +%.1f); "
                  "la proyección desde la 1.ª vuelta de esas mismas secciones ya daba ganador a Lula. Orden real de "
                  "llegada del TSE." % (_coma(100 * r.fraccion), "Flávio", r.escrutado),
        izq=("Lula (PT)", "Lula", LULA), der=("Flávio Bolsonaro (PL)", "Flávio", FLAVIO),
        margen=r.margen, p25=r.p25, p75=r.p75, p2=r.p2, p97=r.p97, prob=r.prob, escala=10,
        serie=dict(x=list(pd.to_datetime(df.hora)), margen=list(df.margen), p25=list(df.p25), p75=list(df.p75),
                   p2=list(df.p2), p97=list(df.p97), crudo=list(df.escrutado),
                   xlabel="hora de Brasília (totalización parcial de cada sección en el TSE)",
                   crudo_lab="conteo parcial", tiempo=True),
        real=real, real_lab="resultado final: Lula +%s" % _coma(abs(real)),
        fuerzas=[("Lula", r.lula), ("Flávio", 100 - r.lula)], fuerzas_lab="votos válidos",
        momento=pd.Timestamp(r.hora),
        pie="Proyección: Goodman por UF (encogido hacia la matriz nacional) con las secciones ya totalizadas, aplicado "
            "a la 1.ª vuelta de las que faltan. Banda: 50 %% y 95 %%, bootstrap de municipios más un error por el orden "
            "de llegada. Antes de las 19 h solo había %s %% contado. %s secciones (99,6 %% del "
            "padrón). Repetición retrospectiva, no una aguja publicada." % (
                _coma(100 * temprano.fraccion.max()), format(n, ",").replace(",", ".")))


def _coma(v):
    return ("%.1f" % v).replace(".", ",")


if __name__ == "__main__":
    main()
