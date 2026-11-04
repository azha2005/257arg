import json
from pathlib import Path
import pandas as pd
p=Path('proyeccion/fotos_18_19'); names=json.loads((p/'inventario.json').read_text(encoding='utf8'))['unicas']
# Orden: LLA, FP, PU, FIT, OTRAS, blancos, nulos, otros no positivos.
# Los valores son lectura manual de las fotos, no votos copiados del provisorio.
items=[
(0,'04',8,'106','5023',[107,7,70,1,42,4,8,0]),
(1,'21',1,'202','1074',[105,57,36,1,19,0,6,0]),
(2,'12',1,'1E','61',[88,55,7,6,22,2,3,2]),
(3,'21',6,'1580','2422',[83,56,49,3,20,12,10,0]),
(4,'19',3,'40','1012',[134,13,6,0,3,4,4,0]),
(6,'02',122,'1000','426',[123,88,6,15,28,1,4,0]),
(7,'02',50,'365C','550',[130,57,12,8,29,0,7,0]),
(8,'12',1,'1M','306',[88,57,8,1,17,3,7,0]),
(10,'02',114,'955A','44',[24,13,4,3,4,0,1,0]),
(11,'05',12,'72','2130',[80,77,57,0,12,2,6,0]),
(13,'02',60,'444','101',[135,75,7,8,19,5,5,0]),
(16,'21',13,'3344','5401',[61,57,27,5,30,2,16,0]),
(19,'04',1,'9F','1158',[83,24,37,11,54,2,3,0]),
(22,'02',61,'635A','2030',[71,119,2,18,16,2,8,0]),
(25,'05',8,'49','1835',[36,37,28,0,1,0,3,0]),
(26,'02',119,'337A','48',[87,84,2,17,25,1,4,0]),
(28,'02',61,'635B','2414',[65,91,1,18,22,2,3,1]),
(30,'02',36,'291','632',[93,79,7,11,61,1,8,0]),
(31,'21',5,'1180','1940',[133,24,44,1,18,8,13,0]),
(33,'14',1,'2','72',[104,17,0,0,97,1,3,0]),
(38,'11',15,'57','549',[115,93,21,7,4,2,3,0]),
(39,'21',8,'2100','2753',[75,45,36,4,13,5,14,0]),
(42,'11',15,'57','525',[128,102,17,1,3,2,5,0]),
(43,'05',1,'4','132',[130,26,64,0,6,1,2,0]),
(44,'11',15,'57','562',[101,120,21,2,4,2,7,0]),
(45,'23',12,'142','2638',[103,158,5,8,18,5,2,0]),
(46,'02',19,'164','23',[123,80,6,3,26,7,8,0]),
(49,'03',3,'30','722',[66,74,9,3,8,9,1,0]),
(50,'01',5,'65','2199',[98,75,18,22,17,15,2,0]),
]
rows=[]
for idx,d,s,c,mesa,vals in items:
 for bloc,v in zip(['LLA','FP','PU','FIT','OTRAS','BLANCO','NULO','OTROS'],vals):
  rows.append(dict(foto=names[idx],distrito_id=d,seccion_id=s,circuito=c,mesa=mesa,completa='si',lista=bloc,bloque='NULO' if bloc=='OTROS' else bloc,votos=v,detalle_listas='no'))
# Acta parcialmente escrita: no presumir que las filas vacías equivalen a cero.
for bloc,v in [('LLA',92),('FP',63),('PU',39),('FIT',4)]:
 rows.append(dict(foto=names[17],distrito_id='21',seccion_id=13,circuito='3060',mesa='3765',completa='no',lista=bloc,bloque=bloc,votos=v,detalle_listas='no'))
a=pd.DataFrame(rows);a.to_csv(p/'actas.csv',index=False,encoding='utf-8-sig')
# Comparación informativa posterior. Los votos de entrada nunca se sustituyen.
m=pd.read_pickle('proyeccion/mesas_2025bl.pkl');out=[]
for idx,d,s,c,mesa,vals in items:
 q=m[(m.distrito_id==d)&(m.seccion_id==s)&(m.circuito==c)&(m.mesa_id.astype(str)==mesa)]
 for k,v in zip(['LLA','FP','PU','FIT','OTRAS','BLANCO','NULO','OTROS'],vals):
  official=int(q.iloc[0][k]) if len(q)==1 else None
  out.append(dict(foto=names[idx],distrito=d,seccion=s,circuito=c,mesa=mesa,bloque=k,foto_votos=v,provisorio=official,diferencia=None if official is None else v-official))
q=m[(m.distrito_id=='21')&(m.seccion_id==13)&(m.circuito=='3060')&(m.mesa_id.astype(str)=='3765')]
for k,v in [('LLA',92),('FP',63),('PU',39),('FIT',4)]:
 official=int(q.iloc[0][k]) if len(q)==1 else None
 out.append(dict(foto=names[17],distrito='21',seccion=13,circuito='3060',mesa='3765',bloque=k,foto_votos=v,provisorio=official,diferencia=None if official is None else v-official))
pd.DataFrame(out).to_csv(p/'control_provisorio.csv',index=False,encoding='utf-8-sig')
print('mesas',len(items)+1,'circuitos',len(set((d,s,c) for _,d,s,c,_,_ in items)|{('21',13,'3060')}))
print(pd.DataFrame(out).query('diferencia != 0').to_string(index=False))
