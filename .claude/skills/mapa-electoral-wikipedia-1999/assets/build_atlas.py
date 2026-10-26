#!/usr/bin/env python3
"""Genera un atlas electoral HTML autonomo en el estilo del mapa de Wikipedia
"Elecciones presidenciales de Argentina de 1999" a partir de un dataset.json.

    python3 build_atlas.py --dataset dataset.json --out atlas.html [--start-mode ID]

Entradas que vive junto a este script (carpeta assets/ del skill):
  base_1999_departamentos.svg  geometria de departamentos (mapa de Wikipedia, 1999)
  territories.json             indice de las 538 unidades (provincia, nombre, tipo) y id de trazo -> indice
  geom_rows.json               caja de cada trazo (para clasificar insets)
  frontiers.png                fronteras / rios limitrofes / nombres de paises (arte fijo de 1999.png)
  template.html                maqueta y JS (todo el comportamiento depende del dataset)

El formato del dataset esta en references/dataset-schema.md.
"""
import argparse, base64, json, math, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SVGNS = "http://www.w3.org/2000/svg"
INK = "http://www.inkscape.org/namespaces/inkscape"

# --- calibracion del mapa principal respecto de 1999.png (px del poster 1920x1649)
MAIN = dict(s=0.5425, tx=544.2, ty=228.1)

PROV_BORDER_IDS = {
    "path4403": "Capital Federal", "path5065": "Formosa", "path4988": "Chaco",
    "path4769": "Jujuy", "path4610": "Salta", "path3380": "Tucumán",
    "path4142": "Santiago del Estero", "path4340": "Catamarca", "path3685": "La Rioja",
    "path3899": "Misiones", "path50": "Corrientes", "path4620": "Entre Ríos",
    "path4402": "Santa Fe", "path4137": "Córdoba", "path3869": "San Luis",
    "path3744": "Mendoza", "path3598": "Buenos Aires", "path947": "La Pampa",
    "path4251": "Río Negro", "path3708": "Neuquén", "path3952": "Santa Cruz",
    "path2423": "Chubut", "path2874": "San Juan",
}


def load_base():
    b = open(os.path.join(HERE, "base_1999_departamentos.svg"), "rb").read()
    s = b.decode("utf-8", errors="replace")   # el original trae bytes que no son UTF-8 validos (solo en etiquetas)
    s = re.sub(r"<\?xml[^>]*\?>", "", s, count=1)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    return ET.fromstring(s)


def tag(el):
    return el.tag.replace("{%s}" % SVGNS, "") if isinstance(el.tag, str) else ""


def parse_scale(tr):
    """escala lineal acumulada de un atributo transform"""
    if not tr:
        return 1.0
    k = 1.0
    for name, args in re.findall(r"(\w+)\(([^)]*)\)", tr):
        v = [float(x) for x in re.split(r"[ ,]+", args.strip()) if x]
        if name == "matrix":
            k *= math.sqrt(abs(v[0] * v[3] - v[1] * v[2]))
        elif name == "scale":
            k *= math.sqrt(abs(v[0] * (v[1] if len(v) > 1 else v[0])))
    return k


def fmt(x):
    return ("%.4f" % x).rstrip("0").rstrip(".")


def build_map():
    T = json.load(open(os.path.join(HERE, "territories.json"), encoding="utf8"))
    idm = T["IDMAP"]
    ROWS = json.load(open(os.path.join(HERE, "geom_rows.json"), encoding="utf8"))
    geom = {r[1]: dict(tag=r[0], label=r[2], prov=r[3], gl=r[4], bb=r[5]) for r in ROWS}
    pb_d, tdf_paths, counts = {}, [], {}

    def classify(pid):
        g = geom.get(pid, {})
        if pid in idm:
            f = idm[pid]
            bb = g.get("bb", [0, 0, 0, 0])
            if f["label"] == "Recuadro" or g.get("gl") == "Recuadro" or pid in ("SF", "SF2"):
                return "rcc" if f["prov"] == "Capital Federal" else "rcb"
            if pid == "path2418":
                return "ant"
            if f["prov"] == "Capital Federal" and bb[1] < 1000:
                return "dc"   # CABA del mapa principal (28 circunscripciones), para su propio inset
            return "d"
        if pid in PROV_BORDER_IDS:
            return "pb"
        if pid == "path3665":
            return "out"
        if pid == "path6122":
            return "out2"
        if pid == "path2146":
            return "cabab"
        if pid in ("path24289", "path5230"):
            return "antf"
        gl = g.get("gl", "")
        if gl == "Antartida Argentina":
            return "ant"
        if gl.startswith("Islas Georgias"):
            return "antg"
        if pid == "path6122-7" or gl.startswith("Islas Malvinas"):
            return "mal"
        return None

    def emit(el, k_parent, out):
        t = tag(el)
        if t == "g":
            if el.get("{%s}label" % INK) == "Recuadro AMBA":
                # solo se conserva el contorno de CABA (un unico poligono, como en 1999)
                for c in el:
                    if c.get("id") == "path2146":
                        tr = el.get("transform")
                        buf = []
                        emit(c, k_parent * parse_scale(tr), buf)
                        out.append("<g%s>" % (' transform="%s"' % tr if tr else ""))
                        out.extend(buf)
                        out.append("</g>")
                return
            tr = el.get("transform")
            k = k_parent * parse_scale(tr)
            buf = []
            for c in el:
                emit(c, k, buf)
            if not buf:
                return
            out.append("<g%s>" % (' transform="%s"' % tr if tr else ""))
            out.extend(buf)
            out.append("</g>")
        elif t == "path":
            pid = el.get("id") or ""
            cls = classify(pid)
            if cls is None:
                return
            d = el.get("d")
            tr = el.get("transform")
            k = k_parent * parse_scale(tr)
            attrs = ['id="%s"' % pid, 'class="%s"' % cls]
            if tr:
                attrs.append('transform="%s"' % tr)
            style = el.get("style") or ""
            m = re.search(r"fill-rule:(\w+)", style)
            if m and m.group(1) == "evenodd":
                attrs.append('fill-rule="evenodd"')
            if abs(k - 1) > 1e-6:
                attrs.append('style="--k:%s"' % fmt(k))   # escala acumulada: el CSS la usa para el ancho de linea
            if pid in idm:
                attrs.append('data-i="%d"' % idm[pid]["f"])
            if cls == "pb":
                attrs.append('data-prov="%s"' % PROV_BORDER_IDS[pid])
                pb_d[PROV_BORDER_IDS[pid]] = (d, tr, k)
            counts[cls] = counts.get(cls, 0) + 1
            if cls == "d" and idm[pid]["prov"] == "Tierra del Fuego":
                tdf_paths.append((d, tr, k))
            out.append("<path %s d=\"%s\"/>" % (" ".join(attrs), d))

    root = load_base()
    body = []
    for c in root:
        if tag(c) in ("g", "path"):
            emit(c, 1.0, body)
    pv = ['<g transform="translate(51.500304,-5.3258707)">']
    for prov, (d, tr, k) in pb_d.items():
        pv.append('<path class="pf" data-prov="%s" d="%s"%s/>' % (prov, d, ' transform="%s"' % tr if tr else ""))
    for d, tr, k in tdf_paths:
        pv.append('<path class="pf" data-prov="Tierra del Fuego" d="%s"%s/>' % (d, ' transform="%s"' % tr if tr else ""))
    pv.append("</g>")
    print("clases:", counts, file=sys.stderr)
    return "".join(body), "".join(pv), T["units"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start-mode", default=None, help="id del modo inicial (por defecto el primero)")
    a = ap.parse_args()

    ds = json.load(open(a.dataset, encoding="utf8"))
    map_svg, pv_svg, units = build_map()
    n = len(units)
    for m in ds["modes"]:
        if len(m["units"]) != n:
            sys.exit("modo %r: units tiene %d entradas, se esperaban %d (una por territorio de territories.json)" % (m["id"], len(m["units"]), n))
    ds["territories"] = [dict(n=u["name"], p=u["prov"], k=u["kind"]) for u in units]
    start = a.start_mode or ds["modes"][0]["id"]
    if start not in [m["id"] for m in ds["modes"]]:
        sys.exit("start-mode %r no existe" % start)

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf8").read()
    fr = base64.b64encode(open(os.path.join(HERE, "frontiers.png"), "rb").read()).decode()
    html = (tpl.replace("{{FRONTIERS}}", "data:image/png;base64," + fr)
               .replace("{{MAP}}", map_svg).replace("{{PV}}", pv_svg)
               .replace("{{DATA}}", json.dumps(ds, ensure_ascii=False, separators=(",", ":")))
               .replace("{{MODE}}", start)
               .replace("{{MAIN_S}}", fmt(MAIN["s"])).replace("{{MAIN_TX}}", fmt(MAIN["tx"]))
               .replace("{{MAIN_TY}}", fmt(MAIN["ty"])))
    with open(a.out, "w", encoding="utf8", newline="\n") as f:
        f.write(html)
    print("escrito", a.out, round(len(html) / 1e6, 2), "MB", file=sys.stderr)


if __name__ == "__main__":
    main()
