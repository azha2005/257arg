from pathlib import Path
from urllib.parse import quote
import requests,json
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
plan=json.loads((ROOT/'plan_descargas.json').read_text(encoding='utf-8'))
commit=json.loads((META/'ceur_legacy_historia.json').read_text(encoding='utf-8'))[-1]
sha=commit['sha'];date=commit['commit']['committer']['date']
for year in [1991,2001,2010]:
    path=f'censos_shp_CONICET/{year}_RADIOS_ARGENTINA.rar';ident=f'ceur_legacy_{year}'
    if not any(x['id']==ident for x in plan):
        plan.append(dict(id=ident,url=f'https://raw.githubusercontent.com/matuteiglesias/argentina-geography/{sha}/'+quote(path),archivo=f'ceur_legacy/{year}_RADIOS_ARGENTINA.rar',tipo='radio censal',corte=str(year),fuente=f'https://github.com/matuteiglesias/argentina-geography/tree/{sha}',nota=f'Copia de una versión CEUR anterior a V2025-1, existente en commit {date}; verificar diferencias y licencia original. No es otro censo.',licencia='ver registro CEUR original',cobertura='Argentina'))

item=json.loads((META/'conicet_radios_2001_boccolini.json').read_text(encoding='utf-8'))
b=requests.get(item['_links']['bundles']['href'],timeout=30).json()
for bundle in b.get('_embedded',{}).get('bundles',[]):
    if bundle.get('name')!='ORIGINAL':continue
    bits=requests.get(bundle['_links']['bitstreams']['href']+'?size=100',timeout=30).json()
    (META/'boccolini2001_bitstreams.json').write_text(json.dumps(bits,ensure_ascii=False,indent=2),encoding='utf-8')
    for bit in bits.get('_embedded',{}).get('bitstreams',[]):
        ident='boccolini2001_'+bit['uuid']
        if any(x['id']==ident for x in plan):continue
        plan.append(dict(id=ident,url=bit['_links']['content']['href'],archivo='boccolini_2001/'+bit['name'],tipo='radio censal (subconjunto)',corte='2001',fuente='https://ri.conicet.gov.ar/handle/11336/284090',nota='Solo radios con densidad superior a 1 hab/ha. Atributos derivados; la autora declara geometría INDEC sin modificar. No es cobertura nacional íntegra.',licencia='CC BY 2.5 según registro; revisar excepciones',cobertura='Argentina: subconjunto denso'))
(ROOT/'plan_descargas.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('PLAN',len(plan),flush=True)
