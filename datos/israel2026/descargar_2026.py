"""Guardar instantáneas CSV oficiales cuando el servidor las entregue."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import requests

root = Path(__file__).resolve().parent
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
for name in ('expc.csv', 'expb.csv'):
    url = 'https://media26.bechirot.gov.il/files/' + name
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.content
        if len(data) < 100 or b'<html' in data[:1000].lower() or b'<!doctype' in data[:1000].lower():
            raise ValueError('La respuesta no parece un archivo CSV de resultados')
        dest = root / 'instantaneas' / stamp
        dest.mkdir(parents=True, exist_ok=True)
        (dest / name).write_bytes(data)
        meta = {'url': url, 'utc': stamp, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'content_type': r.headers.get('content-type')}
        (dest / (name + '.json')).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
        print(name, 'guardado:', len(data), 'bytes; verificar contenido y carácter provisional')
    except (requests.RequestException, ValueError) as e:
        print(name, 'no descargado:', str(e))
