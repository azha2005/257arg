#!/usr/bin/env python3
"""EJEMPLO: arma dataset.json (formato de references/dataset-schema.md) para las elecciones de 1976.

Sirve de modelo para otros datos: lo unico que cambia entre elecciones es esta preparacion.
Entradas (en la carpeta src/ del proyecto de 1976): data_1976.json, names.json, hist_1976.json, segunda_vuelta.py

    python3 example_prepare_1976.py <carpeta_src> <salida_dataset.json>

Incluye, ademas de los porcentajes por candidato, lo que usa el panel de detalle: metricas, secciones
(correspondencia con los mapas historicos, comparacion con la primera vuelta) y notas.
"""
import json, os, sys

src, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, src)
import segunda_vuelta as sv

D = json.load(open(os.path.join(src, "data_1976.json"), encoding="utf8"))
N = json.load(open(os.path.join(src, "names.json"), encoding="utf8"))
HIST = json.load(open(os.path.join(src, "hist_1976.json"), encoding="utf8"))
P = D["PROVS"]
MAIN4 = ["UCR", "PJ", "AF", "MID"]
MINOR = ["Ghioldi", "Coral", "Ramos"]


def n_(v):
    return "{:,}".format(int(v)).replace(",", ".")


def pct(a, b):
    return round(100 * a / b, 2) if b else 0.0


def lines_r1(c, valid, total):
    """4 candidaturas y 3 menores como % de votos validos; blanco y nulo como % de la participacion."""
    L = [[k, c[k], pct(c[k], valid)] for k in MAIN4 + MINOR]
    L += [["Blanco", c["Blanco"], pct(c["Blanco"], total)], ["Nulo", c["Nulo"], pct(c["Nulo"], total)]]
    return L


def hist_rows(hs):
    rows = []
    for h in hs:
        v = h["fracciones"]
        if h["cantidad_pixeles"]:
            txt = "Azul %d %% · rojo %d %%" % (round(100 * (v.get("PJ") or 0)), round(100 * (v.get("UCR") or 0)))
            if "1973" in h["mapa"]:
                txt += " · amarillo %d %%" % round(100 * (v.get("PF") or 0))
        else:
            txt = "Sin cobertura suficiente"
        rows.append([h["mapa"], txt])
    return rows


def hist_section(hs):
    return {"title": "Correspondencia con los tres mapas históricos", "rows": hist_rows(hs)}


def hist_prov(prov):
    agg = [{"mapa": h["mapa"], "cantidad_pixeles": 0, "fracciones": {k: 0.0 for k in ("PJ", "UCR", "PF")}} for h in HIST[0]]
    for i, d in enumerate(D["DEPTS"]):
        if d["prov"] != prov:
            continue
        for j, h in enumerate(HIST[i]):
            n = h["cantidad_pixeles"]
            agg[j]["cantidad_pixeles"] += n
            for k in agg[j]["fracciones"]:
                if h["fracciones"].get(k) is not None:
                    agg[j]["fracciones"][k] += n * h["fracciones"][k]
    for a in agg:
        t = a["cantidad_pixeles"]
        a["fracciones"] = {k: (v / t if t else None) for k, v in a["fracciones"].items()}
    return hist_section(agg)


def first_round_section(c, valid):
    return {"title": "Primera vuelta (estimación)", "rows": [[k, "%s %%" % ("%.2f" % pct(c[k], valid)).replace(".", ",")] for k in MAIN4]}


NOTE_DEPT = "Estimación departamental: votos modelados, no resultados observados. Blanco y nulo: % sobre la participación; el resto, sobre votos válidos."
NOTE_PROV = "Cifras finales de la tabla del DOCX, sin recalcular. Blanco y nulo: % sobre la participación; el resto, sobre votos válidos."


def units_r1(rows, with_hist):
    u = []
    for i, r in enumerate(rows):
        d = D["DEPTS"][i]
        c = r.get("counts") or r["c"]
        v = r.get("valid") or r["v"]
        t = r.get("total") or r["t"]
        unit = dict(w=r.get("winner") or r["w"], q=r.get("pct") or r["q"], lines=lines_r1(c, v, t),
                    metrics=[["Votos válidos", n_(v)], ["Participación (votos)", n_(t)]], note=NOTE_DEPT)
        unit["sections"] = [hist_section(HIST[i])] if with_hist else []
        u.append(unit)
    return u


def prov_rec_r1():
    out = {}
    for k, p in P.items():
        out[k] = dict(w=p["winner"], q=p["pct"], lines=lines_r1(p["counts"], p["valid"], p["total"]),
                      metrics=[["Votos válidos", n_(p["valid"])], ["Participación (votos)", n_(p["total"])], ["Registrados", n_(p["registered"])]],
                      note=NOTE_PROV, sections=[hist_prov(k)])
    return out


def units_prov_r1():
    out = []
    for d in D["DEPTS"]:
        pr = prov_rec_r1_cache[d["prov"]]
        out.append(dict(pr, note="Total provincial (todo departamento hereda el resultado de su provincia)"))
    return out


# --- nacional 1.a vuelta
tot = {k: sum(P[p]["counts"][k] for p in P) for k in MAIN4 + MINOR + ["Blanco", "Nulo"]}
part = sum(P[p]["total"] for p in P)
reg = sum(P[p]["registered"] for p in P)
others = sum(tot[k] for k in MINOR)
valid = sum(tot[k] for k in MAIN4) + others
cands = sorted(({"code": k, "votes": tot[k], "pct": pct(tot[k], valid)} for k in MAIN4), key=lambda c: -c["votes"])
nat1 = dict(cands=cands, partp=pct(part, reg),
            slices=[dict(code=c["code"], v=c["votes"]) for c in cands] + [dict(fill="#717274", v=others), dict(fill="#dfe0e5", v=tot["Blanco"] + tot["Nulo"])],
            metrics=[["Votos válidos", n_(valid)], ["Participación (votos)", n_(part)], ["Registrados", n_(reg)]])

# --- segunda vuelta (provincias y departamentos) con las reglas de traspaso de segunda_vuelta.py
prov2 = {k: sv.provincia(p["counts"], p["registered"], p["total"]) for k, p in P.items()}
T2 = sv.total(prov2)
r2d = [sv.departamento(d["counts"], d["total"]) for d in D["DEPTS"]]
r2m = [sv.departamento(m["counts"], m["total"]) for m in D["MARCH"]]
c2 = sorted([dict(code="UCR", votes=T2["UCR"], pct=T2["UCRp"]), dict(code="PJ", votes=T2["PJ"], pct=T2["PJp"])], key=lambda c: -c["votes"])
nat2 = dict(cands=c2, partp=T2["Partp"],
            slices=[dict(code=c["code"], v=c["votes"]) for c in c2] + [dict(fill="#dfe0e5", v=T2["Blanco"] + T2["Nulo"])],
            metrics=[["Votos a candidatos", n_(T2["PJ"] + T2["UCR"])], ["Participación (votos)", n_(T2["Part"])], ["Registrados", n_(T2["Reg"])]])


def win2(p):
    return ("UCR", p["UCRp"]) if p["UCR"] >= p["PJ"] else ("PJ", p["PJp"])


def lines_r2(r, part2):
    t = r["PJ"] + r["UCR"]
    return [["UCR", r["UCR"], pct(r["UCR"], t)], ["PJ", r["PJ"], pct(r["PJ"], t)],
            ["Blanco", r["Blanco"], pct(r["Blanco"], part2)], ["Nulo", r["Nulo"], pct(r["Nulo"], part2)]]


def units_r2(rows, first):
    u = []
    for i, r in enumerate(rows):
        d = D["DEPTS"][i]
        part2 = d["total"] - r["AbstNueva"]
        f = first[i]
        u.append(dict(w=r["w"], q=r["q"], lines=lines_r2(r, part2),
                      metrics=[["Votos a candidatos", n_(r["PJ"] + r["UCR"])], ["Participación (votos)", n_(part2)], ["Abstención adicional", n_(r["AbstNueva"])]],
                      note="Segunda vuelta · estimación a partir del traspaso de votos. Blanco y nulo: % sobre la participación.",
                      sections=[first_round_section(f.get("counts") or f["c"], f.get("valid") or f["v"])]))
    return u


def prov_r2():
    out = {}
    for k, p in prov2.items():
        w, q = win2(p)
        out[k] = dict(w=w, q=q, lines=lines_r2(p, p["Part"]),
                      metrics=[["Votos a candidatos", n_(p["PJ"] + p["UCR"])], ["Participación (votos)", n_(p["Part"])], ["Registrados", n_(p["Reg"])]],
                      note="Tabla del DOCX (segunda vuelta simulada). Blanco y nulo: % sobre la participación.", sections=[first_round_section(P[k]["counts"], P[k]["valid"])])
    return out


def units_prov_r2():
    pr = prov_r2()
    return [dict(pr[d["prov"]], note="Total provincial (simulación)") for d in D["DEPTS"]]


prov_rec_r1_cache = prov_rec_r1()
prov_r1 = prov_rec_r1_cache
prov_r2d = prov_r2()

MINOR_CAND = lambda n, base: dict(n=n, base=base, minor=True)
ds = dict(
    slug="elecciones_1976", locale="es-AR", country="Argentina",
    title="Elecciones presidenciales de Argentina de", year="1976",
    exterior=dict(caption="sin voto en 1976"),
    sets={"1": dict(label="1ª V."), "2": dict(label="2ª V.", subtitle="Segunda vuelta · simulación")},
    candidates={
        "UCR": dict(n="Alfonsín / Alende", sub="FREDEPO", logo="UCR", base="#dc0143", bar="#dc0143"),
        "PJ": dict(n="Luder / Menem", sub="PJ", logo="PJ", base="#1c5ece", bar="#1c5ece"),
        "AF": dict(n="Manrique / Chamizo", sub="FUREFE", logo="AF", base="#f0b100", bar="#c99600", txt="#c99600"),
        "MID": dict(n="Frigerio / Bárbaro", sub="FREDEJUSO", logo="MID", base="#14b3a3", bar="#14978a"),
        "Ghioldi": MINOR_CAND("Ghioldi / Balestra (PSD)", "#8e949b"),
        "Coral": MINOR_CAND("Coral / Ciapponi (PST)", "#a37cc4"),
        "Ramos": MINOR_CAND("Ramos / Silvetti (FIP)", "#c28b5a"),
        "Blanco": MINOR_CAND("Votos en blanco", "#b8bcc2"),
        "Nulo": MINOR_CAND("Votos nulos", "#6e7379"),
    },
    modes=[
        dict(id="dept", tile="DEPT", set="1", note="Departamentos: estimación suavizada (85 % primera extrapolación + 15 % tres mapas históricos), no resultados observados.",
             units=units_r1(D["DEPTS"], True), prov=prov_r1, national=nat1),
        dict(id="march", tile="MAR73", set="1", note="Departamentos: variante marzo 1973, extrapolación espacial, no resultados observados.",
             units=units_r1(D["MARCH"], True), prov=prov_r1, national=nat1),
        dict(id="prov", tile="PROV", set="1", note="Primera vuelta por provincia.",
             units=units_prov_r1(), prov=prov_r1, national=nat1),
        dict(id="r2d", tile="DEPT", set="2", note="Segunda vuelta (simulación): traspaso de votos aplicado a la estimación departamental de la 1.ª vuelta; no son resultados observados.",
             units=units_r2(r2d, D["DEPTS"]), prov=prov_r2d, national=nat2),
        dict(id="r2m", tile="MAR73", set="2", note="Segunda vuelta (simulación), variante marzo 1973.",
             units=units_r2(r2m, D["MARCH"]), prov=prov_r2d, national=nat2),
        dict(id="r2p", tile="PROV", set="2", note="Segunda vuelta (simulación) por provincia.",
             units=units_prov_r2(), prov=prov_r2d, national=nat2),
    ],
)
json.dump(ds, open(out, "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("dataset escrito:", out, round(os.path.getsize(out) / 1e6, 2), "MB")
