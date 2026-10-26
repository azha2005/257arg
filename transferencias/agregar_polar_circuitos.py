"""Agrega PolAr (mesas de diputados nacionales, 2003-2009) por circuito -> transferencias/circ_<anio>.pkl, con el formato de agregar_circuitos.py.
    python transferencias/agregar_polar_circuitos.py 2009
    python transferencias/agregar_polar_circuitos.py 2003p 2007p     (presidente: data__arg_presi_gral<anio>.csv, codigos nacionales)
Entrada: datos_oficiales/polar/data__<prov>_dip_gral<anio>.csv (codprov, depto, coddepto, circuito, mesa, electores, blancos, nulos, una columna por lista).
Ademas guarda transferencias/secciones_<anio>.csv (distrito, seccion, nombre) para emparejar por departamento."""
import os, glob, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FIX = ["codprov", "depto", "coddepto", "circuito", "mesa", "electores", "blancos", "nulos"]

for arg in sys.argv[1:] or ["2009"]:
    anio = arg.rstrip("p")
    patron = "data__arg_presi_gral%s.csv" if arg.endswith("p") else "data__*_dip_gral%s.csv"
    vs, es, secs = [], [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "datos_oficiales", "polar", patron % anio))):
        d = pd.read_csv(f, dtype=str)
        d = d.loc[:, ~d.columns.duplicated()]
        num = d.columns.drop(FIX, errors="ignore")
        for c in list(num) + ["electores", "blancos", "nulos"]:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
        d["distrito_id"] = d.codprov.astype(int).map("{:02d}".format)
        d["seccion_id"] = d.coddepto.astype(int)
        d["circuito"] = d.circuito.fillna("").str.strip().str.upper().str.lstrip("0").replace("", "0")
        key = ["distrito_id", "seccion_id", "circuito"]
        tot = d[list(num) + ["blancos", "nulos"]].sum(1)
        es.append(d[tot > 0].groupby(key).electores.sum())
        l = d.melt(id_vars=key, value_vars=list(num), var_name="agrupacion_id", value_name="v")
        l["votos_tipo"] = "POSITIVO"
        b = d.melt(id_vars=key, value_vars=["blancos", "nulos"], var_name="votos_tipo", value_name="v")
        b["votos_tipo"] = b.votos_tipo.map({"blancos": "EN BLANCO", "nulos": "NULO"}); b["agrupacion_id"] = "0000"
        vs.append(pd.concat([l, b]).groupby(key + ["agrupacion_id", "votos_tipo"]).v.sum())
        secs.append(d[["distrito_id", "seccion_id", "depto"]].drop_duplicates())
    votes = pd.concat(vs).reset_index(); elect = pd.concat(es)
    pd.to_pickle((votes, elect), os.path.join(HERE, "circ_%s.pkl" % arg))
    pd.concat(secs).drop_duplicates(["distrito_id", "seccion_id"]).to_csv(os.path.join(HERE, "secciones_%s.csv" % anio), index=False, encoding="utf-8-sig")
    print(arg, "circuitos", len(elect), "electores", int(elect.sum()), "votos", int(votes.v.sum()),
          "positivos", int(votes[votes.votos_tipo == "POSITIVO"].v.sum()))
    print(votes.groupby("distrito_id").v.sum().astype(int).to_dict())
