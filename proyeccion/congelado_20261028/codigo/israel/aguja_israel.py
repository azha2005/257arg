"""Aguja de bloques de la Knesset (estilo New York Times 2020): repeticion de la noche de noviembre de 2022 desde la
eleccion de 2021, con un orden de llegada simulado (geo: localidades chicas primero, ciudades grandes y localidades
arabes despues; el doble sobre llega al final).
    python -X utf8 proyeccion/israel/aguja_israel.py [--corte 0.1] [--seed 7]
Salida: proyeccion/img/aguja_israel_2022.png y proyeccion/israel/aguja_israel_2022.csv."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import datos as dt
import modelo as md
import aguja_dibujo as ad

O, D = 24, 25
NBOOT = 300
COLORES = {"bibi": "#1f4e9c", "sin": "#e07b00", "arabe": "#2e8b57", "empate": "#727272"}


def opt(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def main():
    corte, seed = opt("--corte", 0.0), opt("--seed", 7)
    st = md.preparar(O, D)
    ac = dt.ACUERDOS[D]
    rng = np.random.default_rng(seed)
    ordn = md.orden(st, "geo", rng)
    n = len(ordn)
    Yv = st["Y"] * st["w"][:, None]
    fr = np.unique(np.r_[np.geomspace(0.003, 0.05, 14), np.linspace(0.06, 1, 40)])
    rows, keep = [], {}
    for f in fr:
        cnt = ordn[:max(1, int(round(f * n)))]
        s, _ = md.proyectar(st, cnt, rng, NBOOT, ac)
        b = md.bloques(st, s, dt.BLOQUE[D])
        res = md.resultado(b["bibi"][1:], b["oposicion"][1:])
        vc = Yv[cnt].sum(0)
        sc = dt.bancas({st["dcols"][i]: vc[i] for i in range(len(st["dcols"]) - 1)}, ac)
        bc = md.bloques(st, np.array([[sc[x] for x in st["listas"]]]), dt.BLOQUE[D])
        r = dict(fraccion=f, bibi=b["bibi"][0], opo=b["oposicion"][0], arabe=b["arabe"][0],
                 conteo_bibi=bc["bibi"][0], conteo_opo=bc["oposicion"][0],
                 p_bibi=(res == "bibi").mean(), p_opo=(res == "oposicion").mean(), p_empate=(res == "empate").mean())
        for k, kk in (("bibi", "b"), ("oposicion", "o")):
            for q in (5, 25, 75, 95):
                r["%s%d" % (kk, q)] = np.percentile(b[k][1:], q)
        r.update({"s_" + x: s[0, j] for j, x in enumerate(st["listas"])})
        rows.append(r)
        keep[f] = (s, b)
        print("%5.1f %%  bibi %d [%g-%g]  opo %d  P(bibi) %.2f P(opo) %.2f P(empate) %.2f  conteo bibi %d" % (
            100 * f, r["bibi"], r["b5"], r["b95"], r["opo"], r["p_bibi"], r["p_opo"], r["p_empate"],
            r["conteo_bibi"]), flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "aguja_israel_2022.csv"), index=False)
    v, p = dt.cargar(D)
    real = dt.bancas(v[p].sum().to_dict(), ac)
    rb = md.bloques(st, np.array([[real[x] for x in st["listas"]]]), dt.BLOQUE[D])
    # momento de la foto: por defecto, el primer corte con 10 % o mas contado
    i = int(np.argmin(np.abs(df.fraccion - (corte or 0.1))))
    r = df.iloc[i]
    nombres = dt.LISTAS[D]
    txt = "Bancas proyectadas: " + ", ".join("%s %d" % (nombres.get(x, x), r["s_" + x]) for x in
                                              sorted(st["listas"], key=lambda x: -r["s_" + x]) if r["s_" + x] > 0)
    fuera = [nombres.get(x, x) for x in st["listas"] if r["s_" + x] == 0]
    txt += ". Debajo del umbral: " + ", ".join(fuera) + "."
    ad.dibujar_bancas(
        os.path.join(HERE, "..", "img", "aguja_israel_2022.png"),
        titulo="Knesset 2022: la aguja con el %s %% de las urnas" % _coma(100 * r.fraccion),
        subtitulo="Repetición de la noche del 1-nov-2022 con la proyección desde la elección de 2021, urna por urna. "
                  "Orden de llegada simulado: localidades chicas primero, ciudades y localidades árabes después; el "
                  "doble sobre (soldados, etc.) siempre proyectado.",
        bibi=int(r.bibi), p50=(r.b25, r.b75), p95=(int(r.b5), int(r.b95)),
        probs=[("Netanyahu ≥ 61", r.p_bibi, COLORES["bibi"]),
               ("Nadie sin las listas árabes", r.p_empate, COLORES["empate"]),
               ("Oposición judía ≥ 61", r.p_opo, COLORES["sin"])],
        colores=COLORES,
        serie=dict(x=list(df.fraccion), bibi=list(df.bibi), b5=list(df.b5), b25=list(df.b25), b75=list(df.b75),
                   b95=list(df.b95), opo=list(df.opo), o5=list(df.o5), o25=list(df.o25), o75=list(df.o75),
                   o95=list(df.o95), conteo_bibi=list(df.conteo_bibi), conteo_opo=list(df.conteo_opo),
                   xlabel="urnas comunes contadas (escala logarítmica)"),
        real=(rb["bibi"][0], rb["oposicion"][0]), bancas_txt=txt, momento=r.fraccion,
        pie="Bloque de Netanyahu: Likud, Sionismo Religioso, Shas y UTJ. Oposición judía: Yesh Atid, Unidad Nacional, "
            "Israel Beitenu, Laborismo, Meretz y Hogar Judío. Árabes: Raam, Hadash-Taal y Balad. Resultado final: "
            "64 / 46 / 10. Modelo: Goodman por sector con las urnas contadas, bootstrap de grupos de urnas, reparto "
            "con umbral de 3,25 %, Bader-Ofer y acuerdos de excedentes. Repetición retrospectiva, no una aguja "
            "publicada.")


def _coma(v):
    return ("%.0f" % v) if v >= 10 else ("%.1f" % v).replace(".", ",")


if __name__ == "__main__":
    main()
