"""Córdoba por circuito, 1983-2001, de los archivos de Ernesto Calvo (Bases Ernesto/Cordoba x circuito), en el formato de
agregar_circuitos.py -> transferencias/circ_<año>c.pkl (presidente: circ_<año>pc.pkl).
    python transferencias/cordoba_circuitos.py
    python transferencias/estimar.py 1995pc 1999pc
Once formatos distintos, uno por año. Ninguno trae electores por circuito salvo 1991, así que el análisis es sobre votos
emitidos: «electores» = votos emitidos y no hay categoría «No votó». La clave es el número de circuito sin ceros a la
izquierda (1, 4A, 10L); la sección sale de PolAr 2003 para empalmar con circ_2003p.pkl. 1997 no trae el número: se toma
del nombre del circuito en 1995 y 1999 (solo nombres que no se repiten). Detalle en LEEME.md."""
import os, re, sys, unicodedata, warnings
import pandas as pd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "Bases Ernesto", "Cordoba x circuito")


def code(x):
    s = str(x).strip().upper().replace("*", "").replace(" ", "")
    s = re.sub(r"\.0$", "", s)
    m = re.match(r"^0*(\d+)([A-Z]?)$", s)
    return m.group(1) + m.group(2) if m else None


def norm(s):
    return " ".join(unicodedata.normalize("NFD", str(s).upper()).encode("ascii", "ignore").decode().replace(".", " ").split())


def x(f):
    return os.path.join(SRC, f)


def p1983():
    out = []
    xl = pd.ExcelFile(x("04001ENP1983T.xls"))
    for s in xl.sheet_names[1:]:
        d = xl.parse(s, header=None)
        cur = None
        for _, r in d.iterrows():
            lab = str(r[1]).strip()
            if lab in ("POS", "TOT") or lab.startswith("SECCI"): continue
            if code(lab) and not lab.isalpha():
                cur = code(lab); continue
            if cur is None or not lab.isalpha(): continue
            for cargo, c in (("p", 2), ("", 3)):
                v = pd.to_numeric(r[c], errors="coerce")
                if v == v: out.append(dict(anio="1983" + cargo, circ=cur, nombre=str(r[0]), partido=lab, v=v))
    return out


def ancho(f, hoja, anio, suf):
    d = pd.read_excel(x(f), hoja)
    out = []
    for _, r in d.iterrows():
        c = code(r["numero"])
        if not c: continue
        for k in d.columns:
            m = re.match(r"^([a-z]+)\d\d(%s)?$" % suf, k)
            if not m or (m.group(2) is None and k != "fdp85") or m.group(1) in ("pos", "tot"): continue
            v = pd.to_numeric(r[k], errors="coerce")
            if v == v: out.append(dict(anio=anio, circ=c, nombre=r["circuito"], partido=m.group(1), v=v))
    return out


def p1991():
    d = pd.read_excel(x("04001ENP1991T.xls"), "DATOS", header=None)
    cols = [c for c in d.columns if d.iloc[2, c] == "Diputado Nacional"]
    out = []
    for i in range(8, len(d)):
        c = code(d.iloc[i, 3])
        if not c: continue
        for k in cols:
            v = pd.to_numeric(d.iloc[i, k], errors="coerce")
            if v == v: out.append(dict(anio="1991", circ=c, nombre=d.iloc[i, 2], partido=str(d.iloc[i, k] and d.iloc[4, k]), v=v))
    return out


def largo(f, hoja, filtro, ccirc, cnom, cpart, cargos, cod4=True):
    """cod4: el circuito viene con cuatro cifras (0001, 0004A); las filas con otro formato son subtotales (departamento, distrito)."""
    d = pd.read_excel(x(f), hoja, header=None)
    if filtro is not None: d = d[d[0].astype(str).str.strip().str.upper() == filtro]
    out, nom = [], None
    for _, r in d.iterrows():
        c = code(r[ccirc])
        if not c or (cod4 and not re.match(r"^\d{4}[A-Z]?$", str(r[ccirc]).strip())): continue
        if cnom is not None and str(r[cnom]) != "nan": nom = r[cnom]
        for anio, k in cargos:
            v = pd.to_numeric(r[k], errors="coerce")
            if v == v: out.append(dict(anio=anio, circ=c, nombre=nom, partido=str(r[cpart]).strip(), v=v))
    return out


def p1997(nombres):
    out = []
    for f, h in (("04001ENP1997F.xls", "CIRCUIF"), ("04001ENP1997M.xls", "CIRCUIM")):
        d = pd.read_excel(x(f), h, header=None).iloc[1:]
        for _, r in d.iterrows():
            c = nombres.get(norm(r[0]))
            v = pd.to_numeric(r[3], errors="coerce")
            if c and v == v: out.append(dict(anio="1997", circ=c, nombre=r[0], partido=str(r[2]).strip(), v=v))
    return out


def leer():
    L = p1983()
    L += ancho("04001ENP1985T.xls", "elecc.85", "1985", "dn")
    L += ancho("04001ENP1987T.xls", "elecc.87", "1987", "dn")
    L += p1991()
    L += largo("04001ENP1993T.xls", "Sheet 1", "CIRCUITO", 1, 2, 4, [("1993", 5)])
    L += largo("04001ENP1995T.xls", "Hoja1", None, 0, 1, 3, [("1995p", 4), ("1995", 5)])
    L += largo("04001ENP1999T.xls", "ARMARES", "CIRCUITO", 1, 2, 4, [("1999p", 5), ("1999", 6)])
    L += largo("04001ENP2001T.xls", "Hoja1", "CIRCUITO", 2, 1, 4, [("2001", 6)], cod4=False)
    D = pd.DataFrame(L)
    # nombres de 1995 y 1999 -> número, para 1997
    n = D[D.anio.isin(["1995", "1999"])].drop_duplicates(["circ", "nombre"])
    n["k"] = n.nombre.map(norm)
    g = n.groupby("k").circ.nunique()
    nombres = n[n.k.isin(g[g == 1].index)].drop_duplicates("k").set_index("k").circ.to_dict()
    D = pd.concat([D, pd.DataFrame(p1997(nombres))])
    D["partido"] = D.partido.map(norm)
    return D


# partido (nombre normalizado o sigla de Ernesto) -> bloque; blancos y nulos aparte; lo demás «OTRO»
BLANCO = {"BLA", "NUL", "BLANCOS", "NULOS", "VOTOS EN BLANCO", "VOTOS NULOS"}
FUERA = {"TOTALES", "VOTOS IMPUGNADOS", "VOTOS RECURRIDOS", "ELECTORES"}
BLOQUE = {
    "1983p": {"PJ": "PJ", "UCR": "UCR", "PI": "PI"}, "1983": {"PJ": "PJ", "UCR": "UCR", "PI": "PI"},
    "1985": {"PJ": "PJ", "UCR": "UCR", "PI": "PI", "UDC": "UCEDE"},
    "1987": {"PJ": "PJ", "UCR": "UCR", "UDC": "UCEDE"},
    "1991": {"PARTIDO JUSTICIALISTA": "PJ", "UNION CIVICA RADICAL": "UCR", "U C D": "UCEDE", "C F I": "CFI"},
    "1993": {"PARTIDO JUSTICIALISTA": "PJ", "UNION CIVICA RADICAL": "UCR", "UNION DEL CENTRO DEMOCRATICO": "UCEDE",
             "MOV DIGNIDAD E INDEPENDENCIA": "MODIN"},
    "1995p": {"PARTIDO JUSTICIALISTA": "PJ", "UNION CIVICA RADICAL": "UCR", "ALIANZA FRENTE PAIS SOLIDARIO": "FREPASO",
              "UNION DEL CENTRO DEMOCRATICO": "UCEDE"},
    "1995": {"PARTIDO JUSTICIALISTA": "PJ", "UNION CIVICA RADICAL": "UCR", "ALIANZA FRENTE PAIS SOLIDARIO": "FREPASO",
             "UNION DEL CENTRO DEMOCRATICO": "UCEDE"},
    "1997": {"PARTIDO JUSTICIALISTA": "PJ", "UNION CIVICA RADICAL": "UCR", "ALIANZA FREPASO": "FREPASO",
             "ALIANZA ACCION POR LA REP-PAIS": "AR", "UNION DE CENTRO DEMOCRATICO": "UCEDE"},
    "1999p": {"A P/EL TRAB JUSTICIA Y EDUC": "ALIANZA", "A CONCERT JUSTIC P/CAMBIO": "PJ", "A NAC ACCION POR LA REPUBLICA": "AR",
              "UNION DE CENTRO DEMOCRATICO": "UCEDE"},
    "1999": {"A P/EL TRAB JUSTICIA Y EDUC": "ALIANZA", "PARTIDO JUSTICIALISTA": "PJ", "ACCION POR LA REPUBLICA": "AR",
             "UNION DE CENTRO DEMOCRATICO": "UCEDE", "NUEVO MOVIMIENTO": "NM"},
    "2001": {"PARTIDO JUSTICIALISTA": "PJ", "UNION CIVICA RADICAL": "UCR", "UNION DEL CENTRO DEMOCRATICO": "UCEDE",
             "MOVIMIENTO ACCION VECINAL": "MAV"},
}


def guardar(D, anio, sec):
    T = D[(D.anio == anio) & ~D.partido.isin(FUERA)].copy()
    T["bloque"] = [("BLANCO" if p in BLANCO else BLOQUE[anio].get(p, "OTRO")) for p in T.partido]
    T = T.groupby(["circ", "bloque"]).v.sum().unstack(fill_value=0)
    T = T[T.sum(1) > 0]
    v, e = [], {}
    for c, r in T.iterrows():
        key = ("04", sec.get(c, 0), c)
        e[key] = r.sum()
        for b, val in r.items():
            if b == "BLANCO": v.append(dict(distrito_id="04", seccion_id=key[1], circuito=c, agrupacion_id="", votos_tipo="EN BLANCO", v=val))
            else: v.append(dict(distrito_id="04", seccion_id=key[1], circuito=c, agrupacion_id=b, votos_tipo="POSITIVO", v=val))
    idx = ["distrito_id", "seccion_id", "circuito"]
    v = pd.DataFrame(v)
    e = pd.Series(e); e.index = pd.MultiIndex.from_tuples(e.index, names=idx)
    pd.to_pickle((v, e), os.path.join(HERE, "circ_%sc.pkl" % anio))
    tot = T.sum()
    print("%-6s circuitos %4d  votos %9d  | %s" % (anio, len(T), T.values.sum(), "  ".join("%s %.1f" % (b, 100 * t / tot.sum()) for b, t in tot.sort_values(ascending=False).items())))


def main():
    D = leer()
    _, e03 = pd.read_pickle(os.path.join(HERE, "circ_2003p.pkl"))
    sec = {c: s for d, s, c in e03.index if d == "04"}
    for a in BLOQUE: guardar(D, a, sec)
    # presidente 2003 (PolAr) solo Córdoba y sobre votos emitidos, para empalmar sin «No votó»
    v03, _ = pd.read_pickle(os.path.join(HERE, "circ_2003p.pkl"))
    v03 = v03[v03.distrito_id == "04"]
    e = v03.groupby(["distrito_id", "seccion_id", "circuito"]).v.sum()
    pd.to_pickle((v03, e), os.path.join(HERE, "circ_2003pc.pkl"))
    print("2003p  circuitos %4d  votos %9d (PolAr)" % (len(e), e.sum()))
    if "--otros" in sys.argv:     # partidos que caen en «OTRO», para revisar el mapeo
        for a in BLOQUE:
            t = D[(D.anio == a) & ~D.partido.isin(FUERA | BLANCO) & ~D.partido.isin(BLOQUE[a])].groupby("partido").v.sum()
            print(a, t.sort_values(ascending=False).head(6).astype(int).to_dict())


if __name__ == "__main__":
    main()
