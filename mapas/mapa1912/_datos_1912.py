import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
# ---------------------------------------------------------------- datos: busqueda1912 + totales provinciales de la Wikipedia
import pandas as pd
import csv
SRC = os.path.join(HERE, "..", "..", "transcripciones", "busqueda1912")

KEY = {(u["prov"], norm(u["name"])): i for i, u in enumerate(U)}
# nombre de la fuente -> poligono(s) de 1914
ALIAS = {
    ("Mendoza", "Ciudad de Mendoza"): (["Capital"], None),
    ("Mendoza", "Luján"): (["Lujan de Cuyo"], None),
}
CAP_CIRC = {"Velez Sarsfield": 1, "San Cristóbal Sud": 2, "Santa Lucía": 3, "San Juan Evangelista": 4, "Flores": 5, "San Carlos Sud": 6,
            "San Carlos Norte": 7, "San Cristóbal Norte": 8, "Balvanera Oeste": 9, "Balvanera Sud": 10, "Balvanera Norte": 11,
            "Concepción": 12, "Monserrat": 13, "San Nicolás": 14, "San Bernardo": 15, "Belgrano": 16, "Palermo": 17, "Las Heras": 18,
            "Pilar": 19, "Socorro": 20}
CAP_CIRC = {norm(k): v for k, v in CAP_CIRC.items()}

# columna/candidato de la fuente -> codigo de fuerza. Cada partido usa los votos de su primer candidato (como la Wikipedia: «votos al partido»).
LAB = {
    "Capital Federal": {"Unión Cívica Radical": "UCR", "Socialista [columna 4]": "SOC", "Unión Cívica": "UC", "Unión Nacional": "UN", "Unión Comunal": "COM"},
    "Córdoba": {"Unión Cívica Radical": "UCR", "Unión Nacional": "UN", "Constitucional": "CNT", "Autonomista Nacional": "AUT"},
    "Mendoza": {"Candidato: Pedro Benegas": "PPO", "Candidato: Estanislao D. Gaviola": "OFI"},
    "Santa Fe": {"Candidato: Rogelio Araya": "UCR", "Candidato: Lisandro de la Torre": "LDS", "Candidato: Víctor P. Pesenti": "COA"},
}
# candidatos que acompanan al primero de la lista de un partido (no suman: la Wikipedia da los votos del partido = los del primer candidato)
ACOMP = {"Santa Fe": {"Candidato: Benjamín Ávalos", "Candidato: Miguel Coronado", "Candidato: Francisco G. Valdez",      # lista radical
                      "Candidato: Cornelio Casablanca", "Candidato: Ovidio A. Lagos", "Candidato: Fermín Lejarza",      # Liga del Sur
                      "Candidato: Domingo Regules", "Candidato: Hernán Saavedra Lamas", "Candidato: Gregorio García Vieyra"}}   # Coalicion
PARTY = {"UCR": "Unión Cívica Radical", "CNS": "Partido Conservador", "CNT": "Partido Constitucional", "AUT": "Autonomista Nacional",
         "OFI": "Partido Oficial", "PPO": "Partido Popular", "COA": "Partido de la Coalición", "LCO": "Partido Liberal de Corrientes",
         "ACO": "Partido Autonomista de Corrientes", "CCV": "Concentración Cívica", "PLT": "Partido Liberal de Tucumán",
         "UN": "Unión Nacional", "UC": "Unión Cívica", "SOC": "Partido Socialista", "LDS": "Liga del Sur",
         "COM": "Unión Comunal", "DRU": "Defensa Rural", "OTR": "Otros"}
PCOL = {"UCR": "#e10019", "CNS": "#22b5aa", "CNT": "#5cc9c0", "AUT": "#1a9a91", "OFI": "#30d5c8", "PPO": "#3fc2b8", "COA": "#6fe3da",
        "LCO": "#35aae0", "ACO": "#7fc8ec", "CCV": "#a3eee8", "PLT": "#2fb8ad", "UN": "#7b4fc9", "UC": "#000000", "SOC": "#ff9900",
        "LDS": "#005c9e", "COM": "#bdbdbd", "DRU": "#cfcfcf", "OTR": "#9a9a9a"}
# bloques como la Wikipedia: «Partidos Conservadores» suma las diez filas conservadoras de la tabla nacional (incluye las coaliciones provinciales)
BLOC = {c: "CON" for c in ("CNS", "CNT", "AUT", "OFI", "PPO", "COA", "LCO", "ACO", "CCV", "PLT")}
BLOC.update({"UCR": "UCR", "UN": "UN", "SOC": "SOC", "UC": "UC", "LDS": "LDS", "COM": "OTR", "DRU": "OTR", "OTR": "OTR"})
BLOCS = ["UCR", "CON", "UN", "SOC", "UC", "LDS"]


def fmt_n(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def fmt_p(v):
    return ("%.1f" % v).replace(".", ",")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --- cifras departamentales: Capital, Cordoba, Mendoza y 5 departamentos de Santa Fe (carpeta busqueda1912)
canton = {}      # (prov, nombre) -> dict(P, vacios, src)
for r in read(os.path.join(SRC, "datos_1912_depto.csv")):
    prov, dep = r["provincia"], r["departamento"]
    if prov not in LAB: continue          # San Juan: 32 colegios sin asignar a departamento; se pinta la provincia entera
    row = canton.setdefault((prov, dep), dict(prov=prov, name=dep, P={}, vacios=0, src=r["fuente_id"]))
    lab = r["partido_o_lista"]
    code = LAB[prov].get(lab)
    if code is None:
        if lab in ACOMP.get(prov, ()): continue
        if prov == "Capital Federal" or prov == "Córdoba": raise SystemExit("columna sin codigo: %s %s" % (prov, lab))
        if r["votos"] != "":
            row["P"]["OTR"] = row["P"].get("OTR", 0) + float(r["votos"])     # el resto de las candidaturas va a «otros»
        continue
    if r["votos"] == "":
        row["vacios"] += 1
    else:
        row["P"][code] = row["P"].get(code, 0) + float(r["votos"])

unit_src, unmapped = {}, []
for (prov, n), r in canton.items():
    if prov == "Capital Federal":
        k = CAP_CIRC.get(norm(n))
        idx = [KEY[("Capital Federal", norm("Circ. %02d" % k))]] if k else []
        why = None
    elif (prov, n) in ALIAS:
        names, why = ALIAS[(prov, n)]
        idx = [KEY[(prov, norm(x))] for x in names]
    else:
        k = (prov, norm(n))
        idx, why = ([KEY[k]] if k in KEY else []), None
    if not idx:
        if r["P"]: unmapped.append(r)
        continue
    for i in idx:
        assert i not in unit_src, (prov, n, U[i]["name"])
        unit_src[i] = (r, why, len(idx))

LOS_ANDES = {("Catamarca", "Antofagasta de la Sierra"), ("Jujuy", "Susques"), ("Salta", "Pastos Grandes"), ("Salta", "San Antonio de los Cobres")}
NOELIGE = set()      # en 1912 votaron las 13 provincias y la Capital

# --- totales provinciales: tablas de la Wikipedia («Elecciones legislativas de Argentina de 1912», Resultados por provincia)
# votos de cada partido = votos de su primer candidato; ins = electores registrados; tot = «total de votos»; base de %: suma de los votos a candidatos
PROV = {
    "Buenos Aires": dict(P={"CNS": 75010, "UC": 27818, "UN": 21042, "SOC": 4354}, tot=153602, ins=232000),
    "Capital Federal": dict(P={"UCR": 35721, "UC": 32749, "SOC": 32512, "UN": 29825, "COM": 17102, "DRU": 1643, "OTR": 36453}, tot=106157, ins=126303),
    "Catamarca": dict(P={"OFI": 12017, "OTR": 247}, tot=12434, ins=18332, bla=170),
    "Córdoba": dict(P={"CNT": 23582, "UCR": 15690, "UN": 14850}, tot=57148, ins=99929),
    "Corrientes": dict(P={"LCO": 14515, "ACO": 14367, "OTR": 8773, "UCR": 2702}, tot=40357, ins=53485),
    "Entre Ríos": dict(P={"CNS": 24058, "UCR": 21326}, tot=45384, ins=63184),
    "Jujuy": dict(P={"OFI": 4841, "UCR": 2657}, tot=8460, ins=12380),
    "La Rioja": dict(P={"UN": 4120, "UCR": 3724}, tot=11596, ins=15916),
    "Mendoza": dict(P={"PPO": 15833, "OFI": 8247, "OTR": 74}, tot=24467, ins=38500, bla=313),
    "Salta": dict(P={"CNS": 12404, "UCR": 2695, "OTR": 4367}, tot=19466, ins=26627),
    "San Juan": dict(P={"OFI": 8853, "CCV": 8593, "OTR": 88}, tot=17746, ins=21111, bla=194),
    "San Luis": dict(P={"CNS": 7867, "UN": 3432, "OTR": 4754}, tot=16442, ins=22787),
    "Santa Fe": dict(P={"UCR": 36747, "COA": 17856, "LDS": 17630, "SOC": 154, "OTR": 5958}, tot=78345, ins=98371),
    "Santiago del Estero": dict(P={"UN": 9509, "CNS": 6547}, tot=23136, ins=35261),
    "Tucumán": dict(P={"PLT": 29155}, tot=39891, ins=70815),
}
PROV["Santiago del Estero"]["P"] = {"UN": 9509, "AUT": 6547}      # el «Partido Autonomista Nacional» de la Wikipedia
assert sum(v["tot"] for v in PROV.values()) == 654631 and sum(v["ins"] for v in PROV.values()) == 935001       # cierran con la tabla nacional
SOLID = {"Buenos Aires", "Catamarca", "Corrientes", "Entre Ríos", "Jujuy", "La Rioja", "Salta", "San Juan", "San Luis", "Santiago del Estero", "Tucumán"}   # sin cuadro departamental: se pinta toda la provincia con su resultado
PROV_NOTE = {
    "Buenos Aires": "Expediente 19-D-1912: solo trae el cómputo provincial por candidato, no un cuadro por partido ni por distrito. Partido Conservador (Atencio) 75.010; Unión Cívica (Carballido) 27.818; Unión Nacional (Moreno) 21.042; Partido Socialista (Justo) 4.354.",
    "Capital Federal": "Expediente 12-D-1912 (cómputo distrital por candidato) y Cantón (1968).",
    "Catamarca": "Expediente 28-P-1912 (incluye la repetición del 28 de abril de once mesas anuladas). Partido Oficial (Castillo) 12.017 votos; el resto son 250 votos dispersos.",
    "Córdoba": "Expediente 3-D-1912. Partido Constitucional (Del Barco) 23.582; UCR (Molina) 15.690; Unión Nacional (Mateo Bas) 14.850.",
    "Corrientes": "Expediente 51-D-1912. Partido Liberal (Mora y Araujo) 14.515; Partido Autonomista (Breard) 14.367; Ezquer (Otros en la Wikipedia) 8.773; UCR (Blanco) 2.702.",
    "Entre Ríos": "Expediente 46-D-1912: sin matriz departamental. Partido Conservador (Carbó) 24.058; UCR (Laurencena) 21.326.",
    "Jujuy": "Partido Oficial (González Pérez) 4.841; UCR (Sánchez de Bustamante) 2.657 (la Wikipedia).",
    "La Rioja": "La Junta no completó el escrutinio y lo hizo la Cámara. Unión Nacional (Jaramillo) 4.120; UCR (Luna) 3.724.",
    "Mendoza": "Expediente 42-D-1912: Partido Popular (Benegas) 15.833; Partido Oficial (Gaviola) 8.247; 27 candidatos con 74 votos.",
    "Salta": "Expediente 49-D-1912: sin transcripción completa por mesa. Partido Conservador (Leguizamón) 12.404; UCR (Castellanos) 2.695; el resto, dispersos.",
    "San Juan": "Expediente 27-D-1912. Partido Oficial (Etchegaray) 8.853 y Concentración Cívica (Garro) 8.593: los dos van en Partidos Conservadores, así que el mapa por bloques no distingue entre ellos. La carpeta busqueda1912 trae 107 mesas en 32 colegios (cuatro candidatos), pero no están asignados a departamentos y sus sumas difieren algo del resumen provincial.",
    "San Luis": "Expediente 44-D-1912. Partido Conservador (Arancibia Rodríguez) 7.867; Unión Nacional (Origone) 3.432; Jofré, Rodríguez Jurado y Lucero (Otros en la Wikipedia) 4.417.",
    "Santa Fe": "Expediente 17-D-1912. Los totales de la Wikipedia (78.345) cuentan votos a candidatos; el diario Santa Fe del 16/4 da 74.878 sufragantes.",
    "Santiago del Estero": "Unión Nacional (Arias) 9.509; Partido Autonomista Nacional (Santillán) 6.547. Diferencia de actas 7.080.",
    "Tucumán": "Solo figura el Partido Liberal (Mariño) con 29.155 votos positivos, 73,1 % del total; la diferencia de actas es 10.736. El expediente 26-P-1912 (117 páginas, con 82 mesas anuladas y complementarias) está inventariado en busqueda1912 sin transcribir.",
}
GREY_T, GREY_N, GREY_P = "#cfcfcf", "#8c8c8c", "#e6dcc3"
KEYS = [[GREY_T, "Sin elección: territorio nacional"], [GREY_N, "Cifras subsumidas en otra unidad"],
        [GREY_P, "Sin cifras departamentales"]]


def analyse(P):
    P = {c: x for c, x in P.items() if x > 0}
    D = sum(P.values()) or None
    bloc = {b: 0 for b in BLOCS}
    for c, x in P.items():
        b = BLOC[c]
        if b in bloc: bloc[b] += x
    return dict(P=P, D=D, bloc=bloc)


def lines_of(P, D):
    out = [["P_" + c, int(round(x)), round(100 * x / D, 2)] for c, x in sorted(P.items(), key=lambda kv: -kv[1]) if x > 0]
    return out


def rec_from(a, extra_note=None, met=None, fill=None):
    D = a["D"]
    if not D: return None
    rec = {"lines": lines_of(a["P"], D), "metrics": met or []}
    w = max(a["bloc"], key=lambda b: a["bloc"][b])
    if a["bloc"][w] > 0:
        rec.update(w=w, q=round(100 * a["bloc"][w] / D, 2))
    else:
        rec["fill"] = GREY_N
    if extra_note: rec["note"] = extra_note
    return rec


GEN = "Lista incompleta: cada elector votaba por hasta dos tercios de los cargos y podía tachar y agregar nombres; las cifras son los votos del primer candidato de cada partido."
unit_rec, unit_an = {}, {}
for i, u in enumerate(U):
    p = u["prov"]
    if p in geom.TERR:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1912: sus habitantes no votaban."}
    elif (p, u["name"]) in LOS_ANDES:
        unit_rec[i] = {"fill": GREY_T, "lines": [], "note": "Territorio Nacional de Los Andes (1900-1943): sus habitantes no votaban (Cacopardo 1967)."}
    elif p in SOLID:
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin cuadro departamental. " + PROV_NOTE[p] + " El mapa pinta toda la provincia con este resultado."}
    elif i in unit_src:
        r, why, n = unit_src[i]
        if not r["P"]:
            unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Cantón marca las cifras de «%s» como subsumidas en una unidad mayor o no tomadas en cuenta (**, tomo I, Apéndice C): no hay cifra impresa y no es cero." % r["name"]}
            continue
        extras = []
        if norm(r["name"]) != norm(u["name"]) and p != "Capital Federal": extras.append("Nombre en la fuente: «%s»." % r["name"])
        if why: extras.append(why)
        if p == "Capital Federal":
            extras.append("Cantón (1968, t. II), una columna por partido. El título de la tabla dice 1912 pero el pie cita La Nación del 7 y 14/4/1916; los totales de las veinte circunscripciones coinciden con los de la Wikipedia 1912 (p. ej. Unión Cívica 32.739 contra 32.749), así que se tratan como de 1912. La columna 4 no lleva clave impresa y se rotula Socialista por una anotación manuscrita.")
        if p == "Córdoba":
            extras.append("Cantón (1968, t. II): cada columna es una lista y las cuatro suman los votantes del departamento. Constitucional y Autonomista Nacional se cuentan en Partidos Conservadores. La Wikipedia usa otras cifras provinciales (el máximo por candidato).")
        if p == "Mendoza":
            extras.append("Expediente 42-D-1912: suma de las cifras expresas de cada mesa (con las repeticiones del 28/4 en lugar de las mesas anuladas). Benegas es el Partido Popular y Gaviola el Oficial; ambos van en Partidos Conservadores, así que el departamento sale de un solo color. Los 188 votos de las mesas coinciden con el total del acta.")
            if r["name"] == "San Martín": extras.append("La mesa 7 no tiene cómputo en el expediente.")
        if p == "Santa Fe":
            extras.append("Diario Santa Fe (18, 20 y 23/4/1912), escrutinio de la Junta anterior al diploma del 29/4: votos del primer candidato de cada lista (Araya UCR, de la Torre Liga del Sur, Pesenti Coalición). Quedaban mesas complementarias pendientes.")
            if r["name"] == "Belgrano": extras.append("La fuente repite a Valdez con dos cifras (183 y 933); se usa Araya, 183.")
            if r["name"] == "Rosario": extras.append("Una cifra (Coronado) ilegible: no se usa, es acompañante de lista.")
        if p == "Santa Fe" or p == "Mendoza": extras.append(GEN)
        if r["vacios"] and p != "Mendoza": extras.append("%d celda(s) sin cifra en la fuente." % r["vacios"])
        a = analyse(r["P"]); unit_an[i] = a
        unit_rec[i] = rec_from(a, " ".join(extras) or None, [])
    elif p == "Santa Fe":
        unit_rec[i] = {"fill": GREY_P, "lines": [], "note": "Sin cifras: de los 19 departamentos solo 5 (Rosario, Las Colonias, San Lorenzo, Vera y Belgrano) tienen votos por candidato en el diario Santa Fe del 16 al 25/4/1912."}
    else:
        unit_rec[i] = {"fill": GREY_N, "lines": [], "note": "Sin fila para esta unidad en la base de 1912."}

disp = {}
for i, (r, why, n) in unit_src.items():
    p = U[i]["prov"]
    disp[i] = ("Circunscripción %d · %s" % (CAP_CIRC[norm(r["name"])], r["name"])) if p == "Capital Federal" else (r["name"] if n == 1 else U[i]["name"])

# provincias: totales de la Wikipedia
prov_an = {}
for p_, v_ in PROV.items():
    prov_an[p_] = dict(a=analyse(v_["P"]), ins=v_["ins"], vot=v_["tot"], bla=v_.get("bla"), par=100 * v_["tot"] / v_["ins"])
prov_rec = {}
for p in PROVS:
    if p in geom.TERR:
        prov_rec[p] = {"fill": GREY_T, "lines": [], "note": "Territorio nacional en 1912: sin voto."}
    else:
        t = prov_an[p]
        met = [["Inscriptos", fmt_n(t["ins"])], ["Votantes", fmt_n(t["vot"])], ["Participación", fmt_p(t["par"]) + " %"]]
        if t["bla"]: met.append(["En blanco", fmt_n(t["bla"])])
        prov_rec[p] = rec_from(t["a"], PROV_NOTE.get(p, "Total provincial según la Wikipedia (Elecciones legislativas de Argentina de 1912).") + " " + GEN, met)

# resultado nacional: tabla del articulo de Wikipedia (ver ../wikitop.py)
sys.path.insert(0, os.path.join(HERE, ".."))
import wikitop
cands, slices, partp, NAT_MET = wikitop.national(1912)
print("sin poligono:", [(r["prov"], r["name"]) for r in unmapped], file=sys.stderr)
_wins = {}
for i, rec in unit_rec.items():
    if rec.get("w"): _wins[rec["w"]] = _wins.get(rec["w"], 0) + 1
for p_ in SOLID:
    w_ = prov_rec[p_].get("w")
    print("  solida", p_, w_, prov_rec[p_].get("q"), file=sys.stderr)
print("unidades ganadas por bloque (sin contar las provincias solidas):", _wins, file=sys.stderr)

CAND = {
    "UCR": dict(n="Unión Cívica Radical", sub="UCR", logo="UCR", base="#e10019"),
    "CON": dict(n="Partidos Conservadores", sub="Conservadores y afines", logo="PC", base="#30d5c8", bar="#1fa89d", txt="#1a8f86"),
    "UN": dict(n="Unión Nacional", sub="Unión Nacional", logo="UN", base="#7b4fc9"),
    "SOC": dict(n="Partido Socialista", sub="Socialistas", logo="PS", base="#ff9900", bar="#e08700", txt="#b87500"),
    "UC": dict(n="Unión Cívica", sub="Capital Federal", logo="UC", base="#000000", bar="#000000", txt="#333333"),
    "LDS": dict(n="Liga del Sur", sub="Santa Fe", logo="LDS", base="#005c9e"),
    }
for c, col in PCOL.items():
    CAND["P_" + c] = dict(n=PARTY[c], base=col, minor=True)
