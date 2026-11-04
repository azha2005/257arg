"""Atlas de las elecciones legislativas bonaerenses del 7-sep-2025 por circuito electoral (estilo Wikipedia 1999).
  python mapas/mapaPBA2025sep/build_circuitos.py amba  -> atlas_amba2025sep.html  (40 partidos; niveles Partido / Circuito)
  python mapas/mapaPBA2025sep/build_circuitos.py pba   -> atlas_pba2025sep.html   (135 partidos; niveles Sección / Partido / Circuito)
Antes: preparar.py (mesas). Reutiliza el constructor del atlas AMBA 2025 por circuito (../mapaAMBA2025/build_amba2025.py = cabeza +
mid_amba.py + tail_amba.py) con reemplazos: cada texto reemplazado tiene que aparecer una sola vez; si falla, cambió el original.
Votos: base por mesa del provisorio (graficarpba), senadores y diputados provinciales como un solo cargo legislativo (cada mesa vota uno).
Unidades extra del selector de nivel: partido y sección electoral = suma exacta de sus circuitos."""
import os, re, sys

REGION = sys.argv[1] if len(sys.argv) > 1 else "pba"
assert REGION in ("amba", "pba")
HERE = os.path.dirname(os.path.abspath(__file__))
CIRC = os.path.join(HERE, "..", "mapaAMBA2025")
sys.path.insert(0, HERE); sys.path.insert(0, CIRC)
from niveles import nivel_patches

_src = open(os.path.join(CIRC, "build_amba2025.py"), encoding="utf8").read()
_mid = open(os.path.join(CIRC, "mid_amba.py"), encoding="utf8").read().lstrip("\n")
_tail = open(os.path.join(CIRC, "tail_amba.py"), encoding="utf8").read()
HEAD = _src[:_src.index(_mid)]


def patch(t, patches, name):
    for old, new in patches:
        assert t.count(old) == 1, (name, old[:70], t.count(old))
        t = t.replace(old, new)
    return t


def patch_re(t, pat, new, name):
    t2, k = re.subn(pat, lambda m: new, t, count=1, flags=re.S)
    assert k == 1, (name, pat[:60])
    return t2


# ---------------------------------------------------------------- cabeza: datos, unidades, proyeccion
HP = [("import geomamba", "import cargar"),
      ("d, feats, target = geomamba.load()", "d, feats, target = cargar.load(REGION)")]
if REGION == "pba":
    HP += [("KX = math.cos(math.radians(34.7))\nLON0, LAT1 = -59.3775, -33.9233\nS, X0, Y0 = 975.0, 548.0, 140.0",
            "KX = math.cos(math.radians(36.6))\nLON0, LAT1 = -63.45, -33.12\nS, X0, Y0 = 194.0, 610.0, 112.0")]
HEAD = patch(HEAD, HP, "cabeza")
HEAD = patch_re(HEAD, r"def bloc_of\(n\):.*?DEFAULT_COL = \"#9a9a9a\"\n",
                'from partidos_sep import bloc_of, slug, title as _title, BLOCS, COLOR, LABEL\n'
                'POS = POS[POS.v > 0].copy()\n'
                'POS["bloc"] = POS.agrupacion_nombre.map(bloc_of)\n'
                'POS["code"] = [b if b else slug(n) for b, n in zip(POS.bloc, POS.agrupacion_nombre)]\n'
                'LAB = {}\n'
                'for c, n in zip(POS.code, POS.agrupacion_nombre): LAB.setdefault(c, _title(n))\n'
                'LAB.update(LABEL)\n'
                'DEFAULT_COL = "#9a9a9a"\n', "bloques")

# ---------------------------------------------------------------- despues de la cabeza: leyenda (regla 3) y niveles
EXTRA_CODE = r'''
WIN = collections.Counter(r.get("w") for r in unit_rec.values() if r.get("w"))
LEG = [b for b in BLOCS if WIN.get(b)]
print(REGION, "circuitos:", len(UKEYS), "ganadores:", dict(WIN), "positivos", TOT["pos"], {b: TOT["bloc"][b] for b in BLOCS}, file=sys.stderr)
NR = len(UKEYS)
EXTRA = []   # (clase, nombre, partido, d)
SECN = {1: "Primera", 2: "Segunda", 3: "Tercera", 4: "Cuarta", 5: "Quinta", 6: "Sexta", 7: "Séptima", 8: "Capital"}
p2s = {p: int(s) for p, s in d.drop_duplicates("part")[["part", "secc"]].itertuples(index=False)}
p2keys = collections.defaultdict(list)
for k in target: p2keys[part_of[(k[0], k[1])]].append(k)
def _shape(ix):
    u = unary_union([G_raw[i] for i in ix])
    return fill_slivers(u.buffer(0.7, join_style=2).buffer(-0.7, join_style=2)).simplify(0.04, preserve_topology=True)
SEC_GEOM = {}
if REGION == "pba":
    for s in sorted(set(p2s.values())):
        ps = [p for p in p2s if p2s[p] == s]
        a = agg_for([k for p in ps for k in p2keys[p]]); a["ok"] = 1 if a["pos"] else 0
        j = NR + len(EXTRA); unit_an[j] = a; disp[j] = "Sección %s" % SECN[s]
        unit_rec[j] = rec_from(a, "Sección electoral %s: %d partidos, suma de sus circuitos. Eligió %s provinciales." % (SECN[s], len(ps), "senadores" if s in (1, 4, 5, 7) else "diputados"))
        SEC_GEOM[s] = _shape([i for i in range(NR) if p2s.get(PART[i]) == s])
        EXTRA.append(("ss", disp[j], ps[0], geom_d(SEC_GEOM[s]), "seccion"))
for p in PARTIDOS:
    a = agg_for(p2keys[p]); a["ok"] = 1 if a["pos"] else 0
    j = NR + len(EXTRA); unit_an[j] = a; disp[j] = p
    unit_rec[j] = rec_from(a, "Suma de los circuitos del partido (sección %s)." % SECN[p2s[p]])
    EXTRA.append(("pp", p, p, geom_d(_shape([i for i in range(NR) if PART[i] == p])), "partido"))
NU = NR + len(EXTRA)
_SVG_EXTRA = "".join('<path class="%s" data-i="%d" d="%s"/>' % (e[0], j, e[3]) for j, e in enumerate(EXTRA, NR))
if REGION == "pba":   # limites de seccion electoral, mas gruesos que los de partido
    _SVG_EXTRA += "".join('<path class="pb sb" d="%s"/>' % line_d(g.boundary) for g in SEC_GEOM.values())
if REGION == "amba":   # Capital no voto el 7-sep: gris, rotulada
    _cb = unary_union([proj_geom(g) for g in cargar.caba_feats()]).buffer(0.5).buffer(-0.5)
    _cx, _cy = _cb.representative_point().coords[0]
    _SVG_EXTRA += '<path d="%s" fill="#d6d6d6" stroke="#fff" stroke-width="1"/>' % geom_d(_cb.simplify(0.05))
    _SVG_EXTRA += '<text class="cn" x="%.0f" y="%.0f" text-anchor="middle" font-size="15">CABA</text>' % (_cx, _cy + 5)
'''

# ---------------------------------------------------------------- parte del medio
FUENTE = ("Fuente: escrutinio provisorio por mesa de las elecciones legislativas bonaerenses del 7 de septiembre de 2025 (Junta Electoral / "
          "Ministerio de Gobierno de la Provincia de Buenos Aires; base de graficarpba). Senadores provinciales en las secciones 1.ª, 4.ª, 5.ª y 7.ª y "
          "diputados provinciales en la 2.ª, 3.ª, 6.ª y Capital: cada mesa vota un solo cargo y se suman como una sola categoría legislativa. "
          "Incluye las mesas de extranjeros residentes. Porcentajes sobre votos positivos; la torta y las barras son la suma %s del recuento provisorio "
          "(no el escrutinio definitivo). Somos Buenos Aires incluye la lista ligada «Espacio Abierto para el Desarrollo y la Integración Social», como "
          "la tabla de la Wikipedia. La base no informa votos nulos. %%d de %%s mesas sin votos en el provisorio. Geometría: circuitos CNE/INDEC de 2021; "
          "los circuitos que la base subdivide con letras se muestran con el polígono del circuito de origen; los que la capa no tiene se dibujan con el "
          "hueco que dejan sus vecinos (inferido)." % ("de los 40 partidos del AMBA (Capital no votó)" if REGION == "amba" else "de la provincia"))
if REGION == "amba":
    INS = ('INSETS = [\n'
           '    dict(id="core", label="Conurbano", f=[70, 610, 440, 470], win=win_ll(-58.52, -34.66, 0.40, 440 / 470), show=["d", "pb"], sd=1.5, sp=2.4),\n'
           '    dict(id="lp", label="Gran La Plata", f=[1450, 140, 430, 420], win=win_ll(-57.955, -34.905, 0.16, 430 / 420), show=["d", "pb"], sd=1.8, sp=2.6),\n'
           ']\n')
else:
    INS = ('INSETS = [\n'
           '    dict(id="core", label="Conurbano", f=[60, 560, 470, 430], win=win_ll(-58.52, -34.68, 0.66, 470 / 430), show=["d", "pb"], sd=1.2, sp=2.2),\n'
           '    dict(id="lp", label="Gran La Plata", f=[1500, 150, 400, 260], win=win_ll(-57.99, -34.95, 0.46, 400 / 260), show=["d", "pb"], sd=1.2, sp=2.2),\n'
           '    dict(id="mdp", label="Mar del Plata", f=[1700, 760, 210, 230], win=win_ll(-57.58, -38.02, 0.22, 210 / 230), show=["d", "pb"], sd=1.2, sp=2.2),\n'
           '    dict(id="bb", label="Bahía Blanca", f=[1700, 1050, 210, 230], win=win_ll(-62.27, -38.72, 0.32, 210 / 230), show=["d", "pb"], sd=1.2, sp=2.2),\n'
           ']\n')
MODES_T = ('    ("fp", "FP", pct("FP"), COLOR["FP"], [0, 25, 35, 45, 55, 65, 75], "% Fuerza Patria"),\n'
           '    ("lla", "LLA", pct("LLA"), COLOR["LLA"], [0, 15, 25, 30, 35, 40, 50], "% La Libertad Avanza"),\n'
           '    ("sb", "SOMOS", pct("SB"), "#d63384", [0, 3, 5, 8, 12, 20, 30], "% Somos Buenos Aires"),\n'
           '    ("par", "PART.", lambda a: 100 * a["E"] / a["elok"], "#4a4a4a", [30, 45, 52, 57, 62, 67, 72], "Participación (mesas con votos)")):\n')
OUT = "atlas_%s2025sep" % REGION
MID = patch(_mid, [
    ('    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], logo="FP"),\n'
     '    "LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a2f85", txt="#5a2f85", logo="LLA"),\n'
     '    "FIT": dict(n="Frente de Izquierda", sub="y de Trabajadores - Unidad", base=COLOR["FIT"], logo="FIT"),\n'
     '    "PU": dict(n="Provincias Unidas", sub="Ciudadanos Unidos en Capital", base=COLOR["PU"], bar="#f06a0b", txt="#d9560a", logo="PU"),\n',
     '    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], bar="#0089c9", logo="FP"),\n'
     '    "LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a3f80", txt="#5a3f80", logo="LLA"),\n'
     '    "SB": dict(n="Somos Buenos Aires", sub="y Espacio Abierto", base=COLOR["SB"], bar="#e0609a", txt="#c2457f", logo="SOMOS"),\n'
     '    "FIT": dict(n="Frente de Izquierda", sub="y de Trabajadores - Unidad", base=COLOR["FIT"], bar="#d93840", txt="#d93840", logo="FIT"),\n'),
    ('_lg = os.path.join(HERE, "logos_amba2025.py")', '_lg = os.path.join(HERE, "logos_sep.py")'),
    ('for b in BLOCS], key=lambda c: -c["votes"])', 'for b in LEG], key=lambda c: -c["votes"])'),
    ('["Mesas escrutadas", "%s de %s" % (fmt_n(TOT["ok"]), fmt_n(TOT["mesas"]))]]', '["Mesas con votos", "%s de %s" % (fmt_n(TOT["ok"]), fmt_n(TOT["mesas"]))]]'),
    ('legend=dict(keys=[[BEIGE, "Circuito sin mesas en la base provisoria"]]))]',
     'legend=dict(keys=[[BEIGE, "Circuito sin mesas (tampoco en octubre)" if REGION == "pba" else "Sin mesas con votos en el provisorio"]] + ([["#d6d6d6", "Capital: no votó (elección local del 18 de mayo)"]] if REGION == "amba" else [])))]'),
    ('    ("fp", "FP", pct("FP"), COLOR["FP"], [0, 20, 30, 40, 50, 60, 70], "% Fuerza Patria"),\n'
     '    ("lla", "LLA", pct("LLA"), COLOR["LLA"], [0, 20, 30, 40, 50, 60, 70], "% La Libertad Avanza"),\n'
     '    ("fit", "FIT", pct("FIT"), COLOR["FIT"], [0, 3, 5, 8, 12, 18, 25], "% Frente de Izquierda - Unidad"),\n'
     '    ("par", "PART.", lambda a: 100 * a["E"] / a["elok"], "#4a4a4a", [40, 55, 62, 66, 70, 74, 78], "Participación (mesas escrutadas)")):\n', MODES_T),
    ('    for i in range(len(UKEYS)):\n        r = unit_rec[i]; a = unit_an[i]', '    for i in range(NU):\n        r = unit_rec[i]; a = unit_an[i]'),
    ('units=[unit_rec[i] for i in range(len(UKEYS))], prov=prov_rec', 'units=[unit_rec[i] for i in range(NU)], prov=prov_rec'),
    ('PGEOM = {}\n', 'body.append(_SVG_EXTRA)\nPGEOM = {}\n'),
    ('slug="diputados_amba_2025"', 'slug=OUT'),
    ('title="Elecciones legislativas en el AMBA de", year="2025"',
     'title=("Legislativas bonaerenses en el AMBA de" if REGION == "amba" else "Legislativas bonaerenses de"), year="2025"'),
    ('sets={"1": dict(label="2025", subtitle="Por circuito · provisorio")},', 'sets={"1": dict(label="2025", subtitle="7 sep. · por circuito · provisorio")},'),
    ('territories=[dict(n=disp[i], p=PART[i], k="circuito") for i in range(len(UKEYS))],',
     'territories=[dict(n=disp[i], p=PART[i], k="circuito") for i in range(NR)] + [dict(n=e[1], p=e[2], k=e[4]) for e in EXTRA],'),
    ('json.dump(ds, open(os.path.join(HERE, "dataset_amba2025.json"), "w", encoding="utf8"), ensure_ascii=False)',
     'json.dump(ds, open(os.path.join(HERE, "dataset_%s2025sep.json" % REGION), "w", encoding="utf8"), ensure_ascii=False)'),
], "mid")
MID = patch_re(MID, r"\nNOTE = \(.*?\n\n", "\nNOTE = (%r %% (TOT[\"mesas\"] - TOT[\"ok\"], fmt_n(TOT[\"mesas\"])))\n\n" % FUENTE, "nota")
MID = patch_re(MID, r"INSETS = \[\n.*?\n\]\n", INS, "recuadros")

if REGION == "amba":
    LEVELS = [("p", "pp", "Partido", "Partidos: suma de sus circuitos", "partido"), ("c", "d", "Circuito", "Circuitos electorales", "circuito")]
    DEF = "c"
else:
    LEVELS = [("s", "ss", "Sección", "Secciones electorales: suma de sus partidos", "seccion"), ("p", "pp", "Partido", "Partidos: suma de sus circuitos", "partido"),
              ("c", "d", "Circuito", "Circuitos electorales", "circuito")]
    DEF = "p"
TAIL = patch(_tail, [
    ('sub("<title>Atlas electoral</title>", "<title>Diputados nacionales 2025 · AMBA por circuito</title>")',
     'sub("<title>Atlas electoral</title>", "<title>%s</title>")' % ("Bonaerenses 2025 · AMBA" if REGION == "amba" else "Bonaerenses 2025 · provincia")),
    ('out = os.path.join(HERE, "atlas_amba2025.html")', 'out = os.path.join(HERE, OUT + ".html")'),
] + ([("1024):1266;", "1024):1150;")] if REGION == "pba" else []), "cola")
_marker = 'html = (tpl.replace('
extra_css = ".sb{stroke-width:calc(var(--sp,3px) * 1.9 / var(--k,1)) !important}" if REGION == "pba" else ""
for old, new in nivel_patches(LEVELS, DEF, extra_css):
    TAIL = TAIL.replace(_marker, "sub(" + repr(old) + "," + repr(new) + ")\n" + _marker)
exec(HEAD + EXTRA_CODE + MID + TAIL)
