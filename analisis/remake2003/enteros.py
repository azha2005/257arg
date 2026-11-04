"""Redondeo controlado a votos enteros, con márgenes y ganadores conservados."""
from pathlib import Path
import csv,json
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
from escalas import apply_scales

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'mapas/mapa2003alt'

def integerize(matrix,target,groups):
    a=np.asarray(matrix,float);n,k=a.shape;target=np.rint(target).astype(np.int64)
    floor=np.floor(a).astype(np.int64);frac=a-floor
    # Positivos locales enteros por restos mayores, con el total nacional exacto.
    row_float=a.sum(axis=1);rows=np.floor(row_float).astype(np.int64)
    left=int(target.sum()-rows.sum())
    assert 0<=left<=n
    rows[np.argsort(-(row_float-rows),kind='stable')[:left]]+=1
    rr=[];cc=[];vv=[];lower=[];upper=[]
    def add(ix,coef,lo,hi):
        r=len(lower);rr.extend([r]*len(ix));cc.extend(ix);vv.extend(coef);lower.append(lo);upper.append(hi)
    for i in range(n):add(list(range(i*k,(i+1)*k)),[1]*k,int(rows[i]-floor[i].sum()),int(rows[i]-floor[i].sum()))
    for j in range(k):add([i*k+j for i in range(n)],[1]*n,int(target[j]-floor[:,j].sum()),int(target[j]-floor[:,j].sum()))
    winner=a.argmax(axis=1)
    for i,w in enumerate(winner):
        for j in range(k):
            if j!=w:add([i*k+int(w),i*k+j],[1,-1],int(floor[i,j]-floor[i,w]+1),np.inf)
    for idx in groups:
        w=int(a[idx].sum(axis=0).argmax())
        for j in range(k):
            if j!=w:add([int(i)*k+w for i in idx]+[int(i)*k+j for i in idx],[1]*len(idx)+[-1]*len(idx),int(floor[idx,j].sum()-floor[idx,w].sum()+1),np.inf)
    sparse=coo_matrix((vv,(rr,cc)),shape=(len(lower),n*k)).tocsc()
    result=milp((1-2*frac).ravel(),integrality=np.ones(n*k),bounds=Bounds(np.zeros(n*k),np.ceil(a).ravel()-floor.ravel()),constraints=LinearConstraint(sparse,lower,upper),options=dict(time_limit=30,mip_rel_gap=0))
    assert result.success, result.message
    rounded=floor+np.rint(result.x).astype(np.int64).reshape(n,k)
    assert np.array_equal(rounded.sum(axis=0),target)
    assert np.array_equal(rounded.sum(axis=1),rows)
    assert np.array_equal(rounded.argmax(axis=1),winner)
    assert all(np.all(rounded[i,w]>np.delete(rounded[i],w)) for i,w in enumerate(winner))
    assert all(int(rounded[idx].sum(axis=0).argmax())==int(a[idx].sum(axis=0).argmax()) for idx in groups)
    return rounded,dict(method='Redondeo controlado a piso/techo por celda; restos mayores para totales locales; márgenes nacionales y ganadores locales/provinciales exactos.',max_cell_change=float(np.max(np.abs(rounded-a))),max_local_total_change=float(np.max(np.abs(rows-row_float))),national_error=0,local_total_error=0,local_winners_changed=0,provincial_winners_changed=0)

def number(n):return f'{int(n):,}'.replace(',','.')

def new_record(old,values,codes,kind):
    r=dict(old);total=int(values.sum());j=int(values.argmax())
    r['lines']=[[codes[j],int(values[j]),round(100*int(values[j])/total,4)] for j in np.argsort(-values) if values[j]]
    r['metrics']=[['Votos modelados',number(total)]]
    if kind=='gan':r.update(w=codes[j],q=round(100*int(values[j])/total,4))
    r['note']=r.get('note','').replace('votos esperados, mostrados redondeados.','votos enteros por redondeo controlado.')
    return r

def main():
    manifest=json.loads((DEST/'manifiesto.json').read_text('utf8'));reports=[]
    for s in manifest:
        p=DEST/f'dataset_2003alt_{s["id"]}.json';ds=json.loads(p.read_text('utf8'))
        modes=ds['modes'];T=ds['territories'];codes=list(s['national_target']);valid=[i for i,t in enumerate(T) if t['n']!='Islas Malvinas']
        a=np.array([[dict((v[0],v[1]) for v in modes[0]['units'][i]['lines']).get(c,0) for c in codes] for i in valid])
        provinces=sorted({T[i]['p'] for i in valid});groups=[np.array([j for j,i in enumerate(valid) if T[i]['p']==p]) for p in provinces]
        integer,report=integerize(a,list(s['national_target'].values()),groups)
        for mode in modes:
            for j,i in enumerate(valid):mode['units'][i]=new_record(mode['units'][i],integer[j],codes,mode['id'])
            for prov,idx in zip(provinces,groups):
                if prov in mode.get('prov',{}):mode['prov'][prov]=new_record(mode['prov'][prov],integer[idx].sum(axis=0),codes,mode['id'])
        apply_scales(ds,ds['reconstruction']['national']['round'])
        fit=ds['reconstruction']['fit'];fit['rounding']=report;fit['max_national_error']=0
        htmlp=p.with_name(p.name.replace('dataset_','atlas_').replace('.json','.html'));html=htmlp.read_text('utf8')
        start=html.index('const DATA=');end=html.index('const START_MODE=',start)
        html=html[:start]+'const DATA='+json.dumps(ds,ensure_ascii=False,separators=(',',':'))+';\n'+html[end:]
        htmlp.write_text(html,'utf8');p.write_text(json.dumps(ds,ensure_ascii=False,indent=2),'utf8')
        s['rounding']=report;s['max_national_error']=0;s['national_target']={c:int(v) for c,v in s['national_target'].items()}
        (DEST/f'control_{s["id"]}.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
        with (DEST/f'estimacion_{s["id"]}.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['provincia','unidad','ganador_imagen','lectura_suficiente',*codes])
            for j,i in enumerate(valid):
                reading=ds['reconstruction']['reading'].get(str(i),{})
                w.writerow([T[i]['p'],T[i]['n'],(reading.get('reading') or {}).get('w',''),reading.get('readable',False),*map(int,integer[j])])
        reports.append(dict(id=s['id'],**report));print(s['id'],'enteros, cierre nacional exacto, ganadores conservados.',flush=True)
    (DEST/'manifiesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
    (ROOT/'outputs/2003alt/control_enteros.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),'utf8')

if __name__=='__main__':main()
