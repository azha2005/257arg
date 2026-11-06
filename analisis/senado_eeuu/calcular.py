"""Senado con el sistema de EE. UU. (4-nov-2026): 2 senadores por provincia (48), uno por vez, mayoría simple,
mandatos de 6 años y tres clases de 16. Cada provincia conserva su turno real (2021, 2023 o 2025, donde se
usa su elección de senadores) y suma otro turno; en ese año no eligió senadores, así que se usa su elección de
diputados nacionales como aproximación. Dos rotaciones posibles del segundo turno (A: el turno siguiente;
B: el anterior). Se compara con el Senado real que salió de esas tres elecciones (2 + 1 por provincia).
Fuente: tablas de los artículos de la Wikipedia (escrutinio definitivo), leídas por tablas.py."""
import json, os, re, unicodedata
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "tablas.json"), encoding="utf8"))
AÑOS = (2021, 2023, 2025)
NO = re.compile(r"Electores|blanco|nulo|Votos", re.I)

def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

# bloque de cada fuerza: primero excepciones por (año, provincia, nombre), después palabras clave
EXC = {
    "Juntos Somos Rio Negro": "Provinciales",
    "Hacemos por Cordoba": "Provincias Unidas / peronismo federal", "Hacemos por Nuestro Pais": "Provincias Unidas / peronismo federal",
    "Provincias Unidas": "Provincias Unidas / peronismo federal", "Vamos Corrientes": "Provincias Unidas / peronismo federal",
    "Frente Jujuy Crece": "Provincias Unidas / peronismo federal", "Por San Juan": "Provincias Unidas / peronismo federal",
    "Juntos por Entre Rios": "Juntos por el Cambio", "Union por San Luis": "Juntos por el Cambio", "Fuerza San Luis": "Juntos por el Cambio",
    "Unidos por San Luis": "Peronismo", "Mas para Entre Rios": "Peronismo", "Fuerza Entre Rios": "Peronismo",
    "Fuerza Justicialista Mendoza": "Peronismo", "Frente Justicialista": "Peronismo", "Frente Defendemos La Pampa": "Peronismo",
    "Federales Defendamos La Rioja": "Peronismo", "Frente de la Victoria": "Peronismo", "Fuerza San Juan": "Peronismo",
    "Fuerza Santacrucena": "Peronismo", "Tucuman Primero": "Peronismo", "Frente Civico por Santiago": "Peronismo",
    "Frente Unidos Podemos": "Provincias Unidas / peronismo federal",
}
CLAVE = [("libertad avanza", "La Libertad Avanza"), ("avanza libertad", "La Libertad Avanza"),
         ("frente de todos", "Peronismo"), ("union por la patria", "Peronismo"), ("fuerza patria", "Peronismo"),
         ("juntos", "Juntos por el Cambio"), ("cambia", "Juntos por el Cambio"), ("eco +", "Juntos por el Cambio"),
         ("concordia", "Provinciales"), ("neuquin", "Provinciales"), ("por santa cruz", "Provinciales"),
         ("saltenos", "Provinciales"), ("somos rio negro", "Provinciales"), ("independiente del chubut", "Provinciales"),
         ("despierta chubut", "Provinciales")]

def bloque(nombre):
    n = norm(nombre)
    for k, b in EXC.items():
        if n.startswith(norm(k)): return b
    for k, b in CLAVE:
        if k in n: return b
    return "?? " + nombre

# Bloques actuales del Senado (senado.gob.ar, «agrupados por bloques» y «listado por provincia», 4-nov-2026).
# Bancas del turno real: bloque de quien encabezó la lista ganadora (CABEZA). Turno agregado (diputados): bloque
# donde se sientan hoy los senadores de esa fuerza en esa provincia (POR_PROV); sin senador hoy, el más cercano.
ACTUAL = {"Justicialista": 22, "La Libertad Avanza": 21, "UCR": 10, "Convicción Federal": 3, "Frente PRO": 3,
          "Frente Cívico por Santiago": 2, "Movere Santa Cruz": 2, "Movimiento por Misiones": 2, "Provincias Unidas": 2,
          "Despierta Chubut": 1, "Independencia": 1, "Justicia Social Federal": 1, "La Neuquinidad": 1,
          "Primero los Salteños": 1}
CABEZA = {  # turno real: (provincia) -> bloque actual del primer senador de la lista ganadora
    "Buenos Aires": "Justicialista", "Catamarca": "Justicialista", "Capital Federal": "La Libertad Avanza",
    "Chaco": "La Libertad Avanza", "Chubut": "Frente PRO", "Córdoba": "La Libertad Avanza", "Corrientes": "UCR",
    "Entre Ríos": "La Libertad Avanza", "Formosa": "Justicialista", "Jujuy": "La Libertad Avanza",
    "La Pampa": "UCR", "La Rioja": "Justicialista", "Mendoza": "UCR", "Misiones": "Movimiento por Misiones",
    "Neuquén": "La Libertad Avanza", "Río Negro": "Justicialista", "Salta": "La Libertad Avanza",
    "San Juan": "Justicialista", "San Luis": "La Libertad Avanza", "Santa Cruz": "Movere Santa Cruz",
    "Santa Fe": "UCR", "Santiago del Estero": "Frente Cívico por Santiago", "Tierra del Fuego": "La Libertad Avanza",
    "Tucumán": "Justicialista"}
PER = {"Corrientes": "Provincias Unidas", "San Luis": "Justicia Social Federal",
       "Santiago del Estero": "Frente Cívico por Santiago"}  # resto: Justicialista
JXC = {"Capital Federal": "Frente PRO", "Chubut": "Frente PRO", "Entre Ríos": "Frente PRO", "Misiones": "Frente PRO",
       "Córdoba": "La Libertad Avanza", "Tucumán": "Independencia"}  # resto: UCR
FUERZA = {"Tucuman Primero": "Convicción Federal", "Vamos Corrientes": "UCR", "Hacemos": "Provincias Unidas",
          "Frente Renovador de la Concordia": "Movimiento por Misiones", "Por Santa Cruz": "Movere Santa Cruz",
          "La Neuquinidad": "La Neuquinidad", "Primero los Saltenos": "Primero los Salteños",
          "Movimiento Popular Neuquino": "MPN (sin bloque hoy)", "Juntos Somos Rio Negro": "JSRN (sin bloque hoy)"}

def bloque_actual(prov, fuerza, b, fuente):
    if fuente == "senadores": return CABEZA[prov]
    n = norm(fuerza)
    for k, v in FUERZA.items():
        if n.startswith(norm(k)): return v
    if b == "La Libertad Avanza": return b
    if b == "Peronismo": return PER.get(prov, "Justicialista")
    if b == "Juntos por el Cambio": return JXC.get(prov, "UCR")
    return "?? " + fuerza

def filas(clave, prov):
    return [r for r in T[clave][prov] if not NO.search(r["fuerza"])]

def ganador(anio, prov):
    """(fuerza, %, margen, fuente) del más votado de la provincia ese año."""
    fuente = "senadores" if prov in T[f"sen{anio}"] else "diputados"
    f = filas(("sen" if fuente == "senadores" else "dip") + str(anio), prov)
    return f[0]["fuerza"], f[0]["pct"], round(f[0]["pct"] - f[1]["pct"], 2), fuente

turno = {p: a for a in AÑOS for p in T[f"sen{a}"]}
provs = sorted(turno, key=norm)
assert len(provs) == 24

# Senado real: 2 bancas al primero y 1 al segundo de cada provincia, en su turno
real = Counter()
for p in provs:
    f = filas(f"sen{turno[p]}", p)
    real[bloque(f[0]["fuerza"])] += 2; real[bloque(f[1]["fuerza"])] += 1

res = {"real_por_lista": dict(real), "actual": ACTUAL}
assert sum(ACTUAL.values()) == 72
detalle = {}
for nombre, paso in (("A", 1), ("B", -1)):
    c, filas_d = Counter(), []
    for p in provs:
        a0 = turno[p]; a1 = AÑOS[(AÑOS.index(a0) + paso) % 3]
        for a in sorted((a0, a1)):
            fz, pct, mg, fu = ganador(a, p)
            b = bloque(fz); ba = bloque_actual(p, fz, b, fu); c[ba] += 1
            filas_d.append({"provincia": p, "clase": a, "fuerza": fz, "bloque": b, "bloque_actual": ba,
                            "pct": pct, "margen": mg, "fuente": fu})
    assert sum(c.values()) == 48
    res[nombre] = dict(c); detalle[nombre] = filas_d

if __name__ == "__main__":
    for k, v in res.items():
        print(k, sum(v.values()), sorted(v.items(), key=lambda x: -x[1]))
    for d in detalle["A"]:
        pass
    for k in ("A", "B"):
        for d in detalle[k]:
            if d["fuente"] == "diputados": print(k, d["clase"], d["provincia"], "|", d["fuerza"], "->", d["bloque_actual"])
    json.dump({"totales": res, "detalle": detalle}, open(os.path.join(HERE, "resultado.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
