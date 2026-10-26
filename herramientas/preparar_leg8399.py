from pathlib import Path
import requests, time, json
ROOT=Path(__file__).resolve().parents[1]
session=requests.Session()
session.headers['User-Agent']='DataeleccAtlas/1.0 (electoral research; contact: https://commons.wikimedia.org/wiki/User:ItsAHardLife)'
for year in (1983,1989,1995,1999):
    folder=ROOT/f'mapas/mapa{year}dip'; folder.mkdir(exist_ok=True)
    params=dict(action='parse',page=f'Elecciones legislativas de Argentina de {year}',prop='wikitext|text',format='json')
    out=folder/f'w{year}.json'
    if not out.exists():
        for n in range(5):
            r=session.get('https://es.wikipedia.org/w/api.php',params=params,timeout=60)
            if r.status_code==429: time.sleep(5*(n+1)); continue
            r.raise_for_status(); obj=r.json(); assert 'parse' in obj,obj
            out.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf8'); break
        else: raise RuntimeError(year)
    obj=json.loads(out.read_text(encoding='utf8'))['parse']
    (folder/f'w{year}.txt').write_text(obj['wikitext']['*'],encoding='utf8')
    (folder/'wiki.html').write_text(obj['text']['*'],encoding='utf8')
    import lxml.html
    soup=lxml.html.fromstring(obj['text']['*'])
    for i,t in enumerate(soup.xpath('//table[contains(@class,"wikitable")]')):
        text=' | '.join(x.strip() for x in t.itertext() if x.strip())
        (folder/f'table_{i}.txt').write_text(text,encoding='utf8')
        print(year,i,text[:200])
