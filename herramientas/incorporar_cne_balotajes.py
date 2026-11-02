"""Incorpora las doce consultas CNE de sección completa descargadas el 2-nov-2026.

Los votos se leen de los XLS; los inscriptos fueron transcritos de la pantalla
por el agente que realizó las consultas y están documentados en cne/LEEME.md.
"""
from pathlib import Path
import hashlib, json, re, unicodedata
import xlrd

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'datos/fuentes_leg2003_2025/presidenciales/busqueda_faltantes/cne'
COMP=ROOT/'datos/fuentes_leg2003_2025/presidenciales/complementos.json'
SPECS=[
    (2015,'catamarca','03','014','Antofagasta de la Sierra',1199),
    (2015,'jujuy','10','008','Valle Grande',2642),
    (2015,'salta','17','006','Rivadavia',22850),
    (2015,'salta','17','010','Santa Victoria',7896),
    (2023,'catamarca','03','014','Antofagasta de la Sierra',1800),
    (2023,'chubut','07','003','Telsen',1418),
    (2023,'chubut','07','004','Gastre',1134),
    (2023,'chubut','07','011','Florentino Ameghino',1519),
    (2023,'jujuy','10','008','Valle Grande',2906),
    (2023,'jujuy','10','016','Susques',3479),
    (2023,'lapampa','11','009','Curacó',892),
    (2023,'salta','17','010','Santa Victoria',8231),
]

def fold(s):
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower())

def integer(n):
    assert isinstance(n,(float,int)) and n>=0 and int(n)==n,n
    return int(n)

added=[]; controls=[]
for year,slug,d,s,name,elect in SPECS:
    file=FOLDER/f'{year}_{slug}_s{s}.xls'
    sheet=xlrd.open_workbook(str(file),ignore_workbook_corruption=True).sheet_by_index(0)
    rows=[sheet.row_values(i) for i in range(sheet.nrows)]
    txt=lambda r:' '.join(str(x) for x in r if x!='')
    date='22/11/2015' if year==2015 else '19/11/2023'
    assert any(date in txt(r) and 'FECHA ELECCION' in txt(r) for r in rows),file
    assert any('SEGUNDA VUELTA' in txt(r) for r in rows),file
    section=next(r for r in rows if fold(r[0])=='seccionelectoral')
    assert int(re.match(r'\s*(\d+)',section[1])[1])==int(s),file
    assert any(fold(name)==fold(str(x).split(' - ',1)[-1]) for x in section), (file,section)
    district=next(txt(r) for r in rows if str(r[0]).startswith('Distrito:'))
    assert fold(slug) in fold(district), (file,district)
    hi=next(i for i,r in enumerate(rows) if r[0]=='NRO')
    vc=next(i for i,c in enumerate(rows[hi]) if str(c).strip().startswith('PRESIDENTE'))
    ac=next(i for i,c in enumerate(rows[hi]) if str(c).strip()=='AGRUPACION POLITICA')
    votes={}; parties=[]; special={}
    for r in rows[hi+1:]:
        if r[vc]=='':continue
        n=integer(r[vc]);label=str(r[ac]).strip();f=fold(label)
        if r[0]!='':
            code=({'frenteparalavictoria':'FPV','cambiemos':'CAM'} if year==2015 else
                  {'unionporlapatria':'UP','lalibertadavanza':'LLA'})
            hit=[c for a,c in code.items() if a in f]
            assert len(hit)==1,(file,label)
            votes[hit[0]]=votes.get(hit[0],0)+n
            parties.append(dict(codigo_original=r[0],nombre=label,codigo=hit[0],votos=n))
        else:special[f]=n
    assert set(votes)==({'FPV','CAM'} if year==2015 else {'UP','LLA'}),file
    pos=sum(votes.values());bla=special['votosenblanco']
    nul=sum(special.get(k,0) for k in ('votosnulos','votosrecurridos','votosimpugnados'))
    total=special['totales']
    assert pos+bla+nul==total,(file,votes,special)
    assert special.get('votosrecurridos',0)==special.get('votosimpugnados',0)==0,file
    # Sólo contrasta el padrón transcrito; no lo calcula a partir del porcentaje.
    turnout=next(str(x) for r in rows if str(r[0])=='Votantes' for x in r if '%' in str(x))
    assert abs(100*total/elect-float(turnout.rstrip('%').replace(',','.')))<=.0051,(file,elect,turnout)
    mesas=next(integer(r[r.index('Normal (padron Electoral)')+1]) for r in rows if 'Normal (padron Electoral)' in r)
    rel=str(file.relative_to(ROOT)).replace('\\','/')
    note=(f'CNE, consulta de escrutinio definitivo por zona del {date}, sección completa {s}, {name}, {mesas} mesas, '
          f'categoría Presidente y Vice. Archivo {file.name}; consulta del 2-nov-2026 con localidad y circuito en blanco. '
          f'Inscriptos ({elect}): transcripción de la cifra mostrada en pantalla, documentada en cne/LEEME.md; '
          'el XLS no incluye esa cifra. No se infiere el padrón ni se imputan votos.')
    added.append(dict(key=f'{year}bal',d=d,s=s,name=name,v=votes,pos=pos,bla=bla,nul=nul,el=elect,
                      archivo=rel,archivo_inscriptos=str((FOLDER/'LEEME.md').relative_to(ROOT)).replace('\\','/'),
                      url='https://www.padron.gob.ar/publica/',nota=note,mesas=mesas))
    controls.append(dict(archivo=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),fecha=date,
                         distrito=d,seccion=s,nombre=name,partidos=parties,positivos=pos,blancos=bla,nulos=nul,
                         emitidos=total,inscriptos_pantalla=elect,participacion_pantalla=turnout,mesas=mesas,cierre_ok=True))

old=json.loads(COMP.read_text(encoding='utf8'))
keys={(x['key'],x['d'],x['s']) for x in added}
result=[x for x in old if (x['key'],x['d'],x['s']) not in keys]+added
assert len(result)==len(old)+len([x for x in added if not any((q['key'],q['d'],q['s'])==(x['key'],x['d'],x['s']) for q in old)])
COMP.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(FOLDER/'CONTROL_INCORPORACION.json').write_text(json.dumps(controls,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Doce secciones completas: fecha, identidad, votos, totales y padrón transcrito cotejados.',flush=True)
