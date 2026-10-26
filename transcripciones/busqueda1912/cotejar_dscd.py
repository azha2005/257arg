"""Consulta pública del tomo DSCD 1912; conserva respuestas sin inferir cifras."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import csv,hashlib,json
P=Path(__file__).resolve().parent
rows=[]
for term in ['Mendoza elecciones','Mendoza votos','San Martín','Benegas','La Rioja','Jujuy']:
    url='https://books.google.com/books?'+urlencode(dict(jscmd='SearchWithinVolume2',q=term,vid='VrxHAQAAMAAJ'))
    name='dscd_1912_'+str(len(rows))+'.json'
    try:
        with urlopen(Request(url,headers={'User-Agent':'Historical-election-research/1.0'}),timeout=45) as r:
            raw=r.read();enc=r.headers.get_content_charset() or 'latin-1'
        decoded=raw.decode(enc)
        (P/'fuentes'/name).write_text(decoded,encoding='utf-8')
        obj=json.loads(decoded)
        print(term,json.dumps(obj,ensure_ascii=False)[:11000])
        rows.append(dict(url=url,archivo=name,fecha_consulta='2026-10-15',tamano=len(raw),sha256_descarga=hashlib.sha256(raw).hexdigest(),estado='Respuesta de búsqueda interna, NO imagen de página ni transcripción de votos'))
    except Exception as e:
        rows.append(dict(url=url,archivo='',fecha_consulta='2026-10-15',tamano='',sha256_descarga='',estado=str(e)))
with (P/'fuentes'/'dscd_consultas.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
