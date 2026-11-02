"""Visor de internas de la PASO 2023: sólo competidores y porcentajes internos.

Usa el reparto existente por candidato; no vuelve a estimar ni repartir votos.
python mapas/serieAMBA2005_2023radios/internas2023.py
"""
import copy,html,json,re
from collections import defaultdict,Counter
import numpy as np
import pandas as pd
from serie import HERE,dump

KEY='2023pasointernas'
source=json.loads((HERE/'dataset_2023pasocand.json').read_text(encoding='utf8'))
allocation=pd.read_pickle(HERE/'asignacion_2023pasocand.pkl')
A=allocation['A'];ci={c:i for i,c in enumerate(allocation['CATS'])}
NR=len(A)
# Unidades del selector de nivel (partidos y circuitos), guardadas por render.py después de los radios.
_niv=pd.read_pickle(HERE/'niveles_2023pasocand.pkl');A=np.vstack([A,_niv['V']])
members=defaultdict(list)
for c,value in source['candidates'].items():
    if c in ci and value.get('agr'):members[value['agr']].append(c)
members={g:sorted(cs,key=lambda c:-A[:,ci[c]].sum()) for g,cs in members.items() if len(cs)>1}
order=['B02','B03','B05','B09','B13','B14']
assert set(order)==set(members)
forces=json.loads((HERE/'dataset_2023pasofuerza.json').read_text(encoding='utf8'))['candidates']
names={g:forces[g]['n'] for g in order}
short={g:forces[g].get('logo',g) for g in order}
candidates={c:copy.deepcopy(source['candidates'][c]) for cs in members.values() for c in cs}
territories=source['territories'];n=len(territories)
part_rows=defaultdict(list)
for i,t in enumerate(territories[:NR]):part_rows[t['p']].append(i)
assert len(territories)==len(A),(len(territories),len(A))
BEIGE='#e6dcc3';GREY='#8c8c8c'
modes=[];sets={};checks=[]
edges=[0,20,35,50,65,80,95]


def rgb(c):return '#%02x%02x%02x'%tuple(max(0,min(255,round(v))) for v in c)


def ramp(color):
    c=[int(color[i:i+2],16) for i in (1,3,5)]
    return [rgb([255+(x-255)*f for x in c]) for f in (.12,.4,.7,1)]+[rgb([x*f for x in c]) for f in (.82,.64,.45)]


def records(values,cs):
    total=values.sum(axis=1)
    pcts=np.divide(values*100,total[:,None],out=np.zeros_like(values),where=total[:,None]>0)
    out=[]
    for row,pct,d in zip(values,pcts,total):
        if d<=1e-12:
            out.append(dict(lines=[],metrics=[],fill=BEIGE,note='Sin votos asignados en esta interna.'))
            continue
        first=int(np.argmax(row));tied=np.sum(np.abs(row-row[first])<1e-9)>1
        r=dict(lines=[[c,None,round(float(pct[j]),2)] for j,c in sorted(enumerate(cs),key=lambda item:-pct[item[0]])],metrics=[])
        if tied:r['fill']=GREY
        else:r.update(w=cs[first],q=round(float(pct[first]),2))
        out.append(r)
    return out,total,pcts


for g in order:
    cs=members[g];values=A[:,[ci[c] for c in cs]]
    rec,total,pcts=records(values,cs)
    active=total>1e-12
    error=float(np.max(np.abs(pcts[active].sum(axis=1)-100)))
    assert error<1e-9,(g,error)
    gan='gan' if g==order[0] else g.lower()+'_gan'
    sets[g]=dict(label=names[g],subtitle='Interna '+short[g]+' · estimada')
    prov={}
    for p,idx in part_rows.items():prov[p]=records(values[idx].sum(axis=0,keepdims=True),cs)[0][0]
    regional=values[:NR].sum(axis=0);den=float(regional.sum())
    national=dict(cands=[dict(code=c,votes=float(regional[j]),pct=round(float(regional[j]/den*100),2)) for j,c in enumerate(cs)],
                  slices=[dict(code=c,v=float(regional[j])) for j,c in enumerate(cs)],partp=None,metrics=[])
    note=(names[g]+': porcentajes sobre la suma de votos de sus '+str(len(cs))+' precandidatos. '
          'Estimación por radio con el mismo reparto de la serie: circuitos, locales de referencia 2025 e IDW; radios del censo 2022. '
          'La participación, blancos, nulos y las otras agrupaciones no intervienen en estos porcentajes.')
    keys=[]
    if any(r.get('fill')==BEIGE for r in rec):keys.append([BEIGE,'Sin votos asignados en esta interna'])
    if any(r.get('fill')==GREY for r in rec):keys.append([GREY,'Empate en la interna'])
    modes.append(dict(id=gan,set=g,tile='GANÓ',label='Ganador de la interna',units=rec,prov=prov,national=national,note=note,legend=dict(keys=keys)))
    for j,c in enumerate(cs):
        cols=ramp(candidates[c]['base'])
        bins=np.maximum(0,np.searchsorted(edges,pcts[:,j],side='right')-1)
        units=[dict(fill=cols[int(k)] if active[i] else BEIGE) for i,k in enumerate(bins)]
        pv={}
        for p,idx in part_rows.items():
            r=prov[p];v=values[idx].sum(axis=0);d=v.sum()
            b=max(0,int(np.searchsorted(edges,100*v[j]/d,side='right')-1)) if d>0 else 0
            pv[p]={**r,'fill':cols[b] if d>0 else BEIGE}
            pv[p].pop('w',None);pv[p].pop('q',None)
        modes.append(dict(id=g.lower()+'_'+c.lower(),set=g,tile=candidates[c].get('logo',c)[:6],label='% '+candidates[c]['n'],
                          card_base=gan,units=units,prov=pv,national=national,note=note,
                          legend=dict(title='% '+candidates[c]['n']+' en la interna',stops=[[col,('%g%%'%e if i<6 else '+%g%%'%e)] for i,(col,e) in enumerate(zip(cols,edges))],bars=False,keys=keys)))
    checks.append(dict(grupo=g,nombre=names[g],candidatos=cs,positivos_interna=den,
                       error_max_suma_porcentajes=error,radios_sin_votos=int((~active[:NR]).sum()),
                       ganadores=dict(Counter(r.get('w') for r in rec[:NR] if r.get('w')))))

data=dict(slug=KEY,locale='es-AR',country='Argentina',title='PASO presidenciales en el AMBA de',year='2023',
          labels=dict(pie1='Porcentajes dentro de la interna',pie2='',provinces=''),exterior=False,
          candidates=candidates,bins=[40,45,50,55,60,70],bin_labels=['<40%','40%','45%','50%','55%','60%','+70%'],
          sets=sets,modes=modes,insets=source['insets'],territories=territories)
(HERE/f'dataset_{KEY}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
text=(HERE/'atlas_2023pasocand.html').read_text(encoding='utf8')
i=text.index('const DATA=');j=text.index(';\nconst START_MODE=',i)
text=text[:i]+'const DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+text[j:]


def sub(old,new):
    global text
    assert text.count(old)==1,(old[:90],text.count(old))
    text=text.replace(old,new)


group_options=''.join('<option value="'+g+'">'+html.escape(names[g])+'</option>' for g in order)
controls=('<div class="grp"><label for="internal-group">Interna:</label><select id="internal-group" style="max-width:300px">'+group_options+'</select></div>'
          '<div class="grp"><label for="internal-view">Vista:</label><select id="internal-view" style="max-width:300px"></select></div>')
start=text.index('<div class="grp"><label for="paso-mode">');end=text.index('</div>',start)+6
text=text[:start]+controls+text[end:]
sub('const g=DATA.modes[0].units[i];if(!u.lines)', 'const g=(MODES[m.card_base]||DATA.modes[0]).units[i];if(!u.lines)')
sub('function tilesNow(){const out=DATA.modes.slice(0,4).map(m=>[m.id,m.tile||m.id]);if(!out.some(x=>x[0]===MODE))out.push([MODE,MODES[MODE].tile||MODE]);return out;}',
    'function tilesNow(){return DATA.modes.filter(m=>m.set===MODES[MODE].set).map(m=>[m.id,m.tile||m.id]);}')
sub('function setMode(m){MODE=m;const sm=$("#paso-mode");if(sm)sm.value=m;',
    'function setMode(m){MODE=m;syncInternalControls(m);')
sub('const psel=$("#paso-mode");psel.addEventListener("change",()=>setMode(psel.value));', '''
function syncInternalControls(m){
  const g=MODES[m].set,sg=$("#internal-group"),sv=$("#internal-view");sg.value=g;
  sv.replaceChildren();DATA.modes.filter(x=>x.set===g).forEach(x=>{const op=document.createElement("option");op.value=x.id;op.textContent=x.label||x.tile;sv.appendChild(op);});sv.value=m;
}
$("#internal-group").addEventListener("change",()=>setMode(DATA.modes.find(m=>m.set===$("#internal-group").value).id));
$("#internal-view").addEventListener("change",()=>setMode($("#internal-view").value));''')
sub('href="atlas_2023pasofuerza.html">Ver por fuerza</a>', 'href="atlas_2023pasocand.html">Ver elección completa</a>')
sub('placeholder="Buscar departamento…" aria-label="Buscar departamento"','placeholder="Buscar radio…" aria-label="Buscar radio"')
sub('aria-label="Filtrar provincia"','aria-label="Filtrar partido"')
sub('Todo el país','Todo el AMBA')
sub('</head>','<style>.c-row{grid-template-columns:1fr 80px}.c-row .vt{display:none}.c-met{display:none}</style></head>')
sub('const MANY=N.cands.length>5,Y0=MODE==="gan"?1200:1266;', 'const MANY=N.cands.length>5,Y0=1266;')
# CSV de la interna seleccionada, con porcentajes y sin columnas de otras candidaturas.
start=text.index('$("#b-csv").addEventListener("click",()=>{');end=text.index('\n});',start)+4
text=text[:start]+'''$("#b-csv").addEventListener("click",()=>{
  const M=MODES[MODE],codes=M.national.cands.map(c=>c.code),q=v=>'"'+String(v).replace(/"/g,'""')+'"';
  const rows=[["partido",NIVK[NIVEL],...codes.map(c=>CAND[c].n+" (%)")].map(q).join(",")];
  M.units.forEach((u,i)=>T[i].k===NIVK[NIVEL]&&rows.push([T[i].p,T[i].n,...codes.map(c=>{const l=(u.lines||[]).find(x=>x[0]===c);return l?l[2]:"";})].map(q).join(",")));
  save(new Blob(["\\ufeff"+rows.join("\\n")],{type:"text/csv;charset=utf-8"}),"interna_"+M.set+".csv");
});'''+text[end:]
(HERE/f'atlas_{KEY}.html').write_text(text,encoding='utf8'); __import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "comun")); __import__("logos_al_ras").aplicar(str(HERE/f'atlas_{KEY}.html'))   # logos al ras (2-nov-2026)
dump(HERE/'CONTROL_INTERNAS2023.json',dict(radios=n,internas=checks,modos=len(modes),
     denominador='Suma de los votos estimados de los candidatos de la interna seleccionada',
     color_HRL=candidates['C132_A']['base'],fuente_asignacion='asignacion_2023pasocand.pkl'))
print('Visor:',len(checks),'internas,',len(modes),'modos; HRL',candidates['C132_A']['base'])
