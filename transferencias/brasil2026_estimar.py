"""Brasil 2026: RxC por sección con matrices jerárquicas (centro nacional → UF → región geográfica del IBGE).

Cada UF se encoge hacia el centro nacional (λ1) y cada región, intermedia o inmediata, hacia su UF (λ2). λ1, λ2 y el nivel
se eligen por validación cruzada con municipios enteros por fold; el nivel regional solo reemplaza a la UF si baja el error
fuera de muestra más de 1 %. Todo el ajuste usa estadísticos suficientes por región inmediata y fold (rxc_calvo.fit_ss):
el resultado es el mismo que ajustar sección por sección.
    python -X utf8 transferencias/brasil2026_estimar.py --preparar   # emparejamiento de secciones (una vez)
    python -X utf8 transferencias/brasil2026_estimar.py              # CV, fuera de muestra, sensibilidad, bootstrap
BOOT=200 y WORKERS=4 por defecto; los procesos corren con prioridad baja."""
import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")
import concurrent.futures
import sys
import time

import numpy as np
import pandas as pd

from rxc_calvo import fit_ss
from brasil2026_datos import OUT, dump

LAMBDAS = (2e-3, 2e-4, 2e-5, 2e-6, 2e-7, 0)              # UF hacia el centro nacional
LAMBDAS_REG = (2e-1, 2e-2, 2e-3, 2e-4, 2e-5, 2e-6, 0)    # región hacia su UF
NIVELES = {"intermedia": "cod_rgint", "inmediata": "cod_rgi"}
NF = 5
REPS = 3              # repeticiones de la prueba fuera de muestra (la 0 usa los folds de la selección)
BORDE = 0.5           # puntos: una celda por debajo está en el límite del modelo (no puede bajar de 0)
BOOT = int(os.environ.get("BOOT", "200"))
WORKERS = int(os.environ.get("WORKERS", "4"))
KEY = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
EXTRA = ["Blanco y nulo", "No votó"]


def baja_prioridad():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 10)
    except Exception:
        pass


def prepare():
    detail = pd.read_pickle(OUT / "detalle.pkl")
    votes = pd.read_pickle(OUT / "votos.pkl")
    names = pd.read_csv(OUT / "candidatos_codigos.csv", dtype=str)
    specials = names[names.SQ_CANDIDATO.eq("-1")]
    special_codes = specials.NR_VOTAVEL.unique().tolist()
    assert set(special_codes) <= {"95", "96"}, specials.to_string()
    labels = {"13": "Lula (PT)", "22": "Flávio Bolsonaro (PL)", "30": "Romeu Zema", "55": "Ronaldo Caiado", "14": "Renan Santos", "16": "Hertz Dias", "21": "Edmilson Costa", "27": "Clariana Barão", "28": "Leonardo Araújo", "29": "Rui Costa Pimenta", "35": "Wilson Grassi", "70": "Augusto Cury", "80": "Samara Martins"}
    candidates = names[~names.NR_VOTAVEL.isin(special_codes)].drop_duplicates("NR_VOTAVEL")
    for row in candidates.itertuples():
        labels.setdefault(row.NR_VOTAVEL, row.NM_VOTAVEL.title())
    frames, metas = {}, {}
    problems = []
    for turn in ["1", "2"]:
        d = detail.xs(turn, level=0).copy()
        v = votes.xs(turn, level=0).reindex(d.index).fillna(0)
        codes = [c for c in v if c not in special_codes and v[c].sum() > 0]
        codes.sort(key=lambda c: -v[c].sum())
        table = v[codes].rename(columns=labels)
        table[EXTRA[0]] = d.QT_VOTOS_BRANCOS + d.QT_VOTOS_NULOS
        table[EXTRA[1]] = d.QT_ABSTENCOES
        checks = pd.DataFrame(index=d.index)
        checks["sin_votos"] = ~d.index.isin(votes.xs(turn, level=0).index)
        checks["cierre_padron"] = d.QT_APTOS.ne(d.QT_COMPARECIMENTO + d.QT_ABSTENCOES)
        checks["cierre_nominal"] = v[codes].sum(axis=1).ne(d.QT_VOTOS_NOMINAIS)
        checks["cierre_blanco_nulo"] = v.reindex(columns=special_codes, fill_value=0).sum(axis=1).ne(table[EXTRA[0]])
        checks["cierre_emitidos"] = table.drop(columns=EXTRA[1]).sum(axis=1).ne(d.QT_COMPARECIMENTO)
        checks["sin_padron"] = d.QT_APTOS.le(0)
        checks["no_instalada"] = ~d.ST_SECAO_INSTALADA.eq("Sim")
        checks["anulada"] = d.ST_SECAO_ANULADA.ne("Não")
        bad = checks.any(axis=1)
        report = checks.loc[bad].copy()
        report["turno"] = turn
        problems.append(report.reset_index())
        dump(OUT / f"calidad_turno_{turn}.json", {"secciones": len(d), "fallos_por_regla": checks.sum().astype(int).to_dict(), "estados_seccion": d.ST_SECAO_INSTALADA.value_counts().to_dict(), "anulada": d.ST_SECAO_ANULADA.value_counts().to_dict(), "total_padron": int(d.QT_APTOS.sum()), "categorias": table.sum().astype(int).to_dict()})
        frames[turn], metas[turn] = table.loc[~bad], d
    A, B = frames["1"], frames["2"]
    common = A.index.intersection(B.index)
    d1, d2 = metas["1"], metas["2"]
    delta = (d1.loc[common].QT_APTOS-d2.loc[common].QT_APTOS).abs()
    changed = delta.gt(0)
    small = delta.le(5) & delta.div(d1.loc[common].QT_APTOS).le(.01)
    used = common[small]
    # No se atribuye identidad de votantes por el mero cierre del padrón.
    exclusion = pd.DataFrame(index=d1.index.union(d2.index))
    exclusion["apto_1"] = d1.QT_APTOS
    exclusion["apto_2"] = d2.QT_APTOS
    exclusion["motivo"] = np.where(~exclusion.index.isin(common), "ausente o invalida en un turno", "padron cambia mas de 5 electores o 1 pct")
    exclusion.loc[~exclusion.index.isin(used)].to_csv(OUT / "exclusiones.csv", encoding="utf-8-sig")
    pd.concat(problems, ignore_index=True).to_csv(OUT / "fallos_calidad.csv", index=False, encoding="utf-8-sig")
    A, B = A.loc[used], B.loc[used]
    meta = d1.loc[used, ["NR_LOCAL_VOTACAO", "NM_MUNICIPIO"]].copy()
    meta["municipio"] = ["/".join(k[:2]) for k in used]
    meta["local"] = ["/".join(k[:3]) + "/" + loc for k, loc in zip(used, meta.NR_LOCAL_VOTACAO)]
    meta["munzona"] = ["/".join(k[:3]) for k in used]
    coverage = []
    for uf in sorted(set(d1.index.get_level_values(0)) | set(d2.index.get_level_values(0))):
        a = d1.loc[uf].QT_APTOS.sum() if uf in d1.index.get_level_values(0) else 0
        b = d2.loc[uf].QT_APTOS.sum() if uf in d2.index.get_level_values(0) else 0
        u = A.loc[uf].sum().sum() if uf in A.index.get_level_values(0) else 0
        u2 = B.loc[uf].sum().sum() if uf in B.index.get_level_values(0) else 0
        coverage.append(dict(uf=uf, electores_1=int(a), electores_2=int(b), electores_origen_usados=int(u), electores_usados=int(u2), cobertura_1_pct=100*u/a if a else 0, cobertura_2_pct=100*u2/b if b else 0, secciones_usadas=int((A.index.get_level_values(0) == uf).sum())))
    pd.DataFrame(coverage).to_csv(OUT / "cobertura_por_uf.csv", index=False, encoding="utf-8-sig")
    assert (A >= 0).all().all() and (B >= 0).all().all()
    strict = used.isin(common[~changed])
    pd.to_pickle((A.loc[strict], B.loc[strict], meta.loc[strict]), OUT / "pareadas_estrictas.pkl")
    pd.DataFrame(dict(padron_1=A.sum(axis=1), padron_2=B.sum(axis=1))).to_csv(OUT / "padrones_pareados.csv", encoding="utf-8-sig")
    pd.to_pickle((A, B, meta), OUT / "pareadas.pkl")
    print("Emparejadas", len(A), "electores", int(A.sum().sum()), "padron diferente", int(changed.sum()), flush=True)
    return A, B, meta


def con_regiones(meta):
    """Agrega a meta la región intermedia e inmediata de cada municipio (brasil2026_regiones.py)."""
    r = pd.read_csv(OUT / "regiones_municipio.csv", dtype=str)
    r.index = r.SG_UF + "/" + r.CD_MUNICIPIO
    meta = meta.copy()
    for nivel, col in NIVELES.items():
        meta[nivel] = meta.municipio.map(r[col]).to_numpy()
        assert meta[nivel].notna().all(), nivel
    return meta


def folds(ufs, municipios, seed=20261026):
    """Municipios enteros repartidos en NF folds dentro de cada UF (mismo sorteo que la versión anterior)."""
    rng = np.random.default_rng(seed)
    fold = np.empty(len(ufs), dtype=int)
    for uf in np.unique(ufs):
        mask = ufs == uf
        groups, inv = np.unique(municipios[mask], return_inverse=True)
        f = np.arange(len(groups)) % NF
        rng.shuffle(f)
        fold[mask] = f[inv]
    return fold


def unidades(A, B, meta):
    """Proporciones por unidad y la jerarquía región inmediata ⊂ intermedia ⊂ UF."""
    N = B.sum(axis=1).to_numpy(float)
    X, Y = A.to_numpy(float) / A.sum(axis=1).to_numpy()[:, None], B.to_numpy(float) / N[:, None]
    ufs = A.index.get_level_values(0).to_numpy()
    imed, ii = np.unique(meta.inmediata.to_numpy(), return_inverse=True)
    tab = pd.DataFrame(dict(ii=ii, uf=ufs, inter=meta.intermedia.to_numpy()))
    assert tab.groupby("ii").uf.nunique().eq(1).all() and tab.groupby("ii").inter.nunique().eq(1).all()
    first = tab.drop_duplicates("ii").set_index("ii").sort_index()
    uf_names, uf_of = np.unique(first.uf.to_numpy(), return_inverse=True)
    inter_names, inter_of = np.unique(first.inter.to_numpy(), return_inverse=True)
    inter_uf = np.zeros(len(inter_names), dtype=int)
    inter_uf[inter_of] = uf_of
    xm = np.zeros((len(imed), X.shape[1]))
    np.add.at(xm, ii, X * N[:, None])
    return dict(X=X, Y=Y, N=N, w=N / N.mean(), ufs=ufs, ii=ii, imed_names=imed, uf_names=uf_names, uf_of=uf_of,
                inter_names=inter_names, inter_of=inter_of, inter_uf=inter_uf, xm=xm,
                fold=folds(ufs, meta.municipio.to_numpy()), blocks=pd.factorize(meta.local)[0])


def stats(U, w, fold):
    """Estadísticos suficientes por (región inmediata, fold): S = X'WX, T = X'WY, q = Σ w y², n = unidades, m = Σ w."""
    X, Y = U["X"], U["Y"]
    gi, R, C = len(U["imed_names"]), X.shape[1], Y.shape[1]
    gid = U["ii"] * NF + fold
    order = np.argsort(gid, kind="stable")
    bounds = np.searchsorted(gid[order], np.arange(gi * NF + 1))
    S, T = np.zeros((gi * NF, R, R)), np.zeros((gi * NF, R, C))
    q, n, m = np.zeros((gi * NF, C)), np.zeros(gi * NF), np.zeros(gi * NF)
    for g in range(gi * NF):
        idx = order[bounds[g]:bounds[g + 1]]
        if len(idx) == 0:
            continue
        x, ww, y = X[idx], w[idx], Y[idx]
        xw = x * ww[:, None]
        S[g], T[g], q[g], n[g], m[g] = x.T @ xw, xw.T @ y, ww @ y**2, len(idx), ww.sum()
    return {k: v.reshape((gi, NF) + v.shape[1:]) for k, v in dict(S=S, T=T, q=q, n=n, m=m).items()}


def tomar(st, fs):
    return {k: v[:, fs].sum(axis=1) for k, v in st.items()}


def agrupar(st, of, G):
    out = {}
    for k, v in st.items():
        out[k] = np.zeros((G,) + v.shape[1:])
        np.add.at(out[k], of, v)
    return out


def lr(P):
    return np.log(np.maximum(P[:, :-1], 1e-12) / np.maximum(P[:, -1:], 1e-12)).ravel()


def ajuste(S, T, q, n, lam, g):
    """Una matriz encogida hacia g (log-cocientes), sin los destinos vacíos del grupo, como en la versión por sección."""
    R, C = T.shape
    keep = T.sum(axis=0) > 0
    keep[-1] = True
    out = np.zeros((R, C))
    if keep.sum() < 2:
        out[:, keep] = 1
        return out
    red = g.reshape(R, C - 1)[:, keep[:-1]].ravel()
    Tk, qk = T[:, keep], q[keep]
    out[:, keep] = fit_ss(S, Tk[:, :-1], qk[:-1].sum(), lam * n, red)
    assert np.isfinite(out).all() and np.allclose(out.sum(axis=1), 1)
    return out


def centro(tot, const=.001):
    P = fit_ss(tot["S"], tot["T"][:, :-1], tot["q"][:-1].sum(), const)
    return lr(P), P


def sse(P, S, T, q, todas=False):
    """Σ w ||x P − y||² a partir de los estadísticos; sin la última columna salvo todas=True (como la CV del proyecto)."""
    c = slice(None) if todas else slice(None, -1)
    Pc = P[:, c]
    return float((Pc * (S @ Pc)).sum() - 2 * (Pc * T[:, c]).sum() + q[c].sum())


def matrices_uf(U, tr, lam1, g, minimo=1):
    su = agrupar(tr, U["uf_of"], len(U["uf_names"]))
    return [ajuste(su["S"][u], su["T"][u], su["q"][u], su["n"][u], lam1, g) if su["n"][u] >= minimo else None
            for u in range(len(U["uf_names"]))]


def matrices_region(U, tr, Puf, nivel, lam2, Pg):
    """Matriz de cada región inmediata: la de su grupo del nivel (o de su UF, o el centro si faltan datos)."""
    gi = len(U["imed_names"])
    base = [Puf[U["uf_of"][i]] if Puf[U["uf_of"][i]] is not None else Pg for i in range(gi)]
    if nivel == "uf":
        return np.stack(base)
    if nivel == "inmediata":
        of, guf = np.arange(gi), U["uf_of"]
    else:
        of, guf = U["inter_of"], U["inter_uf"]
    sg = agrupar(tr, of, len(guf))
    Pk = [ajuste(sg["S"][k], sg["T"][k], sg["q"][k], sg["n"][k], lam2, lr(Puf[guf[k]] if Puf[guf[k]] is not None else Pg))
          if sg["n"][k] > 0 else None for k in range(len(guf))]
    return np.stack([Pk[of[i]] if Pk[of[i]] is not None else base[i] for i in range(gi)])


def error_cv(U, te, Pimed, ok):
    """Error en las regiones de prueba de las UF con entrenamiento suficiente."""
    sel = ok[U["uf_of"]] & (te["n"] > 0)
    e = sum(sse(Pimed[i], te["S"][i], te["T"][i], te["q"][i]) for i in np.flatnonzero(sel))
    return e, float(te["m"][sel].sum())


def cv_fold(U, st, f, lams1, plan):
    """plan: lista de (nivel, λ2) a evaluar con cada λ1 de lams1. Devuelve {(λ1, nivel, λ2): (error, masa)}."""
    tr, te = tomar(st, [k for k in range(NF) if k != f]), tomar(st, [f])
    g, Pg = centro({k: v.sum(axis=0) for k, v in tr.items()})
    su_tr = agrupar(tr, U["uf_of"], len(U["uf_names"]))
    ok = su_tr["n"] >= 5      # como la versión por sección: UF sin entrenamiento suficiente no se evalúan
    out = {}
    for lam1 in lams1:
        Puf = matrices_uf(U, tr, lam1, g)
        for nivel, lam2 in plan:
            out[(lam1, nivel, lam2)] = error_cv(U, te, matrices_region(U, tr, Puf, nivel, lam2, Pg), ok)
    return out


def rmse_cv(partes, C):
    tot = {}
    for p in partes:
        for k, (e, m) in p.items():
            a = tot.setdefault(k, [0., 0.])
            a[0] += e
            a[1] += m
    return {k: (e / m / (C - 1))**.5 * 100 for k, (e, m) in tot.items()}


def elegir(errores):
    """La penalización más fuerte dentro del 1 % del mínimo."""
    best = min(errores.values())
    return max(l for l, e in errores.items() if e <= 1.01 * best)


_G = {}


def init_pool(U, st, municipios, sel=None):
    baja_prioridad()
    _G.update(U=U, st=st, municipios=municipios, sel=sel)


def tarea_cv(args):
    f, lams1, plan = args
    return cv_fold(_G["U"], _G["st"], f, lams1, plan)


def seleccionar(U, st, mapper=None, lams1=LAMBDAS, lams2=LAMBDAS_REG, niveles=("uf", "intermedia", "inmediata")):
    """λ1 por CV; luego λ2 de cada nivel con ese λ1; luego el nivel (el más simple dentro del 1 % del mejor).
    mapper(tareas) reparte los folds entre procesos; sin mapper, en serie."""
    mapper = mapper or (lambda tareas: [cv_fold(U, st, *t) for t in tareas])
    C = U["Y"].shape[1]
    cv1 = rmse_cv(mapper([(f, lams1, [("uf", None)]) for f in range(NF)]), C)
    lam1 = elegir({k[0]: v for k, v in cv1.items()})
    plan = [(n, l) for n in niveles if n != "uf" for l in lams2]
    cv2 = rmse_cv(mapper([(f, [lam1], plan) for f in range(NF)]), C) if plan else {}
    lam2 = {n: elegir({k[2]: v for k, v in cv2.items() if k[1] == n}) for n in niveles if n != "uf"}
    err = {"uf": cv1[(lam1, "uf", None)]}
    err.update({n: cv2[(lam1, n, lam2[n])] for n in lam2})
    orden = [n for n in ("uf", "intermedia", "inmediata") if n in err]
    nivel = next(n for n in orden if err[n] <= 1.01 * min(err.values()))
    return dict(lam1=lam1, lam2=lam2, nivel=nivel, error_nivel=err,
                cv_uf={str(k[0]): v for k, v in cv1.items()},
                cv_region={n: {str(k[2]): v for k, v in cv2.items() if k[1] == n} for n in lam2})


def ajustar_todo(U, st, lam1, nivel, lam2):
    """Ajuste final con todas las unidades: matrices por región inmediata, votos por grupo, UF y país."""
    tot = tomar(st, slice(None))
    g, Pg = centro({k: v.sum(axis=0) for k, v in tot.items()})
    Puf = matrices_uf(U, tot, lam1, g)
    Pimed = matrices_region(U, tot, Puf, nivel, lam2, Pg)
    partes = Pimed * U["xm"][:, :, None]
    rmse = (sum(sse(Pimed[i], tot["S"][i], tot["T"][i], tot["q"][i], todas=True) for i in range(len(Pimed)))
            / tot["m"].sum() / U["Y"].shape[1])**.5 * 100
    return dict(M=partes.sum(axis=0), partes=partes, Pimed=Pimed, Puf=Puf, rmse=rmse)


def config(sel, nivel=None):
    nivel = nivel or sel["nivel"]
    return sel["lam1"], nivel, sel["lam2"].get(nivel)


def tarea_fuera(args):
    """Una repetición y un fold de la prueba fuera de muestra: errores por UF de cada modelo, ponderados por electores."""
    rep, f, sel = args
    U = _G["U"]
    fold = U["fold"] if rep == 0 else folds(U["ufs"], _G["municipios"], seed=1000 + rep)
    st, st1 = stats(U, U["w"], fold), stats(U, np.ones(len(U["w"])), fold)
    fs = [k for k in range(NF) if k != f]
    tr, tr1 = tomar(st, fs), tomar(st1, fs)
    g, Pg = centro({k: v.sum(axis=0) for k, v in tr.items()})
    _, Pc = centro({k: v.sum(axis=0) for k, v in tr1.items()})
    Puf = matrices_uf(U, tr, sel["lam1"], g)
    gi = len(U["imed_names"])
    modelos = {"media nacional": None, "sin origen": None, "Calvo (nacional)": np.repeat(Pc[None], gi, 0),
               "centro nacional": np.repeat(Pg[None], gi, 0), "UF": matrices_region(U, tr, Puf, "uf", None, Pg)}
    for nivel, lam2 in sel["lam2"].items():
        modelos[nivel] = matrices_region(U, tr, Puf, nivel, lam2, Pg)
    te = fold == f
    X, Y, N, ii, ufi = U["X"][te], U["Y"][te], U["N"][te], U["ii"][te], U["uf_of"][U["ii"][te]]
    su = agrupar(tr, U["uf_of"], len(U["uf_names"]))
    med_uf = su["T"].sum(axis=1) / np.maximum(su["m"], 1e-12)[:, None]
    med_nac = su["T"].sum(axis=(0, 1)) / su["m"].sum()
    out = {}
    for nombre, P in modelos.items():
        if nombre == "media nacional":
            pred = np.repeat(med_nac[None], len(X), 0)
        elif nombre == "sin origen":
            pred = np.where((su["m"][ufi] > 0)[:, None], med_uf[ufi], med_nac[None])
        else:
            pred = np.einsum("ir,irc->ic", X, P[ii])
        e_all = ((100 * (pred - Y))**2).mean(axis=1)
        pv, yv = pred[:, :-1] / pred[:, :-1].sum(axis=1, keepdims=True), Y[:, :-1] / np.maximum(Y[:, :-1].sum(axis=1, keepdims=True), 1e-12)
        e_vot = ((100 * (pv - yv))**2).mean(axis=1)
        out[nombre] = (np.bincount(ufi, N * e_all, len(U["uf_names"])), np.bincount(ufi, N * e_vot, len(U["uf_names"])),
                       np.bincount(ufi, N, len(U["uf_names"])))
    return out


def tarea_boot(b):
    """Réplica bootstrap: locales remuestreados dentro de cada UF; centro, λ1 y λ2 recalculados (grillas completas, para que
    la regla del 1 % mire el mismo mínimo que la estimación principal); nivel fijo."""
    U, sel = _G["U"], _G["sel"]
    rng = np.random.default_rng([20261026, b])
    count = np.zeros(len(U["w"]))
    for uf in np.unique(U["ufs"]):
        m = U["ufs"] == uf
        _, inv = np.unique(U["blocks"][m], return_inverse=True)
        count[m] = np.bincount(rng.integers(0, inv.max() + 1, inv.max() + 1), minlength=inv.max() + 1)[inv]
    st = stats(U, U["w"] * count, U["fold"])
    nivel = sel["nivel"]
    s = seleccionar(U, st, niveles=("uf", nivel) if nivel != "uf" else ("uf",))
    lam2 = s["lam2"].get(nivel)
    # Origen fijo: el remuestreo cambia el ajuste, no la masa de cada categoría.
    return ajustar_todo(U, st, s["lam1"], nivel, lam2)["M"], s["lam1"], lam2


def aggregate(A, B, meta, field):
    keys = [A.index.get_level_values(0), meta[field]]
    a, b = A.groupby(keys).sum(), B.groupby(keys).sum()
    a.index.names = b.index.names = ["SG_UF", field]
    mm = meta.groupby(keys)[["municipio"]].first()
    mm["local"] = mm.index.get_level_values(1)
    return a, b, con_regiones(mm)


def pct(M):
    return M / M.sum(axis=1, keepdims=True)


def main():
    start = time.monotonic()
    baja_prioridad()
    A, B, meta = pd.read_pickle(OUT / "pareadas.pkl") if (OUT / "pareadas.pkl").exists() else prepare()
    meta = con_regiones(meta)
    U = unidades(A, B, meta)
    st = stats(U, U["w"], U["fold"])
    rows, cols = list(A.columns), list(B.columns)
    with concurrent.futures.ProcessPoolExecutor(WORKERS, initializer=init_pool, initargs=(U, st, meta.municipio.to_numpy())) as pool:
        sel = seleccionar(U, st, lambda tareas: list(pool.map(tarea_cv, tareas)))
        print("Selección", sel, flush=True)
        main_fit = ajustar_todo(U, st, *config(sel))
        variantes = {"UF": ajustar_todo(U, st, *config(sel, "uf"))["M"]}
        for nivel in sel["lam2"]:
            if nivel != sel["nivel"]:
                variantes[nivel] = ajustar_todo(U, st, *config(sel, nivel))["M"]
        partes = list(pool.map(tarea_fuera, [(rep, f, sel) for rep in range(REPS) for f in range(NF)]))
    oos = {}
    for p in partes:
        for nombre, (ea, ev, n) in p.items():
            acc = oos.setdefault(nombre, [0, 0, 0])
            acc[0], acc[1], acc[2] = acc[0] + ea, acc[1] + ev, acc[2] + n
    fuera = [dict(modelo=k, uf="Brasil", rmse=float(np.sqrt(ea.sum() / n.sum())), rmse_votantes=float(np.sqrt(ev.sum() / n.sum())))
             for k, (ea, ev, n) in oos.items()]
    fuera += [dict(modelo=k, uf=U["uf_names"][u], rmse=float(np.sqrt(ea[u] / n[u])), rmse_votantes=float(np.sqrt(ev[u] / n[u])))
              for k, (ea, ev, n) in oos.items() for u in range(len(U["uf_names"])) if n[u] > 0]
    pd.DataFrame(fuera).to_csv(OUT / "fuera_de_muestra.csv", index=False, encoding="utf-8-sig")
    print(pd.DataFrame(fuera).query("uf == 'Brasil'").to_string(index=False), flush=True)
    M = main_fit["M"]
    sensitivity, n_unidades, seleccion_escalas = [], {}, {}
    for scale in ["local", "munzona", "estricta"]:
        if scale == "estricta":
            a, b, mm = pd.read_pickle(OUT / "pareadas_estrictas.pkl")
            mm = con_regiones(mm)
        else:
            a, b, mm = aggregate(A, B, meta, scale)
        Us = unidades(a, b, mm)
        n_unidades[scale] = len(a)
        # Cada escala elige su penalización y nivel: con menos unidades, el de las secciones sobreajusta.
        sts = stats(Us, Us["w"], Us["fold"])
        ss = seleccionar(Us, sts)
        seleccion_escalas[scale] = {k: ss[k] for k in ("lam1", "lam2", "nivel", "error_nivel")}
        S = ajustar_todo(Us, sts, *config(ss))
        variantes[scale] = S["M"]
        pd.DataFrame(S["M"], index=rows, columns=cols).to_csv(OUT / f"matriz_votos_{scale}.csv", encoding="utf-8-sig")
    for nombre, S in variantes.items():
        sensitivity.append(dict(escala=nombre, unidades=n_unidades.get(nombre, len(A)), electores=int(S.sum().round()), votos_distintos_a_masa_comun=float(np.abs(S / S.sum() * M.sum() - M).sum() / 2),
                                max_diferencia_pp=float(np.abs(pct(S) - pct(M)).max() * 100)))
        print("Sensibilidad", sensitivity[-1], flush=True)
    with concurrent.futures.ProcessPoolExecutor(WORKERS, initializer=init_pool, initargs=(U, st, meta.municipio.to_numpy(), sel)) as pool:
        boots, lam_boot = [], []
        for i, (Mb, l1, l2) in enumerate(pool.map(tarea_boot, range(BOOT))):
            boots.append(Mb)
            lam_boot.append((l1, l2))
            if (i + 1) % 10 == 0:
                print("bootstrap", i + 1, "/", BOOT, round(time.monotonic() - start), "s", flush=True)
    sel["escalas"] = seleccion_escalas
    escribir(A, B, U, sel, main_fit, variantes, boots, lam_boot, sensitivity, fuera, start)


def escribir(A, B, U, sel, fit_, variantes, boots, lam_boot, sensitivity, fuera, start):
    rows, cols = list(A.columns), list(B.columns)
    M = fit_["M"]
    tot1 = {k: v.sum(axis=(0, 1)) for k, v in stats(U, np.ones(len(U["w"])), U["fold"]).items()}
    C = centro(tot1)[1] * U["xm"].sum(axis=0)[:, None]
    mat = pd.DataFrame(M, index=rows, columns=cols)
    pd.DataFrame(C, index=rows, columns=cols).round().astype(int).to_csv(OUT / "calvo_nacional.csv", encoding="utf-8-sig")
    mat.round().astype(int).to_csv(OUT / "matriz_votos.csv", encoding="utf-8-sig")
    (mat.div(mat.sum(axis=1), axis=0) * 100).round(2).to_csv(OUT / "matriz_pct.csv", encoding="utf-8-sig")
    # Por UF (formato del proyecto) y por región del nivel elegido.
    partes = fit_["partes"]
    puf = np.zeros((len(U["uf_names"]),) + M.shape)
    np.add.at(puf, U["uf_of"], partes)
    pd.DataFrame([dict(distrito=U["uf_names"][u], origen=r, destino=c, votos=round(puf[u, i, j])) for u in range(len(puf))
                  for i, r in enumerate(rows) for j, c in enumerate(cols)]).to_csv(OUT / "por_provincia.csv", index=False, encoding="utf-8-sig")
    if sel["nivel"] != "uf":
        of, names = (np.arange(len(U["imed_names"])), U["imed_names"]) if sel["nivel"] == "inmediata" else (U["inter_of"], U["inter_names"])
        preg = np.zeros((len(names),) + M.shape)
        np.add.at(preg, of, partes)
        reg = pd.read_csv(OUT / "regiones_municipio.csv", dtype=str)
        col, nom = (NIVELES[sel["nivel"]], "nome_rgi" if sel["nivel"] == "inmediata" else "nome_rgint")
        nombre = reg.drop_duplicates(col).set_index(col)[[nom, "SG_UF"]]
        pd.DataFrame([dict(uf=nombre.at[names[k], "SG_UF"], region=names[k], nombre=nombre.at[names[k], nom], origen=r, destino=c, votos=round(preg[k, i, j]))
                      for k in range(len(names)) for i, r in enumerate(rows) for j, c in enumerate(cols)]).to_csv(OUT / "por_region.csv", index=False, encoding="utf-8-sig")
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [5, 95], axis=0)
    P = pct(M)
    # Rango entre especificaciones: cada variante con la masa de origen de la principal.
    V = np.array([pct(S) for S in list(variantes.values()) + [C]]) * M.sum(axis=1)[None, :, None]
    vmin, vmax = np.minimum(V.min(axis=0), M), np.maximum(V.max(axis=0), M)
    pd.DataFrame([dict(origen=r, destino=c, votos=round(M[i, j]), p5=round(lo[i, j]), p95=round(hi[i, j]), min_modelos=round(vmin[i, j]), max_modelos=round(vmax[i, j]))
                  for i, r in enumerate(rows) for j, c in enumerate(cols)]).to_csv(OUT / "intervalos.csv", index=False, encoding="utf-8-sig")
    Q = pct(C)
    dif = np.abs(P - Q).max(axis=1) * 100
    weight = M.sum(axis=1) / M.sum() * 100
    scale_dif = np.zeros(len(rows))
    for S in variantes.values():
        scale_dif = np.maximum(scale_dif, np.abs(P - pct(S)).max(axis=1) * 100)
    hi_pct = hi / M.sum(axis=1, keepdims=True) * 100
    borde = [dict(origen=r, destino=c, pct=round(float(P[i, j] * 100), 2), p95_pct=round(float(hi_pct[i, j]), 2))
             for i, r in enumerate(rows) for j, c in enumerate(cols) if P[i, j] * 100 < BORDE]
    audit, extra = [], {}
    for i, r in enumerate(rows):
        near = float(.5 * np.abs(P[i] - M.sum(axis=0) / M.sum()).sum() * 100)
        noid = bool(dif[i] > 30 or (weight[i] < 5 and dif[i] > 20) or scale_dif[i] > 20)
        sens = bool(not noid and max(dif[i], scale_dif[i]) > 10)
        cells = [b["destino"] for b in borde if b["origen"] == r]
        audit.append(dict(origen=r, peso_pct=float(weight[i]), diferencia_calvo_pp=float(dif[i]), diferencia_escala_pp=float(scale_dif[i]),
                          separacion_promedio_pp=near, ancho_max_ic_pp=float(((hi - lo)[i] / M[i].sum()).max() * 100),
                          ancho_max_modelos_pp=float(((vmax - vmin)[i] / M[i].sum()).max() * 100), no_identificada=noid, sensible=sens,
                          celdas_borde=";".join(cells), cerca_promedio=bool(weight[i] >= 5 and r not in EXTRA and near < 25)))
        extra[r] = dict(no_identificada=noid, sensible=sens, borde=cells)
    pd.DataFrame(audit).to_csv(OUT / "auditoria_filas.csv", index=False, encoding="utf-8-sig")
    marginals, real_uf = [], {}
    obs_uf = B.groupby(level=0).sum()
    for u, uf in enumerate(U["uf_names"]):
        real_uf[uf] = obs_uf.loc[uf].astype(int).to_dict()
        for j, c in enumerate(cols):
            obs, pred = int(obs_uf.loc[uf, c]), float(puf[u, :, j].sum())
            marginals.append(dict(uf=uf, destino=c, observado=obs, estimado=round(pred), diferencia_pct=100 * (pred - obs) / obs if obs else None, alerta=bool(pred > 1.25 * obs + 2000)))
    pd.DataFrame(marginals).to_csv(OUT / "control_marginales_uf.csv", index=False, encoding="utf-8-sig")
    fz = pd.DataFrame(fuera).query("uf == 'Brasil'").set_index("modelo")
    lb = pd.DataFrame(lam_boot, columns=["lam1", "lam2"]).astype(str)
    ctl = dict(secciones=len(A), locales=int(len(np.unique(U["blocks"]))), municipios=int(len({k[:2] for k in A.index})), ufs=list(map(str, U["uf_names"])),
               electores=int(B.sum().sum()), tolerancia_padron="hasta 5 electores y 1%; origen reescalado al padron de destino; sensibilidad con padron identico",
               nivel=sel["nivel"], regiones={"intermedia": len(U["inter_names"]), "inmediata": len(U["imed_names"])},
               **{"lambda": sel["lam1"]}, lambda_region=sel["lam2"], error_cv_por_nivel=sel["error_nivel"], validacion_cruzada_pp=sel["cv_uf"], validacion_cruzada_region_pp=sel["cv_region"],
               folds="municipios enteros; centro nacional y matrices de UF recalculados sin el fold",
               fuera_de_muestra={k: dict(rmse=float(v.rmse), rmse_votantes=float(v.rmse_votantes)) for k, v in fz.iterrows()},
               bootstrap=BOOT, bloque_bootstrap="local de votacion dentro de UF; centro nacional, lambda1 y lambda2 recalculados en cada replica (grillas completas); nivel y marginales de origen fijos",
               seleccion_por_escala=sel.get("escalas", {}),
               lambda_bootstrap=dict(lam1=lb.lam1.value_counts().to_dict(), lam2=lb.lam2.value_counts().to_dict()),
               rmse_territorial_pp=fit_["rmse"], votos_distintos_vs_calvo=float(np.abs(M - C).sum() / 2), sensibilidad=sensitivity,
               marginal_origen_observada=A.sum().astype(int).to_dict(), marginal_origen_modelada=mat.sum(axis=1).round().astype(int).to_dict(),
               marginal_destino=B.sum().astype(int).to_dict(), marginal_destino_estimada=mat.sum().round().astype(int).to_dict(),
               marginal_destino_provincia=real_uf, filas=audit, auditoria_extra=extra, celdas_borde=borde, umbral_borde_pp=BORDE,
               alertas_marginales=[r for r in marginals if r["alerta"]], segundos=time.monotonic() - start)
    dump(OUT / "control.json", ctl)
    print(mat.div(mat.sum(axis=1), axis=0).mul(100).round(1).to_string(), flush=True)
    print("Tiempo", ctl["segundos"], flush=True)


if __name__ == "__main__":
    if "--preparar" in sys.argv:
        prepare()
    else:
        main()
