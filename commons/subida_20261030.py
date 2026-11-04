"""Read-only Commons inventory and local queue for browser uploads."""
import collections
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'publicacion_20261030'
OUT.mkdir(exist_ok=True)
HOLD = {'2013paso', '2015paso', '2015pasodip'}
UA = {'User-Agent': 'atlas-electoral-argentina/1.0 (https://commons.wikimedia.org/wiki/User:ItsAHardLife)'}

def api(**params):
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(dict(format='json', **params))
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 502, 503, 504) or attempt == 4:
                raise
            time.sleep(min(int(exc.headers.get('Retry-After', 5*(attempt+1))), 30))

def inventory():
    rows = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or not re.fullmatch(r'20(?:0[3-9]|1[0-9]|2[0-5])(?:paso(?:dip)?)?', d.name):
            continue
        readme = (d/'LEEME_SUBIDA.md').read_text(encoding='utf-8')
        # Explicit user instruction on 30-Oct: upload every logo-bearing version.
        logo_hold = False
        for p in sorted((d/'subir').iterdir()):
            if p.suffix not in ('.svg', '.png'):
                continue
            reason = ('Atlas en espera por faltantes' if d.name in HOLD else
                      'Versiones con logos en espera' if logo_hold and not any(v in p.name for v in ('(solo mapa)', '(con leyenda y siglas)', '(siglas)')) else '')
            text = Path(str(p)+'.txt').read_text(encoding='utf-8')
            assert '{{Cc-by-2.5-ar}}' in text and re.search(r'\{\{self\|cc-by(?:-sa)?-4.0\}\}', text), p
            rows.append(dict(key=d.name, name=p.name, path=str(p.resolve()), sha1=hashlib.sha1(p.read_bytes()).hexdigest(), eligible=not reason, reason=reason, description=text))
    return rows

def check(rows):
    for start in range(0, len(rows), 40):
        batch = rows[start:start+40]
        query = api(action='query', titles='|'.join('File:'+r['name'] for r in batch), redirects=1, prop='imageinfo', iiprop='sha1|timestamp|url', iiurlwidth=1280, maxage=0, smaxage=0, requestid=str(time.time_ns()))['query']
        pages = {p['title']: p for p in query['pages'].values()}
        aliases = {r['from']: r['to'] for r in query.get('redirects', [])}
        normalized = {r['from']: r['to'] for r in query.get('normalized', [])}
        for row in batch:
            title = normalized.get('File:'+row['name'], 'File:'+row['name'])
            target = aliases.get(title, title)
            info = pages.get(target, {}).get('imageinfo', [{}])[0]
            row['remote'] = dict(target=target, sha1=info.get('sha1'), timestamp=info.get('timestamp'), thumbnail=info.get('thumburl'), url=info.get('descriptionurl'))
            row['status'] = 'IGUAL' if info.get('sha1') == row['sha1'] else 'DISTINTO' if info.get('sha1') else 'NO SUBIDO'
        print('Checked', min(start+40, len(rows)), '/', len(rows), flush=True)

def plan(rows):
    eligible = [r for r in rows if r['eligible']]
    order = lambda r: (r['key'], 0 if ' - Resultados por departamento ' in r['name'] else 1,
                       0 if '(solo mapa)' in r['name'] else 1, r['name'])
    same = {r['sha1']: r for r in eligible if r['status'] == 'IGUAL'}
    queue, aliases = [], []
    for row in sorted(eligible, key=order):
        if row['status'] == 'IGUAL':
            row['action'] = 'EXISTENTE IGUAL'
        elif row['status'] == 'DISTINTO':
            row['action'] = 'REVISAR NUEVA VERSION'
            queue.append(row)
            same[row['sha1']] = row
        elif row['sha1'] in same:
            row['action'] = 'REDIRECCION'
            row['alias'] = same[row['sha1']]['name']
            aliases.append(row)
        else:
            row['action'] = 'SUBIR'
            queue.append(row)
            same[row['sha1']] = row
    return queue, aliases

def write_manifest(queue, aliases):
    for i in range(0, len(queue), 10):
        data = json.dumps(queue[i:i+10], ensure_ascii=False)
        (OUT/f'cola_{i//10:03}.html').write_text('<!doctype html><meta charset=utf-8><pre>'+html.escape(data)+'</pre>', encoding='utf-8')
    (OUT/'aliases.html').write_text('<!doctype html><meta charset=utf-8><pre>'+html.escape(json.dumps(aliases, ensure_ascii=False))+'</pre>', encoding='utf-8')

if __name__ == '__main__':
    import sys
    rows = inventory()
    if '--through2015' in sys.argv:
        rows = [r for r in rows if int(r['key'][:4]) <= 2015]
    check(rows)
    queue, aliases = plan(rows)
    name = 'final' if '--final' in sys.argv else 'inicial'
    (OUT/f'{name}.json').write_text(json.dumps(dict(files=rows, queue=queue, aliases=aliases), ensure_ascii=False, indent=2), encoding='utf-8')
    if name == 'inicial':
        write_manifest(queue, aliases)
    for key in dict.fromkeys(r['key'] for r in rows):
        fs = [r for r in rows if r['key']==key]
        print(key, dict(collections.Counter((r.get('action', 'EN ESPERA') if r['eligible'] else r['reason']) for r in fs)))
    print('ELIGIBLE',sum(r['eligible'] for r in rows),'QUEUE',len(queue),'ALIASES',len(aliases),'EXISTING',sum(r['eligible'] and r['status']=='IGUAL' for r in rows))
