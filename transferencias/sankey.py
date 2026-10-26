"""Diagrama de transferencias (sankey) en SVG a partir de transferencias/<o>_<d>/matriz_votos.csv.
    python transferencias/sankey.py 2021 2025
    python transferencias/sankey.py 2023p 2025 --votantes   # sin «No votó» en origen ni destino -> sankey_<o>_<d>_votantes.*
    python transferencias/sankey.py 2023p 2025 --reducido   # «No votó» dibujado a escala 1:4, cifras reales -> sankey_<o>_<d>_reducido.*
Escribe transferencias/<o>_<d>/sankey_<o>_<d>.svg y .html. Colores de los atlas (dataset_<anio>.json)."""
import os, re, sys, html, unicodedata, json
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))

COL = {"Frente de Todos": "#2ea3ff", "Juntos por el Cambio": "#f4ce00", "Libertarios (AL + LLA)": "#6c4c98",
       "FIT-U": "#f65058", "Tercera Vía / PF": "#2f3b81", "Unión por la Patria": "#009ce4",
       "La Libertad Avanza": "#6c4c98", "Hacemos": "#283084", "Fuerza Patria": "#009ce4",
       "Provincias Unidas": "#FF682C", "Frente para la Victoria": "#50ade6", "UDESO (UCR)": "#d31515",
       "FAP": "#ff6600", "Frente Popular / PRO": "#b73c96", "Frente Popular": "#b73c96", "Compromiso Federal": "#1aff98", "CC-ARI": "#6FB53E",
       "FIT": "#f65058", "Consenso Federal": "#2f3b81", "NOS + Unite": "#8d6e63", "FPCyS / UNEN": "#ff6600",
       "Frente Renovador": "#3d454d", "Acuerdo Cívico y Social": "#e10019", "PRO / Unión-PRO": "#f4ce00",
       "Peronismo Federal": "#1aff98", "Proyecto Sur": "#389b00", "PRO": "#f4ce00", "Unión por Córdoba": "#19bc9d", "Partido Peronista": "#318ce7", "UCR": "#e10019", "UCRI (Frondizi)": "#f4845f", "UCRP (Balbín)": "#e10019", "Unión Popular": "#009999", "UP y neoperonistas": "#009999", "UCRP": "#e10019", "MID": "#0f2b3d", "UCRI": "#f4845f", "FNPC (centro)": "#1f2f6b", "Kirchner (FPV)": "#1c5ece", "Menem (Lealtad)": "#87ceeb", "López Murphy (Recrear)": "#f4ce00", "Rodríguez Saá (MNP)": "#1aff98", "Carrió (ARI)": "#74b744", "UCR y aliados": "#e10019", "ARI y aliados": "#74b744", "FPCyS (Santa Fe)": "#ff6600", "Cristina Kirchner (FPV)": "#50ade6", "Carrió (CC)": "#74b744", "Lavagna (UNA)": "#d31515", "Rodríguez Saá (FREJULI)": "#1aff98", "Cambiemos": "#f4ce00", "UNA (Massa)": "#231f20", "Progresistas": "#ff6600", "UCR (yrigoyenismo)": "#e10019", "Conservadores": "#30d5c8", "Antipersonalistas": "#76acdc", "Socialistas": "#ff9900", "UCR (Alvear)": "#e10019", "Concordancia (Ortiz)": "#30d5c8", "Concordancia": "#30d5c8", "Socialista": "#ff9900", "Perón": "#318ce7", "Unión Democrática": "#f0566a", "Demócrata Nacional": "#1fa89d", "UCR (Alfonsín)": "#e10019", "PJ (Luder)": "#318ce7", "PI": "#d10047", "PJ": "#318ce7", "UCeDé": "#8e6bd8", "CFI": "#f59e0b", "MODIN": "#e67e22", "PJ (Menem)": "#318ce7", "UCR (Massaccesi)": "#e10019", "FREPASO (Bordón)": "#a349a4", "FREPASO": "#a349a4", "Acción por la República": "#3e5298", "Alianza (De la Rúa)": "#dc0143", "PJ (Duhalde)": "#318ce7", "AR (Cavallo)": "#3e5298", "Alianza": "#dc0143", "Nuevo Movimiento": "#00897b", "Acción Vecinal": "#9ccc65", "Otros": "#9e9e9e", "Blanco y nulo": "#5b5b5b", "No votó": "#c8c8c8"}
COL.update({"Unidad Ciudadana": "#2ea3ff", "Peronismo no kirchnerista": "#1aff98", "1País": "#D0D0D0"})
JXC = {2023: "#fcbc00"}
COL.update({"Massa (UxP)": "#009ce4", "Grabois (UxP)": "#7fd0f5", "Milei (LLA)": "#6c4c98", "Bullrich (JxC)": "#fcbc00",
            "Larreta (JxC)": "#ffe680", "Schiaretti (Hacemos)": "#283084"})   # PASO 2023: el precandidato perdedor en un tono más claro
COL.update({'UCR (Angeloz)':'#e10019', 'Alianza de Centro':'#8e6bd8', 'Unidad Socialista':'#ff9900', 'MPN':'#14306e', 'Izquierda Unida':'#d10047', 'Frente Grande':'#a349a4', 'Fuerza Republicana':'#7b3f00', 'PD':'#1f4096', 'PAL':'#40e0d0', 'MPJ':'#f59e0b', 'PRS':'#cddc39', 'Convocatoria Independiente':'#ff69b4'})
COL.update({'Peronismo renovador':'#f59e0b','Frente del Pueblo':'#b51d27','Bloquista':'#44944a','FAP (Catamarca)':'#f59e0b','PPR':'#b5651d'})
COL.update({'Alianza Federal':'#f59e0b','MOFEPA':'#0097a7','Partido Nuevo':'#ff8800','Desarrollo y Justicia':'#00bfc4'})
COL.update({'Unión Cívica':'#222222','Independientes (Peña)':'#777777','PDP':'#005c9e','Socialista Argentino':'#b73c96','Radicales disidentes':'#a52a2a','Concentración Cívica':'#35aae0'})
W, H, TOP, GAP, NODE = 900, 760, 90, 10, 18
X0, X1 = 250, 650


def fmt(p):
    return ("%.1f" % p).replace(".", ",") + " %"


REDUCIDO = 0.25     # escala de «No votó» en la versión --reducido


def main(y0, y1, votantes=False, reducido=False):
    d = os.path.join(HERE, "%s_%s" % (y0, y1))
    cba = str(y0).endswith("c")     # Córdoba por circuito (cordoba_circuitos.py)
    emi = str(y0).endswith("e")     # nacional sobre votos emitidos, por departamento y Córdoba por circuito (presidente_1999.py)
    n0, n1 = (str(y)[:-1] if str(y).endswith(("c", "e")) else str(y) for y in (y0, y1))
    cargo = "Presidente" if n0.endswith(("p", "b")) else "Diputados nacionales"
    t0, t1 = n0.rstrip("pbd"), n1.rstrip("pbd")
    if n0 == "1954p":      # Canton: diputados 1954 (vicepresidente/delegados en territorios) -> presidente 1958
        cargo, t0, t1 = "Diputados", "1954", "presidente 1958"
    if n0.endswith("p") and not n1.endswith(("p", "b")) and n0 != "1954p":   # presidente -> diputados
        t1 = "diputados " + t1
    if n0 in ("1930d", "1937d", "1940d"):    # Canton: diputados 1930/1940 o presidente 1937 -> presidente 1946
        cargo, t0, t1 = ("Presidente" if n0 == "1937d" else "Diputados"), t0, "presidente 1946"
    if n0 == "1958d":      # Canton: presidente 1958 -> diputados 1962
        cargo, t0, t1 = "Presidente", "1958", "diputados 1962"
    if n1.endswith("b"):   # balotaje: «2023, 1.ª vuelta → balotaje» o «2019 → balotaje 2023»
        t0, t1 = (t0 + ", 1.ª vuelta", "balotaje") if t0 == t1 else (t0, "balotaje " + t1)
    if str(y0) in ("2015p", "2015b") and str(y1) in ("2023p", "2023b"):
        t0 = "2015, " + ("general" if n0.endswith("p") else "balotaje")
        t1 = "2023, " + ("general" if n1.endswith("p") else "balotaje")
    if y0 in (2009, 2013) and str(y1) in ("2015p", "2015b"):
        t1 = "presidente 2015, " + ("general" if n1.endswith("p") else "balotaje")
    if y0 == 2017 and y1 == "2019p":
        t1 = "presidente 2019"
    if str(y0) in ("2015p", "2015b") and y1 == "2019p":
        t0 = "2015, " + ("general" if n0.endswith("p") else "balotaje")
        t1 = "2019, general"
    if str(y0) in ("2023pp", "2023p", "2023b") and y1 == 2025:   # presidente 2023 (PASO, general o balotaje) -> diputados 2025
        cargo, t0, t1 = "Presidente", {"2023pp": "2023, PASO", "2023p": "2023, general", "2023b": "2023, balotaje"}[str(y0)], "diputados 2025"
    if cba: cargo = "Córdoba: " + cargo.lower()
    historical = (y0, y1) in [('1989p','1995p'), ('1989d','1994c'), ('1985d','1987d'),('1983p','1989p'),('1987d','1989p'),('1985d','1989p'),('1989p','1997d')]
    historical |= (y0,y1) in [('1995p','1997d'),('1995p','1999p'),('1983p','1985d')]
    historical |= (y0,y1)==('1914d','1916d')
    if historical and y1 == '1989p' and y0.endswith('d'): t1 = 'presidente 1989'
    if y1 == '1994c': t1 = 'constituyentes 1994'
    M = pd.read_csv(os.path.join(d, "matriz_votos.csv"), index_col=0, encoding="utf-8-sig")
    from auditar import auditar
    aud = auditar("%s_%s" % (y0, y1))
    ctl = json.load(open(os.path.join(d, "control.json"), encoding="utf8"))
    from estimar import DISTRITOS
    if y0=='1914d':
        DISTRITOS=dict(DISTRITOS);DISTRITOS['01']='Capital Federal'

    def dibujar(M, prov=None):
        if votantes:    # solo quienes votaron en las dos: misma estimación, sin la fila ni la columna «No votó»
            M = M.drop(index="No votó", columns="No votó", errors="ignore")
        M = M.loc[M.sum(1) > 0, M.sum(0) > 0]      # sin categorias vacias (p. ej. Proyecto Sur sin Capital en 2003 -> 2009)
        """SVG del sankey de la matriz M; prov: nombre de la provincia (sin auditoría por fila, que es nacional)."""
        tot = M.values.sum(); usable = H - TOP - 60
        G = M.copy()        # geometría: igual a M salvo en --reducido, donde «No votó» se dibuja a escala REDUCIDO
        if reducido:
            nv = (G.index == "No votó")[:, None] | (G.columns == "No votó")[None, :]
            G = G.where(~nv, G * REDUCIDO)
        k0 = (usable - GAP * (len(M) - 1)) / G.values.sum(); k1 = (usable - GAP * (len(M.columns) - 1)) / G.values.sum()

        def col(name, y):
            y = int(str(y).rstrip("pbdce"))
            return JXC[y] if name == "Juntos por el Cambio" and y in JXC else COL.get(name, "#888")

        def nodes(sizes, k):
            y, out = TOP, {}
            for n, v in sizes.items():
                out[n] = [y, v * k]; y += v * k + GAP
            return out

        L, R = nodes(G.sum(1), k0), nodes(G.sum(0), k1)
        noid = set() if prov else {f["origen"] for f in aud["filas"] if f["no_identificada"]}
        cerca = set() if prov else {f["origen"] for f in aud["filas"] if f["cerca_promedio"]}
        notas = ["Matriz provincial, penalizada hacia la nacional: con pocas unidades se parece a ella. La auditoría por fila (* y †) es solo nacional."] if prov else []
        if reducido: notas.append("«No votó» y sus cintas están dibujados a escala 1:%d para ahorrar espacio; las cifras son las reales." % round(1 / REDUCIDO))
        if noid: notas.append("* Fila no identificada: los datos no alcanzan para saber adónde fue; las dos variantes del modelo no coinciden (ver AUDITORIA.md).")
        if cerca: notas.append("† Fila cerca del promedio: se reparte casi como el total; puede ser un reparto real o falta de señal para esa fila (ver AUDITORIA.md).")
        unidad = "departamento; Córdoba por circuito" if emi else "departamento" if int(n0.rstrip("pbd")) < 1960 else "circuito"
        if ctl.get("unidades_por_provincia") and ctl.get("correspondencias"):
            ids = [k for k in ctl["unidades_por_provincia"] if not prov or DISTRITOS.get(k) == prov]
            counts = {k: sum(ctl["unidades_por_provincia"][dd][k] for dd in ids)
                      for k in ("circuitos", "grupos_circuitos", "departamentos")}
            resumen = ", ".join(f"{n:,} {k.replace('_', ' ')}".replace(",", ".") for k, n in counts.items() if n)
            if int(n0.rstrip('pbd'))<1960:
                resumen=resumen.replace('grupos circuitos','grupos territoriales').replace('departamentos','deptos./circunscripciones')
            if y0=='1914d':resumen=f"{sum(counts.values())} unidades comunes (departamentos, circunscripciones y grupos)"
            notas.append("Base del ajuste: " + resumen + ". Correspondencias y reservas: ver LEEME.md y correspondencias.csv.")
            if not prov:
                cov = 100 * ctl["electores_origen_usados"] / ctl["electores_origen_total"]
                base = 'voto desglosado' if historical else 'padrón'
                if y0=='1914d':base='voto desglosado de la selección disponible'
                notas.append("Cobertura: " + fmt(cov) + " del " + base + " de origen. Uniones completas; sin repartir votos.")
            unidad = "unidades compatibles"
            if historical:
                unidad = 'departamentos y circunscripciones'
                notas.append('Sobre votos desglosados; sin abstención. ' + ('Deseado 1995 extrapolado. ' if '1995p' in (y0,y1) and y1!='1999p' else '') + 'Ver RESUMEN.md.')
                if not prov:
                    missing=[name for dd,name in DISTRITOS.items() if dd not in ctl['unidades_por_provincia']]
                    if missing and y0!='1914d': notas.append('Sin estimación por falta de unidades utilizables: '+', '.join(missing)+'. Ver RESUMEN.md.')
                    if y0=='1914d':notas.append('Selección territorial parcial; se excluyen lecturas dudosas y provincias sin desglose. No es un total nacional.')
                elif y0=='1914d' and sum(counts.values())<5:
                    notas.append('Menos de cinco unidades: matriz provincial sin identificación suficiente; depende del centro nacional.')
                elif y0=='1914d' and prov=='Capital Federal':
                    notas.append('Conservadores y Unión Cívica: reparto provincial inestable entre variantes; ver Capital.md.')
            if prov and counts["circuitos"] and not (counts["grupos_circuitos"] or counts["departamentos"]):
                unidad = "circuito"
        titulo = "Transferencias de votos" + (": " + prov if prov else " (cobertura parcial)" if y0=='1914d' else "")
        ajuste_titulo = ' textLength="850" lengthAdjust="spacingAndGlyphs"' if len(titulo) > 49 else ""
        subtitulo = f"{cargo} {t0} → {t1} (inferencia ecológica por {unidad})"
        ajuste_subtitulo = ' textLength="850" lengthAdjust="spacingAndGlyphs"' if len(subtitulo) > 90 else ""
        HH = H + 18 * max(0, len(notas) - 1) + (20 if y0=='1914d' else 0)
        s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="Helvetica, Arial, sans-serif">' % (W, HH),
             '<rect width="100%" height="100%" fill="#fff"/>',
             '<text x="%d" y="40" font-size="30" font-weight="bold" text-anchor="middle" fill="#333"%s>%s</text>' % (W / 2, ajuste_titulo, html.escape(titulo)),
             '<text x="%d" y="68" font-size="17" font-weight="bold" text-anchor="middle" fill="#444"%s>%s</text>' % (W / 2, ajuste_subtitulo, html.escape(subtitulo))]
        lo, ro = {n: v[0] for n, v in L.items()}, {n: v[0] for n, v in R.items()}
        flows = []
        for a in M.index:
            for b in M.columns:
                v = M.loc[a, b]
                if v <= 0: continue
                h0, h1 = G.loc[a, b] * k0, G.loc[a, b] * k1
                ya, yb = lo[a], ro[b]; lo[a] += h0; ro[b] += h1
                if v / tot < 0.0005: continue            # cintas de menos de 0,05 % del padron: no se dibujan
                c = (X0 + X1) / 2
                p = "M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f L%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1fZ" % (
                    X0 + NODE, ya, c, ya, c, yb, X1, yb, X1, yb + h1, c, yb + h1, c, ya + h0, X0 + NODE, ya + h0)
                flows.append('<path d="%s" fill="%s" fill-opacity="0.45"><title>%s → %s: %s votos\n%s del origen (%s)\n%s del destino (%s)%s</title></path>' % (
                    p, col(a, y0), html.escape(a), html.escape(b), f"{round(v):,}".replace(",", "."),
                    fmt(100 * v / M.loc[a].sum()), html.escape(a), fmt(100 * v / M[b].sum()), html.escape(b),
                    "\n(fila no identificada)" if a in noid else ""))
        s += flows
        def label_positions(nodes):
            result, last = {}, TOP - 14
            for name, (y,h) in nodes.items():
                result[name] = max(y+h/2,last+14) if historical else y+h/2
                last = result[name]
            return result
        ly, ry = label_positions(L), label_positions(R)
        for n, (y, h) in L.items():
            s.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s"/>' % (X0, y, NODE, max(h, 1), col(n, y0)))
            s.append('<text x="%d" y="%.1f" font-size="14" font-weight="bold" text-anchor="end" dominant-baseline="middle" fill="#222">%s: %s</text>' % (X0 - 8, ly[n], html.escape(n) + (" *" if n in noid else "") + (" †" if n in cerca else ""), fmt(100 * M.loc[n].sum() / tot)))
        for n, (y, h) in R.items():
            s.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s"/>' % (X1, y, NODE, max(h, 1), col(n, y1)))
            label = html.escape(n) + ": " + fmt(100 * M[n].sum() / tot)
            fit_label = ' textLength="210" lengthAdjust="spacingAndGlyphs"' if len(label) > 30 else ""
            s.append('<text x="%d" y="%.1f" font-size="14" font-weight="bold" dominant-baseline="middle" fill="#222"%s>%s</text>' % (X1 + NODE + 8, ry[n], fit_label, label))
        s.append('<text x="20" y="%d" font-size="11.5" fill="#555">Porcentajes sobre el padrón %s de los %s usados. Método: mínimos cuadrados penalizados RxC (código de E. Calvo), una matriz por provincia.</text>' % (HH - 30, ("del balotaje " + n1.rstrip("b")) if n1.endswith("b") else "de " + n1.rstrip("pd"), "departamentos" if int(n0.rstrip("pbd")) < 1960 else "circuitos"))
        if emi:
            s[-1] = s[-1].replace("Porcentajes sobre el padrón de %s de los circuitos usados" % n1.rstrip("pd"),
                                  "Porcentajes sobre los votos emitidos de %s (como Calvo y Escolar, 2005)" % n1.rstrip("pd")).replace(" (código de E. Calvo)", "")
        if cba:     # votos emitidos, no padrón; fuentes de Córdoba
            s[-1] = s[-1].replace("Porcentajes sobre el padrón de %s de los circuitos usados" % n1.rstrip("pd"),
                                  "Porcentajes sobre los votos emitidos de %s en los circuitos usados (no hay electores por circuito)" % n1.rstrip("pd")).replace(", una matriz por provincia", "")
        if ctl.get("correspondencias"):
            s[-1] = s[-1].replace("de los circuitos usados", "de las unidades usadas")
        if historical:
            s[-1] = s[-1].replace('Porcentajes sobre el padrón', 'Porcentajes sobre votos desglosados')
        if votantes:
            s[-1] = re.sub(r">Porcentajes sobre .*</text>", ">Sin «No votó»: % sobre quienes votaron en las dos elecciones (misma estimación). Método: RxC penalizado (E. Calvo), por provincia.</text>", s[-1])
        if y0=='1914d':s[-1]=s[-1].replace('votos desglosados','votos partidarios publicados')
        if y0=='1914d':s[-1]=f'<text x="20" y="{HH-30}" font-size="11.5" fill="#555">Porcentajes sobre votos partidarios publicados de 1916. Ajuste RxC penalizado por provincia; ver RESUMEN.md.</text>'
        fuente = ("E. Calvo (Córdoba por circuito), Lupu y Stokes (San Luis, Santa Cruz) y PolAr" if emi else
                  "E. Calvo, Córdoba por circuito" + (", y PolAr (A. Tow), por mesa" if int(n1.rstrip("pbd")) >= 2003 else "") if cba else
                  "Cantón, Materiales... (1968), t. II, por departamento" if int(n0.rstrip("pbd")) < 1960 else
                  "PolAr (Atlas Electoral de A. Tow), por mesa" if int(n1.rstrip("pbd")) <= 2009 else
                  "PolAr (Atlas Electoral de A. Tow) y DINE, por mesa" if int(n0.rstrip("pbd")) <= 2009 else "DINE, escrutinio provisorio por mesa")
        if historical: fuente = 'Base departamental de E. Calvo; agrupaciones de los atlas locales'
        if y0=='1914d':fuente='Cantón y actas HCDN, transcripciones locales; sin cifras estimadas ni duplicación de datos compartidos'
        s.append('<text x="20" y="%d" font-size="11.5" fill="#555">Fuente: %s. Las celdas de categorías chicas (&lt;5 %%) tienen márgenes de error grandes: ver intervalos.csv.</text>' % (HH - 12, fuente))
        if y0=='1914d':s[-1]=f'<text x="20" y="{HH-12}" font-size="11.5" fill="#555">Fuentes: Cantón y actas HCDN, transcripciones locales. Sin cifras estimadas ni duplicación de datos compartidos.</text>'
        for i, t in enumerate(notas):
            s.append('<text x="20" y="%d" font-size="11.5" fill="#555">%s</text>' % (HH - 48 - 18 * i, html.escape(t)))
        if aud["poco_informativa"] and not prov:
            s.append('<text x="%d" y="86" font-size="12.5" font-weight="bold" text-anchor="middle" fill="#a40000">Matriz poco informativa: el voto de origen casi no predice el de destino, y las filas repiten el promedio por falta de señal (ver AUDITORIA.md).</text>' % (W / 2))
        s.append("</svg>")
        return "\n".join(s)

    svg = dibujar(M)
    suf = "_votantes" if votantes else "_reducido" if reducido else ""
    open(os.path.join(d, "sankey_%s_%s%s.svg" % (y0, y1, suf)), "w", encoding="utf8").write(svg)
    # HTML: nacional y una vista por provincia (por_provincia.csv), con un selector
    vistas = [("nacional", "Total parcial" if y0=='1914d' else "Nacional", svg)]
    f = os.path.join(d, "por_provincia.csv")
    if os.path.exists(f):
        P = pd.read_csv(f, dtype={"distrito": str}, encoding="utf-8-sig")
        P["distrito"] = P.distrito.str.zfill(2)
        for dd, g in sorted(P.groupby("distrito"), key=lambda x: unicodedata.normalize("NFD", DISTRITOS.get(x[0], x[0])).encode("ascii", "ignore")):
            Mp = g.pivot_table(index="origen", columns="destino", values="votos", aggfunc="sum").reindex(index=M.index, columns=M.columns).fillna(0)
            if Mp.values.sum() > 0 and P.distrito.nunique() > 1:
                vistas.append((dd, DISTRITOS.get(dd, dd), dibujar(Mp, DISTRITOS.get(dd, dd))))
    sel = "" if len(vistas) == 1 else (
        '<div style="padding:10px 16px;font:15px Helvetica,Arial,sans-serif"><label for="v">Provincia:</label> <select id="v" style="font-size:15px">%s</select></div>'
        % "".join('<option value="%s">%s</option>' % (k, html.escape(n)) for k, n, _ in vistas))
    divs = "".join('<div class="vista" id="v-%s"%s>%s</div>' % (k, "" if i == 0 else " hidden", sv) for i, (k, _, sv) in enumerate(vistas))
    js = "" if len(vistas) == 1 else (
        "<script>const s=document.getElementById('v');function ver(k){document.querySelectorAll('.vista').forEach(e=>e.hidden=e.id!=='v-'+k);s.value=k;}"
        "s.onchange=()=>{ver(s.value);history.replaceState(null,'','#'+s.value);};"
        "function desdeHash(){const k=location.hash.slice(1);ver(document.getElementById('v-'+k)?k:'nacional');}"
        "window.addEventListener('hashchange',desdeHash);desdeHash();</script>")
    open(os.path.join(d, "sankey_%s_%s%s.html" % (y0, y1, suf)), "w", encoding="utf8").write(
        '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Transferencias %s-%s</title>'
        '<style>body{margin:0;background:#fff}.vista svg{display:block;width:100%%;max-width:900px;height:auto}.vista path:hover{fill-opacity:.8;cursor:help}</style><body>%s%s%s</body>' % (y0, y1, sel, divs, js))


if __name__ == "__main__":
    main(*[a if a.endswith(("p", "b", "d", "c", "e")) else int(a) for a in sys.argv[1:3]], votantes="--votantes" in sys.argv, reducido="--reducido" in sys.argv)
