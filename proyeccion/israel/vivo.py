"""La noche de la eleccion de la Knesset 2026: proyeccion y aguja con el archivo por urna que se vaya publicando.
    python -X utf8 proyeccion/israel/vivo.py https://media26.bechirot.gov.il/files/expb.csv     # o un archivo local
    python -X utf8 proyeccion/israel/vivo.py --prueba 0.1      # ensayo: 10 % de las urnas de 2022 desde 2021
Supone el mismo formato que expb.csv de 2019-2022 (una fila por urna; columnas סמל ישוב, קלפי, בזב, מצביעים,
כשרים y una columna por letra de boleta). Las letras de 2026 se pasan a listas con letras26.csv (letra,lista; lista =
un nombre de datos.LISTAS26); las letras sin fila van como listas sin antecesor (las de menos del 1 % a «otras»).
Las urnas contadas = filas con votantes; las que faltan = las urnas de 2022 que todavia no aparecen, con su padron
de 2022 por el crecimiento observado. El doble sobre (localidad 9999) se proyecta salvo que se pase --doble-contado.
Para no cargar el servidor, bajarlo como mucho cada pocos minutos.
Salida: proyeccion/israel/vivo_<hora>.md y proyeccion/img/aguja_israel_vivo.png."""
import os, sys, io, datetime, urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import datos as dt
import modelo as md
import aguja_dibujo as ad

ORIG = 25
NBOOT = 400
UA = "dataeleccproyecto (proyeccion academica)"
MIN_URNAS = 120    # ~1 % de las urnas comunes; con menos no se proyecta
CREC = 1.03       # crecimiento del padron de las urnas comunes respecto de 2022 si no se pasa --padron
COLORES = {"bibi": "#1f4e9c", "sin": "#e07b00", "arabe": "#2e8b57", "empate": "#727272"}
# boca de urna de las 22:00 (hora de Israel), para comparar; Canal 12 (Mano Geva), foto de la pantalla
BOCA = {"Canal 12": dict(bibi=50, oposicion=52, arabe=18,
                         detalle="Likud 24, Yashar 22, Juntos 12, Lista Conjunta 11, Israel Beitenu 9, Demócratas 9, "
                                 "Shas 8, Raam 7, UTJ 6, Sionismo Religioso 6, Otzma 6; Amcha Yisrael y "
                                 "Reservistas 0")}


def leer(fuente):
    if os.path.isdir(fuente):             # carpeta: el expb*.csv mas reciente (p. ej. la de Descargas)
        cands = [os.path.join(fuente, f) for f in os.listdir(fuente) if f.startswith("expb") and f.endswith(".csv")]
        if not cands:
            sys.exit("No hay ningun expb*.csv en %s" % fuente)
        fuente = max(cands, key=os.path.getmtime)
        print("Archivo:", fuente, datetime.datetime.fromtimestamp(os.path.getmtime(fuente)).strftime("%H:%M:%S"))
    if fuente.startswith("http"):
        r = urllib.request.urlopen(urllib.request.Request(fuente, headers={"User-Agent": UA}), timeout=60)
        raw = r.read()
        if r.status != 200 or not raw:    # en 2026 el servidor responde 202 vacio (desafio antibots de AWS WAF)
            sys.exit("El servidor respondio %d sin datos: bajar expb.csv con el navegador y pasar el archivo o "
                     "la carpeta" % r.status)
        path = os.path.join(HERE, "vivo_ultimo.csv")
        open(path, "wb").write(raw)
        fuente = path
    for enc in ("utf-8-sig", "cp1255"):
        try:
            global FUENTE
            FUENTE = os.path.basename(fuente)
            return pd.read_csv(fuente, encoding=enc)
        except UnicodeDecodeError:
            continue


def normalizar(d):
    d = d[[c for c in d.columns if not str(c).startswith("Unnamed")]]
    kal = "קלפי" if "קלפי" in d else "מספר קלפי"
    out = pd.DataFrame({"loc": d["סמל ישוב"].astype(int), "kalpi": d[kal].astype(float), "bzb": d["בזב"].astype(float),
                        "votantes": d["מצביעים"].astype(float), "validos": d["כשרים"].astype(float)})
    out["doble"] = out["loc"].isin(dt.DOBLE)
    partidos = [c for c in d.columns if c not in dt.META]
    return out.join(d[partidos].astype(float)), partidos


def estado(dest, pdest, nombre_de, antecesores, bloque, o=ORIG, crec=CREC):
    """Estado para modelo.proyectar: urnas contadas (con Y) y urnas de origen que faltan (sin Y)."""
    do, po = dt.cargar(o)
    ko = [p for p in po if do[p].sum() >= md.MIN_PCT * do.validos.sum()]
    reg_o = do[~do.doble].copy()
    Vo = md._tabla(reg_o, po, ko)
    reg_o["k"] = reg_o.kalpi.astype(int)
    by_k = Vo.groupby([reg_o["loc"], reg_o["k"]]).sum()
    by_l = Vo.groupby(reg_o["loc"]).sum()
    cont = dest[(~dest.doble) & (dest.votantes > 0)].copy()
    cont["k"] = cont.kalpi.astype(int)
    tot_val = cont.validos.sum()
    kd = [p for p in pdest if p in nombre_de or cont[p].sum() >= md.MIN_PCT * max(tot_val, 1)]
    Vd = md._tabla(cont, pdest, kd)
    key = list(zip(cont["loc"], cont["k"]))
    Xk = by_k.reindex(key).to_numpy(float)
    Xl = by_l.reindex(cont["loc"]).to_numpy(float)
    Xa = np.where(~np.isnan(Xk).any(1)[:, None], Xk, Xl)
    sin = np.isnan(Xa).any(1) | (Xa.sum(1) <= 0)
    Xa[sin] = Vo.sum().to_numpy(float)
    w = np.maximum(cont.bzb.to_numpy(float), Vd.drop(columns="NOVOTO").sum(1).to_numpy(float))
    Vd["NOVOTO"] = w - Vd.drop(columns="NOVOTO").sum(1)
    # lo que falta: por urna de origen, su padron x crec menos lo contado con esa urna; despues, en cada localidad,
    # se ajusta para que el total sea el padron de la localidad x crec menos lo contado en ella (la numeracion de
    # las urnas cambia entre elecciones y una urna de origen puede estar contada a medias)
    eo_k = by_k.sum(1)
    cnt_k = pd.Series(w, index=pd.MultiIndex.from_tuples(key)).groupby(level=[0, 1]).sum()
    falta_k = np.maximum(eo_k * crec - cnt_k.reindex(eo_k.index).fillna(0), 0)
    cnt_l = pd.Series(w, index=cont["loc"].to_numpy()).groupby(level=0).sum()
    falta_l = np.maximum(by_l.sum(1) * crec - cnt_l.reindex(by_l.index).fillna(0), 0)
    sk = falta_k.groupby(level=0).transform("sum")
    esc = (falta_l.reindex(falta_k.index.get_level_values(0)).to_numpy() / np.maximum(sk.to_numpy(), 1e-9))
    wf_all = falta_k.to_numpy() * np.where(sk.to_numpy() > 0, esc, 0)
    keep = wf_all > 0.5
    falta = by_k[keep]
    wf = wf_all[keep]
    Xf = falta.to_numpy(float)
    X = np.vstack([Xa / Xa.sum(1, keepdims=True), Xf / np.maximum(Xf.sum(1, keepdims=True), 1)])
    Y = np.vstack([Vd.to_numpy(float) / w[:, None], np.zeros((len(falta), Vd.shape[1]))])
    ww = np.r_[w, wf]
    locs = np.r_[cont["loc"].to_numpy(), falta.index.get_level_values(0).to_numpy()]
    ks = np.r_[cont["k"].to_numpy(), falta.index.get_level_values(1).to_numpy()]
    sec_l, size = md.sectores(by_l, ko, o)
    sec = sec_l.reindex(locs).fillna(4).to_numpy().astype(int)
    grande = pd.Series(locs).map(pd.Series(locs).value_counts()).to_numpy() > 40
    clus = pd.factorize(pd.Series(list(zip(locs, np.where(grande, ks // 20, 0)))))[0]
    dbo = md._tabla(do[do.doble], po, ko).drop(columns="NOVOTO").sum().to_numpy(float)
    dbd = md._tabla(dest[dest.doble], pdest, kd).drop(columns="NOVOTO").sum().to_numpy(float)
    ocols, dcols = list(Vo.columns), list(Vd.columns)
    src = [[ocols.index(a) for a in antecesores.get(c, [c]) if a in ocols] for c in dcols]
    st = dict(X=X, Y=Y, w=ww, sec=sec, clus=clus, loc=locs, arab=(sec == 0), ocols=ocols, dcols=dcols, src=src,
              dbo=dbo * crec, dbd=dbd, reg_o_tot=Vo.drop(columns="NOVOTO").sum().to_numpy(float),
              listas=[c for c in dcols if c not in ("OTRAS", "NOVOTO")])
    return st, np.arange(len(cont)), crec


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    doble = "--doble-contado" in sys.argv
    if "--prueba" in sys.argv:            # ensayo con 2022: urnas al azar, letras y bloques de 2022
        f = float(sys.argv[sys.argv.index("--prueba") + 1])
        global ORIG
        ORIG = 24
        d, p = dt.cargar(25)
        rng = np.random.default_rng(5)
        ok = d.doble | (rng.random(len(d)) < f)
        dest = d[ok].drop(columns=["nombre"])
        nombre_de = {k: dt.LISTAS[25][k] for k in p if k in dt.LISTAS[25]}
        ant = dt.ANTECESORES[(24, 25)]
        blo = dt.BLOQUE[25]
        acuerdos = dt.ACUERDOS[25]
        titulo = "Ensayo: Knesset 2022 con el %s %% de las urnas" % ("%g" % (100 * f))
        sys.argv += ["--padron", str(d.loc[~d.doble, "bzb"].sum())]
    else:
        dest, p = normalizar(leer(args[0]))
        letras = pd.read_csv(os.path.join(HERE, "letras26.csv"), dtype=str).dropna()
        nombre_de = dict(zip(letras.letra.str.strip(), letras.lista.str.strip()))
        de_nombre = {v: k for k, v in nombre_de.items()}
        # las letras sin fila en letras26.csv no tienen antecesor: varias de 2026 eran de otra lista en 2022
        # (פה era Yesh Atid y ahora es una lista menor; ד era Balad)
        ant = {k: [] for k in p}
        ant.update({k: dt.LISTAS26[n][0] for k, n in nombre_de.items() if n in dt.LISTAS26})
        blo = {k: dt.LISTAS26[n][1] for k, n in nombre_de.items() if n in dt.LISTAS26}
        acuerdos = [(de_nombre[a], de_nombre[b]) for a, b in dt.ACUERDOS26 if a in de_nombre and b in de_nombre]
        titulo = "Knesset 2026: proyección con %s" % FUENTE
    crec = CREC
    if "--padron" in sys.argv:            # electores de las urnas comunes de 2026 (sin el exterior)
        do, _ = dt.cargar(ORIG)
        crec = float(sys.argv[sys.argv.index("--padron") + 1]) / do.loc[~do.doble, "bzb"].sum()
    st, cnt, crec = estado(dest, p, nombre_de, ant, blo, ORIG, crec)
    if len(cnt) < MIN_URNAS:              # backtest: con menos del ~1 % de las urnas la matriz no es confiable
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        v = dest.loc[~dest.doble, [c for c in p if c in blo]].sum()
        tb = v.groupby(pd.Series(blo)).sum()
        print("Solo %d urnas contadas (mínimo %d para proyectar). Conteo crudo por bloque: %s" % (
            len(cnt), MIN_URNAS, ", ".join("%s %.1f %%" % (k, 100 * x / dest.loc[~dest.doble, "כשרים" if "כשרים" in
                                                 dest else "validos"].sum()) for k, x in tb.items())))
        return
    rng = np.random.default_rng(0)
    s, tot = md.proyectar(st, cnt, rng, NBOOT, acuerdos, doble_contado=doble)
    b = md.bloques(st, s, blo)
    res = md.resultado(b["bibi"][1:], b["oposicion"][1:])
    pr = {k: (res == k).mean() for k in ("bibi", "empate", "oposicion")}
    frac = st["w"][cnt].sum() / st["w"].sum()
    v = pd.Series(tot[:-1], index=st["dcols"][:-1])
    pct = 100 * v / v.sum()
    L = ["# %s" % titulo, "", "Urnas comunes contadas: %d (%.1f %% del padrón estimado). Doble sobre: %s." % (
        len(cnt), 100 * frac, "contado" if doble else "proyectado"), "",
         "| Lista | % proyectado | Bancas | Banda 90 % | Entra al Knesset |", "|---|---:|---:|---:|---:|"]
    for j in np.argsort(-s[0]):
        x = st["listas"][j]
        lo, hi = np.percentile(s[1:, j], [5, 95])
        L.append("| %s | %.2f | **%d** | %d–%d | %.0f %% |" % (nombre_de.get(x, x), pct[x], s[0, j], lo, hi,
                                                             100 * (s[1:, j] > 0).mean()))
    L += ["", "| Bloque | Bancas | Banda 90 % |", "|---|---:|---:|"]
    for k in ("bibi", "oposicion", "arabe"):
        L.append("| %s | %d | %d–%d |" % (k, b[k][0], *np.percentile(b[k][1:], [5, 95])))
    L += ["", "Netanyahu ≥ 61: **%.0f %%** · oposición judía ≥ 61: **%.0f %%** · nadie sin las listas árabes: "
          "**%.0f %%**" % (100 * pr["bibi"], 100 * pr["oposicion"], 100 * pr["empate"])]
    if "--prueba" not in sys.argv:
        L += [""] + ["Boca de urna %s: bibi %d · oposición %d · árabes %d (%s)." % (
            k, v["bibi"], v["oposicion"], v["arabe"], v["detalle"]) for k, v in BOCA.items()]
    out = os.path.join(HERE, "vivo_%s.md" % datetime.datetime.now().strftime("%H%M"))
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n".join(L), "\n->", out)
    txt = "Bancas proyectadas: " + ", ".join("%s %d" % (nombre_de.get(st["listas"][j], st["listas"][j]), s[0, j])
                                              for j in np.argsort(-s[0]) if s[0, j] > 0)
    p5, p25, p75, p95 = np.percentile(b["bibi"][1:], [5, 25, 75, 95])
    serie = historia(st, cnt, frac, b, acuerdos, blo) if "--prueba" not in sys.argv else None
    ad.dibujar_bancas(
        os.path.join(HERE, "..", "img", "aguja_israel_vivo.png"), titulo=titulo,
        subtitulo="Proyección urna por urna desde la elección de 2022 con %d urnas contadas (%.0f %% del padrón)." % (
            len(cnt), 100 * frac),
        bibi=int(b["bibi"][0]), p50=(p25, p75), p95=(int(p5), int(p95)),
        probs=[("Netanyahu ≥ 61", pr["bibi"], COLORES["bibi"]), ("Nadie sin las listas árabes", pr["empate"],
               COLORES["empate"]), ("Oposición judía ≥ 61", pr["oposicion"], COLORES["sin"])],
        colores=COLORES, serie=serie, bancas_txt=txt, momento=frac if serie else None,
        pie="Modelo de proyeccion/israel/modelo.py (backtest 2019–2022 en RESUMEN_BACKTEST.md). Antecesores y bloques "
            "de datos.LISTAS26.")
    import hemiciclo
    hs = hemiciclo.dibujar_ambos({nombre_de.get(x, x): s[0, j] for j, x in enumerate(st["listas"])},
                                 os.path.join(HERE, "..", "img", "knesset_vivo"), "Knesset 2026: bancas proyectadas",
                                 "%d urnas contadas (%.0f %% del padrón) · %s" % (len(cnt), 100 * frac, titulo[-5:]))
    print("->", *hs)
    html(L, os.path.join(HERE, "..", "img", "aguja_israel_vivo.png"), os.path.join(HERE, "vivo.html"), hs)


def historia(st, cnt, frac, b, acuerdos, blo):
    """Agrega esta corrida a vivo_historia.csv (una fila por archivo de datos) y devuelve la serie para la linea de
    tiempo de la aguja: bancas proyectadas por bloque con sus bandas y las del conteo tal cual."""
    vc = (st["Y"][cnt] * st["w"][cnt, None]).sum(0)
    sc = dt.bancas({st["dcols"][i]: vc[i] for i in range(len(st["dcols"]) - 1)}, acuerdos)
    bc = md.bloques(st, np.array([[sc[x] for x in st["listas"]]]), blo)
    r = dict(archivo=FUENTE, fraccion=frac, urnas=len(cnt), bibi=b["bibi"][0], opo=b["oposicion"][0],
             conteo_bibi=bc["bibi"][0], conteo_opo=bc["oposicion"][0])
    for k, kk in (("bibi", "b"), ("oposicion", "o")):
        for q in (5, 25, 75, 95):
            r["%s%d" % (kk, q)] = np.percentile(b[k][1:], q)
    path = os.path.join(HERE, "vivo_historia.csv")
    h = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    h = pd.concat([h[h.archivo != FUENTE] if len(h) else h, pd.DataFrame([r])]).sort_values("fraccion")
    h.to_csv(path, index=False)
    s = {c: list(h[c]) for c in h.columns if c not in ("archivo",)}
    s["x"] = s.pop("fraccion")
    s["xlabel"] = "urnas comunes contadas (escala logarítmica)"
    return s


def html(L, png, out, extra=()):
    """Pagina autocontenida (aguja y hemiciclos embebidos + tablas del informe) que se recarga sola cada minuto."""
    import base64, re
    b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()
    imgs = "".join("<img src='data:image/png;base64,%s'>" % b64(p) for p in (png,) + tuple(extra))
    fmt = lambda s: re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    body, tabla = [], []
    for ln in L[1:] + [""]:
        if ln.startswith("|"):
            if not set(ln) <= set("|-: "):
                tabla.append([c.strip() for c in ln.strip("|").split("|")])
            continue
        if tabla:
            body.append("<table><tr>%s</tr>%s</table>" % ("".join("<th>%s</th>" % c for c in tabla[0]), "".join(
                "<tr>%s</tr>" % "".join("<td>%s</td>" % fmt(c) for c in r) for r in tabla[1:])))
            tabla = []
        if ln:
            body.append("<p>%s</p>" % fmt(ln))
    open(out, "w", encoding="utf-8").write(
        "<!doctype html><html lang='es'><head><meta charset='utf-8'><meta http-equiv='refresh' content='60'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'><title>Aguja Knesset 2026</title><style>"
        "body{font-family:system-ui,sans-serif;max-width:900px;margin:auto;padding:16px;background:#fff;color:#222}"
        "img{width:100%%}table{border-collapse:collapse;margin:12px 0;width:100%%}td,th{padding:4px 8px;"
        "border-bottom:1px solid #ddd;text-align:right}td:first-child,th:first-child{text-align:left}</style></head>"
        "<body><h1>%s</h1>%s%s</body></html>" % (L[0][2:], imgs, "".join(body)))
    print("->", out)


if __name__ == "__main__":
    main()
