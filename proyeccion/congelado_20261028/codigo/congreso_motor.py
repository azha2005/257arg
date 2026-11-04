"""Preparacion de suficientes por acta y ajuste provincial para remuestras.

Equivalente a provinciales + ceros_estructurales, sin repetir filtros de DataFrame
por cada remuestra. No utiliza resultados de la eleccion para ajustar parametros.
"""
import numpy as np
import pandas as pd


def preparar(R, anio, cg):
    base=list(R['blocs']); districts=R['distritos']; dc={d:i for i,d in enumerate(districts)}
    table=cg._tabla_prov(); cfg=table[table.anio==anio].to_dict('records')
    cfg=[x for x in cfg if x['distrito'] in dc]
    columns=base+[x['fuerza'] for x in cfg if x['fuerza'] not in base]
    columns=list(dict.fromkeys(columns));ci={f:i for i,f in enumerate(columns)}
    if cfg:
        if anio not in cg._RET:cg._RET[anio]=cg.retencion(anio)
        retention,ratios=cg._RET[anio]
        cv=np.std(ratios,ddof=1)/np.mean(ratios)
    else:retention,cv=0.,0.
    groups={k:g for k,g in R['actas'].groupby('mesa_key',sort=False)}
    fv=np.zeros((len(R['F']),len(cfg)));ft=fv.copy()
    for i,r in R['F'].iterrows():
        if not r.completa:continue
        a=groups[r.mesa_key];a=a[a.bloque!='BN']
        for j,x in enumerate(cfg):
            if r.distrito_id!=x['distrito']:continue
            if x['fuerza'].startswith('PROV:'):
                if 'lista' not in a:continue
                if 'detalle_listas' in a:
                    avalid=a[a.detalle_listas.astype(str).str.lower().isin(['si','true','1'])]
                else:
                    detail=~a.lista.isin(list(cg.FUERZAS)+['OTRAS','BN','BLANCO','NULO'])
                    avalid=a if detail.any() else a.iloc[:0]
                ft[i,j]=avalid.votos.sum()
                fv[i,j]=avalid.loc[avalid.lista.str.upper().str.contains(x['lista'].upper(),regex=False,na=False),'votos'].sum()
            else:
                ft[i,j]=a.votos.sum();fv[i,j]=a.loc[a.bloque==x['fuerza'],'votos'].sum()
    pad=cg.padron(anio)
    scale=np.array([pad[d]/R['pad'][d] for d in districts])[:,None]
    allowed=cg.presencia(anio)
    mask=np.ones((len(districts),len(columns)))
    for d,i in dc.items():
        for f,j in ci.items():
            if f in cg.FUERZAS and f not in allowed.get(d,set()):mask[i,j]=0.

    def apply(raw,idx=None,rng=None):
        V=np.zeros((len(districts),len(columns)))
        V[:,:len(base)]=raw*scale
        if not np.isfinite(V).all():raise ValueError('Proyeccion provincial no estimable')
        obsfv=fv.sum(0) if idx is None else fv[idx].sum(0)
        obsft=ft.sum(0) if idx is None else ft[idx].sum(0)
        for j,x in enumerate(cfg):
            i=dc[x['distrito']];k=ci[x['fuerza']];v=V[i];total=v.sum()
            if total<=0:raise ValueError('Proyeccion provincial vacia')
            s=retention*x['pct_gob']/100*(np.exp(rng.normal(0,cv)-cv**2/2) if rng is not None else 1)
            s=float(np.clip((s*cg.K_FOTOS+obsfv[j])/(cg.K_FOTOS+obsft[j]),0,1))
            if x['fuerza'].startswith('PROV:') and 'OTRAS' in ci:
                take=min(v[ci['OTRAS']],max(s*total-v[k],0))
                v[ci['OTRAS']]-=take;v[k]+=take
            tom=x.get('toma_de')
            if isinstance(tom,str) and tom in ci and s*total>v[k]:
                take=min(v[ci[tom]]*cg.TOMA_MAX,s*total-v[k]);v[ci[tom]]-=take;v[k]+=take
            other=np.arange(len(columns))!=k
            remainder=v[other].sum()
            if remainder>0:v[other]*=(1-s)*total/remainder
            v[k]=s*total
        V=np.maximum(V,0)
        before=V.sum(1);V*=mask;after=V.sum(1)
        V*=np.divide(before,after,out=np.ones_like(before),where=after>0)[:,None]
        return pd.DataFrame(V,index=districts,columns=columns)
    return apply,pad
