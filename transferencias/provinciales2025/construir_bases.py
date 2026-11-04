"""Cruces territoriales explícitos con diputados nacionales de octubre.

No se unen IDs de mesas de elecciones distintas. Los subcircuitos de Salta
se cotejan por código; los faltantes quedan fuera de ambas bases.
"""
import json
import re
import pandas as pd
from preparar import HERE, RAW, norm, nacional, nacional_circuitos

CONFIG={
 'pba':('Buenos Aires','02','07/09/2025','Legislatura provincial'),
 'caba':('Ciudad de Buenos Aires','01','18/05/2025','Legislatura porteña'),
 'chaco':('Chaco','06','11/05/2025','Diputados provinciales'),
 'corrientes_diputados':('Corrientes','05','31/08/2025','Diputados provinciales'),
 'corrientes_gobernador':('Corrientes','05','31/08/2025','Gobernador'),
 'corrientes_senadores':('Corrientes','05','31/08/2025','Senadores provinciales'),
 'jujuy':('Jujuy','10','11/05/2025','Diputados provinciales'),
 'misiones':('Misiones','14','08/06/2025','Diputados provinciales'),
 'salta_diputado':('Salta','17','11/05/2025','Diputados provinciales'),
 'salta_senador':('Salta','17','11/05/2025','Senadores provinciales'),
 'sanluis_diputados':('San Luis','19','11/05/2025','Diputados provinciales'),
 'sanluis_senadores':('San Luis','19','11/05/2025','Senadores provinciales'),
 'santafe':('Santa Fe','21','13/04/2025','Convencionales: distrito único'),
}
NOTAS={
 'pba':'135 municipios. Se combina diputados o senadores provinciales según la sección. Sólo votos válidos: la publicación municipal no informa nulos. Somos Buenos Aires y Potencia se conservan separados. Las páginas públicas de San Miguel y Lezama no están enlazadas en el índice, pero fueron recuperadas por su nombre de archivo y verificadas por encabezado.',
 'caba':'167 circuitos, escrutinio provisorio de mayo. Se excluyen las mesas extranjeras. Sin abstención.',
 'chaco':'25 departamentos. La suma coincide al voto con todos los totales partidarios y no positivos del definitivo. Sin abstención.',
 'corrientes':'25 departamentos. Esquina se reconstruye con sus dos municipios: Esquina y Pueblo Libertador. El agregado departamental difiere ligeramente del total general publicado por la misma API; se conservan las cifras territoriales sin ajustar.',
 'jujuy':'149 circuitos del escrutinio definitivo. Positivos: 369.394, iguales al resumen provincial. Sin abstención.',
 'misiones':'78 tablas municipales, agregadas a 17 departamentos. La publicación estadística oficial presenta diferencias internas: suma municipal 555.879 emitidos frente a 555.868 del resumen. Se conservan los datos municipales, sin completar residuos. Sin abstención.',
 'salta':'Subcircuitos del cargo correspondiente. Se excluyen resoluciones sin subcircuito y códigos sin correspondencia nacional; cobertura cuantificada. Sólo válidos (positivos y blancos): la planilla no incluye nulos. Cada cargo cubre departamentos distintos.',
 'sanluis':'Sólo los departamentos que eligieron este cargo. Transcripción verificada visualmente del definitivo. Diputados y senadores se superponen en Belgrano; nunca se suman entre sí. Muy pocas unidades: las estimaciones no identifican transferencias precisas.',
 'santafe':'Elección general de convencionales de distrito único del 13 de abril. No se usan las PASO municipales ni se la presenta como elección de diputados. 19 departamentos. Sin abstención.',
}
FUENTES={
 'pba':'https://www.juntaelectoral.gba.gov.ar/escrutinio-definitivo-2025/escrutinio-argentinos/',
 'caba':'https://data.buenosaires.gob.ar/dataset/elecciones-2025/resource/807c17bb-4684-4eb9-980a-ba6c8fbca739/download',
 'chaco':'https://resultados.electoralchaco.gob.ar/historico/15/cargos-provinciales/',
 'corrientes':'https://elecciones2025-definitivo.corrientes.gob.ar/escrutinio',
 'jujuy':'https://www.electoraljujuy.gob.ar/Contenido/TEP/Estadisticas/20251105/ele25.rar',
 'misiones':'https://www.electoralmisiones.gov.ar/wp-content/uploads/2025/09/Estadisticas-Elecciones-Legislativas-8-de-Junio-de-2025-1.pdf',
 'salta':'https://www.electoralsalta.gov.ar/elecciones/escrutinio/escrutinio-definitivo-generales-2025.xlsx',
 'sanluis':'https://electoral.justiciasanluis.gov.ar/wp-content/uploads/2025/05/acordada_15_tep_2025.pdf',
 'santafe':'https://www.santafe.gov.ar/tribunalelectoral/wp-content/uploads/sites/84/2025/07/resultadosPrimarias2025.ods',
}
ALIASES={
 'EXALTACDELACRUZ':'EXALTACIONDELACRUZ','CORONELROSALES':'CORONELDEMARINALROSALES',
 'GENERALMADARIAGA':'GENERALJUANMADARIAGA','DELPILAR':'PILAR','PARTIDODEPINAMAR':'PINAMAR',
 'PARTIDODELACOSTA':'LACOSTA','PDOMONTEHERMOSO':'MONTEHERMOSO','PDOVILLAGESELL':'VILLAGESELL',
 'GENERALJOSEDESANMARTIN':'GENERALSANMARTIN','ROSDELAFRONTERA':'ROSARIODELAFRONTERA',
 'FRAYJSTAMARIADEORO':'FRAYJUSTOSANTAMARIADEORO','GENERALDONOVAN':'GENERALDONOVAN',
 'LIBGENERALSANMARTIN':'LIBERTADORGENERALSANMARTIN','MAYORLJFONTANA':'MAYORLUISJORGEFONTANA',
 'PCIADELAPLAZA':'PRESIDENCIADELAPLAZA','12DEOCTUBRE':'12DEOCTUBRE',
 'CMDTEFERNANDEZ':'COMANDANTEFERNANDEZ','FRAYJSMDEORO':'FRAYJUSTOSANTAMARIADEORO',
 'GOBERNADORDUPUY':'DUPUY','GENERALPEDERNERA':'PEDERNERA',
 'LNALEM':'LEANDRONALEM','GENERALMBELGRANO':'GENERALMANUELBELGRANO','CONCEPCIONDELASIERRA':'CONCEPCION',
}

def normalized_index(t):
 t=t.copy();t.index=t.index.map(lambda s:ALIASES.get(norm(s),norm(s)))
 assert t.index.is_unique,t.index[t.index.duplicated()].tolist()
 return t

def agrupar(t,foco=(),threshold=.02):
 # El umbral se aplica dentro del distrito, nunca sobre el total nacional.
 # Las identidades de interés sobreviven aunque sean pequeñas.
 out=pd.DataFrame(index=t.index)
 for col in t:
  if not t[col].sum():continue
  keep=t[col].sum()/t.values.sum()>=threshold or col in foco or col in ['Blanco','Blanco y nulo']
  key=col if keep else 'Otras listas'
  out[key]=out.get(key,0)+t[col]
 assert out.values.sum()==t.values.sum()
 return out

def construir():
 bases={};checks=[]
 for key,(nombre,dist,fecha,cargo) in CONFIG.items():
  family=key.split('_')[0]
  raw=pd.read_pickle(HERE/('prov_'+key+'.pkl'))
  t=raw.drop(columns=['control_total','id_fuente','cargo'],errors='ignore').copy()
  validos=family in ['pba','salta']
  foco=[];level='departamentos';sin=[]
  if family=='pba':
   t.index=t.index.map(lambda s:re.sub(r'^\d+\s*-\s*','',s))
   t=normalized_index(t)
   foco=[c for c in t if 'SOMOS BUENOS AIRES' in c.upper() or 'POTENCIA' in c.upper()]
   level='municipios'
  elif family in ['caba','jujuy']:
   t.index=t.index.map(lambda s:re.sub(r'^0+(?=\d)','',re.sub(r'\.0$','',str(s))).upper())
   level='circuitos'
  elif family=='misiones':
   corr=pd.read_csv(HERE.parent/'provinciales2023/correspondencias_misiones.csv')
   lookup={norm(r.unidad):r.departamento for r in corr.itertuples()}
   lookup.update({'FRACRAN':'Guaraní','CORPUSCHRISTI':'San Ignacio','ITACARUARE':'San Javier'})
   # Fracrán: departamento Guaraní, fuente estadística oficial p. 23.
   sin=[n for n in t.index if norm(n) not in lookup]
   assert not sin,sin
   t['departamento']=[lookup[norm(n)] for n in t.index]
   t=normalized_index(t.groupby('departamento').sum())
   foco=['Frente Renovador de la Concordia']
  elif family=='salta':
   d=pd.read_pickle(RAW/'salta2025.pkl');v=d[d['Categoría'].eq('DIPUTADO' if key.endswith('diputado') else 'SENADOR')].copy()
   v['cat']=v['Frente electoral'].fillna(v.Lista).str.strip().str.replace('\u00a0',' ')
   v.loc[v.cat.eq('VOTOS EN BLANCO'),'cat']='Blanco'
   total_fuente=int(v.Votos.sum())
   sin=['Resoluciones sin subcircuito: '+str(int(v[v.Subcircuito.isna()].Votos.sum()))+' votos']
   t=v.pivot_table(index='Subcircuito',columns='cat',values='Votos',aggfunc='sum',fill_value=0)
   level='subcircuitos'
  else:
   if family=='sanluis':t.index=t.index.map(lambda s:'Libertador General San Martín' if norm(s)=='SANMARTIN' else s)
   t=normalized_index(t)
  if family!='salta':total_fuente=int(t.values.sum())
  b=nacional_circuitos(dist,validos) if level in ['circuitos','subcircuitos'] else normalized_index(nacional(dist,validos))
  if family=='salta':
   # No hay resultados provinciales de este cargo en el resto de la provincia.
   # El denominador de destino se limita a los departamentos que sí votaron.
   names=nacional(dist,validos).index
   scope=raw.index.map(lambda s:norm(s.replace('ROS. DE','ROSARIO DE').replace('SAN MARTIN','GENERAL SAN MARTIN')))
   # El porcentaje del destino se informa sobre todos los circuitos disponibles
   # de los departamentos del cargo, usando las secciones del cache DINE.
   import estimar
   vv,_=pd.read_pickle(HERE.parent/'circ_2025.pkl')
   sections=estimar.secnames(2025)
   permitted={str(c) for s,c in vv[vv.distrito_id.eq(dist)][['seccion_id','circuito']].drop_duplicates().itertuples(index=False,name=None)
      if ALIASES.get(norm(sections[(dist,int(s))]),norm(sections[(dist,int(s))])) in set(scope)}
   denom_dest=float(b.loc[b.index.intersection(permitted)].values.sum())
  else:denom_dest=float(b.values.sum())
  idx=t.index.intersection(b.index).sort_values()
  zeros=[n for n in idx if t.loc[n].sum()<=0 or b.loc[n].sum()<=0]
  idx=idx.difference(zeros).sort_values()
  missing_a=t.index.difference(b.index).tolist()
  missing_b=b.index.difference(t.index).tolist()
  coverage_a=float(t.loc[idx].values.sum()/total_fuente)
  coverage_b=float(b.loc[idx].values.sum()/denom_dest)
  assert len(idx)>=3,(key,missing_a,missing_b)
  # No coincidencias aproximadas: los nombres no resueltos se registran.
  a=t.loc[idx];b=b.loc[idx]
  a=agrupar(a,foco);b=agrupar(b)
  a=a.loc[:,a.sum()>0];b=b.loc[:,b.sum()>0]
  # La categoría de referencia del logit y la omitida en la pérdida del
  # port de Calvo es siempre el voto no positivo, nunca una fuerza elegida
  # accidentalmente por el orden alfabético.
  special=['Otras listas','Blanco','Blanco y nulo']
  a=a[[c for c in a if c not in special]+[c for c in special if c in a]]
  b=b[[c for c in b if c not in special]+[c for c in special if c in b]]
  id_=key+'_prov2025_dn2025'
  cfg=dict(id=id_,serie='2025',nombre=nombre,distrito=dist,fecha=fecha,cargo=cargo,nivel=level,
   origen=cargo+' '+fecha,destino='Diputados nacionales 26/10/2025',foco=foco,foco_lado='origen',
   nota=NOTAS[family],base='votos válidos (positivos + blancos)' if validos else 'votos emitidos',
   cobertura_origen=coverage_a,cobertura_destino=coverage_b,pendientes=sin+missing_a+['Sin votos informados en una de las elecciones: '+n for n in zeros],
   departamentos_cargo=raw.index.tolist() if family in ['salta','sanluis'] else [],
   fuente=FUENTES[family],agrupacion_menores='Listas menores al 2 % dentro del distrito, salvo identidades destacadas; originales completos conservados.')
  bases[id_]=(a,b,cfg)
  control=dict(id=id_,unidades=len(idx),origen_total_fuente=total_fuente,origen_cruzado=int(t.loc[idx].values.sum()),
   cobertura_origen=coverage_a,cobertura_destino=coverage_b,sin_correspondencia_origen=missing_a,sin_correspondencia_destino=missing_b,unidades_sin_votos=zeros)
  checks.append(control)
  print(key,a.shape,b.shape,'coberturas',round(coverage_a,6),round(coverage_b,6),'sin',missing_a,flush=True)
  a.to_csv(HERE/('base_'+key+'.csv'),encoding='utf-8-sig')
 pd.to_pickle(bases,HERE/'bases.pkl')
 (HERE/'CONTROL_CRUCES.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
 return bases

if __name__=='__main__':construir()
