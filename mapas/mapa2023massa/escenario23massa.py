"""Escenario hipotetico: primera vuelta presidencial 2023 con Massa 40,21 % (imagen del usuario, zocalo de C5N).

Metodo (simple y editable):
1. Punto de partida: generales 2023 por departamento (Massa, Milei, Bullrich, Schiaretti, Bregman; votos positivos,
   escrutinio provisorio DINE, ya emparejados a las unidades del mapa en mapa2027/base27.pkl).
2. Cada departamento conserva sus votos positivos y su posicion relativa: se buscan cinco multiplicadores nacionales
   (uno por candidato, IPF) para que el total nacional de cada uno sea EXACTAMENTE el de la imagen. Equivale a un
   corrimiento logistico multinomial comun.
3. Con multiplicadores uniformes Massa revierte la PASO en 15 provincias; el zocalo dice 9. En las seis donde su
   ventaja era mas chica (HOLD: 0,8 a 3,7 puntos) la celda de Massa lleva un factor provincial comun HOLD_F, el mas
   cercano a 1 que lo deja segundo en las seis (ver buscar_hold()). El IPF reparte el resto en el pais.
   (Probado y descartado: concentrar la suba donde Massa ya era fuerte, (% Massa / % nacional)^gamma; para llegar a 9
   hace falta gamma = 2,48 y Massa caeria de 13 % a 2 % en Cordoba mientras sube en el pais.)
4. Votos por departamento redondeados por resto mayor en cada candidato: los totales nacionales cierran al voto
   (los positivos de cada departamento pueden moverse uno o dos votos respecto de 2023).
"""
import os, pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CANDS = ["MAS", "MIL", "BUL", "SCH", "BRE"]
KEY = {"MAS": "UNION POR LA PATRIA", "MIL": "LA LIBERTAD AVANZA", "BUL": "JUNTOS POR EL CAMBIO",
       "SCH": "HACEMOS POR NUESTRO PAIS", "BRE": "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD"}
PCT = dict(MAS=40.21, MIL=28.13, BUL=21.27, SCH=5.31, BRE=5.08)     # imagen: suman 100,00
HOLD = ["Jujuy", "Neuquén", "Santa Fe", "Misiones", "Chubut", "Salta"]
HOLD_F = None                                                        # None: se busca con buscar_hold()
MARGEN = 1.0                                                         # puntos por los que Massa queda segundo, como minimo
# Ganador de la PASO 2023 por provincia (agrupacion; mapa2023paso): LLA 16, UxP 5, JxC 3
PASO_WIN = {"Capital Federal": "BUL", "Corrientes": "BUL", "Entre Ríos": "BUL", "Buenos Aires": "MAS", "Catamarca": "MAS",
            "Chaco": "MAS", "Formosa": "MAS", "Santiago del Estero": "MAS"}


def load():
    B = pickle.load(open(os.path.join(HERE, "..", "mapa2027", "base27.pkl"), "rb"))
    U = B["U"]
    ok = [i for i, u in enumerate(U) if u[1] != "Islas Malvinas"]
    V = np.array([[B["g23"][i]["P"].get(KEY[c], 0) for c in CANDS] for i in ok], float)
    return U, ok, V, B["g23"]


def largest_remainder(x, total):
    f = np.floor(x).astype(np.int64)
    r = int(round(total - f.sum()))
    idx = np.argsort(-(x - f))[:r]
    f[idx] += 1
    return f


def run(verbose=True, hold_f=None):
    if hold_f is None:
        hold_f = HOLD_F if HOLD_F is not None else buscar_hold()
    U, ok, V0, g23 = load()
    prov = [u[0] for u in U]
    pos = V0.sum(1)
    S = int(pos.sum())
    T = largest_remainder(np.array([PCT[c] for c in CANDS]) / 100 * S, S).astype(float)
    M = np.ones_like(V0)
    M[:, 0] = [hold_f if prov[i] in HOLD else 1.0 for i in ok]
    X = V0 * M
    for _ in range(2000):
        X *= (T / X.sum(0))[None, :]
        X *= (pos / X.sum(1))[:, None]
    R = np.zeros_like(X, dtype=np.int64)
    for k in range(len(CANDS)):
        R[:, k] = largest_remainder(X[:, k], T[k])
    o = dict(ok=ok, prov=prov, U=U, V0=V0, V=R.astype(float), T=T, S=S, g23=g23,
             mult=(X.sum(0) / V0.sum(0)), hold_f=hold_f)
    if verbose:
        report(o)
    return o


def prov_shares(o, p):
    ix = [r for r, i in enumerate(o["ok"]) if o["prov"][i] == p]
    v = o["V"][ix].sum(0)
    return 100 * v / v.sum()


def winners(o):
    return {p: CANDS[int(prov_shares(o, p).argmax())] for p in sorted(set(o["prov"][i] for i in o["ok"]))}


def revierte(o):
    return sorted(p for p, c in winners(o).items() if c == "MAS" and PASO_WIN.get(p, "MIL") != "MAS")


def buscar_hold():
    """Factor comun mas cercano a 1 que deja a Massa segundo por MARGEN puntos en todas las provincias de HOLD."""
    for f in np.arange(1.0, 0.5, -0.005):
        o = run(False, round(f, 3))
        if all(np.sort(prov_shares(o, p))[-1] - prov_shares(o, p)[0] >= MARGEN for p in HOLD):
            return round(f, 3)
    raise ValueError("no alcanza")


def report(o):
    V, V0 = o["V"], o["V0"]
    print("factor provincial de Massa en %s: %.3f" % (", ".join(HOLD), o["hold_f"]))
    print("positivos:", o["S"], " multiplicadores nacionales:", dict(zip(CANDS, np.round(o["mult"], 4))))
    print("nacional:", {c: (int(V[:, k].sum()), round(100 * V[:, k].sum() / V.sum(), 2)) for k, c in enumerate(CANDS)})
    w = winners(o); rv = revierte(o)
    ok, prov = o["ok"], o["prov"]
    for p, c in w.items():
        ix = [r for r, i in enumerate(ok) if prov[i] == p]
        s = prov_shares(o, p); s0 = 100 * V0[ix].sum(0) / V0[ix].sum()
        print("  %-20s %s %5.1f | Massa %5.1f (real %5.1f)  PASO %s %s" % (p, c, s.max(), s[0], s0[0], PASO_WIN.get(p, "MIL"), "<-- revierte" if p in rv else ""))
    print("provincias:", {c: list(w.values()).count(c) for c in CANDS}, "| Massa revierte la PASO en", len(rv), rv)
    print("departamentos:", dict(zip(CANDS, np.bincount(V.argmax(1), minlength=5).tolist())))


if __name__ == "__main__":
    run()
