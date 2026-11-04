from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
p=ROOT/'plan_descargas.json';plan=json.loads(p.read_text(encoding='utf-8'))
def add(ident,url,file,tipo,corte,cobertura,fuente,nota,licencia='Consultar ficha de la fuente'):
    if not any(r['id']==ident for r in plan):plan.append(dict(id=ident,url=url,archivo=file,tipo=tipo,corte=corte,cobertura=cobertura,fuente=fuente,nota=nota,licencia=licencia))
add('cordoba_radios_urbanos','https://idecor-ws.mapascordoba.gob.ar/geoserver/idecor/radios_urbanos/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=idecor:radios_urbanos&outputFormat=SHAPE-ZIP','cordoba/radios_municipales_comunales_actual.zip','municipio/comuna','Actual al descargar; servicio documentado desde 2019','Córdoba','https://www.idecor.gob.ar/usa-y-descarga-los-limites-oficiales-de-las-localidades-de-cordoba/','Radio municipal/comunal jurídico. El artículo de 2019 no convierte el servicio actual en snapshot de 2019.','CC BY-SA según metadatos IDECOR; verificar versión')
for name,tipo in [('departamentos_202610','departamento'),('gob_locales_2022','gobierno local'),('radios_censales_2022','radio censal')]:
    add('neuquen_'+name,f'https://sigestadistica.neuquen.gov.ar/geoserver/geonode/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=geonode:{name}&outputFormat=SHAPE-ZIP',f'neuquen/{name}.zip',tipo,'2022 según visor; snapshot 2026-10-31','Neuquén','https://www.estadisticaneuquen.gob.ar/apps/visor/','Geometría y atributos del visor oficial DPEyC; el nombre técnico no prueba vigencia legal anual.')
for name,tipo in [('departamentos','departamento'),('radios','radio censal'),('localidades','localidad censal (auxiliar)')]:
    add('precenso_'+name,f'https://geoserver.indec.gob.ar/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=precenso:{name}&outputFormat=shape-zip',f'indec/precenso_2019_2020/{name}.zip',tipo,'Precenso 2019–2020; no confundir con censo 2022','Localidades incluidas en el Precenso; cobertura parcial','https://precensodeviviendas.indec.gob.ar/descargas','El operativo refiere a localidades de 2000 habitantes o más. Los agregados no implican cobertura total de los departamentos. Geometría vigente y base censal deben cotejarse en metadatos.')
for year,rid,ext in [(2001,'juqdkmgo-1212-resource','zip'),(2010,'juqdkmgo-1214-resource','zip'),(2010,'c841591b-3719-4e6d-9ab6-71ae3972ec58','geojson')]:
    add(f'caba_radio_{year}_{ext}',f'https://data.buenosaires.gob.ar/dataset/informacion-censal-por-radio/resource/{rid}/download',f'caba/radios_{year}.{ext}','radio censal',str(year),'CABA','https://data.buenosaires.gob.ar/dataset/informacion-censal-por-radio','Descarga enlazada directamente por catálogo oficial; geometría censal, no circuito electoral.','CC BY 2.5 AR')
p.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(plan))
