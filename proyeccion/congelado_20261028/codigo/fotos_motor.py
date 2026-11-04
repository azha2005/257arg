"""Motor de fotos: pesos por observacion, universo comun y remuestras coherentes.

Las actas no observadas no son ceros. Si el bootstrap pierde una fuerza completa,
se conserva el fallo y se suspende la inferencia, sin descartar selectivamente draws.
"""
import numpy as np
import pandas as pd
import fotos_modelo as fm
from enlace import alinear

ORIGENES = {}
BASE_LEG = ["LLA", "FP", "PU", "FIT", "OTRAS"]
NIVELES = [("circuito", ["distrito_id", "seccion_id", "circuito"]),
           ("seccion", ["distrito_id", "seccion_id"]), ("distrito", ["distrito_id"])]


def marco_destino(anio, carpeta):
    """Marco local de electores de destino, sin leer votos para la prediccion.
    En vivo se puede pasar el equivalente publicado antes del escrutinio con --marco.
    """
    from pathlib import Path
    path = Path(carpeta) / ("mesas_%sbl.pkl" % anio)
    if not path.exists():
        raise FileNotFoundError("Falta el marco de electores de destino; proporcionar --marco")
    m = pd.read_pickle(path)
    return m.groupby(["distrito_id", "seccion_id", "circuito"], as_index=False).e.sum()


def actualizar_resumen(R, distritos, draws):
    """Nacional e incertidumbre derivados de los mismos votos distritales."""
    def pct(d):
        t = d.sum(axis=-2)
        return 100*t / t.sum(axis=-1, keepdims=True)
    pt = pct(distritos)
    bs = pct(draws) if len(draws) else np.empty((0, len(pt)))
    ok = bool(len(bs) and np.isfinite(bs).all() and np.isfinite(pt).all()
              and len(np.unique(R["clus"])) >= 2)
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0) if ok else (np.full(len(pt), np.nan),)*2
    o1, o2 = np.argsort(-np.nan_to_num(pt, nan=-np.inf))[:2]
    R.update(pt=pt, bs=bs, lo=lo, hi=hi, o1=o1, o2=o2, marg=bs[:,o1]-bs[:,o2],
             prob_primero=fm.probabilidades_primero(bs) if ok else np.full(len(pt), np.nan),
             inferencia_valida=ok)


def calcular(a, orig, loader, normalizar, antecesores, nboot=2000, seed=0, fuerzas=None,
             marco=None, lam=.1, factor=1.4, kind="goodman"):
    a = normalizar(a)
    if fuerzas is None:
        if not set(a.bloque).difference(["BN"]).issubset(BASE_LEG):
            raise ValueError("Indicar fuerzas/catalogo para una eleccion distinta de los bloques legislativos")
        fuerzas = BASE_LEG
    blocs = list(dict.fromkeys(fuerzas))
    unknown = set(a.bloque).difference(blocs + ["BN"])
    if unknown or len(blocs) < 2:
        raise ValueError("Catalogo incompatible con las actas: " + str(unknown))
    dcols = blocs + ["BN", "ABSTENCION"]
    origs = orig.split(",")
    O = []
    for name in origs:
        if name not in ORIGENES:
            ORIGENES[name] = loader(name)
        P, E, NM = ORIGENES[name]
        keys = P.index.to_frame(index=False)
        keys.columns = ["distrito_id", "seccion_id", "circuito"]
        p = pd.concat([keys.reset_index(drop=True), P.reset_index(drop=True)], axis=1)
        if marco is None and not O:
            frame = keys.assign(e=E.to_numpy(float))
        elif marco is not None:
            frame = marco.copy()
        if (not np.isfinite(frame.e.to_numpy(float)).all() or (frame.e < 0).any()
                or frame.e.sum() <= 0):
            raise ValueError("Marco electoral con electores invalidos")
        frame["distrito_id"] = frame.distrito_id.astype(str).str.zfill(2)
        frame["seccion_id"] = frame.seccion_id.astype(int)
        frame["circuito"] = frame.circuito.astype(str).str.upper().str.lstrip("0").replace("", "0")
        cols = list(P.columns)
        values, levels = alinear(frame, p, cols, E.to_numpy(float), NIVELES)
        codes = sorted(frame.distrito_id.unique())
        dc = pd.Categorical(frame.distrito_id, categories=codes).codes
        natd = np.zeros((len(codes), len(cols)))
        np.add.at(natd, dc, values*frame.e.to_numpy(float)[:,None])
        ant = antecesores.get(name, {})
        src = [[cols.index(c) for c in ant.get(b, [b]) if c in cols] for b in blocs]
        src += [[cols.index("BLANCO/NULO")], [cols.index("ABSTENCION")]]
        O.append(dict(nombre=name, P=P, E=E, NM=NM, p=p, cols=cols, src=src, codes=codes, natd=natd,
                      ed=np.bincount(dc, weights=frame.e, minlength=len(codes)),
                      respaldo=pd.Series(levels).value_counts().to_dict()))
    units = a.drop_duplicates("mesa_key").copy().reset_index(drop=True)
    if not set(units.distrito_id).issubset(set(frame.distrito_id)):
        raise ValueError("Hay actas de distritos ausentes del marco electoral")
    for o in O:
        o["X"], o["levels"] = alinear(units, o["p"], o["cols"], o["E"].to_numpy(float), NIVELES)
    first = O[0]
    # El padron de una foto es dato si viene informado, o estimacion historica si no.
    av = None
    if first["NM"] is not None:
        counts = first["NM"].reindex(first["E"].index).to_numpy(float)
        tmp = first["p"][["distrito_id", "seccion_id", "circuito"]].copy()
        tmp["promedio"] = first["E"].to_numpy(float)/np.maximum(counts,1)
        av, _ = alinear(units, tmp, ["promedio"], counts, NIVELES)
    rows = []
    grouped = {k:g for k,g in a.groupby("mesa_key", sort=False)}
    for i, r in units.iterrows():
        g = grouped[r.mesa_key]
        vb = g.groupby("bloque").votos.sum()
        complete = r.completa == "si"
        estimate = float(av[i,0]) if av is not None else 330.
        stated = pd.to_numeric(pd.Series([r.get("electores", np.nan)]), errors="coerce").iloc[0]
        em = float(stated) if np.isfinite(stated) and stated > 0 else max(estimate, vb.sum())
        if vb.sum() > em + 1e-6:
            raise ValueError("Los votos superan el padron informado: " + r.mesa_key)
        y = np.full(len(dcols), np.nan)
        for j,b in enumerate(dcols[:-1]):
            if complete or b in vb:
                y[j] = vb.get(b,0)/em
        if complete:
            y[-1] = 1-vb.sum()/em
        rows.append(dict(foto=r.foto, mesa_key=r.mesa_key, distrito_id=r.distrito_id, seccion_id=r.seccion_id,
                         circuito=r.circuito, mesa=r.mesa, completa=complete, nivel=first["levels"][i], e=em, y=y))
    F = pd.DataFrame(rows)
    Y, e = np.vstack(F.y), F.e.to_numpy(float)
    sf = fm.region(F.distrito_id, F.seccion_id, "amba")
    sa = fm.region(frame.distrito_id, frame.seccion_id, "amba")
    share = pd.Series(frame.e.to_numpy(float)).groupby(sa).sum().pipe(lambda s:s/s.sum()).to_dict()
    for o in O:
        o["dist"] = pd.Categorical(F.distrito_id, categories=o["codes"]).codes

    def arr(idx, one=None):
        models = O if one is None else [one]
        pred = [fm.goodman(o["X"][idx], Y[idx], e[idx], None, o["src"], lam,
                           prop=kind=="goodman_prop", natd=o["natd"], strata=sf[idx], share=share)
                for o in models]
        return np.maximum(np.mean(pred, axis=0)[:,:len(blocs)],0)

    def proj_d(idx):
        return pd.DataFrame(arr(idx), index=first["codes"], columns=blocs)

    allx = np.arange(len(F))
    point = arr(allx)
    clus = pd.factorize(F.distrito_id+"|"+F.seccion_id.astype(str)+"|"+F.circuito)[0]
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero(clus==c) for c in np.unique(clus)]
    indices = [np.concatenate([groups[i] for i in rng.integers(len(groups),size=len(groups))]) for _ in range(nboot)]
    raw = np.array([arr(idx) for idx in indices]) if nboot else np.empty((0,)+point.shape)
    valid = np.isfinite(raw).all() and np.isfinite(point).all()
    draws = np.maximum(point + factor*(raw-raw.mean(0)),0) if nboot and valid else np.full_like(raw,np.nan)
    support=[]
    for j,b in enumerate(blocs):
        seen=np.isfinite(Y[:,j]); w=fm.poststrat(e[seen],sf[seen],share) if seen.any() else np.array([])
        support.append(dict(fuerza=b, actas=int(seen.sum()), circuitos=len(np.unique(clus[seen])),
                            n_efectivo=float(w.sum()**2/(w@w)) if len(w) else 0,
                            peso_amba=float(w[sf[seen]=="AMBA"].sum()/w.sum()) if len(w) else None))
    notes=[]
    if not valid:
        notes.append("Inferencia no estimable: faltan observaciones de alguna fuerza en el punto o en remuestras; no se descartan remuestras.")
    if marco is None:
        notes.append("Marco de electores del primer origen historico; para una eleccion nueva usar --marco con su padron.")
    for o in O:
        notes.append("Respaldo del universo en %s: %s" % (o["nombre"], o["respaldo"]))
    por_origen={o["nombre"]:fm.pct(arr(allx,o).sum(0),list(range(len(blocs)))) for o in O}
    swing=np.mean([fm.pct(fm.swing(o["X"],Y,e,o["dist"],o["natd"],o["ed"],o["src"]),list(range(len(blocs)))) for o in O],axis=0)
    crudo=fm.pct(np.nansum(Y[:,:len(blocs)]*e[:,None],0),list(range(len(blocs))))
    ix=pd.MultiIndex.from_frame(frame[["distrito_id","seccion_id","circuito"]])
    R=dict(actas=a,F=F,blocs=blocs,origs=origs,clus=clus,por_origen=por_origen,crudo=crudo,swing=swing,
           s_f=sf,share=share,notas=notes,P=pd.DataFrame(index=ix),E=pd.Series(frame.e.to_numpy(float),index=ix),
           proj_d=proj_d,pad=dict(zip(first["codes"],first["ed"])),rng=rng,soporte=support,
           distrito_pt=point,distrito_bs=draws,distrito_bs_raw=raw,indices_boot=indices,
           distritos=first["codes"],factor=factor,marco=frame)
    actualizar_resumen(R,point,draws)
    return R


def remuestrear_actas(R, idx):
    keys=R["F"].mesa_key.iloc[idx].tolist()
    return R["actas"].set_index("mesa_key").loc[keys].reset_index()
