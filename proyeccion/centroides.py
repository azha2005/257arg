"""Centroide (lon, lat) de cada seccion electoral de la DINE -> proyeccion/centroides_secciones.csv
    python proyeccion/centroides.py
Empareja las secciones de 2023 con los poligonos del atlas legislativo (departamentos 2010 + comunas) por nombre,
con los mismos alias que comun/leg2003_2025_data.py. Solo lo usa el metodo A de backtest.py para elegir donantes."""
import os, sys, pickle
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "comun"))
import leg2003_2025_data as L

U = pickle.load(open(os.path.join(HERE, "..", "mapas", "mapa2023", "units_leg2003_2025.pkl"), "rb"))
U = U[0] if isinstance(U, tuple) else U
idx = {(u["prov"], L.norm(u["name"])): u for u in U if u["name"] != "Islas Malvinas"}
amb = pd.read_csv(os.path.join(HERE, "..", "datos_oficiales", "2023", "x", "2023_Generales", "AmbitosElectorales_2023_Generales.csv"), dtype=str)
amb = amb.drop_duplicates(["distrito_id", "seccion_id"])
rows, miss = [], []
for r in amb.itertuples():
    d, s = "%02d" % int(r.distrito_id), int(r.seccion_id)
    p = L.D2P.get(d)
    if p is None: continue
    if p == "Capital Federal":
        key = (p, L.norm("Comuna %d" % s))
    else:
        nn = L.norm(str(r.seccion_nombre))
        key = (p, nn) if (p, nn) in idx else (p, L.PROV_ALIASES.get((p, nn), L.ALIASES.get(nn, nn)))
    u = idx.get(key)
    if u is None:
        miss.append((d, s, r.seccion_nombre)); continue
    c = u["geom"].representative_point() if "geom" in u else None
    lon, lat = (c.x, c.y) if c is not None else (None, None)
    rows.append(dict(distrito_id=d, seccion_id=s, seccion_nombre=r.seccion_nombre, lon=lon, lat=lat))
pd.DataFrame(rows).to_csv(os.path.join(HERE, "centroides_secciones.csv"), index=False, encoding="utf-8")
print("secciones", len(rows), "sin poligono", len(miss), miss[:20])
