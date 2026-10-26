"""¿Qué acerca 1999 -> 2003 a la fig. 6.12 de Calvo y Escolar (2005, p. 202)? Prueba tres diferencias de especificación,
por separado y juntas, sobre la versión todo por departamento (como el libro) de presidente_1999.py:
  - filtro: solo departamentos con más de 10.000 votantes en 1999 (el criterio que usaron para replicar a Gervasoni)
  - tres_filas: origen solo De la Rúa, Duhalde y Cavallo (proporciones entre los tres; sin Otros ni Blanco y nulo de 1999)
  - cinco_destinos: destino solo los cinco candidatos (proporciones entre los cinco; sin Otros ni Blanco y nulo de 2003)
    python transferencias/replica_libro.py
Salida: replica_libro_1999pe_2003pe/ (una carpeta por versión, RESUMEN.md y resumen.csv). Distancia = ½ Σ |diferencia| con
el libro, en puntos de la fila; Otros + Blanco y nulo de 2003 cuentan como su «No estimado»."""
import os, itertools
import pandas as pd
import estimar, agregacion

HERE = os.path.dirname(os.path.abspath(__file__))
Y0, Y1 = "1999pe", "2003pe"
OUT = os.path.join(HERE, "replica_libro_%s_%s" % (Y0, Y1))
D = ["Menem (Lealtad)", "Kirchner (FPV)", "López Murphy (Recrear)", "Rodríguez Saá (MNP)", "Carrió (ARI)"]
O = ["Alianza (De la Rúa)", "PJ (Duhalde)", "AR (Cavallo)"]
LIBRO = pd.DataFrame([[5, 18, 27, 23, 23, 5], [59, 37, 1, 2, 1, 0], [0, 2, 35, 28, 26, 9]], index=O, columns=D + ["No estimado"])
VOTOS_LIBRO = pd.Series([9081487, 7133829, 1894898], index=O)
CAUSAS = ["filtro", "tres_filas", "cinco_destinos"]
DPTO = agregacion.agrupar(agregacion.por_departamento)


def variante(causas):
    def prepare(y0, y1):
        A, B, XA, YB, w, rows, cols, ctl = DPTO(y0, y1)
        if "filtro" in causas:
            ok = A.sum(1) > 10000
            A, B = A[ok], B[ok]
        if "tres_filas" in causas:
            rows = O; A = A[O]
        if "cinco_destinos" in causas:
            cols = D; B = B[D]
        ctl["unidades"] = len(A)
        XA = A.div(A.sum(1), axis=0); YB = B.div(B.sum(1), axis=0)
        w = B.sum(1) / B.sum(1).mean()
        return A, B, XA, YB, w, list(rows), list(cols), ctl
    return prepare


def pct(f):
    M = pd.read_csv(f, index_col=0, encoding="utf-8-sig")
    P = M.div(M.sum(1), axis=0) * 100
    P["No estimado"] = P.drop(columns=D).sum(1)
    return P.loc[O, D + ["No estimado"]]


def main():
    estimar.BOOT = 2                                   # solo interesa la estimación puntual
    nombres = []
    for k in range(len(CAUSAS) + 1):
        for c in itertools.combinations(CAUSAS, k):
            n = "+".join(c) or "base"; nombres.append(n)
            estimar.prepare = variante(c)
            estimar.main(Y0, Y1, out=os.path.join(OUT, n))
    filas, tabla = [], []
    w = VOTOS_LIBRO / VOTOS_LIBRO.sum()
    for n in nombres:
        u = pd.read_json(os.path.join(OUT, n, "control.json"), typ="series")
        for var, f in (("principal", "matriz_votos.csv"), ("Calvo", "calvo_nacional.csv")):
            P = pct(os.path.join(OUT, n, f))
            dist = (P - LIBRO).abs().sum(1) / 2
            filas.append(dict(version=n, variante=var, unidades=u.get("unidades"), media=round((dist * w).sum(), 1),
                              **{o.split(" ")[0]: round(dist[o], 1) for o in O}))
            for o in O: tabla.append(dict(version=n, variante=var, origen=o, **P.loc[o].round(1).to_dict()))
    R = pd.DataFrame(filas).sort_values("media"); R.to_csv(os.path.join(OUT, "resumen.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame(tabla).to_csv(os.path.join(OUT, "matrices.csv"), index=False, encoding="utf-8-sig")
    md = lambda T: "\n".join(["| " + " | ".join(map(str, T.columns)) + " |", "|---" * len(T.columns) + "|"] +
                             ["| " + " | ".join(str(x) for x in r) + " |" for r in T.values])
    mejor = pd.DataFrame(tabla).merge(R.head(1)[["version", "variante"]])
    L = ["# Réplica de la fig. 6.12 de Calvo y Escolar (2005): presidente 1999 → 2003", "",
         "Distancia con el libro = ½ Σ |diferencia| en puntos de la fila (media ponderada por los votos del libro). Todo por departamento.", "",
         md(R), "", "## Libro", "", md(LIBRO.reset_index().rename(columns={"index": "origen"})), "",
         "## La versión más cercana (%s, %s)" % tuple(R.iloc[0][["version", "variante"]]), "",
         md(mejor.drop(columns=["version", "variante"]))]
    open(os.path.join(OUT, "RESUMEN.md"), "w", encoding="utf8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
