"""Portada social (og:image, 1200x630) y miniaturas del índice del sitio para el visor de Capital (7-nov-2026).
    python mapas/capital_canton/portada.py
Abre capital_1864_2007.html con Playwright (Chrome del sistema), captura el mapa de cuatro elecciones
(diputados 1864 y 1896 por parroquia, presidente 1946 y Jefe de Gobierno 2003, 2.ª vuelta) y los compone en una tarjeta
con el estilo Ink de la página. Los mapas salen de la página misma; no se dibuja nada a mano.
Salidas: mapas/capital_canton/portada.png (se publica como capital/portada.png) y
sitio/miniaturas/capital__index{,_claro}.webp (oscura y clara, como las demás tarjetas del índice)."""
import base64, io, os
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = "file:///" + os.path.join(HERE, "capital_1864_2007.html").replace(os.sep, "/")
MINIS = os.path.join(ROOT, "sitio", "miniaturas")
ELECCIONES = [(1, "1864", "Diputados, por parroquia"), (21, "1896", "Diputados, por parroquia"),
              (57, "1946", "Presidente"), (101, "2003", "Jefe de Gobierno, 2.ª vuelta")]

TEMA = {  # tokens de la página (plantilla.html), en hex para la tarjeta
    "light": dict(papel="#fcfcfa", tinta="#1b1b1b", mute="#5e5e5e", regla="#e2e2de", acento="#00777a"),
    "dark": dict(papel="#141619", tinta="#f0f0f0", mute="#adadad", regla="#3a3c40", acento="#5cc6c0"),
}


def mapa(pg, n, tema):
    pg.goto("about:blank")
    pg.add_init_script(f'try{{localStorage.setItem("tema","{tema}")}}catch(e){{}}')
    pg.goto(f"{SRC}#n={n}&m=gan&s=T")
    pg.wait_for_timeout(1500)
    pg.evaluate('document.querySelectorAll(".pp text,.parrEtiquetas,.num").forEach(e=>e.style.display="none");'
                'document.documentElement.style.background=document.body.style.background="transparent"')
    return pg.locator("#svg").screenshot(omit_background=True)


def uri(png):
    return "data:image/png;base64," + base64.b64encode(png).decode()


def tarjeta(pg, imgs, t, w, h, mini):
    cols = "".join(
        f'<figure><img src="{uri(p)}"><figcaption><b>{a}</b>{"" if mini else "<span>" + r + "</span>"}</figcaption></figure>'
        for p, (_, a, r) in zip(imgs, ELECCIONES))
    texto = "" if mini else (
        '<div class="txt"><h1>Ciudad de Buenos Aires, <em>1864-2007</em></h1>'
        '<p>104 elecciones por parroquia y circunscripción.</p>'
        '<p class="url">azha2005.github.io/257arg/capital</p></div>')
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Epilogue:wght@400;600;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:{t['papel']};color:{t['tinta']};font-family:Epilogue,system-ui,sans-serif}}
#c{{width:{w}px;height:{h}px;box-sizing:border-box;padding:{20 if mini else 44}px;display:flex;flex-direction:column;gap:{8 if mini else 20}px}}
h1{{margin:0;font-size:50px;font-weight:700;letter-spacing:-.035em;line-height:1.05}}
h1 em{{font-style:normal;color:{t['acento']}}}
.txt p{{margin:10px 0 0;font-size:23px;color:{t['mute']}}}
.txt p.url{{font-size:18px;font-weight:600;color:{t['acento']}}}
.mapas{{flex:1;min-height:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:{10 if mini else 24}px}}
.mini .mapas{{grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr))}}
figure{{margin:0;display:flex;flex-direction:column;min-height:0;border-top:1px solid {t['regla']};padding-top:{6 if mini else 10}px}}
figure img{{flex:1;min-height:0;width:100%;object-fit:contain}}
figcaption{{font-size:{22 if mini else 17}px;display:flex;flex-direction:column;gap:2px;color:{t['mute']}}}
figcaption b{{color:{t['tinta']};font-size:{30 if mini else 24}px}}
</style></head><body class="{'mini' if mini else ''}"><div id="c">{texto}<div class="mapas">{cols}</div></div></body></html>"""
    pg.set_content(html)
    pg.wait_for_timeout(1200)
    return pg.locator("#c").screenshot()


def main():
    os.makedirs(MINIS, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        ctx = b.new_context(viewport={"width": 1600, "height": 1300}, device_scale_factor=2)
        pg = ctx.new_page()
        for tema in ("light", "dark"):
            imgs = [mapa(pg, n, tema) for n, *_ in ELECCIONES]
            t = TEMA[tema]
            if tema == "light":
                card = pg.context.new_page()
                Image.open(io.BytesIO(tarjeta(card, imgs, t, 1200, 630, False))).convert("RGB").resize((1200, 630), Image.LANCZOS) \
                    .save(os.path.join(HERE, "portada.png"), optimize=True)   # a todo color: con paleta los bordes se manchan; ~190 KB, X la toma (la de uninominal pesa 291 KB)
                card.close()
            card = pg.context.new_page()
            im = Image.open(io.BytesIO(tarjeta(card, imgs, t, 640, 550, True))).convert("RGB").resize((640, 550), Image.LANCZOS)
            card.close()
            im.save(os.path.join(MINIS, "capital__index" + ("_claro" if tema == "light" else "") + ".webp"), "WEBP", quality=78, method=6)
        b.close()
    print("portada.png y miniaturas capital__index{,_claro}.webp")


if __name__ == "__main__":
    main()
