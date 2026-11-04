"""Las actas reales de Twitter: referencia conservada y procedimiento corregido."""
import sys,json,types,contextlib,io
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;PROY=HERE.parent
sys.path.insert(0,str(PROY))
version=sys.argv[1]
if version=='antes':
    for name in ['fotos_modelo','congreso','proyectar_fotos']:
        m=types.ModuleType(name);m.__file__=str(PROY/(name+'.py'));sys.modules[name]=m
        exec(compile((HERE/'baseline'/(name+'.py')).read_text(encoding='utf-8'),m.__file__,'exec'),m.__dict__)
import proyectar_fotos as pf
import congreso as cg
import fotos_modelo as fm

a=pf.leer(PROY/'fotos25/actas.csv')
m=pd.read_pickle(PROY/'mesas_2025bl.pkl')
frame=m.groupby(['distrito_id','seccion_id','circuito'],as_index=False).e.sum()
kw=dict(marco=frame) if version=='despues' else {}
R=pf.calcular(a,'2023p,2021bl',nboot=2000,seed=0,**kw)
blocs=R['blocs'];F=R['F']
truth=100*m[blocs].sum()/m[blocs].sum().sum()

def summary(R):
    j,k=blocs.index('LLA'),blocs.index('FP');margin=R['bs'][:,j]-R['bs'][:,k]
    return dict(punto=dict(zip(blocs,R['pt'])),lo=dict(zip(blocs,R['lo'])),hi=dict(zip(blocs,R['hi'])),
                margen=float(R['pt'][j]-R['pt'][k]),banda_margen=np.percentile(margin,[2.5,97.5]).tolist())

base=summary(R)
if version=='antes':
    D=R['proj_d'](np.arange(len(F)))[blocs]
    corrected,_=cg.provinciales(D,2025,a)
    _,tot=cg.repartir(corrected,2025,R['pad'])
    raw=fm.bootstrap(lambda k:R['proj_d'](k)[blocs].to_numpy(),R['clus'],300,R['rng'])
    raw=np.maximum(D.to_numpy()[None]+pf.FACTOR*(raw-raw.mean(0)),0)
    seats=[]
    for b in raw:
        d,_=cg.provinciales(pd.DataFrame(b,index=D.index,columns=blocs),2025,a,R['rng'])
        seats.append(cg.repartir(d,2025,R['pad'])[1])
    S=pd.DataFrame(seats).fillna(0)
    joint=None
else:
    C=cg.distribucion(R,2025,nboot=300);tot,S=C['tot'],C['S'];joint=summary(R)
true_seats=cg.electos(2025)[1]
result=dict(version=version,actas=len(F),circuitos=len(np.unique(R['clus'])),real=truth.to_dict(),
            real_margen=float(truth.LLA-truth.FP),sin_prior_provincial=base,con_prior_provincial=joint,
            bancas=tot,bandas_bancas={f:np.percentile(S.get(f,pd.Series([0.])),[5,95]).tolist() for f in true_seats},
            bancas_reales=true_seats)
(HERE/('twitter_real_'+version+'.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
