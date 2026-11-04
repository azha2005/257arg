"""Atlas de las legislativas bonaerenses del 7-sep-2025 en el AMBA por radio censal 2022 (método de Poblaciones / LN Data).
  python mapas/mapaPBA2025sep/build_radios.py   -> atlas_amba2025sep_radios.html (niveles Partido / Circuito / Radio)
Antes: preparar.py, locales_sep.py, asignar_sep.py y build_circuitos.py amba (el nivel Circuito toma sus fichas: votos observados).
Reutiliza ../mapaAMBA2025radios/build_amba2025radios.py (que a su vez toma la parte del medio y la cola del atlas por circuito)
con reemplazos; cada texto reemplazado tiene que aparecer una sola vez. Capital no votó el 7-sep: sus radios no entran y se
dibuja en gris."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAD = os.path.join(HERE, "..", "mapaAMBA2025radios")
sys.path.insert(0, HERE)
sys.argv = sys.argv[:1]   # variante «idw» (la principal)


def patch(t, patches, name):
    for old, new in patches:
        assert t.count(old) == 1, (name, old[:70], t.count(old))
        t = t.replace(old, new)
    return t


def patch_re(t, pat, new, name):
    t2, k = re.subn(pat, lambda m: new, t, count=1, flags=re.S)
    assert k == 1, (name, pat[:60])
    return t2


NOTE = ("Fuente: escrutinio provisorio por mesa de las legislativas bonaerenses del 7 de septiembre de 2025 (base de graficarpba): senadores "
        "provinciales en las secciones 1.ª y 7.ª y diputados en la 2.ª, 3.ª y Capital del AMBA, sumados como un solo cargo legislativo; incluye mesas de "
        "extranjeros. Locales de votación de la misma base, ubicados con los del atlas de octubre (misma codificación de la DINE: 91,6 % de los "
        "electores) y, los que solo tienen mesas de extranjeros, con el padrón de escuelas de la DGCyE (6,3 %) o el centro de su circuito (2,1 %). "
        "Cada local reparte sus votos entre los radios censales 2022 de su partido con peso 1/distancia² al centroide del radio (método de "
        "Poblaciones / LN Data); los radios con menos de 1 voto quedan en 0. Es una estimación: el voto no se registra por radio. Los totales por "
        "partido son exactos; la torta y las barras son la suma de los 40 partidos del AMBA (Capital no votó). Somos Buenos Aires incluye la lista "
        "ligada «Espacio Abierto». Radios: CONICET (Rodríguez), censo 2022. Porcentajes sobre votos positivos; la base no informa votos nulos.")

src = open(os.path.join(RAD, "build_amba2025radios.py"), encoding="utf8").read()
src = patch(src, [
    ('HERE = os.path.dirname(os.path.abspath(__file__))\nROOT = os.path.join(HERE, "..")',
     'HERE = %r\nROOT = os.path.join(HERE, "..")' % HERE),
    ('AS = pickle.load(open(os.path.join(HERE, "asignacion_%s.pkl" % VAR), "rb"))', 'AS = pickle.load(open(os.path.join(HERE, "asignacion_sep.pkl"), "rb"))'),
    ('LAB.update(FP="Fuerza Patria", LLA="La Libertad Avanza", FIT="Frente de Izquierda y de Trabajadores - Unidad", PU="Provincias Unidas (Ciudadanos Unidos en Capital)")\n'
     'BLOCS = ["FP", "LLA", "FIT", "PU"]\n',
     'from partidos_sep import BLOCS, LABEL, title as _title\nLAB = {c: _title(AS["LAB"][c]) for c in PCATS}\nLAB.update(LABEL)\n'),
    ('COLOR = dict(FP="#009ce4", LLA="#6c4c98", FIT="#f65058", PU="#FF682C")', 'from partidos_sep import COLOR'),
    ('R = json.load(open(os.path.join(HERE, "radios_amba2022.geojson"), encoding="utf8"))["features"]',
     'R = [f for f in json.load(open(os.path.join(ROOT, "mapaAMBA2025radios", "radios_amba2022.geojson"), encoding="utf8"))["features"] if f["properties"]["PROV"] != "02"]'),
    ('_cds = json.load(open(os.path.join(CIRC, "dataset_amba2025.json"), encoding="utf8"))', '_cds = json.load(open(os.path.join(HERE, "dataset_amba2025sep.json"), encoding="utf8"))'),
    ('_chtml = open(os.path.join(CIRC, "atlas_amba2025.html"), encoding="utf8").read()', '_chtml = open(os.path.join(HERE, "atlas_amba2025sep.html"), encoding="utf8").read()'),
    ('exec(open(os.path.join(HERE, "logos_radios.py"), encoding="utf8").read())', 'exec(open(os.path.join(HERE, "logos_sep.py"), encoding="utf8").read())'),
    ('rec["note"] = ((r.get("note", "") + " ") if r.get("note") else "") + "Resultado observado del circuito (escrutinio provisorio): no es una estimación."',
     'rec["note"] = ((r.get("note", "") + " ") if r.get("note") else "") + "Resultado observado del circuito (recuento provisorio): no es una estimación."'),
    ('"Suma de las estimaciones por radio: coincide con el escrutinio provisorio."', '"Suma de las estimaciones por radio: coincide con el recuento provisorio del partido."'),
], "radios")
src = patch_re(src, r'\nNOTE = \(.*?\)\nMID = ', "\nNOTE = %r\nMID = " % NOTE, "nota")
# despues de que el constructor por radio arma MID y TAIL, los reemplazos propios de esta eleccion
INS = ('INSETS = [\n'
       '    dict(id="core", label="Conurbano", f=[70, 610, 440, 470], win=win_ll(-58.52, -34.66, 0.40, 440 / 470), show=["d", "pb"], sd=0.2, sp=2.4),\n'
       '    dict(id="lp", label="Gran La Plata", f=[1450, 140, 430, 420], win=win_ll(-57.955, -34.905, 0.16, 430 / 420), show=["d", "pb"], sd=0.25, sp=2.6),\n'
       ']\n')
SEP = r'''
MID = _patch(MID, [
    ('    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], bar="#0089c9", logo="FP"),\n'
     '    "LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a3f80", txt="#5a3f80", logo="LLA"),\n'
     '    "FIT": dict(n="Frente de Izquierda", sub="y de Trabajadores - Unidad", base=COLOR["FIT"], bar="#d93840", txt="#d93840", logo="FIT"),\n'
     '    "PU": dict(n="Provincias Unidas", sub="Ciudadanos Unidos en Capital", base=COLOR["PU"], bar="#f06a0b", txt="#d9560a", logo="PU"),\n',
     '    "FP": dict(n="Fuerza Patria", sub="", base=COLOR["FP"], bar="#0089c9", logo="FP"),\n'
     '    "LLA": dict(n="La Libertad Avanza", sub="", base=COLOR["LLA"], bar="#5a3f80", txt="#5a3f80", logo="LLA"),\n'
     '    "SB": dict(n="Somos Buenos Aires", sub="y Espacio Abierto", base=COLOR["SB"], bar="#e0609a", txt="#c2457f", logo="SOMOS"),\n'
     '    "FIT": dict(n="Frente de Izquierda", sub="y de Trabajadores - Unidad", base=COLOR["FIT"], bar="#d93840", txt="#d93840", logo="FIT"),\n'),
    ('legend=dict(keys=[[BEIGE, "Radio sin votos asignados"]]))]',
     'legend=dict(keys=[[BEIGE, "Radio sin votos asignados"], ["#d6d6d6", "Capital: no votó (elección local del 18 de mayo)"]]))]'),
    ('title="Elecciones legislativas en el AMBA de", year="2025"', 'title="Legislativas bonaerenses en el AMBA de", year="2025"'),
    ('subtitle=("Por radio censal · estimado" if VAR == "idw" else "Por radio · estimado (población)")', 'subtitle="7 sep. · por radio · estimado"'),
    ('bins=[42, 45, 47, 50, 55, 60], bin_labels=["<42%", "42%", "45%", "47%", "50%", "55%", "+60%"]',
     'bins=[40, 45, 50, 55, 60, 65], bin_labels=["<40%", "40%", "45%", "50%", "55%", "60%", "+65%"]'),
    ('body.append(_SVG_EXTRA)\nPGEOM = {}\n', 'body.append(_SVG_EXTRA)\nbody.append(_CABA)\nPGEOM = {}\n'),
    ('json.dump(ds, open(os.path.join(HERE, "dataset_amba2025radios%s.json" % SUF), "w", encoding="utf8"), ensure_ascii=False)',
     'json.dump(ds, open(os.path.join(HERE, "dataset_amba2025sep_radios.json"), "w", encoding="utf8"), ensure_ascii=False)'),
])
MID = _patch_re(MID, r"    \(\"fp\", \"FP\".*?\"Participación estimada\"\)\):\n",
    '    ("fp", "FP", pct("FP"), COLOR["FP"], [0, 30, 40, 48, 55, 62, 70], "% Fuerza Patria"),\n'
    '    ("lla", "LLA", pct("LLA"), COLOR["LLA"], [0, 20, 26, 32, 38, 44, 50], "% La Libertad Avanza"),\n'
    '    ("sb", "SOMOS", pct("SB"), "#d63384", [0, 2, 3, 4, 6, 9, 13], "% Somos Buenos Aires"),\n'
    '    ("par", "PART.", lambda a: 100 * a["E"] / a["elok"], "#4a4a4a", [30, 45, 52, 57, 62, 67, 72], "Participación estimada")):\n')
MID = _patch_re(MID, r"INSETS = \[\n.*?\n\]\n", INS)
TAIL = _patch(TAIL, [
    ('<title>Diputados 2025 · AMBA por radio</title>', '<title>Bonaerenses 2025 · AMBA por radio</title>'),
    ('out = os.path.join(HERE, "atlas_amba2025radios%s.html" % SUF)', 'out = os.path.join(HERE, "atlas_amba2025sep_radios.html")'),
])
import cargar
_cb = unary_union([proj_geom(g) for g in cargar.caba_feats()]).buffer(0.5).buffer(-0.5)
_cx, _cy = _cb.representative_point().coords[0]
_CABA = ('<path d="%s" fill="#d6d6d6" stroke="#fff" stroke-width="1"/>' % geom_d(_cb.simplify(0.05))
         + '<text class="cn" x="%.0f" y="%.0f" text-anchor="middle" font-size="15">CABA</text>' % (_cx, _cy + 5))
'''
src = patch(src, [("exec(MID)\nexec(TAIL)", SEP + "exec(MID)\nexec(TAIL)")], "final")
glb = dict(__name__="__main__", __file__=os.path.join(RAD, "build_amba2025radios.py"),
           _patch=lambda t, p: patch(t, p, "radios"), _patch_re=lambda t, pat, new: patch_re(t, pat, new, "radios"), INS=INS)
exec(compile(src, "build_amba2025radios(sep)", "exec"), glb)
