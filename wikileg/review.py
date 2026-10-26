import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bloques_leg import *
def review(anio, cam, top=14):
    groups, D, res, used = match(anio, cam)
    tot = D.sum(); mapped = D[D.index.isin(res)].sum()
    print("== %s %s: listas %d, emparejado %.1f%% de %d votos" % (anio, cam, len(D), 100*mapped/tot, tot))
    bl = pd.Series({n: D[n] for n in res}).groupby(pd.Series(res)).sum()
    wt = {g["grupo"]: g["total"] for g in groups}
    for g, v in bl.sort_values(ascending=False).items():
        r = v / wt[g] if wt.get(g) else 0
        flag = "" if 0.9 < r < 1.1 else "   <<<<"
        if v > 40000 or flag: print("  %-52s DINE %9d  Wiki %9d  %.2f%s" % (g[:52], v, wt.get(g, 0), r, flag))
    print("  sin grupo en DINE:", [ (g["grupo"][:28], g["total"]) for g in groups if g["grupo"] not in bl.index and g["total"] > 40000])
    print("  SIN EMPAREJAR >20k:")
    for n, v in D[~D.index.isin(res)].items():
        if v > 20000: print("     %9d  %s" % (v, n))
if __name__ == "__main__":
    review(int(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "DIPUTADOS")
