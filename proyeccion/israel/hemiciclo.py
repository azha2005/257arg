"""Hemiciclo de la Knesset (120 bancas) al estilo de los diagramas de la Wikipedia: bancas en filas concentricas,
ordenadas por angulo de izquierda a derecha. Colores de {{party color}} de la Wikipedia en ingles (27-oct-2026).
Para los bloques la Wikipedia solo usa un lavanda palido (#D9D9F8) para el bloque de gobierno, asi que cada bloque
lleva el color de su lista principal: Likud (Netanyahu), Yashar (oposicion), Lista Conjunta (arabes); los Reservistas
van aparte con su propio color."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLOR = {"Likud": "#1f5aa5", "Yashar (Eisenkot)": "#62B9F2", "Juntos (Bennett-Lapid)": "#2A2A78",
         "Lista Conjunta": "#01B2AC", "Israel Beitenu": "#23C2EB", "Los Demócratas": "#2A38D7", "Shas": "#000000",
         "Raam": "#15793D", "UTJ": "#003366", "Sionismo Religioso-Zehut": "#4F9298", "Otzma Yehudit": "#FF4500",
         "Noam": "#00B2EF", "Amcha Yisrael (Winter)": "#8f36bf", "Reservistas-Nuevo Partido Economico": "#68692C",
         "Kajol Lavan (Gantz)": "#0DAAFF"}
# de izquierda a derecha
ORDEN = ["Lista Conjunta", "Raam", "Los Demócratas", "Juntos (Bennett-Lapid)", "Yashar (Eisenkot)", "Israel Beitenu",
         "Kajol Lavan (Gantz)", "Reservistas-Nuevo Partido Economico", "Likud", "Shas", "UTJ",
         "Sionismo Religioso-Zehut", "Otzma Yehudit", "Noam", "Amcha Yisrael (Winter)"]
BLOQUES = [("Árabes", "#01B2AC", ["Lista Conjunta", "Raam"]),
           ("Oposición", "#62B9F2", ["Los Demócratas", "Juntos (Bennett-Lapid)", "Yashar (Eisenkot)",
                                      "Israel Beitenu", "Kajol Lavan (Gantz)"]),
           ("Reservistas", "#68692C", ["Reservistas-Nuevo Partido Economico"]),
           ("Bloque de Netanyahu", "#1f5aa5", ["Likud", "Shas", "UTJ", "Sionismo Religioso-Zehut", "Otzma Yehudit",
                                               "Noam", "Amcha Yisrael (Winter)"])]
CORTO = {"Juntos (Bennett-Lapid)": "Juntos", "Yashar (Eisenkot)": "Yashar", "Sionismo Religioso-Zehut":
         "Sionismo Religioso", "Reservistas-Nuevo Partido Economico": "Reservistas",
         "Amcha Yisrael (Winter)": "Amcha Yisrael", "Kajol Lavan (Gantz)": "Kajol Lavan"}


def asientos(n=120, filas=8, r0=0.38):
    """Posiciones (x, y) de n bancas en filas concentricas, ordenadas de izquierda a derecha."""
    radios = np.linspace(r0, 1, filas)
    cap = radios / radios.sum() * n
    k = np.floor(cap).astype(int)
    k[np.argsort(-(cap - k))[:n - k.sum()]] += 1
    pts = []
    for r, m in zip(radios, k):
        for a in np.linspace(np.pi, 0, m) if m > 1 else [np.pi / 2]:
            pts.append((a, r))
    pts.sort(key=lambda p: (-p[0], p[1]))
    return np.array([(r * np.cos(a), r * np.sin(a)) for a, r in pts]), 0.5 * (1 - r0) / (filas - 1)


def dibujar(path, grupos, titulo, subtitulo):
    """grupos = [(etiqueta, color, bancas)] de izquierda a derecha."""
    xy, d = asientos()
    cols = sum([[c] * b for _, c, b in grupos], [])
    cols += ["#dddddd"] * (120 - len(cols))
    fig, ax = plt.subplots(figsize=(10, 6.6), dpi=150)
    for (x, y), c in zip(xy, cols):
        ax.add_patch(plt.Circle((x, y), d * 0.92, color=c, ec="white", lw=0.4))
    ax.plot([0, 0], [0.33, 1.06], color="#888", lw=0.8, ls=(0, (3, 3)))
    ax.text(0, 1.08, "61", ha="center", va="bottom", fontsize=9, color="#555")
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-0.62, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.suptitle(titulo, fontsize=15, fontweight="bold", y=0.97)
    ax.set_title(subtitulo, fontsize=9.5, color="#444", pad=2)
    vis = [(e, c, b) for e, c, b in grupos if b > 0]
    ncol = 3 if len(vis) > 6 else 2
    for i, (e, c, b) in enumerate(vis):
        fila, col = divmod(i, ncol)
        x0, y0 = -1.0 + col * (2.0 / ncol), -0.12 - fila * 0.1
        ax.add_patch(plt.Rectangle((x0, y0 - 0.03), 0.06, 0.06, color=c))
        ax.text(x0 + 0.09, y0, "%s  %d" % (e, b), va="center", fontsize=10.5)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def dibujar_ambos(seats, base, titulo, subtitulo):
    """seats = {lista: bancas}. Guarda <base>_listas.png y <base>_bloques.png."""
    listas = [(CORTO.get(n, n), COLOR.get(n, "#999"), int(seats.get(n, 0))) for n in ORDEN]
    listas += [(n, "#999", int(b)) for n, b in seats.items() if n not in ORDEN and b > 0]
    dibujar(base + "_listas.png", listas, titulo, subtitulo)
    bloques = [(e, c, int(sum(seats.get(n, 0) for n in ns))) for e, c, ns in BLOQUES]
    dibujar(base + "_bloques.png", bloques, titulo, subtitulo)
    return base + "_listas.png", base + "_bloques.png"
