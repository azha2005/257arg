"""Read-only audit of the uploaded atlas files and Wikipedia insertions."""
import hashlib
import json
import urllib.parse
import urllib.request
import urllib.error
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEYS = ['1983dip', '1985', '1987', '1989dip', '1991', '1993', '1994', '1995dip', '1997', '1999dip', '2001', '2001bronca']
UA = {'User-Agent': 'AtlasElectoral/1.0 (ItsAHardLife; Wikimedia Commons)'}

def api(host, **params):
    url = f'https://{host}/w/api.php?' + urllib.parse.urlencode(dict(format='json', **params))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise
            time.sleep(min(int(exc.headers.get('Retry-After', 5 * (attempt + 1))), 30))

files = [p for key in KEYS for p in sorted((ROOT/key/'subir').iterdir()) if p.suffix in ('.png', '.svg')]
checks = []
for start in range(0, len(files), 40):
    batch = files[start:start+40]
    result = api('commons.wikimedia.org', action='query', titles='|'.join('File:'+p.name for p in batch), redirects=1, prop='imageinfo', iiprop='sha1|timestamp|url', iiurlwidth=1280)
    query = result['query']
    pages = {p['title']: p for p in query['pages'].values()}
    aliases = {p['from']: p['to'] for p in query.get('redirects', [])}
    for p in batch:
        title = 'File:'+p.name
        target = aliases.get(title, title)
        page = pages.get(target, {})
        info = page.get('imageinfo', [{}])[0]
        same = info.get('sha1') == hashlib.sha1(p.read_bytes()).hexdigest()
        checks.append(dict(key=p.parent.parent.name, name=p.name, target=target, redirect=title!=target, same=same, thumbnail=info.get('thumburl'), url=info.get('descriptionurl')))
        print('IGUAL' if same else 'FALLO', p.parent.parent.name, p.name)

articles = []
years = list(range(1983, 2002, 2)) + [1994]
titles = [f'Elecciones legislativas de Argentina de {year}' if year != 1994 else 'Elecciones de convencionales constituyentes de Argentina de 1994' for year in years]
(ROOT/'auditoria_archivos_20261020.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
result = api('es.wikipedia.org', action='query', titles='|'.join(titles), prop='revisions', rvprop='ids|timestamp|content', rvslots='main')
pages = {p['title']: p for p in result['query']['pages'].values()}
for year, title in zip(years, titles):
    page = pages[title]
    rev = page['revisions'][0]
    text = rev['slots']['main']['*']
    source = (ROOT/'articulos_20261020'/f'{year}.wiki').read_text(encoding='utf-8')
    import re
    previous = re.search(r'^\|\s*mapa\s*=([^\n]*)', source, re.M)
    previous = previous.group(1).strip() if previous else ''
    checks_article = dict(year=year, title=title, revid=rev['revid'], url=f'https://es.wikipedia.org/w/index.php?title={urllib.parse.quote(title)}&oldid={rev["revid"]}', section='== Resultados por departamento ==' in text, previous_map_preserved=not previous or f'[[{previous}|300px]]' in text, main='Resultados por departamento (con leyenda).svg' in text, switcher='{{Switcher' in text, bronca_below=year!=2001 or text.index('(voto bronca)') > text.index('== Resultados por departamento ==') if '(voto bronca)' in text else year!=2001)
    articles.append(checks_article)
    (ROOT/'articulos_20261020'/f'{year}_publicado.wiki').write_text(text, encoding='utf-8')
    print('ARTICLE', year, checks_article)
report = dict(files=checks, articles=articles)
(ROOT/'auditoria_publicacion_20261020.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('FILES', len(checks), 'MATCH', sum(c['same'] for c in checks), 'REDIRECTS', sum(c['redirect'] for c in checks))
