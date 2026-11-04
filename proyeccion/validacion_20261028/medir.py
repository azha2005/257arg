"""Comparacion emparejada del pipeline operativo con exactamente 30 mesas.

python -X utf8 proyeccion/validacion_20261028/medir.py --version antes --reps 100 --boot 200
python -X utf8 proyeccion/validacion_20261028/medir.py --version despues --reps 100 --boot 200
No usa las actas reales para elegir parametros. Guarda cada fuerza, margen y banda.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import argparse, contextlib, io, json, sys, time, types, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
PROY=HERE.parent
sys.path.insert(0,str(PROY))
parser=argparse.ArgumentParser()
parser.add_argument('--version',choices=['antes','despues'],required=True)
parser.add_argument('--reps',type=int,default=100)
parser.add_argument('--boot',type=int,default=200)
parser.add_argument('--destinos',default='2025bl,2023p,2023b,2015b')
parser.add_argument('--bancas',action='store_true')
parser.add_argument('--factor',type=float,default=1.4)
parser.add_argument('--tag',default='')
args=parser.parse_args()
if args.version=='antes':
    for name in ['fotos_modelo','congreso','proyectar_fotos']:
        module=types.ModuleType(name)
        module.__file__=str(PROY/(name+'.py'))
        sys.modules[name]=module
        source=(HERE/'baseline'/(name+'.py')).read_text(encoding='utf-8')
        exec(compile(source,module.__file__,'exec'),module.__dict__)
import proyectar_fotos as pf
import fotos_modelo as fm
import congreso as cg

KEY=['distrito_id','seccion_id','circuito','mesa_id','mesa_tipo']
FIX=['e','BLANCO','NULO','OTROS']
ANT={
 '2023p':{'LLA':['LA LIBERTAD AVANZA','JUNTOS POR EL CAMBIO'],'FP':['UNION POR LA PATRIA'],
          'PU':['HACEMOS POR NUESTRO PAIS'],'FIT':['FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD']},
 '2021bl':{'LLA':['LLA','JxC'],'FP':['FdT'],'PU':['Tercera Via']}}
ANT2023={
 '2019p':{'UNION POR LA PATRIA':['FRENTE DE TODOS'],'LA LIBERTAD AVANZA':['FRENTE NOS','UNITE POR LA LIBERTAD Y LA DIGNIDAD'],
          'HACEMOS POR NUESTRO PAIS':['CONSENSO FEDERAL']},
 '2021bl':{'UNION POR LA PATRIA':['FdT'],'JUNTOS POR EL CAMBIO':['JxC'],'LA LIBERTAD AVANZA':['LLA'],
          'HACEMOS POR NUESTRO PAIS':['Tercera Via'],'FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD':['FIT']}}


def muestra(m,rng,scheme):
    if scheme=='azar':
        return rng.choice(len(m),30,replace=False)
    amba=fm.region(m.distrito_id,m.seccion_id,'amba')=='AMBA'
    groups=m.groupby(['distrito_id','seccion_id','circuito']).indices
    ia=np.flatnonzero(amba);ir=np.flatnonzero(~amba)
    chosen=[]
    for size in (10,3,3):
        i=int(rng.choice(ia));r=m.iloc[i]
        group=np.array(groups[(r.distrito_id,r.seccion_id,r.circuito)])
        avail=group[~np.isin(group,chosen)]
        chosen.extend(rng.choice(avail,min(size,len(avail)),replace=False).tolist())
    chosen.extend(rng.choice(ia[~np.isin(ia,chosen)],20-len(chosen),replace=False).tolist())
    chosen.extend(rng.choice(ir,10,replace=False).tolist())
    assert len(set(chosen))==30
    return np.array(chosen)


def actas(sub,forces,scheme,top):
    rows=[]
    for i,(_,r) in enumerate(sub.iterrows()):
        partial=scheme=='twitter_parcial' and i<10
        for f in forces+['BN']:
            if partial and f not in top:
                continue
            rows.append(dict(foto='sim_'+str(i),distrito_id=r.distrito_id,seccion_id=int(r.seccion_id),
                             circuito=str(r.circuito),mesa=str(r.mesa_id),completa='no' if partial else 'si',
                             bloque=f,lista=f,detalle_listas='no',
                             votos=float(r[f]) if f!='BN' else float(r[['BLANCO','NULO','OTROS']].sum())))
    a=pd.DataFrame(rows)
    # Formato original para la version de referencia; el nuevo normaliza por identidad electoral.
    a['mesa_key']=a.foto+'|'+a.distrito_id+'|'+a.seccion_id.astype(str)+'|'+a.circuito+'|'+a.mesa
    return a


def legacy_seats(R):
    blocs,F,clus=R['blocs'],R['F'],R['clus']
    d=R['proj_d'](np.arange(len(F)))[blocs]
    pt,_=cg.provinciales(d,2025,R['actas'])
    _,tot=cg.repartir(pt,2025,R['pad'])
    bs=fm.bootstrap(lambda k:R['proj_d'](k)[blocs].to_numpy(),clus,args.boot,R['rng'])
    bs=np.maximum(d.to_numpy()[None]+pf.FACTOR*(bs-bs.mean(0)),0)
    seats=[]
    for b in bs:
        x,_=cg.provinciales(pd.DataFrame(b,index=d.index,columns=blocs),2025,R['actas'],R['rng'])
        seats.append(cg.repartir(x,2025,R['pad'])[1])
    return tot,pd.DataFrame(seats).fillna(0)


def metrics(R,real,top,common):
    b=R['blocs']; idx=[b.index(t) for t in top]
    pt=R['pt']; bs=R['bs']; margin=pt[idx[0]]-pt[idx[1]]
    ok=bool(np.isfinite(bs).all() and np.isfinite(pt).all())
    if args.version=='despues':ok=ok and R['inferencia_valida']
    mb=bs[:,idx[0]]-bs[:,idx[1]]
    low,high=np.percentile(mb,[2.5,97.5]) if ok else (np.nan,np.nan)
    rm=real[top[0]]-real[top[1]]
    probability=float((mb>0).mean()) if ok else np.nan
    side=(margin-low) if margin>rm else (high-margin)
    z=abs(margin-rm)/max(side,1e-12) if ok else np.nan
    rows=[]
    for j,f in enumerate(b):
        rows.append(dict(**common,fuerza=f,punto=pt[j],real=real[f],error=pt[j]-real[f],
                         lo=R['lo'][j] if ok else np.nan,hi=R['hi'][j] if ok else np.nan,
                         disponible=ok,cubre=bool(ok and R['lo'][j]<=real[f]<=R['hi'][j])))
    record=dict(**common,actas=len(R['F']),circuitos=len(np.unique(R['clus'])),margen=margin,real_margen=rm,
                error_margen=margin-rm,mae_fuerzas=np.mean([abs(pt[b.index(f)]-real[f]) for f in real.index]),
                lo=low,hi=high,disponible=ok,cubre=bool(ok and low<=rm<=high),
                z=z,prob_pareada=probability,brier=(probability-1)**2 if ok else np.nan)
    return record,rows


def main():
    records=[]; details=[]; seatrows=[]; start=time.time()
    stem=('bancas_' if args.bancas else 'fotos_')+args.version+args.tag
    for di,dest in enumerate(args.destinos.split(',')):
        m=pd.read_pickle(PROY/('mesas_'+dest+'.pkl'))
        forces=[c for c in m if c not in KEY+FIX]
        frame=m.groupby(['distrito_id','seccion_id','circuito'],as_index=False).e.sum()
        real=100*m[forces].sum()/m[forces].sum().sum()
        top=real.sort_values(ascending=False).index[:2].tolist()
        m=m[m[forces+['BLANCO','NULO']].sum(1)>0].reset_index(drop=True)
        orig={'2025bl':'2023p,2021bl','2023p':'2019p,2021bl','2023b':'2023p','2015b':'2015p'}[dest]
        ant=ANT if dest=='2025bl' else ANT2023 if dest=='2023p' else {'2023p':{}} if dest=='2023b' else {
            '2015p':{'CAMBIEMOS':['ALIANZA CAMBIEMOS'],'FRENTE PARA LA VICTORIA':['ALIANZA FRENTE PARA LA VICTORIA']}}
        pf.ANTECESORES=ant
        for si,scheme in enumerate(['azar','twitter','twitter_parcial']):
            if scheme=='twitter_parcial' and len(forces)==2:continue
            for rep in range(args.reps):
                rng=np.random.default_rng(202610280+di*100000+si*10000+rep)
                a=actas(m.iloc[muestra(m,rng,scheme)],forces,scheme,top)
                kw=dict(nboot=args.boot,seed=50000+rep)
                if args.version=='despues':kw.update(fuerzas=forces,marco=frame,factor=args.factor)
                with contextlib.redirect_stdout(io.StringIO()):R=pf.calcular(a,orig,**kw)
                common=dict(destino=dest,origen=orig,esquema=scheme,rep=rep,version=args.version,factor=args.factor)
                if args.bancas:
                    if args.version=='antes': tot,S=legacy_seats(R)
                    else:
                        C=cg.distribucion(R,2025,nboot=args.boot);tot,S=C['tot'],C['S']
                    truth=cg.electos(2025)[1]
                    for f in ['LLA','FP','PU','FIT','PROV']:
                        v=S.get(f,pd.Series(np.zeros(args.boot)));lo,hi=np.percentile(v,[5,95])
                        seatrows.append(dict(**common,fuerza=f,punto=tot.get(f,0),real=truth.get(f,0),lo=lo,hi=hi,
                                             error=tot.get(f,0)-truth.get(f,0),cubre=lo<=truth.get(f,0)<=hi))
                rec,det=metrics(R,real,top,common);records.append(rec);details+=det
                if (rep+1)%20==0:print(stem,dest,scheme,rep+1,'%.0fs'%(time.time()-start),flush=True)
            pd.DataFrame(records).to_csv(HERE/(stem+'.csv'),index=False)
            pd.DataFrame(details).to_csv(HERE/(stem+'_fuerzas.csv'),index=False)
            if seatrows:pd.DataFrame(seatrows).to_csv(HERE/(stem+'_escanos.csv'),index=False)
    manifest=dict(version=args.version,reps=args.reps,nboot=args.boot,destinos=args.destinos,factor=args.factor,
                  esquema='30 exactas; Twitter 20 AMBA/10 resto, racimos 10+3+3; parcial oculta terceros en las primeras 10',
                  verdad='todo el provisorio disponible, sin restringir al cruce historico',
                  hash_fuentes={n:hashlib.sha256((HERE/'baseline'/n if args.version=='antes' else PROY/n).read_bytes()).hexdigest()
                                for n in ['fotos_modelo.py','proyectar_fotos.py','congreso.py']})
    (HERE/(stem+'_manifest.json')).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(pd.DataFrame(records).assign(abs_margen=lambda d:d.error_margen.abs()).groupby(['destino','esquema'])[
        ['mae_fuerzas','abs_margen','cubre','disponible']].mean().round(3).to_string(),flush=True)


if __name__=='__main__':main()
