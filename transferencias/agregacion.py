"""Cuánto cambia la estimación al pasar de circuitos a departamentos (por defecto, 1.ª vuelta 2023 -> balotaje 2023).
    python transferencias/agregacion.py [2019p 2023p]            (estima; luego resume)
    python transferencias/agregacion.py [2019p 2023p] resumen    (solo el resumen, con lo ya estimado)
Se parte de los mismos circuitos usados por estimar.py (comunes y filtrados) y se agrupan después del filtro, así las tres
versiones tienen exactamente los mismos votantes:
  - circuito: la estimación de siempre (carpeta <y0>_<y1>/)
  - departamento: los circuitos sumados por sección de la DINE (departamento, partido, comuna)
  - azar: dentro de cada provincia, los circuitos repartidos al azar en grupos con la misma cantidad de circuitos que
    los departamentos reales (NAZAR réplicas). Mismo número y tamaño de unidades, sin la geografía.
Departamento menos azar = efecto de agrupar por geografía (sesgo de agregación); azar menos circuito = efecto de tener
menos unidades. Salida en agregacion_<y0>_<y1>/ (RESUMEN.md, resumen.csv y una carpeta por versión).
Las provincias que estimar.py ya trabaja por sección (cobertura baja de circuitos comunes) quedan igual en las tres."""
import os, sys
import numpy as np
import pandas as pd
import estimar

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = [a for a in sys.argv[1:] if a != "resumen"]
Y0, Y1 = ARGS[:2] if ARGS else ("2023p", "2023b")
OUT = os.path.join(HERE, "agregacion_%s_%s" % (Y0, Y1))
NAZAR = int(os.environ.get("NAZAR", 20))
ORIGINAL = estimar.prepare


def agrupar(clave):
    """prepare() de estimar.py con los circuitos ya filtrados sumados según clave(índice) -> (distrito, 0, grupo)."""
    def prepare(y0, y1):
        A, B, XA, YB, w, rows, cols, ctl = ORIGINAL(y0, y1)
        k = pd.MultiIndex.from_tuples(clave(A.index), names=A.index.names)
        A = A.set_axis(k).groupby(level=[0, 1, 2]).sum(); B = B.set_axis(k).groupby(level=[0, 1, 2]).sum()
        ctl["unidades"] = len(A)
        XA = A.div(A.sum(1), axis=0); YB = B.div(B.sum(1), axis=0)
        w = B.sum(1) / B.sum(1).mean()
        return A, B, XA, YB, w, rows, cols, ctl
    return prepare


def seccion(s, c):
    """Grupo de un circuito: su sección; si estimar.py ya pasó la provincia a secciones (s = 0), la unidad misma."""
    return c if s == 0 else "S%d" % s


def por_departamento(idx):
    return [(d, 0, seccion(s, c)) for d, s, c in idx]


def al_azar(semilla):
    def clave(idx):
        rng = np.random.default_rng(semilla)
        s = pd.Series([seccion(s, c) for _, s, c in idx], index=idx)
        out = s.copy()
        for d in idx.get_level_values(0).unique():
            m = s.index.get_level_values(0) == d
            out[m] = rng.permutation(s[m].values)      # mismos tamaños de grupo que los departamentos, circuitos al azar
        return [(d, 0, g) for (d, _, _), g in zip(idx, out.values)]
    return clave


def estimar_todo():
    estimar.prepare = agrupar(por_departamento)
    estimar.main(Y0, Y1, out=os.path.join(OUT, "departamento"))
    estimar.BOOT = 2                                   # en las réplicas al azar solo interesa la estimación puntual
    for i in range(NAZAR):
        estimar.prepare = agrupar(al_azar(i))
        estimar.main(Y0, Y1, out=os.path.join(OUT, "azar", "%02d" % i))


def md(T):
    """Tabla markdown sin depender de tabulate."""
    L = ["| | " + " | ".join(map(str, T.columns)) + " |", "|---" * (len(T.columns) + 1) + "|"]
    return "\n".join(L + ["| %s | %s |" % (i, " | ".join("%g" % x for x in r)) for i, r in zip(T.index, T.values)])


def pct(f):
    M = pd.read_csv(f, index_col=0, encoding="utf-8-sig")
    return M.div(M.sum(1), axis=0) * 100, M.sum(1)


def resumen():
    C, peso = pct(os.path.join(HERE, "%s_%s" % (Y0, Y1), "matriz_votos.csv"))
    D, _ = pct(os.path.join(OUT, "departamento", "matriz_votos.csv"))
    Cc, _ = pct(os.path.join(HERE, "%s_%s" % (Y0, Y1), "calvo_nacional.csv"))
    Dc, _ = pct(os.path.join(OUT, "departamento", "calvo_nacional.csv"))
    R = [pct(os.path.join(OUT, "azar", d, "matriz_votos.csv"))[0] for d in sorted(os.listdir(os.path.join(OUT, "azar")))]
    Az = sum(R) / len(R)
    iv = pd.read_csv(os.path.join(HERE, "%s_%s" % (Y0, Y1), "intervalos.csv"), encoding="utf-8-sig")
    iv = iv.assign(lo=iv.p5 / iv.groupby("origen").votos.transform("sum") * 100,
                   hi=iv.p95 / iv.groupby("origen").votos.transform("sum") * 100).set_index(["origen", "destino"])
    dist = lambda X, Y: (X - Y).abs().sum(1) / 2      # puntos de votos de la fila que cambian de destino
    filas = pd.DataFrame({"peso_%": (peso / peso.sum() * 100).round(1),
                          "dpto_vs_circ": dist(D, C).round(1), "azar_vs_circ": dist(Az, C).round(1),
                          "dpto_vs_azar": dist(D, Az).round(1), "calvo_dpto_vs_circ": dist(Dc, Cc).round(1),
                          "azar_dispersion": pd.concat([dist(r, Az) for r in R], axis=1).mean(1).round(1)})
    fuera = [(o, d, round(C.loc[o, d], 1), round(D.loc[o, d], 1)) for o in C.index for d in C.columns
             if not iv.loc[(o, d), "lo"] - 0.05 <= D.loc[o, d] <= iv.loc[(o, d), "hi"] + 0.05]
    filas.to_csv(os.path.join(OUT, "resumen.csv"), encoding="utf-8-sig")
    w = peso / peso.sum()
    L = ["# Circuitos contra departamentos: %s → %s" % (Y0, Y1), "",
         "Distancia por fila = ½ Σ |diferencia| en puntos: la parte del voto de esa fuerza que cambia de destino de una versión a otra.",
         "Azar = promedio de %d réplicas con grupos al azar del mismo tamaño que los departamentos." % len(R), "",
         "Distancia media ponderada: departamento vs. circuito %.1f; azar vs. circuito %.1f; departamento vs. azar %.1f (variante Calvo: departamento vs. circuito %.1f)."
         % tuple((filas[c] * w).sum() for c in ("dpto_vs_circ", "azar_vs_circ", "dpto_vs_azar", "calvo_dpto_vs_circ")), "",
         md(filas), "", "## Circuito (principal)", "", md(C.round(1)), "", "## Departamento (principal)", "",
         md(D.round(1)), "", "## Azar (promedio)", "", md(Az.round(1)), "",
         "Celdas del departamento fuera del intervalo 5-95 del bootstrap por circuito: %d de %d." % (len(fuera), C.size), ""]
    L += ["- %s → %s: circuito %s, departamento %s" % f for f in fuera]
    open(os.path.join(OUT, "RESUMEN.md"), "w", encoding="utf8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if "resumen" not in sys.argv:
        estimar_todo()
    resumen()
