"""Convierte las bases por mesa de PolAr_Data (electorArg, a partir del Atlas Electoral de Andy Tow / INDRA) al mismo formato que agregar_dine.py.
    python agregar_polar.py            -> datos_oficiales/{2003,2005,2007,2009}/agregado.pkl

Entrada: datos_oficiales/polar/data__<prov>_<cargo>_gral<anio>.csv (una fila por mesa, una columna por lista) y listas__*.csv (codigo de lista -> nombre, por provincia).
Salida: (votos, mesas) con las mismas columnas que la DINE. Unidad = departamento (en CABA, seccion/comuna segun la fuente).
Dos archivos traen una columna repetida (caba 2009: 0146; corrientes senadores 2009: 0543): se suman en una sola y se rotula."""
import os, re, glob, collections
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "datos_oficiales", "polar")
PROV = dict(caba="Ciudad de Buenos Aires", pba="Buenos Aires", catamarca="Catamarca", chaco="Chaco", chubut="Chubut", cordoba="Córdoba", corrientes="Corrientes",
            erios="Entre Ríos", formosa="Formosa", jujuy="Jujuy", mendoza="Mendoza", misiones="Misiones", neuquen="Neuquén", pampa="La Pampa", rioja="La Rioja",
            rnegro="Río Negro", salta="Salta", santiago="Santiago del Estero", scruz="Santa Cruz", sfe="Santa Fe", sjuan="San Juan", sluis="San Luis", tdf="Tierra del Fuego",
            tucuman="Tucumán", arg="")
CARGO = dict(dip="DIPUTADOS NACIONALES", sen="SENADORES NACIONALES", presi="PRESIDENTE Y VICE")
NOTA = {}   # (archivo) -> nota sobre columnas ambiguas


def listas(cargo, anio):
    cc = "dip" if cargo == "dip" else cargo
    f = os.path.join(SRC, "listas__listas_%s_gral%d.csv" % (cc, anio))
    if not os.path.exists(f): return {}
    l = pd.read_csv(f, dtype=str)
    return {(r.vot_proCodigoProvincia.strip().zfill(2), r.vot_parCodigo.strip().zfill(4)): re.sub(r"\s+", " ", r.parDenominacion).strip() for r in l.itertuples()}


out = collections.defaultdict(lambda: ([], []))
for f in sorted(glob.glob(os.path.join(SRC, "data__*_gral*.csv"))):
    m = re.match(r"data__(\w+?)_(dip|sen|presi)_gral(\d{4})\.csv", os.path.basename(f))
    if not m and "arg_presi" in f: m = re.match(r"data__(arg)_(presi)_gral(\d{4})\.csv", os.path.basename(f))
    if not m: continue
    pv, cargo, anio = m.group(1), m.group(2), int(m.group(3))
    import csv; hdr = [h.strip() for h in next(csv.reader(open(f, encoding="utf-8-sig")))]
    d = pd.read_csv(f, dtype=str, header=0, names=[("%s__%d" % (c, i)) for i, c in enumerate(hdr)])
    base = {c.split("__")[0]: c for c in d.columns if not c.split("__")[0].isdigit()}
    codes = [(c, c.split("__")[0]) for c in d.columns if c.split("__")[0].isdigit()]
    for c in [c for c, _ in codes]: d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    const = [c for c, k in codes if d[c].nunique() == 1 and d[c].iloc[0] > 100]       # columna con un valor fijo en todas las mesas (error de la fuente)
    if const:
        NOTA[os.path.basename(f) + " (descartada)"] = [k for c, k in codes if c in const]
        codes = [(c, k) for c, k in codes if c not in const]
    dups = [k for k, v in collections.Counter(k for _, k in codes).items() if v > 1]
    if dups: NOTA[os.path.basename(f)] = dups
    for c in [c for c, _ in codes] + [base["blancos"], base["nulos"]]: d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d["codprov"] = d[base["codprov"]].str.strip().str.zfill(2)
    d["depto_n"] = d[base["depto"]].str.strip()
    d["coddepto"] = d[base["coddepto"]].str.strip()
    d["circ"] = d[base["circuito"]].str.strip()
    d["mesa"] = d[base["mesa"]].str.strip()
    el = pd.to_numeric(d[base["electores"]], errors="coerce").fillna(0)
    ln = listas(cargo, anio)
    # una fila por (provincia, depto) con la suma de cada lista
    rows = []
    for cp, g in d.groupby("codprov"):
        pname = PROV[pv] if PROV[pv] else None
        gk = g.groupby(["coddepto", "depto_n"])
        sums = gk[[c for c, _ in codes] + [base["blancos"], base["nulos"]]].sum()
        for (cd, dn), r in sums.iterrows():
            acc = collections.defaultdict(float)
            for c, k in codes:
                nm = ln.get((cp, k), "lista " + k)
                if k in dups: nm = nm + " (+ columna repetida %s en la fuente)" % k
                acc[(k, nm)] += r[c]
            for (k, nm), v in acc.items(): rows.append((cp, cd, dn, k, nm, "POSITIVO", v))
            rows.append((cp, cd, dn, "", "", "BLANCO", r[base["blancos"]]))
            rows.append((cp, cd, dn, "", "", "NULO", r[base["nulos"]]))
    vt = pd.DataFrame(rows, columns=["distrito_id", "seccion_id", "seccion_nombre", "agrupacion_id", "agrupacion_nombre", "votos_tipo", "v"])
    vt["distrito_nombre"] = vt.distrito_id.map(lambda c: PROV[pv] or "")
    vt["seccionprovincial_nombre"] = ""; vt["cargo_nombre"] = CARGO[cargo]; vt["mesa_tipo"] = ""
    ms = pd.DataFrame(dict(distrito_id=d.codprov, seccion_id=d.coddepto, circuito_id=d.circ, mesa_id=d.mesa, cargo_nombre=CARGO[cargo], mesa_electores=el, mesa_tipo=""))
    out[anio][0].append(vt); out[anio][1].append(ms)

# nombres de provincia para el archivo nacional de presidente (arg): se toma del resto de los archivos del mismo anio
CODEPROV = {}
for f in glob.glob(os.path.join(SRC, "data__*_dip_gral2005.csv")):
    pv = re.match(r"data__(\w+?)_dip", os.path.basename(f)).group(1)
    c = pd.read_csv(f, dtype=str, usecols=["codprov"]).codprov.iloc[0].strip().zfill(2); CODEPROV[c] = PROV[pv]
for anio, (vs, ms) in sorted(out.items()):
    votes = pd.concat(vs, ignore_index=True)
    votes["distrito_nombre"] = votes.distrito_id.map(CODEPROV)
    mesas = pd.concat(ms, ignore_index=True)
    os.makedirs(os.path.join(ROOT, "datos_oficiales", str(anio)), exist_ok=True)
    pd.to_pickle((votes, mesas), os.path.join(ROOT, "datos_oficiales", str(anio), "agregado_polar.pkl"))
    print(anio, len(votes), "filas;", len(mesas), "mesas-cargo;", sorted(votes.cargo_nombre.unique()), "| sin nombre de provincia:", votes.distrito_nombre.isna().sum())
print("columnas repetidas:", NOTA)
