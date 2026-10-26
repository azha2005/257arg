"""Sensibilidad provincial y bootstrap de 1983p→1985d para Buenos Aires."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import estimar as e

HERE=Path(__file__).resolve().parent
FOLDER=HERE/'1983p_1985d'

def main():
    A,B,X,Y,w,rows,cols,ctl=e.prepare('1983p','1985d')
    saved=json.loads((FOLDER/'control.json').read_text(encoding='utf8'))
    lam=saved['lambda']
    xp,yp,wp=X.loc['02'].values,Y.loc['02'].values,w.loc['02'].values
    center=e.fit(X.values,Y.values,const=.001,w=w.values)
    g0=np.log(center[:,:-1]/center[:,-1:]).ravel()
    principal=e.fit_prov(xp,yp,lam*len(xp),wp,g0)
    present=(B.loc['02'].sum().values>0)
    calvo=np.zeros_like(principal)
    calvo[:,present]=e.fit(xp,yp[:,present],const=.001)
    boots=[]
    rng=np.random.default_rng(19831985)
    for _ in range(200):
        idx=rng.integers(0,len(xp),len(xp))
        boots.append(e.fit_prov(xp[idx],yp[idx],lam*len(idx),wp[idx],g0))
    lo,hi=np.percentile(np.array(boots)*100,[5,95],axis=0)
    source=A.loc['02'].sum()
    mass=X.loc['02'].mul(B.loc['02'].sum(1),axis=0).sum()
    observations=[]
    for i,r in enumerate(rows):
        if source[r]<=0: continue
        for j,c in enumerate(cols):
            if not present[j]: continue
            observations.append(dict(origen=r,destino=c,votos_origen=int(source[r]),
                                     peso_origen_pct=100*source[r]/source.sum(),
                                     principal_pct=100*principal[i,j],calvo_provincial_pct=100*calvo[i,j],
                                     diferencia_pp=100*(principal[i,j]-calvo[i,j]),
                                     bootstrap_p5_pct=lo[i,j],bootstrap_p95_pct=hi[i,j]))
    table=pd.DataFrame(observations)
    table.round(4).to_csv(FOLDER/'PBA_comparacion_modelos.csv',index=False,encoding='utf-8-sig')
    # El ajuste puntual reproduce la matriz provincial guardada, al redondeo.
    P=pd.read_csv(FOLDER/'por_provincia.csv',dtype={'distrito':str})
    actual=P[P.distrito=='02'].pivot(index='origen',columns='destino',values='votos').reindex(index=rows,columns=cols)
    assert np.max(np.abs(actual.values-principal*mass.values[:,None]))<=.501
    stats=dict(unidades=len(xp),votos_origen=int(source.sum()),votos_destino=int(B.loc['02'].sum().sum()),
               cobertura_origen=100*A.loc['02'].sum().sum()/e.load('1983p',raw=True)[0].loc['02'].sum().sum(),
               source_totals=source.astype(int).to_dict(),
               destination_totals=B.loc['02'].sum().astype(int).to_dict(),
               max_diferencia_pp_por_fila=table.groupby('origen').diferencia_pp.apply(lambda s:float(s.abs().max())).to_dict(),
               bootstrap=200,lambda_elegida=lam)
    (FOLDER/'PBA_control.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
    lines=['# Buenos Aires: presidente 1983 → diputados 1985','',
           '[Abrir el gráfico provincial](sankey_1983p_1985d.html#02) | [PNG](PBA_1983p_1985d.png)','',
           f"Se conservaron **{stats['unidades']} partidos** y el **{stats['cobertura_origen']:.2f} % del voto desglosado de origen**. No incluye abstención.",
           '','Se distingue PJ de peronismo renovador en 1985. La tabla compara el modelo principal provincial ponderado y penalizado hacia el nacional con una matriz ajustada solo en PBA, sin ponderación y con penalización 0,001, siguiendo la especificación de Calvo. Esta segunda matriz es provincial; no es la variante nacional de `calvo_nacional.csv`.','',
           '| Origen 1983 | Destino 1985 | Principal % | Calvo provincial % | Bootstrap principal 5–95 % |',
           '|---|---|---:|---:|---:|']
    for row in table.itertuples():
        if row.origen not in ('UCR (Alfonsín)','PJ (Luder)') or row.destino not in ('UCR','PJ','Peronismo renovador','PI'): continue
        lines.append(f'| {row.origen} | {row.destino} | {row.principal_pct:.1f} | {row.calvo_provincial_pct:.1f} | {row.bootstrap_p5_pct:.1f}–{row.bootstrap_p95_pct:.1f} |')
    diagnostic=json.loads((FOLDER/'diagnostico.json').read_text(encoding='utf8'))['rmse_validacion_por_provincia_pp']['02']
    improvement=100*(1-diagnostic['modelo']/diagnostic['promedio_provincial'])
    lines += ['',f"Diagnóstico interno en PBA: RMSE {diagnostic['modelo']:.2f} puntos frente a {diagnostic['promedio_provincial']:.2f} del promedio provincial de entrenamiento; mejora del {improvement:.1f} %.",'',
              'El bootstrap provincial remuestrea 200 veces los partidos y mantiene fijo el centro nacional. No incluye la incertidumbre del centro, de las fuentes o de las correspondencias. Las diferencias entre variantes pueden ser mayores que sus intervalos. Los porcentajes describen una inferencia territorial y no identifican cambios individuales de voto.','',
              '[Comparación completa e intervalos](PBA_comparacion_modelos.csv), [control](PBA_control.json), [reservas del cruce nacional](RESUMEN.md).','']
    (FOLDER/'PBA.md').write_text('\n'.join(lines),encoding='utf8')
    print(table[table.origen.isin(['UCR (Alfonsín)','PJ (Luder)'])].round(2).to_string(index=False))

if __name__=='__main__': main()
