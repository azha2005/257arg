"""Ocho remakes condicionados a las imágenes: cifras nacionales + ganadores legibles.

Reutiliza el HTML/cartografía del presidencial 2003. Nunca modifica el histórico.
Los porcentajes departamentales son soluciones de un modelo, no datos recuperados.
"""
from pathlib import Path
from collections import Counter
import base64,copy,csv,hashlib,io,json,re,shutil,sys
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp
from PIL import Image
from registrar import ROOT,SOURCE,OUT
from escalas import color_ramp,apply_scales,patch_shader
from enteros import integerize
from botones import patch_tiles
sys.path.insert(0,str(ROOT/'comun'))
from creditos_escenarios import aplicar as acreditar

HERE=Path(__file__).resolve().parent
DEST=ROOT/'mapas/mapa2003alt'
BEIGE='#e8dfc9'
GREY='#a9a9a9'

# Coeficientes heurísticos de perfiles presidenciales observados; no transferencias identificadas.
PROFILES={
 'MAC':{'L':1,'C':.7,'K':.4,'R':.3},
 'ALV':{'K':.6,'C':.8,'MOREAU':.5,'BRAVO':.7,'R':.15},
 'CAV':{'L':.8,'M':.5,'MOREAU':.1},
 'HIL':{'M':.5,'K':.7,'R':.5},
 'BIL':{'L':.6,'C':.6,'K':.5,'R':.3,'M':.2},
 'DLS':{'K':.7,'M':.4,'R':.2},
 'REU':{'K':1,'L':.6,'C':.4,'R':.3},
 'TERR':{'MOREAU':.6,'C':.5,'L':.4}
}
CROPS={
 'MAC':('macri',(276,2200,326,2219)),
 'ALV':('alvarez',(276,2234,310,2253)),
 'CAV':('alvarez',(276,2262,310,2281)),
 'HIL':('alvarez',(276,2290,326,2309)),
 'BIL':('bilardo',(267,2432,314,2451)),
 'DLS':('lemas',(267,2394,314,2413)),
 'REU':('reutemann',(271,2200,321,2219))
}

def num(v):return f'{v:,.0f}'.replace(',','.')
def pct(v):return f'{v:.2f}'.replace('.',',')+' %'
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
def constrained_fit(prior,mass,target,winners,ratio=1.02):
    """Proyección de entropía con márgenes nacionales y ganador de imagen.

    Se resuelve el dual convexo. Cada fila se proyecta a la región donde el
    ganador leído supera a sus rivales en un factor 1.02 (supuesto de separación).
    """
    prior=np.maximum(prior,1e-8);prior/=prior.sum(axis=1)[:,None]
    logp=np.log(prior);target=np.array(target,float);weights=mass/mass.sum();t=target/target.sum()
    k=prior.shape[1];groups={w:np.where(winners==w)[0] for w in set(winners) if w>=0}
    def calc(beta):
        logs=logp+beta;z=logs.copy()
        for w,idx in groups.items():
            others=np.array([j for j in range(k) if j!=w]);order=np.argsort(-logs[idx][:,others],axis=1)
            ordered=others[order];b=logs[idx,w]-np.log(ratio);a=ratio*b;n=np.full(len(idx),ratio)
            active=np.ones(len(idx),bool);chosen=np.zeros((len(idx),k),bool)
            for j in range(k-1):
                jj=ordered[:,j];value=logs[idx,jj]
                hit=active&(value>b);active=hit
                a[hit]+=value[hit];n[hit]+=1;b[hit]=a[hit]/n[hit]
                chosen[np.where(hit)[0],jj[hit]]=True
            zz=z[idx].copy();zz[chosen]=np.broadcast_to(b[:,None],zz.shape)[chosen];zz[:,w]=b+np.log(ratio);z[idx]=zz
        lz=logsumexp(z,axis=1);p=np.exp(z-lz[:,None])
        return float(weights@lz-t@beta),weights@p-t,p
    def fun(x):
        f,g,_=calc(np.r_[x,0]);return f,g[:-1]
    f=minimize(fun,np.zeros(k-1),jac=True,method='L-BFGS-B',options=dict(maxiter=3000,ftol=1e-15,gtol=1e-12,maxls=50))
    _,grad,p=calc(np.r_[f.x,0]);matrix=p*mass[:,None]
    # Cerrar los márgenes a <0.01 voto con Newton sobre las variables duales.
    for it in range(12):
        diff=matrix.sum(axis=0)-target
        if np.max(np.abs(diff))<.005:break
        b=np.r_[f.x,0];J=np.empty((k-1,k-1));eps=1e-5
        for j in range(k-1):
            bb=b.copy();bb[j]+=eps;_,gg,_=calc(bb);J[:,j]=(gg[:-1]-grad[:-1])/eps
        delta=np.linalg.lstsq(J,grad[:-1],rcond=None)[0]
        f.x-=delta;_,grad,p=calc(np.r_[f.x,0]);matrix=p*mass[:,None]
    err=float(np.max(np.abs(matrix.sum(axis=0)-target)))
    mismatch=[int(i) for i,w in enumerate(winners) if w>=0 and int(matrix[i].argmax())!=w]
    assert err<.01,(err,f.message)
    assert not mismatch,mismatch
    return matrix,dict(max_national_error=err,max_row_error=float(np.max(np.abs(matrix.sum(axis=1)-mass))),optimizer=str(f.message),iterations=int(f.nit),winner_ratio=ratio)

def make_logos(cfg,base):
    (HERE/'logos').mkdir(exist_ok=True);byid={s['id']:s for s in cfg};res={};audit=[]
    for code,(sid,box) in CROPS.items():
        src=SOURCE/byid[sid]['file'];im=Image.open(src).convert('RGB').crop(box)
        p=HERE/'logos'/f'{code}.png';im.save(p)
        b=io.BytesIO();im.save(b,format='PNG')
        res[code]=dict(img='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode(),ar=im.width/im.height,bl=min(1.1,110/(42*(im.width/im.height))))
        audit.append(dict(code=code,source=byid[sid]['file'],crop=box,file=str(p.relative_to(ROOT)),method='Recorte del bloque de logo, sin redibujar ni ampliar artificialmente.'))
    for code,r in base['candidates'].items():
        if r.get('img'):audit.append(dict(code=code,source='mapas/mapa2003pres/dataset_2003pres.json',reference='mapas/mapaAMBA2003radios/atlas_amba2003radios.html',method='Imagen y proporciones heredadas.'))
    dump(HERE/'logos_usados.json',audit)
    return res

def record(values,codes,note):
    total=float(values.sum());j=int(values.argmax())
    return dict(w=codes[j],q=round(100*float(values[j])/total,4),lines=[[codes[j],int(values[j]),round(100*float(values[j])/total,4)] for j in np.argsort(-values) if values[j]>1e-6],metrics=[['Votos modelados',num(total)]],note=note)

def main():
    DEST.mkdir(exist_ok=True);cfg=json.loads((HERE/'escenarios.json').read_text('utf8'))
    readings=json.loads((HERE/'lecturas.json').read_text('utf8'))
    provread=json.loads((HERE/'lecturas_provincias.json').read_text('utf8'))
    base=json.loads((ROOT/'mapas/mapa2003pres/dataset_2003pres.json').read_text('utf8'))
    template=(ROOT/'mapas/mapa2003pres/atlas_2003pres.html').read_text('utf8')
    logos=make_logos(cfg,base);T=base['territories'];old=base['modes'][0]['units']
    valid=[i for i,t in enumerate(T) if t['n']!='Islas Malvinas'];oldcodes=[c for c in base['candidates'] if not c.startswith('P_')]
    raw=np.array([[dict((r[0],r[1]) for r in old[i]['lines']).get(c,0) for c in oldcodes] for i in valid],float)
    row=raw.sum(axis=1);prop=raw/row[:,None];actual={c:prop[:,j] for j,c in enumerate(oldcodes)}
    outputs=[]
    ant={'macri':'MAC','alvarez':'CAV','bilardo':'BIL','kirchner':'M','rodriguezsaa':'L','lemas':'L','menem':'M','reutemann':'REU'}
    sourcehash={str((SOURCE/s['file'])):hashlib.sha256((SOURCE/s['file']).read_bytes()).hexdigest() for s in cfg}
    dump(HERE/'insumos.json',dict(images=sourcehash,base_sha256=hashlib.sha256((ROOT/'mapas/mapa2003pres/dataset_2003pres.json').read_bytes()).hexdigest(),profiles=PROFILES,territorial_boosts={'DLS':{'Córdoba':6,'Entre Ríos':2.5},'REU':{'Santa Fe':2},'HIL':{'Buenos Aires':1.5}}))
    for s in cfg:
        sid=s['id'];codes=[c[0] for c in s['candidates']];den=round(s['padron']*s['turnout']/100)
        target=np.array([c[3] if c[3] is not None else round(den*c[4]/100) for c in s['candidates']],float)
        mass=row/row.sum()*target.sum();prior=[];CAND={}
        for c,name,sub,v,p,col in s['candidates']:
            v0=copy.deepcopy(base['candidates'].get(c,{}));v0.update(n=name,sub=sub,base=col,bar=col,txt=col,ramp=color_ramp(col),logo=c)
            if c in logos:v0.update(logos[c])
            CAND[c]=v0
            if c in PROFILES:z=sum(weight*actual[key] for key,weight in PROFILES[c].items())
            else:z=actual[c].copy()
            z=z.copy()
            for j,i in enumerate(valid):
                p=T[i]['p'];boost=6 if c=='DLS' and p=='Córdoba' else 2.5 if c=='DLS' and p=='Entre Ríos' else 2 if c=='REU' and p=='Santa Fe' else 1.5 if c=='HIL' and p=='Buenos Aires' else 1
                z[j]*=boost
            prior.append(z+.001)
        read={r['i']:r for r in readings['scenarios'][sid]}
        read[len(T)-1]=dict(i=len(T)-1,p='Tierra del Fuego',n='Antártida',readable=True,reading=dict(w=ant[sid],layer='Antártida: lectura visual',agreement=1,pixels=None))
        winners=np.array([codes.index(read[i]['reading']['w']) if read.get(i,{}).get('readable') else -1 for i in valid])
        matrix,audit=constrained_fit(np.array(prior).T,mass,target,winners)
        # Ajuste jerárquico: conservar también el mini mapa provincial del original.
        provinces=sorted({T[i]['p'] for i in valid})
        groups=[np.array([j for j,i in enumerate(valid) if T[i]['p']==p]) for p in provinces]
        aggregate=np.array([matrix[idx].sum(axis=0) for idx in groups])
        pw=np.array([codes.index(provread[sid][p]['w']) for p in provinces])
        aggregate,_=constrained_fit(aggregate,aggregate.sum(axis=1),target,pw)
        subchecks=[]
        for pi,idx in enumerate(groups):
            matrix[idx],check=constrained_fit(matrix[idx],mass[idx],aggregate[pi],winners[idx])
            subchecks.append(check['max_national_error'])
        audit['max_national_error']=float(np.max(np.abs(matrix.sum(axis=0)-target)))
        audit['provincial_winners_matched']=all(codes[int(matrix[idx].sum(axis=0).argmax())]==provread[sid][p]['w'] for p,idx in zip(provinces,groups))
        audit['hierarchical_adjustment']='Global con ganadores locales → márgenes provinciales con ganadores provinciales → ajuste local dentro de cada provincia.'
        assert audit['max_national_error']<.01 and audit['provincial_winners_matched'],audit
        matrix,rounding=integerize(matrix,target,groups)
        audit['rounding']=rounding;audit['max_national_error']=0
        ds=copy.deepcopy(base);ds.update(slug='2003alt_'+sid,candidates=CAND)
        ds['sets']={'1':dict(label='Escenario hipotético',subtitle='Hipotético · '+s['title']+' · '+s['round'])}
        ds['labels'].update(pie1='Votos del original · resto sin desglose',pie2='Anillo exterior: participación del original')
        units=[dict(lines=[],metrics=[],fill=GREY,note='Malvinas: sin voto argentino.') for _ in T]
        compare=copy.deepcopy(units)
        note='ESCENARIO HIPOTÉTICO. Cifras nacionales transcritas del PNG aportado. Votos locales estimados con perfiles de 2003 y ajuste de entropía restringido a ganadores legibles; no son datos originales recuperados ni segundas preferencias observadas. Porcentajes locales sobre candidaturas modeladas. El residuo nacional no se reparte territorialmente. Ver Lectura del original y método.'
        for j,i in enumerate(valid):
            rr=read.get(i,{});q=rr.get('reading');readable=rr.get('readable',False)
            info=(f"Ganador leído automáticamente en {q['layer']} (acuerdo de color {q['agreement']*100:.1f} %)." if readable and q['pixels'] is not None else 'Ganador de Antártida leído visualmente en el recuadro.' if readable else 'Ganador sin lectura suficiente en el original: estimado libremente a partir de los perfiles y los márgenes nacionales.')
            units[i]=record(matrix[j],codes,'Estimación hipotética; votos enteros por redondeo controlado. '+info)
            compare[i]=copy.deepcopy(units[i])
            if readable:
                # Esta vista conserva sólo la identidad leída; no atribuye porcentaje a la imagen.
                compare[i].update(w=q['w'],q=0,note='Lectura de la imagen: sólo el ganador. '+info+' Las cifras de la ficha pertenecen al modelo.')
            else:compare[i].pop('w',None);compare[i].pop('q',None);compare[i].update(fill=BEIGE,note='Lectura insuficiente del original; sin ganador asignado en esta vista. Las cifras de la ficha pertenecen al modelo.')
        win=Counter(r.get('w') for r in units if r.get('w'));wc=sorted(win,key=lambda c:-target[codes.index(c)])
        # Conserva porcentajes impresos aunque haya un cierre incompatible en el original.
        cs=[dict(code=c,votes=int(target[codes.index(c)]),pct=next(a[4] for a in s['candidates'] if a[0]==c)) for c in wc]
        residual=max(0,den-int(target.sum()))
        slices=[dict(code=c,v=int(target[codes.index(c)])) for c in wc]
        other=int(target.sum())-sum(c['votes'] for c in cs)+residual
        if other:slices.append(dict(fill='#717274',v=other))
        nat=dict(cands=cs,slices=slices,partp=s['turnout'],metrics=[['Escenario','Hipotético'],['Vuelta',s['round']],['Participación original',pct(s['turnout'])],['Padrón original',num(s['padron'])],['Resto sin desglose',num(residual)]])
        prov={}
        for p in sorted({t['p'] for t in T}):
            ids=[j for j,i in enumerate(valid) if T[i]['p']==p]
            if ids:prov[p]=record(matrix[ids].sum(axis=0),codes,'Agregado de la estimación; no es un total provincial publicado por el autor.')
        keys=[[BEIGE,'Original no legible (vista Lectura)']]
        modes=[dict(id='gan',tile='GANÓ',note=note,units=units,prov=prov,national=nat,legend=dict(keys=keys))]
        for c in wc:
            edges=[0,10,20,30,40,50,60];colors=color_ramp(CAND[c]['base'])
            def chor(r):
                out={k:v for k,v in r.items() if k not in ('w','q','fill')}
                vals={a[0]:a[2] for a in r['lines']};q=vals.get(c)
                out['fill']=colors[max(j for j,e in enumerate(edges) if q>=e)] if q is not None else r.get('fill',BEIGE)
                return out
            short={'MAC':'MACRI','ALV':'ÁLVAREZ','CAV':'CAVALLO','HIL':'DUHALDE','BIL':'BILARDO','DLS':'DE LA S.','REU':'REUTEM.','M':'MENEM','K':'KIRCH.','L':'L. MUR.','R':'R. SAÁ','C':'CARRIÓ'}
            modes.append(dict(id=c.lower(),tile=short.get(c,c[:6]),note=note,units=[chor(r) for r in units],prov={p:chor(r) for p,r in prov.items()},national=nat,legend=dict(title='% estimado · '+CAND[c]['n'],stops=[[col,('+' if j==6 else '')+str(e)+'%'] for j,(col,e) in enumerate(zip(colors,edges))],bars=False,keys=keys)))
        modes.append(dict(id='lectura',tile='LECTURA',note='Identidad del ganador leída del PNG; color plano, sin porcentaje recuperado. Beige: imagen insuficiente. Los valores de las fichas son estimados por el modelo.',units=compare,prov={},national=nat,legend=dict(keys=keys)))
        assert len(modes)<=8,(sid,len(modes))
        ds['modes']=modes;ds['reconstruction']=dict(source=s['file'],national=s,profiles=PROFILES,reading=read,provincial_reading=provread[sid],fit=audit)
        apply_scales(ds,s['round'])
        fn=f'atlas_2003alt_{sid}.html'
        a=template.index('const DATA=');b=template.index('const START_MODE=',a)
        html=template[:a]+'const DATA='+json.dumps(ds,ensure_ascii=False,separators=(',',':'))+';\n'+template[b:]
        html=re.sub(r'<title>.*?</title>',f'<title>2003 alternativo · {s["title"]} · Estimación</title>',html,count=1,flags=re.S)
        html=html.replace('Diputados 2003</a>','Presidencial histórico</a>').replace('../mapa2003/atlas_2003.html','../mapa2003pres/atlas_2003pres.html')
        html=html.replace('<div class="grp" id="otras-elecciones">','<div class="grp" id="otras-elecciones"><a href="index.html" style="color:inherit">Ocho escenarios 2003</a> · ')
        # El subtítulo ocupa las dos líneas disponibles a la derecha de las pestañas.
        oldsub='if(set.subtitle){sub.textContent=set.subtitle;sub.setAttribute("display","inline");}else sub.setAttribute("display","none");'
        newsub='sub.replaceChildren();sub.setAttribute("display","inline");sub.setAttribute("font-size","18");el("tspan",{x:1505,y:46},sub,"Hipotético · '+s['round']+'");el("tspan",{x:1505,y:76},sub,'+json.dumps(' · '+s['title'])+');'
        assert oldsub in html
        html=html.replace(oldsub,newsub)
        html=patch_shader(html)
        html=patch_tiles(html)
        # Los logos heredados mantienen su dibujo. Los recortes nuevos encajan enteros.
        html=html.replace('x:93,y,width:110,height:h,overflow:"hidden"','x:93,y,width:110,height:h,overflow:"hidden"')
        (DEST/fn).write_text(html,'utf8');dump(DEST/f'dataset_2003alt_{sid}.json',ds)
        acreditar(DEST/fn)
        errors=[]
        for row0 in s['candidates']:
            if row0[3] is not None and round(100*row0[3]/den,2)!=row0[4]:errors.append(dict(code=row0[0],printed=row0[4],calculated=round(100*row0[3]/den,2)))
        report=dict(id=sid,title=s['title'],html=fn,readable=int((winners>=0).sum()),modeled=len(valid),matched=int(sum(w>=0 and matrix[j].argmax()==w for j,w in enumerate(winners))),winners=dict(win),national_target=dict(zip(codes,target.tolist())),denominator_estimated_from_turnout=den,national_residual_not_geographically_allocated=residual,national_percent_discrepancies=errors,percent_sum=sum(c[4] for c in s['candidates']),**audit)
        dump(DEST/f'control_{sid}.json',report);outputs.append(report)
        with (DEST/f'estimacion_{sid}.csv').open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.writer(f);writer.writerow(['provincia','unidad','ganador_imagen','lectura_suficiente',*codes])
            for j,i in enumerate(valid):writer.writerow([T[i]['p'],T[i]['n'],read.get(i,{}).get('reading',{}).get('w','') if read.get(i,{}).get('reading') else '',winners[j]>=0,*map(int,matrix[j])])
        print(sid,'lecturas',report['readable'],'coincidencias',report['matched'],'error nacional',audit['max_national_error'],flush=True)
    dump(DEST/'manifiesto.json',outputs)
    items=''.join(f'<li><a href="{s["html"]}">{s["title"]}</a> · {s["matched"]}/{s["readable"]} ganadores legibles conservados · <a href="estimacion_{s["id"]}.csv">CSV</a></li>' for s in outputs)
    index=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2003 alternativo · ocho remakes</title><style>body{{font:17px/1.65 system-ui;max-width:960px;margin:40px auto;padding:0 22px;background:#fafaf7;color:#202522}}h1{{line-height:1.15}}a{{color:#126855}}li{{padding:10px 0}}.nota{{border-left:4px solid #a07925;padding:12px 20px;background:#f2ede1}}img{{max-width:100%}}</style></head><body><h1>2003 alternativo</h1><p>Ocho remakes de las imágenes aportadas, con la cartografía y el estilo de nuestros atlas.</p><p class="nota"><strong>Reconstrucciones hipotéticas.</strong> Se conservan cifras nacionales transcritas y ganadores de color legibles. Los votos locales se estiman con perfiles reales de 2003. La vista <strong>Lectura</strong> muestra qué se pudo leer del original. No equivale a recuperar la base perdida del autor.</p><ul>{items}</ul><p>Los balotajes reconstruyen la segunda vuelta visible: las primeras vueltas seleccionables del original no están presentes en los PNG. No se inventaron.</p><p>Los porcentajes impresos se conservan, incluso las inconsistencias del escenario Álvarez. El resto no desglosado se muestra en gris y no se reparte territorialmente.</p><p><a href="LEEME_2003ALT.md">Método y limitaciones</a> · <a href="../mapa2003pres/atlas_2003pres.html">Elección histórica de 2003</a></p></body></html>'''
    (DEST/'index.html').write_text(index,'utf8')
    from indice import construir_indice
    construir_indice()

if __name__=='__main__':main()
