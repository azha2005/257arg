"""La noche de la eleccion: proyeccion nacional con las actas que se van juntando (fotos) y la eleccion anterior.
    python proyeccion/proyectar_fotos.py proyeccion/fotos25/actas.csv                    # origen presidente 2023
    python proyeccion/proyectar_fotos.py actas.csv --origen 2023p --real 2025bl          # contra el resultado real
    python proyeccion/proyectar_fotos.py actas.csv --origen 2023p,2025bl                 # 2027: promedio de los dos
Entrada: un CSV (UTF-8) con una fila por acta y fuerza:
    foto, distrito_id, seccion_id, circuito, mesa, completa, bloque, votos
  distrito_id con dos cifras (01 Capital, 02 Buenos Aires...), seccion_id y circuito como en el acta (el circuito
  puede ir vacio: se usa la seccion). completa = si cuando el acta trae todas las fuerzas y blanco y nulo; no cuando
  la fuente da solo algunas (un tuit con LLA y FP): ahi solo cuentan las fuerzas que estan. bloque = el bloque de la
  lista (LLA, FP, PU, FIT, OTRAS...) o BLANCO / NULO; varias listas del mismo bloque pueden ir en filas separadas.
Modelo (elegido con proyeccion/fotos_sim.py, ver fotos_sim/RESUMEN.md): cada acta contra el resultado de su
circuito en la eleccion de origen; regresion de Goodman por fuerza, encogida (lam = 0,1) hacia el swing uniforme, con
las actas repesadas para que el AMBA y el resto del pais pesen lo que pesan en el padron. Banda: bootstrap de los
circuitos, ensanchada x FACTOR (con ~30 actas armadas como las de Twitter el bootstrap solo cubre ~85 %).
Los electores de cada mesa no estan en el acta: se usa el promedio por mesa del circuito en la eleccion de origen."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
import fotos_modelo as fm

LAM = 0.1
KIND = "goodman"                  # "goodman_prop": ancla de cambio proporcional (Israel); no mejora, ver LEEME
FACTOR = 1.4
NBOOT = 2000
# antecesor de cada bloque en la eleccion de origen (agrupacion_id de transferencias/circ_<origen>.pkl)
ANTECESORES = {"2023p": {"LLA": ["LA LIBERTAD AVANZA", "JUNTOS POR EL CAMBIO"], "FP": ["UNION POR LA PATRIA"],
                         "PU": ["HACEMOS POR NUESTRO PAIS"], "FIT": ["FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD"]},
               "2021bl": {"LLA": ["LLA", "JxC"], "FP": ["FdT"], "PU": ["Tercera Via"]},
               "2025bl": {}}                                    # diputados 2025 en bloques: cada bloque es su antecesor
# Para 2027 hay que revisar estos antecesores con los bloques que se presenten (los nombres de la columna «bloque»
# del CSV de actas). Un bloque sin antecesor se proyecta por su nivel medio en las actas (sirve poco).


def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def norm_circ(c):
    c = str(c).strip().upper()
    return (c.lstrip("0") or "0") if c not in ("", "NAN", "NONE") else ""


def origen(arg):
    """Proporciones por circuito sobre electores (con abstencion), electores por circuito y mesas por circuito."""
    own = os.path.join(HERE, "circ_%s.pkl" % arg)                # bloques.py: diputados en bloques
    v, elect = pd.read_pickle(own if os.path.exists(own) else os.path.join(ROOT, "transferencias", "circ_%s.pkl" % arg))
    t = v.votos_tipo.str.upper()
    v = v.assign(col=np.where(t.str.startswith("POSITIVO"), v.agrupacion_id, "BLANCO/NULO"))
    w = v.groupby(["distrito_id", "seccion_id", "circuito", "col"]).v.sum().unstack(fill_value=0)
    w = w.join(elect.rename("e_o"), how="inner")
    cols = [c for c in w.columns if c != "e_o"]
    w["e_o"] = np.maximum(w.e_o, w[cols].sum(1))
    p = w[cols].div(w.e_o, axis=0)
    p["ABSTENCION"] = 1 - p.sum(1)
    mp = os.path.join(HERE, "mesas_%s.pkl" % arg)
    if os.path.exists(mp):
        m = pd.read_pickle(mp)
        m["seccion_id"] = m.seccion_id.astype(int)
        nm = m.groupby(["distrito_id", "seccion_id", "circuito"]).size()
    else:
        nm = None
    return p, w.e_o, nm


def leer(path):
    """CSV de actas normalizado (una fila por acta y fuerza)."""
    a = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    a["votos"] = pd.to_numeric(a.votos).fillna(0)
    a["distrito_id"] = a.distrito_id.str.zfill(2)
    a["seccion_id"] = a.seccion_id.astype(int)
    a["circuito"] = a.circuito.map(norm_circ)
    a["bloque"] = a.bloque.str.strip().str.upper().replace({"BLANCO": "BN", "NULO": "BN", "BLANCOS": "BN", "NULOS": "BN"})
    a["mesa_key"] = a.foto + "|" + a.distrito_id + "|" + a.seccion_id.astype(str) + "|" + a.circuito + "|" + a.mesa
    return a


_ORIGENES = {}


def calcular(a, orig, nboot=NBOOT, seed=0):
    """Proyeccion, banda y remuestras con las actas a (de leer()) y los origenes orig ("2023p" o "2023p,2021bl").
    Devuelve un dict con lo que usa el informe (y aguja_fotos.py)."""
    blocs =[b for b in a.bloque.unique() if b != "BN"]
    blocs = sorted(blocs, key=lambda b: -a.loc[a.bloque == b, "votos"].sum())
    dcols = blocs + ["BN", "ABSTENCION"]
    origs = orig.split(",")                               # con dos o mas, se promedian las proyecciones
    O = []
    for o in origs:
        if o not in _ORIGENES:
            _ORIGENES[o] = origen(o)
        P, E, NM = _ORIGENES[o]
        ocols = list(P.columns)
        ant = ANTECESORES.get(o, {})
        src = [[ocols.index(c) for c in ant.get(b, [b]) if c in ocols] for b in blocs] +               [[ocols.index("BLANCO/NULO")], [ocols.index("ABSTENCION")]]
        dist_codes = sorted(P.index.get_level_values(0).unique())
        dP = P.mul(E, axis=0).groupby(level=0).sum().reindex(dist_codes)
        O.append(dict(nombre=o, P=P, E=E, NM=NM, Ps=P.mul(E, axis=0).groupby(level=[0, 1]).sum(),
                      Es=E.groupby(level=[0, 1]).sum(), NMs=NM.groupby(level=[0, 1]).sum() if NM is not None else None,
                      src=src, dmap={d: i for i, d in enumerate(dist_codes)}, natd=dP[ocols].to_numpy(float),
                      ed=E.groupby(level=0).sum().reindex(dist_codes).to_numpy(float), x=[], dcodes=dist_codes))
        sin = [b for b, sr in zip(blocs, src) if not sr]
        if sin:
            print("aviso: sin antecesor en %s: %s (se proyectan por su nivel medio)" % (o, ", ".join(sin)))

    def buscar(Oo, key):
        """Origen del acta: su circuito; sin circuito (o uno que no esta), su seccion."""
        if key[2] and key in Oo["P"].index:
            nm = Oo["NM"].get(key, np.nan) if Oo["NM"] is not None else np.nan
            return Oo["P"].loc[key].to_numpy(float), Oo["E"].loc[key], nm, "circuito"
        if key[:2] in Oo["Ps"].index:
            nm = Oo["NMs"].get(key[:2], np.nan) if Oo["NMs"] is not None else np.nan
            return (Oo["Ps"].loc[key[:2]] / Oo["Es"].loc[key[:2]]).to_numpy(float), Oo["Es"].loc[key[:2]], nm, "seccion"
        return None
    rows, notas = [], []
    for k, g in a.groupby("mesa_key", sort=False):
        r = g.iloc[0]
        key = (r.distrito_id, r.seccion_id, r.circuito)
        found = [buscar(Oo, key) for Oo in O]
        if any(f is None for f in found):
            notas.append("sin origen: %s (distrito %s, seccion %s, circuito %s) -> se descarta" % (r.foto, *key))
            continue
        _, ec, nm, nivel = found[0]
        e_m = ec / nm if np.isfinite(nm) and nm > 0 else 330.0   # electores de la mesa: promedio del circuito
        vb = g.groupby("bloque").votos.sum()
        completa = r.completa.strip().lower() in ("si", "sí", "s", "1", "true")
        e_m = max(e_m, vb.sum()) if completa else e_m
        y = np.full(len(dcols), np.nan)
        for j, b in enumerate(dcols[:-1]):
            if completa or b in vb.index:
                y[j] = vb.get(b, 0) / e_m
        if completa:
            y[-1] = 1 - vb.sum() / e_m
        for Oo, f in zip(O, found):
            Oo["x"].append(f[0])
        rows.append(dict(foto=r.foto, distrito_id=r.distrito_id, seccion_id=r.seccion_id, circuito=r.circuito,
                         mesa=r.mesa, nivel=nivel, e=e_m, y=y, completa=completa))
    F = pd.DataFrame(rows)
    Y, e = np.vstack(F.y), F.e.to_numpy(float)
    for Oo in O:
        Oo["X"] = np.vstack(Oo["x"])
        Oo["d"] = F.distrito_id.map(Oo["dmap"]).to_numpy()
    P0, E0 = O[0]["P"], O[0]["E"]
    reg_all = fm.region(P0.index.get_level_values(0), P0.index.get_level_values(1), "amba")
    share = pd.Series(E0.to_numpy(float)).groupby(reg_all).sum().pipe(lambda s: s / s.sum()).to_dict()
    s_f = fm.region(F.distrito_id, F.seccion_id, "amba")
    pos = list(range(len(blocs)))

    def proj(idx, spec=(KIND, LAM), ps=True):
        w = fm.poststrat(e[idx], s_f[idx], share) if ps else e[idx]
        return np.mean([fm.pct(fm.project(spec, Oo["X"][idx], Y[idx], w, Oo["d"][idx], Oo["natd"], Oo["ed"],
                                          Oo["src"]), pos) for Oo in O], axis=0)
    def proj_d(idx):
        """Votos proyectados por distrito (DataFrame distrito x columna de destino), promedio de los origenes."""
        w = fm.poststrat(e[idx], s_f[idx], share)
        fr = [pd.DataFrame(fm.goodman(Oo["X"][idx], Y[idx], w, None, Oo["src"], LAM, prop=KIND == "goodman_prop",
                                      natd=Oo["natd"]), index=Oo["dcodes"], columns=dcols) for Oo in O]
        return sum(fr) / len(fr)
    allx = np.arange(len(F))
    pt = proj(allx)
    clus = pd.factorize(F.distrito_id + "|" + F.seccion_id.astype(str) + "|" + F.circuito)[0]
    rng = np.random.default_rng(seed)
    bs = fm.bootstrap(proj, clus, nboot, rng)
    bs = pt + FACTOR * (bs - bs.mean(0))                          # ensanchada alrededor del punto
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
    o1, o2 = np.argsort(-pt)[:2]
    marg = bs[:, o1] - bs[:, o2]
    por_origen = {Oo["nombre"]: fm.pct(fm.project(("goodman", LAM), Oo["X"], Y, fm.poststrat(e, s_f, share), Oo["d"],
                                                   Oo["natd"], Oo["ed"], Oo["src"]), pos) for Oo in O}
    crudo = np.nansum(Y[:, pos] * e[:, None], 0)
    crudo = 100 * crudo / crudo.sum()
    swing = proj(allx, ("swing", np.inf), ps=False)
    return dict(actas=a, F=F, blocs=blocs, origs=origs, pt=pt, bs=bs, lo=lo, hi=hi, o1=o1, o2=o2, marg=marg, clus=clus,
                por_origen=por_origen, crudo=crudo, swing=swing, s_f=s_f, share=share, notas=notas, P=P, E=E,
                proj_d=proj_d, pad=dict(zip(O[0]["dcodes"], O[0]["ed"])), rng=rng)


def congreso_html(R, anio, out, real=None, nboot=300):
    """Bancas de Diputados que se renuevan en anio (D'Hondt por distrito sobre la proyeccion por distrito; banda por
    bootstrap de circuitos, ensanchada como la nacional), la camara completa con las bancas que no se renuevan, el mapa
    por provincia y un HTML con las tablas al final. Devuelve lineas para el informe .md."""
    import congreso as cg
    blocs, F, clus = R["blocs"], R["F"], R["clus"]
    Dpt = R["proj_d"](np.arange(len(F)))[blocs]
    bs = fm.bootstrap(lambda k: R["proj_d"](k)[blocs].to_numpy(), clus, nboot, R["rng"])
    bs = np.maximum(Dpt.to_numpy()[None] + FACTOR * (bs - bs.mean(0)), 0)
    Dpt, pnotas = cg.provinciales(Dpt, anio, R.get("actas"))     # partidos de los gobernadores (provinciales.csv)
    por, tot = cg.repartir(Dpt, anio, R["pad"])
    sims = [cg.repartir(cg.provinciales(pd.DataFrame(b, index=Dpt.index, columns=blocs), anio, R.get("actas"),
                                        R["rng"])[0], anio, R["pad"])[1] for b in bs]
    fz = sorted({f for t in sims + [tot] for f in t}, key=lambda f: cg.ORDEN.index(f) if f in cg.ORDEN else 99)
    S = pd.DataFrame([{f: t.get(f, 0) for f in fz} for t in sims])
    prev = cg.no_renuevan(anio)
    cont = {"UxP": "FP", "HxNP": "PU"}                           # continuidad 2023 -> 2025 para la camara completa
    total = dict(tot)
    for f, b in prev.items():
        k = cont.get(f, f)
        total[k] = total.get(k, 0) + b
    nren = sum(cg.renuevan(anio).values())
    rr = cg.electos(anio)[1] if real else None
    pos = [b for b in Dpt.columns if b != "OTRAS"]
    pct = 100 * Dpt.div(Dpt.sum(1), axis=0)
    gan = {d: Dpt.loc[d, pos].idxmax() for d in Dpt.index}       # mapa: fuerza con mas votos (sin OTRAS)
    gan = {d: "PROV" if g.startswith("PROV:") else g for d, g in gan.items()}
    det = {d: "%s: %s. Bancas: %s" % (cg.DIST[d], ", ".join("%s %.0f %%" % (b, pct.loc[d, b]) for b in
           pct.loc[d].sort_values(ascending=False).index[:3]), ", ".join("%s %d" % kv for kv in por[d].items()))
           for d in Dpt.index}
    nom = lambda f: cg.FUERZAS.get(f, (f,))[0]
    h1 = cg.hemiciclo_svg(cg.ordenar(tot), "Bancas que se renuevan en %d (%d)" % (anio, nren))
    h2 = cg.hemiciclo_svg(cg.ordenar_camara(total), "Cámara completa (257)", mayoria=129)
    mp = cg.mapa_svg(gan, det)
    pts, lo, hi = dict(zip(blocs, R["pt"])), dict(zip(blocs, R["lo"])), dict(zip(blocs, R["hi"]))
    T = ["<table><tr><th>Fuerza</th><th>% proyectado</th><th>Banda 95 %</th><th>Bancas que se renuevan</th>"
         "<th>Banda 90 %</th>" + ("<th>Real</th>" if rr else "") + "<th>No se renuevan</th><th>Cámara</th></tr>"]
    filas = list(dict.fromkeys(list(fz) + list(prev)))
    filas.sort(key=lambda f: -(tot.get(f, 0) + prev.get(f, 0)))
    for f in filas:
        b5, b95 = np.percentile(S[f], [5, 95]) if f in S else (0, 0)
        k = "OTRAS" if f == "PROV" else f
        T.append("<tr><td><span class='sw' style='background:%s'></span>%s</td><td>%s</td><td>%s</td><td><b>%d</b></td>"
                 "<td>%d–%d</td>%s<td>%d</td><td><b>%s</b></td></tr>" % (
                     cg.FUERZAS.get(f, (f, "#9e9e9e"))[1], nom(f), "%.1f" % pts[k] if k in pts else "",
                     "%.1f–%.1f" % (lo[k], hi[k]) if k in lo else "", tot.get(f, 0), b5, b95,
                     "<td>%d</td>" % rr.get(f, 0) if rr else "", prev.get(f, 0),
                     total.get(f, "→ " + nom(cont[f]) if f in cont else "")))
    T.append("</table>")
    P = ["<table><tr><th>Distrito</th><th>Se renuevan</th>" + "".join("<th>%s %%</th>" % ("Otras" if b == "OTRAS" else b) for b in blocs) +
         "<th>Fuerza del gobernador</th><th>Bancas proyectadas</th></tr>"]
    ren = cg.renuevan(anio)
    for d in sorted(Dpt.index, key=lambda d: -ren[d]):
        gob = [c for c in Dpt.columns if c.startswith("PROV:") and Dpt.loc[d, c] > 0]
        P.append("<tr><td>%s</td><td>%d</td>%s<td>%s</td><td>%s</td></tr>" % (cg.DIST[d], ren[d],
                 "".join("<td>%.1f</td>" % pct.loc[d, b] for b in blocs),
                 ", ".join("%s %.1f" % (c[5:], pct.loc[d, c]) for c in gob),
                 ", ".join("%s %d" % (f, n) for f, n in sorted(por[d].items(), key=lambda x: -x[1]))))
    P.append("</table>")
    nota = ("Las bancas que no se renuevan son las de cada bloque de la cámara antes del 10 de diciembre (Wikipedia, "
            "tabla «Bancas por bloque»: totales menos las que se renovaban)" if anio in cg.REVISION else
            "Las bancas que no se renuevan son las ganadas en %d" % (anio - 2))
    if pnotas:
        nota += (". Fuerzas de los gobernadores (provinciales.csv, solo en legislativas): retención × %% del "
                 "gobernador, mezclada con las actas del distrito: " + "; ".join(pnotas)).replace("%%", "%")
    html = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diputados %d: proyección</title><style>
:root{--bg:#fff;--fg:#1b1b1b;--mu:#555;--li:#e5e5e5}
body{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1150px;padding:16px}
h1{font-size:22px;margin:4px 0}.mu{color:var(--mu);font-size:13px}
.fila{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-start}.fila>div{flex:1 1 330px;min-width:0}
svg{max-width:100%%;height:auto}.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%%;margin:10px 0 22px;font-size:14px}
th,td{border-bottom:1px solid var(--li);padding:5px 7px;text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}.sw{display:inline-block;width:11px;height:11px;margin-right:6px;vertical-align:-1px}
</style></head><body>
<h1>Cámara de Diputados %d: proyección con %d actas</h1>
<p class="mu">Fotos de actas proyectadas con %s. Bancas: D'Hondt por distrito con el umbral del 3 %% del padrón; OTRAS se parte entre las listas menores oficializadas del distrito con un perfil de Zipf (la k-ésima saca ∝ k<sup>−%.1f</sup>). Banda: bootstrap de circuitos × %.1f (%d remuestras). %s. Mapa: fuerza más votada en cada distrito (pasar el puntero para ver el detalle).</p>
<div class="fila"><div>%s</div><div>%s</div><div>%s</div></div>
<h2>Tablas</h2><div class="tw">%s</div><h3>Por distrito</h3><div class="tw">%s</div>
</body></html>""" % (anio, anio, len(F), " + ".join(R["origs"]), cg.ZIPF, FACTOR, nboot, nota,
                     h1, h2, mp, "".join(T), "".join(P))
    open(out, "w", encoding="utf-8").write(html)
    L = ["", "## Diputados %d (%d bancas)" % (anio, nren), "",
         "| Fuerza | Bancas | Banda 90 % |" + (" Real |" if rr else "") + " Cámara |",
         "|---|---:|---:|" + ("---:|" if rr else "") + "---:|"]
    for f in fz:
        L.append("| %s | %d | %d–%d |%s %s |" % (nom(f), tot.get(f, 0), *np.percentile(S[f], [5, 95]),
                                                  " %d |" % rr.get(f, 0) if rr else "", total.get(f, "")))
    L += ["", "HTML con los hemiciclos, el mapa y las tablas: `%s`" % os.path.basename(out)]
    return L


def main():
    path = [a for a in sys.argv[1:] if not a.startswith("--") and a.endswith(".csv")][0]
    orig = opt("--origen", "2023p")
    R = calcular(leer(path), orig)
    F, blocs, origs, pt, lo, hi, o1, o2, marg, clus = (R[k] for k in ("F", "blocs", "origs", "pt", "lo", "hi", "o1",
                                                                       "o2", "marg", "clus"))
    por_origen, crudo, swing, s_f, share, notas, P, E = (R[k] for k in ("por_origen", "crudo", "swing", "s_f", "share",
                                                                         "notas", "P", "E"))
    # informe
    L = ["# Proyección con %d actas (%d circuitos) — origen %s" % (len(F), clus.max() + 1, orig), "",
         "Modelo: Goodman encogido al swing (λ = %s) con las actas repesadas AMBA / resto; banda del 95 %% por "
         "bootstrap de circuitos × %.1f%s." % (LAM, FACTOR, "; promedio de los orígenes " + " y ".join(origs)
                                              if len(origs) > 1 else ""), "",
         "| Fuerza | Proyección | Banda 95 % | Suma cruda de las actas | Swing uniforme |" +
         "".join(" Solo %s |" % o for o in origs if len(origs) > 1),
         "|---|---:|---:|---:|---:|" + "---:|" * (len(origs) if len(origs) > 1 else 0)]
    for j, b in enumerate(blocs):
        L.append("| %s | **%.1f** | %.1f–%.1f | %.1f | %.1f |" % (b, pt[j], lo[j], hi[j], crudo[j], swing[j]) +
                 "".join(" %.1f |" % por_origen[o][j] for o in origs if len(origs) > 1))
    L += ["", "Margen %s − %s: **%+.1f** puntos (banda %+.1f a %+.1f). Probabilidad de que %s quede primero: %.0f %%." % (
        blocs[o1], blocs[o2], pt[o1] - pt[o2], *np.percentile(marg, [2.5, 97.5]), blocs[o1], 100 * (marg > 0).mean()), ""]
    # cobertura
    reg8_all = fm.region(P.index.get_level_values(0), P.index.get_level_values(1), "region")
    sh8 = pd.Series(E.to_numpy(float)).groupby(reg8_all).sum().pipe(lambda s: 100 * s / s.sum())
    f8 = pd.Series(fm.region(F.distrito_id, F.seccion_id, "region")).value_counts()
    L += ["## De dónde vienen las actas", "", "| Región | % del padrón | actas |", "|---|---:|---:|"]
    for rg, v in sh8.sort_values(ascending=False).items():
        L.append("| %s | %.0f | %d |" % (rg, v, f8.get(rg, 0)))
    falta = [rg for rg, v in sh8.items() if f8.get(rg, 0) == 0 and v >= 3]
    amba = (s_f == "AMBA").mean() * 100
    L += [""]
    if falta:
        L.append("- **Regiones sin actas**: %s. El modelo les aplica el cambio del resto; las fuerzas fuertes ahí "
                 "(listas provinciales, PU en Córdoba y Santa Fe) pueden quedar bajas." % ", ".join(falta))
    L.append("- %.0f %% de las actas son del AMBA (el AMBA es el %.0f %% del padrón)%s." % (
        amba, 100 * share.get("AMBA", 0), "; están repesadas" if abs(amba - 100 * share.get("AMBA", 0)) > 10 else ""))
    inc = int((~F.completa).sum())
    if inc:
        L.append("- %d actas incompletas (solo algunas fuerzas): cuentan para esas fuerzas." % inc)
    sec = F[F.nivel == "seccion"]
    if len(sec):
        L.append("- %d actas sin circuito reconocido: se comparan con su sección." % len(sec))
    L += ["- " + n for n in notas]
    L += ["", "Error típico del margen con este método (`fotos_sim.py` y `fotos_sim2.py`, 2019/2021 → 2023 y "
          "2021/2023 → 2025), con ~30 actas: 1,9 puntos si son al azar y 2,7–3,1 si están armadas como las de Twitter "
          "(2/3 del AMBA y racimos), promediando dos orígenes; con uno solo, 10–20 % más."]
    real = opt("--real")
    if real:
        w = pd.read_pickle(os.path.join(HERE, "mesas_%s.pkl" % real))
        tot = w[[b for b in blocs if b in w]].sum()
        rp = 100 * tot / tot.sum()
        L += ["", "## Contra el resultado real (%s)" % real, "", "| Fuerza | Real | Proyección | Error |", "|---|---:|---:|---:|"]
        for j, b in enumerate(blocs):
            L.append("| %s | %.1f | %.1f | %+.1f |" % (b, rp[b], pt[j], pt[j] - rp[b]))
        L.append("| Margen %s − %s | %+.1f | %+.1f | %+.1f |" % (blocs[o1], blocs[o2], rp[blocs[o1]] - rp[blocs[o2]],
                 pt[o1] - pt[o2], (pt[o1] - pt[o2]) - (rp[blocs[o1]] - rp[blocs[o2]])))
    if opt("--congreso"):
        L += congreso_html(R, int(opt("--congreso")), path[:-4] + "_congreso.html", real)
    out = path[:-4] + "_proyeccion.md"
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # la consola de Windows no tiene la λ
    print("\n".join(L))
    print("\n->", out)


if __name__ == "__main__":
    main()
