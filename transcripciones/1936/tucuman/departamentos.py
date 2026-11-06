"""Tucumán 1936: tabla por departamento (26-OV-1936).

Fuente principal: resumen impreso p.102 (filas 1-11 = colegios en el orden del acta).
Filas 1-8: lectura visible, revisada por el principal.
Filas 9-11 (Burruyacú, Trancas, Tafí) y fila 12 (total provincial) quedan bajo
la banda blanca/magenta del escaneo; se leyeron con canales R/B y contraste local
y se cotejaron con el renglón de total de cada departamento en la planilla
(p.98 Burruyacú, p.99 Trancas, p.101 Tafí; en p.101 la banda trae la impresión
invertida verticalmente).

Estados:
  firme            lectura visible sin duda
  dos_fuentes      leída igual en p.102 y en la planilla del departamento
  cierra           además, la suma de los 11 departamentos da exacto el total
                   proclamado (p.103) o el de la Wikipedia (PS 2.506)
  lectura_unica    una sola fuente bajo banda, dígitos legibles
  tentativo        dígitos dudosos; se conserva el literal, sin valor numérico
  ilegible         no se pudo leer; sin valor

Nada se imputa por diferencia: las cifras que «cierran» fueron leídas y el
cierre es un control, no la fuente.

Uso: python departamentos.py   (escribe departamentos.csv, celdas_departamento.csv
y CONTROL_DEPARTAMENTOS.json)
"""
import csv, json, hashlib, os

AQUI = os.path.dirname(os.path.abspath(__file__))
COLS = ["Padros", "Padilla", "Fioretti", "Prat_Gay", "Martinez", "Lopez_Garcia",
        "Aragon", "Mendoza_Padilla", "Lozano_Munoz", "E_Lopez", "Vischi", "Fornes",
        "nulos", "blancos"]
LISTA = {"Padros": "Concordancia", "Padilla": "Concordancia", "Fioretti": "Concordancia",
         "Prat_Gay": "UCR Laprida 147", "Martinez": "UCR Laprida 147", "Lopez_Garcia": "UCR Laprida 147",
         "Aragon": "UCR 24 de Setiembre 460", "Mendoza_Padilla": "UCR 24 de Setiembre 460",
         "Lozano_Munoz": "UCR 24 de Setiembre 460",
         "E_Lopez": "Partido Socialista", "Vischi": "Partido Socialista", "Fornes": "Partido Socialista",
         "nulos": "", "blancos": ""}
DEPTOS = ["Capital", "Famaillá", "Monteros", "Chicligasta", "Río Chico", "Graneros",
          "Leales", "Cruz Alta", "Burruyacú", "Trancas", "Tafí"]

# Filas 1-8 del resumen p.102, visibles.
FIRMES = [
    [6992, 6586, 5616, 5342, 4795, 4897, 12805, 12303, 11961, 1069, 1028, 1019, 87, 1441],
    [3194, 3198, 3084, 4481, 4441, 4460, 1518, 1554, 1489, 244, 244, 244, 15, 475],
    [3267, 3245, 2786, 3931, 3497, 3564, 1838, 1784, 1744, 42, 38, 40, 23, 475],
    [2813, 2775, 2682, 3363, 3213, 3300, 1879, 1839, 1868, 147, 147, 147, 20, 252],
    [3255, 3211, 2935, 3911, 3559, 3587, 972, 890, 896, 280, 279, 279, 13, 205],
    [698, 687, 682, 1712, 1668, 1684, 1086, 1074, 1051, 70, 70, 70, 4, 56],
    [1193, 1201, 1105, 1803, 1777, 1792, 825, 752, 749, 3, 3, 3, 13, 127],
    [5216, 5202, 5064, 3750, 3696, 3718, 2531, 2458, 2283, 543, 541, 541, 19, 662],
]
NOTA_FIRME = {("Capital", "blancos"): "cifra con marca superpuesta en p.102"}

# Filas 9-11: (valor, literal, estado, fuente)
F, D, C, U, T, I = "firme", "dos_fuentes", "cierra", "lectura_unica", "tentativo", "ilegible"
BAJO_BANDA = {
    "Burruyacú": {
        "Padros": (1295, "1295", C, "p102 f9 + p98 total"),
        "Padilla": (1221, "1221", D, "p102 f9 + p98 total"),
        "Fioretti": (1189, "1189", D, "p102 f9 + p98 total"),
        "Prat_Gay": (1708, "1708", C, "p102 f9 + p98 total"),
        "Martinez": (1628, "1628", C, "p102 f9 + p98 total"),
        "Lopez_Garcia": (1708, "1708", C, "p102 f9 + p98 total"),
        "Aragon": (1142, "1142", D, "p102 f9 + p98 total"),
        "Mendoza_Padilla": (1098, "1098", D, "p102 f9 + p98 total"),
        "Lozano_Munoz": (1110, "1110", D, "p102 f9 + p98 total"),
        "E_Lopez": (84, "84", C, "p102 f9 + p98 total"),
        "Vischi": (84, "84", D, "p102 f9 + p98 total"),
        "Fornes": (84, "84", D, "p102 f9 + p98 total"),
        "nulos": (None, "", I, "p102 f9 y p98: bajo banda"),
        "blancos": (None, "168?", T, "p102 f9, borde de banda; p98 no legible"),
    },
    "Trancas": {
        "Padros": (448, "448", C, "p99 total + p102 f10 (antes leído 443?)"),
        "Padilla": (420, "420", D, "p99 total + p102 f10"),
        "Fioretti": (None, "33?/387?", T, "p99 lee 331 o 337; p102 lee 387"),
        "Prat_Gay": (754, "754", C, "p99 total + p102 f10"),
        "Martinez": (701, "701", C, "p99 total; p102 f10 se había leído 731?"),
        "Lopez_Garcia": (711, "711", C, "p99 total + p102 f10"),
        "Aragon": (550, "550", D, "p99 total + p102 f10"),
        "Mendoza_Padilla": (None, "48?", T, "p99 bajo banda"),
        "Lozano_Munoz": (None, "4?7", T, "p99 bajo banda"),
        "E_Lopez": (2, "2", C, "p99 bajo banda; cierra PS 2.506"),
        "Vischi": (None, "2?", T, "p99 bajo banda"),
        "Fornes": (None, "", I, "p99 bajo banda"),
        "nulos": (None, "", I, "p99 bajo banda"),
        "blancos": (None, "", I, "p99 bajo banda"),
    },
    "Tafí": {
        "Padros": (2060, "2060", C, "p101 total (invertido) + p102 f11"),
        "Padilla": (2027, "2027", D, "p101 total + p102 f11"),
        "Fioretti": (None, "1886?/1883?", T, "p101 lee 1886, p102 1883 o 1885"),
        "Prat_Gay": (2148, "2148", C, "p101 total + p102 f11"),
        "Martinez": (1989, "1989", C, "p101 total + p102 f11"),
        "Lopez_Garcia": (2011, "2011", C, "p101 total + p102 f11"),
        "Aragon": (1566, "1566", U, "p101 total; p102 f11 se había leído 1766?"),
        "Mendoza_Padilla": (1573, "1573", D, "p101 total + p102 f11"),
        "Lozano_Munoz": (1501, "1501", U, "p101 total"),
        "E_Lopez": (22, "22", C, "p101 total; cierra PS 2.506"),
        "Vischi": (21, "21", U, "p101 total"),
        "Fornes": (22, "22", U, "p101 total"),
        "nulos": (11, "11", U, "p101 total"),
        "blancos": (284, "284", U, "p101 total, esquina doblada"),
    },
}

# Controles externos: proclamación p.103 y tabla de la Wikipedia (expediente + Cantón).
PROCLAMADOS = {"Prat_Gay": 32903, "Lopez_Garcia": 31432, "Martinez": 30964, "Padros": 30431}
WIKIPEDIA = {"E_Lopez": 2506, "Aragon": 26755}
# Fila 12 de p.102 (total provincial), bajo banda.
TOTAL_P102 = {"Padros": "30431", "Padilla": "2977?", "Fioretti": "2735?", "Prat_Gay": "3?90?",
              "Martinez": "3096?", "Lopez_Garcia": "3143?", "Aragon": "?671?", "Mendoza_Padilla": "25?9?"}

PAG_DEPTO = {}
for d, (a, b) in {"Capital": (72, 78), "Famaillá": (79, 81), "Monteros": (82, 84),
                  "Chicligasta": (85, 87), "Río Chico": (88, 89), "Graneros": (90, 91),
                  "Leales": (92, 93), "Cruz Alta": (95, 96), "Burruyacú": (97, 98),
                  "Trancas": (99, 99), "Tafí": (100, 101)}.items():
    for p in range(a, b + 1):
        PAG_DEPTO[p] = d


def filas():
    out = []
    for i, d in enumerate(DEPTOS):
        for j, c in enumerate(COLS):
            if i < 8:
                v = FIRMES[i][j]
                out.append(dict(departamento=d, fila_p102=i + 1, lista=LISTA[c], candidato_categoria=c,
                                votos=v, literal=str(v), estado=F, fuente="p102 fila %d" % (i + 1),
                                observacion=NOTA_FIRME.get((d, c), "")))
            else:
                v, lit, est, fu = BAJO_BANDA[d][c]
                out.append(dict(departamento=d, fila_p102=i + 1, lista=LISTA[c], candidato_categoria=c,
                                votos="" if v is None else v, literal=lit, estado=est, fuente=fu,
                                observacion=""))
    return out


CABEZA = {"Padilla": "Padros", "Fioretti": "Padros", "Mendoza_Padilla": "Aragon", "Lozano_Munoz": "Aragon",
          "Vischi": "E_Lopez", "Fornes": "E_Lopez"}
VECINOS = ("Burruyacú", "Tafí")


def extrapolar(rows):
    """Trancas (pedido del usuario, 5-nov-2026): completa sus celdas faltantes.

    Candidatos: votos del primero de su lista en Trancas x cociente candidato/primero
    en Burruyacú + Tafí (los vecinos con planilla leída). No altera el votos al
    partido (que es el primer candidato y está leído).
    Nulos y blancos: residuo de «blancos y anulados» de la Wikipedia (4.383) menos
    lo leído en los otros diez departamentos, tomando nulos de Burruyacú = 3 (trazo
    parcial en p102), repartido entre nulos y blancos con la proporción de los vecinos.
    """
    V = {(r["departamento"], r["candidato_categoria"]): r for r in rows}
    val = lambda d, c: V[(d, c)]["votos"] if V[(d, c)]["votos"] != "" else None
    for r in rows:
        r["votos_con_extrapolacion"] = r["votos"]
        r["extrapolacion"] = ""
    for c, h in CABEZA.items():
        r = V[("Trancas", c)]
        if r["votos"] != "": continue
        vs = [d for d in VECINOS if val(d, c) is not None]
        num = sum(val(d, c) for d in vs); den = sum(val(d, h) for d in vs)
        r["votos_con_extrapolacion"] = round(val("Trancas", h) * num / den)
        r["extrapolacion"] = "%s Trancas (%d) x %d/%d (%s/%s en %s); literal visible: %s" % (
            h, val("Trancas", h), num, den, c, h, "+".join(vs), r["literal"] or "ninguno")
    leidos = sum(r["votos"] for r in rows if r["candidato_categoria"] in ("nulos", "blancos")
                 and r["votos"] != "" and r["departamento"] != "Trancas")
    burr_nul, burr_bla = 3, 168          # lecturas parciales de p102 fila 9 (nulos «3», blancos «168?»)
    resto = 4383 - leidos - burr_nul - burr_bla
    nv = (val("Tafí", "nulos") or 0) + burr_nul
    bv = (val("Tafí", "blancos") or 0) + burr_bla
    nul = round(resto * nv / (nv + bv))
    for c, v in (("nulos", nul), ("blancos", resto - nul)):
        r = V[("Trancas", c)]
        r["votos_con_extrapolacion"] = v
        r["extrapolacion"] = ("residuo: 4.383 blancos y anulados (Wikipedia) - %d leídos en nueve departamentos - Burruyacú 3 nulos y 168 blancos "
                              "(lecturas parciales de p102) = %d, repartido %d:%d como en Burruyacú+Tafí" % (leidos, resto, nv, bv))
    return dict(nulos_blancos_residuo=resto, trancas_nulos=nul, trancas_blancos=resto - nul)


def main():
    rows = filas()
    ext = extrapolar(rows)
    with open(os.path.join(AQUI, "departamentos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    sumas, completos = {}, {}
    for c in COLS:
        vs = [r["votos"] for r in rows if r["candidato_categoria"] == c]
        completos[c] = all(v != "" for v in vs)
        sumas[c] = sum(v for v in vs if v != "")
    control = {"cierres": {}, "sin_cerrar": {}, "extrapolacion_trancas": ext}
    for c, ref in list(PROCLAMADOS.items()) + list(WIKIPEDIA.items()):
        fuente = "proclamación p103" if c in PROCLAMADOS else "Wikipedia"
        control["cierres"][c] = dict(suma=sumas[c], referencia=ref, fuente=fuente,
                                     completo=completos[c], diferencia=sumas[c] - ref)
    for c in COLS:
        if c not in control["cierres"]:
            control["sin_cerrar"][c] = dict(suma_leida=sumas[c], completo=completos[c],
                                            total_p102_literal=TOTAL_P102.get(c, ""))
    control["estados"] = {}
    for r in rows:
        control["estados"][r["estado"]] = control["estados"].get(r["estado"], 0) + 1
    control["nota_aragon"] = ("La suma leída de Aragón (26.712) no coincide con los 26.755 de la Wikipedia; "
                              "el total impreso de p102 se lee ?671?, compatible con 26.712. Se conserva la lectura.")

    # Copia anotada de celdas: departamento por página (cada página cae entera en un colegio).
    src = os.path.join(AQUI, "celdas.csv")
    with open(src, encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        cel = list(rd)
        campos = rd.fieldnames + ["departamento", "evidencia_departamento"]
    for r in cel:
        p = int(float(r["pagina_pdf"]))
        r["departamento"] = PAG_DEPTO.get(p, "")
        r["evidencia_departamento"] = ("página %d dentro del tramo del colegio (HANDOFF, límites por secuencia; "
                                       "p102 y cierres de p91/p93)" % p) if p in PAG_DEPTO else ""
    with open(os.path.join(AQUI, "celdas_departamento.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(cel)
    control["celdas_departamento"] = dict(
        celdas=len(cel), con_departamento=sum(1 for r in cel if r["departamento"]),
        sha256_celdas=hashlib.sha256(open(src, "rb").read()).hexdigest(),
        nota="Sin circuito: la asignación por bloque a circuitos sigue pendiente.")
    with open(os.path.join(AQUI, "CONTROL_DEPARTAMENTOS.json"), "w", encoding="utf-8") as f:
        json.dump(control, f, ensure_ascii=False, indent=2)
    print(json.dumps(control, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
