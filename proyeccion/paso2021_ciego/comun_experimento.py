"""Adaptador al motor congelado; no contiene resultados del destino."""
from pathlib import Path
import sys,contextlib
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent
FROZEN=HERE.parent/'congelado_20261028/codigo'
sys.path.insert(0,str(FROZEN))
import fotos_modelo as fm
import fotos_motor as motor
from proyectar_fotos import normalizar_actas
from enlace import alinear
from config import FORCES,KEY,SCHEMES,SEED
INPUT=HERE/'permitidos'
CACHE={}
FRAMES={}
SELECT_CACHE={}

def loader(year):
 if year in CACHE:return CACHE[year]
 if int(year)>2019:raise ValueError('Origen posterior al corte temporal')
 w=pd.read_pickle(INPUT/('mesas_'+year+'.pkl'))
 keys=KEY[:3]
 g=w.groupby(keys)[FORCES+['e','BLANCO','NULO','OTROS']].sum()
 nm=w.groupby(keys).size()
 v=g[FORCES].copy();v['BLANCO/NULO']=g[['BLANCO','NULO','OTROS']].sum(1)
 e=np.maximum(g.e,v.sum(1));v['ABSTENCION']=e-v.sum(1)
 P=v.div(e,axis=0)
 CACHE[year]=(P,e,nm)
 return CACHE[year]

def frame(year):
 if year not in FRAMES:FRAMES[year]=pd.read_pickle(INPUT/('marco_'+year+'.pkl')).groupby(KEY[:3],as_index=False).e.sum()
 return FRAMES[year]

def fit(a,origins,year,lam=.1,factor=1.4,boot=0,seed=0,weighted=True):
 ant={o:{f:[f] for f in FORCES} for o in origins}
 original=fm.poststrat
 if not weighted:fm.poststrat=lambda e,s,share:np.asarray(e,dtype=float)
 try:
  return motor.calcular(a,','.join(origins),loader,normalizar_actas,ant,nboot=boot,seed=seed,
    fuerzas=FORCES,marco=frame(year),lam=lam,factor=factor)
 finally:fm.poststrat=original

def raw(a,year,weighted=False):
 a=normalizar_actas(a)
 units=a.drop_duplicates('mesa_key'); e=[];Y=[]
 P,E,N=loader('2019' if year=='2021_paso' else '2017' if year=='2019' else '2015')
 hist=P.index.to_frame(index=False);hist['avg']=E.to_numpy()/N.reindex(E.index).to_numpy()
 av,_=alinear(units,hist,['avg'],N.reindex(E.index).to_numpy(),motor.NIVELES)
 for i,(_,r) in enumerate(units.iterrows()):
  votes=a[a.mesa_key==r.mesa_key].groupby('bloque').votos.sum()
  em=max(float(av[i,0]),votes.sum());e.append(em)
  Y.append([votes.get(f,0)/em if r.completa=='si' or f in votes else np.nan for f in FORCES])
 Y=np.array(Y); e=np.array(e); sf=fm.region(units.distrito_id,units.seccion_id,'amba')
 fr=frame(year);sr=fm.region(fr.distrito_id,fr.seccion_id,'amba')
 share=pd.Series(fr.e.to_numpy()).groupby(sr).sum().pipe(lambda t:t/t.sum()).to_dict()
 v=[]
 for j in range(len(FORCES)):
  seen=np.isfinite(Y[:,j]);w=e[seen]
  if weighted:w=fm.poststrat(w,sf[seen],share)
  v.append(np.average(Y[seen,j],weights=w))
 v=np.maximum(v,0);return 100*v/sum(v)

def select(year,scheme,rep):
 if year not in SELECT_CACHE:
  f=pd.read_pickle(INPUT/('marco_'+year+'.pkl'))
  ready=np.load(INPUT/('disponibilidad_'+year+'.npy'))
  f=f.loc[ready].reset_index().rename(columns={'index':'row'})
  SELECT_CACHE[year]=f
 f=SELECT_CACHE[year]
 rng=np.random.default_rng(SEED+int(year[:4])*100000+SCHEMES.index(scheme)*10000+rep)
 idx=np.arange(len(f));amba=fm.region(f.distrito_id,f.seccion_id,'amba')=='AMBA'
 groups=f.groupby(KEY[:3],sort=True).indices
 if scheme=='azar':chosen=rng.choice(idx,30,replace=False)
 elif scheme=='padron_distrito':
  weights=f.groupby('distrito_id').e.sum();shares=30*weights/weights.sum();n=np.floor(shares).astype(int)
  n.loc[(shares-n).sort_values(ascending=False,kind='stable').index[:30-n.sum()]]+=1
  chosen=np.concatenate([rng.choice(np.flatnonzero(f.distrito_id==d),int(k),replace=False) for d,k in n.items() if k])
 elif scheme=='racimos':
  eligible=[v for v in groups.values() if len(v)>=3]
  chosen=np.concatenate([rng.choice(eligible[i],3,replace=False) for i in rng.choice(len(eligible),10,replace=False)])
 elif scheme in ['twitter','twitter_parcial']:
  # Misma selección para ambas; cambia únicamente la información revelada.
  rng=np.random.default_rng(SEED+int(year[:4])*100000+SCHEMES.index('twitter')*10000+rep)
  ia=np.flatnonzero(amba);ir=np.flatnonzero(~amba);chosen=[]
  for n in [10,3,3]:
   j=int(rng.choice(ia));r=f.iloc[j];g=groups[tuple(r[k] for k in KEY[:3])]
   available=g[~np.isin(g,chosen)];chosen.extend(rng.choice(available,min(n,len(available)),replace=False))
  chosen.extend(rng.choice(ia[~np.isin(ia,chosen)],20-len(chosen),replace=False))
  chosen.extend(rng.choice(ir,10,replace=False));chosen=np.array(chosen)
 elif scheme=='geografico':
  # Usa solamente tamaño del circuito, nunca un voto del destino.
  size=f.groupby(KEY[:3]).e.transform('sum').to_numpy()
  pool=idx[size<=np.quantile(size,.2)];chosen=rng.choice(pool,30,replace=False)
 elif scheme=='sesgo_historico':
  origin='2019' if year=='2021_paso' else '2017' if year=='2019' else '2015'
  P,E,N=loader(origin);h=P.index.to_frame(index=False);h['FDT_share']=(P.FDT/P[FORCES].sum(1).replace(0,np.nan)).fillna(0).to_numpy()
  v,_=alinear(f,h,['FDT_share'],E.to_numpy(),motor.NIVELES)
  pool=idx[v[:,0]>=np.quantile(v[:,0],.8)];chosen=rng.choice(pool,30,replace=False)
 else:raise ValueError(scheme)
 if len(chosen)!=30 or len(set(chosen))!=30:raise AssertionError('Se requieren 30 mesas únicas')
 return f.iloc[chosen].row.to_numpy(dtype=int)

def reveal(table,indices,scheme):
 rows=[]
 for i,r in enumerate(table.iloc[indices].itertuples(index=False)):
  partial=scheme=='twitter_parcial' and i<10
  for f in FORCES+['BN']:
   if partial and f not in ['JXC','FDT']:continue
   rows.append(dict(foto='acta_'+str(i),distrito_id=r.distrito_id,seccion_id=r.seccion_id,circuito=r.circuito,
    mesa=r.mesa_id,mesa_tipo=r.mesa_tipo,completa='no' if partial else 'si',lista=f,bloque=f,
    votos=float(getattr(r,f)) if f!='BN' else float(r.BLANCO+r.NULO+r.OTROS),detalle_listas='no'))
 return pd.DataFrame(rows)
