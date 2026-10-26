from lxml import html
from pathlib import Path
import re,json
for y in [1983,1989,1995,1999]:
    t=html.fromstring(Path(f'mapas/mapa{y}dip/wiki.html').read_text(encoding='utf8')).xpath('//table[contains(@class,"wikitable")]')[1]
    print(y)
    out=[]
    for row in t.xpath('./tr|./tbody/tr'):
        cells=[' '.join(' '.join(c.itertext()).split()) for c in row.xpath('./td|./th')]
        print(' | '.join(cells[:4]))
        out.append(cells)
    Path(f'mapas/mapa{y}dip/wiki_rows.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
