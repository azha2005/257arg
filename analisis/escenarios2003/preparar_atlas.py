"""Atlas interactivos derivados del HTML y la geometría de mapa2003.

No ejecuta ni modifica el atlas legislativo de origen. La fuente presidencial
es PolAr, la misma de los Sankey. Los faltantes quedan beige.
"""
from pathlib import Path
import difflib
import hashlib
import json
import re
import sys
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT/'mapas/mapa2003escenarios'
sys.path[:0] = [str(ROOT/'comun'),str(ROOT/'mapas/mapa2013'),str(HERE)]
from names import norm
from leg2003_2025_data import PROV_ALIASES, ALIASES, D2P
from preparar import CANDIDATOS


def main():
    OUT.mkdir(exist_ok=True)
    data=json.loads((HERE/'datos.json').read_text(encoding='utf8'))
    original=json.loads((ROOT/'mapas/mapa2003/dataset_2003.json').read_text(encoding='utf8'))
    T=original['territories']
    v,e=pd.read_pickle(ROOT/'transferencias/circ_2003p.pkl')
    names=pd.read_csv(ROOT/'transferencias/secciones_2003.csv',dtype={'distrito_id':str})
    lookup={(r.distrito_id,int(r.seccion_id)):r.depto for r in names.itertuples()}
    idx={(t['p'],norm(t['n'])):i for i,t in enumerate(T) if t['p']!='Capital Federal'}
    caba={int(re.search(r'Circ\. (\d+)',t['n'])[1]):i for i,t in enumerate(T) if t['p']=='Capital Federal'}
    linked={};unlinked=[]
    # Equivalencias de escritura, sin fusiones territoriales.
    extra={('Buenos Aires',norm('Florentino Ameghino')):norm('Florentino Ameghino'),
           ('Chubut',norm('Florentino Ameghino')):norm('Florentino Ameghino')}
    for d,s in v.groupby(['distrito_id','seccion_id']).groups:
        p=D2P[d];name=lookup[(d,s)];nn=norm(name)
        if p=='Capital Federal':i=caba.get(int(s))
        else:
            i=idx.get((p,nn))
            if i is None:i=idx.get((p,extra.get((p,nn),PROV_ALIASES.get((p,nn),ALIASES.get(nn,nn)))))
        if i is None:
            nearby=difflib.get_close_matches(nn,[k[1] for k in idx if k[0]==p],n=3,cutoff=.4)
            unlinked.append(dict(d=d,s=int(s),province=p,name=name,candidates=nearby))
        else:
            assert i not in linked,(i,d,s)
            linked[i]=(d,s)
    (OUT/'sin_emparejar.json').write_text(json.dumps(unlinked,ensure_ascii=False,indent=2),encoding='utf8')
    if unlinked:raise ValueError(f'{len(unlinked)} unidades sin emparejar; revisar sin_emparejar.json')
    pv=v[v.votos_tipo.eq('POSITIVO')].pivot_table(index=['distrito_id','seccion_id'],columns='agrupacion_id',values='v',aggfunc='sum',fill_value=0).reindex(columns=[c[3] for c in CANDIDATOS],fill_value=0)
    bn=v[~v.votos_tipo.eq('POSITIVO')].groupby(['distrito_id','seccion_id']).v.sum()
    ev=e.groupby(level=[0,1]).sum()
    total=v.groupby(['distrito_id','seccion_id']).v.sum()
    abst=ev-total
    # Una inconsistencia de padrón no invalida los votos por candidato,
    # pero impide calcular abstención local. Se conserva como ausente.
    bad_abst={key:float(value) for key,value in abst[abst<0].items()}
    target=np.array(data['geographies'][0]['votes'])
    scale=target[:18]/pv.sum().to_numpy()
    bscale=target[18]/bn.sum();ascale=data['geographies'][0]['abstention']/abst.sum()
    rows=[]
    for i,t in enumerate(T):
        if i in linked:
            key=linked[i];votes=np.r_[pv.loc[key].to_numpy(float)*scale,float(bn.loc[key])*bscale]
            if votes[:18].sum()==0:
                rows.append(dict(i=i,missing=True,malvinas=False,reason='PolAr registra cero votos positivos y no aporta padrón utilizable; pendiente, sin imputación.',source=dict(d=key[0],s=int(key[1]),name=lookup[key])))
                continue
            rows.append(dict(i=i,geo=next(j for j,g in enumerate(data['geographies']) if g['id']==key[0]),votes=votes.round(8).tolist(),abstention=None if key in bad_abst else round(float(abst.loc[key])*ascale,8),abstention_error=bad_abst.get(key),source=dict(d=key[0],s=int(key[1]),name=lookup[key])))
        else:rows.append(dict(i=i,missing=True,malvinas=t['n']=='Islas Malvinas'))
    check=[]
    for gi,g in enumerate(data['geographies'][1:],1):
        rs=[r for r in rows if r.get('geo')==gi]
        sums=np.sum([r['votes'] for r in rs],axis=0)
        error=float(np.max(np.abs(sums-np.array(g['votes']))))
        unknown=[r['source']['name'] for r in rs if r['abstention'] is None]
        ae=None if unknown else abs(sum(r['abstention'] for r in rs)-g['abstention'])
        assert error<.01 and (ae is None or ae<.01),(gi,error,ae)
        check.append(dict(provincia=g['name'],unidades=len(rs),max_error_agregacion=error,error_abstencion=ae,abstencion_no_verificable=unknown))
    # Los nombres geográficos siguen los de la geometría (Capital Federal),
    # aunque el catálogo de transferencias rotule el distrito «CABA».
    for g in data['geographies'][1:]:g['name']=D2P[g['id']]
    # Emblemas ya verificados y usados por la base de 2003. FPV y MNP
    # conservan sigla: no se añade un rediseño posterior a la elección.
    logos={key:original['candidates'][source]['img'] for key,source in {'M':'B01','L':'B04','C':'B03'}.items() if original['candidates'][source].get('img')}
    payload=dict(sim=data,units=rows,territories=T,insets=original['insets'],logos=logos)
    (OUT/'base_territorial.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
    if '--solo-base' in sys.argv:
        print('Base territorial preparada, sin regenerar HTML.',flush=True)
        return
    engine=(HERE/'motor.js').read_text(encoding='utf8')
    extension=(HERE/'atlas.js').read_text(encoding='utf8')
    template=(ROOT/'mapas/mapa2003/atlas_2003.html').read_text(encoding='utf8')
    # Reemplazo acotado al bloque JSON. La geometría SVG permanece idéntica.
    a=template.index('const DATA=');b=template.index('const START_MODE=',a)
    prefix=template[:a];suffix=template[b:]
    suffix=re.sub(r'const START_MODE="[^"]+";', 'const START_MODE="gan";',suffix,count=1)
    # El objeto MODES conserva sus referencias; se muta al recalcular.
    suffix=suffix.replace('window.__atlas={setMode,','window.__atlas={setMode,',1)
    # No dejar títulos y fuentes legislativas en el archivo estático inicial.
    prefix=re.sub(r'<title>.*?</title>','<title>Escenarios presidenciales de 2003</title>',prefix,count=1,flags=re.S)
    prefix=prefix.replace('body data-bg="black"','body data-bg="white"')
    extra_css='''<style>#scenario-controls{display:flex;flex-wrap:wrap;gap:10px;align-items:end;padding:12px 14px;border-bottom:1px solid var(--line);background:var(--ctl);color:var(--ctlfg);font-size:13px}#scenario-controls label{display:grid;gap:4px}#scenario-controls select,#scenario-controls input{font:inherit;max-width:290px;min-height:34px;background:var(--ctl);color:var(--ctlfg);border:1px solid var(--line);padding:4px 7px}#scenario-controls input{width:75px}#scenario-status{flex-basis:100%;color:var(--mut);line-height:1.45}#scenario-controls a{color:inherit}body.bare #scenario-controls{display:none}@media(max-width:600px){#scenario-controls{gap:8px}#scenario-controls label{max-width:100%;flex:1 1 145px}#scenario-controls select{max-width:100%;width:100%}#bar .grp{flex-wrap:wrap;width:100%;min-width:0}#bar select,#bar input{box-sizing:border-box;max-width:100%;width:100%}#bar .sp{display:none}}</style>'''
    prefix=prefix.replace('</head>',extra_css+'</head>')
    prefix=prefix.replace('<div id="bar">','<div id="scenario-controls"></div><div id="bar">',1)
    manifest=[]
    for c in data['candidates']:
        boot=f'''{engine}\nconst ATLAS_INPUT={json.dumps(payload,ensure_ascii=False,separators=(',',':'))};\nconst DEFAULT_REMOVED={json.dumps(c['id'])};\n{extension}\nconst DATA=AtlasScenario2003.initial();\n'''.replace('</script','<\\/script')
        html=prefix+boot+suffix
        html=html.replace('</body>','<script>AtlasScenario2003.attach();</script></body>')
        name='atlas_2003_sin_'+c['id'].lower()+'.html'
        (OUT/name).write_text(html,encoding='utf8')
        manifest.append(dict(candidato=c['name'],id=c['id'],html=name,sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest()))
    (OUT/'control_territorial.json').write_text(json.dumps(dict(unidades_con_dato=sum(not r.get('missing',False) for r in rows),sin_dato=[dict(T[r['i']],motivo=r.get('reason','Sin voto registrado')) for r in rows if r.get('missing')],provincias=check),ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'manifiesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    items=''.join(f'<li><a href="{x["html"]}">Sin {x["candidato"]}</a></li>' for x in manifest)
    index=f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Atlas de escenarios 2003</title><style>body{{font:18px/1.6 system-ui;margin:40px auto;max-width:850px;padding:0 20px;background:#fafaf7;color:#202322}}a{{color:#176b60}}li{{padding:5px 0}}</style><h1>Atlas de escenarios de 2003</h1><p>18 atlas autocontenidos. Cada uno abre una retirada distinta y permite cambiar candidato, modelo, primera o segunda vuelta y coropleta. Geometría del atlas de 2003, con votos presidenciales de PolAr.</p><p><strong>Simulaciones condicionales.</strong> Las afinidades históricas no identifican segundas preferencias individuales. Los menores usan el agregado Otros.</p><ul>{items}</ul><p><a href="../../analisis/escenarios2003/simulador_2003.html">Simulador, Sankey y encuestas</a> · <a href="LEEME_2003ESCENARIOS.md">Método y controles</a></p></html>'''
    (OUT/'index.html').write_text(index,encoding='utf8')
    print('Atlas:',len(manifest),'unidades con dato:',sum(not r.get('missing',False) for r in rows),'sin dato:',sum(bool(r.get('missing')) for r in rows))


if __name__=='__main__':main()
