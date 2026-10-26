"""Escenario 2027 (simulacion): primera vuelta y balotaje por departamento a partir de 2023 + traspasos de voto.

Metodo (todo editable aqui):
1. Grupos de origen en cada departamento (votos positivos de las generales 2023, escrutinio provisorio DINE):
     LLA  = Milei 2023
     B    = JxC 2023 x (1 - l)   votantes de Bullrich   (l = Larreta / (Larreta + Bullrich) en la PASO 2023 del departamento)
     L    = JxC 2023 x l         votantes de Larreta
     M    = UxP 2023 x (1 - g)   votantes de Massa      (g = Grabois / (Massa + Grabois) en la PASO 2023 del departamento)
     G    = UxP 2023 x g         votantes de Grabois
     H    = Hacemos por Nuestro Pais 2023 (Schiaretti)
     F    = FIT-U 2023 (Bregman)
2. Matriz de traspasos a priori TAU[origen][candidato 2027] (la de abajo), con inclinaciones locales (Centurion 2019,
   potencial de izquierda, provincias de los gobernadores...).
3. Ajuste IPF: las filas (origen x departamento) conservan sus votos y las columnas se ajustan para que el total
   nacional sea EXACTAMENTE el del escenario (tabla de la imagen: 27.802.349 positivos).
4. Balotaje Milei - Bregman: traspasos de cada candidato de la 1.a vuelta (con abstencion) y un corrimiento logistico
   segun cuan a la derecha vota el departamento; los dos desplazamientos globales se ajustan a los totales nacionales.
"""
import os, sys, pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CANDS = ["MIL", "BRE", "KIC", "VIL", "SCI", "MAN", "SCH"]
# Objetivos nacionales del escenario (primera vuelta, votos positivos) y del balotaje
T1 = dict(MIL=9864273, BRE=4271410, KIC=4154804, VIL=3232384, SCI=2435301, MAN=2326723, SCH=1517454)
T2 = dict(MIL=14698960, BRE=9048802)
assert sum(T1.values()) == 27802349

# ---------------------------------------------------------------- 1.a vuelta: traspasos a priori (filas = origen)
#            MIL   BRE   KIC   VIL   SCI   MAN   SCH
TAU = {
    "LLA": [0.42, 0.15, 0.01, 0.34, 0.01, 0.03, 0.04],   # Bregman 15 % (rango del usuario: 15-25 %); Villarruel se lleva el voto nacionalista
    "B":   [0.93, 0.00, 0.00, 0.05, 0.00, 0.01, 0.01],   # casi todo el voto de Bullrich se queda en la coalicion de Milei
    "L":   [0.78, 0.00, 0.00, 0.04, 0.02, 0.10, 0.06],   # el votante de Larreta es el menos fiel a Milei
    "M":   [0.02, 0.02, 0.50, 0.02, 0.27, 0.16, 0.01],   # Massa: Kicillof, Scioli (Frente Renovador) y algo de Manes
    "G":   [0.00, 0.93, 0.06, 0.00, 0.01, 0.00, 0.00],   # Grabois -> Bregman
    "H":   [0.04, 0.00, 0.01, 0.02, 0.04, 0.10, 0.79],   # Schiaretti conserva ~80 %
    "F":   [0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00],   # FIT-U 2023 -> Bregman
}
for k, v in TAU.items():
    assert abs(sum(v) - 1) < 1e-9, (k, sum(v))

# Provincias con empuje propio (multiplicador de las celdas del candidato)
PROV_BOOST = {
    "KIC": {"Buenos Aires": 1.25},
    "SCI": {"Catamarca": 1.6, "Tucumán": 1.3},          # Jalil (gobernador de Catamarca) de compañero
    "SCH": {"Córdoba": 1.15, "Santa Fe": 1.25, "Chubut": 1.25},   # gobernadores de Provincias Unidas
}
A_VIL = 0.5     # exponente de la inclinacion de Villarruel por Centurion 2019
A_BRE = 0.6     # exponente de la inclinacion de Bregman por potencial de izquierda (FIT + Grabois)
A_MAN = 0.5     # exponente de la inclinacion de Manes por voto de JxC (urbano / moderado)

# ---------------------------------------------------------------- balotaje: Milei - Bregman (origen -> [Milei, Bregman, abstencion])
R2 = {
    "MIL": [0.97, 0.01, 0.02],
    "BRE": [0.01, 0.93, 0.06],
    "KIC": [0.03, 0.70, 0.27],
    "VIL": [0.80, 0.05, 0.15],
    "SCI": [0.25, 0.45, 0.30],
    "MAN": [0.45, 0.25, 0.30],
    "SCH": [0.45, 0.22, 0.33],
}
BETA2 = 0.3     # corrimiento logistico por cada 10 pp de Milei (1.a vuelta) sobre el promedio nacional
# Peso extra sobre el voto a Bregman en el balotaje por provincia (<1 = menos). El escenario dice que Bregman no gana
# ninguna provincia: el peronismo de maquina de Santiago del Estero no la acompanaria con 60 %.
R2_PROV_B = {"Santiago del Estero": 0.3}


def load():
    B = pickle.load(open(os.path.join(HERE, "base27.pkl"), "rb"))
    U = B["U"]
    n = len(U)
    prov = [u[0] for u in U]
    mal = [i for i, u in enumerate(U) if u[1] == "Islas Malvinas"]
    ok = [i for i in range(n) if i not in mal]
    g23, g19, paso = B["g23"], B["g19"], B["paso"]
    gp = lambda e, k: e["P"].get(k, 0)
    d = {}
    for i in ok:
        e = g23[i]
        d[i] = dict(lla=gp(e, "LA LIBERTAD AVANZA"), uxp=gp(e, "UNION POR LA PATRIA"), jxc=gp(e, "JUNTOS POR EL CAMBIO"),
                    hxnp=gp(e, "HACEMOS POR NUESTRO PAIS"), fit=gp(e, "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD"),
                    bla=e["bla"], nul=e["nul"])
    # Centurion 2019 (Frente NOS) como proporcion de positivos; Antofagasta (sin dato 2019) toma el de su provincia
    nos = {}
    for i in ok:
        e = g19.get(i)
        if e:
            nos[i] = (gp(e, "FRENTE NOS"), sum(e["P"].values()))
    pn = {}
    for i, (a, b) in nos.items():
        x = pn.setdefault(prov[i], [0, 0]); x[0] += a; x[1] += b
    nat = sum(a for a, b in nos.values()) / sum(b for a, b in nos.values())
    cshare = {}
    for i in ok:
        if i in nos and nos[i][1] > 0:
            cshare[i] = nos[i][0] / nos[i][1]
        else:
            a, b = pn[prov[i]]; cshare[i] = a / b
    # PASO: Grabois dentro de UxP y Larreta dentro de JxC (si no hay PASO, la proporcion nacional)
    gnat = sum(p["grabois"] for p in paso.values()) / sum(p["grabois"] + p["massa"] for p in paso.values())
    lnat = sum(p["larreta"] for p in paso.values()) / sum(p["larreta"] + p["bullrich"] for p in paso.values())
    for i in ok:
        p = paso.get(i, {})
        den = p.get("grabois", 0) + p.get("massa", 0)
        d[i]["g"] = p["grabois"] / den if den > 50 else gnat
        den = p.get("larreta", 0) + p.get("bullrich", 0)
        d[i]["l"] = p["larreta"] / den if den > 50 else lnat
        d[i]["c"] = cshare[i] / nat
    return U, prov, ok, mal, d


def run(verbose=True):
    U, prov, ok, mal, d = load()
    GROUPS = ["LLA", "B", "L", "M", "G", "H", "F"]
    n = len(ok)
    V = np.zeros((n, 7))
    for r, i in enumerate(ok):
        x = d[i]
        V[r] = [x["lla"], x["jxc"] * (1 - x["l"]), x["jxc"] * x["l"], x["uxp"] * (1 - x["g"]), x["uxp"] * x["g"], x["hxnp"], x["fit"]]
    pos23 = V.sum(1)
    scale = sum(T1.values()) / V.sum()
    V = V * scale                                       # mismo electorado, escalado al total del escenario
    pos = V.sum(1)
    jshare = np.array([d[i]["jxc"] for i in ok]) / pos23
    jnat = sum(d[i]["jxc"] for i in ok) / pos23.sum()
    pot = np.array([d[i]["fit"] + d[i]["uxp"] * d[i]["g"] for i in ok]) / pos23
    pot = pot / (pot @ pos23 / pos23.sum())
    cc = np.array([d[i]["c"] for i in ok])
    P = np.zeros((n, 7, 7))                             # departamento x origen x candidato
    for gi, gname in enumerate(GROUPS):
        for ci, cname in enumerate(CANDS):
            P[:, gi, ci] = TAU[gname][ci]
    for ci, cname in enumerate(CANDS):
        for r, i in enumerate(ok):
            b = PROV_BOOST.get(cname, {}).get(prov[i], 1.0)
            P[r, :, ci] *= b
    ci = CANDS.index("VIL")
    for gi in range(7):
        P[:, gi, ci] *= cc ** A_VIL
    ci = CANDS.index("BRE"); P[:, GROUPS.index("LLA"), ci] *= np.maximum(pot, 0.05) ** A_BRE
    ci = CANDS.index("MAN")
    for g in ("M", "H"):
        P[:, GROUPS.index(g), ci] *= (jshare / jnat) ** A_MAN
    X = P * V[:, :, None]
    tgt = np.array([T1[c] for c in CANDS], float)
    for it in range(500):
        X *= (V / np.maximum(X.sum(2), 1e-12))[:, :, None]
        col = X.sum((0, 1))
        X *= (tgt / col)[None, None, :]
        if np.abs(X.sum((0, 1)) / tgt - 1).max() < 1e-12 and it > 5:
            pass
    X *= (V / np.maximum(X.sum(2), 1e-12))[:, :, None]
    v1 = X.sum(1)                                        # departamento x candidato (votos 1.a vuelta)
    # ajuste fino exacto de los totales (reparto residual proporcional entre departamentos)
    for it in range(200):
        s = tgt / v1.sum(0)
        v1 = v1 * s[None, :]
        v1 = v1 * (pos / v1.sum(1))[:, None]
    # ---- balotaje
    share_mil = v1[:, 0] / pos
    z = (share_mil - v1[:, 0].sum() / pos.sum()) / 0.10
    base = np.array([R2[c] for c in CANDS])              # origen x [M, B, abst]
    pbw = np.array([R2_PROV_B.get(prov[i], 1.0) for i in ok])
    sm, sb = 1.0, 1.0
    for it in range(300):
        pm = base[None, :, 0] * sm * np.exp(BETA2 * z)[:, None]
        pb = base[None, :, 1] * sb * (np.exp(-BETA2 * z) * pbw)[:, None]
        pa = base[None, :, 2] * np.ones((n, 1))
        tot = pm + pb + pa
        pm, pb = pm / tot, pb / tot
        m2 = (v1 * pm).sum(); b2 = (v1 * pb).sum()
        sm *= T2["MIL"] / m2; sb *= T2["BRE"] / b2
    vm = v1 * pm; vb = v1 * pb
    r2 = np.stack([vm.sum(1), vb.sum(1)], 1)
    out = dict(ok=ok, prov=prov, U=U, mal=mal, V=V, pos=pos, v1=v1, r2=r2, X=X, GROUPS=GROUPS, d=d, pm=pm, pb=pb, sm=sm, sb=sb, scale=scale)
    if verbose:
        report(out)
    return out


def report(o):
    ok, prov, v1, r2, X, GROUPS = o["ok"], o["prov"], o["v1"], o["r2"], o["X"], o["GROUPS"]
    print("escala 2023 -> escenario: x%.4f" % o["scale"])
    print("1.a vuelta nacional:", {c: round(100 * v1[:, k].sum() / v1.sum(), 2) for k, c in enumerate(CANDS)})
    print("balotaje nacional:  Milei %.2f %%  Bregman %.2f %%  (votos %s)" % (
        100 * r2[:, 0].sum() / r2.sum(), 100 * r2[:, 1].sum() / r2.sum(), int(r2.sum())))
    print("\nMatriz efectiva origen -> candidato (% de la fila, tras el ajuste):")
    M = X.sum(0); M = M / M.sum(1, keepdims=True)
    print("        " + "  ".join("%5s" % c for c in CANDS))
    for gi, g in enumerate(GROUPS):
        print("%-6s  " % g + "  ".join("%5.1f" % (100 * M[gi, k]) for k in range(7)))
    P = sorted(set(prov[i] for i in ok))
    print("\nProvincias (ganador 1.a vuelta / balotaje con % de Bregman):")
    for p in P:
        ix = [r for r, i in enumerate(ok) if prov[i] == p]
        a = v1[ix].sum(0); b = r2[ix].sum(0)
        print("  %-20s %-4s %5.1f   |  Bregman balotaje %5.1f %%  %s" % (p, CANDS[int(a.argmax())], 100 * a.max() / a.sum(), 100 * b[1] / b.sum(), "<-- gana Bregman" if b[1] > b[0] else ""))
    w1 = np.bincount(v1.argmax(1), minlength=7); w2 = (r2[:, 1] > r2[:, 0]).sum()
    print("\nDepartamentos ganados 1.a vuelta:", dict(zip(CANDS, w1.tolist())))
    print("Departamentos ganados por Bregman en el balotaje:", int(w2), "de", len(ok))


if __name__ == "__main__":
    run()
