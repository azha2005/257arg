"""Descarga pública y registro reproducible de los localizadores de expedientes buscados."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import csv, datetime, urllib.request, time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'fuentes'
OUT.mkdir(exist_ok=True)
SOURCES = [('Capital Federal','13-d-1914'),('Catamarca','42-d-1914'),('Córdoba','26-p-1914'),('Corrientes','21-d-1914'),('Entre Ríos','19-d-1914'),('Jujuy','23-p-1914'),('La Rioja','13-p-1914'),('Mendoza','29-p-1914'),('Salta','27-p-1914'),('San Juan','19-p-1914'),('Santa Fe','27-d-1914'),('Santiago del Estero','18-p-1914'),('Tucumán','343-d-1914'),('Tucumán','12-d-1915'),('Tucumán','5-d-1915')]

def fetch(item):
    province, ident = item
    url = f'https://apym.hcdn.gob.ar/uploads/expedientes/pdf/{ident}.pdf'
    file = OUT / f'{province.lower().replace(" ","_")}_{ident}.pdf'
    errors=[]
    for attempt in range(2):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'AtlasElectoralResearch/1.0 (public historical research; contact: https://commons.wikimedia.org/wiki/User:ItsAHardLife)' if attempt==0 else 'Mozilla/5.0 (compatible; ElectoralHistoricalResearch/1.0)'})
            with urllib.request.urlopen(req, timeout=22) as response:
                data=response.read()
            if not data.startswith(b'%PDF'):
                raise ValueError(f'No es PDF: {data[:60]!r}')
            file.write_bytes(data)
            status='descargado; contenido pendiente de inspección'
            print(ident, len(data), flush=True)
            return dict(fuente_id=ident,provincia=province,url=url,fecha_consulta='2026-10-15',tamano_bytes=len(data),estado=status,archivo=str(file.relative_to(ROOT)),detalle='')
        except Exception as e:
            errors.append(f'intento {attempt+1}: {type(e).__name__}: {e}')
            if attempt==0: time.sleep(1)
    print(ident, 'FALLO', flush=True)
    return dict(fuente_id=ident,provincia=province,url=url,fecha_consulta='2026-10-15',tamano_bytes=0,estado='no recuperado',archivo='',detalle=' | '.join(errors))

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=5) as pool:
        rows=list(pool.map(fetch,SOURCES))
    with (ROOT/'fuentes_hcdn.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
