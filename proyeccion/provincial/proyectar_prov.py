"""La noche de una eleccion provincial: proyeccion con las actas que se van juntando y elecciones anteriores.
    python proyeccion/provincial/proyectar_prov.py actas.csv --prov pba --origen pba2025,2025bl --fuerzas FP,LLA,SB,FIT,OTRAS --anio 2027
    python proyeccion/provincial/proyectar_prov.py actas.csv --prov pba --origen 2023p --real 2025bl    # contra un resultado conocido
Mismo motor que la nacional (fotos_motor.calcular: Goodman encogido al swing, banda por bootstrap de circuitos),
con tres cambios: solo las mesas de la provincia, la unidad de informe (seccion electoral en la PBA) en el lugar del
distrito, y las actas repesadas por los estratos de la provincia (conurbano / interior en la PBA).
Actas: el CSV de proyectar_fotos.py; distrito_id puede faltar (se toma el de la provincia).
Origenes: cualquier circ_<clave>.pkl de proyeccion/ o transferencias/ (nacionales 2023p, 2025bl...) o una provincial
ingresada con ingestar.py (pba2025). Antecesores: los de proyectar_fotos.ANTECESORES, o --antecesores archivo.json
con {"origen": {"BLOQUE": ["columna del origen", ...]}}; un bloque con el mismo nombre en el origen es su antecesor.
--marco: CSV con seccion_id, circuito, e (padron de destino); sin el, el del primer origen.
Bancas: cociente de la provincia (config.PROVINCIAS[...]["regla"]) por unidad con las camaras que renueva --anio;
OTRAS no entra al reparto (son muchas listas chicas)."""
import json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.join(HERE, "..")
sys.path[:0] = [HERE, PROY]
import config as cf
import fotos_motor
import proyectar_fotos as pf
from ingestar import ambitos, codigos_seccion

CACHE = {}


def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def unidades(prov):
    """seccion_id -> codigo de unidad de informe ("01".."08" en la PBA) y nombre de cada unidad."""
    p = cf.PROVINCIAS[prov]
    amb = ambitos(p["distrito"])
    if p["unidad"] == "seccion_electoral":
        u = amb.unidad.astype(int)
    else:
        u = amb.seccion_id
    return dict(zip(amb.seccion_id, u.map("{:02d}".format)))


def recodificar(idx_frame, umap):
    out = idx_frame.copy()
    out["distrito_id"] = out.seccion_id.astype(int).map(umap)
    if out.distrito_id.isna().any():
        raise ValueError("Secciones sin unidad: %s" % sorted(set(out.seccion_id[out.distrito_id.isna()]))[:10])
    return out


def cargador(prov):
    d, umap = cf.PROVINCIAS[prov]["distrito"], unidades(prov)

    def load(name):
        P, E, NM = pf.origen(name)
        keep = P.index.get_level_values(0) == d
        P, E = P[keep], E[keep]
        ix = recodificar(P.index.to_frame(index=False), umap)
        P.index = E.index = pd.MultiIndex.from_frame(ix)
        if NM is not None:
            NM = NM[NM.index.get_level_values(0) == d]
            NM.index = pd.MultiIndex.from_frame(recodificar(NM.index.to_frame(index=False), umap))
            NM = NM.groupby(level=[0, 1, 2]).sum()
        return P, E, NM
    return load


def calcular(a, prov, orig, fuerzas, antecesores=None, marco=None, nboot=pf.NBOOT, seed=0, factor=pf.FACTOR):
    p = cf.PROVINCIAS[prov]
    umap = unidades(prov)
    a = a.copy()
    if "distrito_id" in a and (a.distrito_id.astype(str).str.zfill(2) != p["distrito"]).any():
        raise ValueError("Hay actas de otro distrito")
    a["seccion_id"] = codigos_seccion(a.seccion_id.astype(str), p["distrito"])
    a = recodificar(a, umap)
    if marco is not None:
        marco = recodificar(marco.assign(seccion_id=codigos_seccion(marco.seccion_id.astype(str), p["distrito"])), umap)
    ant = {k: dict(v) for k, v in pf.ANTECESORES.items()}
    for k, v in (antecesores or {}).items():
        ant.setdefault(k, {}).update(v)
    saved, fotos_motor.ORIGENES = fotos_motor.ORIGENES, CACHE.setdefault(prov, {})
    try:
        R = fotos_motor.calcular(a, orig, cargador(prov), pf.normalizar_actas, ant, nboot=nboot, seed=seed,
                                 fuerzas=fuerzas, marco=marco, lam=pf.LAM, factor=factor, kind=pf.KIND,
                                 estrato=p["estrato"])
    finally:
        fotos_motor.ORIGENES = saved
    return R


def hare_piso(v, n, elig=None):
    """Ley 5109 de la PBA, arts. 109 y 110 (texto actualizado, normas.gba.gob.ar):
    cociente = votos de las listas / bancas (sin blancos ni anulados); las listas que no lo alcanzan no tienen
    representacion; cada una saca tantas bancas como veces entra el cociente; las que faltan, una por lista a los
    mayores residuos, y las que sigan faltando, a la lista mas votada. Si ninguna llega al cociente, el piso baja a la
    mitad, y otra vez, hasta que alguna llegue (art. 110); si llegan mas listas que bancas, van a las mas votadas.
    elig: listas que pueden recibir bancas (OTRAS suma al total pero no es una lista)."""
    v = np.maximum(np.asarray(v, float), 0)
    elig = np.ones(len(v), bool) if elig is None else np.asarray(elig, bool)
    s = np.zeros(len(v), int)
    if n <= 0 or not (v[elig] > 0).any():
        return s
    q = piso = v.sum() / n
    while not ((v >= piso) & elig).any():
        piso /= 2
    ok = (v >= piso) & elig
    if ok.sum() > n:
        s[[i for i in np.argsort(-v, kind="stable") if ok[i]][:n]] = 1
        return s
    s[ok] = np.floor(v[ok] / q)
    r = np.where(ok, v / q - s, -np.inf)
    for i in [i for i in np.argsort(-r, kind="stable") if ok[i]][:n - s.sum()]:
        s[i] += 1
    s[np.flatnonzero(ok)[np.argmax(v[ok])]] += n - s.sum()
    return s


REGLAS = {"hare_piso": hare_piso}


def bancas(R, prov, anio):
    """{(camara, unidad): (bancas por bloque en el punto, percentil 5, percentil 95)}"""
    p = cf.PROVINCIAS[prov]
    if anio not in p.get("renueva", {}):
        return {}
    regla = REGLAS[p["regla"]]
    blocs, codes = R["blocs"], list(R["distritos"])
    elig = np.array([b != "OTRAS" for b in blocs])
    out = {}
    for cam, secs in p["renueva"][anio].items():
        for s in secs:
            u = "%02d" % s
            if u not in codes:
                continue
            i, n = codes.index(u), p["camaras"][cam][s]

            def one(v):
                return regla(v, n, elig)
            pt = one(R["distrito_pt"][i])
            bs = np.array([one(dr[i]) for dr in R["distrito_bs"]]) if len(R["distrito_bs"]) and np.isfinite(R["distrito_bs"]).all() else None
            out[(cam, s)] = (pt, *(np.percentile(bs, [5, 95], axis=0) if bs is not None else (pt * np.nan,) * 2))
    return out


def nombres_unidad(prov):
    if cf.PROVINCIAS[prov]["unidad"] != "seccion_electoral":
        return {}
    return {"01": "Primera", "02": "Segunda", "03": "Tercera", "04": "Cuarta", "05": "Quinta", "06": "Sexta",
            "07": "Séptima", "08": "Capital"}


def informe(R, prov, orig, anio=None, real=None):
    blocs, pt, lo, hi, o1, o2 = (R[k] for k in ("blocs", "pt", "lo", "hi", "o1", "o2"))
    nom = nombres_unidad(prov)
    L = ["# %s: proyección con %d actas (%d circuitos) — origen %s" % (cf.PROVINCIAS[prov]["nombre"], len(R["F"]),
         R["clus"].max() + 1, orig), "",
         "Motor nacional (Goodman encogido al swing, λ = %s), actas repesadas por estrato provincial (conurbano / interior), "
         "banda nominal del 95 %% por bootstrap de circuitos × %.1f." % (pf.LAM, R["factor"]), "",
         "| Fuerza | Proyección | Banda 95 % | Suma cruda | Swing uniforme |", "|---|---:|---:|---:|---:|"]
    for j, b in enumerate(blocs):
        band = "%.1f–%.1f" % (lo[j], hi[j]) if R["inferencia_valida"] else "no estimable"
        L.append("| %s | **%.1f** | %s | %.1f | %.1f |" % (b, pt[j], band, R["crudo"][j], R["swing"][j]))
    if R["inferencia_valida"]:
        L += ["", "Margen %s − %s: **%+.1f** (banda %+.1f a %+.1f); primer puesto en las remuestras: %s %.1f %%." % (
            blocs[o1], blocs[o2], pt[o1] - pt[o2], *np.percentile(R["marg"], [2.5, 97.5]), blocs[o1],
            100 * R["prob_primero"][o1])]
    D = pd.DataFrame(R["distrito_pt"], index=R["distritos"], columns=blocs)
    P = 100 * D.div(D.sum(1), axis=0)
    act = R["F"].distrito_id.value_counts()
    L += ["", "## Por %s" % ("sección electoral" if nom else "unidad"), "",
          "| Unidad | Actas |" + "".join(" %s |" % b for b in blocs), "|---|---:|" + "---:|" * len(blocs)]
    for u in P.index:
        L.append("| %s | %d |" % (nom.get(u, u), act.get(u, 0)) + "".join(" %.1f |" % P.loc[u, b] for b in blocs))
    if anio:
        B = bancas(R, prov, anio)
        if B:
            L += ["", "## Bancas %d (cociente provincial; OTRAS fuera del reparto)" % anio, "",
                  "| Cámara | Sección | Bancas |" + "".join(" %s |" % b for b in blocs if b != "OTRAS"),
                  "|---|---|---:|" + "---:|" * sum(b != "OTRAS" for b in blocs)]
            tot = {}
            for (cam, s), (bp, b5, b95) in sorted(B.items()):
                cells = ""
                for j, b in enumerate(blocs):
                    if b == "OTRAS":
                        continue
                    cells += " %d (%s) |" % (bp[j], "%d–%d" % (b5[j], b95[j]) if np.isfinite(b5[j]) else "—")
                    tot.setdefault(cam, {}).setdefault(b, 0)
                    tot[cam][b] += bp[j]
                L.append("| %s | %s | %d |%s" % (cam, nom.get("%02d" % s, s), cf.PROVINCIAS[prov]["camaras"][cam][s], cells))
            for cam, t in tot.items():
                L.append("| %s | **total** | %d |%s" % (cam, sum(cf.PROVINCIAS[prov]["camaras"][cam][s] for s in
                         cf.PROVINCIAS[prov]["renueva"][anio][cam]), "".join(" **%d** |" % t[b] for b in t)))
            L += ["", "Entre paréntesis, percentiles 5–95 de las remuestras. Reglas y bancas por sección marcadas VERIFICAR en `config.py`."]
    L += ["", "## Notas", ""] + ["- " + n for n in R["notas"]]
    L += ["- Peso del conurbano en el padrón: %.1f %%; en las actas: %.1f %% (repesadas)." % (
        100 * R["share"].get("AMBA", 0), 100 * (R["s_f"] == "AMBA").mean())]
    if real:
        w = pd.read_pickle(os.path.join(PROY, "mesas_%s.pkl" % real))
        w = w[w.distrito_id == cf.PROVINCIAS[prov]["distrito"]]
        t = w[[b for b in blocs if b in w]].sum()
        rp = 100 * t / t.sum()
        L += ["", "## Contra el resultado real (%s)" % real, "", "| Fuerza | Real | Proyección | Error |", "|---|---:|---:|---:|"]
        for j, b in enumerate(blocs):
            L.append("| %s | %.1f | %.1f | %+.1f |" % (b, rp.get(b, np.nan), pt[j], pt[j] - rp.get(b, np.nan)))
    return L


def main():
    path = [a for a in sys.argv[1:] if a.endswith(".csv") and not a.startswith("--")][0]
    prov, orig = opt("--prov", "pba"), opt("--origen", "2025bl")
    fz = opt("--fuerzas")
    ant = json.load(open(opt("--antecesores"), encoding="utf-8")) if opt("--antecesores") else None
    marco = pd.read_csv(opt("--marco"), dtype={"circuito": str}) if opt("--marco") else None
    a = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    if "distrito_id" not in a:
        a["distrito_id"] = cf.PROVINCIAS[prov]["distrito"]
    R = calcular(a, prov, orig, fz.split(",") if fz else None, ant, marco, nboot=int(opt("--nboot", pf.NBOOT)))
    L = informe(R, prov, orig, int(opt("--anio")) if opt("--anio") else None, opt("--real"))
    out = path[:-4] + "_proyeccion_%s.md" % prov
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n".join(L))
    print("\n->", out)


if __name__ == "__main__":
    main()
