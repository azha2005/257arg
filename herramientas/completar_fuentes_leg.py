"""Complementos oficiales y logos faltantes; reintentos pausados ante HTTP 429."""
from pathlib import Path
import json,re,time,urllib.request,urllib.parse,urllib.error,shutil
from fuentes_leg2003_2025 import api,UA,OUT,ROOT

def filename(title):return re.sub(r'[<>:"/\\|?*]','',title.replace(' ','_'))

if __name__=='__main__':
    pages=json.loads((OUT/'logos_metadata.json').read_text(encoding='utf8'))
    articles=['Juntos Somos Río Negro','Chubut Somos Todos','Somos Energía para Renovar Santa Cruz','La Neuquinidad','Producción y Trabajo','Partido Agrario y Social','Primero Jujuy','Frente Cívico y Social de Catamarca','Frente Cívico de Córdoba','Partido Unidad Federalista','Partido Demócrata Cristiano (Argentina)','Fuerza Republicana','Partido Federal Fueguino']
    ap=OUT/'logos_regionales_articulos.json'
    if ap.exists():art=json.loads(ap.read_text(encoding='utf8'))
    else:
        art=api(action='query',titles='|'.join(articles),prop='pageimages',piprop='name',redirects=1)
        ap.write_text(json.dumps(art,ensure_ascii=False,indent=2),encoding='utf8')
    titles=['File:'+p['pageimage'] for p in art.get('query',{}).get('pages',{}).values() if p.get('pageimage')]
    titles+=['File:Logo JSRN Argentina.svg','File:Logo_FPCyS.png']
    d=api(host='commons.wikimedia.org',action='query',titles='|'.join(titles),prop='imageinfo',iiprop='url|extmetadata',redirects=1)
    pages.update(d.get('query',{}).get('pages',{}))
    (OUT/'logos_metadata.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf8')
    # PDFs definitivos: se preserva también cualquier error HTTP en el registro.
    urls={
      'la_pampa_2005.pdf':'https://www.argentina.gob.ar/sites/default/files/la_pampa_23_de_octubre_de_2005.pdf',
      'la_pampa_2003.pdf':'https://www.argentina.gob.ar/sites/default/files/la_pampa_26_de_octubre_de_2003.pdf',
      'jujuy_2005.pdf':'https://www.argentina.gob.ar/sites/default/files/jujuy_23_de_octubre_de_2005.pdf',
      'jujuy_2007.pdf':'https://www.argentina.gob.ar/sites/default/files/jujuy_28_de_octubre_de_2007.pdf',
      'buenos_aires_2003.pdf':'https://www.argentina.gob.ar/sites/default/files/buenos_aires_14_de_septiembre_de_2003.pdf',
    }
    for name,url in urls.items():
        dest=OUT/name
        if dest.exists():continue
        try:
            data=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=35).read()
            if data.startswith(b'%PDF'):dest.write_bytes(data);print('PDF OK',name,flush=True)
            else:print('NO PDF',name,flush=True)
        except Exception as e:print('PDF FAILED',name,str(e),flush=True)
    for p in pages.values():
        if not p.get('imageinfo') or p['title'].endswith('HSSamarbete.svg'):continue
        name=p['title'][5:];dest=OUT/'logos'/filename(name)
        if dest.exists():continue
        local=ROOT/'../logos'/filename(name)
        if local.exists():shutil.copy2(local,dest);continue
        url=p['imageinfo'][0]['url'].split('?')[0]
        for attempt in range(3):
            try:
                time.sleep(4 if attempt==0 else 15)
                data=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40).read()
                dest.write_bytes(data);print('LOGO OK',name,flush=True);break
            except Exception as e:print('LOGO RETRY',attempt,name,str(e),flush=True)
