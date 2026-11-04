"""Transcripción comprobada del anexo definitivo municipal de Misiones 2025."""
from pathlib import Path
import concurrent.futures as cf
import io
import re
import subprocess
import numpy as np
import pandas as pd
import pymupdf as pdf
from fuentes import HERE,RAW

NAMES={'71':'Partido del Obrero','96':'La Libertad Avanza','184':'Agrario y Social','641':'Movimiento Positivo',
       '644':'Integración y Militancia','653':'Por la Vida y los Valores','654':'Partido Demócrata',
       '656':'Tierra Techo y Trabajo','657':'Partido Libertario','900':'Frente Renovador de la Concordia',
       '901':'Confluencia Popular por la Patria','902':'Unidos por el Futuro'}


def extraer(pi):
    with pdf.open(RAW/'misiones2025.pdf') as doc:
        page=doc[pi];words=page.get_text('words')
        muni=next((w for w in words if w[4] in ['Municipio','Muriicipio']),None)
        if muni:
            name=' '.join(w[4] for w in words if w[0]>muni[2] and abs(w[1]-muni[1])<4)
            heading=next(w for w in words if w[4]=='Diputado')
        else:
            assert pi==58,pi
            name='Posadas'
            h=next(w for w in doc[pi-1].get_text('words') if w[4]=='Diputado')
            heading=(h[0],0,h[2],0,'Diputado')
        cx=(heading[0]+heading[2])/2
        anchors={}
        for w in words:
            m=re.search(r'(71|96|184|641|644|653|654|656|657|900|901|902)-',w[4])
            if m and w[0]<cx-50 and w[1]>heading[3]:anchors[m[1]]=(w[1]+w[3])/2
        # El OCR confunde el 7 inicial de 71 en algunas páginas.
        if '71' not in anchors:
            w=next((w for w in words if 'Obrero' in w[4] and w[1]>heading[3]),None)
            if w:anchors['71']=(w[1]+w[3])/2
        for key,needle in [('blancos','BLANCO'),('nulos','NULOS')]:
            w=next((w for w in words if needle in w[4].upper() and w[1]>heading[3]),None)
            if w:anchors[key]=(w[1]+w[3])/2
        yend=anchors.get('nulos',max(anchors.values()))+35
        numeric=[w for w in words if abs((w[0]+w[2])/2-cx)<30 and w[4].isdigit() and w[1]>heading[3]]
        row={'unidad':name,'pagina':pi+1}
        for key,y in anchors.items():
            vals=[w for w in numeric if abs((w[1]+w[3])/2-y)<6]
            row[key]=int(vals[0][4]) if len(vals)==1 else np.nan
        totals=[w for w in numeric if anchors.get('nulos',yend)+6<(w[1]+w[3])/2<yend]
        row['emitidos']=int(totals[0][4]) if len(totals)==1 else np.nan
        expected=list(NAMES)+['blancos','nulos']
        for k in expected:row.setdefault(k,np.nan)
        if any(pd.isna(row[k]) for k in expected+['emitidos']) or sum(row[k] for k in expected)!=row['emitidos']:
            # Segunda lectura independiente de la columna de votos. No se
            # completan residuos. Toda corrección se guarda para revisar.
            tmp=HERE/'ocr';tmp.mkdir(exist_ok=True)
            clip=pdf.Rect(cx-31,heading[3]+2,cx+31,min(yend+15,page.rect.height))
            scale=4
            png=tmp/('misiones_%02d.png'%(pi+1))
            page.get_pixmap(matrix=pdf.Matrix(scale,scale),clip=clip).save(png)
            cmd=[r'C:\Program Files\Tesseract-OCR\tesseract.exe',str(png),'stdout','--psm','6','-c','tessedit_char_whitelist=0123456789','tsv']
            proc=subprocess.run(cmd,capture_output=True,check=True)
            data=pd.read_csv(io.BytesIO(proc.stdout),sep='\t',dtype={'text':str}).dropna(subset=['text'])
            nums=[]
            for _,v in data.iterrows():
                if re.fullmatch(r'\d+',v.text):nums.append((clip.y0+(v.top+v.height/2)/scale,int(v.text)))
            candidate=dict(row)
            for k,y in anchors.items():
                vals=sorted([(abs(yy-y),v) for yy,v in nums if abs(yy-y)<7])
                if vals:candidate[k]=vals[0][1]
            totals=[(y,v) for y,v in nums if anchors.get('nulos',yend)+6<y<yend]
            if len(totals)==1:candidate['emitidos']=totals[0][1]
            if all(pd.notna(candidate[k]) for k in expected+['emitidos']) and sum(candidate[k] for k in expected)==candidate['emitidos']:
                candidate['lectura']='OCR independiente; cierre exacto'
                row=candidate
        return row


def main():
    with cf.ThreadPoolExecutor(4) as pool:rows=list(pool.map(extraer,range(1,80)))
    # Posadas continúa en la página 59; no se suman ni duplican celdas.
    merged={}
    for row in rows:
        target=merged.setdefault(row['unidad'],{})
        for k,v in row.items():
            if pd.notna(v):target[k]=v
    t=pd.DataFrame(list(merged.values())).set_index('unidad')
    codes=list(NAMES)
    t['diferencia']=t[codes+['blancos','nulos']].sum(1,min_count=len(codes)+2)-t.emitidos
    t.to_csv(HERE/'misiones_revision.csv',encoding='utf-8-sig')
    t.to_pickle(HERE/'misiones_revision.pkl')
    print(t[t.diferencia.isna() | t.diferencia.ne(0)].to_string(),flush=True)
    print('TOTALES',t[codes+['blancos','nulos','emitidos']].sum().to_dict(),flush=True)
    if t.diferencia.isna().any() or t.diferencia.ne(0).any():return
    out=t[codes].rename(columns=NAMES)
    out['Blanco y nulo']=t.blancos+t.nulos
    out.to_pickle(HERE/'prov_misiones.pkl')


if __name__=='__main__':main()
