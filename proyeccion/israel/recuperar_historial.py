import requests, json, sys, hashlib
from pathlib import Path
import pandas as pd
p=Path('proyeccion/israel');out=p/'vivo_datos';hist=pd.read_csv(p/'vivo_historia.csv');seen=set(hist.urnas.astype(int));s=requests.Session();s.headers['User-Agent']='dataeleccproyecto local research';u='https://api.github.com/repos/smilganir/isr-socio-elections/commits';rr=s.get(u,params={'sha':'gh-pages','path':'results-snapshot/bundle.json','per_page':50},timeout=40);rr.raise_for_status();records=[]
for obj in rr.json():
 sha=obj['sha'];url='https://raw.githubusercontent.com/smilganir/isr-socio-elections/'+sha+'/results-snapshot/bundle.json';resp=s.get(url,timeout=100);resp.raise_for_status();b=resp.json();cov=b.get('coverage',{});n=int(cov.get('ballots_reporting',0));dt=cov.get('official_update','desconocida');rec={'commit':sha,'fecha_commit':obj['commit']['committer']['date'],'actualizacion':dt,'urnas':n,'sha256_bundle':hashlib.sha256(resp.content).hexdigest()}
 if n>=120 and n not in seen:
  rows=[]
  for v in b['kalpis_lookup'].values():
   k=v['kpi']
   if k.get('src')!='real_results':continue
   r={'סמל ישוב':int(v['semel']),'שם ישוב':v.get('name',''),'קלפי':float(v['kalpi']),'בזב':k['bzb'],'מצביעים':k['voted'],'כשרים':k['kosher']};r.update({x['code']:x['votes'] for x in k['parties']});rows.append(r)
  if len(rows)!=n:raise ValueError('Cobertura no coincide: '+str((n,len(rows))))
  hr=dt.split()[-1].replace(':','');dest=out/('expb_smilganir_rec_'+hr+'_'+sha[:7]+'.csv');pd.DataFrame(rows).fillna(0).to_csv(dest,index=False,encoding='utf-8-sig');seen.add(n);rec['csv']=str(dest);print('Recuperado',dt,n,dest.name,flush=True)
 else:print('Ya presente',dt,n,flush=True)
 records.append(rec)
(p/'historial_smilganir_recuperado.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf8')
