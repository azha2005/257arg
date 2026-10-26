"""Agrupa las listas de la DINE (diputados y senadores nacionales 2011-2023) en los bloques de la tabla de Wikipedia («Total de alianzas ligadas a ...»).
    python wikileg/bloques_leg.py 2021 [DIPUTADOS|SENADORES]  -> imprime cobertura y no emparejados; escribe wikileg/bloques_<anio>_<cam>.csv"""
import os, re, sys, difflib, unicodedata
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_wleg import rows, clean
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()
    s = re.sub(r"\([^)]*\)", " ", s)          # siglas entre parentesis
    s = re.sub(r"\b(alianza|frente|partido|union|movimiento)\b", lambda m: m.group(1)[:3], s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def wiki_groups(anio, camara):
    t = open(os.path.join(ROOT, "wikileg", "wleg%s.txt" % anio), encoding="utf8").read()
    i = re.search(r"\n== Resultados( generales)? ==", t).start()
    if camara == "SENADORES":
        j = re.search(r"\n=== (Senadores|Senado)[^=]*===", t[i:]); i = i + j.start()
    j = t.index("{|", i); k = t.index("\n|}", j)
    rs = rows(t[j:k]); groups = []; buf = []
    for r in rs:
        m = re.match(r'^colspan\s*=\s*"?\d+"?\s*\|\s*(.*)$', r["nombre"])
        nm = m.group(1) if m else r["nombre"]
        nm = re.sub(r"^(?:[a-z-]+\s*=\s*\"?[^\s|\"]+\"?\s*)+\|\s*", "", nm).strip()
        low = nm.lower()
        if low.startswith("total"):
            lab = re.sub(r"^total de (alianzas|listas|partidos|frentes)( \w+)? ligad\w+ (a la |al |a los |a las |a |el |la )?", "", nm, flags=re.I).strip() or r["link"]
            lab = re.sub(r"^total (de )?", "", lab, flags=re.I).strip() or lab
            # las ultimas filas del buffer que suman el subtotal forman el grupo; las anteriores son partidos sueltos
            k = len(buf); s = 0
            while k > 0 and s < r["votos"] * 0.985:
                k -= 1; s += buf[k]["votos"]
            if k > 0 and abs(s - r["votos"]) / max(r["votos"], 1) < 0.02:
                for q in buf[:k]: groups.append(dict(grupo=q["nombre"], filas=[q], total=q["votos"]))
                buf = buf[k:]
            groups.append(dict(grupo=lab, filas=buf, total=r["votos"])); buf = []
        elif low.startswith(("votos", "participaci", "electores", "otros", "blanco", "anulado")):
            continue
        else:
            buf.append(dict(r, nombre=nm))
    for r in buf: groups.append(dict(grupo=r["nombre"], filas=[r], total=r["votos"]))
    return groups


def dine_names(anio, camara):
    pk = os.path.join(ROOT, "datos_oficiales", str(anio), "agregado.pkl")
    if not os.path.exists(pk): pk = os.path.join(ROOT, "datos_oficiales", str(anio), "agregado_polar.pkl")
    votes, mesas = pd.read_pickle(pk)
    pat = "DIPUTAD" if camara == "DIPUTADOS" else "SENADOR"
    v = votes[votes.cargo_nombre.str.upper().str.contains(pat) & (votes.votos_tipo == "POSITIVO")]
    g = v.groupby("agrupacion_nombre").v.sum().sort_values(ascending=False)
    return g


def match(anio, camara, overrides=None):
    via_dip = camara == "SENADORES" and anio in (2011, 2013, 2015, 2017)   # esos años la tabla de senadores de Wikipedia es por provincia: se usan los bloques de diputados
    groups = wiki_groups(anio, "DIPUTADOS" if via_dip else camara); D = dine_names(anio, camara)
    wrows = [(g["grupo"], r["nombre"], r["votos"]) for g in groups for r in g["filas"]]
    used = {}; res = {}
    cand = [(n, norm(n), v) for n, v in D.items()]
    for (grp, nom, vot) in sorted(wrows, key=lambda x: -x[2]):
        best = None
        for (n, nn, v) in cand:
            if n in used: continue
            sim = difflib.SequenceMatcher(None, norm(nom), nn).ratio()
            ratio = v / vot if vot else 0
            sc = sim - abs(1 - ratio) * (0.5 if sim < 0.99 else 0.05)
            if via_dip:
                ok = sim >= 0.85
            else:
                ok = sim >= 0.75 and 0.5 < ratio < 1.5 or (abs(1 - ratio) < 0.03 and sim >= 0.5)
            if ok:
                if best is None or sc > best[0]: best = (sc, n)
        if best and via_dip:
            for (n, nn, v) in cand:
                if n not in res and difflib.SequenceMatcher(None, norm(nom), nn).ratio() >= 0.85: res[n] = grp; used[n] = (grp, nom)
        elif best: used[best[1]] = (grp, nom); res[best[1]] = grp
    # segunda pasada: el nombre del bloque (o su sigla) esta contenido en el nombre de la lista
    glabels = sorted({g["grupo"] for g in groups}, key=lambda s: -len(norm(s)))
    for n in D.index:
        if n in res: continue
        nn = norm(n)
        for lab in glabels:
            key = norm(re.sub(r"\s+y\s+(aliados|el\s+\w+).*$", "", lab))
            if len(key) >= 6 and key in nn: res[n] = lab; break
    try:
        from overrides import OVR
    except Exception:
        OVR = {}
    ov = dict(OVR.get((anio, camara), {})); ov.update(overrides or {})
    for n, sub in ov.items():
        if n not in D.index: continue
        if sub is None: res.pop(n, None); continue
        tgt = [g["grupo"] for g in groups if sub.lower() in g["grupo"].lower()]
        if tgt: res[n] = tgt[0]
        else: print("override sin grupo:", n, "->", sub)
    return groups, D, res, used


if __name__ == "__main__":
    anio = int(sys.argv[1]); cam = sys.argv[2] if len(sys.argv) > 2 else "DIPUTADOS"
    groups, D, res, used = match(anio, cam)
    tot = D.sum(); mapped = D[D.index.isin(res)].sum()
    print(anio, cam, "listas DINE:", len(D), "votos", int(tot), "| emparejados", len(res), "= %.1f %% de los votos" % (100 * mapped / tot))
    bl = pd.Series({n: D[n] for n in res}).groupby(pd.Series(res)).sum().sort_values(ascending=False)
    wt = {g["grupo"]: g["total"] for g in groups}
    print("bloque | DINE | Wikipedia")
    for g, v in bl.items(): print("  %-44s %10d %10d  (%.1f%%)" % (g[:44], v, wt.get(g, 0), 100 * v / wt[g] if wt.get(g) else 0))
    print("grupos de Wikipedia sin ninguna lista:", [g["grupo"][:30] for g in groups if g["grupo"] not in bl.index][:10])
    print("SIN EMPAREJAR (top 25):"); 
    for n, v in D[~D.index.isin(res)].head(25).items(): print("   %9d  %s" % (v, n))
