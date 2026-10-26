"""Agrega los provisorios por mesa de la DINE (2011-2023, generales) por seccion y cargo nacional -> datos_oficiales/<anio>/agregado.pkl
    python agregar_dine.py 2017 2019 ...
Salida: (votos, mesas): votos = suma por (distrito, seccion, cargo, agrupacion, tipo de voto); mesas = una fila por mesa y cargo con electores y estado."""
import os, re, sys, glob
import pandas as pd
ROOT = os.path.dirname(os.path.abspath(__file__))
CARGO = re.compile(r"PRESIDENTE|SENADOR.*NACIONAL|DIPUTAD.*NACIONAL|PARLASUR|GOBERNADOR", re.I)
for anio in sys.argv[1:] or ["2011", "2013", "2015", "2017", "2019", "2021", "2023"]:
    f = (glob.glob(os.path.join(ROOT, "datos_oficiales", anio, "x", "*", "Resultado*.csv")) + glob.glob(os.path.join(ROOT, "datos_oficiales", anio, "x", "Resultado*.csv")))[0]
    vs, ms = [], []
    for ch in pd.read_csv(f, dtype=str, chunksize=1_500_000, encoding="utf-8", low_memory=False):
        ch.columns = [c.lower() for c in ch.columns]
        ch = ch[ch.cargo_nombre.fillna("").str.contains(CARGO)].copy()
        if ch.empty: continue
        ch["v"] = pd.to_numeric(ch.votos_cantidad, errors="coerce").fillna(0)
        for c in ("agrupacion_nombre", "seccionprovincial_nombre", "mesa_tipo", "estado_final"):
            if c not in ch: ch[c] = ""
        ch["agrupacion_nombre"] = ch.agrupacion_nombre.fillna("").str.strip()
        ch["seccionprovincial_nombre"] = ch.seccionprovincial_nombre.fillna("")
        key = ["distrito_id", "distrito_nombre", "seccionprovincial_nombre", "seccion_id", "seccion_nombre", "cargo_nombre", "agrupacion_id", "agrupacion_nombre", "votos_tipo", "mesa_tipo"]
        vs.append(ch.groupby(key, dropna=False).v.sum())
        ms.append(ch[["distrito_id", "seccion_id", "circuito_id", "mesa_id", "cargo_nombre", "mesa_electores", "mesa_tipo"]].drop_duplicates())
    votes = pd.concat(vs).groupby(level=list(range(10)), dropna=False).sum().reset_index()
    mesas = pd.concat(ms).drop_duplicates(["distrito_id", "seccion_id", "circuito_id", "mesa_id", "cargo_nombre", "mesa_tipo"])
    pd.to_pickle((votes, mesas), os.path.join(ROOT, "datos_oficiales", anio, "agregado.pkl"))
    print(anio, len(votes), "filas de votos;", len(mesas), "mesas-cargo;", sorted(votes.cargo_nombre.unique()), flush=True)
