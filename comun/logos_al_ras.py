"""Logos de la leyenda al ras de la barra (pedido del usuario, 2-nov-2026).

Regla general: el logo arranca en el borde izquierdo de la barra (x 93), ocupa todo su alto y no deja margen;
como los bloques de los mapas presidenciales de la Wikipedia. No es para todos: donde queda peor, el logo lleva
`ras: false` en `logos_ras_excepciones.json` y se dibuja como antes.

    python comun/logos_al_ras.py <atlas.html> [...]       # aplica al HTML ya construido (idempotente)
    python comun/logos_al_ras.py --todos                  # todos los atlas de mapas/

Hace dos cosas:
1. Recorta el margen transparente de cada logo (los SVG se pasan a PNG con resvg) y recalcula `ar`,
   para que el contenido toque el borde de la barra.
2. Cambia el dibujo de la leyenda de las tres familias de código (plantilla, comun/leyenda_clara.js y la serie AMBA
   por radio) por `RAS()`, que dibuja al ras; con `C.ras===false` queda el dibujo anterior.
"""
import base64, fnmatch, glob, io, json, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXC = os.path.join(ROOT, "comun", "logos_ras_excepciones.json")
MARCA = "/*logos-al-ras*/"

# Dibuja el logo al ras; si es más ancho que mx, se achica (único caso en que queda margen arriba y abajo).
RAS_JS = MARCA + ('function RAS(C,g,y,h,mx,ex){const ar=C.ar||1,iw=Math.min(h*ar,mx),ih=iw/ar,'
                  'cv=el("svg",{x:93,y,width:iw,height:h,overflow:"hidden"},g);'
                  'el("image",Object.assign({href:C.img,x:0,y:(h-ih)/2,width:iw,height:ih,preserveAspectRatio:"xMinYMid meet"},ex||{}),cv);return iw;}\n')


def excepciones():
    try: return json.load(open(EXC, encoding="utf8"))
    except FileNotFoundError: return []


def es_excepcion(rel, code, c, exc):
    for e in exc:
        if not fnmatch.fnmatch(rel, e.get("archivo", "*")): continue
        if e.get("codigo") and e["codigo"] != code: continue
        if e.get("nombre") and e["nombre"].lower() not in (c.get("n") or "").lower(): continue
        return True
    return False


def recortar(uri):
    head, b64 = uri.split(",", 1)
    raw = base64.b64decode(b64)
    if "svg" in head:
        import resvg_py
        raw = bytes(resvg_py.svg_to_bytes(svg_string=raw.decode("utf8"), height=300))
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    bb = im.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()
    if bb and bb != (0, 0, im.width, im.height): im = im.crop(bb)
    elif "svg" not in head: return uri, im.width / im.height       # ya recortado: no se vuelve a codificar
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.width / im.height


def candidatos(cands, rel="", exc=None):
    """Recorta los logos de un diccionario de candidaturas (lo pueden llamar los constructores)."""
    exc = excepciones() if exc is None else exc
    for code, c in cands.items():
        if not isinstance(c, dict) or not c.get("img") or c.get("minor"): continue
        if es_excepcion(rel, code, c, exc):
            c["ras"] = False; continue
        c.pop("ras", None)
        c["img"], c["ar"] = recortar(c["img"])
    return cands


# --------------------------------------------------------------------- JS de cada familia
T_RE = re.compile(r'if\(C\.img\)\{(const ih=h\*\(C\.bl\|\|1\.2\),iw=ih\*\(C\.ar\|\|1\),cv=el\("svg",\{x:93,y,width:(?:C\.logoWidth\|\|)?110,)')
T_NEW = r'if(C.img&&C.ras!==false)RAS(C,g,y,h,116);else if(C.img){\1'

L_OLD = '  if(C.img&&C.blk){   // bloque de un mapa presidencial de la Wikipedia, alineado a la izquierda'
L_NEW = ('  let lw=92*s;\n'
         '  if(C.img&&C.ras!==false){   // regla general: al ras y al alto de la barra (logos_al_ras.py)\n'
         '    const md=C.blk?null:logoMode(C.n),filt=md?"lg_"+md:null;\n'
         '    if(filt&&!document.getElementById(filt)){const f=el("filter",{id:filt,"color-interpolation-filters":"sRGB"},g.ownerSVGElement||g);\n'
         '      el("feColorMatrix",{type:"matrix",values:md==="blanco"?"0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1 0"\n'
         '        :"0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 -0.32 -1.07 -0.11 1.5 0"},f);}\n'
         '    lw=RAS(C,g,y,h,120*s,filt?{filter:`url(#${filt})`}:null);\n'
         '  }else if(C.img&&C.blk){   // bloque de un mapa presidencial de la Wikipedia, alineado a la izquierda')
L_AV_OLD = 'const av=424-(97+92*s)-4,fn=s===1?14.5:Math.min(14.5*s,Math.max(14.5,av/(C.n.length*0.52))),sq=s===1?C.n.length>29:C.n.length*fn*0.52>av;'
L_AV_NEW = 'const av=424-(93+Math.max(lw,92*s))-8,fn=s===1?14.5:Math.min(14.5*s,Math.max(14.5,av/(C.n.length*0.52))),sq=s===1?C.n.length>29||C.n.length*fn*0.52>av:C.n.length*fn*0.52>av;'

L_TL_OLD = '...(sq?{textLength:s===1?232:av,'
L_TL_NEW = '...(sq?{textLength:s===1?Math.min(232,av):av,'

S_RE = re.compile(r'if\(C\.img&&C\.blk\)\{const ar=C\.ar\|\|1,bh=h\*1\.05,')
S_NEW = 'let _lw=0;if(C.img&&C.ras!==false)_lw=RAS(C,g,y,h,140);else if(C.img&&C.blk){const ar=C.ar||1,bh=h*1.05,'
# El nombre (alineado a la derecha en x 424) se comprime al ancho que deja el logo.
S_NL_OLD = 'const nlim=C.img&&C.blk?'
S_NL_NEW = 'const nlim=_lw?Math.min(215,424-93-_lw-10):C.img&&C.blk?'


def parchar_js(s):
    """Devuelve (texto, familias parchadas). No hace nada si ya está parchado."""
    if MARCA in s: return s, ["ya"]
    fam = []
    s, n = T_RE.subn(T_NEW, s)
    if n: fam.append("plantilla×%d" % n)
    if L_OLD in s:
        s = s.replace(L_OLD, L_NEW)
        assert L_AV_OLD in s, "leyenda_clara cambió"
        s = s.replace(L_AV_OLD, L_AV_NEW)
        assert L_TL_OLD in s, "leyenda_clara cambió (textLength)"
        s = s.replace(L_TL_OLD, L_TL_NEW); fam.append("leyenda_clara")
    s, n = S_RE.subn(S_NEW, s)
    if n:
        assert s.count(S_NL_OLD) == n, "serie cambió (nlim)"
        s = s.replace(S_NL_OLD, S_NL_NEW); fam.append("serie×%d" % n)
    if not fam: return s, []
    # En el mismo ámbito que el código que dibuja la leyenda (necesita el()); leyenda_clara define LEGEND_ROW.
    for ancla in ("function LEGEND_ROW(", "function drawLegend("):
        if ancla in s:
            i = s.index(ancla); break
    else:
        raise ValueError("sin función de leyenda")
    return s[:i] + RAS_JS + s[i:], fam


def aplicar(path, exc=None):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    s = open(path, encoding="utf8").read()
    i = s.index("const DATA"); j = s.index("=", i) + 1
    if s[j:j + 1] == "{":
        data, end = json.JSONDecoder().raw_decode(s[j:])
        candidatos(data.get("candidates", {}), rel, exc)
        s = s[:j] + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + s[j + end:]
    else:
        # Escenarios 2003: DATA se arma en el navegador; los logos están en ATLAS_INPUT.logos ({código: uri}).
        k = s.index("ATLAS_INPUT="); j = s.index("{", k)
        data, end = json.JSONDecoder().raw_decode(s[j:])
        cands = {c: {"img": u, "n": c} for c, u in data.get("logos", {}).items()}
        candidatos(cands, rel, exc)
        data["logos"] = {c: v["img"] for c, v in cands.items()}
        data["logo_ar"] = {c: v["ar"] for c, v in cands.items() if "ar" in v}
        data["logo_ras"] = {c: False for c, v in cands.items() if v.get("ras") is False}
        s = s[:j] + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + s[j + end:]
        old = "C[k].img=img;"
        if old in s and "logo_ar" not in s[s.index(old) - 5:s.index(old) + 120]:
            s = s.replace(old, old + "if(ATLAS_INPUT.logo_ar&&ATLAS_INPUT.logo_ar[k])C[k].ar=ATLAS_INPUT.logo_ar[k];"
                                     "if(ATLAS_INPUT.logo_ras&&ATLAS_INPUT.logo_ras[k]===false)C[k].ras=false;", 1)
    s, fam = parchar_js(s)
    tmp = path + ".tmp"
    open(tmp, "w", encoding="utf8").write(s); os.replace(tmp, path)
    return fam


def todos():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "mapas", "*", "*.html"))):
        n = os.path.basename(f)
        if n in ("wiki.html", "INDICE.html", "index.html") or "hemiciclo" in n or "2007circuitos" in f: continue
        out.append(f)
    return out


if __name__ == "__main__":
    files = todos() if sys.argv[1:] == ["--todos"] else sys.argv[1:]
    exc = excepciones()
    for f in files:
        try: fam = aplicar(f, exc)
        except ValueError: fam = ["sin DATA"]
        print(os.path.relpath(f, ROOT), ", ".join(fam) or "SIN FAMILIA CONOCIDA")
