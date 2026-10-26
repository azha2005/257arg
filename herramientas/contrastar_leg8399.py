import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "comun")]  # módulos compartidos (reorganización: ver README)
from lxml import html
from pathlib import Path
import re,json,csv,collections,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlas_leg8399 import norm
for y in [1983,1989,1995,1999]:
    source=Path(f'mapas/mapa{y}dip/wiki.html')
    table=html.fromstring(source.read_text(encoding='utf8')).xpath('//table[contains(@class,"wikitable")]')[2]
    rows=[];p=None
    provs={norm(r['provincia']):r['provincia'] for r in csv.DictReader(open(f'datos/base8399/ernesto/{y}_diputados/dpto_partidos.csv',encoding='utf-8-sig'))}
    provs.update({norm('Provincia de Buenos Aires'):'Buenos Aires',norm('San Luis'):'San Luis',norm('Santa Cruz'):'Santa Cruz',norm('Ciudad de Buenos Aires'):'Capital Federal'})
    for tr in table.xpath('./tr|./tbody/tr'):
        cells=tr.xpath('./td|./th')
        texts=[' '.join(' '.join(c.itertext()).split()) for c in cells]
        if not cells:continue
        if cells[0].tag=='th':
            for n,prov in provs.items():
                if n in norm(texts[0]) and ('Diputado' in texts[0] or 'diputado' in texts[0]):p=prov;break
        for i,text in enumerate(texts):
            if re.fullmatch(r'[\d.,]+',text) and i>0 and int(re.sub(r'\D','',text))>=10:
                name=texts[i-1]
                name=name.split('Ver partidos de la alianza:')[0].strip()
                rows.append(dict(provincia=p,nombre=name,votos=int(re.sub(r'\D','',text))))
                break
    Path(f'mapas/mapa{y}dip/wiki_prov_listas.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
    print(y)
    data=collections.defaultdict(collections.Counter)
    for r in csv.DictReader(open(f'datos/base8399/ernesto/{y}_diputados/dpto_partidos.csv',encoding='utf-8-sig')):
        if r['tipo_fila']=='agrupacion':data[r['provincia']][r['codigo_partido']]+=int(float(r['votos']))
    for p,cs in data.items():
        for c,v in cs.most_common():
            if v<20000:continue
            opts=[r for r in rows if r['provincia']==p and not any(x in r['nombre'].lower() for x in ['votos','registrad','participación','electores'])]
            if opts:
                best=min(opts,key=lambda r:abs(r['votos']-v))
                print(p,c,v,'->',best['nombre'][:90],best['votos'],best['votos']-v)
