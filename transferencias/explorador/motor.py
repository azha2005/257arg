"""Estimación rápida de una matriz de transferencias entre dos elecciones cualesquiera del catálogo.

Mismo método que estimar.py (RxC penalizado de E. Calvo, una matriz por provincia encogida hacia la nacional),
sin bootstrap: una sola estimación puntual. La penalización se elige por validación cruzada (5 grupos de unidades)
como en estimar.py; con `rapido=True` se usa la fija 2e-6.

Unidades:
- Provinciales preparadas (pr:…) con su contraparte: empalme auditado, también si se elige la nacional curada.
- Dos elecciones con pkl de circuitos (pkl:…): estimar.prepare, con las correspondencias revisadas de cada par.
- Cualquier otro par: departamentos emparejados por nombre dentro de cada provincia. Si los emparejados cubren
  menos del 75 % de los votos de la provincia en alguna de las dos, la provincia entra como una sola unidad."""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import datos                                     # noqa: E402
from datos import estimar                        # noqa: E402
from rxc_calvo import fit                        # noqa: E402
from auditar import SEPARACION_MIN, NO_PARTIDO   # noqa: E402  (mismos umbrales que los sankeys publicados)

COBERTURA_DEPTO = .75
RATIO = (0.5, 2.0)            # cambio de tamaño admitido de una unidad, relativo al cambio mediano
LAMBDA_RAPIDA = 2e-6
PARES = os.path.join(datos.CACHE, "pares"); os.makedirs(PARES, exist_ok=True)
VERSION = 7                   # cambiar si cambia el cálculo: invalida los resultados guardados


def alinear(o, d):
    """Selecciona primero empalmes provinciales auditados; después los cruces generales."""
    preparado = datos.par_preparado(o, d)
    if preparado is not None:
        A, B, meta = preparado
        if not A.index.equals(B.index):
            raise ValueError("El empalme provincial preparado tiene unidades diferentes en ambos lados.")
        prov = datos.prov_canon(meta["nombre"])
        modo = meta.get("nivel", "departamentos")
        info = {prov: dict(unidades=len(A), modo=modo, empalme_verificado=True,
                          cobertura_origen=meta.get("cobertura_origen"),
                          cobertura_destino=meta.get("cobertura_destino"))}
        notas = ["Empalme provincial verificado: %d unidades (%s). Se conservan las categorías del cruce preparado." % (len(A), modo)]
        for campo in ("nota", "fuente"):
            if meta.get(campo): notas.append(meta[campo])
        if meta.get("base"): notas.append("Base del empalme: %s." % meta["base"])
        if meta.get("pendientes"):
            notas.append("El empalme conserva %d exclusiones o pendientes documentados, sin imputarlos." % len(meta["pendientes"]))
        return A, B, info, notas, "departamentos" if modo in ("departamentos", "municipios") else "circuitos"
    notas = []
    if o.startswith("pkl:") and d.startswith("pkl:"):
        alin, motivo = _alinear_circuitos(o, d)
        if alin is not None:
            return (*alin, "circuitos")
        notas.append("No se pudo cruzar por circuito (%s): se cruza por departamento." % motivo)
    A, B, info, n2 = _alinear_departamentos(datos.tabla_departamentos(o), datos.tabla_departamentos(d))
    return A, B, info, notas + n2, "departamentos"


def _alinear_circuitos(o, d):
    """Par de pkl: unidades de estimar.prepare (circuitos, con correspondencias). None si no sirve."""
    k0, k1 = (int(x) if x.isdigit() else x for x in (o[4:], d[4:]))
    try:
        A, B, XA, YB, w, rows, cols, ctl = estimar.prepare(k0, k1)
    except Exception as e:
        return None, "sin cruce por circuito (%s)" % type(e).__name__
    if len(A) < 30 or ctl["electores_origen_usados"] < .5 * ctl["electores_origen_total"]:
        return None, "pocos circuitos en común"
    A = A.copy(); B = B.copy()
    prov = [estimar.DISTRITOS.get(x, x) for x in A.index.get_level_values(0)]
    idx = pd.MultiIndex.from_arrays([prov, ["%s|%s" % (s, c) for _, s, c in A.index]], names=["prov", "u"])
    A.index = idx; B.index = idx
    info = {p: dict(unidades=int(n), modo="circuitos y secciones") for p, n in pd.Series(prov).value_counts().items()}
    nota = "Unidades: %d circuitos/secciones en común (estimar.prepare, con las correspondencias revisadas del par); %s del padrón de origen." % (
        len(A), _pct(ctl["electores_origen_usados"] / ctl["electores_origen_total"]))
    return (A, B, info, [nota]), None


def _pct(x):
    return ("%.1f" % (100 * x)).replace(".", ",") + " %"


def _alinear_departamentos(TA, TB):
    """Departamentos por nombre; provincias con mala cobertura, enteras. Devuelve A, B, info por provincia, notas."""
    A_rows, B_rows, keys, info = [], [], [], {}
    sa, sb = TA.drop(columns="No votó", errors="ignore").sum(1), TB.drop(columns="No votó", errors="ignore").sum(1)
    provs = sorted(set(TA.index.get_level_values(0)) & set(TB.index.get_level_values(0)))
    for p in provs:
        a, b = TA.loc[p], TB.loc[p]
        par = datos.emparejar(list(a.index), list(b.index))
        ca = sa.loc[p].reindex(list(par)).sum() / sa.loc[p].sum()
        cb = sb.loc[p].reindex(list(par.values())).sum() / sb.loc[p].sum()
        if len(par) >= 2 and (min(ca, cb) >= COBERTURA_DEPTO or max(ca, cb) >= .95):   # o una es parte de la otra (AMBA, parciales)
            for ua, ub in par.items():
                A_rows.append(a.loc[ua]); B_rows.append(b.loc[ub]); keys.append((p, ua))
            info[p] = dict(unidades=len(par), modo="departamentos", cobertura=round(float(min(ca, cb)), 3))
        else:
            A_rows.append(a.sum(min_count=1)); B_rows.append(b.sum(min_count=1)); keys.append((p, "(provincia entera)"))
            if "No votó" in a and a["No votó"].isna().any(): A_rows[-1]["No votó"] = np.nan
            if "No votó" in b and b["No votó"].isna().any(): B_rows[-1]["No votó"] = np.nan
            info[p] = dict(unidades=1, modo="provincia entera", cobertura=round(float(min(ca, cb)), 3) if par else 0.0)
    idx = pd.MultiIndex.from_tuples(keys, names=["prov", "u"])
    A = pd.DataFrame(A_rows, index=idx).reindex(columns=TA.columns)
    B = pd.DataFrame(B_rows, index=idx).reindex(columns=TB.columns)
    return A, B, info, []


def _base_comun(A, B, notas):
    """«No votó» solo si las dos elecciones tienen electores en (casi) todas las unidades; si no, votos emitidos."""
    tiene = "No votó" in A and "No votó" in B
    if tiene:
        ok = A["No votó"].notna() & B["No votó"].notna()
        peso = B.drop(columns="No votó").sum(1)
        if peso[ok].sum() >= .9 * peso.sum():
            if (~ok).any():
                notas.append("Sin electores en %d unidades: quedan afuera." % (~ok).sum())
            return A[ok], B[ok], True
    if "Blanco" in A and "Blanco" in B:
        notas.append("Base: votos válidos (positivos + blancos), sin nulos ni abstención.")
    else:
        notas.append("Base: votos emitidos (sin «No votó»); faltan electores en al menos una de las elecciones.")
    return A.drop(columns="No votó", errors="ignore"), B.drop(columns="No votó", errors="ignore"), False


def _filtro_tamano(A, B, notas):
    ea, eb = A.sum(1), B.sum(1)
    ok = (ea > 0) & (eb > 0)
    crec = float((eb[ok] / ea[ok]).median())
    ok &= (eb / ea / crec).between(*RATIO)
    if (~ok).sum():
        notas.append("Descartadas %d unidades cuyo tamaño cambia mucho más que el resto (fuera de ×%s–×%s del cambio mediano)." % (
            (~ok).sum(), str(RATIO[0]).replace(".", ","), str(RATIO[1]).replace(".", ",")))
    return A[ok], B[ok]


def _fit_prov(X, Y, lam, w, g0):
    return estimar.fit_prov(X, Y, lam * len(w), w, g0)


def _cv(XA, YB, w, g0, provs, folds=5):
    rng = np.random.default_rng(1)
    acc = {lam: [0., 0.] for lam in estimar.LAMBDAS}
    for p in provs:
        X, Y, wp = XA.loc[p].values, YB.loc[p].values, w.loc[p].values
        if len(X) < 10: continue
        fd = rng.integers(0, folds, len(X))
        for lam in estimar.LAMBDAS:
            for k in range(folds):
                tr, te = fd != k, fd == k
                if te.sum() == 0 or tr.sum() < 5: continue
                Bp = _fit_prov(X[tr], Y[tr], lam, wp[tr], g0)
                acc[lam][0] += (wp[te, None] * (X[te] @ Bp - Y[te])[:, :-1] ** 2).sum(); acc[lam][1] += wp[te].sum()
    cv = {lam: e / t for lam, (e, t) in acc.items() if t > 0}
    if not cv: return LAMBDA_RAPIDA, None
    return max(k for k, v in cv.items() if v <= 1.01 * min(cv.values())), cv


def _separacion(M):
    """½·Σ|fila − promedio| de cada fila, en puntos, y peso de cada fila (% del total)."""
    tot = M.sum()
    P = 100 * M / np.maximum(M.sum(1, keepdims=True), 1e-9)
    marg = 100 * M.sum(0) / max(tot, 1e-9)
    return .5 * np.abs(P - marg).sum(1), 100 * M.sum(1) / max(tot, 1e-9), P


def _sep_media(sep, peso, rows):
    big = [i for i, r in enumerate(rows) if peso[i] >= 5 and r not in NO_PARTIDO]
    return float((sep[big] * peso[big]).sum() / peso[big].sum()) if big else float("nan")


def auditoria(M, Bc, rows, cols, por, real):
    """Los criterios de auditar.py sobre la estimación puntual (sin el ancho del bootstrap, que acá no hay):
    fila no identificada (difiere de la variante de Calvo en más de 30 puntos, o 20 si pesa menos de 5 %), fila cerca del
    promedio (5 % o más del padrón y separación menor a SEPARACION_MIN), matriz poco informativa (separación media de las
    filas grandes menor a SEPARACION_MIN) y provincias donde un destino recibe más del 125 % de sus votos reales."""
    sep, peso, P = _separacion(M)
    sep_c, _, _ = _separacion(Bc * M.sum(1, keepdims=True))
    Q = 100 * Bc
    filas = []
    for i, r in enumerate(rows):
        dif = np.abs(P[i] - Q[i])
        filas.append(dict(origen=r, peso=round(float(peso[i]), 1), dif_calvo=round(float(dif.max()), 1), celda=cols[int(dif.argmax())],
                          sep=round(float(sep[i]), 1), sep_calvo=round(float(sep_c[i]), 1),
                          no_identificada=bool(dif.max() > 30 or (peso[i] < 5 and dif.max() > 20)),
                          cerca_promedio=bool(peso[i] >= 5 and r not in NO_PARTIDO and sep[i] < SEPARACION_MIN)))
    s = _sep_media(sep, peso, rows)
    prov = {}
    for p, Mpv in por.items():
        sp, wp, _ = _separacion(Mpv)
        sm = _sep_media(sp, wp, rows)
        prov[p] = dict(separacion=None if np.isnan(sm) else round(sm, 1), poco_informativa=bool(sm < SEPARACION_MIN),
                       cerca=[r for i, r in enumerate(rows) if wp[i] >= 5 and r not in NO_PARTIDO and sp[i] < SEPARACION_MIN],
                       imposibles=[dict(destino=c, estimado=int(Mpv[:, j].sum()), real=int(real[p][j]))
                                   for j, c in enumerate(cols) if Mpv[:, j].sum() > 1.25 * real[p][j] + 2000])
    return dict(separacion=None if np.isnan(s) else round(s, 1), poco_informativa=bool(s < SEPARACION_MIN),
                umbral=SEPARACION_MIN, filas=filas, provincias=prov)


def calcular(o, d, rapido=False):
    t0 = time.time()
    clave = hashlib.md5(json.dumps([VERSION, o, d, rapido]).encode()).hexdigest()[:16]
    f = os.path.join(PARES, clave + ".json")
    if os.path.exists(f):
        return json.load(open(f, encoding="utf8"))
    A, B, info, notas, nivel = alinear(o, d)
    A, B, nv = _base_comun(A, B, notas)
    A, B = A.fillna(0), B.fillna(0)
    A, B = A.loc[:, A.sum() > 0], B.loc[:, B.sum() > 0]
    # Los empalmes provinciales ya tienen controles y exclusiones propios.
    # Volver a filtrarlos por cambio de participación descartaría áreas válidas.
    if not all(v.get("empalme_verificado") for v in info.values()):
        A, B = _filtro_tamano(A, B, notas)
    if len(A) < 3:
        pa, pb = (sorted(set(datos.tabla(x).index.get_level_values(0))) for x in (o, d))
        comun = sorted(set(pa) & set(pb))
        lista = lambda ps: ", ".join(ps) if len(ps) <= 4 else "%d provincias" % len(ps)
        raise ValueError("Menos de 3 unidades en común: no se puede estimar. Origen: %s; destino: %s; en las dos: %s." % (
            lista(pa), lista(pb), lista(comun) if comun else "ninguna"))
    rows, cols = list(A.columns), list(B.columns)
    XA = A.div(A.sum(1), axis=0); YB = B.div(B.sum(1), axis=0)
    w = B.sum(1) / B.sum(1).mean()
    V = XA.mul(B.sum(1), axis=0)
    provs = list(dict.fromkeys(A.index.get_level_values(0)))
    Bn = fit(XA.values, YB.values, const=0.001, w=w.values)
    Bn = np.clip(Bn, 1e-9, None)
    g0 = np.log(Bn[:, :-1] / Bn[:, -1:]).ravel()
    if rapido:
        lam, cv = LAMBDA_RAPIDA, None
    else:
        lam, cv = _cv(XA, YB, w, g0, provs)
    M = 0; por = {}
    for p in provs:
        Bp = _fit_prov(XA.loc[p].values, YB.loc[p].values, lam, w.loc[p].values, g0)
        P = Bp * V.loc[p].sum().values[:, None]
        por[p] = P; M = M + P
    # Variante «Calvo» (una matriz nacional, sin pesos, penalización 0.001 hacia cero), para la auditoría de auditar.py
    Bc = fit(XA.values, YB.values, const=0.001)
    Mp = M / np.maximum(M.sum(1, keepdims=True), 1e-9)
    real = {p: B.loc[p].sum().values for p in provs}
    aud = auditoria(M, Bc, rows, cols, por, real)
    pred = XA.values @ Mp
    rmse = float(np.sqrt(np.average(((pred - YB.values) * 100) ** 2, axis=0, weights=w.values)).mean())
    a0, a1 = datos.anio(o), datos.anio(d)
    if abs(a1 - a0) > 12:
        notas.append("Las elecciones están separadas por %d años: el padrón se renovó en buena parte y las cintas no siguen a las mismas personas. Leer como comparación de geografías." % abs(a1 - a0))
    if a1 < a0:
        notas.append("El destino es anterior al origen: la matriz es matemáticamente válida pero no describe un traspaso.")
    nprov_entera = sum(1 for v in info.values() if v["modo"] == "provincia entera")
    if nprov_entera:
        notas.append("%d provincias entran como una sola unidad (nombres de departamento que no coinciden o cobertura parcial): su matriz es casi la nacional." % nprov_entera)
    base = "padrón" if nv else "votos válidos (positivos + blancos)" if "Blanco" in rows + cols else "votos emitidos"
    out = dict(origen=o, destino=d, nivel=nivel, base=base, rows=rows, cols=cols,
               nacional=np.round(M, 1).tolist(), provincias={p: np.round(por[p], 1).tolist() for p in provs},
               info={p: dict(info.get(p, {}), unidades_usadas=int(len(A.loc[p]))) for p in provs},
               lambda_=lam, cv={str(k): v for k, v in (cv or {}).items()}, auditoria=aud,
               no_identificadas=[f["origen"] for f in aud["filas"] if f["no_identificada"]],
               rmse_pp=round(rmse, 2), unidades=int(len(A)), notas=notas, segundos=round(time.time() - t0, 1),
               colores=datos.colores(rows + cols))
    json.dump(out, open(f, "w", encoding="utf8"), ensure_ascii=False)
    return out
