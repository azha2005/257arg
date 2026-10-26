import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
files = sorted((root / 'subir').glob('* (con leyenda).svg'))
params = {'action': 'query', 'format': 'json', 'prop': 'imageinfo',
          'iiprop': 'sha1|timestamp|url',
          'titles': '|'.join('File:' + f.name for f in files)}
url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={'User-Agent': 'Commons1928Verification/1.0 (ItsAHardLife; local file verification)'})
with urllib.request.urlopen(req, timeout=45) as response:
    data = json.load(response)
pages = {p['title'].replace('_', ' '): p for p in data['query']['pages'].values()}
results = []
for file in files:
    local = hashlib.sha1(file.read_bytes()).hexdigest()
    info = pages['File:' + file.name]['imageinfo'][0]
    results.append({'file': file.name, 'local_sha1': local,
                    'commons_sha1': info['sha1'], 'match': local == info['sha1'],
                    'timestamp': info['timestamp'], 'url': info['url']})
out = root / 'verificacion_subida' / 'sha1_con_leyenda.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(results, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(r['match'] for r in results) else 1)
