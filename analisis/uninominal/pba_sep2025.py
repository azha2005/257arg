"""Los 73 distritos de Buenos Aires con la eleccion provincial del 7-sep-2025 (ejercicio local, 5-nov-2026).
    <python de Mosaic> analisis/uninominal/pba_sep2025.py  -> pba_sep2025.csv, img/pba_sep2025_<plan>.png
Votos: escrutinio provisorio por mesa de graficarpba (mapas/mapaPBA2025sep/mesas_pba.pkl, senadores o diputados
provinciales segun la seccion, como el atlas). La base no se redistribuye: este script y sus salidas quedan locales.
Agrupaciones de mapas/mapaPBA2025sep/partidos_sep.py (Somos suma su lista ligada); el resto, «Otros».
Circuito -> radios por poblacion, como construir_elecciones.py (99,99 % de los votos empalman por circuito; el
resto va a su partido por poblacion). Los distritos son los de los planes ya dibujados (no se redibuja nada)."""
import os, sys, glob, warnings
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "mapas", "mapaPBA2025sep"))
from partidos_sep import bloc_of, COLOR, LABEL  # noqa: E402
AEA = "+proj=aea +lat_1=-28 +lat_2=-45 +lat_0=-35 +lon_0=-64 +datum=WGS84 +units=m"
B = ["FP", "LLA", "SB", "FIT", "OT"]
COLOR = {**COLOR, "OT": "#9a9a9a"}
LABEL = {**LABEL, "OT": "Otros"}

m = pd.read_pickle(os.path.join(ROOT, "mapas", "mapaPBA2025sep", "mesas_pba.pkl"))
m = m[m.votos_tipo == "POSITIVO"].copy()
m["b"] = m.agrupacion_nombre.map(bloc_of).fillna("OT")
m["s"], m["c"] = m.sec.astype(int).astype(str), m.cir.str.lstrip("0").str.upper()
vc = m.pivot_table(index=["s", "c"], columns="b", values="v", aggfunc="sum", fill_value=0)[B]

rad = gpd.read_file(glob.glob(os.path.join(HERE, "shp_radios", "02_*.shp"))[0]).to_crs(AEA)
rad["s"], rad["c"] = rad.circ.str.split("-").str[1], rad.circ.str.split("-").str[2]
pop = rad.population.astype(float).clip(lower=0) + 1e-6
k = pd.MultiIndex.from_arrays([rad.s, rad.c])
fr = pop / pop.groupby(rad.circ).transform("sum")
V = vc.reindex(k).fillna(0).values * fr.values[:, None]
# circuitos sin radios: a su partido por poblacion
falt = vc[~vc.index.isin(set(zip(rad.s, rad.c)))]
for (s, c), row in falt.iterrows():
    w = np.where(rad.s == s, pop, 0); V += np.outer(w / w.sum(), row.values)
rad[B] = V
# guia para distritar.py (UNI_GUIA=pba25s): mismo formato que radios_elecciones.pkl, local
pd.to_pickle({"radios": pd.DataFrame({"dist": "02", "pid": rad.pid.values,
              **{f"pba25s|{b}": rad[b].values for b in B}})}, os.path.join(HERE, "radios_pba_sep.pkl"))
print("votos por radio / base:", round(rad[B].values.sum() / vc.values.sum(), 6),
      "| FP %.2f LLA %.2f" % tuple(100 * rad[["FP", "LLA"]].sum() / rad[B].values.sum()))

PLANES = [("plan_gpba25s_t2_lla_extremo_circ", "LLA extremo, margen de un punto (circuitos)"), ("plan_gpba25s_v2_lla_extremo_circ", "LLA extremo, margen de un punto, otra semilla (circuitos)")] + [(f"plan_gpba25s_lla{x}_circ", f"LLA {t}guiado por sept. (circuitos)") for x, t in (("", ""), ("_extremo", "extremo "))] + [(f"plan_gpba25sLL_lla{x}_circ", f"LLA {t}guiado por sept., pasada larga (circuitos)") for x, t in (("", ""), ("_extremo", "extremo "))] + [(f"plan_radios{mo}{suf}", f"{t} ({lt})") for mo, t in (("", "Neutral"), ("_proporcional", "Proporcional"),
          ("_peronista", "Gerrymander peronista"), ("_lla", "Gerrymander LLA"),
          ("_peronista_extremo", "Peronista extremo"), ("_lla_extremo", "LLA extremo"))
          for suf, lt in (("", "libres"), ("_deptos", "departamentos"), ("_circ", "circuitos"), ("_dc", "deptos. y circuitos"))]
filas, porplan = [], {}
for carpeta, titulo in PLANES:
    f = os.path.join(HERE, carpeta, "02.csv")
    if not os.path.exists(f): continue
    a = pd.read_csv(f, dtype={"pid": str}).set_index("pid").distrito
    r = rad.assign(distrito=a.reindex(rad.pid).values)
    t = r.groupby("distrito")[B + ["D25", "R25", "D23b", "R23b"]].sum()
    gan = t[B].idxmax(1)
    sh = t.FP / (t.FP + t.LLA)
    filas.append({"plan": titulo, "carpeta": carpeta, **{LABEL[b]: int((gan == b).sum()) for b in B},
                  "FP mano a mano": int((sh > .5).sum()), "FP firmes (+5)": int((sh > .55).sum()),
                  "LLA firmes (+5)": int((sh < .45).sum()),
                  "oct-2025 FP": int((t.D25 > t.R25).sum()), "balotaje 2023 Massa": int((t.D23b > t.R23b).sum())})
    porplan[carpeta] = (r, gan)
res = pd.DataFrame(filas)
res.to_csv(os.path.join(HERE, "pba_sep2025.csv"), index=False)
pd.set_option("display.width", 250)
print(res.drop(columns="carpeta").to_string(index=False))


def mapa(carpeta, titulo, out):
    r, gan = porplan[carpeta]
    d = r.dissolve("distrito", aggfunc={b: "sum" for b in B})
    d["gan"] = gan.reindex(d.index)
    tot = d[B].sum(1)
    d["mg"] = (d[B].max(1) - d[B].apply(lambda x: sorted(x)[-2], axis=1)) / tot
    def col(row):
        c = np.array(matplotlib.colors.to_rgb(COLOR[row.gan]))
        a = .35 + .65 * min(row.mg / .3, 1)  # mas oscuro, mas ventaja sobre el segundo
        return tuple(c * a + (1 - a))
    d["fc"] = d.apply(col, axis=1)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 9), gridspec_kw={"width_ratios": [1.15, 1]})
    for a_, box in ((ax, None), (ax2, (-58.95, -35.05, -57.85, -34.35))):
        dd = d
        if box:
            bb = gpd.GeoSeries.from_xy([box[0], box[2]], [box[1], box[3]], crs=4326).to_crs(AEA).total_bounds
            dd = d.cx[bb[0]:bb[2], bb[1]:bb[3]]
            a_.set_xlim(bb[0], bb[2]); a_.set_ylim(bb[1], bb[3])
        dd.plot(ax=a_, color=dd.fc, edgecolor="white", linewidth=.6 if box else .35)
        a_.set_axis_off()
    ax2.set_title("Conurbano", fontsize=11)
    n = gan.value_counts()
    fig.suptitle(f"Buenos Aires, 73 distritos · {titulo}\nProvinciales del 7-sep-2025: "
                 + " · ".join(f"{LABEL[b]} {n.get(b, 0)}" for b in B if n.get(b, 0)), fontsize=13)
    ax.legend(handles=[Patch(color=COLOR[b], label=LABEL[b]) for b in B if n.get(b, 0)], loc="lower left", frameon=False)
    fig.text(.5, .02, "Más oscuro, más ventaja sobre el segundo. Votos por mesa de graficarpba (provisorio) llevados a "
             "radios por población dentro de cada circuito.", ha="center", fontsize=8, color="#555")
    fig.savefig(out, dpi=110, bbox_inches="tight"); plt.close(fig)


os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
for carpeta in sys.argv[1:] or ["plan_radios_lla_circ", "plan_radios_lla_extremo_circ", "plan_radios_circ"]:
    t = dict((c, t) for c, t in PLANES)[carpeta]
    mapa(carpeta, t, os.path.join(HERE, "img", f"pba_sep2025_{carpeta}.png"))
    print("img", carpeta)
