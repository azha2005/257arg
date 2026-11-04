"""Eleccion provincial por mesa -> proyeccion/mesas_<clave>.pkl y proyeccion/circ_<clave>.pkl (mismo formato que
bloques.py), para usarla como origen o como destino de la proyeccion:
    python proyeccion/provincial/ingestar.py pba2025
La eleccion se describe en config.ELECCIONES. Si falta el CSV de listas -> bloques, se escribe una plantilla con
las listas y sus votos (listas_plantilla.csv junto a donde va el de listas) y se corta: hay que completarla a mano con
los bloques de la tabla de la Wikipedia.
Los electores de cada mesa, si el archivo no los trae, salen del padron de diputados nacionales 2025 de la misma
mesa (mesas_2025bl.pkl); las mesas de extranjeros no tienen ese dato y quedan con sus votos como piso."""
import os, re, sys, unicodedata
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config as cf

PROY = os.path.join(HERE, "..")
KEY = ["distrito_id", "seccion_id", "circuito", "mesa_id", "mesa_tipo"]
NOPOS = {"BLANCO": "EN BLANCO", "NULO": "NULO", "OTROS": "OTROS"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


def norm_circ(c):
    c = str(c).strip().upper()
    return (c.lstrip("0") or "0") if c not in ("", "NAN", "NONE") else "0"


def ambitos(distrito):
    """seccion_id (partido o departamento de la DINE) -> nombre y seccion electoral provincial."""
    import io
    raw = open(cf.AMBITOS, "rb").read().splitlines()   # el encabezado viene en latin-1 y los nombres en UTF-8

    def dec(x):
        try:
            return x.decode("utf-8")
        except UnicodeDecodeError:
            return x.decode("latin-1")
    a = pd.read_csv(io.StringIO("\n".join(map(dec, raw))), dtype=str)
    a.columns = ["anio"] + list(a.columns[1:])
    a = a[a.distrito_id == distrito].drop_duplicates("seccion_id")
    return pd.DataFrame({"seccion_id": a.seccion_id.astype(int), "nombre": a.seccion_nombre.map(norm),
                         "unidad": pd.to_numeric(a.seccionprovincial_id, errors="coerce")})


def codigos_seccion(s, distrito):
    """Columna seccion (codigo o nombre) -> seccion_id de la DINE; corta si algun nombre no aparece."""
    num = pd.to_numeric(s, errors="coerce")
    if num.notna().all():
        return num.astype(int)
    amb = ambitos(distrito)
    mp = dict(zip(amb.nombre, amb.seccion_id))
    mp.update({norm(k): v for k, v in cf.ALIAS.get(distrito, {}).items()})
    out = s.map(norm).map(mp)
    falta = sorted(set(s[out.isna()]))
    if falta:
        raise ValueError("Secciones sin codigo DINE (agregar a ALIAS o pasar el codigo): %s" % falta[:20])
    return out.astype(int)


def tipo(df):
    t = df["tipo"].fillna("").map(norm) if "tipo" in df else pd.Series("", index=df.index)
    lst = df.lista.fillna("").map(norm)
    both = t + " " + lst
    out = pd.Series("POSITIVO", index=df.index)
    out[both.str.contains("BLANCO")] = "BLANCO"
    out[both.str.contains("NULO|ANULADO")] = "NULO"
    out[both.str.contains("RECURRIDO|IMPUGNADO|COMANDO")] = "OTROS"
    if "tipo" in df:                                    # con tipo explicito, lo que no es positivo no es lista
        out[(out == "POSITIVO") & t.ne("") & ~t.str.contains("POSITIV|VALID|AGRUPACION|LISTA")] = "OTROS"
    return out


def leer(cfg):
    for enc in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(cfg["archivo"], dtype=str, encoding=enc, sep=None, engine="python")
            break
        except UnicodeDecodeError:
            continue
    for k, val in cfg.get("filtro", {}).items():
        df = df[df[k].astype(str) == str(val)]
    df = df.rename(columns=cfg.get("columnas", {}))
    df.columns = [c.strip().lower() for c in df.columns]
    df.attrs["por_partido"] = "mesa" not in df and "circuito" not in df
    if df.attrs["por_partido"]:
        df["circuito"], df["mesa"] = "0", "0"
    falta = {"seccion", "circuito", "mesa", "lista", "votos"} - set(df.columns)
    if falta:
        raise ValueError("Faltan columnas %s; completar config.ELECCIONES[...]['columnas']. Hay: %s"
                         % (sorted(falta), list(df.columns)))
    if cfg.get("cargo") and "cargo" in df:
        df = df[df.cargo.fillna("").map(norm).str.contains(cfg["cargo"])]
    return df


def main(clave, sin_listas=False):
    cfg = cf.ELECCIONES[clave]
    prov = cf.PROVINCIAS[cfg["provincia"]]
    d = prov["distrito"]
    df = leer(cfg)
    por_partido = df.attrs["por_partido"]
    df["votos"] = pd.to_numeric(df.votos, errors="raise").fillna(0)
    df["distrito_id"] = d
    df["seccion_id"] = codigos_seccion(df.seccion, d)
    df["circuito"] = df.circuito.map(norm_circ)
    df["mesa_id"] = df.mesa.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.lstrip("0").replace("", "0")
    df["mesa_tipo"] = df.mesa_tipo.fillna("NATIVOS").str.upper() if "mesa_tipo" in df else "NATIVOS"
    df["t"] = tipo(df)
    df["lista"] = df.lista.fillna("").str.strip().str.upper()
    pos = df[df.t == "POSITIVO"]
    if not os.path.exists(cfg["listas"]) and not sin_listas:
        os.makedirs(os.path.dirname(cfg["listas"]), exist_ok=True)
        out = os.path.join(os.path.dirname(cfg["listas"]), "listas_plantilla.csv")
        p = pos.groupby("lista").votos.sum().sort_values(ascending=False).reset_index()
        p["bloque"] = ""
        p[["lista", "bloque", "votos"]].to_csv(out, index=False, encoding="utf-8-sig")
        sys.exit("Falta %s: escrita la plantilla %s (completar la columna bloque)" % (cfg["listas"], out))
    if sin_listas:
        mp, sin = {}, set()
        df["col"] = np.where(df.t == "POSITIVO", df.lista, df.t)
    else:
        L = pd.read_csv(cfg["listas"], dtype=str, encoding="utf-8-sig").fillna("")
        L["lista"] = L.lista.str.strip().str.upper()
        L["bloque"] = L.bloque.str.strip().replace("", "OTRAS")
        por_sec = {(int(r.seccion), r.lista): r.bloque for r in L.itertuples() if "seccion" in L and r.seccion}
        gen = {r.lista: r.bloque for r in L.itertuples() if not ("seccion" in L and r.seccion)}
        b = [por_sec.get((s, l), gen.get(l)) for s, l in zip(df.seccion_id, df.lista)]
        df["col"] = np.where(df.t == "POSITIVO", pd.Series(b, index=df.index).fillna("OTRAS"), df.t)
        sin = set(pos.lista) - set(gen) - {l for _, l in por_sec}
    w = df.groupby(KEY + ["col"]).votos.sum().unstack("col", fill_value=0).reset_index()
    w.columns.name = None
    fixed = [c for c in NOPOS if c in w]
    blocs = [c for c in w.columns if c not in KEY + fixed]
    nota = []
    if "electores" in df:
        e = df.assign(e=pd.to_numeric(df.electores, errors="coerce")).groupby(KEY).e.max()
        w = w.merge(e.reset_index(), on=KEY, how="left")
    else:
        w["e"] = np.nan
    if w.e.isna().any() and not por_partido:
        nac = pd.read_pickle(os.path.join(PROY, "mesas_2025bl.pkl"))
        nac = nac[nac.distrito_id == d][KEY[:-1] + ["e"]].rename(columns={"e": "e_nac"})
        w = w.merge(nac, on=KEY[:-1], how="left")
        miss = w.e.isna()
        w.loc[miss, "e"] = w.loc[miss, "e_nac"]
        nota.append("electores del padron nacional 2025 en %d mesas" % int((miss & w.e_nac.notna()).sum()))
        w = w.drop(columns="e_nac")
    vot = w[blocs + fixed].sum(1)
    sinpad = w.e.isna() | (w.e < vot)
    if sinpad.any():
        nota.append("%d mesas sin padron o con mas votos que electores: e = votos" % int(sinpad.sum()))
        w.loc[sinpad, "e"] = vot[sinpad]
    w = w[KEY + ["e"] + fixed + blocs]
    mp = os.path.join(PROY, "mesas_%s.pkl" % clave)
    if por_partido:            # sin mesas: no hay electores por mesa que dar (el motor usaria el partido entero)
        nota.append("archivo por partido: sin mesas_%s.pkl; las actas se comparan con su partido" % clave)
        if os.path.exists(mp):
            os.remove(mp)
    else:
        w.to_pickle(mp)
    k = ["distrito_id", "seccion_id", "circuito"]
    c = w.groupby(k)[blocs + fixed + ["e"]].sum()
    elect = c.pop("e").rename("e")
    v = c.stack().rename("v").reset_index().rename(columns={"level_3": "col"})
    v["agrupacion_id"] = np.where(v.col.isin(blocs), v.col, "")
    v["votos_tipo"] = v.col.map(NOPOS).fillna("POSITIVO")
    pd.to_pickle((v[k + ["agrupacion_id", "votos_tipo", "v"]], elect), os.path.join(PROY, "circ_%s.pkl" % clave))
    t = w[blocs].sum()
    print(clave, "mesas", len(w), "circuitos", len(elect), "electores", int(w.e.sum()), "votos", int(vot.sum()))
    print("bloques %", (100 * t / t.sum()).round(2).sort_values(ascending=False).to_dict())
    if sin:
        print("listas sin bloque (van a OTRAS):", sorted(sin)[:30])
    for n in nota:
        print("nota:", n)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for a in args:
        main(a, sin_listas="--sin-listas" in sys.argv)
