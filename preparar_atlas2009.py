"""Deriva el atlas 2009 del build 2013, sin modificar la plantilla compartida."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
out = root / 'mapa2009'
out.mkdir(exist_ok=True)
for fn in ('names.py', 'shp.py'):
    shutil.copy2(root/'mapa2013'/fn, out/fn)
g = (root/'mapa2013/geom.py').read_text(encoding='utf8')
g = g.replace('return _split_lezama(out)', 'return out')
g = g.replace(' + partido de Lezama (escindido de Chascomus en dic. 2009)', ' (sin Lezama: elección de junio de 2009)')
(out/'geom.py').write_text(g, encoding='utf8')
s = (root/'mapa2013/build_2013.py').read_text(encoding='utf8').replace('2013', '2009')
a = s.index('# ---------------------------------------------------------------- datos DINE')
b = s.index('def fmt_n(', a)
s = s[:a] + '''# Datos preparados con trazabilidad por lista y controles de cobertura.
from datos_2009 import AG, MESAS, D2P, SUBSEC_MERGE, BLOCS, LIST2BLOC, CAND, EALIAS, NICE, BARRIOS_COMUNA

''' + s[b:]
a = s.index('# Colores de la tabla de Wikipedia')
b = s.index('# Nombres legibles', a)
s = s[:a] + s[b:]
s = s.replace('== "DIPUTADO NACIONAL"', '.str.contains("DIPUTAD")')
# La expresión anterior necesita acceso a Series, no a una comparación.
s = s.replace('votes_df["cargo_nombre"] .str', 'votes_df["cargo_nombre"].str')
# Se conservan el cargador y el archivo logos_2009.py propios del año.
s = s.replace('== "EN BLANCO"', '.isin(["EN BLANCO", "BLANCO"])')
s = s.replace('grp["votos_tipo"] .isin', 'grp["votos_tipo"].isin')
s = s.replace('assert not missing_geom, ("Poligonos sin dato:", missing_geom)', 'assert not missing_geom, ("Poligonos sin dato:", missing_geom)')
s = s.replace('Nombre en la base DINE:', 'Nombre en la base PolAr:')
s = s.replace('    extras.extend(e["notes"])', '''    if p == "Buenos Aires":
        extras.append("Todas las listas: planilla del usuario Merged file (15).xls, hoja Sheet1, elección DN 2009; los totales son compatibles con el definitivo sin votos auxiliares. Electores: PolAr.")
        if e["s"] == "106": extras.append("La planilla dice S. NICOLAS; el código 106 corresponde a San Isidro y el 107 a San Nicolás. Se conserva el código, validado contra PolAr.")
        if e["s"] == "051": extras.append("Se corrigieron siete separadores de miles mal interpretados en General Rodríguez; la suma de todas las listas cierra exactamente con positivos y votantes.")
    if p == "Jujuy" and e["s"] == "008": extras.append("Todas las listas recuperadas de Merged file (15).xls: 1.734 positivos, 49 blancos y 12 nulos. Electores: PolAr.")
    if p == "Tierra del Fuego": extras.append("Escrutinio definitivo DINE: PDF oficial, páginas 6 a 8. No incluye electores en el exterior ni privados de libertad.")
    extras.extend(e["notes"])''')
a = s.index('NOTE = (')
b = s.index('\n\n\ndef stops_for', a)
s = s[:a] + '''NOTE = ("Nacional: tabla de Wikipedia. Mapa: PolAr/Andy Tow (provisorio); Buenos Aires y Valle Grande (Jujuy): planilla recuperada del usuario; "
        "Tierra del Fuego: definitivo DINE. Se muestran todas las listas disponibles sin imputar votos. "
        "Las sumas locales difieren de la tabla nacional; ver LEEME. Capital: 15 comunas. Chascomús incluye el futuro Lezama.")
KEYS = [[GREY_P, "Sin datos disponibles"]]
''' + s[b:]
s = s.replace('("fpcys", "FPCyS", lambda a: 100 * a["bloc"]["FPCyS"] / a["pos"], "#ff8c00"', '("acys", "ACyS", lambda a: 100 * a["bloc"]["ACyS"] / a["pos"], "#e10019"')
s = s.replace('% Frente Progresista Cívico y Social y aliados', '% Acuerdo Cívico y Social y aliados')
s = s.replace('("fr", "FR", lambda a: 100 * a["bloc"]["FR"] / a["pos"], "#4a5568"', '("pf", "PF", lambda a: 100 * a["bloc"]["PF"] / a["pos"], "#8e6bd8"')
s = s.replace('% Frente Renovador y aliados', '% Peronismo Federal y aliados')
s = s.replace('Participación sobre mesas escrutadas (%)', 'Participación según la base disponible (%)')
s = s.replace('DINE (provisorio) · deptos. 2010', 'Diputados nacionales')
s = s.replace('N.cands.length>10)?994:1266', 'N.cands.length>=8)?1160:1266')
s = s.replace('=== Bloques segun la base provisoria DINE vs. Wikipedia (definitivo) ===', '=== Bloques segun PolAr + TDF definitivo vs. Wikipedia ===')
s = s.replace('DINE=%10s', 'Base=%10s')
# La Antártida tiene resultado departamental propio, separado de Ushuaia.
s = s.replace('# Emparejar cada unidad', 'ant_e = sec_raw.pop(("24", "003"))\n\n# Emparejar cada unidad')
s = s.replace('prov_rec = {}', '''ant_an = analyse(ant_e)
pa = prov_an["Tierra del Fuego"]
for k in ("pos", "E", "bla", "nul", "ins", "el_tot", "el_ok", "m_tot", "m_ok"): pa[k] += ant_an[k]
for c,x in ant_an["P"].items(): pa["P"][c] = pa["P"].get(c,0)+x
for b in BLOCS: pa["bloc"][b] += ant_an["bloc"][b]
prov_rec = {}''')
s = s.replace('# ---------------------------------------------------------------- SVG', '''# Antártida: territorio interactivo propio, sin añadirlo al mapa continental.
ANT_I = len(U)
for m in MODES:
    rec = rec_from(ant_an, "Definitivo DINE, página 7: 142 positivos, 14 blancos y 3 nulos. Ocho impugnados de Orcadas informados aparte, sin escrutar.")
    if m["id"] != "gan":
        if m["id"] == "par": value = 100*ant_an["E"]/ant_an["ins"]
        else: value = 100*ant_an["bloc"][{"fpv":"FPV","acys":"ACyS","pf":"PF","pro":"PRO"}[m["id"]]]/ant_an["pos"]
        edges = {"fpv":[0,20,30,40,50,60,70],"acys":[0,15,25,35,45,55,65],"pf":[0,10,20,30,40,50,60],"pro":[0,5,10,20,30,40,50],"par":[0,70,75,80,85,90,95]}[m["id"]]
        rec.pop("w",None); rec.pop("q",None)
        rec["fill"] = m["legend"]["stops"][bin_of(value,edges)][0]
    m["units"].append(rec)

# ---------------------------------------------------------------- SVG''')
s = s.replace('body.append(X99["ant_body"])','body.append(X99["ant_body"].replace(\'class="ant"\', \'class="ant" data-i="%d"\' % ANT_I))')
s = s.replace('territories=[dict(p=u["prov"], n=disp[i], k=u["kind"]) for i, u in enumerate(U)],', 'territories=[dict(p=u["prov"], n=disp[i], k=u["kind"]) for i, u in enumerate(U)]+[dict(p="Tierra del Fuego",n="Antártida Argentina",k="departamento")],')
(out/'build_2009.py').write_text(s, encoding='utf8', newline='\n')
