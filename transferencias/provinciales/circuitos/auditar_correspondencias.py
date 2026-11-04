"""Pruebas independientes de códigos, nombres y tamaño de los circuitos."""
import json
import re
from pathlib import Path
import pandas as pd
from empalmar import HERE,TR,norm,code,unit

def corrientes():
 d=pd.read_pickle(HERE/'corrientes2025.pkl');d=d[d.cargo.eq('Diputados')]
 n=pd.read_pickle(HERE/'nombres_2025.pkl');n=n[n.distrito_id.eq('05')].set_index('circuito_id')
 _,elect=pd.read_pickle(TR/'circ_2025.pkl');elect=elect.loc['05'].groupby(level='circuito').sum()
 rows=[]
 for r in d.itertuples():
  j=json.loads((HERE/f'fuentes/corrientes_circ_{r.id_api}.json').read_text(encoding='utf8'))['data']['header']
  label=n.loc[r.circuito,'circuito_nombre'] if r.circuito in n.index else ''
  normalized=lambda s:norm(re.sub(r'^\s*\d+[A-Z]?\s*-\s*','',s))
  p=normalized(j['titulo']);q=normalized(label)
  compatible=bool(q) and (p==q or (len(p)>5 and p in q) or (len(q)>5 and q in p))
  e=float(elect.get(r.circuito,0));ep=float(j['electores'])
  ratio=e/ep if ep else None
  generic=r.circuito in ['2A','3','5A','5B','6','7'] and p=='CAPITAL' and ratio is not None and .95<ratio<1.05
  spelling=r.circuito in ['27','37A','89'] and ratio is not None and .95<ratio<1.05
  rows.append(dict(circuito=r.circuito,nombre_provincial=j['titulo'].strip(),nombre_nacional=label,
   nombre_compatible=compatible,empalme_admitido=compatible or generic or spelling,
   reserva='Título provincial genérico de Capital; código y padrón compatibles' if generic else 'Variante explícita CTO/CTE, Echevarría/Echeverría o SECC/SECCION; código y padrón compatibles' if spelling else '',
   electores_provinciales=ep,electores_nacionales_informados=e,
   razon_padrones=ratio,mesas_provinciales=j['mesas'],metodo='código electoral y título oficial del circuito; control de padrón'))
 t=pd.DataFrame(rows)
 t.to_csv(HERE/'correspondencias_corrientes2025.csv',index=False,encoding='utf-8-sig')
 print('CORRESPONDENCIAS CORRIENTES',len(t),'nombres compatibles',int(t.nombre_compatible.sum()),
  'ratios',t.razon_padrones.quantile([0,.05,.5,.95,1]).to_dict(),flush=True)
 print('NOMBRES A REVISAR',t[~t.nombre_compatible][['circuito','nombre_provincial','nombre_nacional','razon_padrones']].to_dict('records'),flush=True)
 return t
if __name__=='__main__':corrientes()
