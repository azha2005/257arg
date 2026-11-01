"""Geolocaliza los locales de votacion del AMBA 2025 (localesDeVotacionyMesas.csv de la DINE, sin coordenadas).
Fuentes, por orden de preferencia, siempre validadas contra el poligono del circuito de sus mesas:
  0. padrones oficiales de escuelas con coordenadas (escuelas.py: DGCyE PBA y Ministerio de Educacion GCBA), como LN Data / Poblaciones;
  1. georef (apis.datos.gob.ar, API oficial de normalizacion de direcciones) con la direccion del local;
  2. puntos de establecimientos de La Nacion 2021 (galeano_snapshot_2021/establecimientos-ln.geojson) emparejados por nombre y direccion;
  3. variantes de la direccion para georef (primera palabra de la calle + altura; interseccion).
Un punto que cae fuera del circuito de sus mesas (con 300 m de tolerancia) no se usa; el local sin punto valido va al
punto representativo de su circuito (se anota). Salida: locales_amba2025.csv. Se corre una vez (consulta la API).
"""
import os, re, json, time, unicodedata, difflib, sys
import pandas as pd, numpy as np, requests, shapely
from shapely.geometry import Point
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "mapas", "mapaAMBA2025"))
# copia de circuitos_electorales_AR (2021) que usa el atlas por circuito
os.environ.setdefault("CIRCUITOS_AR_GEOJSON", os.path.join(ROOT, "geometria", "circuitos_busqueda", "galeano_snapshot_2021", "geojson"))
import geomamba

UA = {"User-Agent": "dataeleccproyecto atlas AMBA 2025 por radio"}


def n(s):
    s = unicodedata.normalize("NFD", str(s).upper()).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9 ]", " ", s)


def nn(s): return re.sub(r"\s+", " ", n(s)).strip()


def clean_dir(s):
    s = str(s).replace("N°", " ").replace("Nº", " ").replace("N\xb0", " ").replace("N\xba", " ")
    s = re.sub(r"\bN\s*\W\s*(?=\d)", " ", s)
    s = re.split(r"\bENTRE\b(?!\s+RIOS)", s)[0]
    s = re.sub(r"\bE/\s*", " entre ", s)
    s = re.sub(r"\bESQ\.?\b", " y ", s)
    s = re.sub(r"\b(S/N|SN|S/NRO|BIS)\b", " ", s)
    s = re.sub(r"\(.*?\)", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def variant2(s):
    """primera palabra de la calle + altura: «CALDERON MANUEL GRAL.BRIG. 295» -> «CALDERON 295»"""
    c = clean_dir(s); m = re.search(r"(\d+)\s*$", c)
    if not m or re.search(r"\bentre\b(?!\s+RIOS)", c): return None
    w = c[:m.start()].split()
    return ("%s %s" % (w[0], m.group(1))) if w else None


# ---------------------------------------------------------------- locales y circuitos de sus mesas
d, feats, target = geomamba.load()
mes = d.drop_duplicates("mesa")[["dist", "sec", "cir", "mesa_id", "elec"]].copy()
mes["mid5"] = mes.mesa_id.str.zfill(5)
L = pd.read_csv(os.path.join(ROOT, "datos_oficiales", "2025", "x", "localesDeVotacionyMesas.csv"), dtype=str, encoding="utf8")
L = L[L.distrito_id.isin(["01", "02"])]
L = L.merge(mes, left_on=["distrito_id", "seccion_id", "mesa_id"], right_on=["dist", "sec", "mid5"], how="inner", suffixes=("", "_r"))
L["lk"] = L.distrito_id + "_" + L.seccion_id + "_" + L.localvotacion_codigo
loc = L.groupby("lk").agg(dist=("distrito_id", "first"), sec=("seccion_id", "first"), sn=("seccion_nombre", "first"),
                          nom=("localvotacion_nombre", "first"), dir=("localvotacion_direccion", "first"), lo=("localvotacion_localidad", "first"),
                          mesas=("mesa_id", "size"), elec=("elec", "sum")).reset_index()
cirs = L.groupby("lk").cir.agg(lambda s: sorted(set(s))).to_dict()
loc["cirs"] = loc.lk.map(cirs)
print(len(loc), "locales,", len(L), "mesas", file=sys.stderr)


def circ_poly(r):
    gs = [shapely.make_valid(feats[target[(r.dist, r.sec, c)]]) for c in r.cirs if target.get((r.dist, r.sec, c))]
    return shapely.union_all(gs) if gs else None


CP = {r.lk: circ_poly(r) for r in loc.itertuples()}
TOL = 300 / 111000   # 300 m en grados (aprox.)


def inside(lk, lon, lat):
    g = CP.get(lk)
    if g is None or lon is None or not np.isfinite(lon): return False
    return g.buffer(TOL).contains(Point(lon, lat))


# partido (comuna en Capital) = union de los circuitos de sus mesas en la capa 2021
PP = {}
for (a, b, c), t in target.items():
    if t: PP.setdefault((a, b), []).append(shapely.make_valid(feats[t]))
PP = {k: shapely.union_all(v).buffer(TOL) for k, v in PP.items()}


def dist_circ(lk, lon, lat):
    """metros del punto al circuito de sus mesas (inf si no hay poligono o el punto esta fuera del partido)"""
    g = CP.get(lk); dist, sec = lk.split("_")[:2]
    if lon is None or not np.isfinite(lon) or not PP[(dist, sec)].contains(Point(lon, lat)): return np.inf
    if g is None: return 0.0   # circuito sin poligono (548 de Gral. Las Heras): alcanza con el partido
    return g.distance(Point(lon, lat)) * 100000


# ---------------------------------------------------------------- georef
def dep_name(r):
    if r.dist == "01": return "Comuna %d" % int(re.sub(r"\D", "", r.sn) or 0)
    return r.sn.title()


CACHE = os.path.join(HERE, "georef_cache.json")
cache = json.load(open(CACHE, encoding="utf8")) if os.path.exists(CACHE) else {}


def _post(chunk):
    for t in range(6):
        r = requests.post("https://apis.datos.gob.ar/georef/api/direcciones", json={"direcciones": chunk}, headers=UA, timeout=180)
        if r.status_code in (200, 400): break
        time.sleep(5 * (t + 1))
    if r.status_code == 400:   # alguna direccion invalida en el lote: se parte hasta aislarla
        if len(chunk) == 1: return [{}]
        h = len(chunk) // 2
        return _post(chunk[:h]) + _post(chunk[h:])
    r.raise_for_status()
    return r.json()["resultados"]


def georef(reqs):
    todo = list({json.dumps(q, sort_keys=True): q for q in reqs if json.dumps(q, sort_keys=True) not in cache}.values())
    for i in range(0, len(todo), 500):
        chunk = todo[i:i + 500]
        for q, res in zip(chunk, _post(chunk)):
            ds = res.get("direcciones") or []
            x = ds[0] if ds else {}   # respuesta aplanada: ubicacion_lon, departamento_nombre...
            cache[json.dumps(q, sort_keys=True)] = dict(lon=x.get("ubicacion_lon"), lat=x.get("ubicacion_lat"), dep=x.get("departamento_nombre"), nom=x.get("nomenclatura"))
        json.dump(cache, open(CACHE, "w", encoding="utf8"), ensure_ascii=False)
        print("georef", i + len(chunk), "/", len(todo), file=sys.stderr)
        time.sleep(1)
    return [cache[json.dumps(q, sort_keys=True)] for q in reqs]


def q_of(r, addr):
    return dict(direccion=addr, provincia="02" if r.dist == "01" else "06", departamento=dep_name(r), max=1, aplanar=True)


# padrones oficiales de escuelas (fuente principal, como LN Data / Poblaciones); georef solo para los locales sin escuela valida
import escuelas
ESC = escuelas.load()
esm = [escuelas.match(r.dist, r.sn, r.nom, r.dir, ESC) for r in loc.itertuples()]
need = [not (e and dist_circ(r.lk, e[1], e[2]) <= 300) for r, e in zip(loc.itertuples(), esm)]
g1 = georef([q_of(r, clean_dir(r.dir)) for r, nd in zip(loc.itertuples(), need) if nd])
it1 = iter(g1); g1 = [next(it1) if nd else {} for nd in need]
v2 = [variant2(r.dir) if nd else None for r, nd in zip(loc.itertuples(), need)]
g2 = georef([q_of(r, a) for r, a in zip(loc.itertuples(), v2) if a])
it2 = iter(g2); g2 = [next(it2) if a else {} for a in v2]

# ---------------------------------------------------------------- La Nacion 2021
ln = json.load(open(os.path.join(ROOT, "geometria", "circuitos_busqueda", "galeano_snapshot_2021", "establecimientos-ln.geojson"), encoding="utf8"))
LN = {}
for f in ln["features"]:
    p = f["properties"]
    if p["id_distrito"] not in (1, 2): continue
    LN.setdefault(("%02d" % p["id_distrito"], "%03d" % p["id_seccion"]), []).append((nn(p["nombre"]), nn(p["direccion"]), f["geometry"]["coordinates"]))


def num(s):
    m = re.findall(r"\d+", s); return m[-1] if m else None


def ln_match(r):
    best = (0, None)
    nm, ad = nn(r.nom), nn(clean_dir(r.dir))
    for a, b, c in LN.get((r.dist, r.sec), []):
        sn = difflib.SequenceMatcher(None, nm, a).ratio(); sa = difflib.SequenceMatcher(None, ad, b).ratio()
        same_num = num(ad) is not None and num(ad) == num(b)
        sc = 0.5 * sn + 0.5 * sa + (0.2 if same_num else 0)
        if sc > best[0]: best = (sc, c)
    return best


lnm = [ln_match(r) for r in loc.itertuples()]


# ---------------------------------------------------------------- eleccion del punto
rows = []
for r, a, b, (lsc, lc), e in zip(loc.itertuples(), g1, g2, lnm, esm):
    cand = [e] if e else []
    if lc is not None and lsc >= 0.75: cand.append(("lanacion2021", lc[0], lc[1]))
    if a.get("lon") is not None: cand.append(("georef", a["lon"], a["lat"]))
    if b.get("lon") is not None: cand.append(("georef_variante", b["lon"], b["lat"]))
    # 1) el primero que cae en su circuito (300 m de tolerancia); 2) si ninguno, el primero dentro del partido y a menos de 1,5 km del circuito
    #    (la capa de circuitos es de 2021 y en algunos lugares esta corrida o cambio)
    dc = [dist_circ(r.lk, x, y) for s, x, y in cand]
    pick = next(((s, x, y) for (s, x, y), dd in zip(cand, dc) if dd <= 300), None)
    if pick is None:
        pick = next(((s + "_cerca", x, y) for (s, x, y), dd in zip(cand, dc) if dd <= 1500), None)
    if pick is None:
        g = CP.get(r.lk)
        p = g.representative_point() if g is not None else None
        pick = ("centro_circuito", p.x, p.y) if p is not None else ("sin_punto", np.nan, np.nan)
        outside = ";".join(s for s, _, _ in cand)
    else:
        outside = ""
    rows.append(dict(lk=r.lk, dist=r.dist, sec=r.sec, seccion=r.sn, codigo=r.lk[-5:], nombre=r.nom, direccion=r.dir, localidad=r.lo,
                     mesas=r.mesas, electores=int(r.elec), circuitos=" ".join(r.cirs), fuente=pick[0], lon=pick[1], lat=pick[2],
                     candidatos_fuera_del_circuito=outside, escuela_rechazada=(e[0] if e and not pick[0].startswith(e[0]) else ""), metros_al_circuito=round(min(dc), 0) if dc else None, ln_score=round(lsc, 3), georef_nomenclatura=a.get("nom")))
out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "locales_amba2025.csv"), index=False, encoding="utf8")
print(out.fuente.value_counts().to_string(), file=sys.stderr)
print("electores por fuente:", (out.groupby("fuente").electores.sum() / out.electores.sum()).round(4).to_dict(), file=sys.stderr)
