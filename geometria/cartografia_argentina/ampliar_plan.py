from pathlib import Path
import requests,json
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
plan=json.loads((ROOT/'plan_descargas.json').read_text(encoding='utf-8'))
def add(id,url,path,tipo,corte,fuente,nota='',cobertura='Argentina'):
    if any(x['id']==id for x in plan):return
    plan.append(dict(id=id,url=url,archivo=path,tipo=tipo,corte=corte,fuente=fuente,nota=nota,licencia='ver ficha de origen',cobertura=cobertura))
add('georef_municipios_legacy','https://apis.datos.gob.ar/georef/api/municipios.geojson','georef_actual/municipios_legacy.geojson','municipio','sin vigencia histórica verificada','https://datosgobar.github.io/georef-ar-api/referencia/operations/filename/','Polígonos del dump legacy; el endpoint de consultas en formato GeoJSON devuelve centroides y no es equivalente.')
layers=json.loads((META/'indec_layers.txt').read_text(encoding='utf-8'))['objects']
for name,tipo in [('gobiernos_locales4','gobierno local'),('departamentos','departamento'),('fracciones_censales','fracción censal')]:
    layer=next(x for x in layers if x.get('name')==name)
    metadata_url='https://geonode.indec.gob.ar/layers/geonode_data:geonode:'+name
    r=requests.get(metadata_url,timeout=30)
    (META/('indec_'+name+'.html')).write_text(r.text,encoding='utf-8')
    add('indec2022_'+name,'https://geonode.indec.gob.ar/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=geonode:'+name+'&outputFormat=SHAPE-ZIP','indec/2022/'+name+'.zip',tipo,'2022; confirmar metadata',metadata_url,'Conservar diferencias con IGN y Georef; guardar conteo WFS hits.')
    r=requests.get('https://geonode.indec.gob.ar/geoserver/wfs',params=dict(service='WFS',version='1.1.0',request='GetFeature',typeName='geonode:'+name,resultType='hits'),timeout=30)
    (META/('indec_hits_'+name+'.xml')).write_text(r.text,encoding='utf-8')
(ROOT/'plan_descargas.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('PLAN',len(plan))
