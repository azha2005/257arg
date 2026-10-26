"""Deriva el constructor compartido de la referencia 2009, conservando sus parches SVG/HTML."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=(ROOT/'mapa2009/build_2009.py').read_text(encoding='utf8')
s=s.replace('HERE = os.path.dirname(os.path.abspath(__file__))','ROOT = os.path.dirname(os.path.abspath(__file__))\nYEAR = int(sys.argv[1])\nHERE = os.path.join(ROOT, f"mapa{YEAR}")\nos.makedirs(HERE, exist_ok=True)')
s=s.replace('import geom, wikitop','import leg2003_2025_geom as geom\nimport wikitop')
s=s.replace('raw = geom.load()','raw = geom.load(YEAR)')
s=s.replace('RAW_CACHE = os.path.join(HERE, "units_raw.pkl")','RAW_CACHE = os.path.join(HERE, "units_leg2003_2025.pkl")')
a=s.index('# Datos preparados con trazabilidad');b=s.index('# ---------------------------------------------------------------- SVG',a)
s=s[:a]+'''# Datos y controles compartidos: el cartel nacional se conserva separado del mapa.
from leg2003_2025_data import prepare
D = prepare(YEAR, U)
CAND, MODES, disp, ANT_I = D.CAND, D.MODES, D.disp, D.ANT_I
MALV = {i for i, u in enumerate(U) if u["name"] == "Islas Malvinas"}
\n'''+s[b:]
s=s.replace('year=2009, slug="diputados_2009"','year=YEAR, slug=f"diputados_{YEAR}"')
s=s.replace('"dataset_2009.json"','f"dataset_{YEAR}.json"')
s=s.replace('candidates=CAND, insets=INSETS,','candidates=CAND, insets=INSETS, solid=D.report.get("solid", []),')
s=s.replace('"atlas_2009.html"','f"atlas_{YEAR}.html"')
s=s.replace('"<title>Elecciones legislativas 2009</title>"','f"<title>Elecciones legislativas {YEAR}</title>"')
s=s.replace('"Departamentos_2010")','"Departamentos_2001" if YEAR <= 2007 else "Departamentos_2010")')
# Leyenda adaptable, manteniendo los logos dentro de su celda.
s=s.replace('N.cands.length>=8)?1160:1266','N.cands.length>12)?1022:N.cands.length>=8?1160:1266')
s=s.replace('N.cands.length>10)?1022:1266','N.cands.length>12)?1022:N.cands.length>=8?1160:1266')
s=s.replace('const h=27,win=','const h=rows.length>12?23:27,win=')
s=s.replace('y+=8.5;','y+=(N.cands.length>12?7:8.5);')
s=s.replace(')?1022:N.cands.length>=8',')?1008:N.cands.length>=8')
s=s.replace('"font-size":14.5,fill:"#fff","text-anchor":"end"','"font-size":14.5,fill:"#fff","text-anchor":"end",...(C.n.length>29?{textLength:232,lengthAdjust:"spacingAndGlyphs"}:{})')
(ROOT/'atlas_leg2003_2025.py').write_text(s,encoding='utf8',newline='\n')
for y in (2003,2005,2007,2011,2015,2017,2019,2021,2023,2025):
    p=ROOT/f'mapa{y}';p.mkdir(exist_ok=True)
    (p/f'build_{y}.py').write_text(f'''"""Diputados {y}, constructor compartido derivado de 2009."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(root/'atlas_leg2003_2025.py'),'{y}'],check=True,cwd=root)
''',encoding='utf8')
