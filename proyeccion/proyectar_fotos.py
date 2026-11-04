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
    return normalizar_actas(pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna(""))


def normalizar_actas(a):
    """Una mesa es una observacion; las fotos son fuentes, no unidades adicionales.
    Copias exactas se colapsan. Versiones contradictorias requieren resolver la transcripcion.
    """
    a = a.copy().fillna("")
    a["votos"] = pd.to_numeric(a.votos, errors="raise")
    if (~np.isfinite(a.votos) | (a.votos < 0)).any():
        raise ValueError("Votos ausentes, negativos o no finitos: revisar las actas")
    if "lista" not in a:
        a["lista"] = a.bloque
    a["distrito_id"] = a.distrito_id.astype(str)
    a["distrito_id"] = a.distrito_id.str.zfill(2)
    a["seccion_id"] = a.seccion_id.astype(int)
    a["circuito"] = a.circuito.map(norm_circ)
    a["bloque"] = a.bloque.str.strip().str.upper().replace({"BLANCO": "BN", "NULO": "BN", "BLANCOS": "BN", "NULOS": "BN"})
    a["mesa"] = a.mesa.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.lstrip("0").replace("", "0")
    if "mesa_tipo" not in a:
        a["mesa_tipo"] = "NATIVOS"
    ident = [c for c in ("eleccion", "cargo", "distrito_id", "seccion_id", "circuito", "mesa", "mesa_tipo") if c in a]
    a["mesa_key"] = a[ident].astype(str).agg("|".join, axis=1)
    a["completa"] = a.completa.astype(str).str.lower().isin(["si", "sí", "s", "1", "true"])
    a = a.drop_duplicates()
    output = []
    for key, g in a.groupby("mesa_key", sort=False):
        versions = list(g.groupby("foto", sort=False))
        # Dos fotos completas de la misma mesa deben tener el mismo total por bloque.
        complete = [(f, v) for f, v in versions if v.completa.any()]
        if complete:
            chosen = complete[0][1]
            totals = chosen.groupby("bloque").votos.sum()
            for _, other in versions:
                observed = other.groupby("bloque").votos.sum()
                if not np.allclose(observed, totals.reindex(observed.index, fill_value=0)):
                    raise ValueError("Versiones contradictorias de la mesa " + key)
            output.append(chosen)
        else:
            observations = []
            for _, v in versions:
                for _, part in v.groupby(["lista", "bloque"], sort=False):
                    r = part.iloc[0].copy()
                    r["votos"] = part.votos.sum()
                    observations.append(r)
            v = pd.DataFrame(observations)
            for _, part in v.groupby(["lista", "bloque"], sort=False):
                if part.votos.nunique() != 1:
                    raise ValueError("Versiones contradictorias de la mesa " + key)
            output.append(v.drop_duplicates(["lista", "bloque"]))
    if not output:
        raise ValueError("No hay actas")
    result = pd.concat(output, ignore_index=True)
    result["completa"] = result.completa.map({True: "si", False: "no"})
    return result


def calcular(a, orig, nboot=NBOOT, seed=0, fuerzas=None, marco=None, antecesores=None, factor=FACTOR):
    """Motor operativo compartido por la noche y los backtests."""
    from fotos_motor import calcular as motor
    return motor(a, orig, origen, normalizar_actas,
                 ANTECESORES if antecesores is None else antecesores,
                 nboot=nboot, seed=seed, fuerzas=fuerzas, marco=marco,
                 lam=LAM, factor=factor, kind=KIND)


def congreso_html(R, anio, out, real=None, nboot=300):
    """Bancas de Diputados que se renuevan en anio (D'Hondt por distrito sobre la proyeccion por distrito; banda por
    bootstrap de circuitos, ensanchada como la nacional), la camara completa con las bancas que no se renuevan, el mapa
    por provincia y un HTML con las tablas al final. Devuelve lineas para el informe .md."""
    import congreso as cg
    blocs, F, clus = R["blocs"], R["F"], R["clus"]
    C = R.get("congreso") or cg.distribucion(R, anio, nboot)
    Dpt, pnotas, por, tot, S, nboot = (C[k] for k in ("Dpt", "notas", "por", "tot", "S", "nboot"))
    fz = sorted(set(S.columns) | set(tot), key=lambda f: cg.ORDEN.index(f) if f in cg.ORDEN else 99)
    S = S.reindex(columns=fz, fill_value=0)
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
<p class="mu">Fotos de actas proyectadas con %s. Bancas: D'Hondt por distrito con el umbral del 3 %% del padrón; OTRAS se parte entre las listas menores oficializadas del distrito con un perfil de Zipf (la k-ésima saca ∝ k<sup>−%.1f</sup>). Bandas nominales: bootstrap de circuitos × %.1f (%d remuestras). Porcentajes y bancas derivados de las mismas simulaciones. La selección de fotos puede producir sesgos no cubiertos por estas bandas. %s. Mapa: fuerza más votada en cada distrito (pasar el puntero para ver el detalle).</p>
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
    forces = opt("--fuerzas")
    frame = pd.read_csv(opt("--marco"), dtype={"distrito_id":str,"circuito":str}) if opt("--marco") else None
    if frame is None and opt("--congreso"):
        from fotos_motor import marco_destino
        frame = marco_destino(int(opt("--congreso")), HERE)
    R = calcular(leer(path), orig, fuerzas=forces.split(",") if forces else None, marco=frame)
    if opt("--congreso"):
        import congreso as cg
        cg.distribucion(R, int(opt("--congreso")))
    F, blocs, origs, pt, lo, hi, o1, o2, marg, clus = (R[k] for k in ("F", "blocs", "origs", "pt", "lo", "hi", "o1",
                                                                       "o2", "marg", "clus"))
    por_origen, crudo, swing, s_f, share, notas, P, E = (R[k] for k in ("por_origen", "crudo", "swing", "s_f", "share",
                                                                         "notas", "P", "E"))
    # informe
    L = ["# Proyección con %d actas (%d circuitos) — origen %s" % (len(F), clus.max() + 1, orig), "",
         "Modelo: Goodman encogido al swing (λ = %s) con repesado AMBA / resto por fuerza observada; banda nominal del 95 %% por "
         "bootstrap de circuitos × %.1f%s." % (LAM, FACTOR, "; promedio de los orígenes " + " y ".join(origs)
                                              if len(origs) > 1 else ""), "",
         "| Fuerza | Proyección | Banda 95 % | Suma cruda de las actas | Swing uniforme |" +
         "".join(" Solo %s |" % o for o in origs if len(origs) > 1),
         "|---|---:|---:|---:|---:|" + "---:|" * (len(origs) if len(origs) > 1 else 0)]
    for j, b in enumerate(blocs):
        band = "%.1f–%.1f" % (lo[j], hi[j]) if R["inferencia_valida"] else "no estimable"
        point = "%.1f" % pt[j] if np.isfinite(pt[j]) else "no estimable"
        L.append("| %s | **%s** | %s | %.1f | %.1f |" % (b, point, band, crudo[j], swing[j]) +
                 "".join(" %.1f |" % por_origen[o][j] for o in origs if len(origs) > 1))
    if R["inferencia_valida"]:
        L += ["", "Margen %s − %s: **%+.1f** puntos (banda %+.1f a %+.1f). Frecuencia de primer puesto en las remuestras para %s: %.1f %%." % (
            blocs[o1], blocs[o2], pt[o1] - pt[o2], *np.percentile(marg, [2.5, 97.5]), blocs[o1], 100 * R["prob_primero"][o1]), ""]
    else:
        L += ["", "Bandas y probabilidades: **no estimables** con estas observaciones. No se sustituyen por cero.", ""]
    if "congreso" in R:
        L += ["El nacional proyectado y las bancas salen de las mismas realizaciones por distrito, con corrección provincial. Las columnas de swing y de cada origen son referencias sin esa corrección.", ""]
    L += ["", "## Soporte por fuerza", "",
          "| Fuerza | Actas | Circuitos | Actas efectivas por pesos | Peso AMBA |", "|---|---:|---:|---:|---:|"]
    for item in R["soporte"]:
        weight = "%.1f %%" % (100*item["peso_amba"]) if item["peso_amba"] is not None else "sin dato"
        L.append("| %s | %d | %d | %.1f | %s |" % (item["fuerza"], item["actas"], item["circuitos"], item["n_efectivo"], weight))
    L += ["", "El tamaño efectivo mostrado mide la desigualdad de pesos, no la independencia entre fotos. Los circuitos se remuestrean juntos."]
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
    L += ["", "Validación del procedimiento corregido: `validacion_20261028/RESULTADOS.md`. Las bandas son condicionales al modelo y al esquema de muestreo; el bootstrap no identifica selección por cambio no observado."]
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
