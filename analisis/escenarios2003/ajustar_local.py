"""Condiciona los antecedentes nacionales a márgenes territoriales reales.

No estima segundas preferencias. Sustituye el reparto provincial constante
por matrices locales de escenario, con márgenes observados 1999/2003.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'transferencias'))
import estimar
from presidente_1999 import norm


def rake(kernel,row,col):
    row=np.asarray(row,float);col=np.asarray(col,float)
    row=row*col.sum()/row.sum()
    # Los ceros de estimaciones redondeadas no se tratan como imposibilidades
    # estructurales. Piso estrictamente numérico y declarado.
    B=kernel/kernel.sum(1)[:,None]
    B=np.maximum(B,1e-8);B/=B.sum(1)[:,None]
    F=B*row[:,None]
    active=col>0
    F[:,~active]=0
    for it in range(10000):
        F*=np.divide(col,F.sum(0),out=np.zeros_like(col),where=F.sum(0)>0)[None,:]
        F*=np.divide(row,F.sum(1),out=np.zeros_like(row),where=F.sum(1)>0)[:,None]
        if it%20==0 and np.max(np.abs(F.sum(0)-col))<max(.00001,col.sum()*1e-9):break
    # Último ajuste de columnas: votos locales de 2003 conservados exactamente.
    F*=np.divide(col,F.sum(0),out=np.zeros_like(col),where=F.sum(0)>0)[None,:]
    error=float(np.max(np.abs(F.sum(1)-row)))
    if error>max(.001,col.sum()*1e-7):raise ValueError(('IPF sin converger',error,col.sum()))
    return F,it+1,error


def main():
    subprocess.run([sys.executable,'-X','utf8',str(HERE/'preparar_atlas.py'),'--solo-base'],check=True,cwd=ROOT)
    d=json.loads((HERE/'datos.json').read_text(encoding='utf8'))
    base=json.loads((ROOT/'mapas/mapa2003escenarios/base_territorial.json').read_text(encoding='utf8'))
    units=[u for u in base['units'] if not u.get('missing')]
    A,_,_,_,_,origins,_,match_control=estimar.prepare('1999pe','2003pe')
    V,_=pd.read_pickle(ROOT/'transferencias/circ_2003p.pkl')
    secciones=pd.read_csv(ROOT/'transferencias/secciones_2003.csv',dtype={'distrito_id':str})
    sections={(r.distrito_id,norm(r.depto)):int(r.seccion_id) for r in secciones.itertuples()}
    # Córdoba 1999 conserva circuitos: el propio cruce del proyecto usa esos
    # circuitos. Se agregan a la sección de 2003 por su código verificado.
    cs=V[V.distrito_id.eq('04')][['seccion_id','circuito']].drop_duplicates()
    if cs.groupby('circuito').seccion_id.nunique().max()!=1:raise ValueError('Circuito de Córdoba ambiguo')
    circuit_to_section=dict(zip(cs.circuito,cs.seccion_id))
    hist={};unassigned=[]
    for (di,_,ci),r in A.iterrows():
        s=circuit_to_section.get(ci) if di=='04' else sections.get((di,ci.removeprefix('S:')))
        if s is None:unassigned.append([di,ci]);continue
        key=(di,int(s));hist[key]=hist.get(key,np.zeros(len(origins)))+r.to_numpy(float)
    d['local_units']=units
    for u in units:u['historical_1999']=(u['source']['d'],u['source']['s']) in hist
    report=[]
    for mi,model in enumerate(d['models']):
        kernel=np.array(model['joints'][0]);model['local_joints']=[]
        for u in units:
            key=(u['source']['d'],u['source']['s']);h=hist.get(key)
            observed=bool(h is not None and h.sum()>0)
            if mi<2 and observed:row=h
            elif mi==2 and observed:row=np.r_[h[:3],h[3:].sum()]
            else:row=kernel.sum(1)
            if mi==3:origin_note='Sin margen local 2001 por las ocho categorías del libro; prior nacional condicionado al resultado local 2003.'
            elif observed:origin_note='Margen histórico local 1999 observado en el cruce del proyecto.'
            else:origin_note='Antecedente local 1999 ausente; prior nacional condicionado al resultado local 2003.'
            J,iterations,error=rake(kernel,row,np.array(u['votes']))
            model['local_joints'].append(np.round(J,8).tolist())
            report.append(dict(model=model['id'],i=u['i'],d=key[0],s=key[1],name=u['source']['name'],historical_1999=observed if mi<3 else False,origin_note=origin_note,ipf_iterations=iterations,max_row_error=error))
    missing=[u['source'] for u in units if (u['source']['d'],u['source']['s']) not in hist]
    d['local_method']={
        'default':True,'method':'IPF local con prior nacional de cada matriz histórica',
        'historical_1999_units':sum((u['source']['d'],u['source']['s']) in hist for u in units),
        'units':len(units),'missing_1999':missing,'unassigned_1999_rows':unassigned,
        'historical_pair_control':match_control,
        'numeric_floor':1e-8,
        'warning':'Condicionar márgenes no identifica segundas preferencias. Para el libro 2001 no hay margen local compatible; no se imputa como observado.'}
    for p in ['transferencias/circ_1999pe.pkl','transferencias/secciones_2003.csv']:
        d['manifest'].append(dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()))
    (HERE/'datos.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    (HERE/'control_ajuste_local.json').write_text(json.dumps(dict(method=d['local_method'],units=report),ensure_ascii=False,indent=2),encoding='utf8')
    html=(HERE/'plantilla.html').read_text(encoding='utf8').replace('/*__ENGINE__*/',(HERE/'motor.js').read_text(encoding='utf8')).replace('/*__DATA__*/',json.dumps(d,ensure_ascii=False).replace('</','<\\/'))
    (HERE/'simulador_2003.html').write_text(html,encoding='utf8')
    print(f'Ajuste local: {len(units)} unidades; antecedente 1999 en {d["local_method"]["historical_1999_units"]}.',flush=True)


if __name__=='__main__':main()
