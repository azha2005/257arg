"""Prueba del componedor de la camara con colecciones simuladas de ~30 actas de 2025 (28-oct-2026): se sacan mesas
reales de mesas_2025bl.pkl, se arman como el CSV de fotos y se proyectan con proyectar_fotos.calcular (2023p +
2021bl, como la noche real); las bancas salen de congreso.repartir y se comparan con las electas de verdad.
Con las fuerzas de los gobernadores de provinciales.csv (--sin-gob: sin ellas).
Esquemas: «azar» (30 mesas al azar del pais) y «twitter» (como las de 2025: 2/3 del AMBA, un racimo de 10 y dos de 3).
    python -X utf8 proyeccion/congreso_sim.py [--reps 40] [--nboot 100]
Salida: proyeccion/fotos_sim/congreso_sim.csv y una tabla en pantalla."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fotos_modelo as fm
import proyectar_fotos as pf
import congreso as cg

REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 40
NBOOT = int(sys.argv[sys.argv.index("--nboot") + 1]) if "--nboot" in sys.argv else 100
GOB = "--sin-gob" not in sys.argv          # fuerzas de los gobernadores (congreso.provinciales); --sin-gob para comparar
ICG = "--icg" in sys.argv                  # prior del ICG del mes anterior para el oficialismo (icg/icg_fotos.py)
W_ICG = {"azar": 1.2 ** 2, "twitter": 1.8 ** 2}  # varianza de las fotos en la proporción del oficialismo, por esquema


def ancla_icg(D, w, pri, ofi="LLA"):
    """Lleva la proporción nacional del oficialismo a w × prior + (1 − w) × fotos; en cada distrito el oficialismo se
    multiplica por el mismo factor y las demás fuerzas por el complementario."""
    p = 100 * D[ofi].sum() / D.sum().sum()
    q = w * pri + (1 - w) * p
    D = D.copy()
    otras = [c for c in D.columns if c != ofi]
    D[ofi] *= q / p
    D[otras] *= (100 - q) / (100 - p)
    return D
FZ = ["LLA", "FP", "PU", "FIT", "PROV"]


def muestra(m, amba, rng, scheme):
    if scheme == "azar":
        return rng.choice(len(m), 30, replace=False)
    n = int(rng.integers(25, 36))
    ia = np.where(amba)[0]
    idx = []
    for size in (10, 3, 3):                                   # racimos: mesas seguidas de un mismo circuito del AMBA
        i = rng.choice(ia, p=m.e.to_numpy(float)[ia] / m.e.to_numpy(float)[ia].sum())
        mm = np.where(m.circ_key.to_numpy() == m.circ_key.iat[i])[0]
        s = rng.integers(len(mm))
        idx += list(mm[np.arange(s, s + size) % len(mm)][:min(size, len(mm))])
    na = max(0, int(round(2 / 3 * n)) - len(idx))
    idx += list(rng.choice(ia, na, replace=False)) + list(rng.choice(np.where(~amba)[0], n - len(idx) - na, replace=False))
    return np.unique(idx)


def actas(sub):
    """Mesas -> filas como las de leer() (una por acta y fuerza)."""
    s = sub.copy()
    s["OTRAS"] = s.OTRAS + s.OTROS
    s["BN"] = s.BLANCO + s.NULO
    L = s.melt(id_vars=["distrito_id", "seccion_id", "circuito", "mesa_id"], value_vars=["LLA", "FP", "PU", "FIT", "OTRAS", "BN"],
               var_name="bloque", value_name="votos")
    L["foto"] = "sim"
    L["mesa"] = L.mesa_id.astype(str)
    L["completa"] = "si"
    L["lista"] = L.bloque
    L["distrito_id"] = L.distrito_id.astype(str).str.zfill(2)
    L["seccion_id"] = L.seccion_id.astype(int)
    L["circuito"] = L.circuito.map(pf.norm_circ)
    L["votos"] = L.votos.astype(float)
    L["mesa_key"] = L.foto + "|" + L.distrito_id + "|" + L.seccion_id.astype(str) + "|" + L.circuito + "|" + L.mesa
    return L


def bancas(R, scheme=None):
    blocs, F, clus = R["blocs"], R["F"], R["clus"]
    Dpt = R["proj_d"](np.arange(len(F)))[blocs]
    gob0 = (lambda D, rng=None: cg.provinciales(D, 2025, R["actas"], rng)[0]) if GOB else (lambda D, rng=None: D)
    if ICG:
        sys.path.insert(0, os.path.join(HERE, "icg"))
        import icg_fotos
        pri, sp = icg_fotos.prior("2025-10-26")
        w = W_ICG[scheme] / (W_ICG[scheme] + sp ** 2)
        gob = lambda D, rng=None: gob0(ancla_icg(D, w, pri), rng)
    else:
        gob = gob0
    _, tot = cg.repartir(gob(Dpt), 2025, R["pad"])
    bs = fm.bootstrap(lambda k: R["proj_d"](k)[blocs].to_numpy(), clus, NBOOT, R["rng"])
    bs = np.maximum(Dpt.to_numpy()[None] + pf.FACTOR * (bs - bs.mean(0)), 0)
    S = pd.DataFrame([cg.repartir(gob(pd.DataFrame(b, index=Dpt.index, columns=blocs), R["rng"]), 2025, R["pad"])[1]
                      for b in bs])
    S = S.reindex(columns=FZ).fillna(0)
    return tot, S


def main():
    m = pd.read_pickle(os.path.join(HERE, "mesas_2025bl.pkl"))
    m = m[m.mesa_tipo == "NATIVOS"].reset_index(drop=True)
    m["seccion_id"] = m.seccion_id.astype(int)
    m["circ_key"] = m.distrito_id.astype(str) + "|" + m.seccion_id.astype(str) + "|" + m.circuito.astype(str)
    amba = fm.region(m.distrito_id, m.seccion_id, "amba") == "AMBA"
    real = cg.electos(2025)[1]
    rng = np.random.default_rng(2025)
    rows = []
    for scheme in ("azar", "twitter"):
        for rep in range(REPS):
            a = actas(m.iloc[muestra(m, amba, rng, scheme)])
            R = pf.calcular(a, "2023p,2021bl", nboot=20, seed=rep)
            tot, S = bancas(R, scheme)
            r = dict(esquema=scheme, rep=rep, actas=a.mesa_key.nunique())
            for f in FZ:
                lo, hi = np.percentile(S[f], [5, 95])
                r.update({f: tot.get(f, 0), f + "_lo": lo, f + "_hi": hi, f + "_real": real.get(f, 0)})
            pt = dict(zip(R["blocs"], R["pt"]))
            r["margen"] = pt["LLA"] - pt["FP"]
            rows.append(r)
            print(scheme, rep, "  ".join("%s %d (%.0f-%.0f)" % (f, r[f], r[f + "_lo"], r[f + "_hi"]) for f in FZ), flush=True)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.join(HERE, "fotos_sim"), exist_ok=True)
    df.to_csv(os.path.join(HERE, "fotos_sim", "congreso_sim%s%s.csv" % ("" if GOB else "_sin_gob", "_icg" if ICG else "")), index=False)
    print("\nReal:", "  ".join("%s %d" % (f, real.get(f, 0)) for f in FZ))
    for scheme, g in df.groupby("esquema", sort=False):
        print("\n%s (%d colecciones)" % (scheme, len(g)))
        print("fuerza  media  error_medio  error_abs  p10-p90 del punto  cubre_banda90")
        for f in FZ:
            err = g[f] - g[f + "_real"]
            cub = ((g[f + "_lo"] <= g[f + "_real"]) & (g[f + "_real"] <= g[f + "_hi"])).mean()
            print("%-6s %6.1f %+11.1f %10.1f %9.0f-%-3.0f %16.0f %%" % (f, g[f].mean(), err.mean(), err.abs().mean(),
                  *np.percentile(g[f], [10, 90]), 100 * cub))
        d = g.LLA - g.FP
        print("LLA - FP en bancas: media %+.1f (real %+d), LLA primera en %d %% de las colecciones"
              % (d.mean(), real["LLA"] - real["FP"], 100 * (d > 0).mean()))


if __name__ == "__main__":
    main()
