"""Base departamental para el escenario Kicillof - Milei: balotaje 2023 (Milei - Massa) por unidad del mapa.
Fuente: xlsx_resultados/por_eleccion/2023_presidente_balotaje.xlsx (escrutinio provisorio, DINE). Escribe base27kic.pkl."""
import os, sys, pickle
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from names import norm
import prep27 as P

PN = {norm(p): p for p in set(P.D2P.values())}
PN[norm("Ciudad Autonoma De Buenos Aires")] = "Capital Federal"
MANUAL = {("Buenos Aires", "coronelDemarinaleonardorosales"): None}
wb = openpyxl.load_workbook(os.path.join(HERE, "..", "../resultados_xlsx", "por_eleccion", "2023_presidente_balotaje.xlsx"), read_only=True)
rows = list(wb["resultados"].iter_rows(values_only=True))[1:]
res = {}
for r in rows:
    prov, nm, bla, imp, vot, ele, mil, uxp = r
    p = PN[norm(prov)]
    n = norm(str(nm))
    if p == "Capital Federal":
        i = P.IDX[(p, n)]
    elif p == "Tierra del Fuego" and n.startswith("antartida"):
        i = P.IDX[(p, norm("Ushuaia"))]
    elif p == "Buenos Aires" and "rosales" in n:
        i = P._find(p, "rosales")
    elif p == "Jujuy" and "manuelbelgrano" in n:
        i = P._find(p, "manuelbelgrano")
    elif p == "Tucumán" and n.startswith("famail"):
        i = P._find(p, "famal")
    else:
        i = P.IDX.get((p, n))
        if i is None:
            for (pp, frag), (p2, tgt) in P.ALIAS_FRAG.items():
                if pp == p and frag in n:
                    i = P._find(p2, tgt)
    assert i is not None, (prov, nm)
    e = res.setdefault(i, dict(mil=0, uxp=0, bla=0, nul=0, vot=0, ele=0))
    for k, v in (("mil", mil), ("uxp", uxp), ("bla", bla), ("nul", imp), ("vot", vot), ("ele", ele)):
        e[k] += int(v or 0)
# Unidades sin mesas en el balotaje 2023 de la base pero con generales 2023 (DINE): se estima el balotaje desde las generales
# con traspasos nacionales (JxC -> 85 % Milei / 10 % Massa, Hacemos -> 35 % / 45 %, FIT-U -> 15 % / 50 %; el resto, abstencion).
G = pickle.load(open(os.path.join(HERE, "..", "mapa2027", "base27.pkl"), "rb"))["g23"]
TR = dict(jxc=(0.85, 0.10), hxnp=(0.35, 0.45), fit=(0.15, 0.50))
K = {"JUNTOS POR EL CAMBIO": "jxc", "HACEMOS POR NUESTRO PAIS": "hxnp", "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "fit"}
est = []
for i, u in enumerate(P.U):
    if u["name"] == "Islas Malvinas" or i in res and res[i]["mil"] + res[i]["uxp"] > 0:
        continue
    g = G[i]["P"]
    m = g.get("LA LIBERTAD AVANZA", 0); x = g.get("UNION POR LA PATRIA", 0)
    for name, k in K.items():
        m += g.get(name, 0) * TR[k][0]; x += g.get(name, 0) * TR[k][1]
    res[i] = dict(mil=int(round(m)), uxp=int(round(x)), bla=0, nul=0, vot=0, ele=0, est=True)
    est.append((u["prov"], u["name"], res[i]["mil"], res[i]["uxp"]))
print("estimadas desde generales 2023:", est)
miss = [(u["prov"], u["name"]) for i, u in enumerate(P.U) if u["name"] != "Islas Malvinas" and i not in res]
print("sin dato:", miss)
print("Milei", sum(e["mil"] for e in res.values()), "UxP", sum(e["uxp"] for e in res.values()))
pickle.dump(dict(U=[(u["prov"], u["name"], u["kind"]) for u in P.U], bal=res), open(os.path.join(HERE, "base27kic.pkl"), "wb"))
