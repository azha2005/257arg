"""Extracción de las fuentes provinciales 2025 y base nacional por lista."""
from pathlib import Path
import concurrent.futures as cf
import json
import re
import sys
import unicodedata
import lxml.html
import numpy as np
import pandas as pd
import pymupdf as pdf
from fuentes import HERE, RAW, descargar, INDEX

ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
import estimar


def norm(s):
    s=unicodedata.normalize('NFD',str(s)).encode('ascii','ignore').decode().upper()
    s=re.sub(r'\bGRAL\b','GENERAL',s)
    return re.sub('[^A-Z0-9]','',s)


def number(s):
    s=re.sub(r'[^0-9]','',s)
    return int(s) if s else 0


def pba():
    b='https://www.juntaelectoral.gba.gov.ar/escrutinio-definitivo-2025/escrutinio-argentinos/'
    index=lxml.html.fromstring((RAW/'pba_indice.html').read_bytes())
    links=sorted(set(index.xpath('//a[contains(@href,"distrito_")]/@href')))
    # El índice omite enlaces a San Miguel y Lezama; ambas páginas públicas
    # sí existen y sus encabezados identifican el municipio.
    links=sorted(set(links+['distrito_053.html','distrito_135.html']))
    assert len(links)==135, len(links)
    def task(link):
        f=descargar('pba_'+link,b+link)
        t=lxml.html.fromstring(f.read_bytes())
        # La denominación completa está en el encabezado del municipio.
        details=[' '.join(x.text_content().split()) for x in t.xpath('//div[contains(@class,"detail-group")]')]
        table=t.xpath('//table')[0]
        heads=[' '.join(x.text_content().split()) for x in table.xpath('.//th')]
        assert 'Prov.' in heads[2], heads
        row={}
        for tr in table.xpath('.//tr'):
            cells=[' '.join(c.text_content().split()) for c in tr.xpath('./td')]
            if len(cells)<3:continue
            if cells[0].isdigit():row[cells[1]]=number(cells[2])
            elif 'BLANCO' in cells[1]:row['Blanco']=number(cells[2])
            elif cells[1]=='VOTOS POSITIVOS':positivos=number(cells[2])
        assert sum(v for k,v in row.items() if k!='Blanco')==positivos,link
        detail_labels=t.xpath('//span[contains(@class,"detail-label")]/text()')
        name=''
        for label in t.xpath('//span[contains(@class,"detail-label")]'):
            if 'distrito' in label.text_content().lower() or 'municipio' in label.text_content().lower():
                vals=label.getparent().xpath('.//span[contains(@class,"detail-value")]')
                if vals:name=vals[0].text_content().strip()
        if not name:
            # El nombre es texto fuera de spans en algunos archivos.
            group=t.xpath('//div[contains(@class,"detail-group-big")]')
            name=group[0].text_content().strip() if group else ''
        row['unidad']=name
        row['id_fuente']=link
        row['cargo']=heads[2]
        return row
    with cf.ThreadPoolExecutor(5) as pool:rows=list(pool.map(task,links))
    t=pd.DataFrame(rows).fillna(0).set_index('unidad')
    t.to_pickle(HERE/'prov_pba.pkl')
    t.to_csv(HERE/'prov_pba.csv',encoding='utf-8-sig')
    print('PBA',t.shape,t.index.tolist()[:10],flush=True)
    return t


def salta():
    f=RAW/'salta2025.pkl'
    d=pd.read_pickle(f) if f.exists() else pd.read_excel(RAW/'salta2025.xlsx')
    if not f.exists():d.to_pickle(f)
    out={}
    for cargo in ['DIPUTADO','SENADOR']:
        v=d[d['Categoría'].eq(cargo)].copy()
        v['grupo']=v['Frente electoral'].fillna(v.Lista)
        v['grupo']=v.grupo.str.strip()
        t=v.pivot_table(index='Departamento',columns='grupo',values='Votos',aggfunc='sum',fill_value=0)
        t.to_pickle(HERE/('prov_salta_'+cargo.lower()+'.pkl'))
        t.to_csv(HERE/('prov_salta_'+cargo.lower()+'.csv'),encoding='utf-8-sig')
        print('SALTA',cargo,t.shape,t.sum().to_dict(),flush=True)
        out[cargo]=t
    return out


def nacional(dist,validos=False):
    votes,mesas=pd.read_pickle(ROOT/'datos_oficiales/2025/agregado.pkl')
    v=votes[(votes.distrito_id.astype(int)==int(dist)) & votes.cargo_nombre.str.upper().str.contains('DIPUTADO') & votes.mesa_tipo.eq('NATIVOS')].copy()
    types=v.votos_tipo.str.upper()
    if validos:
        v=v[types.isin(['POSITIVO','EN BLANCO'])].copy()
        v['cat']=np.where(v.votos_tipo.str.upper().eq('POSITIVO'),v.agrupacion_nombre,'Blanco')
    else:v['cat']=np.where(types.eq('POSITIVO'),v.agrupacion_nombre,'Blanco y nulo')
    names=estimar.secnames(2025)
    v['unidad']=[norm(names[(str(int(d)).zfill(2),int(s))]) for d,s in zip(v.distrito_id,v.seccion_id)]
    t=v.pivot_table(index='unidad',columns='cat',values='v',aggfunc='sum',fill_value=0)
    assert not t.empty,(dist,votes.cargo_nombre.unique())
    return t


def nacional_circuitos(dist,validos=False):
    v,e=pd.read_pickle(HERE.parent/'circ_2025.pkl')
    v=v[v.distrito_id.eq(dist)].copy()
    full,_=pd.read_pickle(ROOT/'datos_oficiales/2025/agregado.pkl')
    names=full[full.distrito_id.astype(int).eq(int(dist))][['agrupacion_id','agrupacion_nombre']].dropna().drop_duplicates()
    names['agrupacion_id']=names.agrupacion_id.astype(str).str.zfill(4)
    mapping=names.drop_duplicates('agrupacion_id').set_index('agrupacion_id').agrupacion_nombre.to_dict()
    if validos:v=v[v.votos_tipo.isin(['POSITIVO','EN BLANCO'])].copy()
    v['cat']=np.where(v.votos_tipo.eq('POSITIVO'),v.agrupacion_id.astype(str).str.zfill(4).map(mapping),'Blanco' if validos else 'Blanco y nulo')
    assert not v.cat.isna().any(),v[v.cat.isna()].head()
    v['unidad']=v.circuito.map(lambda s:re.sub(r'^0+(?=\d)','',str(s)).upper())
    t=v.pivot_table(index='unidad',columns='cat',values='v',aggfunc='sum',fill_value=0)
    reference=nacional(dist,validos).sum()
    assert t.sum().sort_index().equals(reference.sort_index()),(dist,(t.sum()-reference).to_dict())
    return t


def caba():
    d=pd.read_csv(RAW/'caba2025.csv',sep=';',encoding='latin1')
    d=d[d.extranjera.str.upper().eq('NO')].copy()
    d['cat']=np.where(d.lista.isin(['BLC','REC','NUL','IMP']),'Blanco y nulo',d.lista)
    d['unidad']=d.circuito.astype(str)
    t=d.pivot_table(index='unidad',columns='cat',values='votos_totales',aggfunc='sum',fill_value=0)
    assert int(d.votos_totales.sum())==int(t.values.sum())
    t.to_pickle(HERE/'prov_caba.pkl')
    print('CABA',t.shape,t.sum().to_dict(),flush=True)
    return t


def jujuy():
    f=RAW/'ele25/Por Circuitos/CircuitosJuntos/Circuitos.pdf'
    names={135:'La Libertad Avanza',502:'Jujuy Crece',503:'FIT-U',504:'Trabajadores Jujeños',505:'Frente Justicialista',506:'Por un Nuevo Jujuy',507:'Confiar en Jujuy',508:'Somos Más',509:'Unir Liberal',510:'Transformación Libertaria',511:'Frente Amplio',528:'Primero Jujuy'}
    rows=[]
    with pdf.open(f) as doc:
        for pi,page in enumerate(doc):
            words=page.get_text('words')
            code=re.search(r'\n(\d+[A-Z]?)\s*-',page.get_text())
            assert code,pi
            row={'unidad':code[1]}
            h=next(w for w in words if w[4]=='Dip.Prov.')
            cx=(h[0]+h[2])/2
            def value(w):
                vals=[v[4] for v in words if abs((v[0]+v[2])/2-cx)<24 and abs(v[1]-w[1])<3 and re.fullmatch(r'[\d,]+',v[4])]
                assert len(vals)==1,(pi,w,vals)
                return number(vals[0])
            for w in words:
                if w[0]<45 and w[4].isdigit() and int(w[4]) in names:
                    row[names[int(w[4])]]=value(w)
            for label in ['BLANCOS','NULOS','RECURRIDOS','IMPUGNADOS','AFIRMATIVOS']:
                w=next(w for w in words if w[4]==label)
                row[label]=value(w)
            assert sum(row.get(n,0) for n in names.values())==row['AFIRMATIVOS'],(pi,row)
            row['Blanco y nulo']=sum(row.pop(k) for k in ['BLANCOS','NULOS','RECURRIDOS','IMPUGNADOS'])
            row.pop('AFIRMATIVOS')
            rows.append(row)
    t=pd.DataFrame(rows).set_index('unidad').fillna(0)
    assert t.index.is_unique
    assert int(t.drop(columns='Blanco y nulo').values.sum())==369394
    t.to_pickle(HERE/'prov_jujuy.pkl')
    t.to_csv(HERE/'prov_jujuy.csv',encoding='utf-8-sig')
    print('JUJUY',t.shape,t.sum().to_dict(),flush=True)
    return t


if __name__=='__main__':
    pba()
    salta()
    caba()
    jujuy()
