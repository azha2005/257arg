"""Read current articles and prepare browser-reviewed edits; no API writes."""
import sys, json, re, html, difflib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from subida_20261030 import UA
import urllib.request, urllib.parse, time
def api(**params):
    url='https://es.wikipedia.org/w/api.php?'+urllib.parse.urlencode(dict(format='json',**params))
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=45) as r:
                return json.load(r)
        except Exception:
            if attempt==4: raise
            time.sleep(5)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'articulos_20261030'
OUT.mkdir(exist_ok=True)
YEARS=list(range(2003,2026,2))
TITLES=[f'Elecciones legislativas de Argentina de {y}' for y in YEARS]+[f'Elecciones primarias de Argentina de {y}' for y in [2011,2017,2019,2021,2023]]
if __name__=='__main__':
    for i,title in enumerate(TITLES):
        q=api(action='query',titles=title,prop='revisions',rvprop='ids|timestamp|content',rvslots='main',maxage=0,smaxage=0)
        page=next(iter(q['query']['pages'].values()))
        rev=page['revisions'][0]
        text=rev['slots']['main']['*']
        (OUT/f'{i:02}.json').write_text(json.dumps(dict(title=title,revid=rev['revid'],timestamp=rev['timestamp'],original=text),ensure_ascii=False,indent=2),encoding='utf8')
        (OUT/f'{i:02}_original.wiki').write_text(text,encoding='utf8')
        fields=re.findall(r'^\|\s*(?:mapa\w*|leyenda_mapa\w*|nombre_elección|nombre_eleccion)\s*=.*',text,re.M)
        heads=re.findall(r'^==+[^\n]+',text,re.M)
        print(i,title,rev['revid'], '\n'+'\n'.join(fields)+'\n'+' / '.join(heads),flush=True)
