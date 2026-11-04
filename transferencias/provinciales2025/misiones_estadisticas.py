"""Versión tipográfica oficial de los mismos resultados, sin OCR ni residuos."""
import re
import pandas as pd
import pdfplumber
from fuentes import HERE,RAW


def norm(s):return re.sub(r'\s+',' ',str(s or '')).strip()


def main():
    rows=[]
    with pdfplumber.open(RAW/'misiones_estadisticas.pdf') as doc:
        for pi,page in enumerate(doc.pages[1:29],start=2):
            for table in page.extract_tables():
                for ri,row in enumerate(table):
                    for ci,cell in enumerate(row):
                        if norm(cell)!='Frente o Partido':continue
                        stop=next((j for j in range(ci+1,len(row)) if norm(row[j])=='Frente o Partido'),len(row))
                        ji=next((j for j in range(ci+1,stop) if norm(row[j])=='Diputados'),None)
                        if ji is None:continue
                        name=''
                        for prev in reversed(table[:ri]):
                            val=norm(prev[ci]) if len(prev)>ci else ''
                            if val:
                                name=re.sub(r'\s*Municipio con Carta Orgánica.*','',val).strip();break
                        record={'unidad':name,'pagina':pi}
                        for rr in table[ri+1:]:
                            if len(rr)<=ji:continue
                            party=norm(rr[ci]);votes=norm(rr[ji])
                            if party=='Frente o Partido':break
                            if not party:continue
                            if re.fullmatch(r'[0-9.]+',votes):record[party]=int(votes.replace('.',''))
                            if 'TOTALES' in party.upper():break
                        rows.append(record)
    name_by_page={2:'Posadas',6:'Leandro N. Alem',13:'Oberá',16:'Puerto Rico',18:'Aristóbulo del Valle',21:'Montecarlo',22:'San Vicente',24:'Eldorado',26:'San Pedro',28:'Puerto Iguazú'}
    for row in rows:
        if row['unidad'] in ['', 'TOTALES']:
            row['unidad']='El Soberbio' if row['pagina']==22 and row['unidad']=='TOTALES' else name_by_page[row['pagina']]
        row['unidad']=row['unidad'].replace(' con VOCOMI','')
        if row['unidad']=='Fachinal':row['TOTALES']=454  # celda impresa, PDF p. 2.
    t=pd.DataFrame(rows).set_index('unidad')
    t.to_csv(HERE/'misiones_estadisticas_revision.csv',encoding='utf-8-sig')
    print('TABLAS',t.shape,flush=True)
    print('COLUMNAS',t.columns.tolist(),flush=True)
    print('NOMBRES',t.index.tolist(),flush=True)
    print('TOTALES',t.sum(numeric_only=True).to_dict(),flush=True)
    t.to_pickle(HERE/'misiones_estadisticas_revision.pkl')
    data=t.drop(columns=['pagina','TOTALES'])
    assert not data.isna().any().any()
    assert data.sum(1).eq(t.TOTALES).all()
    assert data.index.is_unique
    data['Blanco y nulo']=data.pop('Votos en Blanco')+data.pop('Votos Nulos')
    data=data.rename(columns={'Frente Renovador De La Concordia':'Frente Renovador de la Concordia','Partido De Integración y Militancia':'Integración y Militancia','Frente Unidos por el Futuro':'Unidos por el Futuro'})
    data.to_pickle(HERE/'prov_misiones.pkl')
    data.to_csv(HERE/'prov_misiones.csv',encoding='utf-8-sig')


if __name__=='__main__':main()
