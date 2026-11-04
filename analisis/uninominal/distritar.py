"""Distritos uninominales por provincia con Mosaic (radios censales por defecto; UNI_SHP=shp UNI_PLAN=plan
para la version por circuitos) (ReCom + recocido), sin la interfaz grafica.
    <python de Mosaic> analisis/uninominal/distritar.py [--reparto c257_sin_garantia] [--iter 4000] [dd ...]
Lee shp_radios/<dd>_*.shp (de construir_radios.py) y reparto.csv. --modo:
  neutral       aristas cortadas, departamentos partidos, compacidad (Polsby-Popper) y desvio de poblacion; sin
                peso partidario (las elecciones solo se miran despues).
  proporcional  lo mismo + bancas peronistas esperadas = bancas x porcentaje peronista de la provincia
                (peso 30 y temperatura inicial baja, como los gerrymanders).
  peronista/lla gerrymander: bancas peronistas esperadas -> todas / ninguna, con compacidad y departamentos
                a un vigesimo del peso y aristas a 0,2; el peso de las bancas es 30.
La eleccion guia de los modos partidarios es balotaje 2023 + diputados 2025 sumados. Mayoria simple entre
los dos bloques. Salida en plan_radios[_<modo>][_deptos]/.
--deptos: cada departamento con menos poblacion que un distrito es una sola unidad (no se parte); los mas
grandes quedan en radios y se cortan. Ademas departamentos partidos con peso x20 y sesgo de ReCom 20 (en
vez de 2). Pensado para mapas mas legibles y comunidades de interes, en los cuatro modos.
Salida: plan_radios/<dd>.csv (circuito -> distrito), plan/<dd>_distritos.csv y plan/resumen.csv.
El grafo, con las islas unidas al circuito mas cercano, se copia a cache/ de Mosaic para que la
interfaz abra el mismo grafo."""
import os, sys, glob, csv, argparse, pickle, time
from multiprocessing import Pool
import numpy as np, pandas as pd, geopandas as gpd, networkx as nx
HERE = os.path.dirname(os.path.abspath(__file__))
MOSAIC = os.environ.get("MOSAIC", r"C:\Users\JC\Desktop\Escritorio 26\mosaic_python-main")
sys.path.insert(0, os.path.join(MOSAIC, "src"))
from mosaic.graph import build_adjacency_graph
from mosaic.recom import create_initial_partition
from mosaic.recom.recombination import recom_step_ig, GraphContext
from mosaic.recom.annealing import AnnealingConfig, init_annealing, accept_proposal, cool_temperature
from mosaic.scoring import ScoreConfig, score_plan, precompute_pp_data
from mosaic.gui.runner import nx_to_igraph
DEBUG = os.environ.get("UNI_DEBUG")
TEMP_G = float(os.environ.get("UNI_TEMP", 0.002))  # temperatura inicial de los gerrymanders (fraccion del puntaje)
BUF = float(os.environ.get("UNI_BUF", 20))
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"
ELEC = ("23", "23b", "25")
SHP, PLAN = os.environ.get("UNI_SHP", "shp_radios"), os.environ.get("UNI_PLAN", "plan_radios")


def grafo(gdf):
    """Grafo de Mosaic con los poligonos engordados BUF m (la capa tiene rendijas entre circuitos
    vecinos); lo que quede suelto (islas) se une a la componente mas cercana."""
    gb = gdf.copy()
    gb["geometry"] = gdf.geometry.buffer(BUF)
    G = build_adjacency_graph(gb)
    for k in G.nodes: G.nodes[k]["geometry"] = gdf.geometry.iloc[k]
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    unidas = 0
    while len(comps) > 1:
        chica = comps.pop()
        resto = set().union(*comps)
        gs = gdf.geometry
        a = gs.loc[list(chica)].union_all()
        cand = gdf.loc[list(resto)]
        dist = cand.geometry.distance(a)
        j = dist.idxmin()
        i = gs.loc[list(chica)].distance(gs.loc[j]).idxmin()
        G.add_edge(int(i), int(j))
        unidas += 1
        comps = sorted(nx.connected_components(G), key=len, reverse=True)
    return G, unidas


def desde_plan_libre(rad, unidad, G, n, plan, d):
    """Plan inicial para --deptos: el plan del mismo modo con limites libres (ya balanceado), con cada
    departamento chico entero en el distrito que tiene mas poblacion suya; los pedazos que queden sueltos
    pasan al distrito vecino con mas aristas en comun."""
    f = os.path.join(HERE, plan.replace("_deptos", ""), f"{d}.csv")
    if not os.path.exists(f):
        return None
    p = pd.read_csv(f, dtype={"pid": str}).set_index("pid").distrito.reindex(rad.pid).values - 1
    w = rad.population.values + 1e-3
    tab = pd.DataFrame({"u": unidad, "d": p, "w": w}).groupby(["u", "d"]).w.sum().reset_index()
    a = tab.sort_values("w").drop_duplicates("u", keep="last").set_index("u").d.reindex(range(unidad.max() + 1)).values
    a = a.astype(int)
    for _ in range(50):
        cambio = False
        for k in range(n):
            nodos = np.flatnonzero(a == k)
            if len(nodos) == 0: return None
            comps = sorted(nx.connected_components(G.subgraph(nodos)), key=len, reverse=True)
            for c in comps[1:]:
                vec = [a[v] for u in c for v in G.neighbors(u) if a[v] != k]
                if vec:
                    a[list(c)] = max(set(vec), key=vec.count); cambio = True
        if not cambio: return a
    return None


def correr(args):
    """Con --deptos prueba primero con todo departamento mas chico que un distrito entero; si no llega a la
    tolerancia, solo los de menos de medio distrito, despues de un cuarto, y al final ninguno (solo el peso
    y el sesgo de ReCom; \"cortar si hace falta\")."""
    if not args[7]:
        return _correr(args, 0)
    for frac in (1.0, 0.5, 0.25, 0.0):  # 0 = solo radios (parte del plan libre, siempre factible)
        r = _correr(args, frac)
        if "error" not in r: break
    return r


def _correr(args, frac):
    d, n, iters, tol, seed, modo, plan, deptos = args
    bias = float(os.environ.get("UNI_BIAS_D", 20)) if deptos else 2.0
    if os.name == "nt":  # prioridad baja (por la temperatura de la CPU)
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    f = glob.glob(os.path.join(HERE, SHP, f"{d}_*.shp"))[0]
    rad = gpd.read_file(f).to_crs(AEA).reset_index(drop=True)
    gdf, unidad = rad, np.arange(len(rad))
    if deptos and n > 1:
        # los departamentos mas chicos que un distrito pasan a ser una sola unidad indivisible
        cp = rad.groupby("county").population.sum()
        chicos = set(cp.index[cp < frac * cp.sum() / n])
        clave = np.where(rad.county.isin(chicos), "C" + rad.county, "R" + rad.index.astype(str))
        gdf = rad.assign(u=clave).dissolve("u", aggfunc={"county": "first", "population": "sum"}).reset_index()
        unidad = pd.Index(gdf.u).get_indexer(clave)
    pops = gdf.population.values.astype(np.int64)
    G, unidas = grafo(gdf)
    for k in G.nodes: G.nodes[k]["population"] = int(pops[k])
    if not deptos:  # el grafo de radios, para abrir el shp en la interfaz de Mosaic
        cache = os.path.join(MOSAIC, "cache", os.path.splitext(os.path.basename(f))[0] + ".pkl")
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        with open(cache, "wb") as fh:
            pickle.dump({"nodes": list(G.nodes()), "edges": list(G.edges()),
                         "populations": {k: int(pops[k]) for k in G.nodes}}, fh)
    _, county = np.unique(gdf.county.values, return_inverse=True)
    res = {"distrito": d, "bancas": n, "unidades": len(gdf), "islas_unidas": unidas}
    if deptos: res["enteros_hasta"] = frac
    if n == 1:
        a = np.zeros(len(gdf), dtype=int)
    else:
        ctx = GraphContext(nx_to_igraph(G))
        pp = precompute_pp_data(gdf, G)
        ideal = pops.sum() / n
        a = desde_plan_libre(rad, unidad, G, n, plan, d) if deptos else None
        # con departamentos enteros las unidades son grumosas y el corte inicial de Mosaic casi nunca
        # entra en 2-5 %: se arranca flojo y ReCom (cada par recombinado ya cumple tol) lo ajusta
        escalera = (0.15, 0.25, 0.4) if deptos else (tol, tol * 1.5, tol * 2, tol * 3, tol * 4)
        tol_obj = tol
        for t in (escalera if a is None else ()):
            for k in range(3 if deptos else 8):  # cada intento de Mosaic prueba 10 arboles; se cambia la semilla
                try:
                    a = create_initial_partition(G, pops, n, t, seed=seed + 1000 * k)
                except RuntimeError:
                    a = desde_plan_libre(rad, unidad, G, n, plan, d) if deptos else None
                if a is not None: break
            if a is not None:
                if not deptos: tol = tol_obj = t
                break
        if a is None:
            res["error"] = "sin particion inicial"
            return res
        cfg = ScoreConfig(weight_cut_edges=1.0, weight_county_splits=50.0, weight_polsby_popper=100.0,
                          weight_pop_deviation=1.0)
        kw = dict(county_ids=county.astype(np.int32), populations=pops, ideal_pop=ideal, tolerance=tol,
                  pp_data=pp, n_districts=n)
        if modo != "neutral":
            # eleccion guia: balotaje 2023 + diputados 2025 sumados (las dos mano a mano)
            vv = rad[["D23b", "D25", "R23b", "R25"]].groupby(unidad).sum()
            dv = (vv.D23b + vv.D25).values.astype(np.int64)
            rv = (vv.R23b + vv.R25).values.astype(np.int64)
            share = dv.sum() / max(dv.sum() + rv.sum(), 1)
            cfg.weight_dem_seats = 30.0
            cfg.target_dem_seats = {"peronista": float(n), "lla": 0.0, "proporcional": n * share}[modo]
            if modo != "proporcional":
                cfg.weight_polsby_popper, cfg.weight_county_splits, cfg.weight_cut_edges = 5.0, 2.0, 0.2
            else:
                # con la compacidad completa el objetivo no se alcanza (el voto peronista esta concentrado):
                # pesos a mitad de camino entre el neutral y los gerrymanders
                cfg.weight_polsby_popper, cfg.weight_county_splits, cfg.weight_cut_edges = 25.0, 10.0, 0.5
                # bancas esperadas casi = bancas ganadas: si no, un distrito al 45 % cuenta como 0,2 banca y el
                # plan llega al objetivo "en esperanza" sin ganar distritos
                cfg.election_win_prob_at_55, cfg.election_swing_sigma = 0.9999, 0.005
            kw.update(dem_votes=dv, gop_votes=rv)
            res["objetivo_peronismo"] = round(float(cfg.target_dem_seats), 2)
        if deptos:
            cfg.weight_county_splits *= float(os.environ.get("UNI_MULT_D", 20))
            cfg.weight_pop_deviation = 50.0

        def desvio(x):
            return np.abs(np.bincount(x, weights=pops, minlength=n) / ideal - 1).max()

        def factible(x):
            return desvio(x) <= tol_obj + 1e-9
        cut = np.where(a[ctx.edge_u] != a[ctx.edge_v])[0].astype(np.int32)
        cur = score_plan(cut, cfg, assignment=a, **kw)
        ann = init_annealing(cur.total, AnnealingConfig(initial_temp_factor=0.2 if modo == "neutral" else TEMP_G), iters)
        best, best_s = (a.copy(), cur.total) if factible(a) else (None, np.inf)
        # trinquete: ReCom trabaja con el peor desvio actual (nunca empeora) hasta llegar a tol_obj;
        # si al final de iters no se llego, sigue hasta 3 x iters (10 x con --deptos)
        tol_i = max(tol_obj, desvio(a))
        for it in range((10 if deptos else 3) * iters):
            if it >= iters and best is not None: break
            if DEBUG and it % 500 == 0: print(d, it, round(tol_i, 4), round(cur.total, 1), flush=True)
            cand = cut
            if tol_i > tol_obj and np.random.random() < .5:
                # mientras haya distritos fuera de tolerancia, la mitad de las veces se recombina uno de ellos
                dev = np.abs(np.bincount(a, weights=pops, minlength=n) / ideal - 1)
                malos = dev > tol_obj
                sel = cut[malos[a[ctx.edge_u[cut]]] | malos[a[ctx.edge_v[cut]]]]
                if len(sel): cand = sel
            na, ok, nc = recom_step_ig(ctx, a, pops, ideal, tol_i, cand, county_array=county.astype(np.int32),
                                       county_bias=bias)
            if not ok:
                cool_temperature(ann); continue
            dn = desvio(na)
            if dn > tol_i + 1e-9: continue
            ps = score_plan(nc, cfg, assignment=na, **kw)
            if dn < tol_i - 1e-9 and tol_i > tol_obj or accept_proposal(cur.total, ps.total, ann):
                tol_i = max(tol_obj, min(tol_i, dn))
                a, cut, cur = na, nc, ps
                if cur.total < best_s and factible(a): best, best_s = a.copy(), cur.total
            cool_temperature(ann)
        if best is None:
            res["error"] = "ningun plan dentro de la tolerancia"
            return res
        a = best
        res["tolerancia"] = tol
    a = a[unidad]  # de unidades a radios
    gdf, pops = rad, rad.population.values.astype(np.int64)
    os.makedirs(os.path.join(HERE, plan), exist_ok=True)
    pd.DataFrame({"pid": gdf.pid, "distrito": a + 1}).to_csv(os.path.join(HERE, plan, f"{d}.csv"), index=False)
    t = gdf.assign(distrito=a + 1).groupby("distrito")[
        ["population"] + [p + e for e in ELEC for p in ("D", "R")]].sum()
    t["desvio_pob"] = t.population / (pops.sum() / n) - 1
    t["secciones"] = gdf.assign(distrito=a + 1).groupby("distrito").county.nunique()
    t.to_csv(os.path.join(HERE, plan, f"{d}_distritos.csv"))
    res["desvio_max"] = round(float(t.desvio_pob.abs().max()), 4)
    # departamentos partidos en mas distritos de los que su poblacion exige (ceil(pob/ideal))
    cd = gdf.assign(distrito=a).groupby("county").agg(k=("distrito", "nunique"), p=("population", "sum"))
    res["deptos"] = len(cd)
    res["deptos_partidos_de_mas"] = int((cd.k > np.ceil(cd.p / (pops.sum() / n))).sum())
    for e in ELEC:
        res["peronismo_" + e] = int((t["D" + e] > t["R" + e]).sum())
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("prov", nargs="*")
    ap.add_argument("--reparto", default="c257_sin_garantia")
    ap.add_argument("--iter", type=int, default=4000)
    ap.add_argument("--tol", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--deptos", action="store_true", help="respetar departamentos: partirlos solo si hace falta")
    ap.add_argument("--modo", default="neutral", choices=["neutral", "proporcional", "peronista", "lla"])
    o = ap.parse_args()
    rep = {r["distrito"]: int(r[o.reparto]) for r in csv.DictReader(open(os.path.join(HERE, "reparto.csv"), encoding="utf-8"))}
    provs = o.prov or sorted(rep)
    # las grandes primero
    plan = (PLAN if o.modo == "neutral" else f"{PLAN}_{o.modo}") + ("_deptos" if o.deptos else "")
    jobs = sorted([(d, rep[d], o.iter, o.tol, o.seed, o.modo, plan, o.deptos) for d in provs], key=lambda j: -j[1])
    t0 = time.time()
    with Pool(min(o.workers, len(jobs))) as p:
        rs = [r for r in p.imap_unordered(correr, jobs)]
        for r in rs: print(r, flush=True)
    rs.sort(key=lambda r: r["distrito"])
    cols = sorted({k for r in rs for k in r}, key=lambda k: list(rs[0]).index(k) if k in rs[0] else 99)
    if not o.prov:
        with open(os.path.join(HERE, plan, "resumen.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rs)
        for e in ELEC:
            print(e, "peronismo", sum(r.get("peronismo_" + e, 0) for r in rs), "de", sum(r["bancas"] for r in rs))
    print(f"{time.time() - t0:.0f} s")
