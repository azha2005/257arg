"""Escenario hipotetico: balotaje 2027 Kicillof - Milei (21-nov-2027), totales de la imagen del usuario.

Metodo (simple y editable):
1. Punto de partida: balotaje 2023 por departamento (Milei vs Massa, votos positivos; escrutinio provisorio DINE).
2. Cada departamento conserva su posicion relativa: se aplica un corrimiento LOGISTICO comun (delta) al voto de
   Kicillof sobre el de Massa, mas un ajuste opcional por provincia (PROV_LOGIT, vacio por defecto).
3. El tamano del electorado se escala uniformemente al total de votos positivos del escenario.
4. delta se resuelve para que el total nacional de Kicillof sea EXACTAMENTE el de la imagen; los votos de cada
   departamento se redondean por resto mayor para que ambos totales cierren al voto.
"""
import os, pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T2 = dict(KIC=14283190, MIL=14231862)       # imagen: Kicillof 14.283.190 (50,09 %), Milei 14.231.862 (49,90 %)
PARTICIPACION = 79.41                        # % del balotaje, imagen
PROV_LOGIT = {}                              # p. ej. {"Buenos Aires": 0.05}: ajuste logistico propio de una provincia


def load():
    B = pickle.load(open(os.path.join(HERE, "base27kic.pkl"), "rb"))
    U = B["U"]
    ok = [i for i, u in enumerate(U) if u[1] != "Islas Malvinas"]
    return U, ok, B["bal"]


def largest_remainder(x, total):
    f = np.floor(x).astype(np.int64)
    r = int(total - f.sum())
    idx = np.argsort(-(x - f))[:r]
    f[idx] += 1
    return f


def run(verbose=True):
    U, ok, bal = load()
    prov = [u[0] for u in U]
    n = len(ok)
    mil = np.array([bal[i]["mil"] for i in ok], float)
    uxp = np.array([bal[i]["uxp"] for i in ok], float)
    pos23 = mil + uxp
    s23 = uxp / pos23                                   # Massa en 2023
    S = sum(T2.values())
    pos = pos23 * (S / pos23.sum())                     # mismo electorado, escalado al total del escenario
    lg = np.log(s23 / (1 - s23)) + np.array([PROV_LOGIT.get(prov[i], 0.0) for i in ok])
    lo, hi = -2.0, 2.0
    for _ in range(200):
        d = (lo + hi) / 2
        k = (pos / (1 + np.exp(-(lg + d)))).sum()
        if k < T2["KIC"]: lo = d
        else: hi = d
    sk = 1 / (1 + np.exp(-(lg + d)))
    kic = largest_remainder(pos * sk, T2["KIC"]).astype(float)
    posi = largest_remainder(pos, S)
    assert (kic <= posi).all()
    milv = posi - kic                                   # suma exacta: S - Kicillof = Milei
    assert int(milv.sum()) == T2["MIL"]
    o = dict(ok=ok, prov=prov, U=U, bal=bal, kic=kic, mil=milv, pos=kic + milv, s23=s23, delta=d, scale=S / pos23.sum())
    if verbose:
        report(o)
    return o


def report(o):
    ok, prov, kic, mil = o["ok"], o["prov"], o["kic"], o["mil"]
    print("escala 2023 -> escenario: x%.4f   corrimiento logistico delta = %+.4f" % (o["scale"], o["delta"]))
    print("Kicillof %d (%.2f %%)  Milei %d (%.2f %%)  total %d" % (kic.sum(), 100 * kic.sum() / (kic + mil).sum(), mil.sum(), 100 * mil.sum() / (kic + mil).sum(), (kic + mil).sum()))
    P = sorted(set(prov[i] for i in ok))
    print("\nProvincias (% Kicillof 2027 | % Massa 2023):")
    w = 0
    for p in P:
        ix = [r for r, i in enumerate(ok) if prov[i] == p]
        k, m = kic[ix].sum(), mil[ix].sum()
        k23 = sum(o["bal"][ok[r]]["uxp"] for r in ix) / sum(o["bal"][ok[r]]["uxp"] + o["bal"][ok[r]]["mil"] for r in ix)
        w += k > m
        print("  %-20s %5.1f  | %5.1f  %s" % (p, 100 * k / (k + m), 100 * k23, "<-- Kicillof" if k > m else ""))
    print("Provincias ganadas por Kicillof:", w, "de", len(P), "| departamentos:", int((kic > mil).sum()), "de", len(ok))


if __name__ == "__main__":
    run()
