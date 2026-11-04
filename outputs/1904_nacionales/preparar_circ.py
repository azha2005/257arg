from pathlib import Path
import csv,json,collections
p=Path(__file__).resolve().parent
root=p.parents[1]
rows=list(csv.DictReader((root/'mapas/mapa1904/candidatos_1904.csv').open(encoding='utf-8-sig')))
groups=collections.defaultdict(list)
for r in rows:groups[(r['provincia'],int(r['numero']))].append(r)
ds=json.loads((root/'mapas/mapa1904/dataset_1904.json').read_text(encoding='utf8'))
out=[]
for t in ds['territories']:
    if t['k']!='circunscripción':continue
    # Los números se conservan en el CSV para las renovadas y en el orden
    # de los trazos numerados del SVG para las restantes.
    import xml.etree.ElementTree as E,re
    tree=E.parse(root/'mapas/mapa1904/circunscripciones_1904.svg').getroot()
    L='{http://www.inkscape.org/namespaces/inkscape}label'
    layer=next(x for x in tree if x.get('id')=='layer2')
    province=next(x for x in layer if x.get(L)==t['p'])
    labels=[x.get(L,'')for x in province if re.match(r'\d+ - ',x.get(L,''))]
    number=next(int(x.split(' - ')[0])for x in labels if x.split(' - ',1)[1]==t['n'])
    g=groups.get((t['p'],number),[])
    if not g:
        out.append([t['p'],number,t['n'],'','','',None,None,'','Sin elección'])
        continue
    total=sum(int(x['votes'])for x in g if x['votes'])
    for i,r in enumerate(g):
        v=int(r['votes'])if r['votes']else None
        out.append([t['p'],number,t['n'],r['candidate'],r['party'],r['bloque'],v,v/total if v is not None and total else None,'Sí'if i==0 else 'No','Votos publicados'if v is not None else 'Electo conocido; votos no publicados'])
out.sort(key=lambda r:(r[0],r[1],-(r[6]or 0)))
assert len({(r[0],r[1])for r in out})==120
assert sum(r[6]or 0 for r in out)==129796
(p/'circ_datos.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
print(len(out),'filas, 120 circunscripciones')
