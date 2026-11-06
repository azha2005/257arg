"""Hemiciclo y mapas del Senado con el sistema de EE. UU. (4-nov-2026), una figura por rotación.
    <python de Mosaic> analisis/senado_eeuu/figuras.py
Lee resultado.json (de calcular.py). Hemiciclo de 48 bancas por bloque actual y tres mapas, uno por año de
elección (16 provincias cada uno): color del bloque ganador, rayado si se usó la elección de diputados como
aproximación, gris si la provincia no elige ese año. Malvinas en gris, sin Antártida. Salida: img/rotacion_<A|B>.png."""
import json, os, unicodedata
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
R = json.load(open(os.path.join(HERE, "resultado.json"), encoding="utf8"))
AÑOS = (2021, 2023, 2025)
# orden del hemiciclo (izquierda a derecha) y colores del proyecto donde existen
BLOQUES = [("Justicialista", "#009ce4"), ("Convicción Federal", "#7fc8f0"), ("Justicia Social Federal", "#1aff98"),
           ("Frente Cívico por Santiago", "#2e7d32"), ("Movimiento por Misiones", "#0097a7"),
           ("Movere Santa Cruz", "#ea5530"), ("MPN (sin bloque hoy)", "#00708b"), ("JSRN (sin bloque hoy)", "#9ccc65"),
           ("Provincias Unidas", "#FF682C"), ("UCR", "#e10019"), ("Frente PRO", "#f4ce00"),
           ("La Libertad Avanza", "#6c4c98")]
COL = dict(BLOQUES)
GRIS, MALV = "#e4e4e0", "#a9a9a9"


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


ALIAS = {"ciudad autonoma de buenos aires": "capital federal",
         "tierra del fuego, antartida e islas del atlantico sur": "tierra del fuego"}


def provincias():
    g = gpd.read_file(os.path.join(ROOT, "geometria/Base deptos 1869-2022/Departamentos_2022_INDEC.shp"))
    nam = g.nam.map(norm)
    malv = g[nam.str.contains("atlantico sur")].clip((-62, -53, -57, -50.5))  # solo las Malvinas
    g = g[~nam.str.contains("antartida|malvinas|atlantico sur")]
    g["prov"] = g.jur.map(lambda s: ALIAS.get(norm(s), norm(s)))
    p = g.dissolve("prov").reset_index().to_crs("+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64")
    p["geometry"] = p.geometry.simplify(2500)
    return p, malv.to_crs(p.crs)


def hemiciclo(ax, bancas):
    """bancas: lista de colores en orden; filas concéntricas como los diagramas de la Wikipedia (cuñas por bloque)."""
    n, filas = len(bancas), 4
    radios = np.linspace(1.05, 2.0, filas)
    cupo = np.round(radios / radios.sum() * n).astype(int)
    cupo[-1] += n - cupo.sum()
    pos = [(t, r) for r, k in zip(radios, cupo) for t in np.linspace(np.pi, 0, k)]
    pos.sort(key=lambda x: (-round(x[0], 6), x[1]))
    for (t, r), c in zip(pos, bancas):
        ax.add_patch(Circle((r * np.cos(t), r * np.sin(t)), 0.125, color=c, ec="white", lw=.8))
    ax.set_xlim(-2.2, 2.2); ax.set_ylim(-.15, 2.2); ax.set_aspect("equal"); ax.axis("off")


def figura(rot):
    prov, malv = provincias()
    det = R["detalle"][rot]
    tot = R["totales"][rot]
    fig = plt.figure(figsize=(17, 8.2), dpi=110)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 4, width_ratios=[1.45, 1, 1, 1], height_ratios=[1, .07], wspace=.02, hspace=0,
                          top=.84, bottom=.05, left=.01, right=.99)
    rot_txt = {"A": "el turno agregado es el siguiente (2021 → 2023 → 2025 → 2021)",
               "B": "el turno agregado es el anterior (2025 → 2023 → 2021 → 2025)"}[rot]
    fig.suptitle(f"Senado con el sistema de EE. UU.: 2 senadores por provincia, uno por elección (rotación {rot})",
                 fontsize=17, fontweight="bold", x=.02, ha="left", y=.98)
    fig.text(.02, .905, f"48 bancas en tres clases de 16; gana el más votado. Bloques actuales del Senado. Rotación {rot}: {rot_txt}.",
             fontsize=11.5, color="#555")
    ax = fig.add_subplot(gs[0, 0])
    orden = [b for b, _ in BLOQUES if tot.get(b)]
    hemiciclo(ax, [COL[b] for b in orden for _ in range(tot[b])])
    ax.text(0, .25, "48", ha="center", fontsize=30, fontweight="bold")
    ax.text(0, .02, "mayoría: 25", ha="center", fontsize=11, color="#555")
    ley = [Patch(color=COL[b], label=f"{b}  {tot[b]}") for b in orden]
    ax.legend(handles=ley, loc="upper center", bbox_to_anchor=(.5, -.0), ncol=2, frameon=False, fontsize=10, columnspacing=1.2)
    for j, a in enumerate(AÑOS):
        ax = fig.add_subplot(gs[0, j + 1])
        quien = {norm(d["provincia"]): d for d in det if d["clase"] == a}
        for _, r in prov.iterrows():
            d = quien.get(r.prov)
            c = COL[d["bloque_actual"]] if d else GRIS
            gpd.GeoSeries([r.geometry], crs=prov.crs).plot(ax=ax, color=c, edgecolor="white", linewidth=.5,
                                                           hatch="////" if d and d["fuente"] == "diputados" else None)
        malv.plot(ax=ax, color=MALV, edgecolor="none")
        # Capital ampliada: círculo junto al AMBA
        cap = prov[prov.prov == "capital federal"].geometry.iloc[0].centroid
        d = quien.get("capital federal")
        ax.add_patch(Circle((cap.x + 260000, cap.y + 120000), 70000, color=COL[d["bloque_actual"]] if d else GRIS,
                            ec="#333", lw=.6, hatch="////" if d and d["fuente"] == "diputados" else None))
        ax.plot([cap.x, cap.x + 200000], [cap.y, cap.y + 95000], color="#333", lw=.6)
        n = len(quien)
        ax.set_title(f"Clase {a}\n{n} bancas", fontsize=14, fontweight="bold")
        ax.set_aspect("equal"); ax.axis("off")
    pie = fig.add_subplot(gs[1, 1:]); pie.axis("off")
    pie.legend(handles=[Patch(facecolor="white", edgecolor="#555", label="elección de senadores de ese año"),
                        Patch(facecolor="white", edgecolor="#555", hatch="////",
                              label="sin senadores ese año: se usa su elección de diputados"),
                        Patch(color=GRIS, label="no elige ese año"), Patch(color=MALV, label="Malvinas")],
               loc="center", ncol=4, frameon=False, fontsize=10.5)
    fig.text(.98, .012, "Wikipedia (escrutinio definitivo) y senado.gob.ar, bloques al 4-nov-2026 · azha2005.github.io/257arg",
             ha="right", fontsize=9, color="#777")
    os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
    f = os.path.join(HERE, "img", f"rotacion_{rot}.png")
    fig.savefig(f, dpi=110, facecolor="white")
    plt.close(fig)
    print(f)


if __name__ == "__main__":
    for r in ("A", "B"):
        figura(r)
