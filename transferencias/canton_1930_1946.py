"""Cantón 1930 (diputados), 1937 (presidente), 1940 (diputados) y 1946 (presidente) por departamento, en el formato de
agregar_circuitos.py -> transferencias/circ_1930d.pkl, circ_1937d.pkl, circ_1940d.pkl y circ_1946d.pkl.
    python transferencias/canton_1930_1946.py
    RATIO=0.5,2 python transferencias/estimar.py 1937d 1946d      (también 1940d 1946d y 1930d 1946d)
1930: mapa1930/canton (transcripción del atlas, cotejada con Lupu-Stokes). 1937, 1940 y 1946: canton1937_1940 y canton1946.
Cantón publica 1937 y 1940 solo para los distritos donde ganó la oposición (t. I, p. XVI): 1937 Capital, Córdoba, La Rioja y
Tucumán; 1940 Capital, Córdoba, Entre Ríos, Santa Fe y Tucumán. Las cifras «**» (subsumidas en otra unidad) quedan fuera:
son los mismos partidos en los cuatro años, salvo San Cayetano y Gobernador Dupuy en 1946, que no existían antes.
Blanco y nulo = votantes menos la suma de las fuerzas publicadas (muchas tablas no traen blancos ni anulados), si es positivo."""
import os, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "mapas/mapa1930", "canton"))
from canton_1954_1958 import COD, norm
from spec import SPEC, BLOC as BLOC30

ALIAS = {("Santa Fe", "Nueve de Julio"): "9 de Julio"}
B30 = {"UCR": "UCR", "CD": "CD", "RAN": "RAN", "PS": "PS", "PSI": "PS"}       # PDP, lencinistas, bloquistas y varios: otros
BLANCO = {"En Blanco", "Blanco", "Observados y/o anulados", "Blanco y Anulados"}
B37 = {"Unión Cívica Radical": "UCR", "Concordancia": "CON", "Demócrata Nacional": "CON", "Socialista": "PS"}
B40 = {"Unión Cívica Radical": "UCR", "Unión Cívica Radical Capital": "UCR", "Concordancia": "CON", "Demócrata Nacional": "CON",
       "Unión Cívica Radical Santa Fe": "CON", "Socialista": "PS", "Partido Socialista": "PS"}
B46 = {"Conjunción Peronista": "PER", "Laborista": "PER", "Partido Laborista": "PER", "Partido Laborista de Tucumán": "PER",
       "Unión Cívica Radical (Junta Renovadora)": "PER", "Unión Democrática": "UD", "Unión Cívica Radical (Comité Nacional)": "UD",
       "Demócrata Nacional": "PDN"}


def guardar(R, anio):
    """R: (provincia, unidad) -> (inscriptos, votantes, {bloque: votos}, blancos publicados)"""
    v, e = [], {}
    for (p, u), (ins, vot, bloc, bla) in R.items():
        key = (COD[p], 0, norm(ALIAS.get((p, u), u)))
        e[key] = ins
        for b, x in bloc.items():
            v.append(dict(distrito_id=key[0], seccion_id=0, circuito=key[2], agrupacion_id=b, votos_tipo="POSITIVO", v=x))
        resto = max(vot - sum(bloc.values()), bla)
        v.append(dict(distrito_id=key[0], seccion_id=0, circuito=key[2], agrupacion_id="", votos_tipo="EN BLANCO", v=max(resto, 0)))
    idx = ["distrito_id", "seccion_id", "circuito"]
    v = pd.DataFrame(v).groupby(idx + ["agrupacion_id", "votos_tipo"]).v.sum().reset_index()
    e = pd.Series(e); e.index = pd.MultiIndex.from_tuples(e.index, names=idx)
    pd.to_pickle((v, e), os.path.join(HERE, "circ_%sd.pkl" % anio))
    print(anio, "unidades", len(e), "electores", int(e.sum()), "votos", int(v.v.sum()))
    return set(e.index)


def de_1930():
    R = {}
    for p, s in SPEC.items():
        for ln in open(os.path.join(ROOT, "mapas/mapa1930", "canton", s["file"]), encoding="utf8"):
            if ln.startswith("#") or "|" not in ln: continue
            n, x = ln.rstrip("\n").split("|")
            if x.strip() == "-": continue
            ins, vot, bloc = None, None, {}
            for c, y in zip(s["cols"], [None if t == "?" else int(t) for t in x.split()]):
                if y is None: continue
                if c == "INS": ins = y
                elif c == "VOT": vot = y
                else:
                    b = B30.get(BLOC30.get(c), "OTRO")
                    bloc[b] = bloc.get(b, 0) + y
            if ins: R[(p, n)] = (ins, vot, bloc, 0)
    return R


def de_csv(path, anio, bloques):
    d = pd.read_csv(os.path.join(ROOT, path), encoding="utf-8-sig")
    d = d[d.anio == anio]
    R = {}
    for (p, u), g in d.groupby(["provincia", "unidad"], sort=False):
        x = dict(zip(g.concepto, pd.to_numeric(g.valor, errors="coerce")))
        if pd.isna(x.get("Inscriptos")) or pd.isna(x.get("Votantes")): continue
        bloc, bla = {}, 0
        for c, y in x.items():
            if c in ("Inscriptos", "Votantes") or pd.isna(y): continue
            if c in BLANCO: bla += int(y); continue
            b = bloques.get(c, "OTRO")
            bloc[b] = bloc.get(b, 0) + int(y)
        R[(p, u)] = (int(x["Inscriptos"]), int(x["Votantes"]), bloc, bla)
    return R


def main():
    k46 = guardar(de_csv("transcripciones/canton1946/canton_1946.csv", 1946, B46), 1946)
    k30 = guardar(de_1930(), 1930)
    for anio, k in ((1930, k30),
                    (1937, guardar(de_csv("transcripciones/canton1937_1940/canton_1937_1940_1946.csv", 1937, B37), 1937)),
                    (1940, guardar(de_csv("transcripciones/canton1937_1940/canton_1937_1940_1946.csv", 1940, B40), 1940))):
        print(anio, "sin 1946:", sorted(k - k46))
    print("1946 sin 1930:", sorted(k46 - k30))


if __name__ == "__main__":
    main()
