"""Las fotos de actas de diputados 2025 que junto el usuario (fotos25/) pasadas por el modelo como si fuera la noche
de la eleccion y solo hubiera datos de 2023 (presidente, 1.a vuelta, por circuito).
    python proyeccion/fotos25.py
1. Transcripcion a mano de cada foto (FOTOS). Las que no traen numero de mesa se ubicaron buscando en el provisorio
   2025 la mesa con los mismos votos (eso usa datos de 2025, pero solo para saber de donde es la foto: la noche de la
   eleccion uno sabria el lugar por el tuit). Se compara cada transcripcion con el provisorio de la DINE.
2. Proyeccion con solo las fotos + 2023: crudo, swing uniforme sobre el circuito 2023 y matriz de traspasos (Goodman)
   con penalizacion hacia la matriz del swing. Cada columna de destino se ajusta con las mesas donde se conoce
   (Villa Lynch y Sarandi solo dan algunas fuerzas). Banda por bootstrap de las fotos (por circuito).
3. Contra el resultado real (provisorio DINE, bloques de mapas/mapa2025/mapeo_listas_2025.csv).
Salida: proyeccion/fotos25/RESUMEN.md y control_transcripcion.csv."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "fotos25")
os.makedirs(OUT, exist_ok=True)
sys.argv = [sys.argv[0], "2023p", "2025", "--circuito"]
import backtest as bt

B = ["LLA", "FP", "PU", "FIT", "OTRAS"]
ORIG = os.environ.get("ORIG", "2023p")                   # eleccion de origen (ver main)
# nombres de lista como en el provisorio (abreviados aca y expandidos abajo)
AB = {"LLA": "ALIANZA LA LIBERTAD AVANZA", "FP": "ALIANZA FUERZA PATRIA", "PU": "ALIANZA PROVINCIAS UNIDAS",
      "FIT": "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD", "PNBA": "PARTIDO NUEVO BUENOS AIRES", "LIBER": "LIBER.AR",
      "FPF": "FRENTE PATRIOTA FEDERAL", "UL": "UNIÓN LIBERAL", "CC": "COALICIÓN CÍVICA - A.R.I.",
      "PS": "MOVIMIENTO POLÍTICO SOCIAL Y CULTURAL PROYECTO SUR", "PFC": "PROPUESTA FEDERAL PARA EL CAMBIO",
      "POT": "ALIANZA POTENCIA", "UF": "ALIANZA UNIÓN FEDERAL", "NA": "ALIANZA NUEVOS AIRES",
      "MAS": "MOVIMIENTO AVANZADA SOCIALISTA"}
BA = ["LLA", "PNBA", "LIBER", "FIT", "FPF", "UL", "FP", "CC", "PS", "PFC", "PU", "POT", "UF", "NA", "MAS"]


def ba(vals, nulo, blanco):
    d = {AB[k]: v for k, v in zip(BA, vals)}
    d.update(NULO=nulo, BLANCO=blanco)
    return d


# (archivo, distrito, seccion, circuito, mesa, votos de diputados, nota). mesa None = ubicada por los votos.
FOTOS = [
    ("20251026_191620.jpg", "16", 9, "4115", "581", {"PRO - PROPUESTA REPUBLICANA": 17, "FUERZA PATRIA": 39,
        "ALIANZA LA LIBERTAD AVANZA": 77, "PRIMERO RÍO NEGRO": 6, "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": 12,
        "JUNTOS DEFENDEMOS RÍO NEGRO": 22, "MOVIMIENTO AL SOCIALISMO - MAS": 3, "BLANCO": 9, "NULO": 6}, "Bariloche"),
    ("20251026_193402.jpg", "16", 9, "4115", "582", {"PRO - PROPUESTA REPUBLICANA": 14, "FUERZA PATRIA": 58,
        "ALIANZA LA LIBERTAD AVANZA": 69, "PRIMERO RÍO NEGRO": 7, "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": 5,
        "JUNTOS DEFENDEMOS RÍO NEGRO": 27, "MOVIMIENTO AL SOCIALISMO - MAS": 2, "BLANCO": 7, "NULO": 3}, "Bariloche"),
    ("57d45708-d409-41f0-8604-aa5a509135e7.png", "01", 10, "104", "4230", {"UNIÓN DEL CENTRO DEMOCRÁTICO": 1,
        "GEN": 5, "ALIANZA POTENCIA": 9, "HAGAMOS FUTURO": 3, "ALIANZA LA LIBERTAD AVANZA": 111, "PARTIDO FEDERAL": 2,
        "FUERZA PATRIA": 71, "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": 17, "CIUDADANOS UNIDOS": 10,
        "PARTIDO COMUNISTA": 1, "MOVIMIENTO DE JUBILADOS Y JUVENTUD": 1, "NULO": 4, "BLANCO": 12}, "Capital, comuna 10"),
    ("G4OJYHHXcAA71yi.jpg", "01", 5, "60", "2001", {"UNIÓN DEL CENTRO DEMOCRÁTICO": 1, "GEN": 2,
        "LA IZQUIERDA EN LA CIUDAD": 1, "ALIANZA POTENCIA": 3, "HAGAMOS FUTURO": 4, "ALIANZA LA LIBERTAD AVANZA": 102,
        "PARTIDO FEDERAL": 1, "INTEGRAR": 2, "FUERZA PATRIA": 71, "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": 37,
        "CIUDADANOS UNIDOS": 16, "PARTIDO COMUNISTA": 1, "MOVIMIENTO DE JUBILADOS Y JUVENTUD": 3, "NULO": 2,
        "BLANCO": 10}, "Capital, comuna 5"),
    ("G4N-GqiXMAAAZZe.jpg", "19", 3, "40", "1012", {"FRENTE PUEBLO": 4, "FRENTE JUSTICIALISTA": 9,
        "MOVIMIENTO AL SOCIALISMO": 3, "PROVINCIAS UNIDAS": 6, "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": 0,
        "ALIANZA LA LIBERTAD AVANZA": 134, "NULO": 4, "BLANCO": 4}, "San Luis, Villa Reynolds"),
    ("G4OA6GBXoAAP9BO.jpg", "09", 1, "3", "97", {"PRINCIPIOS Y CONVICCIÓN": 1, "PARTIDO DEL OBRERO": 1,
        "FRENTE DE LA VICTORIA": 102, "ALIANZA LA LIBERTAD AVANZA": 121, "JUNTOS POR LA LIBERTAD Y LA REPÚBLICA": 15,
        "NULO": 6, "BLANCO": 2}, "Formosa capital (la mesa se lee 1097; es la 97)"),
    ("G4OLAoFXQAAauRB.jpg", "12", 1, "1E", "61", {"UNIÓN CÍVICA RADICAL": 16, "FEDERALES DEFENDAMOS LA RIOJA": 55,
        "PROVINCIAS UNIDAS": 7, "LAS FUERZAS DEL CENTRO": 3, "LA LIBERTAD AVANZA": 88, "REPUBLICANOS UNIDOS": 3,
        "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": 6, "BLANCO": 2, "NULO": 3}, "La Rioja capital"),
    ("G4N620KW0AAl2Rk.jpg", "02", 60, "444", "101", ba([135, 2, 0, 8, 0, 0, 75, 5, 2, 6, 7, 3, 1, 0, 0], 5, 5), "Lanús (LLA 135; leí 125 la primera vez)"),
    ("G4OCJ2HXAAAM7eg.jpg", "02", 70, "588", "1026", ba([101, 2, 0, 12, 4, 1, 99, 3, 2, 8, 7, 3, 1, 0, 1], 2, 8),
     "Lomas de Zamora"),
    ("G4ODZEzW8AAF4dS.jpg", "02", 61, "629A", "637", ba([69, 4, 0, 22, 3, 1, 124, 0, 0, 9, 2, 1, 2, 3, 1], 0, 3),
     "La Matanza"),
    ("G4OFi53XgAAGKdR.png", "02", 113, "535A", "792", ba([97, 4, 0, 21, 1, 4, 80, 1, 1, 6, 3, 0, 1, 1, 0], 16, 7),
     "Tigre"),
    ("G4OHBSPXMAAufNZ.png", "02", 80, "669", "381", ba([114, 4, 2, 14, 4, 1, 101, 2, 0, 4, 14, 1, 1, 0, 3], 3, 4),
     "Morón"),
    ("G4OIwNlWcAAxQda.jpg", "02", 61, "628", "375", ba([139, 1, 0, 15, 3, 0, 66, 3, 2, 9, 7, 3, 0, 2, 2], 6, 4),
     "La Matanza (foto repetida dos veces)"),
    ("G4ObyboXIAAvnEX.jpg", "02", 61, "628", "439", ba([136, 6, 0, 15, 0, 1, 63, 2, 1, 6, 12, 5, 1, 0, 0], 6, 1),
     "La Matanza (números corridos una fila)"),
    ("G4OJuFaXQAAmLAZ.jpg", "02", 119, "337A", "48", ba([87, 4, 1, 17, 3, 4, 84, 3, 2, 4, 2, 0, 1, 1, 2], 4, 1),
     "La Costa (números corridos una fila)"),
    ("G4OBysKWMAAcpzX.jpg", "02", 3, None, None, ba([132, 1, 0, 7, 1, 1, 79, 4, 2, 1, 8, 5, 1, 2, 3], 5, 3),
     "Almirante Brown, sin circuito ni mesa"),
    ("241fa72c-b268-4b9a-bdc7-1f014ad8f2d4.png", "02", None, None, None,
     {AB["LLA"]: 120, AB["PNBA"]: 2, AB["FIT"]: 22, AB["FPF"]: 3, AB["FP"]: 65, AB["PS"]: 2, AB["PFC"]: 4,
      AB["PU"]: 11, AB["POT"]: 1, AB["NA"]: 1}, "Buenos Aires sin sección ni mesa (foto torcida; los números van "
     "una fila arriba; no se ven MAS, blanco y nulo)"),
    ("image-107.png", "02", 4, None, None, {AB["FP"]: 109, AB["LLA"]: 76, AB["FIT"]: 17, "NULO": 6},
     "Sarandí (Avellaneda), tuit: solo tres fuerzas y nulos"),
] + [("G4OPG0nWEAA2eEy.jpg", "02", 52, "380", str(m), {AB["LLA"]: a, AB["FP"]: f}, "Villa Lynch (San Martín), tuit")
     for m, a, f in [(559, 102, 77), (560, 94, 78), (561, 75, 75), (562, 93, 68), (563, 80, 80), (564, 102, 63),
                     (565, 75, 89), (566, 89, 76), (567, 78, 83), (568, 57, 45)]]
# Sin usar: el borrador de Rio Negro (conteo a medias), el borrador de Buenos Aires (11 mesas con LLA 125 / FP 65 en
# el provisorio) y la mesa de Merlo, San Luis (ninguna mesa de San Luis tiene LLA 127 y FJ 52).


def bloques():
    m = pd.read_csv(os.path.join(ROOT, "mapas", "mapa2025", "mapeo_listas_2025.csv"), dtype=str, encoding="utf-8-sig")
    grp = {"La Libertad Avanza": "LLA", "Fuerza Patria": "FP", "Provincias Unidas": "PU",
           "Frente de Izquierda y de Trabajadores - Unidad": "FIT"}
    return {(r.distrito, r.nombre.strip().upper()): grp.get(r.bloque, "OTRAS") for r in m.itertuples()}


def to_blocs(dist, votes, mp):
    out = dict.fromkeys(B + ["BN"], 0)
    for k, v in votes.items():
        if k in ("BLANCO", "NULO"):
            out["BN"] += v
        else:
            out[mp.get((dist, k.upper()), "OTRAS")] += v
    return out


def ubicar(w):
    """Cada foto -> fila del provisorio 2025. Sin numero de mesa: la unica mesa del lugar con los mismos votos de
    LLA, FP y FIT (solo para saber de donde es la foto)."""
    rows = []
    for f, d, s, c, mesa, votes, nota in FOTOS:
        x = w[w.distrito_id == d]
        if s is not None: x = x[x.seccion_id == s]
        if c is not None: x = x[x.circuito == c]
        if mesa is not None:
            x = x[x.mesa_id == mesa]
        else:
            for k in (AB["LLA"], AB["FP"], AB["FIT"]):
                if k in votes and k in x: x = x[x[k] == votes[k]]
        r = dict(foto=f, nota=nota, distrito=d, ubicada=len(x) == 1, votos=votes)
        if len(x) == 1:
            row = x.iloc[0]
            r.update(seccion=int(row.seccion_id), circuito=row.circuito, mesa=row.mesa_id, idx=x.index[0])
            r["dif_votos"] = int(sum(abs(v - int(row.get(k, 0))) for k, v in votes.items()))
            r["difs"] = "; ".join("%s: foto %d, DINE %d" % (k.title()[:28], v, int(row.get(k, 0)))
                                  for k, v in votes.items() if v != int(row.get(k, 0)))
        rows.append(r)
    return pd.DataFrame(rows)


def destino(w, mp):
    """Votos 2025 de cada mesa por bloque (LLA, FP, PU, FIT, OTRAS, BN)."""
    parties = [c for c in w.columns if c not in bt.KEY + ["e"] + bt.FIXED]
    V = pd.DataFrame(0.0, index=w.index, columns=B + ["BN"])
    for d, g in w.groupby("distrito_id"):
        for p in parties:
            V.loc[g.index, mp.get((d, p), "OTRAS")] += g[p]
        V.loc[g.index, "BN"] += g[[c for c in bt.FIXED if c in g]].sum(1)
    return V


def ajustar(Xi, Yi, ei, nat, src, lam):
    """Total nacional proyectado de cada columna de destino. Para cada columna j, regresion de Goodman con las
    mesas donde se conoce j, encogida (lam x traza media) hacia el swing uniforme: coeficiente 1 en sus columnas de
    origen mas un corrimiento comun (las filas de X suman 1, asi que un corrimiento es sumar una constante a todos
    los coeficientes). lam = inf es el swing uniforme puro; lam = 0, Goodman sin penalizar."""
    tot = np.zeros(Yi.shape[1])
    for j in range(Yi.shape[1]):
        k = ~np.isnan(Yi[:, j])
        x, y, wt = Xi[k], Yi[k, j], ei[k]
        g0 = np.zeros(x.shape[1])
        g0[src[j]] = 1
        g0 += np.average(y - x @ g0, weights=wt)         # swing uniforme de las fotos
        if np.isinf(lam):
            g = g0
        else:
            A = (x * wt[:, None]).T @ x
            C = (x * wt[:, None]).T @ y
            L = lam * np.trace(A) / len(A)
            g = np.linalg.solve(A + (L + 1e-9) * np.eye(len(A)), C + L * g0)
        tot[j] = nat @ g
    return tot


def swing(Xi, Yi, ei, di, natd, src, ratio, kd):
    """Swing por distrito: en cada distrito con fotos, el cambio de sus fotos encogido (kd mesas) hacia el cambio
    de todas las fotos; sin fotos, el de todas. ratio = columnas de destino donde el cambio es proporcional
    (destino / origen) en vez de aditivo: para fuerzas concentradas en pocas provincias. kd = inf: uniforme."""
    tot = np.zeros(Yi.shape[1])
    for j in range(Yi.shape[1]):
        k = ~np.isnan(Yi[:, j])
        x, y, wt, d = Xi[k], Yi[k, j], ei[k], di[k]
        o = x[:, src[j]].sum(1)
        prop = j in ratio and len(src[j]) > 0
        nd = np.bincount(d, minlength=len(natd))
        if prop:
            r0 = (y * wt).sum() / max((o * wt).sum(), 1e-9)
            yd = np.bincount(d, weights=y * wt, minlength=len(natd))
            od = np.bincount(d, weights=o * wt, minlength=len(natd))
            rd = np.where(od > 0, yd / np.maximum(od, 1e-9), r0)
            sh = nd / (nd + kd) if np.isfinite(kd) else 0 * nd
            r = sh * rd + (1 - sh) * r0
            tot[j] = (natd[:, src[j]].sum(1) * r).sum()
        else:
            s0 = np.average(y - o, weights=wt)
            sd = np.bincount(d, weights=(y - o) * wt, minlength=len(natd)) /                 np.maximum(np.bincount(d, weights=wt, minlength=len(natd)), 1e-9)
            sh = nd / (nd + kd) if np.isfinite(kd) else 0 * nd
            s_ = sh * sd + (1 - sh) * s0
            tot[j] = natd[:, src[j]].sum() + (s_ * ED).sum()       # las filas de X suman 1: natd suma ED
    return tot


def pct(tot):
    p = np.maximum(tot[:len(B)], 0)
    return 100 * p / p.sum()


def exportar_csv(mp):
    """fotos25/actas.csv en el formato de proyectar_fotos.py, con solo lo que se ve en cada foto: sin circuito en la
    foto (Almirante Brown, Sarandi, Villa Lynch) va vacio, y la foto torcida, que no muestra ni la seccion, queda
    afuera. Sarandi da nulos pero no blancos: el nulo no se usa."""
    filas = []
    for f, d, s, c, mesa, votes, nota in FOTOS:
        if s is None:
            continue
        circ = "" if ("Almirante" in nota or "Sarand" in nota or "Villa Lynch" in nota) else c
        completa = "no" if ("Villa Lynch" in nota or "Sarand" in nota) else "si"
        for k, v in votes.items():
            if k in ("BLANCO", "NULO"):
                if completa == "no":
                    continue
                b = k
            else:
                b = mp.get((d, k.upper()), "OTRAS")
            filas.append(dict(foto=f, distrito_id=d, seccion_id=s, circuito=circ, mesa=mesa or "", completa=completa,
                              lista=k, bloque=b, votos=v))
    pd.DataFrame(filas).to_csv(os.path.join(OUT, "actas.csv"), index=False, encoding="utf-8-sig")


def main():
    mp = bloques()
    exportar_csv(mp)
    w = pd.read_pickle(os.path.join(HERE, "mesas_2025.pkl"))
    ctl = ubicar(w)
    ctl.drop(columns=["idx", "votos"], errors="ignore").to_csv(os.path.join(OUT, "control_transcripcion.csv"),
                                                               index=False, encoding="utf-8-sig")
    V = destino(w, mp)
    real = pct(V[B].sum().to_numpy())
    # origen: presidente 2023 1.a vuelta por circuito, proporciones sobre electores con abstencion
    key = ["distrito_id", "seccion_id", "circuito"]
    o = None
    for a in ORIG.split("+"):                             # 2023p (por defecto) o 2023b
        oa = bt.load_circ(a, 0.01)
        oa.columns = [c if c in key else (c if a == "2023p" else "B:" + c) for c in oa.columns]
        o = oa if o is None else o.merge(oa, on=key, how="inner")
    ocols = [c for c in o.columns if c.endswith("(orig)")]
    Wm = w[key + ["e"]].merge(o, on=key, how="left")
    has_o = Wm[ocols].notna().all(1).to_numpy()
    e = np.maximum(w.e.to_numpy(float), V.sum(1).to_numpy())
    X = Wm[ocols].to_numpy(float)
    nat = (X[has_o] * e[has_o, None]).sum(0)
    dcode, dnames = pd.factorize(w.distrito_id)
    natd = np.zeros((len(dnames), X.shape[1]))
    np.add.at(natd, dcode[has_o], X[has_o] * e[has_o, None])
    global ED
    ED = np.bincount(dcode[has_o], weights=e[has_o], minlength=len(dnames))
    dcols = B + ["BN", "ABST"]
    oc = {c.split(" (orig)")[0]: i for i, c in enumerate(ocols)}
    if ORIG == "2023b":
        src = [[oc["B:LA LIBERTAD AVANZA"]], [oc["B:UNION POR LA PATRIA"]], [], [], [], [oc["B:BLANCO/NULO"]],
               [oc["B:ABSTENCION"]]]
    else:
        src = [[oc["LA LIBERTAD AVANZA"], oc["JUNTOS POR EL CAMBIO"]], [oc["UNION POR LA PATRIA"]],
               [oc["HACEMOS POR NUESTRO PAIS"]], [oc["FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD"]], [],
               [oc["BLANCO/NULO"]], [oc["ABSTENCION"]]]
    # fotos
    use = ctl[ctl.ubicada].reset_index(drop=True)
    fi = use.idx.to_numpy().astype(int)
    Yf = np.full((len(use), len(dcols)), np.nan)
    for i, r in use.iterrows():
        bl = to_blocs(r.distrito, r.votos, mp)
        known = {"LLA", "FP"} if "Villa Lynch" in r.nota else {"LLA", "FP", "FIT"} if "Sarand" in r.nota else \
            set(B) if "torcida" in r.nota else set(B + ["BN"])
        for j, b in enumerate(dcols[:-1]):
            if b in known: Yf[i, j] = bl[b] / e[fi[i]]
        if known == set(B + ["BN"]): Yf[i, -1] = 1 - sum(bl.values()) / e[fi[i]]
    ok = has_o[fi]
    use, fi, Yf = use[ok].reset_index(drop=True), fi[ok], Yf[ok]
    Xf, ef = X[fi], e[fi]
    circ_id = pd.factorize(use.distrito + "|" + use.seccion.astype(int).astype(str) + "|" + use.circuito)[0]
    nc = circ_id.max() + 1
    rng = np.random.default_rng(2025)
    crudo = np.nansum(Yf[:, :len(B)] * ef[:, None], 0)
    RAT = [2, 3]                                          # PU y FIT: cambio proporcional
    METH = [("Swing uniforme sobre 2023", np.inf), ("Goodman encogido al swing (lam=1)", 1.0),
            ("Goodman encogido al swing (lam=0,1)", 0.1), ("Goodman sin encoger", 0.0),
            ("Swing uniforme, proporcional en PU y FIT", ("sw", RAT, np.inf)),
            ("Swing por provincia (k=5)", ("sw", [], 5.0)),
            ("Swing por provincia (k=5), proporcional en PU y FIT", ("sw", RAT, 5.0))]

    def proj(spec, idx, Xs, Ys, es, ds):
        if isinstance(spec, tuple):
            return pct(swing(Xs[idx], Ys[idx], es[idx], ds[idx], natd, src, spec[1], spec[2]))
        return pct(ajustar(Xs[idx], Ys[idx], es[idx], nat, src, spec))
    df_ = dcode[fi]
    allf = np.arange(len(fi))
    res = {}
    for name, lam in METH:
        pt = proj(lam, allf, Xf, Yf, ef, df_)
        bs = []
        for _ in range(500):
            idx = np.concatenate([np.where(circ_id == c)[0] for c in rng.choice(nc, nc)])
            bs.append(proj(lam, idx, Xf, Yf, ef, df_))
        bs = np.array(bs)
        res[name] = (pt, np.percentile(bs, 2.5, 0), np.percentile(bs, 97.5, 0))
    # misma cantidad de mesas completas, pero al azar en todo el pais y al azar en el conurbano
    Yall = np.column_stack([V.to_numpy(), e - V.sum(1).to_numpy()]) / np.maximum(e, 1)[:, None]
    good = has_o & (V.sum(1).to_numpy() > 0)
    gba = good & (w.distrito_id == "02").to_numpy() & np.isin(w.seccion_id.to_numpy(), GBA)
    n = len(use)
    azar = {}
    for lbl, pool in (("al azar en todo el país", np.where(good)[0]), ("al azar en el conurbano", np.where(gba)[0])):
        err = {name: [] for name, _ in METH}
        for _ in range(300):
            idx = rng.choice(pool, n, replace=False)
            for name, lam in METH:
                p = proj(lam, idx, X, Yall, e, dcode)
                err[name].append(np.abs(p[:2] - real[:2]).mean())
        azar[lbl] = {k: np.mean(v) for k, v in err.items()}
    # ---- informe ----
    L = ["# Fotos de actas 2025 pasadas por el modelo con solo los datos de 2023", "",
         "Generado por `proyeccion/fotos25.py`. %d fotos usables, %d mesas en %d circuitos. Diez mesas de Villa Lynch "
         "(tuit) solo dan LLA y FP; Sarandí (tuit) solo LLA, FP, FIT y nulos. Origen: presidente 2023, 1.ª vuelta, por "
         "circuito (las mesas cambian de número entre elecciones). Bloques de diputados 2025 como en "
         "`mapas/mapa2025/mapeo_listas_2025.csv`: «PU» = Provincias Unidas y sus listas provinciales, «FP» = Fuerza "
         "Patria y las listas peronistas de cada provincia." % (len(set(use.foto)), len(use), nc), "",
         "## Transcripción contra el provisorio de la DINE", "",
         "| Foto | Lugar | Sección / circuito / mesa | Votos distintos | Detalle |", "|---|---|---|---:|---|"]
    for r in ctl.itertuples():
        L.append("| %s | %s | %s | %s | %s |" % (r.foto, r.nota, "%d / %s / %s" % (r.seccion, r.circuito, r.mesa)
                 if r.ubicada else "no ubicada", int(r.dif_votos) if r.ubicada else "",
                 r.difs if r.ubicada and isinstance(r.difs, str) else ""))
    L += ["", "## Proyección nacional de diputados (% sobre los votos de los cinco bloques)", "",
          "| Método | " + " | ".join(B) + " | Error LLA−FP |", "|---|" + "---:|" * (len(B) + 1)]
    cp = pct(crudo)
    L.append("| Crudo (suma de las fotos) | " + " | ".join("%.1f" % v for v in cp) + " | %+.1f |" % (
        (cp[0] - cp[1]) - (real[0] - real[1])))
    for name, _ in METH:
        pt, lo, hi = res[name]
        L.append("| %s | " % name + " | ".join("%.1f (%.1f–%.1f)" % t for t in zip(pt, lo, hi)) +
                 " | %+.1f |" % ((pt[0] - pt[1]) - (real[0] - real[1])))
    L.append("| **Real (provisorio DINE)** | " + " | ".join("**%.1f**" % v for v in real) + " | |")
    L += ["", "Entre paréntesis, banda del 95 %% por bootstrap de los %d circuitos. No cubre el sesgo de selección." % nc,
          "", "## ¿Cuánto es mala suerte de las fotos? Misma cantidad de mesas (%d, completas) al azar" % n, "",
          "Error absoluto medio de LLA y FP (puntos), 300 sorteos:", "",
          "| Método | " + " | ".join(azar) + " |", "|---|" + "---:|" * len(azar)]
    for name, _ in METH:
        L.append("| %s | " % name + " | ".join("%.2f" % azar[k][name] for k in azar) + " |")
    open(os.path.join(OUT, "RESUMEN.md" if ORIG == "2023p" else "RESUMEN_%s.md" % ORIG.replace("+", "_")), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[L.index("## Proyección nacional de diputados (% sobre los votos de los cinco bloques)"):]))


# conurbano (24 partidos), secciones de la DINE; se completa en main() con los nombres de ambitosElectorales.csv
GBA = []


if __name__ == "__main__":
    a = pd.read_csv(os.path.join(ROOT, "datos_oficiales", "2025", "x", "ambitosElectorales.csv"), dtype=str)
    a = a[a.distrito_id == "02"].drop_duplicates("seccion_id")
    NOM = ["ALMIRANTE BROWN", "AVELLANEDA", "BERAZATEGUI", "ESTEBAN ECHEVERR", "EZEIZA", "FLORENCIO VARELA",
           "GENERAL SAN MART", "HURLINGHAM", "ITUZAING", "JOSE C. PAZ", "JOSÉ C. PAZ", "LA MATANZA", "LAN", "LOMAS DE ZAMORA",
           "MALVINAS ARGENTINAS", "MERLO", "MORENO", "MOR", "QUILMES", "SAN FERNANDO", "SAN ISIDRO", "SAN MIGUEL",
           "TIGRE", "TRES DE FEBRERO", "VICENTE L"]
    up = a.seccion_nombre.str.upper()
    sel = up.apply(lambda s: any(s.startswith(n) for n in NOM))
    GBA += a[sel].seccion_id.astype(int).tolist()
    print("conurbano:", sorted(zip(a[sel].seccion_id.astype(int), a[sel].seccion_nombre)), flush=True)
    main()
