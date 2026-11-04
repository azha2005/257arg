"""Catálogo reproducible de originales usados, peticiones y SHA-256."""
from pathlib import Path
import hashlib
import json
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TR=HERE.parent
sys.path.insert(0,str(TR/'provinciales2025'))
from construir_bases import FUENTES

def main():
 records=[]
 def add(file,url,**extra):
  f=Path(file)
  assert f.exists(),f
  records.append(dict(archivo=f.relative_to(ROOT).as_posix(),url=url,bytes=f.stat().st_size,
   sha256=hashlib.sha256(f.read_bytes()).hexdigest(),**extra))
 raw=TR/'provinciales2023/fuentes'
 manifest=json.loads((raw/'manifest.json').read_text(encoding='utf8'))
 for j in manifest:add(raw/j['archivo'],j['url'],serie='2023',tipo='original oficial')
 for f in raw.glob('rn_*.json'):
  if f.name in [j['archivo'] for j in manifest]:continue
  name=f.stem
  if name.startswith('rn_meta_'):url='https://www.jusrionegro.gov.ar/inicio/web/escrutinio-16-04-2023/metadata/'+name[8:].replace('.','/')+'/meta.json'
  elif name.startswith('rn_RN.'):url='https://www.jusrionegro.gov.ar/inicio/web/escrutinio-16-04-2023/resultados/'+name[3:].replace('.','/')+'/GOB.json'
  else:continue
  add(f,url,serie='2023')
 add(raw/'neuquen_distribucion.pdf','https://intranet.jusneuquen.gov.ar/images2/Electoral/CP_16-04-2023/datos_generales/mesas_por_establecimiento.pdf',serie='2023',tipo='correspondencia mesas/localidad')
 for name,prov in [('georef_misiones.json','misiones'),('georef_neuquen.json','neuquen'),('georef_rio%20negro.json','rio%20negro')]:
  add(raw/name,'https://apis.datos.gob.ar/georef/api/localidades?provincia='+prov+'&max=1000&campos=id,nombre,departamento,municipio',tipo='correspondencia territorial')
 for name,prov in [('asentamientos_neuquen.json','neuquen'),('asentamientos_rio.json','rio%20negro')]:
  add(raw/name,'https://apis.datos.gob.ar/georef/api/asentamientos?provincia='+prov+'&max=5000',tipo='correspondencia territorial')
 raw=TR/'provinciales2025/fuentes'
 names={'caba':'caba2025.csv','jujuy':'jujuy2025.rar','misiones':'misiones_estadisticas.pdf','salta':'salta2025.xlsx','sanluis':'sanluis_acordada15.pdf','santafe':'sf_primarias2025.ods'}
 for k,name in names.items():add(raw/name,FUENTES[k],serie='2025',distrito=k,tipo='provisorio' if k=='caba' else 'definitivo')
 for f in raw.glob('pba_distrito_*.html'):
  add(f,FUENTES['pba']+f.name[4:],serie='2025',distrito='pba',tipo='definitivo municipal')
 chaco='https://resultados.electoralchaco.gob.ar'
 for f in raw.glob('chaco_dep_*.json'):
  id_=f.stem.rsplit('_',1)[-1]
  if id_=='0':continue
  add(f,chaco+'/api/v1/resultados/resultados-provinciales/',metodo='GET',parametros=dict(eleccion_id=15,tipo_resultado='escrutinio_definitivo',departamento_id=int(id_),municipio_id='',circuito_id='',mesa_id=''),serie='2025',distrito='chaco')
 for name,path,params in [('chaco_general.json','/api/v1/resultados/resultados-provinciales/',dict(eleccion_id=15,tipo_resultado='escrutinio_definitivo',departamento_id='',municipio_id='',circuito_id='',mesa_id='')),('chaco_departamentos.json','/api/v1/departamentos/',dict(eleccion_id=15))]:
  add(raw/name,chaco+path,metodo='GET',parametros=params,serie='2025',distrito='chaco')
 base='https://elecciones2025-definitivo-api.corrientes.gob.ar/api/'
 for f in sorted(raw.glob('corrientes_dep_*.json')):
  j=json.loads(f.read_text(encoding='utf8'))
  if not j.get('data',{}).get('header'):continue
  id_=int(f.stem.rsplit('_',1)[-1])
  add(f,base+'escrutinio/resultados/buscar',metodo='POST',cuerpo=dict(filtroTipoId=2,valor=id_,descripcion='Departamento',seleccionUnica=True,valorDescripcion=''),serie='2025',distrito='corrientes')
 for id_ in [67,44]:
  add(raw/f'corrientes_mun_{id_}.json',base+'escrutinio/resultados/buscar',metodo='POST',cuerpo=dict(filtroTipoId=3,valor=id_,descripcion='Municipio',seleccionUnica=True,valorDescripcion=''),serie='2025',distrito='corrientes')
 add(raw/'corrientes_generales.json',base+'escrutinio/resultados/generales',metodo='GET',serie='2025',distrito='corrientes')
 for key in ['2019p','2023p','2023b','2025']:
  add(TR/f'circ_{key}.pkl','https://portal-andino.datos.gob.ar/dataset/dine-resultados-provisionales-elecciones-'+key[:4],tipo='caché DINE local por circuito',nota='Derivado local por agregar_circuitos.py; no es un archivo descargado con este nombre.')
 add(ROOT/'datos_oficiales/2025/agregado.pkl','https://portal-andino.datos.gob.ar/dataset/dine-resultados-provisionales-elecciones-2025',tipo='caché DINE local por sección',nota='Derivado local de los provisorios oficiales.')
 finer=HERE/'circuitos/fuentes'
 if finer.exists():
  for filename,url in [
   ('santafe2023.ods','https://www.santafe.gov.ar/tribunalelectoral/wp-content/uploads/sites/84/2024/08/resultadosGenerales2023.ods'),
   ('misiones_circuitos2023.pdf','https://www.electoralmisiones.gov.ar/wp-content/uploads/2023/04/Circuitos-Mnes-2023-Completo.pdf'),
   ('chaco_territorio2019.html','https://electoralchaco.gov.ar/384-circuitos/')]:
   if (finer/filename).exists():add(finer/filename,url,tipo='original oficial del empalme')
  for year,eleccion,prefix in [(2023,3,'chaco2023'),(2025,15,'chaco')]:
   units_file=finer/(prefix+'_circuitos.json')
   if not units_file.exists():continue
   add(units_file,'https://resultados.electoralchaco.gob.ar/api/v1/circuitos/',metodo='GET',parametros=dict(eleccion_id=eleccion),serie=str(year))
   total_file=finer/(prefix+'_total.json')
   if total_file.exists():add(total_file,'https://resultados.electoralchaco.gob.ar/api/v1/resultados/resultados-provinciales/',metodo='GET',
     parametros=dict(eleccion_id=eleccion,tipo_resultado='escrutinio_definitivo',departamento_id='',municipio_id='',circuito_id='',mesa_id=''),serie=str(year),tipo='resumen oficial de control')
   units=json.loads(units_file.read_text(encoding='utf8'))['results']
   for u in units:
    if not u['circuito_id']:continue
    f=finer/(prefix+'_circ_'+str(u['circuito_id'])+'.json')
    if f.exists():add(f,'https://resultados.electoralchaco.gob.ar/api/v1/resultados/resultados-provinciales/',metodo='GET',
      parametros=dict(eleccion_id=eleccion,tipo_resultado='escrutinio_definitivo',departamento_id='',municipio_id='',circuito_id=u['circuito_id'],mesa_id=''),serie=str(year))
  cf=finer/'corrientes_filtro_circuito.json'
  if cf.exists():
   add(cf,'https://elecciones2025-definitivo-api.corrientes.gob.ar/api/comun/filtroTipo',metodo='POST',cuerpo=dict(filtroTipoId=4),serie='2025')
   units=next(j['datos'] for j in json.loads(cf.read_text(encoding='utf8')) if j['filtroTipoId']==4)
   for u in units:
    f=finer/('corrientes_circ_'+str(u['valor'])+'.json')
    if f.exists():add(f,'https://elecciones2025-definitivo-api.corrientes.gob.ar/api/escrutinio/resultados/buscar',metodo='POST',
      cuerpo=dict(filtroTipoId=4,valor=u['valor'],descripcion='Circuito',seleccionUnica=True,valorDescripcion=u['descripcion']),serie='2025')
  for f in (HERE/'circuitos').glob('nombres_*.pkl'):
   year=f.stem.rsplit('_',1)[-1]
   add(f,'https://portal-andino.datos.gob.ar/dataset/dine-resultados-provisionales-elecciones-'+year,tipo='nombres derivados del original DINE por circuito')
  add(HERE/'circuitos/dine_gob2023.pkl','https://portal-andino.datos.gob.ar/dataset/dine-resultados-provisionales-elecciones-2023',tipo='gobernadores y jefe de Gobierno por circuito, derivado de DINE')
 result=dict(fecha='2026-11-02',archivos=records,
  pendiente_formosa=dict(estado='No estimado; descargas interrumpidas por el servidor',indice='https://tep.jusformosa.gob.ar/resultados',
   departamentos={k:'https://archivostep.jusformosa.gob.ar/archivos/archivo_'+str(n)+'.pdf' for k,n in {'Formosa':1752760038,'Laishí':1752760154,'Pilcomayo':1752760190,'Pirané':1752760224,'Pilagás':1752760251,'Patiño':1752760299,'Bermejo':1752760348,'Matacos':1752760380,'Ramón Lista':1752760419}.items()}))
 (HERE/'FUENTES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print('Fuentes catalogadas:',len(records),flush=True)

if __name__=='__main__':main()
