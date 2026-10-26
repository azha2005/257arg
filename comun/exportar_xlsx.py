"""Exporta todos los resultados por departamento (y circuito en el AMBA 2025) que hay en el proyecto a xlsx.

    python comun/exportar_xlsx.py      -> resultados_xlsx/MASTER_resultados.xlsx  + resultados_xlsx/por_eleccion/<anio>_<cargo>.xlsx

Fuentes (formato largo unificado: anio, cargo, nivel, provincia, unidad, tipo_fila, codigo_partido, partido, votos, fuente):
  - 1916, 1922, 1928, 1930: datasets de los atlas (Canton, 1968, deptos. de 1914; ver LEEME de cada atlas)
  - 1983-1999: base de Ernesto Calvo (base8399/ernesto/*/dpto_partidos.csv), sin corregir; incluye 1994 constituyentes
  - 2025: escrutinio provisorio por mesa de la DINE (datos_oficiales/2025), agregado por seccion; AMBA por circuito
  - 1912, 1914, 1937, 1940, 1946, 1954, 1958, 1962, 1965: transcripciones propias (transcripciones_xlsx.py)
No se incluyen las planillas locales del usuario (2003-2023) ni el atlas ficticio de 1916.
"""
import os, re, sys, json, glob, collections
import numpy as np
import pandas as pd
from openpyxl import Workbook

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "../resultados_xlsx")
POR = os.path.join(OUT, "por_eleccion")
os.makedirs(POR, exist_ok=True)
COLS = ["anio", "cargo", "nivel", "provincia", "unidad", "tipo_fila", "codigo_partido", "partido", "bloque", "votos", "fuente_id", "fuente"]
FRAMES = []
sys.path.insert(0, os.path.join(ROOT, "../datos/wikileg"))
try:
    from bloques_leg import match as match_bloques
except Exception as e:
    match_bloques = None; print("sin bloques de Wikipedia:", e)


def add(df, meta):
    for k, v in meta.items(): df[k] = v
    if "bloque" not in df: df["bloque"] = ""
    if "fuente_id" not in df: df["fuente_id"] = "principal"
    FRAMES.append(df[COLS])


def norm(s):
    import unicodedata
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()).strip()


# ---------------------------------------------------------------- 1. antes de 1983: datasets de los atlas
PRE = [("../mapas/mapa1916dip/dataset_1916.json", 1916, "diputados"), ("../mapas/mapa1922/dataset_1922.json", 1922, "presidente"),
       ("../mapas/mapa1928/dataset_1928.json", 1928, "presidente"), ("../mapas/mapa1930/dataset_1930.json", 1930, "diputados")]


def num(s):
    s = str(s).replace(".", "").replace(",", ".").replace("%", "").strip()
    try: return float(s)
    except ValueError: return None


for path, anio, cargo in PRE:
    d = json.load(open(os.path.join(ROOT, path), encoding="utf8"))
    cand = d["candidates"]; T = d["territories"]; M = d["modes"][0]["units"]
    src = "Cantón (1968), deptos. de 1914; vía %s (cifras de los atlas, ver su LEEME)" % path
    rows = []
    for i, u in enumerate(M):
        if not u or not u.get("lines"): continue
        t = T[i]
        for code, v, pct in u["lines"]:
            c = code[2:] if code.startswith("P_") else code
            tipo = "blancos" if c == "BLA" else "nulos" if c == "NUL" else "agrupacion"
            rows.append((t["p"], t["n"], tipo, c, cand.get(code, {}).get("n", ""), v))
        for lab, val in u.get("metrics", []):
            key = {"Inscriptos": "electores", "Votantes": "votantes"}.get(lab)
            if key and num(val) is not None: rows.append((t["p"], t["n"], key, "", "", num(val)))
    df = pd.DataFrame(rows, columns=["provincia", "unidad", "tipo_fila", "codigo_partido", "partido", "votos"])
    add(df, dict(anio=anio, cargo=cargo, nivel="departamento", fuente=src))

# ---------------------------------------------------------------- 2. 1983-1999: Ernesto Calvo
ERN = os.path.join(ROOT, "../datos/base8399", "ernesto")
# descripcion de los codigos: codigos_AAAA.csv (hojas de leyendas, formato irregular: se interpreta lo que tiene la forma "SIGLA: descripcion" bajo una provincia)
LEY = {}
for f in glob.glob(os.path.join(ERN, "codigos_*.csv")):
    anio = int(re.search(r"codigos_(\d+)", f).group(1)); prov = ""
    for r in pd.read_csv(f, dtype=str, encoding="utf-8-sig").fillna("").itertuples():
        c1 = str(r.c1).strip()
        m = re.match(r"^(?:\d+\s*-\s*)?([A-Za-z0-9ÁÉÍÓÚÑáéíóúñ.\-/]{1,14})\s*:\s*(.*)$", c1)
        if m and prov:
            LEY[(anio, norm(prov), norm(m.group(1)).replace(" ", ""))] = m.group(2).strip()
        elif c1 and ":" not in c1 and len(c1) > 3 and c1.upper() == c1 or (c1.endswith(":") and " " not in c1[:-1].strip()[:3]):
            prov = c1.rstrip(":")
        elif c1 and c1.endswith(":"):
            prov = c1.rstrip(":")
# nombres de los atlas (mas completos para 1983-1994): dataset de cada atlas
ATL = {}
for anio, p in ((1983, "../mapas/mapa1983/dataset_1983.json"), (1985, "../mapas/mapa1985/dataset_1985.json"), (1987, "../mapas/mapa1987/dataset_1987.json"), (1989, "../mapas/mapa1989/dataset_1989.json"),
                (1991, "../mapas/mapa1991/dataset_1991.json"), (1993, "../mapas/mapa1993/dataset_1993.json"), (1994, "../mapas/mapa1994/dataset_1994.json")):
    cd = json.load(open(os.path.join(ROOT, p), encoding="utf8"))["candidates"]
    for k, v in cd.items():
        if k.startswith("P_") and v.get("n"): ATL[(anio, k[2:].lower())] = v["n"]

import ast


def code2bloc_of(anio):
    """CODE2BLOC de los builds de cada atlas (o de mapeo_<anio>.py) y la etiqueta de cada bloque (dataset)."""
    folder = os.path.join(ROOT, "../mapas/mapa%d" % anio)
    mp = os.path.join(folder, "mapeo_%d.py" % anio)
    if os.path.exists(mp):
        ns = {}; exec(open(mp, encoding="utf8").read(), ns); c2b = ns["CODE2BLOC"]
    else:
        src = open(os.path.join(folder, "build_%d.py" % anio), encoding="utf8").read()
        i = src.index("CODE2BLOC = {") + len("CODE2BLOC = "); depth = 0
        for j in range(i, len(src)):
            depth += src[j] == "{"; depth -= src[j] == "}"
            if depth == 0: break
        c2b = ast.literal_eval(src[i:j + 1])
    cd = json.load(open(os.path.join(folder, "dataset_%d.json" % anio), encoding="utf8"))["candidates"]
    FB = dict(AF="Alianza Federal", MID="Movimiento de Integración y Desarrollo", PI="Partido Intransigente", FDP="Frente del Pueblo", APL="Acción Popular para la Liberación",
              DC="Democracia Cristiana", IU="Izquierda Unida", MOD="MODIN", NC="Partido Nacionalista Constitucional", PD="Partido Demócrata", PDP="Partido Demócrata Progresista",
              PO="Partido Obrero", PTP="Partido del Trabajo y del Pueblo", US="Unidad Socialista", BJU="Partido Blanco de los Jubilados", BLO="Partido Bloquista", CR="Cruzada Renovadora",
              FG="Frente Grande", MAS="Movimiento al Socialismo", MCI="Movimiento Cristiano Independiente", MPF="Movimiento Popular Fueguino", MPJ="Movimiento Popular Jujeño",
              PF="Partido Federal", PH="Partido Humanista", UCD="Unión del Centro Democrático")
    lab = {b: ((cd[b]["n"] + (" (%s)" % cd[b]["sub"] if cd[b].get("sub") else "")) if b in cd else FB.get(b, b)) for b in set(c2b.values())}
    return {c.lower(): lab.get(b, b) for c, b in c2b.items()}


ATLAS_CARGO = {1983: "presidente", 1985: "diputados", 1987: "diputados", 1989: "presidente", 1991: "diputados", 1993: "diputados", 1994: "constituyentes"}
for f in sorted(glob.glob(os.path.join(ERN, "*", "dpto_partidos.csv"))):
    folder = os.path.basename(os.path.dirname(f)); anio = int(folder[:4]); cargo = folder[5:]
    df = pd.read_csv(f, encoding="utf-8")
    out = pd.DataFrame(dict(provincia=df.provincia, unidad=df.departamento, tipo_fila=df.tipo_fila, codigo_partido=df.codigo_partido.where(df.tipo_fila == "agrupacion", ""), votos=df.votos))
    names = []
    for prov, cod, tipo in zip(df.provincia, df.codigo_partido.astype(str), df.tipo_fila):
        if tipo != "agrupacion": names.append(""); continue
        names.append(LEY.get((anio, norm(prov), norm(cod).replace(" ", ""))) or ATL.get((anio, cod.lower()), ""))
    out["partido"] = names
    if ATLAS_CARGO.get(anio) == cargo:
        c2b = code2bloc_of(anio)
        out["bloque"] = np.where(out.tipo_fila == "agrupacion", out.codigo_partido.astype(str).str.lower().map(c2b).fillna("Otros (sin agrupar)"), "")
    add(out, dict(anio=anio, cargo=cargo, nivel="departamento", fuente="Ernesto Calvo, %s (sin corregir; ver base8399/ernesto/LEEME.md)" % os.path.basename(df.archivo.iloc[0])))

# ---------------------------------------------------------------- 3. 2025: provisorio por mesa de la DINE
CSV25 = os.path.join(ROOT, "../datos_oficiales", "2025", "x", "resultados2025.csv")
AGG25 = os.path.join(ROOT, "../datos_oficiales", "2025", "agregado_secciones.pkl")
if os.path.exists(AGG25):
    votes, mesas = pd.read_pickle(AGG25)
else:
    cols = ["distrito_id", "distrito_nombre", "seccion_id", "seccion_nombre", "seccionprovincial_nombre", "circuito_id", "mesa_id", "cargo_nombre", "mesa_electores",
            "estado_final", "agrupacion_nombre", "votos_tipo", "votos_cantidad"]
    vs, ms = [], []
    for ch in pd.read_csv(CSV25, usecols=cols, dtype=str, chunksize=2_000_000, encoding="utf-8"):
        ch = ch[ch.cargo_nombre.isin(["DIPUTADO NACIONAL", "SENADOR NACIONAL"])].copy()
        ch["v"] = pd.to_numeric(ch.votos_cantidad, errors="coerce").fillna(0)
        ch["agrupacion_nombre"] = ch.agrupacion_nombre.fillna("")
        ch["seccionprovincial_nombre"] = ch.seccionprovincial_nombre.fillna("")
        vs.append(ch.groupby(["distrito_id", "distrito_nombre", "seccion_id", "seccion_nombre", "seccionprovincial_nombre", "cargo_nombre", "agrupacion_nombre", "votos_tipo"]).v.sum())
        ms.append(ch[["distrito_id", "distrito_nombre", "seccion_id", "seccion_nombre", "seccionprovincial_nombre", "circuito_id", "mesa_id", "cargo_nombre", "mesa_electores", "estado_final"]].drop_duplicates())
    votes = pd.concat(vs).groupby(level=list(range(8))).sum().reset_index()
    mesas = pd.concat(ms).drop_duplicates(["distrito_id", "seccion_id", "circuito_id", "mesa_id", "cargo_nombre"])
    pd.to_pickle((votes, mesas), AGG25)
mesas = mesas.copy(); mesas["elec"] = pd.to_numeric(mesas.mesa_electores, errors="coerce").fillna(0); mesas["ok"] = mesas.estado_final == "ESCRUTADO"
for cargo_n, cargo in (("DIPUTADO NACIONAL", "diputados"), ("SENADOR NACIONAL", "senadores")):
    v = votes[votes.cargo_nombre == cargo_n]
    if v.empty: continue
    rows = []
    for r in v.itertuples():
        tipo = {"POSITIVO": "agrupacion", "EN BLANCO": "blancos", "NULO": "nulos", "IMPUGNADO": "impugnados", "RECURRIDO": "recurridos"}.get(r.votos_tipo)
        if not tipo: continue
        prov = r.distrito_nombre
        unidad = ("%s · %s" % (r.seccionprovincial_nombre.title(), r.seccion_nombre)) if r.seccionprovincial_nombre else r.seccion_nombre
        rows.append((prov, unidad, tipo, "", r.agrupacion_nombre if tipo == "agrupacion" else "", r.v))
    m = mesas[mesas.cargo_nombre == cargo_n]
    g = m.groupby(["distrito_nombre", "seccion_id", "seccion_nombre", "seccionprovincial_nombre"]).agg(mesas=("elec", "size"), ok=("ok", "sum"), el=("elec", "sum")).reset_index()
    g["elok"] = m.assign(e=np.where(m.ok, m.elec, 0)).groupby(["distrito_nombre", "seccion_id", "seccion_nombre", "seccionprovincial_nombre"]).e.sum().values
    for r in g.itertuples():
        unidad = ("%s · %s" % (r.seccionprovincial_nombre.title(), r.seccion_nombre)) if r.seccionprovincial_nombre else r.seccion_nombre
        for tipo, val in (("electores", r.el), ("electores_mesas_escrutadas", r.elok), ("mesas", r.mesas), ("mesas_escrutadas", r.ok)):
            rows.append((r.distrito_nombre, unidad, tipo, "", "", val))
    df = pd.DataFrame(rows, columns=["provincia", "unidad", "tipo_fila", "codigo_partido", "partido", "votos"])
    if match_bloques is not None:
        _g, _D, _res, _u = match_bloques(2025, "DIPUTADOS" if cargo == "diputados" else "SENADORES")
        df["bloque"] = np.where(df.tipo_fila == "agrupacion", df.partido.str.strip().map(_res).fillna("Otros (sin agrupar)"), "")
        pd.DataFrame(dict(lista_dine=_D.index, votos=_D.values, bloque_wikipedia=[_res.get(n, "") for n in _D.index])).to_csv(os.path.join(OUT, "mapeo_bloques", "2025_%s.csv" % cargo), index=False, encoding="utf-8-sig")
    add(df, dict(anio=2025, cargo=cargo, nivel="seccion", fuente="DINE, escrutinio provisorio por mesa (datos.mininterior.gob.ar, elecciones_legislativas_2025.zip); no es el definitivo"))


# ---------------------------------------------------------------- 4. presidenciales 2003 y 2011-2023 (carpetas locales del usuario)
# EA: copia local de eleccionesargentina-main; EX03: planilla 2003 por seccion (no publicadas)
EA = os.environ.get("ATLAS_ELECCIONESARGENTINA", "eleccionesargentina-main")
EX03 = os.environ.get("ATLAS_EX03", "2003porseccion.xls")
B03 = dict(MENEM="Frente por la Lealtad (Menem)", FPV="Frente para la Victoria (Kirchner)", RECREAR="Movimiento Federal Recrear (López Murphy)",
           SAA="Frente Movimiento Nacional y Popular (Rodríguez Saá)", ARI="Alternativa por una República de Iguales (Carrió)", UCR="Unión Cívica Radical (Moreau)",
           IU="Izquierda Unida (Walsh)", PS="Partido Socialista", MID="MID", PDC="Partido Demócrata Cristiano", PO="Partido Obrero", PH="Partido Humanista",
           PSA="Partido Socialista Auténtico", MODIN="MODIN", PPR="Partido Popular de la Reconstrucción", QST="Quebracho/Sin determinar (columna QST de la fuente)")
if False and os.path.exists(EX03):   # reemplazado por PolAr_Data (trae Capital Federal); se deja por si se quiere comparar
    x = pd.read_excel(EX03)
    rows = []
    for r in x.itertuples(index=False):
        prov, _, un = str(r[0]).partition("_")
        for c in B03:
            v = getattr(r, c, None)
            if v is not None and not pd.isna(v): rows.append((prov.title(), un.title(), "agrupacion", c, B03[c], B03[c], float(v)))
    df = pd.DataFrame(rows, columns=["provincia", "unidad", "tipo_fila", "codigo_partido", "partido", "bloque", "votos"])
    add(df, dict(anio=2003, cargo="presidente", nivel="departamento",
                 fuente="Planilla del usuario 2003porseccion.xls (sin Capital Federal; el total queda ~15 % por debajo de Wikipedia; sin blancos ni nulos)"))

PRES = [("2011", "GENERALES 2011", "presidente"), ("2011", "PASO 2011", "presidente_paso"), ("2015", "GENERALES 2015", "presidente"), ("2015", "PASO 2015", "presidente_paso"),
        ("2015", "BALLOTAGE 2015", "presidente_balotaje"), ("2019", "GENERALES 2019", "presidente"), ("2019", "PASO 2019", "presidente_paso"),
        ("2023", "GENERALES 2023", "presidente"), ("2023", "PASO 2023", "presidente_paso"), ("2023", "BALLOTAGE 2023", "presidente_balotaje")]
for anio, carpeta, cargo in PRES:
    fs = glob.glob(os.path.join(EA, anio, carpeta, "NIVEL NACIONAL", "*_resultados_x_seccion.csv"))
    if not fs: print("falta", carpeta); continue
    d0 = pd.read_csv(fs[0], encoding="utf-8-sig")
    if str(d0.columns[0]).startswith("Unnamed") or d0.columns[0] == "": d0 = d0.drop(columns=d0.columns[0])
    d0 = d0.rename(columns={d0.columns[0]: "id"})
    rows = []
    for r in d0.to_dict("records"):
        prov, _, un = str(r["id"]).partition("_")
        for c, v in r.items():
            if not c.endswith("_votos") or pd.isna(v): continue
            nom = re.sub(r"\s+", " ", c[:-6]).strip()
            tipo = {"BLANCO": "blancos", "NULO": "nulos", "IMPUGNADO": "impugnados"}.get(nom, "agrupacion")
            rows.append((prov.title(), un.title(), tipo, nom if tipo == "agrupacion" else "", nom.title() if tipo == "agrupacion" else "", nom.title() if tipo == "agrupacion" else "", float(v)))
        for k, tipo in (("electores", "electores"), ("votantes", "votantes")):
            if k in r and not pd.isna(r[k]): rows.append((prov.title(), un.title(), tipo, "", "", "", float(r[k])))
    df = pd.DataFrame(rows, columns=["provincia", "unidad", "tipo_fila", "codigo_partido", "partido", "bloque", "votos"])
    add(df, dict(anio=int(anio), cargo=cargo, nivel="seccion", fuente="eleccionesargentina-main (%s) a partir del escrutinio provisorio; agrupación = frente, como en la tabla de Wikipedia" % carpeta))

# ---------------------------------------------------------------- 5. DINE 2011-2023: diputados y senadores nacionales por seccion, con los bloques de Wikipedia
MAPEO = os.path.join(OUT, "mapeo_bloques"); os.makedirs(MAPEO, exist_ok=True)


def tipo_of(s):
    s = str(s).upper()
    return "agrupacion" if s.startswith("POSIT") else "blancos" if "BLANCO" in s else "nulos" if "NULO" in s else "impugnados" if "IMPUG" in s else "recurridos" if "RECURR" in s else None


for anio in (2011, 2013, 2015, 2017, 2019, 2021, 2023):
    pk = os.path.join(ROOT, "../datos_oficiales", str(anio), "agregado.pkl")
    if not os.path.exists(pk) or match_bloques is None: continue
    votes, mesas = pd.read_pickle(pk)
    votes = votes.copy(); votes["tipo"] = votes.votos_tipo.map(tipo_of)
    votes["unidad"] = np.where(votes.seccionprovincial_nombre.fillna("") != "", votes.seccionprovincial_nombre.fillna("").str.title() + " · " + votes.seccion_nombre, votes.seccion_nombre)
    for cam, pat, cargo in (("DIPUTADOS", "DIPUTAD", "diputados"), ("SENADORES", "SENADOR", "senadores")):
        v = votes[votes.cargo_nombre.str.upper().str.contains(pat) & votes.tipo.notna()]
        if v.empty: continue
        groups, D, res, used = match_bloques(anio, cam)
        g = v.groupby(["distrito_id", "distrito_nombre", "unidad", "tipo", "agrupacion_nombre"], dropna=False).v.sum().reset_index()
        g["bloque"] = np.where(g.tipo == "agrupacion", g.agrupacion_nombre.map(res).fillna("Otros (sin agrupar)"), "")
        df = pd.DataFrame(dict(provincia=g.distrito_nombre.str.title(), unidad=g.unidad, tipo_fila=g.tipo, codigo_partido=np.where(g.tipo == "agrupacion", g.agrupacion_nombre, ""),
                               partido=np.where(g.tipo == "agrupacion", g.agrupacion_nombre, ""), bloque=g.bloque, votos=g.v))
        # electores por seccion (mesas del cargo)
        mm = mesas[mesas.cargo_nombre.str.upper().str.contains(pat)].copy(); mm["e"] = pd.to_numeric(mm.mesa_electores, errors="coerce").fillna(0)
        nm = v.drop_duplicates(["distrito_id", "seccion_id"])[["distrito_id", "seccion_id", "distrito_nombre", "unidad"]]
        el = mm.groupby(["distrito_id", "seccion_id"]).e.sum().reset_index().merge(nm, on=["distrito_id", "seccion_id"], how="left").dropna(subset=["unidad"])
        el = pd.DataFrame(dict(provincia=el.distrito_nombre.str.title(), unidad=el.unidad, tipo_fila="electores", codigo_partido="", partido="", bloque="", votos=el.e))
        df = pd.concat([df, el], ignore_index=True)
        add(df, dict(anio=anio, cargo=cargo, nivel="seccion",
                     fuente="DINE, escrutinio provisorio por mesa (datos.gob.ar, «Resultados Provisionales Elecciones %d»); bloque = tabla de Wikipedia «Elecciones legislativas de Argentina de %d», emparejado por nombre (ver mapeo_bloques/)" % (anio, anio)))
        tot = D.sum()
        pd.DataFrame(dict(lista_dine=D.index, votos=D.values, bloque_wikipedia=[res.get(n, "") for n in D.index])).to_csv(os.path.join(MAPEO, "%d_%s.csv" % (anio, cargo)), index=False, encoding="utf-8-sig")
        print(anio, cargo, "bloques: %.1f %% de los votos agrupados" % (100 * D[D.index.isin(res)].sum() / tot))

# ---------------------------------------------------------------- 5b. 2003-2009 (PolAr_Data, a partir del Atlas Electoral de Andy Tow / INDRA): presidente 2003 y 2007, diputados y senadores 2005-2009
try:
    from bloques_prov import match_prov
except Exception as e:
    match_prov = None; print("sin bloques provinciales:", e)
PRES_BLOQ = {
    2003: {"Al. Frente por la Lealtad": "Frente por la Lealtad (Menem)", "Al. Frente para la Victoria": "Frente para la Victoria (Kirchner)",
           "Al. Mov. Fed. P/Recrear el Crecimiento": "Movimiento Federal Recrear (López Murphy)", "Al. Frente Movimiento Popular": "Frente Movimiento Nacional y Popular (Rodríguez Saá)",
           "Al. Afirm.para una Rep. Igualitaria": "Afirmación para una República Igualitaria (Carrió)", "Unión Cívica Radical": "Unión Cívica Radical (Moreau)",
           "Al. Izquierda Unida": "Izquierda Unida (Walsh)"},
    2007: {"Alianza Frente para la Victoria": "Frente para la Victoria (Fernández de Kirchner)", "Confederación Coalición Cívica": "Coalición Cívica (Carrió)",
           "Alianza Concertación UNA": "Concertación UNA (Lavagna)", "Alianza Frente Justicia, Unión y Libertad": "Frente Justicia, Unión y Libertad (Rodríguez Saá)"}}
for anio in (2003, 2005, 2007, 2009):
    pk = os.path.join(ROOT, "../datos_oficiales", str(anio), "agregado_polar.pkl")
    if not os.path.exists(pk): continue
    votes, mesas = pd.read_pickle(pk)
    votes = votes.copy(); votes["tipo"] = votes.votos_tipo.map(tipo_of); votes["unidad"] = votes.seccion_nombre.str.strip().str.title()
    for cam, pat, cargo in (("PRESIDENTE", "PRESIDENTE", "presidente"), ("DIPUTADOS", "DIPUTAD", "diputados"), ("SENADORES", "SENADOR", "senadores")):
        v = votes[votes.cargo_nombre.str.upper().str.contains(pat) & votes.tipo.notna()]
        if v.empty: continue
        g = v.groupby(["distrito_id", "distrito_nombre", "unidad", "tipo", "agrupacion_nombre"], dropna=False).v.sum().reset_index()
        if cam == "PRESIDENTE":
            pb = PRES_BLOQ.get(anio, {})
            g["bloque"] = np.where(g.tipo == "agrupacion", g.agrupacion_nombre.map(lambda n: pb.get(n, re.sub(r"^Al\. ", "Alianza ", n))), "")
            fuente = "PolAr_Data (electorArg), escrutinio provisorio por mesa del Atlas Electoral de Andy Tow / INDRA; no es el definitivo; bloque = frente (como la tabla de Wikipedia)"
        else:
            if match_prov is None or anio == 2003: continue
            groups, res, log, gg = match_prov(anio, cam)
            g["bloque"] = [("Otros (sin agrupar)" if t == "agrupacion" else "") if (p, n) not in res else res[(p, n)] for p, n, t in zip(g.distrito_nombre, g.agrupacion_nombre, g.tipo)]
            fuente = "PolAr_Data (electorArg), escrutinio provisorio por mesa del Atlas Electoral de Andy Tow / INDRA; no es el definitivo; bloque = tabla de Wikipedia «Elecciones legislativas de Argentina de %d», emparejado lista por lista con la tabla provincial (ver mapeo_bloques/)" % anio
            mp = gg.copy(); mp["bloque_wikipedia"] = [res.get((p, n), "") for p, n in zip(mp.distrito_nombre, mp.agrupacion_nombre)]
            mp.rename(columns={"distrito_nombre": "provincia", "agrupacion_nombre": "lista_polar", "v": "votos"}).to_csv(os.path.join(MAPEO, "%d_%s.csv" % (anio, cargo)), index=False, encoding="utf-8-sig")
            print(anio, cargo, "bloques: %.1f %% de los votos agrupados" % (100 * g[(g.tipo == "agrupacion") & (g.bloque != "Otros (sin agrupar)")].v.sum() / g[g.tipo == "agrupacion"].v.sum()))
        df = pd.DataFrame(dict(provincia=g.distrito_nombre, unidad=g.unidad, tipo_fila=g.tipo, codigo_partido=np.where(g.tipo == "agrupacion", g.agrupacion_nombre, ""),
                               partido=np.where(g.tipo == "agrupacion", g.agrupacion_nombre, ""), bloque=g.bloque, votos=g.v))
        mm = mesas[mesas.cargo_nombre.str.upper().str.contains(pat)]
        nm = v.drop_duplicates(["distrito_id", "seccion_id"])[["distrito_id", "seccion_id", "distrito_nombre", "unidad"]]
        el = mm.groupby(["distrito_id", "seccion_id"]).mesa_electores.sum().reset_index().merge(nm, on=["distrito_id", "seccion_id"], how="inner")
        el = el.groupby(["distrito_nombre", "unidad"]).mesa_electores.sum().reset_index()
        el = pd.DataFrame(dict(provincia=el.distrito_nombre, unidad=el.unidad, tipo_fila="electores", codigo_partido="", partido="", bloque="", votos=el.mesa_electores))
        add(pd.concat([df, el], ignore_index=True), dict(anio=anio, cargo=cargo, nivel="departamento", fuente=fuente))

# ---------------------------------------------------------------- 6. el resto de lo que hay en el proyecto
# 6a. gobernadores 2011-2023 (DINE, provisorio por mesa, agregado por seccion; sin bloques: cada provincia tiene su oferta)
for anio in (2011, 2013, 2015, 2017, 2019, 2021, 2023):
    pk = os.path.join(ROOT, "../datos_oficiales", str(anio), "agregado.pkl")
    if not os.path.exists(pk): continue
    votes, mesas = pd.read_pickle(pk)
    v = votes[votes.cargo_nombre.str.upper().str.contains("GOBERNADOR")].copy(); v["tipo"] = v.votos_tipo.map(tipo_of); v = v[v.tipo.notna()]
    if v.empty: continue
    v["unidad"] = np.where(v.seccionprovincial_nombre.fillna("") != "", v.seccionprovincial_nombre.fillna("").str.title() + " · " + v.seccion_nombre, v.seccion_nombre)
    g = v.groupby(["distrito_nombre", "unidad", "tipo", "agrupacion_nombre"], dropna=False).v.sum().reset_index()
    df = pd.DataFrame(dict(provincia=g.distrito_nombre.str.title(), unidad=g.unidad, tipo_fila=g.tipo, codigo_partido="", partido=np.where(g.tipo == "agrupacion", g.agrupacion_nombre, ""), bloque="", votos=g.v))
    add(df, dict(anio=anio, cargo="gobernador", nivel="seccion", fuente="DINE, escrutinio provisorio por mesa (datos.gob.ar, «Resultados Provisionales Elecciones %d»); sin bloques; no es el definitivo" % anio))

# 6b. Entre Ríos: diputados nacionales 1991 (parcial), 1997 y 2001 (portal de datos de la provincia; capas ya consolidadas en preparados/)
ERD = os.path.join(ROOT, "../datos/preparados")
er = []
f = os.path.join(ERD, "entre_rios_diputados_2001_por_departamento.csv")
if os.path.exists(f):
    d = pd.read_csv(f); er.append((2001, pd.DataFrame(dict(unidad=d.departamento_archivo.str.title(), partido=d.fuerza_original, votos=d.votos)), "Entre Ríos, datos abiertos (datos.entrerios.gov.ar), diputados nacionales 2001; una tabla por departamento"))
f = os.path.join(ERD, "entre_rios_diputados_1997_por_departamento.csv")
if os.path.exists(f):
    d = pd.read_csv(f); er.append((1997, pd.DataFrame(dict(unidad=np.where(d.tipo_unidad.str.contains("custod", case=False), "Custodias", d.departamento_archivo.str.title()), partido=d.fuerza_original, votos=d.votos)), "Entre Ríos, datos abiertos, diputados nacionales 1997; el grupo «custodias» es aparte"))
f = os.path.join(ERD, "entre_rios_diputados_1991_parcial.csv")
if os.path.exists(f):
    d = pd.read_csv(f); er.append((1991, pd.DataFrame(dict(unidad=d.departamento_archivo.str.title(), partido=d.fuerza_original, votos=d.votos_original)), "Entre Ríos, datos abiertos, diputados nacionales 1991; PARCIAL: 15 departamentos (falta Feliciano) y celdas vacías conservadas"))
for anio, d, fte in er:
    d = d.copy(); d["provincia"] = "Entre Ríos"; d["tipo_fila"] = "agrupacion"; d["codigo_partido"] = ""; d["bloque"] = ""
    add(d[["provincia", "unidad", "tipo_fila", "codigo_partido", "partido", "bloque", "votos"]], dict(anio=anio, cargo="diputados", nivel="departamento", fuente=fte, fuente_id="entre_rios_oficial"))

# 6c. dat.ar, elecciones nacionales 2003 (resultados «definitivos» por departamento, SIN VALIDAR): diputados y senadores 2003 (no hay otra fuente) y presidente (duplica a PolAr)
f = os.path.join(ROOT, "../raw", "datar_2003_departamento_SIN_VALIDAR.csv")
if os.path.exists(f):
    d = pd.read_csv(f); u = d.partido.str.upper()
    d["tipo_fila"] = np.select([u.str.contains("BLANCO"), u.str.contains("NULO"), u.str.contains("TOTALES"), u.str.contains("POSITIVOS")], ["blancos", "nulos", "total", "positivos"], "agrupacion")
    for cod, cargo in (("DN", "diputados"), ("SN", "senadores"), ("Presidente", "presidente")):
        x = d[d.eleccion == cod]
        df = pd.DataFrame(dict(provincia=x.provincia, unidad=x.departamento.str.title(), tipo_fila=x.tipo_fila, codigo_partido="", partido=np.where(x.tipo_fila == "agrupacion", x.partido, ""), bloque="", votos=x.votos))
        add(df, dict(anio=2003, cargo=cargo, nivel="departamento", fuente_id="principal" if cargo != "presidente" else "datar_2003",
                     fuente="dat.ar (datar.info), «Elecciones nacionales 2003, resultados definitivos» por departamento; SIN VALIDAR: la fuente trae errores de formato e inconsistencias (ver raw/ y preparados/datar_2003_valores_para_revisar.csv); falta La Pampa en diputados"))

# 6d. capa 2 de base8399: detalle por partido de Mendoza (UNCuyo), Corrientes, Córdoba 1999 y Entre Ríos (esta ultima ya va por 6b); complementa a Ernesto
for f in sorted(glob.glob(os.path.join(ROOT, "../datos/base8399", "elecciones", "*", "detalle_partidos.csv"))):
    d = pd.read_csv(f); d = d[d.provincia != "Entre Ríos"]
    if d.empty: continue
    s = d.partido_fuente.fillna("").str.lower()
    d["tipo"] = np.where(d.tipo_fila == "agrupacion", "agrupacion", np.where(d.tipo_fila == "total", "total", np.where(d.tipo_fila == "subtotal_alianza", "subtotal_alianza",
                np.select([s.str.contains("blanc"), s.str.contains("nul"), s.str.contains("impug"), s.str.contains("recurr")], ["blancos", "nulos", "impugnados", "recurridos"], "tipo_voto"))))
    for (anio, cargo, prov), x in d.groupby(["anio", "cargo", "provincia"]):
        df = pd.DataFrame(dict(provincia=prov, unidad=x.departamento.astype(str).str.title(), tipo_fila=x.tipo, codigo_partido="", partido=np.where(x.tipo.isin(["agrupacion", "subtotal_alianza"]), x.partido_fuente, ""), bloque="", votos=x.votos))
        add(df, dict(anio=int(anio), cargo=cargo, nivel="departamento", fuente_id="detalle_" + norm(prov).replace(" ", "_"),
                     fuente="base8399, capa 2: detalle por partido de %s (%s); ver base8399/LEEME.md. subtotal_alianza y total conviven con las agrupaciones: no sumar" % (prov, "; ".join(sorted(set(x.fuente.astype(str).str.split("!").str[0])))[:120])))

# ---------------------------------------------------------------- 7. transcripciones propias 1912-1965 (ver transcripciones_xlsx.py)
from transcripciones_xlsx import frames as frames_transcripciones
FRAMES += frames_transcripciones()

LARGO = pd.concat(FRAMES, ignore_index=True)
LARGO["votos"] = pd.to_numeric(LARGO.votos, errors="coerce")

# ---------------------------------------------------------------- AMBA 2025 por circuito (hoja aparte: no se suma con el resto)
AMBA = None
pk = os.path.join(ROOT, "../mapas/mapaAMBA2025", "dip_amba_mesas.pkl")
if os.path.exists(pk):
    a = pd.read_pickle(pk)
    a["ok"] = a.estado_final == "ESCRUTADO"
    pos = a[a.votos_tipo == "POSITIVO"].groupby(["part", "sec", "cir", "agrupacion_nombre"]).v.sum().reset_index()
    pos["tipo_fila"] = "agrupacion"; pos = pos.rename(columns={"agrupacion_nombre": "partido"})
    oth = a[a.votos_tipo.isin(["EN BLANCO", "NULO", "IMPUGNADO", "RECURRIDO"])].groupby(["part", "sec", "cir", "votos_tipo"]).v.sum().reset_index()
    oth["tipo_fila"] = oth.votos_tipo.map({"EN BLANCO": "blancos", "NULO": "nulos", "IMPUGNADO": "impugnados", "RECURRIDO": "recurridos"}); oth["partido"] = ""
    mm = a.drop_duplicates("mesa").groupby(["part", "sec", "cir"]).agg(mesas=("mesa", "size"), escrutadas=("ok", "sum"), electores=("elec", "sum")).reset_index()
    mm = mm.melt(id_vars=["part", "sec", "cir"], var_name="tipo_fila", value_name="v"); mm["partido"] = ""
    AMBA = pd.concat([pos[["part", "sec", "cir", "tipo_fila", "partido", "v"]], oth[["part", "sec", "cir", "tipo_fila", "partido", "v"]], mm[["part", "sec", "cir", "tipo_fila", "partido", "v"]]], ignore_index=True)
    AMBA = AMBA.rename(columns={"part": "ambito", "sec": "seccion_id", "cir": "circuito", "v": "votos"})
    AMBA.insert(0, "anio", 2025); AMBA.insert(1, "cargo", "diputados")

# ---------------------------------------------------------------- por eleccion: ancho (una fila por unidad)
META = ["positivos", "blancos", "nulos", "blancos_y_nulos", "impugnados_recurridos", "impugnados", "recurridos", "total", "votantes", "electores", "electores_mesas_escrutadas", "mesas", "mesas_escrutadas"]
INDEX = []


def pivot(df):
    ag = df[df.tipo_fila.isin(["agrupacion", "candidato"])].copy()
    ag["col"] = np.where(ag.codigo_partido != "", ag.codigo_partido, ag.partido)
    P = ag.pivot_table(index=["provincia", "unidad"], columns="col", values="votos", aggfunc="sum")
    P = P[P.sum().sort_values(ascending=False).index]
    me = df[~df.tipo_fila.isin(["agrupacion", "candidato"])].pivot_table(index=["provincia", "unidad"], columns="tipo_fila", values="votos", aggfunc="sum")
    me = me[[c for c in META if c in me.columns]]
    W = me.join(P, how="outer").reset_index()
    return W, ag


for (anio, cargo, fid), df in LARGO.groupby(["anio", "cargo", "fuente_id"], sort=True):
    W, ag = pivot(df)
    part = (ag.groupby(["provincia", "codigo_partido", "partido"], dropna=False).votos.sum().reset_index().sort_values(["provincia", "votos"], ascending=[True, False]))
    fn = "%d_%s.xlsx" % (anio, cargo) if fid == "principal" else "%d_%s__%s.xlsx" % (anio, cargo, fid)
    with pd.ExcelWriter(os.path.join(POR, fn), engine="openpyxl") as xw:
        W.to_excel(xw, sheet_name="resultados", index=False)
        part.to_excel(xw, sheet_name="partidos", index=False)
        bl = ag[ag.bloque != ""]
        if len(bl) and bl.bloque.nunique() > 1:
            B = bl.pivot_table(index=["provincia", "unidad"], columns="bloque", values="votos", aggfunc="sum")
            B = B[B.sum().sort_values(ascending=False).index].reset_index()
            B.to_excel(xw, sheet_name="bloques", index=False)
        pd.DataFrame({"nota": ["Una fila por %s; columnas: totales de la unidad y votos por partido (codigo de la fuente)." % df.nivel.iloc[0],
                               "Fuente: " + df.fuente.iloc[0],
                               "La hoja «partidos» trae la descripcion del codigo cuando se pudo leer (hojas de leyendas de Ernesto o nombres de los atlas); el mismo codigo puede significar cosas distintas segun la provincia.",
                               "Sin corregir ni imputar: las sumas de partidos pueden no cerrar con positivos/total (ver LEEME de cada base)."]}).to_excel(xw, sheet_name="LEEME", index=False)
    INDEX.append(dict(anio=anio, cargo=cargo, fuente_id=fid, nivel=df.nivel.iloc[0], unidades=len(W), partidos=ag.codigo_partido.replace("", np.nan).fillna(ag.partido).nunique(),
                      filas_largo=len(df), archivo="por_eleccion/" + fn, fuente=df.fuente.iloc[0]))
if AMBA is not None:
    fn = "2025_diputados_AMBA_circuito.xlsx"
    W = AMBA[AMBA.tipo_fila == "agrupacion"].pivot_table(index=["ambito", "seccion_id", "circuito"], columns="partido", values="votos", aggfunc="sum")
    W = W[W.sum().sort_values(ascending=False).index]
    me = AMBA[AMBA.tipo_fila != "agrupacion"].pivot_table(index=["ambito", "seccion_id", "circuito"], columns="tipo_fila", values="votos", aggfunc="sum")
    me = me[[c for c in ["blancos", "nulos", "impugnados", "recurridos", "electores", "mesas", "escrutadas"] if c in me.columns]]
    W = me.join(W).reset_index()
    with pd.ExcelWriter(os.path.join(POR, fn), engine="openpyxl") as xw:
        W.to_excel(xw, sheet_name="resultados", index=False)
    INDEX.append(dict(anio=2025, cargo="diputados", fuente_id="circuito_AMBA", nivel="circuito (AMBA: Capital + 40 partidos)", unidades=len(W), partidos=AMBA[AMBA.tipo_fila == "agrupacion"].partido.nunique(),
                      filas_largo=len(AMBA), archivo="por_eleccion/" + fn, fuente="DINE, provisorio por mesa; ver mapaAMBA2025/LEEME_AMBA2025.md (no esta en la hoja «largo»: se superpone con las secciones)"))

# ---------------------------------------------------------------- master
TARGET = os.path.join(OUT, "MASTER_resultados.xlsx")
try:
    open(TARGET, "ab").close()
except PermissionError:      # abierto en Excel: se escribe al lado con otro nombre
    TARGET = os.path.join(OUT, "MASTER_resultados_NUEVO.xlsx"); print("MASTER_resultados.xlsx esta abierto: se escribe", TARGET)
wb = Workbook(write_only=True)
ws = wb.create_sheet("largo"); ws.append(COLS)
for r in LARGO.itertuples(index=False):
    ws.append([None if (isinstance(x, float) and np.isnan(x)) else x for x in r])
ws = wb.create_sheet("elecciones"); idx = pd.DataFrame(INDEX); ws.append(list(idx.columns))
for r in idx.itertuples(index=False): ws.append(list(r))
if AMBA is not None:
    ws = wb.create_sheet("AMBA2025_circuitos"); ws.append(list(AMBA.columns))
    for r in AMBA.itertuples(index=False): ws.append([None if (isinstance(x, float) and np.isnan(x)) else x for x in r])
ws = wb.create_sheet("LEEME")
for line in ["MASTER de resultados electorales por departamento (proyecto de atlas electorales).",
             "Hoja «largo»: formato largo unificado (anio, cargo, nivel, provincia, unidad, tipo_fila, codigo_partido, partido, bloque, votos, fuente_id, fuente). fuente_id = principal para la serie de cada eleccion; otro valor = fuente complementaria o alternativa de la misma eleccion (archivo con sufijo __fuente_id).",
             "tipo_fila: agrupacion (votos del partido), positivos, blancos, nulos, impugnados, recurridos, total, votantes, electores, mesas, mesas_escrutadas. No sumar positivos/total/electores con las agrupaciones.",
             "Hoja «elecciones»: indice con el archivo por eleccion de la carpeta por_eleccion/ (formato ancho: una fila por unidad).",
             "1916/1922/1928/1930: Canton (1968) por departamentos de 1914, tal como estan en los atlas (con sus notas y huecos). 1983-1999: Ernesto Calvo, sin corregir (mas el detalle por partido de Mendoza, Corrientes y Cordoba como fuente complementaria; Entre Rios 1991, 1997 y 2001 del portal de la provincia). 2003: PolAr_Data (presidente), dat.ar (diputados y senadores, sin validar). 2005-2009: PolAr_Data. 2011-2025: DINE (provisorio por mesa), mas presidenciales 2011-2023 de las carpetas del usuario y gobernadores 2011-2023.",
             "bloque: agrupacion segun la tabla de Wikipedia de cada eleccion (diputados y senadores 2005-2025, 1983-1994 segun los atlas, presidenciales por frente). Vacio donde no hubo criterio (ver LEEME.md de esta carpeta).",
             "No incluidos: atlas ficticio de 1916, el CSV de Gemini 1912-1973, la base de Lupu-Stokes, PASO legislativas y cargos provinciales distintos de gobernador."]:
    ws.append([line])
os.makedirs(OUT, exist_ok=True)
wb.save(TARGET)
idx.to_csv(os.path.join(OUT, "indice_elecciones.csv"), index=False, encoding="utf-8-sig")
print("listo:", len(LARGO), "filas en largo;", len(INDEX), "archivos por eleccion")
