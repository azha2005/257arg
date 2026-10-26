"""Circuitos de 2025 donde es más común una secuencia de votos dada (perfil de un votante).
    python transferencias/perfil_votante.py
Puntaje = suma, elección por elección, del logaritmo de la proporción de votos (sin «No votó») que sacó en el circuito la
opción elegida: es el log de la probabilidad de que un votante al azar del circuito vote esa secuencia si sus votos fueran
independientes entre elecciones. Los votos están correlacionados, así que el valor absoluto no es una probabilidad real;
sirve para ordenar circuitos.
Enlace entre años: el circuito con la misma clave (distrito, sección, circuito) si su padrón es comparable; si no, la sección
con el mismo nombre (Santa Fe renumeró en 2023, otras provincias partieron circuitos); Capital antes de 2008 por
circunscripción (caba_cruce.py); si nada empareja, la provincia."""
import os, sys, math
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import estimar, caba_cruce

PERFIL = [("2003p", "López Murphy (Recrear)"), (2005, "UCR y aliados"), ("2007p", "Lavagna (UNA)"),
          (2009, "Acuerdo Cívico y Social"), ("2011p", "UDESO (UCR)"), (2013, "FPCyS / UNEN"), ("2015p", "Cambiemos"),
          ("2015b", "Cambiemos"), (2017, "Cambiemos"), ("2019p", "Juntos por el Cambio"), (2021, "Juntos por el Cambio"),
          ("2023p", "Juntos por el Cambio"), ("2023b", "La Libertad Avanza"), (2025, "Provincias Unidas")]
BASE = 2025
MIN_ELECTORES = 500


def tabla(anio):
    T, _ = estimar.load(anio)
    e = T.sum(1)
    V = T.drop(columns="No votó")
    return V, e


def alianza97(cand, nb):
    """Proporción de la Alianza (UCR + FREPASO y aliados) en diputados 1997 por departamento, emparejada por nombre."""
    src = open(os.path.join(ROOT, "mapa1997", "build_1997.py"), encoding="utf8").read()
    cods = src.split('"ALI": "', 1)[1].split('"', 1)[0].split()
    x = pd.read_excel(os.path.join(ROOT, "xlsx_resultados", "por_eleccion", "1997_diputados.xlsx"))
    ali = x[[c for c in cods if c in x]].fillna(0).sum(1)
    tot = x[[c for c in x.columns if c not in ("provincia", "unidad", "positivos", "total", "electores", "pos19", "pos")]].fillna(0).sum(1)
    pid = {v: k for k, v in estimar.DISTRITOS.items()}; pid["Capital Federal"] = "01"
    norm = lambda s: " ".join(estimar.unicodedata.normalize("NFD", str(s).upper()).encode("ascii", "ignore").decode().replace(".", " ").split())
    sh = {}
    for p, u, a, t in zip(x.provincia, x.unidad, ali, tot):
        d = pid.get(p)
        if d and t: sh.setdefault((d, norm(u)), [0, 0]); sh[(d, norm(u))][0] += a; sh[(d, norm(u))][1] += t
    cap = [v for (d, _), v in sh.items() if d == "01"]
    capv = sum(a for a, _ in cap) / sum(t for _, t in cap) if cap else np.nan
    prov = {}
    for (d, _), (a, t) in sh.items():
        prov.setdefault(d, [0, 0]); prov[d][0] += a; prov[d][1] += t
    out, lv = [], []
    for d, s, _ in cand:
        if d == "01": out.append(capv); lv.append("provincia"); continue
        v = sh.get((d, norm(nb.get((d, s), "?"))))
        if v: out.append(v[0] / v[1]); lv.append("sección")
        else: out.append(prov[d][0] / prov[d][1] if d in prov else np.nan); lv.append("provincia")
    return pd.Series(out, index=cand), pd.Series(lv, index=cand)


def main():
    Vb, eb = tabla(BASE)
    nb = estimar.secnames(BASE)
    cand = Vb.index[eb.reindex(Vb.index) >= MIN_ELECTORES]
    W = caba_cruce.pesos()
    score = pd.Series(0.0, index=cand); det = {}; nivel = {}
    for anio, cat in PERFIL:
        V, e = tabla(anio)
        a = int(str(anio).rstrip("pb"))
        if cat not in V: raise KeyError("%s no está en %s: %s" % (cat, anio, list(V.columns)))
        sh_c = V[cat] / V.sum(1)
        n = estimar.secnames(anio)
        S = V.copy(); S["sec"] = [n.get((d, s), "?") for d, s, _ in V.index]
        S = S.groupby([S.index.get_level_values(0), "sec"]).sum()
        sh_s = S[cat] / S.sum(1)
        P = V.groupby(level=0).sum(); sh_p = P[cat] / P.sum(1)
        if a < caba_cruce.CORTE:
            C = caba_cruce.cruzar(V, a).loc["01"]; C.index = [int(c[1:]) for c in C.index.get_level_values(-1)]
        out, lv = [], []
        for k in cand:
            d, s, c = k
            if d == "01" and a < caba_cruce.CORTE and c in W.index:
                w = W.loc[c]; num = (w * C[cat].reindex(w.index).fillna(0)).sum(); den = (w * C.sum(1).reindex(w.index).fillna(0)).sum()
                out.append(num / den if den else np.nan); lv.append("circ."); continue
            if k in sh_c.index and 0.4 < eb[k] / e[k] * (e.sum() / eb.sum()) < 2.5:
                out.append(sh_c[k]); lv.append("circuito"); continue
            key = (d, nb.get((d, s), "?"))
            if key in sh_s.index:
                out.append(sh_s[key]); lv.append("sección"); continue
            out.append(sh_p.get(d, np.nan)); lv.append("provincia")
        x = pd.Series(out, index=cand)
        det[str(anio)] = x; nivel[str(anio)] = pd.Series(lv, index=cand)
        score += np.log(x.clip(lower=1e-4)).fillna(math.log(1e-4))
    # 1997: Alianza por departamento (base de E. Calvo, códigos de mapa1997/build_1997.py); Capital como un todo
    x97, l97 = alianza97(cand, nb)
    det["1997"] = x97; nivel["1997"] = l97
    score += np.log(x97.clip(lower=1e-4)).fillna(math.log(1e-4))
    D = pd.DataFrame(det); L = pd.DataFrame(nivel)
    D["puntaje"] = score; D["electores_2025"] = eb.reindex(cand)
    D["seccion"] = [nb.get((d, s), "?") for d, s, _ in cand]
    D["n_circuito"] = (L == "circuito").sum(1) + (L == "circ.").sum(1)
    D = D.sort_values("puntaje", ascending=False)
    D.to_csv(os.path.join(HERE, "perfil_votante.csv"), encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print((100 * D.drop(columns=["puntaje", "electores_2025", "seccion", "n_circuito"]).head(25)).round(0).astype("Int64").to_string())
    print(D[["seccion", "electores_2025", "n_circuito", "puntaje"]].head(25).to_string())
    print("niveles de enlace (top 25):"); print(L.loc[D.index[:25]].apply(pd.Series.value_counts).fillna(0).astype(int).to_string())


if __name__ == "__main__":
    main()
