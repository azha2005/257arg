import os as _os, sys as _sys; _sys.path[:0] = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "comun")]  # módulos compartidos (reorganización: ver README)
from pathlib import Path
import sys,json,re,csv,os,collections,copy
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from atlas_leg8399 import logo
src=ROOT/'mapa2001'
ds=json.loads((src/'dataset_2001.json').read_text(encoding='utf8'))
ds['candidates']['MPN'].update(n='Movimiento Popular',sub='Neuquino')
ds['candidates']['ARI']['sub']='y aliados'
ds['candidates']['PAUFE']['base']='#f59e0b'
original=ds['modes'][0]
text=(src/'build_2001.py').read_text(encoding='utf8')
ns=dict(csv=csv,os=os,HERE=str(src))
exec(text[text.index('import unicodedata'):text.index('CODE2BLOC = {}')],ns)
for code,candidate in ds['candidates'].items():
    if code.startswith('P_') and ':' in code and ns['bloc_of'](code[2:])=='PAUFE':
        candidate['base']='#f59e0b'
def transform(r):
    if not r.get('lines'):return copy.deepcopy(r),None
    m=dict(r['metrics']);positive=int(m['Votos positivos'].replace('.',''))
    bronca=sum(v for c,v,q in r['lines'] if c in ('P_BLA','P_NUL'))
    denominator=positive+bronca
    groups=collections.Counter(BRONCA=bronca)
    lines=[]
    for c,v,q in r['lines']:
        if c in ('P_BLA','P_NUL'):continue
        if c.startswith('P_') and ':' in c:groups[ns['bloc_of'](c[2:])]+=v
        lines.append([c,v,round(100*v/denominator,2)])
    lines.append(['BRONCA',bronca,round(100*bronca/denominator,2)])
    lines.sort(key=lambda x:-x[1]);w=max(groups,key=groups.get)
    if w not in ds['candidates']:raise ValueError(('Ganador no identificado',w))
    metrics=r['metrics']+[['Blancos + nulos',f'{bronca:,}'.replace(',','.')],['Base de comparación',f'{denominator:,}'.replace(',','.')]]
    note=(r.get('note','')+' Variante analítica: blancos y nulos se agrupan como voto bronca; no son una lista electoral. Porcentajes sobre positivos + blancos + nulos; no se suman otra vez como votos de una candidatura real.').strip()
    return dict(w=w,q=round(100*groups[w]/denominator,2),lines=lines,metrics=metrics,note=note),dict(groups=groups,denominator=denominator)
ds['candidates']['BRONCA']=dict(n='Voto bronca',sub='Blancos + nulos',base='#5b5b5b',logo='BRONCA',**logo('Voto_bronca_urna.svg'))
records=[];analyses=[]
for r in original['units']:
    a,b=transform(r);records.append(a);analyses.append(b)
prov={};pa={}
for p,r in original['prov'].items():prov[p],pa[p]=transform(r)
wins=collections.Counter(r.get('w') for r in records if r.get('w'))
oldnat=original['national'];metrics=dict(oldnat['metrics'])
v=lambda k:int(metrics[k].replace('.',''))
den=v('Votos positivos')+v('En blanco')+v('Nulos');bronca=v('En blanco')+v('Nulos')
nat=copy.deepcopy(oldnat)
allnat={c['code']:c['votes'] for c in oldnat['cands']};allnat['BRONCA']=bronca
nat['cands']=sorted([dict(code=c,votes=n,pct=round(100*n/den,2)) for c,n in allnat.items() if wins[c]],key=lambda r:-r['votes'])
nat['slices']=[dict(code=c['code'],v=c['votes']) for c in nat['cands']]+[dict(fill='#9a9a9a',v=den-sum(c['votes'] for c in nat['cands']))]
nat['metrics'] += [['Voto bronca (blancos + nulos)',f'{bronca:,}'.replace(',','.')],['Base de comparación',f'{den:,}'.replace(',','.')]]
note='VARIANTE ANALÍTICA · Elecciones legislativas de 2001. Voto bronca = blancos + nulos, tratado como una opción para comparar ganadores. No fue una candidatura real. Porcentajes sobre positivos + blancos + nulos. Datos territoriales y alianzas: atlas original de 2001; total nacional: Wikipedia.'
modes=[dict(id='gan',tile='GANÓ',note=note,units=records,prov=prov,national=nat,legend=dict(keys=[]))]
for code in ['BRONCA','PJ','ALI','ARI']:
    col=ds['candidates'][code]['base'];rgb=[int(col[i:i+2],16) for i in (1,3,5)];edges=[0,10,20,30,40,50,60]
    shades=['#'+''.join(f'{round(255+(v-255)*(0.12+0.88*j/6)):02x}' for v in rgb) for j in range(7)]
    def recolor(r,a):
        nr={k:v for k,v in r.items() if k not in ('w','q')}
        if a:
            pct=100*a['groups'][code]/a['denominator'];nr['fill']=shades[max(j for j,e in enumerate(edges) if pct>=e)]
        return nr
    modes.append(dict(id=code.lower(),tile='BRON.' if code=='BRONCA' else code,note=note,units=[recolor(r,a) for r,a in zip(records,analyses)],prov={p:recolor(prov[p],a) for p,a in pa.items()},national=nat,legend=dict(title='% '+ds['candidates'][code]['n'],stops=list(zip(shades,[f'{x} %' for x in edges])),bars=False)))
ds.update(slug='legislativas_2001_voto_bronca',title='Legislativas con voto bronca de',modes=modes,sets={'1':dict(label='2001',subtitle='Variante: blancos + nulos')},labels=dict(pie1='Sobre positivos + blancos + nulos'))
payload=json.dumps(ds,ensure_ascii=False,separators=(',',':'))
(HERE/'dataset_2001bronca.json').write_text(payload,encoding='utf8')
html=(src/'atlas_2001.html').read_text(encoding='utf8')
html,n=re.subn(r'const DATA=.*?;\n',lambda m:'const DATA='+payload+';\n',html,count=1);assert n==1
html=re.sub(r'<title>.*?</title>','<title>Legislativas 2001 · Variante con voto bronca</title>',html,count=1)
(HERE/'atlas_2001bronca.html').write_text(html,encoding='utf8')
(HERE/'auditoria.json').write_text(json.dumps(dict(ganadores=dict(wins),bronca_nacional=bronca,denominador_nacional=den,porcentaje=round(100*bronca/den,4),provincias_ganadas=[p for p,r in prov.items() if r.get('w')=='BRONCA']),ensure_ascii=False,indent=2),encoding='utf8')
print('Ganadores',dict(wins),'Voto bronca nacional',bronca,'/',den)
