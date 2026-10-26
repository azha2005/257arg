"""Segunda vuelta 1976 calculada a partir de la primera vuelta.

Reglas de traspaso (las del pedido):
  Manrique/Chamizo (AF)  : 3/6 Alfonsin (UCR), 1/6 Luder (PJ), 2/6 a discrecion
  Frigerio/Barbaro (MID) : 4/6 Luder (PJ),     1/6 Alfonsin,   1/6 a discrecion
  Ghioldi (PSD)          : 2/3 Alfonsin,       1/3 a discrecion
  Coral (PST)            : 3/4 Alfonsin,       1/4 a discrecion
  Ramos (FIP)            : 100 % Luder
Los votos en blanco y nulos de la primera vuelta se mantienen; la abstencion
de la primera vuelta tambien. Las personas de la parte "a discrecion" se reparten
segun DISCRECION entre blanco, nulo y abstencion (decision del analisis).

El mismo calculo se aplica a cada provincia (con los totales del docx) y a cada
departamento (con la estimacion departamental de la primera vuelta, que ya
incorpora la metodologia de extrapolacion con marzo 73, septiembre 73 y 1983).
Como las reglas son lineales, la suma de los departamentos reproduce la provincia.
"""

# fraccion de los votantes "a discrecion" que va a cada destino
DISCRECION = {"Blanco": 0.30, "Nulo": 0.20, "Abst": 0.50}

# (candidato) -> (a UCR, a PJ, a discrecion)
REGLAS = {
    "AF":      (3 / 6, 1 / 6, 2 / 6),
    "MID":     (1 / 6, 4 / 6, 1 / 6),
    "Ghioldi": (2 / 3, 0.0,   1 / 3),
    "Coral":   (3 / 4, 0.0,   1 / 4),
    "Ramos":   (0.0,   1.0,   0.0),
}


def traspasar(c):
    """c: dict con PJ, UCR, AF, MID, Ghioldi, Coral, Ramos, Blanco, Nulo (votos de 1.a vuelta).
    Devuelve dict de flotantes: PJ, UCR, Blanco, Nulo, AbstNueva."""
    pj, ucr = float(c["PJ"]), float(c["UCR"])
    disc = 0.0
    for k, (a_ucr, a_pj, a_d) in REGLAS.items():
        v = float(c.get(k, 0))
        ucr += v * a_ucr
        pj += v * a_pj
        disc += v * a_d
    return {
        "PJ": pj,
        "UCR": ucr,
        "Blanco": float(c["Blanco"]) + disc * DISCRECION["Blanco"],
        "Nulo": float(c["Nulo"]) + disc * DISCRECION["Nulo"],
        "AbstNueva": disc * DISCRECION["Abst"],
    }


def resto_mayor(vals, total):
    """Redondea una lista de flotantes a enteros que suman `total` (metodo del mayor resto)."""
    base = [int(v) for v in vals]
    falta = int(round(total)) - sum(base)
    orden = sorted(range(len(vals)), key=lambda i: vals[i] - base[i], reverse=True)
    for i in orden[:max(falta, 0)]:
        base[i] += 1
    return base


def provincia(counts, registrados, participacion):
    t = traspasar(counts)
    abst1 = registrados - participacion
    vals = [t["PJ"], t["UCR"], t["Blanco"], t["Nulo"], abst1 + t["AbstNueva"]]
    pj, ucr, bl, nu, ab = resto_mayor(vals, registrados)
    part = registrados - ab
    return dict(PJ=pj, UCR=ucr, Blanco=bl, Nulo=nu, Abst=ab, Part=part, Reg=registrados,
                PJp=round(100 * pj / (pj + ucr), 2), UCRp=round(100 * ucr / (pj + ucr), 2),
                Blancop=round(100 * bl / part, 2), Nulop=round(100 * nu / part, 2),
                Abstp=round(100 * ab / registrados, 2), Partp=round(100 * part / registrados, 2))


def departamento(counts, participacion):
    t = traspasar(counts)
    vals = [t["PJ"], t["UCR"], t["Blanco"], t["Nulo"], t["AbstNueva"]]
    pj, ucr, bl, nu, ab = resto_mayor(vals, participacion)
    w = "UCR" if ucr >= pj else "PJ"
    q = round(100 * max(pj, ucr) / (pj + ucr), 2) if pj + ucr else 0.0
    return dict(PJ=pj, UCR=ucr, Blanco=bl, Nulo=nu, AbstNueva=ab, w=w, q=q)


def total(provs):
    keys = ("PJ", "UCR", "Blanco", "Nulo", "Abst", "Part", "Reg")
    T = {k: sum(p[k] for p in provs.values()) for k in keys}
    T.update(PJp=round(100 * T["PJ"] / (T["PJ"] + T["UCR"]), 2), UCRp=round(100 * T["UCR"] / (T["PJ"] + T["UCR"]), 2),
             Blancop=round(100 * T["Blanco"] / T["Part"], 2), Nulop=round(100 * T["Nulo"] / T["Part"], 2),
             Abstp=round(100 * T["Abst"] / T["Reg"], 2), Partp=round(100 * T["Part"] / T["Reg"], 2))
    return T
