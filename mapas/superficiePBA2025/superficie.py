"""Superficie interpolada del margen Fuerza Patria - La Libertad Avanza en la PBA, como el modo «surface» de theoelections.com.
    python mapas/superficiePBA2025/superficie.py
Entrada: locales_superficie.csv (preparar_superficie.py). Salida: img/sup_<sep|oct|swing>.png y superficie_pba2025.html.

Metodo: cada punto de una grilla de 1 km (250 m en el recuadro del AMBA) toma el margen de los votos de los locales cercanos con un
nucleo gaussiano de ancho adaptativo h = distancia hasta juntar V0 votos positivos (entre HMIN y HMAX km):
    margen(x) = sum_i K(d_i/h) (FP_i - LLA_i) / sum_i K(d_i/h) pos_i
Es decir, la proporcion de votos suavizada, no un promedio de porcentajes: un local grande pesa mas que uno chico. En el AMBA y en
las ciudades el ancho baja a un par de km; en el campo sube y la superficie se vuelve lisa. Entre pueblos el color es una
interpolacion: no hay votos ahi.
"""
import os, sys, base64, json, textwrap
import numpy as np, pandas as pd, shapely
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import matplotlib.patheffects as pe

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "mapas", "mapaPBA2025sep"))
import shapefile
from shapely.geometry import shape

V0, HMIN, HMAX = 6000, 1.5, 30.0   # ancho = distancia hasta juntar V0 votos positivos
LAT0 = -36.5
CX = np.cos(np.radians(LAT0)) * 111.32
CY = 110.57


def proj(lon, lat):
    return (np.asarray(lon) + 60) * CX, np.asarray(lat) * CY


LV = [-1e9, -32, -16, -8, -4, 0, 4, 8, 16, 32, 1e9]   # margen FP - LLA en puntos
LLA_C = ["#4a2f73", "#6c4c98", "#9479bd", "#b9a6d8", "#ddd3ec"]   # 32+ ... 0
FP_C = ["#cfe7f6", "#94cdee", "#4fb0e3", "#1188cc", "#0a5a92"]    # 0 ... 32+
CMAP = ListedColormap(LLA_C + FP_C)       # solo para la barra de conteo
NORM = BoundaryNorm(LV, CMAP.N)
# degradado continuo del mapa (como Theo): rampa suave LLA violeta -> blanco roto -> FP celeste, bandas finas cada punto
from matplotlib.colors import LinearSegmentedColormap
TOP = 40
RAMP = LinearSegmentedColormap.from_list("ramp", [
    (0.00, "#2e1652"), (0.20, "#55348a"), (0.35, "#8a68bd"), (0.45, "#c3b0e0"), (0.50, "#f2eef3"),
    (0.55, "#bfe1f4"), (0.65, "#5cb5e6"), (0.80, "#1680c8"), (1.00, "#063a6b")])
FINE = np.arange(-TOP, TOP + 0.1, 1.0)
FINE_NORM = matplotlib.colors.Normalize(-TOP, TOP)


def band_color(i):
    """color de la banda i de la barra (0..9), tomado del mismo degradado"""
    mid = [-36, -24, -12, -6, -2, 2, 6, 12, 24, 36][i]
    return RAMP(FINE_NORM(mid))
BG, LAND = "#e3e3e0", "#d3d3cf"

# --- geometria ---------------------------------------------------------------------------------------
SHP = os.path.join(ROOT, "geometria", "Base deptos 1869-2022", "Departamentos_2022_INDEC")
r = shapefile.Reader(SHP, encoding="latin1")
pba, caba, otras = [], [], []
for sh, rec in zip(r.shapes(), r.records()):
    g = shapely.make_valid(shape(sh.__geo_interface__))
    (pba if rec["cpr"] == "06" else caba if rec["cpr"] == "02" else otras).append(g)
PBA = shapely.union_all(pba).buffer(0.002).buffer(-0.002)
CABA = shapely.union_all(caba)
VEC = shapely.union_all([g for g in otras if g.intersects(shapely.box(-64.5, -41.5, -56, -32.5))]).simplify(0.01)
# islas diminutas fuera
PBA = shapely.MultiPolygon([p for p in getattr(PBA, "geoms", [PBA]) if p.area > 2e-4])


def to_path(geom, tol=0.0):
    if tol: geom = geom.simplify(tol)
    verts, codes = [], []
    for poly in getattr(geom, "geoms", [geom]):
        if poly.geom_type != "Polygon": continue
        for ring in [poly.exterior, *poly.interiors]:
            x, y = proj(*np.asarray(ring.coords).T)
            verts += list(zip(x, y)); codes += [Path.MOVETO] + [Path.LINETO] * (len(x) - 2) + [Path.CLOSEPOLY]
    return Path(verts, codes)


# --- datos -------------------------------------------------------------------------------------------
L = pd.read_csv(os.path.join(HERE, "locales_superficie.csv"), dtype={"sec": str, "cir": str})
L["x"], L["y"] = proj(L.lon, L.lat)


class Surf:
    def __init__(self, e):
        t = L[L[e + "_pos"] > 0]
        self.xy = t[["x", "y"]].to_numpy(); self.d = (t[e + "_FP"] - t[e + "_LLA"]).to_numpy(float); self.p = t[e + "_pos"].to_numpy(float)
        self.tree = cKDTree(self.xy)

    def __call__(self, X, Y, kq=400):
        pts = np.c_[X.ravel(), Y.ravel()]
        out = np.empty(len(pts))
        for a in range(0, len(pts), 20000):
            dd, ii = self.tree.query(pts[a:a + 20000], k=kq)
            cum = np.cumsum(self.p[ii], 1)
            j = np.minimum((cum < V0).sum(1), kq - 1)
            h = np.clip(dd[np.arange(len(dd)), j], HMIN, HMAX)[:, None]
            w = np.exp(-0.5 * (dd / h) ** 2)
            out[a:a + 20000] = 100 * (w * self.d[ii]).sum(1) / np.maximum((w * self.p[ii]).sum(1), 1e-9)
        return out.reshape(X.shape)


def grid(bounds, step):
    x0, y0 = proj(bounds[0], bounds[1]); x1, y1 = proj(bounds[2], bounds[3])
    xs = np.arange(x0, x1 + step, step); ys = np.arange(y0, y1 + step, step)
    return np.meshgrid(xs, ys)


B = PBA.bounds
B = (B[0] - .05, B[1] - .05, B[2] + .05, B[3] + .05)
AMBA_B = (-59.25, -35.15, -57.75, -34.25)
print("grillas...")
GX, GY = grid(B, 1.0)
AX, AY = grid(AMBA_B, 0.25)
S = {e: Surf(e) for e in ("sep", "oct")}
Z = {e: S[e](GX, GY) for e in S}
ZA = {e: S[e](AX, AY) for e in S}
Z["swing"] = Z["oct"] - Z["sep"]; ZA["swing"] = ZA["oct"] - ZA["sep"]

# conteo por circuito (como la barra de Theo: unidades por ventaja)
C = L.groupby(["sec", "cir"])[[c for c in L.columns if c[:4] in ("sep_", "oct_")]].sum()
CM = {}
for e in ("sep", "oct"):
    c = C[C[e + "_pos"] > 0]; CM[e] = 100 * (c[e + "_FP"] - c[e + "_LLA"]) / c[e + "_pos"]
c = C[(C.sep_pos > 0) & (C.oct_pos > 0)]
CM["swing"] = 100 * (c.oct_FP - c.oct_LLA) / c.oct_pos - 100 * (c.sep_FP - c.sep_LLA) / c.sep_pos

# rotulos: punto en la ciudad y nombre al costado (dx, dy en km del mapa), para no tapar la mancha de la ciudad
CIUD = [("La Plata", -57.95, -34.92, 8, -6), ("Mar del Plata", -57.55, -38.00, -8, 0, "right"), ("Bahía Blanca", -62.27, -38.72, -8, 4, "right"),
        ("Tandil", -59.13, -37.32, 8, 0), ("Olavarría", -60.32, -36.89, 8, 0), ("Junín", -60.95, -34.59, 8, 0),
        ("Pergamino", -60.57, -33.89, 8, 0), ("San Nicolás", -60.22, -33.33, 8, 0), ("Necochea", -58.74, -38.55, 8, 0),
        ("Azul", -59.86, -36.78, 8, 0), ("Trenque Lauquen", -62.73, -35.97, 8, 0), ("Chivilcoy", -60.02, -34.90, 8, 0),
        ("Tres Arroyos", -60.28, -38.37, 8, 0), ("Carmen de Patagones", -62.98, -40.80, 8, 0), ("Pehuajó", -61.90, -35.81, 8, 0),
        ("Dolores", -57.68, -36.31, 8, 0), ("Chascomús", -58.01, -35.58, 8, 0), ("Coronel Suárez", -61.93, -37.46, 8, 0)]
CIUD_A = [("La Matanza", -58.60, -34.75), ("Lomas de Zamora", -58.42, -34.79), ("Quilmes", -58.27, -34.72), ("La Plata", -57.95, -34.92),
          ("Pilar", -58.91, -34.46), ("Tigre", -58.58, -34.42), ("San Isidro", -58.53, -34.48), ("Moreno", -58.79, -34.65),
          ("Florencio Varela", -58.28, -34.83), ("San Martín", -58.54, -34.57), ("Escobar", -58.80, -34.35),
          ("Ezeiza", -58.52, -34.85), ("Cañuelas", -58.76, -35.05), ("Luján", -59.10, -34.57),
          ("José C. Paz", -58.75, -34.52), ("CABA", -58.44, -34.61)]

TIT = dict(sep=("Legislativas bonaerenses, 7 de septiembre de 2025", "quién gana: Fuerza Patria contra La Libertad Avanza (senadores y diputados provinciales)"),
           oct=("Diputados nacionales en la provincia, 26 de octubre de 2025", "quién gana: Fuerza Patria contra La Libertad Avanza"),
           swing=("Corrimiento de septiembre a octubre de 2025", "cambio del margen FP − LLA, en puntos"))
HALO = [pe.withStroke(linewidth=1.6, foreground=(1, 1, 1, 0.75))]


def label(ax, txt, x, y, fs, dx=0, dy=0, ha="left"):
    if dx or dy:
        ax.plot([x], [y], "o", ms=2.6, color="#111", mec="white", mew=0.6, zorder=10)
    ax.text(x + dx, y + dy, txt, fontsize=fs, fontweight="semibold", color="#111", ha=ha if (dx or dy) else "center",
            va="center", path_effects=HALO, zorder=10)


def draw(ax, X, Y, z, clip, extra=None):
    cs = ax.contourf(X, Y, np.clip(z, -TOP + 0.01, TOP - 0.01), levels=FINE, cmap=RAMP, norm=FINE_NORM, antialiased=True, zorder=2)
    cs.set_edgecolor("face"); cs.set_linewidth(0.35)   # sin rendijas entre bandas
    cl = ax.contour(X, Y, z, levels=[0], colors="#1a1a1a", linewidths=0.7, zorder=3)
    patch = PathPatch(clip, transform=ax.transData, facecolor="none", edgecolor="none")
    ax.add_patch(patch)
    cs.set_clip_path(patch); cl.set_clip_path(patch)


def render(e):
    fig = plt.figure(figsize=(17, 13), dpi=110, facecolor=BG)
    ax = fig.add_axes([0.01, 0.01, 0.58, 0.88]); ax.set_facecolor(BG)
    pba_path = to_path(PBA)
    draw(ax, GX, GY, Z[e], pba_path)
    ax.add_patch(PathPatch(to_path(CABA), facecolor=LAND, edgecolor="#9a9a95", lw=0.4, zorder=4))
    x0, y0 = proj(B[0], B[1]); x1, y1 = proj(B[2], B[3])
    ax.set_xlim(x0 - 10, x1 + 10); ax.set_ylim(y0 - 10, y1 + 10); ax.set_aspect("equal"); ax.axis("off")
    for n, lo, la, dx, dy, *ha in CIUD:
        x, y = proj(lo, la); label(ax, n, x, y, 9, dx, dy, *(ha or ["left"]))
    # recuadro AMBA
    ia = fig.add_axes([0.605, 0.36, 0.38, 0.52]); ia.set_facecolor(BG)
    draw(ia, AX, AY, ZA[e], to_path(PBA.intersection(shapely.box(*AMBA_B))))
    ia.add_patch(PathPatch(to_path(CABA), facecolor=LAND, edgecolor="#9a9a95", lw=0.6, zorder=4))
    a0 = proj(AMBA_B[0], AMBA_B[1]); a1 = proj(AMBA_B[2], AMBA_B[3])
    ia.set_xlim(a0[0], a1[0]); ia.set_ylim(a0[1], a1[1]); ia.set_aspect("equal"); ia.set_xticks([]); ia.set_yticks([])
    for s in ia.spines.values(): s.set_edgecolor("#555"); s.set_linewidth(1)
    for n, lo, la in CIUD_A:
        x, y = proj(lo, la); label(ia, n, x, y, 8.5)
    ia.text(0.02, 0.97, "Área metropolitana", transform=ia.transAxes, fontsize=12, fontweight="bold", va="top", path_effects=HALO)
    # marco del recuadro en el mapa
    ax.add_patch(PathPatch(Path([(a0[0], a0[1]), (a1[0], a0[1]), (a1[0], a1[1]), (a0[0], a1[1]), (a0[0], a0[1])]),
                           facecolor="none", edgecolor="#555", lw=0.8, zorder=5))
    # titulo
    fig.text(0.03, 0.975, TIT[e][0], fontsize=22, fontweight="bold", va="top", color="#111")
    fig.text(0.03, 0.945, TIT[e][1], fontsize=13, va="top", color="#333")
    # barra de conteo por circuito
    m = CM[e]
    cnt = np.histogram(m.clip(-999, 999), bins=LV)[0]
    lx, ly, bw, bh = 0.605, 0.21, 0.036, 0.026
    fig.text(lx, ly + 0.055, "circuitos por ventaja" if e != "swing" else "circuitos por corrimiento", fontsize=12, color="#333")
    lab = ["32+", "16", "8", "4", "0", "0", "4", "8", "16", "32+"]
    for i in range(10):
        x = lx + i * (bw + 0.002)
        fig.patches.append(plt.Rectangle((x, ly), bw, bh, transform=fig.transFigure, facecolor=band_color(i), edgecolor="white", lw=1))
        fig.text(x + bw / 2, ly + bh / 2, str(cnt[i]), ha="center", va="center", fontsize=11, fontweight="bold",
                 color="white" if i in (0, 1, 2, 7, 8, 9) else "#222")
        fig.text(x + bw / 2, ly + bh + 0.008, lab[i], ha="center", fontsize=10, color="#444")
    lft, rgt = ("← La Libertad Avanza", "Fuerza Patria →") if e != "swing" else ("← hacia LLA", "hacia FP →")
    fig.text(lx, ly - 0.012, lft, fontsize=11, color=RAMP(0.2), fontweight="bold", va="top")
    fig.text(lx + 10 * (bw + 0.002), ly - 0.012, rgt, fontsize=11, color=RAMP(0.8), fontweight="bold", va="top", ha="right")
    nota = ("Superficie interpolada (núcleo gaussiano adaptativo) desde los votos de ~6.400 locales de votación; entre pueblos el color es "
            "una interpolación, no hay votos ahí.\nFuentes: " + dict(sep="provisorio por mesa de graficarpba. ", oct="provisorio por mesa de la DINE. ",
            swing="provisorios por mesa de graficarpba (septiembre) y de la DINE (octubre). ")[e] +
            "Locales ubicados con el padrón de escuelas de la DGCyE; Capital no participa.")
    fig.text(0.605, 0.04, textwrap.fill(" ".join(nota.split()), 70), fontsize=10, color="#555", va="bottom")
    os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
    f = os.path.join(HERE, "img", "sup_%s.png" % e)
    fig.savefig(f, facecolor=BG); plt.close(fig)
    return f


files = {e: render(e) for e in ("sep", "oct", "swing")}
tot = {}
for e in ("sep", "oct"):
    tot[e] = 100 * (L[e + "_FP"].sum() - L[e + "_LLA"].sum()) / L[e + "_pos"].sum()
    print(e, "margen provincial %.2f" % tot[e], "| circuitos por banda", np.histogram(CM[e], bins=LV)[0].tolist())

# --- HTML con selector ---------------------------------------------------------------------------------
img = {e: base64.b64encode(open(f, "rb").read()).decode() for e, f in files.items()}
html = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Superficie PBA 2025</title><style>
:root{--bg:#e3e3e0;--fg:#111;--chip:#111;--chipfg:#fff}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.4 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:16px}
nav{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 12px}
button{font:inherit;font-weight:600;border:1px solid #111;background:transparent;color:#111;padding:6px 12px;cursor:pointer}
button.on{background:var(--chip);color:var(--chipfg)}
img{width:100%%;height:auto;display:block}
p{color:#444;font-size:13px}
</style></head><body><main>
<nav><button data-k="sep" class="on">• 7 de septiembre •</button><button data-k="oct">26 de octubre</button><button data-k="swing">corrimiento</button></nav>
<img id="m" alt="Superficie del margen Fuerza Patria - La Libertad Avanza en la provincia de Buenos Aires">
<p>Margen provincial FP − LLA: septiembre %+.1f puntos; octubre %+.1f. Superficie interpolada desde los votos por local de votación;
es una lectura visual, no un resultado por zona.</p>
</main><script>
const I=%s;const m=document.getElementById('m');
function go(k){m.src='data:image/png;base64,'+I[k];document.querySelectorAll('button').forEach(b=>{const on=b.dataset.k===k;b.classList.toggle('on',on);b.textContent=b.textContent.replace(/^• | •$/g,'');if(on)b.textContent='• '+b.textContent+' •'})}
document.querySelectorAll('button').forEach(b=>b.onclick=()=>go(b.dataset.k));go('sep');
</script></body></html>""" % (tot["sep"], tot["oct"], json.dumps(img))
open(os.path.join(HERE, "superficie_pba2025.html"), "w", encoding="utf8").write(html)
print("listo")
