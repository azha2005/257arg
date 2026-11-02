"""Identidad de las listas presidenciales PASO 2023, cotejada con Wikipedia y DINE."""
import sys,re,json,copy,io,base64
import pandas as pd
from serie import ROOT,HERE,norm,dump


def candidates(key):
    sys.path.insert(0,str(ROOT/'datos/wikipaso'))
    from parse_paso import presidente
    wiki=presidente(2023)
    ds=json.loads((ROOT/'mapas/mapa2023paso/dataset_2023paso.json').read_text(encoding='utf8'))
    groups={f'B{i:02d}':copy.deepcopy(ds['candidates'][f'B{i:02d}']) for i,_ in enumerate(wiki['agr'],1)}
    groups['B05']['base']='#f65058'
    # La extracción antigua quitaba también el amarillo de la franja, creando huecos.
    # Conservar el recorte opaco completo y ajustar su tamaño al bloque de la leyenda.
    from PIL import Image
    band=ROOT/'logos/bloques_presidenciales/jxc23_franja_completa.png'
    im=Image.open(band).convert('RGBA');buffer=io.BytesIO();im.save(buffer,'PNG',optimize=True)
    ar=im.width/im.height
    groups['B02'].update(img='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode(),
                         ar=ar,bl=round(min(1.1,98/(ar*50)),3),logo_file='logos/bloques_presidenciales/jxc23_franja_completa.png')
    groups['B02'].pop('blk',None)
    raw,_=pd.read_pickle(ROOT/'datos_oficiales/2023_paso/agregado.pkl')
    nomen=raw[raw.cargo_nombre.str.contains('PRESIDENTE')&(raw.votos_tipo=='POSITIVO')][['agrupacion_id','agrupacion_nombre','lista_numero','lista_nombre']].drop_duplicates()
    by_num={re.match(r'\d+',a['listas'][0]['codigo']).group(): (f'B{i:02d}',a) for i,a in enumerate(wiki['agr'],1)}
    # Colores diferentes dentro de las internas para que se distinga cada candidato.
    colors={'132 A':'#e10019','134 B':'#16a085','136 B':'#aa3388',
            '90 A':'#a37818','90 B':'#d0ab00','94 A':'#e31c79','94 B':'#963a88','94 C':'#d174b7',
            '131 A':'#7956a8','131 B':'#362162','131 C':'#9a82af'}
    short={'Javier Milei':'MILEI','Patricia Bullrich':'BULLR.','Horacio Rodríguez Larreta':'LARRET.',
           'Sergio Massa':'MASSA','Juan Grabois':'GRAB.','Myriam Bregman':'BREG.','Gabriel Solano':'SOLANO',
           'Juan Schiaretti':'SCHIA.','Guillermo Moreno':'MORENO'}
    cand={};lookup={};labels={};rows=[]
    for r in nomen.itertuples():
        group,ag=by_num[str(int(r.agrupacion_id))]
        prefix=re.match(r'\s*([0-9]*[A-Z])\s*-',r.lista_nombre)
        assert prefix,(r.agrupacion_id,r.lista_nombre)
        suffix=prefix.group(1)
        options=[l for l in ag['listas'] if l['codigo'].split()[-1]==suffix]
        assert len(options)==1,(r,options)
        l=options[0];code='C'+l['codigo'].replace(' ','_')
        value=copy.deepcopy(groups[group]);value.update(n=l['pres'],sub=groups[group]['logo'],
              base=colors.get(l['codigo'],groups[group]['base']),logo=short.get(l['pres'],l['pres'].split()[-1].upper()[:6]),
              agr=group,vice=l['vice'],lista=l['lista'],codigo_lista=l['codigo'])
        value.pop('logpal',None);value.pop('logcov',None)
        value['bl']=round(min(1.1,98/(max(value.get('ar',1),.01)*50)),3)
        cand[code]=value
        rawkey=r.agrupacion_nombre.strip().upper()+' | '+r.lista_nombre.strip().upper()
        lookup[rawkey]=code if key.endswith('cand') else group
        labels[rawkey]=l['pres']
        rows.append(dict(identificador_dine=rawkey,agrupacion_id=r.agrupacion_id,lista_numero=r.lista_numero,
                         codigo=code,grupo=group,presidente=l['pres'],vice=l['vice'],lista=l['lista'],color=value['base']))
    assert len(cand)==27 and len(lookup)==27
    dump(HERE/'mapeo_paso2023_candidatos.json',rows)
    collection=groups if key.endswith('fuerza') else cand
    dump(HERE/f'logos_{key}.json',[dict(codigo=code,nombre=value['n'],
         archivo=value.get('logo_file') or ('logos/bloques_presidenciales/'+value['blk']+'.png' if value.get('blk') else 'Emblema embebido en mapas/mapa2023paso/dataset_2023paso.json'),
         fuente='Emblemas ya documentados del atlas PASO 2023 y logos/LICENCIAS.md')
         for code,value in collection.items() if value.get('img')])
    if key.endswith('fuerza'):
        for g in groups.values():g['sub']=''
        return groups,lookup,labels
    return cand,lookup,labels
