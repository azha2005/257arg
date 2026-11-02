"""Sitio de GitHub Pages con todos los atlas (2-nov-2026).

    python sitio/armar.py miniaturas [filtro]   # capturas en sitio/miniaturas/ (Chrome con Playwright)
    python sitio/armar.py indice               # sitio/index.html desde catalogo.py
    python sitio/armar.py copiar _site         # arma el sitio (lo corre el workflow .github/workflows/pages.yml)

El índice sigue el estilo Ink de transferencias/provinciales/INDICE.html, con modo oscuro.
"""
import glob, html, io, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalogo import GRUPOS, EXTRA, MINI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "sitio")
MINIS = os.path.join(HERE, "miniaturas")


def entradas():
    for g in GRUPOS:
        for e in g[3]: yield e


def mini_nombre(ruta):
    return ruta.replace("mapas/", "").replace("/", "__").replace(".html", ".webp")


def miniaturas(filtro=""):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    os.makedirs(MINIS, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1920, "height": 1700})
        for ruta, *_ in entradas():
            if filtro not in ruta: continue
            src = MINI.get(ruta, ruta)
            pg.goto("about:blank")
            pg.goto("file:///" + os.path.join(ROOT, src).replace(os.sep, "/"))
            pg.wait_for_timeout(2500)
            im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
            im.thumbnail((640, 640), Image.LANCZOS)
            im.save(os.path.join(MINIS, mini_nombre(ruta)), "WEBP", quality=72, method=6)
            print(ruta, flush=True)
        b.close()


CSS = open(os.path.join(HERE, "estilo.css"), encoding="utf8").read()


def indice():
    n = sum(1 for _ in entradas())
    nav = "".join(f'<a href="#{gid}">{html.escape(t.split(",")[0])}</a>' for gid, t, _, _ in GRUPOS)
    secs = []
    for gid, titulo, bajada, items in GRUPOS:
        cards = []
        for ruta, anio, rot, nota in items:
            m = mini_nombre(ruta)
            ok = os.path.exists(os.path.join(MINIS, m))
            img = (f'<img src="miniaturas/{m}" alt="" loading="lazy" width="640" height="567">' if ok else "")
            nota_h = f'<span class="nota">{html.escape(nota)}</span>' if nota else ""
            cards.append(f'<li><a class="atlas" href="{ruta}"><span class="mini">{img}</span>'
                         f'<span class="anio num">{anio}</span><span class="rot">{html.escape(rot)}</span>{nota_h}</a></li>')
        secs.append(f'<section id="{gid}" aria-labelledby="h-{gid}"><div class="cab"><h2 id="h-{gid}">{html.escape(titulo)}</h2>'
                    f'<p>{html.escape(bajada)}</p></div><ul class="grilla">{"".join(cards)}</ul></section>')
    out = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas electorales argentinos</title>
<meta name="description" content="{n} atlas electorales de la Argentina por departamento, circuito y radio censal, de 1912 a 2025, al estilo de los mapas de la Wikipedia.">
<link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;600;700&display=swap" rel="stylesheet">
<script>try{{const t=localStorage.getItem("tema");if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<style>
{CSS}</style></head>
<body>
<header class="tope"><div class="container fila"><a class="marca" href="./">Atlas electorales</a>
<nav aria-label="Secciones">{nav}</nav>
<button type="button" class="tema" id="tema" aria-label="Cambiar entre modo claro y oscuro">Modo oscuro</button></div></header>
<main>
<section class="hero container"><h1>Cómo votó la Argentina, departamento por departamento</h1>
<p class="lead">{n} atlas interactivos de 1912 a 2025, al estilo Wikipedia.</p>
<p class="acc"><a class="btn" href="#1912-1930">Ver los atlas</a></p></section>
<div class="container">{"".join(secs)}</div>
</main>
<footer class="pie"><div class="container">
<p>Cada atlas es un HTML autocontenido: pestañas por modo, ficha de cada unidad y descarga en SVG o PNG. Lo que falta queda en beige y rotulado; no se imputa.</p>
<p>Fuentes: Darío Cantón, base de Ernesto Calvo, Lupu y Stokes, DINE, PolAr (Andy Tow), CNE, Wikipedia. Cartografía de Rodríguez (CEUR-CONICET), CC BY 2.5 Argentina. Código y datos en <a href="https://github.com/azha2005/257arg">github.com/azha2005/257arg</a>.</p>
</div></footer>
<script>
(function(){{const b=document.getElementById("tema"),r=document.documentElement;
function oscuro(){{return r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;}}
function rot(){{b.textContent=oscuro()?"Modo claro":"Modo oscuro";}}
b.addEventListener("click",function(){{r.dataset.theme=oscuro()?"light":"dark";try{{localStorage.setItem("tema",r.dataset.theme);}}catch(e){{}}rot();}});rot();}})();
</script>
</body></html>
"""
    open(os.path.join(HERE, "index.html"), "w", encoding="utf8", newline="\n").write(out)
    print("index.html,", n, "entradas")


# Solo en la copia publicada (los HTML del repo no cambian): enlace al índice, la nota de fuentes plegada
# y el modo claro u oscuro que eligió el visitante en el índice (localStorage «tema», el mismo origen).
SITIO_CSS = ('<style>/*sitio*/#bar a.sitio-ind{color:var(--ctlfg);text-decoration:none;font-weight:600;padding:4px 6px}'
             '#bar a.sitio-ind:hover{text-decoration:underline}'
             '#barnote-d{flex-basis:100%;order:9;color:var(--mut);font-size:13px}'
             '#barnote-d summary{cursor:pointer;width:max-content}#barnote-d #barnote{margin-top:4px}</style>\n')
SITIO_JS = ('<script>/*sitio*/(function(){var b=document.body,bar=document.getElementById("bar"),n=document.getElementById("barnote");'
            'if(bar){var a=document.createElement("a");a.className="sitio-ind";a.href="../../";a.textContent="Todos los atlas";'
            'bar.insertBefore(a,bar.firstChild);}'
            'if(n){var d=document.createElement("details");d.id="barnote-d";var s=document.createElement("summary");'
            's.textContent="Fuentes y notas";d.appendChild(s);n.parentNode.insertBefore(d,n);d.appendChild(n);}'
            'var t=null;try{t=localStorage.getItem("tema");}catch(e){}'
            'var claro=t?t==="light":matchMedia("(prefers-color-scheme: light)").matches;'
            'if(claro&&location.hash.indexOf("bare")<0){b.dataset.bg="white";var g=document.getElementById("b-bg");if(g)g.textContent="Fondo: blanco";}'
            '})();</script>\n')


def preparar(html):
    if "/*sitio*/" in html or '<div id="bar">' not in html: return html
    html = html.replace("</head>", SITIO_CSS + "</head>", 1)
    i = html.rindex("</body>") if "</body>" in html else len(html)
    return html[:i] + SITIO_JS + html[i:]


def copiar(dest):
    rutas = [e[0] for e in entradas()]
    for pat in EXTRA: rutas += [os.path.relpath(f, ROOT).replace(os.sep, "/") for f in glob.glob(os.path.join(ROOT, pat))]
    os.makedirs(dest, exist_ok=True)
    shutil.copy(os.path.join(HERE, "index.html"), dest)
    shutil.copytree(MINIS, os.path.join(dest, "miniaturas"), dirs_exist_ok=True)
    open(os.path.join(dest, ".nojekyll"), "w").close()
    tot = 0
    for r in sorted(set(rutas)):
        d = os.path.join(dest, r); os.makedirs(os.path.dirname(d), exist_ok=True)
        s = open(os.path.join(ROOT, r), encoding="utf8").read()
        open(d, "w", encoding="utf8", newline="").write(preparar(s)); tot += os.path.getsize(d)
    print(len(set(rutas)), "HTML,", round(tot / 2**20), "MB")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "miniaturas": miniaturas(sys.argv[2] if len(sys.argv) > 2 else "")
    elif cmd == "indice": indice()
    elif cmd == "copiar": copiar(sys.argv[2])
