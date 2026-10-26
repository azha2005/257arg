import sys, json, re, difflib, collections, unicodedata
sys.path.insert(0, "../.claude/skills/mapa-electoral-wikipedia-1999/scripts")
from match_territories import norm, nprov
from common import ROOT
import os

SK = "../.claude/skills/mapa-electoral-wikipedia-1999/assets/"
BASE = json.load(open(SK + "territories.json", encoding="utf8"))["units"]
bkey = {}
for u in BASE: bkey.setdefault((nprov(u["prov"]), norm(u["name"])), u["i"])
byprov = collections.defaultdict(list)
for u in BASE: byprov[nprov(u["prov"])].append(u)

CFG = {
    1983: dict(folder="mapa1983", W2={"UCR": "red", "PJ": "blue", "PAL": "teal"}),
    1989: dict(folder="mapa1989", W2={"MEN": "blue", "ANG": "red", "ALS": "purple"}),
    1995: dict(folder="mapa1995", W2={"MEN": "blue", "BOR": "magenta", "MAS": "red"}),
}


NUM = [("25 de mayo", "veinticinco de mayo"), ("9 de julio", "nueve de julio"), ("12 de octubre", "doce de octubre"), ("2 de abril", "dos de abril"), ("1 de mayo", "primero de mayo")]
MANUAL = {("jujuy", "capital"): "doctor manuel belgrano", ("la rioja", "general lavalle"): "coronel felipe varela", ("la rioja", "general sarmiento"): "vinchina",
          ("la rioja", "gobernador gordillo"): "chamical", ("san luis", "la capital"): "juan martin de pueyrredon", ("tucuman", "san miguel de tucuman"): "capital",
          ("santiago del estero", "brigadier juan felipe ibarra"): "juan felipe ibarra", ("buenos aires", "gnral sarmiento"): "general sarmiento",
          ("buenos aires", "coronel de marina leonardo rosales"): "coronel rosales", ("buenos aires", "bartolome mitre"): "bartolome mitre"}


def nn(s):
    n = norm(s)
    for a, b in NUM:
        if n == a: n = b
    return n


def match(ds):
    res = {}; fuzzy = []; miss = []
    for i, t in enumerate(ds["territories"]):
        p = nprov(t["p"]); n = nn(t["n"])
        n = MANUAL.get((p, n), n)
        k = (p, n)
        if k in bkey: res[i] = bkey[k]; continue
        cands = {norm(u["name"]): u["i"] for u in byprov[p]}
        m = difflib.get_close_matches(n, list(cands), 1, 0.8)
        if m: res[i] = cands[m[0]]; fuzzy.append((t["p"], t["n"], m[0]))
        else: miss.append((t["p"], t["n"]))
    return res, fuzzy, miss


def run(year):
    cfg = CFG[year]
    ds = json.load(open("../%s/dataset_%d.json" % (cfg["folder"], year), encoding="utf8"))
    wc = {int(k): v for k, v in json.load(open("wiki_colors_%d.json" % year)).items()}
    res, fuzzy, miss = match(ds)
    used = collections.Counter(res.values())
    units = ds["modes"][0]["units"]
    rows = []
    for i, b in res.items():
        u = units[i]; t = ds["territories"][i]
        if b not in wc: continue
        w = wc[b]
        oc = cfg["W2"].get(u.get("w"), "otro:" + str(u.get("w")))
        # ganador entre los candidatos de la leyenda de Wikipedia, según nuestras líneas
        rows.append(dict(i=i, base=b, prov=t["p"], name=t["n"], wiki=w["cls"], wshare=w["share"], wrgb=w["rgb"], npx=w["npx"], ours=oc, ours_w=u.get("w"), q=u.get("q"), lines=u["lines"][:4], dup=used[b] > 1))
    return ds, rows, fuzzy, miss, res


if __name__ == "__main__":
    y = int(sys.argv[1])
    ds, rows, fuzzy, miss, res = run(y)
    print(y, "unidades del atlas", len(ds["territories"]), "emparejadas", len(res), "fuzzy", len(fuzzy), "sin pareja", len(miss), "duplicadas", sum(1 for r in rows if r["dup"]))
    for m in miss[:15]: print("  sin pareja", m)
    for f in fuzzy[:10]: print("  fuzzy", f)
    rows = [r for r in rows if not r["prov"].startswith("Capital")]
    ok = [r for r in rows if r["ours"] == r["wiki"]]
    print("  comparables", len(rows), "coinciden", len(ok), "%.1f%%" % (100. * len(ok) / len(rows)))
    cm = collections.Counter((r["ours"], r["wiki"]) for r in rows)
    for (a, b), v in sorted(cm.items(), key=lambda x: -x[1]): print("   nuestro %-12s wiki %-8s %d" % (a, b, v))
    json.dump(rows, open("cmp2_%d.json" % y, "w", encoding="utf8"), ensure_ascii=False)
