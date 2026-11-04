"""Aguja al estilo del New York Times (2020) con las fotos de actas de Twitter de 2025, en el orden en que se publicaron:
el modelo de proyectar_fotos.py (Goodman lam=0,1 + AMBA/resto, origenes 2023p y 2021bl) despues de cada foto.
    python proyeccion/aguja_fotos.py
La hora de cada tuit sale del identificador de la imagen de X (los primeros 8 bytes son un snowflake: ms desde
2010-11-04 01:42:54.657 UTC en los bits 22 en adelante); las fotos de telefono, del nombre del archivo. Las dos sin hora
(la de Capital comuna 10 y la de Sarandi) van al final.
Salida: proyeccion/img/aguja_fotos_2025.png y fotos25/aguja_fotos.csv."""
import os, sys, base64, datetime
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = sys.argv[:1]
import proyectar_fotos as pf
import aguja_dibujo as ad

ORIG = "2023p,2021bl"
NBOOT = 1000
REAL = 40.66 - 33.60                        # diputados 2025, bloques (bloques.py)
MIN_CIRC = 5
SIN_HORA = datetime.datetime(2025, 10, 26, 21, 10)


def hora(foto):
    k = os.path.splitext(foto)[0].split(" ")[0]
    if k.startswith("2025") and "_" in k:
        return datetime.datetime.strptime(k, "%Y%m%d_%H%M%S")
    if k.startswith("G4"):
        n = int.from_bytes(base64.urlsafe_b64decode(k + "=" * (-len(k) % 4))[:8], "big")
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=(n >> 22) + 1288834974657) \
            - datetime.timedelta(hours=3)
    return SIN_HORA


def main():
    a = pf.leer(os.path.join(HERE, "fotos25", "actas.csv"))
    fotos = sorted(a.foto.unique(), key=hora)
    rows = []
    for i in range(1, len(fotos) + 1):
        sub = a[a.foto.isin(fotos[:i])]
        R = pf.calcular(sub, ORIG, nboot=NBOOT, seed=i)
        b = R["blocs"]
        if "LLA" not in b or "FP" not in b:
            continue
        j, k = b.index("LLA"), b.index("FP")
        m = R["bs"][:, j] - R["bs"][:, k]
        crudo = R["crudo"][j] - R["crudo"][k]
        rows.append(dict(foto=fotos[i - 1], hora=hora(fotos[i - 1]), actas=len(R["F"]),
                         circuitos=R["clus"].max() + 1, margen=R["pt"][j] - R["pt"][k],
                         p25=np.percentile(m, 25), p75=np.percentile(m, 75), p2=np.percentile(m, 2.5),
                         p97=np.percentile(m, 97.5), prob=(m > 0).mean(), crudo=crudo,
                         **{"pct_" + x: R["pt"][n] for n, x in enumerate(b)}))
        print(rows[-1]["hora"].strftime("%H:%M"), rows[-1]["actas"], "%+.1f" % rows[-1]["margen"], flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "fotos25", "aguja_fotos.csv"), index=False)
    last = df.iloc[-1]
    df = df[df.circuitos >= MIN_CIRC]                  # con menos grupos el bootstrap no mide nada
    fuerzas = [(x[4:], last[x]) for x in df.columns if x.startswith("pct_") and np.isfinite(last[x])]
    ad.dibujar(
        os.path.join(HERE, "img", "aguja_fotos_2025.png"),
        titulo="Diputados nacionales 2025: la aguja con 27 fotos de actas",
        subtitulo="Proyección con las fotos de mesas publicadas en X entre las 18:41 y las 21:05, antes del primer "
                  "dato oficial. Modelo de proyectar_fotos.py desde presidente 2023 y diputados 2021.",
        izq=("Fuerza Patria", "FP", "#009ce4"), der=("La Libertad Avanza", "LLA", "#6c4c98"),
        margen=last.margen, p25=last.p25, p75=last.p75, p2=last.p2, p97=last.p97, prob=last.prob, escala=20,
        serie=dict(x=list(df.hora), margen=list(df.margen), p25=list(df.p25), p75=list(df.p75), p2=list(df.p2),
                   p97=list(df.p97), crudo=list(df.crudo), xlabel="hora de publicación de la foto (Argentina)",
                   crudo_lab="suma cruda de las fotos", tiempo=True, n=list(df.actas)),
        real=REAL, real_lab="resultado final: LLA +7,1",
        fuerzas=sorted(fuerzas, key=lambda t: -t[1]),
        pie="Banda: 50 % (oscura) y 95 % (clara), bootstrap de circuitos ×1,4. Dos fotos sin hora conocida (Capital "
            "comuna 10 y Sarandí) van al final. La aguja arranca con 5 circuitos distintos (19:13). Simulación "
            "retrospectiva: en 2025 esta aguja no existió.")


if __name__ == "__main__":
    main()
