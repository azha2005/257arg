"""Cantón 1958 (presidente) y 1962 (diputados) por departamento, en el formato de agregar_circuitos.py
-> transferencias/circ_1958d.pkl y circ_1962d.pkl (sufijo d: armados por departamento desde Cantón para este par).
    python transferencias/canton_1958_1962.py
    RATIO=0.6,2.3 python transferencias/estimar.py 1958d 1962d
Los dos años salen de canton5865 (Cantón t. II corregido, el mismo de los atlas). Detalle y caveats en LEEME.md."""
import os, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "transcripciones/canton5865"))
from canton_1954_1958 import COD, norm

# 1962 -> partido de 1958 que lo contenía (creados en 1959-61; en Cantón 1958 figuran sin datos)
GRUPO = {"Berazategui": "Quilmes", "3 de Febrero": "General San Martín", "Escobar": "Pilar",
         "Hipólito Irigoyen": "Pehuajó", "San Cayetano": "Necochea", "Capitán Sarmiento": "Bartolomé Mitre"}
# La inferencia usa la unión completa Pilar+Tigre e Hipólito+sus cuatro orígenes
# en correspondencias.apply_pair; estas claves solo preparan la tabla intermedia.
ALIAS = {("Córdoba", "Ischilín"): "Ischillín", ("Salta", "Gral. Martín Miguel de Güemes"): "General Martín Miguel de Güemes",
         ("Santa Fe", "Nueve de Julio"): "9 de Julio"}
FUERA = {("Buenos Aires", "Florencio Varela")}    # 1962 sin inscriptos (9 celdas imputadas en canton5865)
B58 = {"UCRI": "UCRI", "URB": "UCRI", "UCRP": "UCRP", "CON": "CON"}
B62 = {"FJ": "FJ", "UCRI": "UCRI", "UCRP": "UCRP", "FNPC": "FNPC"}


def armar(U, anio, bloques):
    v, e = [], {}
    for (p, u), r in U.items():
        if p not in COD or (p, u) in FUERA or not isinstance(r["ins"], int): continue
        u = ALIAS.get((p, u), u)
        if p == "Buenos Aires": u = GRUPO.get(u, u)
        key = (COD[p], 0, norm(u))
        e[key] = e.get(key, 0) + r["ins"]
        for b, val in r["bloc"].items():
            v.append(dict(distrito_id=key[0], seccion_id=0, circuito=key[2], agrupacion_id=bloques.get(b, "OTRO " + str(b)),
                          votos_tipo="POSITIVO", v=val))
        v.append(dict(distrito_id=key[0], seccion_id=0, circuito=key[2], agrupacion_id="", votos_tipo="EN BLANCO", v=r["bla"] + r["nul"]))
    idx = ["distrito_id", "seccion_id", "circuito"]
    v = pd.DataFrame(v).groupby(idx + ["agrupacion_id", "votos_tipo"]).v.sum().reset_index()
    e = pd.Series(e); e.index = pd.MultiIndex.from_tuples(e.index, names=idx)
    pd.to_pickle((v, e), os.path.join(HERE, "circ_%sd.pkl" % anio))
    print(anio, "unidades", len(e), "electores", int(e.sum()), "votos", int(v.v.sum()))
    return set(e.index)


def main():
    import datos
    T, _ = datos.cargar_todo()
    k58 = armar(datos.unidades(T, 1958), 1958, B58)
    k62 = armar(datos.unidades(T, 1962), 1962, B62)
    print("solo 1958:", sorted(k58 - k62)); print("solo 1962:", sorted(k62 - k58))


if __name__ == "__main__":
    main()
