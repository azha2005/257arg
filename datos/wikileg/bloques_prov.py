"""Bloques de Wikipedia para 2005, 2007 y 2009 (PolAr_Data), lista por lista y provincia por provincia.
Las listas de PolAr tienen nombres distintos en cada provincia y a veces repetidos para fuerzas distintas, asi que no alcanza con emparejar por nombre nacional.
Metodo: (1) filas de la tabla provincial de Wikipedia («Resultados por provincia/distrito», un bloque por provincia con votos de cada alianza);
(2) cada lista de PolAr de la provincia se empareja con la fila de la tabla provincial de mayor cercania de votos (y de nombre);
(3) el nombre de esa fila se busca en la tabla nacional (grupos «Total de alianzas ligadas a ...»).
    python wikileg/bloques_prov.py 2009 DIPUTADOS    -> cobertura por bloque
"""
import os, re, sys, difflib, unicodedata
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_wleg import rows, clean
from bloques_leg import wiki_groups, norm as norm0, ROOT

PROVN = {"Ciudad de Buenos Aires": ["capital federal", "ciudad"], "Buenos Aires": ["provincia de buenos aires"], "Córdoba": ["córdoba"], "Entre Ríos": ["entre ríos"],
         "Santiago del Estero": ["santiago del estero"], "Río Negro": ["río negro"], "La Pampa": ["la pampa"], "La Rioja": ["la rioja"], "San Juan": ["san juan"],
         "San Luis": ["san luis"], "Santa Cruz": ["santa cruz"], "Santa Fe": ["santa fe"], "Tierra del Fuego": ["tierra del fuego"], "Tucumán": ["tucumán"],
         "Catamarca": ["catamarca"], "Chaco": ["chaco"], "Chubut": ["chubut"], "Corrientes": ["corrientes"], "Formosa": ["formosa"], "Jujuy": ["jujuy"],
         "Mendoza": ["mendoza"], "Misiones": ["misiones"], "Neuquén": ["neuquén"], "Salta": ["salta"]}


PROVSET = set()


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()
    s = re.sub(r"\([^)]*\)", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def prov_of(header):
    h = clean(header.split("<br")[0]).lower()
    h = unicodedata.normalize("NFC", h)
    for p, keys in PROVN.items():
        for k in keys:
            if k in h and not (p == "Buenos Aires" and "ciudad" in h) and not (p == "Santa Fe" and "santa fe" not in h) : return p
    return None


def prov_tables(anio, camara):
    t = open(os.path.join(ROOT, "wikileg", "wleg%s.txt" % anio), encoding="utf8").read()
    s = re.search(r"\n== Resultados por (provincia|distrito)s? ==", t).start()
    if camara == "SENADORES":
        a = re.search(r"\n=== Senado[^=]*===", t[s:]); i = s + a.start(); j = t.index("{|", i); k = t.index("\n|}", j)
    else:
        a = re.search(r"\n=== C[aá]mara de Diputados ===", t[s:]); i = s + a.start(); j = t.index("{|", i); k = t.index("\n|}", j)
    tbl = t[j:k]
    out = {}; cur = None
    for blk in tbl.split("\n|-"):
        m = re.search(r"^!\s*colspan\s*=\s*\"?\d+\"?[^|\n]*\|\s*(.*)$", blk, re.M)
        if m and re.search(r"Diputad|Senador", m.group(1)) and "Partido/Alianza" not in m.group(1):
            cur = prov_of(m.group(1)); continue
        if cur is None: continue
        for r in rows("{|\n|-" + blk):
            r = dict(r, nombre=re.sub(r"^(?:[a-z-]+\s*=\s*\"?[^\s|\"]+\"?\s*)+\|\s*", "", r["nombre"]).strip())
            out.setdefault(cur, []).append(r)
    for prov, rs in out.items():                  # componentes de una fila «Total ...» (suman exacto) -> comparten alianza
        used = set()
        for i, r in enumerate(rs):
            if not re.match(r"total", r["nombre"].strip(), re.I): continue
            sm = 0; k = i
            while k > 0 and sm < r["votos"] * 0.995:
                k -= 1
                if k in used or re.match(r"total", rs[k]["nombre"].strip(), re.I): k += 1; break
                sm += rs[k]["votos"]
            if k < i and abs(sm - r["votos"]) <= 0.005 * r["votos"]:
                lab = re.sub(r"^total( de)?( la)?( alianza)?\s*", "", r["nombre"].strip(), flags=re.I).strip()
                for q in range(k, i): rs[q]["alianza"] = lab; used.add(q)
    return out


def national_index(anio, camara):
    groups = wiki_groups(anio, camara)
    idx = []
    for g in groups:
        for r in g["filas"]:
            par = " ".join(re.findall(r"\(([^)]*)\)", r["nombre"]))
            idx.append((norm(r["nombre"]), g["grupo"], r["votos"], norm(par)))
    return groups, idx


def match_prov(anio, camara, votes_path=None):
    """-> (groups, res, cov) con res[(provincia, nombre_lista)] = nombre del grupo de Wikipedia"""
    groups, idx = national_index(anio, camara)
    ptabs = prov_tables(anio, camara)
    pat = "DIPUTAD" if camara == "DIPUTADOS" else "SENADOR"
    pk = votes_path or os.path.join(ROOT, "../datos_oficiales", str(anio), "agregado_polar.pkl")
    votes, mesas = pd.read_pickle(pk)
    v = votes[votes.cargo_nombre.str.upper().str.contains(pat) & (votes.votos_tipo == "POSITIVO")]
    g = v.groupby(["distrito_nombre", "agrupacion_nombre"]).v.sum().reset_index()
    res = {}; log = []
    nat_names = [x[0] for x in idx]

    def group_of(prow_name, prov=None, pv=None):
        n = norm(prow_name); pn = norm(prov or "")
        best = None
        for (nn, gr, vv, par) in idx:
            sim = 1.0 if nn == n else difflib.SequenceMatcher(None, n, nn).ratio()
            if len(n) >= 6 and len(nn) >= 6 and (n in nn or nn in n): sim = max(sim, 0.9 - abs(len(n) - len(nn)) / 200)
            if sim < 0.8: continue
            if pv and vv < pv * 0.95: continue                      # la fila nacional agrega a la provincial: no puede ser menor
            sc = sim + (0.3 if (pn and pn and pn in par) else 0) - (0.3 if (par and pn and pn not in par and par not in PROVSET) else 0) - (min(2.0, vv / pv - 1) * 0.05 if pv else 0)
            if best is None or sc > best[0]: best = (sc, gr)
        return best[1] if best else None

    for prov, sub in g.groupby("distrito_nombre"):
        rows_w = ptabs.get(prov, [])
        used = set()
        for _, r in sub.sort_values("v", ascending=False).iterrows():
            best = None
            for i, w in enumerate(rows_w):
                if i in used or not w["votos"] or re.match(r"(votos|electores|total|participaci)", w["nombre"].strip(), re.I): continue
                ratio = r.v / w["votos"]
                sim = difflib.SequenceMatcher(None, norm0(r.agrupacion_nombre), norm0(w["nombre"])).ratio()
                # votos muy parecidos, o votos aceptables y nombre parecido
                ok = (abs(1 - ratio) < 0.02) or (abs(1 - ratio) < 0.08 and sim > 0.35) or (0.6 < ratio < 1.6 and sim > 0.6)
                if not ok: continue
                sc = sim - abs(1 - ratio) * 4
                if best is None or sc > best[0]: best = (sc, i, w)
            if best:
                used.add(best[1]); w = best[2]
                gr = group_of(w["nombre"], prov, w["votos"])
                if w.get("alianza") is not None:
                    ag = group_of(w["alianza"], prov, None) if len(norm(w["alianza"])) > 3 else None
                    gr = ag or gr
                log.append((prov, r.agrupacion_nombre, int(r.v), best[2]["nombre"], best[2]["votos"], gr))
                if gr: res[(prov, r.agrupacion_nombre)] = gr
    try:
        from overrides import OVRP
    except Exception:
        OVRP = {}
    for (prov, nm), sub in OVRP.get((anio, camara), {}).items():
        if sub is None: res.pop((prov, nm), None); continue
        tgt = [x["grupo"] for x in groups if sub.lower() in x["grupo"].lower()] or [x["grupo"] for x in groups if any(sub.lower() in f["nombre"].lower() for f in x["filas"])]
        if tgt: res[(prov, nm)] = tgt[0]
        else: print("override sin grupo:", prov, nm, "->", sub)
    return groups, res, log, g


if __name__ == "__main__":
    anio = int(sys.argv[1]); cam = sys.argv[2] if len(sys.argv) > 2 else "DIPUTADOS"
    groups, res, log, g = match_prov(anio, cam)
    tot = g.v.sum(); mp = sum(r.v for r in g.itertuples() if (r.distrito_nombre, r.agrupacion_nombre) in res)
    print(anio, cam, "listas", len(g), "votos", int(tot), "| agrupados %.1f %%" % (100 * mp / tot))
    import collections
    acc = collections.defaultdict(float)
    for r in g.itertuples():
        k = res.get((r.distrito_nombre, r.agrupacion_nombre))
        if k: acc[k] += r.v
    s = pd.Series(acc).sort_values(ascending=False)
    wt = {x["grupo"]: x["total"] for x in groups}
    for k, vv in s.items():
        if vv > 30000: print("  %-50s PolAr %9d  Wiki %9d  %.2f" % (k[:50], vv, wt.get(k, 0), vv / wt[k] if wt.get(k) else 0))
    print("sin emparejar >15k:")
    for r in g.sort_values("v", ascending=False).itertuples():
        if (r.distrito_nombre, r.agrupacion_nombre) not in res and r.v > 15000: print("   %8d  %-14s %s" % (r.v, r.distrito_nombre[:14], r.agrupacion_nombre))
    print("provincias en la tabla:", sorted(prov_tables(anio, cam)))
