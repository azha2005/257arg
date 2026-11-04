"""Proyeccion de la Knesset durante el conteo, urna por urna, desde la eleccion anterior.

Origen de cada urna: la misma urna (localidad + numero entero de urna) en la eleccion anterior si existe, si no su
localidad. X = proporciones de origen sobre el padron (listas de mas del 1 %, otras, y «no voto» = padron - validos);
Y = lo mismo en destino. Con las urnas contadas:
  - matriz nacional de Goodman (casi sin encoger: hay miles de urnas);
  - una matriz por sector (arabe, haredi, derecha religiosa, localidades chicas, ciudades), encogida hacia la nacional
    con N0 urnas de peso; las urnas que faltan se proyectan con la matriz de su sector;
  - los votos de doble sobre (soldados, etc.: localidad 9999, se cuentan dias despues) = los de doble sobre de la
    eleccion anterior por la matriz nacional, escalados por el crecimiento del padron.
Banda: bootstrap de grupos de urnas (localidad y bloques de 20 urnas en las ciudades) con pesos de Poisson; cada
remuestra se pasa a bancas (umbral 3,25 %, Bader-Ofer, acuerdos de excedentes) y a bloques."""
import os
import numpy as np
import pandas as pd

import datos as dt

N0 = 150          # urnas de peso de la matriz nacional en cada sector
# padron de peso (~2-3 urnas) con que se encoge el residuo por localidad; 0 = sin residuo. Backtest orden geo, error
# medio por lista en bancas: 10 % 0,44 -> 0,37; 20 % 0,32 -> 0,23; 40 % 0,24 -> 0,13 (1-5 %: igual; azar: +0,03)
KR = float(os.environ.get("KR", 1500))
KV = float(os.environ.get("KV", 0))    # padron de peso del residuo de vecinas (requiere KR > 0); 0 = sin vecinas
MP = 3000        # votos de peso con que el cambio proporcional del ancla se encoge hacia 1
NP = 300         # urnas de peso del ancla (antecesores con cambio proporcional) en la matriz nacional; 0 = sin ancla
MIN_PCT = 0.01    # listas con menos del 1 % del pais van a «otras»
SECTORES = ["arabe", "haredi", "derecha religiosa", "chicas", "ciudades"]
RELIG = {"טב", "נ", "ב", "ט", "כף", "נץ", "ז"}


def _tabla(d, partidos, keep):
    V = pd.DataFrame({k: d[k] for k in keep})
    V["OTRAS"] = d[[p for p in partidos if p not in keep]].sum(1)
    V["NOVOTO"] = np.maximum(d["bzb"] - V.sum(1), 0)
    return V


def sectores(by_l, ko, o):
    """Sector de cada localidad por su composicion en la eleccion de origen (by_l = votos por localidad)."""
    lo = by_l.div(by_l.sum(1), axis=0)
    val = lo.drop(columns="NOVOTO").sum(1)
    arab = sum(lo[c] for c in ko if dt.BLOQUE[o].get(c) == "arabe") / val
    har = sum(lo[c] for c in ko if c in ("שס", "ג")) / val
    rel = sum(lo[c] for c in ko if c in RELIG) / val
    size = by_l.sum(1)
    return pd.Series(np.select([arab > .5, har > .45, rel > .25, size < 2500], [0, 1, 2, 3], 4),
                     index=by_l.index), size


def preparar(o, de):
    """Estado para proyectar la eleccion de con origen o."""
    do, po = dt.cargar(o)
    dd, pd_ = dt.cargar(de)
    ko = [p for p in po if do[p].sum() >= MIN_PCT * do.validos.sum()]
    kd = [p for p in pd_ if dd[p].sum() >= MIN_PCT * dd.validos.sum()]
    reg_o, reg_d = do[~do.doble].copy(), dd[~dd.doble].copy()
    Vo = _tabla(reg_o, po, ko)
    Vd = _tabla(reg_d, pd_, kd)
    reg_o["k"] = reg_o.kalpi.astype(int)
    reg_d["k"] = reg_d.kalpi.astype(int)
    # origen por urna (localidad + numero entero) o por localidad
    by_k = Vo.groupby([reg_o["loc"], reg_o["k"]]).sum()
    by_l = Vo.groupby(reg_o["loc"]).sum()
    key = list(zip(reg_d["loc"], reg_d["k"]))
    Xk = by_k.reindex(key).to_numpy(float)
    Xl = by_l.reindex(reg_d["loc"]).to_numpy(float)
    usa_k = ~np.isnan(Xk).any(1)
    Xa = np.where(usa_k[:, None], Xk, Xl)
    sin = np.isnan(Xa).any(1) | (Xa.sum(1) <= 0)          # localidad nueva: origen = el pais
    Xa[sin] = Vo.sum().to_numpy(float)
    X = Xa / Xa.sum(1, keepdims=True)
    w = np.maximum(reg_d.bzb.to_numpy(float), Vd.drop(columns="NOVOTO").sum(1).to_numpy(float))
    Vd["NOVOTO"] = w - Vd.drop(columns="NOVOTO").sum(1)
    ok = w > 0
    reg_d, Vd, X, w, usa_k = reg_d[ok], Vd[ok], X[ok], w[ok], usa_k[ok]
    Y = Vd.to_numpy(float) / w[:, None]
    sec_l, size = sectores(by_l, ko, o)
    sec = sec_l.reindex(reg_d["loc"]).fillna(4).to_numpy().astype(int)
    # grupos para el bootstrap: la localidad, y en las grandes bloques de 20 urnas
    grande = reg_d.groupby("loc")["loc"].transform("size").to_numpy() > 40
    gk = np.where(grande, reg_d["k"].to_numpy() // 20, 0)
    clus = pd.factorize(pd.Series(list(zip(reg_d["loc"], gk))))[0]
    # doble sobre
    dbo = _tabla(do[do.doble], po, ko).drop(columns="NOVOTO").sum().to_numpy(float)
    dbd = _tabla(dd[dd.doble], pd_, kd).drop(columns="NOVOTO").sum().to_numpy(float)
    crec = dd.loc[~dd.doble, "bzb"].sum() / do.loc[~do.doble, "bzb"].sum()
    reg_o_tot = Vo.drop(columns="NOVOTO").sum().to_numpy(float)       # votos comunes de origen por lista
    ocols, dcols = list(Vo.columns), list(Vd.columns)
    src = [[ocols.index(a) for a in dt.ANTECESORES.get((o, de), {}).get(c, [c]) if a in ocols] for c in dcols]
    return dict(o=o, de=de, X=X, Y=Y, w=w, sec=sec, clus=clus, loc=reg_d["loc"].to_numpy(), kalpi=reg_d["k"].to_numpy(),
                bzb_loc=size,
                arab=(sec == 0), ocols=ocols, dcols=dcols, src=src, dbo=dbo * crec, dbd=dbd, reg_o_tot=reg_o_tot, usa_k=usa_k.mean(),
                listas=[c for c in dcols if c not in ("OTRAS", "NOVOTO")])


def orden(st, kind, rng):
    """Orden de llegada simulado de las urnas comunes (el doble sobre llega al final, dias despues).
    azar: urnas al azar; geo: localidades chicas primero, ciudades grandes y localidades arabes despues (como suele
    pasar en Israel), con efecto de localidad y ruido de urna."""
    n = len(st["w"])
    if kind == "azar":
        return rng.permutation(n)
    lo = pd.factorize(st["loc"])[0]
    size = pd.Series(st["w"]).groupby(lo).transform("sum").to_numpy()
    z = (np.log(size) - np.log(size).mean()) / np.log(size).std()
    t = 0.5 * z + 0.6 * st["arab"] + rng.normal(0, 0.6, lo.max() + 1)[lo] + rng.normal(0, 0.5, n)
    return np.argsort(t)


DOBLE = "proporcional"     # o "matriz": la matriz nacional aplicada al doble sobre de origen
# Error del doble sobre en las remuestras: % de cada lista x exp(N(0, SD_DOBLE)) y total x exp(N(0, SD_DOBLE_TOT)).
# Calibrado con 2019-2022 (backtest): el cambio proporcional erra 0,55-0,90 puntos por lista en el doble sobre
# (hasta 3 en las listas que cambiaron mucho) y el crecimiento del padron erra el total en ~5 %.
SD_DOBLE, SD_DOBLE_TOT = 0.25, 0.06


def proyectar(st, cnt, rng, nboot=200, acuerdos=(), doble_contado=False):
    """Bancas por lista (nboot+1 x listas; la fila 0 es la proyeccion puntual) y votos proyectados (fila 0)."""
    X, Y, w, sec, clus = st["X"], st["Y"], st["w"], st["sec"], st["clus"]
    k, q = X.shape[1], Y.shape[1]
    c = np.zeros(len(w), bool)
    c[cnt] = True
    cl = clus[c]
    ucl, inv = np.unique(cl, return_inverse=True)
    Xw = X[c] * w[c, None]
    S = np.zeros((len(ucl), len(SECTORES), k, k))
    T = np.zeros((len(ucl), len(SECTORES), k, q))
    np.add.at(S, (inv, sec[c]), Xw[:, :, None] * X[c][:, None, :])
    np.add.at(T, (inv, sec[c]), Xw[:, :, None] * Y[c][:, None, :])
    Wb = np.ones((nboot + 1, len(ucl)))
    Wb[1:] = rng.poisson(1, (nboot, len(ucl)))
    Ss = np.einsum("bm,msij->bsij", Wb, S)
    Ts = np.einsum("bm,msij->bsij", Wb, T)
    Sn, Tn = Ss.sum(1), Ts.sum(1)
    eye = np.eye(k)
    trn = np.trace(Sn, axis1=1, axis2=2)[:, None, None]
    if NP > 0 and "src" in st:
        # ancla: cada columna de origen pasa a su sucesora (por partes iguales si son varias; sin sucesora, segun el
        # reparto de lo contado), escalada por el cambio observado (cambio proporcional). Con pocas urnas las filas
        # no identificadas (p. ej. las listas arabes cuando casi no hay urnas arabes) quedan en el ancla
        P0 = np.zeros((k, q))
        for j, sj in enumerate(st["src"]):
            for i in sj:
                P0[i, j] += 1
        nd = P0.sum(1, keepdims=True)
        obs = (Y[c] * w[c, None]).sum(0)
        P0 = np.where(nd > 0, P0 / np.maximum(nd, 1), np.r_[obs[:-1], 0] / max(obs[:-1].sum(), 1e-9))
        pred = Xw.sum(0) @ P0
        # el cambio se encoge hacia 1 cuando la lista tiene pocos votos contados (M votos de peso)
        r = np.clip((obs + MP) / (pred + MP), 0.05, 20)
        P = P0 * r[None, :]
        Lp = NP / max(c.sum(), 1) * trn / k
        G0 = np.linalg.solve(Sn + Lp * eye, Tn + Lp * P[None])
    else:
        G0 = np.linalg.solve(Sn + 1e-4 * trn / k * eye, Tn)
    nc = max(c.sum(), 1)
    L = (N0 / nc * trn / k)[:, None]
    Gs = np.linalg.solve(Ss + L * eye, Ts + L * G0[:, None])
    # sin recortar la matriz a >= 0 (con muchas columnas de origen el recorte infla a las listas chicas, que son las
    # del umbral); se recorta lo proyectado de cada sector
    U = np.zeros((len(SECTORES), k))
    np.add.at(U, sec[~c], X[~c] * w[~c, None])
    proy = np.einsum("si,bsij->bsj", U, Gs)
    if KR > 0:
        # residuo por localidad (lo local del metodo peruano): el desvio de las urnas contadas de cada localidad
        # respecto del modelo se suma a sus urnas sin contar, encogido por W/(W+KR) (W = padron contado ahi).
        # Sumado sobre localidades: R_s = a.A - (a.B) G_s con A = sum w*Y y B = sum w*X de lo contado por
        # localidad y a = padron sin contar x encogimiento / padron contado
        lc = pd.factorize(st["loc"])[0]
        nl = lc.max() + 1
        Wc = np.bincount(lc[c], weights=w[c], minlength=nl)
        Wu = np.bincount(lc[~c], weights=w[~c], minlength=nl)
        a = np.where(Wc > 0, Wu / np.maximum(Wc, 1e-9) * Wc / (Wc + KR), 0)
        A = np.zeros((nl, q))
        B = np.zeros((nl, k))
        np.add.at(A, lc[c], Y[c] * w[c, None])
        np.add.at(B, lc[c], X[c] * w[c, None])
        sl = np.zeros(nl, int)
        sl[lc] = sec
        for s_ in range(len(SECTORES)):
            m = sl == s_
            if a[m].sum() > 0:
                proy[:, s_] += (a[m] @ A[m])[None] - np.einsum("i,bij->bj", a[m] @ B[m], Gs[:, s_])
        if KV > 0:
            # vecinas (lo regional del metodo peruano): las localidades sin nada contado toman el desvio de las
            # localidades contadas de su concejo regional o subdistrito, del mismo sector, encogido por W/(W+KV)
            g = pd.factorize(pd.Series(dt.region(st["loc"])).astype(str) + "_" + pd.Series(sec).astype(str))[0]
            ng = g.max() + 1
            sg = np.zeros(ng, int)
            sg[g] = sec
            Wg = np.bincount(g[c], weights=w[c], minlength=ng)
            nada = ~c & (Wc[lc] == 0)
            Wn = np.bincount(g[nada], weights=w[nada], minlength=ng)
            ag = np.where(Wg > 0, Wn / np.maximum(Wg, 1e-9) * Wg / (Wg + KV), 0)
            Ag = np.zeros((ng, q))
            Bg = np.zeros((ng, k))
            np.add.at(Ag, g[c], Y[c] * w[c, None])
            np.add.at(Bg, g[c], X[c] * w[c, None])
            for s_ in range(len(SECTORES)):
                m = sg == s_
                if ag[m].sum() > 0:
                    proy[:, s_] += (ag[m] @ Ag[m])[None] - np.einsum("i,bij->bj", ag[m] @ Bg[m], Gs[:, s_])
    tot = (Y[c] * w[c, None]).sum(0)[None] + np.maximum(proy, 0).sum(1)
    # NOVOTO es la ultima columna (de origen y de destino); el doble sobre se suma a las demas
    if doble_contado:
        tot[:, :-1] += st["dbd"][None, :]
    elif DOBLE == "matriz":
        Gv = G0[:, :-1, :-1] / np.maximum(G0[:, :-1, :-1].sum(2, keepdims=True), 1e-9)
        dob = np.maximum(np.einsum("i,bij->bj", st["dbo"], Gv), 0)
        dob[1:] *= np.exp(rng.normal(0, SD_DOBLE, dob[1:].shape))
        dtot = st["dbo"].sum() * np.r_[1, np.exp(rng.normal(0, SD_DOBLE_TOT, len(dob) - 1))]
        tot[:, :-1] += dob / dob.sum(1, keepdims=True) * dtot[:, None]
    else:
        # cambio proporcional: % de la lista en el doble sobre de origen (su antecesor) x (su % proyectado en las
        # urnas comunes / el % del antecesor en las urnas comunes de origen); sin antecesor, su % proyectado
        reg = tot[:, :-1] / tot[:, :-1].sum(1, keepdims=True)
        ro = st["reg_o_tot"] / st["reg_o_tot"].sum()
        do_ = st["dbo"] / st["dbo"].sum()
        dob = np.empty_like(reg)
        for j, sj in enumerate(st["src"][:-1]):
            sj = [i for i in sj if i < len(ro)]
            dob[:, j] = do_[sj].sum() * reg[:, j] / ro[sj].sum() if sj and ro[sj].sum() > 0 else reg[:, j]
        dob[1:] *= np.exp(rng.normal(0, SD_DOBLE, dob[1:].shape))
        dtot = st["dbo"].sum() * np.r_[1, np.exp(rng.normal(0, SD_DOBLE_TOT, len(dob) - 1))]
        tot[:, :-1] += dob / dob.sum(1, keepdims=True) * dtot[:, None]
    listas = range(q - 1)
    seats = []
    for b in range(nboot + 1):
        v = {st["dcols"][i]: tot[b, i] for i in listas}
        s = dt.bancas(v, acuerdos)
        seats.append([s[x] for x in st["listas"]])
    return np.array(seats), tot[0]


def bloques(st, seats, bloque):
    """Bancas por bloque (bibi, oposicion, arabe) de cada fila de seats."""
    out = {b: np.zeros(len(seats), int) for b in ("bibi", "oposicion", "arabe")}
    for j, x in enumerate(st["listas"]):
        out[bloque.get(x, "oposicion")] += seats[:, j]
    return out


def resultado(bibi, opo):
    """Desenlace: bibi >= 61, oposicion judia >= 61, o ninguno (depende de las listas arabes)."""
    return np.where(bibi >= 61, "bibi", np.where(opo >= 61, "oposicion", "empate"))
