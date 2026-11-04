"""Informe HTML del ICG como prior del oficialismo (28-oct-2026): ajuste histórico, backtests de 30 actas
(icg_fotos.py), bancas con 30 mesas (congreso_sim.py con y sin --icg) y las 27 actas de 2025.
    python -X utf8 proyeccion/icg/informe_icg.py
Salida: proyeccion/icg/icg_prior.html."""
import os, sys, html
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.join(HERE, "..")
sys.path.insert(0, PROY)
sys.path.insert(0, HERE)
import icg_voto as iv
import icg_fotos as ifo


def tabla(df, fmt=None, cls=""):
    fmt = fmt or {}
    h = "<table class='%s'><tr>%s</tr>" % (cls, "".join("<th>%s</th>" % html.escape(str(c)) for c in df.columns))
    for _, r in df.iterrows():
        h += "<tr>%s</tr>" % "".join("<td>%s</td>" % (fmt.get(c, "{}").format(v) if pd.notna(v) else "")
                                     for c, v in r.items())
    return h + "</table>"


def dispersion(df, b):
    """SVG: voto al oficialismo contra ICG del mes anterior, con la recta (sin 2003)."""
    W, H, m = 560, 330, 46
    xs, ys = df.mes_anterior.to_numpy(), df.voto.to_numpy()
    x0, x1, y0, y1 = 0.7, 3.0, 20, 56
    X = lambda x: m + (x - x0) / (x1 - x0) * (W - 2 * m)
    Y = lambda y: H - m + 10 - (y - y0) / (y1 - y0) * (H - 2 * m)
    s = ['<svg viewBox="0 0 %d %d" role="img" aria-label="Voto al oficialismo contra ICG">' % (W, H)]
    for t in np.arange(1, 3.01, 0.5):
        s.append('<line x1="%.0f" x2="%.0f" y1="%d" y2="%.0f" class="grid"/>' % (X(t), X(t), m - 10, H - m + 10))
        s.append('<text x="%.0f" y="%d" class="ax" text-anchor="middle">%.1f</text>' % (X(t), H - m + 26, t))
    for t in range(20, 57, 10):
        s.append('<line x1="%d" x2="%d" y1="%.0f" y2="%.0f" class="grid"/>' % (m, W - m, Y(t), Y(t)))
        s.append('<text x="%d" y="%.0f" class="ax" text-anchor="end">%d %%</text>' % (m - 6, Y(t) + 4, t))
    for tipo, cl in (("P", "pres"), ("L", "leg")):
        xx = np.array([x0 + .2, x1 - .1])
        yy = b[0] + b[1] * xx + (b[2] if tipo == "P" else 0)
        s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="fit %s"/>' % (X(xx[0]), Y(yy[0]), X(xx[1]), Y(yy[1]), cl))
    for _, r in df.iterrows():
        cl = "pres" if r.tipo == "P" else "leg"
        s.append('<circle cx="%.1f" cy="%.1f" r="5" class="pt %s"><title>%s: ICG %.2f, %.1f %%</title></circle>'
                 % (X(r.mes_anterior), Y(r.voto), cl, r.fecha[:4], r.mes_anterior, r.voto))
        dy = 14 if r.fecha[:4] == "2019" else (-6 if r.fecha[:4] == "2025" else 4)    # 2019 y 2025 casi se tocan
        s.append('<text x="%.1f" y="%.1f" class="lab">%s</text>' % (X(r.mes_anterior) + 7, Y(r.voto) + dy, r.fecha[:4]))
    s.append('<text x="%d" y="%d" class="ax" text-anchor="middle">ICG del mes anterior (0 a 5)</text>' % (W / 2, H - 6))
    s.append("</svg>")
    return "".join(s)


def actas27():
    """Las 27 actas de 2025: proporciones y bancas sin y con el prior (w de una colección tipo Twitter)."""
    import proyectar_fotos as pf
    import congreso as cg
    import congreso_sim as cs
    a = pf.leer(os.path.join(PROY, "fotos25", "actas.csv"))
    R = pf.calcular(a, "2023p,2021bl", nboot=50)
    blocs = R["blocs"]
    pri, sp = ifo.prior("2025-10-26")
    w = cs.W_ICG["twitter"] / (cs.W_ICG["twitter"] + sp ** 2)
    m = pd.read_pickle(os.path.join(PROY, "mesas_2025bl.pkl"))
    m["OTRAS"] = m.OTRAS + m.OTROS
    tr = m[blocs].sum()
    real = 100 * tr / tr.sum()
    pt = pd.Series(R["pt"], index=blocs)
    j = blocs.index("LLA")
    q = pd.Series(ifo.mezclar(pt.to_numpy(), j, pri, w), index=blocs)
    D = R["proj_d"](np.arange(len(R["F"])))[blocs]
    out = {}
    for tag, DD in (("sin ICG", D), ("con ICG", cs.ancla_icg(D, w, pri))):
        _, t = cg.repartir(cg.provinciales(DD, 2025, R["actas"])[0], 2025, R["pad"])
        out[tag] = t
    rr = cg.electos(2025)[1]
    V = pd.DataFrame({"Fuerza": blocs, "Real": real.values, "Fotos": pt.values, "Fotos + ICG": q.values})
    V["Error fotos"] = V.Fotos - V.Real
    V["Error con ICG"] = V["Fotos + ICG"] - V.Real
    mg = V.set_index("Fuerza").loc["LLA", ["Real", "Fotos", "Fotos + ICG"]] - V.set_index("Fuerza").loc["FP", ["Real", "Fotos", "Fotos + ICG"]]
    V.loc[len(V)] = ["Margen LLA − FP", mg.Real, mg.Fotos, mg["Fotos + ICG"], mg.Fotos - mg.Real, mg["Fotos + ICG"] - mg.Real]
    fz = ["LLA", "FP", "PU", "FIT", "PROV"]
    B = pd.DataFrame({"Fuerza": fz, "Reales": [rr.get(f, 0) for f in fz],
                      "Sin ICG": [out["sin ICG"].get(f, 0) for f in fz], "Con ICG": [out["con ICG"].get(f, 0) for f in fz]})
    return V, B, pri, sp, w


def main():
    df = pd.read_csv(os.path.join(HERE, "elecciones.csv"))
    s = df[df.fecha > "2004"].reset_index(drop=True)
    X = np.c_[np.ones(len(s)), s.mes_anterior, s.pres]
    b = np.linalg.lstsq(X, s.voto.to_numpy(float), rcond=None)[0]
    loo = iv.loo(s, ["mes_anterior", "pres"])
    H = df[["fecha", "tipo", "voto", "mes_anterior", "mes_eleccion"]].copy()
    H["Prior sin esa elección"] = [np.nan] + list(s.voto.to_numpy() + loo)
    H["Error"] = H["Prior sin esa elección"] - H.voto
    H.columns = ["Fecha", "Tipo", "Oficialismo %", "ICG mes anterior", "ICG mes de la elección", "Prior sin esa elección", "Error"]
    f2 = {c: "{:.2f}" for c in H.columns[2:]}
    C = []
    for col in ("mes_anterior", "mes_eleccion", "ventana", "prom_2_meses"):
        for sub, x in (("todas", df), ("sin 2003", s)):
            x = x.reset_index(drop=True)
            C.append({"ICG": col.replace("_", " "), "Elecciones": sub, "Correlación": x[[col, "voto"]].corr().iloc[0, 1],
                      "Error (solo ICG)": np.abs(iv.loo(x, [col])).mean(),
                      "Error (ICG + presidencial)": np.abs(iv.loo(x, [col, "pres"])).mean()})
    C.append({"ICG": "sin ICG: promedio", "Elecciones": "sin 2003", "Correlación": np.nan,
              "Error (solo ICG)": np.abs(iv.loo(s, [])).mean(), "Error (ICG + presidencial)": np.abs(iv.loo(s, ["pres"])).mean()})
    C = pd.DataFrame(C)
    sims = []
    for f in sorted(os.listdir(HERE)):
        if f.startswith("sim_") and f.endswith(".csv"):
            d = pd.read_csv(os.path.join(HERE, f))
            d = d[d.variante.isin(["w 0.0", "w óptimo"])]
            g = d.assign(a_ofi=d.err_ofi.abs(), a_mar=d.err_margen.abs()).groupby(["par", "esquema", "variante"], sort=False)
            t = g.agg(w=("w", "mean"), ofi=("a_ofi", "mean"), mar=("a_mar", "mean"), mae=("mae", "mean")).reset_index()
            for (par, esq), u in t.groupby(["par", "esquema"], sort=False):
                a0, a1 = u[u.variante == "w 0.0"].iloc[0], u[u.variante == "w óptimo"].iloc[0]
                sims.append({"Par": par, "Esquema": esq, "w": a1.w, "Oficialismo: fotos": a0.ofi, "Oficialismo: + ICG": a1.ofi,
                             "Margen: fotos": a0.mar, "Margen: + ICG": a1.mar, "Por fuerza: fotos": a0.mae,
                             "Por fuerza: + ICG": a1.mae})
    S = pd.DataFrame(sims)
    Bk = []
    for tag, f in (("sin ICG", "congreso_sim.csv"), ("con ICG", "congreso_sim_icg.csv")):
        p = os.path.join(PROY, "fotos_sim", f)
        if not os.path.exists(p):
            continue
        d = pd.read_csv(p)
        for esq, g in d.groupby("esquema", sort=False):
            r = {"Bancas": tag, "Esquema": esq}
            for fz in ("LLA", "FP", "PU", "FIT", "PROV"):
                r[fz] = "%.1f (%+.1f)" % ((g[fz] - g[fz + "_real"]).abs().mean(), (g[fz] - g[fz + "_real"]).mean())
            r["Cubre banda LLA"] = "%.0f %%" % (100 * ((g.LLA_lo <= g.LLA_real) & (g.LLA_real <= g.LLA_hi)).mean())
            Bk.append(r)
    Bk = pd.DataFrame(Bk)
    V, B, pri, sp, w = actas27()
    page = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ICG como prior</title><style>
:root{--bg:#fff;--fg:#1b1b1b;--mu:#555;--li:#e5e5e5;--p:#6c4c98;--l:#009ce4}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}
h1{font-size:23px;margin:6px 0}h2{font-size:18px;margin:26px 0 6px}.mu{color:var(--mu);font-size:13.5px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%%;margin:8px 0 14px;font-size:14px}
th,td{border-bottom:1px solid var(--li);padding:5px 8px;text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}
svg{max-width:100%%;width:600px;height:auto;display:block}.grid{stroke:var(--li)}.ax{font-size:11px;fill:var(--mu)}.lab{font-size:10.5px;fill:var(--mu)}
.pt.pres{fill:var(--p)}.pt.leg{fill:var(--l)}.fit{stroke-width:1.5;stroke-dasharray:5 4}.fit.pres{stroke:var(--p)}.fit.leg{stroke:var(--l)}
.key span{display:inline-block;width:10px;height:10px;border-radius:50%%;margin:0 5px 0 12px}
.box{background:#f6f6f6;border-radius:6px;padding:10px 14px;margin:10px 0}
</style></head><body>
<h1>El ICG de la UTDT como prior del voto al oficialismo</h1>
<p class="mu">28-oct-2026. Microdatos y serie de la Escuela de Gobierno de la UTDT (datos/icg/). Oficialismo: %% de votos positivos de la fuerza del gobierno (1.ª vuelta presidencial o diputados nacionales). Scripts: proyeccion/icg/icg_voto.py, icg_fotos.py, congreso_sim.py --icg, informe_icg.py.</p>
<div class="box"><b>En resumen.</b> El ICG del mes anterior correlaciona 0,78 con el voto al oficialismo. Como prior erra 3,8 puntos (dejando cada elección afuera, sin 2003 y separando presidenciales de legislativas), contra 5,3 del promedio histórico. Mezclado con las fotos con un peso chico (0,05 a 0,17) baja el error del oficialismo en las colecciones tipo Twitter en los tres backtests, y casi no cambia nada con mesas al azar. En 2025 el prior quedó bajo (%s contra 40,7): mejora la proporción de las 27 actas pero empeora las bancas de LLA, que ya salían cortas.</div>
<h2>Voto al oficialismo e ICG</h2>
<p class="key mu"><span style="background:var(--p)"></span>presidenciales <span style="background:var(--l)"></span>legislativas; rectas ajustadas sin 2003</p>
%s
<div class="tw">%s</div>
<h2>¿Qué mes del ICG?</h2>
<p class="mu">Error medio absoluto dejando una elección afuera (puntos). «ventana» = entrevistas entre 45 y 7 días antes de la elección (microdatos).</p>
<div class="tw">%s</div>
<h2>Backtests con 30 actas: votos</h2>
<p class="mu">300 colecciones simuladas por esquema y par, modelo actual (Goodman λ = 0,1, AMBA/resto). Errores medios absolutos en puntos. w = σ²<sub>fotos</sub> / (σ²<sub>fotos</sub> + σ²<sub>prior</sub>), con el prior ajustado sin la elección de destino.</p>
<div class="tw">%s</div>
<h2>30 mesas al azar: bancas de 2025</h2>
<p class="mu">congreso_sim.py, 40 colecciones por esquema, con las fuerzas de los gobernadores. Error absoluto medio en bancas (entre paréntesis, con signo).</p>
<div class="tw">%s</div>
<h2>Las 27 actas de 2025</h2>
<p class="mu">Prior ICG para 2025 (sin usar 2025): %.1f %% (σ %.1f); peso w = %.2f (colección tipo Twitter).</p>
<div class="tw">%s</div><div class="tw">%s</div>
</body></html>""" % (("%.1f" % pri).replace(".", ","), dispersion(df, b), tabla(H, f2), tabla(C, {"Correlación": "{:.2f}", "Error (solo ICG)": "{:.2f}",
                                                                   "Error (ICG + presidencial)": "{:.2f}"}),
                     tabla(S, {c: "{:.2f}" for c in S.columns[2:]}), tabla(Bk), pri, sp, w,
                     tabla(V, {c: "{:.1f}" for c in V.columns[1:]}), tabla(B))
    out = os.path.join(HERE, "icg_prior.html")
    open(out, "w", encoding="utf-8").write(page)
    print(V.round(1).to_string(index=False))
    print(B.to_string(index=False))
    print("->", out)


if __name__ == "__main__":
    main()
