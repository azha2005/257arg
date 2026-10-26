"""Presidente 1999 -> 2003 nacional, como Calvo y Escolar (2005, cap. 6): por departamento y sobre votos emitidos, pero con
Córdoba por circuito (base de E. Calvo, cordoba_circuitos.py). Escribe transferencias/circ_1999pe.pkl y circ_2003pe.pkl
(sufijo e: votos emitidos, sin «No votó»).
    python transferencias/cordoba_circuitos.py      (una vez: circ_1999pc.pkl)
    python transferencias/presidente_1999.py
    python transferencias/estimar.py 1999pe 2003pe
    NAZAR=5 python transferencias/agregacion.py 1999pe 2003pe     (Córdoba también por departamento: la versión de Calvo)
1999: base de Ernesto Calvo por departamento (sin San Luis ni Santa Cruz). Las listas se suman por candidato según la tabla
«Acceso a boletas» del artículo de la Wikipedia (fuentes/w1999p.txt): la UCeDé va con Duhalde salvo en Santa Fe (Cavallo), y
el PDP de Santa Fe y el PAL-PDP de Corrientes con De la Rúa. Los totales por provincia se cotejan con la tabla «Resultados
por distrito». 2003: PolAr por circuito, sumado por departamento fuera de Córdoba; Capital por circunscripción (1 a 28)."""
import os, re, difflib, unicodedata
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
from estimar import DISTRITOS

CANDS = ["DLR", "DUH", "CAV", "OTRO"]
DLR = {"ali", "ali00", "alisal", "alisj", "alifcso", "frepaso", "aftod", "adp", "palpdp"}
DUH = {"pj", "apj", "fed", "afjes", "afifed", "fifnc", "ucd"}
CAV = {"apr", "aapr", "aaprf", "aaprmpatp"}


def candidato(prov, cod):
    if cod == "acjc00": return None                              # Corrientes y Santiago: total de los sublemas acjc01-03
    if prov == "Santa Fe" and cod == "ucd": return "CAV"          # en Santa Fe la UCeDé llevó a Cavallo
    if cod in DLR or cod.startswith("ali"): return "DLR"
    if cod in DUH or "cjc" in cod: return "DUH"
    if cod in CAV or cod.startswith("aapr"): return "CAV"
    return "OTRO"


ABREV = {"GRAL": "GENERAL", "CNEL": "CORONEL", "PTE": "PRESIDENTE", "TTE": "TENIENTE", "DR": "DOCTOR", "PDCIA": "PRESIDENCIA",
         "R": "ROSARIO", "SL": "SAN LUIS", "F": "FELIPE"}


def norm(s):
    s = unicodedata.normalize("NFD", str(s).upper()).encode("ascii", "ignore").decode()
    s = re.sub(r"\s*-\s*\d+\s*$", "", s)                        # «Capital - 481» (Misiones, Río Negro)
    return " ".join(ABREV.get(w, w) for w in re.sub(r"[^A-Z0-9 ]", " ", s).split())


# (distrito, nombre 1999 normalizado) -> nombre 2003 normalizado, para lo que no empareja exacto (o empareja mal por parecido)
ALIAS = {("02", "AMEGHINO"): "FELIPE AMEGHINO", ("02", "BARTOLOME MITRE"): "ARRECIFES", ("02", "PERON"): "PRESIDENTE PERON",
         ("02", "GENERAL LAS HERAS"): "LAS HERAS", ("06", "1 DE MAYO"): "PRIMERO DE MAYO", ("07", "FLORENTINO AMEGHINO"): "FELIPE AMEGUINO",
         ("09", "CAPITAL"): "FORMOSA", ("10", "BELGRANO"): "GENERAL BELGRANO", ("11", "QUEMU"): "QUEMU QUEMU",
         ("12", "GENERAL ANGEL PENALOZA"): "ANGEL VICENTE PENALOZA", ("16", "SAN CARLOS DEBARILOCHE"): "BARILOCHE",
         ("22", "GENERAL TABOADA"): "TABOADA", ("22", "MARIANO MORENO"): "MORENO", ("24", "ANTARTIDA"): "ANTARTIDA ARGENTINA",
         ("22", "VILLA SALAVINA"): "SALAVINA"}   # «F.» = Florentino en Buenos Aires y Chubut: la clave es solo para emparejar


def wiki():
    """Tabla «Resultados por distrito»: provincia -> votos por candidato, otras y blancos/nulos."""
    t = open(os.path.join(HERE, "fuentes", "w1999p.txt"), encoding="utf8").read()
    t = t[t.index("=== Resultados por distrito ==="):]
    t = t[t.index("{| class=\"wikitable sortable\""):]; t = t[:t.index("\n|}")]
    out = {}
    for row in t.split("\n|-")[1:]:
        c = [x.strip().strip("'") for x in re.split(r"\n\||\|\|", row)[1:]]
        if len(c) < 11: continue
        name = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", c[0]).strip()
        n = lambda s: int(re.sub(r"\D", "", s) or 0)
        out[norm(name)] = dict(DLR=n(c[1]), DUH=n(c[3]), CAV=n(c[5]), OTRO=n(c[7]), BLANCO=n(c[9]))
    return out


def base99():
    d = pd.read_csv(os.path.join(ROOT, "datos/base8399", "ernesto", "1999_presidente", "dpto_partidos.csv"), dtype=str)
    d["votos"] = pd.to_numeric(d.votos, errors="coerce").fillna(0)
    a = d[d.tipo_fila == "agrupacion"].copy()
    a["cand"] = [candidato(p, c) for p, c in zip(a.provincia, a.codigo_partido)]
    a = a[a.cand.notna()]
    T = a.pivot_table(index=["provincia", "departamento"], columns="cand", values="votos", aggfunc="sum", fill_value=0)
    bn = d[d.tipo_fila.isin(["blancos", "nulos"])].groupby(["provincia", "departamento"]).votos.sum()
    T["BLANCO"] = bn.reindex(T.index).fillna(0)
    return pd.concat([T.reindex(columns=CANDS + ["BLANCO"], fill_value=0), sl_sc()])


def sl_sc():
    """San Luis y Santa Cruz no están en la base de Ernesto: Lupu-Stokes por departamento (ucr = De la Rúa, pj = Duhalde,
    total = positivos; coinciden con la Wikipedia a menos de 0,5 %). El resto (total - ucr - pj) se reparte entre Cavallo y
    Otros, y los blancos y nulos se asignan, con las proporciones provinciales de la Wikipedia (imputado: sin variación propia)."""
    l = pd.read_csv(os.path.join(ROOT, "datos/base8399", "elecciones", "1999_presidente", "lupu_stokes.csv"), dtype=str)
    l = l[l.province.isin(["San Luis", "Santa Cruz"])]
    W = wiki(); out = []
    for _, r in l.iterrows():
        w = W[norm(r.province)]; tot, ucr, pj = (float(r[c]) for c in ("total", "ucr", "pj"))
        resto = tot - ucr - pj; pos = w["DLR"] + w["DUH"] + w["CAV"] + w["OTRO"]
        out.append(dict(provincia=r.province, departamento=r.department, DLR=ucr, DUH=pj, CAV=resto * w["CAV"] / (w["CAV"] + w["OTRO"]),
                        OTRO=resto * w["OTRO"] / (w["CAV"] + w["OTRO"]), BLANCO=tot * w["BLANCO"] / pos))
    return pd.DataFrame(out).set_index(["provincia", "departamento"])


def cotejo(T):
    W = wiki(); P = T.groupby(level=0).sum()
    print("Provincia: base menos Wikipedia (% del total provincial de la Wikipedia)")
    for p, r in P.iterrows():
        w = W.get("CABA" if p == "Capital Federal" else norm(p))
        if w is None: print("  %-20s sin fila en la Wikipedia" % p); continue
        tot = sum(w.values())
        print("  %-20s %s" % (p, "  ".join("%s %+5.1f" % (k, 100 * (r[k] - w[k]) / tot) for k in w)))
    faltan = [k for k in W if k not in {norm(p) for p in P.index} | {"CABA", "TOTAL"}]
    print("Sin datos en la base:", faltan)


def secciones03():
    s = pd.read_csv(os.path.join(HERE, "secciones_2003.csv"), dtype=str)
    s["distrito_id"] = s.distrito_id.str.zfill(2)
    return {(d, int(i)): n for d, i, n in zip(s.distrito_id, s.seccion_id, s.depto)}


def main():
    T = base99(); cotejo(T)
    sec = secciones03()
    pid = {norm(n): d for d, n in DISTRITOS.items()}; pid[norm("Capital Federal")] = "01"
    por_nombre = {(d, norm(n)): (i, norm(n)) for (d, i), n in sec.items()}
    rows, sin, parecidos = {}, [], []
    for (p, u), r in T.iterrows():
        d = pid[norm(p)]
        if d == "04": continue                                  # Córdoba va por circuito
        if d == "01":
            i = int(u); key = (d, 0, "S:" + norm(sec[(d, i)]))
        else:
            nu = ALIAS.get((d, norm(u)), norm(u))
            if (d, nu) not in por_nombre:
                cand = difflib.get_close_matches(nu, [n for dd, n in por_nombre if dd == d], n=1, cutoff=0.75)
                if not cand: sin.append((p, u)); continue
                parecidos.append("%s: %s -> %s" % (p, u, cand[0])); nu = cand[0]
            key = (d, 0, "S:" + nu)
        rows[key] = rows.get(key, 0) + r
    print("Emparejados por parecido:", *parecidos, sep="\n  ")
    print("Departamentos 1999 sin pareja en 2003:", sin)
    # Córdoba por circuito (cordoba_circuitos.py), con la UCeDé sumada a Duhalde como en la boleta
    vc, ec = pd.read_pickle(os.path.join(HERE, "circ_1999pc.pkl"))
    mapa = {"ALIANZA": "DLR", "PJ": "DUH", "UCEDE": "DUH", "AR": "CAV"}
    vc = vc.assign(agrupacion_id=[("" if t != "POSITIVO" else mapa.get(a, "OTRO")) for a, t in zip(vc.agrupacion_id, vc.votos_tipo)])
    v = [dict(distrito_id=k[0], seccion_id=k[1], circuito=k[2], agrupacion_id=("" if c == "BLANCO" else c),
              votos_tipo=("EN BLANCO" if c == "BLANCO" else "POSITIVO"), v=x) for k, r in rows.items() for c, x in r.items()]
    v = pd.concat([pd.DataFrame(v), vc], ignore_index=True)
    idx = ["distrito_id", "seccion_id", "circuito"]
    e = v.groupby(idx).v.sum()
    pd.to_pickle((v, e), os.path.join(HERE, "circ_1999pe.pkl"))
    print("1999pe: unidades %d (Córdoba %d circuitos), votos %d" % (len(e), len(ec), e.sum()))
    # 2003: fuera de Córdoba, circuitos sumados por sección (departamento); votos emitidos
    v3, _ = pd.read_pickle(os.path.join(HERE, "circ_2003p.pkl"))
    v3 = v3.copy()
    fuera = v3.distrito_id != "04"
    v3.loc[fuera, "circuito"] = ["S:" + norm(sec.get((d, int(s)), "?")) for d, s in zip(v3.distrito_id[fuera], v3.seccion_id[fuera])]
    v3.loc[fuera, "seccion_id"] = 0
    v3 = v3.groupby(idx + ["agrupacion_id", "votos_tipo"]).v.sum().reset_index()
    e3 = v3.groupby(idx).v.sum()
    pd.to_pickle((v3, e3), os.path.join(HERE, "circ_2003pe.pkl"))
    print("2003pe: unidades %d, votos %d; unidades 1999 sin 2003: %s" % (len(e3), e3.sum(), sorted(set(e.index) - set(e3.index))[:20]))


if __name__ == "__main__":
    main()
