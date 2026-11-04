"""Baja el wikitext de los artículos «Elecciones provinciales de <provincia> de <año>» de es.wikipedia (28-oct-2026),
para el prior de las fuerzas provinciales del componedor de la Cámara (proyeccion/congreso.py).
    python herramientas/bajar_gobernadores_wiki.py 2019 2021 2023 2025
Salida: datos/gobernadores_wiki/<provincia>_<año>.txt (si existe el artículo)."""
import os, sys, time, json, urllib.request, urllib.parse
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "datos", "gobernadores_wiki")
PROV = ["Catamarca", "Córdoba", "Corrientes", "Chaco", "Chubut", "Entre Ríos", "Formosa", "Jujuy", "La Pampa",
        "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz",
        "Santa Fe", "Santiago del Estero", "Tucumán", "Tierra del Fuego"]
UA = {"User-Agent": "dataelecc-atlas/1.0 (bttfjc@gmail.com)"}


def wikitext(title):
    q = urllib.parse.urlencode(dict(action="parse", page=title, prop="wikitext", format="json", redirects=1))
    for k in range(5):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request("https://es.wikipedia.org/w/api.php?" + q, headers=UA), timeout=30))
            return r.get("parse", {}).get("wikitext", {}).get("*")
        except Exception:
            time.sleep(3 * (k + 1))
    return None


def buscar(p, y):
    """Título real del artículo cuando no es «Elecciones provinciales de <p> de <y>» (p. ej. «del Neuquén»)."""
    q = urllib.parse.urlencode(dict(action="query", list="search", srsearch='intitle:elecciones intitle:%s "%s"' % (y, p),
                                    srlimit=10, format="json"))
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request("https://es.wikipedia.org/w/api.php?" + q, headers=UA), timeout=30))
    except Exception:
        return None
    for h in r.get("query", {}).get("search", []):
        t = h["title"]
        if y in t and p.split()[-1] in t and "provincial" in t.lower() and "legislativ" not in t.lower():
            return t
    return None


os.makedirs(OUT, exist_ok=True)
for y in sys.argv[1:]:
    for p in PROV:
        f = os.path.join(OUT, "%s_%s.txt" % (p.replace(" ", "_"), y))
        if os.path.exists(f):
            continue
        t = None
        for title in ("Elecciones provinciales de %s de %s" % (p, y), "Elecciones provinciales de la Provincia de %s de %s" % (p, y)):
            t = wikitext(title)
            if t:
                break
        if not t:
            title = buscar(p, y)
            t = wikitext(title) if title else None
        print(y, p, "ok" if t else "-", flush=True)
        if t:
            open(f, "w", encoding="utf-8").write(t)
        time.sleep(0.5)
