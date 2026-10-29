"""Agrega los provisorios por mesa de las PASO (DINE, 2011-2023) por sección, cargo nacional, agrupación y lista interna.
    python datos/agregar_dine_paso.py 2011 2013 ...
Lee el zip de datos_oficiales/<año>_paso/ sin descomprimirlo en disco y escribe datos_oficiales/<año>_paso/agregado.pkl:
(votos, mesas) como agregar_dine.py, con las columnas extra lista_numero y lista_nombre."""
import os, re, sys, glob, zipfile
import pandas as pd
ROOT = os.path.dirname(os.path.abspath(__file__))
CARGO = re.compile(r"PRESIDENTE|SENADOR.*NACIONAL|DIPUTAD.*NACIONAL|PARLASUR", re.I)
for anio in sys.argv[1:] or ["2011", "2013", "2015", "2017", "2019", "2021", "2023"]:
    d = os.path.join(ROOT, "../datos_oficiales", anio + "_paso")
    z = zipfile.ZipFile(glob.glob(os.path.join(d, "*.zip"))[0])
    name = next(n for n in z.namelist() if re.search(r"Resultado[^/]*\.csv$", n))
    vs, ms = [], []
    for ch in pd.read_csv(z.open(name), dtype=str, chunksize=1_500_000, encoding="utf-8", low_memory=False):
        ch.columns = [c.lower() for c in ch.columns]
        ch = ch[ch.cargo_nombre.fillna("").str.contains(CARGO)].copy()
        if ch.empty: continue
        ch["v"] = pd.to_numeric(ch.votos_cantidad, errors="coerce").fillna(0)
        for c in ("agrupacion_nombre", "seccionprovincial_nombre", "mesa_tipo", "lista_numero", "lista_nombre"):
            if c not in ch: ch[c] = ""
            ch[c] = ch[c].fillna("").str.strip()
        key = ["distrito_id", "distrito_nombre", "seccionprovincial_nombre", "seccion_id", "seccion_nombre", "cargo_nombre",
               "agrupacion_id", "agrupacion_nombre", "lista_numero", "lista_nombre", "votos_tipo", "mesa_tipo"]
        vs.append(ch.groupby(key, dropna=False).v.sum())
        ms.append(ch[["distrito_id", "seccion_id", "circuito_id", "mesa_id", "cargo_nombre", "mesa_electores", "mesa_tipo"]].drop_duplicates())
    votes = pd.concat(vs).groupby(level=list(range(12)), dropna=False).sum().reset_index()
    mesas = pd.concat(ms).drop_duplicates(["distrito_id", "seccion_id", "circuito_id", "mesa_id", "cargo_nombre", "mesa_tipo"])
    pd.to_pickle((votes, mesas), os.path.join(d, "agregado.pkl"))
    print(anio, len(votes), "filas de votos;", len(mesas), "mesas-cargo;", sorted(votes.cargo_nombre.unique()), flush=True)
