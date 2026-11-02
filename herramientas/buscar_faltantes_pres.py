"""Registro de búsquedas públicas de faltantes presidenciales; no consulta la CNE con captcha."""
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import json, re, sys
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'datos/fuentes_leg2003_2025/presidenciales/busqueda_faltantes'
OUT.mkdir(exist_ok=True)

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a': self.links.append(d)

def get(item):
    name,url=item
    try:
        r=requests.get(url,timeout=25,headers={'User-Agent':'AtlasElectoral-dataeleccproyecto/1.0 (investigacion historica individual)'})
        (OUT/name).write_bytes(r.content)
        result=dict(archivo=name,url=url,status=r.status_code,bytes=len(r.content))
        if name.endswith('.html'):
            p=Links();p.feed(r.text)
            result['enlaces']=[d for d in p.links if any(q in str(d).lower() for q in ('2023','2015','acta','definitiv','escrut'))]
            result['contexto']=[re.sub(r'\s+',' ',r.text[max(0,m.start()-150):m.end()+180]) for m in re.finditer('Actas de escrutinio|Consulta del escrutinio',r.text,re.I)]
        elif name.endswith('.json'): result['respuesta']=r.text[:9000]
        return result
    except Exception as e:return dict(archivo=name,url=url,error=str(e))

if sys.argv[1:] == ['exportaciones']:
    import pandas as pd
    target={('03','014'),('07','004'),('07','011'),('07','015'),('10','008'),('10','016'),('11','006'),('17','022')}
    for p in Path('C:/Users/JC/Downloads').glob('presentacionDeResultados*.csv'):
        try:
            d=pd.read_csv(p,dtype=str,usecols=lambda c:c in ('año','eleccion_tipo','distrito_id','seccion_id','votos_tipo','votos_cantidad'),encoding='utf8')
            selected=d[d.votos_tipo=='POSITIVO']
            found=[(di,se,int(pd.to_numeric(g.votos_cantidad).sum())) for (di,se),g in selected.groupby([selected.distrito_id.str.zfill(2),selected.seccion_id.str.zfill(3)]) if (di,se) in target]
            print(p.name,len(d),d['año'].unique(),d.eleccion_tipo.unique(),found,flush=True)
        except Exception as e:print(p.name,str(e),flush=True)
    exit()
if sys.argv[1:] == ['archivos-locales']:
    import xlrd, hashlib
    inventory=[]
    for f in Path('C:/Users/JC/Downloads').glob('zona*.xls'):
        s=xlrd.open_workbook(str(f),ignore_workbook_corruption=True).sheet_by_index(0)
        rs=[s.row_values(i) for i in range(min(s.nrows,14))]
        relevant=[r for r in rs if any(t in str(r) for t in ('FECHA ELECCION','Distrito:','Secci','Localidad'))]
        inventory.append(dict(archivo=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),encabezado=relevant,
                              cargos=next((r for r in rs if r[0]=='NRO'),[])))
        print(f.name,relevant)
    (OUT/'inventario_xls_descargas.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
    exit()

if sys.argv[1:] == ['actas2023']:
    import pymupdf, unicodedata
    from urllib.parse import quote
    def pdf(prov):
        url='https://www.electoral.gov.ar/nuevo/paginas/pdf/actas_escrutinio/2023/SEGUNDA%20VUELTA/'+quote(prov)+'.pdf'
        x=get((prov.replace(' ','_')+'_2023bal.pdf',url))
        if x.get('status')==200:
            d=pymupdf.open(OUT/x['archivo'])
            x['paginas']=len(d); x['texto_caracteres']=sum(len(p.get_text()) for p in d)
            x['paginas_departamentos']=[(i+1,p.get_text()[:240]) for i,p in enumerate(d)
                if any(n in unicodedata.normalize('NFKD',p.get_text()).encode('ascii','ignore').decode().upper()
                       for n in ('SARMIENTO','ANTOFAGASTA','SANTA VICTORIA','VALLE GRANDE','SUSQUES','CURACO','GASTRE','TELSEN','AMEGHINO'))]
            (OUT/(prov.replace(' ','_')+'_2023bal.txt')).write_text('\n'.join(f'PAGINA {i+1}\n'+p.get_text() for i,p in enumerate(d)),encoding='utf8')
        return x
    res=list(ThreadPoolExecutor(max_workers=3).map(pdf,['CATAMARCA','CHUBUT','JUJUY','LA PAMPA','SALTA']))
    (OUT/'actas2023_fuentes.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8')
    for x in res: print(json.dumps(x,ensure_ascii=False),flush=True)
    exit()

urls=[
 ('cne2023.html','https://www.electoral.gov.ar/nuevo/paginas/btn/elecc2023.php'),
 ('archivo_santiago2007.json','https://web.archive.org/cdx/search/cdx?url=www.elecciones.gob.ar/estadistica/archivos/2007/&matchType=prefix&output=json&filter=statuscode:200&filter=original:.*[Ss]antiago.*&collapse=urlkey'),
 ('archivo_sgo2007.json','https://web.archive.org/cdx/search/cdx?url=www.elecciones.gob.ar/estadistica/archivos/2007/&matchType=prefix&output=json&filter=statuscode:200&filter=original:.*[Ee]stero.*&collapse=urlkey'),
]
if __name__=='__main__':
    result=list(ThreadPoolExecutor(max_workers=3).map(get,urls))
    (OUT/'registro.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    for x in result: print(json.dumps(x,ensure_ascii=False),flush=True)
