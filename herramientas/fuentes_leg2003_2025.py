"""Descarga instantáneas y metadatos de Wikipedia/Commons para los atlas solicitados."""
from pathlib import Path
import json, re, urllib.request, urllib.parse, time, sys, hashlib, os
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'../datos/fuentes_leg2003_2025'
OUT.mkdir(exist_ok=True)
UA={'User-Agent':'AtlasElectoralArgentina/1.0 (%s)' % os.environ.get("ATLAS_CONTACT", "sin contacto; definir ATLAS_CONTACT")}

def api(host='es.wikipedia.org',**params):
    params['format']='json'
    url='https://'+host+'/w/api.php?'+urllib.parse.urlencode(params)
    for n in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=45))
        except Exception:
            if n==4: raise
            time.sleep(3*(n+1))

if __name__=='__main__':
    colors=set(); images=set(); articles={}
    for y in range(2003,2026,2):
        p=OUT/f'wleg{y}.json'
        if not p.exists():
            d=api(action='parse',page=f'Elecciones legislativas de Argentina de {y}',prop='wikitext|revid')
            p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
        d=json.loads(p.read_text(encoding='utf8'))
        t=d['parse']['wikitext']['*']
        (OUT/f'wleg{y}.txt').write_text(t,encoding='utf8')
        colors.update(re.findall(r'\{\{Color político\|([^}|]+)',t,re.I))
        imgs=re.findall(r'^\s*\|\s*imagen\d*\s*=\s*(.*?)\s*$',t,re.M)
        imgs=[re.sub(r'^(?:Archivo|File|Imagen):','',i).strip() for i in imgs if i and '{{' not in i]
        images.update(imgs)
        articles[y]={'revid':d['parse'].get('revid'),'logos_infobox':imgs,'sha256':hashlib.sha256(t.encode()).hexdigest()}
        print(y,'logos',imgs,flush=True)
    cp=OUT/'colores.json'
    if not cp.exists():
        cs=sorted(colors)
        resolved={}
        for n in range(0,len(cs),20):
            batch=cs[n:n+20]
            d=api(action='expandtemplates',text='@@@'.join('{{Color político|'+c+'}}' for c in batch),prop='wikitext')
            resolved.update(zip(batch,d['expandtemplates']['wikitext'].split('@@@')))
        cp.write_text(json.dumps(resolved,ensure_ascii=False,indent=2),encoding='utf8')
    extra=['Logo Cambiemos.svg','Cambiemos logo.png','Logo Juntos por el Cambio.svg','Logo Frente de Todos.svg','Unión por la Patria logo.svg']
    images.update(extra)
    titles=['File:'+i for i in sorted(images)]
    pages={}
    for n in range(0,len(titles),35):
        d=api(host='commons.wikimedia.org',action='query',titles='|'.join(titles[n:n+35]),prop='imageinfo',iiprop='url|extmetadata',redirects='1')
        pages.update(d.get('query',{}).get('pages',{}))
    (OUT/'logos_metadata.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'articulos.json').write_text(json.dumps(articles,ensure_ascii=False,indent=2),encoding='utf8')
    dl=OUT/'logos';dl.mkdir(exist_ok=True)
    for p in pages.values():
        if not p.get('imageinfo'): continue
        fn=p['title'][5:].replace(' ','_')
        dest=dl/fn
        if not dest.exists():
            u=p['imageinfo'][0]['url'].split('?')[0]
            try:
                dest.write_bytes(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=45).read())
            except Exception as e: print('DOWNLOAD FAILED',fn,str(e),flush=True)
    print('descarga finalizada',flush=True)
