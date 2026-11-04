"""Tabla ancha por mesa (provisorio DINE) para las pruebas de proyeccion -> proyeccion/mesas_<arg>.pkl
    python proyeccion/mesas.py 2023p 2023b            # presidente 2023, 1.a vuelta y balotaje
    python proyeccion/mesas.py 2015p 2015b 2023 2025  # sin sufijo = diputados nacionales
Columnas: distrito_id, seccion_id, circuito, mesa_id, mesa_tipo, e (electores) y una columna de votos por
agrupacion (nombre en mayusculas) mas BLANCO, NULO y OTROS (recurridos, impugnados, comando).
En diputados la agrupacion es el nombre de la lista de cada distrito; para comparar entre distritos hay que
llevarla a bloques (mapas/mapa<anio>/mapeo_listas_<anio>.csv)."""
import os, sys
import pandas as pd
OUT = os.path.dirname(os.path.abspath(__file__))
KEY = ["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]


def src(arg):
    import glob
    root = os.path.join(OUT, "..")
    anio = arg.rstrip("pb")
    d = os.path.join(root, "datos_oficiales", anio + "_balotaje" if arg.endswith("b") else anio, "x")
    return (glob.glob(os.path.join(d, "*", "Resultado*.csv")) + glob.glob(os.path.join(d, "resultados*.csv")))[0]


def tipo(t, nombre):
    t = t.fillna("").str.upper()
    return pd.Series(pd.NA, index=t.index, dtype=object).mask(t.str.startswith("POSITIVO"), nombre) \
        .mask(t.str.contains("BLANCO"), "BLANCO").mask(t.str.contains("NULO"), "NULO").fillna("OTROS")


for arg in sys.argv[1:] or ["2023p", "2023b"]:
    pres = arg.endswith(("p", "b"))
    parts = []
    for ch in pd.read_csv(src(arg), dtype=str, chunksize=1_500_000, encoding="utf-8", low_memory=False):
        ch.columns = [c.lower() for c in ch.columns]
        ch = ch[ch.cargo_nombre.fillna("").str.upper().str.contains("PRESIDENTE" if pres else "DIPUTAD.*NACIONAL")].copy()
        if ch.empty: continue
        ch["v"] = pd.to_numeric(ch.votos_cantidad, errors="coerce").fillna(0)
        ch["e"] = pd.to_numeric(ch.mesa_electores, errors="coerce").fillna(0)
        ch["distrito_id"] = ch.distrito_id.astype(int).map("{:02d}".format)
        ch["seccion_id"] = ch.seccion_id.astype(int)
        ch["circuito"] = ch.circuito_id.fillna("").str.strip().str.upper().str.lstrip("0").replace("", "0")
        ch["mesa_id"] = ch.mesa_id.astype(str).str.strip()
        ch["col"] = tipo(ch.votos_tipo, ch.agrupacion_nombre.fillna("").str.strip().str.upper())
        parts.append(ch.groupby(KEY + ["e", "col"]).v.sum())
    s = pd.concat(parts)
    s = s.groupby(level=list(range(len(s.index.names)))).sum()
    w = s.unstack("col", fill_value=0).reset_index()
    w = w.groupby(KEY).agg({c: ("max" if c == "e" else "sum") for c in w.columns if c not in KEY}).reset_index()
    w.columns.name = None
    w.to_pickle(os.path.join(OUT, "mesas_%s.pkl" % arg))
    vot = w.drop(columns=KEY + ["e"]).sum(axis=1)
    print(arg, "mesas", len(w), "con votos", int((vot > 0).sum()), "electores", int(w.e.sum()), "votos", int(vot.sum()),
          "columnas", [c for c in w.columns if c not in KEY], flush=True)
