"""Reparto de las 257 bancas por provincia con el censo 2022 (Ley 22.847, «ley Bignone»).
    python analisis/uninominal/reparto.py   -> reparto.csv
Ley 22.847: un diputado cada 161.000 habitantes o fraccion no menor de 80.500, mas 3 por distrito,
y ningun distrito con menos de los que tenia (art. 3/4; piso de 5 en la practica).
Dos versiones: «literal» (la ley tal cual con 2022, la Camara crece) y «257» (se busca el cociente
que deja la Camara en 257, con los mismos +3, piso de 5 y la garantia de no perder bancas)."""
import os, csv
OUT = os.path.dirname(os.path.abspath(__file__))
# Censo 2022, poblacion en viviendas particulares: suma de POB_TOT_P de los radios de CONICET
# (RADIOS_2022_V2025-1; 45.618.784 hab., sin viviendas colectivas ni situacion de calle). Ver construir_radios.py.
CENSO = {"01": ("Capital Federal", 3095454), "02": ("Buenos Aires", 17408906), "03": ("Catamarca", 427625),
         "04": ("Córdoba", 3812064), "05": ("Corrientes", 1209671), "06": ("Chaco", 1124603),
         "07": ("Chubut", 589454), "08": ("Entre Ríos", 1415097), "09": ("Formosa", 605507),
         "10": ("Jujuy", 809364), "11": ("La Pampa", 359193), "12": ("La Rioja", 382453),
         "13": ("Mendoza", 2030773), "14": ("Misiones", 1273347), "15": ("Neuquén", 708578),
         "16": ("Río Negro", 747697), "17": ("Salta", 1434225), "18": ("San Juan", 819445),
         "19": ("San Luis", 540548), "20": ("Santa Cruz", 335677), "21": ("Santa Fe", 3519059),
         "22": ("Santiago del Estero", 1057749), "23": ("Tucumán", 1727337), "24": ("Tierra del Fuego", 184958)}
ACTUAL = {"01": 25, "02": 70, "03": 5, "04": 18, "05": 7, "06": 7, "07": 5, "08": 9, "09": 5, "10": 6, "11": 5,
          "12": 5, "13": 10, "14": 7, "15": 5, "16": 5, "17": 7, "18": 6, "19": 5, "20": 5, "21": 19, "22": 7,
          "23": 9, "24": 5}
assert sum(ACTUAL.values()) == 257


def reparto(q, garantia=True):
    r = {}
    for d, (_, p) in CENSO.items():
        n = p // q + (1 if p % q >= q / 2 else 0) + 3
        n = max(n, 5)
        if garantia: n = max(n, ACTUAL[d])
        r[d] = n
    return r




if __name__ == "__main__":
    lit = reparto(161000)
    # el mayor cociente que da 257 (con garantia, el excedente solo baja si q sube)
    lo, hi = 161000, 2_000_000
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if sum(reparto(mid).values()) > 257: lo = mid
        else: hi = mid
    q257 = hi
    r257 = reparto(q257)
    sin_gar = None
    for q in range(150000, 400000, 50):
        if sum(reparto(q, False).values()) == 257: sin_gar = q; break
    r257s = reparto(sin_gar, False) if sin_gar else {}
    with open(os.path.join(OUT, "reparto.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["distrito", "provincia", "censo2022", "actual", "literal_161000", "c257_garantia", "c257_sin_garantia"])
        for d, (nom, p) in CENSO.items():
            w.writerow([d, nom, p, ACTUAL[d], lit[d], r257[d], r257s.get(d, "")])
    print("censo total", sum(p for _, p in CENSO.values()))
    print("literal:", sum(lit.values()), "| 257 con garantia: cociente", q257, sum(r257.values()),
          "| sin garantia: cociente", sin_gar, sum(r257s.values()))
    for d, (nom, p) in CENSO.items():
        print(f"{nom:22s} {ACTUAL[d]:3d} {lit[d]:4d} {r257[d]:4d} {r257s.get(d, '-'):>4}")
