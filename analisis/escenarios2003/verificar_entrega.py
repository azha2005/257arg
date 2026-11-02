"""Integridad de los HTML y de las exportaciones finales de esta entrega."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'mapas/mapa2003escenarios'
manifest=json.loads((OUT/'manifiesto.json').read_text(encoding='utf8'))
assert len(manifest)==18
for item in manifest:
    p=OUT/item['html']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],p


class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links.append(dict(attrs)['href'])


links=Links();links.feed((OUT/'index.html').read_text(encoding='utf8'))
for link in links.links:
    if not link.startswith('http'):assert (OUT/link).exists(),link
images=[]
for item in manifest:
    html=OUT/item['html']
    for mode in ['gan','voto','margen']:
        name=html.stem+'_'+mode+'.png'
        transparent=ROOT/'png_transparentes/mapa2003escenarios'/name
        white=ROOT/'png_blanco/mapa2003escenarios'/name
        copy=ROOT/'png_transparentes/all elections white bg'/name
        assert transparent.exists() and white.exists() and copy.exists(),name
        assert transparent.stat().st_mtime>=html.stat().st_mtime,name+' transparente anterior al HTML'
        assert white.stat().st_mtime>=html.stat().st_mtime,name+' blanco anterior al HTML'
        assert white.read_bytes()==copy.read_bytes(),name+' copia blanca distinta'
        images.append(name)
report=dict(html=len(manifest),png_transparentes=len(images),png_blancos=len(images),copias_blancas=len(images),
            hashes_html_correctos=True,enlaces_locales_completos=True,
            navegador=json.loads((OUT/'revision_automatizada.json').read_text(encoding='utf8')),
            motor=json.loads((ROOT/'analisis/escenarios2003/verificacion.json').read_text(encoding='utf8')))
(OUT/'CONTROL_ENTREGA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
