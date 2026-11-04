"""Consulta documentada del visor oficial: filtro departamento (enum 2)."""
import concurrent.futures as cf
import json
import requests
import pandas as pd
from fuentes import HERE,RAW

URL='https://elecciones2025-definitivo-api.corrientes.gob.ar/api/escrutinio/resultados/buscar'


def task(i):
    file=RAW/('corrientes_dep_%02d.json'%i)
    if not file.exists():
        r=requests.post(URL,json={'filtroTipoId':2,'valor':i,'descripcion':'Departamento','seleccionUnica':True,'valorDescripcion':''},verify=False,timeout=60)
        r.raise_for_status();file.write_bytes(r.content)
    return json.loads(file.read_text(encoding='utf8'))['data']


def main():
    with cf.ThreadPoolExecutor(4) as pool:data=list(pool.map(task,range(1,26)))
    data=[j for j in data if j.get('header')]
    # Esquina no está disponible en el filtro departamental del visor.
    # Se suman sus dos municipios, identificados por nombre en el mismo visor.
    extra=[json.loads((RAW/('corrientes_mun_'+str(i)+'.json')).read_text(encoding='utf8'))['data'] for i in [67,44]]
    data+=extra
    for cargo in ['Gobernador','Diputados','Senadores']:
        rows=[]
        for j in data:
            row={'unidad':'ESQUINA' if j in extra else j['header']['titulo']}
            for a in j['alianzas']:
                val=next((v['votos'] for v in a['alianzaData'] if v['titulo']==cargo),None)
                if val is not None:row[a['alianza']]=val
            special=0
            for p in j['partidos']:
                if p['partido'].upper().startswith('VOTOS '):
                    special+=sum(v['votos'] for v in p['partidoData'] if v['titulo']==cargo)
            row['Blanco y nulo']=special
            total=next(x['totalGeneral'] for x in j['totalVotos'] if x['cargoDescripcion']==cargo)
            row['control_total']=total
            rows.append(row)
        t=pd.DataFrame(rows).set_index('unidad').fillna(0).groupby(level=0).sum()
        t.to_csv(HERE/('corrientes_revision_'+cargo+'.csv'),encoding='utf-8-sig')
        print(cargo,t.shape,'cierres',(t.drop(columns='control_total').sum(1)-t.control_total).to_dict(),flush=True)
        t.to_pickle(HERE/('prov_corrientes_'+cargo.lower()+'.pkl'))


if __name__=='__main__':main()
