"""Una vez: deriva el dibujo del constructor 1930, sin ejecutar ni modificar ese atlas."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'mapas/mapa1930/build_1930.py').read_text(encoding='utf-8')
head='''"""Atlas 1926/1937/1940, derivado del dibujo de 1930 y de los atlas publicados 1922/1928.
Uso desde la raíz: python transcripciones/entreguerras/construir.py 1926
"""
from pathlib import Path
import sys, os, json, pickle, copy
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'comun'),str(ROOT/'mapas/mapa1930')]
import numpy as np, shapely
from shapely.ops import unary_union
import geom
from names import norm
from atlas_datos import prepare
from datos import NATIONAL
Y=int(sys.argv[1]);assert Y in (1926,1937,1940)
HERE=str(ROOT/'mapas'/f'mapa{Y}');Path(HERE).mkdir(exist_ok=True)
TEMPLATE_SRC=str(ROOT/'.claude/skills/mapa-electoral-wikipedia-1999/assets/template.html')
'''
geometry=src[src.index('# ---------------------------------------------------------------- proyeccion'):src.index('# ---------------------------------------------------------------- datos:')]
geometry=geometry.replace('PKL = os.path.join(HERE, "units_raw.pkl")','PKL = str(ROOT / "mapas/mapa1930/units_raw.pkl")')
data='''
ctx=prepare(Y,U,norm)
for k in ('KEY','CAND','BLOCS','GREY_T','GREY_N','KEYS','unit_rec','unit_an','prov_rec','prov_an','disp','unmapped'):
    globals()[k]=ctx[k]
an_of=lambda t:t
import wikitop
cands,slices,partp,NAT_MET=wikitop.national(Y)
NOTE=(wikitop.note(Y)+
      ' Fuente local: Cantón (1968), t. II, varones solamente. Geometría de 1914, como los atlas publicados de 1922/1928; '
      'correspondencias nominales y unidades compartidas documentadas. Sin imputación de votos. ')
if Y in (1937,1940):
    NOTE+='Cobertura parcial: selección de distritos publicada por Cantón según su criterio editorial de 1931–1942; no certifica ausencia de irregularidades. '
NOTE+='La suma territorial puede diferir del resultado nacional de Wikipedia; se conservan las discrepancias del original.'
def fmt_n(v):return f'{int(v):,}'.replace(',','.')
def fmt_p(v):return ('%.1f'%v).replace('.',',')
'''
mode=src[src.index('def mix(hexc, t):'):src.index('NOTE = ("Fuente: D. Cantón')]
mode+=src[src.index('def mode_choropleth('):src.index('MODES = [dict(id="gan"')]
mode+='''
MODES=[dict(id='gan',tile='GANÓ',note=NOTE,units=[unit_rec[i] for i in range(len(U))],prov=prov_rec,
            national=dict(cands=cands,slices=slices,partp=partp,metrics=NAT_MET),legend=dict(keys=KEYS))]
for b in BLOCS:
    un,pv,lg=mode_choropleth(lambda a,b=b:100*a['bloc'].get(b,0)/a['D'],CAND[b]['base'],list(range(0,70,10)),'% '+CAND[b]['n'])
    MODES.append(dict(id=b.lower(),tile=b if b in ('UCR','CON','ANT') else '',note=NOTE,units=un,prov=pv,
                      national=dict(cands=cands,slices=slices,partp=partp,metrics=NAT_MET),legend=lg))
un,pv,lg=mode_choropleth(lambda a:100*a['vot']/a['ins'] if a['vot'] and a['ins'] else None,
                         '#2a6f97',[0,40,50,60,70,80,90],'Participación (votantes / inscriptos)')
MODES.append(dict(id='par',tile='PART',note=NOTE,units=un,prov=pv,
                  national=dict(cands=cands,slices=slices,partp=partp,metrics=NAT_MET),legend=lg))
'''
tail=src[src.index('# ---------------------------------------------------------------- SVG'):]
start=tail.index('_c = prov_geom["San Luis"].representative_point()');end=tail.index('for txt, lon',start)
tail=tail[:start]+tail[end:]
tail='\n'.join(l for l in tail.split('\n') if not l.startswith('pv.append(\'<text x="%s" y="%s"'))
tail=tail.replace('slug="elecciones_1930"','slug=f"elecciones_{Y}"').replace('year="1930"','year=str(Y)')
tail=tail.replace('title="Elecciones legislativas de Argentina de", year=', 'title=("Elecciones presidenciales de Argentina de" if Y==1937 else "Elecciones legislativas de Argentina de"), year=')
tail=tail.replace('label="1930", subtitle="Cantón (1968) · deptos. de 1914"','label=str(Y), subtitle="Cantón · deptos. de 1914"')
tail=tail.replace('"dataset_1930.json"','f"dataset_{Y}.json"').replace('"atlas_1930.html"','f"atlas_{Y}.html"')
tail=tail.replace('"<title>Diputados nacionales 1930</title>"','f"<title>Atlas electoral {Y}</title>"')
# Se preserva el tratamiento centrado de los logos del dibujo histórico.
start=tail.index('# logos de la leyenda al ras');tail=tail[:start]+'''print('escrito',out,flush=True)
from collections import Counter
control=dict(anio=Y,unidades_geometricas=len(U),unidades_con_votos=len(unit_an),
    ganadores_por_poligono=dict(Counter(r.get('w') for r in unit_rec.values() if r.get('w'))),
    sin_poligono=[dict(prov=r['prov'],unidad=r['name'],pagina_pdf=r['page'],votos=sum(r['P'].values())) for r in unmapped],
    filas_fuente_usadas_sin_duplicar=len(ctx['usedrows']),
    fuente_geometria='Departamentos_1914; mismo dibujo y proyección que 1922/1928/1930',
    modos=[m['id'] for m in MODES])
Path(HERE,'CONTROL_ATLAS.json').write_text(json.dumps(control,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(control,ensure_ascii=False),flush=True)
'''
# Nueve filas en 1926: conserva el estilo de 1930 con barras algo más bajas.
tail=tail.replace('const MANY=N.cands.length>5,Y0=MANY?1024:1266;', 'const MANY=N.cands.length>5,Y0=N.cands.length>8?980:MANY?1024:1266;')
tail=tail.replace('const h=MANY?42:50,k=h/50', 'const h=N.cands.length>8?34:MANY?42:50,k=h/50')
(ROOT/'transcripciones/entreguerras/construir.py').write_text(head+geometry+data+mode+tail,encoding='utf-8')
