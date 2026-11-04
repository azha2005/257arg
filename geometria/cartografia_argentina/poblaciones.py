from pathlib import Path
import json,requests,concurrent.futures as cf
ROOT=Path(__file__).resolve().parent;META=ROOT/'metadatos'
s=(META/'poblaciones_app.txt').read_text(encoding='utf-8')
for needle in ['GetSelectedBoundary','GetConfiguration','name:"boundaryDownload"']:
    m=s.find(needle);print(needle,s[max(0,m-350):m+1500],flush=True)
server=json.loads((META/'poblaciones_transaction.json').read_text(encoding='utf-8'))['Server']
jobs=[('poblaciones_config_real',server+'/services/GetConfiguration'),('poblaciones_boundary19_real',server+'/services/boundaries/GetSelectedBoundary?a=19'),('poblaciones_boundary2_real',server+'/services/boundaries/GetSelectedBoundary?a=2')]
def f(a):
    n,u=a
    try:
        r=requests.get(u,timeout=(10,25));(META/(n+'.json')).write_text(r.text,encoding='utf-8');print(n,r.status_code,len(r.content),r.text[:700],flush=True)
    except Exception as e:print(n,e,flush=True)
with cf.ThreadPoolExecutor(3) as ex:list(ex.map(f,jobs))
