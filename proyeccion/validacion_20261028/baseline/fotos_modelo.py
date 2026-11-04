"""Modelo para proyectar el total nacional con unas pocas actas sueltas (fotos) y la eleccion anterior.
Lo usan fotos25.py (las fotos de 2025), fotos_sim.py (calibracion con elecciones viejas) y proyectar_fotos.py (la
noche de la eleccion).

Notacion: X = proporciones de origen de la mesa sobre electores (incluida la abstencion; con el origen por circuito,
las del circuito de la mesa), Y = proporciones de destino sobre electores (NaN donde la foto no da esa fuerza),
e = electores de la mesa, d = distrito (codigo 0..nd-1). natd = suma de X x e por distrito sobre todas las mesas del
pais, ed = electores por distrito. src[j] = columnas de origen que corresponden a la columna de destino j (vacio si
no hay antecesor)."""
import numpy as np


def swing(X, Y, e, d, natd, ed, src, kd=np.inf, ratio=()):
    """Swing por distrito: en cada distrito con fotos, el cambio de sus fotos (destino menos su antecesor) encogido
    con kd mesas hacia el cambio de todas las fotos; en los distritos sin fotos, el de todas. kd = inf es el swing
    uniforme. ratio = columnas de destino con cambio proporcional (destino / antecesor) en vez de aditivo.
    Devuelve el total proyectado de cada columna de destino (en votos)."""
    nd = len(ed)
    tot = np.zeros(Y.shape[1])
    for j in range(Y.shape[1]):
        k = ~np.isnan(Y[:, j])
        if not k.any():
            tot[j] = np.nan
            continue
        y, w, dj = Y[k, j], e[k], d[k]
        o = X[k][:, src[j]].sum(1)
        n = np.bincount(dj, minlength=nd)
        sh = n / (n + kd) if np.isfinite(kd) else np.zeros(nd)
        if j in ratio and len(src[j]):
            r0 = (y * w).sum() / max((o * w).sum(), 1e-9)
            yd, od = np.bincount(dj, y * w, nd), np.bincount(dj, o * w, nd)
            r = sh * np.where(od > 0, yd / np.maximum(od, 1e-9), r0) + (1 - sh) * r0
            tot[j] = (natd[:, src[j]].sum(1) * r).sum()
        else:
            s0 = np.average(y - o, weights=w)
            sd = np.bincount(dj, (y - o) * w, nd) / np.maximum(np.bincount(dj, w, nd), 1e-9)
            tot[j] = natd[:, src[j]].sum() + ((sh * sd + (1 - sh) * s0) * ed).sum()
    return tot


def goodman(X, Y, e, nat, src, lam, prop=False, mp=3000.0, natd=None):
    """Regresion de Goodman por columna de destino (con las mesas donde se conoce), encogida hacia el swing
    uniforme con lam x la traza media de X'WX: lam = inf es el swing uniforme, lam = 0 Goodman sin encoger. El
    swing como matriz: coeficiente 1 en las columnas antecesoras mas un corrimiento comun (las filas de X suman 1).
    nat = suma de X x e de todo el pais.
    prop: el ancla es el cambio proporcional (el de Israel, 27-oct-2026): coeficiente r en las antecesoras, con
    r = (votos + mp) / (votos del antecesor + mp) en las actas, sin corrimiento comun. lam = "np" usa el peso de
    Israel: 300 mesas (lam = 300 / actas).
    natd (distritos x origen): devuelve los totales por distrito (distritos x destino) en vez del nacional."""
    tot = np.zeros(Y.shape[1]) if natd is None else np.full((len(natd), Y.shape[1]), np.nan)
    for j in range(Y.shape[1]):
        k = ~np.isnan(Y[:, j])
        if not k.any():
            if natd is None:
                tot[j] = np.nan
            continue
        x, y, w = X[k], Y[k, j], e[k]
        g0 = np.zeros(X.shape[1])
        if prop and len(src[j]):
            o = x[:, src[j]].sum(1)
            g0[src[j]] = ((y * w).sum() + mp) / ((o * w).sum() + mp)
        else:
            g0[src[j]] = 1
            g0 += np.average(y - x @ g0, weights=w)
        lam_j = 300.0 / k.sum() if lam == "np" else lam
        if np.isinf(lam_j):
            g = g0
        else:
            A = (x * w[:, None]).T @ x
            L = lam_j * np.trace(A) / len(A)
            g = np.linalg.solve(A + (L + 1e-9) * np.eye(len(A)), (x * w[:, None]).T @ y + L * g0)
        if natd is None:
            tot[j] = nat @ g
        else:
            tot[:, j] = natd @ g
    return tot


def project(spec, X, Y, e, d, natd, ed, src):
    """spec = ("swing", kd), ("goodman", lam) o ("goodman_prop", lam)."""
    if spec[0] == "swing":
        return swing(X, Y, e, d, natd, ed, src, spec[1], spec[2] if len(spec) > 2 else ())
    return goodman(X, Y, e, natd.sum(0), src, spec[1], prop=spec[0] == "goodman_prop")


def pct(tot, pos):
    """% de cada fuerza positiva (indices pos) sobre la suma de las fuerzas positivas."""
    p = np.maximum(tot[pos], 0)
    return 100 * p / p.sum()


def bootstrap(fn, clus, nboot, rng):
    """Remuestra los grupos (clus = codigo de grupo de cada foto, p. ej. el circuito o el local) y devuelve las
    proyecciones fn(indices) de cada remuestra."""
    groups = [np.where(clus == c)[0] for c in np.unique(clus)]
    out = []
    for _ in range(nboot):
        pick = rng.integers(len(groups), size=len(groups))
        out.append(fn(np.concatenate([groups[i] for i in pick])))
    return np.array(out)


# Regiones para postestratificar (codigos de distrito de la DINE). AMBA = Capital + los 24 partidos del conurbano.
GBA = [3, 4, 11, 36, 38, 52, 53, 61, 62, 70, 77, 79, 80, 92, 105, 106, 113, 118, 122, 129, 130, 132, 133, 134]
REGION_DIST = {"01": "AMBA", "02": "Buenos Aires interior", "04": "Centro", "21": "Centro", "08": "Centro",
               "13": "Cuyo", "18": "Cuyo", "19": "Cuyo", "10": "NOA", "17": "NOA", "23": "NOA", "03": "NOA", "12": "NOA",
               "22": "NOA", "05": "NEA", "06": "NEA", "14": "NEA", "09": "NEA", "11": "Patagonia", "15": "Patagonia",
               "16": "Patagonia", "07": "Patagonia", "20": "Patagonia", "24": "Patagonia"}


def region(distrito_id, seccion_id, kind="region"):
    """Estrato de cada mesa: kind = "region" (ocho regiones) o "amba" (AMBA / resto del pais)."""
    distrito_id = np.asarray(distrito_id).astype(str)
    seccion_id = np.asarray(seccion_id).astype(int)
    amba = (distrito_id == "01") | ((distrito_id == "02") & np.isin(seccion_id, GBA))
    if kind == "amba":
        return np.where(amba, "AMBA", "resto")
    return np.where(amba, "AMBA", np.array([REGION_DIST.get(d, "?") for d in distrito_id]))


def poststrat(e, s, share, cap=5.0):
    """Pesos de las fotos para que cada estrato pese lo que pesa en el padron: e x (share del estrato / share en
    las fotos), con tope cap. Los estratos sin fotos no se pueden compensar: su peso se reparte entre los demas."""
    s = np.asarray(s)
    out = e.astype(float).copy()
    have = [k for k in np.unique(s) if k in share]
    tot_sh = sum(share[k] for k in have)
    for k in have:
        m = s == k
        w = (share[k] / tot_sh) / (e[m].sum() / e.sum())
        out[m] *= min(w, cap)
    return out
