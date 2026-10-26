"""Prepara la base departamental para el escenario 2027: junta 2023 (general y PASO por lista) y 2019 (FRENTE NOS)
sobre las unidades del mapa (Departamentos_2010 + Lezama + 15 comunas). Escribe base27.pkl.

Todo sale de la DINE (escrutinio provisorio por mesa, agregado por seccion):
  datos_oficiales/2023/agregado.pkl             generales 2023 (presidente)
  datos_oficiales/2023_paso/presidente_paso_por_lista_seccion.csv   PASO 2023 por lista (Massa, Grabois, Bullrich, Larreta)
  datos_oficiales/2019/agregado.pkl             generales 2019 (Frente NOS = Gomez Centurion)
"""
import os, sys, pickle, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from names import norm

ROOT = os.path.join(HERE, "..")
raw = pickle.load(open(os.path.join(HERE, "units_raw.pkl"), "rb"))
U = sorted(raw, key=lambda u: (u["prov"], int(u["name"].split()[1]) if u["prov"] == "Capital Federal" else u["name"]))

D2P = {1: "Capital Federal", 2: "Buenos Aires", 3: "Catamarca", 4: "Córdoba", 5: "Corrientes", 6: "Chaco", 7: "Chubut",
       8: "Entre Ríos", 9: "Formosa", 10: "Jujuy", 11: "La Pampa", 12: "La Rioja", 13: "Mendoza", 14: "Misiones",
       15: "Neuquén", 16: "Río Negro", 17: "Salta", 18: "San Juan", 19: "San Luis", 20: "Santa Cruz", 21: "Santa Fe",
       22: "Santiago del Estero", 23: "Tucumán", 24: "Tierra del Fuego"}

IDX = {}
for i, u in enumerate(U):
    if u["name"] == "Islas Malvinas":
        continue
    IDX[(u["prov"], norm(u["name"]))] = i


def _find(prov, *frag):
    """unidad de la provincia cuyo nombre normalizado contiene todos los fragmentos"""
    c = [i for (p, n), i in IDX.items() if p == prov and all(f in n for f in frag)]
    assert len(c) == 1, (prov, frag, c)
    return c[0]


# nombre normalizado en la base DINE -> unidad del mapa (los nombres de Departamentos_2010 son otros)
ALIAS_FRAG = {
    ("La Rioja", "vicentepe"): ("La Rioja", "generalangelv"),
    ("La Rioja", "juanfacundoquiroga"): ("La Rioja", "generaljuanf"),
    ("La Rioja", "ortizdeocampo"): ("La Rioja", "generalocampo"),
    ("La Rioja", "generalangelv"): ("La Rioja", "generalangelv"),
    ("Río Negro", "pilcaniyeu"): ("Río Negro", "pilnaniyeu"),
    ("San Luis", "juanmartin"): ("San Luis", "lacapital"),
    ("San Luis", "pueyrredon"): ("San Luis", "lacapital"),
    ("Buenos Aires", "arrecifes"): ("Buenos Aires", "mitre"),
    ("Santiago del Estero", "pellegrini"): ("Santiago del Estero", "pelegrini"),
    ("Tucumán", "alberdi"): ("Tucumán", "alberdi"),
    ("Chaco", "1odemayo"): ("Chaco", "1demayo"),
    ("Chubut", "pasodeindios"): ("Chubut", "pasodelosindios"),
    ("Chubut", "pasodelosindios"): ("Chubut", "pasodelosindios"),
}

# secciones de la DINE que se suman a otra unidad (mismo criterio que mapa2013)
MERGE = {
    (24, "3"): (24, "1"),       # Antartida Argentina -> Ushuaia
}


def unit_for(d, sid, name):
    """-> indice de unidad del mapa o None"""
    p = D2P[int(d)]
    if p == "Capital Federal":
        return IDX[(p, norm("Comuna %d" % int(sid)))]
    n = norm(str(name))
    if (p, n) in IDX:
        return IDX[(p, n)]
    for (pp, frag), (p2, tgt) in ALIAS_FRAG.items():
        if pp == p and frag in n:
            return _find(p2, tgt)
    if p == "Tucumán" and n.startswith("famail"):
        return _find("Tucumán", "famal")
    if p == "Tucumán" and n.startswith("famall"):
        return _find("Tucumán", "famal")
    return None


def to_unit_map(df, keycols=("distrito_id", "seccion_id", "seccion_nombre")):
    """DataFrame con distrito_id, seccion_id, seccion_nombre -> dict (d, sid) -> unidad, aplicando MERGE"""
    out, bad = {}, []
    names = {}
    for r in df[list(keycols)].drop_duplicates().itertuples(index=False):
        names[(int(r[0]), str(r[1]))] = r[2]
    for (d, sid), nm in names.items():
        k = (d, sid)
        if k in MERGE:
            tgt = MERGE[k]
            nm2 = names.get(tgt)
            i = unit_for(tgt[0], tgt[1], nm2 if nm2 is not None else "")
        else:
            i = unit_for(d, sid, nm)
        if i is None:
            bad.append((d, sid, nm))
        else:
            out[k] = i
    return out, bad


def load_gen(year):
    a = pickle.load(open(os.path.join(ROOT, "../datos_oficiales", str(year), "agregado.pkl"), "rb"))[0]
    q = a[a.cargo_nombre.str.startswith("PRESIDENTE")].copy()
    q["v"] = q["v"].astype(int)
    return q


def agg_gen(q, year=2023):
    if year == 2019:
        # mismos ids que 2023 salvo Santa Fe (renumerado): ahi se empareja por nombre
        m23, _ = to_unit_map(load_gen(2023))
        m, bad = {}, []
        for r in q[["distrito_id", "seccion_id", "seccion_nombre"]].drop_duplicates().itertuples(index=False):
            d, sid = int(r[0]), str(r[1])
            if d == 21:
                nm = str(r[2]).replace("Nueve de Julio", "9 de Julio")
                i = unit_for(d, "x", nm) if nm.strip().lower() != "rosario" else IDX[("Santa Fe", norm("Rosario"))]
            else:
                i = m23.get((d, sid))
            if i is None:
                bad.append((d, sid, r[2]))
            else:
                m[(d, sid)] = i
    else:
        m, bad = to_unit_map(q)
    assert not bad, bad
    res = {}
    for r in q.itertuples(index=False):
        i = m[(int(r.distrito_id), str(r.seccion_id))]
        e = res.setdefault(i, dict(P={}, bla=0, nul=0))
        if r.votos_tipo == "POSITIVO":
            e["P"][r.agrupacion_nombre] = e["P"].get(r.agrupacion_nombre, 0) + r.v
        elif r.votos_tipo == "EN BLANCO":
            e["bla"] += r.v
        elif r.votos_tipo in ("NULO", "RECURRIDO", "IMPUGNADO"):
            e["nul"] += r.v
    return res


if __name__ == "__main__":
    g23 = agg_gen(load_gen(2023))
    g19 = agg_gen(load_gen(2019), 2019)
    paso = pd.read_csv(os.path.join(ROOT, "../datos_oficiales", "2023_paso", "presidente_paso_por_lista_seccion.csv"),
                       dtype={"seccion_id": str, "distrito_id": str})
    pm, _ = to_unit_map(load_gen(2023))     # mismos ids que la general 2023 (los nombres del csv vienen con la codificacion rota)
    assert all((int(d), str(s_)) in pm for d, s_ in paso[["distrito_id", "seccion_id"]].drop_duplicates().itertuples(index=False))
    LISTS = {"3005": "massa", "3006": "grabois", "3007": "larreta", "3008": "bullrich"}
    pas = {}
    for r in paso[paso.votos_tipo == "POSITIVO"].itertuples(index=False):
        i = pm[(int(r.distrito_id), str(r.seccion_id))]
        e = pas.setdefault(i, dict(massa=0, grabois=0, larreta=0, bullrich=0, otros=0))
        e[LISTS.get(str(r.lista_numero), "otros")] += int(r.votos_cantidad)
    nU = len([u for u in U if u["name"] != "Islas Malvinas"])
    print("unidades con dato: 2023=%d 2019=%d PASO=%d de %d" % (len(g23), len(g19), len(pas), nU))
    miss = lambda d: [(U[i]["prov"], U[i]["name"]) for i, u in enumerate(U) if u["name"] != "Islas Malvinas" and i not in d]
    print("sin 2023:", miss(g23)); print("sin 2019:", miss(g19)); print("sin PASO:", miss(pas))
    pickle.dump(dict(U=[(u["prov"], u["name"], u["kind"]) for u in U], g23=g23, g19=g19, paso=pas),
                open(os.path.join(HERE, "base27.pkl"), "wb"))
    t = {}
    for e in g23.values():
        for k, v in e["P"].items(): t[k] = t.get(k, 0) + v
    print("2023 positivos por agrupacion:", t, sum(t.values()))
    t = {}
    for e in g19.values():
        for k, v in e["P"].items(): t[k] = t.get(k, 0) + v
    print("2019:", t)
    s = {k: sum(e[k] for e in pas.values()) for k in ("massa", "grabois", "larreta", "bullrich", "otros")}
    print("PASO:", s, "grabois/(massa+grabois)=%.3f larreta/(larreta+bullrich)=%.3f" % (
        s["grabois"] / (s["massa"] + s["grabois"]), s["larreta"] / (s["larreta"] + s["bullrich"])))
