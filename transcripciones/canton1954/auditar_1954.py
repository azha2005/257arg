"""Auditoria independiente de canton_1954.csv: busca lo raro que los controles de la transcripcion no miran.
    python canton1954/auditar_1954.py        -> canton1954/AUDITORIA_1954.md
Controles:
  1. Suma de fila (votantes = partidos + blanco) y varones + mujeres = total, recalculados desde el CSV.
  2. Celda culpable: cuando una diferencia es de 10, 100 o 1000, se busca la celda que la explica y se dice cual de
     las tres tablas (varones, mujeres, total) queda sola contra las otras dos (probable error de imprenta o de lectura).
  3. Participacion: votantes > inscriptos, menos de 60 %, y diferencia de mas de 12 puntos entre varones y mujeres.
  4. Proporcion peronista: diferencia de mas de 15 puntos entre varones y mujeres de la misma unidad.
  5. Inscriptos 1954 contra 1958 (Canton, canton5865): crecimiento fuera de lo normal en la provincia.
  6. Totales provinciales contra la Wikipedia (suma de las circunscripciones; wiki1954_prov.json).
  7. Nombres de unidades que no estan en 1958."""
import os, sys, json, unicodedata
from collections import defaultdict
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
CAT = {"varones solamente": "V", "mujeres solamente": "M", "varones y mujeres": "T"}


def norm(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().upper()
    return " ".join(s.replace(".", " ").replace("-", " ").split())


def cargar():
    d = pd.read_csv(os.path.join(HERE, "canton_1954.csv"))
    d["cat"] = d.categoria.map(CAT)
    tab = defaultdict(dict)     # (prov, unidad, cat) -> {concepto: valor}
    pag = {}
    for r in d.itertuples():
        if pd.notna(r.valor): tab[(r.provincia, r.unidad, r.cat)][r.concepto] = int(r.valor)
        pag[(r.provincia, r.unidad, r.cat)] = r.pagina_pdf
    return d, tab, pag


def partes(row):
    return {k: v for k, v in row.items() if k not in ("Inscriptos", "Votantes")}


def main():
    d, tab, pag = cargar()
    out = ["# Auditoría de la transcripción de Cantón 1954", "",
           "Generado por `auditar_1954.py` sobre `canton_1954.csv`. Complementa a `DIFERENCIAS_ORIGINAL_1954.md`: aquí se ubica la celda que "
           "explica cada diferencia y se agregan controles externos (Cantón 1958 y Wikipedia). Nada se corrigió.", ""]
    unidades = sorted({(p, u) for p, u, c in tab})

    # 2. celda culpable
    out += ["## 1. Celdas que no cierran, ubicadas", "",
            "Para cada diferencia entre varones + mujeres y el total impreso, la columna «sola» es la tabla que no cierra su propia fila "
            "(votantes ≠ suma de votos) por la misma cantidad: ahí está el error. «Imprenta» = las tres tablas cierran sus filas y aun así "
            "no suman (error del original que no se puede ubicar).", "",
            "| Distrito | Unidad | Concepto | Varones | Mujeres | Total | V+M−T | Dónde está | Págs. |", "|---|---|---|---:|---:|---:|---:|---|---|"]
    n1 = 0
    for p, u in unidades:
        V, M, T = (tab.get((p, u, c)) for c in "VMT")
        if not (V and M and T): continue
        res = {c: (r.get("Votantes", 0) - sum(partes(r).values())) for c, r in (("V", V), ("M", M), ("T", T))}
        for k in T:
            if k not in V or k not in M: continue
            dif = V[k] + M[k] - T[k]
            if dif == 0: continue
            n1 += 1
            # una diferencia en una celda de partido: la tabla con residuo de fila que la compensa es la sospechosa
            sosp = []
            if k not in ("Inscriptos", "Votantes"):
                if res["V"] == -dif: sosp.append("varones")
                if res["M"] == -dif: sosp.append("mujeres")
                if res["T"] == dif: sosp.append("total")
            elif k == "Votantes":
                if res["V"] == dif: sosp.append("varones")
                if res["M"] == dif: sosp.append("mujeres")
                if res["T"] == -dif: sosp.append("total")
            donde = " o ".join(sosp) if sosp else ("imprenta (las filas cierran)" if all(v == 0 for v in res.values()) else "sin ubicar")
            out.append("| %s | %s | %s | %d | %d | %d | %+d | %s | %s |" % (p, u, k, V[k], M[k], T[k], dif, donde,
                       "/".join(str(pag[(p, u, c)]) for c in "VMT")))
    out += ["", "%d diferencias." % n1, ""]

    # 3-4. participacion y proporcion peronista
    out += ["## 2. Participación y voto peronista raros", "",
            "| Distrito | Unidad | Tabla | Inscriptos | Votantes | Particip. | Peronista % | Motivo |", "|---|---|---|---:|---:|---:|---:|---|"]
    n2 = 0
    for p, u in unidades:
        info = {}
        for c in "VMT":
            r = tab.get((p, u, c))
            if not r or not r.get("Inscriptos") or not r.get("Votantes"): continue
            pe = r.get("Partido Peronista"); vot = r["Votantes"]
            info[c] = (r["Inscriptos"], vot, vot / r["Inscriptos"], (pe / vot) if pe is not None and vot else None)
        for c, (i, v, part, pe) in info.items():
            mot = []
            if part > 1: mot.append("más votantes que inscriptos")
            elif part < 0.6: mot.append("participación < 60 %")
            if c == "V" and "M" in info:
                if abs(part - info["M"][2]) > 0.12: mot.append("participación V/M difiere %.0f pp" % (100 * (part - info["M"][2])))
                if pe is not None and info["M"][3] is not None and abs(pe - info["M"][3]) > 0.15:
                    mot.append("peronismo V/M difiere %.0f pp" % (100 * (pe - info["M"][3])))
            if mot:
                n2 += 1
                out.append("| %s | %s | %s | %d | %d | %.1f %% | %s | %s |" % (p, u, c, i, v, 100 * part, "%.1f %%" % (100 * pe) if pe is not None else "", "; ".join(mot)))
    out += ["", "%d casos." % n2, ""]

    # 5. inscriptos contra 1958
    sys.path.insert(0, os.path.join(ROOT, "canton5865"))
    import datos
    T58, _ = datos.cargar_todo(); U58 = datos.unidades(T58, 1958)
    ins58 = {(p, norm(u)): r["ins"] for (p, u), r in U58.items() if isinstance(r["ins"], int)}
    out += ["## 3. Inscriptos 1954 contra 1958", "",
            "Cociente inscriptos 1958 / 1954 por unidad (tabla total; en San Luis y Tucumán, varones × 2 como aproximación). "
            "Se marcan las unidades que se apartan más de 35 % de la mediana de su provincia: un dígito mal leído o un cambio de límites.", "",
            "| Distrito | Unidad | Inscr. 1954 | Inscr. 1958 | Cociente | Mediana prov. |", "|---|---|---:|---:|---:|---:|"]
    rat = defaultdict(dict)
    for p, u in unidades:
        r = tab.get((p, u, "T")); f = 1
        if r is None and (p, u, "V") in tab: r, f = tab[(p, u, "V")], 2
        if not r or not r.get("Inscriptos"): continue
        k = (p, norm(u))
        if k in ins58: rat[p][u] = (r["Inscriptos"] * f, ins58[k])
    n3 = 0
    for p, us in rat.items():
        med = pd.Series({u: b / a for u, (a, b) in us.items()}).median()
        for u, (a, b) in sorted(us.items()):
            q = b / a
            if abs(q / med - 1) > 0.35:
                n3 += 1; out.append("| %s | %s | %d | %d | %.2f | %.2f |" % (p, u, a, b, q, med))
    out += ["", "%d unidades." % n3, ""]

    # 7. nombres
    out += ["## 4. Unidades de 1954 sin par en 1958", ""]
    prov58 = {p for p, _ in U58}
    sin = [(p, u) for p, u in unidades if p in prov58 and (p, norm(u)) not in ins58]
    out += ["- %s: %s" % (p, ", ".join(u for q, u in sin if q == p)) for p in sorted({p for p, _ in sin})] or ["Ninguna."]
    out += ["", "Provincias de 1954 que no están en 1958 por departamento: " + ", ".join(sorted({p for p, _ in unidades} - prov58)), ""]

    # 6. Wikipedia
    W = json.load(open(os.path.join(HERE, "wiki1954_prov.json"), encoding="utf8"))
    alias = {"Provincia Eva Perón": "La Pampa", "Provincia Presidente Perón": "Chaco"}
    out += ["## 5. Totales provinciales contra la Wikipedia", "",
            "La Wikipedia da los resultados por circunscripción (1954 fue uninominal) y en varias provincias faltan circunscripciones o el total; "
            "una diferencia grande puede ser de la Wikipedia. Peronista y UCR, tabla total (varones en San Luis y Tucumán).", "",
            "| Distrito | Peronista Cantón | Peronista Wiki | Dif. % | UCR Cantón | UCR Wiki | Dif. % |", "|---|---:|---:|---:|---:|---:|---:|"]
    for wp, wd in W.items():
        p = alias.get(wp, wp); c = "T" if (p, "T") in {(q, cc) for q, _, cc in tab} else "V"
        pe = sum(r.get("Partido Peronista", 0) for (q, u, cc), r in tab.items() if q == p and cc == c)
        uc = sum(r.get("Unión Cívica Radical", 0) for (q, u, cc), r in tab.items() if q == p and cc == c)
        a, b = wd.get("Partido Peronista", 0), wd.get("Unión Cívica Radical", 0)
        out.append("| %s%s | %d | %d | %+.1f | %d | %d | %+.1f |" % (p, " (varones)" if c == "V" else "", pe, a, 100 * (pe / a - 1) if a else 0, uc, b, 100 * (uc / b - 1) if b else 0))
    out.append("")
    open(os.path.join(HERE, "AUDITORIA_1954.md"), "w", encoding="utf8").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
