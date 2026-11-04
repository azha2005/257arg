"""Correspondencia explícita del mapa oficial de abril de 2023.

Fuente: Circuitos-Mnes-2023-Completo.pdf. Nunca se deriva pertenencia
municipal de un prefijo numérico: cada código está declarado aquí.
"""
from pathlib import Path
import json
import pandas as pd
from empalmar import HERE,TR,norm,unit,national
MAP={
 'Posadas':'1 2 3 3A 4 4A 4B 5 6 7 7A 7B 7C',
 'Garupá':'8 8A 8B 8C','Fachinal':'9','Apóstoles':'10 10A','San José':'11','Azara':'12 12A','Tres Capones':'13',
 'Santa Ana':'14','Candelaria':'15','Profundidad':'16','Cerro Corá':'17','Bonpland':'18','Mártires':'19','Loreto':'20',
 'Leandro N. Alem':'21','Olegario Víctor Andrade':'22','Cerro Azul':'23','Arroyo del Medio':'24','Dos Arroyos':'25',
 'Gobernador López':'26','Caá Yarí':'27','Almafuerte':'28','Concepción de la Sierra':'29 30','Santa María':'31',
 'San Javier':'32','Itacaruaré':'33','Mojón Grande':'34','Florentino Ameghino':'35 35A',
 'San Ignacio':'36','Corpus Christi':'37','Gobernador Roca':'38','Santo Pipó':'39','Hipólito Yrigoyen':'40',
 'General Urquiza':'41','Colonia Polana':'42','Jardín América':'43','Oberá':'44','General Alvear':'45',
 'Colonia Alberdi':'46','Campo Viera':'47','Campo Ramón':'48','Panambí':'49','Los Helechos':'50','Guaraní':'51','San Martín':'52',
 'Puerto Rico':'53','Puerto Leoni':'54 54A','Capioví':'55','Ruiz de Montoya':'56','Garuhapé':'57','El Alcázar':'58',
 'Dos de Mayo':'59 59B','Campo Grande':'60','Aristóbulo del Valle':'61 61B','Salto Encantado':'61A',
 'Alba Posse':'62','25 de Mayo':'63','Colonia Aurora':'64 64A 64B','Montecarlo':'65','Caraguatay':'66 66A','Puerto Piray':'67',
 'El Soberbio':'68 68A 68B 68C 68D','San Vicente':'59A','Fracran':'68E',
 'Eldorado':'69 70','9 de Julio':'71','Santiago de Liniers':'72','Colonia Victoria':'73','Colonia Delicia':'74',
 'San Pedro':'75 75A 76','Pozo Azul':'76A','Puerto Esperanza':'77','Colonia Wanda':'78','Libertad':'79','Puerto Iguazú':'80',
 'Bernardo de Irigoyen':'81','San Antonio':'82','Comandante Andresito':'82A',
}

def preparar(year):
 corr=pd.read_csv(TR/'provinciales2023/correspondencias_misiones.csv')
 depts={norm(r.unidad):norm(r.departamento) for r in corr.itertuples()}
 depts.update({'ITACARUARE':'SANJAVIER','FRACRAN':'GUARANI','CONCEPCIONDELASIERRA':'CONCEPCION'})
 # Nombres administrativos abreviados de la DINE.
 aliases={'GENERALMBELGRANO':'GENERALMANUELBELGRANO','LNALEM':'LEANDRONALEM','CONCEPCIONDELASIERRA':'CONCEPCION','LIBGENERALSANMARTIN':'LIBERTADORGENERALSANMARTIN'}
 codes={}
 rows=[]
 for name,seq in MAP.items():
  dep=depts[norm(name)]
  if norm(name)=='SANMARTIN':dep='LIBERTADORGENERALSANMARTIN'
  for c in seq.split():
   assert c not in codes
   codes[c]=(dep,norm(name));rows.append(dict(circuito=c,municipio=name,departamento=dep,fuente='Mapa oficial abril 2023'))
 pd.DataFrame(rows).to_csv(HERE/'misiones_circuitos_municipios.csv',index=False,encoding='utf-8-sig')
 if year==2023:
  raw=pd.read_pickle(TR/'provinciales2023/prov_misiones.pkl')
  t=raw[['71','644','653','654','900','901','902','903','blancos','nulos']].copy()
  t['Blanco y nulo']=t.pop('blancos')+t.pop('nulos')
  t=t.rename(columns={'900':'Frente Renovador de la Concordia','901':'Juntos por el Cambio','902':'La Fuerza de Todos','903':'Frente Amplio','71':'Partido del Obrero','644':'Integración y Militancia','653':'Por la Vida y los Valores','654':'Partido Demócrata'})
 else:t=pd.read_pickle(TR/'provinciales2025/prov_misiones.pkl')
 t.index=[depts.get(norm(n),'LIBERTADORGENERALSANMARTIN' if norm(n)=='SANMARTIN' else '')+':'+norm('Itacaruaré' if n=='ltacaruaré' else n) for n in t.index]
 def match(key):
  b=national(key,'14')
  transformed=[];fallback=set();records=[]
  for u in b.index:
   dep,c=u.split(':');dep=aliases.get(dep,dep)
   found=codes.get(c)
   if found and found[0]==dep:target=found[0]+':'+found[1]
   else:target=None;fallback.add(dep)
   transformed.append(target);records.append(dict(unidad_nacional=u,unidad_municipal=target))
  # Si una municipalidad nueva no tiene circuito propio en un año previo,
  # se usa todo su departamento en ambas elecciones. No se rellena ni se
  # adjudica arbitrariamente al municipio vecino.
  represented=set(m for m in transformed if m is not None)
  fallback.update(u.split(':')[0] for u in t.index if u not in represented)
  transformed=[aliases.get(u.split(':')[0],u.split(':')[0])+':DEPARTAMENTO' if aliases.get(u.split(':')[0],u.split(':')[0]) in fallback else m for u,m in zip(b.index,transformed)]
  b.index=transformed;b=b[b.index.notna()].groupby(level=0).sum()
  a=t.copy();a.index=[u.split(':')[0]+':DEPARTAMENTO' if u.split(':')[0] in fallback else u for u in a.index];a=a.groupby(level=0).sum()
  pd.DataFrame(records).to_csv(HERE/f'empalme_misiones_{year}_{key}.csv',index=False,encoding='utf-8-sig')
  return a,b,fallback
 return t,match

if __name__=='__main__':
 for year,keys in [(2023,['2019p','2023p','2023b']),(2025,['2025'])]:
  t,match=preparar(year)
  for k in keys:
   a,b,fallback=match(k);print('MISIONES',year,k,len(a),len(b),sorted(fallback),a.index.difference(b.index).tolist())
