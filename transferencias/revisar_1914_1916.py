"""Sensibilidad de fuentes/filtro y revisión provincial de PBA y Capital."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import estimar as e

HERE=Path(__file__).resolve().parent
FOLDER=HERE/'1914d_1916d'

def estimate(destination,ratio,lam):
    old=e.RATIO
    try:
        e.RATIO=ratio
        A,B,X,Y,w,rows,cols,ctl=e.prepare('1914d',destination)
    finally:e.RATIO=old
    center=e.fit(X.values,Y.values,const=.001,w=w.values)
    g0=np.log(center[:,:-1]/center[:,-1:]).ravel()
    V=X.mul(B.sum(1),axis=0)
    parts={}
    for d in X.index.get_level_values(0).unique():
        p=e.fit_prov(X.loc[d].values,Y.loc[d].values,lam*len(X.loc[d]),w.loc[d].values,g0)
        parts[d]=pd.DataFrame(p*V.loc[d].sum().values[:,None],index=rows,columns=cols)
    total=sum(parts.values())
    return total,parts,(A,B,X,Y,w,rows,cols,ctl),g0

def main():
    ctl=json.loads((FOLDER/'control.json').read_text(encoding='utf8'))
    lam=ctl['lambda']
    variants=[('principal','1916d',e.RATIO),('lecturas_Lupu','1916de',e.RATIO),
              ('sin_filtro_crecimiento','1916d',(0.,float('inf'))),
              ('Lupu_sin_filtro','1916de',(0.,float('inf')))]
    reference=None;prov_ref=None;results=[];comparisons=[]
    for label,dest,ratio in variants:
        matrix,parts,data,g0=estimate(dest,ratio,lam)
        A,B,X,Y,w,rows,cols,c=data
        pct=matrix.div(matrix.sum(1),axis=0)*100
        if reference is None:
            reference=pct;prov_ref={d:M.div(M.sum(1),axis=0)*100 for d,M in parts.items()}
            principal_data=data;principal_g0=g0
            saved=pd.read_csv(FOLDER/'matriz_votos.csv',index_col=0)
            assert np.max(np.abs(saved.reindex(index=rows,columns=cols).values-matrix.values))<=.501
        else:
            pct.round(3).to_csv(FOLDER/f'sensibilidad_{label}_pct.csv',encoding='utf-8-sig')
        delta=(pct-reference).abs().max(1)
        results.append(dict(variante=label,unidades=c['usados'],cobertura_seleccion=100*c['electores_origen_usados']/c['electores_origen_total'],
                            unidades_por_provincia=c['unidades_por_provincia'],cambio_maximo_pp_por_fila=delta.round(3).to_dict()))
        for d,M in parts.items():
            pp=M.div(M.sum(1),axis=0)*100
            for r in rows:
                if A.loc[d][r].sum()==0:continue
                for col in cols:
                    comparisons.append(dict(variante=label,distrito=d,origen=r,destino=col,pct=pp.loc[r,col],diferencia_principal_pp=pp.loc[r,col]-prov_ref[d].loc[r,col]))
    pd.DataFrame(comparisons).round(4).to_csv(FOLDER/'sensibilidad_provincial.csv',index=False,encoding='utf-8-sig')
    (FOLDER/'sensibilidad.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    A,B,X,Y,w,rows,cols,c=principal_data
    diag=json.loads((FOLDER/'diagnostico.json').read_text(encoding='utf8'))
    for d,title,slug in [('02','Buenos Aires','PBA'),('01','Capital Federal','Capital')]:
        xp,yp,wp=X.loc[d].values,Y.loc[d].values,w.loc[d].values
        P=e.fit_prov(xp,yp,lam*len(xp),wp,principal_g0)
        keep=B.loc[d].sum().values>0
        C=np.zeros_like(P);C[:,keep]=e.fit(xp,yp[:,keep],const=.001)
        rng=np.random.default_rng(19141916+int(d))
        boots=[]
        for _ in range(200):
            idx=rng.integers(0,len(xp),len(xp))
            boots.append(e.fit_prov(xp[idx],yp[idx],lam*len(idx),wp[idx],principal_g0))
        lo,hi=np.percentile(np.array(boots)*100,[5,95],axis=0)
        rr=[]
        source=A.loc[d].sum()
        flags=[]
        for i,r in enumerate(rows):
            if source[r]==0:continue
            maximum=float(np.max(np.abs(P[i]-C[i]))*100)
            if maximum>30 or (source[r]/source.sum()<.05 and maximum>20):flags.append(r)
            for j,col in enumerate(cols):
                if not keep[j]:continue
                rr.append(dict(origen=r,destino=col,principal_pct=P[i,j]*100,calvo_provincial_pct=C[i,j]*100,
                               bootstrap_p5_pct=lo[i,j],bootstrap_p95_pct=hi[i,j],dif_calvo_pp=(P[i,j]-C[i,j])*100))
        table=pd.DataFrame(rr)
        table.round(4).to_csv(FOLDER/f'{slug}_comparacion.csv',index=False,encoding='utf-8-sig')
        coverage=100*c['cobertura_por_provincia'][d]
        metrics=diag['rmse_validacion_por_provincia_pp'][d]
        lines=[f'# {title}: diputados 1914 → diputados 1916','',
               f'[Abrir gráfico provincial](sankey_1914d_1916d.html#{d}) | [PNG]({slug}_1914_1916.png)','',
               f'**{len(xp)} unidades utilizadas**. Cobertura del voto de la selección legible y completa de 1914: **{coverage:.1f} %**. No es cobertura provincial total ni cobertura del padrón.','',
               'Solo cifras observadas. No se añaden ceros para reemplazar lecturas dudosas. La matriz Calvo provincial se ajusta solo con estas unidades, sin pesos y con penalización 0,001; es distinta de la variante nacional de Calvo.','',
               '| Origen | Destino | Principal % | Calvo provincial % | Bootstrap principal 5–95 % |',
               '|---|---|---:|---:|---:|']
        for row in table.itertuples():
            lines.append(f'| {row.origen} | {row.destino} | {row.principal_pct:.1f} | {row.calvo_provincial_pct:.1f} | {row.bootstrap_p5_pct:.1f}–{row.bootstrap_p95_pct:.1f} |')
        lines+=['',f"RMSE interno: {metrics['modelo']:.2f} puntos, frente a {metrics['promedio_provincial']:.2f} del promedio provincial de entrenamiento.",'',
                'Filas inestables entre las dos especificaciones provinciales: '+(', '.join(flags) or 'ninguna con el umbral de la auditoría')+'.','',
                'Sensibilidad a fuentes y selección:','',
                '| Variante | Unidades | Mayor cambio por celda en filas presentes |','|---|---:|---:|']
        s=pd.DataFrame(comparisons)
        for label,_,_ in variants[1:]:
            delta=s[(s.distrito==d)&(s.variante==label)].diferencia_principal_pp.abs().max()
            n=sum(results[[r['variante'] for r in results].index(label)]['unidades_por_provincia'][d].values())
            lines.append(f'| {label} | {n} | {delta:.1f} puntos |')
        lines+=['','Los intervalos remuestrean 200 veces las unidades y mantienen fijo el centro nacional. No cubren toda la incertidumbre de fuentes, agregación, selección o modelo. Las transferencias son inferencias sobre territorios, no seguimiento individual.','',
                f'[CSV completo]({slug}_comparacion.csv), [sensibilidad por provincia](sensibilidad_provincial.csv), [fuentes y límites](../fuentes_1914_1916/LEEME.md).','']
        (FOLDER/f'{slug}.md').write_text('\n'.join(lines),encoding='utf8')
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
