"""Transcripción reproducible y controles de PDF definitivos (sólo filas seleccionadas)."""
from pathlib import Path
import json,re
import pymupdf
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'fuentes_leg2003_2025'
def n(s):return int(s.strip().replace('.',''))
def first(lines,label):
    i=lines.index(label)
    return n(next(x for x in lines[i+1:] if re.fullmatch(r'\d[\d.]*',x.strip())))

data=[]
doc=pymupdf.open(OUT/'la_pampa_2005_archivo.pdf')
labels={'0002':'JUSTICIALISTA','0003':'UNION CIVICA RADICAL','0022':'HUMANISTA','0048':'RECREAR PARA EL CRECIMIENTO','0221':'DEL FRENTE','0220':'AL. ENCUENTRO ARI-PS'}
for page,sec,name in [(21,'017','Quemú Quemú'),(22,'018','Rancul'),(23,'019','Realicó'),(24,'020','Toay'),(25,'021','Trenel'),(26,'022','Utracán')]:
    lines=[s.strip() for s in doc[page-1].get_text().splitlines()]
    votes={a:first(lines,l) for a,l in labels.items()}
    pos=first(lines,'VOTOS POSITIVOS');bla=first(lines,'VOTOS BLANCOS');nul=first(lines,'VOTOS NULOS');total=first(lines,'TOTAL VOTANTES')
    assert sum(votes.values())==pos and pos+bla+nul==total,(page,votes)
    data.append(dict(year=2005,d='11',s=sec,name=name,votes=votes,pos=pos,bla=bla,nul=nul,el=first(lines,'Electores Hábiles'),source=f'DINE definitivo: la_pampa_2005_archivo.pdf, página {page}. Tabla completa, total ambos sexos; no se mezclan votos de senadores.',pdf='la_pampa_2005_archivo.pdf',page=page))
    doc[page-1].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(OUT/f'pampa05_p{page}.png')
# Valle Grande: lectura de la columna DIPUTADOS NAC. en página 32, validada en el render.
votes={'0111':0,'0014':2,'0022':2,'0038':1,'0045':2,'0281':1,'0505':2,'0506':313,'0101':872,'0507':286}
assert sum(votes.values())==1481 and 1481+93+13==1587
data.append(dict(year=2005,d='10',s='008',name='Valle Grande',votes=votes,pos=1481,bla=93,nul=13,el=2004,source='DINE definitivo: jujuy_2005_archivo.pdf, página 32, columna DIPUTADOS NAC. (total ambos sexos). La primera página tiene una errata de año; las tablas dicen 23-oct-2005.',pdf='jujuy_2005_archivo.pdf',page=32))
(OUT/'complementos_departamentales.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('Tablas que cierran al voto:',len(data))
