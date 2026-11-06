"""Planes de Buenos Aires (73 distritos) con diputados nacionales del 26-oct-2025 (ejercicio local, 5-nov-2026).
    <python de Mosaic> analisis/uninominal/pba_oct2025.py [carpeta ...]  -> img/pba_oct2025_<carpeta>.png
Votos por radio de radios_partidos.pkl (construir_partidos.py, DINE provisorio), todas las fuerzas, gana la mas votada.
Sirve para ver como rinde en octubre un plan dibujado con las provinciales de septiembre (pba_sep2025.py)."""
import os, sys, glob, warnings
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"
pp = pd.read_pickle(os.path.join(HERE, "radios_partidos.pkl"))
x = pp["radios"]; x = x[x.dist == "02"]
cs = [c for c in x.columns if c.startswith("25|")]
cs = [c for c in cs if x[c].sum() > 0]
INFO = {c: pp["partidos"]["25"][c.split("|")[1]] for c in cs}
rad = gpd.read_file(glob.glob(os.path.join(HERE, "shp_radios", "02_*.shp"))[0]).to_crs(AEA)[["pid", "geometry"]]
rad = rad.merge(x[["pid"] + cs], on="pid", how="left").fillna(0)
FP, LLA = "25|B02", "25|B01"
tot = rad[cs].values.sum()
print("FP %.2f LLA %.2f" % (100 * rad[FP].sum() / tot, 100 * rad[LLA].sum() / tot))

PLANES = {"plan_gpba25s_t2_lla_extremo_circ": "LLA extremo dibujado con sept. 2025, margen de un punto",
          "plan_gpba25s_v2_lla_extremo_circ": "LLA extremo dibujado con sept. 2025, otra semilla",
          "plan_radios_circ": "Neutral (circuitos)", "plan_radios_lla_circ": "Gerrymander LLA (circuitos)",
          "plan_radios_lla_extremo_circ": "LLA extremo (circuitos)",
          "plan_radios_peronista_extremo_circ": "Peronista extremo (circuitos)"}
res = {}
for k, t in PLANES.items():
    a = pd.read_csv(os.path.join(HERE, k, "02.csv"), dtype={"pid": str}).set_index("pid").distrito
    r = rad.assign(distrito=a.reindex(rad.pid).values)
    d = r.groupby("distrito")[cs].sum()
    gan = d.idxmax(1)
    s = d[FP] / (d[FP] + d[LLA])
    res[k] = (r, d, gan)
    n = gan.value_counts()
    print(f"{t:58s}", " · ".join(f"{INFO[c]['n']} {n[c]}" for c in n.index),
          f"| LLA por 5+: {int((s < .45).sum())}, FP por 5+: {int((s > .55).sum())}, a menos de 2 puntos: {int((abs(s - .5) < .01).sum())}")


def mapa(k, out):
    r, d, gan = res[k]
    g = r.dissolve("distrito")[["geometry"]].join(d)
    srt = np.sort(d[cs].values, 1)
    mg = pd.Series((srt[:, -1] - srt[:, -2]) / d[cs].sum(1).values, index=d.index)

    def col(i):
        c = np.array(matplotlib.colors.to_rgb(INFO[gan[i]]["c"])); a = .35 + .65 * min(mg[i] / .3, 1)
        return tuple(c * a + (1 - a))
    g["fc"] = [col(i) for i in g.index]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 9), gridspec_kw={"width_ratios": [1.15, 1]})
    for a_, box in ((ax, None), (ax2, (-58.95, -35.05, -57.85, -34.35))):
        gg = g
        if box:
            bb = gpd.GeoSeries.from_xy([box[0], box[2]], [box[1], box[3]], crs=4326).to_crs(AEA).total_bounds
            gg = g.cx[bb[0]:bb[2], bb[1]:bb[3]]; a_.set_xlim(bb[0], bb[2]); a_.set_ylim(bb[1], bb[3])
        gg.plot(ax=a_, color=gg.fc, edgecolor="white", linewidth=.6 if box else .35); a_.set_axis_off()
    ax2.set_title("Conurbano", fontsize=11)
    n = gan.value_counts()
    fig.suptitle(f"Buenos Aires, 73 distritos · {PLANES[k]}\nDiputados nacionales del 26-oct-2025: "
                 + " · ".join(f"{INFO[c]['n']} {n[c]}" for c in n.index), fontsize=13)
    ax.legend(handles=[Patch(color=INFO[c]["c"], label=INFO[c]["n"]) for c in n.index], loc="lower left", frameon=False)
    fig.text(.5, .02, "Más oscuro, más ventaja sobre el segundo. Provisorio DINE por circuito llevado a radios por población.",
             ha="center", fontsize=8, color="#555")
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)


for k in sys.argv[1:] or ["plan_gpba25s_t2_lla_extremo_circ"]:
    mapa(k, os.path.join(HERE, "img", f"pba_oct2025_{k}.png")); print("img", k)
