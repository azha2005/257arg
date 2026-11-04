from pathlib import Path
from urllib.parse import urlparse
import requests,json,concurrent.futures as cf
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
plan=[]
def record(ident,url,file,tipo,corte,source,nota='',license='sin verificar',cobertura='Argentina'):
    plan.append(dict(id=ident,url=url,archivo=file,tipo=tipo,corte=corte,fuente=source,nota=nota,licencia=license,cobertura=cobertura))
for name,kind in [('radios','radio censal'),('deptos','departamento')]:
    item=json.loads((META/('dspace_find_'+name+'.txt')).read_text(encoding='utf-8'))
    bundles=requests.get(item['_links']['bundles']['href'],timeout=30).json()
    (META/('conicet_'+name+'_bundles.json')).write_text(json.dumps(bundles,ensure_ascii=False,indent=2),encoding='utf-8')
    for bundle in bundles.get('_embedded',{}).get('bundles',[]):
        if bundle.get('name')!='ORIGINAL':continue
        url=bundle['_links']['bitstreams']['href']+'?size=100'
        streams=requests.get(url,timeout=30).json()
        (META/('conicet_'+name+'_bitstreams.json')).write_text(json.dumps(streams,ensure_ascii=False,indent=2),encoding='utf-8')
        for n,bit in enumerate(streams.get('_embedded',{}).get('bitstreams',[])):
            filename=bit['name'];print('CONICET',name,filename,bit.get('sizeBytes'),flush=True)
            if not filename.lower().endswith(('.zip','.rar','.7z','.docx','.pdf','.txt')):continue
            import re
            years=re.findall(r'(?:18|19|20)\d\d',filename)
            corte=years[0] if years else 'documentación'
            record('conicet_'+name+'_'+bit['uuid'],bit['_links']['content']['href'],'conicet/'+name+'/'+filename,kind,corte,'https://ri.conicet.gov.ar/handle/'+item['handle'],'Cartografía de investigación corregida/armonizada; no atribuir a límites originales INDEC. Nombre de archivo conserva revisión.','ver metadata del registro')

config=json.loads((META/'radios_indec2010_config.txt').read_text(encoding='utf-8'))
for r in config['source_files']:
    record('indec2010_'+r['province_code'],r['download_url'],'indec/2010/'+r['file_name'],'radio censal','2010','https://www.indec.gob.ar/indec/web/Institucional-Indec-Codgeo','Archivo provincial oficial. Validar capas y cobertura.','ver página oficial',r['province_name'])
record('indec2022_radios','https://geonode.indec.gob.ar/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=geonode:radios_censales2&outputFormat=SHAPE-ZIP','indec/2022/radios_censales_nacional.zip','radio censal','2022','https://geonode.indec.gob.ar/layers/geonode_data:geonode:radios_censales2','Obtener hits WFS para contrastar cantidad; no suponer cobertura completa por éxito HTTP.')
for res,kind in [('departamentos','departamento'),('municipios','municipio'),('gobiernos-locales','gobierno local')]:
    record('georef_'+res,'https://apis.datos.gob.ar/georef/api/v2.0/'+res+'.geojson','georef_actual/'+res+'.geojson',kind,'sin vigencia histórica verificada','https://www.argentina.gob.ar/georef/descarga-de-la-base-completa','Snapshot de consulta 2026-10-31; comprobar si geometrías son polígonos o puntos.')
for res,kind in [('municipio','municipio'),('departamento','departamento')]:
    record('ign_'+res,'https://www.ign.gob.ar/descargas/geodatos/'+res+'.zip','ign_actual/'+res+'.zip',kind,'sin vigencia histórica verificada','https://www.ign.gob.ar/NuestrasActividades/InformacionGeoespacial/CapasSIG','Snapshot de consulta; fecha de descarga no determina año de límites.')
package=json.loads((META/'pba_radios.txt').read_text(encoding='utf-8'))['result']
for n,r in enumerate(package['resources']):
    if 'zip' not in r.get('format','').lower():continue
    filename=Path(urlparse(r['url']).path).name
    record('pba_radios_'+r['id'],r['url'],'pba/radios/'+filename,'radio censal','2022' if '2022' in r['name'] else '2010','https://catalogo.datos.gba.gob.ar/dataset/radios-censales',r.get('description',''),'CC BY 4.0','Buenos Aires')
(ROOT/'plan_descargas.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('PLAN',len(plan),flush=True)
