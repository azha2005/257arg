"""Fuentes observadas, sin imputación, de 1926/1937/1940. Ejecutar para exportar y controlar."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, hashlib, json, re, unicodedata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def norm(s):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode())

NAMES = dict(UCR='Unión Cívica Radical', PS='Partido Socialista', ANT='UCR Antipersonalista',
             PC='Partido Comunista', UNI='Partido Unitario', SAL='Salud Pública', FEM='Partido Feminista',
             IND='Independientes', CI='Comité Independiente', CON='Partido Conservador',
             DEM='Partido Demócrata', PAL='Liberal y Autonomista', CP='Concentración Popular',
             PRI='UCR Principista', LIB='Partido Liberal', LEN='UCR Lencinista', UP='Unión Provincial',
             BLO='UCR Bloquista', UNIF='UCR Unificada', CC='Concentración Cívica (Bates)', VID='Videla',
             ALEM='UCR Alem', BLA_RAD='UCR Blanca', ROJA='UCR Roja', CAR='UCR Doctor Carranza')
BLOC26 = {c:c for c in ('UCR','PS','ANT','LEN','BLO','UNIF','IND')}
BLOC26.update({c:'CON' for c in ('CON','DEM','PAL','CP','LIB','UP','CC')})
BLOC26.update({c:'DIS' for c in ('PRI','BLA_RAD','ROJA','CAR')})
BLOC26.update(CI='IND')

# Columnas nacionales publicadas en el artículo, no la suma territorial.
NATIONAL = {
 1918: dict(art='Elecciones legislativas de Argentina de 1918',
   blocs=dict(UCR=349622,CON=167673,PS=65099,DIS=62791,PDP=57826,PSA=35309),
   positivos=745073,blancos=9897,dif=7182+60+11+76,total=762299,inscriptos=1303446),
 1920: dict(art='Elecciones legislativas de Argentina de 1920',
   blocs=dict(UCR=338881,CON=130351,PDP=116383,PS=83959,DIS=32334,PSA=8726),
   positivos=717957,blancos=19845,dif=34100+11,total=771913,inscriptos=1436472),
 1926: dict(art='Elecciones legislativas de Argentina de 1926',
   blocs=dict(UCR=336351,CON=162042,ANT=98049,PS=97880,UNIF=74463,DIS=28351,LEN=18327,BLO=13333,IND=11771),
   positivos=852285,blancos=32052,dif=309,total=884646,inscriptos=1799131),
 1937: dict(art='Elecciones presidenciales de Argentina de 1937',blocs=dict(CON=1097660,UCR=814750,PS=50952),
   positivos=1968280,blancos=52069,dif=15490,total=2035839,inscriptos=2672750),
 1940: dict(art='Elecciones legislativas de Argentina de 1940',blocs=dict(UCR=876057,CON=724085,PS=155178,FP=23888),
   positivos=1840953,blancos=63531,dif=10826,total=1915310,inscriptos=2721806,
   extra=[['Anulados (incluidos en diferencia)',330],['Diferencia de votos (sin anulados)',10496]]),
}

def load(y):
    rows=[]
    if y in (1918,1920):
        return load_early(y)
    if y==1926:
        for line in (HERE/'manual1926.txt').read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#'): continue
            if line.startswith('@'):
                page,prov,cols=line[1:].split('|');cols=cols.split();continue
            name,vals=line.split('|');vals=vals.split();assert len(vals)==len(cols),(name,vals,cols)
            d=dict(zip(cols,vals)); p={NAMES[c]:int(v) for c,v in d.items() if c not in ('INS','VOT') and v.isdigit()}
            blocs=defaultdict(int)
            for c,v in d.items():
                if c not in ('INS','VOT') and v.isdigit():
                    b='DIS' if prov=='Corrientes' and c=='IND' else BLOC26.get(c,'X_'+c)
                    blocs[b]+=int(v)
            rows.append(dict(prov=prov,name=name,page=int(page),book=int(page)-4,
                ins=int(d['INS']) if d['INS'].isdigit() else None,
                vot=int(d['VOT']) if d['VOT'].isdigit() else None,P=p,bloc=dict(blocs),
                marks={c:v for c,v in d.items() if not v.isdigit()},blancos=None,nulos=None,
                circ=CAP.get(norm(name)) if prov=='Capital Federal' else None))
    else:
        source=ROOT/f'transcripciones/canton1937_1940/{y}/canton_{y}.json'
        for pg in json.loads(source.read_text(encoding='utf-8'))['paginas']:
            for r in pg['filas']:
                p={};blocs=defaultdict(int);ins=vot=bla=nul=None
                for c,label in pg['columnas'].items():
                    v=r['valores'].get(c)
                    if v is None: continue
                    n=norm(label)
                    if n=='inscriptos': ins=v;continue
                    if n=='votantes': vot=v;continue
                    if 'blanco' in n: bla=v;continue
                    if 'anulados' in n: nul=v;continue
                    p[label]=p.get(label,0)+v
                    if y==1937:
                        b=('UCR' if n=='unioncivicaradical' else 'CON' if n in ('concordancia','democratanacional','unioncivicaradicaljuntarenovadoranacional') else 'PS' if n=='socialista' else 'X_'+n)
                    else:
                        b=('UCR' if n in ('unioncivicaradical','unioncivicaradicalcapital') else
                           'CON' if n in ('concordancia','democratanacional','unioncivicaradicalsantafe','radicalunificado','socialindependiente') else
                           'PS' if n in ('socialista','partidosocialista') else 'FP' if n=='unioncivicaradicalfrentepopular' else 'X_'+n)
                    blocs[b]+=v
                rows.append(dict(prov=pg['provincia'],name=r['unidad'],page=pg['pagina_pdf'],book=pg['pagina_libro'],
                    ins=ins,vot=vot,P=p,bloc=dict(blocs),marks=r.get('marcas',{}),blancos=bla,nulos=nul,circ=r.get('circunscripcion')))
    return rows

def load_early(y):
    """Agrupación explícita por provincia, sin tocar la transcripción canónica."""
    doc=json.loads((ROOT/f'transcripciones/canton{y}/canton_{y}.json').read_text(encoding='utf-8'))
    mapping={
      1918:{
        'Capital Federal':{'3':'UCR','4':'PDP','5':'PS','6':'PSA'},
        'Buenos Aires':{'3':'UCR','4':'PS','5':'CON'},
        'Catamarca':{'3':'UCR','4':'CON'},
        'Córdoba':{'3':'UCR','4':'DIS','5':'PDP'},
        'Corrientes':{'3':'UCR','4':'CON','5':'CON','6':'DIS'},
        'Entre Ríos':{'3':'UCR','4':'DIS','5':'CON'},
        'Mendoza':{'3':'UCR','4':'PS','5':'CON'},
        'Santa Fe':{'3':'UCR','4':'PDP','5':'DIS'},
      },
      1920:{
        'Capital Federal':{'3':'UCR','4':'PS','5':'PDP','6':'PSA'},
        'Buenos Aires':{'3':'UCR','4':'CON','5':'PS'},
        'Córdoba':{'3':'UCR','4':'PS','5':'PDP'},
        'Corrientes':{'3':'UCR','4':'CON'},
        'Entre Ríos':{'3':'UCR','4':'PS'},
        # La clave del impreso de Jujuy contradice las identidades de la tabla distrital:
        # conservar rótulos/cifras, sin identificar un ganador partidario por proximidad numérica.
        'Jujuy':{'3':'X_J3','4':'X_J4','5':'X_J5'},
        'Mendoza':{'3':'PS','4':'DIS','5':'CON','6':'UCR'},
        'San Luis':{'3':'UCR','4':'PDP','5':'CON'},
        'Santa Fe':{'3':'UCR','4':'PDP'},
        'Tucumán':{'3':'UCR','4':'CON'},
      }}[y]
    rows=[]
    for pg in doc['paginas']:
        for r in pg['filas']:
            p={};bloc=defaultdict(int);pbloc={};ins=vot=bla=nul=None
            for c,label in pg['columnas'].items():
                v=r['valores'].get(c)
                if v is None:continue
                if c=='1':ins=v;continue
                if c=='2':vot=v;continue
                if 'blanco' in norm(label):bla=v;continue
                if 'anulado' in norm(label):nul=v;continue
                b=mapping[pg['provincia']][c]
                p[label]=p.get(label,0)+v;bloc[b]+=v;pbloc[label]=b
            note=' '.join(str(r.get(k,'')) for k in ('nota','nota_revision')).strip()
            if y==1920 and pg['provincia']=='Jujuy':
                note+=' Identidad partidaria pendiente: las claves impresas «Socialista», «Demócrata» y «Liberal» no coinciden con las fuerzas de la tabla distrital de Wikipedia. Se muestran las cifras bajo sus rótulos originales, sin asignar ganador ni porcentajes a bloques nacionales.'
            rows.append(dict(prov=pg['provincia'],name=r['unidad'],page=pg['pagina_pdf'],book=pg['pagina_libro'],
                ins=ins,vot=vot,P=p,bloc=dict(bloc),party_bloc=pbloc,marks=r.get('marcas',{}),blancos=bla,nulos=nul,
                circ=r.get('circunscripcion'),source_note=note,reserva=pg.get('reserva_cronologica',''),
                unresolved=y==1920 and pg['provincia']=='Jujuy'))
    return rows

CAP={norm(s):i for i,s in enumerate(['Vélez Sarsfield','San Cristóbal Sud','Santa Lucía','San Juan Evangelista','Flores',
    'San Carlos Sud','San Carlos Norte','San Cristóbal Norte','Balvanera Oeste','Balvanera Sud','Balvanera Norte',
    'Concepción','Monserrat','San Nicolás','San Bernardo','Belgrano','Palermo','Las Heras','Pilar','Socorro'],1)}

def export(y):
    rows=load(y);counts=Counter();tot=defaultdict(int);alerts=[]
    for r in rows:
        if r['P']:
            win=max(r['bloc'],key=r['bloc'].get);counts[win]+=1
            for b,v in r['bloc'].items():tot[b]+=v
            tab=sum(r['P'].values())+(r['blancos'] or 0)+(r['nulos'] or 0)
            if r['vot'] is not None and tab!=r['vot']:
                alerts.append(dict(provincia=r['prov'],unidad=r['name'],pagina_pdf=r['page'],votantes=r['vot'],suma_publicada=tab,diferencia=tab-r['vot']))
    nat=NATIONAL[y];winners=[b for b in counts if not b.startswith('X_')]
    ctrl=dict(anio=y,filas=len(rows),filas_con_votos=sum(bool(r['P']) for r in rows),distritos=len({r['prov'] for r in rows}),
        ganadores_por_fila_fuente=dict(counts),bloques_segun_base=dict(tot),bloques_segun_wikipedia=nat['blocs'],
        diferencias_por_bloque={b:tot[b]-v for b,v in nat['blocs'].items()},alertas_aritmeticas=alerts,
        origen='Cantón (1968), tomo II; lectura visual, cifras impresas conservadas; sin imputación',
        sha256_pdf=hashlib.sha256((ROOT/'raw/canton_1968/1968_materiales-para-el-estudio-de-la-sociologia_2.pdf').read_bytes()).hexdigest())
    (HERE/f'canton_{y}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/f'CONTROL_{y}.json').write_text(json.dumps(ctrl,ensure_ascii=False,indent=2),encoding='utf-8')
    if y==1926:
        with (HERE/'canton_1926.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['anio','provincia','unidad','pagina_pdf','pagina_impresa','concepto','valor','marca'])
            for r in rows:
                for c,v in dict(Inscriptos=r['ins'],Votantes=r['vot'],**r['P']).items():
                    if v is not None:w.writerow([y,r['prov'],r['name'],r['page'],r['book'],c,v,''])
                for c,v in r['marks'].items():w.writerow([y,r['prov'],r['name'],r['page'],r['book'],NAMES.get(c,c),'',v])
    print(y,len(rows),'con votos',ctrl['filas_con_votos'],'ganadores',dict(counts),'bloques',dict(tot))
    return ctrl

if __name__=='__main__':
    for y in (1926,1937,1940):export(y)
