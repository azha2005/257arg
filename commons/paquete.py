"""Arma el paquete de subida a Commons de un atlas: SVG «solo mapa» y «con leyenda», PNG y wikitext, mas LEEME_SUBIDA.md.

    python commons/paquete.py 1930            # uno
    python commons/paquete.py 1930 1922       # varios
    python commons/paquete.py                 # todos los de config.py

Salida: commons/<año>/subir/ (archivos + <archivo>.txt con el wikitext) y commons/<año>/LEEME_SUBIDA.md.
Requisitos: haber corrido el build del atlas y render_transparentes.py (los PNG se copian de png_transparentes/<carpeta>/).
Reusa del paquete de 1928 (commons_1928/): inline_logo, to_hex, content_bbox, DejaVu para el texto a trazados.
"""
import io
import html as _html
import json
import os
import re
import shutil
import sys
import unicodedata
import urllib.parse
import urllib.request

from lxml import etree
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "commons_1928"))
import build_commons_svg as B1928   # funciones del paquete de 1928 (inline_logo, to_hex, content_bbox, Face...)
from config import ATLAS, GEOM, GEOM_SHORT, HOLD_TEXT

Q, NS, XL = B1928.Q, B1928.NS, B1928.XL
FLATTEN = open(os.path.join(HERE, "flatten.js"), encoding="utf8").read()
UA = {"User-Agent": "atlas-electoral-argentina/1.0 (%s)" % os.environ.get("ATLAS_CONTACT", "sin contacto; definir ATLAS_CONTACT")}
DATE = "2026-10-20"


def api(**k):
    k["format"] = "json"
    return json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(k), headers=UA), timeout=60))


def exist(titles):
    """titulos de Commons que existen (consulta en vivo, de a 40)"""
    out = set()
    for i in range(0, len(titles), 40):
        r = api(action="query", titles="|".join(titles[i:i + 40]), prop="info")
        for p in r["query"]["pages"].values():
            if "missing" not in p:
                out.add(p["title"])
    return out


def ascii_fold(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[\[\]{}|#<>:/%]", "", s).strip()


# ------------------------------------------------------------------ nombres de modo
def mode_names(ds):
    """modo -> (descripcion corta, nombre base del archivo)"""
    out = {}
    for m in ds["modes"]:
        lg = m.get("legend") or {}
        t = (lg.get("title") or "") if isinstance(lg, dict) else ""
        if m["id"] == "gan":
            out["gan"] = ("bloque ganador por departamento", "Resultados por departamento")
        elif "provincial" in t.lower() and t.lower().startswith("participaci"):
            out[m["id"]] = ("participación provincial (votos sobre electores registrados; sin cifras por departamento)", "Participacion por provincia")
        elif m["id"] == "par" or t.lower().startswith("participaci"):
            out[m["id"]] = ("participación (votantes sobre inscriptos) por departamento", "Participacion por departamento")
        else:
            lab = re.sub(r"^%\s*", "", t) or m.get("tile") or m["id"]
            out[m["id"]] = ("porcentaje de %s por departamento" % lab, "Voto a %s por departamento" % ascii_fold(lab))
    return out


# ------------------------------------------------------------------ 1) exportar
def export_flat(cfg, tmp, drop=None, prefix=""):
    url = "file:///" + os.path.join(ROOT, cfg["folder"], cfg["html"]).replace("\\", "/")
    ds = json.load(open(os.path.join(ROOT, cfg["folder"], cfg["dataset"]), encoding="utf8"))
    os.makedirs(tmp, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1920, "height": 1800}, device_scale_factor=1)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url); pg.wait_for_timeout(800)
        for m in pg.evaluate("DATA.modes.map(m=>m.id)"):
            pg.goto(url + "#m-" + m); pg.reload(); pg.wait_for_timeout(1200)
            assert pg.evaluate("(document.querySelector('#tiles .tile.on')||{dataset:{}}).dataset.mode") == m, m
            if drop:   # variante sin los emblemas dudosos: quedan las siglas
                pg.evaluate("codes => { for (const c of codes) if (DATA.candidates[c]) delete DATA.candidates[c].img; document.querySelector('#tiles .tile.on').dispatchEvent(new MouseEvent('click', {bubbles: true})); }", drop)
                pg.wait_for_timeout(600)
                pg.add_style_tag(content="html,body{background:transparent!important}")
                pg.locator("#atlas").first.screenshot(path=os.path.join(tmp, "png_%s%s.png" % (prefix, m)), omit_background=True)
            pg.evaluate("m => { window.MI = DATA.modes.findIndex(x => x.id === m); }", m)
            res = pg.evaluate(FLATTEN)
            open(os.path.join(tmp, "flat_%s%s.svg" % (prefix, m)), "w", encoding="utf8").write(res["xml"])
            json.dump(res["texts"], open(os.path.join(tmp, "textos_%s%s.json" % (prefix, m)), "w"))
        b.close()
    if errs:
        print("  errores de página:", errs)
    return ds


# ------------------------------------------------------------------ 2) variantes
def png_logo_fallback(svg_bytes, img):
    """logo SVG que no se puede inlinear (trae <style>): se rasteriza a PNG y se deja como <image> con data:image/png"""
    import base64
    import resvg_py
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg_bytes.decode("utf8"), width=360))
    img.set("href", "data:image/png;base64," + base64.b64encode(png).decode())
    return img


def build_variant(tmp, mode, variant, title, desc, name_out, fprefix=""):
    infos = json.load(open(os.path.join(tmp, "textos_%s%s.json" % (fprefix, mode))))
    root = etree.parse(os.path.join(tmp, "flat_%s%s.svg" % (fprefix, mode)), etree.XMLParser(remove_comments=True, huge_tree=True)).getroot()
    if variant == "mapa":
        for i in ("title", "yearbox", "pie", "legend"):
            for e in root.iter(Q("g"), Q("rect")):
                if e.get("id") == i:
                    e.getparent().remove(e); break
        for t in list(root.iter(Q("text"))):
            t.getparent().remove(t)
    else:
        for t in list(root.iter(Q("text"))):
            t.getparent().replace(t, B1928.text_to_path(t, infos[int(t.get("data-t"))]))
    n_png = 0
    for i, img in enumerate(list(root.iter(Q("image")))):
        try:
            new = B1928.inline_logo(img, i)
        except AssertionError:   # logo con <style>: se rasteriza
            import base64
            href = img.get("href") or img.get("{%s}href" % XL)
            raw = base64.b64decode(re.match(r"data:image/svg\+xml;base64,(.*)$", href, re.S).group(1))
            png_logo_fallback(raw, img); new = None
        if new is not None:
            img.getparent().replace(img, new)
    for img in root.iter(Q("image")):   # los PNG: href y xlink:href (visores viejos)
        h = img.get("href")
        if h and h.startswith("data:image/png"):
            img.set("{%s}href" % XL, h); n_png += 1
    for e in list(root.iter()):
        if not isinstance(e.tag, str):
            continue
        if e.get("data-title") and e.tag == Q("path"):
            ti = etree.Element(Q("title")); ti.text = e.get("data-title"); e.insert(0, ti)
        for a in ("fill", "stroke"):
            v = e.get(a)
            if v:
                h, al = B1928.to_hex(v); e.set(a, h)
                if al is not None:
                    k = a + "-opacity"; e.set(k, "%g" % (float(e.get(k, 1)) * al))
        for a in list(e.attrib):
            if a.startswith("data-"):
                del e.attrib[a]
        if e.tag == Q("path") and e.get("fill") == "none" and e.get("stroke") == "none":
            e.getparent().remove(e)
    for f in root.iter(Q("filter")):
        for ch in list(f):
            f.remove(ch)
        for tag, at in (("feGaussianBlur", {"in": "SourceAlpha", "stdDeviation": "1.6"}), ("feOffset", {"dx": "0", "dy": "1", "result": "b"})):
            etree.SubElement(f, Q(tag), at)
        ct = etree.SubElement(f, Q("feComponentTransfer")); etree.SubElement(ct, Q("feFuncA"), {"type": "linear", "slope": ".35"})
        mg = etree.SubElement(f, Q("feMerge")); etree.SubElement(mg, Q("feMergeNode")); etree.SubElement(mg, Q("feMergeNode"), {"in": "SourceGraphic"})
    xml = etree.tostring(root, encoding="unicode")
    refs = set(re.findall(r"url\(#([^)]+)\)", xml)) | set(re.findall(r'href="#([^"]+)"', xml))
    for e in root.iter():
        if isinstance(e.tag, str) and e.get("id") and e.get("id") not in refs:
            del e.attrib["id"]
    for e in list(root.findall(Q("title")) + root.findall(Q("desc"))):
        root.remove(e)
    ti = etree.Element(Q("title")); ti.text = title
    de = etree.Element(Q("desc")); de.text = desc
    root.insert(0, ti); root.insert(1, de)
    s = re.sub(r">\s+<", "><", etree.tostring(root, encoding="unicode"))
    if variant == "mapa":
        x, y, w, h = B1928.content_bbox(s)
        root.set("viewBox", "%d %d %d %d" % (x, y, w, h)); root.set("width", str(w)); root.set("height", str(h))
        s = re.sub(r">\s+<", "><", etree.tostring(root, encoding="unicode"))
    open(name_out, "w", encoding="utf8").write('<?xml version="1.0" encoding="UTF-8"?>\n' + s)


# ------------------------------------------------------------------ 3) wikitext
def wikitext(year, cfg, mode, kind, names, cats, logos_ok, logos_missing, files):
    omitted=set(cfg.get('logos_omitidos_siglas',[])) if kind in ('leyenda_s','png_s') else set()
    logos_ok=[x for x in logos_ok if x not in omitted]
    logos_missing=[x for x in logos_missing if x not in omitted]
    what, _ = names[mode]
    geom = GEOM_SHORT[cfg["geom"]]
    var = "solo varones; " if cfg["varones"] else ""
    ant = ("" if cfg["antartida"] else " No lleva recuadro de la Antártida: en %s no había sector antártico reclamado ni voto allí." % year)
    base_rec = [r for r in ("Tucumán", "Gran San Juan", "Gran Mendoza", "Resistencia + Corrientes capital", "Área Metropolitana de Buenos Aires") if r not in cfg.get("inset_omit", [])]
    rec = ", ".join(base_rec) + "%s y Capital Federal (%s)" % (", Antártida Argentina" if cfg["antartida"] else "",cfg.get('capital_division','por circunscripción'))
    sol = (" %s: %s." % cfg["solido"]) if cfg.get("solido") else ""
    es = ("Resultados por departamento de las %s del %s de Argentina (%s%s): %s. Los bloques siguen la tabla del artículo de la Wikipedia en español. "
          "Beige: resultados pendientes o sin desagregar; gris: territorios sin voto. La versión con leyenda lo aclara.%s Recuadros: %s.%s") % (
        cfg["tipo"], cfg["fecha"], var, geom, what, sol, rec, ant)
    MES = {"enero": "January", "febrero": "February", "marzo": "March", "abril": "April", "mayo": "May", "junio": "June", "julio": "July", "agosto": "August",
           "septiembre": "September", "octubre": "October", "noviembre": "November", "diciembre": "December"}
    TIPO = {"elecciones presidenciales": "presidential election", "elecciones legislativas (diputados nacionales)": "legislative election (national deputies)",
            "elecciones de convencionales constituyentes": "constituent convention election"}
    if cfg.get('fecha_en'):
        fecha_en=cfg['fecha_en']
    else:
        d_, _, m_, _, y_ = cfg["fecha"].split()
        fecha_en = "%s %s %s" % (d_, MES[m_], y_)
    if mode == "gan":
        what_en = "winning bloc by department"
    elif names[mode][1].startswith("Participacion"):
        what_en = "turnout (voters over registered)"
    else:
        what_en = "vote share of %s by department" % re.sub(r"^porcentaje de ", "", re.sub(r" por departamento$", "", what))
    en = "Results by department of the %s of Argentina on %s (%s%s): %s. Blocs follow the table of the Spanish Wikipedia article." % (
        TIPO[cfg["tipo"]], fecha_en, "men only; " if cfg["varones"] else "", cfg.get('geometry_en',"%s department boundaries" % cfg["geom"]), what_en)
    if cfg.get('description_es'): es += ' ' + cfg['description_es']
    if cfg.get('description_en'): en += ' ' + cfg['description_en']
    src = ["* Votos: " + v for v in cfg["votos"]]
    src.append("* Geometría: Rodríguez, Gonzalo Martín (2022). ''Base cartográfica de departamentos para los censos nacionales de la República Argentina desde 1869 a 2010'' "
               "(versión 2026 v2; contribuidor: Pablo Ernesto De Grande). CONICET. Dataset, [http://hdl.handle.net/11336/149867 hdl:11336/149867] "
               "([https://datosdeinvestigacion.conicet.gov.ar/handle/11336/149867 Datos de Investigación CONICET]), licencia CC BY 2.5 Argentina. %s; se les unieron, simplificaron y recortaron los polígonos." % GEOM[cfg["geom"]])
    src.append("* Bloques y resultado nacional: [[:es:%s]]." % cfg["article"] + (" Antártida: Natural Earth 1:50m (dominio público)." if cfg["antartida"] else ""))
    if kind != "mapa" and (logos_ok or logos_missing):
        src.append("* Emblemas (licencia libre en Commons): " + ", ".join("[[:File:%s|]]" % n for n in logos_ok) + "." + (
            " Sin página en Commons con ese nombre: " + ", ".join(logos_missing) + "." if logos_missing else ""))
        for attr in cfg.get('logos_atribucion',[]):
            if attr['title'] in logos_ok:
                author=_html.unescape(re.sub(r'<[^>]+>','',attr['author'])).replace('|','&#124;')
                src.append('* Atribución del emblema [[:File:%s|%s]]: %s; licencia %s.' % (attr['title'],attr['title'],author,attr['license']))
    if kind in ("leyenda", "png") and cfg.get("logos_sin_licencia"):
        src.append("* Emblemas sin licencia libre verificada, usados solo para identificar a cada partido en la leyenda: " + "; ".join(cfg["logos_sin_licencia"]) + ".")
    src.append("* Elaborado con código propio y asistido por herramientas de IA; los mapas no son imágenes generadas por IA.")
    if kind == "mapa":
        src.append("* Cada departamento lleva un elemento <title> con su nombre y resultado; el archivo no contiene texto ni leyenda (como el mapa por departamento de 2019).")
    others = "\n".join("[[:File:%s|]]" % f for k, f in files[mode].items() if k != kind)
    license_name=cfg.get('map_license','cc-by-4.0') if kind in ('leyenda','png') else 'cc-by-4.0'
    return ("=={{int:filedesc}}==\n{{Information\n|description={{es|1=%s}}\n{{en|1=%s}}\n|date=%s\n|source={{own}}<br/>\n%s\n"
            "|author=[[User:ItsAHardLife|ItsAHardLife]]\n|permission=\n|other versions=%s\n}}\n\n=={{int:license-header}}==\n{{self|%s}}\n"
            "{{Cc-by-2.5-ar}} <!-- base cartográfica de Rodríguez (CONICET), ver |source= -->\n\n%s\n") % (
        es, en, DATE, "\n".join(src), others, license_name, "\n".join("[[Category:%s]]" % c for c in cats + (["SVG maps of Argentina"] if not kind.startswith("png") else [])))


# ------------------------------------------------------------------ 4) LEEME por carpeta
def leeme(year, cfg, names, files, cats_missing, logos_missing, hold_all, hold_logos):
    base = "Elecciones…"
    rows = []
    for m, f in files.items():
        for k, label in (("mapa", "solo mapa"), ("leyenda", "con leyenda"), ("png", "png"), ("leyenda_s", "con leyenda y siglas (sin emblemas dudosos)"), ("png_s", "png con siglas (sin emblemas dudosos)")):
            if k not in f:
                continue
            hold = hold_all or (hold_logos and k not in ("mapa", "leyenda_s", "png_s"))
            rows.append("| %s | %s | %s |" % (names[m][1], label, "**NO subir todavía**" if hold else "Para subir"))
    est = "\n".join(rows)
    holds = []
    for h in cfg["hold"]:
        holds.append("- **Todo el atlas en espera:** " + HOLD_TEXT[h])
    for h in cfg["hold_logos"]:
        holds.append("- **Versiones con logos en espera («con leyenda» y PNG):** " + HOLD_TEXT.get(h,h))
    if cfg.get("logos_sin_licencia"):
        holds.append("- **Riesgo asumido por el usuario (15-oct-2026):** las versiones «con leyenda» y PNG llevan un emblema sin licencia libre verificada (" + "; ".join(cfg["logos_sin_licencia"]) + "). El wikitext lo declara. Commons puede borrar esos archivos por derechos de autor; los «solo mapa» no llevan logos y no corren ese riesgo.")
    av = "\n".join("- " + a for a in cfg["avisos"])
    prio = "**Prioridad:** subir primero `gan` «solo mapa» y comprobar la miniatura; después el resto de los modos. " if not hold_all else "**No subir nada hasta resolver lo de arriba.** "
    logo_license_note=(' Las versiones con logos ShareAlike llevan `{{self|cc-by-sa-4.0}}`; las variantes que omiten esos emblemas conservan CC BY 4.0.' if cfg.get('map_license')=='cc-by-sa-4.0' else '')
    return f"""# Paquete {year} para Commons — {cfg['article']}

Estado al {DATE}. Todo **sin subir**. Instrucciones del procedimiento: [`../INSTRUCCIONES_GENERICAS.md`](../INSTRUCCIONES_GENERICAS.md). Usuario de Commons: `ItsAHardLife`.

## Qué hay en `subir/`
Por cada modo del atlas, tres versiones (cada archivo con su wikitext `<archivo>.txt`): `(solo mapa).svg` (sin texto ni leyenda, como el mapa por departamento de 2019 de es.wikipedia; cada unidad con `<title>`), `(con leyenda).svg` (el cartel completo, texto a trazados) y `.png` (el cartel del atlas, transparente).

{prio}

| Modo | Versión | Estado |
|---|---|---|
{est}

## Antes de subir
{chr(10).join(holds) if holds else '- Sin impedimentos conocidos más allá de los avisos de abajo.'}

## Avisos de este atlas
{av}

## Fuentes y licencia
- **Votos:** {' '.join(cfg['votos'])}
- **Geometría:** {GEOM[cfg['geom']]}. Rodríguez, G. M. (2022), CONICET, hdl:11336/149867, **CC BY 2.5 Argentina**. Los mapas sin emblemas llevan `{{{{self|cc-by-4.0}}}}` + `{{{{Cc-by-2.5-ar}}}}`.{logo_license_note} Ver las instrucciones genéricas.
- **Logos** (solo «con leyenda» y PNG): {', '.join(cfg['logos']) or 'ninguno'}.{(' Sin página en Commons con ese nombre (se dejaron sin enlace): ' + ', '.join(logos_missing) + '.') if logos_missing else ''} El detalle de cada licencia está en `logos_wikipedia/LICENCIAS.md`.
- **Fecha de la elección:** {cfg['fecha']}{' (cotejada con el artículo)' if cfg.get('fecha_verificada') else ' (confirmar con el artículo)'}.
{('- **Categorías de Commons que no existen y se omitieron:** ' + ', '.join(cats_missing) + '.') if cats_missing else ''}

## Discusión del artículo
Texto sugerido para la página de discusión de «{cfg['article']}» en es.wikipedia (editarlo a gusto, y avisar al autor del mapa vigente):
```
== Propuesta: mapa de resultados por departamento ==
Hola. Subí a Commons mapas de esta elección por departamento ({GEOM_SHORT[cfg['geom']]}): [[:commons:File:{files['gan']['mapa'] if 'gan' in files else list(list(files.values())[0].values())[0]}|ganador por departamento]]{', más las versiones con el voto de cada bloque y la participación' if len(files) > 1 else ''}.

Las cifras salen de las fuentes citadas en la descripción de cada archivo y los bloques siguen la tabla de este artículo. La geometría es la base cartográfica de Rodríguez (CONICET, CC BY 2.5 AR).

Propongo sumarlo en la sección de resultados, sin reemplazar los mapas que ya están. ¿Les parece bien? ~~~~
```
"""


# ------------------------------------------------------------------ principal
def run(year, solo_textos=False):
    cfg = ATLAS[year]
    out = os.path.join(HERE, year)
    tmp = os.path.join(out, "_tmp")
    sub = os.path.join(out, "subir")
    if solo_textos:   # solo reescribe wikitext y LEEME con los archivos ya generados
        ds = json.load(open(os.path.join(ROOT, cfg["folder"], cfg["dataset"]), encoding="utf8"))
    else:
        shutil.rmtree(sub, ignore_errors=True); os.makedirs(sub)
        print("== %s: exportando…" % year, flush=True)
        ds = export_flat(cfg, tmp)
    names = mode_names(ds)
    base = cfg.get("filename_prefix", cfg["article"]) + " - "
    files = {m: {"mapa": base + n[1] + " (solo mapa).svg", "leyenda": base + n[1] + " (con leyenda).svg", "png": base + n[1] + ".png"} for m, n in names.items()}
    if cfg.get("sin_logo"):   # variantes sin los emblemas dudosos (siglas en su lugar)
        for m, n in names.items():
            files[m]["leyenda_s"] = base + n[1] + " (con leyenda y siglas).svg"
            files[m]["png_s"] = base + n[1] + " (siglas).png"
    # categorias y logos que existen en Commons
    calendar_year = cfg.get('year', year)
    cand = ["%s elections in Argentina" % calendar_year, "%s Argentine general election" % calendar_year, "%s Argentine legislative election" % calendar_year,
            "%s Argentine presidential election" % calendar_year, "%s election maps" % calendar_year, "Maps of Argentina by department"] + cfg["cats_extra"]
    ex = exist(["Category:" + c for c in cand] + ["File:" + l for l in cfg["logos"]])
    cats = [c for c in cand if "Category:" + c in ex]
    cats_missing = [c for c in cand if "Category:" + c not in ex and not c.startswith(year + " Argentine")]
    logos_ok = [l for l in cfg["logos"] if "File:" + l in ex]
    logos_missing = [l for l in cfg["logos"] if "File:" + l not in ex]
    if cfg.get("sin_logo") and not solo_textos:
        print("   exportando variante sin emblemas dudosos…", flush=True)
        export_flat(cfg, tmp, drop=cfg["sin_logo"], prefix="s_")
    title_es = ds.get("title", cfg["article"])
    for m in names:
        what = names[m][0]
        t = "%s: %s" % (cfg["article"], what)
        d = "Mapa por departamento de las %s de Argentina del %s. Fuentes y licencias: ver la página del archivo en Commons." % (cfg["tipo"], cfg["fecha"])
        for variant, key in (("mapa", "mapa"), ("leyenda", "leyenda")):
            fn = os.path.join(sub, files[m][key])
            if not solo_textos:
                build_variant(tmp, m, variant, t, d, fn)
                print("   %s %s %.1f MB" % (m, variant, os.path.getsize(fn) / 1e6), flush=True)
            open(fn + ".txt", "w", encoding="utf8").write(wikitext(year, cfg, m, key, names, cats, logos_ok, logos_missing, files))
        src = os.path.join(ROOT, "png_transparentes", cfg["folder"], "%s_%s.png" % (os.path.splitext(cfg["html"])[0], m))
        if not solo_textos:
            shutil.copy(src, os.path.join(sub, files[m]["png"]))
        open(os.path.join(sub, files[m]["png"]) + ".txt", "w", encoding="utf8").write(wikitext(year, cfg, m, "png", names, cats, logos_ok, logos_missing, files))
        if cfg.get("sin_logo"):
            if not solo_textos:
                build_variant(tmp, m, "leyenda", t, d, os.path.join(sub, files[m]["leyenda_s"]), fprefix="s_")
                shutil.copy(os.path.join(tmp, "png_s_%s.png" % m), os.path.join(sub, files[m]["png_s"]))
            for k in ("leyenda_s", "png_s"):
                open(os.path.join(sub, files[m][k]) + ".txt", "w", encoding="utf8").write(wikitext(year, cfg, m, k, names, cats, logos_ok, logos_missing, files))
    shutil.rmtree(tmp, ignore_errors=True)
    hold_all = bool(cfg["hold"]); hold_logos = bool(cfg["hold_logos"])
    open(os.path.join(out, "LEEME_SUBIDA.md"), "w", encoding="utf8").write(leeme(year, cfg, names, files, cats_missing, logos_missing, hold_all, hold_logos))
    print("   categorías:", cats, "| sin categoría:", cats_missing, "| logos sin página:", logos_missing, flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for y in (args or list(ATLAS)):
        run(y, solo_textos="--textos" in sys.argv)
