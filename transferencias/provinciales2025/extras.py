"""Fuentes territoriales complementarias, sin completar residuos."""
from pathlib import Path
import pandas as pd
from preparar import HERE, RAW

def santafe():
 d=pd.read_pickle(RAW/'sf_primarias2025.pkl')
 d['v']=pd.to_numeric(d['Convencional Reformador Distrito Único'])
 d['cat']=d.nombre_partido.str.strip()
 d.loc[d.partido.isin(['9998','9999']),'cat']='Blanco y nulo'
 t=d.pivot_table(index='nomsec',columns='cat',values='v',aggfunc='sum',fill_value=0)
 t=t.loc[:,t.sum()>0]
 assert int(t.values.sum())==1569465
 t.to_pickle(HERE/'prov_santafe.pkl')
 t.to_csv(HERE/'prov_santafe.csv',encoding='utf-8-sig')
 print('SANTA FE',t.shape,t.sum().to_dict())

def sanluis():
 # Transcripción del PDF oficial, páginas físicas 2–11. Copias OCR y
 # capturas conservadas para revisar cada celda; no se calcula residuo.
 # Orden: Ahora, PJ, Tercera, Viva, Justicia, MOVIPRO, PROCLAME,
 # Primero, NOS, Futuro, FIT, blanco, nulo.
 names=['Ahora San Luis','Frente Justicialista','Tercera Posición','¡Viva la Libertad! ¡Carajo!',
  'Frente por la Justicia Social','MOVIPRO','PROCLAME','Primero San Luis','NOS','San Luis Futuro','FIT-U','Blanco','Nulo']
 senate={
  'Ayacucho':[4353,4176,819,0,410,0,0,0,0,0,0,1487,828],
  'Belgrano':[1383,816,625,0,0,96,0,0,0,0,0,490,96],
  'Pedernera':[30285,10603,5117,8801,1467,679,758,0,0,0,0,4256,4090],
  'San Martín':[2463,937,0,0,0,0,0,0,0,0,0,80,78],
 }
 deputy={
  'Belgrano':[1180,856,808,0,0,86,0,0,0,0,0,467,109],
  'Gobernador Dupuy':[3094,2995,418,0,0,147,0,0,0,0,0,456,195],
  'Juan Martín de Pueyrredón':[48327,29068,7292,5678,1833,818,2434,4049,4180,2019,1637,6130,7049],
  'Junín':[7425,3205,1527,1329,450,797,0,1078,0,0,0,1793,1067],
  'Coronel Pringles':[2955,3116,623,0,0,430,0,301,0,0,0,843,540],
 }
 assert [sum(x[:11]) for x in deputy.values()]==[2930,6654,107335,15811,7425]
 assert [sum(x[:11]) for x in senate.values()]==[9758,2920,57710,3400]
 for cargo,rows in [('diputados',deputy),('senadores',senate)]:
  t=pd.DataFrame.from_dict(rows,orient='index',columns=names)
  t['Blanco y nulo']=t.pop('Blanco')+t.pop('Nulo')
  t=t.loc[:,t.sum()>0]
  t.to_pickle(HERE/('prov_sanluis_'+cargo+'.pkl'))
  t.to_csv(HERE/('prov_sanluis_'+cargo+'.csv'),encoding='utf-8-sig')
  print('SAN LUIS',cargo,t.shape)

if __name__=='__main__':
 santafe()
 sanluis()
