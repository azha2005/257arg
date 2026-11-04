from pathlib import Path
import re,json,requests,zipfile,io
from urllib.parse import urljoin,urlparse,unquote
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
found=[]
for year in [2010,2022]:
    text=(META/f'ipec_plantas{year}.txt').read_text(encoding='utf-8')
    urls=sorted(set(urljoin('https://www.santafe.gov.ar',s) for s in re.findall(r'(?:href|src)=["\x27]([^"\x27]+)',text) if '.zip' in s.lower()))
    found.extend(dict(anio=year,url=u,archivo='santafe/ipec/'+str(year)+'/'+unquote(urlparse(u).path.split('/')[-1])) for u in urls)
    print(year,len(urls),flush=True)
    r=requests.get(urls[0],timeout=30)
    z=zipfile.ZipFile(io.BytesIO(r.content))
    print('MUESTRA',len(r.content),z.namelist()[:30],flush=True)
    for n in z.namelist():
        if n.lower().endswith('metadatos.zip'):
            sub=zipfile.ZipFile(io.BytesIO(z.read(n)))
            for name in sub.namelist():
                if name.lower().endswith(('.txt','.doc','.pdf')):
                    data=sub.read(name);(META/f'ipec_muestra_{year}_{Path(name).name}').write_bytes(data)
                    if name.lower().endswith('.txt'):print(data.decode('latin1',errors='replace')[:3500],flush=True)
(META/'ipec_enlaces.json').write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf-8')
planpath=ROOT/'plan_descargas.json';plan=json.loads(planpath.read_text(encoding='utf-8'))
import hashlib
for row in found:
    ident='ipec_'+str(row['anio'])+'_'+hashlib.sha256(row['url'].encode()).hexdigest()[:10]
    if not any(r['id']==ident for r in plan):
        plan.append(dict(id=ident,url=row['url'],archivo=row['archivo'],tipo='cartografía urbana IPEC',corte=str(row['anio']),cobertura='Santa Fe: planta urbana de localidad',fuente='https://www.estadisticasantafe.gob.ar/contenido/cartografia-censal/',nota='Archivo enlazado por portal IPEC bajo año censal. Incluye radios, manzanas y ejes. Conservar metadatos internos; no constituye ejido municipal.',licencia='Consultar metadatos internos IPEC; no asumir licencia de otra colección.'))
planpath.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('PLAN',len(plan),flush=True)
