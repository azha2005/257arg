"""Provinciales bonaerenses del 7-sep-2025 por mesa -> formato largo de los atlas AMBA 2025 (como ../mapaAMBA2025/dip_amba_mesas.pkl).
    python mapas/mapaPBA2025sep/preparar.py
Entrada: datos/provinciales/pba2025/resultados_{senadores,diputados}_provinciales.csv (graficarpba, a pedido; no versionados).
Cargo legislativo unificado: cada mesa vota senadores (secciones 1.a, 4.a, 5.a, 7.a) o diputados (2.a, 3.a, 6.a, 8.a).
Mesas de nativos (X) y de extranjeros (E, solo votan provinciales): las dos entran en circuitos, partidos y secciones.
Salidas (fuera de git, se regeneran): mesas_pba.pkl (toda la provincia) y mesas_amba.pkl (los 40 partidos del AMBA).
Columnas como dip_amba_mesas.pkl: dist, sec, cir, mesa_id, mesa, part, seccion_nombre, votos_tipo, agrupacion_nombre, v, elec,
estado_final; ademas secc (seccion electoral 1-8), cargo, tipo (X/E), lk (local: '02_<sec>_<colegio>') y colegio_nombre.
La base no trae nulos (columna en 0): se informan blancos, recurridos, impugnados y comando.
"""
import os, re, unicodedata
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
SRC = os.path.join(ROOT, "datos", "provinciales", "pba2025")
COLS = ["mesa_key", "circuito_codigo", "colegio_codigo", "colegio_nombre", "seccion_electoral_codigo", "name", "votos",
        "census", "totalVotos", "blancos", "recurridos", "impugnados", "comando", "nulos"]
NUM = ["votos", "census", "totalVotos", "blancos", "recurridos", "impugnados", "comando", "nulos"]


def n(s): return re.sub(r"[^a-z ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()).strip()


G24 = "almirante brown,avellaneda,berazategui,esteban echeverria,ezeiza,florencio varela,general san martin,hurlingham,ituzaingo,jose c paz,la matanza,lanus,lomas de zamora,malvinas argentinas,merlo,moreno,moron,quilmes,san fernando,san isidro,san miguel,tigre,tres de febrero,vicente lopez".split(",")
X16 = "berisso,brandsen,campana,canuelas,ensenada,escobar,exaltacion de la cruz,general las heras,general rodriguez,la plata,lujan,marcos paz,pilar,presidente peron,san vicente,zarate".split(",")
AMBA = set(G24) | set(X16)

if __name__ == "__main__":
    d = pd.concat([pd.read_csv(os.path.join(SRC, "resultados_%s_provinciales.csv" % c), dtype=str, usecols=COLS).assign(cargo=c)
                   for c in ("senadores", "diputados")], ignore_index=True)
    for c in NUM:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    assert not d.duplicated(["mesa_key", "name"]).any()
    d["dist"] = "02"
    d["sec"] = d.mesa_key.str[2:5]
    d["mesa_id"] = d.mesa_key.str[5:10].str.lstrip("0")
    d["tipo"] = d.mesa_key.str[-1]
    d["cir"] = d.circuito_codigo.str[5:]
    d["secc"] = d.seccion_electoral_codigo.str[-1].astype(int)
    d["lk"] = "02_" + d.sec + "_" + d.colegio_codigo.str[-5:]
    # nombre del partido como la DINE (localesDeVotacionyMesas.csv), para empalmar con la geometria y los atlas de octubre
    L = pd.read_csv(os.path.join(ROOT, "datos_oficiales", "2025", "x", "localesDeVotacionyMesas.csv"), dtype=str, encoding="utf8",
                    usecols=["distrito_id", "seccion_id", "seccion_nombre"])
    secname = L[L.distrito_id == "02"].drop_duplicates("seccion_id").set_index("seccion_id").seccion_nombre.to_dict()
    assert set(d.sec) <= set(secname), set(d.sec) - set(secname)
    d["seccion_nombre"] = d.sec.map(secname)
    d["part"] = d.seccion_nombre.str.title()
    d["mesa"] = d.dist + "|" + d.sec + "|" + d.cir + "|" + d.mesa_id + "|" + d.tipo
    # mesa escrutada = tiene votantes en el provisorio (la base no trae estado de la mesa)
    m = d.drop_duplicates("mesa_key")
    m = m.assign(estado_final=(m.totalVotos > 0).map({True: "ESCRUTADO", False: "NO ESCRUTADO"}))
    keep = ["mesa_key", "dist", "sec", "cir", "mesa_id", "mesa", "part", "seccion_nombre", "secc", "cargo", "tipo", "lk", "colegio_nombre", "estado_final"]
    pos = d[keep[:-1] + ["name", "votos"]].merge(m[["mesa_key", "estado_final"]], on="mesa_key")
    pos = pos.assign(votos_tipo="POSITIVO", agrupacion_nombre=pos.name, v=pos.votos)
    otros = []
    for col, t in (("blancos", "EN BLANCO"), ("nulos", "NULO"), ("recurridos", "RECURRIDO"), ("impugnados", "IMPUGNADO"), ("comando", "COMANDO")):
        otros.append(m[keep].assign(votos_tipo=t, agrupacion_nombre=None, v=m[col]))
    out = pd.concat([pos[keep + ["votos_tipo", "agrupacion_nombre", "v"]]] + otros, ignore_index=True)
    out = out.merge(m[["mesa_key", "census"]].rename(columns={"census": "elec"}), on="mesa_key")
    out["v"] = out.v.astype(int); out["elec"] = out.elec.astype(int)
    # control: votantes = afirmativos + blancos + recurridos + impugnados + comando (la base lo define asi)
    chk = out.groupby("mesa_key").v.sum().reindex(m.mesa_key).to_numpy() - m.totalVotos.to_numpy()
    print("mesas", len(m), "| X", int((m.tipo == "X").sum()), "E", int((m.tipo == "E").sum()), "| sin votos", int((m.totalVotos == 0).sum()),
          "| diferencia maxima votantes", float(abs(chk).max()))
    out.to_pickle(os.path.join(HERE, "mesas_pba.pkl"))
    a = out[out.seccion_nombre.map(n).isin(AMBA)]
    assert a.sec.nunique() == 40, a.sec.nunique()
    a.to_pickle(os.path.join(HERE, "mesas_amba.pkl"))
    p = out[out.votos_tipo == "POSITIVO"].groupby("agrupacion_nombre").v.sum().sort_values(ascending=False)
    print("PBA positivos", int(p.sum()), "| AMBA", int(a[a.votos_tipo == "POSITIVO"].v.sum()))
    print(p.head(10).to_string())
