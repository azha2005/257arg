"""Imagen para compartir (og:image, 1200x630, fondo oscuro) de cada uno de los ocho escenarios 2003alt (4-nov-2026).
    python analisis/remake2003/portadas.py
Toma el póster «Ganó» de png_transparentes/mapa2003alt/ (resolución completa) sobre el papel oscuro del sitio, con
el título, la vuelta y el crédito al autor del original. Escribe mapas/mapa2003alt/miniaturas/portada_<id>.jpg y agrega
a cada atlas_2003alt_<id>.html descripción, canónica, Open Graph y tarjeta de X/Twitter (idempotente, entre marcas).
Usa Playwright con el Chrome del sistema y la Epilogue de mapas/mapa2003alt/assets/."""
import base64, html, io, json, os, re
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "mapas/mapa2003alt"
URL = "https://azha2005.github.io/257arg/mapas/mapa2003alt/"
AUTOR = "u/Alarmed_Rope5383"
PAPEL = (20, 22, 25)   # oklch(17% 0.004 250), el papel oscuro del sitio


def datos():
    entries = json.loads((DEST / "manifiesto.json").read_text("utf8"))
    cfg = {s["id"]: s for s in json.loads((Path(__file__).parent / "escenarios.json").read_text("utf8"))}
    return [(s["id"], s["title"], cfg[s["id"]]["round"], s["html"]) for s in entries]


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def tarjeta(sid, titulo, vuelta):
    im = Image.open(ROOT / "png_transparentes/mapa2003alt" / f"atlas_2003alt_{sid}_gan.png").convert("RGBA")
    fondo = Image.new("RGBA", im.size, PAPEL + (255,)); fondo.alpha_composite(im)
    buf = io.BytesIO(); fondo.convert("RGB").save(buf, "PNG")
    poster = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    fuentes = "".join(f'@font-face{{font-family:E;font-weight:{w};src:url("{b64(DEST / "assets" / f"epilogue-{w}.woff2", "font/woff2")}") format("woff2")}}'
                      for w in (400, 600, 700))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fuentes}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:rgb{PAPEL};font-family:E,sans-serif;color:#f1f1ef}}
.t{{display:grid;grid-template-columns:420px 1fr;height:630px}}
.izq{{display:flex;flex-direction:column;justify-content:center;gap:18px;padding:0 0 0 52px}}
.k{{font-size:17px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#5cc6c0}}
h1{{margin:0;font-size:54px;font-weight:700;letter-spacing:-.04em;line-height:1}}
.v{{font-size:24px;color:#b9b9b4}}
.c{{margin-top:22px;padding-top:18px;border-top:1px solid #3a3d42;font-size:18px;line-height:1.45;color:#a9a9a4}}
.c b{{color:#f1f1ef;font-weight:600}}
.der{{display:flex;align-items:center;justify-content:center;padding:10px 10px 10px 0}}
.der img{{max-width:100%;max-height:610px;display:block}}</style></head><body><div class="t">
<div class="izq"><div class="k">Elecciones alternativas de 2003</div><h1>{html.escape(titulo)}</h1><div class="v">{html.escape(vuelta)} · escenario hipotético</div>
<div class="c">Mapa original de <b>{AUTOR}</b>, rehecho en un atlas interactivo con votos locales estimados.<br><b>azha2005.github.io/257arg</b></div></div>
<div class="der"><img src="{poster}" alt=""></div></div></body></html>"""


def cabecera(sid, titulo, vuelta, pagina):
    img = URL + f"miniaturas/portada_{sid}.jpg"
    desc = (f"{titulo}: elección presidencial alternativa de 2003 ({vuelta.lower()}), por departamento. "
            f"Remake interactivo del mapa de {AUTOR}, con resultados locales estimados.")
    og = f"Escenario hipotético de 2003 ({vuelta.lower()}). Mapa original de {AUTOR}, rehecho como atlas interactivo."
    alt = f"Mapa por departamento del escenario {titulo}, elecciones alternativas de 2003"
    e = lambda s: html.escape(s, quote=True)
    return (f'<!--og-->\n<meta name="description" content="{e(desc)}">\n<link rel="canonical" href="{URL + pagina}">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Atlas electorales argentinos">\n'
            f'<meta property="og:locale" content="es_AR">\n<meta property="og:url" content="{URL + pagina}">\n'
            f'<meta property="og:title" content="{e("2003 alternativo: " + titulo)}">\n<meta property="og:description" content="{e(og)}">\n'
            f'<meta property="og:image" content="{img}">\n<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{e(alt)}">\n<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:image" content="{img}">\n<meta name="twitter:image:alt" content="{e(alt)}">\n<!--/og-->\n')


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=2)
        for sid, titulo, vuelta, pagina in datos():
            pg.set_content(tarjeta(sid, titulo, vuelta)); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB").resize((1200, 630), Image.LANCZOS)
            im.save(DEST / "miniaturas" / f"portada_{sid}.jpg", quality=88, optimize=True, progressive=True)
            f = DEST / pagina
            s = f.read_bytes().decode("utf8")   # se conservan los finales de línea CRLF del constructor
            s = re.sub(r"<!--og-->.*?<!--/og-->\r?\n", "", s, flags=re.S)
            i = s.index("\n", s.index("</title>")) + 1
            nl = "\r\n" if s[i - 2:i] == "\r\n" else "\n"
            f.write_bytes((s[:i] + cabecera(sid, titulo, vuelta, pagina).replace("\n", nl) + s[i:]).encode("utf8"))
            print(sid, "listo", flush=True)
        b.close()


if __name__ == "__main__":
    main()
