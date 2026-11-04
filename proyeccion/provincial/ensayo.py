"""Ensayo general de la proyeccion provincial con una eleccion ya escrutada como si fuera la noche:
    python proyeccion/provincial/ensayo.py --prov pba --destino 2025bl --origen 2023p --n 30 --rep 100
    python proyeccion/provincial/ensayo.py --prov pba --destino pba2025 --origen 2023p,2023 --fuerzas FP,LLA,SB,FIT,OTRAS
Sortea --rep colecciones de --n mesas del destino (mesas_<destino>.pkl), arma las actas completas, proyecta con
proyectar_prov.calcular y compara con el escrutinio: error del margen provincial, error medio por fuerza y por
seccion, y cobertura de la banda del 95 %. Esquemas: azar (todas las mesas iguales) y conurbano (65 % de las
actas del conurbano, como las fotos de Twitter de 2025). El marco de electores es el del destino (en vivo se conoce
el padron antes de votar). --antecesores: JSON como en proyectar_prov.py. Escribe ensayo_<prov>_<destino>_<origen>.md y .csv en esta carpeta."""
import json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..")]
import config as cf
import proyectar_prov as pp

KEY = ["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]


def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def actas(m, blocs):
    """Tabla ancha de mesas -> CSV largo de actas completas."""
    m = m.assign(BN=m[[c for c in ("BLANCO", "NULO") if c in m]].sum(1))
    L = m.melt(id_vars=["distrito_id", "seccion_id", "circuito", "mesa_id", "e"], value_vars=blocs + ["BN"],
               var_name="bloque", value_name="votos")
    return L.rename(columns={"mesa_id": "mesa", "e": "electores"}).assign(foto="ensayo", completa="si")


def main():
    prov, dest, orig = opt("--prov", "pba"), opt("--destino", "2025bl"), opt("--origen", "2023p")
    n, rep, nboot = int(opt("--n", 30)), int(opt("--rep", 100)), int(opt("--nboot", 300))
    p = cf.PROVINCIAS[prov]
    m = pd.read_pickle(os.path.join(HERE, "..", "mesas_%s.pkl" % dest))
    m = m[m.distrito_id == p["distrito"]]
    fixed = [c for c in ("BLANCO", "NULO", "OTROS") if c in m]
    blocs = opt("--fuerzas").split(",") if opt("--fuerzas") else [c for c in m.columns if c not in KEY + ["e"] + fixed]
    m = m[m[blocs].sum(1) > 0].reset_index(drop=True)
    umap = pp.unidades(prov)
    m["u"] = m.seccion_id.map(umap)
    real_u = m.groupby("u")[blocs].sum()
    real = 100 * real_u.sum() / real_u.sum().sum()
    real_u = 100 * real_u.div(real_u.sum(1), axis=0)
    o1, o2 = real.sort_values(ascending=False).index[:2]
    marco = m.groupby(["seccion_id", "circuito"], as_index=False).e.sum()
    st = p["estrato"](m.distrito_id, m.seccion_id)
    ant = json.load(open(opt("--antecesores"), encoding="utf-8")) if opt("--antecesores") else None
    rng = np.random.default_rng(int(opt("--seed", 1)))
    rows = []
    for esquema in opt("--esquemas", "azar,conurbano").split(","):
        for r in range(rep):
            if esquema == "azar":
                idx = rng.choice(len(m), n, replace=False)
            else:
                k = int(round(.65 * n))
                idx = np.concatenate([rng.choice(np.flatnonzero(st == "AMBA"), k, replace=False),
                                      rng.choice(np.flatnonzero(st != "AMBA"), n - k, replace=False)])
            R = pp.calcular(actas(m.iloc[idx], blocs), prov, orig, blocs, ant, marco=marco, nboot=nboot, seed=r)
            pt, lo, hi = (pd.Series(R[k], index=R["blocs"]) for k in ("pt", "lo", "hi"))
            D = pd.DataFrame(R["distrito_pt"], index=R["distritos"], columns=blocs)
            D = 100 * D.div(D.sum(1), axis=0)
            rows.append(dict(esquema=esquema, rep=r, err_margen=(pt[o1] - pt[o2]) - (real[o1] - real[o2]),
                             mae_fuerza=float((pt - real[blocs]).abs().mean()),
                             mae_seccion=float((D[[o1, o2]] - real_u.loc[D.index, [o1, o2]]).abs().mean().mean()),
                             gana_ok=bool((pt[o1] > pt[o2]) == (real[o1] > real[o2])),
                             **{"cubre_" + b: bool(lo[b] <= real[b] <= hi[b]) for b in blocs}))
            print(esquema, r, "margen %+.2f" % rows[-1]["err_margen"], flush=True)
    T = pd.DataFrame(rows)
    tag = "ensayo_%s_%s_%s" % (prov, dest, orig.replace(",", "+"))
    T.to_csv(os.path.join(HERE, tag + ".csv"), index=False)
    L = ["# Ensayo: %s, destino %s, origen %s, %d mesas, %d colecciones por esquema" % (p["nombre"], dest, orig, n, rep), "",
         "Resultado real: " + ", ".join("%s %.2f" % (b, real[b]) for b in blocs) + "; margen %s − %s %+.2f." % (o1, o2, real[o1] - real[o2]), "",
         "| Esquema | Error medio abs. del margen | Sesgo del margen | Error medio por fuerza | Error por sección (2 primeras) | Ganador correcto |"
         + "".join(" Cobertura %s |" % b for b in blocs),
         "|---|---:|---:|---:|---:|---:|" + "---:|" * len(blocs)]
    for e, g in T.groupby("esquema", sort=False):
        L.append("| %s | %.2f | %+.2f | %.2f | %.2f | %.0f %% |" % (e, g.err_margen.abs().mean(), g.err_margen.mean(),
                 g.mae_fuerza.mean(), g.mae_seccion.mean(), 100 * g.gana_ok.mean())
                 + "".join(" %.0f %% |" % (100 * g["cubre_" + b].mean()) for b in blocs))
    L += ["", "Cobertura: proporción de colecciones en que la banda nominal del 95 % contiene el resultado real. "
          "Las colecciones de una misma elección no son elecciones independientes."]
    open(os.path.join(HERE, tag + ".md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n".join(L))


if __name__ == "__main__":
    main()
