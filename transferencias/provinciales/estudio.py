"""Estimaciones provinciales RxC, CV territorial, sensibilidad y bootstrap.

Cada provincia se ajusta por separado. Los conteos son equivalentes en la
base de destino, como en estimar.py; las columnas son flujos modelados y
no se confunden con los márgenes observados, que se exportan aparte.
"""
from pathlib import Path
import os
# Los sistemas suficientes tienen pocas categorías; BLAS multihilo dentro
# de cuatro remuestreos simultáneos sobrecarga la CPU sin mejorar el ajuste.
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import concurrent.futures as cf
import json
import hashlib
import inspect
import sys
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
TR=HERE.parent
sys.path.insert(0,str(TR))
from rxc_calvo import fit

LAMBDAS=[.001,.0001,.00001,.000001,.0000001]


def cv_fit(X,Y,w):
    # Folds deterministas con al menos dos unidades de validación cuando
    # el número de departamentos es pequeño.
    rng=np.random.default_rng(114)
    folds=np.arange(len(X))%min(5,max(2,len(X)//3))
    rng.shuffle(folds)
    errors={}
    for lam in LAMBDAS:
        num=den=0.
        for f in np.unique(folds):
            tr=folds!=f;te=~tr
            B=fit(X[tr],Y[tr],const=lam*tr.sum(),w=w[tr])
            num+=(w[te,None]*(X[te]@B-Y[te])**2).sum()
            den+=w[te].sum()
        errors[lam]=num/den
    lam=max(k for k,v in errors.items() if v<=min(errors.values())*1.01)
    return lam,errors


def bootstrap_one(args):
    X,Y,w,lam,seed=args
    rng=np.random.default_rng(seed)
    ids=rng.integers(0,len(X),len(X))
    return fit(X[ids],Y[ids],const=lam*len(X),w=w[ids])


def calcular(a,b,cfg,nboot=200):
    assert a.index.equals(b.index)
    assert (a.values>=0).all() and (b.values>=0).all()
    good=(a.sum(1)>0)&(b.sum(1)>0)
    a,b=a[good],b[good]
    rows,cols=a.columns.tolist(),b.columns.tolist()
    X=a.div(a.sum(1),axis=0).values;Y=b.div(b.sum(1),axis=0).values
    w=b.sum(1).values;w=w/w.mean()
    lam,cv=cv_fit(X,Y,w)
    B=fit(X,Y,const=lam*len(X),w=w)
    C=fit(X,Y,const=.001) # comparación con la variante sin pesos del proyecto
    # Sensibilidad adicional a elegir lambda y a eliminar una unidad.
    alternatives=[C]+[fit(X,Y,const=l*len(X),w=w) for l in LAMBDAS]
    alternatives += [fit(np.delete(X,i,0),np.delete(Y,i,0),const=lam*(len(X)-1),w=np.delete(w,i)) for i in range(len(X))]
    alt=np.stack(alternatives)
    with cf.ThreadPoolExecutor(4) as pool:
        boot=np.stack(list(pool.map(bootstrap_one,[(X,Y,w,lam,s) for s in range(1100,1100+nboot)])))
    lo,hi=np.quantile(boot,[.05,.95],axis=0)
    mass=(X*b.sum(1).values[:,None]).sum(0)
    M=B*mass[:,None];MC=C*mass[:,None]
    real=b.sum().values
    marginal=real/real.sum()
    warnings=[]
    singular=np.linalg.svd(X,compute_uv=False)
    rank=int(np.linalg.matrix_rank(X))
    condition=float(singular[0]/singular[-1]) if singular[-1]>1e-14 else None
    for i,r in enumerate(rows):
        diff=float(abs(B[i]-C[i]).max()*100)
        sens=float((alt[:,i,:].max(0)-alt[:,i,:].min(0)).max()*100)
        width=float((hi[i]-lo[i]).max()*100)
        sep=float(abs(B[i]-marginal).sum()*50)
        weight=float(mass[i]/mass.sum()*100)
        unidentified=diff>30 or (weight<5 and diff>20) or width>40 or rank<len(rows) or len(X)<max(10,2*len(rows)) or sens>35
        warnings.append(dict(origen=r,peso=round(weight,2),dif_variante_pp=round(diff,2),sensibilidad_pp=round(sens,2),
            ancho_intervalo_pp=round(width,2),separacion_pp=round(sep,2),no_identificada=unidentified))
    pred=X@B
    error=(pred-Y)*100
    ctl=dict(cfg,unidades=len(a),categorias_origen=len(rows),rango=rank,condicion=condition,lambda_=lam,
        validacion_cruzada={str(k):float(v) for k,v in cv.items()},bootstrap=nboot,intervalo_percentiles=[5,95],
        rmse_pp=float(np.sqrt(np.average(error**2,weights=w,axis=0)).mean()),
        desviacion_max_margen_destino_pp=float(abs(M.sum(0)/M.sum()-marginal).max()*100),
        electores_o_votos_origen=float(a.values.sum()),electores_o_votos_destino=float(b.values.sum()),
        filas=warnings,unidad_conteos='equivalentes en la base de destino; no son personas observadas',
        reservas=['Inferencia ecológica: resultados territoriales, sin seguimiento individual.',
            'El bootstrap no mide el sesgo por heterogeneidad territorial ni por cambios de padrón.',
            'Los márgenes de destino del Sankey son modelados; los observados se muestran aparte.',
            'Las filas con asterisco no permiten una atribución precisa de destinos.'])
    folder=HERE/'resultados'/cfg['id'];folder.mkdir(parents=True,exist_ok=True)
    for name,t in [('origen_observado',a),('destino_observado',b),('matriz_votos',pd.DataFrame(M,index=rows,columns=cols)),
        ('matriz_pct',pd.DataFrame(B*100,index=rows,columns=cols)),('variante_pct',pd.DataFrame(C*100,index=rows,columns=cols)),
        ('intervalo_p05',pd.DataFrame(lo*100,index=rows,columns=cols)),('intervalo_p95',pd.DataFrame(hi*100,index=rows,columns=cols))]:
        t.to_csv(folder/(name+'.csv'),encoding='utf-8-sig')
    (folder/'control.json').write_text(json.dumps(ctl,ensure_ascii=False,indent=2),encoding='utf8')
    return dict(**ctl,rows=rows,cols=cols,matriz=M.round(3).tolist(),variante=MC.round(3).tolist(),
        pct=(B*100).round(3).tolist(),p05=(lo*100).round(2).tolist(),p95=(hi*100).round(2).tolist(),
        observado_destino=(marginal*100).round(3).tolist())


if __name__=='__main__':
    bases={}
    for folder in ['provinciales2023','provinciales2025','provinciales/circuitos']:
        f=TR/folder/'bases.pkl'
        if f.exists():bases.update(pd.read_pickle(f))
    out=[]
    for k,(a,b,c) in bases.items():
        cached=HERE/'resultados'/k/'resultado.json'
        model=inspect.getsource(calcular)+inspect.getsource(cv_fit)+inspect.getsource(bootstrap_one)+(TR/'rxc_calvo.py').read_text(encoding='utf8')
        signature=hashlib.sha256((a.to_csv()+b.to_csv()+json.dumps(c,sort_keys=True)+model).encode()).hexdigest()
        if cached.exists() and json.loads(cached.read_text(encoding='utf8')).get('firma_insumos')==signature:
            j=json.loads(cached.read_text(encoding='utf8'))
        else:
            print('Estimando',k,a.shape,b.shape,flush=True)
            j=calcular(a,b,c)
            j['firma_insumos']=signature
            cached.write_text(json.dumps(j,ensure_ascii=False),encoding='utf8')
        out.append(j)
        print(k,'listo',j['rmse_pp'],'filas inciertas',sum(x['no_identificada'] for x in j['filas']),flush=True)
    (HERE/'resultados.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
