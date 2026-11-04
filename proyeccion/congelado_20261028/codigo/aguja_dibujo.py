"""Dibujo de una aguja al estilo del New York Times 2020 (dial semicircular con el margen estimado, zonas
«empate / inclinado / probable / muy probable», franja del 50 % y del 95 %, y debajo la evolucion de la aguja).
Lo usan aguja_fotos.py y aguja_brasil.py."""
import textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Wedge, Polygon, Circle
from matplotlib import font_manager

for _f in ("Franklin Gothic Medium", "Arial", "DejaVu Sans"):
    if any(f.name == _f for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = _f
        break
GRIS, TINTA, SUAVE = "#d9d9d9", "#121212", "#727272"
ZONAS = [(0.05, "Empate"), (0.25, "Inclinado"), (0.5, "Probable"), (1.0, "Muy probable")]


def _mezcla(c, t):
    c = np.array(matplotlib.colors.to_rgb(c))
    return tuple(1 - t * (1 - c))


def _ang(m, escala):
    return 90 - 90 * np.clip(m / escala, -1, 1)


def _fmt(m, izq, der):
    return "%s +%.1f" % ((der if m >= 0 else izq)[1], abs(m))


def dibujar(path, titulo, subtitulo, izq, der, margen, p25, p75, p2, p97, prob, escala, serie, real=None,
            real_lab="", fuerzas=(), pie="", momento=None,
            fuerzas_lab="votos positivos", prob_izq=None, prob_lab="probabilidad de ganar"):
    """izq/der = (nombre, sigla, color); margen = der - izq en puntos; prob = probabilidad de que gane der.
    serie = dict(x, margen, p25, p75, p2, p97, crudo, xlabel, crudo_lab, tiempo, n)."""
    fig = plt.figure(figsize=(8, 10.4), dpi=150, facecolor="white")
    fig.text(0.06, 0.965, titulo, fontsize=17, weight="bold", color=TINTA, va="top")
    fig.text(0.06, 0.928, textwrap.fill(subtitulo, 112), fontsize=9.5, color=SUAVE, va="top")
    # dial
    ax = fig.add_axes([0.08, 0.53, 0.84, 0.34])
    ax.set_xlim(-1.18, 1.18)
    ax.set_ylim(-0.42, 1.12)
    ax.set_aspect("equal")
    ax.axis("off")
    r0, r1 = 0.58, 1.0
    lim = [0] + [z[0] for z in ZONAS]
    for lado, (nom, sig, col) in ((1, der), (-1, izq)):
        for i, (hi, lab) in enumerate(ZONAS):
            lo = lim[i]
            if i == 0:
                continue
            t = 0.35 + 0.65 * i / (len(ZONAS) - 1)
            a1, a2 = sorted([_ang(lado * lo * escala, escala), _ang(lado * hi * escala, escala)])
            ax.add_patch(Wedge((0, 0), r1, a1, a2, width=r1 - r0, fc=_mezcla(col, t), ec="white", lw=1.5))
            am = np.radians((a1 + a2) / 2)
            rot = (a1 + a2) / 2 - 90
            ax.text(0.79 * np.cos(am), 0.79 * np.sin(am), lab.upper() if i < 3 else "MUY\nPROBABLE",
                    ha="center", va="center", rotation=rot, fontsize=5.9 if i == 1 else 6.6,
                    color="white" if t > 0.6 else TINTA, weight="bold", linespacing=0.9)
    a1, a2 = _ang(ZONAS[0][0] * escala, escala), _ang(-ZONAS[0][0] * escala, escala)
    ax.add_patch(Wedge((0, 0), r1, a1, a2, width=r1 - r0, fc=GRIS, ec="white", lw=1.5))
    ax.text(0, 1.1, "EMPATE", ha="center", va="center", fontsize=7.5, weight="bold", color=SUAVE)
    # franjas de incertidumbre (la aguja del NYT tiembla dentro de la del 50 %)
    for lo, hi, al in ((p2, p97, 0.16), (p25, p75, 0.34)):
        b1, b2 = sorted([_ang(lo, escala), _ang(hi, escala)])
        ax.add_patch(Wedge((0, 0), r0 - 0.02, b1, b2, fc=TINTA, alpha=al, lw=0))
    # marcas
    for m in np.arange(-escala, escala + 1e-9, escala / 4):
        a = np.radians(_ang(m, escala))
        ax.plot([1.0 * np.cos(a), 1.04 * np.cos(a)], [1.0 * np.sin(a), 1.04 * np.sin(a)], color=SUAVE, lw=0.8)
        if m:
            ax.text(1.1 * np.cos(a), 1.1 * np.sin(a), "+%g" % abs(m), ha="center", va="center", fontsize=7.5,
                    color=SUAVE)
    # aguja
    a = np.radians(_ang(margen, escala))
    tip = np.array([0.97 * np.cos(a), 0.97 * np.sin(a)])
    n = np.array([-np.sin(a), np.cos(a)]) * 0.028
    ax.add_patch(Polygon([tip, n, -n], closed=True, fc=TINTA, ec=TINTA, zorder=5))
    ax.add_patch(Circle((0, 0), 0.05, fc=TINTA, zorder=6))
    # nombres y cifras
    for lado, (nom, sig, col), p in ((-1, izq, 1 - prob if prob_izq is None else prob_izq), (1, der, prob)):
        x = lado * 1.0
        ha = "left" if lado < 0 else "right"
        ax.text(x, -0.07, nom, ha=ha, va="top", fontsize=12, weight="bold", color=col)
        ax.text(x, -0.2, "%s %%" % _pct(p), ha=ha, va="top", fontsize=19, weight="bold", color=col)
        ax.text(x, -0.35, prob_lab, ha=ha, va="top", fontsize=8, color=SUAVE)
    ax.text(0, -0.09, "MARGEN ESTIMADO", ha="center", va="top", fontsize=7.5, color=SUAVE, weight="bold")
    ax.text(0, -0.17, _fmt(margen, izq, der), ha="center", va="top", fontsize=21, weight="bold",
            color=(der if margen >= 0 else izq)[2])
    r95 = sorted([p2, p97], key=abs) if p2 * p97 > 0 else [p2, p97]
    ax.text(0, -0.34, "95 %%: %s a %s" % (_fmt(r95[0], izq, der), _fmt(r95[1], izq, der)), ha="center", va="top",
            fontsize=8, color=SUAVE)
    # fuerzas
    if len(fuerzas):
        fig.text(0.06, 0.505, "Proyección por fuerza (%% de %s):  " % fuerzas_lab + "   ".join(
            "%s %.1f" % (f, v) for f, v in fuerzas), fontsize=8.8, color=TINTA, va="top")
    # evolucion
    bx = fig.add_axes([0.1, 0.12, 0.84, 0.33])
    x = serie["x"]
    col_m = lambda v: der[2] if v >= 0 else izq[2]
    bx.fill_between(x, serie["p2"], serie["p97"], color=TINTA, alpha=0.08, lw=0, step=None)
    bx.fill_between(x, serie["p25"], serie["p75"], color=TINTA, alpha=0.16, lw=0)
    bx.axhline(0, color=SUAVE, lw=0.8)
    if real is not None:
        bx.axhline(real, color=col_m(real), lw=1, ls=(0, (4, 3)))
        bx.text(x[0], real, " " + real_lab, fontsize=7.5, color=col_m(real), va="bottom")
    if serie.get("crudo") is not None:
        bx.plot(x, serie["crudo"], color=SUAVE, lw=1.1, ls=":", marker="o" if serie.get("tiempo") else None, ms=2.5)
        bx.text(x[-1], serie["crudo"][-1], serie["crudo_lab"] + "\n", fontsize=7.5, color=SUAVE, va="bottom",
                ha="right")
    mg = np.array(serie["margen"])
    for i in range(len(x) - 1):
        bx.plot(x[i:i + 2], mg[i:i + 2], color=col_m((mg[i] + mg[i + 1]) / 2), lw=2.4, solid_capstyle="round")
    if serie.get("tiempo"):
        bx.scatter(x, mg, s=14, color=[col_m(v) for v in mg], zorder=4)
        bx.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        bx.set_xscale("log")
        bx.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ("%g" % (100 * v)) + " %"))
    if momento is not None:
        bx.axvline(momento, color=TINTA, lw=0.8)
        bx.text(momento, bx.get_ylim()[1], " la aguja de arriba", fontsize=7.5, color=TINTA, va="top")
    bx.text(-0.01, 1.04, "Margen estimado a lo largo de la noche  (%s arriba, %s abajo)" % (der[1], izq[1]),
            transform=bx.transAxes, fontsize=9.5, weight="bold", color=TINTA)
    bx.set_xlabel(serie["xlabel"], fontsize=8.5, color=SUAVE)
    bx.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: ("%s +%g" % ((der if v > 0 else izq)[1], abs(v))) if v else "0"))
    for s in ("top", "right", "left"):
        bx.spines[s].set_visible(False)
    bx.tick_params(labelsize=8, colors=SUAVE, length=0)
    bx.grid(axis="y", color="#eeeeee", lw=0.8)
    fig.text(0.06, 0.035, textwrap.fill(pie, 150), fontsize=7.6, color=SUAVE, va="bottom")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("->", path)


def _pct(p):
    if p > 0.99:
        return ">99"
    if p < 0.01:
        return "<1"
    return "%.0f" % (100 * p)


def dibujar_bancas(path, titulo, subtitulo, bibi, p50, p95, probs, colores, serie, real=None, bancas_txt="",
                   pie="", momento=None, vmin=45, vmax=77, mayoria=61):
    """Aguja de una mayoria parlamentaria: el dial marca las bancas del bloque de gobierno (vmin a vmax, la mayoria
    arriba); probs = [(etiqueta, probabilidad, color), ...] con los desenlaces; serie = dict(x, bibi, b25, b75, b5,
    b95, opo, o25, o75, conteo, xlabel); real = (bancas reales del bloque, de la oposicion)."""
    fig = plt.figure(figsize=(8, 10.4), dpi=150, facecolor="white")
    fig.text(0.06, 0.965, titulo, fontsize=17, weight="bold", color=TINTA, va="top")
    fig.text(0.06, 0.928, textwrap.fill(subtitulo, 112), fontsize=9.5, color=SUAVE, va="top")
    ax = fig.add_axes([0.08, 0.53, 0.84, 0.34])
    ax.set_xlim(-1.18, 1.18)
    ax.set_ylim(-0.46, 1.12)
    ax.set_aspect("equal")
    ax.axis("off")
    ang = lambda v: 180 - 180 * (np.clip(v, vmin, vmax) - vmin) / (vmax - vmin)
    r0, r1 = 0.58, 1.0
    cb, co = colores["bibi"], colores["sin"]
    cortes = [vmin, mayoria - 6, mayoria - 2, mayoria - 0.5, mayoria + 1.5, mayoria + 5.5, vmax]
    tonos = [(co, 1.0, "LEJOS"), (co, 0.7, "CERCA"), (co, 0.45, ""), (cb, 0.45, ""), (cb, 0.7, "JUSTA"),
             (cb, 1.0, "AMPLIA")]
    for (a, b), (c, t, lab) in zip(zip(cortes[:-1], cortes[1:]), tonos):
        a1, a2 = sorted([ang(a), ang(b)])
        ax.add_patch(Wedge((0, 0), r1, a1, a2, width=r1 - r0, fc=_mezcla(c, t), ec="white", lw=1.5))
        if lab:
            am = np.radians((a1 + a2) / 2)
            ax.text(0.79 * np.cos(am), 0.79 * np.sin(am), lab, ha="center", va="center", rotation=(a1 + a2) / 2 - 90,
                    fontsize=6.6, weight="bold", color="white" if t > 0.6 else TINTA)
    a = np.radians(ang(mayoria - 0.5))
    ax.plot([0.55 * np.cos(a), 1.06 * np.cos(a)], [0.55 * np.sin(a), 1.06 * np.sin(a)], color=TINTA, lw=1.2)
    ax.text(1.13 * np.cos(a), 1.13 * np.sin(a), "%d = mayoría" % mayoria, ha="center", va="bottom", fontsize=8,
            weight="bold", color=TINTA)
    for v in range(vmin, vmax + 1, 5):
        if abs(v - mayoria) < 2:
            continue
        a = np.radians(ang(v))
        ax.plot([np.cos(a), 1.04 * np.cos(a)], [np.sin(a), 1.04 * np.sin(a)], color=SUAVE, lw=0.8)
        ax.text(1.1 * np.cos(a), 1.1 * np.sin(a), str(v), ha="center", va="center", fontsize=7.5, color=SUAVE)
    for (lo, hi), al in ((p95, 0.16), (p50, 0.34)):
        b1, b2 = sorted([ang(lo - 0.5), ang(hi + 0.5)])
        ax.add_patch(Wedge((0, 0), r0 - 0.02, b1, b2, fc=TINTA, alpha=al, lw=0))
    a = np.radians(ang(bibi))
    tip = np.array([0.97 * np.cos(a), 0.97 * np.sin(a)])
    nn = np.array([-np.sin(a), np.cos(a)]) * 0.028
    ax.add_patch(Polygon([tip, nn, -nn], closed=True, fc=TINTA, ec=TINTA, zorder=5))
    ax.add_patch(Circle((0, 0), 0.05, fc=TINTA, zorder=6))
    ax.text(0, -0.09, "BLOQUE DE NETANYAHU", ha="center", va="top", fontsize=7.5, color=SUAVE, weight="bold")
    ax.text(0, -0.17, "%d bancas" % bibi, ha="center", va="top", fontsize=21, weight="bold",
            color=cb if bibi >= mayoria else co)
    ax.text(0, -0.34, "95 %%: %d a %d" % p95, ha="center", va="top", fontsize=8, color=SUAVE)
    for (lab, p, c), x, ha in zip(probs, (-1.0, 0, 1.0), ("left", "center", "right")):
        if x == 0:
            continue
        ax.text(x, -0.07, lab, ha=ha, va="top", fontsize=10.5, weight="bold", color=c)
        ax.text(x, -0.2, "%s %%" % _pct(p), ha=ha, va="top", fontsize=19, weight="bold", color=c)
    lab, p, c = probs[1]
    ax.text(0, -0.41, "%s: %s %%" % (lab, _pct(p)), ha="center", va="top", fontsize=9, weight="bold", color=c)
    if bancas_txt:
        fig.text(0.06, 0.5, textwrap.fill(bancas_txt, 130), fontsize=8.4, color=TINTA, va="top")
    if serie is None:                                  # sin evolucion (una sola foto de la noche)
        fig.text(0.06, 0.035, textwrap.fill(pie, 150), fontsize=7.6, color=SUAVE, va="bottom")
        fig.savefig(path, facecolor="white")
        plt.close(fig)
        print("->", path)
        return
    bx = fig.add_axes([0.1, 0.12, 0.84, 0.31])
    x = serie["x"]
    for k, kk, col, nom in (("bibi", "b", cb, "bloque de Netanyahu"), ("opo", "o", co, "oposición judía")):
        bx.fill_between(x, serie[kk + "5"], serie[kk + "95"], color=col, alpha=0.10, lw=0, step="post")
        bx.fill_between(x, serie[kk + "25"], serie[kk + "75"], color=col, alpha=0.22, lw=0, step="post")
        bx.step(x, serie[k], where="post", color=col, lw=2.2)
        bx.text(x[-1], serie[k][-1] + (1.2 if k == "bibi" else -1.2), nom, color=col, fontsize=8, ha="right",
                va="bottom" if k == "bibi" else "top", weight="bold")
        if serie.get("conteo_" + k) is not None:
            bx.step(x, serie["conteo_" + k], where="post", color=col, lw=0.9, ls=":")
    bx.set_ylim(max(20, mayoria - 30), min(100, mayoria + 22))
    bx.axhline(mayoria, color=TINTA, lw=0.9)
    bx.text(x[0], mayoria + 0.3, "mayoría (61)", fontsize=7.5, color=TINTA, va="bottom")
    if real is not None:
        for v, col in zip(real, (cb, co)):
            bx.axhline(v, color=col, lw=0.9, ls=(0, (4, 3)))
    if momento is not None:
        bx.axvline(momento, color=TINTA, lw=0.8)
        bx.text(momento, bx.get_ylim()[1], "la aguja de arriba ", fontsize=7.5, color=TINTA, va="top", ha="right")
    bx.set_xscale("log")
    bx.set_xticks([t for t in (0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1) if min(x) / 1.5 <= t <= max(x) * 1.5])
    bx.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ("%g" % (100 * v)) + " %"))
    bx.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    bx.text(-0.01, 1.04, "Bancas proyectadas a lo largo del conteo (punteado: el conteo parcial tal cual%s)" % (
            "; rayado: resultado final" if real is not None else ""), transform=bx.transAxes, fontsize=9,
            weight="bold", color=TINTA)
    bx.set_xlabel(serie["xlabel"], fontsize=8.5, color=SUAVE)
    for s in ("top", "right", "left"):
        bx.spines[s].set_visible(False)
    bx.tick_params(labelsize=8, colors=SUAVE, length=0)
    bx.grid(axis="y", color="#eeeeee", lw=0.8)
    fig.text(0.06, 0.035, textwrap.fill(pie, 150), fontsize=7.6, color=SUAVE, va="bottom")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("->", path)
