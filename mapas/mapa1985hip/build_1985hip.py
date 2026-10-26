"""Escenario presidencial: perfiles territoriales reales 1985, márgenes del DOCX."""
from pathlib import Path
import json, re, zipfile, xml.etree.ElementTree as ET, collections, csv
ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
source = HERE / '1985_completo.docx'
if not source.exists():
    import shutil
    shutil.copy2(Path.home() / 'Downloads' / '1985_completo.docx', source)
with zipfile.ZipFile(source) as z:
    tree = ET.fromstring(z.read('word/document.xml'))
rows = []
for tr in tree.findall('.//w:tr', NS):
    rows.append([''.join(t.text or '' for t in tc.findall('.//w:t', NS)).strip() for tc in tr.findall('w:tc', NS)])
targets = {}
for row in rows:
    if len(row) == 16 and row[0] not in ('Provincia',''):
        try: targets[row[0]] = [int(row[j].replace('.','')) for j in (1,3,5,7,9,11,13,15)]
        except ValueError: pass
assert len(targets) == 25, (len(targets), rows[:3])
doc_total = targets.pop('TOTAL')
base = json.loads((ROOT/'mapa1985/dataset_1985.json').read_text(encoding='utf8'))
codes = ['MCN','FDS','AF','PC']
names = ['Alfonsín / Cafiero','Massera / Bajczman','Manrique / Rawson','Nadra / Íscaro']
subs = ['Convergencia Nacional','PJ · Democracia Social','Alianza Federal','Partido Comunista']
colors = ['#91316b','#4d5976','#d69b27','#b51d27']
base['candidates'] = {c:dict(n=n,sub=s,base=col) for c,n,s,col in zip(codes,names,subs,colors)}
base['candidates'].update(P_BLA=dict(n='En blanco',base='#cccccc'),P_NUL=dict(n='Anulados',base='#999999'))
import base64, io
from PIL import Image
for code, filename in [('MCN','RA_chapa_Alfonsin_1983.png'),('FDS','Flag_of_the_Justicialist_Party_(square_version).svg'),('AF','ALIANZA_FEDERAL1983_2.png'),('PC','Frepu_logo.png')]:
    path = ROOT / '../logos' / filename
    if path.suffix == '.svg':
        data=path.read_bytes(); mime='image/svg+xml'; ar=1
    else:
        im=Image.open(path).convert('RGBA'); ar=im.width/im.height
        im.thumbnail((400,300)); buf=io.BytesIO(); im.save(buf,format='PNG')
        data=buf.getvalue(); mime='image/png'
    base['candidates'][code].update(img='data:'+mime+';base64,'+base64.b64encode(data).decode(),ar=ar,bl=min(1.1,98/(ar*50)))
pj = {'pj','frejuli','frejuchu','fren','cbt','lab','fupop'}
pc = {'frepu','frepun','pc','mas'}
af = {'ucd','adc','unpop','apce','pd','dl','dj','adi','dc','tbdc','pdp','palfdp'}
def group(c,p):
    if c=='flib': return 1 if p=='Capital Federal' else 3
    return 1 if c in pj else 3 if c in pc else 2 if c in af else 0
territories = base['territories']
profiles = []
for t,r in zip(territories,base['modes'][0]['units']):
    a=[0]*8
    if t['n']!='Islas Malvinas':
        for c,v,_ in r['lines']:
            if c=='P_BLA': a[4]+=v
            elif c=='P_NUL': a[5]+=v
            else: a[group(c[2:],t['p'])]+=v
        metrics=dict(r['metrics'])
        a[6]=int(metrics['Votantes'].replace('.',''))
        a[7]=int(metrics.get('Inscriptos','0').replace('.',''))
    profiles.append(a)
def allocate(weights,total):
    if not total: return [0]*len(weights)
    assert sum(weights)>0, ('Perfil territorial ausente',total)
    raw=[w*total/sum(weights) for w in weights]
    out=[int(v) for v in raw]
    for i in sorted(range(len(out)),key=lambda i:-(raw[i]-out[i]))[:total-sum(out)]: out[i]+=1
    return out
votes=[[0]*8 for _ in profiles]
audit=[]
for p,target in targets.items():
    ids=[i for i,t in enumerate(territories) if t['p']==p and t['n']!='Islas Malvinas']
    assert ids,p
    for k in range(8):
        weights=[profiles[i][k] for i in ids]
        if target[k] and not sum(weights):
            weights=[sum(profiles[i][:4]) for i in ids]
            audit.append(dict(provincia=p,perfil_sin_votos=codes[k] if k<4 else str(k),criterio='Distribución proporcional a los positivos reales de 1985; estimación hipotética'))
        vals=allocate(weights,target[k])
        for i,v in zip(ids,vals): votes[i][k]=v
    audit.append(dict(provincia=p,positivos=sum(target[:4]),votantes=target[6],diferencia_votantes=target[6]-sum(target[:6])))
fmt=lambda v:f'{v:,}'.replace(',','.')
def rec(v):
    pos=sum(v[:4]); w=max(range(4),key=lambda k:v[k])
    return dict(w=codes[w],q=round(v[w]*100/pos,2),lines=[[c,int(n),round(n*100/pos,2)] for c,n in zip(codes,v[:4])] + [[c,v[k],round(100*v[k]/v[6],2)] for c,k in [('P_BLA',4),('P_NUL',5)]],metrics=[['Inscriptos',fmt(v[7])],['Votantes',fmt(v[6])],['Participación',(f'{100*v[6]/v[7]:.2f} %'.replace('.',',') if v[7] else 'Sin padrón local')],['Votos positivos',fmt(pos)]],note='Escenario hipotético: estimación departamental ajustada a los totales provinciales del documento, con perfiles electorales de 1985. Votantes, blancos y nulos se ajustan por separado; las discrepancias del documento se conservan.')
unit=[rec(v) if sum(v[:4]) else dict(lines=[],metrics=[],fill='#a9a9a9',note='Sin votación en este escenario.') for v in votes]
prov={p:rec(v) for p,v in targets.items()}
tot=[sum(v[k] for v in targets.values()) for k in range(8)]
wins=collections.Counter(r.get('w') for r in unit)
ranking=sorted(range(4),key=lambda k:-tot[k]); pos=sum(tot[:4])
nat=dict(cands=[dict(code=codes[k],votes=tot[k],pct=round(tot[k]*100/pos,2)) for k in ranking if wins[codes[k]]],slices=[dict(code=codes[k],v=tot[k]) if wins[codes[k]] else dict(fill=colors[k],v=tot[k]) for k in ranking],partp=round(100*tot[6]/tot[7],2),metrics=rec(tot)['metrics']+[['En blanco',fmt(tot[4])],['Anulados',fmt(tot[5])]])
note='SIMULACIÓN · 10 de marzo de 1985. Totales provinciales: documento aportado. Distribución territorial: votos legislativos reales de 1985 agrupados según el escenario y ajustados por candidatura y provincia. No son resultados históricos.'
modes=[dict(id='gan',tile='GANÓ',note=note,units=unit,prov=prov,national=nat,legend={})]
for k,c in enumerate(codes):
    edges=[0,1,2,3,5,10,20] if k==3 else [0,10,20,30,40,50,60]
    col=colors[k]; rgb=[int(col[j:j+2],16) for j in (1,3,5)]
    shades=['#'+''.join(f'{round(255+(x-255)*(0.12+0.88*j/6)):02x}' for x in rgb) for j in range(7)]
    def shade(v): return shades[max(j for j,e in enumerate(edges) if 100*v[k]/sum(v[:4])>=e)]
    un=[dict(r,fill=shade(v)) if sum(v[:4]) else dict(r) for r,v in zip(unit,votes)]
    pv={p:dict(prov[p],fill=shade(v)) for p,v in targets.items()}
    modes.append(dict(id=c.lower(),tile=c,note=note,units=un,prov=pv,national=nat,legend=dict(title='% '+names[k],stops=list(zip(shades,[str(e)+' %' for e in edges])),bars=False)))
malvinas = [i for i,t in enumerate(territories) if t['n']=='Islas Malvinas']
for mode in modes:
    for i in malvinas:
        ref=mode['prov']['Tierra del Fuego']
        mode['units'][i]={k:v for k,v in ref.items() if k in ('w','q','fill')}
        mode['units'][i].update(lines=[],metrics=[],note='Color de referencia: resultado provincial de Tierra del Fuego. No se asignan ni suman votos propios a las Malvinas.')
base.update(slug='presidenciales_1985_hipoteticas',title='Presidenciales hipotéticas de',modes=modes,sets={'1':dict(label='1985',subtitle='Simulación · 10 de marzo')})
payload=json.dumps(base,ensure_ascii=False,separators=(',',':'))
(HERE/'dataset_1985hip.json').write_text(payload,encoding='utf8')
html=(ROOT/'mapa1985/atlas_1985.html').read_text(encoding='utf8')
html,n=re.subn(r'const DATA=.*?;\n',lambda m:'const DATA='+payload+';\n',html,count=1)
assert n==1
html=html.replace('<title>Elecciones legislativas 1985</title>','<title>1985 · Presidenciales hipotéticas</title>')
html=html.replace('class="pfm" style="fill:#a9a9a9;stroke:#a9a9a9;stroke-width:5px;stroke-linejoin:round"', 'class="pf" data-prov="Tierra del Fuego" style="stroke:#1b1b1b;stroke-width:5px;stroke-linejoin:round"')
(HERE/'atlas_1985hip.html').write_text(html,encoding='utf8')
report=dict(totales_provincias=tot,total_declarado_docx=doc_total,diferencia=[a-b for a,b in zip(tot,doc_total)],ganadores=dict(wins),auditoria=audit,mapeo=dict(Massera=sorted(pj),Nadra=sorted(pc),Manrique=sorted(af),Alfonsin='Todos los códigos restantes',flib='Massera en Capital; Nadra en el resto'))
(HERE/'auditoria.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
with (HERE/'estimaciones_departamentales.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['provincia','unidad']+codes+['blancos','nulos','votantes','inscriptos'])
    writer.writerows([t['p'],t['n']]+v for t,v in zip(territories,votes) if sum(v[:4]))
print(json.dumps(report,ensure_ascii=True))


