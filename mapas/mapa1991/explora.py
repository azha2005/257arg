import csv, sys, collections, importlib.util
y = sys.argv[1]
spec = importlib.util.spec_from_file_location("m", f"mapas/mapa{y}/mapeo_{y}.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
C2B = m.CODE2BLOC
U = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(f"datos/base8399/ernesto/{y}_diputados/dpto_partidos.csv", encoding="utf-8-sig")):
    if r["tipo_fila"] == "agrupacion" and r["codigo_partido"] not in getattr(m, "SKIP", ()): U[(r["provincia"], r["departamento"])][r["codigo_partido"]] += float(r["votos"])
tot = collections.Counter(); win = collections.Counter(); winc = collections.Counter()
for k, P in U.items():
    b = collections.Counter()
    for c, v in P.items():
        tot[C2B.get(c, "~" + c)] += v
        if c in C2B: b[C2B[c]] += v
    top = max(P, key=P.get)
    w = max(b, key=b.get) if b else None
    if w and b[w] >= P[top]: win[w] += 1
    else: winc[top] += 1
print("bloques:", {k: int(v) for k, v in tot.most_common() if not k.startswith("~")})
print("ganadores bloque:", dict(win)); print("ganadores codigo suelto:", dict(winc))
