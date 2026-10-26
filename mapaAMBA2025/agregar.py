"""Agrega los votos de diputados nacionales 2025 (provisorio por mesa, datos.mininterior.gob.ar) por circuito del AMBA.
Salida: circuitos_amba.pkl con una fila por unidad (circuito o circuito + subdivisiones) y su geometria."""
import json, re, unicodedata, pickle, os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
d = pd.read_pickle(os.path.join(ROOT, "datos_oficiales", "2025", "dip_amba_mesas.pkl"))
d["dist"] = d.distrito_id.str.zfill(2)

def n(s): return re.sub(r"[^a-z ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()).strip()
G24 = "almirante brown,avellaneda,berazategui,esteban echeverria,ezeiza,florencio varela,general san martin,hurlingham,ituzaingo,jose c paz,la matanza,lanus,lomas de zamora,malvinas argentinas,merlo,moreno,moron,quilmes,san fernando,san isidro,san miguel,tigre,tres de febrero,vicente lopez".split(",")
X16 = "berisso,brandsen,campana,canuelas,ensenada,escobar,exaltacion de la cruz,general las heras,general rodriguez,la plata,lujan,marcos paz,pilar,presidente peron,san vicente,zarate".split(",")
AMBA = set(G24) | set(X16)
d["pn"] = d.seccion_nombre.map(n)
d = d[(d.dist == "01") | (d.pn.isin(AMBA))].copy()
d["part"] = d.apply(lambda r: "CABA" if r.dist == "01" else r.seccion_nombre.title(), axis=1)
d["sec"] = d.seccion_id.str.zfill(3)
d["cir"] = d.circuito_id
d["v"] = pd.to_numeric(d.votos_cantidad, errors="coerce").fillna(0)
d["elec"] = pd.to_numeric(d.mesa_electores, errors="coerce").fillna(0)
d["mesa"] = d.dist + "|" + d.sec + "|" + d.cir + "|" + d.mesa_id
d.to_pickle(os.path.join(HERE, "dip_amba_mesas.pkl"))
print(d.part.nunique(), "ambitos;", d.groupby(["dist", "sec", "cir"]).ngroups, "circuitos;", d.mesa.nunique(), "mesas")
