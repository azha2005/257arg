"""Descarga y conserva las fuentes originales públicas del piloto provincial."""
from pathlib import Path
import concurrent.futures as cf
import hashlib
import json
import requests

HERE = Path(__file__).resolve().parent
RAW = HERE / 'fuentes'
RAW.mkdir(exist_ok=True)
RN = 'https://www.jusrionegro.gov.ar/inicio/web/escrutinio-16-04-2023/'
SA = 'https://www.electoralsalta.gov.ar/'
URLS = {
    'rn_ubicaciones.json': RN + 'metadata/ubicaciones.json',
    'rn_total.json': RN + 'resultados/RN/GOB.json',
    'rn_meta.json': RN + 'metadata/RN/meta.json',
    'salta_total.json': SA + 'JSON/Escrutinio/2023G/1/0.json',
    'salta_departamentos.json': SA + 'JSON/departamentos.json',
    'salta_municipios.json': SA + 'JSON/municipios.json',
    'salta_2023.xlsx': SA + 'Elecciones/Escrutinio/Escrutinio-2023G.xlsx',
    'neuquen_mesas.pdf': 'https://intranet.jusneuquen.gov.ar/images2/Electoral/CP_16-04-2023/escrutinio_def/Escrutinio_DefinitivoxMesas_2023.pdf',
    'misiones_municipios.pdf': 'https://www.electoralmisiones.gov.ar/wp-content/uploads/2023/05/Acta-Acuerdo-N%C2%B01166-Anexo-I.pdf',
}


def descargar(item):
    name, url = item
    out = RAW / name
    if not out.exists():
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        out.write_bytes(r.content)
    data = out.read_bytes()
    return dict(archivo=name, url=url, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


if __name__ == '__main__':
    manifest = []
    with cf.ThreadPoolExecutor(4) as pool:
        futs = {pool.submit(descargar, item): item[0] for item in URLS.items()}
        for f in cf.as_completed(futs):
            try:
                item = f.result()
                manifest.append(item)
                print(item['archivo'], item['bytes'], flush=True)
            except Exception as e:
                print(futs[f], type(e).__name__, str(e), flush=True)
    (RAW / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf8')
