"""Guarda metadatos de Commons y los emblemas usados por el artículo de 2009."""
from pathlib import Path
import requests, json, time, os
ROOT=Path(__file__).resolve().parent.parent
FILES={
 'ACyS':'Acuerdo Cívico y Socia.png',
 'FPV':'Logo Frente para la Victoria.svg',
 'PRO':'Union Pro.png',
 'PF':'Flag of the Justicialist Party (square version).svg',
 'SUR':'Proyectosur logo.png',
 'NE':'Nuevo Encuentro (small).png',
 'FRC':'Frente Renovador de la Concordia Social.png',
 'MPN':'Logo MPN.png',
 'UdN':'Logo Frente Grande.png',
}
s=requests.Session();s.trust_env=False
s.headers['User-Agent']='atlas-electoral-argentina/1.0 (%s)' % os.environ.get("ATLAS_CONTACT", "sin contacto; definir ATLAS_CONTACT")
params=dict(action='query',format='json',prop='imageinfo',iiprop='url|extmetadata',titles='|'.join('File:'+n for n in FILES.values()))
for i in range(4):
    r=s.get('https://commons.wikimedia.org/w/api.php',params=params,timeout=45)
    if r.status_code!=429: break
    time.sleep(3*(i+1))
r.raise_for_status();data=r.json()
(ROOT/'mapa2009/logos_metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
for p in data['query']['pages'].values():
    ii=p.get('imageinfo',[{}])[0]; meta=ii.get('extmetadata',{})
    title=p['title'][5:]
    print(title,'| fecha:',meta.get('DateTimeOriginal',{}).get('value'),'| licencia:',meta.get('LicenseShortName',{}).get('value'),'| missing:', 'missing' in p)
    if 'url' not in ii: continue
    target=ROOT/'../logos'/title.replace(' ','_')
    if not target.exists():
        rr=s.get(ii['url'],timeout=40);rr.raise_for_status();target.write_bytes(rr.content)
