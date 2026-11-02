"""Cotejos independientes: agregado DINE por sección y suma de listas radio a radio."""
import json
from collections import defaultdict
import numpy as np
import pandas as pd
from serie import ROOT,HERE,norm,section_names,dump

c=pd.read_pickle(HERE/'asignacion_2023pasocand.pkl')
f=pd.read_pickle(HERE/'asignacion_2023pasofuerza.pkl')
mapping=json.loads((HERE/'mapeo_paso2023_candidatos.json').read_text(encoding='utf8'))
lookup={r['identificador_dine']:r['codigo'] for r in mapping}
groups={r['codigo']:r['grupo'] for r in mapping}
v,_=pd.read_pickle(ROOT/'datos_oficiales/2023_paso/agregado.pkl')
allowed=set(c['ctrl']['sections'])
v=v[v.cargo_nombre.str.contains('PRESIDENTE') & (v.votos_tipo=='POSITIVO')].copy()
v['d']=v.distrito_id.map(lambda x:f'{int(x):02d}')
v['s']=v.seccion_id.map(lambda x:f'{int(x):03d}')
v=v[[d+'_'+s in allowed for d,s in zip(v.d,v.s)]].copy()
v['code']=[lookup[str(a).strip().upper()+' | '+str(l).strip().upper()] for a,l in zip(v.agrupacion_nombre,v.lista_nombre)]
names=section_names(2023)
expected=defaultdict(float)
for r in v.itertuples():
    unit=('01',r.s) if r.d=='01' else ('02',norm(names[r.d,r.s]))
    expected[unit,r.code]+=float(r.v)
ri=defaultdict(list)
for i,u in enumerate(c['radios'].unit):ri[u].append(i)
ci={code:i for i,code in enumerate(c['CATS'])}
err=0.
for (u,code),votes in expected.items():err=max(err,abs(c['A'][ri[u],ci[code]].sum()-votes))
assert err<1e-6,err
fi={code:i for i,code in enumerate(f['CATS'])}
group_err=0.
for group in {g for g in groups.values()}:
    cols=[ci[code] for code,g in groups.items() if g==group and code in ci]
    assert cols and group in fi,group
    group_err=max(group_err,float(np.max(np.abs(c['A'][:,cols].sum(axis=1)-f['A'][:,fi[group]]))))
assert group_err<1e-6,group_err
cc=[x for x in c['CATS'] if not x.startswith('_')]
fc=[x for x in f['CATS'] if not x.startswith('_')]
cw=np.array(cc)[c['A'][:,[ci[x] for x in cc]].argmax(axis=1)]
fw=np.array(fc)[f['A'][:,[fi[x] for x in fc]].argmax(axis=1)]
positive=c['A'][:,[ci[x] for x in cc]].sum(axis=1)>=.5
changed=int(np.sum(np.array([groups[x] for x in cw])[positive]!=fw[positive]))
report=dict(candidaturas_presentes=len(cc),candidaturas_nacionales=len(mapping),
            positivos_fuente=int(v.v.sum()),error_max_candidato_unidad_contra_agregado_dine=float(err),
            error_max_suma_candidatos_por_fuerza_y_radio=group_err,
            radios_donde_ganador_individual_no_pertenece_a_fuerza_ganadora=changed,
            poblacion_en_esos_radios=int(c['radios'].POB[positive & (np.array([groups[x] for x in cw])!=fw)].sum()),
            totales_por_candidato={code:int(v[v.code==code].v.sum()) for code in cc})
dump(HERE/'CONTROL_PASO2023_CRUCE.json',report)
print(json.dumps(report,ensure_ascii=False,indent=2))
