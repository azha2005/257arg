"""Empalmes auditables: claves dentro del departamento, nombres y uniones.

No reparte votos. Los circuitos sin correspondencia o sin votos quedan fuera.
Las versiones gruesas anteriores se conservan para comparar sensibilidad.
"""
from pathlib import Path
import json
import re
import sys
import unicodedata
import pandas as pd
import numpy as np
HERE=Path(__file__).resolve().parent;TR=HERE.parents[1];ROOT=TR.parent
sys.path.insert(0,str(TR))
import estimar

def norm(s):
 s=unicodedata.normalize('NFD',str(s)).encode('ascii','ignore').decode().upper()
 s=re.sub(r'\bGRAL\b','GENERAL',s)
 n=re.sub('[^A-Z0-9]','',s)
 return {'LIBGENERALSANMARTIN':'LIBERTADORGENERALSANMARTIN','GENERALJOSEDESANMARTIN':'GENERALSANMARTIN',
  'SANMARTIN':'GENERALSANMARTIN','CMDTEFERNANDEZ':'COMANDANTEFERNANDEZ','FRAYJSMDEORO':'FRAYJUSTOSANTAMARIADEORO',
  'FRAYJSTAMARIADEORO':'FRAYJUSTOSANTAMARIADEORO','PCIADELAPLAZA':'PRESIDENCIADELAPLAZA',
  'MAYORLJFONTANA':'MAYORLUISJORGEFONTANA','MAYORLUISJFONTANA':'MAYORLUISJORGEFONTANA','ROSDELAFRONTERA':'ROSARIODELAFRONTERA',
  'NUEVEDEJULIO':'9DEJULIO','VEINTICINCODEMAYO':'25DEMAYO','1DEMAYO':'PRIMERODEMAYO'}.get(n,n)

def code(s):return str(s).strip().upper().lstrip('0') or '0'
def unit(dep,c):return norm(dep)+':'+code(c)

def national(key,dist,validos=False):
 if str(key)=='2025':
  v,_=pd.read_pickle(TR/'circ_2025.pkl');v=v[v.distrito_id.eq(dist)].copy()
  full,_=pd.read_pickle(ROOT/'datos_oficiales/2025/agregado.pkl')
  names=full[full.distrito_id.astype(int).eq(int(dist))][['agrupacion_id','agrupacion_nombre']].dropna().drop_duplicates()
  names['id']=names.agrupacion_id.astype(str).str.zfill(4)
  mapping=names.drop_duplicates('id').set_index('id').agrupacion_nombre.to_dict()
  v['cat']=np.where(v.votos_tipo.eq('POSITIVO'),v.agrupacion_id.astype(str).str.zfill(4).map(mapping),'Blanco y nulo')
  assert not v.cat.isna().any()
  t=v.pivot_table(index=['seccion_id','circuito'],columns='cat',values='v',aggfunc='sum',fill_value=0)
 else:
  t,_=estimar.load(key);t=t.loc[dist].drop(columns='No votó',errors='ignore')
 if validos:
  v,_=pd.read_pickle(TR/f'circ_{key}.pkl');v=v[v.distrito_id.eq(dist)&v.votos_tipo.eq('EN BLANCO')]
  whites=v.groupby(['seccion_id','circuito']).v.sum()
  t=t.drop(columns='Blanco y nulo');t['Blanco']=whites.reindex(t.index).fillna(0)
 names=estimar.secnames(key)
 t.index=[unit(names[(dist,int(s))],c) for s,c in t.index]
 assert t.index.is_unique
 return t.loc[:,t.sum()>0]

def raw_chaco(year):
 d=pd.read_pickle(HERE/f'chaco{year}.pkl');meta=d[['circuito','departamento','municipio','id_api']].copy()
 d.index=[unit(dep,c) for dep,c in zip(d.departamento,d.circuito)]
 meta.index=d.index
 t=d.drop(columns=meta.columns).copy()
 assert t.index.is_unique
 # Códigos son los circuitos oficiales, no las claves internas circuito_id.
 return t,meta

def grupos(t,threshold=.02,focus=()):
 out=pd.DataFrame(index=t.index)
 for c in t:
  if t[c].sum()==0:continue
  dest=c if t[c].sum()/t.values.sum()>=threshold or c in focus or c in ['Blanco','Blanco y nulo'] else 'Otras listas'
  out[dest]=out.get(dest,0)+t[c]
 special=['Otras listas','Blanco','Blanco y nulo']
 return out[[c for c in out if c not in special]+[c for c in special if c in out]]

def union_chaco(t,year):
 # Aviso expreso del visor oficial y catálogo territorial del Tribunal:
 # https://electoralchaco.gov.ar/384-circuitos/ (09/04/2019).
 # La Eduvigis ocupa 31,58,59 en dos departamentos nacionales; Cote Lai
 # ocupa 36 y 68. Se unen globalmente, sin mezclar sus códigos con otros.
 pairs={'25':'24','31':'59','35':'32','36':'68','56':'54','116':'115'}
 keys=[]
 for u in t.index:
  dep,c=u.split(':');target=pairs.get(c,c)
  if c in ['31','58','59']:
   keys.append('UNION:LAEDUVIGIS');continue
  if c in ['36','68']:
   keys.append('UNION:COTELAI');continue
  if target in pairs.values():target='U'+target
  keys.append(dep+':'+target)
 out=t.copy();out.index=keys;out=out.groupby(level=0).sum()
 np.testing.assert_allclose(out.sum(),t.sum())
 return out

def sf_raw(year):
 if year==2025:
  d=pd.read_pickle(TR/'provinciales2025/fuentes/sf_primarias2025.pkl').copy()
  d['v']=pd.to_numeric(d['Convencional Reformador Distrito Único'])
  d=d.rename(columns={'nomsec':'dep','nomcir':'localidad','circuito':'c','nombre_partido':'cat'})
  d.loc[d.partido.isin(['9998','9999']),'cat']='Blanco y nulo'
 else:
  rows=pd.read_pickle(HERE/'sf2023_distritales2023.pkl')
  d=pd.DataFrame([r[:13] for r in rows[1:]],columns=[s.strip() for s in rows[0][:13]])
  d=d.rename(columns={'DEPARTAMENTO':'dep','CIRCUITO':'c','LOCALIDAD':'localidad','NOMBRE':'cat'})
  d['v']=pd.to_numeric(d['VOTOS GOBERNADOR'])
  d.loc[d.cat.str.contains('VOTOS ANULADOS|VOTOS BLANCOS'),'cat']='Blanco y nulo'
 d['cat']=d.cat.str.strip();d['u']=[unit(dep,c) for dep,c in zip(d.dep,d.c)]
 t=d.pivot_table(index='u',columns='cat',values='v',aggfunc='sum',fill_value=0)
 t=t.loc[:,t.sum()>0]
 meta=d[['u','dep','localidad','c']].drop_duplicates().set_index('u')
 assert meta.index.is_unique
 return t,meta

def sf_mapping(meta,year):
 # Mismo sistema nuevo en 2023 y 2025. Los nombres nacionales de 2025
 # permiten comprobar la localidad; el anexo CNE 66/2022 traduce 2019.
 names=pd.read_pickle(HERE/'nombres_2025.pkl');names=names[names.distrito_id.eq('21')]
 def locality(s):
  s=re.sub(r'^\d+[A-Z]?\s*-\s*','',s)
  s=re.split(r'\(|\bSEC\.',s)[0].strip()
  return norm(s)
 aliases={'VILLAGDORGALVEZ':'VILLAGOBERNADORGALVEZ','VILLAGOBGALVEZ':'VILLAGOBERNADORGALVEZ',
  'SANFCO':'SANFRANCISCO','SANFCO DESANTAFE':'SANFRANCISCODESANTAFE',
  'SANJOSEDELRINCON':'SANJOSEDELRINCON'}
 def localnorm(s):
  n=norm(s);return aliases.get(n,n)
 candidates={}
 for k,row in meta.iterrows():candidates.setdefault((norm(row.dep),localnorm(row.localidad)),[]).append(k)
 mapping={};audit=[]
 for row in names.itertuples():
  dep=norm(row.seccion_nombre);loc=locality(row.circuito_nombre)
  exact=unit(row.seccion_nombre,row.circuito_id)
  possible=candidates.get((dep,loc),[])
  if len(possible)==1:target=possible[0];reason='misma localidad y departamento en ambas fuentes'
  elif exact in meta.index and localnorm(meta.loc[exact,'localidad'])==loc:target=exact;reason='código, localidad y departamento coincidentes'
  else:target=None;reason='sin correspondencia nominal unívoca'
  mapping[(int(row.seccion_id),row.circuito_id)]=target
  audit.append(dict(seccion=int(row.seccion_id),circuito=row.circuito_id,nombre_nacional=row.circuito_nombre,unidad_provincial=target,motivo=reason))
 if year==2019:
  table=pd.read_csv(TR/'correspondencias_2013_2017/santa_fe_2022.csv',dtype=str)
  translated={}
  for row in table.itertuples():
   target=mapping.get((int(row.seccion_nueva),row.circuito_nuevo))
   translated.setdefault((int(row.seccion_anterior),row.circuito_anterior),set()).add(target)
  out={k:next(iter(v)) for k,v in translated.items() if len(v)==1 and None not in v}
  return out,audit
 return mapping,audit

def sf_national(key,meta):
 year=int(key[:4]);mapping,audit=sf_mapping(meta,year)
 if str(key)=='2025':
  t=national(key,'21')
  # Recupera la sección numérica sólo para aplicar la tabla oficial.
  named=estimar.secnames(2025);reverse={norm(n):s for (d,s),n in named.items() if d=='21'}
  t.index=pd.MultiIndex.from_tuples([(reverse[u.split(':')[0]],u.split(':')[1]) for u in t.index])
 else:
  t,_=estimar.load(key);t=t.loc['21'].drop(columns='No votó',errors='ignore')
 mapped=[mapping.get((int(s),c)) for s,c in t.index]
 # Si falta un circuito de una localidad, no se compara esa localidad
 # completa con una fracción nacional. Se baja todo el departamento a la
 # unión común, conservando circuitos/distritos sólo donde el empalme cierra.
 names=estimar.secnames(key)
 fallback={norm(names[('21',int(s))]) for (s,c),m in zip(t.index,mapped) if m is None and t.loc[(s,c)].sum()>0}
 mapped=[norm(names[('21',int(s))])+':DEPARTAMENTO' if norm(names[('21',int(s))]) in fallback else m for (s,c),m in zip(t.index,mapped)]
 unmatched=[dict(seccion=int(s),circuito=c,votos=float(t.loc[(s,c)].sum())) for (s,c),m in zip(t.index,mapped) if m is None]
 t.index=mapped;out=t[t.index.notna()].groupby(level=0).sum()
 return out,unmatched,audit,float(t.values.sum()),fallback

def salta():
 d=pd.read_pickle(TR/'provinciales2023/salta_detalle.pkl')
 d=d[d['Categoría'].eq('GOBERNADOR')].copy()
 d['u']=[unit(dep.replace('ROS. DE','ROSARIO DE'),c) if pd.notna(c) else None for dep,c in zip(d.Departamento,d.Subcircuito)]
 d['cat']=d.Lista.str.strip().replace({'ALIANZA GUSTAVO GOBERNADOR':'Gustavo Gobernador','FRENTE AVANCEMOS':'Avancemos','VOTOS EN BLANCO':'Blanco'})
 t=d.pivot_table(index='u',columns='cat',values='Votos',aggfunc='sum',fill_value=0)
 return t,float(d.Votos.sum()),int(d[d.u.isna()].Votos.sum())

def dine_source(dist):
 d=pd.read_pickle(HERE/'dine_gob2023.pkl');d=d[d.distrito_id.eq(str(int(dist)))].copy()
 d['u']=[unit(dep,c) for dep,c in zip(d.seccion_nombre,d.circuito_id)]
 d['cat']=np.where(d.votos_tipo.eq('POSITIVO'),d.agrupacion_nombre,'Blanco y nulo')
 t=d.pivot_table(index='u',columns='cat',values='v',aggfunc='sum',fill_value=0)
 return t

def estabilidad_2019(dist,chaco=False):
 parts=[]
 for key in ['2019p','2023p']:
  _,e=pd.read_pickle(TR/f'circ_{key}.pkl');e=e.loc[dist]
  names=estimar.secnames(key)
  e.index=[unit(names[(dist,int(s))],c) for s,c in e.index]
  frame=e.to_frame(key)
  if chaco:frame=union_chaco(frame,2023)
  parts.append(frame)
 audit=pd.concat(parts,axis=1)
 matched=audit.dropna();matched=matched[(matched>0).all(axis=1)]
 ratio=matched['2023p']/matched['2019p'];growth=float(ratio.median())
 audit['razon_relativa']=ratio/growth
 audit['excluir']=audit.razon_relativa.notna() & ~audit.razon_relativa.between(.75,1.33)
 audit.to_csv(HERE/f'estabilidad_padron_{dist}_2019_2023.csv',encoding='utf-8-sig')
 return audit.index[audit.excluir].tolist()

def construir():
 bases={};controls=[]
 def add(id_,t,b,cfg,source_total=None,dest_total=None,missing=None):
  source_total=source_total or float(t.values.sum());dest_total=dest_total or float(b.values.sum())
  idx=t.index.intersection(b.index).sort_values()
  idx=idx[(t.loc[idx].sum(1)>0)&(b.loc[idx].sum(1)>0)]
  assert len(idx)>=10,(id_,len(idx))
  a=t.loc[idx];bb=b.loc[idx]
  c=dict(cfg,id=id_,cobertura_provincial=float(a.values.sum()/source_total),
   cobertura_origen=float(a.values.sum()/source_total),cobertura_destino=float(bb.values.sum()/dest_total),
   pendientes=(missing or [])+t.index.difference(idx).tolist(),foco_lado='origen',foco=cfg.get('foco',[]))
  a=grupos(a,focus=c['foco']);bb=grupos(bb)
  if c.pop('invertir',False):a,bb=bb,a;c['foco_lado']='destino'
  bases[id_]=(a,bb,c)
  ctl=dict(id=id_,unidades=len(idx),fuente_votos=source_total,cruzados=float(t.loc[idx].values.sum()),
   cobertura_provincial=c['cobertura_provincial'],destino_votos=dest_total,destino_cruzado=float(b.loc[idx].values.sum()),
   sin_empalme_origen=t.index.difference(idx).tolist(),sin_empalme_destino=b.index.difference(idx).tolist())
  controls.append(ctl)
  pd.DataFrame({'unidad':idx}).to_csv(HERE/(id_+'_unidades.csv'),index=False,encoding='utf-8-sig')
  print('EMPALME',id_,len(idx),'cobertura',round(c['cobertura_provincial']*100,3),flush=True)

 elections=['2019p','2023p','2023b']
 for family,name,dist,date in [('salta','Salta','17','14/05/2023'),('chaco','Chaco','06','17/09/2023'),('santafe','Santa Fe','21','10/09/2023'),('pba','Buenos Aires','02','22/10/2023'),('caba','Ciudad de Buenos Aires','01','22/10/2023'),('catamarca','Catamarca','03','22/10/2023')]:
  if family=='chaco' and not (HERE/'chaco2023.pkl').exists():continue
  if family=='santafe':t,meta=sf_raw(2023);total=float(t.values.sum())
  elif family=='salta':t,total,no_code=salta()
  elif family=='chaco':t,meta=raw_chaco(2023);total=float(t.values.sum());t=union_chaco(t,2023)
  else:t=dine_source(dist);total=float(t.values.sum())
  for key in elections:
   if family=='santafe':
    b,unmatched,audit,denom,fallback=sf_national(key,meta)
    tt=t.copy();tt.index=[u.split(':')[0]+':DEPARTAMENTO' if u.split(':')[0] in fallback else u for u in tt.index];tt=tt.groupby(level=0).sum()
    pd.DataFrame(audit).to_csv(HERE/f'empalme_sf_{key}.csv',index=False,encoding='utf-8-sig')
   else:
    tt=t
    b=national(key,dist,validos=family=='salta');denom=float(b.values.sum())
    if family=='chaco':b=union_chaco(b,2023)
   back=key=='2019p'
   unstable=[]
   if back and family!='santafe':
    unstable=estabilidad_2019(dist,chaco=family=='chaco')
    tt=tt.drop(index=unstable,errors='ignore');b=b.drop(index=unstable,errors='ignore')
   cargo='Jefe de Gobierno' if family=='caba' else 'Gobernador'
   source='https://resultados.gob.ar/2023' if family in ['pba','caba','catamarca'] else {'salta':'https://www.electoralsalta.gov.ar/Elecciones/Escrutinio/Escrutinio-2023G.xlsx','santafe':'https://www.santafe.gov.ar/tribunalelectoral/wp-content/uploads/sites/84/2024/08/resultadosGenerales2023.ods','chaco':'https://resultados.electoralchaco.gob.ar/historico/3/cargos-provinciales/'}[family]
   level='distritos provinciales empalmados' if family=='santafe' else 'circuitos y uniones' if family=='chaco' else 'subcircuitos' if family=='salta' else 'circuitos'
   note={'salta':'Válidos (positivos y blancos); excluye resoluciones sin subcircuito. Sáenz y Avancemos quedan separados. La alianza Avancemos no identifica por separado a Ahora Patria.',
    'chaco':'Definitivo provincial por circuito. Uniones de circuitos reflejados en otros según aviso expreso del visor oficial; se aplica la misma unión al nacional. Se cotejan departamento y código, no IDs internos de la API.',
    'santafe':'Definitivo provincial por distrito/localidad. Las ciudades de Santa Fe y Rosario aparecen agregadas como 9999: se suman los circuitos nacionales de esas localidades. Correspondencias nominales y departamentales, sin reparto. Para 2019 se usa la tabla oficial CNE 66/2022.',
    'pba':'Provisorio DINE de gobernador por circuito, mesas nativas. Gobernador y presidente general se votaron el mismo día: es un cruce ecológico entre cargos simultáneos, no un desplazamiento temporal de votos.',
    'caba':'Provisorio DINE de jefe de Gobierno por circuito, mesas nativas. Elecciones simultáneas el 22 de octubre: permite estudiar composición entre cargos, no observar elecciones individuales.',
    'catamarca':'Provisorio DINE de gobernador por circuito, mesas nativas. Gobernador y presidente general se votaron el mismo día; no representa una transferencia temporal.'}[family]
   if key=='2019p':origin='Presidente 2019';dest=cargo+' '+date+' ('+level+')'
   else:origin=cargo+' '+date+' ('+level+')';dest='Presidente 22/10/2023' if key=='2023p' else 'Balotaje 19/11/2023'
   cfg=dict(nombre=name,distrito=dist,serie='2023',fecha=date,origen=origin,destino=dest,nivel=level,
    base='votos válidos (positivos + blancos)' if family=='salta' else 'votos emitidos',
    fuente=source,nota=note,invertir=back,foco=['Gustavo Gobernador','Avancemos'] if family=='salta' else [])
   if back and family!='santafe':
    cfg['nota']+=' Empalme 2019–2023 por departamento y código; se excluyen '+str(len(unstable))+' claves con cambios de padrón fuera de 0,75–1,33 del crecimiento mediano. Es un control de estabilidad, no certificación de límites históricos.'
   if family=='santafe':
    cfg['nivel']='distritos y departamentos empalmados'
    cfg['nota']+=' Departamentos agregados completos por correspondencias internas incompletas: '+', '.join(sorted(fallback))+'.'
   missing=[f'Resoluciones sin subcircuito: {no_code} votos'] if family=='salta' else []
   missing+=['Padrón inestable 2019–2023: '+u for u in unstable]
   add(f'{family}_'+('2019p_gob2023' if back else 'gob2023_'+key)+'_circuitos',tt,b,cfg,total,denom,missing)

 if (HERE/'chaco2025.pkl').exists():
  t,meta=raw_chaco(2025);total=float(t.values.sum());t=union_chaco(t,2025)
  b=union_chaco(national('2025','06'),2025)
  add('chaco_prov2025_dn2025_circuitos',t,b,dict(nombre='Chaco',distrito='06',serie='2025',fecha='11/05/2025',
   origen='Diputados provinciales 11/05/2025 (circuitos)',destino='Diputados nacionales 26/10/2025',nivel='circuitos y uniones',base='votos emitidos',
   fuente='https://resultados.electoralchaco.gob.ar/historico/15/cargos-provinciales/',nota='Definitivo por circuito. Se agrupan las seis parejas expresamente indicadas por el aviso del visor oficial; no se reparten votos.'),total)
 if (HERE/'corrientes2025.pkl').exists():
  d=pd.read_pickle(HERE/'corrientes2025.pkl')
  names=pd.read_pickle(HERE/'nombres_2025.pkl');names=names[names.distrito_id.eq('05')]
  audit=pd.read_csv(HERE/'correspondencias_corrientes2025.csv',dtype={'circuito':str})
  allowed=set(audit.loc[audit.empalme_admitido,'circuito'])
  national_bycode={code(r.circuito_id):r.seccion_nombre for r in names.itertuples()}
  assert names.circuito_id.is_unique
  for cargo,g in d.groupby('cargo'):
   t=g.drop(columns=['cargo','circuito','nombre','id_api']).copy()
   # Verificación nominal completa de los códigos se conserva para revisión.
   t.index=[unit(national_bycode[c],c) if c in national_bycode else 'PENDIENTE:'+c for c in g.circuito]
   t=t.loc[[c in allowed for c in g.circuito]]
   assert t.index.is_unique
   b=national('2025','05')
   add(f'corrientes_{cargo.lower()}_prov2025_dn2025_circuitos',t,b,dict(nombre='Corrientes',distrito='05',serie='2025',fecha='31/08/2025',
    origen=cargo+' 31/08/2025 (circuitos)',destino='Diputados nacionales 26/10/2025',nivel='circuitos',base='votos emitidos',
    fuente='https://elecciones2025-definitivo.corrientes.gob.ar/escrutinio',nota='Resultados por circuito del definitivo. Código electoral, título oficial y padrón cotejados con la DINE. Seis títulos genéricos de Capital y tres variantes ortográficas se admiten expresamente con padrón compatible; correspondencias completas exportadas. El circuito 62 no tiene votos nacionales informados. Diferencias mínimas entre circuitos y resumen general conservadas sin ajuste.'))
 t,meta=sf_raw(2025);b,unmatched,audit,denom,fallback=sf_national('2025',meta)
 t.index=[u.split(':')[0]+':DEPARTAMENTO' if u.split(':')[0] in fallback else u for u in t.index];t=t.groupby(level=0).sum()
 pd.DataFrame(audit).to_csv(HERE/'empalme_sf_2025.csv',index=False,encoding='utf-8-sig')
 add('santafe_prov2025_dn2025_circuitos',t,b,dict(nombre='Santa Fe',distrito='21',serie='2025',fecha='13/04/2025',
  origen='Convencionales 13/04/2025 (empalme territorial)',destino='Diputados nacionales 26/10/2025',nivel='distritos y departamentos empalmados',
  base='votos emitidos',fuente='https://www.santafe.gov.ar/tribunalelectoral/wp-content/uploads/sites/84/2025/07/resultadosPrimarias2025.ods',
  nota='Convencionales de distrito único. Santa Fe y Rosario están publicadas completas como 9999. Se agregan departamentos completos donde falte algún circuito nacional por empalmar; sólo se conservan distritos pequeños donde cierra la correspondencia. No se compara una localidad completa contra una fracción. Departamentos agregados: '+', '.join(sorted(fallback))+'.'),dest_total=denom)
 from misiones_municipios import preparar as preparar_misiones
 for year,keys in [(2023,['2019p','2023p','2023b']),(2025,['2025'])]:
  raw,match=preparar_misiones(year)
  for key in keys:
   t,b,fallback=match(key);back=key=='2019p'
   date='07/05/2023' if year==2023 else '08/06/2025'
   cargo='Gobernador' if year==2023 else 'Diputados provinciales'
   id_='misiones_'+('2019p_gob2023' if back else 'gob2023_'+key)+'_municipios' if year==2023 else 'misiones_prov2025_dn2025_municipios'
   source='https://www.electoralmisiones.gov.ar/wp-content/uploads/2023/05/Acta-Acuerdo-N%C2%B01166-Anexo-I.pdf' if year==2023 else 'https://www.electoralmisiones.gov.ar/wp-content/uploads/2025/09/Estadisticas-Elecciones-Legislativas-8-de-Junio-de-2025-1.pdf'
   add(id_,t,b,dict(nombre='Misiones',distrito='14',serie=str(year),fecha=date,
    origen='Presidente 2019' if back else cargo+' '+date+' (municipios empalmados)',
    destino=cargo+' '+date+' (municipios empalmados)' if back else 'Diputados nacionales 26/10/2025' if year==2025 else 'Presidente 22/10/2023' if key=='2023p' else 'Balotaje 19/11/2023',
    nivel='municipios y departamentos empalmados',base='votos emitidos',fuente=source,invertir=back,foco=['Frente Renovador de la Concordia'],
    nota='Resultado provincial observado por municipio; se agregan circuitos nacionales con la correspondencia explícita del mapa oficial de abril 2023. No son resultados observados por circuito provincial. Donde hay códigos nuevos o municipios sin equivalente previo, se agrega todo el departamento en ambos lados. Departamentos agregados: '+', '.join(sorted(fallback))+'. Fracrán tiene reserva de límites en el propio mapa. Se conservan las diferencias internas de publicación ya documentadas.'),float(raw.values.sum()))
 pd.to_pickle(bases,HERE/'bases.pkl')
 (HERE/'CONTROL_EMPALMES.json').write_text(json.dumps(controls,ensure_ascii=False,indent=2),encoding='utf8')
 return bases

if __name__=='__main__':construir()
