"""Transcripciones propias -> formato largo del MASTER (resultados_xlsx/MASTER_resultados.xlsx).

    python comun/transcripciones_xlsx.py   -> agrega (o reemplaza) estas elecciones en el MASTER ya generado,
                                          sin volver a correr exportar_xlsx.py; escribe por_eleccion/ y el indice

exportar_xlsx.py tambien llama a frames(), asi que una regeneracion completa las incluye.

Elecciones:
  - 1912 y 1914 diputados: busqueda1912/datos_1912_depto.csv, busqueda1914/datos_1914_depto.csv
    (+ busqueda1914/datos_1914_parciales.csv como fuente_id «parciales»: Santa Fe, Jujuy y Tucuman, cobertura parcial)
  - 1937 presidente y 1940 diputados: canton1937_1940/canton_1937_1940_1946.csv
  - 1946 presidente: canton1946/canton_1946.csv
  - 1954 diputados, vicepresidente y delegados: canton1954/canton_1954.csv
  - 1958 presidente y diputados, 1962 y 1965 diputados: canton5865 (transcripcion con las correcciones de correcciones.py)
Cifras tal como se transcribieron: no se imputa ni se completa nada (salvo las 9 celdas de Florencio Varela 1962
que ya imputa canton5865). Las celdas marcadas «*» (sin dato) y «**» (incluida en otra unidad) se omiten.
tipo_fila «candidato»: votos por candidato (lista incompleta de 1912/1914); no se suman entre si para dar votos por partido.
"""
import os, re, sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "../resultados_xlsx")
POR = os.path.join(OUT, "por_eleccion")
COLS = ["anio", "cargo", "nivel", "provincia", "unidad", "tipo_fila", "codigo_partido", "partido", "bloque", "votos", "fuente_id", "fuente"]
CANTON = "Cantón (1968), Materiales para el estudio de la sociología política en la Argentina, t. II"
SEXO = {"varones y mujeres": "principal", "varones solamente": "varones", "mujeres solamente": "mujeres"}


def tipo_de(n):
    s = n.lower().strip()
    if s in ("inscriptos",): return "electores"
    if s in ("votantes",): return "votantes"
    if "anulad" in s and "blanco" in s: return "blancos_y_nulos"
    if s.startswith("en blanco") or s in ("blanco", "blancos", "votos en blanco"): return "blancos"
    if "anulad" in s or "observad" in s or s in ("nulos",): return "nulos"
    return "agrupacion"


def frame(rows, **meta):
    df = pd.DataFrame(rows)
    for k, v in meta.items():
        if k not in df: df[k] = v
    for k in COLS:
        if k not in df: df[k] = ""
    return df[COLS]


# ---------------------------------------------------------------- 1912 y 1914 (busquedas propias: Cantón, expedientes HCDN, prensa)
# provincias donde la fuente da votos por candidato y no por partido
CAND14 = {"Corrientes", "Córdoba", "La Rioja", "Mendoza"}


def busqueda(path, anio, fid, cand_prov=(), nivel_col=None):
    d = pd.read_csv(os.path.join(ROOT, path), dtype=str, encoding="utf-8-sig").fillna("")
    rows = []
    for r in d.itertuples(index=False):
        n = r.partido_o_lista
        t = tipo_de(n)
        if t == "agrupacion" and (n.startswith("Candidato") or r.provincia in cand_prov): t = "candidato"
        v = float(r.votos) if r.votos.strip() else np.nan       # vacio = ilegible o sin cifra en la fuente (ver nota)
        nota = "; ".join(x for x in (r.fila_fuente, r.nota) if x)
        rows.append(dict(provincia=r.provincia, unidad=r.departamento, tipo_fila=t, partido=re.sub(r"^Candidato:\s*", "", n) if t == "candidato" else n,
                         votos=v, nivel=getattr(r, nivel_col) if nivel_col else "departamento",
                         fuente="%s [%s] %s" % (path, r.fuente_id, nota)))
    return frame(rows, anio=anio, cargo="diputados", fuente_id=fid)


# ---------------------------------------------------------------- Cantón 1937, 1940, 1946 y 1954 (formato largo celda a celda)
CARGOS = {"Electores de Presidente y Vice": "presidente", "Diputados nacionales": "diputados", "Diputados": "diputados",
          "Vicepresidente": "vicepresidente", "Delegados": "delegados"}


def canton_largo(path, anios):
    d = pd.read_csv(os.path.join(ROOT, path), dtype=str, encoding="utf-8-sig").fillna("")
    d = d[d.anio.astype(int).isin(anios) & (d.valor != "")]      # sin las celdas «*» y «**»
    solo_varones = d.groupby("anio").categoria.agg(lambda s: set(s) == {"varones solamente"})
    out = []
    for (anio, el, cat), g in d.groupby(["anio", "eleccion", "categoria"], sort=False):
        fid = "principal" if solo_varones[anio] else SEXO[cat]
        rows = [dict(provincia=r.provincia, unidad=r.unidad, tipo_fila=tipo_de(r.concepto), partido="" if tipo_de(r.concepto) != "agrupacion" else r.concepto,
                     votos=float(r.valor), fuente="%s, %s; %s, pág. %s (PDF %s)%s" % (CANTON, cat, path, r.pagina_libro, r.pagina_pdf,
                     "" if fid != "varones" or solo_varones[anio] else "; San Luis y Tucumán solo tienen la tabla de varones"))
                for r in g.itertuples(index=False)]
        out.append(frame(rows, anio=int(anio), cargo=CARGOS[el], nivel="departamento", fuente_id=fid))
    return out


# ---------------------------------------------------------------- Cantón 1958, 1962, 1965 (canton5865, con correcciones)
def canton5865():
    sys.path.insert(0, os.path.join(ROOT, "../transcripciones/canton5865"))
    from datos import cargar_todo, unidades
    from sospechas import kinds
    T, _ = cargar_todo()
    blo = {}
    for a in (1958, 1962, 1965):
        for (p, u), d in unidades(T, a).items():
            for n, v, b in d["parties"]: blo[(a, p, n)] = b or ""
    out = []
    for (a, c, p, cat), t in sorted(T.items()):
        ins, vot, rest = kinds(t["cols"])
        fid = {"T": "principal", "V": "varones", "M": "mujeres"}[cat]
        cargo = {"P": "presidente", "D": "diputados"}[c]
        rows = []
        for u, r in t["rows"].items():
            imp = u in t.get("imput", ())
            src = "%s; canton5865 (correcciones.py aplicadas), PDF %s%s" % (CANTON, ", ".join(str(x) for x in t["pages"]), "; celdas imputadas" if imp else "")
            for k, tf in ((ins, "electores"), (vot, "votantes")):
                if k is not None and isinstance(r.get(k), int): rows.append(dict(provincia=p, unidad=u, tipo_fila=tf, votos=float(r[k]), fuente=src))
            for k in rest:
                v = r.get(k); n = t["cols"][k]
                if not isinstance(v, int): continue
                tf = tipo_de(n)
                rows.append(dict(provincia=p, unidad=u, tipo_fila=tf, partido=n if tf == "agrupacion" else "",
                                 bloque=blo.get((a, p, n), "") if tf == "agrupacion" else "", votos=float(v), fuente=src))
        if rows: out.append(frame(rows, anio=a, cargo=cargo, nivel="departamento", fuente_id=fid))
    return out


def frames():
    F = [busqueda("../transcripciones/busqueda1912/datos_1912_depto.csv", 1912, "principal"),
         busqueda("../transcripciones/busqueda1914/datos_1914_depto.csv", 1914, "principal", cand_prov=CAND14),
         busqueda("../transcripciones/busqueda1914/datos_1914_parciales.csv", 1914, "parciales", cand_prov={"Santa Fe", "Jujuy", "Tucumán"}, nivel_col="nivel")]
    F += canton_largo("../transcripciones/canton1937_1940/canton_1937_1940_1946.csv", (1937, 1940))
    F += canton_largo("../transcripciones/canton1946/canton_1946.csv", (1946,))
    F += canton_largo("../transcripciones/canton1954/canton_1954.csv", (1954,))
    F += canton5865()
    return F


# ---------------------------------------------------------------- por eleccion (ancho) e indice, como exportar_xlsx.py
META = ["positivos", "blancos", "nulos", "blancos_y_nulos", "total", "votantes", "electores"]


def por_eleccion(df):
    anio, cargo, fid = int(df.anio.iloc[0]), df.cargo.iloc[0], df.fuente_id.iloc[0]
    ag = df[df.tipo_fila.isin(["agrupacion", "candidato"])].copy()
    ag["col"] = np.where(ag.codigo_partido != "", ag.codigo_partido, ag.partido)
    P = ag.pivot_table(index=["provincia", "unidad"], columns="col", values="votos", aggfunc="sum")
    P = P[P.sum().sort_values(ascending=False).index]
    me = df[~df.tipo_fila.isin(["agrupacion", "candidato"])].pivot_table(index=["provincia", "unidad"], columns="tipo_fila", values="votos", aggfunc="sum")
    me = me[[c for c in META if c in me.columns]]
    W = me.join(P, how="outer").reset_index()
    part = ag.groupby(["provincia", "tipo_fila", "partido"], dropna=False).votos.sum().reset_index().sort_values(["provincia", "votos"], ascending=[True, False])
    fn = "%d_%s.xlsx" % (anio, cargo) if fid == "principal" else "%d_%s__%s.xlsx" % (anio, cargo, fid)
    with pd.ExcelWriter(os.path.join(POR, fn), engine="openpyxl") as xw:
        W.to_excel(xw, sheet_name="resultados", index=False)
        part.to_excel(xw, sheet_name="partidos", index=False)
        bl = ag[ag.bloque != ""]
        if len(bl) and bl.bloque.nunique() > 1:
            B = bl.pivot_table(index=["provincia", "unidad"], columns="bloque", values="votos", aggfunc="sum")
            B[B.sum().sort_values(ascending=False).index].reset_index().to_excel(xw, sheet_name="bloques", index=False)
        pd.DataFrame({"nota": ["Una fila por unidad; columnas: totales de la unidad y votos por partido (o por candidato, donde la fuente los da asi).",
                               "Fuente: " + df.fuente.iloc[0].split(";")[0],
                               "Transcripcion propia; ver el LEEME de la carpeta de origen. Cifras como estan impresas: no se imputa ni se completa.",
                               "Las columnas de candidatos (1912/1914) no se suman entre si: con lista incompleta cada votante elegia mas de un candidato."]}).to_excel(xw, sheet_name="LEEME", index=False)
    return dict(anio=anio, cargo=cargo, fuente_id=fid, nivel=df.nivel.iloc[0], unidades=len(W), partidos=ag.partido.nunique(),
                filas_largo=len(df), archivo="por_eleccion/" + fn, fuente=df.fuente.iloc[0].split(";")[0])


if __name__ == "__main__":
    from openpyxl import Workbook, load_workbook
    NEW = pd.concat(frames(), ignore_index=True)
    keys = set(map(tuple, NEW[["anio", "cargo", "fuente_id"]].drop_duplicates().itertuples(index=False)))
    src = os.path.join(OUT, "MASTER_resultados.xlsx")
    wb0 = load_workbook(src, read_only=True)
    sheets = {ws.title: [list(r) for r in ws.iter_rows(values_only=True)] for ws in wb0.worksheets}
    wb0.close()
    head, body = sheets["largo"][0], sheets["largo"][1:]
    assert head == COLS, head
    body = [r for r in body if (r[0], r[1], r[10]) not in keys]          # vuelve a correr sin duplicar
    INDEX = [dict(zip(sheets["elecciones"][0], r)) for r in sheets["elecciones"][1:]]
    INDEX = [r for r in INDEX if (r["anio"], r["cargo"], r["fuente_id"]) not in keys]
    for k, df in NEW.groupby(["anio", "cargo", "fuente_id"], sort=True):
        INDEX.append(por_eleccion(df)); print(k, len(df))
    INDEX.sort(key=lambda r: (int(r["anio"]), r["cargo"], r["fuente_id"] != "principal", r["fuente_id"]))
    new_rows = [[None if (isinstance(x, float) and np.isnan(x)) else (int(x) if isinstance(x, np.integer) else x) for x in r] for r in NEW[COLS].itertuples(index=False)]
    allrows = sorted(body + new_rows, key=lambda r: int(r[0]))         # orden estable por año
    wb = Workbook(write_only=True)
    ws = wb.create_sheet("largo"); ws.append(COLS)
    for r in allrows: ws.append(r)
    idx = pd.DataFrame(INDEX)
    ws = wb.create_sheet("elecciones"); ws.append(list(idx.columns))
    for r in idx.itertuples(index=False): ws.append(list(r))
    for name in ("AMBA2025_circuitos",):
        if name in sheets:
            ws = wb.create_sheet(name)
            for r in sheets[name]: ws.append(r)
    ws = wb.create_sheet("LEEME")
    for (line,) in [(r[0],) for r in sheets["LEEME"]]:
        if line and line.startswith("No incluidos:"):
            line = "No incluidos: atlas ficticio de 1916, el CSV de Gemini 1912-1973, la base de Lupu-Stokes, PASO legislativas y cargos provinciales distintos de gobernador."
        ws.append([line])
    ws.append(["Transcripciones propias (transcripciones_xlsx.py): 1912 y 1914 diputados (Cantón, expedientes HCDN y prensa; 1914 «parciales» aparte), "
               "1937 y 1946 presidente, 1940 diputados, 1954 diputados/vicepresidente/delegados y 1958-1965 de Cantón (t. II). fuente_id «varones»/«mujeres»: tablas por sexo de 1954 y 1958; "
               "tipo_fila «candidato»: votos por candidato (no sumar), «blancos_y_nulos»: columna conjunta de 1954."])
    wb.save(src)
    idx.to_csv(os.path.join(OUT, "indice_elecciones.csv"), index=False, encoding="utf-8-sig")
    print("listo:", len(allrows), "filas en largo;", len(idx), "archivos por eleccion")
