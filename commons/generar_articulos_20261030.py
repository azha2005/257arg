import json,re,html,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'articulos_20261030'
published=json.loads((ROOT/'publicacion_20261030/final.json').read_text(encoding='utf8'))['files']
def params(text):
    start=text.index('{{Ficha de elección')
    braces=0; links=0; pipes=[]; i=start
    while i<len(text):
        pair=text[i:i+2]
        if pair=='{{':braces+=1;i+=2;continue
        if pair=='}}':
            braces-=1
            if braces==0:
                end=i;break
            i+=2;continue
        if pair=='[[':links+=1;i+=2;continue
        if pair==']]':links-=1;i+=2;continue
        if text[i]=='|' and braces==1 and links==0:pipes.append(i)
        i+=1
    result={}
    for a,b in zip(pipes,pipes[1:]+[end]):
        seg=text[a+1:b]
        if '=' in seg:
            name,value=seg.split('=',1)
            result[name.strip()]=(a,b,value.strip())
    return result,end
def files(key):
    fs=[r['name'] for r in published if r['key']==key and r['eligible'] and r['name'].endswith('.svg')]
    assert fs and all(r['status']=='IGUAL' for r in published if r['key']==key)
    return fs
def main(key):return next(f for f in files(key) if 'Resultados por departamento (con leyenda).svg' in f)
rows=[]
for path in sorted(OUT.glob('[0-9][0-9].json')):
    d=json.loads(path.read_text(encoding='utf8'));idx=int(path.stem);year=d['title'][-4:];primary=idx>=12
    keys=([year+'paso',year+'pasodip'] if year in ['2011','2019','2023'] else [year+'paso']) if primary else [year]
    orig=d['original'];text=orig
    pp,end=params(text)
    oldmap=pp.get('mapa',(0,0,''))[2]
    oldleg=pp.get('leyenda_mapa1',(0,0,''))[2]
    oldleg2=pp.get('leyenda_mapa2',(0,0,''))[2]
    new=''
    for key in keys:
        office='presidenciales' if key in ['2011paso','2019paso','2023paso'] else 'de diputados'
        new+=f'| [[Archivo:{main(key)}|300px]]\n| Mostrar resultados {office} por departamento\n'
    if '{{Switcher' in oldleg:
        # Keep all existing options and their legends verbatim.
        legacy=oldleg.split('{{Switcher',1)[1]
        close=legacy.rfind('}}')
        assert close>=0
        new+=legacy[:close].strip()+'\n'
    elif oldmap:
        oldmap=oldmap if ':' in oldmap else 'Archivo:'+oldmap
        new+=f'| [[{oldmap}|300px]]'
        if oldleg or oldleg2:new+='<br>'+oldleg+' '+oldleg2
        new+='\n| Mostrar mapa por distrito\n'
    selector=len(keys)>1 or bool(oldmap or oldleg)
    block='| mapa_título = Resultados electorales\n'
    if selector:block+='| leyenda_mapa1 = <center>{{Switcher\n'+new+'}}</center>\n'
    else:block+=f'| mapa = Archivo:{main(keys[0])}\n| mapa_tamaño = 300px\n'
    remove=[v[:2] for k,v in pp.items() if k in ['mapa','mapa_tamaño','mapa_título','leyenda_mapa1','leyenda_mapa2','mapa_subtítulo']]
    at=min(a for a,b in remove) if remove else end
    for a,b in sorted(remove,reverse=True):text=text[:a]+text[b:]
    text=text[:at]+block+'\n'+text[at:]
    section='\n== Resultados por departamento ==\n'
    for key in keys:
        office='presidenciales' if key in ['2011paso','2019paso','2023paso'] else 'de diputados nacionales'
        if len(keys)>1:section+=f'\n=== Elecciones {office} ===\n'
        fs=files(key);plain=next(f for f in fs if 'Resultados por departamento (solo mapa).svg' in f)
        note=''
        if key=='2003':note=' La Pampa se muestra con su resultado provincial, sin detalle departamental.'
        if key=='2013':note=' Ramón Lista y Valle Grande aparecen sin datos por no tener mesas escrutadas en el provisorio.'
        section+=f'[[Archivo:{plain}|miniaturadeimagen|centro|550px|Resultados {office} por departamento y divisiones electorales de la ciudad de Buenos Aires.{note} Las fuentes y salvedades se detallan en la descripción del archivo.]]\n\n'
        section+='<gallery mode="packed" heights="200px">\n'
        for f in fs:
            if '(solo mapa)' not in f or f==plain:continue
            label=f.split(' - ',1)[1].removesuffix(' por departamento (solo mapa).svg').replace('Participacion','Participación')
            section+=f'Archivo:{f}|{label}\n'
        section+='</gallery>\n'
    target=re.search(r'^==\s*Resultados por (?:provincia|distrito)\s*==',text,re.M)
    if not target:target=re.search(r'^==\s*(?:Véase también|Referencias)\s*==',text,re.M)
    assert target
    text=text[:target.start()]+section+'\n'+text[target.start():]
    oldimages=re.findall(r'(?:Archivo|File):([^\]|\n]+)',orig)
    assert all(f.strip() in text for f in oldimages), (idx,'Lost old image')
    assert text.count('{{')==text.count('}}'),(idx,'Unbalanced templates')
    d.update(proposed=text,keys=keys,selector=selector,oldmap=oldmap)
    (OUT/f'{idx:02}_propuesto.wiki').write_text(text,encoding='utf8')
    (OUT/f'{idx:02}.diff').write_text(''.join(difflib.unified_diff(orig.splitlines(True),text.splitlines(True))),encoding='utf8')
    (OUT/f'editar_{idx:02}.html').write_text('<meta charset=utf-8><pre>'+html.escape(json.dumps(d,ensure_ascii=False))+'</pre>',encoding='utf8')
    rows.append({k:v for k,v in d.items() if k not in ['original','proposed']})
(OUT/'plan.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('Preparados',len(rows),'artículos;',sum(len(r['keys']) for r in rows),'atlas; imágenes anteriores conservadas.')
