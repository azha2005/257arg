"""Inferencia ecologica RxC por minimos cuadrados penalizados (port del codigo R de Ernesto Calvo,
«Codigo Transferencias PASO-General para R-2019»).

X (n x R) y Y (n x C): proporciones de cada unidad sobre sus electores (filas que suman 1, con «no voto» incluido).
Modelo: Y_i ~ X_i B, con B (R x C) = softmax por fila de G (la ultima columna es la base, G[:, C-1] = 0).
Se minimiza sum_i ||(X_i B - Y_i)[:C-1]||^2 + const * ||G||^2, como call.difp sin covariable.
Diferencias con el R: gradiente analitico y arranque en cero (el R arranca en rnorm y sin gradiente).
La perdida es cuadratica en B: sum_i w_i ||(X_i B - Y_i)[:C-1]||^2 = sum_c (B_c' S B_c - 2 B_c' T_c) + q, con
S = X'WX (R x R) y T = X'WY; cada evaluacion cuesta O(R^2 C) en vez de O(n R C), sin cambiar el optimo."""
import numpy as np
from scipy.optimize import minimize


def fractions(g, R, C):
    G = np.hstack([g.reshape(R, C - 1), np.zeros((R, 1))])
    G -= G.max(axis=1, keepdims=True)
    E = np.exp(G)
    return E / E.sum(axis=1, keepdims=True)


def fit(X, Y, const=0.001, w=None, g0=None):
    """Devuelve B (R x C): fraccion de cada categoria de origen que va a cada categoria de destino.
    w: pesos por unidad (None = todas iguales, como el R).
    g0: centro de la penalizacion (None = cero, como el R); con g0 se encoge hacia otra matriz (p. ej. la nacional)."""
    X = np.asarray(X, float); Y = np.asarray(Y, float)
    w = np.ones(len(X)) if w is None else np.asarray(w, float)
    Xw = X * w[:, None]
    S, T = X.T @ Xw, Xw.T @ Y[:, :-1]                 # estadisticos suficientes (la ultima columna no entra)
    q = (w[:, None] * Y[:, :-1] ** 2).sum()
    return fit_ss(S, T, q, const, g0)


def fit_ss(S, T, q=0.0, const=0.001, g0=None):
    """Igual que fit, a partir de los estadisticos suficientes S = X'WX (R x R), T = X'WY sin la ultima columna
    (R x C-1) y q = sum w y^2 sin la ultima columna (q no cambia el optimo, pero si el criterio de parada)."""
    R, C = T.shape[0], T.shape[1] + 1
    g0 = np.zeros(R * (C - 1)) if g0 is None else np.asarray(g0, float)

    def f(g):
        B = fractions(g, R, C)
        SB = S @ B[:, :-1]
        loss = (B[:, :-1] * (SB - 2 * T)).sum() + q + const * ((g - g0) ** 2).sum()
        dB = np.zeros((R, C)); dB[:, :-1] = 2 * (SB - T)
        dG = B * (dB - (B * dB).sum(axis=1, keepdims=True))
        return loss, dG[:, :-1].ravel() + 2 * const * (g - g0)

    r = minimize(f, g0.copy(), jac=True, method="L-BFGS-B", options=dict(maxiter=5000, gtol=1e-10))
    return fractions(r.x, R, C)
