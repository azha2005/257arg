"""Visor de Capital Federal 1864-2007 por circunscripción, desde el CD de Cantón y Jorrat
(*Elecciones en la ciudad*, tomo III, 2007).

  python datos/canton_ciudad/leer_cd.py        # CD -> cd_largo.csv / cd_elecciones.json
  "<venv Mosaic>/python.exe" mapas/capital_canton/geometria.py   # una vez
  python mapas/capital_canton/construir.py     # -> capital_1864_2007.html + control.json

No imputa ni corrige: copia el CD. Lo que la hoja no trae queda beige.
Excepción 1954: vista provisional por 14 circunscripciones con votos Wikipedia
(AGN/HCDN); conserva las 20 secciones y los datos originales del CD como variante.
"""
import collections
import csv
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(AQUI))
CDIR = os.path.join(R, "datos", "canton_ciudad")
sys.path.insert(0, AQUI)
import partidos as P  # noqa: E402
from electorado import estimar  # noqa: E402

GEO = json.load(open(os.path.join(AQUI, "geometria.json"), encoding="utf-8"))
ELEC = json.load(open(os.path.join(CDIR, "cd_elecciones.json"), encoding="utf-8"))
CTRL = json.load(open(os.path.join(CDIR, "cd_control.json"), encoding="utf-8"))

CARGO = {"DI": "Diputados nacionales", "SE": "Senador nacional", "PR": "Presidente", "PRDI": "Presidente y diputados",
         "CC": "Convencionales constituyentes", "JG": "Jefe de Gobierno", "LEG": "Legisladores porteños"}
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()


def cargo_de(tipo, titulo, n):
    t = re.sub(r"(2S|AS|V)$", "", tipo)
    t = re.sub(r"(1V|2V)$", "", t)
    base = CARGO.get(t, t)
    tt = " ".join(str(x) for x in titulo).upper()
    if "PROV" in tt and "NACIONALES" not in tt:
        base = "Legislatura de Buenos Aires"
    if n in (88,):
        base = "Convencionales estatuyentes"
    if tipo.startswith("JG1V"):
        base += ", 1.ª vuelta"
    if tipo.startswith("JG2V") or n == 105:
        base += ", 2.ª vuelta"
    if n == 73:
        base += ", 2.ª vuelta"
    if n == 74:
        base += " (septiembre)"
    if n == 72:
        base += " (marzo)"
    return base


def fecha_de(titulo):
    for t in titulo:
        t = str(t)
        if re.search(r"\b(1[89]|20)\d\d\b", t) and " DE " in t.upper():
            return t.strip().capitalize().replace(" De ", " de ")
    return ""


def parroquia(nombre):
    u = P.norm(nombre)
    u = re.sub(r"\bSUD\b", "SUR", u)
    u = {"CATEDRAL NORTE": "CATEDRAL AL NORTE", "CATEDRAL SUR": "CATEDRAL AL SUR", "SAN JUAN": "SAN JUAN EVANGELISTA"}.get(u, u)
    return u


def geom_de(n, anio):
    if anio < 1904:
        return "parr"
    if n in (60, 61):
        return "g51"
    return "g28" if anio >= 1973 else "g20"


# --- celdas
celdas = collections.defaultdict(dict)   # (n, sexo) -> {unidad: {col: valor}}
crudos = collections.defaultdict(list)
nombres = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(CDIR, "cd_largo.csv"), encoding="utf-8-sig")):
    n = int(r["n"])
    if int(r["anio"]) < 1904:
        u = parroquia(r["unidad"])
    else:
        try:
            u = int(float(r["unidad_num"]))
        except ValueError:
            continue
    nombres[n].setdefault(u, r["unidad"])
    d = celdas[(n, r["sexo"])].setdefault(u, {})
    if r["valor"] != "":
        d[r["columna"]] = float(r["valor"])
    elif r["crudo"].strip():
        crudos[(n, r["sexo"])].append((u, r["columna"], r["crudo"]))

# 1886: el CD trae tres versiones (Partidos Unidos, juarismo, policía) que no cierran entre sí.
# Se usa la de la policía: inscriptos, votantes y votos por los dos partidos.
import glob  # noqa: E402
import xlrd  # noqa: E402
V1886 = {10: (5, 10, 11), 11: (4, 7, 8)}
for n, (cv, cpu, cj) in V1886.items():
    f = glob.glob(os.path.join(CDIR, "cd", f"({n}) *"))[0]
    sh = xlrd.open_workbook(f, ignore_workbook_corruption=True).sheet_by_index(0)
    d = {}
    for r in range(sh.nrows):
        fila = sh.row_values(r)
        nm = str(fila[1]).strip()
        if not nm or not isinstance(fila[2], float) or nm.upper().startswith("TOTAL"):
            continue
        num = lambda x: x if isinstance(x, float) else None  # noqa: E731
        d[parroquia(nm)] = {c: v for c, v in (("INSCRIPTOS", num(fila[2])), ("VOTANTES", num(fila[cv])),
                                               ("PARTIDOS UNIDOS", num(fila[cpu])), ("JUARISMO", num(fila[cj])))
                           if v is not None}
        nombres[n][parroquia(nm)] = nm
    celdas[(n, "V")] = d

hojas = collections.defaultdict(list)
for e in ELEC:
    hojas[e["n"]].append(e)

# Las hojas de varones y de mujeres nombran distinto a las mismas listas («U. C. R.» / «UCR»,
# «JUSTICIALISTA» / «PJ») en las mismas posiciones. Con igual cantidad de columnas se empareja
# por posición y valen los nombres de la hoja de varones; si no (1995 senador: la de mujeres no
# trae Demócrata Cristiano), por nombre.
RENOMBRE_M = {}
for n, hs in hojas.items():
    cv = next((h["columnas"] for h in hs if h["sexo"] == "V"), None)
    cm = next((h["columnas"] for h in hs if h["sexo"] == "M"), None)
    if cv and cm:
        mapa = dict(zip(cm, cv)) if len(cv) == len(cm) else {c: c for c in cm}
        RENOMBRE_M[n] = {a: b for a, b in mapa.items() if a != b}
        celdas[(n, "M")] = {u: {mapa.get(c, c): v for c, v in d.items()} for u, d in celdas[(n, "M")].items()}
        crudos[(n, "M")] = [(u, mapa.get(c, c), v) for u, c, v in crudos[(n, "M")]]
        for h in hs:
            if h["sexo"] == "M":
                h["columnas"] = [mapa.get(c, c) for c in h["columnas"]]
                if h["total"]:
                    h["total"] = {mapa.get(c, c): v for c, v in h["total"].items()}

salida, control = [], []
for n in sorted(hojas):
    hs = hojas[n]
    e0 = hs[0]
    anio, tipo = e0["anio"], e0["tipo"]
    if not any(h["unidades"] for h in hs):
        control.append({"n": n, "anio": anio, "excluida": "la hoja no trae cifras por unidad"})
        continue
    g = geom_de(n, anio)
    # columnas en orden de aparición, unión de las hojas
    cols = []
    if n in V1886:
        cols = ["INSCRIPTOS", "VOTANTES", "PARTIDOS UNIDOS", "JUARISMO"]
    for h in ([] if n in V1886 else hs):
        for c in h["columnas"]:
            if c not in cols:
                cols.append(c)
    tipos = {c: P.tipo(c) for c in cols}
    # INSCRIPTOS manda sobre EMPADRONADOS; VOTANTES sobre VOTANTES SEGÚN ACTA
    for k, pref in (("ins", "INSCRIPTOS"), ("vot", "VOTANTES")):
        cs = [c for c in cols if tipos[c] == k]
        if len(cs) > 1:
            keep = next((c for c in cs if P.norm(c) == pref), cs[0])
            for c in cs:
                if c != keep:
                    tipos[c] = "descartada"
    pcols = [c for c in cols if tipos[c] in ("partido", "otros")]
    sexos_h = [h["sexo"] for h in hs]

    def unidades(sexo):
        if sexo == "T":
            if sexos_h == ["V"] or sexos_h == ["AS"]:
                return celdas[(n, sexos_h[0])]
            tot = {}
            for s in ("V", "M"):
                for u, d in celdas[(n, s)].items():
                    t = tot.setdefault(u, {})
                    for c, v in d.items():
                        t[c] = t.get(c, 0) + v
            # si a una unidad le falta una celda en una de las dos hojas, la suma no vale
            for u in tot:
                for c in cols:
                    a = celdas[(n, "V")].get(u, {}).get(c)
                    b = celdas[(n, "M")].get(u, {}).get(c)
                    if (a is None) != (b is None):
                        tot[u].pop(c, None)
            return tot
        return celdas[(n, sexo)]

    sexos = ["T"] + (["V", "M"] if sexos_h == ["V", "M"] else [])
    total_pp = collections.Counter()
    for u, d in unidades("T").items():
        for c in pcols:
            total_pp[c] += d.get(c, 0)
    # colores
    col_c, usados = {}, set()
    for c in sorted(pcols, key=lambda c: -total_pp[c]):
        cc, ok = P.color(c, anio) if tipos[c] == "partido" else ("#9a9a9a", True)
        if cc is None or cc in usados:
            cc = next(x for x in P.RESPALDO if x not in usados)
        usados.add(cc)
        col_c[c] = cc
    # datos por sexo
    U = {}
    for s in sexos:
        uu = unidades(s)
        U[s] = {}
        for u in sorted(uu, key=str):
            d = uu[u]
            fila = {"ins": next((d[c] for c in cols if tipos[c] == "ins" and c in d), None),
                    "vot": next((d[c] for c in cols if tipos[c] == "vot" and c in d), None),
                    "bla": sum(d[c] for c in cols if tipos[c] in ("bla",) and c in d) if any(
                        tipos[c] == "bla" and c in d for c in cols) else None,
                    "nul": sum(d[c] for c in cols if tipos[c] in ("nul", "blnul") and c in d) if any(
                        tipos[c] in ("nul", "blnul") and c in d for c in cols) else None,
                    "p": [d.get(c) for c in pcols]}
            U[s][str(u)] = fila
    # totales de la hoja (fila TOTAL del CD)
    tot_hoja = {}
    for h in hs:
        if h["total"] and n not in V1886:
            for c, v in h["total"].items():
                if v is not None:
                    tot_hoja[c] = tot_hoja.get(c, 0) + v
    # nombres de unidad
    nom = {}
    for u in sorted(set().union(*[set(U[s]) for s in sexos]), key=lambda x: (len(x), x)):
        x = nombres[n].get(int(u) if u.isdigit() else u, "")
        if not x or re.fullmatch(r"[\d.]+", x):
            x = GEO["nombres28"].get(str(u)) if g == "g28" else ""
        nom[str(u)] = x or ""
    avisos = [f"{c['sexo']}: {c['columna']}: suma de unidades {c['suma_unidades']:,.0f} contra total de la hoja "
              f"{c['total_hoja']:,.0f}" for c in CTRL if c["n"] == n]
    ilegibles = [f"{'Varones' if s == 'V' else 'Mujeres' if s == 'M' else ''} circ. {u}, {c}: «{v}»".strip()
                 for s in sexos_h for (u, c, v) in crudos[(n, s)]]
    notas = []
    for h in hs:
        for x in h["notas"]:
            if x not in notas:
                notas.append(x)
    censo = None
    if g == "parr":
        g = next(f"p{etapa}" for etapa in (1898, 1896, 1890, 1872, 1864) if anio >= etapa)
        faltan = set(U["T"]) - set(GEO[g])
        if faltan:
            raise ValueError(f"Elección {n}: parroquias sin geometría: {faltan}")
    if n == 21:
        censo = json.load(open(os.path.join(AQUI, "canton1895.json"), encoding="utf-8"))
        if set(censo["poblacion"]) != set(U["T"]) or set(GEO[g]) != set(U["T"]) | {"DIQUES"}:
            raise ValueError("Las parroquias del censo, el CD y el mapa de 1896 deben coincidir")
    salida.append({
        "n": n, "anio": anio, "tipo": tipo, "cargo": cargo_de(tipo, e0["titulo"], n),
        "titulo": str(e0["titulo"][1]) if len(e0["titulo"]) > 1 else "", "fecha": fecha_de(e0["titulo"]),
        "g": g, "sexos": sexos, "cols": [{"n": c, "c": col_c[c], "o": tipos[c] == "otros"} for c in pcols],
        "hayBla": any(tipos[c] == "bla" for c in cols), "hayNul": any(tipos[c] in ("nul", "blnul") for c in cols),
        "nom": nom, "u": U,
        "tot": {"ins": next((tot_hoja[c] for c in cols if tipos[c] == "ins" and c in tot_hoja), None),
                "vot": next((tot_hoja[c] for c in cols if tipos[c] == "vot" and c in tot_hoja), None),
                "p": [tot_hoja.get(c) for c in pcols]},
        "notas": notas, "avisos": avisos, "ilegibles": ilegibles,
    })
    if censo:
        salida[-1]["censo"] = {k: censo[k] for k in ("poblacion", "total")}
    salida[-1]["electorado"] = estimar(n, anio)


def candidatos_1904(eleccion):
    """Variante nominal con la misma cobertura que la hoja de diputados."""
    partidos = {
        "PAN": ("Partido Autonomista Nacional", "#74acdf"),
        "PA": ("Partido Autonomista", "#0067a5"),
        "PR": ("Partido Republicano", "#4169e1"),
        "PS": ("Partido Socialista", "#ff9900"),
        "UCR": ("Unión Cívica Radical", "#e10019"),
        "IND": ("Independientes", "#777777"),
    }
    indices = {sigla: i for i, sigla in enumerate(partidos)}
    archivo = os.path.join(R, "mapas", "mapa1904", "candidatos_1904.csv")
    unidades = {}
    with open(archivo, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["provincia"] != "Capital Federal":
                continue
            u = unidades.setdefault(r["numero"], {"p": [0] * len(partidos), "candidatos": []})
            i, votos = indices[r["bloque"]], int(r["votes"])
            u["p"][i] += votos
            u["candidatos"].append({"i": i, "v": votos, "n": r["candidate"]})
    if unidades.keys() != eleccion["u"]["T"].keys():
        raise ValueError("La cobertura nominal de diputados de Capital 1904 difiere de la del CD")
    for u in unidades.values():
        u["candidatos"].sort(key=lambda c: -c["v"])
    return {
        **eleccion, "fuente": "Atlas nacional de 1904, resultados por candidato",
        "nominal": True, "u": {"T": unidades},
        "cols": [{"n": n, "c": c, "o": False} for n, c in partidos.values()],
        "tot": None, "avisos": [], "ilegibles": [],
        "notas": ["Resultados por candidato del atlas nacional de 1904 (tabla de Wikipedia con referencias "
                  "a expedientes y diarios de sesiones del HCDN). Las barras suman por afiliación. "
                  "Cobertura: 11 circunscripciones que eligieron diputados."],
    }


import capital1954
for i,e in enumerate(salida):
    if e["n"] == 24:
        e["por_candidato"] = candidatos_1904(e)
    elif e['n'] == 62:
        salida[i], control54 = capital1954.para_visor(e)
        json.dump(control54, open(os.path.join(AQUI, 'CONTROL_CAPITAL_1954.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# --- control: ganadores por elección y colores de respaldo usados por ganadores
for e in salida:
    gan = collections.Counter()
    for u, f in e["u"]["T"].items():
        vs = [(v or 0) if not e["cols"][i]["o"] else -1 for i, v in enumerate(f["p"])]
        if not any(v and v > 0 for v in vs):
            continue
        m = max(vs)
        w = [i for i, v in enumerate(vs) if v == m]
        gan["(empate)" if len(w) > 1 else e["cols"][w[0]]["n"]] += 1
    resp = [c["n"] for c in e["cols"] if c["c"] in P.RESPALDO and c["n"] in gan]
    control.append({"n": e["n"], "anio": e["anio"], "cargo": e["cargo"], "unidades": len(e["u"]["T"]),
                    "ganadores": dict(gan), "ganadores_con_color_de_respaldo": resp})

json.dump(control, open(os.path.join(AQUI, "control.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
html = open(os.path.join(AQUI, "plantilla.html"), encoding="utf-8").read()
geometrias = {k: v for k, v in GEO.items() if k not in {"control1896", "nombres28"}}
# La presidencial usa el cuadro de prensa y mantiene sus marcas y cifras parciales.
prensa = open(os.path.join(R, "mapas", "mapa1874pres", "atlas_1874pres.html"), encoding="utf-8").read()
mapas1874, notas1874 = prensa.split("<main>", 1)[1].split("</main>", 1)
# Limpieza de estilo (Hallmark): sin puntos medios ni rayas en el texto del recorte de 1874.
notas1874 = notas1874.replace("Mitre 14.971 · Alsina–Avellaneda 12.103 · Diferencia 2.868", "Mitre 14.971, Alsina-Avellaneda 12.103, diferencia 2.868")
notas1874 = re.sub(r"(\d)–(\d)", r" a ", notas1874).replace("Alsina–Avellaneda", "Alsina-Avellaneda")
mapas1874 = mapas1874.replace("Alsina–Avellaneda", "Alsina-Avellaneda")
# Fichas y títulos: la raya del diario (cifra ausente) pasa a «sin cifra» y los puntos medios a frases.
def _ficha(m):
    t = m.group(2).replace(" — ", " sin cifra ").replace(" —", " sin cifra").replace(" · ", ". ")
    return m.group(1) + t + m.group(3)
mapas1874 = re.sub(r'(data-ficha=")([^"]*)(")', _ficha, mapas1874)
mapas1874 = re.sub(r"(<title>)([^<]*)(</title>)", _ficha, mapas1874)
html = html.replace("<!-- MAPAS_1874 -->", mapas1874)
html = html.replace("<!-- NOTAS_1874 -->", notas1874.split("<script>", 1)[0])
pos1874 = next(i for i, e in enumerate(salida) if e["n"] == 5) + 1
salida.insert(pos1874, {"n": 107, "anio": 1874, "cargo": "Presidente (abril)", "g": "p1872"})
datos = json.dumps({"E": salida, "G": geometrias}, ensure_ascii=False, separators=(",", ":"))
html = html.replace("/*__DATOS__*/null", datos)
open(os.path.join(AQUI, "capital_1864_2007.html"), "w", encoding="utf-8").write(html)
print(len(salida), "elecciones;", sum(1 for c in control if "excluida" in c), "excluidas;",
      f"{len(datos) / 1e6:.2f} MB de datos")
for c in control:
    if "excluida" not in c:
        print(c["n"], c["anio"], c["cargo"][:28].ljust(28), c["ganadores"], ("RESPALDO " + str(c["ganadores_con_color_de_respaldo"])) if c["ganadores_con_color_de_respaldo"] else "")
