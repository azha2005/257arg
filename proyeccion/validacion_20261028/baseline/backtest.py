"""Prueba de proyeccion del escrutinio provisorio con pocas mesas, usando una eleccion ya terminada.
    python proyeccion/backtest.py 2023p 2023b          # 1.a vuelta -> balotaje 2023 (mesa a mesa)
    python proyeccion/backtest.py 2015p 2015b --reps 10
Se toman las mesas de la eleccion destino en un orden de llegada simulado, se corta al 0,2 %, 0,5 %, 1 %... de las
mesas y se proyecta el total con tres metodos:
  crudo  lo contado tal cual (lo que muestra el conteo).
  A      el de elecciones-peru.live (chubakueno/Elecciones2026): por seccion, lo contado se escala por la fraccion de
         mesas contadas; una seccion sin mesas copia los votos por mesa de las 2 secciones contadas mas cercanas
         (centroide de sus locales de votacion, peso 1/distancia). No usa la eleccion anterior.
  B      matriz de traspasos nacional (regresion de Goodman, sin restringir al simplex: con pocas mesas la restriccion
         sesga) ajustada con las mesas contadas sobre el resultado de la misma mesa en la eleccion origen; cada mesa
         que falta = su origen x la matriz.
  C      como B, pero una matriz por distrito encogida hacia la nacional (N0 mesas promedio de peso) y el residuo de
         las mesas contadas del mismo circuito y seccion sumado a las que faltan (encogido con K mesas); el total
         nacional se ajusta al de B (benchmarking), asi que C solo cambia el reparto entre distritos.
  D      como C, pero la matriz nacional depende del tamaño de la seccion y del circuito (log de electores): el cambio
         entre elecciones de las secciones chicas, que llegan primero, no se traslada tal cual a las grandes.
Con --circuito la eleccion origen se toma por circuito (transferencias/circ_<origen>.pkl): es el caso de una eleccion
de otro año, donde las mesas no se corresponden (p. ej. diputados 2025 -> 2027).
Ordenes de llegada (no hay hora de carga en los datos de la DINE, se simula):
  azar   todas las mesas al azar.
  geo    primero las secciones chicas y al final las grandes (conurbano, capitales), con ruido por distrito,
         seccion, circuito y mesa: el patron habitual de la noche electoral, sin calibrar con horas reales.
  geo_circ  igual, pero el retraso lo manda el tamaño del circuito y no el de la seccion.
  capital  en cada distrito la seccion mas grande (la capital o su equivalente) carga primero y el interior despues.
  sesgo  peor caso: entran primero las secciones donde mas saca el ganador del destino.
Metodos E: como D, pero una seccion sin mesas contadas toma la correccion de sus 3 vecinas contadas del mismo distrito
(«_sin_ajuste»: sin llevar el total nacional al de la matriz, porque ese ajuste anula lo que E aporta al total).
Salida en proyeccion/<origen>_<destino>/: corridas.csv (una fila por corrida y metodo) y RESUMEN.md."""
import os, sys, math, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = ["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]
FIXED = ["BLANCO", "NULO", "OTROS"]
CUTS = [0.002, 0.005, 0.01, 0.02, 0.05, 0.10, 0.25, 0.50]
N0, K = 200.0, 5.0
NB = 3                            # secciones vecinas contadas que presta su residuo (E)
N0S = 400.0                      # peso (en mesas promedio) que lleva a 0 los terminos por tamaño (D); con 20 extrapola
                                  # de mas cuando las secciones grandes todavia no tienen mesas (probado 27-oct-2026)
NP, MP = 300.0, 3000.0          # ancla (de Israel, 27-oct-2026): peso en mesas de la matriz de sucesores y votos con
                                  # que el cambio proporcional se encoge hacia 1
# Sucesora de cada fuerza de origen (sin la marca « (orig)»); por defecto la del mismo nombre. Sin sucesora, la fila
# del ancla es el reparto de lo contado.
SUCESORES = {("2019p", "2023p"): {"FRENTE DE TODOS": "UNION POR LA PATRIA", "CONSENSO FEDERAL": "HACEMOS POR NUESTRO PAIS",
                                  "UNITE POR LA LIBERTAD Y LA DIGNIDAD": "LA LIBERTAD AVANZA",
                                  "FRENTE NOS": "LA LIBERTAD AVANZA"},
             ("2015p", "2015b"): {"ALIANZA CAMBIEMOS": "CAMBIEMOS", "ALIANZA FRENTE PARA LA VICTORIA": "FRENTE PARA LA VICTORIA"}}
# Swing en log-razon respecto de otra eleccion del mismo tipo (idea de Mahlmeister, Brasil 2026): --swing 2015b usa el
# balotaje 2015 por circuito; cada finalista del destino con su par en esa eleccion.
SW = sys.argv[sys.argv.index("--swing") + 1] if "--swing" in sys.argv else None
SWING_MAP = {("2015b", "2023b"): {"UNION POR LA PATRIA": "FRENTE PARA LA VICTORIA", "LA LIBERTAD AVANZA": "CAMBIEMOS"}}
RESTRICT, CLIP = False, True      # matriz en el simplex (sesga con pocas mesas); mesas sin proporciones negativas
args = [a for a in sys.argv[1:] if not a.startswith("--")]
Y0, Y1 = args[:2] if len(args) >= 2 else ("2023p", "2023b")
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 20
CIRC = "--circuito" in sys.argv                                  # origen por circuito (elecciones de otro año)
ORDERS = ["azar", "geo", "geo_circ", "capital", "sesgo"]
if "--ordenes" in sys.argv:
    ORDERS = sys.argv[sys.argv.index("--ordenes") + 1].split(",")


# ---------- datos ----------
def load(arg, minshare):
    w = pd.read_pickle(os.path.join(HERE, "mesas_%s.pkl" % arg))
    parties = [c for c in w.columns if c not in KEY + ["e"] + FIXED]
    tot = w[parties].sum()
    keep = [p for p in parties if tot[p] >= minshare * tot.sum()]
    w["OTRAS LISTAS"] = w[[p for p in parties if p not in keep]].sum(axis=1)
    w["BLANCO/NULO"] = w[[c for c in FIXED if c in w.columns]].sum(axis=1)
    cols = keep + (["OTRAS LISTAS"] if len(keep) < len(parties) else []) + ["BLANCO/NULO"]
    return w[KEY + ["e"] + cols], keep, cols


def centroids():
    """Centroide de cada seccion (proyeccion/centroides.py; los locales de la DINE no traen coordenadas)."""
    c = pd.read_csv(os.path.join(HERE, "centroides_secciones.csv"), dtype={"distrito_id": str})
    return c.set_index(["distrito_id", "seccion_id"])[["lat", "lon"]]


def load_circ(arg, minshare):
    """Origen por circuito (transferencias/circ_<arg>.pkl), en proporciones sobre electores, con abstencion."""
    own = os.path.join(HERE, "circ_%s.pkl" % arg)                # bloques.py (diputados en bloques)
    v, elect = pd.read_pickle(own if os.path.exists(own) else os.path.join(HERE, "..", "transferencias", "circ_%s.pkl" % arg))
    t = v.votos_tipo.str.upper()
    v = v.assign(col=np.where(t.str.startswith("POSITIVO"), v.agrupacion_id, "BLANCO/NULO"))
    tot = v[v.col != "BLANCO/NULO"].groupby("col").v.sum()
    keep = tot[tot >= minshare * tot.sum()].index
    v["col"] = v.col.where(v.col.isin(keep) | (v.col == "BLANCO/NULO"), "OTRAS LISTAS")
    w = v.groupby(["distrito_id", "seccion_id", "circuito", "col"]).v.sum().unstack(fill_value=0)
    cols = list(keep) + (["OTRAS LISTAS"] if "OTRAS LISTAS" in w else []) + ["BLANCO/NULO"]
    w = w[cols].join(elect.rename("e_o"), how="inner")
    w["e_o"] = np.maximum(w.e_o, w[cols].sum(axis=1))
    p = w[cols].div(w.e_o, axis=0)
    p["ABSTENCION (orig)"] = 1 - p.sum(axis=1)
    p.columns = [c + " (orig)" if c != "ABSTENCION (orig)" else c for c in p.columns]
    return p.reset_index()


def prepare():
    d, dpart, dcols = load(Y1, 0.01)
    if CIRC:                                                       # eleccion anterior: solo el circuito de la mesa
        p = load_circ(Y0, 0.01)
        m = d.merge(p, on=["distrito_id", "seccion_id", "circuito"], how="inner")
        ocols = [c for c in p.columns if c.endswith("(orig)")]
        Xo = m[ocols].to_numpy(float)
    else:
        o, _, ocols = load(Y0, 0.01)
        m = d.merge(o.drop(columns="e"), on=KEY, how="inner", suffixes=("", " (orig)"))
        ocols = [c + " (orig)" if c in dcols else c for c in ocols]
        Vo = m[ocols].to_numpy(float)
    e = m.e.to_numpy(float)
    Vd = m[dcols].to_numpy(float)
    if CIRC:
        e = np.maximum(e, Vd.sum(1))
        X = Xo
        ocols = ocols[:-1]
    else:
        e = np.maximum(e, np.maximum(Vd.sum(1), Vo.sum(1)))      # mesas con mas votos que electores
        X = np.column_stack([Vo, e - Vo.sum(1)]) / e[:, None]
        Vo_ok = Vo.sum(1) > 0
    Y = np.column_stack([Vd, e - Vd.sum(1)]) / e[:, None]          # destino sobre electores, con abstencion
    ok = (m.e > 0) & (Vd.sum(1) > 0) & (True if CIRC else Vo_ok)
    info = dict(mesas_destino=len(d), mesas_cruzadas=len(m), mesas_usadas=int(ok.sum()),
                origen="circuito" if CIRC else "mesa")
    m, e, X, Y = m[ok].reset_index(drop=True), e[ok], X[ok], Y[ok]
    return m, e, X, Y, dpart, dcols + ["ABSTENCION"], ocols + ["ABSTENCION (orig)"], info


# ---------- metodos ----------
def simplex_rows(B):
    """Proyecta cada fila de B al simplex (no negativa, suma 1)."""
    n = B.shape[1]
    u = -np.sort(-B, axis=1)
    css = np.cumsum(u, axis=1) - 1
    idx = np.arange(1, n + 1)
    rho = (u - css / idx > 0).sum(axis=1)
    theta = css[np.arange(len(B)), rho - 1] / rho
    return np.maximum(B - theta[:, None], 0)


def fit_matrix(A, C, B0=None, iters=400):
    """min tr(B'AB) - 2 tr(B'C); con RESTRICT, filas de B en el simplex (gradiente proyectado)."""
    if not RESTRICT:
        return np.linalg.solve(A + 1e-9 * np.eye(len(A)), C)
    L = np.linalg.eigvalsh(A).max() + 1e-12
    B = simplex_rows(np.linalg.lstsq(A + 1e-9 * np.eye(len(A)), C, rcond=None)[0]) if B0 is None else B0.copy()
    for _ in range(iters):
        B = simplex_rows(B - (A @ B - C) / L)
    return B


def project_A(st, cnt):
    """Por seccion: escala por mesas; secciones vacias copian a las 2 contadas mas cercanas."""
    sec, nmes, Vd = st["sec"], st["sec_n"], st["Vd"]
    ns = len(nmes)
    cs = np.bincount(sec[cnt], minlength=ns)
    S = np.zeros((ns, Vd.shape[1]))
    np.add.at(S, sec[cnt], Vd[cnt])
    has = cs > 0
    P = np.zeros_like(S)
    P[has] = S[has] * (nmes[has] / cs[has])[:, None]
    per = np.zeros_like(S)
    per[has] = S[has] / cs[has][:, None]
    lat, lon, dist = st["lat"], st["lon"], st["sec_dist"]
    hidx = np.where(has)[0]
    for s in np.where(~has)[0]:
        if np.isfinite(lat[s]) and len(hidx):
            cand = hidx[np.isfinite(lat[hidx])]
            if len(cand):
                dd = haversine(lat[s], lon[s], lat[cand], lon[cand])
                j = np.argsort(dd)[:2]
                wgt = 1 / np.maximum(dd[j], 1e-3)
                P[s] = (per[cand[j]] * wgt[:, None]).sum(0) / wgt.sum() * nmes[s]
                continue
        same = hidx[dist[hidx] == dist[s]]
        src = same if len(same) else hidx
        P[s] = per[src].mean(0) * nmes[s]
    return P.sum(0), P, st["sec_dist"]


def haversine(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


def anchor(st, cnt):
    """Matriz de sucesores con cambio proporcional (la del modelo de Israel): cada fuerza de origen va entera a su
    sucesora, escalada por cuanto crecio la sucesora en lo contado respecto de lo que daria la matriz; ese cambio se
    encoge hacia 1 con MP votos. Filas sin sucesora: el reparto de lo contado."""
    X, Y, e = st["X"], st["Y"], st["e"]
    k, q = X.shape[1], Y.shape[1]
    suc = SUCESORES.get((Y0, Y1), {})
    P0 = np.zeros((k, q))
    obs = (Y[cnt] * e[cnt, None]).sum(0)
    for i, c in enumerate(st["ocols"]):
        name = c.replace(" (orig)", "")
        name = suc.get(name, name)
        if name in st["dcols"]:
            P0[i, st["dcols"].index(name)] = 1
        else:
            P0[i, :-1] = obs[:-1] / max(obs[:-1].sum(), 1e-9)
    pred = (X[cnt] * e[cnt, None]).sum(0) @ P0
    return P0 * np.clip((obs + MP) / (pred + MP), 0.05, 20)[None, :]


def fijas(st):
    """Lealtad fija (idea de Mahlmeister, Brasil 2026): {fila de origen: columna de destino} para las dos fuerzas mas
    votadas del destino que tienen antecesora (por SUCESORES o por el mismo nombre)."""
    if "fijas" not in st:
        suc = SUCESORES.get((Y0, Y1), {})
        top = sorted(st["pos"], key=lambda j: -st["Vd"][:, j].sum())[:2]
        st["fijas"] = {}
        for i, c in enumerate(st["ocols"]):
            name = c.replace(" (orig)", "")
            name = suc.get(name, name)
            if name in st["dcols"] and st["dcols"].index(name) in top:
                st["fijas"][i] = st["dcols"].index(name)
    return st["fijas"]


def solve_fijas(A, C, fx, extra=None):
    """min tr(B'AB) - 2 tr(B'C) con las filas fx fijas (1 en su columna); extra = matriz que se suma a A en las
    filas libres (encogimiento)."""
    k, q = C.shape
    fr = [i for i in range(k) if i not in fx]
    P = np.zeros((len(fx), q))
    for r, j in enumerate(fx.values()):
        P[r, j] = 1
    fxi = list(fx)
    B = np.zeros((k, q))
    B[fxi] = P
    B[fr] = np.linalg.solve(A[np.ix_(fr, fr)] + 1e-9 * np.eye(len(fr)), C[fr] - A[np.ix_(fr, fxi)] @ P)
    return B


def project_BC(st, cnt, hier, feat=None, vecinas=False, bench=True, ancla=False, leal=False, grupos=None):
    """B (hier=False) o C (hier=True). feat = nombre de una matriz de st con columnas extra (interacciones del origen
    con el tamaño de la seccion): la matriz nacional pasa a depender del tamaño, con esas columnas encogidas a 0 con
    el peso de N0S mesas promedio. Sin feat, C se lleva al total de B; con feat, al del modelo con tamaño.
    vecinas: una seccion sin mesas contadas toma el residuo medio de las NB secciones contadas mas cercanas de su
    distrito (peso 1/(distancia + 5 km)), encogido con K mesas: el cambio de la capital no se traslada al interior
    si hay algo contado cerca. bench=False no ajusta el total al del modelo nacional."""
    X, Y, e, dist = st["X"], st["Y"], st["e"], st["dist"]
    if feat is not None:
        X = np.column_stack([X, st[feat]])
    Xc, Yc, ec = X[cnt], Y[cnt], e[cnt]
    A = (Xc * ec[:, None]).T @ Xc
    C = (Xc * ec[:, None]).T @ Yc
    pen = np.zeros(len(A))
    pen[st["X"].shape[1]:] = N0S * np.diag(A)[st["X"].shape[1]:] / max(cnt.sum(), 1)
    if ancla:                                                    # encoge la parte del origen hacia la de sucesores
        k0 = st["X"].shape[1]
        lp = np.zeros(len(A))
        lp[:k0] = NP / max(cnt.sum(), 1) * np.trace(A[:k0, :k0]) / k0
        C = C.copy()
        C[:k0] += lp[:k0, None] * anchor(st, cnt)
        pen = pen + lp
    fx = fijas(st) if leal else None
    Bn = solve_fijas(A + np.diag(pen), C, fx) if leal else fit_matrix(A + np.diag(pen), C)
    pred = X @ Bn
    if hier:
        M = A / max(ec.sum(), 1) * np.mean(ec)                   # una mesa promedio de las contadas
        gr = dist if grupos is None else st[grupos]
        for d in range(gr.max() + 1):
            ind = cnt & (gr == d)
            rows = gr == d
            if ind.sum() == 0:
                continue
            Xd, Yd, ed = X[ind], Y[ind], e[ind]
            Ad = (Xd * ed[:, None]).T @ Xd + N0 * M
            Cd = (Xd * ed[:, None]).T @ Yd + N0 * M @ Bn
            pred[rows] = X[rows] @ (solve_fijas(Ad, Cd, fx) if leal else fit_matrix(Ad, Cd, Bn, iters=150))
        res = (Y - pred) * cnt[:, None]
        for g, prior_k in ((st["sec"], K), (st["circ"], K)):    # seccion y despues circuito, encogidos
            ng = g.max() + 1
            wsum = np.bincount(g, weights=e * cnt, minlength=ng)
            nsum = np.bincount(g, weights=cnt.astype(float), minlength=ng)
            rs = np.column_stack([np.bincount(g, weights=e * res[:, j], minlength=ng) for j in range(Y.shape[1])])
            shrink = nsum / (nsum + prior_k)
            raw = np.where(wsum[:, None] > 0, rs / np.maximum(wsum, 1)[:, None], 0)
            corr = raw * shrink[:, None]
            if vecinas and g is st["sec"]:
                for s in np.where(nsum == 0)[0]:
                    nb, dd = st["sec_nb"][s]
                    ok = nsum[nb] > 0
                    nb, dd = nb[ok][:NB], dd[ok][:NB]
                    if len(nb):
                        w = 1 / (dd + 5)
                        corr[s] = (raw[nb] * w[:, None]).sum(0) / w.sum() * (nsum[nb].sum() / (nsum[nb].sum() + prior_k))
            pred = pred + corr[g]
            res = (Y - pred) * cnt[:, None]
        if CLIP:
            pred = np.maximum(pred, 0)
            pred = pred / pred.sum(1, keepdims=True)
        # Benchmarking: las correcciones locales corrigen del todo las unidades con muchas mesas contadas y casi nada
        # las chicas; si unas y otras se desvian en sentidos opuestos el total se corre (hasta 0,6 puntos con 1 % de
        # mesas). El total nacional se lleva al de la matriz nacional, que es lineal e insesgado con mesas al azar.
        if bench:
            un = ~cnt
            delta = ((pred[un] - (X[un] @ Bn)) * e[un, None]).sum(0) / e[un].sum()
            pred[un] -= delta
    V = pred * e[:, None]
    V[cnt] = Y[cnt] * e[cnt, None]
    return V


def logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def project_S(st, cnt, Vbase):
    """Swing de log(a / b) de los dos finalistas respecto de la eleccion SW: delta = logit(destino) - logit(SW) en las
    mesas contadas, regresion ponderada por votos validos sobre [1, tamaño de la seccion], intercepto por distrito
    encogido con N0 mesas y residuo de circuito con K; los votos de a + b de cada mesa que falta salen de Vbase."""
    a, b = st["sw_ab"]
    Y, e, dist, circ = st["Y"], st["e"], st["dist"], st["circ"]
    v = e * (Y[:, a] + Y[:, b])
    ok = cnt & (v > 0)
    d = logit(Y[:, a] / np.maximum(Y[:, a] + Y[:, b], 1e-9)) - st["sw0"]
    Z = np.column_stack([np.ones(len(e)), st["z_sec"]])
    W = v[ok]
    A_ = (Z[ok] * W[:, None]).T @ Z[ok]
    beta = np.linalg.solve(A_ + np.diag([0, N0S * A_[1, 1] / max(ok.sum(), 1)]), (Z[ok] * W[:, None]).T @ d[ok])
    pred = Z @ beta
    for g, k0 in ((dist, N0), (circ, K)):
        ng = g.max() + 1
        r = np.bincount(g[ok], W * (d - pred)[ok], ng)
        wn = np.bincount(g[ok], W, ng)
        nn = np.bincount(g[ok], minlength=ng)
        pred = pred + (np.where(wn > 0, r / np.maximum(wn, 1e-9), 0) * nn / (nn + k0))[g]
    sh = 1 / (1 + np.exp(-(st["sw0"] + pred)))
    V = Vbase.copy()
    un = ~cnt
    val = V[un, a] + V[un, b]
    V[un, a], V[un, b] = val * sh[un], val * (1 - sh[un])
    return V


# ---------- simulacion ----------
def order(st, kind, rng):
    n = len(st["e"])
    if kind == "azar":
        return rng.permutation(n)
    sec, circ, dist = st["sec"], st["circ"], st["dist"]
    if kind == "geo":
        size = np.log(st["sec_n"])
        size = (size - size.mean()) / size.std()
        t = (rng.normal(0, .5, st["ndist"])[dist] + (0.8 * size + rng.normal(0, .5, len(size)))[sec]
             + rng.normal(0, .3, circ.max() + 1)[circ] + rng.normal(0, .6, n))
        return np.argsort(t)
    if kind == "geo_circ":                                       # como geo, pero manda el tamaño del circuito
        size = np.log(np.bincount(circ))
        size = (size - size.mean()) / size.std()
        t = (rng.normal(0, .5, st["ndist"])[dist] + rng.normal(0, .5, sec.max() + 1)[sec]
             + (0.8 * size + rng.normal(0, .3, len(size)))[circ] + rng.normal(0, .6, n))
        return np.argsort(t)
    if kind == "capital":                                        # la seccion mas grande de cada distrito primero
        t = (-1.5 * st["sec_cap"][sec] + rng.normal(0, .5, st["ndist"])[dist] + rng.normal(0, .5, sec.max() + 1)[sec]
             + rng.normal(0, .3, circ.max() + 1)[circ] + rng.normal(0, .6, n))
        return np.argsort(t)
    share = st["sec_win"]                                        # sesgo: secciones del ganador primero
    t = -(share - share.mean()) / share.std()
    return np.argsort(t[sec] + rng.normal(0, .3, n))


def summarize(V, st, vd):
    """% del ganador (sobre positivos), participacion y % del ganador por distrito; vd = distrito de cada fila de V.
    La participacion del metodo crudo sale de las mesas contadas."""
    pos = st["pos"]
    tot = V.sum(0)
    win = st["win"]
    nat = 100 * tot[win] / tot[pos].sum()
    turn = 100 * (1 - tot[-1] / tot.sum())
    D = np.zeros((st["ndist"], V.shape[1]))
    np.add.at(D, vd, V)
    with np.errstate(invalid="ignore", divide="ignore"):
        dpct = 100 * D[:, win] / D[:, pos].sum(1)
    dwin = D[:, pos].argmax(1)
    return nat, turn, dpct, dwin


def zscore(v, e):
    return (v - np.average(v, weights=e)) / np.sqrt(np.cov(v, aweights=e))


def state():
    m, e, X, Y, dpart, dcols, ocols, info = prepare()
    codes = lambda s: pd.factorize(s)[0]
    dist = codes(m.distrito_id)
    seckey = m.distrito_id + "|" + m.seccion_id.astype(str)
    sec = codes(seckey)
    circ = codes(seckey + "|" + m.circuito)
    ns = sec.max() + 1
    secs = pd.DataFrame({"distrito_id": m.distrito_id, "seccion_id": m.seccion_id, "sec": sec}).drop_duplicates("sec").sort_values("sec")
    cen = centroids()
    cc = secs.join(cen, on=["distrito_id", "seccion_id"])
    Vfull = Y * e[:, None]
    pos = [dcols.index(p) for p in dpart]
    win = pos[int(np.argmax(Vfull.sum(0)[pos]))]
    sw = np.zeros(ns)
    np.add.at(sw, sec, Vfull[:, win])
    sp = np.zeros(ns)
    np.add.at(sp, sec, Vfull[:, pos].sum(1))
    st = dict(X=X, Y=Y, e=e, Vd=Vfull, dist=dist, sec=sec, circ=circ, ndist=dist.max() + 1,
              sec_n=np.bincount(sec), sec_dist=np.bincount(sec, weights=dist, minlength=ns) // np.bincount(sec),
              lat=cc.lat.to_numpy(), lon=cc.lon.to_numpy(), sec_win=sw / np.maximum(sp, 1), pos=pos, win=win)
    st["sec_dist"] = st["sec_dist"].astype(int)
    st.update(distrito_id=m.distrito_id.to_numpy(), seccion_id=m.seccion_id.to_numpy(), ocols=ocols, dcols=dcols,
              circuito=m.circuito.to_numpy(), mesa_id=m.mesa_id.to_numpy())
    se = np.bincount(sec, weights=e)
    big = pd.Series(se).groupby(st["sec_dist"]).transform("max").to_numpy()
    st["sec_cap"] = (se == big).astype(float)                    # la seccion mas grande de su distrito
    st["dist_cap"] = dist * 2 + st["sec_cap"][sec].astype(int)   # distrito x (capital / resto)
    # E: secciones del mismo distrito ordenadas por distancia entre centroides
    st["sec_nb"] = []
    for s_ in range(ns):
        same = np.where((st["sec_dist"] == st["sec_dist"][s_]) & (np.arange(ns) != s_) & np.isfinite(st["lat"]))[0]
        if not np.isfinite(st["lat"][s_]) or len(same) == 0:
            st["sec_nb"].append((same[:0], np.zeros(0)))
            continue
        dd = haversine(st["lat"][s_], st["lon"][s_], st["lat"][same], st["lon"][same])
        o_ = np.argsort(dd)
        st["sec_nb"].append((same[o_], dd[o_]))
    # D: origen x log(electores de la seccion) y x log(electores del circuito). Probado el 27-oct-2026 contra solo la
    # seccion y contra cuatro estratos de seccion: con solo la seccion no mejora el orden «geo_circ», y los estratos
    # sin datos en las secciones grandes no extrapolan.
    z = zscore(np.log(np.bincount(sec, weights=e))[sec], e)
    zc = zscore(np.log(np.bincount(circ, weights=e))[circ], e)
    st["F_tam"] = np.column_stack([X * z[:, None], X * zc[:, None]])
    st["z_sec"] = z
    if SW:                                                       # logit de a / b en la eleccion SW, por circuito
        p = load_circ(SW, 0.0)
        mp = SWING_MAP[(SW, Y1)]
        fa, fb = [c for c in dcols if c in mp][:2]
        st["sw_ab"] = (dcols.index(fa), dcols.index(fb))
        ca, cb = mp[fa] + " (orig)", mp[fb] + " (orig)"
        p["sh"] = p[ca] / (p[ca] + p[cb]).replace(0, np.nan)
        key = pd.DataFrame({"distrito_id": m.distrito_id, "seccion_id": m.seccion_id, "circuito": m.circuito})
        sh = key.merge(p[["distrito_id", "seccion_id", "circuito", "sh"]], how="left").sh
        nsin = int(sh.isna().sum())
        for lv in (["distrito_id", "seccion_id"], ["distrito_id"]):   # circuitos renumerados: la seccion o el distrito
            sh = sh.fillna(key.merge(p.groupby(lv).sh.mean().reset_index(), on=lv, how="left").sh)
        st["sw0"] = logit(sh.fillna(p.sh.mean()).to_numpy())
        print("swing desde", SW, fa, "/", fb, "mesas sin su circuito en", SW, nsin, flush=True)
    print(info, "ganador", dcols[win], "secciones con centroide", int(np.isfinite(st["lat"]).sum()), "de", ns, flush=True)
    return st, info, dcols


def main():
    t0 = time.time()
    st, info, dcols = state()
    out = os.path.join(HERE, "%s_%s%s%s" % (Y0, Y1, "_circuito" if CIRC else "", "_ancla" if "--ancla" in sys.argv else "_leal" if "--leal" in sys.argv else "_swing" + SW if SW else ""))
    os.makedirs(out, exist_ok=True)
    e, dist, Vfull, win = st["e"], st["dist"], st["Vd"], st["win"]
    real_nat, real_turn, real_d, real_w = summarize(Vfull, st, dist)
    rows = []
    rng = np.random.default_rng(2027)
    n = len(e)
    for kind in ORDERS:
        for rep in range(REPS):
            o = order(st, kind, rng)
            for f in CUTS:
                cnt = np.zeros(n, bool)
                cnt[o[:max(1, int(round(f * n)))]] = True
                _, PA, _ = project_A(st, cnt)                  # A proyecta por seccion, no por mesa
                res = {"crudo": (Vfull * cnt[:, None], dist), "A": (PA, st["sec_dist"]),
                       "B": (project_BC(st, cnt, False), dist), "C": (project_BC(st, cnt, True), dist),
                       "D": (project_BC(st, cnt, True, "F_tam"), dist),
                       "E": (project_BC(st, cnt, True, "F_tam", vecinas=True), dist),
                       "E_sin_ajuste": (project_BC(st, cnt, True, "F_tam", vecinas=True, bench=False), dist),
                       "D_sin_ajuste": (project_BC(st, cnt, True, "F_tam", bench=False), dist)}
                if SW:
                    Vd_ = project_BC(st, cnt, True, "F_tam", bench=False)
                    Vs_ = project_S(st, cnt, Vd_)
                    wgt = min(max((f - 0.05) / 0.10, 0), 1)
                    res = {m_: res[m_] for m_ in ("crudo", "A", "D", "D_sin_ajuste")}
                    res.update({"S_swing": (Vs_, dist), "mezcla_5_15": ((1 - wgt) * Vd_ + wgt * Vs_, dist),
                                "promedio": ((Vd_ + Vs_) / 2, dist)})
                if "--leal" in sys.argv:
                    res = {m_: res[m_] for m_ in ("crudo", "A", "B", "C", "D", "D_sin_ajuste")}
                    res.update({"B_leal": (project_BC(st, cnt, False, leal=True), dist),
                                "C_leal": (project_BC(st, cnt, True, leal=True), dist),
                                "C_leal_cap": (project_BC(st, cnt, True, leal=True, grupos="dist_cap"), dist),
                                "C_leal_cap_sin_ajuste": (project_BC(st, cnt, True, leal=True, grupos="dist_cap",
                                                                     bench=False), dist)})
                if "--ancla" in sys.argv:
                    res = {m_: res[m_] for m_ in ("crudo", "A", "C", "D", "D_sin_ajuste")}
                    res.update({"C_ancla": (project_BC(st, cnt, True, ancla=True), dist),
                                "D_ancla": (project_BC(st, cnt, True, "F_tam", ancla=True), dist),
                                "D_sin_ajuste_ancla": (project_BC(st, cnt, True, "F_tam", bench=False, ancla=True), dist)})
                for meth, (V, vd) in res.items():
                    nat, turn, dpct, dwin = summarize(V, st, vd)
                    ok = np.isfinite(dpct)
                    rows.append(dict(orden=kind, rep=rep, corte=f, mesas=int(cnt.sum()), metodo=meth,
                                     err_nac=nat - real_nat, err_part=turn - real_turn,
                                     mae_dist=np.abs(dpct - real_d)[ok].mean() if ok.any() else np.nan,
                                     max_dist=np.abs(dpct - real_d)[ok].max() if ok.any() else np.nan,
                                     dist_acierto=int((dwin == real_w)[ok].sum()), dist_con_dato=int(ok.sum())))
            print(kind, rep, "%.0f s" % (time.time() - t0), flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out, "corridas.csv"), index=False)
    report(df, info, dcols[win], real_nat, real_turn, st["ndist"], out)


def report(df, info, winner, real_nat, real_turn, ndist, out):
    g = df.groupby(["orden", "corte", "metodo"])
    t = pd.DataFrame({"mesas": g.mesas.first(),
                      "err_med": g.err_nac.mean(), "err_abs": g.err_nac.apply(lambda s: s.abs().mean()),
                      "err_p90": g.err_nac.apply(lambda s: s.abs().quantile(.9)),
                      "mae_dist": g.mae_dist.mean(), "acierto_dist": g.dist_acierto.mean()}).reset_index()
    L = ["# Proyeccion del provisorio con pocas mesas: %s -> %s" % (Y0, Y1), "",
         "Generado por `python proyeccion/backtest.py %s %s` (%d repeticiones por orden). Mesas: %s." % (Y0, Y1, df.rep.max() + 1, info),
         "Cifra que se proyecta: %% de **%s** sobre votos positivos (real %.2f %%) y la participacion (real %.2f %%)." % (winner, real_nat, real_turn),
         "", "Errores en puntos porcentuales. `err_med` = sesgo medio, `err_abs` = error absoluto medio, `err_p90` = el 90 %% de las corridas "
         "queda por debajo; `mae_dist` = error medio del %% del ganador por distrito; `acierto_dist` = distritos con el ganador correcto (de %d)." % ndist, ""]
    for kind in ORDERS:
        L += ["## Orden «%s»" % kind, "", "| % mesas | mesas | metodo | err_med | err_abs | err_p90 | mae_dist | acierto_dist |", "|---|---|---|---|---|---|---|---|"]
        for _, r in t[t.orden == kind].iterrows():
            L.append("| %.1f | %d | %s | %+.2f | %.2f | %.2f | %.2f | %.1f |" % (100 * r.corte, r.mesas, r.metodo, r.err_med, r.err_abs, r.err_p90, r.mae_dist, r.acierto_dist))
        L.append("")
    open(os.path.join(out, "RESUMEN.md"), "w", encoding="utf-8").write("\n".join(L))
    print("RESUMEN en", out)


if __name__ == "__main__":
    main()
