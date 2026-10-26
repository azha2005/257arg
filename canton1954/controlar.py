"""Cotejos: nunca calcula ni imputa celdas de la transcripción."""
from pathlib import Path
import json,re,unicodedata,difflib,itertools
import numpy as np
from armar import GRUPOS
ROOT=Path(__file__).resolve().parent
def norm(s):
    return re.sub('[^a-z]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def manual():
    pages={}
    for line in (ROOT/'manual.txt').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):continue
        p,name,values=line.split('|');p=int(p)
        pages.setdefault(p,[]).append({'departamento':name,'valores':{str(i):int(v) if v.isdigit() else None for i,v in enumerate(values.split(),1)},'literales':{str(i):v for i,v in enumerate(values.split(),1)},'estado':'transcripción visual'})
    return pages
def main():
    man=manual(); pages={}; dudas=[]
    globalnames={}; aligned={}
    for prov,start,count,stride,cols,cargo in GRUPOS:
        if stride==1:continue
        for cat in range(2):
            entries=[]
            for pp in range(start+cat*stride,start+(cat+1)*stride):
                dd=json.loads((ROOT/f'borrador/p_{pp}.json').read_text(encoding='utf-8'))
                entries.extend((pp,r) for r in dd['filas'])
            globalnames[(prov,cat)]=entries
            canonical=[r['departamento'] for pp in range(start+2*stride,start+3*stride) for r in man[pp]]
            entries=[(pp,r) for pp,r in entries if norm(r['departamento']) not in ('partidos','departamentos','clave','clava')]
            n,m=len(canonical),len(entries)
            dp=np.full((n+1,m+1),-1e9);dp[0,0]=0;trace={}
            for ii in range(n+1):
                for jj in range(m+1):
                    if ii<n and dp[ii,jj]-.8>dp[ii+1,jj]:dp[ii+1,jj]=dp[ii,jj]-.8;trace[ii+1,jj]=(ii,jj,'skipname')
                    if jj<m and dp[ii,jj]-.8>dp[ii,jj+1]:dp[ii,jj+1]=dp[ii,jj]-.8;trace[ii,jj+1]=(ii,jj,'skiprow')
                    if ii<n and jj<m:
                        sc=difflib.SequenceMatcher(None,norm(canonical[ii]),norm(entries[jj][1]['departamento'])).ratio()
                        score=3*sc-1
                        if dp[ii,jj]+score>dp[ii+1,jj+1]:dp[ii+1,jj+1]=dp[ii,jj]+score;trace[ii+1,jj+1]=(ii,jj,'match')
            ii,jj=n,m;lookup={}
            while ii or jj:
                prev_i,prev_j,op=trace[ii,jj]
                if op=='match':lookup[canonical[ii-1]]=entries[jj-1]
                ii,jj=prev_i,prev_j
            aligned[(prov,cat)]=lookup
    dest=ROOT/'transcripcion';dest.mkdir(exist_ok=True)
    for prov,start,count,stride,cols,cargo in GRUPOS:
        for off in range(count):
            p=start+off
            raw=json.loads((ROOT/f'revision/p_{p}_celdas.json').read_text(encoding='utf-8'))
            draft=json.loads((ROOT/f'borrador/p_{p}.json').read_text(encoding='utf-8'))
            if p in man:
                draft['filas']=man[p]
                draft['estado']='transcripción visual'
            else:
                canonical=man[start+2*stride+off%stride]
                names=[r['departamento'] for r in canonical]
                available=list(enumerate(draft['filas']))
                matches={};used=set()
                candidates=[]
                for i,name in enumerate(names):
                    for j,row in available:
                        score=difflib.SequenceMatcher(None,norm(name),norm(row['departamento'])).ratio()
                        if score>=.58:candidates.append((score,i,j))
                for score,i,j in sorted(candidates,reverse=True):
                    if i not in matches and j not in used:
                        matches[i]=j;used.add(j)
                coords=[]
                for i,j in matches.items():
                    row=draft['filas'][j]
                    coords.append((i,row['coordenadas']['1']['y']))
                slopes=[(y2-y1)/(i2-i1) for (i1,y1),(i2,y2) in itertools.combinations(coords,2) if i1!=i2 and 35<(y2-y1)/(i2-i1)<70]
                slope=float(np.median(slopes)) if slopes else 49
                origin=float(np.median([y-slope*i for i,y in coords])) if coords else 300
                rows=[]
                for i,name in enumerate(names):
                    if i in matches:
                        y=draft['filas'][matches[i]]['coordenadas']['1']['y']
                    else:
                        y=origin+slope*i;dudas.append([p,name,'nombre/fila no reconocido'])
                    sourcep=p
                    sourceraw=raw
                    if stride>1:
                        found=aligned[(prov,off//stride)].get(name)
                        if found:
                            sourcep,source_row=found
                            y=source_row['coordenadas']['1']['y']
                            sourceraw=json.loads((ROOT/f'revision/p_{sourcep}_celdas.json').read_text(encoding='utf-8'))
                    values={};literals={}
                    for ci,col in enumerate(sourceraw['columnas_ocr'][1:len(cols)+1],1):
                        near=[w for w in col if abs(w['y']+w['h']/2-y)<22]
                        token=' '.join(w['text'] for w in near)
                        digits=re.sub('[^0-9]','',token)
                        val=int(digits) if digits else None
                        key=str(ci)
                        # The source marker is known from the visually read total.
                        mark=canonical[i]['literales'][key]
                        if mark in ('*','**'):val=None;token=mark
                        values[key]=val;literals[key]=token
                    rows.append({'departamento':name,'valores':values,'literales':literals,'y':y,'pagina_fuente':sourcep,'estado':'OCR pendiente de cotejo visual'})
                draft['filas']=rows
                draft['estado']='OCR pendiente de cotejo visual'
                second=ROOT/f'revision/p_{p}_rapid.json'
                if second.exists():
                    second=json.loads(second.read_text(encoding='utf-8'))
                    for row in draft['filas']:
                        for c,read in second.get(row['departamento'],{}).items():
                            row['valores'][c]=read['valor']
                            row['literales'][c]=read['literal']
                    draft['estado']='segunda lectura local pendiente de cotejo'
            pages[p]=draft
            paired=ROOT/'revision_pares.txt'
            if paired.exists():
                for line in paired.read_text(encoding='utf-8').splitlines():
                    if not line or line.startswith('#'):continue
                    sheet,readings=line.split('|')
                    tag=sheet if sheet[0].isalpha() else f'{int(sheet):02}'
                    entries=json.loads((ROOT/f'revision/hoja_{tag}.json').read_text(encoding='utf-8'))
                    readings=readings.split()
                    assert len(readings)==len(entries),(sheet,len(readings),len(entries))
                    for entry,pair in zip(entries,readings):
                        for pp,v in zip(entry['paginas'][:2],pair.split(',')):
                            if pp!=p:continue
                            row=next(r for r in draft['filas'] if r['departamento']==entry['unidad'])
                            c=entry['columna'];row['valores'][c]=int(v) if v.isdigit() else None;row['literales'][c]=v
                            row.setdefault('celdas_revisadas',[]).append(c)
            overrides=ROOT/'correcciones_filas.txt'
            if overrides.exists():
                for line in overrides.read_text(encoding='utf-8').splitlines():
                    if not line or line.startswith('#'):continue
                    pp,name,values=line.split('|')
                    if int(pp)!=p:continue
                    row=next(r for r in draft['filas'] if r['departamento']==name)
                    row['valores']={str(i):int(v) if v.isdigit() else None for i,v in enumerate(values.split(),1)}
                    row['literales']={str(i):v for i,v in enumerate(values.split(),1)}
                    row['celdas_revisadas']=list(row['valores'])
                    row['estado']='transcripción visual'
            if p==180:
                row=next(r for r in draft['filas'] if r['departamento']=='General Arenales')
                row['pagina_fuente']=179
            (dest/f'p_{p}.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2),encoding='utf-8')
    mismatches=[]; ok=0
    for prov,start,count,stride,cols,cargo in GRUPOS:
        if count==1:continue
        for k in range(stride):
            pp=[start+k,start+stride+k,start+2*stride+k]
            maps=[{r['departamento']:r for r in pages[p]['filas']} for p in pp]
            for name,total in maps[2].items():
                for c in total['valores']:
                    vs=[m[name]['valores'][c] for m in maps]
                    if all(v is not None for v in vs):
                        if vs[0]+vs[1]==vs[2]:ok+=1;continue
                    elif total['literales'][c] in ('*','**'):continue
                    mismatches.append({'paginas':pp,'unidad':name,'columna':c,'lecturas':vs})
    (ROOT/'revision/cotejo_sexos.json').write_text(json.dumps(mismatches,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'revision/nombres_dudosos.json').write_text(json.dumps(dudas,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Visuales',len(man),'filas',sum(len(v) for v in man.values()),'coincidencias',ok,'diferencias',len(mismatches),'nombres',len(dudas))
if __name__=='__main__':main()
