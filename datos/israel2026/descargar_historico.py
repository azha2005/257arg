"""Descarga los recursos oficiales CKAN disponibles, conservando respuestas originales."""
import csv
import hashlib
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
API = 'https://data.gov.il/api/3/action/'
s = requests.Session()
s.headers['User-Agent'] = 'DataeleccProyecto research data archive (contact: data.gov.il publisher)'

def get(action, params):
    r = s.get(API + action, params=params, timeout=90)
    r.raise_for_status()
    obj = r.json()
    if not obj.get('success'):
        raise ValueError(str(obj.get('error')))
    return obj

package = get('package_show', {'id': 'votes-knesset'})
(ROOT / 'catalogo_ckan.json').write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding='utf-8')
out = ROOT / 'historico_ckan'
out.mkdir(exist_ok=True)
manifest = []
for resource in package['result']['resources']:
    rid = resource['id']
    item = {'id': rid, 'nombre': resource.get('name'), 'url': resource.get('url')}
    try:
        offset = 0
        rows = []
        fields = None
        while True:
            page = get('datastore_search', {'resource_id': rid, 'limit': 5000, 'offset': offset})['result']
            fields = page['fields']
            records = page['records']
            rows.extend(records)
            offset += len(records)
            if not records or offset >= page['total']:
                break
        if len(rows) != page['total']:
            raise ValueError('incomplete dataset')
        path = out / (rid + '.json')
        path.write_text(json.dumps({'resource': resource, 'fields': fields, 'total': page['total'], 'records': rows}, ensure_ascii=False), encoding='utf-8')
        item.update(archivo=str(path.relative_to(ROOT)), filas=len(rows), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    except Exception as e:
        item['error'] = str(e)
    manifest.append(item)
    print(json.dumps(item, ensure_ascii=False), flush=True)
    (ROOT / 'inventario.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
