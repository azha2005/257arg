"""Knesset por urna (kalpi): archivos expb.csv del Comite Central Electoral (media<N>.bechirot.gov.il/files/expb.csv,
bajados a datos_oficiales/israel/k<N>_expb.csv) y reparto de bancas.
    python proyeccion/israel/datos.py        # valida el reparto contra los resultados oficiales (Wikipedia)
Knesset 21 = abril 2019, 22 = septiembre 2019, 23 = marzo 2020, 24 = marzo 2021, 25 = noviembre 2022, 26 = 2026.
Los votos de doble sobre (soldados, diplomaticos, presos, hospitales) vienen como la localidad 9999 (99999 en 2019a),
sin electores propios: sus electores estan en el padron de su urna de origen."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "..", "datos_oficiales", "israel")
META = ["סמל ועדה", "ברזל", "שם ישוב", "סמל ישוב", "קלפי", "מספר קלפי", "ריכוז", "שופט", "בזב", "מצביעים", "פסולים",
        "כשרים", "חיצוניות", "קלפי אחרת"]    # las dos ultimas, nuevas en el expb.csv de 2026
DOBLE = (9999, 99999)
UMBRAL = 0.0325
NOMBRE = {21: "abril 2019", 22: "septiembre 2019", 23: "marzo 2020", 24: "marzo 2021", 25: "noviembre 2022"}

# Por eleccion: nombre de cada lista (letras de la boleta), acuerdos de excedentes y bloque. Fuente: Wikipedia
# (articulos de cada eleccion) y Times of Israel. Bloques: "bibi" = los que formaron o apoyaron el gobierno de
# Netanyahu en ese ciclo; "arabe" = listas arabes; "oposicion" = el resto (partidos judios no netanyahuistas).
LISTAS = {
    21: {"מחל": "Likud", "פה": "Kajol Lavan", "שס": "Shas", "ג": "UTJ", "ום": "Hadash-Taal", "אמת": "Laborismo",
         "ל": "Israel Beitenu", "טב": "Unión de la Derecha", "מרצ": "Meretz", "כ": "Kulanu", "דעם": "Raam-Balad",
         "נ": "Nueva Derecha", "ז": "Zehut", "נר": "Gesher"},
    22: {"מחל": "Likud", "פה": "Kajol Lavan", "ודעם": "Lista Conjunta", "שס": "Shas", "ל": "Israel Beitenu",
         "ג": "UTJ", "טב": "Yamina", "אמת": "Laborismo-Gesher", "מרצ": "Unión Democrática", "כף": "Otzma"},
    23: {"מחל": "Likud", "פה": "Kajol Lavan", "ודעם": "Lista Conjunta", "שס": "Shas", "ג": "UTJ",
         "אמת": "Laborismo-Gesher-Meretz", "ל": "Israel Beitenu", "טב": "Yamina", "נץ": "Otzma"},
    24: {"מחל": "Likud", "פה": "Yesh Atid", "שס": "Shas", "כן": "Kajol Lavan", "ב": "Yamina", "אמת": "Laborismo",
         "ג": "UTJ", "ל": "Israel Beitenu", "ט": "Sionismo Religioso", "ודעם": "Lista Conjunta", "ת": "Nueva Esperanza",
         "מרצ": "Meretz", "עם": "Raam"},
    25: {"מחל": "Likud", "פה": "Yesh Atid", "ט": "Sionismo Religioso", "כן": "Unidad Nacional", "שס": "Shas",
         "ג": "UTJ", "ל": "Israel Beitenu", "עם": "Raam", "ום": "Hadash-Taal", "אמת": "Laborismo", "מרצ": "Meretz",
         "ד": "Balad", "ב": "Hogar Judío"},
}
ACUERDOS = {24: [("ב", "ת"), ("פה", "ל"), ("מחל", "ט"), ("אמת", "מרצ"), ("שס", "ג")],
            25: [("אמת", "מרצ"), ("מחל", "ט"), ("כן", "פה"), ("שס", "ג")]}
BLOQUE = {e: {} for e in LISTAS}
for e, bibi, arabe in [(21, "מחל שס ג טב כ נ ז", "ום דעם"), (22, "מחל שס ג טב כף", "ודעם"),
                       (23, "מחל שס ג טב נץ", "ודעם"), (24, "מחל שס ג ט", "ודעם עם"), (25, "מחל שס ג ט", "עם ום ד")]:
    for k in LISTAS[e]:
        BLOQUE[e][k] = "bibi" if k in bibi.split() else "arabe" if k in arabe.split() else "oposicion"
# Antecesores (lista de la eleccion anterior de la que sale cada lista); lo que no esta: la misma letra
ANTECESORES = {
    (21, 22): {"מחל": ["מחל", "כ"], "ודעם": ["ום", "דעם"], "טב": ["טב", "נ"], "אמת": ["אמת", "נר"], "כף": []},
    (22, 23): {"אמת": ["אמת", "מרצ"], "נץ": ["כף"]},
    (23, 24): {"פה": ["פה"], "כן": ["פה"], "ת": ["מחל"], "ב": ["טב"], "ט": ["נץ"], "מרצ": ["אמת"], "עם": ["ודעם"]},
    (24, 25): {"ט": ["ט"], "כן": ["כן", "ת"], "ום": ["ודעם"], "ד": ["ודעם"], "ב": ["ב"]},
}

# 2026 (Knesset 26, 27-oct-2026): listas con su antecesor de 2022 (letras de k25), bloque y acuerdos de excedentes.
# Las letras de la boleta de 2026 todavia no estan: se emparejan por nombre cuando se publique el archivo de la noche.
# Fuentes: es/en.wikipedia «2026 Israeli legislative election» y «Party lists for the 2026 Israeli legislative
# election»; Times of Israel, «Israel's election takes shape as 38 parties submit slates» (sept-2026); Haaretz,
# «These Are the Candidates on the Final Knesset Slates» (8-sept-2026). Consultadas el 27-oct-2026.
LISTAS26 = {
    "Likud": (["מחל"], "bibi", "Netanyahu; absorbe Nueva Esperanza (Sa'ar), que en 2022 iba en Unidad Nacional"),
    "Juntos (Bennett-Lapid)": (["פה"], "oposicion", "Bennett 2026 + Yesh Atid; Bennett no se presento en 2022"),
    "Sionismo Religioso-Zehut": (["ט"], "bibi", "Smotrich + Feiglin; en 2022 iba en una lista comun con Otzma y Noam"),
    "Otzma Yehudit": (["ט"], "bibi", "Ben Gvir; mismo antecesor (lista comun de 2022)"),
    "Noam": (["ט"], "bibi", "Maoz; mismo antecesor"),
    "Shas": (["שס"], "bibi", ""),
    "UTJ": (["ג"], "bibi", "Degel HaTorah + Agudat Yisrael"),
    "Israel Beitenu": (["ל"], "oposicion", "Lieberman"),
    "Los Demócratas": (["אמת", "מרצ"], "oposicion", "Laborismo + Meretz (fusion de 2024)"),
    "Yashar (Eisenkot)": (["כן"], "oposicion", "Eisenkot y ex Kajol Lavan; en 2022 Eisenkot iba en Unidad Nacional"),
    "Reservistas-Nuevo Partido Economico": (["כן", "ב"], "oposicion", "Hendel y Zelekha; sin antecesor claro"),
    "Amcha Yisrael (Winter)": ([], "bibi", "Ofer Winter; el Times of Israel la ubica en el bloque de Netanyahu"),
    "Raam": (["עם"], "arabe", "Mansour Abbas"),
    "Lista Conjunta": (["ום", "ד"], "arabe", "Hadash + Taal + Balad, reunidos"),
    "Kajol Lavan (Gantz)": (["כן"], "oposicion", "anuncio que se retiraba el 19-oct; sigue en la lista de boletas"),
}
ACUERDOS26 = [("Juntos (Bennett-Lapid)", "Israel Beitenu"), ("Yashar (Eisenkot)", "Los Demócratas"),
              ("Lista Conjunta", "Raam"), ("Likud", "Sionismo Religioso-Zehut"), ("Shas", "UTJ")]


def region(locs):
    """Vecindad de cada localidad para el residuo de vecinas: su concejo regional (מועצה אזורית) y, si no tiene
    (ciudades, concejos locales), su subdistrito (נפה). Tabla de localidades del CBS en data.gov.il (resource
    5c78e9fa-c2e2-4771-93ff-7f400a12f7ba), bajada el 27-oct-2026 a localidades_cbs.csv."""
    global _REG
    if _REG is None:
        t = pd.read_csv(os.path.join(RAW, "localidades_cbs.csv"), encoding="utf-8-sig").set_index("סמל_ישוב")
        _REG = pd.Series(np.where(t["סמל_מועצה_איזורית"] > 0, "M" + t["סמל_מועצה_איזורית"].astype(str),
                                  "N" + t["סמל_נפה"].astype(str)), index=t.index)
    return _REG.reindex(np.asarray(locs)).fillna("X").to_numpy()


_REG = None


def cargar(n):
    """Una fila por urna: loc, kalpi, bzb (electores), votos por letra, doble (bool)."""
    path = os.path.join(RAW, "k%d_expb.csv" % n)
    for enc in ("utf-8-sig", "cp1255"):
        try:
            d = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    d = d[[c for c in d.columns if not c.startswith("Unnamed")]]
    kal = "קלפי" if "קלפי" in d else "מספר קלפי"
    out = pd.DataFrame({"loc": d["סמל ישוב"].astype(int), "nombre": d["שם ישוב"].astype(str).str.strip(),
                        "kalpi": d[kal].astype(float), "bzb": d["בזב"].astype(float),
                        "votantes": d["מצביעים"].astype(float), "validos": d["כשרים"].astype(float)})
    out["doble"] = out["loc"].isin(DOBLE)
    partidos = [c for c in d.columns if c not in META]
    V = d[partidos].astype(float)
    return out.join(V), partidos


def bancas(votos, acuerdos=(), umbral=UMBRAL, total=120):
    """votos = {lista: votos validos}. Umbral sobre el total de validos; D'Hondt (Bader-Ofer) entre unidades (las
    parejas con acuerdo de excedentes cuentan como una si las dos pasan el umbral) y D'Hondt dentro de la pareja."""
    tot = sum(votos.values())
    pasa = {k: v for k, v in votos.items() if v >= umbral * tot}
    unidades, usadas = [], set()
    for a, b in acuerdos:
        if a in pasa and b in pasa:
            unidades.append((a, b))
            usadas |= {a, b}
    unidades += [(k,) for k in pasa if k not in usadas]
    vu = np.array([sum(pasa[k] for k in u) for u in unidades])
    su = _dhondt(vu, total)
    out = {k: 0 for k in votos}
    for u, s in zip(unidades, su):
        if len(u) == 1:
            out[u[0]] = s
        else:
            r = _dhondt(np.array([pasa[k] for k in u]), s)
            out.update(dict(zip(u, r)))
    return out


def _dhondt(v, s):
    seats = np.zeros(len(v), int)
    for _ in range(int(s)):
        seats[np.argmax(v / (seats + 1))] += 1
    return seats


if __name__ == "__main__":
    real = {24: {"מחל": 30, "פה": 17, "שס": 9, "כן": 8, "ב": 7, "אמת": 7, "ג": 7, "ל": 7, "ט": 6, "ודעם": 6, "ת": 6,
                 "מרצ": 6, "עם": 4},
            25: {"מחל": 32, "פה": 24, "ט": 14, "כן": 12, "שס": 11, "ג": 7, "ל": 6, "עם": 5, "ום": 5, "אמת": 4}}
    for n in (21, 22, 23, 24, 25):
        d, partidos = cargar(n)
        v = d[partidos].sum().to_dict()
        s = bancas(v, ACUERDOS.get(n, ()))
        gan = {LISTAS[n].get(k, k): x for k, x in sorted(s.items(), key=lambda t: -t[1]) if x}
        bl = pd.Series({k: x for k, x in s.items() if x}).groupby(lambda k: BLOQUE[n].get(k, "?")).sum().to_dict()
        ok = "" if n not in real else ("  coincide con el oficial" if all(s.get(k, 0) == x for k, x in real[n].items())
                                       else "  NO COINCIDE")
        print(n, NOMBRE[n], gan, bl, ok)
