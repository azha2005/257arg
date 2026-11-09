"""Atlas 1868-1886 y Capital 1864-2007 (CD de Cantón y Jorrat) -> resultados_xlsx.

    python comun/historicos_xlsx.py   -> agrega (o reemplaza) estas elecciones en MASTER_resultados.xlsx,
                                         escribe sus archivos en por_eleccion/ y rehace indice_elecciones.csv

Como comun/transcripciones_xlsx.py: no vuelve a correr exportar_xlsx.py.

1868, 1874, 1880 y 1886 (presidente): se leen de dataset_<año>.json de cada atlas, con las cifras que muestra el mapa.
  - Las unidades con la misma cifra y la misma nota se juntan en una fila (p. ej. Capital 1868: total de la ciudad,
    no por parroquia; nombre «A + B + ...»).
  - Las provincias que el atlas pinta en color sólido llevan el número de ELECTORES del colegio que ganó cada fórmula
    (tipo_fila «electores_colegio», nivel «provincia»): no son votos y no se suman con ellos.
  - 1886 trae dos versiones de Capital: la de los Partidos Unidos (principal) y la de la policía (fuente_id «policia»).

Capital 1864-2007: datos/canton_ciudad/cd_largo.csv (salida de leer_cd.py, 106 planillas del CD de
*Elecciones en la ciudad*, t. III). Una elección por planilla, fuente_id «capital_canton_<n>» (n = número de la
planilla en el CD). El total suma varones + mujeres cuando la planilla viene por sexo; las tablas por sexo van en
hojas aparte del archivo por elección. Unidades marcadas ** en el CD se conservan tal cual.
"""
import csv, json, os, re, sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from transcripciones_xlsx import COLS, OUT, POR, frame  # noqa: E402

ATLAS = [(1868, "mapa1868"), (1874, "mapa1874"), (1880, "mapa1880"), (1886, "mapa1886")]
METRIC = {"Inscriptos": "electores", "Votantes": "votantes"}


def num(s):
    s = str(s).replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except ValueError:
        return None


def atlas_frames():
    F = []
    for anio, carpeta in ATLAS:
        d = json.load(open(os.path.join(ROOT, "..", "mapas", carpeta, "dataset_%d.json" % anio), encoding="utf8"))
        cand, T, solid = d["candidates"], d["territories"], set(d.get("solid") or [])
        modos = [(m, "principal") for m in d["modes"][:1]]
        if anio == 1886:
            modos += [(m, "policia") for m in d["modes"] if m.get("id") == "pol"]
        for modo, fid in modos:
            grupos = {}
            for i, u in enumerate(modo["units"]):
                if not u or not u.get("lines"):
                    continue
                if fid == "policia" and T[i]["p"] != "Capital":
                    continue
                k = (T[i]["p"], json.dumps(u["lines"]), u.get("note", ""), json.dumps(u.get("metrics") or []))
                grupos.setdefault(k, []).append(T[i]["n"])
            rows = []
            for (prov, lines, nota, mets), nombres in grupos.items():
                colegio = prov in solid
                unidad = prov if colegio else " + ".join(nombres)
                nivel = "provincia (electores del colegio)" if colegio else ("departamento/parroquia" if len(nombres) == 1 else "conjunto de unidades")
                src = "Atlas %d (mapas/%s/dataset_%d.json; ver LEEME_%d.md). %s" % (anio, carpeta, anio, anio, nota)
                for code, v, _pct in json.loads(lines):
                    rows.append(dict(provincia=prov, unidad=unidad, tipo_fila="electores_colegio" if colegio else "agrupacion",
                                     codigo_partido=code, partido=cand.get(code, {}).get("n", code), votos=v, nivel=nivel, fuente=src))
                for lab, val in json.loads(mets):
                    if lab in METRIC and num(val) is not None:
                        rows.append(dict(provincia=prov, unidad=unidad, tipo_fila=METRIC[lab], votos=num(val), nivel=nivel, fuente=src))
            F.append(frame(rows, anio=anio, cargo="presidente", fuente_id=fid))
    return F


# ---------------------------------------------------------------- Capital, CD de Cantón y Jorrat
CD = os.path.join(ROOT, "..", "datos", "canton_ciudad")
CANTON_CD = "Cantón y Jorrat, Elecciones en la ciudad, t. III (2007), CD"


def cargo_cd(tipo, titulo):
    t = re.sub(r"V$", "", re.sub(r"(AS|2S)$", "", tipo.strip()))
    if re.search(r"PROV\.", titulo.upper()) or t == "GOB":
        return "legislatura_bonaerense"
    return {"DI": "diputados", "PR": "presidente", "PRDI": "presidente_y_diputados", "SE": "senadores",
            "CC": "constituyentes", "LEG": "legisladores", "JG": "jefe_de_gobierno", "JG1": "jefe_de_gobierno_1v",
            "JG2": "jefe_de_gobierno_2v"}[t]


def tipo_cd(col):
    s = col.upper().strip()
    if s.startswith("INSCRIP"): return "electores"
    if s.startswith("VOTANTE"): return "votantes"
    if s in ("BLANCOS", "BLANCO", "EN BLANCO", "VOTOS EN BLANCO"): return "blancos"
    if s.startswith("NULOS") or s.startswith("ANULADO"): return "nulos"
    return "agrupacion"


def capital_frames():
    meta, cols = {}, {}
    for x in json.load(open(os.path.join(CD, "cd_elecciones.json"), encoding="utf8")):
        titulo = " / ".join(s for s in x["titulo"] if isinstance(s, str))
        meta.setdefault(int(x["n"]), (x["tipo"], titulo, "; ".join(x.get("notas") or [])))
        cols[(int(x["n"]), x.get("sexo"))] = x["columnas"]
    # la tabla de mujeres a veces nombra distinto a los partidos («PJ» por «JUSTICIALISTA»): se toma el nombre
    # de la de varones en la misma posición; si las tablas no tienen las mismas columnas, se empareja por nombre.
    renombre = {}
    for (n, s), c in cols.items():
        if s == "M" and (n, "V") in cols and len(cols[(n, "V")]) == len(c):
            renombre[n] = dict(zip(c, cols[(n, "V")]))
    rows = []
    for r in csv.DictReader(open(os.path.join(CD, "cd_largo.csv"), encoding="utf-8-sig")):
        n = int(r["n"]); tipo, titulo, notas = meta[n]
        unidad = r["unidad"].strip() or ("Circunscripción %s" % r["unidad_num"])
        v = num(r["valor"]) if r["valor"].strip() else np.nan
        col = r["columna"]
        if r["sexo"] == "M": col = renombre.get(n, {}).get(col, col)
        rows.append(dict(n=n, anio=int(r["anio"]), cargo=cargo_cd(tipo, titulo), sexo=r["sexo"], provincia="Capital Federal",
                         unidad=unidad, tipo_fila=tipo_cd(col), partido=col.strip(), votos=v,
                         nivel="parroquia" if int(r["anio"]) < 1904 else "circunscripción",
                         fuente="%s, planilla (%d) %s: %s%s" % (CANTON_CD, n, r["archivo"], titulo, (". " + notas) if notas else "")))
    D = pd.DataFrame(rows)
    F, SEXO = [], {}
    for n, g in D.groupby("n", sort=True):
        fid = "capital_canton_%03d" % n
        keys = ["anio", "cargo", "provincia", "unidad", "tipo_fila", "partido", "nivel"]
        tot = g.groupby(keys, sort=False, dropna=False).votos.sum(min_count=1).reset_index()
        tot["fuente"] = g.fuente.iloc[0]
        F.append(frame(tot.to_dict("records"), fuente_id=fid))
        if set(g.sexo) >= {"V", "M"}:
            SEXO[fid] = {s: g[g.sexo == s] for s in ("V", "M")}
    return F, SEXO


# ---------------------------------------------------------------- por elección (ancho)
META = ["positivos", "blancos", "nulos", "total", "votantes", "electores"]


def ancho(df):
    ag = df[df.tipo_fila.isin(["agrupacion", "electores_colegio"])].copy()
    ag["col"] = np.where(ag.codigo_partido != "", ag.partido + " (" + ag.codigo_partido + ")", ag.partido)
    orden = list(dict.fromkeys(df.unidad))
    P = ag.pivot_table(index=["provincia", "unidad"], columns="col", values="votos", aggfunc="sum", sort=False)
    P = P[P.sum().sort_values(ascending=False).index]
    me = df[~df.tipo_fila.isin(["agrupacion", "electores_colegio"])]
    if len(me):
        me = me.pivot_table(index=["provincia", "unidad"], columns="tipo_fila", values="votos", aggfunc="sum", sort=False)
        P = me[[c for c in META if c in me.columns]].join(P, how="outer")
    W = P.reset_index()
    W["_o"] = W.unidad.map({u: i for i, u in enumerate(orden)})
    return W.sort_values(["_o"]).drop(columns="_o"), ag


def por_eleccion(df, sexo=None):
    anio, cargo, fid = int(df.anio.iloc[0]), df.cargo.iloc[0], df.fuente_id.iloc[0]
    W, ag = ancho(df)
    fn = "%d_%s.xlsx" % (anio, cargo) if fid == "principal" else "%d_%s__%s.xlsx" % (anio, cargo, fid)
    capital = fid.startswith("capital_canton")
    notas = ["Una fila por unidad; columnas: totales de la unidad y votos por partido o fórmula.",
             "Fuente: " + df.fuente.iloc[0]]
    if capital:
        notas += ["Planilla del CD copiada tal cual (datos/canton_ciudad/leer_cd.py): no se corrige ni se imputa. "
                  "Si la planilla viene por sexo, «resultados» suma varones y mujeres y las hojas «varones» y «mujeres» traen cada tabla.",
                  "Antes de 1904 las unidades son parroquias; después, circunscripciones. Ver mapas/capital_canton/LEEME.md."]
    else:
        notas += ["Cifras del atlas (mapas/mapa%d/): prensa y actas de época, ver su LEEME. Unidades con la misma cifra juntas en una fila." % anio,
                  "Las filas de nivel «provincia (electores del colegio)» son electores ganados por cada fórmula, no votos: no se suman con los votos."]
    with pd.ExcelWriter(os.path.join(POR, fn), engine="openpyxl") as xw:
        W.to_excel(xw, sheet_name="resultados", index=False)
        for s, nombre in (("V", "varones"), ("M", "mujeres")):
            if sexo and s in sexo:
                g = sexo[s].copy(); g["fuente_id"] = fid; g["codigo_partido"] = ""
                ancho(g)[0].to_excel(xw, sheet_name=nombre, index=False)
        pd.DataFrame({"nota": notas}).to_excel(xw, sheet_name="LEEME", index=False)
    return dict(anio=anio, cargo=cargo, fuente_id=fid, nivel=df.nivel.iloc[0], unidades=len(W), partidos=ag.partido.nunique(),
                filas_largo=len(df), archivo="por_eleccion/" + fn, fuente=df.fuente.iloc[0][:300])


LEEME_LINEA = ("Históricas (historicos_xlsx.py): presidenciales 1868, 1874, 1880 y 1886 de los atlas (prensa y actas; tipo_fila «electores_colegio» "
               "= electores por provincia donde no hay votos, no sumar con votos; 1886 «policia» = versión policial de Capital) y Capital 1864-2007 "
               "por parroquia o circunscripción del CD de Cantón y Jorrat (fuente_id «capital_canton_<planilla>», varones + mujeres).")


if __name__ == "__main__":
    from openpyxl import Workbook, load_workbook
    F, SEXO = capital_frames()
    F = atlas_frames() + F
    NEW = pd.concat(F, ignore_index=True)
    keys = set(map(tuple, NEW[["anio", "cargo", "fuente_id"]].drop_duplicates().itertuples(index=False)))
    src = os.path.join(OUT, "MASTER_resultados.xlsx")
    wb0 = load_workbook(src, read_only=True)
    sheets = {ws.title: [list(r) for r in ws.iter_rows(values_only=True)] for ws in wb0.worksheets}
    wb0.close()
    head, body = sheets["largo"][0], sheets["largo"][1:]
    assert head == COLS, head
    viejo = lambda a, c, f: (a, c, f) in keys or str(f).startswith("capital_canton_")     # vuelve a correr sin duplicar
    body = [r for r in body if not viejo(r[0], r[1], r[10])]
    INDEX = [dict(zip(sheets["elecciones"][0], r)) for r in sheets["elecciones"][1:]]
    INDEX = [r for r in INDEX if not viejo(r["anio"], r["cargo"], r["fuente_id"])]
    for f in os.listdir(POR):
        if "__capital_canton_" in f: os.remove(os.path.join(POR, f))
    for k, df in NEW.groupby(["anio", "cargo", "fuente_id"], sort=True):
        INDEX.append(por_eleccion(df, SEXO.get(k[2])))
    INDEX.sort(key=lambda r: (int(r["anio"]), r["cargo"], r["fuente_id"] != "principal", r["fuente_id"]))
    new_rows = [[None if (isinstance(x, float) and np.isnan(x)) else (int(x) if isinstance(x, np.integer) else x) for x in r]
                for r in NEW[COLS].itertuples(index=False)]
    allrows = sorted(body + new_rows, key=lambda r: int(r[0]))
    wb = Workbook(write_only=True)
    ws = wb.create_sheet("largo"); ws.append(COLS)
    for r in allrows: ws.append(r)
    idx = pd.DataFrame(INDEX)
    ws = wb.create_sheet("elecciones"); ws.append(list(idx.columns))
    for r in idx.itertuples(index=False): ws.append([None if (isinstance(x, float) and np.isnan(x)) else x for x in r])
    for name in sheets:
        if name not in ("largo", "elecciones", "LEEME"):
            ws = wb.create_sheet(name)
            for r in sheets[name]: ws.append(r)
    ws = wb.create_sheet("LEEME")
    for (line,) in [(r[0],) for r in sheets["LEEME"]]:
        if line and not line.startswith("Históricas (historicos_xlsx.py)"):
            ws.append([line])
    ws.append([LEEME_LINEA])
    wb.save(src)
    idx.to_csv(os.path.join(OUT, "indice_elecciones.csv"), index=False, encoding="utf-8-sig")
    print("listo:", len(allrows), "filas en largo;", len(idx), "archivos por eleccion;", len(keys), "nuevos o reemplazados")
