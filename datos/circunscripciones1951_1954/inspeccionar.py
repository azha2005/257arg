from pathlib import Path
from lxml import html
from urllib.parse import unquote
import requests, json, time
HERE = Path(__file__).resolve().parent
s = requests.Session()
s.headers['User-Agent'] = 'AtlasElectoral/1.0 (research cartography)'
for year in (1951, 1954):
    t = html.fromstring((HERE / f'wiki{year}.html').read_text(encoding='utf8'))
    print(year, [(i,len(x.xpath('./tbody/tr|./tr')),x.text_content()[:100].replace('\n',' ')) for i,x in enumerate(t.xpath('//table')) if len(x.xpath('./tbody/tr|./tr'))>1])
    if year == 1951:
        urls = [u for u in t.xpath('//img/@src') if 'Mapa_de_las_elecciones_legislativas' in u]
        print('\n'.join(unquote(u) for u in urls[:3]))
        url='https:'+urls[0]
        url=url.replace('thumb.wikimedia.org','upload.wikimedia.org').replace('/thumb/','/').rsplit('/',1)[0]
        redirect='https://commons.wikimedia.org/wiki/Special:Redirect/file/'+unquote(url.rsplit('/',1)[-1])
        for attempt in range(4):
            r=s.get(redirect,timeout=30)
            if r.status_code!=429: break
            time.sleep(5*(attempt+1))
        r.raise_for_status()
        assert b'<svg' in r.content
        (HERE/'circunscripciones_1951.svg').write_bytes(r.content)
        print('SVG',len(r.content),url)
        title='File:'+unquote(url.rsplit('/',1)[-1]).replace('_',' ')
        r=s.get('https://commons.wikimedia.org/w/api.php',params=dict(action='query',format='json',titles=title,prop='imageinfo',iiprop='url|extmetadata'),timeout=30)
        (HERE/'commons1951.json').write_bytes(r.content)
