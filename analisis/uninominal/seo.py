"""Cabecera para buscadores y redes de mapa_257.html (4-nov-2026). Idempotente.
    python analisis/uninominal/seo.py
Reemplaza <title> y la descripción y agrega canónica, Open Graph, tarjeta de X/Twitter y JSON-LD,
en la plantilla (para que mapa.py la conserve) y en el HTML ya generado (sin volver a correr Mosaic).
También agrega bajo el título el enlace al índice de atlas y el modo oscuro (tokens de sitio/estilo.css; respeta la
preferencia del sistema y la elección guardada en el índice, localStorage «tema»; el degradado del mapa va hacia el papel). Publicado en https://azha2005.github.io/257arg/uninominal/"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://azha2005.github.io/257arg/uninominal/"
IMG = URL + "portada.png"
TITULO = "Argentina con 257 distritos uninominales: mapa interactivo"
DESC = ("¿Y si cada diputado se eligiera en su distrito? Los 257 distritos uninominales de la Argentina, "
        "dibujados con el censo 2022, y quién los ganaría en 2023 y 2025.")   # < 160 caracteres, lo que muestra Google
OG_DESC = "Cada banca de Diputados, un distrito. Con los votos de 2025 y cada partido por separado, LLA gana 160 de 257 bancas con el 40,8 %."
ALT = ("Mapa de la Argentina dividida en 257 distritos y hemiciclo con los votos de diputados 2025: La Libertad Avanza 160 bancas, "
       "Fuerza Patria 83, Innovación Federal 7, Provincias Unidas 3, La Neuquinidad 2 y Por San Juan 2")
CLAVES = ("distritos uninominales, sistema uninominal, circunscripciones uninominales, reforma electoral, Cámara de Diputados, "
          "gerrymandering, redistritación, ley 22.847, censo 2022, elecciones 2025, elecciones 2023, Argentina, mapa electoral")
LD = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebPage", "@id": URL, "url": URL, "name": TITULO, "description": DESC, "inLanguage": "es-AR",
     "isPartOf": {"@type": "WebSite", "name": "Atlas electorales argentinos", "url": "https://azha2005.github.io/257arg/"},
     "primaryImageOfPage": IMG, "datePublished": "2026-11-04", "keywords": CLAVES,
     "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
         {"@type": "ListItem", "position": 1, "name": "Atlas electorales", "item": "https://azha2005.github.io/257arg/"},
         {"@type": "ListItem", "position": 2, "name": "257 distritos uninominales", "item": URL}]}},
    {"@type": "Map", "name": "Argentina con 257 distritos uninominales", "url": URL, "image": IMG, "inLanguage": "es-AR",
     "about": ["Sistema electoral uninominal", "Cámara de Diputados de la Nación Argentina", "Gerrymandering"],
     "spatialCoverage": {"@type": "Country", "name": "Argentina"},
     "isBasedOn": ["Censo Nacional 2022, radios censales (INDEC / CONICET)", "Escrutinio provisorio DINE 2023 y 2025",
                   "Mosaic (ReCom y recocido simulado)"],
     "sameAs": "https://github.com/azha2005/257arg/tree/master/analisis/uninominal", "license": "https://creativecommons.org/licenses/by/4.0/"}]}

HEAD = f"""<title>{TITULO}</title>
<meta name="description" content="{DESC}">
<meta name="keywords" content="{CLAVES}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{URL}">
<meta name="theme-color" content="#fcfcfa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141619" media="(prefers-color-scheme: dark)">
<script>try{{const t=localStorage.getItem("tema");if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<meta property="og:type" content="website">
<meta property="og:site_name" content="Atlas electorales argentinos">
<meta property="og:locale" content="es_AR">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="Argentina con 257 distritos uninominales">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:image" content="{IMG}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{ALT}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Argentina con 257 distritos uninominales">
<meta name="twitter:description" content="{OG_DESC}">
<meta name="twitter:image" content="{IMG}">
<meta name="twitter:image:alt" content="{ALT}">
<script type="application/ld+json">{json.dumps(LD, ensure_ascii=False)}</script>
<!--/seo-->"""

VOLVER = '<p class="volver"><a href="https://azha2005.github.io/257arg/">← Todos los atlas electorales</a></p>\n'
CSS_VOLVER = ".volver { margin: 0 0 var(--space-xs); font-size: var(--text-sm); }\n.volver a { color: var(--color-accent); font-weight: 600; text-decoration: none; }\n.volver a:hover { text-decoration: underline; }\n</style>"


# Modo oscuro (pedido del usuario, 4-nov-2026): mismos valores que el índice del sitio.
OSCURO = """  --color-paper: oklch(17% 0.004 250); --color-paper-2: oklch(21% 0.005 250); --color-paper-3: oklch(25% 0.006 250);
  --color-ink: oklch(95% 0 0); --color-ink-2: oklch(85% 0 0); --color-muted: oklch(72% 0 0);
  --color-rule: oklch(32% 0.006 250);
  --color-accent: oklch(74% 0.1 188); --color-accent-soft: oklch(32% 0.05 190); --color-accent-soft-ink: oklch(92% 0.04 190);
  --color-focus: oklch(74% 0.1 188); --color-tip-shadow: oklch(0% 0 0 / 0.5);
  --mix-base: 20,22,25;"""
CSS_TEMA = ("/* tema oscuro (4-nov-2026) */\n:root { --mix-base: 250,250,248; }\n"
            "@media (prefers-color-scheme: dark) {\n  :root:not([data-theme=\"light\"]) {\n  color-scheme: dark;\n" + OSCURO + "\n  }\n}\n"
            ":root[data-theme=\"dark\"] {\n  color-scheme: dark;\n" + OSCURO + "\n}\n"
            ".volver { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--space-xs); }\n"
            ".tema { min-height: var(--control-h); padding: var(--space-2xs) var(--space-sm); border: var(--rule-hair) solid var(--color-rule); "
            "border-radius: var(--radius-control); background: var(--color-paper-2); color: var(--color-ink); font-size: var(--text-sm); font-weight: 600; cursor: pointer; }\n"
            ".tema:hover { background: var(--color-paper-3); border-color: var(--color-muted); }\n\n/* base */")
BOTON = '<button type="button" class="tema" id="tema" aria-label="Cambiar entre modo claro y oscuro">Modo oscuro</button></p>'
JS_MIX = ('let MIXB=[250,250,248];function leerBase(){const v=css("--mix-base");if(v)MIXB=v.split(",").map(Number)}\n'
          '(function(){const b=$("tema"),r=document.documentElement,mq=matchMedia("(prefers-color-scheme: dark)");\n'
          ' const osc=()=>r.dataset.theme?r.dataset.theme==="dark":mq.matches,rot=()=>{b.textContent=osc()?"Modo claro":"Modo oscuro"};\n'
          ' const re=()=>{leerBase();rot();if(typeof draw==="function"&&DATA)draw()};\n'
          ' b.addEventListener("click",()=>{r.dataset.theme=osc()?"light":"dark";try{localStorage.setItem("tema",r.dataset.theme)}catch(e){}re()});\n'
          ' mq.addEventListener("change",()=>{if(!r.dataset.theme)re()});leerBase();rot()})();\n')



def tema(s):
    if "--mix-base" in s: return s
    for a, b in (("/* Hallmark · dropped the dark theme · the explorer it matches is printed on paper only */",
                  "/* Hallmark · dark theme added on request (4-nov-2026) · the tokens of the site index (sitio/estilo.css) */"),
                 ("\n/* base */", "\n" + CSS_TEMA),
                 ("← Todos los atlas electorales</a></p>", "← Todos los atlas electorales</a>" + BOTON),
                 ("w=[250,250,248];", "w=MIXB;")):
        assert s.count(a) == 1, a
        s = s.replace(a, b)
    a = "function ei(e){"
    assert s.count(a) == 1
    return s.replace(a, JS_MIX + a)


def aplicar(path):
    s = open(path, encoding="utf-8").read()
    if "<!--/seo-->" in s:
        s = re.sub(r"<title>.*?<!--/seo-->", lambda m: HEAD, s, count=1, flags=re.S)
    else:
        s, n = re.subn(r'<title>[^<]*</title>\n<meta name="description" content="[^"]*">', lambda m: HEAD, s, count=1)
        assert n == 1, path
    if 'class="volver"' not in s:
        assert s.count("<header>\n<h1>") == 1 and s.count("</style>") == 1, path
        s = s.replace("<header>\n<h1>", "<header>\n" + VOLVER + "<h1>").replace("</style>", CSS_VOLVER)
    s = tema(s)
    open(path, "w", encoding="utf-8").write(s)   # finales de línea de Windows, como los escribe mapa.py
    print("ok", os.path.basename(path))


for f in ("mapa_plantilla.html", "mapa_257.html"):
    aplicar(os.path.join(HERE, f))
