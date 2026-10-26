"""Agrega los provisorios por mesa de la DINE (diputados nacionales) por circuito electoral -> transferencias/circ_<anio>.pkl
    python transferencias/agregar_circuitos.py 2021 2023 2025
    python transferencias/agregar_circuitos.py 2019p 2023p      # presidente -> circ_<anio>p.pkl
    python transferencias/agregar_circuitos.py 2023b            # balotaje 2023 -> circ_2023b.pkl
    python transferencias/agregar_circuitos.py 2023pp           # PASO presidencial 2023, por lista -> circ_2023pp.pkl
En presidente, agrupacion_id guarda el nombre de la agrupacion (es el mismo en todos los distritos).
Salida: (votos, electores). votos = suma por (distrito, seccion, circuito, agrupacion, tipo de voto);
electores = suma de mesa_electores de las mesas que tienen algun voto para el cargo (las no escrutadas no cuentan)."""
import os, glob, sys
import pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.dirname(os.path.abspath(__file__))


def src(arg):
    """2023b = segunda vuelta 2023 (datos_oficiales/2023_balotaje/); 2023pp = PASO 2023, leida del zip sin extraer (3,7 GB)."""
    if arg == "2023pp":
        import zipfile
        return zipfile.ZipFile(os.path.join(ROOT, "datos_oficiales", "2023_paso", "2023-PROVISORIOS_PASO.zip")).open("2023_PASO/ResultadosElectorales.csv")
    anio = arg.rstrip("pb")
    d = os.path.join(ROOT, "datos_oficiales", anio + "_balotaje" if arg.endswith("b") else anio, "x")
    return (glob.glob(os.path.join(d, "*", "Resultado*.csv")) + glob.glob(os.path.join(d, "resultados*.csv")))[0]


def circ(s):
    """Codigo de circuito normalizado: 2021/2023 vienen '00221', 2025 tambien; se quitan ceros a la izquierda."""
    s = s.fillna("").str.strip().str.upper()
    return s.str.lstrip("0").replace("", "0")


for arg in sys.argv[1:] or ["2021", "2023", "2025"]:
    anio, pres = arg.rstrip("pb"), arg.endswith(("p", "b"))
    vs, ms = [], []
    for ch in pd.read_csv(src(arg), dtype=str, chunksize=1_500_000, encoding="utf-8", low_memory=False):
        ch.columns = [c.lower() for c in ch.columns]
        ch = ch[ch.cargo_nombre.fillna("").str.upper().str.contains("PRESIDENTE" if pres else "DIPUTAD.*NACIONAL")].copy()
        if ch.empty: continue
        ch["v"] = pd.to_numeric(ch.votos_cantidad, errors="coerce").fillna(0)
        ch["distrito_id"] = ch.distrito_id.astype(int).map("{:02d}".format)
        ch["seccion_id"] = ch.seccion_id.astype(int)
        ch["circuito"] = circ(ch.circuito_id)
        if arg == "2023pp":    # PASO: agrupacion | lista (Massa y Grabois, Bullrich y Larreta por separado)
            ch["agrupacion_id"] = ch.agrupacion_nombre.fillna("").str.strip().str.upper() + " | " + ch.lista_nombre.fillna("").str.strip().str.upper()
        elif pres:
            ch["agrupacion_id"] = ch.agrupacion_nombre.fillna("").str.strip().str.upper()
        else:
            ch["agrupacion_id"] = ch.agrupacion_id.fillna("").str.strip().str.zfill(4)
        key = ["distrito_id", "seccion_id", "circuito", "agrupacion_id", "votos_tipo"]
        vs.append(ch.groupby(key, dropna=False).v.sum())
        m = ch.groupby(["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]).agg(e=("mesa_electores", "first"), v=("v", "sum")).reset_index()
        ms.append(m)
    votes = pd.concat(vs).groupby(level=list(range(5)), dropna=False).sum().reset_index()
    mesas = pd.concat(ms).groupby(["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]).agg(e=("e", "first"), v=("v", "sum")).reset_index()
    mesas["e"] = pd.to_numeric(mesas.e, errors="coerce").fillna(0)
    elect = mesas[mesas.v > 0].groupby(["distrito_id", "seccion_id", "circuito"]).e.sum()
    pd.to_pickle((votes, elect), os.path.join(OUT, "circ_%s.pkl" % arg))
    print(arg, "circuitos", len(elect), "electores", int(elect.sum()), "votos", int(votes.v.sum()),
          "tipos", sorted(votes.votos_tipo.unique()), "mesa_tipo", sorted(mesas.mesa_tipo.unique()),
          "mesas sin votos", int((mesas.v == 0).sum()), flush=True)
